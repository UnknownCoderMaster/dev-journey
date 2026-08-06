# Generics — Generic Klass, Metod, Interfeys, Constraint — Junior A

## 1. Nima? (Ta'rif)

**Generics** — turni (Type) **parametr** sifatida qabul qiluvchi
klass/metod/interfeys yaratish imkonini beruvchi mexanizm — bir xil
kodni **istalgan tur** bilan, **compile-time xavfsizligini**
yo'qotmasdan qayta ishlatish.

## 2. Nima uchun kerak?

Generics'siz — har tur uchun **alohida** klass yozish (`IntRepository`,
`StringRepository`) yoki `object` bilan ishlash (boxing, runtime
cast xatolari) kerak bo'lardi. Generics — **bitta** kod bilan
**barcha turlarni**, **xavfsiz va tez** qo'llab-quvvatlaydi.

## 3. Ichida nima sodir bo'ladi? (Mexanizm)

### 3.1 Generic klass — `Repository<T>`

```csharp
public class Repository<T> where T : class
{
    private readonly List<T> _items = new();
    public void Add(T item) => _items.Add(item);
    public T? GetFirst() => _items.FirstOrDefault();
}

var employeeRepo = new Repository<Employee>(); // T = Employee
var departmentRepo = new Repository<Department>(); // T = Department
```

### 3.2 Generic metod

```csharp
public T GetById<T>(int id) where T : IEntity, new()
{
    // ... DB'dan qidirish
    return new T();
}

var employee = GetById<Employee>(1); // T — CHAQIRISHDA aniq belgilanadi
```

### 3.3 Generic interfeys

```csharp
public interface IRepository<T> where T : class
{
    Task<T?> GetByIdAsync(int id);
    Task AddAsync(T entity);
}

public class EmployeeRepository : IRepository<Employee>
{
    public Task<Employee?> GetByIdAsync(int id) => /* ... */;
    public Task AddAsync(Employee entity) => /* ... */;
}
```

### 3.4 Type constraints — `where`

```csharp
public class Repository<T> where T : class { }              // T — REFERENCE type bo'lishi kerak
public class Calculator<T> where T : struct { }              // T — VALUE type bo'lishi kerak
public class Factory<T> where T : new() { }                  // T — parametrsiz konstruktorga EGA bo'lishi kerak
public class Service<T> where T : IEntity { }                 // T — IEntity interfeysini IMPLEMENT qiladi
public class Handler<T> where T : BaseCommand { }             // T — BaseCommand'dan MEROS OLADI

// Multiple constraints — VERGUL bilan
public class Repository<T> where T : class, IEntity, new()
{
    public T CreateNew() => new T(); // 'new()' constraint TUFAYLI mumkin
}
```

```
⚠️ MUHIM: `new T()` — FAQAT `where T : new()` constraint BO'LSA
   ISHLAYDI! Aks holda compiler XATO beradi (chunki T — ISTALGAN
   tur bo'lishi mumkin, va HAR turda parametrsiz konstruktor
   BO'LISHI KAFOLATLANMAYDI).
```

### 3.5 Covariance va Contravariance — `out T`, `in T`

```csharp
// Covariance (out) — "chiqish" pozitsiyasida, KENGROQ turga MOSLASHTIRISH mumkin
public interface IReadOnlyRepository<out T> { T GetById(int id); }

IReadOnlyRepository<Manager> managerRepo = GetManagerRepo();
IReadOnlyRepository<Employee> employeeRepo = managerRepo; // ✅ Manager IS-A Employee, RUXSAT ETILADI (out tufayli)

// Contravariance (in) — "kirish" pozitsiyasida, TORROQ turga MOSLASHTIRISH mumkin
public interface IComparer2<in T> { int Compare(T a, T b); }

IComparer2<Employee> empComparer = GetEmployeeComparer();
IComparer2<Manager> managerComparer = empComparer; // ✅ Employee comparer — Manager UCHUN ham ISHLAYDI (in tufayli)
```

```
out T — T FAQAT METOD QAYTARISH TURIDA ishlatilishi mumkin (chiqish)
in T  — T FAQAT METOD PARAMETRIDA ishlatilishi mumkin (kirish)

Bu cheklovlar — TYPE SAFETY'ni saqlash uchun MAJBURIY (aks holda
runtime'da noto'g'ri turdagi obyekt "kirib qolishi" mumkin).
```

### 3.6 Generic vs object — boxing/unboxing yo'qligi

```csharp
// ❌ object bilan — BOXING (value type'lar uchun)
ArrayList list = new ArrayList();
list.Add(42); // int → object, BOXING (Heap allocation)

// ✅ Generic bilan — BOXING YO'Q
List<int> list2 = new List<int>();
list2.Add(42); // int TO'G'RIDAN saqlanadi, boxing YO'Q
```

### 3.7 CLR'da generics — type specialization

```
Reference type (T : class):
  Barcha REFERENCE turlar (string, Employee va h.k.) — BIR XIL
  JIT-compiled kod'ni BO'LISHADI (chunki HAMMASI — 8-byte reference,
  bir xil o'lchamda)

Value type (T : struct):
  HAR bir VALUE type (int, decimal, DateTime) UCHUN — JIT ALOHIDA,
  MAXSUSLASHTIRILGAN (specialized) NATIVE KOD generatsiya qiladi
  (chunki HAR birining O'LCHAMI/LAYOUT'I TURLICHA)

List<int> va List<double> — CLR darajasida IKKI XIL, ALOHIDA
generatsiya qilingan implementatsiyaga EGA (lekin List<string>
va List<Employee> — BIR XIL implementatsiyani BO'LISHADI).
```

Bu — Java'ning "type erasure" (compile-time'da generic ma'lumot
YO'QOTILADI) yondashuvidan **TUBDAN FARQ QILADI** — C#'da generic
ma'lumot **runtime'da HAM saqlanadi** (`typeof(T)` ISHLAYDI).

### 3.8 `default(T)` — generic'da default qiymat

```csharp
public T? GetOrDefault<T>(List<T> list, int index)
    => index < list.Count ? list[index] : default(T); // default(T) yoki qisqa: default

// default(T):
//   Reference type uchun → null
//   Value type uchun     → 0, false, DateTime.MinValue va h.k.
```

### 3.9 Reflection bilan Generic — `typeof(T)`, `MakeGenericType`

```csharp
public void PrintTypeName<T>() => Console.WriteLine(typeof(T).Name);

// Runtime'da generic tur YARATISH
Type openGeneric = typeof(List<>);
Type closedGeneric = openGeneric.MakeGenericType(typeof(Employee)); // List<Employee> ni RUNTIME'da yaratish
var instance = Activator.CreateInstance(closedGeneric);
```

## 4. Kod — Generic Repository pattern

```csharp
public interface IRepository<T> where T : class, IEntity
{
    Task<T?> GetByIdAsync(int id);
    Task<List<T>> GetAllAsync();
    Task AddAsync(T entity);
}

public class Repository<T> : IRepository<T> where T : class, IEntity
{
    private readonly AppDbContext _context;
    private readonly DbSet<T> _dbSet;

    public Repository(AppDbContext context)
    {
        _context = context;
        _dbSet = context.Set<T>();
    }

    public async Task<T?> GetByIdAsync(int id) => await _dbSet.FindAsync(id);
    public async Task<List<T>> GetAllAsync() => await _dbSet.ToListAsync();
    public async Task AddAsync(T entity) => await _dbSet.AddAsync(entity);
}

public interface IEntity { int Id { get; set; } }
```

## 5. Qachon ishlatish kerak?

| Vaziyat | Yechim |
|---|---|
| Bir xil mantiq, turli turlar bilan | Generic klass/metod |
| Type safety'ni yo'qotmasdan qayta ishlatish | Generics (object emas) |
| Faqat o'qish uchun API (kengroq turga moslashtirish) | `out T` (covariance) |
| Faqat yozish uchun API | `in T` (contravariance) |
| Konstruktorsiz yaratish kerak | `where T : new()` |

## 6. Muhim nuqtalar

- Generic — **boxing/unboxing**ni yo'qotadi (value type'lar uchun) —
  bu sezilarli performance foyda beradi (masalan `List<int>` vs
  `ArrayList`).
- Covariance/Contravariance — FAQAT **interfeys** va **delegate**larda
  ishlaydi, oddiy generic klasslarda YO'Q.
- Value type generic'lar — HAR biri uchun **alohida** JIT kod
  generatsiya qilinadi — bu ozgina **assembly hajmi** oshishiga
  olib kelishi mumkin (lekin runtime tezligi uchun arzon narx).

## 7. Imtihon savollari

1. Generics boxing/unboxing muammosini qanday hal qiladi?
2. `where T : new()` constraint nima uchun kerak?
3. `out T` va `in T` (covariance/contravariance) orasidagi farq
   nima?
4. CLR'da value type va reference type generic'lar qanday farqli
   ishlov beriladi?
5. `default(T)` value type va reference type uchun nima qaytaradi?
6. C#'ning generics implementatsiyasi Java'ning "type erasure"
   yondashuvidan qanday farq qiladi?
7. `MakeGenericType` qanday vaziyatda ishlatiladi?
