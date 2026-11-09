# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "User agent"
CATEGORY = "Web"
TITLE = "User-Agent"
SUBTITLE = "Mijoz o'zini qanday tanishtiradi va unga qanchalik ishonish mumkin"
FILENAME = "User agent.docx"


def build(d):
    h1(d, "1. User-Agent nima")

    para(d, "`User-Agent` — HTTP so'rov sarlavhasi bo'lib, so'rovni yuborgan dastur "
            "o'zi haqida ma'lumot beradi: qaysi brauzer, qaysi versiya, qaysi "
            "operatsion tizim.")

    code(d, """User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64)
            AppleWebKit/537.36 (KHTML, like Gecko)
            Chrome/131.0.0.0 Safari/537.36""")

    para(d, "Bu satr serverga mijozni taniy olish imkonini beradi, lekin unga "
            "ishonish masalasi alohida mavzu.")

    # ───────────────────────────────────────────
    h1(d, "2. Nega bu satr shunchalik g'alati")

    para(d, "Yuqoridagi misolda Chrome o'zini bir vaqtda Mozilla, AppleWebKit, KHTML, "
            "Gecko va Safari deb atayapti. Bu bema'nilikdek ko'rinadi va buning "
            "tarixiy sababi bor.")

    para(d, "1990-yillarda serverlar brauzer imkoniyatlarini `User-Agent` bo'yicha "
            "aniqlardi. Yangi brauzer chiqqanda serverlar uni tanimay, sodda sahifa "
            "qaytarardi. Shuning uchun har bir yangi brauzer o'zini oldingisi deb "
            "tanishtirishni boshladi — shunda eski serverlar uni to'liq versiyali "
            "brauzer deb qabul qilardi.")

    para(d, "Bu zanjir o'ttiz yil davomida yig'ilib, hozirgi tushunarsiz satrni hosil "
            "qilgan.")

    note(d, "Bundan chiqaradigan amaliy xulosa:",
         "`User-Agent` satri aniq ma'lumot berish uchun emas, moslik uchun "
         "shakllangan. Shuning uchun undan brauzer nomini ajratib olish — "
         "ishonchsiz ish. Zamonaviy yondashuv brauzer nomini emas, kerakli "
         "imkoniyat mavjudligini tekshirishdir.")

    # ───────────────────────────────────────────
    h1(d, "3. User-Agent ga ishonib bo'lmaydi")

    para(d, "Bu sarlavhani har qanday mijoz xohlagan qiymat bilan yuborishi mumkin. "
            "Uni tekshirishning hech qanday usuli yo'q:")

    code(d, """curl -H "User-Agent: Mozilla/5.0 (iPhone)" https://example.com/

# .NET da ham xuddi shunday
client.DefaultRequestHeaders.UserAgent.ParseAdd("MyBot/1.0");""")

    bullets(d, [
        "**Xavfsizlik qarorlarini unga tayanib qabul qilmaslik kerak.** Ruxsatni "
        "`User-Agent` bo'yicha berish — soxta himoya.",
        "**Botlarni faqat shu satr bo'yicha bloklab bo'lmaydi** — zararli bot "
        "o'zini oddiy brauzer deb ko'rsatadi.",
        "**Statistika uchun esa yaroqli** — ko'pchilik mijoz haqiqiy qiymat yuboradi.",
    ])

    note(d, "Shunga qaramay men undan voz kechmayman:",
         "U statistika va nosozlikni topish uchun foydali. Masalan \"bu xatolik "
         "faqat ma'lum brauzer versiyasida chiqyapti\" degan xulosani aynan shu "
         "satr orqali chiqarish mumkin. Faqat unga **qaror** qurmaslik kerak.")

    # ───────────────────────────────────────────
    h1(d, "4. ASP.NET Core da o'qish")

    code(d, """app.MapGet("/ua", (HttpContext ctx) =>
{
    var ua = ctx.Request.Headers.UserAgent.ToString();
    return Results.Ok(new { userAgent = ua });
});""")

    code(d, """// Loglarga qo'shish
app.Use(async (ctx, next) =>
{
    using (logger.BeginScope(new Dictionary<string, object>
    {
        ["UserAgent"] = ctx.Request.Headers.UserAgent.ToString(),
        ["RemoteIp"] = ctx.Connection.RemoteIpAddress?.ToString() ?? "-"
    }))
    {
        await next();
    }
});""")

    h2(d, "4.1 Tahlil qilish")

    para(d, "Satrni qo'lda ajratish juda ko'p chegaraviy holatga ega, shuning uchun "
            "tayyor kutubxona ishlatilgani ma'qul:")

    code(d, """dotnet add package UAParser""")

    code(d, """var parser = Parser.GetDefault();
var info = parser.Parse(userAgentString);

info.UA.Family      // Chrome
info.UA.Major       // 131
info.OS.Family      // Windows
info.Device.Family  // Other""")

    # ───────────────────────────────────────────
    h1(d, "5. Chiquvchi so'rovlarda User-Agent")

    para(d, "Mening ilovam boshqa xizmatga so'rov yuborganda ham o'zini tanishtirishi "
            "kerak. Ko'p API lar `User-Agent` bo'lmagan so'rovni rad etadi.")

    code(d, """builder.Services.AddHttpClient("github", client =>
{
    client.BaseAddress = new Uri("https://api.github.com/");
    client.DefaultRequestHeaders.UserAgent.ParseAdd(
        "BooksCatalog/1.2 (+https://books.example.com)");
});""")

    note(d, "Bu kichik odat ko'p muammoni oldini oladi:",
         "Tashqi API ning egasi loglarida mening so'rovlarimni ko'radi. Agar u yerda "
         "ilova nomi va aloqa manzili bo'lsa, muammo chiqqanda ular men bilan "
         "bog'lana oladi. Nomsiz so'rovlar esa odatda birinchi bo'lib bloklanadi.")

    # ───────────────────────────────────────────
    h1(d, "6. Zamonaviy muqobil — Client Hints")

    para(d, "Brauzerlar `User-Agent` satrini asta-sekin soddalashtirmoqda, chunki u "
            "foydalanuvchini kuzatish uchun ham ishlatilgan. O'rniga `Sec-CH-UA` "
            "sarlavhalari taklif qilingan:")

    code(d, """Sec-CH-UA: "Chromium";v="131", "Not_A Brand";v="24"
Sec-CH-UA-Mobile: ?0
Sec-CH-UA-Platform: "Windows\"""")

    para(d, "Bu sarlavhalar tuzilgan va tahlil qilish oson. Qo'shimcha tafsilotlar "
            "server so'raganda beriladi:")

    code(d, """Accept-CH: Sec-CH-UA-Platform-Version, Sec-CH-UA-Full-Version-List""")

    code(d, """app.Use(async (ctx, next) =>
{
    ctx.Response.Headers["Accept-CH"] =
        "Sec-CH-UA-Platform-Version, Sec-CH-UA-Model";
    await next();
});""")

    para(d, "Client Hints hozircha asosan Chromium asosidagi brauzerlarda "
            "qo'llab-quvvatlanadi, shuning uchun `User-Agent` ham saqlanib qolgan.")

    # ───────────────────────────────────────────
    h1(d, "7. Amaliy qo'llanishlar")

    bullets(d, [
        "**Statistika** — qaysi brauzer va qurilmalar ko'p ishlatilayotganini bilish.",
        "**Nosozlikni topish** — xatolik ma'lum platformaga bog'liqmi.",
        "**Bot trafigini ajratish** — qidiruv tizimlari o'zini halol tanishtiradi.",
        "**Rate limiting uchun qo'shimcha belgi** — lekin yagona mezon sifatida emas.",
    ])

    code(d, """// Qidiruv botlarini ajratish (faqat statistika uchun)
private static readonly string[] KnownBots =
    ["googlebot", "bingbot", "yandexbot", "duckduckbot"];

var ua = ctx.Request.Headers.UserAgent.ToString().ToLowerInvariant();
var isBot = KnownBots.Any(bot => ua.Contains(bot));""")

    # ───────────────────────────────────────────
    h1(d, "8. Xulosa")

    bullets(d, [
        "`User-Agent` mijoz haqida ma'lumot beradi, lekin uni istalgan qiymatga "
        "o'zgartirish mumkin.",
        "Satrning g'alati tuzilishi tarixiy moslik ehtiyojidan kelib chiqqan.",
        "Xavfsizlik va ruxsat qarorlarini unga tayanib qabul qilib bo'lmaydi.",
        "Statistika, nosozlikni topish va bot ajratish uchun esa foydali.",
        "Tahlil qilish uchun tayyor kutubxona ishlatish ishonchliroq.",
        "Chiquvchi so'rovlarda o'z ilovamni tanishtirish yaxshi amaliyot.",
        "Client Hints (`Sec-CH-UA`) — tuzilgan va aniqroq muqobil, lekin hali "
        "hamma joyda qo'llab-quvvatlanmaydi.",
    ])

    sources(d, [
        ("User-Agent header — MDN",
         "https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/User-Agent"),
        ("User-Agent Client Hints — MDN",
         "https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Client_hints"),
        ("Browser detection using the user agent — MDN",
         "https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Browser_detection_using_the_user_agent"),
    ])
