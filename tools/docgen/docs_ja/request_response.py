# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "Request, Response"
CATEGORY = "Web"
TITLE = "HTTP So'rov va Javob"
SUBTITLE = "Xabarlar tuzilishi va metodlar semantikasi"
FILENAME = "Request, Response.docx"


def build(d):
    h1(d, "1. So'rov tuzilishi")

    para(d, "HTTP so'rovi uch qismdan iborat: start qatori, "
            "header'lar va tana. Tana ixtiyoriy va header'lardan "
            "bo'sh qator bilan ajratiladi.")

    code(d, """POST /api/orders HTTP/1.1
Host: api.example.com
Content-Type: application/json
Content-Length: 87
Authorization: Bearer eyJhbGciOiJIUzI1NiJ9...
Accept: application/json
User-Agent: MyApp/2.4

{"customerId":"3f2b...","items":[{"productId":"a1c9...","quantity":2}]}""")

    bullets(d, [
        "**Start qatori** — metod, yo'l va protokol versiyasi.",
        "**Header'lar** — metadata: kontent turi, autentifikatsiya, "
        "qabul qilinadigan formatlar.",
        "**Bo'sh qator** — header'lar tugaganini bildiradi.",
        "**Tana** — yuboriladigan ma'lumot.",
    ])

    para(d, "`Host` header'i HTTP/1.1 da **majburiy**: bitta IP "
            "manzilda bir nechta sayt turishi mumkin, shuning uchun "
            "server qaysi saytga so'rov kelganini shu header'dan "
            "biladi. Bu virtual hosting deb ataladi.")

    # ───────────────────────────────────────────
    h1(d, "2. Javob tuzilishi")

    code(d, """HTTP/1.1 201 Created
Content-Type: application/json; charset=utf-8
Content-Length: 142
Location: /api/orders/7f3c9a1e
Date: Mon, 09 Nov 2026 08:14:22 GMT

{"id":"7f3c9a1e","number":"ORD-1042","total":250000,"status":"new"}""")

    para(d, "Start qatorida status kod va uning matnli izohi "
            "turadi. `Location` header'i yangi yaratilgan resursning "
            "manzilini ko'rsatadi — `201` javobida u bo'lishi kerak.")

    # ───────────────────────────────────────────
    h1(d, "3. Metodlar semantikasi")

    table(d, ["Metod", "Xavfsiz", "Idempotent", "Tana"],
          [["`GET`", "Ha", "Ha", "Yo'q"],
           ["`HEAD`", "Ha", "Ha", "Yo'q"],
           ["`OPTIONS`", "Ha", "Ha", "Yo'q"],
           ["`POST`", "Yo'q", "Yo'q", "Ha"],
           ["`PUT`", "Yo'q", "Ha", "Ha"],
           ["`PATCH`", "Yo'q", "Yo'q", "Ha"],
           ["`DELETE`", "Yo'q", "Ha", "Yo'q"]],
          widths=[3.0, 3.6, 3.9, 4.0])

    para(d, "Ikki tushunchani ajratish muhim:")

    bullets(d, [
        "**Xavfsiz (safe)** — server holatini o'zgartirmaydi. "
        "Shuning uchun brauzer va qidiruv tizimi ularni erkin "
        "chaqirishi mumkin.",
        "**Idempotent** — bir xil so'rovni bir necha marta "
        "yuborish bir marta yuborish bilan **bir xil natija** "
        "beradi.",
    ])

    para(d, "Bu nafaqat nazariya: amalda idempotentlik **qayta "
            "urinish** mumkinligini belgilaydi. Tarmoq xatosi "
            "bo'lganda `GET`, `PUT` va `DELETE` ni xotirjam "
            "qayta yuborish mumkin. `POST` ni esa yo'q — ikki "
            "marta to'lov o'tib ketishi mumkin.")

    note(d, "POST ni xavfsiz qayta urinish",
         "Kerak bo'lsa **idempotency key** ishlatiladi: mijoz "
         "so'rovga unikal ID qo'shadi, server shu ID ni eslab "
         "qoladi va takroriy so'rovda yangi operatsiya "
         "bajarmasdan oldingi natijani qaytaradi.")

    h2(d, "PUT va PATCH farqi")

    code(d, """# PUT — resursni TO'LIQ almashtirish
PUT /api/customers/42
{"name":"Orzibek","phone":"+998901112233","email":"a@b.uz"}

# PATCH — faqat ko'rsatilgan maydonlarni o'zgartirish
PATCH /api/customers/42
{"phone":"+998935556677"}""")

    para(d, "`PUT` da yuborilmagan maydon `null` bo'lishi kerak — "
            "chunki semantika \"butun resursni shu bilan "
            "almashtir\". Ko'p API bu qoidani buzadi va `PUT` ni "
            "`PATCH` kabi ishlatadi; bu chalkashlik keltiradi, "
            "shuning uchun qaysi semantika ishlatilayotganini "
            "hujjatda aniq yozish kerak.")

    # ───────────────────────────────────────────
    h1(d, "4. Status kodlar guruhlari")

    bullets(d, [
        "**1xx** — ma'lumot. `100 Continue`, `101 Switching "
        "Protocols` (WebSocket upgrade).",
        "**2xx** — muvaffaqiyat. `200`, `201`, `202`, `204`.",
        "**3xx** — yo'naltirish. `301` (doimiy), `302` "
        "(vaqtinchalik), `304 Not Modified` (kesh).",
        "**4xx** — mijoz xatosi. `400`, `401`, `403`, `404`, "
        "`409`, `422`, `429`.",
        "**5xx** — server xatosi. `500`, `502`, `503`, `504`.",
    ])

    para(d, "Guruh raqamining amaliy ma'nosi: `4xx` — \"so'rovni "
            "o'zgartirmasdan qayta yuborish foydasiz\", `5xx` — "
            "\"keyinroq qayta urinish mantiqiy\". Shuning uchun "
            "retry mantiqi odatda faqat `5xx` va `429` da "
            "ishlaydi.")

    # ───────────────────────────────────────────
    h1(d, "5. ASP.NET Core da so'rov va javob")

    code(d, """app.Use(async (context, next) =>
{
    var request = context.Request;

    var method = request.Method;
    var path = request.Path;
    var query = request.Query["page"];
    var header = request.Headers.UserAgent.ToString();
    var scheme = request.Scheme;          // http / https
    var host = request.Host.Value;

    await next(context);

    var statusCode = context.Response.StatusCode;
});""")

    h2(d, "Tanani o'qish — bir martalik oqim")

    code(d, """// So'rov tanasi OQIM — bir marta o'qiladi
app.Use(async (context, next) =>
{
    context.Request.EnableBuffering();      // qayta o'qishga ruxsat

    using var reader = new StreamReader(context.Request.Body, leaveOpen: true);
    var body = await reader.ReadToEndAsync();
    context.Request.Body.Position = 0;      // keyingi middleware uchun qaytarish

    await next(context);
});""")

    para(d, "`EnableBuffering()` bo'lmasa, middleware tanani o'qib "
            "bo'lgandan keyin controller bo'sh tana oladi. Bu "
            "log yozadigan middleware yozganda eng ko'p "
            "uchraydigan muammo.")

    note(d, "Diqqat",
         "Bufferlash butun tanani xotiraga yoki vaqtinchalik "
         "faylga oladi. Katta fayl yuklanadigan endpoint'larda "
         "buni yoqmaslik kerak, aks holda xotira tez to'lib "
         "ketadi.")

    h2(d, "Javob boshlangandan keyin o'zgartirib bo'lmaydi")

    code(d, """if (!context.Response.HasStarted)
{
    context.Response.StatusCode = StatusCodes.Status503ServiceUnavailable;
    context.Response.Headers.RetryAfter = "30";
}""")

    para(d, "Birinchi bayt mijozga ketgandan keyin header va "
            "status kodni o'zgartirish mumkin emas — "
            "`InvalidOperationException` chiqadi. Shuning uchun "
            "xato boshqaruvchi middleware'da `HasStarted` ni "
            "tekshirish kerak.")

    # ───────────────────────────────────────────
    h1(d, "6. HTTP versiyalari")

    table(d, ["Versiya", "Asosiy o'zgarish"],
          [["HTTP/1.0", "Har so'rov uchun yangi ulanish"],
           ["HTTP/1.1", "Keep-alive, `Host` majburiy, chunked transfer"],
           ["HTTP/2", "Binar format, multiplexing, header siqish, server push"],
           ["HTTP/3", "QUIC (UDP) ustida, head-of-line blocking yo'q"]],
          widths=[3.4, 11.1])

    para(d, "HTTP/1.1 da bitta ulanishda so'rovlar ketma-ket "
            "ketadi, shuning uchun brauzer bir vaqtda 6 ta ulanish "
            "ochadi. HTTP/2 da bitta ulanishda ko'p so'rov "
            "parallel ketadi (multiplexing) — bu ko'p kichik "
            "fayl yuklashda sezilarli tezlik beradi.")

    para(d, "Backend ishlab chiquvchi uchun amaliy ta'siri: "
            "HTTP/2 da \"fayllarni birlashtirish\" (bundling) "
            "optimizatsiyasi ma'nosini yo'qotadi, va gRPC aynan "
            "HTTP/2 ga tayanadi.")

    sources(d, [
        ("HTTP Messages — MDN",
         "https://developer.mozilla.org/en-US/docs/Web/HTTP/Messages"),
        ("HTTP request methods — MDN",
         "https://developer.mozilla.org/en-US/docs/Web/HTTP/Methods"),
        ("HttpRequest Class — ASP.NET Core",
         "https://learn.microsoft.com/en-us/dotnet/api/microsoft.aspnetcore.http.httprequest"),
        ("RFC 9110 — HTTP Semantics",
         "https://datatracker.ietf.org/doc/html/rfc9110"),
    ])
