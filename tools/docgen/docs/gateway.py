# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "Gateway"
CATEGORY = "Web"
TITLE = "API Gateway"
SUBTITLE = "Mikroservislar oldidagi yagona kirish nuqtasi"
FILENAME = "Gateway.docx"


def build(d):
    h1(d, "1. Gateway qanday muammoni hal qiladi")

    para(d, "Tizim bir nechta mustaqil xizmatdan iborat bo'lganda mijoz ularning har "
            "biri bilan alohida gaplashishi kerak bo'ladi. Bu bir nechta noqulaylik "
            "tug'diradi.")

    bullets(d, [
        "Mijoz har bir xizmatning manzilini bilishi kerak.",
        "Autentifikatsiya har bir xizmatda alohida amalga oshiriladi.",
        "Bitta sahifani ko'rsatish uchun mijoz beshta so'rov yuborishi mumkin.",
        "Xizmatlar ichki tuzilmasi o'zgarsa, mijoz ham o'zgarishi kerak.",
    ])

    para(d, "API Gateway bu muammolarni yagona kirish nuqtasini qo'yish orqali hal "
            "qiladi. Mijoz faqat gateway bilan gaplashadi, u esa so'rovni kerakli "
            "xizmatga yo'naltiradi.")

    code(d, """                        ┌──►  Buyurtmalar xizmati
Mijoz  ──►  [Gateway]  ─┼──►  Katalog xizmati
                        ├──►  To'lov xizmati
                        └──►  Bildirishnoma xizmati""")

    # ───────────────────────────────────────────
    h1(d, "2. Reverse proxy dan farqi")

    para(d, "Gateway texnik jihatdan reverse proxy ustiga quriladi, lekin uning "
            "vazifalari kengroq. Farqni shunday ifodalash mumkin: reverse proxy "
            "tarmoq darajasida ishlaydi, gateway esa API darajasida.")

    table(d, ["Vazifa", "Reverse proxy", "API Gateway"],
          [["So'rovni yo'naltirish", "Ha", "Ha"],
           ["TLS tugatish", "Ha", "Ha"],
           ["Yuk taqsimlash", "Ha", "Ha"],
           ["Autentifikatsiya va avtorizatsiya", "Cheklangan", "Ha"],
           ["So'rov va javobni o'zgartirish", "Cheklangan", "Ha"],
           ["Bir nechta chaqiruvni birlashtirish", "Yo'q", "Ha"],
           ["Protokol almashtirish", "Yo'q", "Ha"],
           ["Mijozga qarab versiyalash", "Yo'q", "Ha"]],
          widths=[5.6, 4.9, 5.0])

    note(d, "Chegarani men shunday tortaman:",
         "Agar oraliq qatlam so'rovning **mazmuni** bilan ishlayotgan bo'lsa — bu "
         "gateway. Agar u faqat so'rovni bir joydan boshqasiga uzatayotgan bo'lsa — "
         "bu reverse proxy. Amalda esa ko'p loyihada bitta Nginx ikkala rolni ham "
         "bajaradi va buni alohida atash shart emas.")

    # ───────────────────────────────────────────
    h1(d, "3. Gateway ning asosiy vazifalari")

    h2(d, "3.1 Marshrutlash")

    code(d, """/api/orders/**    →  orders-service:8080
/api/catalog/**   →  catalog-service:8080
/api/payments/**  →  payments-service:8080""")

    h2(d, "3.2 Markazlashgan autentifikatsiya")

    para(d, "Gateway tokenni bir marta tekshiradi va orqadagi xizmatlarga "
            "foydalanuvchi ma'lumotini ishonchli shaklda uzatadi. Shunda har bir "
            "xizmat token tekshirish kodini takrorlamaydi.")

    code(d, """// Gateway da
app.Use(async (ctx, next) =>
{
    var user = ctx.User;
    if (user.Identity?.IsAuthenticated == true)
    {
        ctx.Request.Headers["X-User-Id"] =
            user.FindFirst(ClaimTypes.NameIdentifier)?.Value;
        ctx.Request.Headers["X-User-Roles"] =
            string.Join(',', user.FindAll(ClaimTypes.Role).Select(c => c.Value));
    }
    await next();
});""")

    note(d, "Bu yerda xavfsizlik sharti bor:",
         "Orqadagi xizmatlar `X-User-Id` sarlavhasiga ishonadi. Demak ular "
         "to'g'ridan-to'g'ri murojaat qilinadigan bo'lmasligi kerak — aks holda "
         "har kim bu sarlavhani o'zi yuborib, istalgan foydalanuvchi nomidan ish "
         "qila oladi. Ichki xizmatlar faqat ichki tarmoqda ko'rinishi shart.")

    h2(d, "3.3 So'rov sonini cheklash")

    code(d, """builder.Services.AddRateLimiter(options =>
{
    options.AddFixedWindowLimiter("per-user", limiter =>
    {
        limiter.PermitLimit = 100;
        limiter.Window = TimeSpan.FromMinutes(1);
        limiter.QueueLimit = 0;
    });

    options.RejectionStatusCode = StatusCodes.Status429TooManyRequests;
});

app.UseRateLimiter();""")

    h2(d, "3.4 Agregatsiya")

    para(d, "Gateway bir nechta xizmatdan ma'lumot yig'ib, mijozga bitta javob "
            "qaytarishi mumkin:")

    code(d, """app.MapGet("/api/orders/{id:int}/full", async (
    int id, IHttpClientFactory factory, CancellationToken ct) =>
{
    var orders = factory.CreateClient("orders");
    var catalog = factory.CreateClient("catalog");

    var order = await orders.GetFromJsonAsync<OrderDto>($"/orders/{id}", ct);
    if (order is null) return Results.NotFound();

    var itemsTask = catalog.GetFromJsonAsync<List<ProductDto>>(
        $"/products?ids={string.Join(',', order.ProductIds)}", ct);

    return Results.Ok(new { order, products = await itemsTask });
});""")

    note(d, "Agregatsiya bilan ehtiyot bo'lish kerak:",
         "U mijoz uchun qulay, lekin gateway ga biznes mantiq olib kiradi. Agar "
         "bunday endpoint lar ko'payib ketsa, gateway o'zi bir xizmatga aylanadi "
         "va uni o'zgartirmasdan hech narsa qilib bo'lmaydi. Men agregatsiyani "
         "faqat haqiqatan ko'p so'rov tejaydigan joylarda ishlataman.")

    h2(d, "3.5 Chidamlilik")

    code(d, """builder.Services.AddHttpClient("catalog")
    .AddStandardResilienceHandler(options =>
    {
        options.Retry.MaxRetryAttempts = 3;
        options.CircuitBreaker.FailureRatio = 0.5;
        options.AttemptTimeout.Timeout = TimeSpan.FromSeconds(5);
    });""")

    para(d, "Circuit breaker bir xizmat ishlamay qolganda unga so'rov yuborishni "
            "vaqtincha to'xtatadi. Bu nosozlikning butun tizimga tarqalishini "
            "oldini oladi.")

    # ───────────────────────────────────────────
    h1(d, "4. BFF — har mijozga o'z gateway i")

    para(d, "Backend for Frontend naqshida har bir mijoz turi uchun alohida gateway "
            "quriladi:")

    code(d, """Web brauzer   →  [Web BFF]    ─┐
Mobil ilova   →  [Mobile BFF] ─┼──►  Xizmatlar
Hamkor API    →  [Partner GW]  ─┘""")

    para(d, "Sababi — turli mijozlarning ehtiyoji turlicha. Mobil ilovaga kichikroq "
            "javob va kamroq so'rov kerak, web ga esa to'liqroq ma'lumot. Bitta "
            "umumiy gateway ikkalasiga ham murosaga kelgan yechim beradi.")

    note(d, "Bu naqshning narxi ham bor:",
         "Har bir BFF — alohida joylashtiriladigan, kuzatiladigan va yangilanadigan "
         "xizmat. Kichik jamoada bu yuk og'irlik qiladi. Men buni faqat mijoz "
         "turlari haqiqatan keskin farq qilganda ishlataman.")

    # ───────────────────────────────────────────
    h1(d, "5. Gateway ning xavfi")

    bullets(d, [
        "**Yagona nosozlik nuqtasi** — gateway ishlamasa, butun tizim ko'rinmay "
        "qoladi. Shuning uchun u bir nechta nusxada ishlashi kerak.",
        "**Unumdorlik to'siqlari** — barcha trafik undan o'tadi.",
        "**Mantiq to'planib qolishi** — har bir yangi talab gateway ga qo'shilsa, "
        "u asta-sekin monolitga aylanadi.",
        "**Joylashtirish bog'liqligi** — gateway ni yangilash barcha xizmatlarga "
        "ta'sir qiladi.",
    ])

    note(d, "Eng muhim maslahat:",
         "Gateway ni iloji boricha \"ahmoq\" tutish kerak — u faqat yo'naltirish, "
         "autentifikatsiya va cheklash bilan shug'ullansin. Biznes qoidalari "
         "xizmatlarda qolsin. Bu qoidaga amal qilinmasa, gateway eng qiyin "
         "o'zgartiriladigan komponentga aylanadi.")

    # ───────────────────────────────────────────
    h1(d, "6. Mavjud yechimlar")

    table(d, ["Yechim", "Xususiyati"],
          [["YARP", "`.NET` kutubxonasi; o'z gateway ini yozish uchun"],
           ["Nginx", "Yengil, tez; murakkab mantiq uchun qulay emas"],
           ["Kong", "Plaginlar tizimi, keng imkoniyatlar"],
           ["Traefik", "Konteynerlarni avtomatik topadi"],
           ["Bulutli yechimlar", "Boshqarish talab qilmaydi, lekin provayderga bog'laydi"]],
          widths=[4.2, 11.3])

    para(d, "`.NET` loyihalari uchun YARP tabiiy tanlov bo'ladi — u bir xil "
            "ekotizimda, kodda sozlanadi va mavjud middleware lar bilan ishlaydi.")

    # ───────────────────────────────────────────
    h1(d, "7. Xulosa")

    bullets(d, [
        "Gateway — mikroservislar oldidagi yagona kirish nuqtasi.",
        "Reverse proxy tarmoq darajasida, gateway API darajasida ishlaydi.",
        "Asosiy vazifalari: marshrutlash, markazlashgan autentifikatsiya, so'rov "
        "sonini cheklash, agregatsiya, chidamlilik.",
        "Ichki xizmatlar gateway dan o'tmagan so'rovni qabul qilmasligi kerak.",
        "BFF naqshi har bir mijoz turi uchun alohida gateway quradi.",
        "Gateway yagona nosozlik nuqtasi — u bir nechta nusxada ishlashi lozim.",
        "Biznes mantiqni gateway ga ko'chirmaslik kerak, aks holda u monolitga "
        "aylanadi.",
    ])

    sources(d, [
        ("Gateway Routing pattern — Azure Architecture Center",
         "https://learn.microsoft.com/en-us/azure/architecture/patterns/gateway-routing"),
        ("Gateway Aggregation pattern — Azure Architecture Center",
         "https://learn.microsoft.com/en-us/azure/architecture/patterns/gateway-aggregation"),
        ("Backends for Frontends pattern",
         "https://learn.microsoft.com/en-us/azure/architecture/patterns/backends-for-frontends"),
        ("YARP — Yet Another Reverse Proxy",
         "https://microsoft.github.io/reverse-proxy/"),
    ])
