# Pattern Matching (C# 8+, 9+, 10+, 11+) — Junior A

## 1. Nima? (Ta'rif)

**Pattern Matching** — bir ifodaning **turi va/yoki qiymatini**
tekshirish, va mos kelsa **avtomatik cast qilingan** o'zgaruvchi
bilan ishlash imkonini beruvchi til xususiyati — C# 7'dan boshlab
har versiyada kengaytirilgan.

## 2. Nima uchun kerak?

An'anaviy `if (obj is Type) { var x = (Type)obj; ... }` — **ikki
bosqichli** (tekshirish + cast), takrorlanuvchi. Pattern matching —
buni **BITTA** ifodaga birlashtiradi, va murakkab shartlarni
(kombinatsiya, diapazon, struktura) **deklarativ** tarzda ifodalash
imkonini beradi.

## 3. Ichida nima sodir bo'ladi? (Mexanizm)

### 3.1 `is` pattern (C# 7+)

```csharp
object obj = "salom";
if (obj is string s) // Tur TEKSHIRILADI + CAST qilinadi, BIR VAQTDA
    Console.WriteLine(s.Length);
```

### 3.2 Switch Expression (C# 8+)

```csharp
string GetCategory(int age) => age switch
{
    < 18 => "Voyaga yetmagan",
    >= 18 and < 65 => "Kattalar",
    _ => "Pensioner" // '_' — discard, "boshqa BARCHA holatlar"
};
```

```
Switch STATEMENT (eski):        Switch EXPRESSION (yangi):
switch (age) {                  var result = age switch {
  case < 18:                      < 18 => "...",
    result = "...";               >= 18 and < 65 => "...",
    break;                        _ => "..."
  ...                            };
}
QIYMAT QAYTARMAYDI (statement)  QIYMAT QAYTARADI (expression),
                                 QISQAROQ, "break" KERAK EMAS
```

### 3.3 Type pattern

```csharp
object shape = new Circle(5);
string description = shape switch
{
    Circle c => $"Doira, radius: {c.Radius}",
    Rectangle r => $"To'rtburchak: {r.Width}x{r.Height}",
    _ => "Noma'lum shakl"
};
```

### 3.4 Constant pattern

```csharp
int statusCode = 404;
string message = statusCode switch
{
    200 => "OK",
    404 => "Not Found",
    500 => "Server Error",
    _ => "Noma'lum"
};

object? obj = null;
if (obj is null) Console.WriteLine("Bo'sh"); // Constant pattern — null bilan
```

### 3.5 Relational pattern (C# 9+)

```csharp
string GetAgeGroup(int age) => age switch
{
    < 0 => "Noto'g'ri yosh",
    < 13 => "Bola",
    < 18 => "O'smir",
    < 65 => "Kattalar",
    _ => "Pensioner"
};
```

### 3.6 Logical pattern — `and`, `or`, `not` (C# 9+)

```csharp
bool IsValidAge(int age) => age is >= 0 and <= 120; // 0 <= age <= 120

bool IsSpecialRole(string role) => role is "Admin" or "SuperAdmin"; // role == "Admin" || role == "SuperAdmin"

bool IsNotNull(object? obj) => obj is not null; // !(obj == null)
```

### 3.7 Property pattern (C# 8+)

```csharp
public record Employee(string Name, int Age, string Department);

string Describe(Employee emp) => emp switch
{
    { Department: "IT", Age: > 30 } => "Tajribali IT xodimi",
    { Department: "IT" } => "IT xodimi",
    { Age: < 18 } => "Voyaga yetmagan xodim (NOTO'G'RI holat!)",
    _ => "Oddiy xodim"
};

// Nested property pattern
if (order is { Customer: { IsVip: true }, Total: > 1000000 })
    Console.WriteLine("VIP katta buyurtma");
```

### 3.8 Positional pattern — record deconstruction bilan

```csharp
public record Point(int X, int Y);

string Classify(Point p) => p switch
{
    (0, 0) => "Markazda",
    (0, _) => "Y o'qida",
    (_, 0) => "X o'qida",
    var (x, y) when x == y => "Diagonalda",
    _ => "Boshqa joyda"
};
```

### 3.9 List pattern (C# 11+)

```csharp
int[] numbers = { 1, 2, 3 };

string Describe(int[] arr) => arr switch
{
    [] => "Bo'sh massiv",
    [var single] => $"Bitta element: {single}",
    [var first, var second] => $"Ikkita: {first}, {second}",
    [var first, .., var last] => $"Birinchi: {first}, oxirgi: {last}", // '..' — QOLGAN elementlar (slice)
    _ => "Boshqa"
};
```

### 3.10 Guard clause — `when` kalit so'zi

```csharp
string Classify(Employee emp) => emp switch
{
    { Salary: > 10000000 } e when e.YearsOfService > 10 => "Senior, yuqori maosh",
    { Salary: > 10000000 } => "Yuqori maosh",
    _ => "Oddiy"
};
```

`when` — pattern MOS KELGANDAN KEYIN, QO'SHIMCHA **ixtiyoriy shart**
qo'shish imkonini beradi (pattern o'zi ifoda ETA OLMAYDIGAN
murakkab mantiq uchun).

### 3.11 Compiler optimizatsiyasi — pattern matching vs if-else

```
Switch Expression (KO'P pattern bilan) — compiler ICHKARIDA buni
ODATDA:
  - Konstantalar bo'lsa — JUMP TABLE (O(1), if-else ZANJIRIDAN TEZROQ)
  - Type pattern bo'lsa — KETMA-KET `is` tekshiruvlari (yuqoridan
    pastga, BIRINCHI mos kelgani QO'LLANADI)

Bu — DEBUG paytida ODDIY if-else zanjiridan farq QILMAYDI (natija
BIR XIL), LEKIN KOD ANCHA O'QILISHI OSON va DEKLARATIV.
```

### 3.12 Real misol — HTTP status code handler

```csharp
public static IActionResult HandleResponse(HttpResponseMessage response) => response.StatusCode switch
{
    HttpStatusCode.OK => new OkResult(),
    HttpStatusCode.NotFound => new NotFoundResult(),
    HttpStatusCode.Unauthorized or HttpStatusCode.Forbidden => new UnauthorizedResult(),
    var code when (int)code >= 500 => new StatusCodeResult(500),
    _ => new BadRequestResult()
};
```

### 3.13 Real misol — DTO converter

```csharp
public static string FormatEmployee(object entity) => entity switch
{
    FullTimeEmployee { MonthlySalary: var s } => $"To'liq stavka: {s:C}",
    Contractor { HourlyRate: var rate, HoursWorked: var hours } => $"Pudratchi: {rate * hours:C}",
    null => "Bo'sh",
    _ => "Noma'lum tur"
};
```

## 4. Kod — to'liq misol

```csharp
public record ApiResult<T>(bool Success, T? Data, string? Error);

public static IActionResult ToActionResult<T>(ApiResult<T> result) => result switch
{
    { Success: true, Data: not null } r => new OkObjectResult(r.Data),
    { Success: false, Error: "NotFound" } => new NotFoundResult(),
    { Success: false } r => new BadRequestObjectResult(r.Error),
    _ => new StatusCodeResult(500)
};
```

## 5. Qachon ishlatish kerak?

| Vaziyat | Pattern turi |
|---|---|
| Tur tekshirish + cast | Type pattern (`is`) |
| Ko'p shartli tanlov (if-else zanjiri o'rniga) | Switch expression |
| Diapazon tekshiruvi | Relational pattern (`< 18`) |
| Bir nechta shartni birlashtirish | Logical pattern (`and`/`or`/`not`) |
| Obyekt strukturasini tekshirish | Property pattern |
| Massiv/list strukturasi | List pattern (C# 11+) |

## 6. Muhim nuqtalar

- Switch expression — **BARCHA holatlar** qamrab olinmasa (masalan
  `_` yo'q) — compiler **ogohlantirish** beradi va runtime'da
  `SwitchExpressionException` tashlanishi mumkin.
- Property pattern — **nested** obyektlarni ham tekshirish imkonini
  beradi, lekin **haddan ortiq chuqurlashtirish** — o'qilishini
  yomonlashtiradi.
- `when` — pattern'ning **o'zi** ifoda eta olmaydigan shartlar uchun,
  lekin **haddan ortiq** ishlatilsa — oddiy `if-else`dan farqi
  yo'qoladi.

## 7. Imtihon savollari

1. `is` pattern va oddiy tur tekshirish + cast orasidagi farq nima?
2. Switch statement va switch expression orasidagi farq nima?
3. Property pattern nima va u qanday holatlarda foydali?
4. `when` guard clause nima uchun kerak?
5. List pattern (C# 11+) qanday ishlaydi — misol bilan tushuntiring.
6. Logical pattern (`and`, `or`, `not`) qanday ishlatiladi?
7. Switch expression compiler tomonidan qanday optimallashtiriladi
   (konstanta holatida)?
