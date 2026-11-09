# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "Token-based authentication, OAuth"
CATEGORY = "Auth"
TITLE = "Token Asosidagi Autentifikatsiya va OAuth"
SUBTITLE = "Access token, refresh token va vakolat berish oqimlari"
FILENAME = "Token-based authentication, OAuth.docx"


def build(d):
    h1(d, "1. Nima uchun token")

    para(d, "Sessiyaga asoslangan autentifikatsiyada server har bir foydalanuvchi "
            "uchun holat saqlaydi. Bu bitta serverda muammo emas, lekin bir nechta "
            "nusxa bo'lganda sessiyalarni bo'lishish kerak bo'ladi.")

    para(d, "Token asosidagi yondashuvda server hech narsa saqlamaydi. Token ning "
            "o'zida foydalanuvchi haqidagi ma'lumot bor va u imzolangan — demak "
            "server uni tekshirib, ishonishi mumkin.")

    table(d, ["Jihat", "Sessiya", "Token"],
          [["Server holati", "Saqlaydi", "Saqlamaydi"],
           ["Miqyoslash", "Umumiy ombor kerak", "Oson"],
           ["Bekor qilish", "Darhol", "Qiyin — muddati tugashini kutish kerak"],
           ["Hajmi", "Kichik kalit", "Kattaroq, har so'rovda ketadi"],
           ["Mobil mijozlar", "Noqulay", "Tabiiy"]],
          widths=[3.6, 5.4, 6.5])

    note(d, "Bekor qilish masalasi eng muhim murosa:",
         "Token ning asosiy afzalligi — server unga qaramasdan ishonadi. Lekin "
         "aynan shu sababli uni muddatidan oldin bekor qilib bo'lmaydi. "
         "Foydalanuvchi \"chiqish\" tugmasini bossa ham, token amal qilaveradi. "
         "Shuning uchun access token ni qisqa muddatli qilish shart — men odatda "
         "15 daqiqa qo'yaman.")

    # ───────────────────────────────────────────
    h1(d, "2. Access va refresh token")

    para(d, "Ikki tokenli sxema qisqa muddatlilik va qulaylik o'rtasidagi "
            "muvozanatni topadi:")

    table(d, ["Token", "Muddati", "Qayerda saqlanadi", "Nima uchun"],
          [["Access", "5–30 daqiqa", "Xotirada", "Har so'rovda yuboriladi"],
           ["Refresh", "7–30 kun", "`HttpOnly` cookie yoki xavfsiz ombor",
            "Yangi access token olish"]],
          widths=[2.6, 3.0, 5.4, 4.5])

    code(d, """POST /auth/login
  → { accessToken: "eyJ...", expiresIn: 900 }
    Set-Cookie: refreshToken=...; HttpOnly; Secure; SameSite=Strict

# 15 daqiqadan keyin
POST /auth/refresh      (cookie avtomatik ketadi)
  → { accessToken: "eyJ...", expiresIn: 900 }""")

    h2(d, "2.1 Refresh token rotatsiyasi")

    para(d, "Har safar refresh token ishlatilganda yangisi beriladi va eskisi bekor "
            "qilinadi. Bu o'g'irlangan tokenni aniqlash imkonini beradi:")

    code(d, """public async Task<TokenPair> RefreshAsync(string token, CancellationToken ct)
{
    var stored = await _db.RefreshTokens
        .FirstOrDefaultAsync(t => t.Token == token, ct);

    if (stored is null)
        throw new SecurityTokenException("Noma'lum token");

    if (stored.RevokedAt is not null)
    {
        // Bekor qilingan token qayta ishlatildi — o'g'irlangan bo'lishi mumkin
        await RevokeAllForUserAsync(stored.UserId, ct);
        throw new SecurityTokenException("Token qayta ishlatildi");
    }

    if (stored.ExpiresAt < DateTime.UtcNow)
        throw new SecurityTokenException("Muddati tugagan");

    stored.RevokedAt = DateTime.UtcNow;
    var fresh = await IssueAsync(stored.UserId, ct);
    return fresh;
}""")

    note(d, "Bu mexanizm nega ishlaydi:",
         "Agar tajovuzkor refresh token ni o'g'irlasa, ikkalasi ham undan "
         "foydalanishga urinadi. Birinchisi yangi token oladi, eskisi bekor "
         "bo'ladi. Ikkinchisi esa bekor qilingan token bilan keladi — va aynan "
         "shu paytda men o'g'irlik bo'lganini bilaman. Javob sifatida "
         "foydalanuvchining barcha sessiyalarini yopaman.")

    # ───────────────────────────────────────────
    h1(d, "3. ASP.NET Core da JWT")

    code(d, """builder.Services
    .AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddJwtBearer(options =>
    {
        options.TokenValidationParameters = new TokenValidationParameters
        {
            ValidateIssuer = true,
            ValidIssuer = config["Jwt:Issuer"],

            ValidateAudience = true,
            ValidAudience = config["Jwt:Audience"],

            ValidateLifetime = true,
            ClockSkew = TimeSpan.FromSeconds(30),

            ValidateIssuerSigningKey = true,
            IssuerSigningKey = new SymmetricSecurityKey(
                Encoding.UTF8.GetBytes(config["Jwt:Key"]!))
        };
    });

app.UseAuthentication();
app.UseAuthorization();""")

    note(d, "`ClockSkew` ning sukutdagi qiymati 5 daqiqa:",
         "Ya'ni muddati tugagan token yana besh daqiqa qabul qilinaveradi. Bu "
         "serverlar soatidagi farqni qoplash uchun qo'yilgan. Lekin agar men "
         "access token ni 15 daqiqalik qilgan bo'lsam, bu 33% qo'shimcha muddat "
         "degani. Shuning uchun uni aniq kichraytirib qo'yaman.")

    # ───────────────────────────────────────────
    h1(d, "4. OAuth 2.0")

    para(d, "OAuth — bu autentifikatsiya protokoli **emas**, vakolat berish "
            "protokoli. U quyidagi savolga javob beradi: foydalanuvchi parolini "
            "bermasdan turib, bir ilovaga boshqa xizmatdagi ma'lumotiga qanday "
            "ruxsat bera oladi.")

    h2(d, "4.1 Ishtirokchilar")

    table(d, ["Rol", "Kim"],
          [["Resource Owner", "Foydalanuvchi"],
           ["Client", "Ruxsat so'rayotgan ilova"],
           ["Authorization Server", "Tokenni beruvchi xizmat"],
           ["Resource Server", "Ma'lumotni saqlovchi API"]],
          widths=[4.6, 10.9])

    h2(d, "4.2 Authorization Code oqimi")

    code(d, """1. Foydalanuvchi "Google bilan kirish" ni bosadi

2. Ilova uni authorization serverga yo'naltiradi:
   GET /authorize?response_type=code
                 &client_id=abc
                 &redirect_uri=https://app.example.com/callback
                 &scope=openid email profile
                 &state=xyz123
                 &code_challenge=...&code_challenge_method=S256

3. Foydalanuvchi u yerda kiradi va ruxsat beradi

4. Authorization server qaytaradi:
   GET https://app.example.com/callback?code=AUTH_CODE&state=xyz123

5. Ilova server tomonidan kodni tokenga almashtiradi:
   POST /token
     grant_type=authorization_code
     code=AUTH_CODE
     client_id=abc
     client_secret=...        (yoki code_verifier)

6. Javobda access token (va ko'pincha refresh token) keladi""")

    para(d, "Diqqat qiladigan joy — token hech qachon brauzer manzil satriga "
            "tushmaydi. Faqat qisqa muddatli kod ko'rinadi va u faqat bir marta "
            "ishlatiladi.")

    h2(d, "4.3 PKCE")

    para(d, "PKCE (Proof Key for Code Exchange) kodni ushlab qolish xavfini yopadi. "
            "Ilova tasodifiy `code_verifier` yaratadi, uning hash ini so'rovga "
            "qo'shadi, tokenni olishda esa asl qiymatni ko'rsatadi.")

    code(d, """code_verifier  = tasodifiy 43–128 belgili satr
code_challenge = BASE64URL(SHA256(code_verifier))""")

    note(d, "PKCE endi hamma uchun tavsiya etiladi:",
         "Avval u faqat mobil va SPA ilovalar uchun kerak deb hisoblanardi — "
         "chunki ular `client_secret` ni xavfsiz saqlay olmaydi. Hozirgi OAuth 2.1 "
         "loyihasida esa PKCE barcha Authorization Code oqimlari uchun majburiy "
         "qilingan. Men uni server tomonidagi ilovalarda ham qo'shaman.")

    h2(d, "4.4 Boshqa oqimlar")

    table(d, ["Oqim", "Qachon", "Holati"],
          [["Authorization Code + PKCE", "Web, mobil, SPA", "Tavsiya etiladi"],
           ["Client Credentials", "Xizmatdan xizmatga", "Tavsiya etiladi"],
           ["Device Code", "TV, konsol — klaviaturasi cheklangan", "Tavsiya etiladi"],
           ["Implicit", "Eski SPA yondashuvi", "Ishlatilmaydi"],
           ["Password (ROPC)", "Ishonchli mijoz", "Ishlatilmaydi"]],
          widths=[5.2, 5.6, 4.7])

    note(d, "Implicit va ROPC dan voz kechish sababi:",
         "Implicit oqimida token to'g'ridan-to'g'ri manzil satrida qaytadi — u "
         "brauzer tarixiga, loglarga va `Referer` sarlavhasiga tushadi. ROPC esa "
         "foydalanuvchi parolini mijoz ilovasiga beradi, ya'ni OAuth ning asosiy "
         "maqsadini butunlay yo'qqa chiqaradi.")

    # ───────────────────────────────────────────
    h1(d, "5. OpenID Connect")

    para(d, "OAuth kimligini aniqlash uchun mo'ljallanmagan. Uning ustiga qurilgan "
            "OpenID Connect esa aynan shu bo'shliqni to'ldiradi — u `id_token` "
            "qo'shadi va foydalanuvchi haqidagi ma'lumotni standart shaklda beradi.")

    code(d, """scope=openid email profile

// Javobda qo'shimcha:
{
  "access_token": "...",
  "id_token": "eyJ...",     // foydalanuvchi haqida
  "token_type": "Bearer"
}""")

    para(d, "Farqni eslab qolish uchun oddiy qoida: `access_token` — \"nima qilishga "
            "ruxsat bor\", `id_token` — \"bu kim\".")

    code(d, """builder.Services
    .AddAuthentication(options =>
    {
        options.DefaultScheme = CookieAuthenticationDefaults.AuthenticationScheme;
        options.DefaultChallengeScheme = OpenIdConnectDefaults.AuthenticationScheme;
    })
    .AddCookie()
    .AddOpenIdConnect(options =>
    {
        options.Authority = "https://accounts.google.com";
        options.ClientId = config["Google:ClientId"];
        options.ClientSecret = config["Google:ClientSecret"];
        options.ResponseType = "code";
        options.UsePkce = true;

        options.Scope.Add("email");
        options.Scope.Add("profile");
        options.SaveTokens = true;
    });""")

    # ───────────────────────────────────────────
    h1(d, "6. Xavfsizlik qoidalari")

    bullets(d, [
        "`state` parametrini har doim tekshirish — u CSRF dan himoya qiladi.",
        "`redirect_uri` ni authorization serverda aniq ro'yxatdan o'tkazish, "
        "joker belgilarsiz.",
        "Access token ni qisqa muddatli qilish; refresh token ni rotatsiyalash.",
        "Tokenni `localStorage` da saqlamaslik — XSS uni ochadi.",
        "`client_secret` ni hech qachon brauzer kodiga qo'ymaslik.",
        "Token imzosini albatta tekshirish — `ValidateIssuerSigningKey = true`.",
        "`scope` ni minimal talab bilan cheklash.",
    ])

    # ───────────────────────────────────────────
    h1(d, "7. Xulosa")

    bullets(d, [
        "Token asosidagi autentifikatsiyada server holat saqlamaydi — bu "
        "miqyoslashni osonlashtiradi, lekin bekor qilishni qiyinlashtiradi.",
        "Qisqa access token + uzoq refresh token sxemasi muvozanatni topadi.",
        "Refresh token rotatsiyasi o'g'irlikni aniqlash imkonini beradi.",
        "`ClockSkew` ning sukutdagi 5 daqiqasini kichraytirish kerak.",
        "OAuth — vakolat berish protokoli, autentifikatsiya emas.",
        "Authorization Code + PKCE — hozirgi tavsiya etiladigan oqim.",
        "Implicit va Password oqimlari ishlatilmaydi.",
        "Kimligini aniqlash uchun OpenID Connect va `id_token` ishlatiladi.",
    ])

    sources(d, [
        ("RFC 6749 — The OAuth 2.0 Authorization Framework",
         "https://www.rfc-editor.org/rfc/rfc6749"),
        ("RFC 7636 — Proof Key for Code Exchange (PKCE)",
         "https://www.rfc-editor.org/rfc/rfc7636"),
        ("OAuth 2.0 Security Best Current Practice",
         "https://datatracker.ietf.org/doc/html/draft-ietf-oauth-security-topics"),
        ("OpenID Connect Core 1.0",
         "https://openid.net/specs/openid-connect-core-1_0.html"),
        ("Authentication and authorization in ASP.NET Core",
         "https://learn.microsoft.com/en-us/aspnet/core/security/"),
    ])
