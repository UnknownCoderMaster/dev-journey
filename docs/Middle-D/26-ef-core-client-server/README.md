# EF Core — Client vs Server Evaluation — Middle D

## 1. Nima? (Ta'rif)

**Server Evaluation** — LINQ operatsiyasi **SQL**ga tarjima qilinib,
DB serverida bajariladi. **Client Evaluation** — operatsiya SQL'ga
tarjima QILINMAY, ma'lumot **C# xotirasiga** yuklab olingach, C#
kodida bajariladi.

## 2. Nima uchun kerak?

Har bir LINQ metodini EF Core SQL'ga tarjima qila olmaydi (masalan,
custom C# metodlar). Bu farqni tushunmaslik — **kutilmagan
performance falokati**ga olib kelishi mumkin (butun jadval RAM'ga
yuklanib, keyin filtrlanadi).

## 3. Ichida nima sodir bo'ladi? (Mexanizm)

### 3.1 Server vs Client evaluation

```csharp
// ✅ Server evaluation — SQL WHERE ga tarjima qilinadi
var employees = await _context.Employees.Where(e => e.Age > 25).ToListAsync();
// SQL: SELECT * FROM employees WHERE age > 25

// ❌ Client evaluation — CUSTOM metod SQL'ga TARJIMA QILINMAYDI
var employees = await _context.Employees
    .Where(e => CalculateBonus(e.Salary) > 1000) // EF Core buni SQL'ga AYLANTIRA OLMAYDI!
    .ToListAsync();
```

### 3.2 `ToList()` — keyingi operatsiyalar CLIENT'da

```csharp
// ❌ XAVFLI PATTERN
var employees = await _context.Employees.ToListAsync(); // BARCHA qatorlar RAM'ga YUKLANADI!
var filtered = employees.Where(e => CalculateBonus(e.Salary) > 1000).ToList(); // Endi C# da filtrlanadi

// Agar jadvalda 1,000,000 qator bo'lsa — HAMMASI RAM'ga YUKLANADI,
// FAQAT keyin filtrlanadi — BU JUDA SAMARASIZ!
```

```
✅ TO'G'RI YONDASHUV: Custom mantiqni SQL'GA TARJIMA QILINADIGAN
   ifodaga AYLANTIRISH:

var employees = await _context.Employees
    .Where(e => e.Salary * 0.1m > 1000) // Oddiy arifmetika — SQL'GA TARJIMA QILINADI
    .ToListAsync();
```

### 3.3 EF Core 3+ da Strict Mode

```
EF Core 2.x — Client Evaluation'ni JIMGINA (ogohlantirmasdan) amalga
oshirar edi — bu KO'P loyihada SEZILMAGAN performance muammosiga
olib kelgan.

EF Core 3.0+ — Client Evaluation faqat ENG OXIRGI operatsiyada
(masalan Select proektsiyasida) RUXSAT ETILADI; WHERE ichida
tarjima qilib bo'lmaydigan ifoda bo'lsa — RUNTIME XATOSI tashlanadi
(jimgina C#'ga o'tkazish YO'Q):

InvalidOperationException: "could not be translated"
```

Bu — EF Core'ning **ataylab qilingan** dizayn qarori: samarasiz
so'rov **jimgina** ishlashi o'rniga, developer **darhol** xabardor
qilinadi.

### 3.4 Custom method lar — server bajarmaydigan misol

```csharp
// ❌ EF Core SQL'ga TARJIMA QILA OLMAYDI
public static bool IsSenior(Employee e) => e.Age > 50 && e.YearsOfService > 10;

var seniors = await _context.Employees.Where(e => IsSenior(e)).ToListAsync(); // 💥 XATO!

// ✅ Inline LINQ ifodasi — SQL'GA TARJIMA QILINADI
var seniors = await _context.Employees
    .Where(e => e.Age > 50 && e.YearsOfService > 10)
    .ToListAsync();
```

### 3.5 Raw SQL — `FromSqlRaw`, `ExecuteSqlRaw`

```csharp
// FromSqlRaw — SELECT so'rovi, entity qaytaradi
var employees = await _context.Employees
    .FromSqlRaw("SELECT * FROM employees WHERE department_id = {0}", departmentId)
    .ToListAsync();

// FromSqlInterpolated — PARAMETRIZATSIYA avtomatik (SQL Injection'dan HIMOYALANGAN)
var employees2 = await _context.Employees
    .FromSqlInterpolated($"SELECT * FROM employees WHERE department_id = {departmentId}")
    .ToListAsync();

// ExecuteSqlRaw — INSERT/UPDATE/DELETE (entity qaytarmaydi)
await _context.Database.ExecuteSqlRawAsync(
    "UPDATE employees SET is_active = false WHERE department_id = {0}", departmentId);
```

```
⚠️ FromSqlRaw — string CONCATENATION bilan ishlatilsa SQL Injection
   XAVFI bor. FromSqlInterpolated — $"" INTERPOLATED string ishlatib,
   AVTOMATIK parametrlashtiradi — XAVFSIZROQ.
```

### 3.6 Compiled Queries — tez-tez ishlatiladigan so'rovlar uchun

```csharp
private static readonly Func<AppDbContext, int, Task<Employee?>> GetByIdCompiled =
    EF.CompileAsyncQuery((AppDbContext context, int id) =>
        context.Employees.FirstOrDefault(e => e.Id == id));

var employee = await GetByIdCompiled(_context, 42);
```

```
Oddiy LINQ so'rov — HAR CHAQIRISHDA Expression Tree'ni QAYTA
TAHLIL QILADI (SQL'ga tarjima jarayoni QAYTA-QAYTA bajariladi).

Compiled Query — BIR MARTA tahlil qilinadi, KEYINGI chaqiruvlarda
QAYTA TAHLIL QILINMAYDI — juda TEZ-TEZ (masalan soniyasiga minglab
marta) chaqiriladigan so'rovlar uchun sezilarli performance foyda
beradi.
```

## 4. Kod — to'liq misol

```csharp
// ❌ Client evaluation — BARCHA ma'lumot yuklanadi
var result = (await _context.Employees.ToListAsync())
    .Where(e => IsEligibleForBonus(e))
    .ToList();

// ✅ Server evaluation — faqat SQL'ga tarjima qilinadigan shart
var result = await _context.Employees
    .Where(e => e.YearsOfService > 5 && e.PerformanceScore > 80)
    .ToListAsync();
```

## 5. Qachon ishlatish kerak?

| Vaziyat | Yechim |
|---|---|
| Oddiy filtr/agregatsiya | Server evaluation (LINQ to Entities) |
| Murakkab, SQL'ga tarjima qilib bo'lmaydigan mantiq | Ma'lumotni CHEKLAB (masalan `Where` bilan) yuklab, KEYIN C#'da qayta ishlash |
| Murakkab, optimallashtirilgan SQL kerak | `FromSqlInterpolated`/Raw SQL |
| Juda tez-tez chaqiriladigan oddiy so'rov | Compiled Query |

## 6. Muhim nuqtalar

- EF Core 3+ — Client Evaluation'ni **WHERE ichida** ruxsat bermaydi,
  bu **yaxshi** — samarasiz so'rovlar erta aniqlanadi.
- `FromSqlRaw` — string concatenation bilan ISHLATILMASIN (SQL
  Injection xavfi), `FromSqlInterpolated` afzal.
- Compiled Query — faqat **juda yuqori chastotali** so'rovlar uchun
  foydali, oddiy holatlarda ortiqcha murakkablik qo'shadi.

## 7. Imtihon savollari

1. Server Evaluation va Client Evaluation orasidagi farq nima?
2. EF Core 3+ da Client Evaluation qanday cheklangan va nima uchun
   bu yaxshi dizayn qarori?
3. `FromSqlRaw` va `FromSqlInterpolated` orasidagi xavfsizlik farqi
   nima?
4. Compiled Query qanday performance foyda beradi va qachon
   ishlatiladi?
5. Custom C# metodni `Where()` ichida ishlatish nima uchun xato
   beradi?
