# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "Authentication va Authorization. Ularning farqlari."
CATEGORY = "Auth"
TITLE = "Authentication va Authorization"
SUBTITLE = "Kim ekani va nimaga ruxsati borligi"
FILENAME = "Authentication va Authorization farqlari.docx"


def build(d):
    h1(d, "1. Ikki savol, ikki javob")

    para(d, "**Authentication** (autentifikatsiya) bitta savolga javob "
            "beradi: *bu kim?* Foydalanuvchi o'zi aytgan shaxs ekanini "
            "isbotlaydi — parol, token, sertifikat yoki barmoq izi bilan.")

    para(d, "**Authorization** (avtorizatsiya) boshqa savolga javob beradi: "
            "*bu odamga shu ishni qilish ruxsat etilganmi?* Kim ekani "
            "allaqachon ma'lum, endi huquq tekshiriladi.")

    para(d, "Tartib har doim shunday: avval autentifikatsiya, keyin "
            "avtorizatsiya. Kim ekanini bilmasdan ruxsatni tekshirib "
            "bo'lmaydi.")

    table(d, ["", "Authentication", "Authorization"],
          [["Savol", "Bu kim?", "Nimaga ruxsati bor?"],
           ["Qachon", "Birinchi", "Ikkinchi"],
           ["Natija", "Shaxs aniqlandi yoki yo'q", "Ruxsat bor yoki yo'q"],
           ["HTTP kodi", "`401 Unauthorized`", "`403 Forbidden`"],
           ["Qayerda saqlanadi", "Token, cookie, sessiya",
            "Rol, claim, siyosat, ACL"]],
          widths=[4.0, 5.2, 5.3])

    note(d, "Atama noaniqligi",
         "HTTP `401` kodi \"Unauthorized\" deb nomlanadi, lekin u aslida "
         "**autentifikatsiya** yo'qligini bildiradi. Avtorizatsiya "
         "muammosi `403 Forbidden` bilan ifodalanadi. Bu nomlashdagi "
         "tarixiy xato va uni eslab qolish kerak.")

    # ───────────────────────────────────────────
    h1(d, "2. Nega farqni bilish amalda muhim")

    para(d, "Mijoz tomoni bu ikki kodga boshqacha munosabat bildiradi. "
            "`401` kelganda login sahifasiga yuborish yoki token'ni "
            "yangilash kerak. `403` kelganda esa qayta login qilish "
            "yordam bermaydi — foydalanuvchiga \"ruxsatingiz yo'q\" deb "
            "aytish kerak.")

    para(d, "Ikkisini aralashtirish tipik xatolarga olib keladi: `403` ga "
            "javoban mijoz cheksiz qayta login qilishga urinadi, yoki "
            "`401` da foydalanuvchiga \"sizga ruxsat berilmagan\" degan "
            "chalg'ituvchi xabar ko'rsatiladi.")

    # ───────────────────────────────────────────
    h1(d, "3. ASP.NET Core da qanday amalga oshiriladi")

    para(d, "Ikki alohida middleware bor va ularning tartibi qat'iy:")

    code(d, """app.UseRouting();

app.UseAuthentication();    // token/cookie o'qiladi, User to'ldiriladi
app.UseAuthorization();     // endpoint talablari tekshiriladi

app.MapControllers();""")

    para(d, "`UseAuthentication()` so'rovdan token yoki cookie'ni o'qib, "
            "`HttpContext.User` ni to'ldiradi. U **hech kimni rad etmaydi** — "
            "token bo'lmasa, `User` shunchaki anonim bo'ladi.")

    para(d, "`UseAuthorization()` esa tanlangan endpoint'ning talablarini "
            "tekshiradi va kerak bo'lsa `401` yoki `403` qaytaradi.")

    note(d, "Tartib xatosi",
         "`UseAuthorization()` ni `UseRouting()` dan oldin qo'ysam, hech "
         "qanday xato chiqmaydi — avtorizatsiya shunchaki **ishlamaydi**, "
         "chunki u endpoint metadata'sini o'qiy olmaydi. Bu jim "
         "xavfsizlik muammosi.")

    # ───────────────────────────────────────────
    h1(d, "4. Claim va ClaimsPrincipal")

    para(d, "Autentifikatsiya natijasi — `ClaimsPrincipal`. U "
            "foydalanuvchi haqidagi tasdiqlar (claim) to'plami:")

    code(d, """var claims = new List<Claim>
{
    new(ClaimTypes.NameIdentifier, user.Id.ToString()),
    new(ClaimTypes.Name, user.UserName),
    new(ClaimTypes.Email, user.Email),
    new(ClaimTypes.Role, "Manager"),
    new("branch_id", user.BranchId.ToString()),
    new("permission", "order:approve")
};

var identity = new ClaimsIdentity(claims, "jwt");
var principal = new ClaimsPrincipal(identity);""")

    para(d, "Claim — \"bu foydalanuvchi haqida nima ma'lum\" degan fakt. "
            "Rol ham aslida claim, shunchaki maxsus turi.")

    code(d, """// Controller ichida o'qish
var userId = User.FindFirst(ClaimTypes.NameIdentifier)?.Value;
var branchId = User.FindFirst("branch_id")?.Value;
var isManager = User.IsInRole("Manager");""")

    # ───────────────────────────────────────────
    h1(d, "5. Avtorizatsiyaning uch darajasi")

    h2(d, "1. Oddiy autentifikatsiya talabi")

    code(d, """[Authorize]                          // kirgan bo'lishi yetarli
public class OrdersController : ControllerBase
{
    [AllowAnonymous]                 // bu action hamma uchun ochiq
    [HttpGet("public-stats")]
    public IActionResult Stats() => Ok();
}""")

    h2(d, "2. Rol yoki siyosat bo'yicha")

    code(d, """[Authorize(Roles = "Manager,Admin")]
public IActionResult Approve(int id) => Ok();""")

    para(d, "Rolni atributga matn sifatida yozish ishlaydi, lekin men "
            "**siyosat** (policy) ni afzal ko'raman — u ruxsatni koddan "
            "ajratadi:")

    code(d, """builder.Services.AddAuthorizationBuilder()
    .AddPolicy("CanApproveOrders", policy =>
        policy.RequireClaim("permission", "order:approve"))
    .AddPolicy("BranchManager", policy =>
        policy.RequireRole("Manager").RequireClaim("branch_id"));""")

    code(d, """[Authorize(Policy = "CanApproveOrders")]
public IActionResult Approve(int id) => Ok();""")

    para(d, "Shunda rol o'zgarsa yoki yangi rol qo'shilsa, faqat siyosat "
            "ta'rifi o'zgaradi — controller'lar tegilmaydi.")

    h2(d, "3. Resursga bog'liq avtorizatsiya")

    para(d, "Eng muhim daraja va eng ko'p esdan chiqadigani. \"Faqat o'z "
            "buyurtmasini ko'rsin\" degan qoidani atribut bilan ifodalab "
            "bo'lmaydi, chunki qaror aniq obyektga bog'liq:")

    code(d, """[HttpGet("{id:int}")]
public async Task<IActionResult> GetById(int id, CancellationToken ct)
{
    var order = await _service.FindAsync(id, ct);
    if (order is null) return NotFound();

    var result = await _authorization.AuthorizeAsync(User, order, "OrderOwner");
    if (!result.Succeeded) return Forbid();

    return Ok(order.ToDto());
}""")

    code(d, """public sealed class OrderOwnerHandler
    : AuthorizationHandler<OperationAuthorizationRequirement, Order>
{
    protected override Task HandleRequirementAsync(
        AuthorizationHandlerContext context,
        OperationAuthorizationRequirement requirement,
        Order resource)
    {
        var userId = context.User.FindFirst(ClaimTypes.NameIdentifier)?.Value;

        if (userId == resource.CustomerId.ToString() || context.User.IsInRole("Admin"))
            context.Succeed(requirement);

        return Task.CompletedTask;
    }
}""")

    # ───────────────────────────────────────────
    h1(d, "6. Eng ko'p uchraydigan xato: IDOR")

    para(d, "Autentifikatsiya bor, avtorizatsiya yo'q — bu OWASP "
            "ro'yxatida birinchi o'rinda turadigan muammo. "
            "Kod shunday ko'rinadi:")

    code(d, """// ZAIF: token to'g'ri, lekin bu buyurtma kimga tegishli?
[Authorize]
[HttpGet("{id:int}")]
public async Task<IActionResult> GetById(int id, CancellationToken ct)
    => Ok(await _db.Orders.FindAsync([id], ct));""")

    para(d, "Har qanday tizimga kirgan foydalanuvchi `id` ni o'zgartirib "
            "boshqa odamning buyurtmasini ko'ra oladi. `[Authorize]` bu "
            "yerda hech narsa qilmaydi — u faqat \"kirgan bo'lsin\" deydi.")

    para(d, "Eng ishonchli yechim — egalikni **so'rovning o'ziga** "
            "qo'shish, shunda tekshiruvni unutish imkoni qolmaydi:")

    code(d, """var order = await _db.Orders
    .Where(o => o.Id == id && o.CustomerId == _currentUser.Id)
    .FirstOrDefaultAsync(ct);

return order is null ? NotFound() : Ok(order.ToDto());""")

    note(d, "Mening qoidam",
         "Avtorizatsiya tekshiruvini har bir controller'da qo'lda yozish "
         "41-chi endpoint'da albatta esdan chiqadi. Shuning uchun uni "
         "majburlaydigan mexanizm qo'yishga harakat qilaman: global "
         "`[Authorize]` filtri, so'rovga egalik filtri, yoki EF query "
         "filtri.")

    sources(d, [
        ("Overview of ASP.NET Core authentication",
         "https://learn.microsoft.com/en-us/aspnet/core/security/authentication/"),
        ("Introduction to authorization in ASP.NET Core",
         "https://learn.microsoft.com/en-us/aspnet/core/security/authorization/introduction"),
        ("Resource-based authorization",
         "https://learn.microsoft.com/en-us/aspnet/core/security/authorization/resourcebased"),
        ("OWASP Top 10 — Broken Access Control",
         "https://owasp.org/Top10/A01_2021-Broken_Access_Control/"),
    ])
