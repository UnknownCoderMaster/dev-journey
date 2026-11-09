# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "Method mocking"
CATEGORY = "Testing"
TITLE = "Metodlarni Mock Qilish"
SUBTITLE = "Bog'liqliklarni sinov uchun almashtirish"
FILENAME = "Method mocking.docx"


def build(d):
    h1(d, "1. Nima uchun mock kerak")

    para(d, "Birlik testi bitta klassning xatti-harakatini tekshiradi. Lekin "
            "ko'pchilik klasslar boshqalarga bog'liq bo'ladi — bazaga, tashqi "
            "API ga, vaqtga, fayl tizimiga.")

    para(d, "Bu bog'liqliklarni haqiqiy holda ishlatish testni sekin, beqaror va "
            "ba'zan umuman imkonsiz qiladi. Mock — ularni nazorat qilinadigan "
            "o'rinbosarlar bilan almashtirish usuli.")

    code(d, """public class OrderService
{
    private readonly IOrderRepository _repo;
    private readonly IPaymentGateway _payment;
    private readonly IEmailSender _email;

    // Test uchun uchalasini ham almashtirish kerak bo'ladi
}""")

    note(d, "Mock qilish imkoniyati dizayn haqida ham xabar beradi:",
         "Agar klassni testlash uchun o'nta bog'liqlikni almashtirish kerak "
         "bo'lsa, demak u juda ko'p ish qilyapti. Men buni dizayn muammosining "
         "belgisi deb qabul qilaman — test qiyinlashyapti, chunki klass "
         "murakkablashgan.")

    # ───────────────────────────────────────────
    h1(d, "2. Test dublyorlarining turlari")

    table(d, ["Turi", "Nima qiladi"],
          [["Dummy", "Faqat parametr sifatida uzatiladi, ishlatilmaydi"],
           ["Stub", "Oldindan belgilangan qiymat qaytaradi"],
           ["Mock", "Chaqiruvlarni yozib boradi va ularni tekshiradi"],
           ["Spy", "Haqiqiy obyekt, lekin chaqiruvlarni ham qayd qiladi"],
           ["Fake", "Soddalashtirilgan, lekin ishlaydigan amalga oshirish"]],
          widths=[3.0, 12.5])

    para(d, "Amalda bu atamalar tez-tez aralashtiriladi va hammasi \"mock\" deb "
            "ataladi. Lekin farqni bilish testning nimani tekshirayotganini "
            "aniqroq tushunishga yordam beradi.")

    code(d, """// Stub — qiymat qaytaradi, tekshirilmaydi
repo.GetByIdAsync(1).Returns(book);

// Mock — chaqirilganini tekshiramiz
await email.Received(1).SendAsync(Arg.Any<string>(), Arg.Any<string>());

// Fake — ishlaydigan soddalashtirilgan versiya
public class InMemoryOrderRepository : IOrderRepository
{
    private readonly List<Order> _orders = new();
    public Task AddAsync(Order o, CancellationToken ct) { _orders.Add(o); return Task.CompletedTask; }
}""")

    # ───────────────────────────────────────────
    h1(d, "3. Mock qilish uchun shart — abstraksiya")

    para(d, "Mock kutubxonalari interfeyslar va `virtual` metodlar bilan ishlaydi. "
            "Ular ish vaqtida yangi tip generatsiya qiladi, shuning uchun "
            "`sealed` klass yoki statik metodni almashtira olmaydi.")

    code(d, """// Mock qilinadi
public interface IClock { DateTime UtcNow { get; } }

// Mock qilinmaydi
public static class DateTimeHelper
{
    public static DateTime Now => DateTime.UtcNow;
}""")

    h2(d, "3.1 Vaqt bilan bog'liq kod")

    para(d, "`DateTime.UtcNow` ni to'g'ridan-to'g'ri ishlatish testni "
            "noaniqlashtiradi. Yechim — vaqtni abstraksiya ortiga olish:")

    code(d, """// .NET 8 dan boshlab platformada bor
public class SubscriptionService
{
    private readonly TimeProvider _time;

    public SubscriptionService(TimeProvider time) => _time = time;

    public bool IsExpired(Subscription s)
        => s.ExpiresAt < _time.GetUtcNow();
}""")

    code(d, """// Testda
var time = new FakeTimeProvider(
    new DateTimeOffset(2026, 10, 31, 0, 0, 0, TimeSpan.Zero));

var service = new SubscriptionService(time);

time.Advance(TimeSpan.FromDays(40));   // vaqtni oldinga suramiz""")

    note(d, "Bu menga juda yoqqan qo'shimcha:",
         "Avval o'zim `IClock` interfeysini yozardim. `.NET 8` dan boshlab "
         "`TimeProvider` platformaning o'zida bor va `Microsoft.Extensions."
         "TimeProvider.Testing` paketida `FakeTimeProvider` ham bor. Endi "
         "vaqtni oldinga surish, timer larni tezlashtirish — hammasi tayyor.")

    # ───────────────────────────────────────────
    h1(d, "4. Nimani mock qilish, nimani qilmaslik")

    bullets(d, [
        "**Mock qilinadi:** tashqi API, email yuborish, to'lov tizimi, fayl "
        "tizimi, vaqt, tasodifiy sonlar.",
        "**Odatda mock qilinmaydi:** domen obyektlari, qiymat obyektlari, "
        "oddiy hisoblashlar.",
        "**Munozarali:** ma'lumotlar bazasi — mock o'rniga ko'pincha haqiqiy "
        "baza konteyneri afzalroq.",
    ])

    note(d, "Bazani mock qilish haqida alohida fikrim bor:",
         "`DbContext` ni mock qilish texnik jihatdan mumkin, lekin natija "
         "ishonchsiz bo'ladi — LINQ so'rovi xotirada boshqacha ishlaydi va "
         "bazada xato beradigan kod testda muvaffaqiyatli o'tadi. Shuning uchun "
         "men baza bilan ishlaydigan kodni haqiqiy bazada, Testcontainers "
         "orqali tekshiraman.")

    note(d, "Haddan ortiq mock qilishning belgisi:",
         "Agar test faqat mock larni sozlashdan va keyin ularning chaqirilganini "
         "tekshirishdan iborat bo'lsa, u aslida hech narsani tekshirmayapti — "
         "faqat kodning hozirgi tuzilishini takrorlayapti. Bunday test "
         "refaktoring paytida buziladi, lekin xatolikni topmaydi.")

    # ───────────────────────────────────────────
    h1(d, "5. Holat va xatti-harakat tekshiruvi")

    para(d, "Ikki xil tekshirish usuli mavjud va ularni ongli tanlash kerak.")

    code(d, """// Holat tekshiruvi — natijaga qaraymiz
var result = await service.CreateOrderAsync(command, ct);

Assert.Equal(OrderStatus.Pending, result.Status);
Assert.Equal(3, result.Quantity);""")

    code(d, """// Xatti-harakat tekshiruvi — chaqiruvga qaraymiz
await service.CreateOrderAsync(command, ct);

await _email.Received(1).SendAsync(
    "customer@example.com",
    Arg.Is<string>(body => body.Contains("buyurtma")));""")

    note(d, "Qaysi birini qachon tanlayman:",
         "Agar metod natija qaytarsa — holatni tekshiraman, bu mustahkamroq. "
         "Xatti-harakat tekshiruvini esa faqat yon ta'sir muhim bo'lganda "
         "ishlataman — masalan email haqiqatan yuborilganini bilish kerak "
         "bo'lganda. Birinchisi kod tuzilishiga bog'liq emas, ikkinchisi esa "
         "bog'liq.")

    # ───────────────────────────────────────────
    h1(d, "6. Mocksiz yondashuvlar")

    h2(d, "6.1 Qo'lda yozilgan fake")

    code(d, """public class FakeEmailSender : IEmailSender
{
    public List<(string To, string Subject)> Sent { get; } = new();

    public Task SendAsync(string to, string subject, CancellationToken ct = default)
    {
        Sent.Add((to, subject));
        return Task.CompletedTask;
    }
}""")

    code(d, """var email = new FakeEmailSender();
var service = new OrderService(repo, payment, email);

await service.CreateOrderAsync(command, ct);

Assert.Single(email.Sent);
Assert.Equal("customer@example.com", email.Sent[0].To);""")

    note(d, "Bu usul ko'pincha mock kutubxonasidan o'qiladiganroq:",
         "Ayniqsa bitta fake ko'p testda ishlatilsa. Mock sozlash kodi har bir "
         "testda takrorlanadi, fake esa bir marta yoziladi. Bundan tashqari fake "
         "ni oddiy kod sifatida o'qish mumkin — maxsus sintaksis kerak emas.")

    h2(d, "6.2 Sof funksiyalarni ajratish")

    para(d, "Eng yaxshi yechim — mock umuman kerak bo'lmasligi. Hisoblash mantiqini "
            "yon ta'sirlardan ajratsam, uni to'g'ridan-to'g'ri testlay olaman:")

    code(d, """// Mock kerak emas — sof funksiya
public static decimal CalculateDiscount(
    decimal total, int customerYears, bool isHoliday)
{
    var rate = customerYears switch
    {
        >= 5 => 0.15m,
        >= 2 => 0.10m,
        _ => 0.05m
    };

    if (isHoliday) rate += 0.05m;
    return Math.Round(total * rate, 2);
}""")

    code(d, """[Theory]
[InlineData(100_000, 1, false, 5_000)]
[InlineData(100_000, 3, false, 10_000)]
[InlineData(100_000, 7, true, 20_000)]
public void CalculateDiscount_returns_expected(
    decimal total, int years, bool holiday, decimal expected)
{
    Assert.Equal(expected, Discounts.CalculateDiscount(total, years, holiday));
}""")

    # ───────────────────────────────────────────
    h1(d, "7. Xulosa")

    bullets(d, [
        "Mock bog'liqliklarni nazorat qilinadigan o'rinbosar bilan almashtiradi.",
        "Stub qiymat qaytaradi, mock chaqiruvni tekshiradi, fake ishlaydigan "
        "soddalashtirilgan versiya.",
        "Mock kutubxonalari interfeys va `virtual` metod talab qiladi — statik "
        "metodni almashtirib bo'lmaydi.",
        "Vaqtni `TimeProvider` orqali abstraksiya qilish kerak; "
        "`FakeTimeProvider` testda vaqtni boshqarish imkonini beradi.",
        "`DbContext` ni mock qilish ishonchsiz — haqiqiy baza konteyneri "
        "afzalroq.",
        "Holat tekshiruvi xatti-harakat tekshiruvidan mustahkamroq.",
        "Qo'lda yozilgan fake ko'pincha mock sozlashdan o'qiladiganroq.",
        "Eng yaxshisi — mantiqni sof funksiyalarga ajratib, mock ni umuman "
        "kerak qilmaslik.",
    ])

    sources(d, [
        ("Unit testing best practices with .NET",
         "https://learn.microsoft.com/en-us/dotnet/core/testing/unit-testing-best-practices"),
        ("Mocks Aren't Stubs — Martin Fowler",
         "https://martinfowler.com/articles/mocksArentStubs.html"),
        ("TimeProvider class — .NET",
         "https://learn.microsoft.com/en-us/dotnet/api/system.timeprovider"),
    ])
