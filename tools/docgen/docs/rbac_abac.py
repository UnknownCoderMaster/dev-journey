# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "Role-based access control (RBAC), Attribute-based access control (ABAC)"
CATEGORY = "Auth"
TITLE = "RBAC va ABAC"
SUBTITLE = "Rol bo'yicha va atribut bo'yicha ruxsatlarni boshqarish"
FILENAME = "Role-based access control (RBAC), Attribute-based access control (ABAC).docx"


def build(d):
    h1(d, "1. Ikki yondashuvning mohiyati")

    para(d, "Avtorizatsiya — foydalanuvchi nima qilishga haqli ekanini aniqlash. "
            "Buni tashkil qilishning ikki asosiy modeli mavjud.")

    para(d, "**RBAC** da ruxsat rolga bog'lanadi: \"administrator o'chira oladi\". "
            "Foydalanuvchiga rol beriladi va shu orqali ruxsat ham o'tadi.")

    para(d, "**ABAC** da ruxsat atributlar asosida hisoblanadi: \"foydalanuvchi "
            "hujjat muallifi bo'lsa va hujjat hali tasdiqlanmagan bo'lsa, "
            "o'zgartira oladi\". Bu yerda rol emas, kontekst hal qiladi.")

    table(d, ["Jihat", "RBAC", "ABAC"],
          [["Qaror asosi", "Rol", "Foydalanuvchi, resurs va muhit atributlari"],
           ["Tushunarliligi", "Yuqori", "Pastroq"],
           ["Moslashuvchanligi", "Cheklangan", "Yuqori"],
           ["Qoidalar soni", "Kam", "Ko'payib ketishi mumkin"],
           ["Audit qilish", "Oson", "Murakkab"]],
          widths=[3.6, 4.2, 7.7])

    note(d, "Amalda ular qarama-qarshi emas:",
         "Men ko'pincha ikkalasini birga ishlataman. Rol qo'pol filtr beradi — "
         "\"faqat menejerlar bu bo'limga kira oladi\". Atribut esa nozik qaror "
         "qabul qiladi — \"lekin faqat o'z filiali ma'lumotlarini ko'radi\". "
         "Bittasini tanlash shart emas.")

    # ───────────────────────────────────────────
    h1(d, "2. RBAC")

    h2(d, "2.1 Oddiy ko'rinishi")

    code(d, """[Authorize(Roles = "Admin")]
public class AdminController : ControllerBase { }

[Authorize(Roles = "Admin,Manager")]     // yoki shartli
[HttpGet]
public async Task<IActionResult> GetReports() => ...;""")

    para(d, "Vergul bilan ajratilgan rollar \"yoki\" ma'nosini beradi. \"Va\" kerak "
            "bo'lsa, atributni ikki marta yozish kerak:")

    code(d, """[Authorize(Roles = "Manager")]
[Authorize(Roles = "Verified")]          // ikkalasi ham bo'lishi shart""")

    h2(d, "2.2 RBAC ning muammosi")

    para(d, "Loyiha o'sgani sayin rollar soni ortadi. \"Manager\" roli bir bo'limda "
            "bir narsani, boshqasida boshqa narsani anglatadi. Natijada "
            "`SeniorManagerNorthRegion` kabi rollar paydo bo'ladi.")

    note(d, "Bu muammoni men ham ko'rganman:",
         "Rollar ro'yxati yigirmaga yaqinlashganda, kimga nima ruxsat borligini "
         "hech kim aniq ayta olmay qoladi. Yangi rol qo'shish oson, olib tashlash "
         "esa qo'rqinchli — chunki u qayerda ishlatilayotgani noma'lum.")

    h2(d, "2.3 Ruxsatga asoslangan yondashuv")

    para(d, "Yechim — rolni to'g'ridan-to'g'ri tekshirmasdan, **ruxsatni** "
            "tekshirish. Rol esa ruxsatlar to'plamiga aylanadi:")

    code(d, """Rol: Admin      →  books.read, books.write, books.delete, users.manage
Rol: Editor     →  books.read, books.write
Rol: Viewer     →  books.read""")

    code(d, """[Authorize(Policy = "books.delete")]
[HttpDelete("{id:int}")]
public async Task<IActionResult> Delete(int id) => ...;""")

    code(d, """// Barcha ruxsatlarni siyosat sifatida ro'yxatdan o'tkazish
foreach (var permission in Permissions.All)
{
    builder.Services.AddAuthorizationBuilder()
        .AddPolicy(permission, policy =>
            policy.RequireClaim("permission", permission));
}""")

    note(d, "Bu o'zgarish nima beradi:",
         "Endi yangi rol qo'shilganda kodga tegish shart emas — faqat ruxsatlar "
         "to'plami o'zgaradi. Kod esa \"o'chirish ruxsati bormi\" deb so'raydi, "
         "\"admin mi\" deb emas. Bu ikki savolning farqi loyiha kattalashganda "
         "juda sezilarli bo'ladi.")

    # ───────────────────────────────────────────
    h1(d, "3. ABAC va siyosatlar")

    para(d, "ASP.NET Core da ABAC siyosatlar (policy) va talablar (requirement) "
            "orqali amalga oshiriladi.")

    h2(d, "3.1 Oddiy siyosat")

    code(d, """builder.Services.AddAuthorizationBuilder()
    .AddPolicy("AtLeast18", policy =>
        policy.RequireAssertion(ctx =>
        {
            var claim = ctx.User.FindFirst("birthdate");
            if (claim is null) return false;

            var age = DateTime.UtcNow.Year -
                      DateTime.Parse(claim.Value).Year;
            return age >= 18;
        }));""")

    h2(d, "3.2 Resursga bog'liq avtorizatsiya")

    para(d, "Ko'pincha qaror resursning o'ziga bog'liq bo'ladi — uni atribut "
            "sifatida qarash mumkin:")

    code(d, """public class DocumentOwnerRequirement : IAuthorizationRequirement { }

public class DocumentOwnerHandler
    : AuthorizationHandler<DocumentOwnerRequirement, Document>
{
    protected override Task HandleRequirementAsync(
        AuthorizationHandlerContext context,
        DocumentOwnerRequirement requirement,
        Document document)
    {
        var userId = context.User.FindFirstValue(ClaimTypes.NameIdentifier);

        var isOwner = document.AuthorId.ToString() == userId;
        var isDraft = document.Status == DocumentStatus.Draft;

        if (isOwner && isDraft)
            context.Succeed(requirement);

        return Task.CompletedTask;
    }
}""")

    code(d, """builder.Services.AddSingleton<IAuthorizationHandler, DocumentOwnerHandler>();

builder.Services.AddAuthorizationBuilder()
    .AddPolicy("CanEditDocument", p =>
        p.Requirements.Add(new DocumentOwnerRequirement()));""")

    code(d, """[HttpPut("{id:int}")]
public async Task<IActionResult> Update(
    int id, UpdateDocumentDto dto,
    [FromServices] IAuthorizationService auth)
{
    var document = await _repo.GetAsync(id);
    if (document is null) return NotFound();

    var result = await auth.AuthorizeAsync(User, document, "CanEditDocument");
    if (!result.Succeeded) return Forbid();

    ...
}""")

    note(d, "Nega bu tekshiruv kontrollerda:",
         "Atribut sifatidagi `[Authorize]` so'rov boshida ishlaydi va o'sha paytda "
         "resurs hali yuklanmagan bo'ladi. Resursga bog'liq qaror esa resursni "
         "ko'rmasdan qabul qilinmaydi. Shuning uchun u metod ichida, ma'lumot "
         "olingandan keyin tekshiriladi.")

    h2(d, "3.3 Bir nechta handler")

    para(d, "Bitta talab uchun bir nechta handler yozish mumkin — ulardan bittasi "
            "`Succeed` chaqirsa, talab bajarilgan hisoblanadi:")

    code(d, """// Hujjat egasi tahrirlay oladi
public class OwnerHandler : AuthorizationHandler<EditRequirement, Document> { ... }

// Administrator ham tahrirlay oladi
public class AdminOverrideHandler : AuthorizationHandler<EditRequirement, Document>
{
    protected override Task HandleRequirementAsync(
        AuthorizationHandlerContext context,
        EditRequirement requirement,
        Document resource)
    {
        if (context.User.IsInRole("Admin"))
            context.Succeed(requirement);

        return Task.CompletedTask;
    }
}""")

    para(d, "Agar biror handler `context.Fail()` chaqirsa, boshqalari `Succeed` "
            "qilsa ham natija rad etilgan bo'ladi.")

    # ───────────────────────────────────────────
    h1(d, "4. Ma'lumot darajasida cheklash")

    para(d, "Avtorizatsiya faqat \"ruxsat bormi\" degan savol emas — \"qaysi "
            "yozuvlarni ko'ra oladi\" degan savol ham bor. Buni so'rov darajasida "
            "hal qilish kerak:")

    code(d, """var query = _db.Orders.AsQueryable();

if (!User.IsInRole("Admin"))
{
    var branchId = int.Parse(User.FindFirstValue("branch_id")!);
    query = query.Where(o => o.BranchId == branchId);
}

var items = await query.ToListAsync(ct);""")

    note(d, "Bu joyni unutish keng tarqalgan xato:",
         "Endpoint `[Authorize]` bilan himoyalangan, lekin ichkarida hamma "
         "ma'lumot qaytariladi. Foydalanuvchi faqat identifikatorni o'zgartirib, "
         "boshqa filialning buyurtmasini ko'ra oladi. Bu OWASP ro'yxatidagi "
         "\"Broken Access Control\" ning eng tipik ko'rinishi.")

    para(d, "EF Core da buni global filtr bilan avtomatlashtirish ham mumkin:")

    code(d, """modelBuilder.Entity<Order>()
    .HasQueryFilter(o => o.BranchId == _currentUser.BranchId);""")

    # ───────────────────────────────────────────
    h1(d, "5. Qaysi modelni tanlash")

    bullets(d, [
        "**Kichik tizim, aniq rollar** — oddiy RBAC yetarli.",
        "**Rollar soni o'sib borayotgan bo'lsa** — ruxsatga asoslangan RBAC.",
        "**Qaror resurs holatiga bog'liq bo'lsa** — ABAC, resursga bog'liq "
        "handler lar bilan.",
        "**Ko'p ijarachi tizim** — ABAC va ma'lumot darajasidagi filtr majburiy.",
    ])

    note(d, "Bir maslahatni o'zimga qoida qilganman:",
         "Avtorizatsiya qoidalarini kod bo'ylab tarqatib yubormaslik kerak. Agar "
         "\"kim nimaga haqli\" degan savolga javob berish uchun o'nta faylni "
         "ochishim kerak bo'lsa, demak tuzilma noto'g'ri. Qoidalar bir joyda "
         "to'planib, kod esa ularni faqat chaqirishi lozim.")

    # ───────────────────────────────────────────
    h1(d, "6. Xulosa")

    bullets(d, [
        "RBAC ruxsatni rolga, ABAC esa atributlarga bog'laydi.",
        "Ikkalasi birga ishlatilishi mumkin va amalda ko'pincha shunday bo'ladi.",
        "Rol o'rniga ruxsatni tekshirish rollar sonining o'sishi muammosini "
        "yopadi.",
        "Resursga bog'liq qaror `IAuthorizationService` orqali, resurs "
        "yuklangandan keyin tekshiriladi.",
        "Bir nechta handler dan bittasining `Succeed` i yetarli, lekin bitta "
        "`Fail` hammasini bekor qiladi.",
        "Ruxsat tekshiruvi so'rov darajasida ham bo'lishi kerak — aks holda "
        "foydalanuvchi begona yozuvlarni ko'rishi mumkin.",
        "Avtorizatsiya qoidalari bir joyda to'planishi lozim.",
    ])

    sources(d, [
        ("Introduction to authorization in ASP.NET Core",
         "https://learn.microsoft.com/en-us/aspnet/core/security/authorization/introduction"),
        ("Policy-based authorization in ASP.NET Core",
         "https://learn.microsoft.com/en-us/aspnet/core/security/authorization/policies"),
        ("Resource-based authorization in ASP.NET Core",
         "https://learn.microsoft.com/en-us/aspnet/core/security/authorization/resourcebased"),
        ("OWASP Top 10 — A01:2021 Broken Access Control",
         "https://owasp.org/Top10/A01_2021-Broken_Access_Control/"),
    ])
