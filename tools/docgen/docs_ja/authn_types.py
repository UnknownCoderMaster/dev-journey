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

    # ───────────────────────────────────────────
    h1(d, "8. Amaliyotdan: bitta tizimda ikki mustaqil autentifikatsiya")

    para(d, "Ish joyimdagi MAD ERP tizimida 7-bo'limdagi jadvaldan bitta usul "
            "tanlanmagan — ikkita butunlay mustaqil autentifikatsiya tizimi yonma-yon "
            "ishlaydi. Buni birinchi ko'rganimda ortiqcha murakkablik deb o'yladim, "
            "sababini tushungach esa fikrim o'zgardi.")

    h2(d, "8.1 Nega ikkita")

    para(d, "Tizimda ikki xil foydalanuvchi bor va ularning ehtiyojlari to'liq boshqa:")

    table(d, ["", "Xodimlar", "Tashqi mijozlar"],
          [["Kim", "Muassasa xodimlari", "Fuqarolar, yuridik shaxslar"],
           ["Qayerdan", "Tashkilot ichidan", "Internetdan, mobil ilovadan"],
           ["Kim yaratadi", "Administrator", "O'zini o'zi ro'yxatdan o'tkazadi"],
           ["Shaxsni kim tasdiqlaydi", "Tashkilot", "Davlat identifikatsiya tizimi"],
           ["Yechim", "Keycloak (OIDC)", "O'z IdP si + OneID"]],
          widths=[4.0, 5.5, 6.0])

    para(d, "Ya'ni farq texnik emas, tashkiliy. Xodimni ishga olish va uning huquqini "
            "belgilash — administratorning ishi. Fuqaro esa o'zini o'zi ro'yxatdan "
            "o'tkazadi va uning shaxsini davlat tizimi tasdiqlaydi. Bitta "
            "autentifikatsiya oqimiga ikkisini joylashtirish — ikki xil biznes "
            "jarayonini bitta kodga tiqishtirish bo'lardi.")

    h2(d, "8.2 Xodimlar — 6-bo'limdagi OIDC")

    para(d, "Bu yo'l standart: Keycloak identifikatsiya provayderi sifatida ishlaydi, "
            "har bir servis o'z mijozini unda ro'yxatdan o'tkazadi, token esa JWT "
            "bearer sifatida tekshiriladi. 4-bo'limda aytilgan hamma narsa shu yerda "
            "ishlaydi.")

    h2(d, "8.3 Tashqi mijozlar — o'z IdP si va RS256")

    para(d, "Ikkinchi oqimda Keycloak umuman qatnashmaydi. Bitta servis o'zi "
            "identifikatsiya provayderi bo'lib ishlaydi va RS256 bilan imzolangan "
            "token chiqaradi. Shaxsni tasdiqlash esa OneID — davlat tizimi — orqali "
            "bajariladi.")

    para(d, "3-bo'limdagi cookie va 4-bo'limdagi token yondashuvlari bu yerda "
            "aralashgan. Token cookie da ham uzatilishi mumkin:")

    code(d, """OnMessageReceived = ctx =>
{
    if (string.IsNullOrEmpty(ctx.Token))
    {
        var cookie = ctx.Request.Cookies[AuthCookieNames.PersonAccessToken];
        if (!string.IsNullOrEmpty(cookie))
            ctx.Token = cookie;
    }
    return Task.CompletedTask;
}""", caption="PersonAuthExtensions.cs")

    para(d, "Mantiq oddiy: mobil ilova tokenni `Authorization` sarlavhasida yuboradi, "
            "veb interfeys esa `HttpOnly` cookie da. Server ikkisini ham qabul qiladi. "
            "Bu 3-bo'limda aytilgan cookie ning XSS dan himoyasini brauzer uchun "
            "saqlaydi, mobil mijoz uchun esa 4-bo'limdagi oddiy sarlavha qoladi.")

    h2(d, "8.4 Tokendan keyingi tekshiruv")

    para(d, "Imzo tasdiqlangandan keyin yana ikki tekshiruv bajariladi:")

    code(d, """OnTokenValidated = async ctx =>
{
    var userType = ctx.Principal?.FindFirst(PersonClaims.UserType)?.Value;
    if (!string.Equals(userType, PersonClaims.UserTypePerson, StringComparison.OrdinalIgnoreCase))
    {
        ctx.Fail("user_type is not person");
        return;
    }

    // Logout/revoke qilingan sessiya bo'lsa — access token amal qilmasin.
    await TokenRevocationCheck.EnforceAsync(
        ctx, PersonAuthRedisKeys.RevokedPrefix, JwtRegisteredClaimNames.Jti);
}""")

    bullets(d, [
        "**Birinchisi** — tokendagi foydalanuvchi turi kutilganiga mos kelishini "
        "tekshiradi. Ya'ni xodim tokeni bilan fuqarolar endpoint iga kirib bo'lmaydi, "
        "garchi ikkala token ham texnik jihatdan to'g'ri bo'lsa.",
        "**Ikkinchisi** — 4-bo'limda aytilgan tokenni bekor qilib bo'lmaslik "
        "muammosini yumshatadi. Chiqish qilingan sessiya identifikatori Redis ga "
        "yoziladi va har so'rovda tekshiriladi.",
    ])

    note(d, "Bu yerda meni o'ylantirgan qaror:",
         "Redis yo'q yoki xato bersa, tekshiruv so'rovni **o'tkazib yuboradi** va "
         "faqat ogohlantirish log yozadi. Men avval buni xato deb o'yladim — "
         "xavfsizlik tekshiruvi yiqilganda rad etish kerak emasmi? Keyin tushundim: "
         "agar rad etilsa, Redis o'chganda hech kim tizimga kira olmay qolardi. "
         "Qora ro'yxat esa qo'shimcha qatlam, uning vazifasi bazadagi haqiqiy "
         "bekor qilishni **tezroq** kuchga kiritish. Ya'ni ongli murosa: Redis "
         "tushgan oynada bekor qilingan token muddati tugaguncha ishlab ketishi "
         "mumkin, lekin tizim ishlab turadi. Shundan o'rgandim: xavfsizlik "
         "tekshiruvining yiqilishida nima bo'lishini oldindan hal qilib qo'yish "
         "kerak, va javob har doim \"rad etish\" bo'lavermaydi.")

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
