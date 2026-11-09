# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "Configuring a primary key, composite key, Alternate Keys"
CATEGORY = "EF CORE"
TITLE = "Birlamchi, Kompozit va Alternativ Kalitlar"
SUBTITLE = "Kalitlarni sozlash va kalit turini tanlash"
FILENAME = "Configuring a primary key, composite key, Alternate Keys.docx"


def build(d):
    h1(d, "1. Convention bo'yicha kalit")

    para(d, "EF Core kalitni o'zi topadi: xossa nomi `Id` yoki "
            "`{EntityName}Id` bo'lsa, u birlamchi kalit bo'ladi.")

    code(d, """public class Order
{
    public Guid Id { get; set; }        // kalit — avtomatik topiladi
}

public class Customer
{
    public int CustomerId { get; set; } // bu ham kalit sifatida taniladi
}""")

    para(d, "Nom boshqa bo'lsa, uni aniq ko'rsatish kerak:")

    code(d, """// Data annotation
public class Invoice
{
    [Key]
    public Guid InvoiceNumber { get; set; }
}

// Fluent API — afzal ko'raman
modelBuilder.Entity<Invoice>().HasKey(i => i.InvoiceNumber);""")

    # ───────────────────────────────────────────
    h1(d, "2. Kalit turini tanlash")

    para(d, "Bu loyiha boshida qabul qilinadigan va keyinchalik "
            "o'zgartirish juda qimmat bo'lgan qaror.")

    table(d, ["Tur", "Yutuq", "Yo'qotish"],
          [["`int` / `long`", "Kichik, indeks samarali, o'qishga qulay",
            "Bazada generatsiya, ketma-ket (oshkor)"],
           ["`Guid` (v4)", "Mijozda yasash mumkin, taxmin qilinmaydi",
            "16 bayt, tasodifiy — indeks fragmentatsiyasi"],
           ["`Guid` (v7)", "Vaqt bo'yicha tartiblangan, indeksga qulay",
            "16 bayt"],
           ["Tabiiy kalit", "Qo'shimcha ustun kerak emas",
            "O'zgarishi mumkin, FK'larga tarqaladi"]],
          widths=[3.0, 5.6, 5.9])

    para(d, "Mening tanlovim ko'p holatda — `Guid` v7 "
            "(`Guid.CreateVersion7()`, .NET 9+). U tasodifiy Guid'ning "
            "indeks muammosini yechadi, chunki qiymatlar vaqt bo'yicha "
            "o'sib boradi va yangi satrlar indeksning oxiriga qo'shiladi.")

    code(d, """modelBuilder.Entity<Order>()
    .Property(o => o.Id)
    .ValueGeneratedNever();        // ID ni kod o'zi beradi""")

    para(d, "Kalitni kodda yasashning amaliy foydasi: obyektni bazaga "
            "yozishdan **oldin** uning ID'si ma'lum bo'ladi. Shuning "
            "uchun bog'liq obyektlarni bir tranzaksiyada qurish va "
            "hodisalarga ID qo'shish oson.")

    note(d, "Tabiiy kalit haqida",
         "Pasport raqami yoki INN kabi qiymatni birlamchi kalit qilish "
         "jozibali ko'rinadi, lekin xavfli: bu qiymatlar o'zgarishi "
         "mumkin (xato kiritilgan, hujjat almashgan) va o'zgarish hamma "
         "FK'ga tarqaladi. Shuning uchun ularni **alternativ kalit** "
         "qilaman, birlamchi emas.")

    # ───────────────────────────────────────────
    h1(d, "3. Kompozit kalit")

    para(d, "Ikki yoki undan ko'p ustundan tashkil topgan kalit. "
            "Convention bilan aniqlanmaydi — faqat Fluent API orqali:")

    code(d, """public class OrderItem
{
    public Guid OrderId { get; set; }
    public Guid ProductId { get; set; }
    public int Quantity { get; set; }
}

modelBuilder.Entity<OrderItem>()
    .HasKey(i => new { i.OrderId, i.ProductId });""")

    para(d, "Ustunlar tartibi muhim: kalit ustida avtomatik yaratilgan "
            "indeks ham shu tartibda bo'ladi. `(OrderId, ProductId)` "
            "indeksi `OrderId` bo'yicha qidiruvga yordam beradi, lekin "
            "faqat `ProductId` bo'yicha qidiruvga yordam bermaydi.")

    para(d, "Shuning uchun tartibni so'rovlarga qarab tanlayman: "
            "ko'proq filtrlanadigan ustun oldinda bo'lishi kerak.")

    h2(d, "Ko'pga-ko'p munosabatidagi qo'shimcha jadval")

    para(d, "Kompozit kalit ko'pincha shu holatda uchraydi. EF Core 5+ da "
            "oddiy ko'pga-ko'p uchun bu jadvalni e'lon qilish ham shart "
            "emas — EF o'zi yasaydi:")

    code(d, """// Qo'shimcha maydon kerak bo'lmasa — entity yozish shart emas
modelBuilder.Entity<Post>()
    .HasMany(p => p.Tags)
    .WithMany(t => t.Posts)
    .UsingEntity(j => j.ToTable("post_tags"));""")

    para(d, "Lekin qo'shimcha maydon (`AddedAt`, `AddedBy`) kerak bo'lsa, "
            "o'rta entity'ni aniq e'lon qilaman — shunda uni to'liq "
            "boshqarish mumkin.")

    # ───────────────────────────────────────────
    h1(d, "4. Alternativ kalit")

    para(d, "Alternativ kalit — birlamchi kalitdan boshqa, lekin "
            "**unikal va FK uchun maqsad bo'la oladigan** ustun.")

    code(d, """modelBuilder.Entity<Customer>()
    .HasAlternateKey(c => c.TaxNumber);

// Bir nechta ustundan
modelBuilder.Entity<Branch>()
    .HasAlternateKey(b => new { b.CompanyId, b.Code });""")

    h2(d, "Unikal indeksdan farqi")

    para(d, "Ikkisi ham unikallikni ta'minlaydi, lekin farq bor:")

    table(d, ["", "Alternativ kalit", "Unikal indeks"],
          [["Bazada", "`UNIQUE` constraint", "`UNIQUE INDEX`"],
           ["NULL ruxsat", "Yo'q — NOT NULL majburiy", "Ha, ruxsat etiladi"],
           ["FK maqsadi bo'la oladimi", "Ha", "Ko'p holatda ha, lekin "
            "EF buni modelda bilmaydi"],
           ["Niyat", "Bu ham kalit", "Bu qidiruv va cheklov"]],
          widths=[4.6, 4.9, 5.0])

    code(d, """// Oddiy unikallik kerak bo'lsa — indeks yetarli
modelBuilder.Entity<Customer>()
    .HasIndex(c => c.Email)
    .IsUnique();

// Soft delete bilan birga — filtrlangan indeks
modelBuilder.Entity<Customer>()
    .HasIndex(c => c.Email)
    .IsUnique()
    .HasFilter("deleted_at IS NULL");""")

    para(d, "Oxirgi misol amalda juda ko'p kerak bo'ladi: soft delete "
            "ishlatilsa, o'chirilgan yozuvning email'i yangi "
            "foydalanuvchini bloklamasligi kerak.")

    note(d, "Mening qoidam",
         "Alternativ kalitni faqat boshqa jadval unga FK bilan "
         "bog'lanishi kerak bo'lganda ishlataman. Oddiy unikallik "
         "talabida — unikal indeks, chunki u moslashuvchanroq va "
         "`NULL` bilan ishlaydi.")

    # ───────────────────────────────────────────
    h1(d, "5. Kalit qiymatini generatsiya qilish")

    code(d, """// Bazada generatsiya (identity / serial)
modelBuilder.Entity<Order>()
    .Property(o => o.Number)
    .ValueGeneratedOnAdd();

// Kod o'zi beradi
modelBuilder.Entity<Order>()
    .Property(o => o.Id)
    .ValueGeneratedNever();

// Sequence orqali
modelBuilder.HasSequence<long>("order_numbers").StartsAt(1000).IncrementsBy(1);

modelBuilder.Entity<Order>()
    .Property(o => o.Number)
    .HasDefaultValueSql("nextval('order_numbers')");""")

    para(d, "Sequence ishlatganda bilish kerak bo'lgan narsa: u "
            "tranzaksiyadan tashqarida ishlaydi, shuning uchun rollback "
            "bo'lsa raqam qaytmaydi va bo'shliq paydo bo'ladi. Hujjat "
            "raqami uzluksiz bo'lishi kerak bo'lsa, sequence yaramaydi.")

    # ───────────────────────────────────────────
    h1(d, "6. Kalit o'zgartirishning narxi")

    para(d, "Birlamchi kalit turini keyinchalik o'zgartirish — eng "
            "qimmat migratsiyalardan biri. Chunki unga ishora qiladigan "
            "hamma FK ustuni ham o'zgaradi, indekslar qayta quriladi, "
            "va migratsiya paytida jadval qulflanadi.")

    para(d, "Shuning uchun loyiha boshida shu savollarga javob "
            "beraman:")

    bullets(d, [
        "ID tashqariga ko'rinadimi (URL, hujjat)? Ha bo'lsa, ketma-ket "
        "`int` ma'lumot oshkor qiladi — raqobatchi buyurtmalar sonini "
        "bilib oladi.",
        "Ma'lumot bir nechta bazadan birlashtiriladimi yoki offline "
        "yaratiladimi? Ha bo'lsa — `Guid`.",
        "Jadval juda katta bo'ladimi? `int` (4 bayt) va `Guid` (16 bayt) "
        "farqi milliard satrda sezilarli bo'ladi — indekslar ham "
        "to'rt barobar katta bo'ladi.",
    ])

    sources(d, [
        ("Keys — EF Core",
         "https://learn.microsoft.com/en-us/ef/core/modeling/keys"),
        ("Alternate Keys — EF Core",
         "https://learn.microsoft.com/en-us/ef/core/modeling/keys#alternate-keys"),
        ("Indexes — EF Core",
         "https://learn.microsoft.com/en-us/ef/core/modeling/indexes"),
        ("Generated values",
         "https://learn.microsoft.com/en-us/ef/core/modeling/generated-properties"),
    ])
