# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "OWASP Top 10"
CATEGORY = "Cybersecurity"
TITLE = "OWASP Top 10"
SUBTITLE = "Web ilovalardagi eng keng tarqalgan xavfsizlik xatolari"
FILENAME = "OWASP Top 10.docx"


def build(d):
    h1(d, "1. OWASP Top 10 nima")

    para(d, "OWASP (Open Worldwide Application Security Project) — web ilovalar "
            "xavfsizligi bilan shug'ullanuvchi notijorat tashkilot. Top 10 — "
            "ularning eng mashhur hujjati bo'lib, u real ma'lumotlar asosida "
            "to'plangan eng keng tarqalgan zaifliklar ro'yxatini beradi.")

    para(d, "Ro'yxat bir necha yilda bir yangilanadi. Bu hujjatda 2021-yilgi "
            "versiya ko'rib chiqiladi — u hozircha eng keng ishlatiladigan "
            "mos yozuv hisoblanadi.")

    note(d, "Bu ro'yxatga qanday munosabatda bo'laman:",
         "Top 10 — bu to'liq xavfsizlik standarti emas, balki \"avval shularni "
         "tekshir\" degan ro'yxat. U eng ko'p uchraydigan xatolarni qamrab "
         "oladi, ya'ni undan boshlash eng katta foyda beradi. Lekin \"Top 10 ni "
         "yopdim, demak xavfsizman\" degan xulosa noto'g'ri bo'lar edi.")

    # ───────────────────────────────────────────
    h1(d, "2. A01 — Broken Access Control")

    para(d, "Foydalanuvchi o'ziga tegishli bo'lmagan ma'lumotga kirishi yoki "
            "ruxsat etilmagan amalni bajarishi. 2021-yilgi ro'yxatda birinchi "
            "o'rinda turadi.")

    code(d, """// Zaif — identifikatorni o'zgartirib, begona buyurtma ko'riladi
[HttpGet("orders/{id:int}")]
public async Task<IActionResult> Get(int id)
    => Ok(await _db.Orders.FindAsync(id));""")

    code(d, """// To'g'ri — egasini tekshirish
[HttpGet("orders/{id:int}")]
public async Task<IActionResult> Get(int id, CancellationToken ct)
{
    var userId = int.Parse(User.FindFirstValue(ClaimTypes.NameIdentifier)!);

    var order = await _db.Orders
        .Where(o => o.Id == id && o.CustomerId == userId)
        .FirstOrDefaultAsync(ct);

    return order is null ? NotFound() : Ok(order);
}""")

    note(d, "Bu eng ko'p uchraydigan xato:",
         "Endpoint `[Authorize]` bilan himoyalangan — demak tizimga kirgan har "
         "kim unga murojaat qila oladi. Lekin \"kirgan\" degani \"shu yozuvga "
         "haqli\" degani emas. Men bu tekshiruvni so'rov shartiga qo'shishni "
         "odat qilganman, keyin alohida `if` yozishdan ko'ra ishonchliroq.")

    # ───────────────────────────────────────────
    h1(d, "3. A02 — Cryptographic Failures")

    para(d, "Maxfiy ma'lumotning yetarli himoyalanmagani: shifrlanmagan uzatish, "
            "zaif algoritmlar, noto'g'ri saqlash.")

    bullets(d, [
        "HTTPS ni majburiy qilish va HSTS yoqish.",
        "Parollar uchun `Argon2id`, `bcrypt` yoki `PBKDF2`; `MD5` va `SHA-1` "
        "emas.",
        "Shifrlash uchun `AES-GCM`; `ECB` rejimidan qochish.",
        "Tasodifiy qiymatlar uchun `RandomNumberGenerator`, `Random` emas.",
    ])

    code(d, """// Xavfli — bashorat qilsa bo'ladi
var token = new Random().Next().ToString();

// Xavfsiz
var token = Convert.ToBase64String(
    RandomNumberGenerator.GetBytes(32));""")

    code(d, """app.UseHttpsRedirection();
app.UseHsts();""")

    # ───────────────────────────────────────────
    h1(d, "4. A03 — Injection")

    para(d, "Foydalanuvchi ma'lumotining buyruq sifatida bajarilishi. SQL "
            "injection eng mashhuri, lekin yagonasi emas — buyruq qatori, LDAP, "
            "XPath va NoSQL injection ham shu toifaga kiradi.")

    code(d, """// SQL — parametr bilan
await db.Users.FromSql($"SELECT * FROM users WHERE email = {email}")
    .ToListAsync(ct);

// Buyruq qatori — argumentlarni alohida berish
var psi = new ProcessStartInfo("convert");
psi.ArgumentList.Add(inputPath);     // satr birlashtirish emas
psi.ArgumentList.Add(outputPath);""")

    h2(d, "4.1 XSS ham shu toifada")

    code(d, """// Razor avtomatik qochiradi
<p>@Model.UserComment</p>

// Bu esa qochirmaydi — faqat ishonchli kontent uchun
<p>@Html.Raw(Model.UserComment)</p>""")

    code(d, """// Qo'shimcha himoya — Content Security Policy
app.Use(async (ctx, next) =>
{
    ctx.Response.Headers["Content-Security-Policy"] =
        "default-src 'self'; script-src 'self'; object-src 'none'";
    await next();
});""")

    # ───────────────────────────────────────────
    h1(d, "5. A04 — Insecure Design")

    para(d, "Bu toifa 2021-yilda qo'shilgan va u kodlash xatosi emas, "
            "loyihalash xatosini bildiradi. Masalan parolni tiklash jarayoni "
            "o'zi zaif bo'lsa, uni qanchalik to'g'ri kodlash ham yordam "
            "bermaydi.")

    bullets(d, [
        "Biznes mantiqni suiiste'mol qilish imkoniyatlarini oldindan o'ylash.",
        "So'rov sonini cheklash va bot himoyasini loyihaga kiritish.",
        "Muhim amallarni tasdiqlash talab qilish.",
        "Tahdidlarni modellashtirish — \"bu yerda nima noto'g'ri ketishi "
        "mumkin\" degan savolni berish.",
    ])

    note(d, "Bu toifa menga eng qiziq tuyuldi:",
         "Qolgan toifalar \"shunday yozma\" deydi, bu esa \"shunday o'ylama\" "
         "deydi. Misol: chegirma kuponini necha marta ishlatish mumkinligini "
         "belgilamaslik — bu kod xatosi emas, loyihaning o'zida bo'shliq. "
         "Keyinroq uni yopish ancha qimmatga tushadi.")

    # ───────────────────────────────────────────
    h1(d, "6. A05 — Security Misconfiguration")

    para(d, "Noto'g'ri sozlangan muhit — sukutdagi parollar, ochiq qolgan "
            "boshqaruv panellari, haddan ortiq batafsil xatolik xabarlari.")

    bullets(d, [
        "`UseDeveloperExceptionPage` ni production da o'chirish.",
        "API hujjati sahifasini yopish yoki himoyalash.",
        "Keraksiz HTTP metodlarini o'chirish.",
        "Server versiyasini oshkor qiluvchi sarlavhalarni olib tashlash.",
        "Sukutdagi hisoblarni o'chirish yoki parolini o'zgartirish.",
        "CORS siyosatini aniq cheklash.",
    ])

    code(d, """// Juda xavfli CORS sozlamasi
policy.AllowAnyOrigin().AllowAnyHeader().AllowAnyMethod();

// To'g'ri
policy.WithOrigins("https://app.example.com")
      .AllowAnyHeader()
      .AllowAnyMethod()
      .AllowCredentials();""")

    # ───────────────────────────────────────────
    h1(d, "7. A06 — Vulnerable and Outdated Components")

    para(d, "Ma'lum zaifligi bo'lgan kutubxonalardan foydalanish. Zamonaviy "
            "loyihada yuzlab bog'liqlik bo'ladi va ularning har biri — "
            "potensial kirish nuqtasi.")

    code(d, """dotnet list package --vulnerable --include-transitive
dotnet list package --outdated""")

    code(d, """# GitHub Actions da avtomatik tekshiruv
- name: Check vulnerable packages
  run: |
    dotnet list package --vulnerable --include-transitive 2>&1 \\
      | tee output.txt
    ! grep -q "has the following vulnerable packages" output.txt""")

    note(d, "`--include-transitive` bayrog'i muhim:",
         "Men to'g'ridan-to'g'ri qo'shgan paketlar odatda yangi bo'ladi. Xavf "
         "esa ko'pincha ularning ichidagi bog'liqliklarda — men ularni hatto "
         "ko'rmayman ham. Bu bayroqsiz tekshiruv muammoning yarmini o'tkazib "
         "yuboradi.")

    # ───────────────────────────────────────────
    h1(d, "8. A07 — Identification and Authentication Failures")

    bullets(d, [
        "Zaif parol siyosati yoki sizib chiqqan parollarni qabul qilish.",
        "Sessiya identifikatorini URL da uzatish.",
        "Chiqishdan keyin sessiyani bekor qilmaslik.",
        "Kirish urinishlarini cheklamaslik.",
        "MFA ni taklif qilmaslik.",
    ])

    code(d, """options.Lockout.MaxFailedAccessAttempts = 5;
options.Lockout.DefaultLockoutTimeSpan = TimeSpan.FromMinutes(15);
options.Lockout.AllowedForNewUsers = true;""")

    # ───────────────────────────────────────────
    h1(d, "9. A08 — Software and Data Integrity Failures")

    para(d, "Tekshirilmagan manbadan kelgan kod yoki ma'lumotga ishonish. Bunga "
            "ta'minot zanjiri hujumlari va xavfsiz bo'lmagan deserializatsiya "
            "kiradi.")

    code(d, """// Xavfli — tip ma'lumoti bilan deserializatsiya
var settings = new JsonSerializerSettings
{
    TypeNameHandling = TypeNameHandling.All   // ishlatmaslik kerak
};""")

    bullets(d, [
        "Paketlarni faqat ishonchli manbadan olish.",
        "`packages.lock.json` bilan versiyalarni qotirish.",
        "CI/CD quvurida kod imzosini tekshirish.",
        "Tashqi skriptlarni `integrity` atributi bilan ulash.",
    ])

    # ───────────────────────────────────────────
    h1(d, "10. A09 — Security Logging and Monitoring Failures")

    para(d, "Hujumni aniqlash imkonsiz bo'lishi. Agar hodisa logga yozilmasa, "
            "buzilish oylar davomida sezilmasligi mumkin.")

    bullets(d, [
        "Kirish urinishlari — muvaffaqiyatli va muvaffaqiyatsiz.",
        "Ruxsat rad etilgan holatlar.",
        "Huquqlar o'zgarishi.",
        "Muhim ma'lumotlarga kirish.",
    ])

    code(d, """_logger.LogWarning(
    "Ruxsat rad etildi: {UserId} {Resource} {Ip}",
    userId, resource, ctx.Connection.RemoteIpAddress);""")

    note(d, "Lekin logga sir yozmaslik kerak:",
         "Bu ikki talab bir-biriga zid ko'rinadi — ko'proq yozish kerak, lekin "
         "sirlarni emas. Men shunday hal qilaman: hodisaning **o'zi** yoziladi, "
         "lekin tafsilotlar emas. \"Foydalanuvchi 7 noto'g'ri parol kiritdi\" — "
         "ha. Kiritilgan parol — hech qachon.")

    # ───────────────────────────────────────────
    h1(d, "11. A10 — Server-Side Request Forgery (SSRF)")

    para(d, "Server foydalanuvchi bergan manzilga so'rov yuborishga "
            "majburlanadi. Bu ichki tarmoqdagi xizmatlarga yetib borish "
            "imkonini beradi.")

    code(d, """// Zaif
[HttpPost("fetch-image")]
public async Task<IActionResult> Fetch([FromBody] string url)
{
    var bytes = await _http.GetByteArrayAsync(url);
    return File(bytes, "image/png");
}""")

    para(d, "Tajovuzkor `http://169.254.169.254/latest/meta-data/` yoki "
            "`http://localhost:5432` manzilini berib, ichki resurslarga yetadi.")

    code(d, """// Himoya
private static readonly string[] AllowedHosts =
    ["images.example.com", "cdn.example.com"];

if (!Uri.TryCreate(url, UriKind.Absolute, out var uri))
    return BadRequest("Noto'g'ri manzil");

if (uri.Scheme != Uri.UriSchemeHttps)
    return BadRequest("Faqat HTTPS");

if (!AllowedHosts.Contains(uri.Host))
    return BadRequest("Ruxsat etilmagan manba");

var addresses = await Dns.GetHostAddressesAsync(uri.Host);
if (addresses.Any(IsPrivateAddress))
    return BadRequest("Ichki manzil");""")

    note(d, "DNS tekshiruvi nega kerak:",
         "Oq ro'yxatdagi domen ichki IP ga ishora qilishi mumkin — bu "
         "\"DNS rebinding\" deb ataladi. Shuning uchun domen nomini tekshirish "
         "yetarli emas, u qaysi manzilga yechilishini ham ko'rish kerak.")

    # ───────────────────────────────────────────
    h1(d, "12. Amaliy tekshiruv ro'yxati")

    bullets(d, [
        "Har bir endpoint da resurs egasi tekshirilyaptimi.",
        "HTTPS majburiymi, HSTS yoqilganmi.",
        "Barcha SQL parametrlanganmi.",
        "Production da batafsil xatolik o'chirilganmi.",
        "CORS aniq domenlar bilan cheklanganmi.",
        "Zaif paketlar bormi.",
        "Kirish urinishlari cheklanganmi va logga yozilyaptimi.",
        "Tashqi manzilga so'rov yuborish oq ro'yxat bilan cheklanganmi.",
    ])

    # ───────────────────────────────────────────
    h1(d, "13. Xulosa")

    bullets(d, [
        "OWASP Top 10 — eng ko'p uchraydigan zaifliklar ro'yxati, to'liq "
        "standart emas.",
        "Broken Access Control birinchi o'rinda — `[Authorize]` yetarli emas, "
        "resurs egasi ham tekshirilishi kerak.",
        "Injection faqat SQL emas — buyruq qatori, XSS va boshqalar ham shu "
        "toifada.",
        "Insecure Design kod emas, loyihalash bosqichidagi xatolarni bildiradi.",
        "Bog'liqliklarni `--include-transitive` bilan tekshirish shart.",
        "Xavfsizlik hodisalarini logga yozish kerak, lekin sirlarsiz.",
        "SSRF dan himoya uchun domen va u yechiladigan IP ikkalasi ham "
        "tekshiriladi.",
    ])

    sources(d, [
        ("OWASP Top 10:2021",
         "https://owasp.org/Top10/"),
        ("OWASP Cheat Sheet Series",
         "https://cheatsheetseries.owasp.org/"),
        ("Overview of ASP.NET Core security",
         "https://learn.microsoft.com/en-us/aspnet/core/security/"),
        ("Prevent Cross-Site Scripting (XSS) in ASP.NET Core",
         "https://learn.microsoft.com/en-us/aspnet/core/security/cross-site-scripting"),
    ])
