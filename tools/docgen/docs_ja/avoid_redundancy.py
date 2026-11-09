# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "Avoid redundancy principle"
CATEGORY = "Database Design Principles"
TITLE = "Takrorlanishdan Qochish Printsipi"
SUBTITLE = "Bir xil fakt bir joyda saqlanishi kerak"
FILENAME = "Avoid redundancy principle.docx"


def build(d):
    h1(d, "1. Printsip nima deydi")

    para(d, "Bitta fakt bazada **bitta joyda** saqlanishi kerak. "
            "Agar bir xil ma'lumot ikki joyda bo'lsa, ular bir-biriga "
            "zid bo'lib qolish ehtimoli paydo bo'ladi — va vaqt o'tishi "
            "bilan bu albatta sodir bo'ladi.")

    para(d, "Bu normalizatsiya bilan chambarchas bog'liq, lekin "
            "undan kengroq tushuncha: normalizatsiya rasmiy qoidalar "
            "to'plami, takrorlanishdan qochish esa umumiy maqsad.")

    # ───────────────────────────────────────────
    h1(d, "2. Takrorlanish keltiradigan anomaliyalar")

    code(d, """CREATE TABLE orders (
    id              bigserial PRIMARY KEY,
    customer_name   text,          -- takrorlanadi
    customer_phone  text,          -- takrorlanadi
    customer_city   text,          -- takrorlanadi
    product_name    text,
    product_price   numeric,
    quantity        integer,
    total           numeric        -- hisoblanadi
);""")

    h2(d, "Yangilash anomaliyasi (update anomaly)")

    para(d, "Mijoz telefon raqamini o'zgartirdi. Uning 40 ta "
            "buyurtmasi bor, demak 40 ta satrni yangilash kerak. "
            "Agar 39 tasi yangilansa va bittasi qolib ketsa — "
            "ma'lumot zid bo'ladi va qaysi biri to'g'ri ekanini "
            "aniqlash imkoni yo'q.")

    h2(d, "Qo'shish anomaliyasi (insert anomaly)")

    para(d, "Yangi mijozni buyurtmasiz ro'yxatga olish mumkin emas, "
            "chunki mijoz ma'lumoti faqat `orders` jadvalida yashaydi. "
            "Shuning uchun \"bo'sh\" buyurtma yaratishga to'g'ri "
            "keladi — bu esa ma'lumotni yana buzadi.")

    h2(d, "O'chirish anomaliyasi (delete anomaly)")

    para(d, "Mijozning oxirgi buyurtmasi o'chirilsa, uning kontakt "
            "ma'lumoti ham butunlay yo'qoladi. Bu ma'lumotni "
            "bexosdan yo'qotish — eng xavfli holatlardan biri.")

    note(d, "Qo'shimcha narx",
         "Takrorlangan ma'lumot disk joyini ham oladi va bu "
            "kutilganidan ko'proq: `customer_name` 50 bayt bo'lsa va "
            "10 million buyurtma bo'lsa, faqat shu ustun 500 MB joy "
            "egallaydi. Indekslar esa yana shuncha.")

    # ───────────────────────────────────────────
    h1(d, "3. To'g'ri sxema")

    code(d, """CREATE TABLE customers (
    id      bigserial PRIMARY KEY,
    name    text NOT NULL,
    phone   text NOT NULL,
    city_id bigint REFERENCES cities(id)
);

CREATE TABLE products (
    id    bigserial PRIMARY KEY,
    name  text    NOT NULL,
    price numeric NOT NULL
);

CREATE TABLE orders (
    id          bigserial   PRIMARY KEY,
    customer_id bigint      NOT NULL REFERENCES customers(id),
    created_at  timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE order_items (
    order_id   bigint  NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
    product_id bigint  NOT NULL REFERENCES products(id),
    quantity   integer NOT NULL CHECK (quantity > 0),
    unit_price numeric NOT NULL,          -- ataylab nusxa, pastga qarang
    PRIMARY KEY (order_id, product_id)
);""")

    para(d, "Endi mijoz telefoni bitta joyda — uni yangilash bitta "
            "`UPDATE`. Mijozni buyurtmasiz ro'yxatga olish mumkin. "
            "Buyurtma o'chirilsa mijoz qoladi.")

    # ───────────────────────────────────────────
    h1(d, "4. Ataylab takrorlash: tarixiy qiymat")

    para(d, "`order_items.unit_price` — bu takrorlanish emas, "
            "ataylab saqlangan **tarixiy fakt**.")

    para(d, "Agar narx faqat `products` jadvalida bo'lsa va narx "
            "o'zgarsa, eski buyurtmalar summasi ham o'zgarib "
            "ketadi — ya'ni o'tgan oy chiqarilgan hisobot bugun "
            "boshqa raqam beradi. Bu jiddiy buxgalteriya xatosi.")

    bullets(d, [
        "`products.price` — **joriy** narx, yangi buyurtmalar uchun.",
        "`order_items.unit_price` — **o'sha paytdagi** narx, bu "
        "boshqa fakt.",
    ])

    para(d, "Shuning uchun qoidaning aniq ta'rifi muhim: takrorlanish "
            "— bir **xil faktning** ikki nusxasi. Ikki turli vaqtdagi "
            "narx esa ikki turli fakt.")

    para(d, "Shu mantiq bilan buyurtmada manzil va mijoz ismini ham "
            "nusxalash to'g'ri bo'ladi — chek bosilgandan keyin mijoz "
            "ko'chib ketsa, chekdagi manzil o'zgarmasligi kerak.")

    # ───────────────────────────────────────────
    h1(d, "5. Hisoblanadigan maydonlar")

    para(d, "`orders.total` — hisoblanadigan qiymat, shuning uchun "
            "uni saqlash takrorlanish hisoblanadi. Uch variant bor.")

    h2(d, "1. Har safar hisoblash")

    code(d, """SELECT o.id, SUM(i.quantity * i.unit_price) AS total
FROM orders o
JOIN order_items i ON i.order_id = o.id
GROUP BY o.id;""")

    para(d, "Eng toza, zid bo'lish imkoni yo'q. Lekin katta hajmda "
            "sekin bo'lishi mumkin.")

    h2(d, "2. Generated column")

    code(d, """-- Satr ichidagi ustunlardan hisoblanadi
ALTER TABLE order_items
ADD COLUMN line_total numeric
GENERATED ALWAYS AS (quantity * unit_price) STORED;""")

    para(d, "Baza o'zi hisoblaydi va zid bo'lishi mumkin emas. Lekin "
            "faqat **bir satr ichidagi** ustunlardan hisoblash "
            "mumkin — boshqa jadvaldan agregatsiya qilib bo'lmaydi.")

    h2(d, "3. Denormalizatsiya — ataylab saqlash")

    code(d, """-- Trigger bilan avtomatik yangilash
CREATE OR REPLACE FUNCTION refresh_order_total() RETURNS trigger
LANGUAGE plpgsql AS $$
BEGIN
    UPDATE orders o
    SET total = (SELECT COALESCE(SUM(quantity * unit_price), 0)
                 FROM order_items WHERE order_id = o.id)
    WHERE o.id = COALESCE(NEW.order_id, OLD.order_id);

    RETURN NULL;
END;
$$;""")

    para(d, "Bu tez o'qish beradi, lekin narxi bor: trigger "
            "ko'rinmas (kodni o'qigan odam nega qiymat o'zgarganini "
            "tushunmaydi), bulk insert sekinlashadi, va `ExecuteUpdate` "
            "kabi ORM operatsiyalari trigger'ni chetlab o'tishi "
            "mumkin.")

    note(d, "Mening tartibim",
         "Avval hisoblashni tanlayman. Sekin bo'lishi **o'lchov bilan "
         "tasdiqlansa** — generated column yoki materialized view. "
         "Trigger bilan denormalizatsiyani oxirgi chora deb bilaman, "
         "chunki u zid holatga tushish imkonini qoldiradi.")

    # ───────────────────────────────────────────
    h1(d, "6. Qachon denormalizatsiya to'g'ri")

    bullets(d, [
        "**Hisobot va analitika.** O'qish juda ko'p, yozish kam, "
        "bir necha daqiqa eskirish qabul qilinadi — materialized "
        "view yoki alohida read model.",
        "**Tarixiy nusxa.** Yuqorida ko'rilgan narx va manzil "
        "misollari.",
        "**Juda qimmat agregatsiya.** Million satr bo'yicha "
        "hisoblash har so'rovda bajarilishi mumkin emas.",
        "**Taqsimlangan tizim.** Servislar orasida `JOIN` qilib "
        "bo'lmaydi, shuning uchun ma'lumotni nusxalash kerak "
        "bo'ladi — lekin bunda bir manba \"haqiqat egasi\" "
        "bo'lishi kerak.",
    ])

    para(d, "Har bir denormalizatsiyada men uchta savolga javob "
            "beraman: **kim yangilaydi**, **qancha eskirish qabul "
            "qilinadi**, va **zid bo'lsa qaysi manba to'g'ri "
            "hisoblanadi**. Uchtasiga javob bo'lmasa, "
            "denormalizatsiya qilmayman.")

    sources(d, [
        ("Database normalization basics",
         "https://learn.microsoft.com/en-us/office/troubleshoot/access/database-normalization-description"),
        ("Generated columns — PostgreSQL",
         "https://www.postgresql.org/docs/current/ddl-generated-columns.html"),
        ("Materialized views — PostgreSQL",
         "https://www.postgresql.org/docs/current/rules-materializedviews.html"),
    ])
