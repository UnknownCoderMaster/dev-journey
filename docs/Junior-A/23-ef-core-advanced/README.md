# EF Core — DbSet, Keys, Backing Fields, Value Conversions — Junior A

## 1. Nima? (Ta'rif)

Bu hujjat — EF Core'ning **ilg'or** konfiguratsiya imkoniyatlarini
qamrab oladi: kalitlar (Primary/Composite/Alternate), Backing
Fields (inkapsulyatsiya), Value Conversion (DB↔C# tur o'zgartirish),
Value Comparers, Sequence, Shared-type Entity.

## 2. Nima uchun kerak?

Oddiy CRUD'dan tashqari — real ERP loyihalarda **murakkab** talablar
paydo bo'ladi: enum'ni DB'da string sifatida saqlash, composite
key, encapsulated property'lar bilan EF Core'ni **moslashtirish**.

## 3. Ichida nima sodir bo'ladi? (Mexanizm)

### 3.1 `DbSet<T>` — CRUD operatsiyalar

```csharp
_context.Employees.Add(employee);           // Added holatiga o'tadi
_context.Employees.Update(employee);          // Modified
_context.Employees.Remove(employee);          // Deleted
var emp = await _context.Employees.FindAsync(1); // Primary Key bo'yicha, TRACKING CACHE'ni AVVAL tekshiradi
```

`Find`/`FindAsync` — **avval** Change Tracker'da mavjudligini
tekshiradi (agar allaqachon yuklangan bo'lsa — **DB'ga umuman
so'rov yubormaydi**), keyin DB'ga murojaat qiladi.

### 3.2 Primary Key — `[Key]`, `HasKey()`

```csharp
public class Employee
{
    [Key] public int Id { get; set; } // Data Annotation
}

modelBuilder.Entity<Employee>().HasKey(e => e.Id); // Fluent API
```

### 3.3 Composite Key

```csharp
public class EmployeeProject
{
    public int EmployeeId { get; set; }
    public int ProjectId { get; set; }
}

modelBuilder.Entity<EmployeeProject>().HasKey(ep => new { ep.EmployeeId, ep.ProjectId });
```

```
⚠️ Composite Key — FAQAT Fluent API orqali sozlanadi, Data
   Annotation orqali IMKONSIZ (chunki [Key] BITTA propertyga
   qo'yiladi).
```

### 3.4 Alternate Keys

```csharp
modelBuilder.Entity<Employee>().HasAlternateKey(e => e.Email); // UNIQUE, LEKIN Primary Key EMAS
```

Alternate Key — **relationship**larda ishlatilishi mumkin (FK —
Primary Key'ga EMAS, Alternate Key'ga bog'lanishi mumkin) — kamdan-kam
kerak bo'ladi, odatda **Unique Index** yetarli.

### 3.5 Foreign Key va Index

```csharp
modelBuilder.Entity<Employee>()
    .HasOne(e => e.Department)
    .WithMany(d => d.Employees)
    .HasForeignKey(e => e.DepartmentId)
    .HasConstraintName("FK_Employee_Department");
```

```
EF Core — Foreign Key ustuniga AVTOMATIK indeks yaratadi (JOIN
performance uchun) — buni QO'LDA qo'shish SHART EMAS, LEKIN
ATAYLAB to'xtatish mumkin:

modelBuilder.Entity<Employee>().HasIndex(e => e.DepartmentId).IsUnique(false); // Odatiy indeks (default)
```

### 3.6 Sequence sozlamalari — `HasSequence()`, `UseSequence()`

```csharp
modelBuilder.HasSequence<int>("EmployeeIdSequence").StartsAt(1000);
modelBuilder.Entity<Employee>().Property(e => e.Id).UseSequence("EmployeeIdSequence");

// UseHiLo — batch orqali ID band qilish (yuqori parallellikda samarali)
modelBuilder.Entity<Employee>().Property(e => e.Id).UseHiLo("EmployeeHiLoSequence");
```

`UseHiLo` — bir vaqtda ko'p INSERT bo'lganda, DB'ga har safar
"keyingi ID" so'rash o'rniga, C# tomonida **oldindan band qilingan
ID diapazoni**dan foydalanadi — performance foydali (lekin ID'lar
orasida "gap" qoldirishi mumkin).

### 3.7 Backing Fields — `HasField()`

```csharp
public class Employee
{
    private string _fullName = null!; // Backing field — INKAPSULYATSIYA uchun

    public string FullName
    {
        get => _fullName;
        private set => _fullName = value.Trim(); // FAQAT klass ICHIDA o'rnatiladi, validatsiya bilan
    }

    public void Rename(string newName) => FullName = newName; // METOD orqali BOSHQARILADIGAN o'zgarish
}

modelBuilder.Entity<Employee>()
    .Property(e => e.FullName)
    .HasField("_fullName"); // EF Core — TO'G'RIDAN _fullName field'iga MUROJAAT qiladi (setter'ni CHETLAB o'tib)
```

EF Core — ODATDA **property** orqali o'qish/yozish qiladi (hatto
`private set` bo'lsa ham, Reflection orqali). `HasField()` —
EF Core'ga **to'g'ridan backing field**ga murojaat qilishni
buyuradi — DOMAIN MODEL'ning **encapsulation**ini buzmasdan
saqlash imkonini beradi.

### 3.8 Value Conversions — DB ↔ C# tur o'zgartirish

```csharp
public enum EmployeeStatus { Active, Inactive, OnLeave }

modelBuilder.Entity<Employee>()
    .Property(e => e.Status)
    .HasConversion<string>(); // Enum → DB'da STRING sifatida saqlanadi ("Active", "Inactive")

// Custom converter
modelBuilder.Entity<Employee>()
    .Property(e => e.Salary)
    .HasConversion(
        v => v.ToString("F2"),         // C# → DB (decimal → string)
        v => decimal.Parse(v));         // DB → C# (string → decimal)

// ValueConverter<TModel, TProvider> — qayta ishlatiladigan sifatida
public class EncryptedStringConverter : ValueConverter<string, string>
{
    public EncryptedStringConverter() : base(
        v => Encrypt(v),
        v => Decrypt(v)) { }
}

modelBuilder.Entity<Employee>().Property(e => e.SSN).HasConversion<EncryptedStringConverter>();
```

```
Value Conversion — DB'da SAQLANADIGAN "provider" turi bilan C#'dagi
"model" turi orasida farq bo'lganda ISHLATILADI:
  Enum → string (o'qilishi OSON DB'da)
  DateTime → Unix timestamp
  JSON obyekt → text ustun (jsonb)
  Maxfiy ma'lumot → shifrlangan qiymat
```

### 3.9 Value Comparers — Change Tracker uchun solishtirish

```csharp
modelBuilder.Entity<Employee>()
    .Property(e => e.Tags) // List<string> — DB'da JSON sifatida saqlangan
    .HasConversion(
        v => JsonSerializer.Serialize(v, (JsonSerializerOptions?)null),
        v => JsonSerializer.Deserialize<List<string>>(v, (JsonSerializerOptions?)null)!)
    .Metadata.SetValueComparer(new ValueComparer<List<string>>(
        (c1, c2) => c1!.SequenceEqual(c2!),               // TENGLIK qanday TEKSHIRILADI
        c => c.Aggregate(0, (a, v) => HashCode.Combine(a, v.GetHashCode())), // HASH qanday HISOBLANADI
        c => c.ToList()));                                  // NUSXA qanday OLINADI
```

```
⚠️ MUHIM: List<string> kabi "reference" turlar uchun — Change
   Tracker DEFAULT holda "REFERENCE equality" (bir xil obyektmi)
   TEKSHIRADI, DEEP COMPARISON (ICHIDAGI elementlar BIR XILMI)
   EMAS! Agar List'ning ICHIDAGI elementlar o'zgarsa (lekin
   REFERENCE bir xil qolsa) — EF Core buni "o'zgarish" deb
   SEZMASLIGI mumkin — Value Comparer bu muammoni HAL qiladi.
```

### 3.10 Table-valued Function, Shared-type Entity

```csharp
// Table-valued Function
modelBuilder.Entity<EmployeeStats>().ToFunction("GetEmployeeStats");

// FromSqlRaw — Table-valued function chaqirish
var stats = await _context.Set<EmployeeStats>()
    .FromSqlRaw("SELECT * FROM GetEmployeeStats({0})", departmentId)
    .ToListAsync();

// Shared-type Entity (EF Core 5+) — bitta klass, bir nechta jadval uchun
modelBuilder.SharedTypeEntity<Dictionary<string, object>>("EmployeeSettings", b =>
{
    b.Property<int>("EmployeeId");
    b.Property<string>("Key");
    b.Property<string>("Value");
});
```

## 4. Kod — to'liq misol

```csharp
public class Employee
{
    public int Id { get; set; }
    private string _fullName = null!;
    public string FullName { get => _fullName; private set => _fullName = value; }
    public EmployeeStatus Status { get; set; }

    public void UpdateName(string name) => _fullName = name.Trim();
}

modelBuilder.Entity<Employee>(entity =>
{
    entity.Property(e => e.FullName).HasField("_fullName");
    entity.Property(e => e.Status).HasConversion<string>();
});
```

## 5. Qachon ishlatish kerak?

| Vaziyat | Yechim |
|---|---|
| Ikkita ustunli PK | Composite Key |
| Enum → o'qilishi oson DB qiymat | `HasConversion<string>()` |
| Domain model encapsulation saqlash | `HasField()` |
| List/Dictionary kabi murakkab property tracking | Value Comparer |
| Yuqori parallel INSERT | `UseHiLo()` |

## 6. Muhim nuqtalar

- Value Conversion — **filter/sort** so'rovlarga ta'sir qiladi
  (masalan, string'ga aylantirilgan enum — SQL'da **matn**
  sifatida solishtiriladi, bu ba'zan **kutilmagan** natija berishi
  mumkin murakkab so'rovlarda).
- Backing Field — domain-driven design (DDD) uslubidagi entity'lar
  uchun **muhim** vosita.
- Value Comparer — **reference type** property'lar (List, Dictionary)
  uchun MUTLAQO zarur, aks holda Change Tracking **noto'g'ri**
  ishlashi mumkin.

## 7. Imtihon savollari

1. Composite Key qanday konfiguratsiya qilinadi va nima uchun
   Data Annotation orqali mumkin emas?
2. `HasField()` nima muammoni (encapsulation) hal qiladi?
3. Value Conversion nima va u qachon ishlatiladi?
4. Value Comparer nima uchun kerak — List<T> misolida tushuntiring.
5. `UseHiLo()` qanday performance foyda beradi?
6. `Find`/`FindAsync` DB'ga har doim so'rov yuboradimi?
