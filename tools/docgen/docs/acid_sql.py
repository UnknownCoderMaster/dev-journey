# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "ACID"
CATEGORY = "SQL"
TITLE = "ACID — Tranzaksiya Kafolatlari"
SUBTITLE = "Atomiclik, izchillik, izolyatsiya va bardoshlilik"
FILENAME = "ACID.docx"


def build(d):
    h1(d, "1. Tranzaksiya nima")

    para(d, "Tranzaksiya — bitta mantiqiy amalni tashkil qiluvchi bir nechta "
            "operatsiyalar guruhi. Baza ular ustida to'rtta kafolatni beradi va "
            "bu kafolatlar ACID qisqartmasi ostida birlashtiriladi.")

    code(d, """BEGIN;
    UPDATE accounts SET balance = balance - 100000 WHERE id = 1;
    UPDATE accounts SET balance = balance + 100000 WHERE id = 2;
COMMIT;""")

    para(d, "Bu ikki amal alohida bajarilsa va orasida nosozlik yuz bersa, pul "
            "bir hisobdan chiqib, ikkinchisiga tushmay qoladi. Tranzaksiya "
            "bunday holatni oldini oladi.")

    # ───────────────────────────────────────────
    h1(d, "2. Atomicity — atomiclik")

    para(d, "Tranzaksiya bo'linmas birlik sifatida bajariladi: yo barcha "
            "operatsiyalar qo'llaniladi, yo hech biri. Oraliq holat mavjud "
            "bo'lmaydi.")

    code(d, """BEGIN;
    INSERT INTO orders (customer_id, total) VALUES (7, 150000);
    UPDATE products SET stock = stock - 3 WHERE id = 42;
    -- Bu yerda xatolik yuz bersa...
ROLLBACK;   -- ...ikkala o'zgarish ham bekor qilinadi""")

    para(d, "Baza buni jurnal (write-ahead log) orqali ta'minlaydi — o'zgarish "
            "avval jurnalga, keyin ma'lumot fayliga yoziladi. Nosozlik bo'lsa, "
            "jurnal asosida holat tiklanadi.")

    code(d, """// EF Core da SaveChanges o'zi tranzaksiya ochadi
db.Orders.Add(order);
product.Stock -= 3;
await db.SaveChangesAsync(ct);   // ikkalasi ham, yoki hech biri""")

    # ───────────────────────────────────────────
    h1(d, "3. Consistency — izchillik")

    para(d, "Tranzaksiya bazani bir to'g'ri holatdan boshqa to'g'ri holatga "
            "o'tkazadi. \"To'g'ri\" deganda barcha cheklovlarning bajarilishi "
            "tushuniladi: birlamchi va tashqi kalitlar, `NOT NULL`, `CHECK`, "
            "noyoblik.")

    code(d, """ALTER TABLE accounts
    ADD CONSTRAINT balance_non_negative CHECK (balance >= 0);""")

    code(d, """BEGIN;
    UPDATE accounts SET balance = balance - 1000000 WHERE id = 1;
    -- Agar natija manfiy bo'lsa, CHECK buzadi va tranzaksiya rad etiladi
COMMIT;""")

    note(d, "Bu harf eng ko'p chalkashtiradigan:",
         "Consistency bu yerda CAP teoremasidagi \"consistency\" bilan bir xil "
         "narsa **emas**. ACID dagi C — bazaning o'z cheklovlari buzilmasligi. "
         "CAP dagi C — taqsimlangan tizimda barcha tugunlar bir xil ma'lumotni "
         "ko'rishi. Ikkalasi bir xil so'z bilan atalgan, lekin turli "
         "muammolarni tasvirlaydi.")

    note(d, "Yana bir muhim tafsilot:",
         "Baza faqat **o'zi biladigan** qoidalarni ta'minlaydi. Agar men "
         "\"buyurtma summasi uning qatorlari yig'indisiga teng bo'lsin\" degan "
         "qoidani faqat C# kodida yozgan bo'lsam, baza uni bilmaydi va "
         "ta'minlamaydi. Shuning uchun muhim qoidalarni baza cheklovi sifatida "
         "ham ifodalashga harakat qilaman.")

    # ───────────────────────────────────────────
    h1(d, "4. Isolation — izolyatsiya")

    para(d, "Parallel bajarilayotgan tranzaksiyalar bir-biriga xalaqit "
            "bermasligi. Bu eng murakkab kafolat, chunki u to'liq ta'minlansa, "
            "unumdorlik keskin tushadi. Shuning uchun bir nechta daraja "
            "mavjud.")

    h2(d, "4.1 Izolyatsiyasiz yuzaga keladigan hodisalar")

    table(d, ["Hodisa", "Nima bo'ladi"],
          [["Dirty read", "Tasdiqlanmagan o'zgarish o'qiladi"],
           ["Non-repeatable read",
            "Bir xil satr ikki marta o'qilganda turlicha chiqadi"],
           ["Phantom read",
            "Bir xil shart bo'yicha ikki marta o'qilganda satrlar soni "
            "o'zgaradi"],
           ["Lost update",
            "Ikki tranzaksiya bir satrni yangilaydi, biri yo'qoladi"]],
          widths=[4.4, 11.1])

    h2(d, "4.2 Izolyatsiya darajalari")

    table(d, ["Daraja", "Dirty", "Non-repeatable", "Phantom"],
          [["Read Uncommitted", "Mumkin", "Mumkin", "Mumkin"],
           ["Read Committed", "Yo'q", "Mumkin", "Mumkin"],
           ["Repeatable Read", "Yo'q", "Yo'q", "Mumkin"],
           ["Serializable", "Yo'q", "Yo'q", "Yo'q"]],
          widths=[5.1, 3.4, 4.0, 3.0])

    para(d, "PostgreSQL da sukutdagi daraja — `Read Committed`. Shuni ham qayd "
            "etish kerakki, PostgreSQL `Read Uncommitted` ni qabul qiladi, lekin "
            "u amalda `Read Committed` kabi ishlaydi.")

    code(d, """-- Sessiya uchun
SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;

-- Yoki bitta tranzaksiya uchun
BEGIN ISOLATION LEVEL SERIALIZABLE;""")

    code(d, """await using var tx = await db.Database.BeginTransactionAsync(
    System.Data.IsolationLevel.Serializable, ct);""")

    note(d, "Yuqori daraja — bepul emas:",
         "`Serializable` eng kuchli kafolat beradi, lekin PostgreSQL da u "
         "tranzaksiyani rad etishi mumkin — `could not serialize access` "
         "xatosi bilan. Ya'ni ilova qayta urinishga tayyor bo'lishi kerak. "
         "Agar men buni hisobga olmasam, yuk ortganda tasodifiy xatolar "
         "paydo bo'ladi.")

    h2(d, "4.3 Lost update va uni oldini olish")

    code(d, """-- Ikki tranzaksiya bir vaqtda
-- T1: SELECT stock FROM products WHERE id=1;   → 10
-- T2: SELECT stock FROM products WHERE id=1;   → 10
-- T1: UPDATE products SET stock = 7 WHERE id=1;
-- T2: UPDATE products SET stock = 8 WHERE id=1;   ← T1 ning o'zgarishi yo'qoldi""")

    para(d, "Yechimlar uchta: atomar yangilash, pessimistik qulf yoki "
            "optimistik parallellik nazorati.")

    code(d, """-- 1. Atomar yangilash — eng oddiy
UPDATE products SET stock = stock - 3 WHERE id = 1 AND stock >= 3;""")

    code(d, """-- 2. Pessimistik qulf
SELECT * FROM products WHERE id = 1 FOR UPDATE;""")

    code(d, """// 3. Optimistik — EF Core da
modelBuilder.Entity<Product>()
    .Property(p => p.Version)
    .IsRowVersion();

// Konflikt bo'lsa DbUpdateConcurrencyException otiladi
try
{
    await db.SaveChangesAsync(ct);
}
catch (DbUpdateConcurrencyException)
{
    // Qayta o'qib, qayta urinish
}""")

    note(d, "Qaysi birini tanlayman:",
         "Agar o'zgarish oddiy hisob bo'lsa — atomar `UPDATE` eng yaxshisi, "
         "chunki u umuman konflikt yaratmaydi. Agar foydalanuvchi formani uzoq "
         "to'ldirib o'tirsa — optimistik nazorat, chunki pessimistik qulf butun "
         "shu vaqt davomida satrni bloklab turadi. Pessimistik qulfni esa faqat "
         "qisqa va kritik operatsiyalarda ishlataman.")

    # ───────────────────────────────────────────
    h1(d, "5. Durability — bardoshlilik")

    para(d, "Tasdiqlangan tranzaksiya saqlanib qoladi — hatto shu zahoti "
            "elektr o'chsa ham. Bu write-ahead log orqali ta'minlanadi: "
            "`COMMIT` javobi qaytishidan oldin jurnal diskga fizik yozilgan "
            "bo'lishi kerak.")

    code(d, """-- PostgreSQL sozlamalari
fsync = on                  -- diskka majburiy yozish
synchronous_commit = on     -- COMMIT jurnalni kutadi
wal_level = replica""")

    note(d, "`synchronous_commit = off` ni ko'rganimda tushundim:",
         "Bu sozlama yozish tezligini sezilarli oshiradi, chunki `COMMIT` "
         "diskni kutmaydi. Lekin evaziga — server to'satdan o'chsa, oxirgi bir "
         "necha tranzaksiya yo'qolishi mumkin. Ya'ni bu D harfini qisman "
         "savdoga qo'yish. Loglar yoki analitika uchun bu maqbul bo'lishi "
         "mumkin, to'lovlar uchun esa yo'q.")

    para(d, "Haqiqiy bardoshlilik uchun bitta server yetarli emas — disk ham "
            "ishdan chiqishi mumkin. Shuning uchun replikatsiya va zaxira "
            "nusxalar ham shu kafolatning bir qismi hisoblanadi.")

    # ───────────────────────────────────────────
    h1(d, "6. Amaliy maslahatlar")

    bullets(d, [
        "Tranzaksiyani iloji boricha qisqa tutish — u qulflarni ushlab turadi.",
        "Tranzaksiya ichida tashqi xizmatga murojaat qilmaslik.",
        "Foydalanuvchi kiritishini kutayotganda tranzaksiya ochiq "
        "qoldirmaslik.",
        "Bir xil jadvallarga bir xil tartibda murojaat qilish — bu deadlock "
        "ehtimolini kamaytiradi.",
        "`Serializable` ishlatilsa, qayta urinish mantiqini yozish.",
    ])

    code(d, """// Deadlock va serializatsiya xatosida qayta urinish
var strategy = db.Database.CreateExecutionStrategy();

await strategy.ExecuteAsync(async () =>
{
    await using var tx = await db.Database.BeginTransactionAsync(ct);
    // ... amallar
    await db.SaveChangesAsync(ct);
    await tx.CommitAsync(ct);
});""")

    # ───────────────────────────────────────────
    h1(d, "7. Xulosa")

    bullets(d, [
        "ACID — tranzaksiyalar uchun to'rtta kafolat.",
        "Atomicity: yo hammasi, yo hech biri — write-ahead log orqali.",
        "Consistency: baza cheklovlari buzilmaydi; bu CAP dagi C emas.",
        "Isolation: parallel tranzaksiyalar bir-biriga xalaqit bermaydi; "
        "to'rtta daraja mavjud.",
        "PostgreSQL da sukutdagi daraja — `Read Committed`.",
        "Lost update ni atomar `UPDATE`, pessimistik qulf yoki optimistik "
        "nazorat bilan yopish mumkin.",
        "Durability: tasdiqlangan o'zgarish saqlanadi; "
        "`synchronous_commit = off` buni qisman savdoga qo'yadi.",
        "Tranzaksiya qisqa bo'lishi va tashqi chaqiruvlarni o'z ichiga "
        "olmasligi kerak.",
    ])

    sources(d, [
        ("Transaction Isolation — PostgreSQL hujjati",
         "https://www.postgresql.org/docs/current/transaction-iso.html"),
        ("Reliability and the Write-Ahead Log — PostgreSQL",
         "https://www.postgresql.org/docs/current/wal.html"),
        ("Transactions — EF Core",
         "https://learn.microsoft.com/en-us/ef/core/saving/transactions"),
        ("Handling concurrency conflicts — EF Core",
         "https://learn.microsoft.com/en-us/ef/core/saving/concurrency"),
    ])
