# EF Core — DbContext Lifecycle — Middle D

## 1. Nima? (Ta'rif)

**DbContext** — EF Core'ning markaziy klassi, DB bilan bo'ladigan
sessiyani ifodalaydi. U — **Unit of Work** (bir nechta o'zgarishni
bitta transaction sifatida saqlash) va **Repository** (DbSet orqali
so'rov yuborish) patternlarini o'zida birlashtiradi.

## 2. Nima uchun kerak?

`DbContext` — ICHIDA **Change Tracker** saqlaydi (qaysi entity
o'zgargani haqida ma'lumot) va bitta **DB connection**ni boshqaradi.
Uni noto'g'ri lifetime bilan ishlatish (masalan Singleton) — jiddiy
thread-safety va xotira muammolariga olib keladi.

## 3. Ichida nima sodir bo'ladi? (Mexanizm)

### 3.1 DbContext lifecycle — nima uchun Scoped

```
Singleton — BUTUN ilova umri davomida BITTA instance
Scoped    — HAR HTTP so'rov uchun YANGI instance (so'rov tugaganda Dispose)
Transient — HAR chaqiruvda YANGI instance

DbContext — Scoped bo'lishi SHART, chunki:
  ❌ Singleton bo'lsa — bir vaqtda 100 ta parallel so'rov BITTA
     DbContext'ni BOSHQARADI → Change Tracker'ga BIR VAQTDA yozish →
     THREAD-SAFETY buzilishi, "DbContext is not thread safe" xatosi

  ✅ Scoped bilan — har so'rov O'ZINING DbContext'iga ega, boshqa
     so'rovlarga ta'sir qilmaydi
```

```csharp
builder.Services.AddDbContext<AppDbContext>(options =>
    options.UseNpgsql(builder.Configuration.GetConnectionString("DefaultConnection")));
// AddDbContext — DEFAULT holda Scoped lifetime bilan ro'yxatdan o'tadi
```

### 3.2 `AddDbContext` vs `AddDbContextFactory`

```csharp
// AddDbContext — Controller/Handler konstruktoriga TO'G'RIDAN inject qilinadi
public class EmployeeService
{
    private readonly AppDbContext _context;
    public EmployeeService(AppDbContext context) => _context = context;
}

// AddDbContextFactory — BackgroundService, Blazor kabi Scoped BO'LMAGAN
// joylarda, HAR OPERATSIYA uchun YANGI DbContext yaratish uchun
builder.Services.AddDbContextFactory<AppDbContext>(options => options.UseNpgsql(connStr));

public class MyBackgroundService : BackgroundService
{
    private readonly IDbContextFactory<AppDbContext> _factory;

    protected override async Task ExecuteAsync(CancellationToken ct)
    {
        using var context = _factory.CreateDbContext(); // Har safar YANGI
        // ...
    }
}
```

### 3.3 Multiple DbContext — bir loyihada

```csharp
builder.Services.AddDbContext<HrDbContext>(o => o.UseNpgsql(hrConnStr));
builder.Services.AddDbContext<FinanceDbContext>(o => o.UseNpgsql(financeConnStr));
```

Bir nechta `DbContext` — turli **Bounded Context** (masalan HR va
Moliya modullari) yoki hatto turli DB'lar bilan ishlash uchun
ishlatiladi.

### 3.4 DbContext thread safety — parallel ishlatish muammosi

```csharp
// ❌ XATO — BIR XIL DbContext instance'ni PARALLEL ishlatish
var task1 = _context.Employees.ToListAsync();
var task2 = _context.Departments.ToListAsync();
await Task.WhenAll(task1, task2); // 💥 InvalidOperationException!

// ✅ TO'G'RI — ketma-ket (await bilan) yoki HAR BIRI uchun ALOHIDA scope/context
var employees = await _context.Employees.ToListAsync();
var departments = await _context.Departments.ToListAsync();
```

`DbContext` — **bitta vaqtda faqat bitta operatsiya**ni bajara oladi
(hatto async bo'lsa ham) — chunki ichkarida BITTA DB connection va
BITTA Change Tracker holatini boshqaradi.

### 3.5 Connection string — appsettings'dan olish

```json
{ "ConnectionStrings": { "DefaultConnection": "Host=localhost;Database=erp;Username=postgres;Password=..." } }
```

```csharp
options.UseNpgsql(builder.Configuration.GetConnectionString("DefaultConnection"));
```

### 3.6 DbContext Pooling — `AddDbContextPool`

```csharp
builder.Services.AddDbContextPool<AppDbContext>(options =>
    options.UseNpgsql(connStr), poolSize: 128);
```

```
Oddiy AddDbContext:
  Har so'rov → YANGI DbContext OBYEKTI yaratiladi (allocation)
              → so'rov oxirida Dispose

AddDbContextPool:
  Har so'rov → POOL'dan MAVJUD (allaqachon yaratilgan) DbContext OLINADI
              → so'rov oxirida — TOZALANIB, POOL'GA QAYTARILADI (YANGIDAN
                yaratilmaydi)

Foyda: yuqori TRAFIKLI ilovalarda — obyekt YARATISH/GC overhead'i
       KAMAYADI (10-15% performance yaxshilanishi bo'lishi mumkin)

⚠️ Cheklov: DbContext'da CONSTRUCTOR ichida "bir martalik" holat
   saqlamaslik kerak (pool orqali QAYTA ISHLATILGANI uchun state
   "sizib chiqishi" mumkin)
```

### 3.7 DbContext Dispose — `using` vs Scoped lifetime

```csharp
// Controller/Handler ichida — DI O'ZI Dispose qiladi (so'rov tugaganda)
public class EmployeeService
{
    private readonly AppDbContext _context; // using YOZISH SHART EMAS!
}

// Controller'dan TASHQARIDA (masalan Console App, Background job)
using var context = new AppDbContext(options); // Qo'lda Dispose SHART
```

### 3.8 Migration

```bash
dotnet ef migrations add AddEmployeeTable
dotnet ef database update
```

```
Add-Migration — Model o'zgarishlarini SOLISHTIRADI (oldingi
                 migratsiya bilan) va YANGI migration fayl (Up/Down
                 metodlari bilan) yaratadi
Update-Database — Migratsiyalarni HAQIQIY DB'ga QO'LLAYDI (SQL
                    generatsiya qilib bajaradi)
```

### 3.9 `DbSet<T>` — qanday ishlaydi

```csharp
public DbSet<Employee> Employees { get; set; }
```

`DbSet<T>` — `IQueryable<T>` va `IEnumerable<T>`ni implement qiladi —
LINQ so'rovlar unga qo'llanilganda **Expression Tree** yig'iladi,
faqat materialize qilinganda (`.ToList()`, `foreach`) SQL generatsiya
qilinib DB'ga yuboriladi.

## 4. Kod — to'liq DI sozlash

```csharp
// Program.cs
builder.Services.AddDbContext<AppDbContext>(options =>
{
    options.UseNpgsql(builder.Configuration.GetConnectionString("DefaultConnection"));
    if (builder.Environment.IsDevelopment())
        options.EnableSensitiveDataLogging().LogTo(Console.WriteLine);
});
```

## 5. Qachon ishlatish kerak?

| Vaziyat | Yechim |
|---|---|
| Oddiy Web API, Controller/Handler | `AddDbContext` (Scoped) |
| BackgroundService, Console App, Blazor Server | `AddDbContextFactory` |
| Yuqori trafik, performance kritik | `AddDbContextPool` |
| Bir nechta bog'liq bo'lmagan modul/DB | Bir nechta `DbContext` klassi |

## 6. Muhim nuqtalar

- DbContext HECH QACHON **Singleton** qilib ro'yxatdan o'tkazilmasin
  — thread-safety buziladi.
- Bir DbContext instance ustida **parallel** (`Task.WhenAll`) so'rov
  yubormang — ketma-ket await qiling yoki alohida context ishlating.
- `AddDbContextPool` — cheklovlari bor (masalan constructor'da murakkab
  logika bo'lmasligi kerak) — faqat performance muhim bo'lganda
  ishlatiladi.

## 7. Imtihon savollari

1. `DbContext` nima uchun Scoped bo'lishi kerak, Singleton EMAS?
2. `AddDbContext` va `AddDbContextFactory` orasidagi farq nima va
   qachon qaysi birini ishlatasiz?
3. Bitta `DbContext` instance'da ikkita so'rovni PARALLEL (`Task.WhenAll`)
   yuborish nima uchun xato beradi?
4. `AddDbContextPool` qanday performance foyda beradi va qanday
   cheklovi bor?
5. `DbSet<T>` qanday interfeyslarni implement qiladi va bu nima
   uchun muhim?
6. Migration'da `Add-Migration` va `Update-Database` orasidagi
   farq nima?
