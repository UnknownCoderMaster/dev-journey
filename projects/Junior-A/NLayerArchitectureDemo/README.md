# N-Layer Architecture Demo — O'quv Loyihasi

Bu loyiha — `docs/Junior-A/12-mvc-nlayer-architecture` mavzusidagi
**N-Layer Architecture** (3-tier: Presentation → Business → Data)
qismini **amalda** sinab ko'rish uchun yaratilgan. Qatlamlar —
shunchaki papkalar EMAS, **UCHTA ALOHIDA .csproj loyiha**:

```
NLayerDemo.DataAccess      (class library)  — DAL
NLayerDemo.BusinessLogic   (class library)  — BLL, DataAccess'ga ProjectReference
NLayerDemo.Api             (Web API)        — Presentation, FAQAT BusinessLogic'ga ProjectReference
```

## Nima uchun ALOHIDA loyihalar?

Agar hammasi BITTA loyihada, shunchaki papkalarda bo'lsa —
"Controller to'g'ridan DAL'ga murojaat qilmasin" degan qoidaga
rioya qilish FAQAT **kelishuv** (convention) darajasida qoladi —
hech narsa buni jismonan TO'XTATMAYDI. Bu loyihada esa:

- `NLayerDemo.Api.csproj` — **`NLayerDemo.DataAccess`ga ProjectReference'GA EGA EMAS**
- `EmployeeRepository` (konkret DAL klassi) — DataAccess loyihasida
  **`internal`** deb belgilangan

## Ishga tushirish

```bash
cd projects/Junior-A/NLayerArchitectureDemo
dotnet build      # 3 ta loyihani BIRGA build qiladi (.sln orqali)
cd NLayerDemo.Api
dotnet run
```

Brauzer avtomatik `https://localhost:7180/swagger` (yoki
`http://localhost:5280/swagger`) sahifasini ochadi.

## AMALIY sinov — dependency direction'ni "buzishga urinib ko'ring"

`NLayerDemo.Api/Controllers/EmployeesController.cs` fayli boshidagi
izohni o'qing va SHU YERDA tavsiya etilgan ikkita narsani sinab
ko'ring:

1. `using NLayerDemo.DataAccess;` qo'shib, `IEmployeeRepository`
   yoki `Entities.Employee` turlaridan foydalanib ko'ring — **bu
   COMPILE bo'ladi!** (.NET'da ProjectReference **tranzitiv**:
   Api → BusinessLogic → DataAccess, shuning uchun DataAccess'ning
   PUBLIC turlari Api'da ham "ko'rinadi" — bu .NET'ning normal,
   kutilgan xatti-harakati).
2. Endi `new NLayerDemo.DataAccess.EmployeeRepository(null!)`
   yozib ko'ring — **`CS0122: 'EmployeeRepository' is inaccessible
   due to its protection level` xatosini olasiz!**

**Xulosa:** Dependency direction — loyiha reference'lari orqali
EMAS, balki **`internal` access modifier** orqali, C# tili
darajasida MAJBURLANADI. Bu — real loyihalarda "qatlamlar orasidagi
chegara"ni qanday QATTIQ (hard boundary) qilib qo'yish mumkinligining
amaliy namunasi.

## API endpoint'lar

| Method | URL | Vazifa |
|---|---|---|
| GET | `/api/employees` | Barcha xodimlar (BLL orqali DTO'ga aylantirilgan) |
| GET | `/api/employees/{id}` | Bitta xodim (404 agar topilmasa) |
| POST | `/api/employees` | Yangi xodim (BLL validatsiyasi bilan) |
| PUT | `/api/employees/{id}` | Yangilash |
| DELETE | `/api/employees/{id}` | O'chirish |
| GET | `/api/employees/{id}/bonus` | Yillik bonusni hisoblash (docs 3.8-bo'limdagi misol) |

## Loyiha ichida nima bor

```
NLayerDemo.DataAccess/
  Entities/Employee.cs         — DB'ga mos entity
  AppDbContext.cs               — internal, EF Core InMemory
  IEmployeeRepository.cs        — public interfeys
  EmployeeRepository.cs         — internal implementatsiya!
  DependencyInjection.cs        — public "eshik" (AddDataAccessLayer)

NLayerDemo.BusinessLogic/
  Dtos/                          — EmployeeDto, Create/UpdateEmployeeDto
  EmployeeService.cs             — "God Service" (docs 4-bo'limdagi anti-pattern namunasi)
  DependencyInjection.cs         — AddBusinessLogicLayer (DAL'ni ICHIDA ulaydi)

NLayerDemo.Api/
  Controllers/EmployeesController.cs — FAQAT IEmployeeService'ga bog'liq
  Program.cs                          — bitta qator: AddBusinessLogicLayer()
```

## "God Service" haqida

`EmployeeService` — CRUD + validatsiya + bonus hisoblash — HAMMASINI
o'z ichiga oladi (docs 4-bo'limdagi aynan shu anti-pattern misoli).
Bu KICHIK loyihada MUAMMO EMAS, lekin o'nlab operatsiya qo'shilsa —
klass "shishib" ketadi. Buni `projects/Junior-D/HrManagementApi` yoki
Middle-D hujjatlaridagi **CQRS/MediatR** yondashuvi bilan solishtiring
— u yerda har operatsiya alohida, kichik Handler bo'ladi.
