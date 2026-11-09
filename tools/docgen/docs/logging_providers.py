# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "Logging providers"
CATEGORY = "ASP.NET"
TITLE = "Logging Provayderlari"
SUBTITLE = "Loglarni qayerga va qanday yozish"
FILENAME = "Logging providers.docx"


def build(d):
    h1(d, "1. Logging arxitekturasi")

    para(d, "ASP.NET Core da log yozish ikki qismdan iborat. Birinchisi — `ILogger` "
            "interfeysi, kod shu orqali xabar yuboradi. Ikkinchisi — provayder, u "
            "xabarni biror joyga yetkazadi: konsolga, faylga, tashqi xizmatga.")

    para(d, "Bu ajratish tufayli kod log qayerga borishini bilmaydi. Bitta xabar bir "
            "vaqtning o'zida bir nechta provayderga yuborilishi ham mumkin.")

    code(d, """public class OrderService
{
    private readonly ILogger<OrderService> _logger;

    public OrderService(ILogger<OrderService> logger) => _logger = logger;

    public void Process(int orderId)
    {
        _logger.LogInformation("Buyurtma {OrderId} qayta ishlanmoqda", orderId);
    }
}""")

    note(d, "Bitta oddiy, lekin muhim qoida:",
         "Xabarni `$\"Buyurtma {orderId}\"` deb interpolyatsiya bilan yozish mumkin, "
         "lekin yuqoridagidek shablon va parametr sifatida yozish kerak. Farqi shundaki, "
         "ikkinchi holatda `OrderId` alohida maydon bo'lib saqlanadi va keyinchalik "
         "\"shu buyurtma bo'yicha barcha loglarni ko'rsat\" deb qidirish mumkin bo'ladi. "
         "Interpolyatsiyada esa bu shunchaki matn ichidagi raqam bo'lib qoladi.")

    # ───────────────────────────────────────────
    h1(d, "2. O'rnatilgan provayderlar")

    table(d, ["Provayder", "Qayerga yozadi"],
          [["Console", "Standart chiqishga"],
           ["Debug", "Tuzatuvchi oynasiga (`Debug.WriteLine`)"],
           ["EventSource", "Platformaning hodisa oqimiga (`dotnet-trace`)"],
           ["EventLog", "Windows hodisalar jurnaliga"],
           ["ApplicationInsights", "Azure monitoring xizmatiga"]],
          widths=[4.6, 10.9])

    para(d, "`WebApplication.CreateBuilder()` chaqirilganda Console, Debug va EventSource "
            "provayderlari avtomatik ulanadi. Qo'shimcha hech narsa yozish shart emas.")

    h2(d, "2.1 Sukutdagilarni o'chirish")

    code(d, """builder.Logging.ClearProviders();
builder.Logging.AddConsole();""")

    para(d, "Bu konteyner muhitida foydali: Debug provayderi u yerda keraksiz, "
            "Console esa konteyner loglariga to'g'ridan-to'g'ri tushadi.")

    h2(d, "2.2 Fayl provayderi")

    para(d, "Platformada faylga yozadigan o'rnatilgan provayder **yo'q**. Buning uchun "
            "uchinchi tomon kutubxonasi kerak bo'ladi.")

    note(d, "Bu meni dastlab hayron qoldirgan:",
         "Men faylga log yozish eng oddiy ehtiyoj deb o'ylardim va uni platformada "
         "topmaganimdan ajablandim. Keyin sababini tushundim — zamonaviy joylashtirishda "
         "ilova odatda konteynerda ishlaydi va log konsolga chiqadi, uni esa Docker, "
         "Kubernetes yoki systemd yig'ib oladi. Ya'ni faylga yozish ilovaning ishi emas. "
         "Lekin an'anaviy serverda baribir fayl kerak bo'ladi.")

    # ───────────────────────────────────────────
    h1(d, "3. Log darajalari")

    table(d, ["Daraja", "Qachon ishlatiladi"],
          [["`Trace`", "Eng mayda tafsilotlar; production da deyarli hech qachon"],
           ["`Debug`", "Dasturchi uchun diagnostika"],
           ["`Information`", "Odatdagi oqim: so'rov keldi, vazifa bajarildi"],
           ["`Warning`", "Kutilmagan holat, lekin ish davom etyapti"],
           ["`Error`", "Operatsiya bajarilmadi"],
           ["`Critical`", "Tizim ishlay olmayapti"]],
          widths=[3.2, 12.3])

    h2(d, "3.1 Darajani sozlash")

    code(d, """{
  "Logging": {
    "LogLevel": {
      "Default": "Information",
      "Microsoft.AspNetCore": "Warning",
      "Microsoft.EntityFrameworkCore.Database.Command": "Information",
      "MyApp.Services.PaymentService": "Debug"
    },
    "Console": {
      "LogLevel": { "Default": "Warning" }
    }
  }
}""")

    para(d, "Kalitlar kategoriya nomi bo'yicha prefiks sifatida ishlaydi — eng aniq mos "
            "kelgan yozuv tanlanadi. `Console` bo'limi esa faqat shu provayderga "
            "tegishli darajani belgilaydi.")

    note(d, "Amalda eng ko'p ishlatadigan sozlamam:",
         "`Microsoft.AspNetCore` ni `Warning` ga tushirish. Aks holda har bir so'rov "
         "uchun bir nechta `Information` xabari chiqadi va men o'z loglarimni "
         "ular orasidan topa olmayman. Bu shovqin ayniqsa development da bezovta qiladi.")

    # ───────────────────────────────────────────
    h1(d, "4. Serilog — eng keng tarqalgan muqobil")

    para(d, "Serilog strukturalangan loglarni turli joylarga yozish imkonini beradi va "
            "amalda standart tanlovga aylangan.")

    code(d, """dotnet add package Serilog.AspNetCore""")

    code(d, """builder.Host.UseSerilog((context, config) =>
{
    config.ReadFrom.Configuration(context.Configuration)
          .Enrich.FromLogContext()
          .Enrich.WithMachineName()
          .WriteTo.Console()
          .WriteTo.File(
              "logs/app-.log",
              rollingInterval: RollingInterval.Day,
              retainedFileCountLimit: 14);
});""")

    para(d, "Serilog ulangandan keyin ham kod o'zgarmaydi — `ILogger<T>` o'sha-o'sha "
            "ishlatiladi. Faqat xabarlarning borish joyi o'zgaradi.")

    h2(d, "4.1 So'rov loglarini soddalashtirish")

    code(d, """app.UseSerilogRequestLogging();""")

    para(d, "Bu middleware har bir so'rov uchun bitta yig'ma satr yozadi — usul, yo'l, "
            "javob kodi va bajarilish vaqti. Platformaning o'zi yozadigan bir nechta "
            "satr o'rniga bitta tushunarli yozuv chiqadi.")

    h2(d, "4.2 Kontekst qo'shish")

    code(d, """using (LogContext.PushProperty("OrderId", orderId))
{
    _logger.LogInformation("To'lov boshlandi");
    await _payment.ChargeAsync(orderId);
    _logger.LogInformation("To'lov yakunlandi");
}""")

    para(d, "Blok ichidagi barcha xabarlarga `OrderId` maydoni avtomatik qo'shiladi. "
            "Bu uzun jarayonlarni kuzatishda juda qo'l keladi.")

    # ───────────────────────────────────────────
    h1(d, "5. Scope — bog'liq xabarlarni guruhlash")

    para(d, "Serilog ishlatilmasa ham, platformaning o'zida scope mexanizmi bor:")

    code(d, """using (_logger.BeginScope(new Dictionary<string, object>
{
    ["UserId"] = userId,
    ["RequestId"] = requestId
}))
{
    _logger.LogInformation("Profil yangilanmoqda");
}""")

    para(d, "Console provayderida scope ni ko'rsatish uchun uni yoqish kerak:")

    code(d, """"Console": { "IncludeScopes": true }""")

    # ───────────────────────────────────────────
    h1(d, "6. Nimani logga yozmaslik kerak")

    bullets(d, [
        "Parol, token, API kalit — hech qanday ko'rinishda.",
        "To'liq karta raqami, pasport ma'lumotlari va boshqa shaxsiy ma'lumotlar.",
        "Butun so'rov tanasi — unda sezgir maydonlar bo'lishi mumkin.",
        "Sikl ichidagi har bir iteratsiya — log fayli tez to'lib ketadi.",
    ])

    note(d, "Bu haqida alohida o'ylaganim bor:",
         "Log — bu ham ma'lumotlar ombori, faqat himoyasi zaifroq. Bazaga kirish uchun "
         "parol kerak, log fayliga esa ko'pincha serverga kirgan har kim qaray oladi. "
         "Shuning uchun \"bazaga yozmaydigan narsani logga ham yozmayman\" degan qoidani "
         "o'zimga o'rnatganman.")

    # ───────────────────────────────────────────
    h1(d, "7. Unumdorlik")

    para(d, "Log yozish ham resurs talab qiladi. Og'ir obyektni formatlashdan oldin "
            "daraja yoqilganini tekshirish mumkin:")

    code(d, """if (_logger.IsEnabled(LogLevel.Debug))
{
    _logger.LogDebug("Holat: {State}", JsonSerializer.Serialize(bigObject));
}""")

    para(d, "Tez-tez chaqiriladigan joylar uchun manba generatsiyasi eng samarali usul "
            "hisoblanadi — u formatlashni kompilyatsiya vaqtida tayyorlaydi:")

    code(d, """public static partial class Log
{
    [LoggerMessage(
        EventId = 1001,
        Level = LogLevel.Information,
        Message = "Buyurtma {OrderId} {Status} holatiga o'tdi")]
    public static partial void OrderStatusChanged(
        ILogger logger, int orderId, string status);
}

// Chaqirish
Log.OrderStatusChanged(_logger, order.Id, "Paid");""")

    # ───────────────────────────────────────────
    h1(d, "8. Xulosa")

    bullets(d, [
        "`ILogger` kod tomoni, provayder esa yetkazish tomoni — ular bir-biridan "
        "mustaqil.",
        "Console, Debug va EventSource avtomatik ulanadi; faylga yozish uchun tashqi "
        "kutubxona kerak.",
        "Xabarni shablon va parametr sifatida yozish strukturalangan qidiruv imkonini "
        "beradi.",
        "`Microsoft.AspNetCore` darajasini `Warning` ga tushirish shovqinni sezilarli "
        "kamaytiradi.",
        "Serilog fayl, tashqi xizmat va boyitilgan kontekstni bitta sozlamada beradi.",
        "Sezgir ma'lumotlar logga tushmasligi kerak — log himoyasi bazanikidan zaifroq.",
        "Tez-tez chaqiriladigan loglar uchun `LoggerMessage` manba generatori eng "
        "samarali usul.",
    ])

    sources(d, [
        ("Logging in .NET Core and ASP.NET Core",
         "https://learn.microsoft.com/en-us/aspnet/core/fundamentals/logging/"),
        ("High-performance logging with LoggerMessage",
         "https://learn.microsoft.com/en-us/dotnet/core/extensions/logger-message-generator"),
        ("Serilog — rasmiy hujjat",
         "https://serilog.net/"),
    ])
