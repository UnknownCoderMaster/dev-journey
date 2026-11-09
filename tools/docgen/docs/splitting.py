# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "Table splitting, Entity splitting"
CATEGORY = "EF Core"
TITLE = "Table Splitting va Entity Splitting"
SUBTITLE = "Bitta jadvalni bir nechta entity ga va bitta entity ni bir nechta jadvalga bo'lish"
FILENAME = "Table splitting, Entity splitting.docx"


def build(d):
    h1(d, "1. Ikki qarama-qarshi tushuncha")

    para(d, "Odatda bitta entity bitta jadvalga mos keladi. Lekin EF Core bu moslikni "
            "ikki yo'nalishda buzish imkonini beradi:")

    table(d, ["Nomi", "Mohiyati"],
          [["Table splitting",
            "Bir nechta entity **bitta** jadvalga joylashadi"],
           ["Entity splitting",
            "Bitta entity **bir nechta** jadvalga yoyiladi"]],
          widths=[4.0, 11.5])

    para(d, "Nomlar o'xshash bo'lgani uchun ularni chalkashtirish oson. Esda saqlash "
            "uchun qulay usul: nom nimaning bo'linayotganini aytadi. Table splitting — "
            "jadval bo'linadi, ya'ni bitta jadval bir nechta entity orasida taqsimlanadi. "
            "Entity splitting — entity bo'linadi, ya'ni uning maydonlari bir nechta "
            "jadvalga tarqaladi.")

    # ═══════════════════════════════════════════
    h1(d, "2. Table splitting")

    h2(d, "2.1 Qanday muammoni hal qiladi")

    para(d, "Ba'zi jadvallarda kam ishlatiladigan, lekin og'ir ustunlar bo'ladi — uzun "
            "matn, JSON hujjat, rasm baytlari. Har bir so'rovda ularni o'qish keraksiz "
            "yuk hosil qiladi.")

    para(d, "Table splitting bitta jadvalni ikki entity ga ajratadi: biri \"yengil\" "
            "ustunlarni, ikkinchisi \"og'ir\" ustunlarni olib yuradi. Ikkalasi ham bir xil "
            "jadvalga va bir xil birlamchi kalitga tayanadi.")

    h2(d, "2.2 Misol")

    code(d, """public class Article
{
    public int Id { get; set; }
    public string Title { get; set; }
    public DateTime PublishedAt { get; set; }

    public ArticleBody Body { get; set; }     // og'ir qism
}

public class ArticleBody
{
    public int Id { get; set; }
    public string Content { get; set; }       // uzun matn
    public string RawHtml { get; set; }
}""")

    code(d, """modelBuilder.Entity<Article>(e =>
{
    e.ToTable("articles");
    e.HasOne(a => a.Body)
     .WithOne()
     .HasForeignKey<ArticleBody>(b => b.Id);
});

modelBuilder.Entity<ArticleBody>()
    .ToTable("articles");          // aynan bitta jadval""")

    para(d, "Ikkala entity ham `articles` jadvaliga ko'rsatilgani uchun EF Core buni "
            "table splitting deb tushunadi va qo'shimcha jadval yaratmaydi.")

    h2(d, "2.3 So'rovlarga ta'siri")

    code(d, """// Yengil so'rov — Content va RawHtml o'qilmaydi
var list = await db.Articles
    .OrderByDescending(a => a.PublishedAt)
    .Take(20)
    .ToListAsync();

// SELECT "Id", "Title", "PublishedAt" FROM "articles" ...

// Kerak bo'lganda to'liq qism yuklanadi
var full = await db.Articles
    .Include(a => a.Body)
    .FirstAsync(a => a.Id == id);""")

    note(d, "Nega bu menga yoqadi:",
         "Ro'yxat sahifasida maqolaning to'liq matni umuman kerak emas, lekin oddiy "
         "model bilan u baribir o'qiladi — yigirmata maqola uchun bir necha megabayt "
         "keraksiz trafik. Table splitting bu masalani baza sxemasiga tegmasdan hal "
         "qiladi: jadval o'sha-o'sha, faqat model ikkiga bo'lingan.")

    note(d, "Muqobil yechimni ham bilish kerak:",
         "Xuddi shu natijani proyeksiya bilan ham olish mumkin — `Select` da faqat "
         "kerakli maydonlarni yozsam bo'ldi. Farqi shundaki, table splitting bu "
         "qoidani modelning o'ziga yozib qo'yadi va men har bir so'rovda esdan "
         "chiqarmayman. Agar og'ir ustun bitta joyda ishlatilsa — proyeksiya yetarli; "
         "agar model bo'ylab tarqalgan bo'lsa — splitting afzal.")

    h2(d, "2.4 Cheklovlar")

    bullets(d, [
        "Barcha ishtirokchi entity lar **bir xil birlamchi kalitga** ega bo'lishi shart.",
        "Bog'lanish majburiy bir-ga-bir bo'lishi kerak.",
        "Ikkinchi entity mustaqil ravishda qo'shib yoki o'chirib bo'lmaydi — u egasining "
        "satri bilan birga yashaydi.",
    ])

    # ═══════════════════════════════════════════
    h1(d, "3. Entity splitting")

    h2(d, "3.1 Qanday muammoni hal qiladi")

    para(d, "Bu teskari holat: bazada allaqachon ikkita jadval bor va ular aslida bitta "
            "tushunchani tasvirlaydi. Masalan `customers` va `customer_contacts` — "
            "ikkalasi ham bitta mijoz haqida.")

    para(d, "Mavjud bazani o'zgartirmasdan, kodda ularni bitta entity sifatida ko'rsatish "
            "kerak bo'ladi. Entity splitting aynan shuni qiladi. Bu imkoniyat "
            "EF Core 7 dan boshlab mavjud.")

    h2(d, "3.2 Misol")

    code(d, """public class Customer
{
    public int Id { get; set; }
    public string Name { get; set; }

    // boshqa jadvaldan keladigan maydonlar
    public string Phone { get; set; }
    public string Email { get; set; }
    public string City { get; set; }
}""")

    code(d, """modelBuilder.Entity<Customer>(e =>
{
    e.ToTable("customers");

    e.SplitToTable("customer_contacts", t =>
    {
        t.Property(c => c.Phone);
        t.Property(c => c.Email);
        t.Property(c => c.City);
    });
});""")

    para(d, "Endi `Customer` bilan ishlaganda ikkala jadval ham avtomatik qo'shiladi:")

    code(d, """SELECT c."Id", c."Name",
       cc."Phone", cc."Email", cc."City"
FROM "customers" AS c
INNER JOIN "customer_contacts" AS cc ON c."Id" = cc."Id";""")

    para(d, "Yozishda esa EF Core ikkita `INSERT` yuboradi va ularni bitta tranzaksiyaga "
            "o'raydi.")

    h2(d, "3.3 Qachon ishlatiladi")

    bullets(d, [
        "Eski (legacy) bazaga ulanganda, uning sxemasini o'zgartirish imkoni bo'lmaganda.",
        "Tarixan ikkiga bo'lingan jadvallarni kodda birlashtirgan holda ko'rsatish "
        "kerak bo'lganda.",
        "Boshqa tizim tomonidan boshqariladigan jadvalni o'z modeliga qo'shishda.",
    ])

    note(d, "Mening munosabatim:",
         "Entity splitting — bu asosan moslashuv vositasi, arxitektura qarori emas. "
         "Agar bazani noldan loyihalayotgan bo'lsam, bitta tushunchani ikki jadvalga "
         "bo'lib, keyin uni kodda qayta birlashtirishning ma'nosi yo'q. Lekin tayyor "
         "bazaga ulanishda u juda asqotadi — baza sxemasiga tegmasdan toza model "
         "qurish imkonini beradi.")

    h2(d, "3.4 Cheklovlar")

    bullets(d, [
        "Qo'shimcha jadvalning kaliti asosiy jadval kaliti bilan mos bo'lishi kerak.",
        "Har bir so'rov `INNER JOIN` hosil qiladi — shuning uchun qo'shimcha jadvalda "
        "har bir yozuv uchun satr bo'lishi shart.",
        "Bitta entity ni ikkitadan ortiq jadvalga bo'lish mumkin, lekin JOIN lar soni "
        "mos ravishda ortadi.",
    ])

    # ═══════════════════════════════════════════
    h1(d, "4. Taqqoslash")

    table(d, ["Jihat", "Table splitting", "Entity splitting"],
          [["Jadvallar soni", "1", "2 yoki undan ko'p"],
           ["Entity lar soni", "2 yoki undan ko'p", "1"],
           ["Asosiy maqsad", "Og'ir ustunlarni kechiktirib yuklash",
            "Mavjud sxemani bitta modelga yig'ish"],
           ["So'rovda JOIN", "Faqat `Include` qilinganda", "Har doim"],
           ["Qo'shilgan versiya", "EF Core 2.0", "EF Core 7.0"]],
          widths=[3.6, 5.9, 6.0])

    # ═══════════════════════════════════════════
    h1(d, "5. Xulosa")

    bullets(d, [
        "Table splitting bitta jadvalni bir nechta entity orasida taqsimlaydi; asosiy "
        "foydasi — og'ir ustunlarni faqat kerak bo'lganda o'qish.",
        "Entity splitting bitta entity ni bir nechta jadvalga yoyadi; asosiy foydasi — "
        "mavjud baza sxemasiga moslashish.",
        "Table splitting da barcha entity lar bir xil kalitga ega bo'lishi shart.",
        "Entity splitting har bir so'rovga `INNER JOIN` qo'shadi.",
        "Og'ir ustun bitta joyda ishlatilsa, splitting o'rniga oddiy proyeksiya ham "
        "yetarli bo'lishi mumkin.",
    ])

    sources(d, [
        ("Table Splitting — EF Core",
         "https://learn.microsoft.com/en-us/ef/core/modeling/table-splitting"),
        ("Entity Splitting — EF Core",
         "https://learn.microsoft.com/en-us/ef/core/modeling/entity-splitting"),
        ("What's New in EF Core 7.0 — Entity splitting",
         "https://learn.microsoft.com/en-us/ef/core/what-is-new/ef-core-7.0/whatsnew#entity-splitting"),
    ])
