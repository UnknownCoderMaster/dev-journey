# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "View, MV"
CATEGORY = "Postgres / Oracle"
TITLE = "View va Materialized View"
SUBTITLE = "Saqlangan so'rovlar va saqlangan natijalar"
FILENAME = "View, MV.docx"


def build(d):
    h1(d, "1. View nima")

    para(d, "View — nom berilgan va saqlangan `SELECT` so'rovi. U jadval "
            "kabi ishlatiladi, lekin o'z ma'lumotini saqlamaydi — har "
            "murojaatda asosiy so'rov qaytadan bajariladi.")

    code(d, """CREATE VIEW active_customers AS
SELECT c.id, c.full_name, c.email, COUNT(o.id) AS order_count
FROM customers c
LEFT JOIN orders o ON o.customer_id = c.id AND o.status = 'paid'
WHERE c.is_deleted = false
GROUP BY c.id, c.full_name, c.email;""")

    code(d, """SELECT * FROM active_customers WHERE order_count > 5;""")

    h2(d, "1.1 Nima uchun foydali")

    bullets(d, [
        "**Murakkab so'rovni soddalashtirish** — ko'p `JOIN` li so'rov bir "
        "marta yoziladi.",
        "**Takrorlanishni kamaytirish** — bir xil mantiq bir joyda turadi.",
        "**Kirishni cheklash** — foydalanuvchiga jadval emas, view ga "
        "ruxsat berish mumkin.",
        "**Sxema o'zgarishini yashirish** — jadval tuzilmasi o'zgarsa, view "
        "eski ko'rinishni saqlab qolishi mumkin.",
    ])

    code(d, """-- Maxfiy ustunlarsiz ko'rinish
CREATE VIEW public_users AS
SELECT id, full_name, created_at FROM users;

GRANT SELECT ON public_users TO reporting_user;
-- users jadvalining o'ziga ruxsat berilmaydi""")

    note(d, "Bu oxirgi qo'llanish menga juda mantiqiy tuyuladi:",
         "Hisobot tizimiga bazaga kirish kerak, lekin unga parol hash lari "
         "yoki shaxsiy ma'lumotlar kerak emas. View orqali men aynan "
         "kerakli ustunlarni ochaman va qolganini butunlay yashiraman. "
         "Ilova kodidagi tekshiruvdan farqli o'laroq, buni chetlab o'tib "
         "bo'lmaydi.")

    # ───────────────────────────────────────────
    h1(d, "2. View ning unumdorligi")

    para(d, "View — bu shunchaki saqlangan matn. Unga murojaat qilinganda "
            "PostgreSQL uning ta'rifini asosiy so'rovga qo'shib yuboradi va "
            "butun so'rovni birgalikda optimallashtiradi.")

    code(d, """-- Bu so'rov
SELECT * FROM active_customers WHERE id = 7;

-- Taxminan shunga aylanadi
SELECT c.id, c.full_name, ...
FROM customers c LEFT JOIN orders o ...
WHERE c.is_deleted = false AND c.id = 7
GROUP BY ...;""")

    note(d, "Shuning uchun view o'zi tezlik bermaydi:",
         "Men avval view ni optimallashtirish vositasi deb o'ylardim. "
         "Aslida u faqat **kod tashkiloti** vositasi. Agar asosiy so'rov "
         "sekin bo'lsa, view ham sekin bo'ladi. Tezlik uchun materialized "
         "view kerak.")

    note(d, "Yana bir tuzoq — ichma-ich view lar:",
         "View ustiga view, uning ustiga yana view qurilsa, planner oxirida "
         "juda katta so'rov bilan ishlaydi. Bir necha darajadan keyin u "
         "yaxshi reja tuza olmay qoladi. Men ikki darajadan ortiq "
         "ichma-ichlikdan qochaman.")

    # ───────────────────────────────────────────
    h1(d, "3. Materialized View")

    para(d, "Materialized view so'rov natijasini **fizik saqlaydi**. "
            "Murojaat qilinganda so'rov qaytadan bajarilmaydi — tayyor "
            "ma'lumot o'qiladi.")

    code(d, """CREATE MATERIALIZED VIEW monthly_sales AS
SELECT
    date_trunc('month', o.created_at) AS month,
    p.category_id,
    SUM(oi.quantity * oi.unit_price) AS revenue,
    COUNT(DISTINCT o.id) AS order_count
FROM orders o
JOIN order_items oi ON oi.order_id = o.id
JOIN products p ON p.id = oi.product_id
WHERE o.status = 'paid'
GROUP BY 1, 2
WITH DATA;""")

    code(d, """-- Indeks qo'yish mumkin — oddiy view da bu imkonsiz
CREATE INDEX ix_monthly_sales_month ON monthly_sales (month);
CREATE UNIQUE INDEX ux_monthly_sales ON monthly_sales (month, category_id);""")

    h2(d, "3.1 Yangilash")

    code(d, """-- Oddiy yangilash — davomida view ni o'qib bo'lmaydi
REFRESH MATERIALIZED VIEW monthly_sales;

-- Bloklanmasdan — noyob indeks talab qilinadi
REFRESH MATERIALIZED VIEW CONCURRENTLY monthly_sales;""")

    note(d, "`CONCURRENTLY` uchun noyob indeks majburiy:",
         "Usiz PostgreSQL xatolik beradi. Sababi — u eski va yangi "
         "ma'lumotni satr-satr solishtirishi kerak va buning uchun har bir "
         "satrni aniqlaydigan kalit zarur. Bu talab birinchi marta "
         "chalkashtiradi, lekin mantiqi aniq.")

    h2(d, "3.2 Avtomatik yangilash")

    para(d, "PostgreSQL materialized view ni avtomatik yangilamaydi — buni "
            "o'zim tashkil qilishim kerak:")

    code(d, """-- pg_cron kengaytmasi bilan
SELECT cron.schedule(
    'refresh-monthly-sales',
    '0 2 * * *',
    'REFRESH MATERIALIZED VIEW CONCURRENTLY monthly_sales'
);""")

    code(d, """// Yoki ilovadagi fon vazifasi bilan
RecurringJob.AddOrUpdate(
    "refresh-monthly-sales",
    () => _db.Database.ExecuteSqlRaw(
        "REFRESH MATERIALIZED VIEW CONCURRENTLY monthly_sales"),
    "0 2 * * *");""")

    # ───────────────────────────────────────────
    h1(d, "4. Taqqoslash")

    table(d, ["Jihat", "View", "Materialized View"],
          [["Ma'lumot saqlaydi", "Yo'q", "Ha"],
           ["Har doim dolzarb", "Ha", "Yo'q — yangilashga bog'liq"],
           ["O'qish tezligi", "Asosiy so'rovga teng", "Juda tez"],
           ["Indeks qo'yish", "Mumkin emas", "Mumkin"],
           ["Disk joyi", "Egallamaydi", "Egallaydi"],
           ["Yangilash kerakmi", "Yo'q", "Ha"]],
          widths=[4.0, 5.4, 6.1])

    para(d, "Tanlov oddiy savolga bog'liq: ma'lumot necha daqiqa eskirgan "
            "bo'lishi mumkin? Agar javob \"umuman emas\" bo'lsa — oddiy "
            "view. Agar \"bir necha soat\" bo'lsa — materialized view.")

    note(d, "Amalda ko'p hisobotlar ikkinchi toifaga tushadi:",
         "\"Kecha qancha sotildi\" degan savolga javob kechagi ma'lumot "
         "asosida beriladi va u bugun o'zgarmaydi. Bunday hisobotni har "
         "safar qaytadan hisoblash — bekorga resurs sarflash.")

    # ───────────────────────────────────────────
    h1(d, "5. Yangilanadigan view")

    para(d, "Oddiy view ga yozish ham mumkin, agar u yetarlicha sodda "
            "bo'lsa — bitta jadval, agregatsiyasiz, `DISTINCT` siz.")

    code(d, """CREATE VIEW active_products AS
SELECT id, name, price, category_id
FROM products
WHERE is_deleted = false
WITH CHECK OPTION;""")

    code(d, """-- Bu ishlaydi
UPDATE active_products SET price = 55000 WHERE id = 42;

-- Bu rad etiladi — WITH CHECK OPTION tufayli
INSERT INTO active_products (name, is_deleted) VALUES ('Test', true);""")

    h2(d, "5.1 INSTEAD OF trigger")

    para(d, "Murakkab view ga yozish uchun trigger yoziladi:")

    code(d, """CREATE OR REPLACE FUNCTION customers_view_insert()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO customers (full_name, email)
    VALUES (NEW.full_name, NEW.email)
    RETURNING id INTO NEW.id;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER active_customers_insert
    INSTEAD OF INSERT ON active_customers
    FOR EACH ROW
    EXECUTE FUNCTION customers_view_insert();""")

    # ───────────────────────────────────────────
    h1(d, "6. EF Core bilan ishlash")

    code(d, """public class MonthlySales
{
    public DateTime Month { get; set; }
    public int CategoryId { get; set; }
    public decimal Revenue { get; set; }
    public int OrderCount { get; set; }
}""")

    code(d, """modelBuilder.Entity<MonthlySales>(e =>
{
    e.HasNoKey();                      // yoki kalit bo'lsa HasKey
    e.ToView("monthly_sales");
});""")

    code(d, """var sales = await db.Set<MonthlySales>()
    .Where(s => s.Month >= from)
    .OrderBy(s => s.Month)
    .ToListAsync(ct);""")

    note(d, "`ToView` muhim tafsilot beradi:",
         "U EF Core ga bu obyekt uchun migratsiya yaratmaslikni aytadi — "
         "view ni men o'zim SQL orqali boshqaraman. Agar `ToTable` yozsam, "
         "EF Core uni jadval deb hisoblab, migratsiyada `CREATE TABLE` "
         "generatsiya qiladi.")

    code(d, """// View ni migratsiya orqali yaratish
migrationBuilder.Sql(@"
    CREATE OR REPLACE VIEW active_customers AS
    SELECT ...;
");""")

    # ───────────────────────────────────────────
    h1(d, "7. Boshqarish buyruqlari")

    code(d, """-- Mavjud view lar
SELECT table_name FROM information_schema.views
WHERE table_schema = 'public';

-- Materialized view lar va to'ldirilganmi
SELECT matviewname, ispopulated,
       pg_size_pretty(pg_total_relation_size(oid)) AS size
FROM pg_matviews
JOIN pg_class ON pg_class.relname = matviewname;

-- Ta'rifini ko'rish
SELECT pg_get_viewdef('active_customers'::regclass, true);""")

    # ───────────────────────────────────────────
    h1(d, "8. Xulosa")

    bullets(d, [
        "View — saqlangan so'rov; u ma'lumot saqlamaydi va tezlik bermaydi.",
        "U kod tashkiloti va kirishni cheklash vositasi sifatida qimmatli.",
        "Ichma-ich view lar plannerni chalg'itadi — ikki darajadan oshmaslik "
        "kerak.",
        "Materialized view natijani fizik saqlaydi va indekslanishi mumkin.",
        "U avtomatik yangilanmaydi — `REFRESH` ni o'zim rejalashtirishim "
        "kerak.",
        "`REFRESH CONCURRENTLY` bloklamaydi, lekin noyob indeks talab "
        "qiladi.",
        "Oddiy view ga yozish mumkin; murakkabi uchun `INSTEAD OF` trigger "
        "kerak.",
        "EF Core da `ToView` ishlatiladi va view migratsiya SQL i bilan "
        "boshqariladi.",
    ])

    sources(d, [
        ("CREATE VIEW — PostgreSQL hujjati",
         "https://www.postgresql.org/docs/current/sql-createview.html"),
        ("Materialized Views — PostgreSQL hujjati",
         "https://www.postgresql.org/docs/current/rules-materializedviews.html"),
        ("REFRESH MATERIALIZED VIEW — PostgreSQL",
         "https://www.postgresql.org/docs/current/sql-refreshmaterializedview.html"),
        ("Keyless entity types — EF Core",
         "https://learn.microsoft.com/en-us/ef/core/modeling/keyless-entity-types"),
    ])
