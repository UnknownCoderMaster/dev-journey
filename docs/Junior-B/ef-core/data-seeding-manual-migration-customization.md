# Data Seeding, Manual Migration Customization — Junior B

## 1. What (Nima?)

**Data Seeding** — DB YARATILGANDA/MIGRATSIYA QILINGANDA,
**BOSHLANG'ICH, OLDINDAN BELGILANGAN MA'LUMOTLARNI** (masalan
rol turlari, standart sozlamalar) AVTOMATIK KIRITISH JARAYONI.
**Manual Migration Customization** — EF Core AVTOMATIK
GENERATSIYA QILGAN MIGRATSIYA FAYLINI, **QO'LDA TAHRIRLASH**
(masalan RAW SQL QO'SHISH, MAVJUD MA'LUMOTLARNI KO'CHIRISH
MANTIQINI YOZISH) — EF Core O'ZI AVTOMATIK ANIQLAY OLMAYDIGAN
O'ZGARISHLAR UCHUN ZARUR.

## 2. Real hayot analogiyasi

**Data Seeding — YANGI DO'KON OCHILGANDA, "BOSHLANG'ICH
TOVAR RO'YXATI" BILAN TAMINLASH.** Yangi DO'KON (yangi DB) —
BO'SH JAVONLAR BILAN OCHILMAYDI — UNDA, DOIM MAVJUD BO'LISHI
KERAK BO'LGAN ASOSIY TOVARLAR (masalan "standart o'lchov
birliklari", "asosiy toifalar") — OLDINDAN JOYLASHTIRILADI.
**Manual Migration — DO'KONNI QAYTA JIHOZLASHDA, ARXITEKTOR
REJASIGA QO'LDA TUZATISH KIRITISH** (masalan "eski javonlarni
ko'chirishdan oldin, ulardagi tovarlarni vaqtinchalik boshqa
joyga o'tkazish kerak" — bu, AVTOMATIK REJALASHTIRUVCHI
(EF Core) BILA OLMAYDIGAN, BIZNES-SPETSIFIK QADAM).

## 3. Why (Nega kerak?)

Ba'zi MA'LUMOTLAR (masalan `Role` jadvalidagi "Admin",
"User" YOZUVLARI) — **ILOVA MANTIQINING AJRALMAS QISMI**
(kod, shu ID'larga QAT'IY TAYANADI) — ULAR, HAR MUHITDA (dev,
staging, production) **BIR XIL BO'LISHI SHART**. Data Seeding
— BU MA'LUMOTLARNI, QO'LDA, HAR MUHITDA ALOHIDA INSERT QILISH
O'RNIGA, **MIGRATSIYA JARAYONINING BIR QISMI** QILIB, AVTOMAT-
LASHTIRADI. Manual Migration Customization — EF Core, USTUN
NOMINI O'ZGARTIRISHNI, YANGI USTUN QO'SHISH + ESKISINI
O'CHIRISH DEB "NOTO'G'RI TUSHUNGANDA" (data yo'qolishi
xavfi bilan), QO'LDA TO'G'RILASH UCHUN ZARUR.

## 4. Internals (Ichki mexanizm)

### `HasData()` — Seeding'ning EF Core MIGRATSIYA MEXANIZMI

```csharp
modelBuilder.Entity<Role>().HasData(
    new Role { Id = 1, Name = "Admin" },
    new Role { Id = 2, Name = "User" }
);
```

```
HasData() — MODEL SNAPSHOT'GA (EF Core'ning "OXIRGI HOLAT"
XOTIRASI) QO'SHILADI. MIGRATSIYA YARATILGANDA
(`dotnet ef migrations add`), EF Core, OLDINGI SNAPSHOT bilan
SOLISHTIRIB, YANGI QATORLARNI ANIQLAB, MIGRATSIYA FAYLIGA
`migrationBuilder.InsertData(...)` QATORLARINI AVTOMATIK
QO'SHADI — bu, ODDIY DB SCHEMA O'ZGARISHI (ustun qo'shish) 
BILAN BIR XIL MEXANIZM ORQALI ISHLAYDI (deklarativ, DIFF-BASED).
```

### Migratsiya faylining STRUKTURASI — `Up()` va `Down()`

```csharp
public partial class SeedRoles : Migration
{
    protected override void Up(MigrationBuilder migrationBuilder)
    {
        migrationBuilder.InsertData(
            table: "Roles",
            columns: new[] { "Id", "Name" },
            values: new object[,] { { 1, "Admin" }, { 2, "User" } });
    }

    protected override void Down(MigrationBuilder migrationBuilder)
    {
        migrationBuilder.DeleteData(table: "Roles", keyColumn: "Id", keyValues: new object[] { 1, 2 });
    }
}
```

```
HAR MIGRATSIYA — IKKI METODGA EGA: Up() — MIGRATSIYA
QO'LLANGANDA BAJARILADIGAN O'ZGARISHLAR (dotnet ef database
update). Down() — MIGRATSIYA "ORQAGA QAYTARILGANDA"
(ROLLBACK) BAJARILADIGAN, TESKARI O'ZGARISHLAR. EF Core,
Up() METODINI AVTOMATIK GENERATSIYA QILADI, LEKIN Down()NI
HAM, ODATDA, TO'G'RI "TESKARI" MANTIQ bilan O'ZI YOZADI.
```

### Manual Customization — Column Rename MISOLI

```csharp
// EF Core AVTOMATIK generatsiya qilgan (XATO!) migratsiya — DATA YO'QOTADI:
migrationBuilder.DropColumn(name: "FullName", table: "Employees");
migrationBuilder.AddColumn<string>(name: "EmployeeFullName", table: "Employees");

// QO'LDA TO'G'RILANGAN (data saqlanadi) — RenameColumn ishlatiladi:
migrationBuilder.RenameColumn(
    name: "FullName", table: "Employees", newName: "EmployeeFullName");
```

```
EF Core'ning MIGRATSIYA GENERATORI — USTUN NOMI O'ZGARTIRILGANDA
(C# property nomi), BU HOLATNI, "ESKI USTUN O'CHIRILDI + YANGI
USTUN QO'SHILDI" DEB **NOTO'G'RI ANIQLASHI MUMKIN** (chunki
u, ODDIY MODEL SNAPSHOT SOLISHTIRUVI ASOSIDA ISHLAYDI, "BU
QAYTA NOMLASHMI YOKI HAQIQATDA IKKI ALOHIDA O'ZGARISHMI"
degan NIYATNI TUSHUNMAYDI) — natijada, MIGRATSIYA
QO'LLANILGANDA, MAVJUD MA'LUMOTLAR (FullName qiymatlari)
YO'QOLADI! DASTURCHI, MIGRATSIYA FAYLINI QO'LDA OCHIB,
`DropColumn`+`AddColumn`NI, `RenameColumn`GA ALMASHTIRISHI
SHART.
```

## 5. Code (Amaliy kod)

```csharp
// Data Seeding — Fluent API orqali
public class AppDbContext : DbContext
{
    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.Entity<Role>().HasData(
            new Role { Id = 1, Name = "Admin" },
            new Role { Id = 2, Name = "User" },
            new Role { Id = 3, Name = "Manager" }
        );
    }
}

// ⚠️ MUHIM: HasData()'da ISHLATILADIGAN OBYEKTLAR — HAR DOIM ANIQ, "QAT'IY" ID'GA EGA BO'LISHI SHART
// (Migration snapshot — solishtirish uchun ID'ga tayanadi, DB avtomatik generatsiya qiladigan ID emas)
```

```bash
# Migratsiya yaratish va qo'llash
dotnet ef migrations add SeedRoles
dotnet ef database update
```

```csharp
// Manual Migration Customization — RAW SQL qo'shish (EF Core avtomatik generatsiya qila olmaydigan holat)
public partial class AddFullTextSearchIndex : Migration
{
    protected override void Up(MigrationBuilder migrationBuilder)
    {
        // EF Core Fluent API'da to'g'ridan-to'g'ri mavjud bo'lmagan, PostgreSQL-specific funksiya
        migrationBuilder.Sql(@"
            CREATE INDEX idx_employees_fulltext 
            ON employees USING GIN (to_tsvector('english', full_name));
        ");
    }

    protected override void Down(MigrationBuilder migrationBuilder)
    {
        migrationBuilder.Sql("DROP INDEX idx_employees_fulltext;");
    }
}
```

```csharp
// Data migration — mavjud ma'lumotlarni yangi ustunga ko'chirish (qo'lda yozilishi shart)
public partial class SplitFullNameIntoFirstLast : Migration
{
    protected override void Up(MigrationBuilder migrationBuilder)
    {
        migrationBuilder.AddColumn<string>(name: "FirstName", table: "Employees", nullable: true);
        migrationBuilder.AddColumn<string>(name: "LastName", table: "Employees", nullable: true);

        // Mavjud ma'lumotlarni yangi ustunlarga bo'lib yozish — EF Core BUNI O'ZI BILA OLMAYDI!
        migrationBuilder.Sql(@"
            UPDATE ""Employees""
            SET ""FirstName"" = split_part(""FullName"", ' ', 1),
                ""LastName"" = split_part(""FullName"", ' ', 2);
        ");

        migrationBuilder.DropColumn(name: "FullName", table: "Employees");
    }
}
```

## 6. Keng tarqalgan xatolar / noto'g'ri tushunchalar

```
❌ "HasData() — production'da HAM, HAR SAFAR DASTUR ISHGA
   TUSHGANDA, MA'LUMOTLARNI QAYTA KIRITADI" — YO'Q! HasData()
   — MIGRATSIYA FAYLIGA, BIR MARTALIK InsertData() sifatida
   YOZILADI — MIGRATSIYA BIR MARTA QO'LLANGANDAN KEYIN, QAYTA
   ISHLAMAYDI (agar YANGI migratsiya yaratilmasa).

❌ "USTUN NOMINI C# klassida o'zgartirsam, EF Core buni HAR
   DOIM 'RENAME' deb TO'G'RI ANIQLAYDI" — YO'Q! KO'PINCHA, EF
   Core buni "DROP + ADD" deb NOTO'G'RI GENERATSIYA QILADI —
   MIGRATSIYA FAYLINI QO'LDA TEKSHIRIB, KERAK BO'LSA
   RenameColumn'GA O'ZGARTIRISH SHART (aks holda DATA
   YO'QOLADI!).

❌ "Migratsiya faylini QO'LDA TAHRIRLASH — XAVFLI, HECH QACHON
   QILMASLIK KERAK" — YO'Q, AYRIM HOLATLARDA (RAW SQL, DATA
   MIGRATION, RENAME) BU — YAGONA TO'G'RI YECHIM. XAVF —
   FAQAT NOTO'G'RI, TEKSHIRILMAGAN TAHRIRLASHDA.

❌ "Down() metodi — HECH QACHON ISHLATILMAYDI, YOZISH SHART
   EMAS" — YO'Q, ROLLBACK KERAK BO'LGANDA (masalan production'da
   MUAMMO CHIQSA) — Down() METODI, DB'NI OLDINGI HOLATGA
   QAYTARISH UCHUN ZARUR.
```

## 7. Exam (Interview savollari)

**1. Data Seeding nima, va u EF Core'da QANDAY MEXANIZM
ORQALI AMALGA OSHIRILADI?**
Data Seeding — DB'ga BOSHLANG'ICH, OLDINDAN BELGILANGAN
MA'LUMOTLARNI KIRITISH JARAYONI. EF Core'da bu,
`modelBuilder.Entity<T>().HasData(...)` ORQALI, MODEL
SNAPSHOT'GA QO'SHILADI VA MIGRATSIYA YARATILGANDA,
`InsertData()` SIFATIDA MIGRATSIYA FAYLIGA AVTOMATIK
YOZILADI.

**2. Migratsiya faylidagi `Up()` va `Down()` metodlari
QANDAY VAZIFANI BAJARADI?**
`Up()` — MIGRATSIYA QO'LLANGANDA (`dotnet ef database
update`) BAJARILADIGAN O'ZGARISHLAR. `Down()` — MIGRATSIYA
ROLLBACK QILINGANDA BAJARILADIGAN, TESKARI O'ZGARISHLAR —
DB'NI OLDINGI HOLATGA QAYTARISH UCHUN ZARUR.

**3. Nima uchun USTUN NOMINI O'ZGARTIRISH, EF Core'da,
XAVFLI HOLAT HISOBLANADI, VA U QANDAY OLDINI OLINADI?**
EF Core, MODEL SNAPSHOT SOLISHTIRUVI ASOSIDA ISHLAGANI UCHUN,
USTUN NOMI O'ZGARISHINI, KO'PINCHA "ESKI USTUN O'CHIRILDI +
YANGI USTUN QO'SHILDI" DEB NOTO'G'RI ANIQLAYDI — BU, MAVJUD
MA'LUMOTLARNI YO'QOTADI. YECHIM — MIGRATSIYA FAYLINI QO'LDA
OCHIB, `DropColumn`+`AddColumn`NI `RenameColumn`GA
ALMASHTIRISH.

**4. Manual Migration Customization QACHON ZARUR BO'LADI —
KONKRET MISOLLAR KELTIRING.**
(1) EF Core Fluent API'da MAVJUD BO'LMAGAN, DB-SPECIFIC
FUNKSIYALAR (masalan PostgreSQL GIN indeksi) — RAW SQL orqali
qo'shiladi. (2) USTUN NOMINI XAVFSIZ O'ZGARTIRISH
(RenameColumn). (3) MAVJUD MA'LUMOTLARNI YANGI STRUKTURAGA
KO'CHIRISH (data migration, masalan FullName'ni FirstName/
LastName'ga bo'lish).

**5. `HasData()`da ISHLATILADIGAN OBYEKTLAR UCHUN, NIMA UCHUN
ANIQ, QAT'IY ID QIYMATI BERISH SHART (DB avtomatik
generatsiya qiladigan ID emas)?**
Chunki EF Core'ning MIGRATSIYA GENERATORI, MODEL SNAPSHOT'LAR
ORASIDA "QAYSI QATOR QO'SHILDI/O'ZGARDI/O'CHIRILDI"NI, ANIQ
ID QIYMATLARI BO'YICHA SOLISHTIRADI — AGAR ID AVTOMATIK
BO'LSA, HAR MIGRATSIYA GENERATSIYASIDA (turli muhitlarda)
TURLICHA QIYMAT OLISHI MUMKIN, BU — SOLISHTIRISH VA
IZCHILLIKNI BUZADI.
