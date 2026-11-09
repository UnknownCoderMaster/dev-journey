# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "Routing"
CATEGORY = "ASP.NET"
TITLE = "Routing"
SUBTITLE = "Marshrut shablonlari, tanlov tartibi va havola yasash"
FILENAME = "Routing.docx"


def build(d):
    h1(d, "1. Routing qanday ishlaydi")

    para(d, "Routing ikki ishni bajaradi. Birinchisi — **URL matching**: "
            "kelgan so'rov yo'lini shablonlarga solishtirib, qaysi endpoint "
            "bajarilishini aniqlash. Ikkinchisi — **URL generation**: "
            "endpoint nomi va parametrlardan havola yasash.")

    para(d, "Middleware zanjirida ikki bosqich ajratilgan:")

    code(d, """app.UseRouting();        // mos endpoint tanlanadi (hali bajarilmaydi)
app.UseAuthentication();
app.UseAuthorization();  // tanlangan endpoint metadata'siga qarab qaror qiladi
app.MapControllers();    // endpoint bajariladi""")

    para(d, "Tartib muhim: `UseAuthorization()` `UseRouting()` dan **keyin** "
            "turishi kerak, chunki u endpoint'ning `[Authorize]` "
            "metadata'sini o'qiydi. Oldin qo'yilsa, hech qanday xato "
            "chiqmaydi — avtorizatsiya shunchaki ishlamaydi. Bu jim "
            "xavfsizlik muammosi, shuning uchun tartibga alohida e'tibor "
            "beraman.")

    # ───────────────────────────────────────────
    h1(d, "2. Shablon sintaksisi")

    code(d, """"orders"                        // aniq matn
"orders/{id}"                   // parametr
"orders/{id?}"                  // ixtiyoriy parametr
"orders/{id:int}"               // constraint
"orders/{id:int=1}"             // standart qiymat
"files/{*path}"                 // catch-all: qolgan hamma segment
"files/{**path}"                // catch-all, kodlanmagan holda""")

    para(d, "Catch-all parametri fayl yo'llari bilan ishlaganda kerak "
            "bo'ladi, chunki yo'lda bir nechta `/` bo'lishi mumkin. "
            "Lekin u bilan ehtiyot bo'lish kerak: foydalanuvchi bergan "
            "yo'lni to'g'ridan-to'g'ri fayl tizimiga uzatish path "
            "traversal zaifligiga olib keladi.")

    h2(d, "Bir nechta segment va literal")

    code(d, """[HttpGet("api/v{version:apiVersion}/orders/{orderId:int}/items/{itemId:int}")]
public Task<IActionResult> GetItem(int orderId, int itemId) => ...;""")

    # ───────────────────────────────────────────
    h1(d, "3. Endpoint tanlash tartibi")

    para(d, "Bir nechta shablon mos kelsa, framework eng **aniq** "
            "(specific) bo'lganini tanlaydi. Aniqlik mezonlari ketma-ketlikda:")

    bullets(d, [
        "Literal segment parametrdan ustun. `orders/new` `orders/{id}` dan "
        "ustun turadi.",
        "Constraint'li parametr constraint'siz parametrdan ustun. "
        "`{id:int}` `{id}` dan ustun.",
        "Catch-all eng oxirgi o'rinda turadi.",
        "`Order` metadata'si (`[Route(Order = ...)]`) qo'lda tartib "
        "belgilaydi — lekin bunga tayanish kodni mo'rt qiladi.",
    ], numbered=True)

    code(d, """[HttpGet("orders/new")]        // 1. aniq matn — birinchi tekshiriladi
[HttpGet("orders/{id:int}")]   // 2. constraint'li parametr
[HttpGet("orders/{slug}")]     // 3. oddiy parametr""")

    para(d, "Shuning uchun `orders/new` so'rovi `{slug}` ga tushib "
            "ketmaydi — bu kutilgan xatti-harakat va unga ishonish mumkin.")

    note(d, "Diqqat",
         "Mos keladigan ikki endpoint bir xil darajada aniq bo'lsa, so'rov "
         "kelganda `AmbiguousMatchException` chiqadi. Bu ilova ishga "
         "tushganda aniqlanmaydi, shuning uchun har bir yangi marshrutni "
         "sinab ko'rish kerak.")

    # ───────────────────────────────────────────
    h1(d, "4. Route value va parametrlar")

    para(d, "Shablondan ajratilgan qiymatlar `RouteData` ga tushadi va "
            "ulardan action parametrlari to'ldiriladi:")

    code(d, """[HttpGet("branches/{city}/orders/{id:int}")]
public IActionResult Get(string city, int id)
{
    var fromRouteData = RouteData.Values["city"];   // parametr bilan bir xil
    return Ok();
}""")

    para(d, "Parametr nomi shablondagi nom bilan bir xil bo'lishi kerak, "
            "aks holda qiymat to'ldirilmaydi va standart qiymat qoladi — "
            "bu jim xato, shuning uchun nomlarni ehtiyot bilan yozaman.")

    # ───────────────────────────────────────────
    h1(d, "5. URL generation — havolani qo'lda yozmaslik")

    para(d, "URL ni matn sifatida yozish eng mo'rt yechim: marshrut "
            "o'zgarsa, hamma joyda qo'lda to'g'rilash kerak bo'ladi. "
            "Shuning uchun havolani framework hisoblashi kerak.")

    code(d, """// Controller ichida
var url = Url.Action(nameof(GetById), "Orders", new { id = 42 });

// 201 javobida — eng ko'p uchraydigan holat
return CreatedAtAction(nameof(GetById), new { id = order.Id }, dto);

// Nomlangan marshrut bo'yicha
var link = Url.Link("order-details", new { id = 42 });""")

    para(d, "Controller'dan tashqarida (masalan background servisda yoki "
            "email shabloni yasashda) `LinkGenerator` ishlatiladi:")

    code(d, """public sealed class EmailComposer(LinkGenerator links)
{
    public string BuildOrderLink(HttpContext context, int orderId) =>
        links.GetUriByAction(context, "GetById", "Orders", new { id = orderId })!;
}""")

    h2(d, "Nomlangan marshrut")

    code(d, """[HttpGet("{id:int}", Name = "order-details")]
public Task<ActionResult<OrderDto>> GetById(int id) => ...;""")

    para(d, "Nom berish havola yasashni barqarorroq qiladi: controller yoki "
            "metod nomi o'zgarsa ham havola ishlashda davom etadi.")

    # ───────────────────────────────────────────
    h1(d, "6. Minimal API da routing")

    code(d, """var orders = app.MapGroup("/api/orders")
                .WithTags("Orders")
                .RequireAuthorization();

orders.MapGet("/", (IOrderService s, CancellationToken ct) => s.ListAsync(ct));

orders.MapGet("/{id:int}", async (int id, IOrderService s, CancellationToken ct) =>
    await s.FindAsync(id, ct) is { } order
        ? Results.Ok(order)
        : Results.NotFound())
    .WithName("order-details");

orders.MapPost("/", async (CreateOrderRequest request, IOrderService s,
                           CancellationToken ct) =>
{
    var created = await s.CreateAsync(request, ct);
    return Results.CreatedAtRoute("order-details", new { id = created.Id }, created);
});""")

    para(d, "`MapGroup` umumiy prefiks, teg va avtorizatsiya talabini bir "
            "joyda belgilaydi — bu controller'dagi `[Route]` va "
            "`[Authorize]` atributlarining ekvivalenti. Katta loyihada "
            "guruhlarni alohida fayllarga ajratib, extension metod bilan "
            "ro'yxatga olaman.")

    # ───────────────────────────────────────────
    h1(d, "7. Amaliy maslahatlar")

    bullets(d, [
        "**Resurs nomlari ko'plikda va ot bo'lsin**: `/orders`, "
        "`/customers`. Harakat HTTP metodida ifodalanadi, URL da emas — "
        "`/getOrders` emas, `GET /orders`.",
        "**Ierarxiyani yo'lda ko'rsataman**: `/orders/42/items`. Lekin "
        "ikki darajadan chuqur ketmaslikka harakat qilaman — "
        "`/customers/1/orders/2/items/3/comments/4` ni hech kim o'qiy "
        "olmaydi.",
        "**Filtr va sahifalash query string da**: `/orders?status=paid&page=2`. "
        "`status` resurs emas, shuning uchun u yo'lda bo'lmasligi kerak.",
        "**Kichik harf**: URL katta-kichik harfga sezgir bo'lishi mumkin, "
        "shuning uchun hamma joyda kichik harf va chiziqcha ishlataman "
        "(`order-items`, `OrderItems` emas).",
        "**Constraint qo'yish**: `{id:int}` yozish 404 ni to'g'ri joyda "
        "beradi va action'ga noto'g'ri ma'lumot kelishini oldini oladi.",
    ])

    sources(d, [
        ("Routing in ASP.NET Core",
         "https://learn.microsoft.com/en-us/aspnet/core/fundamentals/routing"),
        ("Routing to controller actions",
         "https://learn.microsoft.com/en-us/aspnet/core/mvc/controllers/routing"),
        ("Route constraint reference",
         "https://learn.microsoft.com/en-us/aspnet/core/fundamentals/routing#route-constraint-reference"),
        ("Route groups in Minimal APIs",
         "https://learn.microsoft.com/en-us/aspnet/core/fundamentals/minimal-apis/route-handlers"),
    ])
