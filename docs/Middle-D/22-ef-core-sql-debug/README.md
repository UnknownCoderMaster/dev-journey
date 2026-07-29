# EF Core — SQL So'rovini Ko'rish (Debug) — Middle D

## 1. Nima? (Ta'rif)

EF Core — LINQ so'rovlarini **ko'rinmas** SQL'ga tarjima qiladi. Bu
"qora quti"ni ochib, aynan qanday SQL yuborilayotganini ko'rish uchun
bir nechta vosita mavjud.

## 2. Nima uchun kerak?

LINQ so'rov to'g'ri natija bersa ham, ICHKARIDA **samarasiz** SQL
generatsiya qilinishi mumkin (masalan, N+1, keraksiz JOIN). SQL'ni
ko'rmasdan turib bu muammolarni **aniqlab bo'lmaydi**.

## 3. Ichida nima sodir bo'ladi? (Mexanizm)

### 3.1 `LogTo` — Console'ga SQL chiqarish

```csharp
options.UseNpgsql(connStr).LogTo(Console.WriteLine, LogLevel.Information);
```

```
Natija konsolda:
info: Microsoft.EntityFrameworkCore.Database.Command[20101]
      Executed DbCommand (5ms) [Parameters=[@__id_0='1'], CommandType='Text']
      SELECT e.id, e.full_name FROM employees AS e WHERE e.id = @__id_0
```

### 3.2 Serilog bilan SQL logging

```csharp
builder.Host.UseSerilog((context, config) =>
    config.MinimumLevel.Override("Microsoft.EntityFrameworkCore.Database.Command", LogEventLevel.Information)
          .WriteTo.Console());
```

### 3.3 `ToQueryString()` — LINQ'ni SQL'ga

```csharp
var query = _context.Employees.Where(e => e.Age > 25);
string sql = query.ToQueryString(); // Bajarilmasdan, FAQAT SQL matnini oladi

Console.WriteLine(sql);
// SELECT e.id, e.full_name, e.age FROM employees AS e WHERE e.age > 25
```

Bu — so'rovni **bajarmasdan**, faqat qanday SQL generatsiya
qilinishini tekshirish uchun ENG QULAY vosita (unit test/debug'da).

### 3.4 `EnableSensitiveDataLogging` — parametrlarni ko'rish

```csharp
options.EnableSensitiveDataLogging(); // FAQAT Development'da!
```

```
Bu SOZLAMASIZ:  WHERE e.age > @__age_0
Bu SOZLAM bilan: WHERE e.age > 25 (HAQIQIY qiymat ko'rinadi)

⚠️ XAVFSIZLIK: Production'da YOQILMASIN — parol, shaxsiy ma'lumot
   kabi MAXFIY qiymatlar log fayllariga TUSHISHI mumkin!
```

### 3.5 EF Core Power Tools

Visual Studio kengaytmasi — DbContext'dan **vizual model diagrammasi**
generatsiya qilish, mavjud DB'dan **Reverse Engineering** (Scaffold)
orqali entity klasslarini yaratish imkonini beradi.

### 3.6 Slow query topish

```
1. LogTo() yoki Serilog orqali BARCHA SQL so'rovlarni logging qilish
2. Har so'rov uchun BAJARILISH VAQTINI (ms) kuzatish
3. Muayyan chegaradan (masalan 500ms) YUQORI so'rovlarni ALOHIDA
   belgilash (custom middleware yoki APM vosita — Application
   Insights, Datadog)
4. `EXPLAIN ANALYZE` orqali PostgreSQL darajasida query plan
   tekshirish
```

### 3.7 N+1 problem — qanday aniqlanadi

```csharp
// ❌ N+1 — har xodim uchun ALOHIDA so'rov (Department LAZY LOAD qilinsa)
var employees = await _context.Employees.ToListAsync(); // 1 SO'ROV
foreach (var e in employees)
    Console.WriteLine(e.Department.Name); // HAR BIRIDA — YANA 1 SO'ROV! (N ta qo'shimcha)
```

```
LogTo orqali BU quyidagicha ko'rinadi:

SELECT * FROM employees;                              -- 1-so'rov
SELECT * FROM departments WHERE id = 1;                -- 2-so'rov
SELECT * FROM departments WHERE id = 2;                -- 3-so'rov
SELECT * FROM departments WHERE id = 3;                -- 4-so'rov
... (har xodim uchun TAKRORLANADI!)

Agar 1000 ta xodim bo'lsa — 1001 ta SO'ROV yuboriladi!
```

**Yechim — `Include`:**
```csharp
var employees = await _context.Employees.Include(e => e.Department).ToListAsync();
// FAQAT 1 SO'ROV (JOIN orqali) — barcha ma'lumot BIRGA keladi
```

## 4. Kod — to'liq diagnostika sozlash

```csharp
builder.Services.AddDbContext<AppDbContext>(options =>
{
    options.UseNpgsql(connStr);
    if (builder.Environment.IsDevelopment())
    {
        options.EnableSensitiveDataLogging()
               .EnableDetailedErrors()
               .LogTo(message => Debug.WriteLine(message), LogLevel.Information);
    }
});
```

## 5. Qachon ishlatish kerak?

| Vaziyat | Yechim |
|---|---|
| Development'da SQL'ni tez ko'rish | `LogTo(Console.WriteLine)` |
| Unit test'da SQL'ni tekshirish (bajarmasdan) | `ToQueryString()` |
| Production monitoring | Serilog + APM (Application Insights) |
| N+1 shubhasi | Log tahlili — ketma-ket bir xil SQL naqshini qidirish |

## 6. Muhim nuqtalar

- `EnableSensitiveDataLogging()` — FAQAT Development, HECH QACHON
  Production'da yoqilmasin (maxfiy ma'lumot log'ga tushishi mumkin).
- N+1 — EF Core'da **eng ko'p uchraydigan** performance muammosi —
  har doim `Include`/projection bilan tekshirilishi kerak.
- `ToQueryString()` — **parametrlangan** SQL qaytaradi (haqiqiy
  qiymatlar EMAS, agar `EnableSensitiveDataLogging` yoqilmagan bo'lsa).

## 7. Imtihon savollari

1. `LogTo` va `ToQueryString()` orasidagi vazifa farqi nima?
2. `EnableSensitiveDataLogging` nima uchun faqat Development'da
   yoqilishi kerak?
3. N+1 muammosini log orqali qanday aniqlash mumkin?
4. N+1 muammosini `Include` qanday hal qiladi?
5. EF Core Power Tools qanday vazifani bajaradi?
