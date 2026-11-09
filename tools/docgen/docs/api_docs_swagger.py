# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "API documentation with Swagger / OpenAPI"
CATEGORY = "ASP.NET"
TITLE = "Swagger va OpenAPI bilan API Hujjati"
SUBTITLE = "Hujjatni generatsiya qilish, boyitish va ko'rsatish"
FILENAME = "API documentation with Swagger - OpenAPI.docx"


def build(d):
    h1(d, "1. Nima uchun avtomatik hujjat")

    para(d, "API hujjatini qo'lda yozish ikki muammoga olib keladi: u yozishga vaqt "
            "oladi va kod o'zgarganda tez eskiradi. Eskirgan hujjat esa hujjat "
            "yo'qligidan ham yomonroq, chunki unga ishonib ish qilinadi.")

    para(d, "Avtomatik generatsiya bu muammoni hal qiladi — hujjat kodning o'zidan "
            "olinadi, shuning uchun u har doim joriy holatni aks ettiradi.")

    para(d, "Natijada hosil bo'ladigan OpenAPI hujjati uch maqsadda ishlatiladi: "
            "odamlar uchun interaktiv sahifa, mijoz kodini avtomatik generatsiya qilish "
            "va API o'zgarishlarini kuzatish.")

    # ───────────────────────────────────────────
    h1(d, "2. Platformaning o'z paketi (.NET 9+)")

    code(d, """dotnet add package Microsoft.AspNetCore.OpenApi""")

    code(d, """var builder = WebApplication.CreateBuilder(args);

builder.Services.AddOpenApi();

var app = builder.Build();

if (app.Environment.IsDevelopment())
{
    app.MapOpenApi();          // /openapi/v1.json
}""")

    para(d, "Shu ikki satr bilan hujjat tayyor bo'ladi. Lekin ko'rish sahifasi "
            "yaratilmaydi — paket faqat JSON hujjatni beradi.")

    note(d, "Buni bilmasdan vaqt yo'qotgandim:",
         "Yangi loyihada odatdagicha `/swagger` ga kirib, 404 oldim. Keyin tushundimki, "
         ".NET 9 dan boshlab shablondan Swashbuckle olib tashlangan va u bilan birga "
         "Swagger UI ham ketgan. Hujjat `/openapi/v1.json` da turibdi, lekin uni "
         "ko'rsatadigan hech narsa yo'q.")

    h2(d, "2.1 Sahifa qo'shish — Scalar")

    code(d, """dotnet add package Scalar.AspNetCore""")

    code(d, """if (app.Environment.IsDevelopment())
{
    app.MapOpenApi();
    app.MapScalarApiReference();   // /scalar/v1
}""")

    h2(d, "2.2 Sahifa qo'shish — Swagger UI")

    para(d, "Swagger UI ni ham platformaning hujjat generatoriga ulash mumkin — "
            "Swashbuckle ning faqat UI qismi ishlatiladi:")

    code(d, """dotnet add package Swashbuckle.AspNetCore.SwaggerUI""")

    code(d, """app.MapOpenApi();
app.UseSwaggerUI(options =>
{
    options.SwaggerEndpoint("/openapi/v1.json", "API v1");
});""")

    note(d, "Mavzuga aloqador bir kashfiyot:",
         "Swagger UI da mavzu almashtirish tugmasi (lampa belgisi) bor, lekin u faqat "
         "SwaggerUI 10.x versiyasidan boshlab paydo bo'lgan. Eski loyihalarda u "
         "ko'rinmaydi va bu paketning versiyasiga bog'liq — kodda sozlanadigan narsa "
         "emas. `Swashbuckle.AspNetCore` ni 10.x ga ko'tarish orqali uni .NET 8 da ham "
         "olish mumkin, lekin bu `Microsoft.OpenApi` 2.x ga o'tish demakdir va "
         "buzuvchi o'zgarishlar bo'lishi mumkin.")

    # ───────────────────────────────────────────
    h1(d, "3. Swashbuckle bilan to'liq yondashuv")

    code(d, """dotnet add package Swashbuckle.AspNetCore""")

    code(d, """builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen(options =>
{
    options.SwaggerDoc("v1", new OpenApiInfo
    {
        Title = "Books API",
        Version = "v1",
        Description = "Kitoblar katalogi bilan ishlash uchun API",
        Contact = new OpenApiContact { Name = "Backend jamoasi" }
    });
});

var app = builder.Build();
app.UseSwagger();
app.UseSwaggerUI();""")

    # ───────────────────────────────────────────
    h1(d, "4. Hujjatni boyitish")

    h2(d, "4.1 XML izohlar")

    para(d, "Kod ichidagi izohlarni hujjatga chiqarish uchun avval ularni fayl sifatida "
            "yaratish kerak:")

    code(d, """<PropertyGroup>
  <GenerateDocumentationFile>true</GenerateDocumentationFile>
  <NoWarn>$(NoWarn);1591</NoWarn>
</PropertyGroup>""", caption="csproj fayli")

    para(d, "`1591` ogohlantirishini o'chirish kerak, aks holda izohi yo'q har bir "
            "ochiq a'zo uchun ogohlantirish chiqadi.")

    code(d, """/// <summary>
/// Kitobni identifikatori bo'yicha qaytaradi.
/// </summary>
/// <param name="id">Kitob identifikatori</param>
/// <response code="200">Kitob topildi</response>
/// <response code="404">Bunday kitob mavjud emas</response>
[HttpGet("{id:int}")]
[ProducesResponseType<BookDto>(StatusCodes.Status200OK)]
[ProducesResponseType(StatusCodes.Status404NotFound)]
public async Task<IActionResult> GetById(int id) => ...;""")

    para(d, ".NET 10 da platformaning o'z generatori XML izohlarni avtomatik o'qiydi. "
            "Swashbuckle da esa buni aniq ko'rsatish kerak:")

    code(d, """options.IncludeXmlComments(Path.Combine(
    AppContext.BaseDirectory,
    $"{Assembly.GetExecutingAssembly().GetName().Name}.xml"));""")

    h2(d, "4.2 Javob turlarini e'lon qilish")

    para(d, "`ProducesResponseType` atributi hujjatga qaysi status kod qanday tanani "
            "qaytarishini aytadi. Usiz hujjatda faqat 200 ko'rinadi va mijoz boshqa "
            "holatlarga tayyorlanmaydi.")

    code(d, """// Minimal API da
app.MapGet("/api/books/{id:int}", GetBook)
   .Produces<BookDto>(StatusCodes.Status200OK)
   .ProducesProblem(StatusCodes.Status404NotFound)
   .WithSummary("Kitobni olish")
   .WithTags("Books");""")

    note(d, "Bu atributlarni yozish zerikarli, lekin arziydi:",
         "Men avval faqat muvaffaqiyatli javobni yozardim. Keyin mijoz tomonidagi "
         "dasturchi \"404 da nima qaytadi?\" deb so'radi va men javob bera olmadim — "
         "hujjatda yo'q edi. Shundan keyin xatolik javoblarini ham e'lon qilishni "
         "odat qildim. Bu integratsiya paytidagi savollarni sezilarli kamaytirdi.")

    h2(d, "4.3 Guruhlash")

    code(d, """[Tags("Kitoblar")]
[ApiController]
[Route("api/books")]
public class BooksController : ControllerBase { }""")

    # ───────────────────────────────────────────
    h1(d, "5. Avtorizatsiyani qo'shish")

    para(d, "Hujjat sahifasidan himoyalangan endpoint larni sinash uchun token kiritish "
            "imkoni kerak bo'ladi.")

    h2(d, "5.1 Platformaning generatori — transformer orqali")

    code(d, """builder.Services.AddOpenApi(options =>
{
    options.AddDocumentTransformer((document, context, ct) =>
    {
        document.Components ??= new OpenApiComponents();
        document.Components.SecuritySchemes["Bearer"] = new OpenApiSecurityScheme
        {
            Type = SecuritySchemeType.Http,
            Scheme = "bearer",
            BearerFormat = "JWT",
            In = ParameterLocation.Header
        };
        return Task.CompletedTask;
    });
});""")

    h2(d, "5.2 Swashbuckle — AddSecurityDefinition orqali")

    code(d, """options.AddSecurityDefinition("Bearer", new OpenApiSecurityScheme
{
    Name = "Authorization",
    Type = SecuritySchemeType.Http,
    Scheme = "bearer",
    BearerFormat = "JWT",
    In = ParameterLocation.Header,
    Description = "JWT tokenni 'Bearer ' prefiksisiz kiriting"
});

options.AddSecurityRequirement(new OpenApiSecurityRequirement
{
    {
        new OpenApiSecurityScheme
        {
            Reference = new OpenApiReference
            {
                Type = ReferenceType.SecurityScheme,
                Id = "Bearer"
            }
        },
        Array.Empty<string>()
    }
});""")

    # ───────────────────────────────────────────
    h1(d, "6. Transformerlar bilan hujjatni o'zgartirish")

    para(d, "Platformaning generatori uch darajada o'zgartirishga ruxsat beradi: hujjat, "
            "operatsiya va sxema.")

    code(d, """builder.Services.AddOpenApi(options =>
{
    options.AddDocumentTransformer((doc, ctx, ct) =>
    {
        doc.Info.Title = "Books API";
        doc.Info.Version = "v1";
        return Task.CompletedTask;
    });

    options.AddOperationTransformer((operation, ctx, ct) =>
    {
        operation.Responses.TryAdd("500", new OpenApiResponse
        {
            Description = "Ichki server xatosi"
        });
        return Task.CompletedTask;
    });
});""")

    para(d, "Swashbuckle da bu vazifani `IDocumentFilter`, `IOperationFilter` va "
            "`ISchemaFilter` interfeyslari bajaradi.")

    # ───────────────────────────────────────────
    h1(d, "7. Hujjatni fayl sifatida chiqarish")

    para(d, "OpenAPI faylini qurilish paytida yaratib, uni git ga saqlash foydali — "
            "shunda API o'zgarishlari commit lar orasida ko'rinadi:")

    code(d, """dotnet add package Microsoft.Extensions.ApiDescription.Server""")

    code(d, """<PropertyGroup>
  <OpenApiDocumentsDirectory>$(MSBuildProjectDirectory)/docs</OpenApiDocumentsDirectory>
</PropertyGroup>""")

    note(d, "Bu menga juda yoqqan amaliyot:",
         "Hujjat fayli git da turganda, pull request ni ko'rayotgan odam API da nima "
         "o'zgarganini darhol ko'radi. Tasodifan buzuvchi o'zgarish kiritilsa — "
         "masalan maydon nomi o'zgartirilsa — u diff da aniq ko'rinadi. Kodni o'qib "
         "buni payqash ancha qiyinroq.")

    # ───────────────────────────────────────────
    h1(d, "8. Xavfsizlik")

    bullets(d, [
        "Hujjat sahifasini production da ochiq qoldirmaslik — u API ning to'liq "
        "xaritasini beradi.",
        "Agar ochiq qoldirish kerak bo'lsa, uni avtorizatsiya ortiga yashirish.",
        "Ichki yoki eskirgan endpoint larni hujjatdan chiqarib tashlash.",
    ])

    code(d, """// Development dan tashqarida yopiq
if (app.Environment.IsDevelopment())
{
    app.MapOpenApi();
    app.MapScalarApiReference();
}""")

    code(d, """[ApiExplorerSettings(IgnoreApi = true)]
[HttpPost("internal/reindex")]
public async Task<IActionResult> Reindex() => ...;""",
         caption="Alohida endpoint ni hujjatdan yashirish")

    # ───────────────────────────────────────────
    h1(d, "9. Xulosa")

    bullets(d, [
        "`Microsoft.AspNetCore.OpenApi` (.NET 9+) hujjat yaratadi, lekin ko'rish "
        "sahifasini bermaydi — Scalar yoki Swagger UI alohida qo'shiladi.",
        "Swashbuckle to'liq yechim beradi va hali ham qo'llab-quvvatlanadi.",
        "XML izohlar uchun `GenerateDocumentationFile` yoqilishi kerak.",
        "`ProducesResponseType` / `Produces` orqali barcha javob turlarini e'lon qilish "
        "integratsiya savollarini kamaytiradi.",
        "Avtorizatsiya sxemasi platformada transformer, Swashbuckle da "
        "`AddSecurityDefinition` orqali qo'shiladi.",
        "Hujjatni fayl sifatida git ga saqlash API o'zgarishlarini ko'rinarli qiladi.",
        "Production da hujjat sahifasini ochiq qoldirmaslik kerak.",
    ])

    sources(d, [
        ("Generate OpenAPI documents — ASP.NET Core",
         "https://learn.microsoft.com/en-us/aspnet/core/fundamentals/openapi/aspnetcore-openapi"),
        ("Customize OpenAPI documents — ASP.NET Core",
         "https://learn.microsoft.com/en-us/aspnet/core/fundamentals/openapi/customize-openapi"),
        ("Use OpenAPI documents — ASP.NET Core",
         "https://learn.microsoft.com/en-us/aspnet/core/fundamentals/openapi/using-openapi-documents"),
        ("Swashbuckle.AspNetCore — GitHub",
         "https://github.com/domaindrivendev/Swashbuckle.AspNetCore"),
        ("Scalar for .NET — hujjat",
         "https://guides.scalar.com/scalar/scalar-api-references/net-integration"),
    ])
