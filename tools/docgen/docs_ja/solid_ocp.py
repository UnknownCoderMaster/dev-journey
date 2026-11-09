# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "Solid (OCP)"
CATEGORY = "Principles"
TITLE = "OCP — Open/Closed Principle"
SUBTITLE = "Kengaytirishga ochiq, o'zgartirishga yopiq"
FILENAME = "Solid (OCP).docx"


def build(d):
    h1(d, "1. Printsip nima deydi")

    para(d, "Modul **kengaytirishga ochiq**, lekin **o'zgartirishga "
            "yopiq** bo'lishi kerak. Ya'ni yangi xatti-harakat qo'shish "
            "uchun mavjud, sinalgan kodga tegish kerak bo'lmasin.")

    para(d, "Buning amaliy ma'nosi: yangi funksiya qo'shganda ishlab "
            "turgan kodni buzish xavfi yo'q. Chunki sinalgan kod "
            "o'zgarmaydi — faqat yangi kod qo'shiladi.")

    # ───────────────────────────────────────────
    h1(d, "2. Buzilishga misol: o'sib boruvchi switch")

    code(d, """public sealed class PaymentProcessor
{
    public async Task ProcessAsync(Payment payment, CancellationToken ct)
    {
        switch (payment.Method)
        {
            case "card":
                await _cardGateway.ChargeAsync(payment.Amount, payment.CardToken, ct);
                break;

            case "cash":
                await _cashRegister.RegisterAsync(payment.Amount, ct);
                break;

            case "transfer":
                await _bank.CreateTransferAsync(payment.Amount, payment.Account, ct);
                break;

            // Har yangi usul shu faylni o'zgartirishni talab qiladi
            default:
                throw new NotSupportedException(payment.Method);
        }
    }
}""")

    para(d, "To'lov usuli qo'shilganda shu fayl o'zgaradi. Muammo faqat "
            "qulaylikda emas: har bir o'zgarish mavjud, ishlab turgan "
            "uch tarmoqni ham qayta sinashni talab qiladi. Va bunday "
            "`switch` odatda bitta joyda qolmaydi — komissiya hisoblash, "
            "chek yasash, hisobot uchun ham shunga o'xshash zanjir paydo "
            "bo'ladi.")

    # ───────────────────────────────────────────
    h1(d, "3. Strategiya naqshi bilan yechim")

    code(d, """public interface IPaymentHandler
{
    PaymentMethod Method { get; }
    Task ProcessAsync(Payment payment, CancellationToken ct);
}

public sealed class CardPaymentHandler(ICardGateway gateway) : IPaymentHandler
{
    public PaymentMethod Method => PaymentMethod.Card;

    public Task ProcessAsync(Payment payment, CancellationToken ct)
        => gateway.ChargeAsync(payment.Amount, payment.CardToken!, ct);
}

public sealed class CashPaymentHandler(ICashRegister register) : IPaymentHandler
{
    public PaymentMethod Method => PaymentMethod.Cash;

    public Task ProcessAsync(Payment payment, CancellationToken ct)
        => register.RegisterAsync(payment.Amount, ct);
}""")

    code(d, """public sealed class PaymentProcessor(IEnumerable<IPaymentHandler> handlers)
{
    private readonly Dictionary<PaymentMethod, IPaymentHandler> _handlers =
        handlers.ToDictionary(h => h.Method);

    public Task ProcessAsync(Payment payment, CancellationToken ct)
        => _handlers.TryGetValue(payment.Method, out var handler)
            ? handler.ProcessAsync(payment, ct)
            : throw new NotSupportedException($"Qo'llanmaydi: {payment.Method}");
}""")

    code(d, """// Yangi usul qo'shish — faqat yangi fayl va bitta qator
builder.Services.AddScoped<IPaymentHandler, CardPaymentHandler>();
builder.Services.AddScoped<IPaymentHandler, CashPaymentHandler>();
builder.Services.AddScoped<IPaymentHandler, CryptoPaymentHandler>();   // yangi""")

    para(d, "`PaymentProcessor` endi hech qachon o'zgarmaydi. Yangi "
            "to'lov usuli — yangi klass va bitta ro'yxatga olish qatori.")

    # ───────────────────────────────────────────
    h1(d, "4. Boshqa amalga oshirish yo'llari")

    h2(d, "Keyed services (.NET 8+)")

    code(d, """builder.Services.AddKeyedScoped<IPaymentHandler, CardPaymentHandler>("card");
builder.Services.AddKeyedScoped<IPaymentHandler, CashPaymentHandler>("cash");""")

    code(d, """public sealed class PaymentProcessor(IServiceProvider provider)
{
    public Task ProcessAsync(Payment payment, CancellationToken ct)
    {
        var handler = provider.GetRequiredKeyedService<IPaymentHandler>(payment.Method);
        return handler.ProcessAsync(payment, ct);
    }
}""")

    h2(d, "Polimorfizm — mantiq turning o'ziga tegishli bo'lsa")

    code(d, """public abstract class Payment
{
    public abstract decimal CalculateFee();
}

public sealed class CardPayment : Payment
{
    public override decimal CalculateFee() => Amount * 0.01m;
}""")

    h2(d, "Qoidalar zanjiri")

    code(d, """public interface IDiscountRule
{
    bool AppliesTo(Order order);
    decimal Apply(decimal amount, Order order);
}

public sealed class DiscountEngine(IEnumerable<IDiscountRule> rules)
{
    public decimal Calculate(Order order) =>
        rules.Where(r => r.AppliesTo(order))
             .Aggregate(order.Subtotal, (amount, rule) => rule.Apply(amount, order));
}""")

    para(d, "Chegirma qoidalari aynan shunday naqsh uchun yaratilgan: "
            "ularning soni doimiy o'sadi va ular tez-tez o'zgaradi.")

    # ───────────────────────────────────────────
    h1(d, "5. Printsipni haddan oshirib qo'llash")

    para(d, "OCP ni oldindan qo'llash — eng ko'p uchraydigan ortiqcha "
            "injiniring shakli. Bitta variant bo'lgan joyda interfeys, "
            "fabrika va strategiya qurish kodni to'rt barobar "
            "murakkablashtiradi va hech qanday foyda bermaydi.")

    code(d, """// Bitta amalga oshirish, boshqasi kutilmaydi — bu abstraksiya bejiz
public interface IOrderNumberFormatter
{
    string Format(int sequence);
}""")

    note(d, "Mening qoidam",
         "Ikkinchi variant **paydo bo'lganda** abstraksiya qo'yaman, "
         "oldin emas. Birinchi marta `switch` yozsam, uni qoldiraman. "
         "Uchinchi tarmoq qo'shilganda esa bu naqsh kerakligi aniq "
         "bo'ladi va shundagina refactor qilaman.")

    para(d, "Buni \"ikki marta takrorlangandan keyin\" qoidasi deb ham "
            "ataladi. Oldindan qurilgan abstraksiya ko'pincha noto'g'ri "
            "joyda bo'lib chiqadi — chunki haqiqiy o'zgarish yo'nalishini "
            "bilmasdan taxmin qilgan bo'laman.")

    # ───────────────────────────────────────────
    h1(d, "6. Qachon switch qoldirish to'g'ri")

    para(d, "Hamma `switch` ni yo'qotish kerak degan fikr noto'g'ri. "
            "Variantlar to'plami **yopiq va barqaror** bo'lsa, `switch` "
            "toza yechim:")

    code(d, """public static string ToUzbek(this DayOfWeek day) => day switch
{
    DayOfWeek.Monday    => "Dushanba",
    DayOfWeek.Tuesday   => "Seshanba",
    DayOfWeek.Wednesday => "Chorshanba",
    DayOfWeek.Thursday  => "Payshanba",
    DayOfWeek.Friday    => "Juma",
    DayOfWeek.Saturday  => "Shanba",
    DayOfWeek.Sunday    => "Yakshanba"
};""")

    para(d, "Hafta kunlari soni o'zgarmaydi, shuning uchun bu yerda "
            "strategiya naqshi faqat zarar keltiradi. Ustiga "
            "`switch` ifodasining bitta afzalligi bor: kompilyator hamma "
            "variant qoplanmaganini ko'rsa ogohlantiradi — strategiya "
            "naqshida bunday himoya yo'q.")

    para(d, "Shuning uchun savol shunday: **variantlar ro'yxati "
            "o'sishi kutilmoqdami?** Ha bo'lsa — OCP qo'llanadi. Yo'q "
            "bo'lsa — `switch` qoladi.")

    sources(d, [
        ("Open-closed principle",
         "https://learn.microsoft.com/en-us/dotnet/architecture/modern-web-apps-azure/architectural-principles#open-closed"),
        ("Strategy pattern in .NET",
         "https://learn.microsoft.com/en-us/dotnet/architecture/microservices/"),
        ("Keyed services in dependency injection",
         "https://learn.microsoft.com/en-us/dotnet/core/extensions/dependency-injection#keyed-services"),
    ])
