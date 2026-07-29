# EF Core — Table Splitting, Entity Splitting — Middle D

## 1. Nima? (Ta'rif)

**Table Splitting** — BITTA DB jadvalini **bir nechta** C# entity
klassiga bo'lib mapping qilish. **Entity Splitting** — teskarisi,
BITTA C# entity klassini **bir nechta** DB jadvaliga bo'lib mapping
qilish.

## 2. Nima uchun kerak?

Katta jadval (masalan `Employees` — 50 ta ustunga ega, ba'zilari
kamdan-kam kerak bo'ladigan "og'ir" ma'lumot, masalan profil rasmi
binary) — HAR SO'ROVDA barcha ustunni yuklash **samarasiz**. Table
Splitting — asosiy ma'lumotni (tez-tez kerak) va qo'shimcha
ma'lumotni (kamdan-kam kerak) **alohida C# klasslar** sifatida
ifodalab, faqat kerak bo'lganda yuklash imkonini beradi.

## 3. Ichida nima sodir bo'ladi? (Mexanizm)

### 3.1 Table Splitting

```csharp
public class Employee
{
    public int Id { get; set; }
    public string FullName { get; set; } = null!;
    public EmployeeDetails Details { get; set; } = null!; // BIR XIL jadval, ALOHIDA klass
}

public class EmployeeDetails
{
    public int Id { get; set; } // Employee.Id BILAN BIR XIL (Primary Key HAM Foreign Key)
    public string? Biography { get; set; }
    public byte[]? ProfilePhoto { get; set; }
}
```

```csharp
modelBuilder.Entity<Employee>().ToTable("Employees");
modelBuilder.Entity<EmployeeDetails>().ToTable("Employees"); // BIR XIL jadval nomi!

modelBuilder.Entity<Employee>()
    .HasOne(e => e.Details)
    .WithOne()
    .HasForeignKey<EmployeeDetails>(d => d.Id);
```

```
DB'da BITTA jadval "Employees":
┌────┬───────────┬───────────┬───────────────┐
│ Id │ FullName  │ Biography │ ProfilePhoto  │
└────┴───────────┴───────────┴───────────────┘

C# da IKKITA klass: Employee (Id, FullName) va EmployeeDetails
(Id, Biography, ProfilePhoto) — BIR-BIRIGA 1:1 bog'langan
```

**Qachon kerak:** katta, "og'ir" ustunlarni (binary, uzun matn)
asosiy so'rovlardan **AJRATISH** — `Employee`ni yuklaganda
`ProfilePhoto` avtomatik KELMAYDI (faqat `Details` navigation
property orqali kerak bo'lganda `.Include()` bilan yuklanadi).

### 3.2 Owned Entity bilan farqi

```
Table Splitting — IKKALA klass HAM MUSTAQIL DbSet'ga ega bo'lishi
                    MUMKIN, ikkalasi HAM "to'liq" entity
Owned Entity     — Owned klass MUSTAQIL DbSet'ga EGA EMAS, faqat
                    egasi (masalan Employee) ORQALI mavjud bo'ladi
                    (Value Object semantikasi)
```

### 3.3 Entity Splitting (EF Core 7+)

```csharp
public class Employee
{
    public int Id { get; set; }
    public string FullName { get; set; } = null!;
    public string? Biography { get; set; }
}
```

```csharp
modelBuilder.Entity<Employee>(entity =>
{
    entity.ToTable("Employees"); // Asosiy ustunlar shu yerda
    entity.SplitToTable("EmployeeBios", tableBuilder =>
    {
        tableBuilder.Property(e => e.Biography); // Bu ustun BOSHQA jadvalda!
    });
});
```

```
BITTA C# klass "Employee" — IKKITA jadvalga BO'LINGAN:

Employees                    EmployeeBios
┌────┬───────────┐          ┌────┬───────────┐
│ Id │ FullName  │          │ Id │ Biography │
└────┴───────────┘          └────┴───────────┘

C# kodida FAQAT BITTA "Employee" klassi ko'rinadi — EF Core
ICHKARIDA ikkita jadvalga JOIN qilib, BITTA obyekt sifatida
qaytaradi.
```

**Qachon kerak:** **legacy DB** — jadval allaqachon shunday
bo'lingan (masalan tarixiy sabablarga ko'ra), lekin C# kodida buni
**bitta domain modeli** sifatida ko'rsatish kerak bo'lganda.

### 3.4 Model bulk configuration — `ConfigureConventions`

```csharp
protected override void ConfigureConventions(ModelConfigurationBuilder builder)
{
    // BARCHA string propertylar uchun DEFAULT maxlength
    builder.Properties<string>().HaveMaxLength(200);

    // BARCHA decimal propertylar uchun DEFAULT precision
    builder.Properties<decimal>().HavePrecision(18, 2);
}
```

`ConfigureConventions` — HAR entity uchun **alohida** takrorlash
o'rniga, **butun model** uchun umumiy qoida (masalan barcha string —
default 200 belgi) o'rnatish imkonini beradi.

### 3.5 Pre-convention model configuration

```
ConfigureConventions — EF Core "convention pipeline"ga QO'SHIMCHA
qoida qo'shadi, bu OnModelCreating'dan OLDIN ishga tushadi — shuning
uchun keyinchalik Fluent API orqali HAR BIR entity uchun ALOHIDA
override qilish HAM MUMKIN.
```

## 4. Kod — to'liq misol

```csharp
protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    modelBuilder.Entity<Employee>(entity =>
    {
        entity.ToTable("Employees");
        entity.SplitToTable("EmployeeArchive", t => t.Property(e => e.ArchivedNotes));
    });
}
```

## 5. Qachon ishlatish kerak?

| Vaziyat | Yechim |
|---|---|
| Katta, kamdan-kam kerak bo'ladigan ustunlarni ajratish | Table Splitting |
| Legacy DB, bo'lingan jadval, lekin BITTA domain modeli kerak | Entity Splitting |
| Butun model uchun umumiy qoida (masalan maxlength) | `ConfigureConventions` |

## 6. Muhim nuqtalar

- Table/Entity Splitting — **murakkab** konfiguratsiya, faqat aniq
  ehtiyoj (performance yoki legacy integratsiya) bo'lganda ishlatilishi
  kerak — "chunki mumkin" degan asosda ISHLATILMASIN.
- Bu texnikalar — ko'pincha **Value Object** yoki oddiy `Include()`
  bilan HAL qilinadigan muammoni murakkablashtiradigan bo'lishi
  mumkin — avval soddaroq yechimlarni ko'rib chiqish tavsiya etiladi.

## 7. Imtihon savollari

1. Table Splitting va Entity Splitting orasidagi farq nima
   (yo'nalish nuqtai nazaridan)?
2. Table Splitting Owned Entity'dan qanday farq qiladi?
3. Entity Splitting qaysi real vaziyatda (masalan legacy DB) foydali
   bo'lishi mumkin?
4. `ConfigureConventions` nima muammoni hal qiladi?
