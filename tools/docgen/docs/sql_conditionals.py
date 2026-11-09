# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "Shart operatorlari (IF ELSE)"
CATEGORY = "Postgres / Oracle"
TITLE = "SQL va PL/pgSQL da Shart Operatorlari"
SUBTITLE = "CASE, IF, COALESCE va NULL bilan bog'liq tuzoqlar"
FILENAME = "Shart operatorlari (IF ELSE).docx"


def build(d):
    h1(d, "1. Ikki darajadagi shartlar")

    para(d, "SQL da shartlar ikki joyda uchraydi va ular turli vositalar "
            "bilan ifodalanadi:")

    bullets(d, [
        "**So'rov ichida** — `CASE` ifodasi. U qiymat qaytaradi va "
        "`SELECT`, `WHERE`, `ORDER BY` da ishlatiladi.",
        "**Protsessual kodda** — `IF ... THEN ... ELSE`. U PL/pgSQL "
        "blokida, funksiya yoki trigger ichida ishlatiladi.",
    ])

    para(d, "Farq muhim: `CASE` — ifoda, `IF` — buyruq. `CASE` ni so'rovga "
            "qo'yish mumkin, `IF` ni esa mumkin emas.")

    # ───────────────────────────────────────────
    h1(d, "2. CASE ifodasi")

    h2(d, "2.1 Qidiruvli shakl")

    code(d, """SELECT
    id,
    total,
    CASE
        WHEN total >= 1000000 THEN 'VIP'
        WHEN total >= 500000  THEN 'Oltin'
        WHEN total >= 100000  THEN 'Kumush'
        ELSE 'Oddiy'
    END AS customer_tier
FROM orders;""")

    para(d, "Shartlar yuqoridan pastga tekshiriladi va birinchi mos kelgani "
            "tanlanadi. `ELSE` yozilmasa va hech bir shart bajarilmasa, "
            "natija `NULL` bo'ladi.")

    h2(d, "2.2 Oddiy shakl")

    code(d, """SELECT
    id,
    CASE status
        WHEN 'pending'   THEN 'Kutilmoqda'
        WHEN 'paid'      THEN 'To''langan'
        WHEN 'cancelled' THEN 'Bekor qilingan'
        ELSE 'Noma''lum'
    END AS status_text
FROM orders;""")

    note(d, "Oddiy shaklda bitta cheklov bor:",
         "U `=` orqali taqqoslaydi, demak `NULL` bilan hech qachon mos "
         "kelmaydi. `WHEN NULL THEN ...` deb yozsam, u hech qachon "
         "ishlamaydi — chunki `NULL = NULL` natijasi `NULL`, rost emas. "
         "`NULL` ni ushlash uchun qidiruvli shakl va `IS NULL` kerak.")

    code(d, """-- Ishlamaydi
CASE status WHEN NULL THEN 'Yo''q' ELSE 'Bor' END

-- Ishlaydi
CASE WHEN status IS NULL THEN 'Yo''q' ELSE 'Bor' END""")

    h2(d, "2.3 CASE ni turli joylarda ishlatish")

    code(d, """-- Saralashda
SELECT * FROM orders
ORDER BY
    CASE status
        WHEN 'urgent'  THEN 1
        WHEN 'pending' THEN 2
        ELSE 3
    END,
    created_at DESC;""")

    code(d, """-- Agregatsiyada — shartli hisoblash
SELECT
    date_trunc('month', created_at) AS month,
    COUNT(*) AS total,
    COUNT(*) FILTER (WHERE status = 'paid') AS paid,
    SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) AS cancelled
FROM orders
GROUP BY 1;""")

    note(d, "`FILTER` — PostgreSQL ning qulay qo'shimchasi:",
         "`COUNT(*) FILTER (WHERE ...)` va `SUM(CASE WHEN ... THEN 1 ELSE 0 "
         "END)` bir xil natija beradi, lekin birinchisi ancha o'qiladigan. "
         "Bu SQL standartining qismi, lekin hamma bazada "
         "qo'llab-quvvatlanmaydi.")

    code(d, """-- Yangilashda
UPDATE products
SET price = CASE
    WHEN category_id = 1 THEN price * 1.10
    WHEN category_id = 2 THEN price * 1.05
    ELSE price
END
WHERE is_active = true;""")

    # ───────────────────────────────────────────
    h1(d, "3. NULL bilan ishlovchi funksiyalar")

    table(d, ["Funksiya", "Nima qiladi"],
          [["`COALESCE(a, b, c)`", "Birinchi `NULL` bo'lmagan qiymatni "
                                   "qaytaradi"],
           ["`NULLIF(a, b)`", "`a = b` bo'lsa `NULL`, aks holda `a`"],
           ["`GREATEST(a, b)`", "Kattarog'ini qaytaradi"],
           ["`LEAST(a, b)`", "Kichigini qaytaradi"]],
          widths=[4.6, 10.9])

    code(d, """-- Sukutdagi qiymat
SELECT COALESCE(nickname, full_name, 'Mehmon') AS display_name
FROM users;

-- Nolga bo'linishdan himoya
SELECT total / NULLIF(quantity, 0) AS unit_price
FROM order_items;""")

    note(d, "`NULLIF` ning bu qo'llanishi juda qulay:",
         "`quantity` nol bo'lsa, `NULLIF` uni `NULL` ga aylantiradi va "
         "`son / NULL` natijasi `NULL` bo'ladi — xatolik o'rniga bo'sh "
         "qiymat. Keyin uni `COALESCE` bilan noldan iborat qilib ham "
         "qo'yish mumkin.")

    h2(d, "3.1 NULL bilan taqqoslash tuzoqlari")

    code(d, """-- Hammasi NULL qaytaradi, rost emas
SELECT NULL = NULL;        -- NULL
SELECT NULL <> 5;          -- NULL
SELECT NULL > 0;           -- NULL

-- To'g'ri usullar
SELECT NULL IS NULL;               -- true
SELECT NULL IS DISTINCT FROM 5;    -- true
SELECT NULL IS NOT DISTINCT FROM NULL;  -- true""")

    note(d, "Bu meni bir marta chalg'itgan:",
         "`WHERE status <> 'paid'` deb yozsam, `status` qiymati `NULL` "
         "bo'lgan satrlar natijaga **tushmaydi**. Chunki `NULL <> 'paid'` "
         "natijasi `NULL`, ya'ni rost emas. Agar menga ular ham kerak "
         "bo'lsa, `IS DISTINCT FROM` ishlatishim kerak.")

    code(d, """-- NULL larni ham qamrab oladi
WHERE status IS DISTINCT FROM 'paid'

-- Yoki aniq yozish
WHERE status <> 'paid' OR status IS NULL""")

    # ───────────────────────────────────────────
    h1(d, "4. PL/pgSQL dagi IF")

    code(d, """CREATE OR REPLACE FUNCTION apply_discount(
    customer_id bigint,
    order_total numeric
)
RETURNS numeric
LANGUAGE plpgsql
AS $$
DECLARE
    tier text;
    rate numeric;
BEGIN
    SELECT customer_tier INTO tier
    FROM customers WHERE id = customer_id;

    IF tier IS NULL THEN
        RAISE EXCEPTION 'Mijoz topilmadi: %', customer_id;

    ELSIF tier = 'vip' THEN
        rate := 0.20;

    ELSIF tier = 'gold' THEN
        rate := 0.10;

    ELSE
        rate := 0.00;
    END IF;

    RETURN ROUND(order_total * (1 - rate), 2);
END;
$$;""")

    para(d, "Sintaksisda ikki nuqtaga e'tibor berish kerak: `ELSIF` "
            "(`ELSEIF` emas, garchi u ham qabul qilinadi) va blok oxiridagi "
            "`END IF`.")

    h2(d, "4.1 CASE buyrug'i")

    para(d, "PL/pgSQL da `CASE` ifodadan tashqari buyruq sifatida ham "
            "mavjud:")

    code(d, """CASE tier
    WHEN 'vip'  THEN rate := 0.20;
    WHEN 'gold' THEN rate := 0.10;
    ELSE
        RAISE EXCEPTION 'Noma''lum daraja: %', tier;
END CASE;""")

    note(d, "Buyruq shaklida `ELSE` yozilmasligi xatolikka olib keladi:",
         "`CASE` ifodasida `ELSE` bo'lmasa, natija `NULL` bo'ladi. `CASE` "
         "buyrug'ida esa hech bir shart mos kelmasa, "
         "`CASE_NOT_FOUND` istisnosi otiladi. Bu farq ba'zan foydali — u "
         "kutilmagan qiymatni jimgina o'tkazib yubormaydi.")

    # ───────────────────────────────────────────
    h1(d, "5. Shartli tekshirish operatorlari")

    code(d, """-- IN
WHERE status IN ('pending', 'processing')

-- BETWEEN — chegaralar ham kiradi
WHERE created_at BETWEEN '2026-01-01' AND '2026-12-31'

-- EXISTS — mavjudlikni tekshirish
WHERE EXISTS (
    SELECT 1 FROM orders o WHERE o.customer_id = c.id
)

-- ANY / ALL
WHERE price > ALL (SELECT price FROM products WHERE category_id = 1)""")

    note(d, "`NOT IN` va `NULL` — klassik tuzoq:",
         "Agar ichki so'rov natijasida bitta `NULL` bo'lsa, `NOT IN` "
         "**hech qanday satr qaytarmaydi**. Sababi mantiqiy: `x NOT IN "
         "(1, NULL)` degani `x <> 1 AND x <> NULL`, ikkinchi qism esa doim "
         "`NULL`. Shuning uchun men `NOT IN` o'rniga `NOT EXISTS` "
         "ishlataman — u bunday xatti-harakatdan xoli.")

    code(d, """-- Xavfli
WHERE customer_id NOT IN (SELECT customer_id FROM blacklist)

-- Xavfsiz
WHERE NOT EXISTS (
    SELECT 1 FROM blacklist b WHERE b.customer_id = c.id
)""")

    # ───────────────────────────────────────────
    h1(d, "6. Unumdorlikka ta'siri")

    bullets(d, [
        "`CASE` ni `WHERE` da ishlatish indeksdan foydalanishni to'sadi.",
        "`COALESCE(column, ...)` ham xuddi shunday — ustun funksiya ichida "
        "qoladi.",
        "Ko'p shartli `CASE` har bir satr uchun hisoblanadi.",
    ])

    code(d, """-- Indeks ishlamaydi
WHERE CASE WHEN type = 'a' THEN value ELSE other END > 100

-- Indeks ishlaydi
WHERE (type = 'a' AND value > 100)
   OR (type <> 'a' AND other > 100)""")

    code(d, """-- Indeks ishlamaydi
WHERE COALESCE(deleted_at, '9999-12-31') > now()

-- Indeks ishlaydi
WHERE deleted_at IS NULL OR deleted_at > now()""")

    # ───────────────────────────────────────────
    h1(d, "7. EF Core da")

    code(d, """// Ternar operator CASE ga aylanadi
var result = await db.Orders
    .Select(o => new
    {
        o.Id,
        Tier = o.Total >= 1_000_000 ? "VIP"
             : o.Total >= 500_000   ? "Oltin"
             : "Oddiy"
    })
    .ToListAsync(ct);""")

    code(d, """// ?? operatori COALESCE ga aylanadi
.Select(u => new { Name = u.Nickname ?? u.FullName })

// Shartli hisoblash
.GroupBy(o => o.CustomerId)
.Select(g => new
{
    CustomerId = g.Key,
    Paid = g.Count(o => o.Status == OrderStatus.Paid),
    Total = g.Count()
})""")

    # ───────────────────────────────────────────
    h1(d, "8. Xulosa")

    bullets(d, [
        "`CASE` — ifoda, so'rov ichida ishlatiladi; `IF` — buyruq, "
        "PL/pgSQL blokida.",
        "`CASE` ning oddiy shakli `NULL` ni ushlay olmaydi — qidiruvli "
        "shakl va `IS NULL` kerak.",
        "`COALESCE` birinchi `NULL` bo'lmagan qiymatni, `NULLIF` esa "
        "tenglikda `NULL` qaytaradi.",
        "`NULL` bilan taqqoslash `NULL` beradi — `IS DISTINCT FROM` "
        "ishlatish kerak.",
        "`<>` sharti `NULL` qiymatli satrlarni natijadan chiqarib "
        "yuboradi.",
        "`NOT IN` ichki so'rovda `NULL` bo'lsa hech narsa qaytarmaydi — "
        "`NOT EXISTS` afzal.",
        "`WHERE` ichidagi `CASE` va `COALESCE` indeksdan foydalanishni "
        "to'sadi.",
        "`FILTER` shartli agregatsiyani `SUM(CASE ...)` dan o'qiladigan "
        "qiladi.",
    ])

    sources(d, [
        ("Conditional Expressions — PostgreSQL hujjati",
         "https://www.postgresql.org/docs/current/functions-conditional.html"),
        ("PL/pgSQL Control Structures — PostgreSQL",
         "https://www.postgresql.org/docs/current/plpgsql-control-structures.html"),
        ("Comparison Functions and Operators — PostgreSQL",
         "https://www.postgresql.org/docs/current/functions-comparison.html"),
    ])
