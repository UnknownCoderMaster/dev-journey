# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "N-tier Architecture"
CATEGORY = "Architecture"
TITLE = "N-Qatlamli Arxitektura"
SUBTITLE = "Qatlamlarga bo'lish, bog'liqlik yo'nalishi va chegaralar"
FILENAME = "N-tier Architecture.docx"


def build(d):
    h1(d, "1. Asosiy g'oya")

    para(d, "N-qatlamli arxitektura ilovani mas'uliyatlari bo'yicha "
            "qatlamlarga ajratadi. Har bir qatlam o'z vazifasini bajaradi va "
            "faqat qo'shni qatlam bilan gaplashadi.")

    code(d, """┌──────────────────────────────┐
│  Presentation  (API, UI)     │   so'rovni qabul qiladi, javob beradi
├──────────────────────────────┤
│  Application   (xizmatlar)   │   biznes amallarini boshqaradi
├──────────────────────────────┤
│  Domain        (model)       │   biznes qoidalari
├──────────────────────────────┤
│  Infrastructure (EF, HTTP)   │   tashqi dunyo bilan aloqa
└──────────────────────────────┘""")

    note(d, "\"Tier\" va \"layer\" farqi ham bor:",
         "Layer — mantiqiy bo'linish, ya'ni kod tashkiloti. Tier — fizik "
         "bo'linish, ya'ni alohida serverda ishlash. Bitta jarayonda "
         "ishlaydigan uchta papka — bu uch layer, lekin bir tier. Amaliyotda "
         "bu atamalar tez-tez aralashtiriladi.")

    # ───────────────────────────────────────────
    h1(d, "2. Qatlamlarning vazifalari")

    h2(d, "2.1 Presentation")

    para(d, "So'rovni qabul qiladi, kiruvchi ma'lumotni tekshiradi, keyingi "
            "qatlamga uzatadi va natijani javobga aylantiradi. Bu yerda "
            "biznes mantiq bo'lmasligi kerak.")

    code(d, """[HttpPost]
public async Task<IActionResult> Create(
    CreateOrderRequest request, CancellationToken ct)
{
    var command = new CreateOrderCommand(
        request.CustomerId, request.Items);

    var result = await _orderService.CreateAsync(command, ct);

    return CreatedAtAction(nameof(GetById),
        new { id = result.Id }, result);
}""")

    h2(d, "2.2 Application")

    para(d, "Biznes amalini boshqaradi: kerakli ma'lumotni oladi, domen "
            "obyektlarini chaqiradi, natijani saqlaydi. Bu qatlam \"nima "
            "qilinadi\" ni biladi, lekin qoidalarni o'zi hal qilmaydi.")

    code(d, """public async Task<OrderDto> CreateAsync(
    CreateOrderCommand command, CancellationToken ct)
{
    var customer = await _customers.GetByIdAsync(command.CustomerId, ct)
        ?? throw new NotFoundException("Mijoz", command.CustomerId);

    var order = customer.PlaceOrder(command.Items);   // qoida domenda

    await _orders.AddAsync(order, ct);
    await _uow.SaveChangesAsync(ct);

    return _mapper.Map<OrderDto>(order);
}""")

    h2(d, "2.3 Domain")

    para(d, "Biznes qoidalari va ularni himoya qiluvchi obyektlar. Bu qatlam "
            "hech qanday texnologiyaga bog'liq bo'lmasligi kerak — unda EF "
            "Core ham, HTTP ham, fayl tizimi ham yo'q.")

    code(d, """public class Order
{
    private readonly List<OrderItem> _items = new();

    public IReadOnlyList<OrderItem> Items => _items;
    public OrderStatus Status { get; private set; }

    public void AddItem(Product product, int quantity)
    {
        if (Status != OrderStatus.Draft)
            throw new DomainException(
                "Faqat qoralama buyurtmaga qator qo'shish mumkin");

        if (quantity <= 0)
            throw new DomainException("Miqdor musbat bo'lishi kerak");

        _items.Add(new OrderItem(product.Id, quantity, product.Price));
    }
}""")

    note(d, "Bu yerda nozik nuqta bor:",
         "`_items` ro'yxati yopiq, tashqariga esa faqat o'qiladigan ko'rinish "
         "beriladi. Agar men `public List<OrderItem> Items { get; set; }` "
         "deb yozsam, har kim ro'yxatga qoidalarni chetlab o'tib element "
         "qo'sha oladi. Domen obyektining asosiy vazifasi — o'z holatini "
         "himoya qilish.")

    h2(d, "2.4 Infrastructure")

    para(d, "Tashqi dunyo bilan barcha aloqa: baza, fayl tizimi, HTTP "
            "mijozlari, xabar navbatlari, email.")

    # ───────────────────────────────────────────
    h1(d, "3. Bog'liqlik yo'nalishi")

    para(d, "An'anaviy N-qatlamli yondashuvda bog'liqlik yuqoridan pastga "
            "ketadi va domen infratuzilmaga bog'lanib qoladi:")

    code(d, """Presentation  →  Application  →  Domain  →  Infrastructure""")

    para(d, "Bu tuzilmaning kamchiligi shundaki, biznes qoidalari ma'lumotlar "
            "bazasiga bog'liq bo'lib qoladi. Bazani almashtirish yoki "
            "domenni alohida testlash qiyinlashadi.")

    h2(d, "3.1 Bog'liqlikni teskari aylantirish")

    para(d, "Toza arxitektura yondashuvida bog'liqlik yo'nalishi ichkariga "
            "qaratiladi. Buning uchun interfeys domenda e'lon qilinadi, "
            "amalga oshirish esa infratuzilmada bo'ladi.")

    code(d, """// Domain qatlamida
public interface IOrderRepository
{
    Task<Order?> GetByIdAsync(int id, CancellationToken ct = default);
    Task AddAsync(Order order, CancellationToken ct = default);
}""")

    code(d, """// Infrastructure qatlamida
public class OrderRepository : IOrderRepository
{
    private readonly AppDbContext _db;
    ...
}""")

    code(d, """Presentation  →  Application  →  Domain
                                     ↑
                           Infrastructure""")

    note(d, "Bu o'zgarish nima beradi:",
         "Domen endi hech kimga bog'liq emas. Uni alohida loyihada saqlash, "
         "hech qanday paket o'rnatmasdan testlash mumkin. Agar men ertaga EF "
         "Core o'rniga Dapper ga o'tsam, faqat Infrastructure o'zgaradi. "
         "Bu nazariy afzallikdek tuyuladi, lekin domenni mustaqil testlash "
         "imkoni amalda juda qimmatli.")

    # ───────────────────────────────────────────
    h1(d, "4. Loyiha tuzilmasi")

    code(d, """MyApp.sln
├── src/
│   ├── MyApp.Domain/              — entity, qiymat obyektlari, interfeyslar
│   ├── MyApp.Application/         — xizmatlar, DTO, validatsiya
│   ├── MyApp.Infrastructure/      — EF Core, tashqi xizmatlar
│   └── MyApp.Api/                 — kontrollerlar, middleware
└── tests/
    ├── MyApp.Domain.Tests/
    ├── MyApp.Application.Tests/
    └── MyApp.IntegrationTests/""")

    code(d, """<!-- MyApp.Domain.csproj — hech qanday loyihaga havola yo'q -->
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net10.0</TargetFramework>
  </PropertyGroup>
</Project>""")

    note(d, "Loyiha havolalari — eng ishonchli nazorat:",
         "Agar qatlamlar bitta loyihada, faqat papkalar bilan ajratilgan "
         "bo'lsa, chegarani buzish juda oson — bitta `using` yozilsa bo'ldi. "
         "Alohida loyiha bo'lsa, kompilyator chegarani o'zi himoya qiladi. "
         "Men buni qatlamlarni haqiqatan ajratishning yagona ishonchli "
         "usuli deb hisoblayman.")

    # ───────────────────────────────────────────
    h1(d, "5. Keng tarqalgan xatolar")

    table(d, ["Xato", "Nega yomon"],
          [["Entity ni API javobida qaytarish",
            "Ichki maydonlar ochiladi, qatlamlar bog'lanib qoladi"],
           ["Kontrollerda biznes mantiq",
            "Testlash qiyin, qayta ishlatib bo'lmaydi"],
           ["Domen obyektida EF atributlari",
            "Domen infratuzilmaga bog'lanadi"],
           ["Har bir qatlamda alohida DTO",
            "Ortiqcha aylantirish, qiymat qo'shmaydi"],
           ["Qatlamni o'tkazib yuborish",
            "Chegara ma'nosini yo'qotadi"]],
          widths=[5.6, 9.9])

    note(d, "To'rtinchi qator haqida alohida:",
         "Toza arxitektura nomidan har bir qatlamga o'z modeli berilishi "
         "kerak deb aytiladi. Lekin amalda bu `OrderEntity` → `OrderDomain` "
         "→ `OrderDto` → `OrderResponse` zanjiriga aylanadi va har bir "
         "maydon qo'shilganda to'rt joyni o'zgartirishga to'g'ri keladi. "
         "Men bunday ajratishni faqat modellar haqiqatan farq qilganda "
         "qilaman.")

    # ───────────────────────────────────────────
    h1(d, "6. Qatlamlar soni qancha bo'lishi kerak")

    para(d, "Universal javob yo'q. Qatlam qo'shish nazoratni oshiradi, lekin "
            "oddiy ishni ham ko'p fayl o'zgartirishga majbur qiladi.")

    bullets(d, [
        "**Kichik CRUD ilova** — ikki qatlam yetarli: API va ma'lumot.",
        "**O'rta loyiha** — uch qatlam: API, xizmatlar, ma'lumot.",
        "**Murakkab domen** — to'liq to'rt qatlam, bog'liqlik teskari "
        "yo'nalishda.",
    ])

    note(d, "Mening amaliy mezonim:",
         "Agar bitta maydon qo'shish uchun beshta faylni o'zgartirishim "
         "kerak bo'lsa va ularning to'rttasi faqat nusxa ko'chirish bo'lsa — "
         "qatlamlar ortiqcha. Agar men biznes qoidasini qayerga yozishni "
         "bilmay turgan bo'lsam — qatlamlar yetishmayapti. Ikkala holat ham "
         "o'zini aniq bildiradi.")

    # ───────────────────────────────────────────
    h1(d, "7. Chegaralarni avtomatik nazorat qilish")

    code(d, """// Arxitektura testi — NetArchTest kutubxonasi bilan
[Fact]
public void Domain_should_not_depend_on_infrastructure()
{
    var result = Types.InAssembly(typeof(Order).Assembly)
        .ShouldNot()
        .HaveDependencyOn("MyApp.Infrastructure")
        .GetResult();

    Assert.True(result.IsSuccessful,
        string.Join(", ", result.FailingTypeNames ?? []));
}""")

    para(d, "Bunday test qoidani hujjatdan kodga ko'chiradi — endi uni "
            "buzish mumkin emas, chunki CI quvuri to'xtaydi.")

    # ───────────────────────────────────────────
    h1(d, "8. Xulosa")

    bullets(d, [
        "N-qatlamli arxitektura mas'uliyatlarni ajratadi va har bir qatlamga "
        "aniq vazifa beradi.",
        "Layer — mantiqiy, tier — fizik bo'linish.",
        "An'anaviy yondashuvda bog'liqlik pastga, toza arxitekturada esa "
        "ichkariga qaratiladi.",
        "Interfeys domenda, amalga oshirish infratuzilmada e'lon qilinadi.",
        "Domen loyihasi hech qanday tashqi paketga bog'lanmasligi kerak.",
        "Alohida loyihalar chegarani kompilyator darajasida himoya qiladi.",
        "Qatlamlar soni loyihaning murakkabligiga mos bo'lishi lozim.",
        "Arxitektura testlari qoidalarni avtomatik nazorat qiladi.",
    ])

    sources(d, [
        ("Common web application architectures — .NET",
         "https://learn.microsoft.com/en-us/dotnet/architecture/modern-web-apps-azure/common-web-application-architectures"),
        ("N-tier architecture style — Azure Architecture Center",
         "https://learn.microsoft.com/en-us/azure/architecture/guide/architecture-styles/n-tier"),
        ("Designing a DDD-oriented microservice — .NET microservices",
         "https://learn.microsoft.com/en-us/dotnet/architecture/microservices/microservice-ddd-cqrs-patterns/ddd-oriented-microservice"),
    ])
