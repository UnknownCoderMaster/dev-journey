# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "TPC database schema"
CATEGORY = "EF Core"
TITLE = "TPC Strategiyasida Baza Sxemasi"
SUBTITLE = "Generatsiya qilinadigan jadvallar, ketma-ketliklar va UNION so'rovlari"
FILENAME = "TPC database schema.docx"


def build(d):
    h1(d, "1. Nimani ko'rib chiqamiz")

    para(d, "TPC strategiyasini sozlash alohida mavzu bo'lsa, bu hujjat shu sozlama "
            "natijasida bazada aynan nima paydo bo'lishini ko'rib chiqadi: qanday "
            "jadvallar yaratiladi, kalitlar qayerdan keladi, indekslar qanday joylashadi "
            "va so'rovlar qanday SQL ga aylanadi.")

    para(d, "Sxemani tushunish muhim, chunki TPC da ilova kodi oddiy ko'rinsa ham, "
            "bazadagi tuzilma an'anaviy relyatsion modeldan sezilarli farq qiladi.")

    # ───────────────────────────────────────────
    h1(d, "2. Misol model")

    code(d, """public abstract class Employee
{
    public int Id { get; set; }
    public string FullName { get; set; }
    public DateTime HiredAt { get; set; }
}

public class Developer : Employee
{
    public string PrimaryLanguage { get; set; }
    public int YearsOfExperience { get; set; }
}

public class Manager : Employee
{
    public int TeamSize { get; set; }
}""")

    code(d, """modelBuilder.Entity<Employee>().UseTpcMappingStrategy();
modelBuilder.Entity<Developer>().ToTable("developers");
modelBuilder.Entity<Manager>().ToTable("managers");""")

    # ───────────────────────────────────────────
    h1(d, "3. Generatsiya qilinadigan sxema")

    para(d, "PostgreSQL uchun migration quyidagini hosil qiladi:")

    code(d, """CREATE SEQUENCE "EmployeeSequence" START WITH 1 INCREMENT BY 1;

CREATE TABLE "developers" (
    "Id"                integer NOT NULL
                        DEFAULT (nextval('"EmployeeSequence"')),
    "FullName"          text NOT NULL,
    "HiredAt"           timestamp with time zone NOT NULL,
    "PrimaryLanguage"   text NOT NULL,
    "YearsOfExperience" integer NOT NULL,
    CONSTRAINT "PK_developers" PRIMARY KEY ("Id")
);

CREATE TABLE "managers" (
    "Id"       integer NOT NULL
               DEFAULT (nextval('"EmployeeSequence"')),
    "FullName" text NOT NULL,
    "HiredAt"  timestamp with time zone NOT NULL,
    "TeamSize" integer NOT NULL,
    CONSTRAINT "PK_managers" PRIMARY KEY ("Id")
);""")

    para(d, "Uch jihatga e'tibor berish kerak:")

    bullets(d, [
        "`employees` nomli jadval **yo'q** — abstrakt tip sxemada umuman ko'rinmaydi.",
        "`FullName` va `HiredAt` ustunlari **ikkala jadvalda ham** takrorlangan.",
        "Ikkala jadval **bitta ketma-ketlikdan** kalit oladi — shuning uchun `Id` "
        "qiymatlari takrorlanmaydi.",
    ])

    note(d, "Ketma-ketlikni ko'rganimda tushundim:",
         "Bu shunchaki texnik tafsilot emas. Ketma-ketlik umumiy bo'lgani uchun "
         "`developers` jadvalidagi Id lar 1, 3, 7 bo'lishi mumkin — oradagi 2, 4, 5, 6 "
         "esa `managers` da. Ya'ni bitta jadvalga qarab \"nechta yozuv bor\" deb Id ga "
         "qarash mutlaqo noto'g'ri bo'ladi. Buni bilmasdan turib hisobot yozsam, "
         "noto'g'ri raqam chiqarardim.")

    h2(d, "3.1 Diskriminator ustuni yo'q")

    para(d, "TPH dan farqli o'laroq, TPC da hech qanday diskriminator ustuni "
            "yaratilmaydi. Tip jadvalning o'zi bilan aniqlanadi — `developers` "
            "jadvalidagi har bir satr, ta'rifiga ko'ra, `Developer`.")

    # ───────────────────────────────────────────
    h1(d, "4. Indekslar")

    para(d, "Indekslar har bir jadvalda alohida yaratiladi. Bazaviy tipdagi ustun "
            "bo'yicha indeks e'lon qilinsa, u barcha jadvallarga nusxalanadi:")

    code(d, """modelBuilder.Entity<Employee>()
    .HasIndex(e => e.FullName);""")

    code(d, """CREATE INDEX "IX_developers_FullName" ON "developers" ("FullName");
CREATE INDEX "IX_managers_FullName"   ON "managers"   ("FullName");""")

    para(d, "Noyoblik cheklovi esa faqat o'z jadvali ichida amal qiladi. Ya'ni "
            "`HasIndex(...).IsUnique()` qo'yilsa, bir xil qiymat `developers` va "
            "`managers` jadvallarida parallel ravishda mavjud bo'lishi mumkin.")

    note(d, "Bu nozik, lekin xavfli joy:",
         "Agar men xodimning tabel raqamini noyob qilmoqchi bo'lsam, TPC bu kafolatni "
         "bermaydi — ikki turli jadvalda bir xil raqamli xodim paydo bo'lishi mumkin. "
         "Buni hal qilish uchun yo ilova darajasida tekshirishim, yo umumiy ketma-ketlik "
         "ishlatishim kerak bo'ladi. TPH da bunday muammo yo'q, chunki u yerda jadval "
         "bitta.")

    # ───────────────────────────────────────────
    h1(d, "5. So'rovlar va SQL")

    h2(d, "5.1 Bitta konkret tip")

    code(d, """var devs = await db.Set<Developer>()
    .Where(x => x.YearsOfExperience > 3)
    .ToListAsync();""")

    code(d, """SELECT d."Id", d."FullName", d."HiredAt",
       d."PrimaryLanguage", d."YearsOfExperience"
FROM "developers" AS d
WHERE d."YearsOfExperience" > 3;""")

    para(d, "Bu TPC ning asosiy yutug'i: so'rov boshqa hech qanday jadvalga tegmaydi, "
            "JOIN ham, `UNION` ham, diskriminator filtri ham yo'q. Shu nuqtada TPC "
            "ierarxiyasiz oddiy jadvaldan farq qilmaydi.")

    h2(d, "5.2 Butun ierarxiya")

    code(d, """var all = await db.Set<Employee>().ToListAsync();""")

    code(d, """SELECT u."Id", u."FullName", u."HiredAt",
       u."PrimaryLanguage", u."YearsOfExperience",
       u."TeamSize", u."Discriminator"
FROM (
    SELECT d."Id", d."FullName", d."HiredAt",
           d."PrimaryLanguage", d."YearsOfExperience",
           NULL AS "TeamSize",
           'Developer' AS "Discriminator"
    FROM "developers" AS d

    UNION ALL

    SELECT m."Id", m."FullName", m."HiredAt",
           NULL, NULL,
           m."TeamSize",
           'Manager'
    FROM "managers" AS m
) AS u;""")

    para(d, "Diskriminator bu yerda jadvalda emas, so'rov ichida konstanta sifatida "
            "hosil qilinadi. Yetishmaydigan ustunlar `NULL` bilan to'ldiriladi, ya'ni "
            "natija to'plami TPH jadvaliga o'xshab qoladi — faqat u vaqtinchalik.")

    h2(d, "5.3 Saralash va sahifalash")

    para(d, "`UNION ALL` ustidan `ORDER BY` qo'yilsa, baza avval barcha jadvallarni "
            "birlashtirib, keyin saralashi kerak bo'ladi:")

    code(d, """var page = await db.Set<Employee>()
    .OrderBy(e => e.HiredAt)
    .Skip(0).Take(20)
    .ToListAsync();""")

    note(d, "Mana shu joyda ehtiyot bo'laman:",
         "Har bir jadvaldagi `HiredAt` indeksi alohida ishlaydi, lekin birlashtirilgan "
         "natijani saralash uchun baza baribir qo'shimcha ish qilishi mumkin. Agar menda "
         "yuz minglab yozuv bo'lsa va men doim butun ierarxiyani sahifalab ko'rsatsam — "
         "TPC noto'g'ri tanlov bo'lgan bo'lardi. TPC ning ma'nosi aynan shundaki, "
         "tiplarni alohida-alohida so'raman.")

    # ───────────────────────────────────────────
    h1(d, "6. Bog'lanishlar sxemada qanday ko'rinadi")

    para(d, "TPC da abstrakt tipga tashqi kalit qo'yib bo'lmaydi, shuning uchun "
            "bog'lanish faqat konkret jadvalga yo'naltiriladi:")

    code(d, """CREATE TABLE "code_reviews" (
    "Id"          integer GENERATED BY DEFAULT AS IDENTITY,
    "DeveloperId" integer NOT NULL,
    CONSTRAINT "FK_code_reviews_developers_DeveloperId"
        FOREIGN KEY ("DeveloperId") REFERENCES "developers" ("Id")
);""")

    para(d, "Agar bog'lanish ierarxiyaning har qanday tipiga kerak bo'lsa, uni baza "
            "darajasida ifodalashning yagona yo'li — cheklovsiz ustun qoldirish yoki "
            "strategiyani o'zgartirish.")

    # ───────────────────────────────────────────
    h1(d, "7. Sxemani tekshirish")

    para(d, "TPC sozlangandan keyin men quyidagilarni albatta tekshiraman:")

    bullets(d, [
        "Ketma-ketlik yaratilganmi va **ikkala** jadval ham undan foydalanyaptimi.",
        "Kutilgan jadvallar ro'yxati to'g'rimi — abstrakt tip uchun jadval "
        "yaratilmaganmi.",
        "Kerakli indekslar har bir jadvalda bormi.",
        "Noyoblik talab qilinadigan ustunlar haqiqatan global noyobligi "
        "ta'minlanganmi.",
    ])

    code(d, """dotnet ef migrations script --idempotent --output tpc.sql""",
         caption="Butun sxemani SQL sifatida chiqarib o'qish")

    # ───────────────────────────────────────────
    h1(d, "8. Xulosa")

    bullets(d, [
        "TPC sxemasida abstrakt tip uchun jadval yaratilmaydi va diskriminator ustuni "
        "ham bo'lmaydi.",
        "Umumiy ustunlar har bir konkret jadvalda takrorlanadi.",
        "Barcha jadvallar bitta ketma-ketlikdan kalit oladi, shuning uchun Id lar "
        "jadvallar aro uzluksiz ketmaydi.",
        "Indekslar har bir jadvalda nusxalanadi; noyoblik faqat jadval ichida "
        "kafolatlanadi.",
        "Bitta tipga so'rov — oddiy `SELECT`; butun ierarxiya — `UNION ALL`.",
        "Tashqi kalit faqat konkret jadvalga yo'naltirilishi mumkin.",
    ])

    sources(d, [
        ("Inheritance: TPC database schema — EF Core",
         "https://learn.microsoft.com/en-us/ef/core/modeling/inheritance#tpc-database-schema"),
        ("Sequences — EF Core",
         "https://learn.microsoft.com/en-us/ef/core/modeling/sequences"),
        ("Indexes — EF Core",
         "https://learn.microsoft.com/en-us/ef/core/modeling/indexes"),
    ])
