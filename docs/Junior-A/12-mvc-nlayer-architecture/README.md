# MVC Architecture, N-Layer Architecture — Junior A

## 1. Nima? (Ta'rif)

**MVC (Model-View-Controller)** — web ilovani 3 qatlamga ajratuvchi
UI dizayn patterni. **N-Layer Architecture** — ilovani **Presentation,
Business, Data** kabi mantiqiy qatlamlarga bo'luvchi arxitektura.

## 2. Nima uchun kerak?

UI mantig'i, biznes qoidalar va ma'lumotlar bazasi kodi **bir joyda
aralashsa** — kod tushunilmas, testlanmas bo'lib qoladi. MVC/N-Layer
— bu mas'uliyatlarni **ajratadi** (Separation of Concerns).

## 3. Ichida nima sodir bo'ladi? (Mexanizm)

### 3.1 MVC — Model, View, Controller

```
Model      — MA'LUMOT va BIZNES MANTIQ (Entity, DTO)
View       — FOYDALANUVCHIGA KO'RSATILADIGAN interfeys (Razor .cshtml)
Controller — Model va View ORASIDA "vositachi" — SO'ROVNI qabul
             qiladi, Model bilan ISHLAYDI, View'ga MA'LUMOT UZATADI
```

```
Request oqimi:

Brauzer → Controller (so'rovni qabul qiladi)
              │
              ▼
          Model (ma'lumotni oladi/o'zgartiradi — DB orqali)
              │
              ▼
          Controller (Model'dan natijani oladi)
              │
              ▼
          View (HTML generatsiya qiladi, Model ma'lumoti bilan)
              │
              ▼
          Brauzer (tayyor HTML sahifa)
```

### 3.2 ASP.NET Core MVC vs ASP.NET Core Web API

```
MVC     — View (Razor .cshtml) QAYTARADI — HTML sahifa
Web API — FAQAT ma'lumot (JSON/XML) QAYTARADI, View YO'Q

ASP.NET Core'da IKKALASI HAM — BIR XIL "Controller" tuzilmasidan
FOYDALANADI:
  Controller : Controller     — MVC uchun (View() metodi BOR)
  Controller : ControllerBase — Web API uchun (View() YO'Q)
```

### 3.3 Razor Pages vs MVC

```
MVC          — Controller + View AJRATILGAN, BITTA Controller —
                KO'P Action (KO'P View)
Razor Pages  — HAR SAHIFA — O'ZINING .cshtml + .cshtml.cs (PageModel)
                juftligi, KO'PROQ "sahifa-markazlashgan"
```

### 3.4 ViewBag, ViewData, TempData

```csharp
// Controller'dan View'ga MA'LUMOT UZATISH usullari:
ViewBag.Title = "Xodimlar ro'yxati";        // dynamic, faqat SHU so'rov ICHIDA
ViewData["Title"] = "Xodimlar ro'yxati";     // Dictionary<string, object>, faqat SHU so'rov ICHIDA
TempData["Message"] = "Muvaffaqiyatli!";     // KEYINGI so'rovGACHA SAQLANADI (Redirect'dan KEYIN HAM)
```

### 3.5 N-Layer Architecture — 3-tier klassik

```
┌─────────────────────┐
│ Presentation (UI)     │  ← Controller, HTTP bilan ishlash
└──────────┬───────────┘
           ▼
┌─────────────────────┐
│ Business Logic (BLL)  │  ← Validatsiya, hisob-kitob, qoidalar
└──────────┬───────────┘
           ▼
┌─────────────────────┐
│ Data Access (DAL)      │  ← ADO.NET/EF Core, DB bilan aloqa
└──────────┬───────────┘
           ▼
        Database
```

### 3.6 Dependency direction

```
Presentation → Business → Data — QAT'IY, BIR YO'NALISHDA

⚠️ Data Access — Business'ga BOG'LIQ BO'LMASLIGI KERAK (aylanma
   bog'liqlik — CIRCULAR DEPENDENCY — TAQIQLANGAN)
```

### 3.7 DAL — ADO.NET, EF Core

```csharp
// Data Access Layer — FAQAT DB bilan ishlash
public class EmployeeRepository
{
    public async Task<Employee?> GetByIdAsync(int id) => await _context.Employees.FindAsync(id);
}
```

### 3.8 BLL — servislar, validatsiya

```csharp
// Business Logic Layer — QOIDALAR, HISOB-KITOB
public class EmployeeBusinessService
{
    private readonly EmployeeRepository _repo;

    public async Task<decimal> CalculateBonusAsync(int employeeId)
    {
        var emp = await _repo.GetByIdAsync(employeeId);
        if (emp is null) throw new NotFoundException("Xodim topilmadi");
        return emp.Salary * 0.1m * emp.YearsOfService; // BIZNES QOIDA — shu YERDA
    }
}
```

### 3.9 Presentation — Controller, API

```csharp
[ApiController]
[Route("api/employees")]
public class EmployeesController : ControllerBase
{
    private readonly EmployeeBusinessService _service;

    [HttpGet("{id}/bonus")]
    public async Task<IActionResult> GetBonus(int id) => Ok(await _service.CalculateBonusAsync(id));
}
```

### 3.10 Afzalliklari va kamchiliklari

```
✅ Afzalliklari:
   - Mas'uliyatlar ANIQ AJRATILGAN
   - HAR qatlamni MUSTAQIL test qilish mumkin
   - UI o'zgarsa (Web → Mobile) — BLL/DAL O'ZGARMAYDI

❌ Kamchiliklari:
   - QAT'IY QATLAMLASH — kichik o'zgarish HAM bir nechta QATLAMGA
     TA'SIR qilishi mumkin (masalan yangi maydon — DAL, BLL, DTO,
     Controller — HAMMASIDA)
   - Kichik loyihalarda ORTIQCHA murakkablik
```

### 3.11 Layered vs Clean Architecture — farqi

```
N-Layer:              UI → BLL → DAL (BOG'LIQLIK YUQORIDAN PASTGA)
Clean Architecture:   UI → Application → Domain ← Infrastructure
                       (Domain — MARKAZDA, HECH NARSAGA bog'liq EMAS,
                        Infrastructure Domain'GA bog'liq — TESKARI!)
```

### 3.12 Sizning ERP tuzilmangiz

```
Controller (Presentation)
    │
    ▼
MediatR Handler (Business Logic — Command/Query)
    │
    ▼
DbContext (Data Access — EF Core)
    │
    ▼
PostgreSQL
```

### 3.13 Nega CQRS/MediatR N-Layer'dan yaxshiroq (ba'zi holatlarda)

```
N-Layer'da: EmployeeService — KO'P metodga ega ("God Service"
             xavfi), HAR metod — TURLI mas'uliyat

CQRS/MediatR: HAR operatsiya = BITTA Handler (BITTA fayl, BITTA
               mas'uliyat) — SRP'ga TABIIY MOS keladi, kod
               TOPILISHI OSON ("GetEmployeeByIdHandler.cs" — nomi
               ANIQ AYTIB TURIBDI)
```

## 4. Kod — N-Layer va CQRS solishtirmasi

```csharp
// N-Layer (klassik BLL) — KO'P metodli "God Service"
public class EmployeeService
{
    public Task<Employee> GetByIdAsync(int id) => /* ... */;
    public Task CreateAsync(CreateEmployeeDto dto) => /* ... */;
    public Task UpdateAsync(int id, UpdateEmployeeDto dto) => /* ... */;
    public Task DeleteAsync(int id) => /* ... */;
    // ... 20+ metod bo'lishi mumkin, HAMMASI BITTA klassda
}

// CQRS/MediatR — HAR operatsiya ALOHIDA, KICHIK Handler
public class GetEmployeeByIdHandler : IRequestHandler<GetEmployeeByIdQuery, EmployeeDto> { }
public class CreateEmployeeHandler : IRequestHandler<CreateEmployeeCommand, EmployeeDto> { }
```

## 5. Qachon ishlatish kerak?

| Vaziyat | Yechim |
|---|---|
| Server-rendered HTML sahifa | MVC |
| REST API, SPA/mobil frontend | Web API (ControllerBase) |
| Oddiy, kichik loyiha | Klassik N-Layer (Service klasslar) |
| Katta, ko'p operatsiyali ERP tizimi | CQRS/MediatR |

## 6. Muhim nuqtalar

- MVC va Web API — ASP.NET Core'da **bir xil** routing/middleware
  infratuzilmasidan foydalanadi, farqi — View mavjudligida.
- N-Layer — **qat'iy** yo'nalishga rioya qilinmasa (masalan
  Controller to'g'ridan DAL'ga murojaat qilsa) — arxitektura
  **buziladi**.
- CQRS/MediatR — N-Layer'ning **muqobili emas**, balki BLL
  qatlamini **tashkil qilishning boshqa usuli**.

## 7. Imtihon savollari

1. MVC'da Model, View, Controller — har biri qanday vazifani
   bajaradi?
2. ASP.NET Core'da MVC va Web API bir xil infratuzilmadan qanday
   foydalanadi?
3. N-Layer arxitekturaning 3 qatlamini ayting.
4. Dependency direction (yuqoridan pastga) nima uchun qat'iy
   bo'lishi kerak?
5. N-Layer va Clean Architecture orasidagi eng muhim farq nima?
6. CQRS/MediatR N-Layer'ning "God Service" muammosini qanday hal
   qiladi?
7. TempData va ViewData/ViewBag orasidagi farq nima?
