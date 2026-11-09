# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "API Key authentication"
CATEGORY = "Auth"
TITLE = "API Key Autentifikatsiyasi"
SUBTITLE = "Server-server integratsiyalari uchun kalit bilan kirish"
FILENAME = "API Key authentication.docx"


def build(d):
    h1(d, "1. API key nima va nima uchun ishlatiladi")

    para(d, "API key — uzun tasodifiy satr, u **ilovani** (yoki mijozni) "
            "aniqlaydi, odamni emas. Shuning uchun u foydalanuvchi logini "
            "o'rnini bosmaydi.")

    para(d, "Men uni shu holatlarda ishlataman:")

    bullets(d, [
        "Boshqa servis mening API'ga murojaat qiladi va unda odam "
        "qatnashmaydi.",
        "Webhook qabul qilish — yuboruvchi o'zini tasdiqlashi kerak.",
        "Hamkor tashkilotga cheklangan kirish berish, har biriga alohida "
        "kalit bilan (shunda kimning qancha so'rov yuborganini bilish "
        "mumkin).",
        "Ichki diagnostika yoki metrika endpoint'lari.",
    ])

    para(d, "Ishlatmaydigan holatlar ham aniq: foydalanuvchi "
            "autentifikatsiyasi, mobil ilova yoki SPA. Brauzerda yoki "
            "mobil ilovada kalitni yashirib bo'lmaydi — uni kodni ochib "
            "ko'rgan har kim topadi.")

    # ───────────────────────────────────────────
    h1(d, "2. Kalit qanday uzatiladi")

    code(d, """# 1. Maxsus header — tavsiya etiladigan usul
X-Api-Key: 7f3c9a1e8b24d6f0...

# 2. Authorization header bilan
Authorization: ApiKey 7f3c9a1e8b24d6f0...

# 3. Query string — eng yomon variant
GET /api/orders?api_key=7f3c9a1e...""")

    para(d, "Query string'dan qochaman, chunki URL har joyga yoziladi: web "
            "server log'i, proxy log'i, brauzer tarixi, `Referer` header'i. "
            "Ya'ni kalit hujjatlashtirilmagan joylarda qolib ketadi.")

    # ───────────────────────────────────────────
    h1(d, "3. Kalitni qanday yarataman")

    para(d, "Kalit **kriptografik tasodifiy** bo'lishi kerak. `Random` "
            "sinfi bu yerda yaramaydi — u oldindan aytib bo'ladigan ketma-"
            "ketlik beradi:")

    code(d, """public static string GenerateKey()
{
    var bytes = RandomNumberGenerator.GetBytes(32);     // 256 bit
    return Convert.ToBase64String(bytes)
        .Replace("+", "").Replace("/", "").Replace("=", "");
}""")

    para(d, "Kalitga prefiks qo'shish amalda juda foydali — uni log'da yoki "
            "git'da avtomatik topish imkonini beradi:")

    code(d, """// shop_live_7f3c9a1e...
// shop_test_2b8e4d1c...
var key = $"shop_{(isProduction ? "live" : "test")}_{GenerateKey()}";""")

    # ───────────────────────────────────────────
    h1(d, "4. Kalitni saqlash — eng muhim qism")

    para(d, "Kalitni bazada **ochiq holda saqlash xato**. U parol bilan "
            "bir xil darajada maxfiy: baza oqib ketsa, hamma mijozning "
            "kaliti qo'lga tushadi.")

    para(d, "Shuning uchun kalit hash qilib saqlanadi va foydalanuvchiga "
            "faqat bir marta — yaratilganda — ko'rsatiladi:")

    code(d, """public sealed class ApiKeyRecord
{
    public Guid Id { get; init; }
    public string ClientName { get; init; } = "";
    public string Prefix { get; init; } = "";        // ko'rsatish uchun: shop_live_7f3c
    public byte[] KeyHash { get; init; } = [];
    public DateTimeOffset CreatedAt { get; init; }
    public DateTimeOffset? ExpiresAt { get; init; }
    public DateTimeOffset? RevokedAt { get; init; }
    public DateTimeOffset? LastUsedAt { get; set; }
    public string[] Scopes { get; init; } = [];
}""")

    note(d, "Parol hashidan farqi",
         "Parol uchun Argon2 yoki bcrypt kabi **sekin** funksiya kerak, "
         "chunki parol qisqa va odam o'ylab topgan. API key esa 256 bitli "
         "tasodifiy qiymat — uni lug'at bilan topish mumkin emas. Shuning "
         "uchun SHA-256 yetarli va har so'rovda hisoblash arzon bo'ladi.")

    code(d, """private static byte[] Hash(string key)
    => SHA256.HashData(Encoding.UTF8.GetBytes(key));""")

    # ───────────────────────────────────────────
    h1(d, "5. Autentifikatsiya sxemasi sifatida amalga oshirish")

    para(d, "Middleware yozish ham mumkin, lekin to'g'ri yo'l — "
            "`AuthenticationHandler` yozish. Shunda `[Authorize]`, "
            "siyosatlar va `User` obyekti odatdagidek ishlaydi:")

    code(d, """public sealed class ApiKeyOptions : AuthenticationSchemeOptions
{
    public const string Scheme = "ApiKey";
    public string HeaderName { get; set; } = "X-Api-Key";
}

public sealed class ApiKeyHandler(
    IOptionsMonitor<ApiKeyOptions> options,
    ILoggerFactory logger,
    UrlEncoder encoder,
    IApiKeyStore store) : AuthenticationHandler<ApiKeyOptions>(options, logger, encoder)
{
    protected override async Task<AuthenticateResult> HandleAuthenticateAsync()
    {
        if (!Request.Headers.TryGetValue(Options.HeaderName, out var values))
            return AuthenticateResult.NoResult();      // kalit yo'q — rad etmaymiz

        var presented = values.ToString();
        if (string.IsNullOrWhiteSpace(presented))
            return AuthenticateResult.Fail("Bo'sh kalit");

        var record = await store.FindAsync(presented, Context.RequestAborted);
        if (record is null)
            return AuthenticateResult.Fail("Kalit topilmadi");

        if (record.RevokedAt is not null)
            return AuthenticateResult.Fail("Kalit bekor qilingan");

        if (record.ExpiresAt < TimeProvider.System.GetUtcNow())
            return AuthenticateResult.Fail("Kalit muddati tugagan");

        var claims = new List<Claim>
        {
            new(ClaimTypes.NameIdentifier, record.Id.ToString()),
            new(ClaimTypes.Name, record.ClientName)
        };
        claims.AddRange(record.Scopes.Select(s => new Claim("scope", s)));

        var identity = new ClaimsIdentity(claims, Scheme.Name);
        return AuthenticateResult.Success(
            new AuthenticationTicket(new ClaimsPrincipal(identity), Scheme.Name));
    }
}""")

    code(d, """builder.Services.AddAuthentication()
    .AddScheme<ApiKeyOptions, ApiKeyHandler>(ApiKeyOptions.Scheme, _ => { });

builder.Services.AddAuthorizationBuilder()
    .AddPolicy("ReadOrders", p => p
        .AddAuthenticationSchemes(ApiKeyOptions.Scheme)
        .RequireClaim("scope", "orders:read"));""")

    code(d, """[Authorize(Policy = "ReadOrders")]
[HttpGet("api/integration/orders")]
public Task<IActionResult> List(CancellationToken ct) => ...;""")

    # ───────────────────────────────────────────
    h1(d, "6. Taqqoslashni xavfsiz qilish")

    para(d, "Kalitni bazadan topish uchun uning hash'i bo'yicha qidiraman — "
            "shunda indeks ishlaydi va hamma yozuvni o'qib chiqish kerak "
            "bo'lmaydi:")

    code(d, """public async Task<ApiKeyRecord?> FindAsync(string presented, CancellationToken ct)
{
    var hash = Hash(presented);

    var record = await db.ApiKeys
        .AsNoTracking()
        .FirstOrDefaultAsync(k => k.KeyHash == hash, ct);

    if (record is null) return null;

    // qo'shimcha himoya: doimiy vaqtda taqqoslash
    return CryptographicOperations.FixedTimeEquals(record.KeyHash, hash)
        ? record
        : null;
}""")

    para(d, "`FixedTimeEquals` baytlarni oxirigacha taqqoslaydi. Oddiy "
            "`==` esa birinchi farqda to'xtaydi va javob vaqti orqali "
            "ma'lumot oqishi mumkin — bu timing attack deb ataladi.")

    # ───────────────────────────────────────────
    h1(d, "7. Amaliy talablar ro'yxati")

    bullets(d, [
        "**TLS majburiy.** Kalit har so'rovda uzatiladi, shifrlanmagan "
        "kanalda u darhol oshkor bo'ladi.",
        "**Rate limiting.** Kalit bo'yicha so'rov cheklovi qo'yiladi — "
        "aks holda bitta mijoz butun servisni band qilib qo'yadi.",
        "**Scope.** Har bir kalitga faqat kerakli huquqlar beriladi. "
        "\"Hammasiga ruxsat\" kaliti oqib ketsa zarar katta bo'ladi.",
        "**Muddat va rotatsiya.** Kalitga tugash sanasi qo'yiladi. "
        "Rotatsiya uchun bir vaqtda ikki kalit amal qilishiga ruxsat "
        "berish kerak, aks holda mijozda uzilish bo'ladi.",
        "**Audit.** Har bir kalitning oxirgi ishlatilgan vaqti va "
        "so'rovlar soni yoziladi — ishlatilmayotgan kalitni topib o'chirish "
        "uchun.",
        "**Log'ga tushmasligi.** Kalit header'i log'da maskalanishi kerak.",
        "**IP cheklash.** Imkoni bo'lsa kalitni ma'lum IP diapazoniga "
        "bog'laman — o'g'irlangan kalit boshqa joydan ishlamaydi.",
    ])

    note(d, "Kalit oqib ketsa",
         "Yagona to'g'ri javob — darhol bekor qilish va yangisini berish. "
         "\"Hech kim topmasa kerak\" degan taxminga tayanib bo'lmaydi: "
         "git tarixiga tushgan kalitni avtomatik skanerlar bir necha "
         "daqiqada topadi.")

    sources(d, [
        ("Authentication handler in ASP.NET Core",
         "https://learn.microsoft.com/en-us/aspnet/core/security/authentication/"),
        ("RandomNumberGenerator Class",
         "https://learn.microsoft.com/en-us/dotnet/api/system.security.cryptography.randomnumbergenerator"),
        ("CryptographicOperations.FixedTimeEquals",
         "https://learn.microsoft.com/en-us/dotnet/api/system.security.cryptography.cryptographicoperations.fixedtimeequals"),
        ("Rate limiting middleware in ASP.NET Core",
         "https://learn.microsoft.com/en-us/aspnet/core/performance/rate-limit"),
    ])
