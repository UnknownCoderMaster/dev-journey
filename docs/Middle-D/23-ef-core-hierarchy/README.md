# EF Core — Entity Type Hierarchy (TPH, TPT, TPC) — Middle D

## 1. Nima? (Ta'rif)

**Inheritance Mapping** — C# klass ierarxiyasini (masalan `Employee`
→ `FullTimeEmployee`, `Contractor`) DB jadval(lar)iga moslashtirish
strategiyasi. Uchta asosiy yondashuv: **TPH** (Table-per-Hierarchy),
**TPT** (Table-per-Type), **TPC** (Table-per-Concrete-type).

## 2. Nima uchun kerak?

ERP tizimida — `Employee` bazaviy klass, `FullTimeEmployee`
(oylik maosh) va `Contractor` (soatlik to'lov) — turli maxsus
maydonlarga ega. Bu OOP ierarxiyani **relatsion** DB'da qanday
saqlash — inheritance mapping strategiyasi hal qiladi.

## 3. Ichida nima sodir bo'ladi? (Mexanizm)

### 3.1 Misol klasslar

```csharp
public abstract class Employee
{
    public int Id { get; set; }
    public string FullName { get; set; } = null!;
}

public class FullTimeEmployee : Employee
{
    public decimal MonthlySalary { get; set; }
}

public class Contractor : Employee
{
    public decimal HourlyRate { get; set; }
}
```

### 3.2 TPH (Table-per-Hierarchy) — DEFAULT strategiya

```csharp
// EF Core — HECH QANDAY sozlashsiz, DEFAULT holda TPH ishlatadi!
```

```
BITTA jadval — "Employees":

┌────┬───────────┬──────────────┬──────────────┬─────────────┐
│ Id │ FullName  │ Discriminator│ MonthlySalary│ HourlyRate  │
├────┼───────────┼──────────────┼──────────────┼─────────────┤
│ 1  │ Orzibek   │ FullTime...  │ 5000000      │ NULL        │
│ 2  │ Dilnoza   │ Contractor   │ NULL         │ 50000       │
└────┴───────────┴──────────────┴──────────────┴─────────────┘

Discriminator — YASHIRIN ustun, QAYSI konkret tur ekanini bildiradi
```

```csharp
// Discriminator custom nomlash
modelBuilder.Entity<Employee>()
    .HasDiscriminator<string>("EmployeeType")
    .HasValue<FullTimeEmployee>("full_time")
    .HasValue<Contractor>("contractor");
```

**Afzalliklari:** eng TEZ (JOIN kerak emas, bitta so'rov — bitta
jadval). **Kamchiliklari:** ko'p NULL ustunlar (agar sub-klasslar
ko'p maydonga ega bo'lsa), jadval "shishib" ketishi mumkin, barcha
sub-klasslar uchun BITTA ustun nomi to'qnashuvi ehtimoli.

### 3.3 TPT (Table-per-Type)

```csharp
modelBuilder.Entity<Employee>().ToTable("Employees");
modelBuilder.Entity<FullTimeEmployee>().ToTable("FullTimeEmployees");
modelBuilder.Entity<Contractor>().ToTable("Contractors");
```

```
Employees (base)          FullTimeEmployees          Contractors
┌────┬───────────┐        ┌────┬──────────────┐      ┌────┬────────────┐
│ Id │ FullName  │        │ Id │MonthlySalary │      │ Id │ HourlyRate │
├────┼───────────┤        ├────┼──────────────┤      ├────┼────────────┤
│ 1  │ Orzibek   │◄──FK───│ 1  │ 5000000      │      │    │            │
│ 2  │ Dilnoza   │◄──FK───┼────┼──────────────┼──────│ 2  │ 50000      │
└────┴───────────┘        └────┴──────────────┘      └────┴────────────┘

Har entity — BAZAVIY jadval + O'ZINING jadvali orasida JOIN qilinadi
```

**Afzalliklari:** DB darajasida **normallashgan**, NULL ustun YO'Q,
har turga xos CONSTRAINT qo'yish mumkin. **Kamchiliklari:** har
so'rovda **JOIN** kerak — TPH'dan SEKINROQ, ayniqsa chuqur ierarxiyada.

### 3.4 TPC (Table-per-Concrete-Type)

```csharp
modelBuilder.Entity<FullTimeEmployee>().ToTable("FullTimeEmployees").UseTpcMappingStrategy();
modelBuilder.Entity<Contractor>().ToTable("Contractors").UseTpcMappingStrategy();
```

```
FullTimeEmployees                    Contractors
┌────┬───────────┬──────────────┐    ┌────┬───────────┬────────────┐
│ Id │ FullName  │MonthlySalary │    │ Id │ FullName  │ HourlyRate │
├────┼───────────┼──────────────┤    ├────┼───────────┼────────────┤
│ 1  │ Orzibek   │ 5000000      │    │ 2  │ Dilnoza   │ 50000      │
└────┴───────────┴──────────────┘    └────┴───────────┴────────────┘

⚠️ BAZAVIY "Employees" jadvali UMUMAN YO'Q! Har konkret tur —
   O'ZINING BARCHA (meros olingan + o'ziga xos) ustunlariga ega,
   MUSTAQIL jadval.
```

```
⚠️ IDENTITY MUAMMOSI: Agar Id — avtomatik oshuvchi (SERIAL) bo'lsa,
   HAR JADVAL O'ZINING ketma-ketligiga ega bo'ladi — IKKI TURLI
   jadvalda BIR XIL Id (masalan ikkalasida ham Id=1) TAKRORLANISHI
   mumkin! Buni oldini olish uchun GLOBAL sequence ishlatilishi kerak.
```

**Afzalliklari:** bazaviy klass so'rovlari kerak bo'lmasa — ENG TEZ
(JOIN yo'q, TPH kabi keraksiz ustun yo'q). **Kamchiliklari:** Identity
muammosi, bazaviy tur bo'yicha UMUMIY so'rov (`_context.Set<Employee>()`)
— ICHKARIDA **UNION** orqali bajariladi (sekinroq).

### 3.5 Solishtirish jadvali

| | TPH | TPT | TPC |
|---|---|---|---|
| Jadval soni | 1 | Ierarxiya darajasi bo'yicha | Faqat konkret turlar |
| Tezlik (so'rov) | ✅ Eng tez | Sekin (JOIN) | Tez (lekin UNION agar bazaviy tur so'ralsa) |
| NULL ustunlar | Ko'p bo'lishi mumkin | Yo'q | Yo'q |
| Identity muammosi | Yo'q | Yo'q | ✅ Bor (sozlash kerak) |
| EF Core default | ✅ Ha | Yo'q (qo'lda) | Yo'q (qo'lda) |

## 4. Kod — to'liq TPH misoli

```csharp
public class AppDbContext : DbContext
{
    public DbSet<Employee> Employees { get; set; } = null!;

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.Entity<Employee>()
            .HasDiscriminator<string>("EmployeeType")
            .HasValue<FullTimeEmployee>("FullTime")
            .HasValue<Contractor>("Contractor");
    }
}

// So'rov — polimorfik, ikkala turni ham qaytaradi
var allEmployees = await _context.Employees.ToListAsync(); // FullTimeEmployee VA Contractor aralash

// Faqat bitta konkret tur
var contractors = await _context.Employees.OfType<Contractor>().ToListAsync();
```

## 5. Qachon ishlatish kerak?

| Vaziyat | Strategiya |
|---|---|
| Sub-klasslar KAM maydonga ega, tezlik muhim | TPH (default) |
| DB darajasida qat'iy normallashgan struktura kerak | TPT |
| Sub-klasslar KO'P farqli maydonga ega, bazaviy so'rov kamdan-kam | TPC |
| Oddiy, kichik ierarxiya | TPH |

## 6. Muhim nuqtalar

- TPH — DEFAULT bo'lgani uchun **hech narsa sozlamasangiz** ham
  ishlaydi, lekin Discriminator ustunini **e'tiborsiz qoldirmaslik**
  kerak (nomlashni nazorat qilish tavsiya etiladi).
- TPC — Identity (auto-increment) muammosi tufayli **kamdan-kam**
  ishlatiladi, ehtiyotkorlik talab qiladi.
- Ierarxiya **chuqur** (3+ daraja) bo'lsa — TPT performance jihatdan
  sezilarli yomonlashishi mumkin (ko'p JOIN).

## 7. Imtihon savollari

1. TPH, TPT va TPC orasidagi asosiy farqlarni jadval strukturasi
   nuqtai nazaridan tushuntiring.
2. EF Core DEFAULT holda qaysi strategiyani ishlatadi?
3. TPC'da Identity muammosi nima va u qanday yuzaga keladi?
4. Discriminator ustuni nima vazifani bajaradi?
5. Qachon TPT, qachon TPH tanlanadi — tezlik va normalizatsiya
   nuqtai nazaridan?
6. `OfType<T>()` metodi nima vazifani bajaradi?
