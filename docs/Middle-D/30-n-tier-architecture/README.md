# N-Tier Architecture — Middle D

## 1. Nima? (Ta'rif)

**N-Tier Architecture** — ilovani mantiqiy **qatlamlarga**
(presentation, business, data) ajratish arxitekturasi. Klassik
ko'rinishi — **3-tier**: UI (Presentation), BLL (Business Logic
Layer), DAL (Data Access Layer).

## 2. Nima uchun kerak?

Agar HTTP so'rovni qabul qilish, biznes qoidalarni tekshirish va SQL
so'rov yuborish — **bitta metod** ichida bo'lsa — kod **testlanmas,
qayta ishlatilmas, tushunilmas** bo'lib qoladi. Qatlamlash —
**separation of concerns** (mas'uliyatlarni ajratish) orqali bu
muammoni hal qiladi.

## 3. Ichida nima sodir bo'ladi? (Mexanizm)

### 3.1 3-tier klassik

```
┌─────────────────────┐
│ Presentation (UI)     │  ← Controller, so'rov qabul qilish, javob qaytarish
└──────────┬───────────┘
           ▼
┌─────────────────────┐
│ Business Logic (BLL)  │  ← Validatsiya, hisob-kitob, biznes qoidalar
└──────────┬───────────┘
           ▼
┌─────────────────────┐
│ Data Access (DAL)      │  ← SQL/EF Core, DB bilan bevosita aloqa
└──────────┬───────────┘
           ▼
        Database
```

**Qoida:** har qatlam FAQAT **bevosita pastdagi** qatlam bilan
gaplashadi — Controller to'g'ridan DB'ga MUROJAAT QILMAYDI.

### 3.2 Sizning ERP tuzilmangiz — Controller → Handler → Repository → DB

```
Controller (Presentation)
    │
    ▼
MediatR Handler (Business Logic — CQRS Command/Query)
    │
    ▼
DbContext / Repository (Data Access)
    │
    ▼
PostgreSQL
```

Bu — 3-tier'ning **CQRS bilan zamonaviylashtirilgan** ko'rinishi:
BLL — endi "Service" klassi emas, balki **har bir operatsiya uchun
alohida Handler** (Command/Query).

### 3.3 Clean Architecture bilan farqi

```
N-Tier:              Clean Architecture:
UI → BLL → DAL       UI → Application → Domain ← Infrastructure

N-Tier'da — QARAM BOG'LIQLIK (dependency) YUQORIDAN PASTGA:
  UI DAL'ga bog'liq (BILVOSITA, BLL orqali)

Clean Architecture'da — DOMAIN MARKAZDA, HECH NARSAGA bog'liq EMAS:
  Infrastructure (DB) → Domain'GA bog'liq (TESKARI YO'NALISH!)
  (Dependency Inversion Principle amaliyoti)
```

N-Tier — **oddiyroq**, lekin DAL o'zgarishi (masalan EF Core'dan
Dapper'ga) BLL'ga **ta'sir qilishi** mumkin. Clean Architecture —
Domain'ni **hech narsadan mustaqil** qiladi, lekin **murakkabroq**.

### 3.4 Dependency direction

```
N-Tier: Presentation → Business → Data (BIR YO'NALISHDA, YUQORIDAN PASTGA)

Bu qat'iy tartib — LOYER'lar orasida "aylanma" bog'liqlik
(circular dependency) bo'lmasligini kafolatlaydi (masalan, DAL
BLL'ga bog'liq bo'lishi MUMKIN EMAS).
```

### 3.5 Nima uchun qatlamlash — Separation of Concerns

```
✅ Har qatlam — O'ZINING mas'uliyatiga ega:
   Controller — HTTP bilan ishlaydi (status kod, routing)
   Handler    — Biznes qoida (validatsiya, hisob)
   DbContext  — DB bilan ishlaydi (SQL, connection)

✅ Har qatlamni MUSTAQIL almashtirish mumkin (masalan UI'ni Web'dan
   mobil ilovaga o'zgartirish — BLL/DAL'ga TEGMAYDI)

✅ Har qatlamni ALOHIDA test qilish mumkin (BLL — DB'siz test qilinadi)
```

### 3.6 Kamchiliklari

```
❌ QAT'IY BOG'LIQLIK — har o'zgarish odatda BIR NECHTA qatlamga
   TEGISHLI bo'lishi mumkin (masalan yangi maydon — DAL, BLL, UI
   HAMMASIDA o'zgarish talab qiladi)

❌ ORTIQCHA ABSTRAKSIYA — kichik loyihalarda 3 qatlam — OVER-ENGINEERING
   bo'lishi mumkin (oddiy CRUD uchun BLL deyarli BO'SH bo'lib qoladi)

❌ Test qilish — agar QATLAMLAR TO'G'RI ABSTRAKSIYA qilinmagan bo'lsa
   (masalan BLL to'g'ridan DbContext'ga bog'liq) — QIYINLASHISHI mumkin
```

## 4. Kod — real misol

```csharp
// Presentation
[HttpPost]
public async Task<ActionResult<EmployeeDto>> Create(CreateEmployeeCommand command)
    => Ok(await _mediator.Send(command));

// Business Logic (Handler)
public class CreateEmployeeHandler : IRequestHandler<CreateEmployeeCommand, EmployeeDto>
{
    public async Task<EmployeeDto> Handle(CreateEmployeeCommand cmd, CancellationToken ct)
    {
        if (cmd.Age < 18) throw new ValidationException(new[] { "Yosh 18 dan kichik bo'lmasligi kerak" });

        var employee = new Employee { FullName = cmd.FullName, Age = cmd.Age };
        _context.Employees.Add(employee);
        await _context.SaveChangesAsync(ct);
        return _mapper.Map<EmployeeDto>(employee);
    }
}

// Data Access — DbContext (EF Core)
```

## 5. Qachon ishlatish kerak?

| Vaziyat | Yechim |
|---|---|
| O'rta-katta hajmli enterprise ilova | 3-tier / N-tier |
| Domain mantig'i juda murakkab, uzoq muddatli loyiha | Clean Architecture |
| Kichik, oddiy CRUD API | Yengil N-tier (ortiqcha qatlamsiz) |

## 6. Muhim nuqtalar

- N-tier — **fizik** joylashuv (masalan alohida server) emas,
  **mantiqiy** ajratish (bir xil process ichida ham bo'lishi mumkin).
- CQRS/MediatR — zamonaviy N-tier'ning BLL qatlamini **Handler**lar
  bilan almashtiradi, har biri "bitta operatsiya" mas'uliyatiga ega.
- Qatlamlash — **har doim** kerak emas — juda kichik xizmat (masalan
  bitta endpoint'li microservice) uchun ortiqcha bo'lishi mumkin.

## 7. Imtihon savollari

1. 3-tier arxitekturaning uch qatlamini ayting va har birining
   vazifasini tushuntiring.
2. N-Tier va Clean Architecture orasidagi eng muhim farq
   (dependency direction) nima?
3. CQRS/MediatR N-tier'ning BLL qatlamini qanday "zamonaviylashtiradi"?
4. N-tier arxitekturaning asosiy kamchiligi nima?
5. Nima uchun har qatlam FAQAT bevosita pastdagi qatlam bilan
   gaplashishi kerak?
