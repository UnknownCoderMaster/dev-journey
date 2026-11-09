# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "Configuring sequence settings"
CATEGORY = "EF CORE"
TITLE = "Sequence Sozlamalari"
SUBTITLE = "Ketma-ket raqam generatori va uning xususiyatlari"
FILENAME = "Configuring sequence settings.docx"


def build(d):
    h1(d, "1. Sequence nima")

    para(d, "Sequence — bazadagi mustaqil obyekt, u so'ralganda keyingi "
            "raqamni qaytaradi. Identity ustunidan farqi shundaki, "
            "sequence **jadvalga bog'lanmagan**: uni bir nechta jadval "
            "ulashishi mumkin yoki undan ilova o'zi raqam so'rashi mumkin.")

    code(d, """modelBuilder.HasSequence<long>("order_numbers")
    .StartsAt(1000)
    .IncrementsBy(1);""")

    code(d, """modelBuilder.Entity<Order>()
    .Property(o => o.Number)
    .HasDefaultValueSql("nextval('order_numbers')");""")

    # ───────────────────────────────────────────
    h1(d, "2. Sozlamalar")

    code(d, """modelBuilder.HasSequence<long>("invoice_numbers", schema: "billing")
    .StartsAt(100_000)
    .IncrementsBy(1)
    .HasMin(100_000)
    .HasMax(999_999)
    .IsCyclic(false);""")

    table(d, ["Sozlama", "Vazifasi"],
          [["`StartsAt`", "Boshlang'ich qiymat"],
           ["`IncrementsBy`", "Qadam; manfiy bo'lsa kamayib boradi"],
           ["`HasMin` / `HasMax`", "Diapazon chegaralari"],
           ["`IsCyclic`", "Chegaraga yetganda boshidan davom etadimi"],
           ["`schema`", "Qaysi sxemada yaratilishi"]],
          widths=[4.6, 9.9])

    para(d, "`IsCyclic(true)` ni ehtiyot bilan ishlatish kerak: "
            "chegaraga yetganda raqamlar **takrorlanadi**, ya'ni unikal "
            "kalit uchun yaramaydi. U faqat aylanma hisoblagich kerak "
            "bo'lganda mos.")

    # ───────────────────────────────────────────
    h1(d, "3. Hi-Lo naqshi")

    para(d, "Sequence'ning eng foydali qo'llanishi — Hi-Lo. Ilova "
            "sequence'dan **bir blok** raqam oladi va keyin uni "
            "xotirada taqsimlaydi. Natijada har bir yangi entity uchun "
            "bazaga murojaat qilish kerak emas:")

    code(d, """modelBuilder.Entity<Order>()
    .Property(o => o.Id)
    .UseHiLo("order_ids");""")

    para(d, "Afzalligi — kalit **bazaga yozishdan oldin** ma'lum "
            "bo'ladi. Bu bog'liq obyektlar grafini qurishda va bulk "
            "insert'da sezilarli yutuq: `SaveChanges` dan oldin hamma "
            "ID tayyor, shuning uchun EF `INSERT` larni "
            "birlashtirishi mumkin.")

    para(d, "Narxi — har bir blok to'liq ishlatilmasa, raqamlar "
            "yo'qoladi. Ilova qayta ishga tushganda yangi blok olinadi "
            "va eski blokning qolgan raqamlari boshqa hech kimga "
            "berilmaydi.")

    note(d, "Npgsql'da",
         "Postgres uchun `UseHiLo` qo'llanadi, lekin amalda ko'pincha "
            "`Guid` v7 yoki `IDENTITY` yetarli bo'ladi. Hi-Lo ni "
            "faqat yozish hajmi juda katta va `int`/`long` kalit "
            "majburiy bo'lganda tanlayman.")

    # ───────────────────────────────────────────
    h1(d, "4. TPC bilan umumiy sequence")

    para(d, "Table-per-concrete-type strategiyasida har bir konkret tur "
            "o'z jadvalida yashaydi. Agar har biri o'z identity'sidan "
            "foydalansa, ID'lar takrorlanadi — `CardPayment` da 1 va "
            "`CashPayment` da ham 1 bo'ladi. Ierarxiya bo'yicha "
            "polimorf so'rovda bu chalkashlik keltiradi.")

    code(d, """modelBuilder.HasSequence<long>("payment_ids");

modelBuilder.Entity<Payment>()
    .UseTpcMappingStrategy()
    .Property(p => p.Id)
    .HasDefaultValueSql("nextval('payment_ids')");""")

    para(d, "Umumiy sequence butun ierarxiya bo'ylab unikal ID beradi. "
            "Bu TPC ni ishlatishning majburiy shartlaridan biri.")

    # ───────────────────────────────────────────
    h1(d, "5. Sequence'ning muhim xususiyati: bo'shliq")

    para(d, "Sequence **tranzaksiyadan tashqarida** ishlaydi. Shuning "
            "uchun tranzaksiya rollback bo'lsa, olingan raqam "
            "**qaytmaydi**:")

    code(d, """-- Tranzaksiya 1
BEGIN;
SELECT nextval('order_numbers');    -- 1001
ROLLBACK;                           -- 1001 yo'qoldi

-- Tranzaksiya 2
SELECT nextval('order_numbers');    -- 1002, 1001 emas""")

    para(d, "Bu nosozlik emas — ataylab shunday. Agar sequence "
            "tranzaksiya ichida bo'lsa, u har bir murojaatni qulflashi "
            "kerak bo'lardi va parallel yozish imkonsiz bo'lib "
            "qolardi.")

    para(d, "Amaliy xulosa: **sequence uzluksizlikni kafolatlamaydi, "
            "faqat unikallikni**. Shuning uchun uni quyidagi joylarda "
            "ishlatmayman:")

    bullets(d, [
        "Qonun talab qiladigan uzluksiz hujjat raqami (hisob-faktura, "
        "chek) — auditor bo'shliqni so'raydi.",
        "Foydalanuvchiga \"nechanchi buyurtma\" deb ko'rsatiladigan "
        "raqam — mijoz 1001 dan keyin 1005 ni ko'rsa savol beradi.",
    ])

    para(d, "Uzluksiz raqam haqiqatan kerak bo'lsa, alohida jadval va "
            "qulflash kerak bo'ladi — bu parallel yozishni "
            "sekinlashtiradi, lekin boshqa yo'l yo'q:")

    code(d, """-- Tranzaksiya ichida satrni qulflab olish
SELECT next_value FROM document_counters
WHERE counter_name = 'invoice'
FOR UPDATE;

UPDATE document_counters
SET next_value = next_value + 1
WHERE counter_name = 'invoice';""")

    # ───────────────────────────────────────────
    h1(d, "6. CACHE sozlamasi")

    para(d, "Postgres'da sequence uchun `CACHE` qiymati har bir ulanish "
            "oldindan oladigan raqamlar sonini belgilaydi:")

    code(d, """CREATE SEQUENCE order_numbers CACHE 50;""")

    para(d, "Bu tezlikni oshiradi, chunki har bir `nextval` uchun "
            "WAL yozish kerak bo'lmaydi. Lekin ikki ta'siri bor: "
            "bo'shliqlar kattalashadi (ulanish yopilganda 50 ta "
            "raqam yo'qoladi) va parallel ulanishlarda raqamlar "
            "**tartibsiz** keladi — ikkinchi ulanish 51 dan "
            "boshlaydi, birinchisi hali 10 da bo'lsa ham.")

    para(d, "Shuning uchun `CACHE 1` (standart) ni qoldiraman, "
            "yuklama haqiqatan juda katta bo'lmasa.")

    # ───────────────────────────────────────────
    h1(d, "7. Sequence'ni boshqarish")

    code(d, """-- Joriy qiymatni ko'rish (nextval chaqirmasdan)
SELECT last_value, log_cnt, is_called FROM order_numbers;

-- Qiymatni o'zgartirish — ma'lumot ko'chirishdan keyin kerak bo'ladi
SELECT setval('order_numbers', (SELECT COALESCE(MAX(number), 0) FROM orders));""")

    para(d, "`setval` ni ma'lumot migratsiyasidan keyin ishlatish kerak "
            "bo'ladi: eski tizimdan 5000 satr ko'chirilsa va sequence "
            "1 da qolsa, keyingi `INSERT` darhol unikal kalit xatosi "
            "beradi. Bu juda ko'p uchraydigan ko'chirish xatosi.")

    sources(d, [
        ("Sequences — EF Core",
         "https://learn.microsoft.com/en-us/ef/core/modeling/sequences"),
        ("Generated values — EF Core",
         "https://learn.microsoft.com/en-us/ef/core/modeling/generated-properties"),
        ("CREATE SEQUENCE — PostgreSQL",
         "https://www.postgresql.org/docs/current/sql-createsequence.html"),
        ("Sequence manipulation functions",
         "https://www.postgresql.org/docs/current/functions-sequence.html"),
    ])
