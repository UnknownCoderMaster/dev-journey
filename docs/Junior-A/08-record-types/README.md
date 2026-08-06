# Record Types (C# 9+) — Junior A

## 1. Nima? (Ta'rif)

**Record** — C# 9'da qo'shilgan, **immutable** (o'zgarmas) va
**value equality** (qiymat bo'yicha tenglik) ga ega **reference
type** (yoki C# 10+ da `record struct` bilan **value type**).

## 2. Nima uchun kerak?

Oddiy `class` — **reference equality** (bir xil obyekt EKANLIGI)
ni tekshiradi, `Equals`/`GetHashCode`/`ToString` — **qo'lda**
yozilishi kerak. DTO larda — ko'pincha **qiymat tengligi** va
**immutability** kerak (masalan, ikkita `Money(100, "USD")` — bir
xil qiymat bo'lsa **teng** hisoblanishi kerak) — record bu boilerplate'ni
**avtomatlashtiradi**.

## 3. Ichida nima sodir bo'ladi? (Mexanizm)

### 3.1 record vs class vs struct — jadval

| | `class` | `struct` | `record` (class) | `record struct` |
|---|---|---|---|---|
| Xotira | Heap | Stack (odatda) | Heap | Stack (odatda) |
| Tenglik | Reference | Value (field-by-field) | Value (avtomatik) | Value (avtomatik) |
| Immutable default | ❌ Yo'q | ❌ Yo'q | ✅ Ha (`init`) | ✅ Ha (`init`) |
| `ToString()` | Object default | Value ko'rsatadi | ✅ Avtomatik chiroyli | ✅ Avtomatik chiroyli |

### 3.2 Positional record

```csharp
public record Employee(string FullName, int Age, decimal Salary);

var emp = new Employee("Orzibek", 25, 5000000);
Console.WriteLine(emp.FullName); // → "Orzibek" (AVTOMATIK property yaratildi!)
```

Compiler — positional record'dan **avtomatik**: `init`-only
propertylar, konstruktor, `Deconstruct` metod, `Equals`/`GetHashCode`,
`ToString()` generatsiya qiladi.

### 3.3 Property record — to'liq nazorat

```csharp
public record Employee
{
    public required string FullName { get; init; }
    public int Age { get; init; }
    public decimal Salary { get; init; } = 0; // Default qiymat
}

var emp = new Employee { FullName = "Orzibek", Age = 25 };
```

### 3.4 `record struct` (C# 10+)

```csharp
public record struct Point(double X, double Y);

var p1 = new Point(1.0, 2.0);
var p2 = new Point(1.0, 2.0);
Console.WriteLine(p1 == p2); // → True (VALUE equality, Stack'da)
```

`record struct` — value semantics (Stack'da, nusxalanadi) BILAN
record'ning qulayligini (avtomatik Equals/ToString) **birlashtiradi**.

### 3.5 Value equality — `==` operator avtomatik

```csharp
public record Employee(string FullName, int Age);

var emp1 = new Employee("Orzibek", 25);
var emp2 = new Employee("Orzibek", 25);

Console.WriteLine(emp1 == emp2);          // → True! (VALUE equality)
Console.WriteLine(emp1.Equals(emp2));      // → True!
Console.WriteLine(ReferenceEquals(emp1, emp2)); // → False (IKKI XIL obyekt)
```

```
Oddiy class'da:
var c1 = new EmployeeClass("Orzibek", 25);
var c2 = new EmployeeClass("Orzibek", 25);
c1 == c2 // → False! (DEFAULT — reference equality, IKKALASI HAM
         //   turli Heap manzillarida)
```

CLR darajasida — record'ning compiler-generated `Equals()` — **har
bir propertyni** **birma-bir** solishtiradi (`EqualityComparer<T>.Default`
orqali), va `GetHashCode()` — barcha propertylar asosida **kombinatsion
hash** hisoblaydi.

### 3.6 `with` expression — immutable copy bilan o'zgartirish

```csharp
var emp1 = new Employee("Orzibek", 25, 5000000);
var emp2 = emp1 with { Salary = 6000000 }; // YANGI obyekt, FAQAT Salary O'ZGARGAN

Console.WriteLine(emp1.Salary); // → 5000000 (ASL obyekt O'ZGARMAGAN!)
Console.WriteLine(emp2.Salary); // → 6000000
```

```
`with` — ICHKARIDA compiler-generated "COPY CONSTRUCTOR"ni
chaqiradi: BARCHA property'larni ASL obyektdan NUSXALAYDI, KEYIN
`with` bloki ICHIDA ko'rsatilgan property'larni O'ZGARTIRADI —
NATIJADA — YANGI, MUSTAQIL obyekt (asl obyekt IMMUTABLE bo'lgani
uchun O'ZGARMAYDI).
```

### 3.7 Deconstruction

```csharp
var emp = new Employee("Orzibek", 25, 5000000);
var (name, age, salary) = emp; // Positional record — AVTOMATIK Deconstruct metodi

Console.WriteLine(name); // → "Orzibek"
```

### 3.8 `ToString()` — avtomatik format

```csharp
var emp = new Employee("Orzibek", 25, 5000000);
Console.WriteLine(emp);
// → "Employee { FullName = Orzibek, Age = 25, Salary = 5000000 }"
```

Bu — DEBUG paytida **juda foydali** (oddiy `class`da `ToString()`
override qilinmasa — FAQAT `"Namespace.ClassName"` chiqadi).

### 3.9 Inheritance — record'dan meros olish

```csharp
public record Employee(string FullName, int Age);
public record Manager(string FullName, int Age, int TeamSize) : Employee(FullName, Age);

var manager = new Manager("Orzibek", 30, 5);
```

```
Record inheritance'da Equals() — HAM TUR (GetType() ORQALI), HAM
PROPERTYLAR bo'yicha solishtiradi:

Employee e = new Employee("X", 25);
Manager m = new Manager("X", 25, 3);
e.Equals(m) // → False! (turlar TURLICHA — Employee != Manager,
            //   HATTO umumiy propertylar BIR XIL bo'lsa ham)
```

### 3.10 DTO sifatida ishlatish — nima uchun mos

```csharp
public record EmployeeDto(int Id, string FullName, decimal Salary);
public record CreateEmployeeCommand(string FullName, decimal Salary) : IRequest<EmployeeDto>;
```

DTO/Command/Query — **o'zgarmas** ma'lumot uzatuvchi konteynerlar
— record'ning **immutability** va **value equality** xususiyatlari
BUNGA **TABIIY MOS KELADI** (masalan, unit testda `Assert.Equal(expectedDto,
actualDto)` — record bilan **to'g'ridan** ishlaydi, oddiy klassda
esa reference equality tufayli **muvaffaqiyatsiz** bo'lardi).

### 3.11 Immutability — thread safety

```
Record (init-only propertylar) — YARATILGANDAN KEYIN o'ZGARTIRIB
BO'LMAYDI — bu, TABIIY ravishda, THREAD-SAFE qiladi: bir nechta
THREAD BIR XIL record obyektiga PARALLEL murojaat qilsa ham,
HECH QANDAY "race condition" (poyga holati) YUZAGA KELMAYDI
(chunki HECH KIM uni O'ZGARTIRA OLMAYDI).
```

## 4. Kod — real ERP misolida record

```csharp
public record EmployeeDto(int Id, string FullName, decimal Salary, string DepartmentName);

public record CreateEmployeeCommand(string FullName, decimal Salary, int DepartmentId) : IRequest<EmployeeDto>;

public class CreateEmployeeHandler : IRequestHandler<CreateEmployeeCommand, EmployeeDto>
{
    public async Task<EmployeeDto> Handle(CreateEmployeeCommand cmd, CancellationToken ct)
    {
        var employee = new Employee { FullName = cmd.FullName, Salary = cmd.Salary };
        _context.Employees.Add(employee);
        await _context.SaveChangesAsync(ct);
        return new EmployeeDto(employee.Id, employee.FullName, employee.Salary, "IT");
    }
}
```

## 5. Qachon ishlatish kerak?

| Vaziyat | Yechim |
|---|---|
| DTO, Command, Query (CQRS) | `record` |
| Immutable domain qiymat (masalan Money, Address) | `record` / `record struct` |
| Mutable entity (EF Core tracking bilan) | Oddiy `class` |
| Kichik, Stack'da yashaydigan qiymat | `record struct` |
| Klassik OOP obyekt (holat o'zgaruvchan) | Oddiy `class` |

## 6. Muhim nuqtalar

- EF Core entity'lar odatda **record EMAS** — chunki Change Tracker
  **mutable** propertylarni kutadi (`init` — faqat YARATISHDA
  o'rnatilishi mumkin, keyin EF Core UPDATE qila olmaydi).
- Record inheritance'da `Equals()` — **turni HAM** tekshiradi, bu
  ba'zida **kutilmagan** natijaga olib kelishi mumkin.
- `record struct` — C# 10+ da mavjud, eskiroq loyihalarda FAQAT
  `record class` (yoki oddiy `record`) ishlatilishi mumkin.

## 7. Imtihon savollari

1. Record va oddiy class orasidagi eng muhim farq (equality
   nuqtai nazaridan) nima?
2. `with` expression qanday ishlaydi va u nima uchun immutable
   obyektlarni "o'zgartirish" imkonini beradi?
3. Positional record compiler tomonidan qanday a'zolarni avtomatik
   generatsiya qiladi?
4. Record inheritance'da `Equals()` nima uchun turni ham tekshiradi?
5. Nima uchun record DTO/CQRS Command uchun ideal tanlov hisoblanadi?
6. `record struct` oddiy `record`dan qanday farq qiladi?
7. Record'ning immutability xususiyati thread-safety bilan qanday
   bog'liq?
