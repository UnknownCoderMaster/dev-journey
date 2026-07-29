# N+1 Problem va Yechimi — Middle D

## 1. Nima? (Ta'rif)

**N+1 Problem** — 1 ta so'rov bilan **N** ta yozuv olingandan keyin,
har bir yozuv uchun **bog'liq ma'lumotni** olish uchun **QO'SHIMCHA
N ta** alohida so'rov yuborilishi (jami — 1 + N ta so'rov, o'rniga
1-2 ta yetarli bo'lgan holatda).

## 2. Nima uchun kerak? (bu yerda: qanday muammo)

```csharp
var employees = await _context.Employees.ToListAsync(); // 1-so'rov: 1000 ta xodim
foreach (var e in employees)
    Console.WriteLine(e.Department.Name); // Lazy loading YOQILGAN bo'lsa — HAR biri uchun 1 SO'ROV!
```

```
1 + 1000 = 1001 ta SQL so'rov yuboriladi (o'rniga 1 ta JOIN so'rov
yetarli bo'lardi)! Har SQL so'rov — tarmoq round-trip (odatda 1-5ms)
— 1000 ta so'rov = 1-5 SONIYA kutish (o'rniga 10-20ms).
```

## 3. Ichida nima sodir bo'ladi? (Mexanizm)

### 3.1 EF Core'da N+1 — lazy loading sabab

```csharp
// Lazy Loading yoqish (Microsoft.EntityFrameworkCore.Proxies)
public class Employee
{
    public virtual Department Department { get; set; } = null!; // "virtual" — LAZY LOADING PROXY yaratiladi
}
```

```
Employee YUKLANGANDA — Department HALI YUKLANMAGAN (NULL emas,
lekin "proxy" holatida). e.Department.Name CHAQIRILGANDA —
ICHKARIDA AVTOMATIK, YASHIRIN SQL so'rov YUBORILADI — bu "YASHIRIN"
xatti-harakat, kod o'quvchisi buni SEZMASLIGI MUMKIN!
```

### 3.2 Eager Loading — `Include`, `ThenInclude`

```csharp
var employees = await _context.Employees
    .Include(e => e.Department)             // 1-DARAJA bog'liqlik
        .ThenInclude(d => d.Manager)          // 2-DARAJA bog'liqlik (Department ICHIDAGI Manager)
    .ToListAsync();
// FAQAT 1 SO'ROV (JOIN orqali) — barcha ma'lumot BIRGA keladi
```

### 3.3 Explicit Loading

```csharp
var employee = await _context.Employees.FindAsync(1);
await _context.Entry(employee).Reference(e => e.Department).LoadAsync(); // FAQAT KERAK BO'LGANDA yuklash

await _context.Entry(department).Collection(d => d.Employees).LoadAsync(); // Collection uchun
```

Explicit Loading — **shartli** ravishda (masalan, faqat ma'lum
holatda) bog'liq ma'lumotni yuklash kerak bo'lganda ishlatiladi.

### 3.4 Projection — faqat kerakli maydonlar

```csharp
// ❌ Butun entity + Include — KO'P ma'lumot yuklanadi (kerak bo'lmagan maydonlar HAM)
var employees = await _context.Employees.Include(e => e.Department).ToListAsync();

// ✅ Projection — FAQAT kerakli maydonlar, N+1 HAM YO'Q!
var employees = await _context.Employees
    .Select(e => new EmployeeDto
    {
        FullName = e.FullName,
        DepartmentName = e.Department.Name // EF Core BUNI AVTOMATIK JOIN qiladi!
    })
    .ToListAsync();
```

Projection (`Select`) — EF Core **avtomatik ravishda** kerakli
JOIN'larni yasaydi, **hech qanday N+1 yo'q**, va faqat **kerakli**
ustunlar SQL'da so'raladi (kamroq trafik).

### 3.5 Split Queries — `AsSplitQuery`

```csharp
var departments = await _context.Departments
    .Include(d => d.Employees)
    .Include(d => d.Projects)
    .AsSplitQuery() // BITTA katta JOIN o'rniga — BIR NECHTA alohida so'rov
    .ToListAsync();
```

```
❌ Bitta JOIN (default) — agar Department'ning KO'P Employees VA
   KO'P Projects'i bo'lsa — natija "Cartesian Explosion" (Employees
   × Projects — KO'PAYTIRILGAN qatorlar soni) beradi, KO'P DUPLICATE
   ma'lumot tarmoqdan o'tadi!

✅ AsSplitQuery — HAR Include UCHUN ALOHIDA SQL so'rov (lekin N+1
   EMAS — FAQAT navigation SONI CHOG'IDA, YOZUVLAR SONI CHOG'IDA
   EMAS)
```

### 3.6 Dapper'da N+1 — multi-mapping

```csharp
// ❌ N+1 — HAR employee UCHUN alohida so'rov
var employees = await connection.QueryAsync<Employee>("SELECT * FROM employees");
foreach (var e in employees)
    e.Department = await connection.QuerySingleAsync<Department>(
        "SELECT * FROM departments WHERE id = @id", new { id = e.DepartmentId }); // N+1!

// ✅ Multi-mapping — BITTA JOIN so'rov, Dapper AVTOMATIK ikkiga AJRATADI
var sql = "SELECT e.*, d.* FROM employees e JOIN departments d ON e.department_id = d.id";
var employees2 = await connection.QueryAsync<Employee, Department, Employee>(
    sql,
    (employee, department) => { employee.Department = department; return employee; },
    splitOn: "id" // Qaysi ustundan "Department" boshlanishini bildiradi
);
```

### 3.7 N+1 aniqlash — logging orqali

```
LogTo() yoki Serilog orqali BARCHA SQL so'rovlarni yozib, BIR XIL
NAQSHDAGI (bir xil SQL, faqat parametr farq qiladigan) so'rovlar
KETMA-KET KO'P MARTA takrorlanayotganini KUZATISH — bu N+1 ning
ANIQ BELGISI.
```

### 3.8 Real ERP misolida N+1 va yechimi

```csharp
// ❌ N+1 — 500 ta xodim uchun 501 ta so'rov
[HttpGet("report")]
public async Task<IActionResult> GetSalaryReport()
{
    var employees = await _context.Employees.ToListAsync();
    var report = employees.Select(e => new
    {
        e.FullName,
        DepartmentName = e.Department.Name // Lazy loading — HAR BIRIDA alohida so'rov!
    });
    return Ok(report);
}

// ✅ Yechim — Projection bilan BITTA so'rov
[HttpGet("report")]
public async Task<IActionResult> GetSalaryReport()
{
    var report = await _context.Employees
        .Select(e => new { e.FullName, DepartmentName = e.Department.Name })
        .ToListAsync(); // FAQAT 1 SO'ROV, JOIN orqali
    return Ok(report);
}
```

## 4. Kod — to'liq solishtirma

```csharp
// N+1 (SEKIN)
var employees = await _context.Employees.ToListAsync();
foreach (var e in employees) _ = e.Department.Name;

// Eager Loading (TEZ)
var employees2 = await _context.Employees.Include(e => e.Department).ToListAsync();

// Projection (ENG TEZ, ENG KAM TRAFIK)
var dtos = await _context.Employees
    .Select(e => new { e.FullName, DeptName = e.Department.Name })
    .ToListAsync();
```

## 5. Qachon ishlatish kerak?

| Vaziyat | Yechim |
|---|---|
| Faqat bir necha maydon kerak (API DTO) | Projection (`Select`) |
| To'liq Entity kerak, bog'liq ma'lumot bilan | `Include`/`ThenInclude` |
| Shartli, kamdan-kam kerak bo'ladigan bog'liqlik | Explicit Loading |
| Bir nechta "1-ko'p" bog'liqlik, katta hajm | `AsSplitQuery` |
| Dapper bilan JOIN natijasi | Multi-mapping |

## 6. Muhim nuqtalar

- Lazy Loading — **QULAY**, lekin N+1'ning **ENG KO'P** sababi —
  ko'p jamoalar uni **butunlay o'chirib qo'yishni** tavsiya qiladi.
- Projection — N+1'ni HAL QILISH BILAN BIRGA, tarmoq trafigini HAM
  kamaytiradi (faqat kerakli ustunlar).
- N+1 — production'da **sekin API** shikoyatlarining ENG KO'P
  uchraydigan sababi, har doim birinchi tekshiriladigan narsa
  bo'lishi kerak.

## 7. Imtihon savollari

1. N+1 muammosi nima va u qanday sodir bo'ladi (misol bilan)?
2. Lazy Loading N+1 muammosiga qanday sabab bo'ladi?
3. `Include` va Projection (`Select`) orasidagi farqni performance
   nuqtai nazaridan tushuntiring.
4. `AsSplitQuery` qanday muammoni (Cartesian Explosion) hal qiladi?
5. Dapper'da N+1 qanday yuzaga keladi va Multi-mapping bu muammoni
   qanday hal qiladi?
6. N+1 muammosini production loglardan qanday aniqlash mumkin?
