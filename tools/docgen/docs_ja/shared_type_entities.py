# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "Shared-type entity types"
CATEGORY = "EF CORE"
TITLE = "Shared-Type Entity"
SUBTITLE = "Bitta CLR turini bir nechta entity sifatida ishlatish"
FILENAME = "Shared-type entity types.docx"


def build(d):
    h1(d, "1. Oddiy holat va cheklov")

    para(d, "Odatda bitta CLR turi bitta entity turiga mos keladi: "
            "`Order` klassi `orders` jadvaliga. EF Core turni "
            "identifikator sifatida ishlatadi, shuning uchun bir xil "
            "klassni ikki marta map qilib bo'lmaydi.")

    para(d, "Lekin ba'zan bitta tur bir nechta jadvalni ifodalashi kerak. "
            "Klassik misol — ko'pga-ko'p munosabatidagi qo'shimcha "
            "jadvallar yoki `Dictionary<string, object>` bilan dinamik "
            "model qurish.")

    # ───────────────────────────────────────────
    h1(d, "2. Shared-type entity e'lon qilish")

    para(d, "Bunday entity **nom bilan** ajratiladi, tur bilan emas:")

    code(d, """// Bitta CLR turi — ikki alohida entity
modelBuilder.SharedTypeEntity<AuditEntry>("OrderAudit", b =>
{
    b.ToTable("order_audit");
    b.HasKey(e => e.Id);
    b.Property(e => e.EntityId).HasColumnName("order_id");
});

modelBuilder.SharedTypeEntity<AuditEntry>("CustomerAudit", b =>
{
    b.ToTable("customer_audit");
    b.HasKey(e => e.Id);
    b.Property(e => e.EntityId).HasColumnName("customer_id");
});""")

    para(d, "Ikkisi bir xil `AuditEntry` klassidan foydalanadi, lekin "
            "turli jadvalga yoziladi va turli ustun nomlariga ega.")

    h2(d, "Murojaat qilish")

    para(d, "Shared-type entity bilan ishlash uchun `Set<T>()` ga "
            "**nom** uzatiladi:")

    code(d, """var orderAudit = db.Set<AuditEntry>("OrderAudit");

await orderAudit
    .Where(e => e.EntityId == orderId)
    .OrderByDescending(e => e.OccurredAt)
    .ToListAsync(ct);

db.Set<AuditEntry>("CustomerAudit").Add(entry);
await db.SaveChangesAsync(ct);""")

    note(d, "Muhim",
         "Oddiy `db.Set<AuditEntry>()` — nomsiz chaqiruv — ishlamaydi va "
         "exception beradi. Shared-type entity har doim nom bilan "
         "so'raladi, chunki tur o'zi qaysi entity ekanini bilmaydi.")

    # ───────────────────────────────────────────
    h1(d, "3. Dictionary bilan dinamik model")

    para(d, "EF Core `Dictionary<string, object>` ni entity sifatida "
            "ishlatishni qo'llab-quvvatlaydi. Bu \"property bag\" deb "
            "ataladi va sxemasi ish vaqtida aniqlanadigan ma'lumot "
            "uchun mo'ljallangan:")

    code(d, """modelBuilder.SharedTypeEntity<Dictionary<string, object>>("ProductAttribute", b =>
{
    b.ToTable("product_attributes");
    b.Property<Guid>("Id");
    b.Property<Guid>("ProductId");
    b.Property<string>("Name").HasMaxLength(64);
    b.Property<string>("Value").HasMaxLength(512);
    b.HasKey("Id");
});""")

    code(d, """var attributes = db.Set<Dictionary<string, object>>("ProductAttribute");

attributes.Add(new Dictionary<string, object>
{
    ["Id"] = Guid.CreateVersion7(),
    ["ProductId"] = productId,
    ["Name"] = "rang",
    ["Value"] = "qora"
});

await db.SaveChangesAsync(ct);""")

    para(d, "Bu kuchli imkoniyat, lekin narxi katta: tiplar tekshirilmaydi, "
            "kalit nomi matn, va IDE yordam bermaydi. Shuning uchun uni "
            "faqat haqiqatan dinamik sxema kerak bo'lganda — masalan "
            "foydalanuvchi o'zi maydon qo'shadigan tizimda — "
            "ishlataman.")

    # ───────────────────────────────────────────
    h1(d, "4. Eng ko'p uchraydigan amaliy holat: join jadvali")

    para(d, "Ko'pga-ko'p munosabatida EF o'zi yashirin shared-type "
            "entity yaratadi. Buni ko'rish uchun:")

    code(d, """modelBuilder.Entity<Post>()
    .HasMany(p => p.Tags)
    .WithMany(t => t.Posts)
    .UsingEntity<Dictionary<string, object>>(
        "PostTag",
        j => j.HasOne<Tag>().WithMany().HasForeignKey("TagId"),
        j => j.HasOne<Post>().WithMany().HasForeignKey("PostId"),
        j =>
        {
            j.ToTable("post_tags");
            j.Property<DateTimeOffset>("AddedAt").HasDefaultValueSql("now()");
        });""")

    para(d, "Bu yerda qo'shimcha maydon (`AddedAt`) qo'shildi, lekin "
            "alohida entity klassi yozilmadi. Natijada kod kam, lekin "
            "`AddedAt` ni o'qish uchun shared-type entity orqali "
            "murojaat qilish kerak:")

    code(d, """var links = await db.Set<Dictionary<string, object>>("PostTag")
    .Where(j => (Guid)j["PostId"] == postId)
    .ToListAsync(ct);""")

    para(d, "Shuning uchun qo'shimcha maydonlar bilan ishlash kerak "
            "bo'lsa, oddiy entity klassini yozishni afzal ko'raman — "
            "u tipik va o'qiladigan bo'ladi:")

    code(d, """public sealed class PostTag
{
    public Guid PostId { get; init; }
    public Guid TagId { get; init; }
    public DateTimeOffset AddedAt { get; init; }
}""")

    # ───────────────────────────────────────────
    h1(d, "5. Qachon ishlatish va qachon yo'q")

    para(d, "Shared-type entity — nozik asbob va uni kerak bo'lmaganda "
            "ishlatish kodni tushunarsiz qiladi.")

    table(d, ["Holat", "Yechim"],
          [["Bir xil tuzilishli audit jadvallari",
            "Shared-type entity mos keladi"],
           ["Dinamik, foydalanuvchi aniqlagan maydonlar",
            "Property bag yoki JSON ustun"],
           ["Qo'shimcha maydonli join jadvali",
            "Oddiy entity klassi yaxshiroq"],
           ["Bir nechta mijoz uchun bir xil jadval",
            "Query filter yoki alohida sxema"],
           ["Bir xil tuzilishli, lekin turli ma'noli entity'lar",
            "Alohida klasslar — aniqroq"]],
          widths=[7.0, 7.5])

    para(d, "Oxirgi qatorni alohida ta'kidlayman: ikki entity bir xil "
            "maydonlarga ega bo'lsa ham, agar ularning **ma'nosi** "
            "boshqa bo'lsa, alohida klass yozish to'g'ri. Kodni "
            "qisqartirish uchun ikki domen tushunchasini bir klassga "
            "siqish keyinchalik chalkashlik keltiradi — masalan biriga "
            "yangi maydon kerak bo'lganda.")

    note(d, "Mening pozitsiyam",
         "Shared-type entity'ni asosan EF ning ichki mexanizmi "
         "sifatida ko'raman — ko'pga-ko'p munosabatlar uning ustida "
         "ishlaydi. O'z kodimda uni kamdan-kam ishlataman, chunki "
         "aniq klasslar deyarli har doim o'qilishi qulayroq.")

    sources(d, [
        ("Shared-type entity types — EF Core",
         "https://learn.microsoft.com/en-us/ef/core/modeling/entity-types#shared-type-entity-types"),
        ("Property bags in EF Core",
         "https://learn.microsoft.com/en-us/ef/core/modeling/shadow-properties#property-bag-entity-types"),
        ("Many-to-many relationships",
         "https://learn.microsoft.com/en-us/ef/core/modeling/relationships/many-to-many"),
    ])
