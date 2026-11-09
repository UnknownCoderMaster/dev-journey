# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "Mapping"
CATEGORY = "EF Core"
TITLE = "EF Core da Mapping"
SUBTITLE = "C# klasslarini ma'lumotlar bazasi sxemasiga bog'lash"
FILENAME = "Mapping.docx"


def build(d):
    h1(d, "1. Mapping nima")

    para(d, "Mapping — bu C# dagi klass, xossa va bog'lanishlarni ma'lumotlar bazasidagi "
            "jadval, ustun va kalitlarga moslashtirish jarayoni. EF Core so'rov yuborishdan "
            "oldin shu moslikni biladigan ichki model quradi va keyin barcha operatsiyalarni "
            "shu model asosida bajaradi.")

    para(d, "Model bir marta, ilova ishga tushganda quriladi va keshlanadi. Shuning uchun "
            "mapping sozlamalari ish vaqtida o'zgartirilmaydi — ular dastur yozilayotganda "
            "aniq belgilanishi kerak.")

    note(d, "Men buni shunday tushundim:",
         "Mapping aslida tarjimon vazifasini bajaradi. Men C# tilida \"Foydalanuvchining "
         "elektron pochtasi\" deb yozaman, baza esa \"users jadvalidagi email ustuni, "
         "varchar(256), bo'sh bo'lmasin\" deb tushunadi. Bu tarjimani kim qilishini "
         "men hal qilaman — yo EF Core o'zi taxmin qiladi, yoki men aniq aytaman.")

    # ───────────────────────────────────────────
    h1(d, "2. Mapping ni belgilashning uch yo'li")

    para(d, "EF Core modelni uch manbadan yig'adi va ular quyidagi tartibda bir-birining "
            "ustiga qo'yiladi:")

    bullets(d, [
        "**Konventsiya** — EF Core nom va tiplarga qarab o'zi taxmin qiladi.",
        "**Data Annotations** — entity klassi ustiga qo'yilgan atributlar.",
        "**Fluent API** — `OnModelCreating` ichidagi aniq sozlamalar.",
    ], numbered=True)

    para(d, "Agar bitta xossa haqida uchala manbada ham ko'rsatma bo'lsa, oxirgisi "
            "— Fluent API — ustun keladi. Shuning uchun murakkab yoki noaniq "
            "holatlarda Fluent API dan foydalanish ishonchliroq.")

    h2(d, "2.1 Konventsiya")

    para(d, "Hech qanday sozlama yozilmasa ham EF Core quyidagilarni o'zi aniqlaydi:")

    bullets(d, [
        "`DbSet<T>` xossasining nomi jadval nomiga aylanadi.",
        "`Id` yoki `<KlassNomi>Id` nomli xossa birlamchi kalit deb olinadi.",
        "`int` tipidagi birlamchi kalit avtomatik o'suvchi qilib sozlanadi.",
        "Nullable bo'lmagan tip `NOT NULL` ustunga aylanadi.",
        "Boshqa entity ga ishora qiluvchi navigatsiya xossasi tashqi kalit hosil qiladi.",
    ])

    code(d, """public class Book
{
    public int Id { get; set; }          // birlamchi kalit, identity
    public string Title { get; set; }    // NOT NULL
    public string? Notes { get; set; }   // NULL
    public int AuthorId { get; set; }    // tashqi kalit
    public Author Author { get; set; }
}""")

    para(d, "Bu kod uchun qo'shimcha sozlama yozmasam ham, EF Core to'g'ri jadval yarata "
            "oladi. Konventsiya oddiy modellar uchun yetarli bo'ladi.")

    h2(d, "2.2 Data Annotations")

    code(d, """[Table("books")]
public class Book
{
    [Key]
    public int Id { get; set; }

    [Required]
    [MaxLength(300)]
    [Column("title")]
    public string Title { get; set; }

    [Precision(18, 2)]
    public decimal Price { get; set; }

    [NotMapped]
    public string DisplayName => $"{Title} ({Price})";
}""")

    para(d, "Atributlar kodni o'qiyotgan odamga darhol ko'rinadi — bu ularning asosiy "
            "afzalligi. Kamchiligi esa shundaki, domen klassi `System.ComponentModel` "
            "va EF Core ga bog'lanib qoladi.")

    h2(d, "2.3 Fluent API")

    code(d, """protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    modelBuilder.Entity<Book>(entity =>
    {
        entity.ToTable("books");
        entity.HasKey(b => b.Id);

        entity.Property(b => b.Title)
              .HasColumnName("title")
              .HasMaxLength(300)
              .IsRequired();

        entity.Property(b => b.Price)
              .HasPrecision(18, 2);

        entity.Ignore(b => b.DisplayName);

        entity.HasIndex(b => b.Title);
    });
}""")

    para(d, "Fluent API barcha imkoniyatlarni qamrab oladi — atributlar bilan ifodalab "
            "bo'lmaydigan sozlamalar ham faqat shu yerda mavjud.")

    note(d, "Amalda qaysi birini tanlayman:",
         "Men domen klasslarini toza saqlashni afzal ko'raman, shuning uchun asosan "
         "Fluent API ishlataman. Lekin hammasini bitta `OnModelCreating` ichiga yozsam, "
         "u tez orada yuzlab satrga aylanadi. Shuning uchun har bir entity uchun alohida "
         "konfiguratsiya klassi yarataman — pastda shu haqida.")

    # ───────────────────────────────────────────
    h1(d, "3. Konfiguratsiyani ajratish")

    para(d, "`IEntityTypeConfiguration<T>` interfeysi har bir entity sozlamasini alohida "
            "faylga chiqarish imkonini beradi.")

    code(d, """public class BookConfiguration : IEntityTypeConfiguration<Book>
{
    public void Configure(EntityTypeBuilder<Book> builder)
    {
        builder.ToTable("books");

        builder.Property(b => b.Title)
               .HasMaxLength(300)
               .IsRequired();

        builder.HasOne(b => b.Author)
               .WithMany(a => a.Books)
               .HasForeignKey(b => b.AuthorId)
               .OnDelete(DeleteBehavior.Restrict);
    }
}""")

    code(d, """protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    modelBuilder.ApplyConfigurationsFromAssembly(
        typeof(AppDbContext).Assembly);
}""", caption="Barcha konfiguratsiyalarni bir yo'la ulash")

    para(d, "Bu usulda yangi entity qo'shilganda `OnModelCreating` ga tegish shart emas — "
            "yangi konfiguratsiya klassi avtomatik topiladi.")

    # ───────────────────────────────────────────
    h1(d, "4. Bog'lanishlarni mapping qilish")

    h2(d, "4.1 Bir-ga-ko'p")

    code(d, """builder.HasOne(b => b.Author)
       .WithMany(a => a.Books)
       .HasForeignKey(b => b.AuthorId);""")

    h2(d, "4.2 Bir-ga-bir")

    code(d, """builder.HasOne(u => u.Profile)
       .WithOne(p => p.User)
       .HasForeignKey<UserProfile>(p => p.UserId);""")

    para(d, "Bir-ga-bir bog'lanishda tashqi kalit qaysi tomonda turishini EF Core o'zi "
            "aniqlay olmaydi, shuning uchun `HasForeignKey<T>` da tipni aniq ko'rsatish shart.")

    h2(d, "4.3 Ko'p-ga-ko'p")

    code(d, """builder.HasMany(b => b.Tags)
       .WithMany(t => t.Books)
       .UsingEntity<BookTag>(
           j => j.HasOne(bt => bt.Tag).WithMany().HasForeignKey(bt => bt.TagId),
           j => j.HasOne(bt => bt.Book).WithMany().HasForeignKey(bt => bt.BookId),
           j => j.ToTable("book_tags"));""")

    para(d, "EF Core 5 dan boshlab oraliq jadvalni alohida entity sifatida yozish shart "
            "emas — EF Core uni o'zi yaratadi. `UsingEntity` esa oraliq jadvalga qo'shimcha "
            "ustun (masalan qo'shilgan sana) kerak bo'lganda ishlatiladi.")

    h2(d, "4.4 O'chirish xatti-harakati")

    table(d, ["Qiymat", "Ota yozuv o'chirilganda"],
          [["`Cascade`", "Bog'liq yozuvlar ham o'chiriladi"],
           ["`Restrict`", "Bog'liq yozuv bo'lsa, o'chirishga ruxsat berilmaydi"],
           ["`SetNull`", "Tashqi kalit `NULL` qilinadi (ustun nullable bo'lishi shart)"],
           ["`NoAction`", "EF Core aralashmaydi, qaror bazaning o'ziga qoladi"]],
          widths=[4.0, 11.5])

    note(d, "Bu yerda ehtiyot bo'lish kerak:",
         "Majburiy bog'lanishda EF Core sukut bo'yicha `Cascade` ni tanlaydi. Ya'ni men "
         "bitta mijozni o'chirsam, uning barcha buyurtmalari ham jimgina o'chib ketadi. "
         "Ko'p holatda men buni xohlamayman — buyurtmalar tarix sifatida qolishi kerak. "
         "Shuning uchun muhim jadvallarda `Restrict` ni aniq yozib qo'yaman.")

    # ───────────────────────────────────────────
    h1(d, "5. Maxsus mapping holatlari")

    h2(d, "5.1 Owned types")

    para(d, "Ba'zi tushunchalarning o'z kaliti bo'lmaydi — ular doimo egasi bilan birga "
            "yashaydi. Manzil shunga misol:")

    code(d, """public class Address          // o'z Id si yo'q
{
    public string City { get; set; }
    public string Street { get; set; }
}

builder.OwnsOne(c => c.Address, a =>
{
    a.Property(x => x.City).HasColumnName("city");
    a.Property(x => x.Street).HasColumnName("street");
});""")

    para(d, "Natijada alohida jadval yaratilmaydi — `city` va `street` ustunlari egasining "
            "jadvaliga qo'shiladi.")

    h2(d, "5.2 Value converter")

    para(d, "Agar C# dagi tip bazada boshqacha saqlanishi kerak bo'lsa, konverter yoziladi:")

    code(d, """builder.Property(o => o.Status)
       .HasConversion<string>();        // enum → matn

builder.Property(b => b.Tags)
       .HasConversion(
           v => string.Join(',', v),
           v => v.Split(',', StringSplitOptions.RemoveEmptyEntries).ToList());""")

    note(d, "Konverterning yashirin narxi bor:",
         "Konverter qo'yilgan ustun bo'yicha `Where` yozsam, shart bazada emas, ilova "
         "tomonida hisoblanishi mumkin — ya'ni butun jadval o'qib olinadi. Enum ni matnga "
         "aylantirish xavfsiz, lekin ro'yxatni vergul bilan birlashtirish kabi narsalarda "
         "men so'rov qanday SQL hosil qilganini albatta tekshiraman.")

    h2(d, "5.3 Shadow property")

    para(d, "C# klassida yo'q, lekin bazada mavjud bo'lgan ustun shadow property deb "
            "ataladi:")

    code(d, """builder.Property<DateTime>("UpdatedAt");

// Qiymat berish va o'qish:
context.Entry(book).Property("UpdatedAt").CurrentValue = DateTime.UtcNow;""")

    h2(d, "5.4 Global query filter")

    code(d, """builder.HasQueryFilter(b => !b.IsDeleted);""")

    para(d, "Bu filtr shu entity ga yozilgan har bir so'rovga avtomatik qo'shiladi. "
            "Yumshoq o'chirish (soft delete) uchun qulay. Kerak bo'lganda "
            "`IgnoreQueryFilters()` bilan chetlab o'tiladi.")

    # ───────────────────────────────────────────
    h1(d, "6. Mapping to'g'ri ishlaganini tekshirish")

    para(d, "Sozlamalar kutilganidek qo'llanganini ko'rish uchun yakuniy modelni chop "
            "etish mumkin:")

    code(d, """var model = context.Model;
Console.WriteLine(model.ToDebugString());""")

    para(d, "Yoki migration yaratib, generatsiya qilingan `Up()` metodiga qarash — u "
            "mapping natijasini SQL ko'rinishida ko'rsatadi:")

    code(d, """dotnet ef migrations add Test --no-build
dotnet ef migrations script""")

    note(d, "Mening odatim:",
         "Yangi mapping yozganimda darhol migration yaratib, uni o'qib chiqaman va keyin "
         "`migrations remove` bilan o'chirib tashlayman. Bu menga bazaga tegmasdan "
         "sozlamalarim nimaga olib kelishini ko'rsatadi. Bir necha marta shu yo'l bilan "
         "noto'g'ri yozilgan `MaxLength` va tasodifan `Cascade` bo'lib qolgan "
         "bog'lanishlarni topganman.")

    # ───────────────────────────────────────────
    h1(d, "7. Xulosa")

    bullets(d, [
        "Mapping uch manbadan yig'iladi: konventsiya → atributlar → Fluent API; "
        "oxirgisi ustun keladi.",
        "Domen klasslarini toza saqlash uchun Fluent API ni `IEntityTypeConfiguration<T>` "
        "klasslariga ajratib yozish qulay.",
        "Majburiy bog'lanishlarda sukutdagi `Cascade` ni ongli ravishda tekshirish kerak.",
        "`OwnsOne` kalitsiz tushunchalarni egasining jadvaliga joylaydi.",
        "Value converter so'rovni ilova tomonida hisoblanishga majburlashi mumkin — "
        "generatsiya qilingan SQL ni tekshirish shart.",
        "Migration yaratib o'qib chiqish — mapping ni tekshirishning eng tez usuli.",
    ])

    sources(d, [
        ("Creating and Configuring a Model — EF Core",
         "https://learn.microsoft.com/en-us/ef/core/modeling/"),
        ("Entity Types — EF Core",
         "https://learn.microsoft.com/en-us/ef/core/modeling/entity-types"),
        ("Relationships — EF Core",
         "https://learn.microsoft.com/en-us/ef/core/modeling/relationships"),
        ("Value Conversions — EF Core",
         "https://learn.microsoft.com/en-us/ef/core/modeling/value-conversions"),
        ("Owned Entity Types — EF Core",
         "https://learn.microsoft.com/en-us/ef/core/modeling/owned-entities"),
    ])
