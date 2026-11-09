# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "Solid (SRP)"
CATEGORY = "Principles"
TITLE = "SRP — Single Responsibility Principle"
SUBTITLE = "Klassning o'zgarishi uchun bitta sabab bo'lishi kerak"
FILENAME = "Solid (SRP).docx"


def build(d):
    h1(d, "1. Printsipning to'g'ri ta'rifi")

    para(d, "SRP ko'pincha \"klass bitta ish qilishi kerak\" deb "
            "tushuntiriladi, lekin bu ta'rif foydasiz — \"bitta ish\" "
            "chegarasi noaniq, shuning uchun uni istalgan tarzda "
            "talqin qilish mumkin.")

    para(d, "Robert Martin bergan aniqroq ta'rif: **klassning o'zgarishi "
            "uchun bittadan ko'p sabab bo'lmasligi kerak**. Ya'ni savol "
            "\"bu klass nechta ish qiladi\" emas, balki \"bu faylni "
            "kimlar o'zgartirishni so'raydi\".")

    # ───────────────────────────────────────────
    h1(d, "2. Buzilishga misol")

    code(d, """public class OrderService
{
    public async Task PlaceAsync(OrderRequest request, CancellationToken ct)
    {
        // 1. Validatsiya
        if (request.Items.Count == 0)
            throw new ArgumentException("Bo'sh buyurtma");

        // 2. Narx hisoblash va chegirma qoidalari
        var total = request.Items.Sum(i => i.Quantity * i.UnitPrice);
        if (total > 1_000_000m) total *= 0.95m;

        // 3. Bazaga yozish
        await using var connection = new NpgsqlConnection(_connectionString);
        await connection.ExecuteAsync("INSERT INTO orders ...", new { total });

        // 4. PDF chek yasash
        var pdf = new PdfDocument();
        pdf.AddPage().AddText($"Summa: {total:N2}");
        var bytes = pdf.Save();

        // 5. Email yuborish
        using var smtp = new SmtpClient("smtp.example.com");
        await smtp.SendMailAsync(new MailMessage { Subject = "Buyurtma", ... });

        // 6. Log
        File.AppendAllText("orders.log", $"{DateTime.Now}: {total}\\n");
    }
}""")

    para(d, "Shu bitta metodni o'zgartirishni **oltita turli sabab** talab "
            "qilishi mumkin:")

    bullets(d, [
        "Buxgalteriya chegirma qoidasini o'zgartirdi.",
        "Baza Postgres'dan boshqasiga ko'chirildi.",
        "Dizayner chekning ko'rinishini o'zgartirdi.",
        "Marketing xat matnini o'zgartirdi.",
        "Validatsiya talabi qo'shildi.",
        "Log formati o'zgardi.",
    ])

    para(d, "Natijada bir fayl ustida bir nechta odam ishlaydi, konflikt "
            "chiqadi, va chekning ko'rinishini o'zgartirish buyurtma "
            "mantiqini buzib qo'yishi mumkin. Testlash ham imkonsiz: "
            "narx hisoblashni sinash uchun baza, SMTP va fayl tizimi "
            "kerak bo'ladi.")

    # ───────────────────────────────────────────
    h1(d, "3. Mas'uliyatlarni ajratish")

    code(d, """// Narx hisoblash — sof mantiq, test oson
public sealed class PriceCalculator
{
    public decimal Calculate(IReadOnlyList<OrderLine> lines)
    {
        var total = lines.Sum(l => l.Quantity * l.UnitPrice);
        return total > 1_000_000m ? total * 0.95m : total;
    }
}

// Saqlash
public interface IOrderRepository
{
    Task AddAsync(Order order, CancellationToken ct);
}

// Chek yasash
public interface IReceiptRenderer
{
    byte[] Render(Order order);
}

// Xabar yuborish
public interface INotificationSender
{
    Task SendAsync(Order order, CancellationToken ct);
}""")

    code(d, """public sealed class PlaceOrderHandler(
    IOrderValidator validator,
    PriceCalculator calculator,
    IOrderRepository repository,
    INotificationSender notifications,
    ILogger<PlaceOrderHandler> logger)
{
    public async Task<Guid> HandleAsync(OrderRequest request, CancellationToken ct)
    {
        validator.EnsureValid(request);

        var order = Order.Create(request.CustomerId, request.Items);
        order.SetTotal(calculator.Calculate(order.Lines));

        await repository.AddAsync(order, ct);
        await notifications.SendAsync(order, ct);

        logger.LogInformation("Buyurtma {OrderId} yaratildi, summa {Total}",
            order.Id, order.Total);

        return order.Id;
    }
}""")

    para(d, "Endi handler faqat **muvofiqlashtiradi** — uning o'zgarish "
            "sababi bitta: buyurtma yaratish oqimi o'zgarsa. Chegirma "
            "qoidasi o'zgarsa faqat `PriceCalculator` tegiladi.")

    # ───────────────────────────────────────────
    h1(d, "4. SRP ni haddan oshirib qo'llash")

    para(d, "Teskari tomonga ketish ham xato. Har bir metodni alohida "
            "klassga ajratish kodni o'qishni qiyinlashtiradi:")

    code(d, """// Haddan oshgan ajratish
public class OrderIdGenerator { }
public class OrderTotalSummer { }
public class OrderTotalDiscountApplier { }
public class OrderTotalRounder { }
public class OrderDateStamper { }""")

    para(d, "Bu holda bitta oddiy operatsiyani tushunish uchun besh faylni "
            "ochish kerak. Mas'uliyat ajratilgandek ko'rinadi, lekin "
            "aslida bitta mas'uliyat — narx hisoblash — beshga "
            "bo'lingan va hech biri o'zicha ma'noga ega emas.")

    note(d, "O'lchov",
         "Klasslar **birga o'zgaradigan** narsalarni birga ushlab "
         "turishi kerak. Agar ikki klass har doim birga o'zgarsa, ular "
         "bitta bo'lishi kerakligi haqidagi signal. Agar bitta klassning "
         "turli qismlari turli vaqtda o'zgarsa — uni ajratish kerak.")

    # ───────────────────────────────────────────
    h1(d, "5. Qanday aniqlayman")

    para(d, "Amalda shu belgilarga qarayman.")

    bullets(d, [
        "**Klass nomida \"va\" bor** yoki nomi juda umumiy "
        "(`OrderManager`, `DataHelper`, `Utils`). Nom topa olmaslik "
        "ko'pincha mas'uliyat aniq emasligini bildiradi.",
        "**Konstruktorda 6–7 dan ko'p bog'liqlik.** Har bir bog'liqlik "
        "potentsial o'zgarish sababi.",
        "**Import/using ro'yxati rang-barang:** `System.Net.Mail`, "
        "`Npgsql`, `PdfSharp` bir faylda bo'lsa, u juda ko'p narsani "
        "biladi.",
        "**Testda juda ko'p mock.** Bitta klassni sinash uchun 5 ta mock "
        "kerak bo'lsa, muammo testda emas — dizaynda.",
        "**Git tarixi.** Fayl juda tez-tez va turli sabablar bilan "
        "o'zgarsa, bu eng ishonchli signal.",
    ])

    # ───────────────────────────────────────────
    h1(d, "6. Nima foyda beradi")

    bullets(d, [
        "O'zgarish ta'siri cheklanadi — chegirma qoidasini o'zgartirish "
        "email yuborishni buzmaydi.",
        "Test yozish oson bo'ladi, chunki sof mantiqni infratuzilmadan "
        "ajratgan bo'laman.",
        "Qayta ishlatish imkoni paydo bo'ladi — `PriceCalculator` ni "
        "boshqa oqimda ham chaqirish mumkin.",
        "Jamoada parallel ishlash osonlashadi, konfliktlar kamayadi.",
    ])

    para(d, "Lekin SRP — maqsad emas, asbob. Uni \"toza bo'lsin\" degan "
            "fikr bilan emas, haqiqiy muammo paydo bo'lganda qo'llayman: "
            "bu faylga tegish qo'rqinchli bo'lib qolgandami, test yozish "
            "imkonsizmi, jamoada konflikt chiqayaptimi.")

    sources(d, [
        ("SOLID principles — architectural principles",
         "https://learn.microsoft.com/en-us/dotnet/architecture/modern-web-apps-azure/architectural-principles"),
        ("Single responsibility principle",
         "https://learn.microsoft.com/en-us/dotnet/architecture/modern-web-apps-azure/architectural-principles#single-responsibility"),
        ("Separation of concerns",
         "https://learn.microsoft.com/en-us/dotnet/architecture/modern-web-apps-azure/architectural-principles#separation-of-concerns"),
    ])
