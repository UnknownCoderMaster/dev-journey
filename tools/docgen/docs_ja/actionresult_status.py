# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "ActionResult,Status Codes,Routing"
CATEGORY = "ASP.NET"
TITLE = "ActionResult, Status Kodlar va Routing"
SUBTITLE = "So'rovni action'ga bog'lash va to'g'ri javob qaytarish"
FILENAME = "ActionResult, Status Codes, Routing.docx"


def build(d):
    h1(d, "1. Action natijasini qanday qaytaraman")

    para(d, "Action metodi javobni to'g'ridan-to'g'ri yozmaydi — u **natija "
            "obyektini** qaytaradi va framework uni HTTP javobiga aylantiradi. "
            "Bu ajratish test yozishni osonlashtiradi: natijani tekshirish "
            "uchun HTTP server ko'tarish kerak emas.")

    code(d, """[HttpGet("{id:int}")]
public async Task<ActionResult<OrderDto>> GetById(int id, CancellationToken ct)
{
    var order = await _service.FindAsync(id, ct);
    if (order is null) return NotFound();

    return Ok(order);
}""")

    para(d, "`ActionResult<T>` ikki narsani birdan beradi: natija turi "
            "hujjatga tushadi (OpenAPI uchun) va status kodni erkin "
            "tanlash mumkin.")

    # ───────────────────────────────────────────
    h1(d, "2. Eng ko'p ishlatadigan natija yordamchilari")

    code(d, """return Ok(dto);                   // 200 + tana
return Ok();                      // 200, tanasiz
return NoContent();               // 204 — muvaffaqiyat, qaytaradigan narsa yo'q
return NotFound();                // 404
return BadRequest("Sabab");       // 400
return Conflict();                // 409
return Forbid();                  // 403
return Unauthorized();            // 401

// 201 + Location header
return CreatedAtAction(nameof(GetById), new { id = order.Id }, dto);

// 202 — qabul qilindi, lekin hali bajarilmadi
return Accepted();

// fayl
return File(bytes, "application/pdf", "hisobot.pdf");

// validatsiya xatolari
return ValidationProblem(ModelState);""")

    para(d, "`CreatedAtAction` ni afzal ko'raman, chunki u `Location` "
            "header'ini **action nomidan** hisoblaydi — ya'ni marshrut "
            "o'zgarsa havola ham o'zi to'g'rilanadi. URL ni qo'lda yozish "
            "esa tez orada eskiradi.")

    # ───────────────────────────────────────────
    h1(d, "3. Status kodlarni to'g'ri tanlash")

    para(d, "Status kod — API shartnomasining qismi. Mijoz unga qarab qaror "
            "qabul qiladi, shuning uchun noto'g'ri kod jiddiy muammo.")

    table(d, ["Kod", "Ma'nosi", "Qachon ishlataman"],
          [["`200`", "OK", "Muvaffaqiyatli o'qish yoki yangilash"],
           ["`201`", "Created", "Yangi resurs yaratildi, `Location` bilan"],
           ["`202`", "Accepted", "Navbatga qo'yildi, keyinroq bajariladi"],
           ["`204`", "No Content", "`DELETE` yoki javob tanasi kerak bo'lmagan `PUT`"],
           ["`400`", "Bad Request", "So'rov shakli yoki qiymati noto'g'ri"],
           ["`401`", "Unauthorized", "Kim ekani aniqlanmadi (token yo'q/yaroqsiz)"],
           ["`403`", "Forbidden", "Kim ekani ma'lum, lekin ruxsat yo'q"],
           ["`404`", "Not Found", "Resurs yo'q"],
           ["`409`", "Conflict", "Joriy holat bilan ziddiyat"],
           ["`422`", "Unprocessable", "Shakl to'g'ri, lekin mazmun qoidaga qarshi"],
           ["`500`", "Server Error", "Kutilmagan xato"]],
          widths=[1.9, 3.6, 9.0])

    h2(d, "401 va 403 ni aralashtirmaslik")

    para(d, "Bu eng ko'p qilinadigan xato. `401` — \"sen kimligingni "
            "bilmayman, autentifikatsiya qil\". `403` — \"kimligingni "
            "bilaman, lekin bu senga ruxsat etilmagan\". Mijoz tomonida "
            "farq muhim: `401` da login sahifasiga yuborish kerak, `403` da "
            "esa yo'q — qayta login qilish yordam bermaydi.")

    h2(d, "400 va 422")

    para(d, "`400` — so'rovni tushunib bo'lmadi: JSON buzilgan, majburiy "
            "maydon yo'q, tip mos emas. `422` — so'rov o'qildi, lekin biznes "
            "qoidasi buzildi: \"yetkazib berish sanasi o'tgan kunga "
            "qo'yilgan\". Amalda ko'p loyihada faqat `400` ishlatiladi va "
            "bu ham qabul qilinadigan yechim — muhimi izchillik.")

    note(d, "Eslatma",
         "Xato javoblarida ProblemDetails (RFC 9457) formatidan "
         "foydalanaman: `type`, `title`, `status`, `detail`, `instance`. "
         "Bu standart bo'lgani uchun mijoz har bir API uchun alohida xato "
         "formatini o'rganmaydi.")

    # ───────────────────────────────────────────
    h1(d, "4. Routing — so'rovni action'ga bog'lash")

    para(d, "ASP.NET Core da ikki yondashuv bor, lekin API uchun amalda "
            "faqat bittasi ishlatiladi.")

    h2(d, "Attribute routing")

    code(d, """[ApiController]
[Route("api/[controller]")]            // api/orders
public class OrdersController : ControllerBase
{
    [HttpGet]                          // GET api/orders
    public Task<ActionResult<List<OrderDto>>> List() => ...;

    [HttpGet("{id:int}")]              // GET api/orders/42
    public Task<ActionResult<OrderDto>> GetById(int id) => ...;

    [HttpGet("{id:int}/items")]        // GET api/orders/42/items
    public Task<ActionResult<List<ItemDto>>> Items(int id) => ...;

    [HttpPost]                         // POST api/orders
    public Task<ActionResult<OrderDto>> Create(CreateOrderRequest request) => ...;
}""")

    para(d, "`[controller]` token controller nomidan \"Controller\" "
            "qo'shimchasini olib tashlab qo'yadi. Bu qulay, lekin controller "
            "nomini o'zgartirsam URL ham o'zgaradi — ommaviy API da buni "
            "hisobga olish kerak, shuning uchun ba'zan yo'lni aniq "
            "yozishni afzal ko'raman.")

    h2(d, "Conventional routing")

    code(d, """app.MapControllerRoute(
    name: "default",
    pattern: "{controller=Home}/{action=Index}/{id?}");""")

    para(d, "Bu shakl MVC va server tomonida HTML render qiladigan "
            "ilovalarda qulay. API uchun esa attribute routing aniqroq: "
            "har bir endpoint o'z joyida ko'rinadi.")

    # ───────────────────────────────────────────
    h1(d, "5. Route constraint — marshrut cheklovlari")

    para(d, "Constraint noto'g'ri so'rovni action'ga yetib bormasdan "
            "to'sadi. `{id:int}` yozilsa, `api/orders/abc` so'rovi 404 "
            "beradi va action umuman chaqirilmaydi.")

    table(d, ["Constraint", "Misol", "Mos keladi"],
          [["`int`", "`{id:int}`", "42"],
           ["`guid`", "`{id:guid}`", "UUID"],
           ["`min`, `max`", "`{page:min(1)}`", "1 va kattalari"],
           ["`range`", "`{size:range(1,100)}`", "1..100"],
           ["`length`", "`{code:length(3)}`", "UZS"],
           ["`alpha`", "`{name:alpha}`", "faqat harflar"],
           ["`regex`", "`{sku:regex(^[A-Z]{{2}}\\d{{4}}$)}`", "AB1234"],
           ["`?`", "`{id?}`", "ixtiyoriy segment"]],
          widths=[3.0, 6.0, 5.5])

    para(d, "Constraint — validatsiya o'rnini bosmaydi. U faqat marshrut "
            "tanlashga yordam beradi: masalan bir xil yo'lda `{id:int}` va "
            "`{slug}` ikki alohida action'ga ketishi mumkin.")

    # ───────────────────────────────────────────
    h1(d, "6. Marshrut noaniqligi (ambiguity)")

    para(d, "Ikki action bir xil so'rovga mos kelsa, ilova ishga tushganda "
            "emas, **shu so'rov kelganda** xato beradi:")

    code(d, """// Ikkisi ham GET api/orders/search ga mos keladi
[HttpGet("search")]
public IActionResult SearchByName(string name) => ...;

[HttpGet("search")]
public IActionResult SearchByDate(DateOnly date) => ...;

// AmbiguousMatchException""")

    para(d, "Query string parametrlari marshrut tanlashga ta'sir qilmaydi — "
            "bu ko'p odamni chalg'itadi. To'g'ri yechim: yo'lni ajratish "
            "(`search/by-name`) yoki bitta action yasab, parametrlarni "
            "ixtiyoriy qilish.")

    # ───────────────────────────────────────────
    h1(d, "7. Model binding — qiymat qayerdan keladi")

    para(d, "Framework parametrlarni avtomatik to'ldiradi va manbani "
            "o'zi tanlaydi. `[ApiController]` bilan qoidalar shunday:")

    bullets(d, [
        "Marshrut shablonida nomi bor bo'lsa — `[FromRoute]`.",
        "Oddiy tur (`int`, `string`, `DateOnly`) bo'lsa — `[FromQuery]`.",
        "Murakkab tur bo'lsa — `[FromBody]`, ya'ni JSON tanasidan.",
        "`IFormFile` bo'lsa — `[FromForm]`.",
    ])

    code(d, """[HttpGet("{id:int}/items")]
public Task<ActionResult<PagedResult<ItemDto>>> Items(
    int id,                                   // marshrutdan
    [FromQuery] int page = 1,                 // query string dan
    [FromQuery] int size = 20,
    [FromHeader(Name = "X-Correlation-Id")] string? correlationId = null,
    CancellationToken ct = default)
    => ...;""")

    note(d, "Diqqat",
         "Bitta action'da faqat **bitta** `[FromBody]` parametri bo'lishi "
         "mumkin, chunki so'rov tanasi bir marta o'qiladi. Ikkitasi "
         "yozilsa, ish vaqtida xato chiqadi.")

    sources(d, [
        ("Routing to controller actions",
         "https://learn.microsoft.com/en-us/aspnet/core/mvc/controllers/routing"),
        ("Controller action return types",
         "https://learn.microsoft.com/en-us/aspnet/core/web-api/action-return-types"),
        ("HTTP response status codes — MDN",
         "https://developer.mozilla.org/en-US/docs/Web/HTTP/Status"),
        ("Model binding in ASP.NET Core",
         "https://learn.microsoft.com/en-us/aspnet/core/mvc/models/model-binding"),
    ])
