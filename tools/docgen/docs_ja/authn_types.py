# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "Authentication ning umumiy turlari"
CATEGORY = "Auth"
TITLE = "Autentifikatsiyaning Umumiy Turlari"
SUBTITLE = "Basic, cookie, token, API key va tashqi provayder"
FILENAME = "Authentication ning umumiy turlari.docx"


def build(d):
    h1(d, "1. Autentifikatsiya omillari")

    para(d, "Hamma usul uch toifadagi dalilga tayanadi:")

    bullets(d, [
        "**Bilgan narsa** — parol, PIN, maxfiy savol.",
        "**Egasi bo'lgan narsa** — telefon, apparat kalit, sertifikat.",
        "**O'zi bo'lgan narsa** — barmoq izi, yuz, ovoz.",
    ])

    para(d, "Ikki **turli** toifadan dalil so'ralsa, bu ko'p faktorli "
            "autentifikatsiya bo'ladi. Ikki parol so'rash MFA emas, chunki "
            "ikkisi ham bitta toifaga tegishli.")

    # ───────────────────────────────────────────
    h1(d, "2. Basic authentication")

    para(d, "Eng oddiy usul: login va parol har bir so'rovda header'da "
            "yuboriladi.")

    code(d, """Authorization: Basic b3J6aWJlazpwYXJvbDEyMw==""")

    para(d, "Qiymat `login:parol` ning base64 kodi. **Shifrlanmagan** — "
            "base64 kodlash, shifrlash emas, uni har kim ochadi. "
            "Shuning uchun Basic faqat TLS ustida ishlatilishi mumkin.")

    bullets(d, [
        "Yutuq: juda sodda, hamma mijoz qo'llab-quvvatlaydi.",
        "Yo'qotish: parol har so'rovda uzatiladi, sessiyani bekor qilish "
        "imkoni yo'q, MFA qo'shib bo'lmaydi, logout tushunchasi yo'q.",
    ])

    para(d, "Men uni faqat ichki servislar orasida yoki tezkor "
            "diagnostika endpoint'ida ishlataman — foydalanuvchilar uchun "
            "emas.")

    # ───────────────────────────────────────────
    h1(d, "3. Cookie asosidagi autentifikatsiya")

    para(d, "Klassik web ilovalar uchun. Foydalanuvchi bir marta login "
            "qiladi, server shifrlangan cookie beradi va brauzer uni har "
            "so'rovda avtomatik yuboradi.")

    code(d, """builder.Services.AddAuthentication(CookieAuthenticationDefaults.AuthenticationScheme)
    .AddCookie(options =>
    {
        options.Cookie.HttpOnly = true;
        options.Cookie.SecurePolicy = CookieSecurePolicy.Always;
        options.Cookie.SameSite = SameSiteMode.Lax;
        options.ExpireTimeSpan = TimeSpan.FromHours(8);
        options.SlidingExpiration = true;
        options.LoginPath = "/login";
    });""")

    code(d, """var claims = new List<Claim>
{
    new(ClaimTypes.NameIdentifier, user.Id.ToString()),
    new(ClaimTypes.Name, user.UserName)
};

var identity = new ClaimsIdentity(claims, CookieAuthenticationDefaults.AuthenticationScheme);
await HttpContext.SignInAsync(new ClaimsPrincipal(identity));""")

    para(d, "Uchta sozlamaning har biri aniq hujumga qarshi turadi:")

    bullets(d, [
        "`HttpOnly` — JavaScript cookie'ni o'qiy olmaydi, ya'ni XSS orqali "
        "o'g'irlanmaydi.",
        "`Secure` — cookie faqat HTTPS orqali yuboriladi.",
        "`SameSite` — boshqa saytdan kelgan so'rovda yuborilmaydi, bu CSRF "
        "ni cheklaydi.",
    ])

    note(d, "CSRF",
         "Cookie avtomatik yuborilgani uchun CSRF xavfi bor. "
         "`SameSite=Lax` ko'p holatni to'sadi, lekin holat o'zgartiradigan "
         "so'rovlarga anti-forgery token ham qo'shish kerak.")

    # ───────────────────────────────────────────
    h1(d, "4. Token (Bearer) asosidagi autentifikatsiya")

    para(d, "API va SPA/mobil mijozlar uchun asosiy usul. Login natijasida "
            "token beriladi va mijoz uni har so'rovda header'ga qo'yadi:")

    code(d, """Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...""")

    code(d, """builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddJwtBearer(options =>
    {
        options.TokenValidationParameters = new TokenValidationParameters
        {
            ValidateIssuer = true,
            ValidIssuer = builder.Configuration["Jwt:Issuer"],
            ValidateAudience = true,
            ValidAudience = builder.Configuration["Jwt:Audience"],
            ValidateLifetime = true,
            ClockSkew = TimeSpan.FromSeconds(30),
            ValidateIssuerSigningKey = true,
            IssuerSigningKey = new SymmetricSecurityKey(key),
            ValidAlgorithms = ["HS256"]
        };
    });""")

    para(d, "Token stateless — server uni tekshirish uchun bazaga "
            "murojaat qilmaydi, imzoni tekshirish yetarli. Bu gorizontal "
            "masshtablash uchun qulay.")

    para(d, "Lekin shu xossaning narxi bor: tokenni **bekor qilib "
            "bo'lmaydi**. Foydalanuvchini bloklasam ham, uning tokeni muddati "
            "tugaguncha ishlashda davom etadi. Shuning uchun amalda:")

    bullets(d, [
        "Access token qisqa muddatli bo'ladi — 5–15 daqiqa.",
        "Refresh token uzoq muddatli, lekin **bazada saqlanadi** — demak "
        "bekor qilinadi.",
        "Kritik harakatlarda foydalanuvchi holati qayta tekshiriladi.",
    ])

    # ───────────────────────────────────────────
    h1(d, "5. API key")

    para(d, "Odamni emas, **ilovani** aniqlash uchun. Server-server "
            "integratsiyalarida qulay:")

    code(d, """X-Api-Key: 7f3c9a1e...""")

    para(d, "Oddiy, lekin cheklovlari bor: muddati yo'q, foydalanuvchi "
            "haqida ma'lumot bermaydi, bitta kalit oqib ketsa hamma "
            "imkoniyat ochiladi. Shuning uchun kalitni muntazam rotatsiya "
            "qilish va har bir mijozga alohida kalit berish kerak.")

    # ───────────────────────────────────────────
    h1(d, "6. Tashqi provayder — OAuth 2.0 va OpenID Connect")

    para(d, "Parolni o'zimda saqlamaslikning eng yaxshi yo'li. Ikki "
            "protokol aralashtiriladi, lekin ularning vazifasi boshqa:")

    bullets(d, [
        "**OAuth 2.0** — avtorizatsiya protokoli: uchinchi tomon ilovasiga "
        "mening nomimdan resursga kirish ruxsatini berish. U \"bu kim\" "
        "degan savolga javob bermaydi.",
        "**OpenID Connect** — OAuth ustidagi autentifikatsiya qatlami. "
        "`id_token` (JWT) qo'shadi va aynan \"bu kim\" degan savolga javob "
        "beradi.",
    ])

    para(d, "Shuning uchun \"OAuth bilan login qilish\" iborasi aslida "
            "noto'g'ri — login uchun OIDC kerak.")

    code(d, """builder.Services.AddAuthentication(options =>
{
    options.DefaultScheme = CookieAuthenticationDefaults.AuthenticationScheme;
    options.DefaultChallengeScheme = "oidc";
})
.AddCookie()
.AddOpenIdConnect("oidc", options =>
{
    options.Authority = "https://login.example.com";
    options.ClientId = builder.Configuration["Oidc:ClientId"];
    options.ClientSecret = builder.Configuration["Oidc:ClientSecret"];
    options.ResponseType = "code";          // Authorization Code + PKCE
    options.UsePkce = true;
    options.Scope.Add("email");
    options.SaveTokens = true;
});""")

    para(d, "Hozirgi tavsiya etilgan oqim — **Authorization Code + PKCE**, "
            "hamma mijoz turi uchun. Implicit flow eskirgan.")

    # ───────────────────────────────────────────
    h1(d, "7. Taqqoslash va tanlov")

    table(d, ["Usul", "Qayerga mos", "Asosiy cheklov"],
          [["Basic", "Ichki servis, diagnostika", "Parol har so'rovda, logout yo'q"],
           ["Cookie", "Server-rendered web ilova", "CSRF, domenlararo murakkab"],
           ["JWT Bearer", "API, SPA, mobil", "Bekor qilish qiyin"],
           ["API key", "Server-server", "Muddati yo'q, odamni aniqlamaydi"],
           ["OIDC", "Foydalanuvchi logini", "Tashqi provayderga bog'liqlik"],
           ["mTLS", "Yuqori ishonch talab qilgan integratsiya",
            "Sertifikat boshqaruvi og'ir"]],
          widths=[2.8, 5.4, 6.3])

    para(d, "O'zim uchun qoida ketma-ketligi shunday. Foydalanuvchilar "
            "uchun — imkoni bo'lsa tashqi provayder (OIDC), chunki parolni "
            "saqlash va himoya qilish eng xavfli mas'uliyat. Buning imkoni "
            "bo'lmasa — o'z parol bilan autentifikatsiya, lekin to'g'ri "
            "hashlash va MFA bilan. API uchun — JWT bearer. Server-server "
            "uchun — API key yoki mTLS.")

    note(d, "Bir ilovada bir nechta sxema",
         "ASP.NET Core bir vaqtda bir nechta autentifikatsiya sxemasini "
         "qo'llab-quvvatlaydi. Masalan web interfeys cookie bilan, API esa "
         "JWT bilan ishlashi mumkin — `[Authorize(AuthenticationSchemes = ...)]` "
         "orqali qaysi biri ishlashi aytiladi.")

    sources(d, [
        ("Overview of ASP.NET Core authentication",
         "https://learn.microsoft.com/en-us/aspnet/core/security/authentication/"),
        ("Cookie authentication without ASP.NET Core Identity",
         "https://learn.microsoft.com/en-us/aspnet/core/security/authentication/cookie"),
        ("OAuth 2.0 for Browser-Based Apps (BCP)",
         "https://datatracker.ietf.org/doc/html/draft-ietf-oauth-browser-based-apps"),
        ("OpenID Connect Core 1.0",
         "https://openid.net/specs/openid-connect-core-1_0.html"),
    ])
