# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "JWT (structure, signing, validation)"
CATEGORY = "Auth"
TITLE = "JWT: Tuzilma, Imzo va Tekshirish"
SUBTITLE = "Token ichida nima bor va unga qanday ishoniladi"
FILENAME = "JWT (structure, signing, validation).docx"


def build(d):
    h1(d, "1. JWT nima")

    para(d, "JWT (JSON Web Token) — ma'lumotni ixcham, URL ga xavfsiz shaklda "
            "uzatish standarti. Uning asosiy xususiyati shundaki, token "
            "imzolangan — ya'ni uni o'zgartirish imkonsiz, lekin **o'qish mumkin**.")

    note(d, "Bu eng muhim tushuncha:",
         "JWT shifrlanmagan, faqat imzolangan. Har kim uni ochib, ichidagini "
         "o'qiy oladi — buning uchun hech qanday kalit kerak emas. Imzo faqat "
         "o'zgartirishdan himoya qiladi. Shuning uchun tokenga parol, karta "
         "raqami yoki boshqa sir yozib bo'lmaydi.")

    # ───────────────────────────────────────────
    h1(d, "2. Tuzilma")

    para(d, "JWT uch qismdan iborat va ular nuqta bilan ajratiladi:")

    code(d, """eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9
.
eyJzdWIiOiI3IiwibmFtZSI6Ik9yemliZWsiLCJleHAiOjE3NjIwMDAwMDB9
.
SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c

└──── header ────┘ └──── payload ────┘ └──── signature ────┘""")

    para(d, "Birinchi ikki qism oddiy Base64URL kodlangan JSON — ularni istalgan "
            "vositada ochib ko'rish mumkin.")

    h2(d, "2.1 Header")

    code(d, """{
  "alg": "HS256",
  "typ": "JWT",
  "kid": "key-2026-01"
}""")

    bullets(d, [
        "`alg` — imzolash algoritmi.",
        "`typ` — token turi.",
        "`kid` — qaysi kalit ishlatilgani; kalitlar aylanishida kerak bo'ladi.",
    ])

    h2(d, "2.2 Payload va standart da'volar")

    code(d, """{
  "sub": "7",
  "name": "Orzibek",
  "role": ["Admin", "Editor"],
  "iss": "https://auth.example.com",
  "aud": "https://api.example.com",
  "exp": 1762000000,
  "iat": 1761999100,
  "nbf": 1761999100,
  "jti": "a3f91c7e-..."
}""")

    table(d, ["Da'vo", "Ma'nosi"],
          [["`sub`", "Subject — token kim haqida"],
           ["`iss`", "Issuer — kim bergan"],
           ["`aud`", "Audience — kim uchun mo'ljallangan"],
           ["`exp`", "Expiration — qachon tugaydi"],
           ["`iat`", "Issued at — qachon berilgan"],
           ["`nbf`", "Not before — qachondan amal qiladi"],
           ["`jti`", "JWT ID — noyob identifikator"]],
          widths=[2.8, 12.7])

    para(d, "Vaqt qiymatlari Unix timestamp — 1970-yildan beri o'tgan soniyalar "
            "soni, UTC da.")

    note(d, "`aud` ni tekshirish nega muhim:",
         "Agar menda bir nechta API bo'lsa va ular bir xil kalit bilan imzolangan "
         "tokenlarni qabul qilsa, bitta API uchun berilgan token boshqasida ham "
         "ishlab ketadi. `aud` ni tekshirish shu yo'lni yopadi — token faqat o'zi "
         "mo'ljallangan joyda qabul qilinadi.")

    h2(d, "2.3 Signature")

    code(d, """HMACSHA256(
    base64UrlEncode(header) + "." + base64UrlEncode(payload),
    secret
)""")

    para(d, "Imzo header va payload ning birgalikdagi hash i. Agar payload da bitta "
            "harf o'zgarsa, imzo mos kelmay qoladi va token rad etiladi.")

    # ───────────────────────────────────────────
    h1(d, "3. Imzolash algoritmlari")

    table(d, ["Algoritm", "Turi", "Qachon"],
          [["`HS256`", "Simmetrik — bitta maxfiy kalit",
            "Token beruvchi va tekshiruvchi bitta tizim"],
           ["`RS256`", "Asimmetrik — maxfiy/ochiq kalit juftligi",
            "Bir nechta xizmat tekshiradi"],
           ["`ES256`", "Asimmetrik, elliptik egri chiziq",
            "RS256 ga o'xshash, lekin qisqaroq imzo"]],
          widths=[2.8, 5.4, 7.3])

    para(d, "Simmetrik algoritmda bir xil kalit ham imzolash, ham tekshirish uchun "
            "ishlatiladi. Demak tekshiruvchi tomon token yarata ham oladi.")

    para(d, "Asimmetrik algoritmda esa maxfiy kalit faqat token beruvchida qoladi, "
            "tekshiruvchilarga faqat ochiq kalit beriladi. Ular tokenni tekshira "
            "oladi, lekin yarata olmaydi.")

    note(d, "Mening tanlash qoidam:",
         "Agar token ni bergan va tekshirgan bitta ilova bo'lsa — `HS256` yetarli "
         "va soddaroq. Agar bir nechta mikroservis tekshirsa — albatta `RS256`, "
         "chunki maxfiy kalitni o'nta xizmatga tarqatish uni o'nta joyda sizib "
         "chiqish xavfiga qo'yadi.")

    h2(d, "3.1 alg: none hujumi")

    para(d, "JWT standartida `\"alg\": \"none\"` qiymati mavjud — u imzosiz tokenni "
            "bildiradi. Ba'zi eski kutubxonalar bunday tokenni tekshirmasdan qabul "
            "qilgan va bu jiddiy zaiflik bo'lgan.")

    code(d, """// Tajovuzkor payload ni o'zgartirib, imzoni olib tashlaydi
{ "alg": "none" }.{ "sub": "1", "role": "Admin" }.""")

    note(d, "Himoya oddiy, lekin aniq yozilishi kerak:",
         "Qabul qilinadigan algoritmlarni aniq ro'yxat bilan cheklash kerak. "
         "Zamonaviy `.NET` kutubxonalari buni o'zi qiladi, lekin men baribir "
         "`ValidAlgorithms` ni yozib qo'yaman — bu kelajakda kimdir sozlamani "
         "o'zgartirsa ham himoya qoladi.")

    code(d, """options.TokenValidationParameters = new TokenValidationParameters
{
    ValidAlgorithms = new[] { SecurityAlgorithms.HmacSha256 },
    ...
};""")

    # ───────────────────────────────────────────
    h1(d, "4. Token yaratish")

    code(d, """public string CreateToken(AppUser user, IEnumerable<string> roles)
{
    var claims = new List<Claim>
    {
        new(JwtRegisteredClaimNames.Sub, user.Id.ToString()),
        new(JwtRegisteredClaimNames.Email, user.Email),
        new(JwtRegisteredClaimNames.Jti, Guid.NewGuid().ToString())
    };

    claims.AddRange(roles.Select(r => new Claim(ClaimTypes.Role, r)));

    var key = new SymmetricSecurityKey(
        Encoding.UTF8.GetBytes(_options.Key));

    var token = new JwtSecurityToken(
        issuer: _options.Issuer,
        audience: _options.Audience,
        claims: claims,
        notBefore: DateTime.UtcNow,
        expires: DateTime.UtcNow.AddMinutes(15),
        signingCredentials: new SigningCredentials(
            key, SecurityAlgorithms.HmacSha256));

    return new JwtSecurityTokenHandler().WriteToken(token);
}""")

    note(d, "Kalit uzunligi haqida:",
         "`HS256` uchun kalit kamida 256 bit, ya'ni 32 bayt bo'lishi kerak. Qisqa "
         "kalit berilsa, `.NET` xatolik beradi — va bu yaxshi, chunki qisqa kalitni "
         "saralab topish mumkin. Kalit konfiguratsiya faylida emas, atrof-muhit "
         "o'zgaruvchisida yoki sir omborida turishi shart.")

    # ───────────────────────────────────────────
    h1(d, "5. Tekshirish")

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
                Encoding.UTF8.GetBytes(config["Jwt:Key"]!)),

            ValidAlgorithms = new[] { SecurityAlgorithms.HmacSha256 }
        };
    });""")

    para(d, "Tekshirish bosqichlari ketma-ketligi: imzo, muddat, issuer, audience. "
            "Birortasi mos kelmasa, so'rov `401` bilan rad etiladi.")

    h2(d, "5.1 Xatolikni aniqlash")

    code(d, """options.Events = new JwtBearerEvents
{
    OnAuthenticationFailed = context =>
    {
        if (context.Exception is SecurityTokenExpiredException)
            context.Response.Headers["Token-Expired"] = "true";

        logger.LogWarning(context.Exception, "Token tekshiruvdan o'tmadi");
        return Task.CompletedTask;
    }
};""")

    para(d, "`Token-Expired` sarlavhasi mijozga aniq sabab beradi — u refresh "
            "so'rovini yuborishi kerakligini tushunadi va foydalanuvchini "
            "chiqarib yubormaydi.")

    h2(d, "5.2 Asimmetrik kalit bilan")

    code(d, """options.Authority = "https://auth.example.com";
options.TokenValidationParameters = new TokenValidationParameters
{
    ValidateIssuer = true,
    ValidAudience = "https://api.example.com"
};""")

    para(d, "`Authority` ko'rsatilsa, kutubxona ochiq kalitlarni "
            "`/.well-known/openid-configuration` orqali o'zi yuklab oladi va "
            "keshlaydi. Kalit almashtirilganda kod o'zgarmaydi.")

    # ───────────────────────────────────────────
    h1(d, "6. Da'volarni ishlatish")

    code(d, """[Authorize(Roles = "Admin")]
[HttpDelete("{id:int}")]
public async Task<IActionResult> Delete(int id)
{
    var userId = User.FindFirstValue(ClaimTypes.NameIdentifier);
    var email = User.FindFirstValue(ClaimTypes.Email);
    ...
}""")

    note(d, "`.NET` dagi bitta chalkashtiruvchi xatti-harakat:",
         "Kutubxona sukut bo'yicha standart JWT da'vo nomlarini uzun "
         "`http://schemas.xmlsoap.org/...` shakliga aylantiradi. Shuning uchun "
         "`sub` ni qidirsam topa olmayman — u `ClaimTypes.NameIdentifier` ga "
         "aylangan bo'ladi. Buni o'chirish mumkin:")

    code(d, """JwtSecurityTokenHandler.DefaultInboundClaimTypeMap.Clear();""")

    # ───────────────────────────────────────────
    h1(d, "7. Cheklovlar va ularni yopish")

    table(d, ["Muammo", "Yechim"],
          [["Tokenni bekor qilib bo'lmaydi",
            "Qisqa muddat + refresh token; kritik holatda qora ro'yxat"],
           ["Token hajmi kattalashadi",
            "Faqat zarur da'volarni qo'shish; huquqlarni bazadan o'qish"],
           ["O'g'irlangan token ishlab ketadi",
            "HTTPS, `HttpOnly` cookie, qurilmaga bog'lash"],
           ["Ma'lumot eskiradi",
            "Rolni token da emas, so'rov paytida tekshirish"]],
          widths=[5.4, 10.1])

    note(d, "Oxirgi qator haqida amaliy misol:",
         "Foydalanuvchining admin huquqini olib tashladim deylik. Uning "
         "tokenida `role: Admin` yozilgan va u muddati tugaguncha admin bo'lib "
         "qolaveradi. Shuning uchun men juda muhim amallarda rolni tokendan "
         "emas, bazadan tekshiraman. Qolgan joylarda esa tokendagi qiymat "
         "yetarli — bu unumdorlik va aniqlik o'rtasidagi ongli murosa.")

    # ───────────────────────────────────────────
    h1(d, "8. Xulosa")

    bullets(d, [
        "JWT uch qismdan iborat: header, payload, signature.",
        "Token imzolangan, lekin **shifrlanmagan** — ichidagini har kim o'qiy "
        "oladi.",
        "Standart da'volar: `sub`, `iss`, `aud`, `exp`, `iat`, `nbf`, `jti`.",
        "`HS256` bitta tizim uchun, `RS256` bir nechta xizmat tekshirganda.",
        "Qabul qilinadigan algoritmlarni aniq ro'yxat bilan cheklash kerak.",
        "`HS256` kaliti kamida 32 bayt bo'lishi va sir omborida saqlanishi shart.",
        "`ValidateIssuer`, `ValidateAudience`, `ValidateLifetime` va "
        "`ValidateIssuerSigningKey` — hammasi yoqilgan bo'lishi kerak.",
        "Tokenni muddatidan oldin bekor qilib bo'lmaydi — shuning uchun u qisqa "
        "muddatli bo'lishi lozim.",
    ])

    sources(d, [
        ("RFC 7519 — JSON Web Token (JWT)",
         "https://www.rfc-editor.org/rfc/rfc7519"),
        ("RFC 8725 — JSON Web Token Best Current Practices",
         "https://www.rfc-editor.org/rfc/rfc8725"),
        ("Configure JWT bearer authentication in ASP.NET Core",
         "https://learn.microsoft.com/en-us/aspnet/core/security/authentication/configure-jwt-bearer-authentication"),
        ("JSON Web Tokens — jwt.io",
         "https://jwt.io/introduction"),
    ])
