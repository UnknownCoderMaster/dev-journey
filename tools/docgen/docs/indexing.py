# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "Indexing"
CATEGORY = "Database Design Principles"
TITLE = "Indekslash"
SUBTITLE = "Qidiruvni tezlashtirish va uning narxi"
FILENAME = "Indexing.docx"


def build(d):
    h1(d, "1. Indeks nima qiladi")

    para(d, "Indekssiz jadvalda qidirish uchun baza barcha satrlarni o'qib "
            "chiqishi kerak — bu ketma-ket skan (sequential scan) deb ataladi. "
            "Indeks esa tartiblangan tuzilma bo'lib, kerakli satrni "
            "to'g'ridan-to'g'ri topish imkonini beradi.")

    code(d, """CREATE INDEX ix_orders_customer_id ON orders (customer_id);""")

    para(d, "Taqqoslash uchun: million satrli jadvalda indekssiz qidiruv "
            "million marta tekshirish talab qiladi. B-tree indeks bilan esa "
            "taxminan yigirma qadamda natija topiladi.")

    note(d, "Lekin indeks bepul emas:",
         "Har bir `INSERT`, `UPDATE` va `DELETE` barcha tegishli indekslarni "
         "ham yangilashi kerak. Ya'ni men o'qishni tezlashtirib, yozishni "
         "sekinlashtiraman. Bundan tashqari indeks disk joyini egallaydi — "
         "ba'zan jadvalning o'zidan ko'proq.")

    # ───────────────────────────────────────────
    h1(d, "2. Indeks turlari")

    table(d, ["Turi", "Nimaga mos"],
          [["B-tree", "Tenglik va diapazon; sukutdagi tur"],
           ["Hash", "Faqat tenglik"],
           ["GIN", "Massiv, `jsonb`, to'liq matnli qidiruv"],
           ["GiST", "Fazoviy ma'lumot, diapazonlar"],
           ["BRIN", "Juda katta, fizik tartiblangan jadvallar"]],
          widths=[3.0, 12.5])

    code(d, """CREATE INDEX ix_articles_tags ON articles USING GIN (tags);
CREATE INDEX ix_branches_location ON branches USING GIST (location);
CREATE INDEX ix_logs_created ON logs USING BRIN (created_at);""")

    note(d, "Amalda deyarli har doim B-tree:",
         "U tenglik, diapazon, saralash va `LIKE 'abc%'` — hammasini qoplaydi. "
         "Boshqa turlar faqat maxsus holatlarda kerak bo'ladi. Shuning uchun "
         "indeks turini tanlash odatda umuman masala emas.")

    # ───────────────────────────────────────────
    h1(d, "3. Kompozit indekslar va ustunlar tartibi")

    code(d, """CREATE INDEX ix_orders_customer_status_date
    ON orders (customer_id, status, created_at);""")

    para(d, "Kompozit indeksda ustunlar tartibi hal qiluvchi ahamiyatga ega. "
            "Indeks faqat **chapdan boshlab** ketma-ket ishlatiladi:")

    table(d, ["So'rov sharti", "Indeks ishlaydimi"],
          [["`customer_id = 7`", "Ha"],
           ["`customer_id = 7 AND status = 'paid'`", "Ha"],
           ["`customer_id = 7 AND status = 'paid' AND created_at > ...`", "Ha"],
           ["`status = 'paid'`", "Yo'q — chapdagi ustun yo'q"],
           ["`customer_id = 7 AND created_at > ...`", "Qisman"]],
          widths=[9.5, 6.0])

    note(d, "Bu qoidani telefon kitobi bilan tushuntirish oson:",
         "Kitob familiya, keyin ism bo'yicha tartiblangan. Familiyani bilsam, "
         "tez topaman. Familiya va ismni bilsam — yanada tez. Lekin faqat "
         "ismni bilsam, butun kitobni varaqlashim kerak. Indeks ham xuddi "
         "shunday ishlaydi.")

    h2(d, "3.1 Tartibni tanlash")

    bullets(d, [
        "Tenglik bo'yicha filtrlanadigan ustunlar oldinda.",
        "Diapazon shartlari oxirida.",
        "Tanlovchanligi yuqori (ko'p turli qiymatli) ustunlar oldinroq.",
    ])

    code(d, """-- So'rov: WHERE status = 'paid' AND created_at BETWEEN ... AND ...
-- To'g'ri tartib:
CREATE INDEX ix_orders_status_created ON orders (status, created_at);

-- Noto'g'ri — diapazon oldinda, keyingi ustun samarasiz
CREATE INDEX ix_orders_created_status ON orders (created_at, status);""")

    # ───────────────────────────────────────────
    h1(d, "4. Maxsus indeks turlari")

    h2(d, "4.1 Noyob indeks")

    code(d, """CREATE UNIQUE INDEX ux_users_email ON users (email);""")

    h2(d, "4.2 Qisman indeks")

    code(d, """-- Faqat faol yozuvlar indekslanadi
CREATE INDEX ix_orders_pending
    ON orders (created_at)
    WHERE status = 'pending';""")

    para(d, "Qisman indeks kichikroq bo'ladi va tezroq yangilanadi. Agar "
            "jadvalning 95% i `completed` bo'lsa va men faqat `pending` "
            "larni qidirsam, bu sezilarli yutuq beradi.")

    h2(d, "4.3 Ifoda bo'yicha indeks")

    code(d, """-- Registrsiz qidiruv uchun
CREATE INDEX ix_users_email_lower ON users (LOWER(email));

-- Endi bu so'rov indeksdan foydalanadi
SELECT * FROM users WHERE LOWER(email) = 'ali@example.com';""")

    note(d, "Bu juda ko'p uchraydigan muammoni hal qiladi:",
         "`WHERE LOWER(email) = ...` yozsam, oddiy `email` indeksi "
         "ishlamaydi — chunki indeksda asl qiymat, so'rovda esa o'zgartirilgan "
         "qiymat. Baza bunday holatda butun jadvalni skan qiladi. Ifoda "
         "bo'yicha indeks aynan shu bo'shliqni yopadi.")

    h2(d, "4.4 Qamrovchi indeks")

    code(d, """CREATE INDEX ix_orders_customer_covering
    ON orders (customer_id)
    INCLUDE (total, created_at);""")

    para(d, "`INCLUDE` dagi ustunlar indeksda saqlanadi, lekin tartiblash "
            "uchun ishlatilmaydi. Agar so'rovga kerakli barcha ustunlar "
            "indeksda bo'lsa, baza jadvalga umuman murojaat qilmaydi — bu "
            "index-only scan deb ataladi.")

    # ───────────────────────────────────────────
    h1(d, "5. Indeks ishlamaydigan holatlar")

    bullets(d, [
        "**Ustun funksiya ichida** — `WHERE YEAR(created_at) = 2026`.",
        "**`LIKE` boshida joker** — `WHERE name LIKE '%ali%'`.",
        "**Tip mos kelmasligi** — `WHERE id = '7'` (matn va son).",
        "**`OR` bilan turli ustunlar** — ba'zan indeks tashlab ketiladi.",
        "**Juda ko'p satr qaytganda** — jadval skani arzonroq bo'lsa, "
        "planner indeksdan voz kechadi.",
    ])

    code(d, """-- Indeks ishlamaydi
WHERE EXTRACT(YEAR FROM created_at) = 2026;

-- Indeks ishlaydi
WHERE created_at >= '2026-01-01' AND created_at < '2027-01-01';""")

    note(d, "Oxirgi punkt ko'pchilikni hayratga soladi:",
         "Ba'zan indeks bor, lekin baza uni ishlatmaydi — va bu **to'g'ri** "
         "qaror bo'lishi mumkin. Agar so'rov jadvalning yarmini qaytarsa, "
         "indeks orqali borish ketma-ket skandan sekinroq bo'ladi, chunki "
         "har bir satr uchun alohida diskka murojaat qilinadi. Planner buni "
         "statistika asosida hisoblaydi.")

    # ───────────────────────────────────────────
    h1(d, "6. So'rov rejasini o'qish")

    code(d, """EXPLAIN ANALYZE
SELECT * FROM orders
WHERE customer_id = 7 AND status = 'paid';""")

    code(d, """Index Scan using ix_orders_customer_status on orders
  (cost=0.43..8.45 rows=1 width=64)
  (actual time=0.025..0.027 rows=3 loops=1)
  Index Cond: ((customer_id = 7) AND (status = 'paid'::text))
Planning Time: 0.112 ms
Execution Time: 0.045 ms""")

    table(d, ["Qator", "Ma'nosi"],
          [["`Seq Scan`", "Butun jadval o'qilyapti — indeks ishlatilmagan"],
           ["`Index Scan`", "Indeks orqali, keyin jadvaldan o'qiladi"],
           ["`Index Only Scan`", "Faqat indeksdan — eng tez variant"],
           ["`Bitmap Heap Scan`", "Ko'p satr uchun indeks; oraliq variant"],
           ["`rows` farqi", "Taxmin va haqiqat farqi — statistika eskirgan "
                            "bo'lishi mumkin"]],
          widths=[4.4, 11.1])

    note(d, "`rows` qiymatlariga alohida qarayman:",
         "Agar `rows=1` deb taxmin qilingan joyda `actual rows=50000` chiqsa, "
         "demak planner noto'g'ri qaror qabul qilgan — statistika eskirgan. "
         "`ANALYZE orders;` buyrug'i uni yangilaydi va so'rov rejasi "
         "butunlay o'zgarishi mumkin.")

    # ───────────────────────────────────────────
    h1(d, "7. Indekslarni boshqarish")

    h2(d, "7.1 Ishlatilmayotganlarini topish")

    code(d, """SELECT schemaname, relname, indexrelname, idx_scan,
       pg_size_pretty(pg_relation_size(indexrelid)) AS size
FROM pg_stat_user_indexes
WHERE idx_scan = 0
ORDER BY pg_relation_size(indexrelid) DESC;""")

    para(d, "`idx_scan = 0` — indeks hech qachon ishlatilmagan. Bunday "
            "indekslar faqat yozishni sekinlashtiradi va joy egallaydi.")

    h2(d, "7.2 Bloklanmasdan yaratish")

    code(d, """CREATE INDEX CONCURRENTLY ix_orders_status ON orders (status);""")

    note(d, "Production da bu majburiy:",
         "Oddiy `CREATE INDEX` jadvalga yozishni butunlay bloklaydi. Katta "
         "jadvalda bu bir necha daqiqa davom etishi mumkin — ya'ni ilova "
         "shu vaqt davomida ishlamaydi. `CONCURRENTLY` sekinroq ishlaydi, "
         "lekin bloklamaydi. Uning sharti — tranzaksiya ichida "
         "bajarilmasligi.")

    h2(d, "7.3 Takrorlanuvchi indekslar")

    code(d, """-- Bu ikkinchisi ortiqcha — birinchisi uni qamrab oladi
CREATE INDEX ix_a ON orders (customer_id, status);
CREATE INDEX ix_b ON orders (customer_id);          -- keraksiz""")

    # ───────────────────────────────────────────
    h1(d, "8. EF Core da indekslar")

    code(d, """modelBuilder.Entity<Order>(e =>
{
    e.HasIndex(o => o.CustomerId);

    e.HasIndex(o => new { o.CustomerId, o.Status, o.CreatedAt })
     .HasDatabaseName("ix_orders_customer_status_created");

    e.HasIndex(o => o.Number).IsUnique();

    e.HasIndex(o => o.CreatedAt)
     .HasFilter("\\"Status\\" = 'pending'");
});""")

    para(d, "EF Core tashqi kalitlar uchun indeksni avtomatik yaratadi. "
            "Bu konventsiyani o'chirish ham mumkin:")

    code(d, """configurationBuilder.Conventions.Remove(typeof(ForeignKeyIndexConvention));""")

    # ───────────────────────────────────────────
    h1(d, "9. Amaliy yondashuv")

    bullets(d, [
        "Indeksni oldindan emas, o'lchov asosida qo'shish.",
        "Sekin so'rovlarni `pg_stat_statements` orqali aniqlash.",
        "Har bir indeksni `EXPLAIN ANALYZE` bilan tekshirish.",
        "Ishlatilmayotgan indekslarni muntazam tozalash.",
        "Jadvalga indeks soni 5-6 tadan oshsa, qayta ko'rib chiqish.",
    ])

    note(d, "O'zimga qo'ygan qoida:",
         "Har bir indeks — o'qish uchun foyda, yozish uchun xarajat. "
         "Shuning uchun \"ehtimol kerak bo'lar\" deb indeks qo'ymayman. "
         "Avval so'rov sekin ekanini ko'raman, keyin rejasini o'qiyman, "
         "keyin indeks qo'shaman va yana o'lchayman. Bu tartib menga bir "
         "necha marta keraksiz indeksdan qutqargan.")

    # ───────────────────────────────────────────
    h1(d, "10. Xulosa")

    bullets(d, [
        "Indeks o'qishni tezlashtiradi, yozishni sekinlashtiradi va joy "
        "egallaydi.",
        "B-tree sukutdagi va deyarli har doim to'g'ri tanlov.",
        "Kompozit indeks faqat chapdan boshlab ketma-ket ishlatiladi.",
        "Tenglik shartlari oldinda, diapazon oxirida bo'lishi kerak.",
        "Qisman va ifoda bo'yicha indekslar maxsus holatlarni yopadi.",
        "Ustun funksiya ichida bo'lsa, oddiy indeks ishlamaydi.",
        "Baza ko'p satr qaytadigan so'rovda indeksdan ongli ravishda voz "
        "kechishi mumkin.",
        "Production da `CREATE INDEX CONCURRENTLY` ishlatish kerak.",
        "`pg_stat_user_indexes` ishlatilmayotgan indekslarni ko'rsatadi.",
    ])

    sources(d, [
        ("Indexes — PostgreSQL hujjati",
         "https://www.postgresql.org/docs/current/indexes.html"),
        ("Using EXPLAIN — PostgreSQL hujjati",
         "https://www.postgresql.org/docs/current/using-explain.html"),
        ("Indexes — EF Core",
         "https://learn.microsoft.com/en-us/ef/core/modeling/indexes"),
        ("pg_stat_statements — PostgreSQL hujjati",
         "https://www.postgresql.org/docs/current/pgstatstatements.html"),
    ])
