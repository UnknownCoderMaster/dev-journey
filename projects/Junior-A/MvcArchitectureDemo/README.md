# MVC Architecture Demo — O'quv Loyihasi

Bu loyiha — `docs/Junior-A/12-mvc-nlayer-architecture` mavzusidagi
**MVC (Model-View-Controller)** qismini **amalda** sinab ko'rish
uchun yaratilgan. Bu — **ASP.NET Core MVC** (Web API emas!) — Razor
View'lar orqali to'liq HTML sahifalar qaytaradi.

## Ishga tushirish

```bash
cd projects/Junior-A/MvcArchitectureDemo
dotnet run
```

Brauzer `https://localhost:7181` (yoki `http://localhost:5281`)
manzilida ochiladi.

## Sinab ko'rish kerak bo'lgan narsalar

### 1. So'rov oqimi (Request Flow)

Bosh sahifada (`/`) — MVC oqimi bosqichma-bosqich yozilgan. `Xodimlar`
bo'limiga o'tib, bu oqimni **AMALDA** kuzating:
`Brauzer → EmployeesController.Index() → IEmployeeStore (Model) →
View(employees) → Employees/Index.cshtml → Brauzer`.

### 2. ViewBag vs ViewData vs TempData

- `HomeController.Index()` — `ViewData["Title"]` VA `ViewBag.WelcomeMessage`
  ikkalasini HAM ishlatadi (ikkalasi — **BIR XIL** ichki Dictionary'ga
  yozadi, faqat sintaksisi farq qiladi).
- `EmployeesController.Index()` — `ViewBag.Title`ni o'rnatadi, `Index.cshtml`
  esa uni `ViewData["Title"]`ga o'qib oladi — shu orqali IKKALASI HAM
  **bir xil narsa** ekanini ko'rasiz.
- **TempData** — eng muhim farq: Xodimlar ro'yxatida **"+ Yangi xodim
  qo'shish"** tugmasini bosib, formani to'ldiring va saqlang. Sahifa
  `RedirectToAction(Index)` orqali qayta yo'naltiriladi (YANGI HTTP
  so'rov!), lekin muvaffaqiyat xabari **hali ham ko'rinadi** — chunki
  u `TempData`da saqlangan. Sahifani **qayta yangilang (F5)** — xabar
  **yo'qolganini** ko'rasiz (TempData — bir marta o'qiladi, keyin
  o'chiriladi).

### 3. Model Validation

"Yangi xodim qo'shish" formasida **Ism**ni bo'sh qoldirib
"Saqlash"ni bosing — `Employee` modelidagi `[Required]` atributi
`ModelState.IsValid`ni `false` qiladi, va Controller **xuddi shu
formani, kiritilgan qiymatlar bilan** qayta ko'rsatadi (`return
View(employee)`), redirect qilinmaydi.

### 4. To'liq CRUD

Index → Details → Edit → Delete — barchasi ishlaydi, `IEmployeeStore`
(xotiradagi oddiy "Model" qatlami) orqali.

## Loyiha tuzilmasi

```
Models/Employee.cs              — Model (ma'lumot + validatsiya atributlari)
Data/IEmployeeStore.cs          — Oddiy "Model" ma'lumot manbai (xotirada)
Controllers/HomeController.cs   — ViewBag/ViewData namunasi
Controllers/EmployeesController.cs — To'liq CRUD, TempData namunasi
Views/Home/Index.cshtml         — MVC oqimi tushuntirilgan bosh sahifa
Views/Employees/*.cshtml        — Index, Details, Create, Edit, Delete
Views/Shared/_Layout.cshtml     — Umumiy shablon (TempData shu yerda ko'rsatiladi)
Program.cs                      — AddControllersWithViews(), convention-based routing
```

## Eslatma

Bu loyiha — **oddiy MVC**ni ko'rsatish uchun, shuning uchun DAL/BLL
qatlamlari **ataylab** ajratilmagan (`IEmployeeStore` — hammasi
birga). To'liq **N-Layer** (DataAccess/BusinessLogic/Presentation —
alohida loyihalar) namunasi uchun qarang:
[`../NLayerArchitectureDemo`](../NLayerArchitectureDemo/README.md).
