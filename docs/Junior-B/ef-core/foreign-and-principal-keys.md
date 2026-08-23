# Foreign and Principal Keys in Relationships — Junior B

## 1. What (Nima?)

**Principal Key** (asosiy kalit) — RELATSIYADA "ASOSIY"
TOMONDAGI JADVALNING, ODATDA PRIMARY KEY (yoki UNIQUE) USTUNI
— UNGA BOSHQA JADVAL "ISHORA QILADI". **Foreign Key (FK)** —
"BOG'LIQ" TOMONDAGI JADVALNING, PRINCIPAL KEYGA ISHORA
QILUVCHI USTUNI. EF Core TERMINOLOGIYASIDA: **Principal Entity**
— RELATSIYANI "BOSHQARUVCHI", MUSTAQIL YASHAY OLADIGAN TOMON;
**Dependent Entity** — FK'NI USHLAB TURUVCHI, PRINCIPAL'GA
"QARAM" TOMON.

## 2. Real hayot analogiyasi

**Principal/Dependent — UNIVERSITET VA STUDENT BILETI.**
UNIVERSITET (Principal) — O'ZI ALOHIDA, MUSTAQIL MAVJUD
BO'LISHI MUMKIN (studentlarsiz ham "universitet" tushunchasi
mavjud). STUDENT BILETI (Dependent) ESA — **MA'LUM BIR
UNIVERSITETGA ISHORA QILMASDAN, MA'NOSIZ** — BILETDA
"Universitet ID: 5" DEGAN YOZUV (FK) BOR, VA BU YOZUV,
UNIVERSITETNING (Principal) "ID: 5" QATORIGA (Principal Key)
ISHORA QILADI.

## 3. Why (Nega kerak?)

Principal/Dependent MUNOSABATI — **QAYSI TOMON QAYSI TOMONGA
"QARAM"LIGINI ANIQLASH UCHUN ZARUR**: BU, DELETE OPERATSIYASI
QANDAY XATTI-HARAKAT QILISHI KERAKLIGINI (masalan CASCADE,
RESTRICT) BELGILAYDI. Agar Principal (Universitet) O'CHIRILSA
— DEPENDENT (Student bileti) NIMA BO'LISHI KERAK? Bu SAVOLGA
JAVOB — RELATSIYA TIPI (Required/Optional) VA DELETE
BEHAVIOR ORQALI ANIQLANADI.

## 4. Internals (Ichki mexanizm)

### Required vs Optional Relationship — NULL FK

```csharp
public class Employee
{
    public int Id { get; set; }
    public int DepartmentId { get; set; }         // int (nullable EMAS) → REQUIRED relationship
    public Department Department { get; set; } = null!;
}

public class Order
{
    public int Id { get; set; }
    public int? AssignedManagerId { get; set; }     // int? (nullable) → OPTIONAL relationship
    public Employee? AssignedManager { get; set; }
}
```

```
FK PROPERTY TURI (`int` yoki `int?`) — EF Core'GA, RELATSIYA
"REQUIRED" (MAJBURIY, FK NULL BO'LMASLIGI KERAK) YOKI
"OPTIONAL" (IXTIYORIY, FK NULL BO'LISHI MUMKIN) EKANINI
AYTADI. Bu, DB DARAJASIDA, USTUN `NOT NULL` YOKI NULLABLE
BO'LIB YARATILISHIGA TO'G'RIDAN-TO'G'RI TA'SIR QILADI.
```

### Delete Behavior — `ON DELETE CASCADE` / `RESTRICT` / `SET NULL`

```sql
-- CASCADE — Principal o'chirilsa, Dependent HAM avtomatik o'chadi
ALTER TABLE employees ADD CONSTRAINT fk_department
    FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE CASCADE;

-- RESTRICT — Principal'ni o'chirishga URINISH, agar bog'liq Dependent bo'lsa, XATOLIK beradi
ALTER TABLE employees ADD CONSTRAINT fk_department
    FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE RESTRICT;

-- SET NULL — Principal o'chirilsa, Dependent'dagi FK NULL qilinadi (faqat OPTIONAL relationship uchun)
ALTER TABLE orders ADD CONSTRAINT fk_manager
    FOREIGN KEY (assigned_manager_id) REFERENCES employees(id) ON DELETE SET NULL;
```

```
EF Core, KONVENSIYA BO'YICHA: REQUIRED RELATSIYALARGA — CASCADE
DELETE'ni AVTOMATIK QO'LLAYDI (Principal o'chsa, Dependent HAM
o'chadi). OPTIONAL RELATSIYALARGA — CLIENT SET NULL (yoki DB
darajasida SET NULL) NI QO'LLAYDI. Bu XATTI-HARAKATNI, Fluent
API orqali (`.OnDelete(DeleteBehavior.Restrict)`) O'ZGARTIRISH
MUMKIN.
```

### FK Constraint — B-Tree LOOKUP orqali TEKSHIRUV

```
HAR INSERT/UPDATE'DA, FK QIYMATI KIRITILGANDA — PostgreSQL,
PRINCIPAL JADVALNING PRIMARY KEY INDEKSI (B-Tree) BO'YICHA,
"BUNDAY QIYMAT HAQIQATDA MAVJUDMI?" DEB TEKSHIRADI. AGAR
PRINCIPAL JADVALDA MOS YOZUV TOPILMASA — FOREIGN KEY VIOLATION
XATOLIGI (`23503`) QAYTARILADI — BU, DB DARAJASIDA, "YETIM"
(orphan) YOZUVLAR PAYDO BO'LISHINING OLDINI OLADI.
```

## 5. Code (Amaliy kod)

```sql
CREATE TABLE departments (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

CREATE TABLE employees (
    id SERIAL PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    department_id INT NOT NULL REFERENCES departments(id) ON DELETE RESTRICT
    -- department_id — FOREIGN KEY, departments.id — PRINCIPAL KEY
);

-- ❌ RESTRICT tufayli — bog'liq xodimlar bo'lsa, department'ni o'chirib bo'lmaydi
DELETE FROM departments WHERE id = 1; -- ERROR: update or delete violates foreign key constraint
```

```csharp
public class Department // Principal Entity
{
    public int Id { get; set; }
    public string Name { get; set; } = null!;
    public List<Employee> Employees { get; set; } = new();
}

public class Employee // Dependent Entity
{
    public int Id { get; set; }
    public string FullName { get; set; } = null!;
    public int DepartmentId { get; set; } // Foreign Key
    public Department Department { get; set; } = null!; // Navigation to Principal
}

public class AppDbContext : DbContext
{
    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.Entity<Employee>()
            .HasOne(e => e.Department)          // Dependent → Principal
            .WithMany(d => d.Employees)          // Principal → Dependents (1:N)
            .HasForeignKey(e => e.DepartmentId)  // Aniq FK property
            .OnDelete(DeleteBehavior.Restrict);  // Konvensiya default'ini (Cascade) OVERRIDE qilish
    }
}
```

```csharp
// Delete behavior — amalda qanday ishlashini ko'rish
var department = await dbContext.Departments.FindAsync(1);
dbContext.Departments.Remove(department!);
await dbContext.SaveChangesAsync();
// ⚠️ Agar Restrict bo'lsa va bog'liq Employee mavjud bo'lsa — DbUpdateException tashlanadi
```

## 6. Keng tarqalgan xatolar / noto'g'ri tushunchalar

```
❌ "Principal va Foreign Key — bir xil narsa" — YO'Q!
   Principal Key — "ASOSIY" tomondagi PK/UNIQUE. Foreign Key —
   "BOG'LIQ" tomondagi, Principal Key'ga ISHORA QILUVCHI ustun.

❌ "Barcha relatsiyalarda CASCADE DELETE eng xavfsiz variant" —
   XAVFLI! CASCADE — ZANJIR REAKSIYA ORQALI, KUTILMAGANDA, KO'P
   MIQDORDA BOG'LIQ YOZUVLARNI O'CHIRIB YUBORISHI MUMKIN
   (masalan, department o'chirilsa — BARCHA employeelar HAM
   o'chadi!) — REQUIRED RELATSIYALARDA, KO'PINCHA RESTRICT
   YOKI ANIQ BUSINESS LOGIC (masalan employeelarni boshqa
   department'ga ko'chirish) TAVSIYA ETILADI.

❌ "SET NULL — HAR QANDAY RELATSIYADA ISHLAYDI" — YO'Q! SET
   NULL — FAQAT OPTIONAL (FK nullable) RELATSIYALARDA ISHLAYDI
   — REQUIRED RELATSIYADA (FK NOT NULL) — SET NULL FIZIK
   JIHATDAN IMKONSIZ (NOT NULL constraint buziladi).

❌ "EF Core, HAR DOIM, Foreign Key'ni AVTOMATIK ANIQLAYDI —
   Fluent API SHART EMAS" — KO'PINCHA TO'G'RI (konvensiya
   ishlaydi), LEKIN MURAKKAB HOLATLARDA (bir nechta FK — bir
   xil Principal'ga, YOKI DELETE BEHAVIOR'NI O'ZGARTIRISH
   kerak bo'lganda) — Fluent API orqali ANIQ KO'RSATISH SHART.
```

## 7. Exam (Interview savollari)

**1. Principal Key va Foreign Key orasidagi FARQ nima?**
Principal Key — RELATSIYADA "ASOSIY" TOMONDAGI JADVALNING
PRIMARY KEY (yoki UNIQUE) USTUNI. Foreign Key — "BOG'LIQ"
TOMONDAGI JADVALNING, PRINCIPAL KEYGA ISHORA QILUVCHI USTUNI.

**2. Required va Optional relationship orasidagi FARQ, EF
Core'da QANDAY ANIQLANADI?**
FK PROPERTY TURI ORQALI: `int` (nullable EMAS) — REQUIRED
(FK NULL BO'LMASLIGI SHART). `int?` (nullable) — OPTIONAL
(FK NULL BO'LISHI MUMKIN).

**3. `ON DELETE CASCADE`, `RESTRICT`, va `SET NULL` orasidagi
FARQNI TUSHUNTIRING.**
CASCADE — Principal o'chirilsa, BOG'LIQ Dependent yozuvlar HAM
AVTOMATIK O'CHADI. RESTRICT — Principal'ni o'chirishga
URINISH, AGAR BOG'LIQ Dependent yozuvlar bo'lsa, XATOLIK
BERADI (o'chirish BLOKLANADI). SET NULL — Principal
o'chirilsa, Dependent'dagi FK QIYMATI NULL QILINADI (faqat
OPTIONAL relationship uchun ishlaydi).

**4. Nima uchun CASCADE DELETE, REQUIRED RELATSIYALARDA
(masalan Department→Employee) XAVFLI BO'LISHI MUMKIN?**
Chunki U, ZANJIR REAKSIYA ORQALI, DASTURCHI KUTMAGAN
MIQDORDA BOG'LIQ YOZUVLARNI (masalan barcha xodimlarni)
AVTOMATIK O'CHIRIB YUBORISHI MUMKIN — REAL LOYIHALARDA,
BUNDAY MA'LUMOT YO'QOTILISHI ODATDA, ANIQ BUSINESS LOGIC
(masalan employeelarni boshqa department'ga ko'chirish yoki
XATOLIK QAYTARISH) BILAN ALMASHTIRILADI.

**5. FK CONSTRAINT, INSERT/UPDATE VAQTIDA, ICHKARIDA QANDAY
TEKSHIRILADI?**
PostgreSQL, PRINCIPAL JADVALNING PRIMARY KEY INDEKSI (B-Tree)
BO'YICHA, KIRITILAYOTGAN FK QIYMATI HAQIQATDA MAVJUDLIGINI
TEKSHIRADI. Agar MOS YOZUV TOPILMASA — Foreign Key Violation
XATOLIGI (`23503`) QAYTARILADI, "YETIM" YOZUVLAR YARATILISHI
OLDINI OLINADI.
