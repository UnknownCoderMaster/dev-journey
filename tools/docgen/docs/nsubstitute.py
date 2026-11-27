# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "NSubstitute"
CATEGORY = "Testing"
TITLE = "NSubstitute"
SUBTITLE = "Mock yaratish kutubxonasi va uning sintaksisi"
FILENAME = "NSubstitute.docx"


def build(d):
    h1(d, "1. Kutubxona haqida")

    para(d, "NSubstitute — `.NET` uchun mock kutubxonasi. Uning asosiy g'oyasi — "
            "sintaksisni iloji boricha oddiy qilish. Boshqa kutubxonalardan farqli "
            "o'laroq, u lambda ifodalar va `Setup`/`Verify` juftligini talab "
            "qilmaydi.")

    code(d, """dotnet add package NSubstitute
dotnet add package NSubstitute.Analyzers.CSharp""")

    para(d, "Ikkinchi paket — analizator. U noto'g'ri ishlatilishni kompilyatsiya "
            "vaqtida aniqlaydi, masalan `virtual` bo'lmagan metodni sozlashga "
            "urinishni.")

    note(d, "Analizator paketini men doim qo'shaman:",
         "Usiz noto'g'ri sozlangan mock jimgina ishlamaydi — xatolik chiqmaydi, "
         "shunchaki sozlama e'tiborga olinmaydi. Natijada test \"ishlayapti\" "
         "deb ko'rinadi, lekin aslida hech narsani tekshirmayapti. Analizator "
         "buni darhol ko'rsatadi.")

    # ───────────────────────────────────────────
    h1(d, "2. Mock yaratish")

    code(d, """var repo = Substitute.For<IOrderRepository>();
var email = Substitute.For<IEmailSender>();
var payment = Substitute.For<IPaymentGateway>();

var service = new OrderService(repo, payment, email);""")

    para(d, "Sozlanmagan metodlar sukutdagi qiymat qaytaradi: `null`, `0`, bo'sh "
            "kolleksiya yoki tugallangan `Task`. Bu qulay — kerak bo'lmagan "
            "metodlarni sozlash shart emas.")

    # ───────────────────────────────────────────
    h1(d, "3. Qaytariladigan qiymatni belgilash")

    code(d, """// Oddiy qiymat
repo.GetByIdAsync(1, Arg.Any<CancellationToken>())
    .Returns(new Order { Id = 1, Total = 150_000 });

// Xususiyat
clock.UtcNow.Returns(new DateTime(2026, 10, 31));

// Ketma-ket chaqiruvlarda turli qiymat
counter.Next().Returns(1, 2, 3);

// Hisoblangan qiymat
repo.GetByIdAsync(Arg.Any<int>(), Arg.Any<CancellationToken>())
    .Returns(call => new Order { Id = call.Arg<int>() });""")

    h2(d, "3.1 Argument moslashtiruvchilari")

    table(d, ["Ifoda", "Mosligi"],
          [["`Arg.Any<T>()`", "Har qanday qiymat"],
           ["`Arg.Is(5)`", "Aynan shu qiymat"],
           ["`Arg.Is<int>(x => x > 10)`", "Shartga mos qiymat"],
           ["`Arg.Is<string>(s => s.StartsWith(\"A\"))`", "Shartga mos matn"],
           ["`Arg.Do<T>(x => captured = x)`", "Qiymatni ushlab qolish"]],
          widths=[6.0, 9.5])

    note(d, "Keng tarqalgan tuzoq:",
         "Agar metodda bir nechta argument bo'lsa va men bittasiga aniq qiymat, "
         "boshqasiga esa oddiy qiymat yozsam, NSubstitute xatolik beradi. "
         "Qoida shunday: **bitta `Arg.` ishlatilsa, hammasi `Arg.` bo'lishi "
         "kerak**. Shuning uchun `CancellationToken` ni ham "
         "`Arg.Any<CancellationToken>()` deb yozaman.")

    code(d, """// Xato — aralash
repo.GetByIdAsync(1, CancellationToken.None).Returns(order);

// To'g'ri
repo.GetByIdAsync(1, Arg.Any<CancellationToken>()).Returns(order);""")

    # ───────────────────────────────────────────
    h1(d, "4. Chaqiruvlarni tekshirish")

    code(d, """// Kamida bir marta chaqirilgan
await email.Received().SendAsync(
    Arg.Any<string>(), Arg.Any<string>(), Arg.Any<CancellationToken>());

// Aynan bir marta
await email.Received(1).SendAsync(
    "customer@example.com", Arg.Any<string>(), Arg.Any<CancellationToken>());

// Umuman chaqirilmagan
await payment.DidNotReceive().RefundAsync(
    Arg.Any<int>(), Arg.Any<CancellationToken>());

// Shartga mos argument bilan
await email.Received(1).SendAsync(
    Arg.Any<string>(),
    Arg.Is<string>(body => body.Contains("buyurtma")),
    Arg.Any<CancellationToken>());""")

    h2(d, "4.1 Tartibni tekshirish")

    code(d, """Received.InOrder(async () =>
{
    await repo.AddAsync(Arg.Any<Order>(), Arg.Any<CancellationToken>());
    await repo.SaveChangesAsync(Arg.Any<CancellationToken>());
    await email.SendAsync(Arg.Any<string>(), Arg.Any<string>(),
                          Arg.Any<CancellationToken>());
});""")

    note(d, "Tartibni tekshirishni kam ishlataman:",
         "U testni amalga oshirish tafsilotiga juda qattiq bog'laydi. Agar men "
         "keyinroq email yuborishni saqlashdan oldinga ko'chirsam — xatti-harakat "
         "o'zgarmaydi, lekin test buziladi. Shuning uchun tartib haqiqatan muhim "
         "bo'lgandagina tekshiraman.")

    h2(d, "4.2 Argumentni ushlab qolish")

    code(d, """Order? captured = null;

await repo.AddAsync(
    Arg.Do<Order>(o => captured = o),
    Arg.Any<CancellationToken>());

await service.CreateOrderAsync(command, ct);

Assert.NotNull(captured);
Assert.Equal(3, captured!.Quantity);""")

    para(d, "Yoki qabul qilingan chaqiruvlardan olish:")

    code(d, """var call = repo.ReceivedCalls()
    .First(c => c.GetMethodInfo().Name == nameof(IOrderRepository.AddAsync));

var order = (Order)call.GetArguments()[0]!;""")

    # ───────────────────────────────────────────
    h1(d, "5. Istisno otish")

    code(d, """// Metod istisno otsin
payment.ChargeAsync(Arg.Any<decimal>(), Arg.Any<CancellationToken>())
    .Returns<Task>(_ => throw new PaymentFailedException("Mablag' yetarli emas"));

// Yoki
payment.When(p => p.ChargeAsync(Arg.Any<decimal>(), Arg.Any<CancellationToken>()))
       .Do(_ => throw new PaymentFailedException("Xato"));""")

    code(d, """await Assert.ThrowsAsync<PaymentFailedException>(
    () => service.CreateOrderAsync(command, ct));

// To'lov muvaffaqiyatsiz bo'lsa, email yuborilmasligi kerak
await email.DidNotReceive().SendAsync(
    Arg.Any<string>(), Arg.Any<string>(), Arg.Any<CancellationToken>());""")

    # ───────────────────────────────────────────
    h1(d, "6. To'liq test misoli")

    code(d, """public class OrderServiceTests
{
    private readonly IOrderRepository _repo = Substitute.For<IOrderRepository>();
    private readonly IPaymentGateway _payment = Substitute.For<IPaymentGateway>();
    private readonly IEmailSender _email = Substitute.For<IEmailSender>();
    private readonly OrderService _sut;

    public OrderServiceTests()
        => _sut = new OrderService(_repo, _payment, _email);

    [Fact]
    public async Task CreateOrder_sends_confirmation_when_payment_succeeds()
    {
        // Arrange
        var command = new CreateOrderCommand(
            CustomerId: 7, BookId: 1, Quantity: 2);

        _repo.GetBookAsync(1, Arg.Any<CancellationToken>())
             .Returns(new Book { Id = 1, Price = 50_000, AvailableCopies = 10 });

        _payment.ChargeAsync(Arg.Any<decimal>(), Arg.Any<CancellationToken>())
                .Returns(PaymentResult.Success("txn-123"));

        // Act
        var result = await _sut.CreateOrderAsync(command, CancellationToken.None);

        // Assert
        Assert.Equal(OrderStatus.Paid, result.Status);

        await _payment.Received(1).ChargeAsync(
            100_000, Arg.Any<CancellationToken>());

        await _email.Received(1).SendAsync(
            Arg.Any<string>(),
            Arg.Is<string>(s => s.Contains("tasdiqlandi")),
            Arg.Any<CancellationToken>());
    }
}""")

    # ───────────────────────────────────────────
    h1(d, "7. Cheklovlar")

    bullets(d, [
        "`sealed` klasslarni almashtirib bo'lmaydi.",
        "Statik va `extension` metodlar mock qilinmaydi.",
        "`virtual` bo'lmagan metodlar jimgina e'tiborga olinmaydi — analizator "
        "buni ko'rsatadi.",
        "Bir nechta interfeysni birlashtirish mumkin, lekin bir nechta klassni "
        "emas.",
    ])

    code(d, """// Bir nechta interfeys
var substitute = Substitute.For<IOrderRepository, IDisposable>();""")

    note(d, "Boshqa kutubxonalar bilan solishtirganda:",
         "Moq keng tarqalgan, lekin uning sintaksisi ko'proq so'z talab qiladi — "
         "`mock.Setup(x => x.Method()).Returns(value)` va keyin `mock.Object`. "
         "NSubstitute da esa mock ning o'zi to'g'ridan-to'g'ri interfeys sifatida "
         "ishlatiladi va `.Object` kerak emas. Men shu sodda sintaksis uchun "
         "NSubstitute ni afzal ko'raman.")

    # ───────────────────────────────────────────
    # ───────────────────────────────────────────
    h1(d, "8. Amaliyotdan: test loyihalari bor, testlar yo'q")

    para(d, "Bu bo'limni yozishdan avval ikkilandim, chunki u muvaffaqiyatli yechim "
            "haqida emas. Lekin menimcha aynan shuning uchun yozishga arziydi.")

    para(d, "Ish joyimdagi MAD ERP tizimida yigirmaga yaqin servis bor va har birining "
            "`Erp.Service.{Domain}.UnitTest` loyihasi mavjud. NSubstitute ham, xUnit "
            "ham bog'langan, markazlashgan paket boshqaruvida versiyalari qadalgan. "
            "Ya'ni infratuzilma to'liq tayyor.")

    para(d, "Lekin test loyihalarining ko'pi bo'sh — faqat skeleton. Bitta servisda "
            "yozilgan yakka test fayli esa butunlay izohga olingan holatda yotadi:")

    code(d, """// services/erp/erp-adm-service/test/.../Users/Commands/UserAttachCommandHandlerTest.cs
//
// public class UserAttachCommandHandlerTest
// {
//     [Fact]
//     public async Task Handle_ValidCommand_AttachesUser()
//     ...""", caption="Butun fayl shu holatda")

    para(d, "Shuning uchun `dotnet test` yashil chiqadi va hech narsani isbotlamaydi. "
            "Bu eng xavfli holat: komanda \"testlar o'tdi\" degan signalni oladi, "
            "signal esa bo'sh.")

    h2(d, "8.1 Nega shunday bo'ldi")

    para(d, "Sababni tushunish qiyin emas. 7-bo'limda NSubstitute ning cheklovlari "
            "aytilgan — virtual bo'lmagan a'zolarni almashtirib bo'lmasligi, statik "
            "metodlarga yetib bo'lmasligi. Bu loyihadagi ishlovchilar esa "
            "`IApplicationDbContext` ni oladi, ya'ni interfeys — demak mock qilish "
            "mumkin. Muammo boshqa joyda.")

    bullets(d, [
        "Ishlovchilar ko'pincha EF Core so'rovlarining o'zidan iborat. `IApplicationDbContext` "
        "ni mock qilsak, `DbSet` ustidagi LINQ ni ham taqlid qilish kerak bo'ladi — "
        "bu amalda EF Core ni qayta yozish degani. Shuning uchun bunday testlar "
        "mock emas, `InMemory` yoki haqiqiy bazani talab qiladi.",
        "Markazlashgan `ApplicationDbContext` yuzlab `DbSet` dan iborat. Uni mock "
        "qilish uchun kerakli `DbSet` larni sozlash o'zi ancha ish.",
        "Ishlovchilar bir-birini `ISender` orqali chaqiradi, ya'ni test chegarasi "
        "aniq emas: bitta ishlovchini sinash uchun zanjirning yarmi kerak bo'ladi.",
    ])

    para(d, "Ya'ni to'siq NSubstitute da emas, kodning sinovga tayyorligida. Bu "
            "1-bo'limda aytilgan \"mock kutubxonasi faqat bog'liqlikni almashtiradi\" "
            "degan fikrning teskari tomoni: agar bog'liqlik toza ajratilmagan bo'lsa, "
            "kutubxona yordam bera olmaydi.")

    h2(d, "8.2 Qaysi joylarda test yozish mumkin edi")

    para(d, "Shu kodbazani o'rganib chiqib, mock bilan bemalol sinaladigan joylarni "
            "ajratdim — ularda EF Core yo'q:")

    bullets(d, [
        "**Holat o'tishlari.** `StatusIdConst.CanApplyStatus(current, new)` — sof "
        "funksiya, hech qanday bog'liqligi yo'q. Unga umuman mock kerak emas, "
        "`[Theory]` va `[InlineData]` yetarli. Bu esa eng muhim biznes qoidasi: "
        "qaysi holatdan qaysi holatga o'tish mumkinligi.",
        "**Validatorlar.** FluentValidation validatorlari ham sof — kirish obyekti "
        "beriladi, xatolar ro'yxati qaytadi.",
        "**SDK handler lari.** `LanguageHeaderHandler` kabi `DelegatingHandler` lar "
        "`IHttpContextAccessor` ni oladi — bu interfeys, NSubstitute bilan "
        "almashtirish uchun ideal. 4-bo'limdagi chaqiruvlarni tekshirish shu yerda "
        "aniq ishlardi: sarlavha qo'shildimi, ikki marta qo'shilmadimi.",
        "**Konfiguratsiya mantig'i.** O'rin egalarini almashtiradigan metod "
        "`IConfiguration` ustida ishlaydi va atrof-muhit o'zgaruvchilarini o'qiydi — "
        "uni ham sinash mumkin.",
    ])

    note(d, "Bu meni qiziqtirgan savolga olib keldi:",
         "Nega infratuzilma qurilgan, lekin ishlatilmagan? Menimcha javob shunda: test "
         "loyihasi shablondan avtomatik yaratiladi, ya'ni uni qo'shish uchun qaror "
         "qabul qilish kerak bo'lmagan. Test **yozish** uchun esa kerak. Shuning uchun "
         "bo'sh test loyihasi mavjudligi hech narsani bildirmaydi, va men boshqa "
         "loyihalarda ham endi `dotnet test` ning yashil natijasiga emas, test "
         "fayllarining soniga qarayman.")

    h1(d, "9. Xulosa")

    bullets(d, [
        "`Substitute.For<T>()` mock yaratadi; `.Object` kerak emas.",
        "Sozlanmagan metodlar sukutdagi qiymat qaytaradi.",
        "`Returns` qiymat, ketma-ketlik yoki hisoblangan natija bera oladi.",
        "Bitta `Arg.` ishlatilsa, barcha argumentlar `Arg.` bo'lishi shart.",
        "`Received(n)`, `DidNotReceive()` va `Received.InOrder` chaqiruvlarni "
        "tekshiradi.",
        "`Arg.Do<T>` argumentni ushlab qolish imkonini beradi.",
        "`sealed` klass, statik va `extension` metodlar mock qilinmaydi.",
        "`NSubstitute.Analyzers` paketi noto'g'ri ishlatilishni kompilyatsiya "
        "vaqtida aniqlaydi.",
    ])

    sources(d, [
        ("NSubstitute — rasmiy hujjat",
         "https://nsubstitute.github.io/help/getting-started/"),
        ("NSubstitute — GitHub",
         "https://github.com/nsubstitute/NSubstitute"),
        ("Unit testing best practices with .NET",
         "https://learn.microsoft.com/en-us/dotnet/core/testing/unit-testing-best-practices"),
    ])
