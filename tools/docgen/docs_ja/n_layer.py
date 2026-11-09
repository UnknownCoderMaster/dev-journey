# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "Layered (N-Layer) Architecture"
CATEGORY = "Architecture"
TITLE = "Qatlamli (N-Layer) Arxitektura"
SUBTITLE = "Mas'uliyatni qatlamlarga ajratish va bog'liqlik yo'nalishi"
FILENAME = "Layered (N-Layer) Architecture.docx"


def build(d):
    h1(d, "1. Qatlam nima va nega kerak")

    para(d, "Qatlam — bir xil turdagi mas'uliyatni bir joyga to'playdigan "
            "guruh. Klassik taqsimot to'rtta:")

    bullets(d, [
        "**Presentation** — API controller'lari, model binding, HTTP "
        "statuslari. Tashqi dunyo bilan gaplashadi.",
        "**Application** — foydalanuvchi holatlari (use case): buyurtma "
        "yaratish, hisobot tayyorlash. Qadamlar ketma-ketligini "
        "muvofiqlashtiradi.",
        "**Domain** — biznes qoidalari va entity'lar. Hech qanday "
        "texnologiyaga bog'lanmaydi.",
        "**Infrastructure** — baza, fayl tizimi, tashqi API, navbat. "
        "Texnik tafsilotlar shu yerda.",
    ])

    para(d, "Asosiy qoida — **bog'liqlik faqat bir yo'nalishda**. "
            "Presentation Application'ni biladi, Application Domain'ni "
            "biladi. Teskarisi bo'lmaydi: domen controller haqida hech narsa "
            "bilmaydi.")

    note(d, "Layer va tier",
         "Layer — kodning mantiqiy bo'linishi. Tier — jismoniy bo'linish, "
         "ya'ni alohida jarayon yoki server. To'rt qatlamli ilova bitta "
         "serverda ishlashi mumkin — u holda 4 layer, 1 tier.")

    # ───────────────────────────────────────────
    h1(d, "2. Loyihalarga bo'lish")

    code(d, """Shop.Api/              -> Presentation
  Controllers/
  Program.cs

Shop.Application/      -> Application
  Orders/
    CreateOrderHandler.cs
    IOrderRepository.cs       (interfeys shu yerda!)

Shop.Domain/           -> Domain
  Orders/
    Order.cs
    OrderStatus.cs

Shop.Infrastructure/   -> Infrastructure
  Persistence/
    AppDbContext.cs
    OrderRepository.cs        (amalga oshirish shu yerda)""")

    para(d, "Bog'liqliklar shunday bo'ladi: `Api` → `Application` → `Domain`, "
            "va `Infrastructure` → `Application` + `Domain`. Ya'ni "
            "`Application` `Infrastructure` ga **bog'lanmaydi**.")

    # ───────────────────────────────────────────
    h1(d, "3. Dependency inversion — qatlamli arxitekturaning kaliti")

    para(d, "Oddiy qatlamli yondashuvda Application baza bilan ishlash uchun "
            "Infrastructure'ga bog'lanishi kerak bo'lardi. Lekin unda eng "
            "muhim kod eng o'zgaruvchan koddan bog'liq bo'lib qoladi.")

    para(d, "Yechim — interfeysni yuqori qatlamda e'lon qilish, amalga "
            "oshirishni pastda qoldirish:")

    code(d, """// Shop.Application ichida — ehtiyoj shu yerda e'lon qilinadi
public interface IOrderRepository
{
    Task<Order?> FindAsync(Guid id, CancellationToken ct);
    void Add(Order order);
}""")

    code(d, """// Shop.Infrastructure ichida — ehtiyoj shu yerda qondiriladi
public sealed class OrderRepository(AppDbContext db) : IOrderRepository
{
    public Task<Order?> FindAsync(Guid id, CancellationToken ct) =>
        db.Orders.Include(o => o.Items)
                 .FirstOrDefaultAsync(o => o.Id == id, ct);

    public void Add(Order order) => db.Orders.Add(order);
}""")

    code(d, """// Program.cs — ikkisi shu yerda bog'lanadi
builder.Services.AddScoped<IOrderRepository, OrderRepository>();""")

    para(d, "Natijada bog'liqlik o'qi ichkariga, domenga qaraydi. Bazani "
            "almashtirish Application kodiga tegmaydi — bu qatlamli "
            "arxitekturaning haqiqiy foydasi.")

    # ───────────────────────────────────────────
    h1(d, "4. Application qatlami nimadan iborat")

    code(d, """public sealed class CreateOrderHandler(
    IOrderRepository orders,
    IProductRepository products,
    IUnitOfWork unitOfWork)
{
    public async Task<Guid> HandleAsync(CreateOrderCommand command, CancellationToken ct)
    {
        var items = new List<OrderItem>();

        foreach (var line in command.Lines)
        {
            var product = await products.FindAsync(line.ProductId, ct)
                ?? throw new NotFoundException(nameof(Product), line.ProductId);

            items.Add(new OrderItem(product.Id, line.Quantity, product.Price));
        }

        var order = Order.Create(command.CustomerId, items);   // domen qoidalari
        orders.Add(order);
        await unitOfWork.SaveChangesAsync(ct);

        return order.Id;
    }
}""")

    para(d, "Bu handler **muvofiqlashtiradi**, lekin qoida qo'ymaydi. "
            "Buyurtma bo'sh bo'lmasligi, summa to'g'ri hisoblanishi kabi "
            "qoidalar `Order.Create` ichida — ya'ni domenda.")

    # ───────────────────────────────────────────
    h1(d, "5. Domen qatlami")

    code(d, """public sealed class Order
{
    private readonly List<OrderItem> _items = [];

    public Guid Id { get; private init; }
    public OrderStatus Status { get; private set; }
    public IReadOnlyList<OrderItem> Items => _items;
    public decimal Total => _items.Sum(i => i.Quantity * i.UnitPrice);

    private Order() { }

    public static Order Create(Guid customerId, IEnumerable<OrderItem> items)
    {
        var list = items.ToList();
        if (list.Count == 0)
            throw new DomainException("Buyurtmada kamida bitta qator bo'lishi kerak");

        var order = new Order { Id = Guid.CreateVersion7(), Status = OrderStatus.New };
        order._items.AddRange(list);
        return order;
    }

    public void Cancel()
    {
        if (Status is OrderStatus.Shipped)
            throw new DomainException("Yetkazilgan buyurtma bekor qilinmaydi");

        Status = OrderStatus.Cancelled;
    }
}""")

    para(d, "Ikki detalga e'tibor beraman. `_items` yopiq, tashqariga faqat "
            "`IReadOnlyList` chiqadi — ya'ni ro'yxatni aylanib o'tib "
            "o'zgartirish mumkin emas. Va holat o'tishi `Cancel()` metodi "
            "ichida tekshiriladi, chaqiruvchida emas.")

    # ───────────────────────────────────────────
    h1(d, "6. Ko'p uchraydigan xatolar")

    h2(d, "Anemik qatlamlar")

    para(d, "Agar qatlam faqat chaqiruvni pastga uzatish bilan shug'ullansa, "
            "u qatlam foyda bermaydi:")

    code(d, """// Bu qatlam nima qo'shdi?
public class OrderService(IOrderRepository repo)
{
    public Task<Order?> GetAsync(Guid id, CancellationToken ct) =>
        repo.FindAsync(id, ct);
}""")

    para(d, "O'zimga beradigan savol: bu qatlamni olib tashlasam, nima "
            "yo'qoladi? Javob yo'q bo'lsa — qatlam kerak emas.")

    h2(d, "Entity'ni hamma qatlamga olib yurish")

    para(d, "EF Core entity'si to'g'ridan-to'g'ri API javobiga aylansa, "
            "ikki muammo chiqadi: ichki maydonlar tashqariga oqadi, va "
            "entity o'zgarishi API shartnomasini buzadi. Shuning uchun "
            "chegarada DTO ga aylantirish kerak.")

    h2(d, "Domendan infratuzilmaga qarash")

    para(d, "Domen entity'sida `[Column]`, `[Table]` atributlari yoki "
            "`DbContext` ga murojaat paydo bo'lsa, qatlamlanish buzilgan "
            "bo'ladi. EF konfiguratsiyasi `IEntityTypeConfiguration<T>` "
            "orqali Infrastructure'da qoladi.")

    h2(d, "Juda ko'p qatlam")

    para(d, "Kichik CRUD servisga to'rt loyiha, mapper, interfeys va handler "
            "qo'shish — foydadan ko'ra ko'proq ish. 5 ta endpoint'li servis "
            "uchun bitta loyiha va ikki papka yetarli bo'lishi mumkin.")

    note(d, "Mening qoidam",
         "Qatlam **nimadan himoya qilayotganini** aytib berolmasam, u "
         "qatlam bejiz. Qatlamni oldindan emas, ehtiyoj paydo bo'lganda "
         "ajrataman — kod o'sgan sari qayerda chegara kerakligi o'zi "
         "ko'rinadi.")

    # ───────────────────────────────────────────
    h1(d, "7. Qatlamli va Clean Architecture")

    para(d, "Clean (yoki Onion) arxitektura — qatlamli yondashuvning "
            "dependency inversion to'liq qo'llanilgan ko'rinishi. Farqi "
            "shundaki, klassik N-Layer'da ma'lumotlarga kirish eng "
            "pastda turadi va yuqoridagilar unga bog'lanadi; Clean'da esa "
            "domen markazda bo'lib, hamma narsa unga qaraydi.")

    para(d, "Amalda ikkisi orasidagi chegara xira. Muhimi — nom emas, "
            "balki ikki savolga javob: **bog'liqlik qaysi tomonga qaraydi** "
            "va **biznes qoidasi qaysi fayldan topiladi**. Bu ikkisi aniq "
            "bo'lsa, arxitektura o'z vazifasini bajargan.")

    sources(d, [
        ("Common web application architectures",
         "https://learn.microsoft.com/en-us/dotnet/architecture/modern-web-apps-azure/common-web-application-architectures"),
        ("Architect modern web applications with ASP.NET Core",
         "https://learn.microsoft.com/en-us/dotnet/architecture/modern-web-apps-azure/"),
        ("Dependency inversion principle",
         "https://learn.microsoft.com/en-us/dotnet/architecture/modern-web-apps-azure/architectural-principles#dependency-inversion"),
    ])
