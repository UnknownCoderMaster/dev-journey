# IQueryable vs IEnumerable — Junior B

## 1. What (Nima?)

**`IEnumerable<T>`** — XOTIRADAGI (in-memory) kolleksiya ustida,
BIR-BIR (element-by-element) ITERATSIYA QILISH interfeysi.
**`IQueryable<T>`** — `IEnumerable<T>`dan MEROS OLADI, LEKIN
QO'SHIMCHA — SO'ROVNI (query) **IFODA DARAXTI** (Expression Tree)
sifatida SAQLAYDI va uni **MA'LUMOTLAR MANBAI DVIGATELIGA**
(masalan PostgreSQL'ga) "TARJIMA QILIB YUBORISH" imkonini beradi.

## 2. Real hayot analogiyasi

**IEnumerable — RESTORANGA KELIB, BARCHA TAOMLARNI OLIB, O'ZINGIZ
STOLDA SARALASH.** Siz OSHXONADAN (DB'dan) BARCHA TAOMLARNI
(qatorlarni) OLASIZ, KEYIN O'ZINGIZ STOLDA "FAQAT VEGETARIAN
TAOMLARNI TANLAB OLASIZ" (Where filtri). **IQueryable — OSHXONAGA
"FAQAT VEGETARIAN TAOMLARNI OLIB KELING" DEB BUYURTMA BERISH.**
OSHXONA (DB SERVERI) — FAQAT KERAKLI TAOMLARNI TAYYORLAB,
STOLGA OLIB KELADI — SIZ ORTIQCHA TAOMLARNI KO'RMAYSIZ HAM,
TASHIB HAM YURMAYSIZ.

## 3. Why (Nega kerak?)

Agar `IEnumerable`'da FILTRLASH QILINSA — DB'DAN **BARCHA**
QATORLAR ILOVA XOTIRASIGA YUKLANADI, KEYIN C# KODI ICHIDA
FILTRLANADI — bu, MILLIONLAB QATORLI JADVALDA, **KATASTROFIK
DARAJADA SEKIN VA XOTIRA ISROFI**. `IQueryable` — FILTRNI SQL
`WHERE` BANDIGA AYLANTIRIB, DB SERVERIGA YUBORADI — DB SERVERI
(INDEKSLAR YORDAMIDA) FAQAT KERAKLI QATORLARNI QAYTARADI —
TARMOQ TRAFIGI VA XOTIRA SEZILARLI DARAJADA KAMAYADI.

## 4. Internals (Ichki mexanizm)

### `Func<T>` vs `Expression<Func<T>>` — ASOSIY FARQ

```csharp
Func<Employee, bool> predicate1 = e => e.Salary > 5000000;              // IEnumerable — KOMPILYATSIYA QILINGAN DELEGATE
Expression<Func<Employee, bool>> predicate2 = e => e.Salary > 5000000;  // IQueryable — IFODA DARAXTI (DATA STRUKTURA)
```

```
IEnumerable'ning Where() — Func<T,bool> QABUL QILADI — bu, ODDIY,
KOMPILYATSIYA QILINGAN C# DELEGATE (METOD KO'RSATKICHI) —
FAQAT CHAQIRISH MUMKIN, "ICHIGA QARAB" TAHLIL QILIB BO'LMAYDI.

IQueryable'ning Where() — Expression<Func<T,bool>> QABUL QILADI —
bu, LAMBDA IFODASINING "DATA STRUKTURA" (DARAXT) KO'RINISHI —
"e.Salary > 5000000" — {BinaryExpression: >, {MemberAccess:
Salary}, {Constant: 5000000}} KABI DARAXTGA AYLANADI. EF Core
PROVIDER — BU DARAXTNI "O'QIB", SQL GA TARJIMA QILADI.
```

### Deferred Execution — SO'ROV QACHON HAQIQATDA BAJARILADI

```csharp
var query = dbContext.Employees.Where(e => e.Salary > 5000000); // HALI SQL YUBORILMAGAN!
var list = await query.ToListAsync(); // ⚡ FAQAT SHU YERDA SQL YUBORILADI VA BAJARILADI
```

```
IQueryable — "LAZY" (KECHIKTIRILGAN): Where/Select/OrderBy —
FAQAT IFODA DARAXTINI "QURADI" — HECH QANDAY SQL YUBORILMAYDI.
FAQAT ToList()/ToListAsync()/First()/Count() KABI "TERMINAL"
METODLAR CHAQIRILGANDA — EF Core, TO'PLANGAN DARAXTNI SQL'GA
TARJIMA QILIB, DB'GA YUBORADI VA NATIJANI QAYTARADI.
```

### LINQ to Objects vs LINQ to Entities — PROVIDER TANLASH

```
`DbSet<T>` — IQueryable<T> IMPLEMENTATSIYASI, `Provider`
XUSUSIYATIGA EGA (masalan Npgsql EF Core Provider). HAR Where/
Select CHAQIRUVI — YANGI IQueryable QAYTARADI, LEKIN Provider —
O'ZGARMAYDI. FAQAT ToList() CHAQIRILGANDA, Provider —
TO'PLANGAN Expression DARAXTINI OLIB, PostgreSQL SQL SINTAKSISIGA
TARJIMA QILADI (masalan Npgsql'ning ICHKI "Query Translator"
qatlami orqali).

Agar .AsEnumerable() yoki .ToList() ERTA CHAQIRILSA — QOLGAN
LINQ ZANJIRI (Where, OrderBy) — ENDI IEnumerable USTIDA,
C# KODIDA (LINQ to Objects) BAJARILADI — DB'GA HECH QANDAY
QO'SHIMCHA SQL YUBORILMAYDI, LEKIN BARCHA MA'LUMOT ALLAQACHON
XOTIRAGA YUKLANGAN BO'LADI.
```

## 5. Code (Amaliy kod)

```csharp
// ❌ XATO — .ToList() ERTA CHAQIRILGAN — BARCHA XODIMLAR XOTIRAGA YUKLANADI
var expensiveEmployees = dbContext.Employees
    .ToList()                              // ⚠️ BUTUN JADVAL SQL orqali OLIB KELINADI!
    .Where(e => e.Salary > 5000000)        // ENDI — C# xotirada, LINQ to Objects
    .ToList();

// ✅ TO'G'RI — filtr SQL WHERE bandiga TARJIMA QILINADI, faqat KERAKLI qatorlar keladi
var expensiveEmployees = await dbContext.Employees
    .Where(e => e.Salary > 5000000)        // SQL: WHERE salary > 5000000
    .ToListAsync();                        // ⚡ FAQAT SHU YERDA SQL BAJARILADI

// IQueryable — QISMLARGA BO'LIB QO'SHISH MUMKIN (dinamik filtr qurish)
IQueryable<Employee> query = dbContext.Employees;

if (minSalary.HasValue)
    query = query.Where(e => e.Salary >= minSalary.Value);

if (!string.IsNullOrEmpty(departmentName))
    query = query.Where(e => e.Department.Name == departmentName);

var result = await query.ToListAsync(); // FAQAT BITTA, TO'LIQ SO'ROV — BARCHA FILTRLAR bilan
```

```csharp
// IEnumerable — C# metod ISHLATILSA, EF Core SQL'GA TARJIMA QILA OLMAYDI
var withCustomLogic = dbContext.Employees
    .AsEnumerable() // ⚡ ONGLI RAVISHDA IEnumerable'ga o'tkazish — BUTUN JADVAL keladi
    .Where(e => CustomBusinessLogic(e)); // C# metod — SQL'ga tarjima QILIB bo'lmaydi
```

## 6. Keng tarqalgan xatolar / noto'g'ri tushunchalar

```
❌ "DbSet<T>.ToList()ni ERTA chaqirish ZARARSIZ, chunki EF Core
   BARIBIR OPTIMALLASHTIRADI" — YO'Q! .ToList() CHAQIRILGANI
   ZAHOTI — SQL SO'ROV YUBORILADI VA BUTUN NATIJA XOTIRAGA
   YUKLANADI — KEYINGI Where/OrderBy — ENDI C# KODIDA, XOTIRADA
   BAJARILADI (SQL EMAS)!

❌ "IEnumerable va IQueryable — DEYARLI BIR XIL, FARQ YO'Q" —
   KATTA FARQ: IQueryable — SO'ROVNI DB'GA "SURIB YUBORADI"
   (TARMOQ orqali FAQAT KERAKLI DATA keladi), IEnumerable —
   BARCHA DATA'NI OLIB, ILOVADA FILTRLAYDI.

❌ "Har qanday C# metodni Where() ICHIDA ISHLATSA BO'LADI" —
   YO'Q! IQueryable ustida — FAQAT EF Core "TUSHUNADIGAN" (SQL'ga
   TARJIMA QILA OLADIGAN) IFODALAR ISHLAYDI. Custom C# metod
   (masalan reflection ishlatuvchi) — `InvalidOperationException`
   BERADI YOKI (eski EF Core versiyalarida) client-side
   evaluation'GA (SEKIN) TUSHIB QOLADI.

❌ ".Count() va .Any() — Where'dan KEYIN BIR XIL PERFORMANCE" —
   .Any() — SQL'DA "EXISTS" GA TARJIMA QILINADI (BIRINCHI MOS
   QATORNI TOPGANDA TO'XTAYDI) — .Count() > 0'dan TEZROQ (Count —
   BARCHA MOS QATORLARNI SANAYDI).
```

## 7. Exam (Interview savollari)

**1. `IQueryable<T>` va `IEnumerable<T>` orasidagi ASOSIY
FARQ nima?**
`IEnumerable` — XOTIRADAGI kolleksiya ustida ITERATSIYA QILADI.
`IQueryable` — SO'ROVNI Expression Tree sifatida SAQLAYDI va
DB PROVIDER'GA (masalan EF Core) SQL'GA TARJIMA QILISH VA
DB SERVERIDA BAJARISH imkonini beradi — bu, TARMOQ TRAFIGI va
XOTIRA ISHLATILISHINI SEZILARLI KAMAYTIRADI.

**2. `Func<T,bool>` va `Expression<Func<T,bool>>` orasidagi
FARQ nima?**
`Func<T,bool>` — KOMPILYATSIYA QILINGAN, TO'G'RIDAN CHAQIRILADIGAN
DELEGATE. `Expression<Func<T,bool>>` — LAMBDA IFODASINING
DATA-STRUKTURA (DARAXT) KO'RINISHI, DB PROVIDER TOMONIDAN
"O'QILIB", SQL'GA TARJIMA QILINISHI MUMKIN.

**3. Deferred Execution (kechiktirilgan bajarilish) nima
degani, va u qanday AMALIY AFZALLIK BERADI?**
LINQ metodlari (Where, Select, OrderBy) — DARHOL BAJARILMAYDI,
FAQAT SO'ROV DARAXTINI QURADI. Faqat ToList()/First() KABI
TERMINAL METOD CHAQIRILGANDA — HAQIQIY SO'ROV BAJARILADI. Bu,
BIR NECHTA FILTRNI QISM-QISM QO'SHIB, OXIRIDA BITTA, OPTIMAL
SQL SO'ROV SIFATIDA YUBORISH imkonini beradi.

**4. Nima uchun `.ToList()`ni ERTA (filterlashdan OLDIN)
chaqirish XAVFLI?**
`.ToList()` — DARHOL SQL SO'ROVNI BAJARADI VA BUTUN NATIJANI
XOTIRAGA YUKLAYDI. Undan KEYINGI Where/OrderBy — ENDI SQL'ga
EMAS, C# LINQ to Objects'GA AYLANADI — BUTUN JADVAL DB'DAN
OLIB KELINGANDAN KEYIN, ILOVADA FILTRLANADI — KATTA JADVALLARDA
JIDDIY PERFORMANCE MUAMMOSI.

**5. `IQueryable` ustida ISHLATILGAN CUSTOM C# METOD (masalan
o'zingiz yozgan business logic funksiya) NIMA UCHUN XATOLIK
BERISHI MUMKIN?**
EF Core PROVIDER — Expression Tree'ni SQL'GA TARJIMA QILISHI
UCHUN, UNDAGI HAR BIR OPERATSIYANI "TANISHI" KERAK. Custom C#
metod (SQL'GA MOS KELMAYDIGAN LOGIKA) — TARJIMA QILIB
BO'LMAYDI, shuning uchun `InvalidOperationException` BERADI —
YECHIM: `.AsEnumerable()`ga O'TKAZIB, C# tomonda BAJARISH (LEKIN
bu, BARCHA MOS DATA'NI OLDIN XOTIRAGA YUKLASHNI TALAB QILADI).
