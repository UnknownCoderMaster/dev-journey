# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "Normalization"
CATEGORY = "Database Design Principles"
TITLE = "Normalizatsiya Jarayoni"
SUBTITLE = "Sxemani bosqichma-bosqich normal holatga keltirish"
FILENAME = "Normalization.docx"


def build(d):
    h1(d, "1. Normalizatsiya nima uchun qilinadi")

    para(d, "Normalizatsiya — jadvallarni shunday qayta tashkil "
            "qilish, bunda takrorlanish yo'qoladi va ma'lumot zid "
            "bo'lib qolish imkoni qolmaydi.")

    para(d, "Bu nazariy mashq emas: normalizatsiya qilinmagan sxema "
            "muqarran zid ma'lumotga olib keladi, va bu xato "
            "kodni tuzatish bilan hal qilinmaydi — chunki muammo "
            "sxemada.")

    para(d, "Bu hujjatda jarayonni **amaliy misolda** bosqichma-bosqich "
            "ko'rib chiqaman. Normal formalarning rasmiy ta'riflari "
            "alohida hujjatda.")

    # ───────────────────────────────────────────
    h1(d, "2. Boshlang'ich holat")

    para(d, "Ta'lim markazi ma'lumotini bitta jadvalga yiqqan "
            "sxemadan boshlaymiz — bu real loyihalarda juda ko'p "
            "uchraydigan boshlang'ich nuqta:")

    code(d, """CREATE TABLE enrollments (
    id               bigserial PRIMARY KEY,
    student_name     text,
    student_phones   text,        -- "+998901112233, +998933334455"
    course_code      text,        -- "CS101"
    course_name      text,        -- "Dasturlash asoslari"
    course_hours     integer,     -- 72
    teacher_name     text,        -- "Alisher Qodirov"
    teacher_email    text,
    teacher_degree   text,
    grade            integer,
    enrolled_at      date
);""")

    para(d, "Namuna ma'lumot:")

    table(d, ["student_name", "student_phones", "course_code", "teacher_name"],
          [["Orzibek", "+998901112233, +998933334455", "CS101", "Alisher Qodirov"],
           ["Orzibek", "+998901112233, +998933334455", "CS202", "Dilnoza Karimova"],
           ["Sardor", "+998935556677", "CS101", "Alisher Qodirov"]],
          widths=[3.0, 4.8, 2.6, 4.1])

    # ───────────────────────────────────────────
    h1(d, "3. 1NF — har katakda bitta qiymat")

    para(d, "Muammo: `student_phones` ustunida vergul bilan ajratilgan "
            "ro'yxat turadi. Natijada telefon bo'yicha qidirish uchun "
            "`LIKE '%...%'` kerak bo'ladi — ya'ni indeks ishlamaydi "
            "va to'liq jadval skanlanadi. Formatni tekshirish ham "
            "imkonsiz.")

    code(d, """CREATE TABLE student_phones (
    student_id bigint  NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    phone      text    NOT NULL,
    is_primary boolean NOT NULL DEFAULT false,
    PRIMARY KEY (student_id, phone)
);""")

    para(d, "Endi telefon bo'yicha qidiruv indeks orqali ketadi, har "
            "bir raqamga `CHECK` qo'yish mumkin, va \"asosiy raqam\" "
            "kabi qo'shimcha atribut ham joy topadi.")

    note(d, "Nozik qaror",
         "Hamma narsani bo'laklash shart emas. Agar telefon faqat "
         "ko'rsatish uchun saqlansa va hech qachon qism bo'yicha "
         "qidirilmasa, bitta ustun ham qabul qilinadi. Savol shunday: "
         "**bu qiymatni qism bo'yicha qidirishim yoki tekshirishim "
         "kerakmi?**")

    # ───────────────────────────────────────────
    h1(d, "4. 2NF — kompozit kalitning qismiga bog'liqlikni yo'qotish")

    para(d, "Mantiqiy kalit — `(student_id, course_code)`. Lekin "
            "jadvaldagi ba'zi ustunlar kalitning faqat **bir "
            "qismiga** bog'liq:")

    bullets(d, [
        "`student_name` faqat `student_id` ga bog'liq — kursga "
        "aloqasi yo'q.",
        "`course_name`, `course_hours` faqat `course_code` ga "
        "bog'liq — talabaga aloqasi yo'q.",
        "`grade` esa ikkisiga ham bog'liq — bu to'g'ri joyda.",
    ])

    para(d, "Shuning uchun qismiy bog'liqliklarni alohida "
            "jadvallarga ajrataman:")

    code(d, """CREATE TABLE students (
    id   bigserial PRIMARY KEY,
    name text NOT NULL
);

CREATE TABLE courses (
    code  text    PRIMARY KEY,
    name  text    NOT NULL,
    hours integer NOT NULL CHECK (hours > 0)
);

CREATE TABLE enrollments (
    student_id  bigint NOT NULL REFERENCES students(id),
    course_code text   NOT NULL REFERENCES courses(code),
    grade       integer CHECK (grade BETWEEN 0 AND 100),
    enrolled_at date   NOT NULL DEFAULT current_date,
    PRIMARY KEY (student_id, course_code)
);""")

    para(d, "Natija: kurs nomini o'zgartirish bitta satrni yangilaydi, "
            "500 ta yozuvni emas. Va talabasi yo'q kursni ham "
            "ro'yxatga olish mumkin bo'ldi.")

    # ───────────────────────────────────────────
    h1(d, "5. 3NF — kalitdan bo'lmagan bog'liqlikni yo'qotish")

    para(d, "`courses` jadvalida o'qituvchi ma'lumoti qolgan edi. "
            "Lekin `teacher_email` va `teacher_degree` kursga emas, "
            "**o'qituvchiga** bog'liq — ya'ni kalitdan bo'lmagan "
            "ustunga bog'liqlik (transitiv bog'liqlik).")

    para(d, "Oqibati: bitta o'qituvchi 5 ta kurs o'tsa, uning "
            "email'i 5 joyda takrorlanadi.")

    code(d, """CREATE TABLE teachers (
    id     bigserial PRIMARY KEY,
    name   text NOT NULL,
    email  text NOT NULL UNIQUE,
    degree text
);

CREATE TABLE courses (
    code       text    PRIMARY KEY,
    name       text    NOT NULL,
    hours      integer NOT NULL CHECK (hours > 0),
    teacher_id bigint  NOT NULL REFERENCES teachers(id)
);""")

    para(d, "Amalda sxemalarning aksariyati 3NF da to'xtaydi va bu "
            "to'g'ri: 3NF anomaliyalarning deyarli hammasini "
            "yo'qotadi, lekin sxemani ortiqcha "
            "murakkablashtirmaydi.")

    # ───────────────────────────────────────────
    h1(d, "6. Natijaviy sxema")

    code(d, """students        (id, name)
student_phones (student_id, phone, is_primary)
teachers       (id, name, email, degree)
courses        (code, name, hours, teacher_id)
enrollments    (student_id, course_code, grade, enrolled_at)""")

    para(d, "Bitta jadvaldan beshta jadval chiqdi. Nima yutildi:")

    bullets(d, [
        "Har bir fakt bitta joyda — zid bo'lish imkoni yo'q.",
        "Yangilash bitta satrga tegadi.",
        "Talabani kursga yozmasdan, kursni talabasiz ro'yxatga olish "
        "mumkin.",
        "Oxirgi yozuv o'chirilsa ham talaba va kurs ma'lumoti "
        "qoladi.",
        "FK orqali butunlik bazada majburlanadi — ilova koddagi xato "
        "ma'lumotni buzolmaydi.",
        "Har bir ustunga aniq `CHECK` va `NOT NULL` qo'yish mumkin.",
    ])

    para(d, "Nima yo'qotildi: ma'lumotni to'liq olish uchun `JOIN` "
            "kerak bo'ladi. Lekin indekslangan FK bo'yicha `JOIN` "
            "arzon — bu deyarli har doim takrorlanish narxidan "
            "kichik.")

    # ───────────────────────────────────────────
    h1(d, "7. Amaliy tartib")

    para(d, "Normalizatsiyani bosqichlarni yodlab emas, savollar "
            "ketma-ketligi bilan bajaraman:")

    bullets(d, [
        "**Bitta katakda bir nechta qiymat bormi?** Bo'lsa — alohida "
        "jadvalga.",
        "**Har bir ustun butun kalitga bog'liqmi?** Faqat qismiga "
        "bog'liq bo'lsa — ajrataman.",
        "**Ustun boshqa ustun orqali bog'langanmi?** Bo'lsa — "
        "alohida jadvalga.",
        "**Bir xil matn bir nechta satrda takrorlanadimi?** "
        "Takrorlansa — bu yo'naltiruvchi (lookup) jadval bo'lishi "
        "kerakligining belgisi.",
    ], numbered=True)

    note(d, "Muhim ogohlik",
         "Normalizatsiya — qoida emas, **asbob**. Maqsad — zid "
         "ma'lumotdan qochish. Agar jadvalni ajratish hech qanday "
         "anomaliyani oldini olmasa va faqat `JOIN` qo'shsa, u "
         "ajratish kerak emas. Ustiga hisobot va tarixiy ma'lumot "
         "uchun ataylab denormalizatsiya to'g'ri qaror bo'lishi "
         "mumkin.")

    # ───────────────────────────────────────────
    h1(d, "8. Amaliyotdan: ko'p tillilik 1NF ni buzadigan joy")

    para(d, "Ish joyimdagi MAD ERP tizimi to'rt tilda ishlaydi: o'zbek lotin, o'zbek "
            "kirill, rus va ingliz. Bu talab 3-bo'limdagi 1NF masalasini juda aniq "
            "ko'rsatadi, shuning uchun uni alohida keltiraman.")

    h2(d, "8.1 Birinchi o'yga keladigan yechim va uning muammosi")

    para(d, "Davlatlar ro'yxati kerak bo'lsa, eng oson yo'l har bir til uchun alohida "
            "ustun qo'yish:")

    code(d, """-- Shunday qilish mumkin edi
CREATE TABLE adm.info_country (
    id          INTEGER GENERATED BY DEFAULT AS IDENTITY,
    name_uz_latn VARCHAR(200),
    name_uz_cyrl VARCHAR(200),
    name_ru      VARCHAR(200),
    name_en      VARCHAR(200)
);""")

    para(d, "Bu 1NF ga rasman mos keladi — har katakda bitta qiymat. Lekin amalda u "
            "takrorlanuvchi guruh: bir xil ma'noli to'rt ustun. 2-bo'limdagi "
            "boshlang'ich holatning aynan o'zi, faqat satr o'rniga ustunda.")

    bullets(d, [
        "Beshinchi til qo'shilsa — migratsiya, ya'ni sxemani o'zgartirish. "
        "Jadvallar soni yuzlab bo'lgan tizimda bu yuzlab migratsiya degani.",
        "Tarjimasi bor ustunlar soni jadvalga qarab farq qiladi: ba'zisida faqat "
        "nom, boshqasida nom va tavsif. Har biri uchun o'z ustunlar to'plami.",
        "\"Qaysi tarjimalar yetishmaydi\" degan so'rov yozish deyarli imkonsiz — "
        "har bir ustunni alohida tekshirish kerak.",
    ])

    h2(d, "8.2 Loyihada tanlangan yechim")

    para(d, "Har bir jadval uchun `{jadval}_translate` nomli juftlik jadval bor va "
            "uning tuzilmasi hamma joyda bir xil:")

    code(d, """CREATE TABLE adm.info_country_translate (
    id                  INTEGER GENERATED BY DEFAULT AS IDENTITY,

    owner_id            INTEGER      NOT NULL,   -- qaysi davlat
    language_id         INTEGER      NOT NULL,   -- qaysi til
    column_name         VARCHAR(100) NOT NULL,   -- qaysi ustun tarjimasi
    translate_text      TEXT         NOT NULL,   -- tarjimaning o'zi

    created_at          TIMESTAMP WITHOUT TIME ZONE NOT NULL DEFAULT NOW(),
    created_by          INTEGER,
    last_modified_at    TIMESTAMP WITHOUT TIME ZONE,
    last_modified_by    INTEGER,

    CONSTRAINT pk_adm_info_country_translate PRIMARY KEY (id),
    CONSTRAINT fk_adm_info_country_translate_owner_id
        FOREIGN KEY (owner_id) REFERENCES adm.info_country(id),
    CONSTRAINT fk_adm_info_country_translate_language_id
        FOREIGN KEY (language_id) REFERENCES adm.enum_language(id)
);""", caption="Konvensiyalar hujjatidan")

    para(d, "Mantiqiy kalit — `(owner_id, language_id, column_name)` uchligi. Ya'ni "
            "\"shu davlatning, shu tildagi, shu ustuni\" bitta qatorga to'g'ri "
            "keladi. Bu 5-bo'limdagi 3NF holatiga mos: `translate_text` to'liq shu "
            "uchlikka bog'liq, boshqa hech narsaga emas.")

    h2(d, "8.3 Nega bu ustunli variantdan yaxshi")

    bullets(d, [
        "Yangi til qo'shish — `enum_language` ga bitta qator. Sxema o'zgarmaydi.",
        "Tuzilma hamma jadval uchun bir xil, shuning uchun C# tomonida umumiy "
        "`TranslateEntity<T>` bazaviy sinfi ishlaydi va har bir jadval uchun "
        "alohida kod yozilmaydi.",
        "Yetishmayotgan tarjimalarni topish bitta so'rov: `language_id` bo'yicha "
        "guruhlab, sonini taqqoslash.",
        "Bo'sh joy tejaladi — tarjimasi yo'q qiymat uchun qator umuman yaratilmaydi, "
        "ustunli variantda esa `NULL` turardi.",
    ])

    h2(d, "8.4 Narxi")

    para(d, "7-bo'limda normalizatsiyaning amaliy tartibi haqida gapirgandim, va "
            "bu yerda uning narxi aniq ko'rinadi.")

    para(d, "Har bir ro'yxatni ko'rsatish uchun endi `JOIN` kerak, va joriy til "
            "parametr sifatida uzatilishi shart. Agar o'nta ma'lumotnoma bir "
            "sahifada ko'rsatilsa — o'nta qo'shimcha birlashtirish. Shuning uchun "
            "kodda projeksiya metodlariga til konteksti beriladi va u hamma joydan "
            "o'tib boradi.")

    note(d, "Menga eng qiziq bo'lgan tomoni:",
         "`column_name` ustuni — bu aslida ma'lumot ichida metama'lumot. Baza "
         "o'zining ustun nomini satr sifatida saqlab yuradi, ya'ni jadval \"o'zi "
         "haqida\" ma'lumot tutadi. Bu toza relyatsion yondashuv emas: "
         "`column_name` ga xato qiymat yozilsa, baza buni sezmaydi. Lekin muqobili "
         "— har bir tarjimalanadigan ustun uchun alohida jadval, ya'ni yuzlab "
         "jadval. Shuning uchun bu yerda normalizatsiya qoidalari biroz bo'shashtirilgan "
         "va buning evaziga bitta universal tuzilma olingan. Men bunday murosalarni "
         "oldin kitoblarda ko'rmagandim — ular odatda \"to'g'ri\" shaklni "
         "ko'rsatadi, real tizimda esa shunday qarorlar ko'p.")

    sources(d, [
        ("Database normalization description",
         "https://learn.microsoft.com/en-us/office/troubleshoot/access/database-normalization-description"),
        ("Data modeling and normalization",
         "https://learn.microsoft.com/en-us/training/modules/design-data-model/"),
        ("Constraints — PostgreSQL",
         "https://www.postgresql.org/docs/current/ddl-constraints.html"),
    ])
