# Minimal APIs — Junior B

## 1. What (Nima?)

**Minimal API** — ASP.NET Core'da (.NET 6+), **Controller
klasslarisiz**, `Program.cs` ichida to'g'ridan **funksional
uslubda** (`app.MapGet(...)`) endpoint yozish imkonini beruvchi
YENGIL YONDASHUV — an'anaviy MVC/Web API'ning Controller
BOILERPLATE'ini (klass, atribut, DI konstruktor) OLIB TASHLAYDI.

## 2. Real hayot analogiyasi

**Minimal API — YENGIL, TEZKOR RESTORAN (FAST FOOD).** An'anaviy
Web API Controller — TO'LIQ XIZMAT KO'RSATUVCHI RESTORAN
(HAR NARSA — STOL, OFITSIANT, MENYU KITOBI — RASMIY TARTIB).
Minimal API — FAST FOOD OYNACHASI: SIZ TO'G'RIDAN BUYURTMA
BERASIZ ("GET /burger"), OVQAT DARHOL TAYYORLANADI — HECH QANDAY
QO'SHIMCHA "RASMIYAT" (Controller klassi, atributlar) YO'Q. KICHIK,
TEZKOR BUYURTMALAR uchun IDEAL, LEKIN MURAKKAB, KO'P BOSQICHLI
XIZMAT (katta ilova) UCHUN — TO'LIQ RESTORAN (Controller-based)
KO'PROQ MOS.

## 3. Why (Nega kerak?)

Kichik microservice, funksiya (Azure Function-ga o'xshash), YOKI
TEZKOR PROTOTIP uchun — TO'LIQ Controller klassi (route atributi,
DI konstruktor, action metod) — **ORTIQCHA BOILERPLATE**. Minimal
API — bu OG'IRLIKNI OLIB TASHLAYDI: BITTA QATOR KOD — BITTA
ENDPOINT.

**Performance sababi HAM bor:** Minimal API — MVC PIPELINE'NING
BA'ZI QISMLARINI (masalan Model Binding'ning to'liq REFLECTION
BOSQICHI) CHETLAB O'TADI — bu, ayniqsa YUQORI TRAFIKLI, KICHIK
microservice'larda, SEZILARLI TEZLIK FARQINI BERISHI mumkin
(benchmark'larda — TechEmpower kabi manbalarda TASDIQLANGAN).

## 4. Internals (Ichki mexanizm)

### Routing — endpoint'lar QANDAY RO'YXATDAN O'TADI

```csharp
var app = builder.Build();

app.MapGet("/employees/{id}", (int id, AppDbContext db) =>
{
    var employee = db.Employees.Find(id);
    return employee is null ? Results.NotFound() : Results.Ok(employee);
});
```

```
MapGet/MapPost — ICHKARIDA "Endpoint" OBYEKTLARINI YARATADI VA
"Endpoint Routing" SISTEMASIGA (ASP.NET Core'ning MARKAZIY
ROUTING mexanizmi — MVC bilan HAM BIR XIL SISTEMA) QO'SHADI.
Controller-based API va Minimal API — BIR XIL ROUTING "DVIGATELI"NI
ISHLATADI, FAQAT ENDPOINT'LARNI RO'YXATDAN O'TKAZISH SINTAKSISI
FARQ QILADI.
```

### Dependency Injection — PARAMETR sifatida "AVTOMATIK" INJECT

```csharp
app.MapGet("/employees", (AppDbContext db, ILogger<Program> logger) =>
{
    logger.LogInformation("Xodimlar ro'yxati so'ralmoqda");
    return db.Employees.ToList();
});
```

```
Minimal API — LAMBDA PARAMETRLARINI, DI CONTAINER'DAN AVTOMATIK
"RESOLVE" QILADI (RUNTIME'da, PARAMETR TURI ASOSIDA) — Controller
konstruktoridagi INJECTION'GA O'XSHASH MEXANIZM, LEKIN SINTAKSIS
QISQAROQ.
```

### Route Handler — DELEGATE sifatida QANDAY BAJARILADI

```
HAR MapGet/MapPost — ICHKARIDA RequestDelegate'ga (ASP.NET Core
pipeline'ning ASOSIY UNIT'I — HttpContext QABUL QILIB, Task
QAYTARUVCHI DELEGATE) AYLANTIRILADI. Lambda PARAMETRLARI —
"Parameter Binding" mexanizmi ORQALI, HttpContext'dan (route,
query, body, DI) OLINADI.
```

### `Results.Ok()` vs `TypedResults.Ok()`

```
Results.Ok(data)     — IResult QAYTARADI, RUNTIME'da HAL QILINADI
TypedResults.Ok(data) — Ok<T> QAYTARADI (GENERIC, COMPILE-TIME
                         MA'LUM TUR) — Swagger/OpenAPI SCHEMA'NI
                         ANIQROQ GENERATSIYA QILADI (ActionResult<T>
                         GA O'XSHASH SABABGA KO'RA, .NET 7+ da
                         QO'SHILGAN)
```

### Endpoint Group'lar — Controller'ning MUQOBILI

```csharp
var employeesGroup = app.MapGroup("/api/employees");

employeesGroup.MapGet("/", GetAllEmployees);
employeesGroup.MapGet("/{id}", GetEmployeeById);
employeesGroup.MapPost("/", CreateEmployee);
```

```
MapGroup — UMUMIY PREFIKS ("/api/employees") va UMUMIY
FILTR/AUTHORIZATION QOIDALARINI, BIR NECHTA ENDPOINT ORASIDA
"BO'LISHISH" imkonini beradi — Controller klassining
"guruhlash" AFZALLIGINI, Minimal API SINTAKSISIDA TAQDIM ETADI.
```

## 5. Code (Amaliy kod)

```csharp
var builder = WebApplication.CreateBuilder(args);
builder.Services.AddDbContext<AppDbContext>(opt => opt.UseNpgsql(connStr));
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

var app = builder.Build();
app.UseSwagger();
app.UseSwaggerUI();

var employees = app.MapGroup("/api/employees").WithTags("Employees");

employees.MapGet("/", async (AppDbContext db) =>
    await db.Employees.ToListAsync());

employees.MapGet("/{id:int}", async Task<Results<Ok<Employee>, NotFound>> (int id, AppDbContext db) =>
{
    var employee = await db.Employees.FindAsync(id);
    return employee is null ? TypedResults.NotFound() : TypedResults.Ok(employee);
});

employees.MapPost("/", async (CreateEmployeeDto dto, AppDbContext db) =>
{
    var employee = new Employee { FullName = dto.FullName, Salary = dto.Salary };
    db.Employees.Add(employee);
    await db.SaveChangesAsync();
    return TypedResults.Created($"/api/employees/{employee.Id}", employee);
});

employees.MapDelete("/{id:int}", async (int id, AppDbContext db) =>
{
    var employee = await db.Employees.FindAsync(id);
    if (employee is null) return Results.NotFound();

    db.Employees.Remove(employee);
    await db.SaveChangesAsync();
    return Results.NoContent();
});

app.Run();

public record CreateEmployeeDto(string FullName, decimal Salary);
```

```csharp
// Validatsiya — Minimal API'da FluentValidation/qo'lda tekshiruv orqali
// ([ApiController] avtomatik ModelState tekshiruvi Minimal API'da YO'Q!)
employees.MapPost("/", async (CreateEmployeeDto dto, AppDbContext db) =>
{
    if (string.IsNullOrWhiteSpace(dto.FullName))
        return Results.BadRequest(new { message = "Ism majburiy" });

    // ... davomi
    return Results.Ok();
});
```

```csharp
// Authorization — Minimal API'da
employees.MapDelete("/{id:int}", async (int id, AppDbContext db) => { /* ... */ })
    .RequireAuthorization("AdminOnly"); // Policy — Controller'dagi [Authorize]ga TENG
```

## 6. Keng tarqalgan xatolar / noto'g'ri tushunchalar

```
❌ "Minimal API — Controller-based API'dan HAR DOIM TEZROQ" —
   FAQAT KICHIK farq (BENCHMARK'DA) — REAL loyihada, DB so'rov
   VAQTI (odatda 10-100ms) — MODEL BINDING/ROUTING FARQIDAN
   (MIKROSEKUNDLARDA) SEZILARLI KATTA — AMALIY PERFORMANCE
   FARQI KO'PINCHA E'TIBORGA OLINMAYDI.

❌ "Minimal API'da [ApiController]'ning AVTOMATIK Model Validation
   XATTI-HARAKATI HAM BOR" — YO'Q! Minimal API'da ModelState
   AVTOMATIK TEKSHIRUVI YO'Q — VALIDATSIYA QO'LDA (yoki
   FluentValidation, MinimalApis.Extensions kabi kutubxonalar
   orqali) AMALGA OSHIRILISHI KERAK.

❌ "Minimal API — FAQAT KICHIK loyihalar uchun" — MapGroup,
   Endpoint Filters kabi vositalar bilan, KATTA loyihalarda HAM
   TARTIBLI, MODULLI tarzda ISHLATISH mumkin.

❌ "Minimal API va Controller-based API — BIR LOYIHADA BIRGA
   ISHLATIB BO'LMAYDI" — NOTO'G'RI! ULAR BIR XIL ROUTING
   SISTEMASINI ISHLATADI — BIR PROJECT'DA IKKALASINI HAM
   ARALASH ISHLATISH MUMKIN (garchi UZLUKSIZLIK uchun ODATDA
   BITTASI TANLANADI).
```

## 7. Exam (Interview savollari)

**1. Minimal API va Controller-based Web API orasidagi ASOSIY
FARQ nima?**
Minimal API — Controller klassi/atributsiz, `Program.cs`da
TO'G'RIDAN `app.MapGet/MapPost` orqali endpoint YOZISH imkonini
beradi. Controller-based — Klass + [ApiController] + [HttpGet]
atributlar orqali, KO'PROQ "RASMIY" STRUKTURA taqdim etadi.
Ikkalasi HAM BIR XIL ROUTING SISTEMASIDAN foydalanadi.

**2. Minimal API'da Model Validation Controller-based API'dan
QANDAY FARQ QILADI?**
Controller-based API'da `[ApiController]` — ModelState.IsValid'ni
AVTOMATIK TEKSHIRADI. Minimal API'da BUNDAY AVTOMATIK MEXANIZM
YO'Q — VALIDATSIYA QO'LDA (masalan `if` tekshiruvlari) yoki
QO'SHIMCHA KUTUBXONA orqali AMALGA OSHIRILISHI KERAK.

**3. `MapGroup` NIMA UCHUN KERAK?**
Bir nechta ENDPOINT orasida UMUMIY PREFIKS (masalan
"/api/employees") va UMUMIY QOIDALARNI (masalan
Authorization, Tags) "BO'LISHISH" imkonini beradi — Controller
klassining "guruhlash" AFZALLIGIGA O'XSHASH, LEKIN Minimal
API sintaksisida.

**4. `Results.Ok()` va `TypedResults.Ok()` orasidagi FARQ nima?**
`Results.Ok()` — `IResult` (UMUMIY interfeys) QAYTARADI.
`TypedResults.Ok()` — GENERIC, ANIQ TUR (`Ok<T>`) QAYTARADI —
bu, Swagger/OpenAPI SCHEMA GENERATSIYASINI ANIQROQ QILADI
(`ActionResult<T>`ga O'XSHASH SABAB BILAN).

**5. Minimal API'da Dependency Injection QANDAY ISHLAYDI?**
LAMBDA PARAMETRLARI — DI CONTAINER'DAN, PARAMETR TURI ASOSIDA,
RUNTIME'DA AVTOMATIK "RESOLVE" QILINADI — Controller
KONSTRUKTORIGA INJECT QILISHGA O'XSHASH MEXANIZM, LEKIN
Parameter Binding orqali AMALGA OSHIRILADI.
