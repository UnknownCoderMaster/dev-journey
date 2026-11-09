# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "Model bulk configuration"
CATEGORY = "EF Core"
TITLE = "Model Bo'yicha Ommaviy Konfiguratsiya"
SUBTITLE = "Bir xil qoidani butun modelga bir marta qo'llash"
FILENAME = "Model bulk configuration.docx"


def build(d):
    h1(d, "1. Muammo")

    para(d, "Modelda o'nlab entity bo'lganda ba'zi qoidalar hamma joyda takrorlanadi: "
            "barcha `decimal` ustunlar bir xil aniqlikda bo'lsin, barcha matn maydonlari "
            "uzunligi cheklansin, barcha sana ustunlari UTC da saqlansin, jadval va "
            "ustun nomlari snake_case da yozilsin.")

    para(d, "Bu qoidalarni har bir entity konfiguratsiyasida qo'lda yozish ikki xavf "
            "tug'diradi: kod takrorlanadi va yangi entity qo'shilganda qoida esdan "
            "chiqib qoladi. EF Core bunday holatlar uchun ommaviy konfiguratsiya "
            "mexanizmlarini beradi.")

    note(d, "Men buni shunday his qildim:",
         "Loyihada o'ntacha entity bo'lgan paytda har biriga `HasPrecision(18, 2)` "
         "yozish zerikarli, lekin chidasa bo'ladigan ish edi. Yigirmanchi entity dan "
         "keyin esa bittasida uni yozishni unutganimni payqadim va bazada pul miqdori "
         "noto'g'ri yaxlitlangan edi. Shundan keyin bu mavzuni jiddiy o'rgandim.")

    # ───────────────────────────────────────────
    h1(d, "2. Uch xil yondashuv")

    table(d, ["Usul", "Qachon ishga tushadi"],
          [["`ConfigureConventions`", "Model qurilishidan oldin, tip darajasida"],
           ["Metadata API bo'ylab aylanish", "Model qurilgandan keyin, `OnModelCreating` oxirida"],
           ["Maxsus konventsiya", "Model qurilishi davomida, har bir element uchun"]],
          widths=[5.0, 10.5])

    para(d, "Birinchi ikkitasi amalda yetarli bo'ladi; uchinchisi murakkab holatlar uchun.")

    # ───────────────────────────────────────────
    h1(d, "3. ConfigureConventions")

    para(d, "EF Core 6 dan boshlab `DbContext` da `ConfigureConventions` metodi mavjud. "
            "U model qurilishidan oldin chaqiriladi va tip bo'yicha sukutdagi "
            "sozlamalarni belgilash imkonini beradi.")

    code(d, """protected override void ConfigureConventions(
    ModelConfigurationBuilder configurationBuilder)
{
    // Barcha decimal ustunlar
    configurationBuilder.Properties<decimal>()
        .HavePrecision(18, 2);

    // Barcha matn ustunlari
    configurationBuilder.Properties<string>()
        .HaveMaxLength(256)
        .UseCollation("und-x-icu");

    // Barcha enum lar matn sifatida saqlansin
    configurationBuilder.Properties<Enum>()
        .HaveConversion<string>();
}""")

    para(d, "Bu sozlamalar sukutdagi qiymat bo'lib xizmat qiladi — konkret entity "
            "konfiguratsiyasida yozilgan qoida ularni bekor qiladi:")

    code(d, """// Umumiy qoida 256, lekin bu maydon uzunroq bo'lishi kerak
builder.Property(a => a.Content).HasMaxLength(8000);""")

    h2(d, "3.1 Maxsus tip uchun")

    para(d, "O'z qiymat obyektlarim uchun ham konverterni bir marta e'lon qilishim mumkin:")

    code(d, """configurationBuilder
    .Properties<Money>()
    .HaveConversion<MoneyConverter>();

configurationBuilder
    .DefaultTypeMapping<DateOnly>()
    .HasColumnType("date");""")

    note(d, "Bu meni ancha vaqt tejaydi:",
         "Avval har bir `Money` tipidagi xossaga alohida konverter yozardim. Endi "
         "bitta satr yozaman va u butun model bo'ylab ishlaydi. Yangi entity "
         "qo'shilganda ham hech narsa qilish kerak emas — qoida avtomatik qo'llanadi.")

    # ───────────────────────────────────────────
    h1(d, "4. Metadata bo'ylab aylanish")

    para(d, "Ba'zi qoidalarni faqat model to'liq qurilgandan keyin qo'llash mumkin — "
            "masalan jadval va ustun nomlarini qayta nomlash. Buning uchun "
            "`OnModelCreating` oxirida model elementlari bo'ylab aylaniladi.")

    h2(d, "4.1 snake_case nomlash")

    code(d, """protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    modelBuilder.ApplyConfigurationsFromAssembly(typeof(AppDbContext).Assembly);

    foreach (var entity in modelBuilder.Model.GetEntityTypes())
    {
        entity.SetTableName(ToSnakeCase(entity.GetTableName()!));

        foreach (var property in entity.GetProperties())
            property.SetColumnName(ToSnakeCase(property.GetColumnName()));

        foreach (var key in entity.GetKeys())
            key.SetName(ToSnakeCase(key.GetName()!));

        foreach (var index in entity.GetIndexes())
            index.SetDatabaseName(ToSnakeCase(index.GetDatabaseName()!));
    }
}

private static string ToSnakeCase(string name) =>
    Regex.Replace(name, "([a-z0-9])([A-Z])", "$1_$2").ToLowerInvariant();""")

    para(d, "Bu kod aylanishi `ApplyConfigurationsFromAssembly` dan **keyin** turishi "
            "muhim — aks holda konkret konfiguratsiyalarda berilgan nomlar qayta yozilib "
            "ketmaydi.")

    h2(d, "4.2 Barcha soft-delete entity larga filtr")

    code(d, """foreach (var entity in modelBuilder.Model.GetEntityTypes())
{
    if (!typeof(ISoftDeletable).IsAssignableFrom(entity.ClrType))
        continue;

    var parameter = Expression.Parameter(entity.ClrType, "e");
    var body = Expression.Not(
        Expression.Property(parameter, nameof(ISoftDeletable.IsDeleted)));

    modelBuilder.Entity(entity.ClrType)
        .HasQueryFilter(Expression.Lambda(body, parameter));
}""")

    para(d, "Bu yerda ifoda daraxti qo'lda quriladi, chunki tip ish vaqtida ma'lum "
            "bo'ladi va umumiy `HasQueryFilter<T>` ni chaqirib bo'lmaydi.")

    h2(d, "4.3 Barcha o'chirish xatti-harakatini Restrict qilish")

    code(d, """foreach (var fk in modelBuilder.Model.GetEntityTypes()
                          .SelectMany(e => e.GetForeignKeys()))
{
    fk.DeleteBehavior = DeleteBehavior.Restrict;
}""")

    note(d, "Bu juda foydali qoida:",
         "EF Core majburiy bog'lanishlarda sukut bo'yicha `Cascade` qo'yadi — ya'ni ota "
         "yozuv o'chsa, bolalari ham jimgina o'chadi. Men buni deyarli hech qachon "
         "xohlamayman. Yuqoridagi bir nechta satr butun model bo'ylab bu xavfni "
         "yo'qotadi, kerak joyda esa `Cascade` ni aniq yozib qo'yaman.")

    # ───────────────────────────────────────────
    h1(d, "5. Maxsus konventsiya")

    para(d, "EF Core 7 dan boshlab o'z konventsiyangizni yozib, uni model qurilish "
            "jarayoniga ulash mumkin. Bu usul avvalgilardan farqli ravishda model "
            "o'zgarganda ham qayta ishlaydi.")

    code(d, """public class MaxStringLengthConvention : IModelFinalizingConvention
{
    public void ProcessModelFinalizing(
        IConventionModelBuilder modelBuilder,
        IConventionContext<IConventionModelBuilder> context)
    {
        foreach (var property in modelBuilder.Metadata.GetEntityTypes()
                     .SelectMany(e => e.GetDeclaredProperties())
                     .Where(p => p.ClrType == typeof(string)))
        {
            property.Builder.HasMaxLength(512);
        }
    }
}""")

    code(d, """protected override void ConfigureConventions(
    ModelConfigurationBuilder configurationBuilder)
{
    configurationBuilder.Conventions.Add(_ => new MaxStringLengthConvention());
}""")

    para(d, "Shuningdek keraksiz konventsiyalarni o'chirish ham mumkin:")

    code(d, """configurationBuilder.Conventions.Remove(
    typeof(ForeignKeyIndexConvention));""")

    para(d, "Yuqoridagi misol har bir tashqi kalit uchun avtomatik indeks yaratishni "
            "o'chiradi — ba'zan bu indekslar keraksiz bo'ladi va yozish tezligini "
            "pasaytiradi.")

    # ───────────────────────────────────────────
    h1(d, "6. Qaysi usulni qachon tanlayman")

    bullets(d, [
        "**Tip bo'yicha oddiy qoida** (aniqlik, uzunlik, konverter) — "
        "`ConfigureConventions`.",
        "**Nomlash, bog'lanishlar, filtrlar** — `OnModelCreating` oxiridagi aylanish.",
        "**Murakkab yoki qayta ishlashi kerak bo'lgan qoida** — maxsus konventsiya.",
    ])

    note(d, "Bitta ogohlantirish:",
         "Ommaviy qoidalar kuchli, lekin ular ko'rinmas bo'ladi. Entity "
         "konfiguratsiyasiga qarab turib, nega ustun `varchar(256)` bo'lganini "
         "tushunib bo'lmaydi — javob butunlay boshqa faylda. Shuning uchun men bunday "
         "qoidalarni bitta joyda to'playman va ular ko'p bo'lsa, qisqacha izoh yozib "
         "qo'yaman.")

    # ───────────────────────────────────────────
    h1(d, "7. Natijani tekshirish")

    code(d, """Console.WriteLine(context.Model.ToDebugString());""")

    para(d, "Yoki migration yaratib, generatsiya qilingan sxemaga qarash — ommaviy "
            "qoidalar haqiqatan qo'llanganini ko'rishning eng ishonchli usuli.")

    # ───────────────────────────────────────────
    h1(d, "8. Xulosa")

    bullets(d, [
        "`ConfigureConventions` tip bo'yicha sukutdagi sozlamalarni belgilaydi "
        "(EF Core 6+).",
        "Konkret entity konfiguratsiyasi umumiy qoidadan ustun turadi.",
        "`OnModelCreating` oxirida metadata bo'ylab aylanish nomlash va bog'lanish "
        "qoidalarini ommaviy qo'llash uchun ishlatiladi.",
        "Sukutdagi `Cascade` ni butun model bo'ylab `Restrict` ga o'zgartirish — "
        "bir necha satrlik, lekin juda foydali qoida.",
        "EF Core 7 dan maxsus konventsiya yozish va mavjudlarini o'chirish mumkin.",
        "Ommaviy qoidalar ko'rinmas bo'lgani uchun ularni bitta joyda to'plash kerak.",
    ])

    sources(d, [
        ("Bulk configuration — EF Core",
         "https://learn.microsoft.com/en-us/ef/core/modeling/bulk-configuration"),
        ("Model building conventions — EF Core",
         "https://learn.microsoft.com/en-us/ef/core/modeling/bulk-configuration#conventions"),
        ("What's New in EF Core 6.0 — Pre-convention model configuration",
         "https://learn.microsoft.com/en-us/ef/core/what-is-new/ef-core-6.0/whatsnew#pre-convention-model-configuration"),
    ])
