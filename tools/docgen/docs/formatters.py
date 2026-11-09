# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "Configure formatters, XML format, System.Text.Json-based formatters"
CATEGORY = "ASP.NET"
TITLE = "Formatterlarni Sozlash"
SUBTITLE = "JSON va XML serializatsiyasi, content negotiation"
FILENAME = "Configure formatters, XML format, System.Text.Json-based formatters.docx"


def build(d):
    h1(d, "1. Formatter nima qiladi")

    para(d, "Kontroller metodi C# obyektini qaytaradi, lekin tarmoq orqali faqat baytlar "
            "uzatiladi. Obyektni baytlarga aylantirish va teskari aylantirish vazifasini "
            "formatter bajaradi.")

    para(d, "Ikki tur mavjud: output formatter javobni hosil qiladi, input formatter esa "
            "so'rov tanasini obyektga aylantiradi. ASP.NET Core da sukut bo'yicha faqat "
            "JSON uchun formatterlar yoqilgan.")

    h2(d, "1.1 Content negotiation")

    para(d, "Mijoz `Accept` sarlavhasi orqali qanday formatda javob kutayotganini "
            "bildiradi. Server mavjud formatterlar orasidan mosini tanlaydi:")

    code(d, """GET /api/books/1
Accept: application/xml""")

    para(d, "Agar mos formatter topilmasa, server `406 Not Acceptable` qaytaradi — "
            "lekin faqat bu xatti-harakat ataylab yoqilgan bo'lsa. Sukut bo'yicha "
            "server o'zida bor formatni qaytaraveradi.")

    code(d, """builder.Services.AddControllers(options =>
{
    options.ReturnHttpNotAcceptable = true;
});""")

    # ───────────────────────────────────────────
    h1(d, "2. System.Text.Json")

    para(d, "ASP.NET Core 3.0 dan boshlab sukutdagi JSON kutubxonasi `System.Text.Json` "
            "hisoblanadi. U `Newtonsoft.Json` ga qaraganda tezroq va kamroq xotira "
            "ishlatadi, lekin ataylab qattiqroq qoidalarga amal qiladi.")

    h2(d, "2.1 Sozlash")

    code(d, """builder.Services.AddControllers()
    .AddJsonOptions(options =>
    {
        var json = options.JsonSerializerOptions;

        json.PropertyNamingPolicy = JsonNamingPolicy.CamelCase;
        json.DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull;
        json.Converters.Add(new JsonStringEnumConverter());
        json.WriteIndented = false;
        json.NumberHandling = JsonNumberHandling.AllowReadingFromString;
    });""")

    table(d, ["Sozlama", "Ta'siri"],
          [["`PropertyNamingPolicy`", "Xossa nomlari camelCase ga aylantiriladi"],
           ["`DefaultIgnoreCondition`", "`null` maydonlar javobdan chiqarib tashlanadi"],
           ["`JsonStringEnumConverter`", "Enum raqam emas, nom sifatida yoziladi"],
           ["`WriteIndented`", "Javob chiroyli formatlanadi (hajmni oshiradi)"],
           ["`NumberHandling`", "`\"42\"` kabi matnli raqamlarni qabul qiladi"]],
          widths=[5.2, 10.3])

    note(d, "Enum ni matn qilish — men deyarli har doim yoqadigan sozlama:",
         "Raqamli enum javobni o'qib bo'lmaydigan qiladi: `\"status\": 2` nima degani? "
         "Matn sifatida esa `\"status\": \"Shipped\"` — hech qanday izoh kerak emas. "
         "Bundan tashqari enum ga yangi qiymat qo'shilganda raqamlar siljib ketmaydi.")

    h2(d, "2.2 Atributlar bilan nozik sozlash")

    code(d, """public class BookDto
{
    [JsonPropertyName("book_title")]
    public string Title { get; set; }

    [JsonIgnore]
    public string InternalCode { get; set; }

    [JsonPropertyOrder(1)]
    public int Id { get; set; }

    [JsonConverter(typeof(DateOnlyConverter))]
    public DateOnly PublishedOn { get; set; }
}""")

    h2(d, "2.3 O'z konverterim")

    code(d, """public class DateOnlyConverter : JsonConverter<DateOnly>
{
    private const string Format = "yyyy-MM-dd";

    public override DateOnly Read(
        ref Utf8JsonReader reader, Type type, JsonSerializerOptions options)
        => DateOnly.ParseExact(reader.GetString()!, Format);

    public override void Write(
        Utf8JsonWriter writer, DateOnly value, JsonSerializerOptions options)
        => writer.WriteStringValue(value.ToString(Format));
}""")

    h2(d, "2.4 Aylanma havolalar")

    para(d, "Agar ikki obyekt bir-biriga ishora qilsa, serializatsiya cheksiz davom "
            "etadi. `System.Text.Json` bu holatda xatolik beradi:")

    code(d, """json.ReferenceHandler = ReferenceHandler.IgnoreCycles;""")

    note(d, "Lekin asl yechim boshqa:",
         "`IgnoreCycles` — bu bintlash, davolash emas. Aylanma havola paydo bo'lgani "
         "entity ni to'g'ridan-to'g'ri javobga qaytarayotganimni bildiradi. To'g'ri "
         "yechim — DTO ishlatish. Shunda nafaqat sikl muammosi yo'qoladi, balki "
         "ichki maydonlar ham tasodifan tashqariga chiqib ketmaydi.")

    # ───────────────────────────────────────────
    h1(d, "3. Newtonsoft.Json ga qaytish")

    para(d, "Ba'zi imkoniyatlar — masalan `JsonPatchDocument` — hali ham "
            "`Newtonsoft.Json` ni talab qiladi:")

    code(d, """dotnet add package Microsoft.AspNetCore.Mvc.NewtonsoftJson""")

    code(d, """builder.Services.AddControllers()
    .AddNewtonsoftJson(options =>
    {
        options.SerializerSettings.ContractResolver =
            new CamelCasePropertyNamesContractResolver();
        options.SerializerSettings.ReferenceLoopHandling =
            ReferenceLoopHandling.Ignore;
    });""")

    para(d, "Bu chaqiruv `System.Text.Json` formatterlarini butunlay almashtiradi — "
            "ikkalasi bir vaqtda ishlamaydi.")

    table(d, ["Jihat", "System.Text.Json", "Newtonsoft.Json"],
          [["Tezlik", "Yuqori", "Pastroq"],
           ["Xotira", "Kam", "Ko'proq"],
           ["Qoidalar", "Qattiq", "Yumshoq"],
           ["`JsonPatchDocument`", "Qo'llab-quvvatlamaydi", "Qo'llab-quvvatlaydi"],
           ["Imkoniyatlar kengligi", "Cheklangan", "Keng"]],
          widths=[4.0, 5.7, 5.8])

    # ───────────────────────────────────────────
    h1(d, "4. XML formatteri")

    para(d, "XML sukut bo'yicha o'chirilgan. Uni yoqish uchun alohida chaqiruv kerak:")

    code(d, """builder.Services.AddControllers()
    .AddXmlSerializerFormatters();""")

    para(d, "Muqobil variant — `DataContractSerializer` ga asoslangan formatter:")

    code(d, """builder.Services.AddControllers()
    .AddXmlDataContractSerializerFormatters();""")

    table(d, ["Serializer", "Xususiyati"],
          [["`XmlSerializer`", "Oddiy, faqat ochiq xossalarni yozadi, parametrsiz "
                               "konstruktor talab qiladi"],
           ["`DataContractSerializer`", "Yopiq a'zolarni ham yoza oladi, obyekt "
                                        "havolalarini qo'llab-quvvatlaydi"]],
          widths=[5.2, 10.3])

    h2(d, "4.1 XML ni sozlash")

    code(d, """[XmlRoot("book")]
public class BookDto
{
    [XmlAttribute("id")]
    public int Id { get; set; }

    [XmlElement("title")]
    public string Title { get; set; }

    [XmlIgnore]
    public string InternalCode { get; set; }
}""")

    h2(d, "4.2 Ma'lum bir formatni majburlash")

    code(d, """[HttpGet("{id}")]
[Produces("application/xml")]
public async Task<BookDto> GetXml(int id) => ...;

// Yoki bir nechta variant
[Produces("application/json", "application/xml")]
public async Task<BookDto> Get(int id) => ...;""")

    note(d, "XML hali ham kerak bo'lib qoladi:",
         "Yangi loyihalarda XML deyarli ishlatilmaydi, lekin davlat tizimlari, bank "
         "integratsiyalari va eski korporativ xizmatlar ko'pincha aynan XML kutadi. "
         "Shuning uchun uni butunlay o'tmish deb hisoblamayman — kerak bo'lganda "
         "bir satr bilan yoqib qo'yiladi.")

    # ───────────────────────────────────────────
    h1(d, "5. O'z formatterim")

    para(d, "Standart bo'lmagan format, masalan CSV, uchun o'z formatterimni yozishim "
            "mumkin:")

    code(d, """public class CsvOutputFormatter : TextOutputFormatter
{
    public CsvOutputFormatter()
    {
        SupportedMediaTypes.Add(
            MediaTypeHeaderValue.Parse("text/csv"));
        SupportedEncodings.Add(Encoding.UTF8);
    }

    protected override bool CanWriteType(Type? type)
        => typeof(IEnumerable<BookDto>).IsAssignableFrom(type);

    public override async Task WriteResponseBodyAsync(
        OutputFormatterWriteContext context, Encoding encoding)
    {
        var books = (IEnumerable<BookDto>)context.Object!;
        var sb = new StringBuilder("Id,Title\\n");

        foreach (var b in books)
            sb.AppendLine($"{b.Id},\\"{b.Title}\\"");

        await context.HttpContext.Response
            .WriteAsync(sb.ToString(), encoding);
    }
}""")

    code(d, """builder.Services.AddControllers(options =>
{
    options.OutputFormatters.Insert(0, new CsvOutputFormatter());
});""")

    para(d, "`Insert(0, ...)` formatterni ro'yxat boshiga qo'yadi — tartib tanlovga "
            "ta'sir qiladi.")

    # ───────────────────────────────────────────
    h1(d, "6. URL orqali format tanlash")

    para(d, "`Accept` sarlavhasi o'rniga kengaytma bilan format tanlash ham mumkin:")

    code(d, """builder.Services.AddControllers(options =>
{
    options.FormatterMappings.SetMediaTypeMappingForFormat(
        "xml", MediaTypeHeaderValue.Parse("application/xml"));
});

// Kontrollerda
[Route("api/books/{id}.{format?}")]
[FormatFilter]
public class BooksController : ControllerBase { }""")

    para(d, "Endi `/api/books/1.xml` so'rovi XML, `/api/books/1.json` esa JSON "
            "qaytaradi. Brauzerda qo'lda tekshirish uchun qulay.")

    # ───────────────────────────────────────────
    h1(d, "7. Xulosa")

    bullets(d, [
        "Output formatter javobni, input formatter so'rov tanasini aylantiradi.",
        "Sukut bo'yicha faqat `System.Text.Json` yoqilgan; u tez, lekin qoidalari qattiq.",
        "`AddJsonOptions` orqali nomlash siyosati, `null` larni tashlab ketish va enum "
        "ni matn qilish sozlanadi.",
        "`AddNewtonsoftJson` `System.Text.Json` ni butunlay almashtiradi; "
        "`JsonPatchDocument` uchun u hali ham kerak.",
        "XML `AddXmlSerializerFormatters()` yoki `AddXmlDataContractSerializerFormatters()` "
        "bilan yoqiladi.",
        "Aylanma havola muammosining asl yechimi — entity o'rniga DTO qaytarish.",
        "`TextOutputFormatter` dan meros olib ixtiyoriy format qo'shish mumkin.",
    ])

    sources(d, [
        ("Format response data in ASP.NET Core Web API",
         "https://learn.microsoft.com/en-us/aspnet/core/web-api/advanced/formatting"),
        ("Custom formatters in ASP.NET Core Web API",
         "https://learn.microsoft.com/en-us/aspnet/core/web-api/advanced/custom-formatters"),
        ("How to customize property names and values with System.Text.Json",
         "https://learn.microsoft.com/en-us/dotnet/standard/serialization/system-text-json/customize-properties"),
        ("Migrate from Newtonsoft.Json to System.Text.Json",
         "https://learn.microsoft.com/en-us/dotnet/standard/serialization/system-text-json/migrate-from-newtonsoft"),
    ])
