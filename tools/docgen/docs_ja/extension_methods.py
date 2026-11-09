# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "extension methodlar yaratish"
CATEGORY = ".NET / C#"
TITLE = "Extension Metodlar Yaratish"
SUBTITLE = "Mavjud turga yangi metod qo'shish"
FILENAME = "extension methodlar yaratish.docx"


def build(d):
    h1(d, "1. Muammo va yechim")

    para(d, "Ba'zan mavjud turga yangi metod qo'shgim keladi, lekin uning "
            "kodiga tegish imkonim yo'q — `string`, `DateTime` yoki boshqa "
            "kutubxonaning klassi bo'lsa. Yoki klass `sealed`, ya'ni meros "
            "ham olinmaydi.")

    para(d, "Odatiy yo'l — statik yordamchi klass yozish:")

    code(d, """public static class StringHelper
{
    public static bool IsValidPhone(string value) => /* ... */;
}

// chaqiruv
if (StringHelper.IsValidPhone(input)) { }""")

    para(d, "Ishlaydi, lekin o'qilishi noqulay: shartlar zanjirida "
            "yordamchi klass nomi takrorlanib turadi. Extension metod ayni "
            "shu mantiqni turning o'z metodi kabi chaqirish imkonini beradi:")

    code(d, """if (input.IsValidPhone()) { }""")

    # ───────────────────────────────────────────
    h1(d, "2. Qanday yoziladi")

    para(d, "Uchta shart bajarilishi kerak: klass `static` bo'lishi, metod "
            "`static` bo'lishi va birinchi parametr `this` bilan "
            "belgilanishi.")

    code(d, """public static class StringExtensions
{
    public static bool IsNullOrBlank(this string? value)
        => string.IsNullOrWhiteSpace(value);

    public static string Truncate(this string value, int maxLength)
        => value.Length <= maxLength ? value : value[..maxLength] + "...";

    public static string ToSnakeCase(this string value)
        => string.Concat(value.Select((c, i) =>
               char.IsUpper(c) && i > 0 ? "_" + char.ToLower(c) : char.ToLower(c).ToString()));
}""")

    code(d, """var title = "Buyurtma tafsilotlari sahifasi".Truncate(20);
var column = "CreatedAt".ToSnakeCase();        // created_at""")

    para(d, "Kompilyator uchun bu shunchaki sintaksis qulayligi — "
            "`value.Truncate(20)` chaqiruvi `StringExtensions.Truncate(value, 20)` "
            "ga aylanadi. Shuning uchun hech qanday ish vaqti xarajati yo'q.")

    note(d, "Eslatma",
         "Extension metod ishlashi uchun uning namespace'i `using` bilan "
         "ulangan bo'lishi kerak. IDE metodni ko'rsatmasa, birinchi "
         "tekshiradigan narsam shu.")

    # ───────────────────────────────────────────
    h1(d, "3. Muhim xususiyatlar")

    h2(d, "null ustida ham chaqirilishi mumkin")

    para(d, "Extension metod aslida statik metod, shuning uchun u obyekt "
            "ustida virtual chaqiruv qilmaydi — `null` da ham ishlaydi:")

    code(d, """string? name = null;
bool empty = name.IsNullOrBlank();     // true, exception yo'q""")

    para(d, "Bu foydali, lekin ehtiyot bo'lish kerak: metod ichida "
            "`value.Length` yozsam, `null` da `NullReferenceException` "
            "chiqadi va chaqiruvchi buni kutmaydi. Shuning uchun `null` "
            "qabul qiladigan extension metodda parametrni `string?` deb "
            "belgilab, ichida albatta tekshiraman.")

    h2(d, "Mavjud metodni bosib keta olmaydi")

    para(d, "Agar turda bir xil imzoli metod bo'lsa, har doim **turning o'z "
            "metodi** tanlanadi. Extension metod faqat mos metod topilmaganda "
            "ko'riladi. Shuning uchun mavjud xatti-harakatni extension bilan "
            "o'zgartirib bo'lmaydi.")

    h2(d, "Interfeysga qo'shish mumkin")

    para(d, "Bu eng foydali tomoni: interfeysga extension metod yozilsa, uni "
            "amalga oshirgan hamma tur shu metodga ega bo'ladi. LINQ butunlay "
            "shu printsipga qurilgan — `Where`, `Select`, `OrderBy` hammasi "
            "`IEnumerable<T>` ga yozilgan extension metodlar.")

    code(d, """public static class EnumerableExtensions
{
    public static IEnumerable<IReadOnlyList<T>> Chunked<T>(
        this IEnumerable<T> source, int size)
    {
        var buffer = new List<T>(size);
        foreach (var item in source)
        {
            buffer.Add(item);
            if (buffer.Count < size) continue;
            yield return buffer.ToArray();
            buffer.Clear();
        }
        if (buffer.Count > 0) yield return buffer.ToArray();
    }
}""")

    # ───────────────────────────────────────────
    h1(d, "4. ASP.NET Core da eng ko'p uchraydigan ishlatilishi")

    para(d, "`Program.cs` tez o'sib ketadi. Servis ro'yxatga olishni mavzu "
            "bo'yicha extension metodlarga ajratish uni o'qiladigan "
            "holatda ushlab turadi:")

    code(d, """public static class ServiceCollectionExtensions
{
    public static IServiceCollection AddPersistence(
        this IServiceCollection services, IConfiguration configuration)
    {
        services.AddDbContext<AppDbContext>(o =>
            o.UseNpgsql(configuration.GetConnectionString("Default")));

        services.AddScoped<IOrderRepository, OrderRepository>();
        return services;
    }
}""")

    code(d, """builder.Services
    .AddPersistence(builder.Configuration)
    .AddApplicationServices()
    .AddApiVersioningSetup();""")

    para(d, "`IServiceCollection` ni qaytarish zanjirli chaqiruvni "
            "(fluent API) imkonli qiladi. Bu .NET bo'ylab qabul qilingan "
            "konvensiya, shuning uchun unga amal qilaman.")

    para(d, "Middleware uchun ham shu naqsh ishlatiladi:")

    code(d, """public static class ApplicationBuilderExtensions
{
    public static IApplicationBuilder UseRequestLogging(this IApplicationBuilder app)
        => app.UseMiddleware<RequestLoggingMiddleware>();
}""")

    # ───────────────────────────────────────────
    h1(d, "5. Qachon ishlatmayman")

    para(d, "Extension metod qulay, lekin har joyda emas. O'zim uchun "
            "qo'ygan chegaralar:")

    bullets(d, [
        "**Domen mantiqini extension'ga chiqarmaslik.** Agar metod "
        "`Order` ning ichki qoidasini ifodalasa, u `Order` klassining o'z "
        "metodi bo'lishi kerak. Extension'ga chiqarish inkapsulyatsiyani "
        "buzadi, chunki u faqat ochiq a'zolarga kira oladi.",
        "**Obyekt holatini o'zgartiradigan extension yozmaslik.** "
        "`order.Cancel()` extension bo'lsa, o'quvchi bu turning o'z metodi "
        "deb o'ylaydi va mantiq qayerda ekanini topa olmaydi.",
        "**`object` ga extension yozmaslik.** U hamma turda ko'rinadi va "
        "IntelliSense ni ifloslantiradi.",
        "**Juda umumiy nom bermaslik.** Ikki kutubxonada bir xil nomli "
        "extension bo'lsa, chaqiruv noaniq bo'lib kompilyatsiya xatosi "
        "chiqadi.",
    ])

    note(d, "Mening qoidam",
         "Extension metod — **o'zgartirmaydigan, yordamchi** amallar uchun. "
         "Formatlash, tekshirish, aylantirish, sozlashni guruhlash. "
         "Biznes qarori qabul qiladigan kod turning ichida qoladi.")

    sources(d, [
        ("Extension methods — C# programming guide",
         "https://learn.microsoft.com/en-us/dotnet/csharp/programming-guide/classes-and-structs/extension-methods"),
        ("Extension methods best practices",
         "https://learn.microsoft.com/en-us/dotnet/csharp/advanced-topics/interface-implementation/"),
    ])
