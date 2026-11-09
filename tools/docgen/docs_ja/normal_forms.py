# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "Ma'lumotlar bazaning normal formalari"
CATEGORY = "SQL"
TITLE = "Normal Formalar"
SUBTITLE = "1NF dan 5NF gacha rasmiy ta'riflar"
FILENAME = "Ma'lumotlar bazaning normal formalari.docx"


def build(d):
    h1(d, "1. Funksional bog'liqlik")

    para(d, "Normal formalar ta'riflari **funksional bog'liqlik** "
            "tushunchasiga asoslangan, shuning uchun avval shuni "
            "aniqlash kerak.")

    para(d, "`A → B` deb yozilsa, bu \"`A` ning qiymati `B` ning "
            "qiymatini bir ma'noda aniqlaydi\" degani. Masalan "
            "`student_id → student_name`: bitta ID bitta ismga mos "
            "keladi.")

    bullets(d, [
        "**To'liq bog'liqlik** — `B` butun kalitga bog'liq.",
        "**Qismiy bog'liqlik** — `B` kompozit kalitning faqat bir "
        "qismiga bog'liq.",
        "**Transitiv bog'liqlik** — `A → B` va `B → C`, demak "
        "`A → C`, lekin bu bilvosita.",
    ])

    para(d, "Yana bir kerakli atama — **nomzod kalit** (candidate "
            "key): satrni bir ma'noda aniqlaydigan minimal "
            "atributlar to'plami. Nomzod kalitga kiradigan atribut "
            "**kalit atribut** deb ataladi.")

    # ───────────────────────────────────────────
    h1(d, "2. 1NF — First Normal Form")

    para(d, "**Ta'rif:** har bir atributning qiymati atomik, ya'ni "
            "bo'linmas; takrorlanuvchi guruhlar yo'q.")

    code(d, """-- 1NF BUZILGAN
phones     = '+998901112233, +998933334455'    -- ro'yxat
phone1, phone2, phone3                          -- takrorlanuvchi guruh

-- 1NF
CREATE TABLE student_phones (
    student_id bigint NOT NULL,
    phone      text   NOT NULL,
    PRIMARY KEY (student_id, phone)
);""")

    para(d, "Takrorlanuvchi guruh ham 1NF buzilishi: `phone1`, "
            "`phone2`, `phone3` ustunlari bo'lsa, to'rtinchi raqam "
            "kerak bo'lganda sxema o'zgarishi kerak va bo'sh "
            "ustunlar paydo bo'ladi.")

    note(d, "Atomiklik nisbiy",
         "\"Atomik\" tushunchasi kontekstga bog'liq. `JSONB` ustun "
         "rasmiy jihatdan 1NF ni buzadi, lekin tuzilishi "
         "o'zgaruvchan ma'lumot uchun amalda to'g'ri yechim bo'lishi "
         "mumkin. Qoida — asbob, maqsad emas.")

    # ───────────────────────────────────────────
    h1(d, "3. 2NF — Second Normal Form")

    para(d, "**Ta'rif:** 1NF bajarilgan va kalit bo'lmagan har bir "
            "atribut **butun** nomzod kalitga to'liq funksional "
            "bog'liq.")

    para(d, "Ya'ni qismiy bog'liqlik bo'lmasligi kerak. Bu shart "
            "faqat **kompozit kalit** bo'lganda ma'noga ega — kalit "
            "bitta ustundan iborat bo'lsa, jadval avtomatik 2NF da.")

    code(d, """-- 2NF BUZILGAN: kalit (order_id, product_id)
order_items(order_id, product_id, quantity, product_name, product_price)
--                                           ^^^^^^^^^^^^^^^^^^^^^^^^^
--                     bular faqat product_id ga bog'liq

-- 2NF
order_items(order_id, product_id, quantity, unit_price)
products(id, name, price)""")

    para(d, "`unit_price` bu yerda qolgani ataylab — u buyurtma "
            "paytidagi narx, ya'ni `(order_id, product_id)` ga "
            "bog'liq tarixiy fakt, `products.price` dan boshqa narsa.")

    # ───────────────────────────────────────────
    h1(d, "4. 3NF — Third Normal Form")

    para(d, "**Ta'rif:** 2NF bajarilgan va kalit bo'lmagan hech bir "
            "atribut boshqa kalit bo'lmagan atributga bog'liq emas "
            "(transitiv bog'liqlik yo'q).")

    code(d, """-- 3NF BUZILGAN
courses(code, name, teacher_id, teacher_email, teacher_degree)
-- code -> teacher_id -> teacher_email
-- ya'ni email kursga emas, o'qituvchiga bog'liq

-- 3NF
courses(code, name, teacher_id)
teachers(id, name, email, degree)""")

    para(d, "Amaliy sxemalarning aksariyati shu yerda to'xtaydi. "
            "3NF anomaliyalarning deyarli hammasini yo'qotadi va "
            "keyingi formalar kamdan-kam qo'shimcha foyda beradi.")

    # ───────────────────────────────────────────
    h1(d, "5. BCNF — Boyce-Codd Normal Form")

    para(d, "**Ta'rif:** har bir noan'anaviy funksional bog'liqlik "
            "`X → Y` uchun `X` **super kalit** bo'lishi kerak.")

    para(d, "BCNF 3NF dan qattiqroq. Farq faqat bitta holatda "
            "sezilarli: jadvalda bir nechta nomzod kalit bo'lsa va "
            "ular kesishsa.")

    code(d, """-- 3NF da, lekin BCNF da emas
schedule(teacher_id, time_slot, room_id)

-- Bog'liqliklar:
--   (teacher_id, time_slot) -> room_id      nomzod kalit
--   room_id -> teacher_id                   room_id super kalit EMAS
-- (har bir xona bitta o'qituvchiga biriktirilgan deb hisoblaymiz)""")

    code(d, """-- BCNF
rooms(id, teacher_id)
schedule(room_id, time_slot)""")

    para(d, "BCNF ga keltirish ba'zan funksional bog'liqlikni "
            "saqlab qolishni imkonsiz qiladi — ya'ni ajratilgan "
            "jadvallarda ba'zi qoidani ifodalab bo'lmaydi. Shunday "
            "holatda 3NF da qolib, qoidani `CHECK` yoki ilova "
            "darajasida majburlash amaliy yechim bo'ladi.")

    # ───────────────────────────────────────────
    h1(d, "6. 4NF va 5NF")

    para(d, "Bu formalar ko'p qiymatli bog'liqliklar bilan "
            "ishlaydi va amalda kamdan-kam kerak bo'ladi.")

    h2(d, "4NF — ko'p qiymatli bog'liqlik")

    para(d, "**Ta'rif:** BCNF bajarilgan va bir-biriga bog'liq "
            "bo'lmagan ikki ko'p qiymatli fakt bitta jadvalda "
            "bo'lmasligi kerak.")

    code(d, """-- 4NF BUZILGAN: o'qituvchining kurslari va tillari mustaqil
teacher_skills(teacher_id, course_code, language)

-- Natijada dekart ko'paytmasi saqlanadi:
-- (1, CS101, uz), (1, CS101, en), (1, CS202, uz), (1, CS202, en)

-- 4NF
teacher_courses(teacher_id, course_code)
teacher_languages(teacher_id, language)""")

    para(d, "Buzilish belgisi aniq: yangi til qo'shilsa, u har bir "
            "kurs uchun takrorlanishi kerak bo'ladi.")

    h2(d, "5NF — birlashtirish bog'liqligi")

    para(d, "**Ta'rif:** 4NF bajarilgan va jadvalni "
            "ma'lumot yo'qotmasdan kichik jadvallarga ajratib "
            "bo'lmaydi. Uch tomonli munosabat ikki tomonli "
            "munosabatlarga bo'linmasligi kerak bo'lgan holatlarda "
            "ma'noga ega.")

    para(d, "Amalda 5NF ni ataylab qo'llashim kerak bo'lgan holatni "
            "deyarli uchratmadim — 4NF ga keltirilgan sxema odatda "
            "5NF da ham bo'ladi.")

    # ───────────────────────────────────────────
    h1(d, "7. Qisqa jadval")

    table(d, ["Forma", "Nimani talab qiladi"],
          [["1NF", "Atomik qiymatlar, takrorlanuvchi guruh yo'q"],
           ["2NF", "Qismiy bog'liqlik yo'q"],
           ["3NF", "Transitiv bog'liqlik yo'q"],
           ["BCNF", "Har bir determinant super kalit"],
           ["4NF", "Mustaqil ko'p qiymatli bog'liqlik yo'q"],
           ["5NF", "Yo'qotishsiz ajratib bo'lmaydi"]],
          widths=[2.6, 11.9])

    para(d, "Formalar ketma-ket: har biri oldingisini o'z ichiga "
            "oladi. Shuning uchun 3NF da bo'lgan jadval 1NF va 2NF "
            "da ham bo'ladi.")

    note(d, "Amaliy pozitsiyam",
         "Loyihada **3NF ni maqsad** qilaman va BCNF buzilishini "
         "faqat muammo chiqsa ko'rib chiqaman. 4NF va 5NF ni "
         "bilish foydali, lekin ularni atama sifatida eslamasdan "
         "ham to'g'ri sxema qurish mumkin — chunki ular ko'proq "
         "nazariy chegaralarni tasvirlaydi.")

    sources(d, [
        ("Database normalization description",
         "https://learn.microsoft.com/en-us/office/troubleshoot/access/database-normalization-description"),
        ("Functional dependency and normalization",
         "https://learn.microsoft.com/en-us/training/modules/design-data-model/"),
        ("Constraints — PostgreSQL",
         "https://www.postgresql.org/docs/current/ddl-constraints.html"),
    ])
