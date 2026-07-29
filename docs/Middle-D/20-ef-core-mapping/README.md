# EF Core — Mapping (Conventions, Annotations, Fluent API) — Middle D

## 1. Nima? (Ta'rif)

**Mapping** — C# klasslarini DB jadvallariga **moslashtirish**
jarayoni. EF Core — buni 3 usulda amalga oshiradi: **Convention**
(avtomatik qoidalar), **Data Annotations** (atributlar), **Fluent
API** (kod orqali, `OnModelCreating`).

## 2. Nima uchun kerak?

EF Core — C# klassidan **avtomatik** jadval strukturasini xulosa
qilishi mumkin (Convention), lekin har doim bu yetarli emas
(masalan, ustun nomi/uzunligi, indeks, murakkab relationship'lar) —
shu holatlarda Annotations yoki Fluent API kerak bo'ladi.

## 3. Ichida nima sodir bo'ladi? (Mexanizm)

### 3.1 Convention-based mapping

```csharp
public class Employee
{
    public int Id { get; set; }              // "Id" yoki "{ClassName}Id" → AVTOMATIK Primary Key
    public string FullName { get; set; } = null!; // string → nvarchar(max) (SQL Server) / text (PostgreSQL)
    public int DepartmentId { get; set; }     // "{Property}Id" → AVTOMATIK Foreign Key deb XULOSA qilinadi
    public Department Department { get; set; } = null!; // Navigation property
}
```

EF Core — klass nomi (`Employee` → jadval `Employees`, ko'plik),
property nomi va turi asosida **avtomatik** ustun/tur/kalit
belgilaydi.

### 3.2 Data Annotations

```csharp
[Table("employees")]
public class Employee
{
    [Key]
    public int Id { get; set; }

    [Column("full_name")]
    [Required]
    [MaxLength(100)]
    public string FullName { get; set; } = null!;

    [Column(TypeName = "decimal(15,2)")]
    public decimal Salary { get; set; }

    [ForeignKey(nameof(Department))]
    public int DepartmentId { get; set; }
    public Department Department { get; set; } = null!;
}
```

### 3.3 Fluent API — `OnModelCreating`

```csharp
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    modelBuilder.Entity<Employee>(entity =>
    {
        entity.ToTable("employees");
        entity.HasKey(e => e.Id);
        entity.Property(e => e.FullName).HasColumnName("full_name").IsRequired().HasMaxLength(100);
        entity.Property(e => e.Salary).HasColumnType("decimal(15,2)");

        entity.HasOne(e => e.Department)
              .WithMany(d => d.Employees)
              .HasForeignKey(e => e.DepartmentId)
              .OnDelete(DeleteBehavior.Restrict);
    });
}
```

### 3.4 Qaysi birini qachon ishlatish

```
Convention   — oddiy, standart holatlar uchun YETARLI
Annotations  — TEZKOR, klass ICHIDA ko'rinadi, lekin CHEKLANGAN
               (murakkab relationship/composite key — MUMKIN EMAS)
Fluent API   — ENG KUCHLI, HAMMA narsani sozlash mumkin, lekin
               ALOHIDA joyda (klassdan AJRALGAN)

⚠️ Fluent API — Annotations'dan USTUN turadi (agar IKKALASI HAM
   bir xil narsani belgilasa, ZIDDIYAT bo'lsa — Fluent API g'olib
   chiqadi)
```

### 3.5 Relationships — One-to-One, One-to-Many, Many-to-Many

```csharp
// One-to-Many (Department → Employees)
modelBuilder.Entity<Employee>()
    .HasOne(e => e.Department)
    .WithMany(d => d.Employees)
    .HasForeignKey(e => e.DepartmentId);

// One-to-One (Employee → EmployeeProfile)
modelBuilder.Entity<Employee>()
    .HasOne(e => e.Profile)
    .WithOne(p => p.Employee)
    .HasForeignKey<EmployeeProfile>(p => p.EmployeeId);

// Many-to-Many (EF Core 5+, JOIN jadval AVTOMATIK yaratiladi)
modelBuilder.Entity<Employee>()
    .HasMany(e => e.Projects)
    .WithMany(p => p.Employees); // Ichkarida "EmployeeProject" jadval yaratiladi

// Many-to-Many — EXPLICIT join entity bilan (qo'shimcha maydon kerak bo'lsa)
public class EmployeeProject
{
    public int EmployeeId { get; set; }
    public int ProjectId { get; set; }
    public DateTime AssignedAt { get; set; } // Qo'shimcha maydon
}
modelBuilder.Entity<EmployeeProject>().HasKey(ep => new { ep.EmployeeId, ep.ProjectId });
```

### 3.6 Foreign key — explicit vs shadow

```csharp
// Explicit — DepartmentId C# klassida KO'RINADI
public int DepartmentId { get; set; }

// Shadow property — DB'da BOR, lekin C# klassida YO'Q (EF Core ICHKARIDA boshqaradi)
modelBuilder.Entity<Employee>()
    .Property<int>("DepartmentId"); // Faqat model'da e'lon qilinadi, klassda YO'Q
```

Shadow properties — legacy DB bilan ishlashda yoki auditing
(`CreatedBy`, kabi C# domenida ko'rinishi shart bo'lmagan maydonlar)
uchun foydali.

### 3.7 Owned Entities va Value Objects

```csharp
public class Employee
{
    public Address HomeAddress { get; set; } = null!; // Value Object — o'zining Id'si YO'Q
}

public class Address // Owned type — MUSTAQIL entity EMAS
{
    public string City { get; set; } = null!;
    public string Street { get; set; } = null!;
}

modelBuilder.Entity<Employee>().OwnsOne(e => e.HomeAddress);
```

```
Owned Entity — Employee jadvalida "HomeAddress_City",
"HomeAddress_Street" ustunlari sifatida SAQLANADI (ALOHIDA jadval
EMAS) — DDD'dagi "Value Object" konsepsiyasiga mos keladi (Address
— o'z-o'zicha mavjud bo'lmaydi, FAQAT Employee'ga tegishli).
```

### 3.8 `ApplyConfigurationsFromAssembly` — `IEntityTypeConfiguration`

```csharp
public class EmployeeConfiguration : IEntityTypeConfiguration<Employee>
{
    public void Configure(EntityTypeBuilder<Employee> builder)
    {
        builder.ToTable("employees");
        builder.Property(e => e.FullName).HasMaxLength(100).IsRequired();
        builder.HasOne(e => e.Department).WithMany(d => d.Employees).HasForeignKey(e => e.DepartmentId);
    }
}

// DbContext'da — HAMMA konfiguratsiyalarni AVTOMATIK topib qo'llaydi
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    modelBuilder.ApplyConfigurationsFromAssembly(typeof(AppDbContext).Assembly);
}
```

Bu pattern — `OnModelCreating`ning **shishib ketishini** oldini
oladi — har entity uchun **alohida fayl** (Single Responsibility
Principle'ga mos).

## 4. Kod — to'liq misol

```csharp
public class EmployeeConfiguration : IEntityTypeConfiguration<Employee>
{
    public void Configure(EntityTypeBuilder<Employee> builder)
    {
        builder.ToTable("employees");
        builder.HasKey(e => e.Id);
        builder.Property(e => e.FullName).HasColumnName("full_name").HasMaxLength(100).IsRequired();
        builder.Property(e => e.Salary).HasColumnType("decimal(15,2)");
        builder.HasIndex(e => e.Email).IsUnique();

        builder.HasOne(e => e.Department).WithMany(d => d.Employees)
            .HasForeignKey(e => e.DepartmentId).OnDelete(DeleteBehavior.Restrict);
    }
}
```

## 5. Qachon ishlatish kerak?

| Vaziyat | Yechim |
|---|---|
| Oddiy, standart entity | Convention (hech narsa yozmasdan) |
| Tez, kichik sozlash (masalan MaxLength) | Data Annotations |
| Murakkab relationship, indeks, composite key | Fluent API + `IEntityTypeConfiguration` |
| Katta loyiha, ko'p entity | HAR DOIM `IEntityTypeConfiguration` (tartib uchun) |

## 6. Muhim nuqtalar

- Fluent API — Annotations bilan ZIDDIYATLI bo'lsa, Fluent API
  ustun turadi.
- Owned Entity — Value Object'lar uchun ideal, lekin ular O'ZINING
  Id'siga ega EMAS (Employee'dan MUSTAQIL mavjud bo'la olmaydi).
- `ApplyConfigurationsFromAssembly` — katta loyihalarda `OnModelCreating`
  metodini **toza** saqlashning STANDART usuli.

## 7. Imtihon savollari

1. Convention, Data Annotations va Fluent API orasidagi ustuvorlik
   tartibi qanday?
2. One-to-Many va Many-to-Many relationship qanday Fluent API bilan
   sozlanadi?
3. Shadow Property nima va u qachon foydali?
4. Owned Entity nima va u DDD'dagi Value Object konsepsiyasi bilan
   qanday bog'liq?
5. `IEntityTypeConfiguration<T>` va `ApplyConfigurationsFromAssembly`
   nima muammoni hal qiladi?
6. Explicit va Shadow Foreign Key orasidagi farq nima?
