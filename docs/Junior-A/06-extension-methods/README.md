# Extension Methods — Junior A

## 1. Nima? (Ta'rif)

**Extension Method** — mavjud klassni (hatto uning **manba kodiga
ega bo'lmasangiz ham**, yoki u `sealed` bo'lsa ham) **o'zgartirmasdan**,
unga **yangi metod "qo'shib qo'ygandek"** ko'rinish beruvchi
mexanizm.

## 2. Nima uchun kerak?

`string`, `int` kabi **BCL** (Base Class Library) klasslariga —
to'g'ridan metod qo'sha olmaysiz (manba kodi sizniki emas). Extension
Method — bu klasslarga **"go'yo"** yangi metod qo'shib, kodni
**o'qish oson** va **tabiiy** qiladi (`emp.IsAdult()` — `IsAdult(emp)`
dan ko'ra o'qilishi осонроq).

## 3. Ichida nima sodir bo'ladi? (Mexanizm)

### 3.1 Sintaksis — static class, static method, `this` parametr

```csharp
public static class StringExtensions
{
    public static bool IsNullOrEmptyCustom(this string? value) // 'this' — BIRINCHI parametr, EXTEND qilinayotgan tur
        => string.IsNullOrEmpty(value);

    public static string ToTitleCase(this string value)
        => CultureInfo.CurrentCulture.TextInfo.ToTitleCase(value.ToLower());
}

// Ishlatish — GO'YO string'ning O'ZINING metodi kabi!
string name = "orzibek toshmatov";
Console.WriteLine(name.ToTitleCase()); // → "Orzibek Toshmatov"
```

### 3.2 Namespace — qayerda e'lon qilinadi, qayerda ko'rinadi

```csharp
namespace MyApp.Extensions;

public static class EmployeeExtensions { /* ... */ }
```

```csharp
// Ishlatish uchun — namespace IMPORT qilinishi SHART
using MyApp.Extensions; // ❌ Bu using YO'Q bo'lsa — extension metod KO'RINMAYDI!

var name = employee.GetFullDisplayName();
```

Extension method — FAQAT **namespace import qilingan** joyda
**IntelliSense**da ko'rinadi va chaqirilishi mumkin — bu **implicit
ko'rinishni** cheklaydigan **dizayn qarori** (aks holda har qanday
loyihada minglab "keraksiz" extension metod ko'rinib, chalkashlik
tug'dirardi).

### 3.3 Compiler qanday tarjima qiladi — static method call

```csharp
name.ToTitleCase();

// COMPILER buni QUYIDAGICHA "TARJIMA" qiladi (IL darajasida):
StringExtensions.ToTitleCase(name);
```

```
MUHIM: Extension Method — RUNTIME'da HECH QANDAY MAXSUS mexanizm
EMAS! Bu — FAQAT COMPILE-TIME "SINTAKTIK QAND" (syntactic sugar) —
`obj.Method()` yozilganda, compiler AVVAL obj'ning O'Z klassida
Method() qidiradi, TOPILMASA — IMPORT qilingan namespace'lardagi
static klasslarda `this` parametrli mos METODNI QIDIRADI.
```

### 3.4 Qachon ishlatiladi

```
✅ Third-party klass (NuGet kutubxonasi) — manba kodiga EGA EMASSIZ
✅ sealed klass (masalan string) — MEROS OLIB kengaytirib bo'lmaydi
✅ Interfeys kengaytirish — HAMMA implementatsiyaga AVTOMATIK qo'shiladi
✅ LINQ — Where, Select — BARCHASI IEnumerable<T> uchun EXTENSION METOD!
```

### 3.5 `IEnumerable<T>` extension — LINQ shu tarzda ishlaydi

```csharp
public static class EnumerableExtensions
{
    public static IEnumerable<T> WhereActive<T>(this IEnumerable<T> source) where T : IActivatable
        => source.Where(x => x.IsActive);
}

var activeEmployees = employees.WhereActive(); // employees.Where(x => x.IsActive) bilan BIR XIL g'oya
```

`Microsoft.Linq`'ning O'ZI — `Where`, `Select`, `OrderBy` — HAMMASI
`IEnumerable<T>` (va `IQueryable<T>`) UCHUN yozilgan **extension
metodlar**! Shuning uchun `List<T>`, `T[]`, `Dictionary<K,V>` —
BARCHASI **avtomatik** LINQ metodlariga **ega** bo'ladi (`IEnumerable<T>`
implement qilgani uchun).

### 3.6 `IQueryable` extension — EF Core'da filter chain

```csharp
public static class EmployeeQueryExtensions
{
    public static IQueryable<Employee> WhereDepartment(this IQueryable<Employee> query, int departmentId)
        => query.Where(e => e.DepartmentId == departmentId);

    public static IQueryable<Employee> WhereActive(this IQueryable<Employee> query)
        => query.Where(e => e.IsActive);
}

// Zanjirlash — filter'larni QAYTA ISHLATISH mumkin bo'lgan bo'laklarga BO'LISH
var result = await _context.Employees
    .WhereDepartment(5)
    .WhereActive()
    .ToListAsync();
```

Bu — EF Core so'rovlarni **modulli, qayta ishlatiladigan** qilib
tuzishning keng tarqalgan usuli — har filter **ALOHIDA, TEST
qilinadigan** extension metod.

### 3.7 DTO extension — `ToDto()`, `ToEntity()`

```csharp
public static class EmployeeMappingExtensions
{
    public static EmployeeDto ToDto(this Employee entity)
        => new EmployeeDto(entity.Id, entity.FullName, entity.Salary);

    public static Employee ToEntity(this CreateEmployeeDto dto)
        => new Employee { FullName = dto.FullName, Salary = dto.Salary };
}

var dto = employee.ToDto(); // AutoMapper'ga ALTERNATIVA — oddiy, sodda holatlar uchun
```

### 3.8 Kamchiliklari — overuse, noaniqlik

```
❌ HADDAN ORTIQ ishlatish — "sehrli", QAYERDAN kelganini TOPISH
   QIYIN bo'lgan metodlar (IDE "Go to definition" YORDAM beradi,
   lekin ko'zdan kechirishda ANIQ emas)

❌ Bir xil nomdagi, TURLI namespace'dagi ikkita extension method —
   ZIDDIYAT (compiler XATO yoki NOANIQ tanlov) keltirib chiqarishi
   mumkin

❌ Extension method — INSTANCE metodni "USTIDAN YOZA" (override qila)
   OLMAYDI — agar klassning O'ZIDA bir xil nomli metod BO'LSA,
   HAR DOIM INSTANCE metod USTUN turadi
```

## 4. Kod — real ERP misolida extension methods

```csharp
public static class EmployeeExtensions
{
    public static bool IsEligibleForBonus(this Employee employee)
        => employee.YearsOfService >= 1 && employee.IsActive;

    public static decimal CalculateAnnualBonus(this Employee employee)
        => employee.IsEligibleForBonus() ? employee.Salary * 0.1m * employee.YearsOfService : 0;

    public static string GetDisplayName(this Employee employee)
        => $"{employee.FullName} ({employee.Department?.Name ?? "Bo'limsiz"})";
}

// Ishlatish
foreach (var emp in employees)
{
    if (emp.IsEligibleForBonus())
        Console.WriteLine($"{emp.GetDisplayName()}: {emp.CalculateAnnualBonus():C}");
}
```

## 5. Qachon ishlatish kerak?

| Vaziyat | Yechim |
|---|---|
| BCL/third-party klassga metod "qo'shish" | Extension method |
| `IEnumerable<T>`/`IQueryable<T>` uchun qayta ishlatiladigan filter | Extension method |
| Oddiy DTO↔Entity mapping (murakkab bo'lmasa) | Extension method |
| Murakkab, konfiguratsiyalanadigan mapping | AutoMapper (extension EMAS) |
| Klassning O'Z xatti-harakatini o'zgartirish | Extension EMAS, meros/composition |

## 6. Muhim nuqtalar

- Extension method — **`private`/`protected` a'zolarga kira olmaydi**
  (faqat klassning **public** interfeysi orqali ishlaydi).
- Extension method — **statik dispatch** (compile-time'da hal
  qilinadi), **polimorfizm** UCHUN ishlatib bo'lmaydi (`virtual`
  emas).
- Har doim `null` tekshiruvini **extension method ICHIDA** qilish
  mumkin (`this` parametr `null` bo'lsa ham — extension method
  CHAQIRILA OLADI, chunki bu — statik metod chaqiruvi, instance
  method emas)!

## 7. Imtihon savollari

1. Extension method compiler tomonidan qanday IL kodga tarjima
   qilinadi?
2. Extension method nima uchun `sealed` klasslarni "kengaytirish"
   imkonini beradi?
3. LINQ (`Where`, `Select`) qanday qilib extension method sifatida
   implement qilingan?
4. Extension method nega `private` a'zolarga kira olmaydi?
5. Bir xil nomli instance metod va extension metod bo'lsa, qaysi
   biri ustun turadi?
6. Extension method'ning asosiy kamchiliklari nimalar?
7. `this string? value` parametri `null` bo'lsa, extension method
   chaqirilganda `NullReferenceException` tashlanadimi? Nima uchun?
