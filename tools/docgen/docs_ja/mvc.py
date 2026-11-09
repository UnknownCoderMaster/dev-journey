# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "MVC architecture"
CATEGORY = "Architecture"
TITLE = "MVC Arxitekturasi"
SUBTITLE = "Model, View va Controller orasidagi mas'uliyat taqsimoti"
FILENAME = "MVC architecture.docx"


def build(d):
    h1(d, "1. MVC nima uchun paydo bo'lgan")

    para(d, "Interfeys kodi, ma'lumot va biznes mantiqi bir joyda "
            "aralashganda har bir o'zgarish xavfli bo'ladi. Tugmaning rangini "
            "o'zgartirish uchun hisoblash kodiga tegish kerak bo'lsa, bu "
            "muqarrar ravishda xatoga olib keladi.")

    para(d, "MVC mas'uliyatni uchga bo'ladi:")

    bullets(d, [
        "**Model** — ma'lumot va uning qoidalari. Interfeys haqida hech "
        "narsa bilmaydi.",
        "**View** — ma'lumotni ko'rsatish. Qarorlar qabul qilmaydi.",
        "**Controller** — kelgan so'rovni qabul qiladi, modelni ishga "
        "soladi va qaysi view ko'rsatilishini tanlaydi.",
    ])

    para(d, "Asosiy foyda — har bir qism alohida o'zgarishi mumkin. "
            "Ko'rinishni butunlay qayta yozsam ham model tegilmaydi; "
            "ma'lumot manbaini o'zgartirsam, view o'zgarmaydi.")

    # ───────────────────────────────────────────
    h1(d, "2. ASP.NET Core da so'rovning yo'li")

    para(d, "So'rov keladi, routing uni controller va action'ga bog'laydi, "
            "model binding parametrlarni to'ldiradi, action ishni bajaradi va "
            "natijani qaytaradi:")

    code(d, """// 1. Routing: GET /orders/42 -> OrdersController.Details(42)
public class OrdersController(IOrderService service) : Controller
{
    // 2. Model binding: "42" -> int id
    public async Task<IActionResult> Details(int id, CancellationToken ct)
    {
        // 3. Model bilan ishlash
        var order = await service.FindAsync(id, ct);
        if (order is null) return NotFound();

        // 4. View tanlash va modelni unga uzatish
        return View(order);
    }
}""")

    code(d, """@* Views/Orders/Details.cshtml *@
@model OrderDetailsViewModel

<h2>Buyurtma @Model.Number</h2>
<p>Summa: @Model.Total.ToString("N2")</p>

@if (Model.CanCancel)
{
    <form asp-action="Cancel" asp-route-id="@Model.Id" method="post">
        <button type="submit">Bekor qilish</button>
    </form>
}""")

    para(d, "View ichida `@if` bor, lekin u **qaror qabul qilmaydi** — "
            "`CanCancel` qiymati allaqachon hisoblangan va modelda keltirilgan. "
            "Bu farq muhim: view faqat tayyor ma'lumotni ko'rsatadi.")

    # ───────────────────────────────────────────
    h1(d, "3. ViewModel — nega domen modelini to'g'ridan-to'g'ri bermayman")

    para(d, "Domen entity'sini view'ga uzatish qulay ko'rinadi, lekin bir "
            "nechta muammo tug'diradi.")

    bullets(d, [
        "View'ga kerak bo'lmagan maydonlar ham ketadi — ba'zan maxfiy "
        "ma'lumot ham (parol hash'i, ichki izohlar).",
        "View domen tuzilishiga bog'lanadi: entity o'zgarsa, view buziladi.",
        "Ko'rsatish uchun kerakli hisoblangan maydonlar (`CanCancel`, "
        "`FormattedDate`) entity'ga sig'maydi — ular ko'rsatish mantiqi.",
        "Lazy loading yoqilgan bo'lsa, view ichida baza so'rovi ketishi "
        "mumkin va bu N+1 muammosiga olib keladi.",
    ])

    code(d, """public sealed class OrderDetailsViewModel
{
    public int Id { get; init; }
    public string Number { get; init; } = "";
    public decimal Total { get; init; }
    public bool CanCancel { get; init; }
    public IReadOnlyList<OrderLineViewModel> Lines { get; init; } = [];
}""")

    note(d, "Eslatma",
         "ViewModel va DTO yaqin tushunchalar, lekin maqsadi boshqa. DTO — "
         "qatlamlar yoki tizimlar orasida ma'lumot uzatish uchun. ViewModel — "
         "aniq bir sahifaning ehtiyoji uchun, shuning uchun unda "
         "ko'rsatishga xos maydonlar bo'lishi normal.")

    # ───────────────────────────────────────────
    h1(d, "4. Controller nimani qilmasligi kerak")

    para(d, "\"Fat controller\" — eng ko'p uchraydigan muammo. Controller "
            "biznes mantiqini o'ziga yiqqanda uni test qilish qiyin, qayta "
            "ishlatish imkonsiz bo'ladi.")

    code(d, """// YOMON: hamma mantiq controller ichida
[HttpPost]
public async Task<IActionResult> Create(CreateOrderRequest request)
{
    if (request.Items.Count == 0)
        return BadRequest("Bo'sh buyurtma");

    var total = 0m;
    foreach (var item in request.Items)
    {
        var product = await _db.Products.FindAsync(item.ProductId);
        if (product is null) return BadRequest("Mahsulot topilmadi");
        if (product.Stock < item.Quantity) return BadRequest("Zaxira yetmaydi");

        total += product.Price * item.Quantity;
        product.Stock -= item.Quantity;
    }

    if (total > 1_000_000m) total *= 0.95m;
    // ... yana 40 qator
}""")

    para(d, "Shu mantiqni servisga ko'chirganda controller qisqa va "
            "tushunarli bo'lib qoladi:")

    code(d, """[HttpPost]
public async Task<IActionResult> Create(CreateOrderRequest request, CancellationToken ct)
{
    if (!ModelState.IsValid) return ValidationProblem(ModelState);

    var result = await _orderService.CreateAsync(request.ToCommand(), ct);

    return result.IsSuccess
        ? CreatedAtAction(nameof(Details), new { id = result.Value.Id }, result.Value)
        : BadRequest(result.Error);
}""")

    para(d, "Controller'ning vazifasi — **tarjima**: HTTP dunyosidan domen "
            "dunyosiga va qaytib. Qoida sifatida o'zimga shunday savol "
            "beraman: bu kod HTTP bo'lmaganda ham kerak bo'ladimi? "
            "Agar ha — u controller'da turmasligi kerak.")

    # ───────────────────────────────────────────
    h1(d, "5. MVC va Web API farqi")

    para(d, "ASP.NET Core da ikkisi bir xil infratuzilmada ishlaydi, lekin "
            "bazaviy klass va natija turlari farq qiladi:")

    table(d, ["", "MVC", "Web API"],
          [["Bazaviy klass", "`Controller`", "`ControllerBase`"],
           ["Natija", "HTML (`View()`)", "JSON (`Ok()`, obyekt)"],
           ["Validatsiya xatosi", "`ModelState` + sahifa qayta ko'rsatiladi",
            "Avtomatik `400` + ProblemDetails"],
           ["Holat", "TempData, Session ishlatilishi mumkin", "Stateless"]],
          widths=[3.6, 5.4, 5.5])

    para(d, "`Controller` `ControllerBase` dan meros bo'lib, unga `View()`, "
            "`PartialView()`, `ViewBag` kabi ko'rinishga xos a'zolarni "
            "qo'shadi. API yozganda `ControllerBase` ni tanlayman — "
            "keraksiz a'zolar IntelliSense'ni to'ldirmaydi.")

    note(d, "Diqqat",
         "`[ApiController]` atributi qo'yilganda xatti-harakat o'zgaradi: "
         "model validatsiyasi avtomatik bo'ladi va noto'g'ri so'rovda action "
         "umuman chaqirilmaydi. Shuning uchun `if (!ModelState.IsValid)` "
         "tekshiruvi API controller'da ortiqcha bo'lib qoladi.")

    # ───────────────────────────────────────────
    h1(d, "6. MVC ning chegarasi")

    para(d, "MVC so'rovni qabul qilish va javob qaytarishni yaxshi tashkil "
            "qiladi, lekin u **butun ilova arxitekturasi emas**. U faqat "
            "taqdimot qatlamiga tegishli.")

    para(d, "Shuning uchun amalda MVC boshqa qatlamlar bilan birga ishlatiladi: "
            "controller → application servis → domen → ma'lumotlarga kirish. "
            "MVC ning \"M\" harfi bu yerda butun model qatlamini emas, "
            "controller'ga ko'rinadigan qismini bildiradi.")

    para(d, "Loyiha o'sganda controller'lar soni ko'payadi va ularni mavzu "
            "bo'yicha guruhlash kerak bo'ladi. Bunda ikki yondashuv bor: "
            "papkalarni tur bo'yicha (Controllers, Services, Models) yoki "
            "funksional bo'yicha (Orders, Customers, Invoices) ajratish. "
            "Loyiha kattalashganda ikkinchisi qulayroq — bitta o'zgarish "
            "bitta papkada qoladi.")

    sources(d, [
        ("Overview of ASP.NET Core MVC",
         "https://learn.microsoft.com/en-us/aspnet/core/mvc/overview"),
        ("Handle requests with controllers",
         "https://learn.microsoft.com/en-us/aspnet/core/mvc/controllers/actions"),
        ("Views in ASP.NET Core MVC",
         "https://learn.microsoft.com/en-us/aspnet/core/mvc/views/overview"),
    ])
