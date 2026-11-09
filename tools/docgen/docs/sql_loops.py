# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "Takrorlash operatorlari (LOOP, FOR, WHILE)"
CATEGORY = "Postgres / Oracle"
TITLE = "PL/pgSQL da Takrorlash Operatorlari"
SUBTITLE = "LOOP, FOR, WHILE va ulardan qochish sabablari"
FILENAME = "Takrorlash operatorlari (LOOP, FOR, WHILE).docx"


def build(d):
    h1(d, "1. Boshlang'ich eslatma")

    para(d, "SQL — to'plamlar bilan ishlaydigan til. Unda \"har bir satr "
            "uchun\" degan tushuncha tabiiy emas; o'rniga butun to'plamga "
            "bitta amal qo'llaniladi.")

    note(d, "Shuning uchun birinchi savol har doim bitta:",
         "Siklni yozishdan oldin \"buni bitta `UPDATE` yoki `INSERT ... "
         "SELECT` bilan qilsa bo'lmaydimi?\" deb so'rayman. Ko'p hollarda "
         "javob \"ha\" bo'ladi va to'plamli yechim o'nlab marta tezroq "
         "ishlaydi. Sikl — oxirgi chora.")

    code(d, """-- Sikl bilan: 100 000 marta UPDATE
FOR rec IN SELECT id, price FROM products LOOP
    UPDATE products SET price = rec.price * 1.1 WHERE id = rec.id;
END LOOP;

-- To'plamli: bitta UPDATE
UPDATE products SET price = price * 1.1;""")

    para(d, "Shunga qaramay sikl haqiqatan kerak bo'ladigan holatlar bor: "
            "ommaviy amalni bo'laklarga bo'lish, har bir satr uchun tashqi "
            "funksiya chaqirish, murakkab iterativ hisoblash.")

    # ───────────────────────────────────────────
    h1(d, "2. Oddiy LOOP")

    para(d, "Eng sodda shakl — shartsiz cheksiz sikl. Undan chiqish "
            "`EXIT` orqali amalga oshiriladi.")

    code(d, """DO $$
DECLARE
    counter int := 0;
BEGIN
    LOOP
        counter := counter + 1;
        RAISE NOTICE 'Qadam: %', counter;

        EXIT WHEN counter >= 5;
    END LOOP;
END;
$$;""")

    table(d, ["Buyruq", "Vazifasi"],
          [["`EXIT`", "Sikldan chiqish"],
           ["`EXIT WHEN shart`", "Shart bajarilganda chiqish"],
           ["`CONTINUE`", "Keyingi iteratsiyaga o'tish"],
           ["`EXIT label`", "Belgilangan tashqi sikldan chiqish"]],
          widths=[4.0, 11.5])

    h2(d, "2.1 Belgilangan sikllar")

    code(d, """DO $$
BEGIN
    <<outer_loop>>
    FOR i IN 1..10 LOOP
        FOR j IN 1..10 LOOP
            EXIT outer_loop WHEN i * j > 50;
            RAISE NOTICE '% x % = %', i, j, i * j;
        END LOOP;
    END LOOP;
END;
$$;""")

    # ───────────────────────────────────────────
    h1(d, "3. FOR sikli")

    h2(d, "3.1 Son oralig'i bo'yicha")

    code(d, """FOR i IN 1..10 LOOP
    RAISE NOTICE '%', i;
END LOOP;

-- Teskari
FOR i IN REVERSE 10..1 LOOP ... END LOOP;

-- Qadam bilan
FOR i IN 1..100 BY 5 LOOP ... END LOOP;""")

    para(d, "Sikl o'zgaruvchisini alohida e'lon qilish shart emas — u "
            "avtomatik yaratiladi va faqat sikl ichida mavjud bo'ladi.")

    h2(d, "3.2 So'rov natijasi bo'yicha")

    code(d, """DO $$
DECLARE
    rec record;
BEGIN
    FOR rec IN
        SELECT id, email, full_name
        FROM customers
        WHERE is_active = true
    LOOP
        RAISE NOTICE '% — %', rec.id, rec.email;
    END LOOP;
END;
$$;""")

    h2(d, "3.3 Massiv bo'yicha")

    code(d, """DECLARE
    tags text[] := ARRAY['dotnet', 'postgres', 'docker'];
    tag text;
BEGIN
    FOREACH tag IN ARRAY tags LOOP
        RAISE NOTICE 'Teg: %', tag;
    END LOOP;
END;""")

    # ───────────────────────────────────────────
    h1(d, "4. WHILE sikli")

    code(d, """DECLARE
    remaining int;
BEGIN
    SELECT COUNT(*) INTO remaining
    FROM orders WHERE status = 'pending';

    WHILE remaining > 0 LOOP
        -- qandaydir ish
        remaining := remaining - 1;
    END LOOP;
END;""")

    note(d, "`WHILE` da cheksiz sikl xavfi bor:",
         "Agar shartni o'zgartiradigan kod yozishni unutsam yoki shart "
         "hech qachon buzilmasa, sikl to'xtamaydi va baza sessiyasi "
         "qotib qoladi. Men shuning uchun har doim xavfsizlik hisoblagichi "
         "qo'yaman — ma'lum sondan oshsa, istisno otiladi.")

    code(d, """DECLARE
    iterations int := 0;
    max_iterations CONSTANT int := 10000;
BEGIN
    WHILE condition LOOP
        iterations := iterations + 1;

        IF iterations > max_iterations THEN
            RAISE EXCEPTION 'Sikl chegaradan oshdi';
        END IF;

        -- asosiy ish
    END LOOP;
END;""")

    # ───────────────────────────────────────────
    h1(d, "5. Eng foydali qo'llanish — bo'laklab ishlov berish")

    para(d, "Million satrni bitta `UPDATE` bilan o'zgartirish jadval "
            "qulflanishiga va jurnal o'sishiga olib keladi. Siklning "
            "haqiqiy foydasi shu yerda ko'rinadi.")

    code(d, """CREATE OR REPLACE PROCEDURE recalculate_order_totals()
LANGUAGE plpgsql
AS $$
DECLARE
    batch_size CONSTANT int := 5000;
    affected int;
    last_id bigint := 0;
BEGIN
    LOOP
        WITH batch AS (
            SELECT id FROM orders
            WHERE id > last_id AND total IS NULL
            ORDER BY id
            LIMIT batch_size
        )
        UPDATE orders o
        SET total = (
            SELECT COALESCE(SUM(oi.quantity * oi.unit_price), 0)
            FROM order_items oi WHERE oi.order_id = o.id
        )
        FROM batch b
        WHERE o.id = b.id
        RETURNING o.id INTO last_id;

        GET DIAGNOSTICS affected = ROW_COUNT;
        EXIT WHEN affected = 0;

        COMMIT;    -- har bo'lakdan keyin tasdiqlash
        RAISE NOTICE '% ta satr qayta hisoblandi', affected;
    END LOOP;
END;
$$;""")

    note(d, "Bu naqshning uchta afzalligi bor:",
         "Birinchidan, qulflar uzoq ushlanmaydi va boshqa so'rovlar "
         "ishlayveradi. Ikkinchidan, jurnal nazorat ostida qoladi. "
         "Uchinchidan, jarayon uzilsa, bajarilgan qism saqlanadi va "
         "qaytadan boshlash shart emas.")

    note(d, "`COMMIT` faqat protsedurada ishlaydi:",
         "Funksiya ichida u xatolik beradi, chunki funksiya chaqiruvchining "
         "tranzaksiyasi ichida bajariladi. Shuning uchun uzoq davom "
         "etadigan ommaviy amallarni protsedura sifatida yozish kerak.")

    # ───────────────────────────────────────────
    h1(d, "6. Kursorlar")

    para(d, "`FOR rec IN SELECT ...` konstruksiyasi ichkarida kursor "
            "ishlatadi va butun natijani xotiraga yuklamaydi. Aniq "
            "boshqaruv kerak bo'lsa, kursorni o'zi e'lon qilish mumkin:")

    code(d, """DECLARE
    cur CURSOR FOR SELECT id, email FROM customers;
    rec record;
BEGIN
    OPEN cur;

    LOOP
        FETCH cur INTO rec;
        EXIT WHEN NOT FOUND;

        -- ish
    END LOOP;

    CLOSE cur;
END;""")

    para(d, "Amalda `FOR` sikli deyarli har doim yetarli bo'ladi — aniq "
            "kursor faqat natijani bo'lib olish yoki siklni to'xtatib, keyin "
            "davom ettirish kerak bo'lganda kerak.")

    # ───────────────────────────────────────────
    h1(d, "7. Unumdorlik taqqoslashi")

    table(d, ["Yondashuv", "100 000 satr uchun taxminiy vaqt"],
          [["Bitta `UPDATE`", "Soniyaning bir qismi"],
           ["`FOR` sikli, har satrga `UPDATE`", "O'nlab soniya yoki ko'proq"],
           ["Bo'laklab (5000 talab)", "Bir necha soniya, lekin qulflamaydi"]],
          widths=[6.4, 9.1])

    para(d, "Raqamlar taxminiy va uskunaga bog'liq, lekin tartiblar "
            "orasidagi farq barqaror qoladi.")

    note(d, "Shuning uchun tanlov mezonim shunday:",
         "Agar amal tez bajarilsa va jadvalni uzoq bloklamasa — oddiy "
         "to'plamli `UPDATE`. Agar u daqiqalar davom etsa — bo'laklab "
         "ishlov beruvchi protsedura. Har bir satr uchun alohida `UPDATE` "
         "yozadigan sikl esa deyarli har doim noto'g'ri yechim.")

    # ───────────────────────────────────────────
    h1(d, "8. Nosozlikni topish")

    code(d, """-- Sikl ichida holatni kuzatish
RAISE NOTICE '[%] Bo''lak: %, qolgan: %',
    clock_timestamp(), batch_number, remaining;

-- Uzoq davom etayotgan so'rovlarni ko'rish
SELECT pid, now() - query_start AS duration, state, left(query, 80)
FROM pg_stat_activity
WHERE state = 'active' AND now() - query_start > interval '1 minute'
ORDER BY duration DESC;

-- Qotib qolgan sessiyani to'xtatish
SELECT pg_cancel_backend(12345);     -- yumshoq
SELECT pg_terminate_backend(12345);  -- qattiq""")

    # ───────────────────────────────────────────
    h1(d, "9. Xulosa")

    bullets(d, [
        "SQL to'plamlar bilan ishlaydi — sikl yozishdan oldin to'plamli "
        "yechimni qidirish kerak.",
        "`LOOP` + `EXIT WHEN` — eng sodda shakl.",
        "`FOR i IN 1..n` son oralig'i, `FOR rec IN SELECT` so'rov natijasi, "
        "`FOREACH` massiv bo'yicha aylanadi.",
        "`WHILE` da cheksiz sikl xavfi bor — xavfsizlik hisoblagichi "
        "foydali.",
        "Belgilangan sikldan `EXIT label` bilan chiqiladi.",
        "Siklning asosiy foydali qo'llanishi — ommaviy amalni bo'laklarga "
        "bo'lish.",
        "`COMMIT` faqat protsedurada ishlaydi, funksiyada emas.",
        "Har bir satr uchun alohida `UPDATE` yozadigan sikl deyarli har "
        "doim noto'g'ri yechim.",
    ])

    sources(d, [
        ("PL/pgSQL Control Structures — PostgreSQL hujjati",
         "https://www.postgresql.org/docs/current/plpgsql-control-structures.html"),
        ("Cursors — PL/pgSQL — PostgreSQL hujjati",
         "https://www.postgresql.org/docs/current/plpgsql-cursors.html"),
        ("Transaction Management — PL/pgSQL",
         "https://www.postgresql.org/docs/current/plpgsql-transactions.html"),
    ])
