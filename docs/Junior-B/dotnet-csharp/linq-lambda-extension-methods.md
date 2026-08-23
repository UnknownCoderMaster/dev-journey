# LINQ, Lambda Expressions, Extension Methods — Junior B

## 1. What (Nima?)

**LINQ (Language Integrated Query)** — kolleksiyalar (massiv, list,
DB jadval) ustida **so'rov yozish**ni C# tilining O'ZIGA
**INTEGRATSIYA QILGAN** funksionallik — SQL'ga O'XSHASH sintaksisda
(`Where`, `Select`, `OrderBy`). **Lambda expression** — nomsiz,
QISQA metod yozish usuli (`x => x * 2`). **Extension method** —
mavjud turga (masalan `IEnumerable<T>`) YANGI metod "QO'SHISH"
imkonini beruvchi mexanizm — LINQ AYNAN shu mexanizm ORQALI
QURILGAN.

## 2. Real hayot analogiyasi

**LINQ — konveyer liniyasi.** Xom ashyo (kolleksiya) — bir NECHTA
STANSIYADAN (Where, Select, OrderBy) O'TADI, HAR STANSIYA — O'Z
VAZIFASINI bajarib, NATIJANI KEYINGI STANSIYAGA UZATADI. Siz
"QANDAY qilib" emas, "NIMA kerakligini" TASVIRLAYSIZ (DEKLARATIV) —
xuddi RESTORANDA "Menga VEGAN, GLUTENSIZ taom bering" DEB
AYTGANINGIZDEK — QANDAY TAYYORLANISHINI OSHPAZ HAL QILADI.

**Lambda — qisqa TOPSHIRIQ qog'ozi.** "Ushbu ISHNI bajar" deyish
o'rniga TO'LIQ INSTRUKSIYA YOZISH (metod), sizga faqat "x kelsa,
x*2 QAYTAR" deb YOZIB QO'YISH (`x => x * 2`) YETARLI — QOG'OZ
KICHIK, LEKIN VAZIFA ANIQ.

## 3. Why (Nega kerak?)

LINQ'siz — kolleksiyani FILTRLASH/SARALASH uchun `for`/`foreach`
BILAN QO'LDA yozilgan, KO'P QATORLI, TAKRORLANUVCHI kod KERAK
bo'lardi. LINQ — bu MANTIQNI **BIR QATORGA** siqadi, VA ENG
MUHIMI — **EF Core** orqali LINQ so'rovlari **SQL'ga TARJIMA**
qilinadi — bu, C# kod yozib, HAQIQIY DB so'rovini GENERATSIYA
QILISH imkonini BERADI (`docs/Junior-C/21-data-structures`,
`docs/Middle-D/26-ef-core-client-server`ga bog'liq).

**Java Stream API bilan solishtirish:** Java 8'dagi Stream API —
LINQ'ga JUDA O'XSHASH G'OYA (`filter`, `map`) — LEKIN LINQ AVVALROQ
(2007) KIRITILGAN va **QUERY SYNTAX** (SQL'ga O'XSHASH) ALTERNATIV
YOZISH USULINI HAM TAQDIM ETADI.

## 4. Internals (Ichki mexanizm)

### Extension method — compiler qanday "ALDAYDI"

```csharp
var adults = employees.Where(e => e.Age >= 18);

// COMPILER buni QUYIDAGICHA "TARJIMA" qiladi:
var adults = Enumerable.Where(employees, e => e.Age >= 18);
```

`Where` — `IEnumerable<T>` klassining METODI EMAS! Bu — `System.Linq.Enumerable`
STATIK klassidagi, `this IEnumerable<T> source` PARAMETRLI
EXTENSION METOD — batafsil: `docs/Junior-A/06-extension-methods`.

### Lambda — Delegate yoki Expression Tree'ga AYLANISHI

```csharp
Func<int, bool> isAdult = x => x >= 18;      // DELEGATE — KOMPILYATSIYA QILINGAN KOD
Expression<Func<int, bool>> expr = x => x >= 18; // EXPRESSION TREE — "MA'LUMOT" sifatida
```

```
Func<T> — LAMBDA COMPILE QILINADI (IL kod), TO'G'RIDAN CHAQIRILADI

Expression<Func<T>> — LAMBDA — MA'LUMOT STRUKTURASI (AST — Abstract
Syntax Tree) sifatida SAQLANADI, CHAQIRILMAYDI! EF Core AYNAN SHUNI
"O'QIYDI" va SQL'GA TARJIMA QILADI.
```

Bu — `IEnumerable<T>` (LINQ to Objects, `Func<T>` ISHLATADI) va
`IQueryable<T>` (LINQ to Entities/EF Core, `Expression<Func<T>>`
ISHLATADI) ORASIDAGI **ASOSIY FARQ**.

### Deferred Execution — LAZY EVALUATION

```csharp
var query = employees.Where(e => e.Age > 25); // HALI BAJARILMAGAN!
employees.Add(new Employee { Age = 30 });       // YANGI element QO'SHILDI

foreach (var e in query) // FAQAT SHU YERDA BAJARILADI — YANGI element HAM QAMRAB OLINADI!
    Console.WriteLine(e.FullName);
```

```
LINQ metodlari — IKKI GURUHGA BO'LINADI:

DEFERRED (LAZY) — Where, Select, OrderBy — DARHOL BAJARILMAYDI,
                   FAQAT "REJA" TUZADI, ITERATSIYA (foreach, ToList())
                   boshlanganda BAJARILADI

IMMEDIATE (EAGER) — ToList(), Count(), First(), Sum() — DARHOL
                     BAJARILADI, NATIJANI QAYTARADI
```

### `yield return` — LINQ metodlari QANDAY IMPLEMENT QILINGAN

```csharp
// Enumerable.Where() ning SODDALASHTIRILGAN implementatsiyasi:
public static IEnumerable<T> Where<T>(this IEnumerable<T> source, Func<T, bool> predicate)
{
    foreach (var item in source)
        if (predicate(item))
            yield return item; // HAR ELEMENT — BITTA-BITTA, "SO'RALGANDA" QAYTARILADI
}
```

`yield return` — COMPILER TOMONIDAN **STATE MACHINE**ga
AYLANTIRILADI (`async/await`ga O'XSHASH mexanizm) — batafsil
`docs/Junior-C/03-collections`da.

## 5. Code (Amaliy kod)

```csharp
// Method syntax (KENG TARQALGAN)
var result = employees
    .Where(e => e.Department == "IT")
    .OrderByDescending(e => e.Salary)
    .Select(e => new { e.FullName, e.Salary })
    .Take(5)
    .ToList();

// Query syntax (SQL'ga O'XSHASH, KAMROQ ISHLATILADI)
var result2 =
    from e in employees
    where e.Department == "IT"
    orderby e.Salary descending
    select new { e.FullName, e.Salary };
```

```csharp
// GroupBy — SQL'dagi GROUP BY'ga TENG
var byDepartment = employees
    .GroupBy(e => e.Department)
    .Select(g => new { Department = g.Key, Count = g.Count(), AvgSalary = g.Average(e => e.Salary) });

// Join — SQL'dagi INNER JOIN'ga TENG
var employeesWithDept = employees.Join(
    departments,
    e => e.DepartmentId,
    d => d.Id,
    (e, d) => new { e.FullName, DepartmentName = d.Name });
```

```csharp
// Custom Extension Method — LINQ'GA O'XSHASH USLUBDA
public static class EmployeeQueryExtensions
{
    public static IEnumerable<Employee> WhereActive(this IEnumerable<Employee> source)
        => source.Where(e => e.IsActive);
}

// Ishlatish — go'yo BUILT-IN LINQ metod kabi!
var activeEmployees = employees.WhereActive().OrderBy(e => e.FullName);
```

```csharp
// IEnumerable vs IQueryable — EF Core'da
IQueryable<Employee> query = _context.Employees.Where(e => e.Age > 25); // HALI SQL YUBORILMAGAN
var list = await query.ToListAsync(); // FAQAT SHU YERDA SQL GENERATSIYA + YUBORILADI
```

## 6. Keng tarqalgan xatolar / noto'g'ri tushunchalar

```
❌ "LINQ — HAR DOIM SEKIN" — NOTO'G'RI! Oddiy `foreach`ga NISBATAN
   OZGINA OVERHEAD bor (delegate chaqiruvi), LEKIN KO'PINCHA
   SEZILARLI EMAS. EF Core'da esa LINQ — SQL'GA TARJIMA QILINGANI
   uchun HATTO TEZROQ (kam ma'lumot YUKLANADI).

❌ "IEnumerable<T> va IQueryable<T> — BIR XIL" — YO'Q! EF Core'da
   `.ToList()`NI ERTA CHAQIRISH — QOLGAN FILTRLARNI C# xotirasida
   BAJARADI (SEKIN) — docs/Middle-D/26-ef-core-client-server'ga
   qarang.

❌ "Deferred execution — HAR DOIM BIR XIL natija BERADI" — NOTO'G'RI!
   Agar MANBA (source) o'ZGARTIRILSA, foreach HAR SAFAR QAYTA
   BAJARILGANDA — YANGI NATIJA BERISHI mumkin (yuqoridagi
   misolga qarang).

❌ "Where().Count() > 0 — Any() bilan BIR XIL" — TEXNIK JIHATDAN
   TO'G'RI natija BERADI, LEKIN Count() — BUTUN kolleksiyani
   AYLANIB CHIQADI, Any() — BIRINCHI mos ELEMENT topilishi bilan
   TO'XTAYDI (TEZROQ).

❌ "Extension method — INSTANCE metodni USTIDAN YOZA OLADI" —
   YO'Q! Agar KLASSNING O'ZIDA BIR XIL nomli metod BO'LSA, U HAR
   DOIM USTUN TURADI.
```

## 7. Exam (Interview savollari)

**1. `IEnumerable<T>` va `IQueryable<T>` orasidagi FARQ nima?**
`IEnumerable<T>` — LINQ to Objects, LAMBDA'lar `Func<T>` (COMPILE
QILINGAN DELEGATE) sifatida SAQLANADI, C# xotirasida BAJARILADI.
`IQueryable<T>` — LINQ to Entities, LAMBDA'lar `Expression<Func<T>>`
(AST) sifatida SAQLANADI, EF Core PROVIDER buni SQL'GA TARJIMA
QILADI, DB'da BAJARILADI.

**2. Deferred execution nima va u qanday XATOGA olib kelishi mumkin?**
LINQ so'rovi (`Where`, `Select`) DARHOL BAJARILMAYDI, FAQAT
ITERATSIYA boshlanganda. Agar SO'ROV BIR NECHTA MARTA (masalan
`.Count()` va KEYIN `foreach`) ISHLATILSA — HAR SAFAR QAYTA
BAJARILADI — bu KUTILMAGAN PERFORMANCE yo'qotish YOKI HATTO
TURLI NATIJALARGA (agar manba OZGARSA) olib KELISHI MUMKIN.

**3. Extension method compiler DARAJASIDA qanday ISHLAYDI?**
Bu — FAQAT COMPILE-TIME "SINTAKTIK QAND" — `obj.Method()` YOZILGANDA,
compiler AVVAL INSTANCE metodni QIDIRADI, TOPILMASA — IMPORT
QILINGAN NAMESPACE'lardagi STATIC klasslarda `this` PARAMETRLI
MOS METODNI QIDIRADI VA `StaticClass.Method(obj)` KO'RINISHIGA
"TARJIMA" QILADI. RUNTIME'da HECH QANDAY MAXSUS mexanizm YO'Q.

**4. `yield return` LINQ metodlarida QANDAY ROL O'YNAYDI?**
`Where`, `Select` KABI LINQ metodlari — ICHKARIDA `yield return`
orqali IMPLEMENT QILINGAN — bu ULARGA **LAZY** (bitta-bitta,
so'ralganda) NATIJA QAYTARISH imkonini BERADI, BUTUN KOLLEKSIYANI
OLDINDAN XOTIRAGA YUKLAMASDAN.

**5. `Select` va `SelectMany` orasidagi FARQ nima?**
`Select` — HAR ELEMENT uchun BITTA NATIJA QAYTARADI (1:1 mapping,
NATIJA — "KOLLEKSIYALAR KOLLEKSIYASI" bo'lishi MUMKIN). `SelectMany`
— HAR ELEMENT uchun KOLLEKSIYA QAYTARSA, NATIJALARNI **TEKISLAYDI**
(FLATTEN) — masalan HAR Department'ning Employees RO'YXATINI BITTA
UMUMIY Employee RO'YXATIGA BIRLASHTIRISH uchun ISHLATILADI.
