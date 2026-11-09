# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "Web server"
CATEGORY = "Web"
TITLE = "Web Server"
SUBTITLE = "HTTP so'rovni qabul qilishdan javob qaytarishgacha"
FILENAME = "Web server.docx"


def build(d):
    h1(d, "1. Web server nima qiladi")

    para(d, "Web server — bu tarmoq portini tinglab turuvchi, kelgan HTTP so'rovlarni "
            "qabul qiladigan va ularga javob qaytaradigan dastur. Uning asosiy vazifasi "
            "oddiy ko'rinadi, lekin ichida bir nechta bosqich bor.")

    para(d, "So'rov kelganda server quyidagilarni bajaradi: TCP ulanishini qabul qiladi, "
            "baytlar oqimidan HTTP so'rovini ajratib oladi, uni kim qayta ishlashini "
            "aniqlaydi, natijani HTTP javobiga o'raydi va ulanishni boshqaradi.")

    note(d, "Men bu atamani ikki ma'noda ishlatilishini payqadim:",
         "Ba'zan \"web server\" deganda Nginx yoki Apache kabi dastur tushuniladi, "
         "ba'zan esa saytni olib yuruvchi jismoniy server. Texnik suhbatda ko'pincha "
         "birinchi ma'no nazarda tutiladi — ya'ni dastur, mashina emas.")

    # ───────────────────────────────────────────
    h1(d, "2. Statik va dinamik kontent")

    para(d, "Dastlabki web serverlar faqat diskdagi fayllarni qaytarardi — HTML, rasm, "
            "CSS. Bu statik kontent deb ataladi va server uchun eng arzon ish: faylni "
            "o'qib, uzatish.")

    para(d, "Dinamik kontent esa har bir so'rovda qaytadan hosil qilinadi — bazadan "
            "ma'lumot olinadi, mantiq bajariladi, natija shakllantiriladi. Buning uchun "
            "server so'rovni ilova kodiga uzatishi kerak.")

    table(d, ["Jihat", "Statik", "Dinamik"],
          [["Manba", "Diskdagi fayl", "Kod bajarilishi natijasi"],
           ["Keshlanishi", "Oson", "Murakkab"],
           ["Tezlik", "Juda yuqori", "Mantiqqa bog'liq"],
           ["Misol", "`logo.png`, `app.js`", "`/api/orders` javobi"]],
          widths=[3.4, 6.0, 6.1])

    # ───────────────────────────────────────────
    h1(d, "3. Kestrel — .NET ning web serveri")

    para(d, "ASP.NET Core o'z web serveri bilan keladi — u Kestrel deb ataladi. Kestrel "
            "kross-platforma, HTTP/1.1, HTTP/2 va HTTP/3 ni qo'llab-quvvatlaydi va "
            "ilova bilan bitta jarayonda ishlaydi.")

    code(d, """var builder = WebApplication.CreateBuilder(args);

builder.WebHost.ConfigureKestrel(options =>
{
    options.ListenAnyIP(8080);

    options.Limits.MaxRequestBodySize = 10 * 1024 * 1024;   // 10 MB
    options.Limits.MaxConcurrentConnections = 1000;
    options.Limits.KeepAliveTimeout = TimeSpan.FromMinutes(2);
});

var app = builder.Build();
app.MapGet("/", () => "Ishlayapti");
app.Run();""")

    h2(d, "3.1 Qaysi manzilni tinglash")

    code(d, """# Atrof-muhit o'zgaruvchisi orqali
ASPNETCORE_URLS=http://+:8080

# Buyruq qatori orqali
dotnet run --urls "http://localhost:5080;https://localhost:5081" """)

    note(d, "Konteynerda ishlashda bu muhim:",
         "`localhost` ni tinglash konteyner ichida ishlaydi, lekin tashqaridan "
         "ulanib bo'lmaydi — chunki `localhost` faqat konteyner ichidagi interfeysni "
         "anglatadi. Konteynerda `http://+:8080` yoki `http://0.0.0.0:8080` yozish "
         "kerak. Men bu xatoni bir marta qilib, konteyner ishga tushgani holda "
         "javob bermayotganiga uzoq hayron bo'lganman.")

    # ───────────────────────────────────────────
    h1(d, "4. Middleware zanjiri")

    para(d, "Kestrel so'rovni qabul qilgandan keyin uni middleware zanjiriga uzatadi. "
            "Har bir middleware so'rovni ko'rib chiqadi, kerak bo'lsa o'zgartiradi va "
            "keyingisiga uzatadi yoki javobni o'zi qaytaradi.")

    code(d, """var app = builder.Build();

app.UseExceptionHandler();      // xatoliklarni ushlaydi
app.UseHttpsRedirection();      // HTTP ni HTTPS ga yo'naltiradi
app.UseStaticFiles();           // wwwroot dagi fayllarni beradi
app.UseRouting();               // qaysi endpoint ekanini aniqlaydi
app.UseAuthentication();        // kimligini aniqlaydi
app.UseAuthorization();         // ruxsatini tekshiradi
app.MapControllers();           // endpoint ni bajaradi

app.Run();""")

    para(d, "Tartib muhim. Masalan `UseAuthorization` `UseAuthentication` dan oldin "
            "tursa, ruxsat tekshirilayotganda foydalanuvchi hali aniqlanmagan bo'ladi "
            "va hamma so'rov rad etiladi.")

    note(d, "Zanjirni shunday tasavvur qilaman:",
         "Bu quvurdagi filtrlar kabi. So'rov birinchi filtrdan oxirgisiga qarab oqadi, "
         "javob esa teskari yo'nalishda qaytadi. Shuning uchun `UseStaticFiles` "
         "`UseRouting` dan oldin turadi — agar so'ralgan narsa oddiy fayl bo'lsa, "
         "u routing bosqichiga umuman yetib bormaydi.")

    h2(d, "4.1 O'z middleware im")

    code(d, """app.Use(async (context, next) =>
{
    var sw = Stopwatch.StartNew();
    await next();
    sw.Stop();

    logger.LogInformation("{Method} {Path} -> {Status} ({Ms} ms)",
        context.Request.Method,
        context.Request.Path,
        context.Response.StatusCode,
        sw.ElapsedMilliseconds);
});""")

    # ───────────────────────────────────────────
    h1(d, "5. Ikki modelli joylashtirish")

    para(d, "Kestrel ni to'g'ridan-to'g'ri internetga ochish mumkin, lekin odatda uning "
            "oldiga boshqa server qo'yiladi.")

    code(d, """Internet  →  Nginx / IIS  →  Kestrel  →  ASP.NET Core ilovasi""")

    para(d, "Oldindagi server quyidagi vazifalarni oladi: TLS sertifikatlarini "
            "boshqarish, statik fayllarni berish, so'rovlarni bir nechta nusxaga "
            "taqsimlash, keshlash va so'rov sonini cheklash.")

    note(d, "Bu albatta shart emas:",
         "Microsoft hujjati Kestrel ni to'g'ridan-to'g'ri internetga ochishni ham "
         "qo'llab-quvvatlaydi va bu to'liq qo'llab-quvvatlanadigan stsenariy. Lekin "
         "amalda oldinda proxy bo'lgani qulayroq — sertifikat yangilanishi, bir nechta "
         "ilovani bitta portda joylash va statik fayllarni samarali berish shu yerda "
         "hal bo'ladi.")

    h2(d, "5.1 Proxy ortida ishlashda")

    para(d, "Proxy ortida ilova mijozning haqiqiy IP manzilini ko'rmaydi — u proxy "
            "ning manzilini ko'radi. Buni to'g'rilash uchun maxsus middleware kerak:")

    code(d, """app.UseForwardedHeaders(new ForwardedHeadersOptions
{
    ForwardedHeaders = ForwardedHeaders.XForwardedFor
                     | ForwardedHeaders.XForwardedProto
});""")

    para(d, "Bu middleware zanjirning eng boshida turishi kerak, aks holda undan "
            "oldingi middleware lar noto'g'ri IP bilan ishlaydi.")

    # ───────────────────────────────────────────
    h1(d, "6. HTTP versiyalari")

    table(d, ["Versiya", "Asosiy xususiyati"],
          [["HTTP/1.1", "Har bir so'rov navbat bilan; matnli protokol"],
           ["HTTP/2", "Bitta ulanishda parallel so'rovlar; ikkilik format"],
           ["HTTP/3", "TCP o'rniga QUIC (UDP ustida); ulanish tezroq tiklanadi"]],
          widths=[3.4, 12.1])

    code(d, """options.ConfigureEndpointDefaults(listen =>
{
    listen.Protocols = HttpProtocols.Http1AndHttp2AndHttp3;
});""")

    para(d, "HTTP/2 va HTTP/3 brauzerlarda faqat HTTPS bilan ishlaydi.")

    # ───────────────────────────────────────────
    h1(d, "7. Ishlashini tekshirish")

    code(d, """curl -v http://localhost:8080/
curl -I http://localhost:8080/            # faqat sarlavhalar
curl --http2 -I https://localhost:8081/   # HTTP/2 ishlayaptimi""")

    para(d, "Server ishga tushganini, lekin javob bermayotganini tekshirish uchun "
            "avval port haqiqatan tinglanayotganini ko'rish kerak:")

    code(d, """netstat -ano | findstr :8080      # Windows
ss -tlnp | grep 8080              # Linux""")

    # ───────────────────────────────────────────
    h1(d, "8. Xulosa")

    bullets(d, [
        "Web server portni tinglaydi, HTTP so'rovni ajratadi va javob qaytaradi.",
        "Kestrel — ASP.NET Core ning o'rnatilgan serveri; u ilova bilan bitta "
        "jarayonda ishlaydi.",
        "Konteynerda `localhost` emas, `+` yoki `0.0.0.0` tinglanishi kerak.",
        "Middleware zanjiridagi tartib ishlashni belgilaydi — xatolik boshida, "
        "autentifikatsiya avtorizatsiyadan oldin.",
        "Kestrel oldiga Nginx yoki IIS qo'yish sertifikat, keshlash va yuk "
        "taqsimlash vazifalarini ajratadi.",
        "Proxy ortida `UseForwardedHeaders` bo'lmasa, mijozning haqiqiy IP si "
        "ko'rinmaydi.",
        "HTTP/2 va HTTP/3 brauzerlarda faqat HTTPS orqali ishlaydi.",
    ])

    sources(d, [
        ("Kestrel web server in ASP.NET Core",
         "https://learn.microsoft.com/en-us/aspnet/core/fundamentals/servers/kestrel"),
        ("ASP.NET Core Middleware",
         "https://learn.microsoft.com/en-us/aspnet/core/fundamentals/middleware/"),
        ("Configure ASP.NET Core to work with proxy servers and load balancers",
         "https://learn.microsoft.com/en-us/aspnet/core/host-and-deploy/proxy-load-balancer"),
    ])
