# Many-to-Many Relationships — Junior B

## 1. What (Nima?)

**Many-to-Many (ko'pdan-ko'pga)** — IKKI ENTITY ORASIDAGI
RELATSIYA TURI, BUNDA **BIR TOMONDAGI BIR NECHTA YOZUV, IKKINCHI
TOMONDAGI BIR NECHTA YOZUV BILAN** BOG'LANISHI MUMKIN (masalan,
BIR STUDENT — BIR NECHTA KURSGA YOZILISHI MUMKIN, VA BIR KURS —
BIR NECHTA STUDENTGA EGA BO'LISHI MUMKIN). RELYATSION DB'LARDA
BU, **JUNCTION TABLE** (bog'lovchi jadval, "join table") ORQALI
AMALGA OSHIRILADI.

## 2. Real hayot analogiyasi

**Many-to-Many — UNIVERSITETDAGI "STUDENT-KURS" RO'YXATI.**
BITTA STUDENT (Ali) — BIR NECHTA KURSGA YOZILGAN BO'LISHI
MUMKIN (Matematika, Fizika). BITTA KURS (Matematika) — KO'PLAB
STUDENTLARGA EGA (Ali, Vali, Guli). BU RELATSIYANI TO'G'RIDAN-
TO'G'RI IKKI JADVALDA IFODALAB BO'LMAYDI — SHUNING UCHUN
UNIVERSITET, **"YOZILISH RO'YXATI" (enrollment) DEGAN ALOHIDA
DAFTAR** YURITADI — HAR QATOR: "QAYSI STUDENT, QAYSI KURSGA
YOZILGAN".

## 3. Why (Nega kerak?)

RELYATSION MODEL (jadval + ustun) — **TO'G'RIDAN-TO'G'RI
"KO'P-KO'PGA" BOG'LANISHNI IFODALAY OLMAYDI** (FK — FAQAT
BITTA QIYMATNI SAQLAYDI, MASSIV EMAS). JUNCTION TABLE —
KO'P-KO'PGA RELATSIYANI, **IKKITA BIR-KO'PGA (one-to-many)
RELATSIYAGA** AYLANTIRISH ORQALI YECHADI — HAR IKKI TOMON
UCHUN HAM, ODDIY FK MEXANIZMI ISHLAYDI.

## 4. Internals (Ichki mexanizm)

### Junction Table — QANDAY QURILGAN

```sql
CREATE TABLE students (
    id SERIAL PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL
);

CREATE TABLE courses (
    id SERIAL PRIMARY KEY,
    title VARCHAR(100) NOT NULL
);

CREATE TABLE student_courses (
    student_id INT NOT NULL REFERENCES students(id),
    course_id INT NOT NULL REFERENCES courses(id),
    enrolled_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    PRIMARY KEY (student_id, course_id) -- COMPOSITE PK — takroriy yozilishni oldini oladi
);
```

```
JUNCTION TABLE — HAR IKKI TOMONGA HAM FK BILAN BOG'LANGAN,
VA ODATDA (student_id, course_id) JUFTLIGI USTIDA COMPOSITE
PRIMARY KEY (yoki UNIQUE constraint) O'RNATILADI — BU, BIR
XIL STUDENT-KURS JUFTLIGINING IKKI MARTA YOZILISHINI (DUPLIKAT
ENROLLMENT) TEXNIK JIHATDAN IMKONSIZ QILADI.
```

### EF Core — Skip Navigation (EF Core 5+, "IMPLICIT" JOIN JADVAL)

```csharp
public class Student
{
    public int Id { get; set; }
    public string FullName { get; set; } = null!;
    public List<Course> Courses { get; set; } = new(); // SKIP NAVIGATION
}

public class Course
{
    public int Id { get; set; }
    public string Title { get; set; } = null!;
    public List<Student> Students { get; set; } = new(); // SKIP NAVIGATION
}
```

```
EF Core 5+ — "Skip Navigation" MEXANIZMI ORQALI, JUNCTION
TABLE'NI, HECH QANDAY ALOHIDA C# ENTITY KLASSI YOZMASDAN,
AVTOMATIK YARATADI VA BOSHQARADI ("IMPLICIT" JOIN ENTITY).
ICHKARIDA, EF Core BARIBIR ODDIY JUNCTION TABLE'NI (masalan
"StudentCourse") YARATADI — U SHUNCHAKI C# TOMONDA "KO'RINMAS".
```

### PAYLOAD BO'LGAN Junction Table — Explicit Entity KERAK

```
Agar JUNCTION TABLE — QO'SHIMCHA MA'LUMOT (masalan
`enrolled_at`, `grade`) SAQLASHI KERAK BO'LSA — SKIP
NAVIGATION YETARLI EMAS: BUNDAY HOLDA, JUNCTION TABLE'NI
ALOHIDA, ANIQ C# ENTITY KLASSI SIFATIDA (masalan
`Enrollment`) YOZISH VA IKKITA ALOHIDA ONE-TO-MANY RELATSIYA
ORQALI BOG'LASH KERAK.
```

## 5. Code (Amaliy kod)

```csharp
// Variant 1 — Skip Navigation (EF Core 5+, oddiy holatlar uchun)
public class Student
{
    public int Id { get; set; }
    public string FullName { get; set; } = null!;
    public List<Course> Courses { get; set; } = new();
}

public class Course
{
    public int Id { get; set; }
    public string Title { get; set; } = null!;
    public List<Student> Students { get; set; } = new();
}

public class AppDbContext : DbContext
{
    public DbSet<Student> Students => Set<Student>();
    public DbSet<Course> Courses => Set<Course>();
    // EF Core, konvensiya orqali, "StudentCourse" junction jadvalini AVTOMATIK yaratadi
}

// Foydalanish
var student = await dbContext.Students.Include(s => s.Courses).FirstAsync();
student.Courses.Add(newCourse); // Yangi enrollment — junction table'ga avtomatik yoziladi
await dbContext.SaveChangesAsync();
```

```csharp
// Variant 2 — Explicit Junction Entity (qo'shimcha ma'lumot — enrolled_at, grade kerak bo'lganda)
public class Student
{
    public int Id { get; set; }
    public string FullName { get; set; } = null!;
    public List<Enrollment> Enrollments { get; set; } = new();
}

public class Course
{
    public int Id { get; set; }
    public string Title { get; set; } = null!;
    public List<Enrollment> Enrollments { get; set; } = new();
}

public class Enrollment
{
    public int StudentId { get; set; }
    public Student Student { get; set; } = null!;
    public int CourseId { get; set; }
    public Course Course { get; set; } = null!;
    public DateTime EnrolledAt { get; set; }
    public string? Grade { get; set; } // ⚡ Qo'shimcha payload — Skip Navigation'da BUNI QO'SHIB BO'LMAYDI
}

public class AppDbContext : DbContext
{
    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.Entity<Enrollment>()
            .HasKey(e => new { e.StudentId, e.CourseId }); // Composite PK

        modelBuilder.Entity<Enrollment>()
            .HasOne(e => e.Student).WithMany(s => s.Enrollments).HasForeignKey(e => e.StudentId);

        modelBuilder.Entity<Enrollment>()
            .HasOne(e => e.Course).WithMany(c => c.Enrollments).HasForeignKey(e => e.CourseId);
    }
}
```

## 6. Keng tarqalgan xatolar / noto'g'ri tushunchalar

```
❌ "Many-to-many relatsiyani, FK'ni MASSIV (array) sifatida
   saqlab AMALGA OSHIRISH MUMKIN" — TEXNIK JIHATDAN
   PostgreSQL'da MASSIV USTUN (`INT[]`) MAVJUD, LEKIN BU —
   REFERENTIAL INTEGRITY'NI (FK constraint) YO'QOTADI, JOIN'NI
   MURAKKABLASHTIRADI — RELYATSION MODELDA TAVSIYA ETILMAYDI.

❌ "Skip Navigation — HAR DOIM YETARLI, Explicit Entity HECH
   QACHON KERAK EMAS" — YO'Q! Agar JUNCTION TABLE QO'SHIMCHA
   MA'LUMOT (masalan sana, baho, status) SAQLASHI KERAK BO'LSA
   — Skip Navigation YETARLI EMAS, EXPLICIT ENTITY SHART.

❌ "Junction table'da COMPOSITE PRIMARY KEY SHART EMAS, oddiy
   `id SERIAL` YETARLI" — MUMKIN, LEKIN BU, BIR XIL
   STUDENT-KURS JUFTLIGINING BIR NECHTA MARTA YOZILISHINI
   (DUPLIKAT) TEXNIK JIHATDAN OLDINI OLMAYDI — COMPOSITE
   PK/UNIQUE constraint QO'SHISH TAVSIYA ETILADI.

❌ "EF Core'da Skip Navigation ISHLATILSA, JUNCTION TABLE
   UMUMAN MAVJUD BO'LMAYDI" — NOTO'G'RI, JUNCTION TABLE BARIBIR
   DB'DA YARATILADI — U FAQAT C# ENTITY MODELIDA "KO'RINMAS"
   (avtomatik boshqariladi).
```

## 7. Exam (Interview savollari)

**1. Many-to-many relatsiyani, RELYATSION DB'DA QANDAY AMALGA
OSHIRISH KERAK?**
JUNCTION TABLE (bog'lovchi jadval) YARATISH ORQALI — bu jadval,
IKKI TOMONGA HAM FK BILAN BOG'LANADI, VA ODATDA (tomon1_id,
tomon2_id) JUFTLIGI USTIDA COMPOSITE PRIMARY KEY O'RNATILADI.

**2. EF Core'dagi "Skip Navigation" nima, va u QACHON
YETARLI EMAS?**
Skip Navigation — EF Core 5+ da, JUNCTION TABLE'NI ALOHIDA C#
ENTITY KLASSISIZ, AVTOMATIK BOSHQARISH IMKONINI BERADI. U,
JUNCTION TABLE QO'SHIMCHA MA'LUMOT (masalan enrollment sanasi,
baho) SAQLASHI KERAK BO'LGANDA YETARLI EMAS — bunday holda,
EXPLICIT (ANIQ) ENTITY KLASSI KERAK.

**3. Junction table'da COMPOSITE PRIMARY KEY NIMA UCHUN
TAVSIYA ETILADI?**
U, BIR XIL IKKI TOMON JUFTLIGINING (masalan bitta student —
bitta kursga) IKKI MARTA YOZILISHINI (DUPLIKAT ENROLLMENT)
TEXNIK JIHATDAN IMKONSIZ QILADI — DB DARAJASIDA DATA
INTEGRITY'NI KAFOLATLAYDI.

**4. Payload (qo'shimcha ma'lumot) bilan Many-to-many
relatsiyani QANDAY MODELLASHTIRISH KERAK?**
JUNCTION TABLE'NI ALOHIDA, ANIQ C# ENTITY KLASSI (masalan
`Enrollment`) SIFATIDA YOZISH VA IKKITA ALOHIDA ONE-TO-MANY
RELATSIYA (Student→Enrollment, Course→Enrollment) ORQALI
BOG'LASH KERAK — Skip Navigation BUNGA IMKON BERMAYDI.

**5. Nima uchun FK'ni MASSIV (array) sifatida saqlash,
RELYATSION MODELDA YAXSHI AMALIYOT DEB HISOBLANMAYDI?**
Massiv ustun — REFERENTIAL INTEGRITY'NI (FK constraint orqali
kafolatlangan bog'liqlik) TA'MINLAY OLMAYDI, JOIN
OPERATSIYALARINI MURAKKABLASHTIRADI, VA INDEKSLASH/PERFORMANCE
JIHATDAN, ODDIY JUNCTION TABLE'GA NISBATAN KAMROQ SAMARALI.
