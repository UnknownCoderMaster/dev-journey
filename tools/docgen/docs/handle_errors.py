# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "Handle errors"
CATEGORY = "ASP.NET"
TITLE = "Xatoliklarni Qayta Ishlash"
SUBTITLE = "Markazlashgan xatolik boshqaruvi va standart javob formati"
FILENAME = "Handle errors.docx"


def build(d):
    h1(d, "1. Nima uchun markazlashgan yondashuv kerak")

    para(d, "Har bir kontroller metodini `try/catch` bilan o'rash mumkin, lekin bu uch "
            "muammoni tug'diradi: kod takrorlanadi, xatolik javoblari turli joylarda "
            "turlicha formatlanadi va biror metodda `catch` yozish unutilsa, "
            "foydalanuvchiga ichki tafsilotlar ko'rinib qolishi mumkin.")

    para(d, "ASP.NET Core bu vazifani ilova darajasiga ko'taradi — xatolik qayerda "
            "yuzaga kelishidan qat'i nazar, u bitta joyda qayta ishlanadi va bitta "
            "formatda qaytariladi.")

    note(d, "Men bu qarorga shunday keldim:",
         "Avvaliga har bir metodda `try/catch` yozardim. Keyin sezdimki, ularning "
         "ko'pchiligi bir xil — xatoni logga yozib, 500 qaytarish. Bir necha joyda esa "
         "`catch` umuman yo'q edi va u yerda stack trace to'g'ridan-to'g'ri javobga "
         "tushardi. Markazlashgan handler shu ikkala muammoni ham hal qildi.")

    # ───────────────────────────────────────────
    h1(d, "2. Development va Production farqi")

    code(d, """var app = builder.Build();

if (app.Environment.IsDevelopment())
{
    app.UseDeveloperExceptionPage();   // to'liq stack trace
}
else
{
    app.UseExceptionHandler("/error"); // umumiy xabar
    app.UseHsts();
}""")

    para(d, "`UseDeveloperExceptionPage` xatolikning to'liq tafsilotini — stack trace, "
            "so'rov sarlavhalari, so'rov tanasi — ko'rsatadi. Bu production da mutlaqo "
            "qabul qilinmaydi, chunki u ilovaning ichki tuzilishi haqida ma'lumot "
            "beradi.")

    note(d, "Buni albatta tekshiring:",
         "`UseDeveloperExceptionPage` ni shart ichiga olishni unutish — jiddiy "
         "xavfsizlik nuqsoni. Stack trace orqali tashqi odam ulanish satri, fayl "
         "yo'llari va ishlatilgan kutubxona versiyalarini bilib oladi. Men serverga "
         "chiqarishdan oldin ataylab noto'g'ri so'rov yuborib, javobda nima "
         "qaytayotganini tekshiraman.")

    # ───────────────────────────────────────────
    h1(d, "3. IExceptionHandler — zamonaviy usul")

    para(d, ".NET 8 dan boshlab `IExceptionHandler` interfeysi mavjud. U xatolik "
            "turlariga qarab turli javob qaytarishni qulay qiladi.")

    code(d, """public class ValidationExceptionHandler : IExceptionHandler
{
    private readonly ILogger<ValidationExceptionHandler> _logger;

    public ValidationExceptionHandler(ILogger<ValidationExceptionHandler> logger)
        => _logger = logger;

    public async ValueTask<bool> TryHandleAsync(
        HttpContext context,
        Exception exception,
        CancellationToken ct)
    {
        if (exception is not ValidationException ve)
            return false;      // bu handler bu xatolikni bilmaydi

        _logger.LogWarning("Validatsiya xatosi: {Message}", ve.Message);

        var problem = new ProblemDetails
        {
            Status = StatusCodes.Status400BadRequest,
            Title = "Kiritilgan ma'lumot noto'g'ri",
            Detail = ve.Message
        };

        context.Response.StatusCode = problem.Status.Value;
        await context.Response.WriteAsJsonAsync(problem, ct);
        return true;           // qayta ishlandi
    }
}""")

    code(d, """builder.Services.AddExceptionHandler<ValidationExceptionHandler>();
builder.Services.AddExceptionHandler<NotFoundExceptionHandler>();
builder.Services.AddExceptionHandler<FallbackExceptionHandler>();
builder.Services.AddProblemDetails();

var app = builder.Build();
app.UseExceptionHandler();""")

    para(d, "Handler lar ro'yxatdan o'tgan tartibda chaqiriladi. Birortasi `true` "
            "qaytarsa, zanjir to'xtaydi. Shuning uchun eng umumiy handler oxirida "
            "turishi kerak.")

    note(d, "Bu tuzilma menga yoqadi:",
         "Har bir xatolik turi o'z faylida qayta ishlanadi va ular bir-biriga "
         "aralashmaydi. Yangi xatolik turi qo'shsam, mavjud kodga tegmayman — "
         "shunchaki yangi handler yozib, ro'yxatga qo'shaman.")

    # ───────────────────────────────────────────
    h1(d, "4. ProblemDetails — standart format")

    para(d, "RFC 9457 (avvalgi RFC 7807) HTTP API lar uchun xatolik javobining standart "
            "formatini belgilaydi. ASP.NET Core uni `ProblemDetails` klassi orqali "
            "qo'llab-quvvatlaydi.")

    code(d, """{
  "type": "https://tools.ietf.org/html/rfc9110#section-15.5.1",
  "title": "Kiritilgan ma'lumot noto'g'ri",
  "status": 400,
  "detail": "Email maydoni to'ldirilmagan",
  "instance": "/api/users",
  "traceId": "00-8f1a...-01"
}""")

    para(d, "Standart formatning foydasi shundaki, mijoz ilovasi har bir API uchun "
            "alohida xatolik tuzilmasini o'rganmaydi.")

    code(d, """builder.Services.AddProblemDetails(options =>
{
    options.CustomizeProblemDetails = ctx =>
    {
        ctx.ProblemDetails.Instance =
            $"{ctx.HttpContext.Request.Method} {ctx.HttpContext.Request.Path}";

        ctx.ProblemDetails.Extensions["traceId"] =
            Activity.Current?.Id ?? ctx.HttpContext.TraceIdentifier;
    };
});""")

    note(d, "traceId eng foydali maydon:",
         "Foydalanuvchi \"xatolik chiqdi\" deganda men undan shu identifikatorni "
         "so'rayman va loglardan aynan o'sha so'rovni topaman. Usiz esa taxminan "
         "o'sha vaqtdagi barcha loglarni ko'rib chiqishga to'g'ri keladi.")

    # ───────────────────────────────────────────
    h1(d, "5. Domen xatoliklari")

    para(d, "Biznes qoidalari buzilganda alohida istisno tiplari yaratish qulay:")

    code(d, """public abstract class AppException : Exception
{
    public abstract int StatusCode { get; }
    protected AppException(string message) : base(message) { }
}

public class NotFoundException : AppException
{
    public override int StatusCode => StatusCodes.Status404NotFound;
    public NotFoundException(string entity, object id)
        : base($"{entity} topilmadi (id: {id})") { }
}

public class ConflictException : AppException
{
    public override int StatusCode => StatusCodes.Status409Conflict;
    public ConflictException(string message) : base(message) { }
}""")

    code(d, """public async ValueTask<bool> TryHandleAsync(
    HttpContext context, Exception exception, CancellationToken ct)
{
    if (exception is not AppException app)
        return false;

    context.Response.StatusCode = app.StatusCode;
    await context.Response.WriteAsJsonAsync(new ProblemDetails
    {
        Status = app.StatusCode,
        Title = app.Message
    }, ct);
    return true;
}""")

    note(d, "Bu yerda o'lchov hissi kerak:",
         "Istisno — bu nazorat oqimini uzish vositasi va u qimmat. Agar men har bir "
         "validatsiya xatosi uchun istisno otsam, oddiy holatlar ham sekinlashadi. "
         "Shuning uchun kutilgan natijalarni (masalan \"bunday foydalanuvchi yo'q\") "
         "odatdagi qaytariladigan qiymat bilan ifodalaganim ma'qul; istisno esa "
         "haqiqatan kutilmagan holatlar uchun.")

    # ───────────────────────────────────────────
    h1(d, "6. Status kodlar uchun sahifa")

    para(d, "Istisno otilmagan, lekin javob kodi xatolikni bildirgan holatlar ham bor — "
            "masalan 404. Ular uchun alohida middleware ishlatiladi:")

    code(d, """app.UseStatusCodePages(async context =>
{
    var response = context.HttpContext.Response;
    if (response.StatusCode == StatusCodes.Status404NotFound)
    {
        await response.WriteAsJsonAsync(new ProblemDetails
        {
            Status = 404,
            Title = "Resurs topilmadi"
        });
    }
});""")

    # ───────────────────────────────────────────
    h1(d, "7. Middleware tartibi")

    para(d, "Xatolik boshqaruvi middleware zanjirining **eng boshida** turishi kerak — "
            "faqat shunda u o'zidan keyingi barcha bosqichlardagi xatoliklarni ushlay "
            "oladi.")

    code(d, """var app = builder.Build();

app.UseExceptionHandler();      // eng birinchi
app.UseStatusCodePages();
app.UseHttpsRedirection();
app.UseRouting();
app.UseAuthentication();
app.UseAuthorization();
app.MapControllers();""")

    note(d, "Bu xato menda bo'lgan:",
         "Bir marta `UseExceptionHandler` ni `UseRouting` dan keyin qo'yib qo'ygandim "
         "va routing bosqichidagi xatolik ushlanmay qoldi. Tartib bu yerda shunchaki "
         "uslub emas — u ishlashni belgilaydi.")

    # ───────────────────────────────────────────
    h1(d, "8. Xulosa")

    bullets(d, [
        "Xatoliklarni markazlashgan joyda qayta ishlash kod takrorlanishini va "
        "sirlarning sizib chiqishini oldini oladi.",
        "`UseDeveloperExceptionPage` faqat `Development` muhitida yoqilishi shart.",
        "`IExceptionHandler` (.NET 8+) xatolik turlarini alohida klasslarga ajratadi; "
        "ular ro'yxatdan o'tgan tartibda chaqiriladi.",
        "`ProblemDetails` — RFC 9457 bo'yicha standart xatolik formati.",
        "`traceId` ni javobga qo'shish nosozlikni topishni sezilarli osonlashtiradi.",
        "Istisno qimmat vosita — kutilgan holatlar uchun oddiy qaytariladigan qiymat "
        "afzalroq.",
        "`UseExceptionHandler` middleware zanjirining eng boshida turishi kerak.",
    ])

    sources(d, [
        ("Handle errors in ASP.NET Core",
         "https://learn.microsoft.com/en-us/aspnet/core/fundamentals/error-handling"),
        ("Handle errors in ASP.NET Core web APIs",
         "https://learn.microsoft.com/en-us/aspnet/core/web-api/handle-errors"),
        ("RFC 9457 — Problem Details for HTTP APIs",
         "https://www.rfc-editor.org/rfc/rfc9457.html"),
    ])
