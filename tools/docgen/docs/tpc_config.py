# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "Table-per-concrete-type configuration"
CATEGORY = "EF Core"
TITLE = "TPC — Konkret Tiplar Uchun Mapping"
SUBTITLE = "Sozlash tartibi, kalit generatsiyasi va cheklovlar"
FILENAME = "Table-per-concrete-type configuration.docx"


def build(d):
    h1(d, "1. TPC nima va u qanday farq qiladi")

    para(d, "Table-per-Concrete-type strategiyasida faqat konkret, ya'ni nusxa yaratish "
            "mumkin bo'lgan tiplar uchun jadval yaratiladi. Abstrakt bazaviy tip uchun "
            "jadval umuman bo'lmaydi; uning ustunlari har bir hosila jadvalda "
            "takrorlanadi.")

    para(d, "TPC EF Core 7 versiyasida qo'shilgan. Undan oldin faqat TPH va TPT mavjud "
            "edi, shuning uchun eski loyihalarda bu strategiyani uchratish kam.")

    para(d, "TPC ning asosiy g'oyasi — har bir konkret tipni mustaqil jadval sifatida "
            "ko'rish. Shu tufayli bitta tipga yozilgan so'rov boshqa hech qanday jadvalga "
            "tegmaydi va JOIN talab qilmaydi.")

    note(d, "Men buni shunday eslab qoldim:",
         "TPH — hamma bitta uyda yashaydi, kim kimligini eshikdagi yorliq aytadi. "
         "TPT — umumiy narsalar omborda, shaxsiy narsalar har kimning xonasida, har safar "
         "ikkalasiga borish kerak. TPC — har kimning o'z to'liq uyi bor, lekin mebel "
         "takrorlanadi.")

    # ───────────────────────────────────────────
    h1(d, "2. Sozlash")

    code(d, """public abstract class Document
{
    public int Id { get; set; }
    public string Number { get; set; }
    public DateTime IssuedAt { get; set; }
}

public class Invoice : Document
{
    public decimal Total { get; set; }
    public string CustomerName { get; set; }
}

public class Contract : Document
{
    public DateTime ValidUntil { get; set; }
    public string PartyName { get; set; }
}""")

    code(d, """modelBuilder.Entity<Document>().UseTpcMappingStrategy();

modelBuilder.Entity<Invoice>().ToTable("invoices");
modelBuilder.Entity<Contract>().ToTable("contracts");""")

    para(d, "`UseTpcMappingStrategy()` butun ierarxiya uchun bir marta, eng yuqoridagi "
            "tipga chaqiriladi. Jadval nomlari berilmasa, ular klass nomlaridan olinadi.")

    h2(d, "2.1 Ko'p darajali ierarxiya")

    para(d, "Agar ierarxiya ikki darajali bo'lsa va oraliq tip ham konkret bo'lsa, u ham "
            "o'z jadvalini oladi:")

    code(d, """Document (abstract)   →  jadval yo'q
  ├── Invoice            →  invoices
  │     └── ProformaInvoice  →  proforma_invoices
  └── Contract           →  contracts""")

    para(d, "`ProformaInvoice` jadvali `Document` va `Invoice` ning barcha ustunlarini "
            "o'z ichiga oladi. Ya'ni meros zanjiri uzun bo'lgan sari takrorlanish "
            "ham ortadi.")

    # ───────────────────────────────────────────
    h1(d, "3. Kalit generatsiyasi — eng muhim cheklov")

    para(d, "TPC da birlamchi kalitlar barcha jadvallar bo'ylab noyob bo'lishi shart. "
            "Agar `invoices` jadvalida `Id = 5` bo'lsa, `contracts` jadvalida `Id = 5` "
            "bo'lgan yozuv bo'lishi mumkin emas.")

    para(d, "Buning sababi — bazaviy tip bo'yicha so'rov yozilganda EF Core barcha "
            "jadvallarni birlashtiradi. Agar kalitlar takrorlansa, natijada bir xil "
            "identifikatorli ikki turli obyekt paydo bo'ladi va change tracker ularni "
            "bitta entity deb hisoblaydi.")

    para(d, "Shu sababli jadval darajasidagi `IDENTITY` yaramaydi — har bir jadval o'z "
            "hisobidan boshlaydi. O'rniga umumiy ketma-ketlik ishlatiladi:")

    code(d, """modelBuilder.HasSequence<int>("document_ids");

modelBuilder.Entity<Document>()
    .UseTpcMappingStrategy()
    .Property(doc => doc.Id)
    .HasDefaultValueSql("nextval('document_ids')");""")

    para(d, "EF Core SQL Server va PostgreSQL uchun bu ketma-ketlikni ko'p hollarda "
            "o'zi yaratadi — strategiya `UseTpcMappingStrategy()` bilan yoqilganda "
            "konventsiya ishga tushadi. Shunga qaramay generatsiya qilingan migration ni "
            "o'qib, kalit manbasi haqiqatan umumiy ekaniga ishonch hosil qilish kerak.")

    note(d, "Bu meni birinchi marta chalkashtirgan joy:",
         "Men odatdagidek `int Id` yozib qo'yaveraman va EF Core identity yaratadi deb "
         "o'ylayman. TPC da esa bu jimgina noto'g'ri ishlaydi — xatolik darhol "
         "chiqmaydi, lekin bazaviy tip bo'yicha so'rov yozganimda ikkita turli hujjat "
         "bitta bo'lib ko'rinishi mumkin. Shuning uchun TPC tanlasam, birinchi ish — "
         "kalit manbasini tekshirish.")

    note(d, "Oddiy muqobil:",
         "Agar kalit sifatida `Guid` ishlatsam, bu muammo umuman yo'qoladi — qiymatlar "
         "o'z-o'zidan global noyob bo'ladi. TPC bilan `Guid` juda yaxshi mos tushadi.")

    code(d, """public abstract class Document
{
    public Guid Id { get; set; }   // ketma-ketlik kerak emas
    ...
}""")

    # ───────────────────────────────────────────
    h1(d, "4. Cheklovlar")

    para(d, "TPC boshqa strategiyalarga nisbatan bir nechta qo'shimcha cheklovga ega:")

    bullets(d, [
        "**Abstrakt bazaviy tipga tashqi kalit qo'yib bo'lmaydi.** Boshqa entity "
        "`Document` ga ishora qila olmaydi, chunki bunday jadval mavjud emas. Faqat "
        "konkret tipga — `Invoice` yoki `Contract` ga — ishora qilish mumkin.",
        "**Bazaviy tipga ko'p-ga-ko'p bog'lanish ishlamaydi** — u ham tashqi kalitga "
        "tayanadi.",
        "**Umumiy ustunlar takrorlanadi**, shuning uchun bazaviy tipga yangi maydon "
        "qo'shish barcha jadvallarni o'zgartiradi.",
        "**Indekslar har bir jadvalda alohida yaratilishi kerak** — umumiy ustun "
        "bo'yicha qidiruv uchun har bir jadvalga indeks qo'yiladi.",
    ])

    note(d, "Tashqi kalit cheklovi amalda nimani anglatadi:",
         "Agar menda \"har qanday hujjatga izoh qoldirish\" degan talab bo'lsa, TPC "
         "bilan buni to'g'ridan-to'g'ri qila olmayman. Izoh jadvalida `DocumentId` "
         "ustunini qo'ysam ham, unga tashqi kalit cheklovini bog'lay olmayman. Bu — "
         "TPC ni tanlashdan oldin o'ylab ko'rish kerak bo'lgan jiddiy nuqta.")

    # ───────────────────────────────────────────
    h1(d, "5. So'rovlar")

    code(d, """// Faqat bitta tip — eng samarali holat
var invoices = await db.Set<Invoice>().ToListAsync();
// SELECT ... FROM "invoices"       — JOIN ham, UNION ham yo'q

// Butun ierarxiya
var docs = await db.Set<Document>().ToListAsync();
// UNION ALL orqali barcha jadvallar birlashtiriladi""")

    para(d, "Birinchi so'rov — TPC ning eng kuchli tomoni. Bitta jadval, bitta skan, "
            "hech qanday ortiqcha ustun yoki satr.")

    para(d, "Ikkinchi so'rov esa `UNION ALL` hosil qiladi; uning tafsilotlari alohida "
            "ko'rib chiqiladi.")

    # ───────────────────────────────────────────
    h1(d, "6. Qachon TPC mos keladi")

    bullets(d, [
        "Konkret tiplar amalda bir-biridan mustaqil bo'lsa va kamdan-kam birgalikda "
        "so'ralsa.",
        "Har bir tipda ko'p va majburiy maydonlar bo'lsa.",
        "Bazaviy tipga tashqi kalit kerak bo'lmasa.",
        "Kalit sifatida `Guid` yoki umumiy ketma-ketlik ishlatish qabul qilinsa.",
    ])

    para(d, "Agar bu shartlarning birortasi bajarilmasa, TPH yoki TPT xavfsizroq tanlov "
            "bo'ladi.")

    # ───────────────────────────────────────────
    h1(d, "7. Xulosa")

    bullets(d, [
        "TPC faqat konkret tiplar uchun jadval yaratadi; abstrakt bazaviy tip jadvalsiz "
        "qoladi.",
        "`UseTpcMappingStrategy()` ierarxiyaning eng yuqori tipiga bir marta chaqiriladi.",
        "Birlamchi kalitlar barcha jadvallar bo'ylab noyob bo'lishi shart — umumiy "
        "ketma-ketlik yoki `Guid` kerak.",
        "Abstrakt bazaviy tipga tashqi kalit va ko'p-ga-ko'p bog'lanish qo'yib bo'lmaydi.",
        "Bitta konkret tipni o'qish — eng tez stsenariy; butun ierarxiya `UNION ALL` "
        "talab qiladi.",
        "EF Core 7 va undan yuqori versiyalarda mavjud.",
    ])

    sources(d, [
        ("Inheritance: Table-per-concrete-type configuration — EF Core",
         "https://learn.microsoft.com/en-us/ef/core/modeling/inheritance#table-per-concrete-type-configuration"),
        ("What's New in EF Core 7.0 — TPC inheritance mapping",
         "https://learn.microsoft.com/en-us/ef/core/what-is-new/ef-core-7.0/whatsnew#table-per-concrete-type-tpc-inheritance-mapping"),
        ("Sequences — EF Core",
         "https://learn.microsoft.com/en-us/ef/core/modeling/sequences"),
    ])
