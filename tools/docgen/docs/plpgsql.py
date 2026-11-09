# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "PLpgSQL (Functions, Procedure)"
CATEGORY = "Postgres / Oracle"
TITLE = "PL/pgSQL: Funksiya va Protsedura"
SUBTITLE = "Baza ichida mantiq yozish"
FILENAME = "PLpgSQL (Functions, Procedure).docx"


def build(d):
    h1(d, "1. PL/pgSQL nima")

    para(d, "SQL deklarativ til — unda \"nima kerak\" aytiladi, \"qanday "
            "qilish\" emas. Shart, sikl va o'zgaruvchi kabi protsessual "
            "tushunchalar unda yo'q.")

    para(d, "PL/pgSQL — PostgreSQL ga o'rnatilgan protsessual til. U SQL ni "
            "shart, sikl, o'zgaruvchi va istisno bilan to'ldiradi, ya'ni "
            "baza ichida to'liq mantiq yozish imkonini beradi.")

    note(d, "Nima uchun bu kerak bo'lishi mumkin:",
         "Agar amal ko'p ma'lumot bilan ishlasa va natija kichik bo'lsa, uni "
         "bazada bajarish tarmoq orqali hammasini tortib olishdan ancha "
         "tezroq. Masalan million satrni qayta hisoblash — ilovaga olib "
         "kelish uchun megabaytlab trafik kerak, bazada esa hech narsa "
         "uzatilmaydi.")

    # ───────────────────────────────────────────
    h1(d, "2. Funksiya")

    code(d, """CREATE OR REPLACE FUNCTION calculate_discount(
    customer_id bigint,
    order_total numeric
)
RETURNS numeric
LANGUAGE plpgsql
AS $$
DECLARE
    years_active int;
    discount_rate numeric;
BEGIN
    SELECT EXTRACT(YEAR FROM age(now(), created_at))
    INTO years_active
    FROM customers
    WHERE id = customer_id;

    IF years_active IS NULL THEN
        RAISE EXCEPTION 'Mijoz topilmadi: %', customer_id;
    END IF;

    discount_rate := CASE
        WHEN years_active >= 5 THEN 0.15
        WHEN years_active >= 2 THEN 0.10
        ELSE 0.05
    END;

    RETURN ROUND(order_total * discount_rate, 2);
END;
$$;""")

    code(d, """SELECT calculate_discount(7, 150000);""")

    h2(d, "2.1 Tuzilma elementlari")

    table(d, ["Qism", "Vazifasi"],
          [["`DECLARE`", "Lokal o'zgaruvchilar e'loni"],
           ["`BEGIN ... END`", "Asosiy blok"],
           ["`:=`", "Qiymat berish operatori"],
           ["`SELECT ... INTO`", "So'rov natijasini o'zgaruvchiga olish"],
           ["`RAISE`", "Xabar chiqarish yoki istisno otish"],
           ["`$$`", "Dollar bilan qo'shtirnoqlash — ichkarida qochirish "
                    "kerak emas"]],
          widths=[4.0, 11.5])

    h2(d, "2.2 Jadval qaytaruvchi funksiya")

    code(d, """CREATE OR REPLACE FUNCTION top_customers(limit_count int)
RETURNS TABLE (
    customer_id bigint,
    full_name text,
    total_spent numeric
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT c.id, c.full_name, SUM(o.total)
    FROM customers c
    JOIN orders o ON o.customer_id = c.id
    WHERE o.status = 'paid'
    GROUP BY c.id, c.full_name
    ORDER BY SUM(o.total) DESC
    LIMIT limit_count;
END;
$$;""")

    code(d, """SELECT * FROM top_customers(10);""")

    h2(d, "2.3 Volatillik toifalari")

    table(d, ["Toifa", "Ma'nosi"],
          [["`IMMUTABLE`", "Bir xil kirishga doim bir xil natija; bazaga "
                           "murojaat qilmaydi"],
           ["`STABLE`", "Bitta so'rov ichida natija o'zgarmaydi"],
           ["`VOLATILE`", "Har chaqiruvda o'zgarishi mumkin; sukutdagi "
                          "qiymat"]],
          widths=[3.4, 12.1])

    code(d, """CREATE FUNCTION slugify(input text)
RETURNS text
LANGUAGE plpgsql
IMMUTABLE
AS $$ ... $$;

-- IMMUTABLE bo'lgani uchun indeksda ishlatish mumkin
CREATE INDEX ix_articles_slug ON articles (slugify(title));""")

    note(d, "Bu belgini to'g'ri qo'yish unumdorlikka ta'sir qiladi:",
         "`IMMUTABLE` deb belgilangan funksiya natijasini planner keshlashi "
         "va uni indeksda ishlatishi mumkin. Lekin agar men bazaga murojaat "
         "qiladigan funksiyani xato bilan `IMMUTABLE` deb belgilasam, "
         "natijalar noto'g'ri bo'ladi va buni aniqlash juda qiyin.")

    # ───────────────────────────────────────────
    h1(d, "3. Protsedura")

    para(d, "PostgreSQL 11 dan boshlab protseduralar qo'shilgan. Funksiyadan "
            "asosiy farqi — protsedura ichida tranzaksiyani boshqarish "
            "mumkin.")

    code(d, """CREATE OR REPLACE PROCEDURE archive_old_orders(cutoff_date date)
LANGUAGE plpgsql
AS $$
DECLARE
    batch_size CONSTANT int := 1000;
    moved int;
BEGIN
    LOOP
        WITH batch AS (
            SELECT id FROM orders
            WHERE created_at < cutoff_date
            LIMIT batch_size
        ),
        archived AS (
            INSERT INTO orders_archive
            SELECT * FROM orders WHERE id IN (SELECT id FROM batch)
            RETURNING id
        )
        DELETE FROM orders WHERE id IN (SELECT id FROM archived);

        GET DIAGNOSTICS moved = ROW_COUNT;
        EXIT WHEN moved = 0;

        COMMIT;        -- funksiyada bu mumkin emas
        RAISE NOTICE '% ta buyurtma arxivlandi', moved;
    END LOOP;
END;
$$;""")

    code(d, """CALL archive_old_orders('2025-01-01');""")

    table(d, ["Jihat", "Funksiya", "Protsedura"],
          [["Chaqirish", "`SELECT`", "`CALL`"],
           ["Qiymat qaytaradi", "Ha", "Faqat `INOUT` orqali"],
           ["So'rov ichida ishlatish", "Mumkin", "Mumkin emas"],
           ["Tranzaksiya boshqaruvi", "Mumkin emas", "Mumkin"]],
          widths=[4.6, 5.4, 5.5])

    note(d, "`COMMIT` imkoniyati nega muhim:",
         "Million satrni bitta tranzaksiyada ko'chirsam, u butun jarayon "
         "davomida qulflarni ushlab turadi va jurnal o'sib ketadi. "
         "Protsedurada esa har ming satrdan keyin tasdiqlab, keyingisiga "
         "o'taman. Bu uzoq davom etadigan ommaviy amallar uchun ancha "
         "xavfsizroq.")

    # ───────────────────────────────────────────
    h1(d, "4. Istisnolar bilan ishlash")

    code(d, """CREATE OR REPLACE FUNCTION transfer_funds(
    from_account bigint,
    to_account bigint,
    amount numeric
)
RETURNS boolean
LANGUAGE plpgsql
AS $$
BEGIN
    UPDATE accounts SET balance = balance - amount
    WHERE id = from_account AND balance >= amount;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Mablag'' yetarli emas'
            USING ERRCODE = 'P0001';
    END IF;

    UPDATE accounts SET balance = balance + amount WHERE id = to_account;
    RETURN true;

EXCEPTION
    WHEN foreign_key_violation THEN
        RAISE NOTICE 'Hisob topilmadi';
        RETURN false;
    WHEN OTHERS THEN
        RAISE;        -- qayta otish
END;
$$;""")

    note(d, "`EXCEPTION` bloki haqida muhim tafsilot:",
         "U PostgreSQL da subtranzaksiya yaratadi, ya'ni qo'shimcha xarajat "
         "qo'shadi. Agar men uni sikl ichiga qo'ysam va sikl million marta "
         "aylansa, bu sezilarli sekinlashishga olib keladi. Shuning uchun "
         "`EXCEPTION` ni faqat haqiqatan kerak joyda ishlataman.")

    # ───────────────────────────────────────────
    h1(d, "5. EF Core dan chaqirish")

    code(d, """// Skalyar funksiya
[DbFunction("calculate_discount", "public")]
public static decimal CalculateDiscount(long customerId, decimal total)
    => throw new NotSupportedException();

// So'rovda ishlatish
var orders = await db.Orders
    .Select(o => new
    {
        o.Id,
        Discount = AppDbContext.CalculateDiscount(o.CustomerId, o.Total)
    })
    .ToListAsync(ct);""")

    code(d, """// Jadval qaytaruvchi funksiya
var top = await db.Database
    .SqlQuery<TopCustomerDto>($"SELECT * FROM top_customers({10})")
    .ToListAsync(ct);""")

    code(d, """// Protsedura
await db.Database.ExecuteSqlAsync(
    $"CALL archive_old_orders({cutoffDate})", ct);""")

    # ───────────────────────────────────────────
    h1(d, "6. Qachon bazada mantiq yozish kerak")

    para(d, "Bu masala bo'yicha fikrlar keskin bo'linadi, shuning uchun "
            "ikki tomonni ham ko'rib chiqish foydali.")

    table(d, ["Bazada yozish foydali", "Ilovada yozish afzal"],
          [["Ko'p ma'lumot, kichik natija", "Murakkab biznes qoidalari"],
           ["Ommaviy ma'lumot ko'chirish", "Tez-tez o'zgaradigan mantiq"],
           ["Bir nechta tizim ishlatadigan qoida", "Birlik testlari zarur "
                                                   "bo'lganda"],
           ["Baza butunligini ta'minlash", "Tashqi xizmatga murojaat kerak "
                                           "bo'lsa"]],
          widths=[7.7, 7.8])

    note(d, "Mening yondashuvim:",
         "Biznes mantiqni ilovada yozaman — u yerda versiya nazorati, "
         "testlar, nosozlikni topish vositalari va kod ko'rib chiqish bor. "
         "Bazada esa faqat ma'lumot bilan zich bog'liq narsalarni yozaman: "
         "ommaviy ko'chirish, murakkab agregatsiya, butunlikni ta'minlovchi "
         "trigger lar.")

    note(d, "Baza funksiyalarining eng katta kamchiligi:",
         "Ular odatiy ishlab chiqish jarayonidan tashqarida qoladi. Migratsiya "
         "orqali versiyalanmasa, kim qachon o'zgartirganini bilib bo'lmaydi. "
         "Shuning uchun men ularni albatta migratsiya fayliga yozaman — "
         "o'shanda ular ham git tarixiga tushadi.")

    code(d, """migrationBuilder.Sql(@"
    CREATE OR REPLACE FUNCTION calculate_discount(...)
    ...
");""")

    # ───────────────────────────────────────────
    h1(d, "7. Nosozlikni topish")

    code(d, """-- Xabar chiqarish
RAISE NOTICE 'Qiymat: %, Holat: %', value, status;

-- Darajalar: DEBUG, LOG, INFO, NOTICE, WARNING, EXCEPTION""")

    code(d, """-- Mavjud funksiyalarni ko'rish
SELECT routine_name, routine_type
FROM information_schema.routines
WHERE routine_schema = 'public';

-- Manbasini o'qish
SELECT prosrc FROM pg_proc WHERE proname = 'calculate_discount';""")

    # ───────────────────────────────────────────
    h1(d, "8. Xulosa")

    bullets(d, [
        "PL/pgSQL SQL ga shart, sikl, o'zgaruvchi va istisno qo'shadi.",
        "Funksiya `SELECT` bilan chaqiriladi va so'rov ichida ishlatiladi.",
        "Protsedura `CALL` bilan chaqiriladi va tranzaksiyani boshqara "
        "oladi.",
        "Volatillik toifasi (`IMMUTABLE`, `STABLE`, `VOLATILE`) planner "
        "qaroriga ta'sir qiladi.",
        "`EXCEPTION` bloki subtranzaksiya yaratadi — sikl ichida qimmatga "
        "tushadi.",
        "EF Core dan `DbFunction`, `SqlQuery` va `ExecuteSqlAsync` orqali "
        "chaqiriladi.",
        "Biznes mantiq ilovada, ma'lumot bilan zich bog'liq amallar bazada "
        "bo'lgani ma'qul.",
        "Baza funksiyalarini migratsiya orqali versiyalash shart.",
    ])

    sources(d, [
        ("PL/pgSQL — SQL Procedural Language — PostgreSQL hujjati",
         "https://www.postgresql.org/docs/current/plpgsql.html"),
        ("CREATE PROCEDURE — PostgreSQL hujjati",
         "https://www.postgresql.org/docs/current/sql-createprocedure.html"),
        ("Function Volatility Categories — PostgreSQL",
         "https://www.postgresql.org/docs/current/xfunc-volatility.html"),
        ("User-defined function mapping — EF Core",
         "https://learn.microsoft.com/en-us/ef/core/querying/user-defined-function-mapping"),
    ])
