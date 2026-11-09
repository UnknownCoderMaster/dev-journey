# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "API Versioning"
CATEGORY = "ASP.NET"
TITLE = "API Versiyalash"
SUBTITLE = "Mijozlarni buzmasdan API ni rivojlantirish"
FILENAME = "API Versioning.docx"


def build(d):
    h1(d, "1. Nima uchun versiyalash kerak")

    para(d, "API chop etilgandan keyin unga boshqa dasturlar bog'lanadi. Ular yangilanishi "
            "mening nazoratimda bo'lmaydi — mobil ilova foydalanuvchining qurilmasida "
            "oylab eski holatda qolishi mumkin.")

    para(d, "Shu sababli API dagi har qanday buzuvchi o'zgarish ishlab turgan mijozlarni "
            "sindiradi. Versiyalash bu muammoni hal qiladi: eski versiya o'z holicha "
            "ishlayveradi, yangi imkoniyatlar esa yangi versiyada beriladi.")

    h2(d, "1.1 Qanday o'zgarish buzuvchi hisoblanadi")

    table(d, ["Buzuvchi", "Buzuvchi emas"],
          [["Maydonni o'chirish yoki nomini o'zgartirish", "Yangi ixtiyoriy maydon qo'shish"],
           ["Maydon tipini o'zgartirish", "Yangi endpoint qo'shish"],
           ["Yangi majburiy parametr qo'shish", "Yangi ixtiyoriy parametr qo'shish"],
           ["Javob tuzilmasini qayta qurish", "Xatolik xabarining matnini aniqlashtirish"],
           ["Endpoint ni o'chirish", "Ichki amalga oshirishni o'zgartirish"]],
          widths=[7.7, 7.8])

    note(d, "O'zimga o'rnatgan qoidam:",
         "Qo'shish — xavfsiz, olib tashlash va o'zgartirish — xavfli. Shuning uchun "
         "yangi versiya chiqarishdan oldin har doim so'rayman: bu o'zgarishni mavjud "
         "versiyaga qo'shimcha sifatida kiritib bo'ladimi? Ko'p hollarda javob \"ha\" "
         "bo'ladi va yangi versiya umuman kerak bo'lmaydi.")

    # ───────────────────────────────────────────
    h1(d, "2. Versiyani uzatish usullari")

    table(d, ["Usul", "Ko'rinishi"],
          [["URL segmenti", "`/api/v1/books`"],
           ["Query parametr", "`/api/books?api-version=1.0`"],
           ["Sarlavha", "`X-Api-Version: 1.0`"],
           ["Media tip", "`Accept: application/json;v=1.0`"]],
          widths=[4.0, 11.5])

    h2(d, "2.1 URL segmenti")

    para(d, "Eng keng tarqalgan usul. Versiya manzilda ko'rinib turadi, brauzerda "
            "sinash oson, keshlash bilan muammo chiqmaydi.")

    para(d, "Kamchiligi — REST nuqtai nazaridan bitta resurs ikki xil manzilga ega "
            "bo'lib qoladi, bu esa nazariy jihatdan noto'g'ri hisoblanadi.")

    h2(d, "2.2 Sarlavha")

    para(d, "Manzil toza qoladi va resurs identifikatori o'zgarmaydi. Lekin brauzerda "
            "oddiy havola orqali sinab bo'lmaydi va nosozlikni topish qiyinroq.")

    note(d, "Amalda nimani tanlayman:",
         "Nazariy tozalik tarafdorlari sarlavhani tavsiya qiladi, lekin men URL "
         "segmentini afzal ko'raman. Sabab amaliy: log faylga qarasam, qaysi versiyaga "
         "so'rov kelganini darhol ko'raman. Sarlavhada esa buni ko'rish uchun qo'shimcha "
         "sozlash kerak. Jamoa bilan ishlashda bu farq sezilarli.")

    # ───────────────────────────────────────────
    h1(d, "3. Asp.Versioning paketi")

    para(d, "ASP.NET Core da versiyalash platformaning o'zida emas, alohida paketda "
            "beriladi. Paket avval `Microsoft.AspNetCore.Mvc.Versioning` deb atalgan, "
            "hozirgi nomi `Asp.Versioning`.")

    code(d, """dotnet add package Asp.Versioning.Mvc
dotnet add package Asp.Versioning.Mvc.ApiExplorer""")

    code(d, """builder.Services.AddApiVersioning(options =>
{
    options.DefaultApiVersion = new ApiVersion(1, 0);
    options.AssumeDefaultVersionWhenUnspecified = true;
    options.ReportApiVersions = true;

    options.ApiVersionReader = ApiVersionReader.Combine(
        new UrlSegmentApiVersionReader(),
        new HeaderApiVersionReader("X-Api-Version"),
        new QueryStringApiVersionReader("api-version"));
})
.AddApiExplorer(options =>
{
    options.GroupNameFormat = "'v'VVV";
    options.SubstituteApiVersionInUrl = true;
});""")

    table(d, ["Sozlama", "Vazifasi"],
          [["`DefaultApiVersion`", "Versiya ko'rsatilmaganda ishlatiladigan qiymat"],
           ["`AssumeDefaultVersionWhenUnspecified`", "Versiyasiz so'rovga ruxsat beradi"],
           ["`ReportApiVersions`", "Javobga mavjud versiyalar ro'yxatini qo'shadi"],
           ["`ApiVersionReader`", "Versiya qayerdan o'qilishini belgilaydi"]],
          widths=[5.6, 9.9])

    note(d, "`ReportApiVersions` ni doim yoqaman:",
         "U javobga `api-supported-versions` sarlavhasini qo'shadi. Mijoz tomonidagi "
         "dasturchi men bilan bog'lanmasdan turib qaysi versiyalar mavjudligini bilib "
         "oladi. Kichik narsa, lekin integratsiya paytidagi savollarni kamaytiradi.")

    # ───────────────────────────────────────────
    h1(d, "4. Kontrollerlarni versiyalash")

    h2(d, "4.1 Alohida kontrollerlar")

    code(d, """[ApiController]
[ApiVersion("1.0")]
[Route("api/v{version:apiVersion}/books")]
public class BooksV1Controller : ControllerBase
{
    [HttpGet("{id:int}")]
    public async Task<BookDto> Get(int id) => ...;
}

[ApiController]
[ApiVersion("2.0")]
[Route("api/v{version:apiVersion}/books")]
public class BooksV2Controller : ControllerBase
{
    [HttpGet("{id:int}")]
    public async Task<BookDetailsDto> Get(int id) => ...;
}""")

    h2(d, "4.2 Bitta kontroller, turli metodlar")

    code(d, """[ApiController]
[ApiVersion("1.0")]
[ApiVersion("2.0")]
[Route("api/v{version:apiVersion}/books")]
public class BooksController : ControllerBase
{
    [HttpGet("{id:int}")]
    [MapToApiVersion("1.0")]
    public async Task<BookDto> GetV1(int id) => ...;

    [HttpGet("{id:int}")]
    [MapToApiVersion("2.0")]
    public async Task<BookDetailsDto> GetV2(int id) => ...;
}""")

    para(d, "Agar metodda `MapToApiVersion` bo'lmasa, u kontrollerga e'lon qilingan "
            "barcha versiyalarda mavjud bo'ladi. Bu o'zgarmagan endpoint larni "
            "takrorlamaslik imkonini beradi.")

    note(d, "Qaysi tuzilmani tanlash kerak:",
         "Agar v2 da bir-ikkita endpoint o'zgargan bo'lsa — bitta kontroller va "
         "`MapToApiVersion` yetarli. Agar butun resurs qayta ishlangan bo'lsa — alohida "
         "kontroller toza bo'ladi. Men odatda ikkinchisini tanlayman, chunki bitta "
         "kontroller ichida ikki versiyaning mantiqi aralashib, o'qish qiyinlashadi.")

    h2(d, "4.3 Eskirganini belgilash")

    code(d, """[ApiVersion("1.0", Deprecated = true)]
[ApiVersion("2.0")]""")

    para(d, "Javobda `api-deprecated-versions` sarlavhasi paydo bo'ladi. Bu mijozlarga "
            "ko'chish vaqti kelganini bildiradi, lekin endpoint ishlashda davom etadi.")

    # ───────────────────────────────────────────
    h1(d, "5. Minimal API da versiyalash")

    code(d, """var versionSet = app.NewApiVersionSet()
    .HasApiVersion(new ApiVersion(1, 0))
    .HasApiVersion(new ApiVersion(2, 0))
    .ReportApiVersions()
    .Build();

app.MapGet("/api/v{version:apiVersion}/books/{id:int}", GetBookV1)
   .WithApiVersionSet(versionSet)
   .MapToApiVersion(1, 0);

app.MapGet("/api/v{version:apiVersion}/books/{id:int}", GetBookV2)
   .WithApiVersionSet(versionSet)
   .MapToApiVersion(2, 0);""")

    # ───────────────────────────────────────────
    h1(d, "6. Hujjatda versiyalarni ko'rsatish")

    para(d, "Har bir versiya uchun alohida OpenAPI hujjati hosil qilinadi:")

    code(d, """builder.Services.AddOpenApi("v1");
builder.Services.AddOpenApi("v2");

var app = builder.Build();
app.MapOpenApi();      // /openapi/v1.json va /openapi/v2.json""")

    para(d, "Swagger UI da esa ro'yxatni to'ldirish kerak:")

    code(d, """app.UseSwaggerUI(options =>
{
    var provider = app.Services
        .GetRequiredService<IApiVersionDescriptionProvider>();

    foreach (var desc in provider.ApiVersionDescriptions)
    {
        options.SwaggerEndpoint(
            $"/openapi/{desc.GroupName}.json",
            desc.GroupName.ToUpperInvariant());
    }
});""")

    # ───────────────────────────────────────────
    h1(d, "7. Amaliy strategiya")

    bullets(d, [
        "Yangi versiyani faqat buzuvchi o'zgarish zarur bo'lgandagina chiqarish.",
        "Bir vaqtda ikkitadan ortiq versiyani qo'llab-quvvatlamaslik — har bir versiya "
        "qo'shimcha test va xatolik tuzatish yuki.",
        "Eski versiyani o'chirishdan oldin uning ishlatilishini loglar orqali tekshirish.",
        "O'chirish muddatini oldindan e'lon qilish va unga rioya qilish.",
        "Umumiy mantiqni xizmat qatlamida saqlash — versiyalar faqat kontroller va DTO "
        "darajasida farq qilsin.",
    ])

    note(d, "Oxirgi punkt eng muhimi:",
         "Agar biznes mantiqni kontrollerga yozib qo'ysam, yangi versiya chiqarishda "
         "uni nusxalashga to'g'ri keladi. Keyin xatolik topilsa — uni ikki joyda "
         "tuzatish kerak bo'ladi va biri albatta unutiladi. Mantiq xizmat qatlamida "
         "bo'lsa, versiyalar shunchaki turli DTO ga aylantirish qatlami bo'lib qoladi.")

    code(d, """// Umumiy mantiq
var book = await _bookService.GetAsync(id);

// v1 — qisqa javob
return _mapper.Map<BookDto>(book);

// v2 — kengaytirilgan javob
return _mapper.Map<BookDetailsDto>(book);""")

    # ───────────────────────────────────────────
    h1(d, "8. Xulosa")

    bullets(d, [
        "Versiyalash mijozlarni buzmasdan API ni rivojlantirish imkonini beradi.",
        "Maydon qo'shish buzuvchi emas; o'chirish, nomini yoki tipini o'zgartirish "
        "buzuvchi hisoblanadi.",
        "Versiya URL, sarlavha, query yoki media tip orqali uzatilishi mumkin; URL "
        "segmenti eng ko'p ishlatiladi.",
        "`Asp.Versioning` paketi `ApiVersion` va `MapToApiVersion` atributlarini beradi.",
        "`ReportApiVersions` mavjud va eskirgan versiyalarni javob sarlavhasida "
        "e'lon qiladi.",
        "Bir vaqtda qo'llab-quvvatlanadigan versiyalar sonini cheklash kerak.",
        "Biznes mantiq xizmat qatlamida qolishi, versiyalar faqat DTO darajasida "
        "farq qilishi lozim.",
    ])

    sources(d, [
        ("ASP.NET API Versioning — GitHub",
         "https://github.com/dotnet/aspnet-api-versioning"),
        ("API versioning wiki — dotnet/aspnet-api-versioning",
         "https://github.com/dotnet/aspnet-api-versioning/wiki"),
        ("Web API design best practices — versioning",
         "https://learn.microsoft.com/en-us/azure/architecture/best-practices/api-design#versioning-a-restful-web-api"),
    ])
