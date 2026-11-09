# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "Specific headers (Authorization, Content-Type, Content-Length, Accept)"
CATEGORY = "Web"
TITLE = "Muhim HTTP Header'lar"
SUBTITLE = "Authorization, Content-Type, Content-Length va Accept"
FILENAME = "Specific headers (Authorization, Content-Type, Content-Length, Accept).docx"


def build(d):
    h1(d, "1. Authorization")

    para(d, "Mijozning kimligini yoki huquqini tasdiqlovchi "
            "ma'lumot. Format: sxema nomi va undan keyin "
            "ma'lumot.")

    code(d, """Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Authorization: Basic b3J6aWJlazpwYXJvbDEyMw==
Authorization: ApiKey 7f3c9a1e8b24d6f0""")

    bullets(d, [
        "**Bearer** — token egasi kim bo'lsa, u ruxsatga ega. "
        "JWT va OAuth access token'lar shu sxemada yuboriladi.",
        "**Basic** — `login:parol` ning base64 kodi. Bu "
        "**shifrlash emas**, shuning uchun faqat TLS ustida.",
        "**Digest, Negotiate, mTLS** — kamroq uchraydigan, lekin "
        "ichki tizimlarda ishlatiladigan sxemalar.",
    ])

    code(d, """// ASP.NET Core da o'qish
var header = context.Request.Headers.Authorization.ToString();

if (AuthenticationHeaderValue.TryParse(header, out var parsed)
    && parsed.Scheme.Equals("Bearer", StringComparison.OrdinalIgnoreCase))
{
    var token = parsed.Parameter;
}""")

    note(d, "Xavfsizlik",
         "`Authorization` header'i **hech qachon log'ga "
         "tushmasligi kerak**. Log'da token bo'lsa, log'ga kirish "
         "huquqi bor har kim foydalanuvchi nomidan ishlay oladi. "
         "Shuning uchun log middleware'ida bu header'ni "
         "maskalayman.")

    para(d, "Yana bir detal: proxy orqali o'tganda bu header "
            "ba'zan tashlab yuboriladi. Agar autentifikatsiya "
            "mahalliyda ishlab, production'da ishlamasa, "
            "birinchi tekshiradigan narsam shu.")

    # ───────────────────────────────────────────
    h1(d, "2. Content-Type")

    para(d, "Yuborilayotgan tananing **formati**. So'rovda ham, "
            "javobda ham bo'ladi.")

    code(d, """Content-Type: application/json; charset=utf-8
Content-Type: application/x-www-form-urlencoded
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary7MA4YWx
Content-Type: text/plain; charset=utf-8
Content-Type: application/pdf
Content-Type: application/problem+json""")

    para(d, "Server bu header'ga qarab tanani qanday parse "
            "qilishni hal qiladi. Noto'g'ri yoki yo'q bo'lsa — "
            "`415 Unsupported Media Type` qaytadi.")

    para(d, "`application/problem+json` — xato javoblari uchun "
            "standart tur (RFC 9457). ASP.NET Core "
            "`ProblemDetails` qaytarganda aynan shuni ishlatadi, "
            "shuning uchun mijoz javob xato ekanini "
            "`Content-Type` dan ham biladi.")

    h2(d, "charset nima uchun muhim")

    para(d, "Kodlash ko'rsatilmasa, mijoz taxmin qilishga majbur "
            "bo'ladi va kirill yoki o'zbek alifbosidagi belgilar "
            "buzilib ketadi. Shuning uchun `charset=utf-8` ni "
            "aniq ko'rsatish kerak.")

    h2(d, "X-Content-Type-Options")

    code(d, """app.Use(async (context, next) =>
{
    context.Response.Headers["X-Content-Type-Options"] = "nosniff";
    await next(context);
});""")

    para(d, "Brauzerlar ba'zan `Content-Type` ga ishonmasdan, "
            "tana mazmunidan turni taxmin qiladi (MIME sniffing). "
            "Bu zaiflik: `.txt` deb yuborilgan fayl HTML sifatida "
            "bajarilishi mumkin. `nosniff` buni to'xtatadi.")

    # ───────────────────────────────────────────
    h1(d, "3. Content-Length va chunked transfer")

    para(d, "`Content-Length` tananing **baytdagi** hajmini "
            "bildiradi. Qabul qiluvchi shu qiymatga qarab "
            "qancha o'qishni biladi.")

    code(d, """Content-Length: 348""")

    para(d, "Agar hajm oldindan ma'lum bo'lmasa (masalan javob "
            "oqim bo'lib generatsiya qilinsa), `Content-Length` "
            "o'rniga chunked kodlash ishlatiladi:")

    code(d, """Transfer-Encoding: chunked

1a
{"id":1,"name":"Birinchi"}
1b
{"id":2,"name":"Ikkinchi"}
0
""")

    para(d, "Har bir bo'lak oldidan uning hajmi o'n oltilik "
            "sanoqda yoziladi, `0` esa oxirini bildiradi.")

    bullets(d, [
        "`Content-Length` bo'lsa — mijoz progress ko'rsatishi "
        "mumkin, chunki umumiy hajm ma'lum.",
        "Chunked bo'lsa — javobni darhol boshlash mumkin, lekin "
        "progress noma'lum.",
    ])

    note(d, "Amaliy xato",
         "Katta fayl qaytaradigan endpoint'da butun faylni "
         "xotiraga o'qib `Content-Length` qo'yish — xotira "
         "muammosi manbai. To'g'ri yechim: oqimni "
         "to'g'ridan-to'g'ri uzatish va chunked kodlashga ruxsat "
         "berish.")

    code(d, """// Oqim sifatida qaytarish — xotiraga to'liq o'qilmaydi
return File(stream, "application/pdf", "hisobot.pdf", enableRangeProcessing: true);""")

    para(d, "`enableRangeProcessing: true` qo'shilsa, mijoz "
            "faylning bir qismini so'rashi mumkin "
            "(`Range: bytes=0-1023`) — bu video oqimi va "
            "uzilgan yuklashni davom ettirish uchun kerak.")

    # ───────────────────────────────────────────
    h1(d, "4. Accept va content negotiation")

    para(d, "`Accept` — mijoz **qanday formatni qabul qila "
            "olishini** bildiradi. Server mavjud variantlardan "
            "mosini tanlaydi.")

    code(d, """Accept: application/json
Accept: application/json, text/plain;q=0.9, */*;q=0.1
Accept: application/xml;q=0.9, application/json;q=1.0""")

    para(d, "`q` — sifat ko'rsatkichi, 0 dan 1 gacha (standart "
            "1.0). Yuqoridagi uchinchi misolda mijoz JSON ni "
            "afzal ko'radi, lekin XML ham qabul qiladi.")

    code(d, """builder.Services.AddControllers(options =>
{
    options.RespectBrowserAcceptHeader = true;
    options.ReturnHttpNotAcceptable = true;      // 406 qaytaradi
})
.AddXmlSerializerFormatters();""")

    para(d, "`ReturnHttpNotAcceptable = true` bo'lsa, so'ralgan "
            "formatni bera olmasa server `406 Not Acceptable` "
            "qaytaradi. Standart holatda esa u mavjud formatni "
            "baribir yuboradi — bu ba'zan qulay, lekin "
            "standartga mos emas.")

    h2(d, "Accept oilasidagi boshqa header'lar")

    table(d, ["Header", "Nima so'raydi"],
          [["`Accept`", "Kontent turi (JSON, XML, HTML)"],
           ["`Accept-Language`", "Til (`uz-UZ`, `ru-RU`, `en-US`)"],
           ["`Accept-Encoding`", "Siqish usuli (`gzip`, `br`, `deflate`)"],
           ["`Accept-Charset`", "Belgilar kodlashi (hozir kam ishlatiladi)"]],
          widths=[4.6, 9.9])

    code(d, """// Accept-Language bo'yicha lokalizatsiya
builder.Services.AddRequestLocalization(options =>
{
    options.SetDefaultCulture("uz-UZ")
           .AddSupportedCultures("uz-UZ", "ru-RU", "en-US")
           .AddSupportedUICultures("uz-UZ", "ru-RU", "en-US");
});

app.UseRequestLocalization();""")

    # ───────────────────────────────────────────
    h1(d, "5. Vary — kesh uchun muhim")

    para(d, "Agar javob `Accept` yoki `Accept-Language` ga qarab "
            "o'zgarsa, keshlovchi proxy buni bilishi kerak. Aks "
            "holda u JSON javobni keshlab, XML so'ragan mijozga "
            "ham shu javobni beradi.")

    code(d, """Vary: Accept, Accept-Language, Accept-Encoding""")

    para(d, "`Vary` ni qo'shmaslik — keshlash bilan bog'liq eng "
            "nozik xatolardan biri, chunki u faqat CDN yoki proxy "
            "orqasida sezilarli bo'ladi va mahalliyda hech qachon "
            "takrorlanmaydi.")

    # ───────────────────────────────────────────
    h1(d, "6. Custom header'lar")

    code(d, """X-Correlation-Id: 7f3c9a1e-8b24-4d6f-9012-3e4f5a6b7c8d
X-Request-Id: ...
X-Api-Version: 2
X-RateLimit-Remaining: 47
Retry-After: 30""")

    para(d, "`X-` prefiksi rasmiy jihatdan eskirgan (RFC 6648), "
            "lekin amalda hali keng ishlatiladi. Yangi header "
            "nomini tanlaganda prefikssiz, aniq nom berishni "
            "tavsiya qilaman.")

    para(d, "**Correlation ID** ni alohida ta'kidlayman: bu bitta "
            "so'rovni bir nechta servis log'ida bog'lash uchun "
            "kerak. Foydalanuvchi \"xato chiqdi\" deganda shu ID "
            "bilan butun so'rov yo'lini ko'rish mumkin:")

    code(d, """app.Use(async (context, next) =>
{
    var correlationId = context.Request.Headers["X-Correlation-Id"].FirstOrDefault()
                        ?? context.TraceIdentifier;

    context.Response.Headers["X-Correlation-Id"] = correlationId;

    using (logger.BeginScope("{CorrelationId}", correlationId))
        await next(context);
});""")

    note(d, "CORS bilan bog'liq detal",
         "Brauzerdan custom header yuborish uchun server uni "
         "`Access-Control-Allow-Headers` da ruxsat berishi kerak. "
         "Javobdagi custom header'ni JavaScript o'qishi uchun esa "
         "`Access-Control-Expose-Headers` kerak — bu ko'p "
         "e'tibordan chetda qoladi.")

    sources(d, [
        ("HTTP headers — MDN",
         "https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers"),
        ("Content negotiation in ASP.NET Core",
         "https://learn.microsoft.com/en-us/aspnet/core/web-api/advanced/formatting"),
        ("RFC 9110 — HTTP Semantics",
         "https://datatracker.ietf.org/doc/html/rfc9110"),
        ("Globalization and localization in ASP.NET Core",
         "https://learn.microsoft.com/en-us/aspnet/core/fundamentals/localization"),
    ])
