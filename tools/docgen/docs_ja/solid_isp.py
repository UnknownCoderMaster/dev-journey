# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "Solid (ISP)"
CATEGORY = "Principles"
TITLE = "ISP — Interface Segregation Principle"
SUBTITLE = "Mijoz o'ziga kerak bo'lmagan metodga bog'lanmasligi kerak"
FILENAME = "Solid (ISP).docx"


def build(d):
    h1(d, "1. Printsip nima deydi")

    para(d, "Hech bir mijoz o'ziga kerak bo'lmagan metodlarga "
            "bog'lanishga majbur bo'lmasligi kerak. Ya'ni bir nechta "
            "kichik, aniq interfeys bitta kattasidan yaxshiroq.")

    para(d, "Bu faqat estetik masala emas. Katta interfeys ikki aniq "
            "zarar keltiradi: amalga oshiruvchi klass kerak bo'lmagan "
            "metodlarni ham yozishga majbur bo'ladi, va interfeysga "
            "o'zgarish kiritilganda unga bog'langan hamma kod qayta "
            "kompilyatsiya qilinadi yoki buziladi.")

    # ───────────────────────────────────────────
    h1(d, "2. Buzilishga misol")

    code(d, """public interface IOrderService
{
    Task<Order?> FindAsync(Guid id, CancellationToken ct);
    Task<IReadOnlyList<Order>> ListAsync(CancellationToken ct);
    Task<Guid> CreateAsync(CreateOrderCommand command, CancellationToken ct);
    Task UpdateAsync(UpdateOrderCommand command, CancellationToken ct);
    Task DeleteAsync(Guid id, CancellationToken ct);
    Task ApproveAsync(Guid id, CancellationToken ct);
    Task<byte[]> ExportToExcelAsync(ReportFilter filter, CancellationToken ct);
    Task<byte[]> RenderInvoicePdfAsync(Guid id, CancellationToken ct);
    Task SendConfirmationEmailAsync(Guid id, CancellationToken ct);
    Task<OrderStatistics> GetStatisticsAsync(DateRange range, CancellationToken ct);
}""")

    para(d, "Bu interfeysga bog'langan kodlarning hech biri uning "
            "hammasini ishlatmaydi. Mijoz paneli faqat `FindAsync` va "
            "`CreateAsync` ni chaqiradi, hisobot moduli faqat "
            "`GetStatisticsAsync` ni, chek yasash esa faqat "
            "`RenderInvoicePdfAsync` ni.")

    para(d, "Oqibatlari amalda shunday ko'rinadi:")

    bullets(d, [
        "Testda `IOrderService` ni mock qilganda 10 metodli stub kerak "
        "bo'ladi, lekin test faqat bittasini ishlatadi.",
        "`ExportToExcelAsync` imzosi o'zgarsa, unga aloqasi yo'q "
        "modullar ham qayta kompilyatsiya qilinadi.",
        "Yangi amalga oshirish yozish qiyin — masalan keshlovchi "
        "dekorator yasash uchun 10 metodni ham yozish kerak.",
        "Interfeysni o'qigan odam \"bu servis nima qiladi\" degan "
        "savolga javob topa olmaydi.",
    ])

    # ───────────────────────────────────────────
    h1(d, "3. Ajratish")

    code(d, """// O'qish
public interface IOrderReader
{
    Task<Order?> FindAsync(Guid id, CancellationToken ct);
    Task<IReadOnlyList<Order>> ListAsync(OrderFilter filter, CancellationToken ct);
}

// Yozish
public interface IOrderWriter
{
    Task<Guid> CreateAsync(CreateOrderCommand command, CancellationToken ct);
    Task UpdateAsync(UpdateOrderCommand command, CancellationToken ct);
}

// Holat o'zgarishi
public interface IOrderApproval
{
    Task ApproveAsync(Guid id, CancellationToken ct);
}

// Hisobot
public interface IOrderStatistics
{
    Task<OrderStatistics> GetAsync(DateRange range, CancellationToken ct);
}

// Hujjat yasash — aslida boshqa mas'uliyat
public interface IInvoiceRenderer
{
    Task<byte[]> RenderAsync(Guid orderId, CancellationToken ct);
}""")

    para(d, "Bitta klass bir nechta interfeysni amalga oshirishi mumkin, "
            "shuning uchun ajratish qo'shimcha fayl sonini "
            "majburlamaydi:")

    code(d, """public sealed class OrderService(AppDbContext db)
    : IOrderReader, IOrderWriter, IOrderApproval
{
    // ...
}""")

    code(d, """// Ro'yxatga olishda bitta instance uchtasiga xizmat qiladi
builder.Services.AddScoped<OrderService>();
builder.Services.AddScoped<IOrderReader>(sp => sp.GetRequiredService<OrderService>());
builder.Services.AddScoped<IOrderWriter>(sp => sp.GetRequiredService<OrderService>());""")

    para(d, "Endi mijoz paneli faqat `IOrderReader` ni oladi va "
            "`ApproveAsync` mavjudligini ham bilmaydi. Bu nafaqat "
            "toza, balki xavfsizroq ham — tasodifan noto'g'ri metodni "
            "chaqirish imkoni yo'q.")

    # ───────────────────────────────────────────
    h1(d, "4. .NET dagi yaxshi misollar")

    para(d, "Standart kutubxonada bu printsip izchil qo'llangan:")

    table(d, ["Interfeys", "Nechta a'zo", "Nimani bildiradi"],
          [["`IDisposable`", "1", "Resursni bo'shatish mumkin"],
           ["`IEnumerable<T>`", "1", "Aylanib o'tish mumkin"],
           ["`IComparable<T>`", "1", "Taqqoslash mumkin"],
           ["`IReadOnlyList<T>`", "3", "Indeks bilan o'qish mumkin"],
           ["`ICollection<T>`", "~7", "O'zgartirish ham mumkin"]],
          widths=[4.4, 2.8, 7.3])

    para(d, "Shuning uchun metod parametrida eng kichik yetarli "
            "interfeysni so'rashga harakat qilaman:")

    code(d, """// Faqat aylanib o'tish kerak bo'lsa
public decimal Sum(IEnumerable<OrderLine> lines) => lines.Sum(l => l.Total);

// Indeks va Count kerak bo'lsa
public OrderLine Largest(IReadOnlyList<OrderLine> lines) => ...;

// List<T> ni so'rash — ortiqcha talab
public decimal Sum(List<OrderLine> lines) => ...;   // massiv bera olmayman""")

    # ───────────────────────────────────────────
    h1(d, "5. Haddan oshirib qo'llash")

    para(d, "Har bir metodga alohida interfeys yasash teskari muammoni "
            "keltiradi:")

    code(d, """public interface IOrderFinder { Task<Order?> FindAsync(Guid id, CancellationToken ct); }
public interface IOrderLister { Task<List<Order>> ListAsync(CancellationToken ct); }
public interface IOrderCounter { Task<int> CountAsync(CancellationToken ct); }
public interface IOrderExister { Task<bool> ExistsAsync(Guid id, CancellationToken ct); }""")

    para(d, "Bu holda konstruktorda to'rtta bog'liqlik paydo bo'ladi, "
            "ularning hammasi bitta klassga ishora qiladi. Foyda yo'q, "
            "shovqin ko'p.")

    note(d, "O'lchov",
         "Interfeysni **mijozning ehtiyoji** bo'yicha ajrataman, "
         "metodlar soni bo'yicha emas. Agar ikki metod har doim birga "
         "ishlatilsa, ular bitta interfeysda qolishi kerak. "
         "Ajratish faqat haqiqatan turli mijozlar turli qismini "
         "ishlatganda ma'noga ega.")

    # ───────────────────────────────────────────
    h1(d, "6. Ajratishning qo'shimcha foydasi: dekorator")

    para(d, "Kichik interfeys dekorator yozishni osonlashtiradi. "
            "Keshlash, log yozish yoki qayta urinishni qo'shish uchun "
            "faqat kerakli metodni o'rab olaman:")

    code(d, """public sealed class CachedOrderReader(
    IOrderReader inner,
    IMemoryCache cache) : IOrderReader
{
    public async Task<Order?> FindAsync(Guid id, CancellationToken ct)
        => await cache.GetOrCreateAsync($"order:{id}", async entry =>
        {
            entry.AbsoluteExpirationRelativeToNow = TimeSpan.FromMinutes(5);
            return await inner.FindAsync(id, ct);
        });

    public Task<IReadOnlyList<Order>> ListAsync(OrderFilter filter, CancellationToken ct)
        => inner.ListAsync(filter, ct);     // keshlanmaydi
}""")

    para(d, "Agar interfeys 10 metodli bo'lsa, bu dekoratorda "
            "sakkizta ortiqcha o'tkazuvchi metod yozishim kerak bo'lardi. "
            "Ikki metodli interfeys bilan esa dekorator qisqa va "
            "maqsadi aniq.")

    sources(d, [
        ("Interface segregation principle",
         "https://learn.microsoft.com/en-us/dotnet/architecture/modern-web-apps-azure/architectural-principles"),
        ("Interfaces — C# fundamentals",
         "https://learn.microsoft.com/en-us/dotnet/csharp/fundamentals/types/interfaces"),
        ("Collections and data structures",
         "https://learn.microsoft.com/en-us/dotnet/standard/collections/"),
    ])
