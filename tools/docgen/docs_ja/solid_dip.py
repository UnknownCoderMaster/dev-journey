# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "Solid (DIP)"
CATEGORY = "Principles"
TITLE = "DIP — Dependency Inversion Principle"
SUBTITLE = "Abstraksiyaga bog'lanish, amalga oshirishga emas"
FILENAME = "Solid (DIP).docx"


def build(d):
    h1(d, "1. Printsip nima deydi")

    para(d, "Ikki qoidadan iborat:")

    bullets(d, [
        "Yuqori darajali modullar quyi darajali modullarga bog'lanmasligi "
        "kerak. Ikkisi ham **abstraksiyaga** bog'lanishi kerak.",
        "Abstraksiya tafsilotga bog'lanmasligi kerak. Tafsilot "
        "abstraksiyaga bog'lanishi kerak.",
    ], numbered=True)

    para(d, "\"Inversion\" (teskari aylantirish) so'zi bog'liqlik "
            "**yo'nalishining** o'zgarishini bildiradi. Oddiy holatda "
            "biznes mantiqi bazaga bog'lanadi; DIP bu o'qni teskari "
            "aylantiradi — baza biznes mantiqi e'lon qilgan interfeysga "
            "bog'lanadi.")

    # ───────────────────────────────────────────
    h1(d, "2. Buzilishga misol")

    code(d, """public sealed class InvoiceService
{
    private readonly SqlInvoiceRepository _repository = new();
    private readonly SmtpEmailSender _sender = new("smtp.example.com", 587);
    private readonly PdfSharpRenderer _renderer = new();

    public async Task IssueAsync(Guid orderId, CancellationToken ct)
    {
        var invoice = await _repository.CreateAsync(orderId, ct);
        var pdf = _renderer.Render(invoice);
        await _sender.SendAsync(invoice.CustomerEmail, pdf, ct);
    }
}""")

    para(d, "Bu kodda biznes mantiqi uchta konkret texnologiyaga "
            "bog'langan: SQL, SMTP va PdfSharp. Natijalari:")

    bullets(d, [
        "Test yozish imkonsiz — har bir test haqiqiy baza va SMTP "
        "serverni talab qiladi.",
        "SMTP ni boshqa provayderga o'tkazish uchun biznes mantiqiga "
        "tegish kerak.",
        "`InvoiceService` ni boshqa loyihada ishlatish uchun uning hamma "
        "texnik bog'liqligini ham olib yurish kerak.",
        "Bog'liqliklar konstruktorda ko'rinmaydi — klass nimaga "
        "tayanayotganini bilish uchun butun kodni o'qish kerak.",
    ])

    # ───────────────────────────────────────────
    h1(d, "3. Interfeys kim tomonida e'lon qilinadi")

    para(d, "Bu DIP ning eng muhim va eng ko'p e'tibordan chetda qoladigan "
            "qismi. Interfeysni **ehtiyoj egasi** e'lon qiladi, uni "
            "qondiruvchi emas.")

    code(d, """// Shop.Application ichida — EHTIYOJ shu yerda e'lon qilinadi
namespace Shop.Application.Invoicing;

public interface IInvoiceRepository
{
    Task<Invoice> CreateAsync(Guid orderId, CancellationToken ct);
}

public interface IInvoiceNotifier
{
    Task NotifyAsync(Invoice invoice, byte[] document, CancellationToken ct);
}

public interface IInvoiceRenderer
{
    byte[] Render(Invoice invoice);
}""")

    code(d, """// Shop.Infrastructure ichida — ehtiyoj shu yerda QONDIRILADI
namespace Shop.Infrastructure.Persistence;

public sealed class EfInvoiceRepository(AppDbContext db) : IInvoiceRepository
{
    public async Task<Invoice> CreateAsync(Guid orderId, CancellationToken ct)
    {
        var invoice = Invoice.ForOrder(orderId);
        db.Invoices.Add(invoice);
        await db.SaveChangesAsync(ct);
        return invoice;
    }
}""")

    code(d, """public sealed class InvoiceService(
    IInvoiceRepository repository,
    IInvoiceRenderer renderer,
    IInvoiceNotifier notifier)
{
    public async Task IssueAsync(Guid orderId, CancellationToken ct)
    {
        var invoice = await repository.CreateAsync(orderId, ct);
        var document = renderer.Render(invoice);
        await notifier.NotifyAsync(invoice, document, ct);
    }
}""")

    para(d, "Endi bog'liqlik o'qi shunday: `Infrastructure` → "
            "`Application`. Ya'ni texnik qatlam biznes qatlamiga "
            "bog'langan, teskarisi emas. Bazani almashtirish "
            "`InvoiceService` ga tegmaydi.")

    note(d, "Nozik farq",
         "Interfeysni infratuzilma loyihasida e'lon qilib, uni "
         "Application'dan ishlatish ham texnik jihatdan ishlaydi — "
         "lekin unda bog'liqlik baribir pastga qaraydi va DIP "
         "bajarilmaydi. Interfeys **qayerda yashayotgani** muhim.")

    # ───────────────────────────────────────────
    h1(d, "4. Bog'lash joyi")

    para(d, "Interfeys va amalga oshirish bir joyda — ilovaning kirish "
            "nuqtasida (composition root) bog'lanadi:")

    code(d, """// Program.cs — faqat bu yer ikkisini ham biladi
builder.Services.AddScoped<IInvoiceRepository, EfInvoiceRepository>();
builder.Services.AddScoped<IInvoiceRenderer, QuestPdfRenderer>();
builder.Services.AddScoped<IInvoiceNotifier, EmailInvoiceNotifier>();
builder.Services.AddScoped<InvoiceService>();""")

    para(d, "Bu joyni bitta faylda ushlab turish muhim. Agar ro'yxatga "
            "olish kod bo'ylab tarqalsa, qaysi interfeys qaysi klass "
            "bilan bog'langanini topish qiyinlashadi.")

    # ───────────────────────────────────────────
    h1(d, "5. Test — eng aniq foyda")

    code(d, """[Fact]
public async Task IssueAsync_SendsDocumentToCustomer()
{
    var repository = Substitute.For<IInvoiceRepository>();
    var renderer = Substitute.For<IInvoiceRenderer>();
    var notifier = Substitute.For<IInvoiceNotifier>();

    var invoice = Invoice.ForOrder(Guid.NewGuid());
    repository.CreateAsync(Arg.Any<Guid>(), Arg.Any<CancellationToken>())
              .Returns(invoice);
    renderer.Render(invoice).Returns([1, 2, 3]);

    var service = new InvoiceService(repository, renderer, notifier);
    await service.IssueAsync(invoice.OrderId, CancellationToken.None);

    await notifier.Received(1).NotifyAsync(
        invoice, Arg.Is<byte[]>(b => b.Length == 3), Arg.Any<CancellationToken>());
}""")

    para(d, "Bu test millisekundlarda ishlaydi, baza va tarmoq talab "
            "qilmaydi, va har doim bir xil natija beradi. DIP "
            "qo'llanmagan bo'lsa, bunday test yozish imkonsiz.")

    # ───────────────────────────────────────────
    h1(d, "6. DI, DIP va IoC — uchtasi bir xil emas")

    table(d, ["Atama", "Nima"],
          [["**DIP**", "Printsip: abstraksiyaga bog'lanish qoidasi"],
           ["**IoC**", "Umumiy g'oya: nazoratni framework'ga berish"],
           ["**DI**", "Usul: bog'liqlikni tashqaridan uzatish"],
           ["**DI container**", "Asbob: bog'liqliklarni yaratuvchi kutubxona"]],
          widths=[4.0, 10.5])

    para(d, "DI container'dan foydalanish o'zi DIP ni bajarmaydi. "
            "Container orqali konkret klassni olish ham mumkin — unda "
            "printsip baribir buzilgan bo'ladi:")

    code(d, """// Container ishlatiladi, lekin DIP yo'q
public sealed class InvoiceService(EfInvoiceRepository repository) { }""")

    # ───────────────────────────────────────────
    h1(d, "7. Qachon abstraksiya qo'ymayman")

    para(d, "DIP ni hamma joyga qo'llash kodni keraksiz "
            "murakkablashtiradi. Abstraksiya qo'yish uchun o'zimga "
            "beradigan savollar:")

    bullets(d, [
        "Bu bog'liqlik **tashqi dunyoga** chiqadimi — baza, HTTP, fayl, "
        "navbat, vaqt, tasodifiy son? Ha bo'lsa, abstraksiya deyarli "
        "har doim arziydi.",
        "Testda uni almashtirish kerakmi? Ha bo'lsa — kerak.",
        "Ikkinchi amalga oshirish bo'ladimi? Ha bo'lsa — kerak.",
    ])

    para(d, "Uchtasiga ham \"yo'q\" bo'lsa, interfeys faqat qo'shimcha "
            "fayl va bir qadam qo'shadi. Masalan sof hisoblash klassi "
            "(`PriceCalculator`) uchun interfeys kerak emas — u tez, "
            "deterministik va almashtirilmaydi.")

    note(d, "Xulosa",
         "DIP eng ko'p foyda beradigan SOLID printsipi, chunki u "
         "qatlamlar orasidagi chegarani haqiqiy qiladi. Lekin uning "
         "qiymati **chegarada** — ilovaning ichidagi har bir klass "
         "orasida emas.")

    sources(d, [
        ("Dependency inversion principle",
         "https://learn.microsoft.com/en-us/dotnet/architecture/modern-web-apps-azure/architectural-principles#dependency-inversion"),
        ("Dependency injection in ASP.NET Core",
         "https://learn.microsoft.com/en-us/aspnet/core/fundamentals/dependency-injection"),
        ("Dependency injection guidelines",
         "https://learn.microsoft.com/en-us/dotnet/core/extensions/dependency-injection-guidelines"),
    ])
