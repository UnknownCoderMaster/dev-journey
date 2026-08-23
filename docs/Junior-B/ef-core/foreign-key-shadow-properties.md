# Foreign Key Shadow Properties — Junior B

## 1. What (Nima?)

**Shadow Property** — EF Core MODELIDA MAVJUD, LEKIN C# ENTITY
KLASSIDA **HECH QANDAY PROPERTY SIFATIDA YOZILMAGAN** USTUN —
EF Core, UNI **ICHKI HOLATIDA (metadata) "SOYA" (shadow)
SIFATIDA KUZATIB BORADI** VA DB'GA SO'ROV YUBORGANDA ISHLATADI.
Eng KENG TARQALGAN HOLAT — **FOREIGN KEY SHADOW PROPERTY**:
NAVIGATION PROPERTY (masalan `Department`) BOR, LEKIN MOS FK
PROPERTY (`DepartmentId`) C# KLASSIDA YO'Q BO'LGANDA, EF Core
UNI O'ZI, "KO'RINMAS" HOLDA YARATADI.

## 2. Real hayot analogiyasi

**Shadow Property — RESTORAN OSHXONASIDAGI "ICHKI JURNAL"
YOZUVI.** Mijoz (dasturchi) — MENYUDA (Entity klassida) FAQAT
"TAOM NOMI VA MIJOZ" NI KO'RADI. LEKIN OSHXONA (EF Core) —
ICHKARIDA, O'Z JURNALIDA (metadata), "QAYSI STOL RAQAMIGA
TEGISHLI" DEGAN QO'SHIMCHA YOZUVNI HAM YURITADI — MIJOZ BUNI
KO'RMAYDI, LEKIN OSHXONA BU MA'LUMOTNI TAOMNI TO'G'RI STOLGA
YETKAZISH UCHUN ICHKARIDA ISHLATADI.

## 3. Why (Nega kerak?)

Ba'zan, DIZAYN QARORI SIFATIDA, **C# ENTITY KLASSINI "TOZA"
SAQLASH** (faqat DOMAIN'GA TEGISHLI PROPERTYLAR, DB-SPECIFIC
FK'siz) — YAXSHI AMALIYOT DEB HISOBLANADI. Ba'zan ESA, FK —
**BOSHQA ASSEMBLY'DA JOYLASHGAN, O'ZGARTIRA OLMAYDIGAN ENTITY**
BILAN ISHLASHDA KERAK BO'LADI. Shadow Property — EF Core'GA,
C# KLASSNI O'ZGARTIRMASDAN, RELATSIYANI TO'LIQ MODELLASHTIRISH
IMKONINI BERADI.

## 4. Internals (Ichki mexanizm)

### EF Core Shadow Property'ni QANDAY AVTOMATIK ANIQLAYDI

```csharp
public class Employee
{
    public int Id { get; set; }
    public string FullName { get; set; } = null!;
    public Department Department { get; set; } = null!; // Navigation property — LEKIN DepartmentId YO'Q!
}

public class Department
{
    public int Id { get; set; }
    public string Name { get; set; } = null!;
}
```

```
EF Core CONVENTION (KONVENSIYA) MEXANIZMI — MODEL QURILISH
BOSQICHIDA (OnModelCreating), `Department` NAVIGATION
PROPERTYNI KO'RIB, MOS FK PROPERTY C# KLASSDA YO'QLIGINI
ANIQLAYDI — VA O'ZI, ICHKI METADATA'GA, "DepartmentId" NOMLI
SHADOW PROPERTY QO'SHADI (nom — konvensiya bo'yicha:
{NavigationPropertyName}{PrincipalKeyPropertyName}).

MIGRATSIYA YARATILGANDA — jadvalda HAQIQIY "DepartmentId" USTUNI
PAYDO BO'LADI — LEKIN C# ENTITY KLASSIDA BU PROPERTY UMUMAN
KO'RINMAYDI.
```

### `ChangeTracker` ORQALI Shadow Property QIYMATINI O'QISH

```csharp
var employee = await dbContext.Employees.Include(e => e.Department).FirstAsync();
var shadowFkValue = dbContext.Entry(employee).Property("DepartmentId").CurrentValue;
```

```
EF Core'ning CHANGE TRACKER'I (o'zgarishlarni kuzatuvchi ichki
mexanizm) — SHADOW PROPERTY QIYMATLARINI HAM, ODDIY PROPERTY
KABI, "EntityEntry" OBYEKTI ORQALI SAQLAYDI VA KUZATIB BORADI —
FAQAT ULARGA C# KOD ORQALI TO'G'RIDAN-TO'G'RI (`employee.
DepartmentId`) MUROJAAT QILIB BO'LMAYDI, `.Property("nomi")`
REFLECTION-LIKE API ORQALI MUROJAAT QILINADI.
```

### LINQ SO'ROVLARIDA Shadow FK ISHLATISH

```csharp
var employees = await dbContext.Employees
    .Where(e => EF.Property<int>(e, "DepartmentId") == 5)
    .ToListAsync();
```

```
`EF.Property<T>()` — MAXSUS EF Core METODI (FAQAT LINQ
IFODALARI ICHIDA MA'NOGA EGA, EXPRESSION TREE'GA TARJIMA
QILINADI) — SHADOW PROPERTYLARGA, C# KOD ORQALI KIRISH
IMKONI BO'LMASA-DA, SQL SO'ROVLARDA FOYDALANISHGA IMKON
BERADI.
```

## 5. Code (Amaliy kod)

```csharp
// Shadow Property — Konvensiya orqali AVTOMATIK (yuqoridagi Employee/Department misoli)
// Migratsiya yaratilganda, EF Core avtomatik "DepartmentId" ustunini qo'shadi

// Shadow Property'ni ONGLI RAVISHDA, Fluent API orqali ANIQ BELGILASH
public class AppDbContext : DbContext
{
    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.Entity<Employee>()
            .Property<int>("DepartmentId"); // ONGLI ravishda shadow property e'lon qilish

        modelBuilder.Entity<Employee>()
            .HasOne(e => e.Department)
            .WithMany()
            .HasForeignKey("DepartmentId"); // String nomi bilan — shadow FK ekanini bildiradi
    }
}

// Shadow property qiymatini o'qish/yozish — Entry() orqali
var employee = await dbContext.Employees.FirstAsync();
dbContext.Entry(employee).Property("DepartmentId").CurrentValue = 3;
await dbContext.SaveChangesAsync();

// LINQ so'rovida shadow FK bo'yicha filtrlash
var itDepartmentEmployees = await dbContext.Employees
    .Where(e => EF.Property<int>(e, "DepartmentId") == 5)
    .ToListAsync();
```

```csharp
// Alternativ — ODATDA TAVSIYA QILINADIGAN YECHIM: FK'ni ANIQ, ODDIY PROPERTY qilib yozish
public class Employee
{
    public int Id { get; set; }
    public string FullName { get; set; } = null!;
    public int DepartmentId { get; set; }       // ✅ ANIQ, KO'RINADIGAN FK — shadow'dan KO'RA TAVSIYA ETILADI
    public Department Department { get; set; } = null!;
}
// SABAB: kodni o'qish, filtrlash (e.DepartmentId == 5), va debug qilish — ANCHA OSON
```

## 6. Keng tarqalgan xatolar / noto'g'ri tushunchalar

```
❌ "Shadow Property — FAQAT ONGLI RAVISHDA, Fluent API orqali
   YARATILADI" — YO'Q! EF Core, KO'PINCHA, KONVENSIYA ORQALI
   (Navigation property bor, LEKIN mos FK property YO'Q bo'lsa)
   AVTOMATIK RAVISHDA SHADOW PROPERTY YARATADI — DASTURCHI
   BUNI SEZMASLIGI MUMKIN!

❌ "Shadow Property'ga oddiy C# kod orqali (masalan
   employee.DepartmentId) MUROJAAT QILISH MUMKIN" — YO'Q, BU
   COMPILE ERROR BERADI (property C# klassida UMUMAN YO'Q) —
   FAQAT `Entry().Property("nomi")` YOKI `EF.Property<T>()`
   ORQALI MUROJAAT QILINADI.

❌ "Shadow Property ISHLATISH — HAR DOIM YAXSHI AMALIYOT
   (kodni 'toza' saqlash uchun)" — KO'PINCHA, ANIQ, ODDIY C#
   PROPERTY (masalan `DepartmentId`) YOZISH TAVSIYA ETILADI —
   Shadow Property — DEBUG QILISH, TEST YOZISH, VA SO'ROV
   YOZISHNI MURAKKABLASHTIRADI.

❌ "Migratsiyada Shadow Property'ni KO'RISH MUMKIN EMAS" — YO'Q,
   MIGRATSIYA FAYLIDA (masalan `migrationBuilder.AddColumn`) —
   ODDIY USTUN KABI TO'LIQ KO'RINADI, FARQ — FAQAT C# ENTITY
   KLASSIDA (u yerda umuman YO'Q).
```

## 7. Exam (Interview savollari)

**1. Shadow Property nima, va u ODDIY (oddiy) PROPERTYDAN
NIMASI BILAN FARQ QILADI?**
Shadow Property — DB'da JADVAL USTUNI SIFATIDA MAVJUD, LEKIN
C# ENTITY KLASSIDA HECH QANDAY PROPERTY SIFATIDA YOZILMAGAN —
EF Core, UNI FAQAT O'ZINING ICHKI METADATASIDA KUZATIB BORADI.
Oddiy property — HAM C# KLASSIDA, HAM DB'DA MAVJUD.

**2. EF Core, QACHON, AVTOMATIK RAVISHDA (KONVENSIYA ORQALI)
FOREIGN KEY SHADOW PROPERTY YARATADI?**
Entity'da NAVIGATION PROPERTY (masalan `Department`) BOR,
LEKIN MOS, ANIQ FK PROPERTY (`DepartmentId`) C# KLASSIDA YO'Q
BO'LGANDA — EF Core, MODEL QURISH BOSQICHIDA, AVTOMATIK
RAVISHDA SHADOW FK PROPERTY QO'SHADI.

**3. Shadow Property QIYMATIGA, C# KODDAN QANDAY MUROJAAT
QILINADI?**
`dbContext.Entry(entity).Property("PropertyName").CurrentValue`
ORQALI (O'QISH/YOZISH UCHUN), yoki LINQ SO'ROVLARDA
`EF.Property<T>(entity, "PropertyName")` MAXSUS METODI ORQALI.

**4. Nima uchun KO'PCHILIK MUTAXASSISLAR, Shadow FK
Property'DAN KO'RA, ANIQ, ODDIY FK PROPERTY (`DepartmentId`)
YOZISHNI TAVSIYA QILADI?**
Chunki ANIQ PROPERTY — LINQ SO'ROVLARDA TO'G'RIDAN-TO'G'RI
(`e.DepartmentId == 5`) ISHLATISH MUMKIN, DEBUGGER'DA OSON
KO'RINADI, VA KODNI O'QISH/TEST YOZISH SODDALASHADI — Shadow
Property BULARNING BARCHASINI QIYINLASHTIRADI.

**5. Migratsiya faylida, Shadow Property'ga TEGISHLI USTUN
QANDAY KO'RINADI — C# ENTITY KLASSIDAGI ODDIY PROPERTYDAN
FARQ QILADIMI?**
Migratsiya faylida (masalan `migrationBuilder.AddColumn<int>
("DepartmentId", ...)`) — FARQ YO'Q, ODDIY USTUN KABI TO'LIQ
KO'RINADI. FARQ FAQAT C# ENTITY KLASSI DARAJASIDA: SHADOW
PROPERTY — U YERDA UMUMAN YO'Q, FAQAT EF Core'NING ICHKI
MODELIDA MAVJUD.
