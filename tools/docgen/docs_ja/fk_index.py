# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "How to stop EF creating indexes for foreign keys"
CATEGORY = "EF CORE"
TITLE = "Foreign Key Indekslarini Boshqarish"
SUBTITLE = "EF avtomatik yaratgan indeksni o'chirish va qachon bu kerak"
FILENAME = "Foreign key uchun indeks yaratishni to'xtatish.docx"


def build(d):
    h1(d, "1. EF nega FK uchun indeks yaratadi")

    para(d, "EF Core har bir foreign key ustuni uchun indeks yaratadi. "
            "Buning sababi bor: FK bo'yicha so'rovlar ko'p uchraydi "
            "(`WHERE order_id = ...`) va ota satrni o'chirishda yoki "
            "yangilashda baza bola satrlarni tekshirishi kerak. Indeks "
            "bo'lmasa, bu tekshiruv to'liq jadval skanlashiga aylanadi.")

    code(d, """modelBuilder.Entity<OrderItem>()
    .HasOne(i => i.Order)
    .WithMany(o => o.Items)
    .HasForeignKey(i => i.OrderId);""")

    code(d, """-- EF yasagan migratsiya
CREATE INDEX "IX_order_items_order_id" ON order_items (order_id);""")

    para(d, "Ko'p holatda bu to'g'ri qaror. Lekin har doim emas.")

    # ───────────────────────────────────────────
    h1(d, "2. Qachon bu indeks ortiqcha")

    h2(d, "Composite kalit allaqachon qoplagan")

    para(d, "Eng ko'p uchraydigan holat. Jadvalning birlamchi kaliti "
            "`(OrderId, ProductId)` bo'lsa, u bilan birga indeks "
            "yaratiladi va u `OrderId` bo'yicha qidiruvni ham qoplaydi.")

    code(d, """modelBuilder.Entity<OrderItem>()
    .HasKey(i => new { i.OrderId, i.ProductId });""")

    para(d, "B-tree indeksi chapdan boshlab ishlatiladi, shuning uchun "
            "`(OrderId, ProductId)` indeksi `WHERE order_id = ...` "
            "so'roviga to'liq yetadi. EF yaratgan alohida "
            "`IX_..._order_id` indeksi esa shu ishni ikkinchi marta "
            "qiladi — ya'ni sof ortiqcha yuk.")

    h2(d, "Mening o'z indeksim kengroq")

    code(d, """modelBuilder.Entity<Order>()
    .HasIndex(o => new { o.CustomerId, o.CreatedAt });""")

    para(d, "Bu indeks `CustomerId` bo'yicha qidiruvni ham qoplaydi, "
            "shuning uchun EF ning `IX_orders_customer_id` indeksi "
            "kerak emas.")

    h2(d, "Tanlanuvchanlik juda past")

    para(d, "FK faqat bir nechta turli qiymatga ega bo'lsa (masalan "
            "`StatusId` — 5 ta holat), indeks deyarli ishlatilmaydi: "
            "planner to'liq skanlashni tezroq deb hisoblaydi va to'g'ri "
            "qiladi.")

    # ───────────────────────────────────────────
    h1(d, "3. Indeksning narxi")

    para(d, "Ortiqcha indeksni \"zarari yo'q\" deb qoldirish — keng "
            "tarqalgan xato. Har bir indeks aniq narxga ega:")

    bullets(d, [
        "**Yozishni sekinlashtiradi.** Har bir `INSERT`, `UPDATE` va "
        "`DELETE` hamma tegishli indeksni ham yangilaydi.",
        "**Disk joyini oladi.** Katta jadvalda indeks asosiy "
        "ma'lumotdan kam bo'lmasligi mumkin.",
        "**Kesh samaradorligini pasaytiradi.** Indeks sahifalari ham "
        "shared buffer'da joy egallaydi va foydali ma'lumotni "
        "siqib chiqaradi.",
        "**Planner'ni chalg'itishi mumkin.** Juda ko'p o'xshash indeks "
        "bo'lsa, optimizator noto'g'ri tanlov qilishi mumkin.",
        "**VACUUM va REINDEX uzoqroq ishlaydi.**",
    ])

    # ───────────────────────────────────────────
    h1(d, "4. Bitta indeksni o'chirish")

    para(d, "EF Core'da \"indeks yaratmasin\" degan to'g'ridan-to'g'ri "
            "sozlama yo'q. Yaratilgan indeksni modeldan **olib tashlash** "
            "kerak:")

    code(d, """var entity = modelBuilder.Entity<OrderItem>().Metadata;

var index = entity.FindIndex(entity.FindProperty(nameof(OrderItem.OrderId))!);
if (index is not null)
    entity.RemoveIndex(index);""")

    para(d, "Yoki `IsCreatedByConvention` tekshiruvi bilan — faqat EF "
            "o'zi yaratganini o'chirish uchun:")

    code(d, """modelBuilder.Entity<OrderItem>()
    .HasIndex(i => i.OrderId)
    .HasDatabaseName("IX_order_items_order_id");

// Keyin migratsiyada o'chirish yoki metadata'dan olib tashlash""")

    note(d, "Oddiy alternativa",
         "Ko'p holatda eng amaliy yo'l — migratsiya faylini qo'lda "
            "tahrirlash va `CreateIndex` chaqiruvini olib tashlash. "
            "Lekin bu holda EF modeli va baza orasida farq paydo "
            "bo'ladi, keyingi migratsiya indeksni qayta yaratishga "
            "urinadi. Shuning uchun modeldan o'chirish to'g'riroq.")

    # ───────────────────────────────────────────
    h1(d, "5. Hamma ortiqcha FK indeksini topib o'chirish")

    para(d, "Loyihada ko'p composite kalit bo'lsa, buni har bir entity "
            "uchun qo'lda yozish zerikarli. Metadata bo'ylab yurib, "
            "boshqa indeks bilan qoplangan FK indekslarini topish "
            "mumkin:")

    code(d, """protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    base.OnModelCreating(modelBuilder);
    modelBuilder.ApplyConfigurationsFromAssembly(typeof(AppDbContext).Assembly);

    RemoveRedundantForeignKeyIndexes(modelBuilder);
}

private static void RemoveRedundantForeignKeyIndexes(ModelBuilder modelBuilder)
{
    foreach (var entity in modelBuilder.Model.GetEntityTypes())
    {
        var indexes = entity.GetIndexes().ToList();

        foreach (var index in indexes)
        {
            // Boshqa indeks shu ustunlardan boshlanadimi?
            var covered = indexes.Any(other =>
                !ReferenceEquals(other, index) &&
                other.Properties.Count > index.Properties.Count &&
                other.Properties.Take(index.Properties.Count)
                     .SequenceEqual(index.Properties));

            var coveredByKey = entity.GetKeys().Any(key =>
                key.Properties.Count >= index.Properties.Count &&
                key.Properties.Take(index.Properties.Count)
                   .SequenceEqual(index.Properties));

            if (covered || coveredByKey)
                entity.RemoveIndex(index);
        }
    }
}""")

    para(d, "Bu kod \"prefiks qoplash\" qoidasiga asoslangan: "
            "`(A, B)` indeksi `(A)` indeksini qoplaydi, teskarisi "
            "emas. Shuning uchun faqat kengroq indeksning prefiksi "
            "bo'lgan indekslar o'chiriladi.")

    note(d, "Ehtiyotkorlik",
         "Bunday avtomatik o'chirish qulay, lekin uni qo'shgandan keyin "
            "yangi migratsiya yasab, uning mazmunini albatta ko'rib "
            "chiqaman — kutilmaganda kerakli indeks ham o'chib "
            "ketmasligi uchun.")

    # ───────────────────────────────────────────
    h1(d, "6. Qaroni o'lchov bilan qabul qilish")

    para(d, "Indeks kerak yoki keraksiz ekanini taxmin bilan emas, "
            "o'lchov bilan aniqlayman. Postgres'da ishlatilmayotgan "
            "indekslarni topish:")

    code(d, """SELECT
    s.relname        AS jadval,
    s.indexrelname   AS indeks,
    s.idx_scan       AS skanlar,
    pg_size_pretty(pg_relation_size(s.indexrelid)) AS hajm
FROM pg_stat_user_indexes s
JOIN pg_index i ON i.indexrelid = s.indexrelid
WHERE s.idx_scan = 0
  AND NOT i.indisunique
  AND NOT i.indisprimary
ORDER BY pg_relation_size(s.indexrelid) DESC;""")

    para(d, "`idx_scan = 0` — indeks hech qachon ishlatilmagan. Lekin "
            "statistika ilova ishga tushgandan beri yig'iladi, shuning "
            "uchun oyiga bir marta ishlaydigan hisobot indeksini "
            "xato o'chirish xavfi bor. Shuning uchun statistikani "
            "yetarlicha uzoq muddat yig'ilgandan keyin baholayman.")

    para(d, "Konkret so'rovni tekshirish uchun esa:")

    code(d, """EXPLAIN (ANALYZE, BUFFERS)
SELECT * FROM order_items WHERE order_id = '...';""")

    para(d, "Rejada `Index Scan using ...` ko'rinsa — indeks "
            "ishlatilmoqda. `Seq Scan` bo'lsa — yo indeks yo'q, yoki "
            "planner uni foydasiz deb hisoblagan.")

    sources(d, [
        ("Indexes — EF Core",
         "https://learn.microsoft.com/en-us/ef/core/modeling/indexes"),
        ("Relationships — EF Core",
         "https://learn.microsoft.com/en-us/ef/core/modeling/relationships"),
        ("pg_stat_user_indexes — PostgreSQL",
         "https://www.postgresql.org/docs/current/monitoring-stats.html"),
        ("Index usage in PostgreSQL",
         "https://www.postgresql.org/docs/current/indexes-examine.html"),
    ])
