# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = ("Query combining (UNION , UNION ALL,EXCEPT , EXCEPT ALL ,"
         "INTERSECT, INTERSECTALL)")
CATEGORY = "SQL"
TITLE = "So'rovlarni Birlashtirish"
SUBTITLE = "UNION, EXCEPT va INTERSECT operatorlari"
FILENAME = "Query combining (UNION, EXCEPT, INTERSECT).docx"


def build(d):
    h1(d, "1. To'plam operatorlari")

    para(d, "`JOIN` jadvallarni **gorizontal** birlashtiradi — "
            "ustunlar qo'shiladi. To'plam operatorlari esa "
            "**vertikal** birlashtiradi — satrlar qo'shiladi.")

    table(d, ["Operator", "Natija"],
          [["`UNION`", "Ikki to'plam birlashmasi, dublikatlar olib tashlanadi"],
           ["`UNION ALL`", "Birlashma, dublikatlar saqlanadi"],
           ["`INTERSECT`", "Faqat ikkisida ham bor satrlar"],
           ["`EXCEPT`", "Birinchisida bor, ikkinchisida yo'q satrlar"]],
          widths=[3.6, 10.9])

    para(d, "`ALL` qo'shimchasi uchtasida ham ishlaydi: `UNION ALL`, "
            "`INTERSECT ALL`, `EXCEPT ALL`. `ALL` bo'lsa dublikatlar "
            "saqlanadi va takrorlanish soni hisobga olinadi.")

    # ───────────────────────────────────────────
    h1(d, "2. Umumiy talablar")

    para(d, "Hamma to'plam operatori uchun uchta shart bajarilishi "
            "kerak:")

    bullets(d, [
        "Ikki so'rovda **ustunlar soni bir xil**.",
        "Mos ustunlarning **tiplari mos** keladi (yoki yashirin "
        "aylantirish mumkin).",
        "Natija ustun nomlari **birinchi** so'rovdan olinadi.",
    ], numbered=True)

    code(d, """-- ORDER BY butun natijaga qo'llanadi va eng oxirida yoziladi
SELECT name, email FROM customers WHERE city = 'Toshkent'
UNION
SELECT name, email FROM suppliers WHERE city = 'Toshkent'
ORDER BY name;""")

    note(d, "Nozik joy",
         "`ORDER BY` ni oraliq so'rovga qo'yib bo'lmaydi — u faqat "
         "yakuniy natijaga tegishli. Agar oraliq so'rovni saralash "
         "kerak bo'lsa, uni qavsga olib subquery qilish kerak.")

    # ───────────────────────────────────────────
    h1(d, "3. UNION va UNION ALL — amaliy farq")

    code(d, """-- Dublikatlarni olib tashlaydi: saralash yoki hash kerak
SELECT product_id FROM order_items
UNION
SELECT product_id FROM wishlist_items;

-- Dublikatlar qoladi: hech qanday qo'shimcha ish yo'q
SELECT product_id FROM order_items
UNION ALL
SELECT product_id FROM wishlist_items;""")

    para(d, "`UNION` dublikatlarni topish uchun butun natijani "
            "saralashi yoki hash jadvali qurishi kerak. Katta "
            "hajmda bu sezilarli xarajat.")

    para(d, "Shuning uchun qoidam: **dublikat bo'lishi mumkin "
            "emasligini bilsam, har doim `UNION ALL`**. Masalan "
            "yuqoridagi birinchi misolda agar har bir manba "
            "o'zining `DISTINCT` natijasini bersa va to'plamlar "
            "kesishmasa, `UNION ALL` to'g'ri va tezroq.")

    code(d, """EXPLAIN ANALYZE
SELECT id FROM orders_2025
UNION ALL
SELECT id FROM orders_2026;""")

    para(d, "Rejada `HashAggregate` yoki `Sort` ko'rinsa, bu "
            "`UNION` ning dublikat olib tashlash bosqichi. "
            "`UNION ALL` da esa faqat `Append` bo'ladi.")

    # ───────────────────────────────────────────
    h1(d, "4. EXCEPT — farqni topish")

    code(d, """-- Hech qachon buyurtma qilmagan mijozlar
SELECT id FROM customers
EXCEPT
SELECT customer_id FROM orders;""")

    para(d, "Bu `NOT IN` va `NOT EXISTS` ga alternativa, lekin "
            "muhim farqi bor: `EXCEPT` `NULL` bilan to'g'ri "
            "ishlaydi.")

    code(d, """-- XAVFLI: agar customer_id da NULL bo'lsa, natija BO'SH bo'ladi
SELECT * FROM customers
WHERE id NOT IN (SELECT customer_id FROM orders);

-- Xavfsiz
SELECT * FROM customers c
WHERE NOT EXISTS (SELECT 1 FROM orders o WHERE o.customer_id = c.id);""")

    para(d, "`NOT IN` ichida bitta `NULL` bo'lsa, butun shart "
            "`UNKNOWN` bo'ladi va natija bo'sh keladi. Bu eng ko'p "
            "uchraydigan SQL tuzoqlaridan biri va uni topish qiyin, "
            "chunki xato chiqmaydi — shunchaki natija yo'q.")

    h2(d, "Sxemalarni taqqoslash — amaliy foyda")

    code(d, """-- Ikki muhitdagi jadvallar farqini topish
SELECT table_name, column_name FROM information_schema.columns
WHERE table_schema = 'public'
EXCEPT
SELECT table_name, column_name FROM staging.columns_snapshot;""")

    para(d, "Bu usulni migratsiyalarni tekshirishda ishlataman: "
            "dev va prod sxemasi farqini bir so'rovda ko'rish "
            "mumkin.")

    # ───────────────────────────────────────────
    h1(d, "5. INTERSECT — umumiy qismni topish")

    code(d, """-- Ikki kursga ham yozilgan talabalar
SELECT student_id FROM enrollments WHERE course_code = 'CS101'
INTERSECT
SELECT student_id FROM enrollments WHERE course_code = 'CS202';""")

    para(d, "Buni `JOIN` bilan ham yozish mumkin, lekin "
            "`INTERSECT` niyatni aniqroq ifodalaydi — ayniqsa "
            "uch yoki undan ko'p shart bo'lsa:")

    code(d, """SELECT student_id FROM enrollments WHERE course_code = 'CS101'
INTERSECT
SELECT student_id FROM enrollments WHERE course_code = 'CS202'
INTERSECT
SELECT student_id FROM enrollments WHERE course_code = 'CS303';""")

    para(d, "`JOIN` bilan bu uch marta o'z-o'ziga qo'shilish bo'lib "
            "o'qilishi qiyinlashadi.")

    # ───────────────────────────────────────────
    h1(d, "6. ALL variantlari va takrorlanish hisobi")

    code(d, """-- A da: 1, 1, 2, 3
-- B da: 1, 2, 2

-- INTERSECT      -> 1, 2
-- INTERSECT ALL  -> 1, 2        (min(2,1)=1 ta bir, min(1,2)=1 ta ikki)

-- EXCEPT         -> 3
-- EXCEPT ALL     -> 1, 3        (2-1=1 ta bir qoladi)""")

    para(d, "`ALL` variantlari takrorlanish sonini hisobga oladi: "
            "`EXCEPT ALL` da har bir element uchun \"birinchi "
            "to'plamdagi soni minus ikkinchisidagi soni\" qoladi.")

    para(d, "Bu nozik semantika kamdan-kam kerak bo'ladi, lekin "
            "inventarizatsiya kabi vazifalarda — \"omborda nechta "
            "ortiqcha\" — aynan shu kerak bo'lishi mumkin.")

    # ───────────────────────────────────────────
    h1(d, "7. EF Core da")

    code(d, """var toshkent = db.Customers.Where(c => c.City == "Toshkent")
                       .Select(c => new ContactDto { Name = c.Name, Email = c.Email });

var suppliers = db.Suppliers.Where(s => s.City == "Toshkent")
                            .Select(s => new ContactDto { Name = s.Name, Email = s.Email });

// UNION
var all = await toshkent.Union(suppliers).ToListAsync(ct);

// UNION ALL
var withDuplicates = await toshkent.Concat(suppliers).ToListAsync(ct);

// INTERSECT va EXCEPT
var common = await toshkent.Intersect(suppliers).ToListAsync(ct);
var only = await toshkent.Except(suppliers).ToListAsync(ct);""")

    para(d, "`Concat` — `UNION ALL`, `Union` — `UNION`. Bu nomlash "
            "chalg'ituvchi, shuning uchun eslab qolish kerak: "
            "LINQ'ning `Union` metodi dublikatlarni olib tashlaydi.")

    note(d, "Cheklov",
         "EF Core to'plam operatorlarini ishlatish uchun ikki "
         "so'rovning **projeksiyasi bir xil** bo'lishi kerak. "
         "Turli shakldagi `Select` bo'lsa, so'rov tarjima "
         "qilinmaydi va xato chiqadi.")

    # ───────────────────────────────────────────
    h1(d, "8. Qachon to'plam operatorini tanlayman")

    bullets(d, [
        "**Turli jadvallardan bir xil shakldagi ro'yxat** kerak "
        "bo'lsa — `UNION ALL`.",
        "**Mavjud emasligini tekshirish** uchun — `NOT EXISTS` ni "
        "afzal ko'raman, chunki u ko'pincha samaraliroq va "
        "qo'shimcha shart qo'shish oson. `EXCEPT` esa butun satrni "
        "taqqoslash kerak bo'lganda qulay.",
        "**Bir nechta shartning kesishmasi** — `INTERSECT`, "
        "chunki `JOIN` zanjiridan o'qilishi oson.",
        "**Sxema yoki ma'lumot farqini topish** — `EXCEPT` eng "
        "to'g'ridan-to'g'ri yo'l.",
    ])

    sources(d, [
        ("Combining Queries — PostgreSQL",
         "https://www.postgresql.org/docs/current/queries-union.html"),
        ("SELECT statement — PostgreSQL",
         "https://www.postgresql.org/docs/current/sql-select.html"),
        ("Set operations — EF Core",
         "https://learn.microsoft.com/en-us/ef/core/querying/complex-query-operators"),
    ])
