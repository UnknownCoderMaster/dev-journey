# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "Value Conversions, Configuring a value converter"
CATEGORY = "EF CORE"
TITLE = "Value Conversion"
SUBTITLE = "CLR tipini baza tipiga aylantirish"
FILENAME = "Value Conversions, Configuring a value converter.docx"


def build(d):
    h1(d, "1. Qachon kerak bo'ladi")

    para(d, "Value converter CLR dagi tur bazada boshqa ko'rinishda "
            "saqlanishi kerak bo'lganda ishlatiladi. Eng ko'p uchraydigan "
            "holatlar:")

    bullets(d, [
        "Enum'ni raqam o'rniga matn sifatida saqlash.",
        "Strongly-typed ID (`OrderId`) ni `Guid` sifatida saqlash.",
        "Value object (`Money`, `Email`) ni oddiy ustunga sig'dirish.",
        "Kolleksiyani JSON sifatida saqlash.",
        "Legacy sxemada `bool` ni `'Y'`/`'N'` sifatida saqlash.",
        "`DateOnly` yoki `TimeOnly` ni qo'llab-quvvatlamaydigan "
        "provayderda ishlash.",
    ])

    # ───────────────────────────────────────────
    h1(d, "2. Enum'ni matn sifatida saqlash")

    code(d, """modelBuilder.Entity<Order>()
    .Property(o => o.Status)
    .HasConversion<string>()
    .HasMaxLength(32);""")

    para(d, "Bu eng ko'p ishlatadigan konvertatsiyam. Sababi — raqam "
            "sifatida saqlash mo'rt: enum'ga yangi qiymat **o'rtaga** "
            "qo'shilsa, mavjud satrlarning ma'nosi o'zgarib ketadi:")

    code(d, """// Boshida
public enum OrderStatus { New = 0, Paid = 1, Shipped = 2 }

// Keyin "Cancelled" o'rtaga qo'shildi
public enum OrderStatus { New = 0, Cancelled = 1, Paid = 2, Shipped = 3 }
// Bazada 1 bo'lgan hamma satr endi "Cancelled" bo'lib o'qiladi""")

    para(d, "Matn sifatida saqlanganda bu muammo yo'q va bazani "
            "to'g'ridan-to'g'ri so'rov bilan o'qish ham qulay bo'ladi. "
            "Narxi — ustun kattaroq va taqqoslash sal sekinroq, lekin "
            "bu deyarli har doim arziydi.")

    note(d, "Postgres'da alternativa",
         "Postgres'da native `enum` turi ham bor va Npgsql uni "
         "qo'llab-quvvatlaydi. Lekin unga yangi qiymat qo'shish "
         "migratsiya talab qiladi, shuning uchun oddiy `text` ustun "
         "moslashuvchanroq.")

    # ───────────────────────────────────────────
    h1(d, "3. Strongly-typed ID")

    para(d, "`Guid` tipidagi ID larni aralashtirib yuborish oson — "
            "kompilyator `orderId` va `customerId` orasidagi farqni "
            "ko'rmaydi. Strongly-typed ID bu xatoni oldini oladi:")

    code(d, """public readonly record struct OrderId(Guid Value)
{
    public static OrderId New() => new(Guid.CreateVersion7());
    public override string ToString() => Value.ToString();
}""")

    code(d, """modelBuilder.Entity<Order>()
    .Property(o => o.Id)
    .HasConversion(
        id => id.Value,              // CLR -> baza
        value => new OrderId(value)); // baza -> CLR""")

    para(d, "Endi `FindAsync(customerId)` yozsam kompilyatsiya xatosi "
            "chiqadi. Bu amalda juda ko'p xatoni oldini oladi, ayniqsa "
            "metod bir nechta ID qabul qilganda.")

    h2(d, "Qayta ishlatiladigan converter")

    code(d, """public sealed class OrderIdConverter : ValueConverter<OrderId, Guid>
{
    public OrderIdConverter()
        : base(id => id.Value, value => new OrderId(value)) { }
}""")

    code(d, """// Hamma shunday turga bir joyda qo'llash
protected override void ConfigureConventions(ModelConfigurationBuilder builder)
{
    builder.Properties<OrderId>().HaveConversion<OrderIdConverter>();
    builder.Properties<CustomerId>().HaveConversion<CustomerIdConverter>();
}""")

    # ───────────────────────────────────────────
    h1(d, "4. Value object")

    code(d, """public readonly record struct Email
{
    public string Value { get; }

    public Email(string value)
    {
        if (!value.Contains('@'))
            throw new ArgumentException("Email formati noto'g'ri");

        Value = value.Trim().ToLowerInvariant();
    }
}""")

    code(d, """modelBuilder.Entity<Customer>()
    .Property(c => c.Email)
    .HasConversion(e => e.Value, v => new Email(v))
    .HasMaxLength(256);""")

    para(d, "Bu yerda qo'shimcha foyda bor: validatsiya turning o'zida "
            "yashaydi, shuning uchun noto'g'ri email bilan `Customer` "
            "yaratish mumkin emas — qaysi qatlamdan kelganidan qat'i "
            "nazar.")

    note(d, "Diqqat",
         "Bazadan o'qiganda ham konstruktor ishlaydi. Agar bazada "
         "allaqachon noto'g'ri ma'lumot bo'lsa, o'qish exception beradi. "
         "Shuning uchun bazadan o'qish uchun validatsiyasiz alohida yo'l "
         "qoldirish yoki ma'lumotni avval tozalash kerak.")

    # ───────────────────────────────────────────
    h1(d, "5. Kolleksiyani JSON sifatida saqlash")

    code(d, """modelBuilder.Entity<Product>()
    .Property(p => p.Tags)
    .HasConversion(
        tags => JsonSerializer.Serialize(tags, (JsonSerializerOptions?)null),
        json => JsonSerializer.Deserialize<List<string>>(json, (JsonSerializerOptions?)null)
                ?? new List<string>())
    .HasColumnType("jsonb");""")

    para(d, "Bu qulay, lekin narxi bor va uni aniq bilish kerak:")

    bullets(d, [
        "Ro'yxat ichidagi element bo'yicha samarali qidiruv qilib "
        "bo'lmaydi (GIN indeks qo'ymasam).",
        "`Where(p => p.Tags.Contains(\"vip\"))` SQL ga tarjima "
        "bo'lmaydi.",
        "1NF buziladi — bitta katakda ro'yxat turadi.",
        "Change tracker o'zgarishni sezishi uchun value comparer kerak "
        "bo'ladi.",
    ])

    para(d, "Shuning uchun teg bo'yicha filtr kerak bo'lsa, alohida "
            "jadval to'g'riroq yechim bo'ladi. JSON esa tuzilishi "
            "o'zgaruvchan, faqat o'qish uchun kerak bo'lgan ma'lumotga "
            "mos.")

    h2(d, "EF Core 7+ da yaxshiroq yo'l")

    code(d, """// Primitive kolleksiya — EF o'zi boshqaradi (EF Core 8+)
modelBuilder.Entity<Product>()
    .PrimitiveCollection(p => p.Tags);

// Murakkab obyekt uchun JSON ustun
modelBuilder.Entity<Order>()
    .OwnsOne(o => o.ShippingAddress, b => b.ToJson());""")

    para(d, "`ToJson()` bilan EF ichki obyektga so'rov yozish imkonini "
            "ham beradi — qo'lda converter'dan ustun.")

    # ───────────────────────────────────────────
    h1(d, "6. Converter'ning cheklovlari")

    para(d, "Eng muhim cheklov: **konvertatsiya .NET tomonida "
            "bajariladi**, shuning uchun bazada u ko'rinmaydi.")

    code(d, """// Enum matn sifatida saqlanadi — bu ishlaydi
await db.Orders.Where(o => o.Status == OrderStatus.Paid).ToListAsync(ct);

// Lekin matn ustida amal qilib bo'lmaydi
await db.Orders.Where(o => o.Status.ToString().StartsWith("P")).ToListAsync(ct);
// tarjima qilinmaydi""")

    bullets(d, [
        "Konvertatsiya qilingan ustun bo'yicha **diapazon so'rovi** "
        "noto'g'ri natija berishi mumkin. Masalan sanani matn sifatida "
        "saqlasam, `>` taqqoslash alifbo bo'yicha ishlaydi.",
        "`null` bilan ishlash alohida e'tibor talab qiladi — "
        "converter `null` qiymatni o'tkazmaydi, shuning uchun "
        "nullable turlar uchun alohida sozlash kerak.",
        "Indeks konvertatsiya qilingan **saqlangan** qiymat ustida "
        "bo'ladi, CLR qiymati ustida emas.",
    ])

    # ───────────────────────────────────────────
    h1(d, "7. Tayyor converter'lar")

    code(d, """// EF Core bilan birga keladigan ba'zi converter'lar
.HasConversion<EnumToStringConverter<OrderStatus>>()
.HasConversion<BoolToStringConverter>()          // 'Y' / 'N'
.HasConversion<DateOnlyConverter>()
.HasConversion<NumberToStringConverter<int>>()""")

    para(d, "O'z converter'imni yozishdan oldin tayyor variantini "
            "izlayman — ular sinalgan va `ConvertsToProviderType` kabi "
            "nozik holatlarni to'g'ri qayta ishlaydi.")

    sources(d, [
        ("Value Conversions — EF Core",
         "https://learn.microsoft.com/en-us/ef/core/modeling/value-conversions"),
        ("Pre-defined conversions",
         "https://learn.microsoft.com/en-us/ef/core/modeling/value-conversions#pre-defined-conversions"),
        ("JSON Columns — EF Core",
         "https://learn.microsoft.com/en-us/ef/core/modeling/owned-entities#mapping-owned-types-to-json"),
        ("Bulk configuration — ConfigureConventions",
         "https://learn.microsoft.com/en-us/ef/core/modeling/bulk-configuration"),
    ])
