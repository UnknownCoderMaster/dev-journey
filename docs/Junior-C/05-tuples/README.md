# Tuples — ValueTuple, Named Tuples, Deconstruction, Tuple vs DTO — Junior C

## 1. Nima?

**Tuple** — bir nechta turli (yoki bir xil) turdagi qiymatni bitta
"yengil to'plam" sifatida birlashtirib saqlash yoki qaytarish uchun
mo'ljallangan tuzilma. C# 7+ da `ValueTuple` — bu **struct** (Value
type), eski `Tuple<T1,T2>` esa **class** (Reference type).

## 2. Nima uchun kerak?

Metod odatda faqat **bitta** qiymat qaytara oladi. Bir nechta qiymatni
qaytarish kerak bo'lganda, an'anaviy yechimlar noqulay edi:

```csharp
// ❌ out parametrlar — ko'p bo'lsa o'qish qiyin
public int Divide(int a, int b, out int remainder) { remainder = a % b; return a / b; }

// ❌ Maxsus klass yaratish — kichik, bir martalik holat uchun ortiqcha
public class DivisionResult { public int Quotient; public int Remainder; }

// ✅ Tuple — qisqa va aniq
public (int quotient, int remainder) Divide(int a, int b)
    => (a / b, a % b);
```

Agar Tuple bo'lmaganida — har bir kichik "bir nechta qiymat qaytarish"
holati uchun alohida DTO klass yaratish kerak bo'lardi — bu ortiqcha
boilerplate kod.

## 3. Ichida nima sodir bo'ladi? (Mexanizm)

### 3.1 Eski `Tuple<T1,T2>` vs yangi `ValueTuple` — xotira farqi

```csharp
// Eski (System.Tuple, .NET 4.0+) — CLASS, Heap'da
Tuple<int, string> old = Tuple.Create(1, "salom");

// Yangi (System.ValueTuple, C# 7+) — STRUCT, Stack'da
(int, string) modern = (1, "salom");
```

```
Tuple<int,string> (eski):          ValueTuple<int,string> (yangi):

STACK          HEAP                STACK
┌──────┐      ┌───────────┐        ┌──────────────────┐
│ old ─┼─────►│ Item1: 1  │        │ modern            │
└──────┘      │ Item2:"s" │        │  ├─ Item1: 1      │
              └───────────┘        │  └─ Item2: "salom"│
                                    └──────────────────┘
```

`ValueTuple` — **struct** bo'lgani uchun:
- Heap allocation **yo'q** (agar mahalliy o'zgaruvchi bo'lsa)
- **Boxing yo'q** (agar `object`/interfeys sifatida ishlatilmasa)
- Nusxalash orqali uzatiladi (value semantics)
- `Equals()` va `GetHashCode()` — **qiymat bo'yicha** solishtiradi
  (eski `Tuple` da ham shunday, lekin reference type bo'lgani uchun
  Heap allocation bor)

```csharp
var t1 = (1, "salom");
var t2 = (1, "salom");
Console.WriteLine(t1 == t2); // → True (qiymat solishtirilishi, C# 7.3+)

var old1 = Tuple.Create(1, "salom");
var old2 = Tuple.Create(1, "salom");
Console.WriteLine(old1.Equals(old2)); // → True, lekin har biri ALOHIDA Heap obyekti
Console.WriteLine(ReferenceEquals(old1, old2)); // → False
```

### 3.2 Named tuple — compiler "metadata" trigi

```csharp
var person = (Name: "Orzibek", Age: 25);
Console.WriteLine(person.Name); // → "Orzibek"
```

Muhim: `Name` va `Age` — **runtime**da mavjud emas! Bu faqat
**compile-time** metadata (`TupleElementNames` atributi orqali IL da
saqlanadi). Runtime darajasida baribir `Item1`, `Item2` ishlatiladi:

```csharp
var person = (Name: "Orzibek", Age: 25);
Console.WriteLine(person.Item1); // → "Orzibek" — ISHLAYDI! (Name — shunchaki alias)
```

### 3.3 Deconstruction — compiler nima qiladi?

```csharp
var (name, age) = GetPerson();
```

Compiler buni quyidagicha "ochadi" (desugar qiladi):

```csharp
var __tuple = GetPerson();
string name = __tuple.Item1;
int age = __tuple.Item2;
```

**Har qanday klass** deconstruction qo'llab-quvvatlashi mumkin —
`Deconstruct` metodini yozish kifoya:

```csharp
public class Employee
{
    public string Name { get; set; }
    public int Age { get; set; }

    public void Deconstruct(out string name, out int age)
    {
        name = Name;
        age = Age;
    }
}

var emp = new Employee { Name = "Orzibek", Age = 25 };
var (n, a) = emp; // ✅ Compiler Deconstruct() ni avtomatik chaqiradi!
```

### 3.4 `_` (discard) — keraksiz qiymatni tashlab yuborish

```csharp
var (_, age) = GetPerson(); // Faqat age kerak, name e'tiborsiz qoldiriladi

// Bir nechta discard
var (_, _, id) = GetTripleResult();

// out parametrlarda ham
if (int.TryParse(input, out _)) // Qiymat kerak emas, faqat muvaffaqiyat/muvaffaqiyatsizlik
{
    Console.WriteLine("Raqam edi");
}
```

`_` — compiler uchun maxsus belgi — u haqiqatda o'zgaruvchi
YARATMAYDI, shuning uchun bir nechta `_` bir joyda ishlatilishi mumkin
(oddiy nom bo'lsa — bu mumkin emas edi).

## 4. Kod — asosiy sintaksis

```csharp
// Nomsiz tuple
var t = (1, "salom", true);
Console.WriteLine(t.Item1); // 1
Console.WriteLine(t.Item2); // "salom"
Console.WriteLine(t.Item3); // true

// Nomli tuple
(string Name, int Age) person = ("Orzibek", 25);
Console.WriteLine(person.Name);

// Metod qaytarish turi sifatida
public (bool success, string message, int id) CreateEmployee(CreateEmployeeDto dto)
{
    if (string.IsNullOrWhiteSpace(dto.Name))
        return (false, "Ism bo'sh bo'lishi mumkin emas", 0);

    var id = _repo.Create(dto);
    return (true, "Muvaffaqiyatli yaratildi", id);
}

// Chaqirish va deconstruct qilish
var (success, message, id) = CreateEmployee(dto);
if (!success)
    return BadRequest(message);

// Tuple massiv/list ichida
var pairs = new List<(int Id, string Name)>
{
    (1, "Orzibek"),
    (2, "Dilnoza")
};
foreach (var (id2, name2) in pairs)
    Console.WriteLine($"{id2}: {name2}");

// Switch expression + tuple pattern matching
string Classify((int age, bool isEmployed) person) => person switch
{
    (< 18, _)          => "Voyaga yetmagan",
    (>= 18, true)       => "Ishlaydigan kattalar",
    (>= 18, false)      => "Ishlamaydigan kattalar",
};
```

## 5. Qachon ishlatish kerak?

| Vaziyat | Yechim | Nima uchun |
|---|---|---|
| Metod ichida, tashqariga chiqmaydigan vaqtinchalik natija | `Tuple` | Qisqa, klass yaratish shart emas |
| 2-3 ta oddiy qiymat, private/internal metod | `Tuple` | Boilerplate kamayadi |
| Public API, Controller javobi | `record`/DTO | Aniq nomlangan, dokumentatsiya, validatsiya mumkin |
| Immutable, qiymat solishtirish kerak, ID sifatida | `record` | `Equals`/`GetHashCode` avtomatik, o'qilishi oson |
| Ko'p (4+) maydon | Klass/`record` | Tuple o'qilishi qiyinlashadi |
| Serialization (JSON) kerak | DTO/`record` | Tuple lar JSON serialization'da `Item1`/`Item2` ko'rinishida chiqishi mumkin |

**Taqqoslash jadvali:**

| | `Tuple`(ValueTuple) | `record` | oddiy `class` DTO |
|---|---|---|---|
| Xotira | Stack (struct) | Heap (class) yoki Stack (`record struct`) | Heap |
| Immutable | Yo'q (o'zgartirsa bo'ladi) | Ha (default) | Yo'q (agar qo'lda qilinmasa) |
| Nomlangan property | Ixtiyoriy (compile-time alias) | Ha, to'liq | Ha, to'liq |
| Value equality | Ha | Ha | Yo'q (default reference equality) |
| Public API uchun mos | ❌ | ✅ | ✅ |

**Anti-pattern:**

```csharp
// ❌ Public Controller metodida Tuple qaytarish — Swagger/client uchun tushunarsiz
[HttpGet]
public (int, string, bool) Get() => (1, "Orzibek", true); // Item1/Item2/Item3 JSON da!

// ✅ record yoki DTO
public record EmployeeDto(int Id, string Name, bool IsActive);

[HttpGet]
public EmployeeDto Get() => new(1, "Orzibek", true);
```

## 6. Qo'shimcha — chuqur nuqtalar

- **`record` (C# 9+)** — Tuple'ning "kattalashtirilgan" alternativasi,
  lekin **immutable reference type**, avtomatik `ToString()`,
  `Equals()`, `GetHashCode()`, va `with` expression bilan nusxa olish:
  ```csharp
  record PersonInfo(string Name, int Age);
  var p1 = new PersonInfo("Orzibek", 25);
  var p2 = p1 with { Age = 26 }; // Yangi obyekt, faqat Age o'zgargan
  ```

- **`record struct` (C# 10+)** — `record`ning value-type versiyasi —
  Tuple bilan record o'rtasidagi ko'prik: value semantics + nomlangan
  propertylar.

- **Tuple equality — element-wise solishtirish:**
  ```csharp
  var a = (1, "x");
  var b = (1, "x");
  Console.WriteLine(a.Equals(b)); // True — har bir element solishtiriladi
  ```

- **8+ elementli tuple** — `ValueTuple` faqat 7 tagacha element uchun
  to'g'ridan qo'llab-quvvatlaydi; 8-chisi — ichma-ich `Rest` orqali
  ishlaydi (kamdan-kam amalda kerak bo'ladi, va bu — juda ko'p element
  bo'lsa DTO ishlatish belgisi).

- **Real loyihada uchraydigan xato:** Tuple'ni EF Core LINQ so'rovida
  `Select` natijasi sifatida qaytarish — ba'zi murakkab holatlarda
  Provider tomonidan noaniq SQL generatsiyaga olib kelishi mumkin;
  bunday hollarda alohida DTO/`record` klass ishlatish tavsiya etiladi.

## 7. Imtihon savollari

1. `ValueTuple` va eski `Tuple<T1,T2>` orasidagi asosiy xotira farqi
   nima?
2. Named tuple'dagi nomlar (`Name`, `Age`) runtime da mavjudmi? Isbot
   qanday?
3. Deconstruction ishlashi uchun klassga qanday metod qo'shish kerak?
4. `_` (discard) oddiy o'zgaruvchi nomidan nima bilan farq qiladi?
5. Qachon Tuple, qachon `record`, qachon oddiy DTO klass ishlatasiz?
6. Public Controller endpoint'ida Tuple qaytarish nima uchun
   tavsiya etilmaydi?
7. `record with` expression nima qiladi va u qanday immutability
   bilan bog'liq?
