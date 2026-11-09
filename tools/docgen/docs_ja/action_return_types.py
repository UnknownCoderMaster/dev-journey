# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = ("Controller action return types, ActionResult vs IActionResult, "
         "Synchronous and Asynchronous action, HttpResults type")
CATEGORY = "ASP.NET"
TITLE = "Action Qaytish Turlari"
SUBTITLE = "IActionResult, ActionResult<T>, HttpResults va async action"
FILENAME = "Controller action return types, ActionResult vs IActionResult.docx"


def build(d):
    h1(d, "1. To'rt xil qaytish turi")

    para(d, "Action metodi to'rt xil ko'rinishda natija qaytarishi mumkin va "
            "ularning har biri boshqa narsani yo'qotadi yoki beradi.")

    h2(d, "1. Aniq tur")

    code(d, """[HttpGet]
public async Task<List<OrderDto>> List(CancellationToken ct)
    => await _service.ListAsync(ct);""")

    para(d, "Eng sodda shakl. Natija avtomatik `200 OK` bo'lib "
            "serializatsiya qilinadi. Lekin bu yerda `404` yoki `400` "
            "qaytarish imkoni yo'q — faqat exception tashlash mumkin.")

    h2(d, "2. IActionResult")

    code(d, """[HttpGet("{id:int}")]
public async Task<IActionResult> GetById(int id, CancellationToken ct)
{
    var order = await _service.FindAsync(id, ct);
    if (order is null) return NotFound();

    return Ok(order);
}""")

    para(d, "Status kodni erkin tanlash mumkin, lekin **natija turi "
            "yashirinadi**. OpenAPI hujjati nima qaytarilishini bilmaydi, "
            "shuning uchun uni `[ProducesResponseType]` bilan qo'lda "
            "aytib berish kerak bo'ladi.")

    h2(d, "3. ActionResult<T>")

    code(d, """[HttpGet("{id:int}")]
public async Task<ActionResult<OrderDto>> GetById(int id, CancellationToken ct)
{
    var order = await _service.FindAsync(id, ct);
    if (order is null) return NotFound();

    return order;          // Ok(order) bilan bir xil — yashirin aylantirish
}""")

    para(d, "Ikkisining yaxshi tomonini birlashtiradi: status kod erkin va "
            "tur hujjatga tushadi. Yashirin aylantirish (`implicit "
            "conversion`) tufayli `Ok()` ni yozish ham shart emas.")

    para(d, "Shuning uchun controller'larda standart tanlovim — "
            "`ActionResult<T>`.")

    h2(d, "4. HttpResults (Results)")

    code(d, """app.MapGet("/api/orders/{id:int}",
    async Task<Results<Ok<OrderDto>, NotFound>> (
        int id, IOrderService service, CancellationToken ct) =>
    {
        var order = await service.FindAsync(id, ct);
        return order is null
            ? TypedResults.NotFound()
            : TypedResults.Ok(order);
    });""")

    para(d, "Minimal API uchun mo'ljallangan. `Results<Ok<T>, NotFound>` "
            "shakli eng aniq: mumkin bo'lgan hamma natija imzoda yozilgan, "
            "shuning uchun OpenAPI hujjati atributsiz to'g'ri bo'ladi va "
            "kompilyator ruxsat etilmagan natijani qaytarishga yo'l "
            "qo'ymaydi.")

    note(d, "Farq",
         "`Results.Ok()` (statik klass) `IResult` qaytaradi — tur "
         "ma'lumoti yo'q. `TypedResults.Ok()` esa `Ok<T>` qaytaradi — tur "
         "saqlanadi. Yangi kodda `TypedResults` ni tanlayman.")

    # ───────────────────────────────────────────
    h1(d, "2. Taqqoslash")

    table(d, ["Tur", "Status kod erkinligi", "OpenAPI uchun atribut kerakmi"],
          [["Aniq tur (`T`)", "Yo'q", "Yo'q"],
           ["`IActionResult`", "Ha", "Ha"],
           ["`ActionResult<T>`", "Ha", "Qisman — xato kodlari uchun"],
           ["`Results<...>`", "Ha", "Yo'q"]],
          widths=[4.0, 4.6, 5.9])

    # ───────────────────────────────────────────
    h1(d, "3. Hujjatga tushishini ta'minlash")

    para(d, "Muvaffaqiyatli javob turi `ActionResult<T>` dan ko'rinadi, "
            "lekin xato javoblari ko'rinmaydi. Shuning uchun ularni e'lon "
            "qilaman:")

    code(d, """[HttpGet("{id:int}")]
[ProducesResponseType<OrderDto>(StatusCodes.Status200OK)]
[ProducesResponseType(StatusCodes.Status404NotFound)]
public async Task<ActionResult<OrderDto>> GetById(int id, CancellationToken ct)
    => await _service.FindAsync(id, ct) is { } order ? order : NotFound();""")

    para(d, "Har bir action'ga qo'lda yozish zerikarli, shuning uchun umumiy "
            "xato kodlarini bir joyda e'lon qilish mumkin:")

    code(d, """// Konvensiya orqali — butun controller uchun
[ApiController]
[ProducesResponseType(StatusCodes.Status401Unauthorized)]
[ProducesResponseType(StatusCodes.Status500InternalServerError)]
public class OrdersController : ControllerBase { }""")

    # ───────────────────────────────────────────
    h1(d, "4. Sinxron va asinxron action")

    para(d, "Backend kodda deyarli hamma action asinxron bo'lishi kerak. "
            "Sabab — thread'lar.")

    para(d, "Sinxron action baza javobini kutganda thread **bloklangan** "
            "holatda turadi va boshqa so'rovga xizmat qila olmaydi. Thread "
            "pool cheklangan, shuning uchun bir vaqtda ko'p so'rov kelsa "
            "navbat paydo bo'ladi. Asinxron action esa kutish paytida "
            "thread'ni bo'shatadi.")

    code(d, """// SINXRON: thread baza javobini kutib turadi
[HttpGet]
public List<OrderDto> List() => _service.List();

// ASINXRON: kutish paytida thread bo'shaydi
[HttpGet]
public Task<List<OrderDto>> List(CancellationToken ct) => _service.ListAsync(ct);""")

    h2(d, "Eng xavfli xato: sync over async")

    code(d, """// HECH QACHON shunday yozmaslik kerak
var orders = _service.ListAsync(ct).Result;
var count = _service.CountAsync(ct).GetAwaiter().GetResult();
_service.SaveAsync(ct).Wait();""")

    para(d, "Bu kod thread'ni bloklaydi va yuklama ostida **thread pool "
            "starvation** ga olib keladi: hamma thread kutib turadi, yangi "
            "so'rovlarni bajaradigan hech kim qolmaydi. Natijada ilova "
            "butunlay javob bermay qo'yadi, lekin CPU bo'sh turadi — "
            "diagnostika qilish juda qiyin holat.")

    note(d, "Qoida",
         "Asinxronlik \"yuqoridan pastgacha\" bo'lishi kerak. Zanjirning "
         "bir joyida `.Result` paydo bo'lsa, undan yuqoridagi hamma "
         "`async` ning foydasi yo'qoladi.")

    h2(d, "async void — umuman yozilmaydi")

    para(d, "`async void` metodidagi exception'ni ushlab bo'lmaydi va u "
            "jarayonni qulatadi. Yagona istisno — event handler'lar, lekin "
            "backend kodda ular deyarli uchramaydi.")

    # ───────────────────────────────────────────
    h1(d, "5. ValueTask va ortiqcha async")

    code(d, """// Agar natija ko'pincha keshda bo'lsa, ValueTask arzonroq
public ValueTask<decimal> GetRateAsync(string code, CancellationToken ct)
    => _cache.TryGetValue(code, out decimal rate)
        ? ValueTask.FromResult(rate)
        : new ValueTask<decimal>(FetchAsync(code, ct));""")

    para(d, "`Task` har safar heap da obyekt yaratadi. `ValueTask` esa "
            "natija sinxron tayyor bo'lganda obyekt yaratmaydi. Lekin uning "
            "cheklovlari bor: bir marta `await` qilinishi kerak, qayta "
            "ishlatilmaydi. Shuning uchun uni faqat o'lchov asosida, isbot "
            "bo'lganda ishlataman.")

    para(d, "Yana bir detal — hech narsa kutilmaydigan `async` metod "
            "ortiqcha:")

    code(d, """// Ortiqcha: state machine yaratiladi, lekin foyda yo'q
public async Task<List<Order>> ListAsync(CancellationToken ct)
    => await _repository.ListAsync(ct);

// Toza: Task to'g'ridan-to'g'ri uzatiladi
public Task<List<Order>> ListAsync(CancellationToken ct)
    => _repository.ListAsync(ct);""")

    para(d, "Lekin `using` yoki `try/catch` ichida bo'lsa, `await` ni "
            "saqlab qolish kerak — aks holda resurs natija kelishidan oldin "
            "yopiladi yoki exception ushlanmaydi.")

    sources(d, [
        ("Controller action return types in ASP.NET Core Web API",
         "https://learn.microsoft.com/en-us/aspnet/core/web-api/action-return-types"),
        ("Create responses in Minimal API applications",
         "https://learn.microsoft.com/en-us/aspnet/core/fundamentals/minimal-apis/responses"),
        ("Async guidance — ASP.NET Core",
         "https://learn.microsoft.com/en-us/aspnet/core/fundamentals/best-practices"),
        ("ValueTask",
         "https://learn.microsoft.com/en-us/dotnet/api/system.threading.tasks.valuetask-1"),
    ])
