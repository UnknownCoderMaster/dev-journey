# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = ("polymorphism (method overloading,method overriding,"
         "constructor overloading)")
CATEGORY = "OOP"
TITLE = "Polimorfizm"
SUBTITLE = "Overloading, overriding va konstruktor variantlari"
FILENAME = ("polymorphism (method overloading,method overriding,"
            "constructor overloading).docx")


def build(d):
    h1(d, "1. Polimorfizmning ikki turi")

    para(d, "Polimorfizm — bir xil nom bilan turli xatti-harakatni "
            "ifodalash. U ikki shaklda bo'ladi va ularni ajratish muhim, "
            "chunki qaror turli vaqtda qabul qilinadi.")

    bullets(d, [
        "**Compile-time polymorphism** (overloading) — qaysi metod "
        "chaqirilishini **kompilyator** argumentlarga qarab tanlaydi.",
        "**Runtime polymorphism** (overriding) — qaysi versiya ishlashini "
        "**ish vaqti** obyektning haqiqiy turiga qarab tanlaydi.",
    ])

    # ───────────────────────────────────────────
    h1(d, "2. Method overloading")

    para(d, "Bir xil nomli, lekin turli imzoli metodlar. Imzo — parametrlar "
            "soni, turi va tartibi:")

    code(d, """public sealed class ReportBuilder
{
    public string Build(int year) => Build(year, month: null);

    public string Build(int year, int? month) => /* ... */;

    public string Build(DateOnly from, DateOnly to) => /* ... */;

    public string Build(IEnumerable<Guid> orderIds) => /* ... */;
}""")

    note(d, "Muhim",
         "Qaytish turi imzoga **kirmaydi**. Faqat qaytish turi bilan farq "
         "qiladigan ikki metod yozib bo'lmaydi — kompilyator xato beradi.")

    h2(d, "Kompilyator qanday tanlaydi")

    para(d, "Eng aniq mos keladigan variant tanlanadi. Agar aniq mos "
            "bo'lmasa, yashirin aylantirish (implicit conversion) bilan "
            "mos keladigani izlanadi:")

    code(d, """void Log(object value) => Console.WriteLine($"object: {value}");
void Log(string value) => Console.WriteLine($"string: {value}");
void Log(int value) => Console.WriteLine($"int: {value}");

Log("salom");      // string — aniq mos
Log(42);           // int — aniq mos
Log(3.14);         // object — double uchun aniq variant yo'q
Log(null);         // string — object dan ko'ra aniqroq""")

    para(d, "Oxirgi qator chalg'ituvchi: `null` ikki variantga ham mos "
            "keladi, lekin `string` `object` dan \"aniqroq\" hisoblanadi. "
            "Shuning uchun `null` bilan ishlashda aniq cast yozishni "
            "afzal ko'raman.")

    h2(d, "Ixtiyoriy parametr va overloading birgalikda")

    code(d, """// Noaniqlik: Build(2026) ikkisiga ham mos keladi
public string Build(int year) => "";
public string Build(int year, int month = 1) => "";""")

    para(d, "Bu kod kompilyatsiya o'tadi, lekin `Build(2026)` chaqiruvi "
            "birinchi variantni tanlaydi — chunki ixtiyoriy parametr "
            "to'ldirilgan variant \"kamroq aniq\" hisoblanadi. Natija "
            "kutilganidan boshqa bo'lishi mumkin, shuning uchun ikkisini "
            "aralashtirmaslikka harakat qilaman.")

    # ───────────────────────────────────────────
    h1(d, "3. Method overriding")

    para(d, "Hosila klass bazaviy klassning virtual metodini o'zgartiradi. "
            "Bu haqiqiy polimorfizm: chaqiruvchi aniq turni bilmaydi, "
            "lekin to'g'ri versiya ishlaydi.")

    code(d, """public abstract class Notification
{
    public abstract Task SendAsync(string recipient, string body, CancellationToken ct);

    public virtual bool IsAvailable => true;
}

public sealed class EmailNotification(IMailSender sender) : Notification
{
    public override async Task SendAsync(string recipient, string body, CancellationToken ct)
        => await sender.SendAsync(recipient, "Xabar", body, ct);
}

public sealed class SmsNotification(ISmsGateway gateway) : Notification
{
    public override async Task SendAsync(string recipient, string body, CancellationToken ct)
        => await gateway.SendAsync(recipient, body, ct);

    public override bool IsAvailable => gateway.HasBalance;
}""")

    code(d, """// Chaqiruvchi aniq turni bilmaydi
foreach (var channel in channels.Where(c => c.IsAvailable))
    await channel.SendAsync(user.Contact, message, ct);""")

    para(d, "Yangi kanal qo'shilganda bu tsikl o'zgarmaydi. Shuning uchun "
            "polimorfizm `switch` zanjiridan afzal: yangi variant "
            "qo'shish mavjud kodga tegmaydi.")

    h2(d, "abstract, virtual va new taqqoslashi")

    table(d, ["Kalit so'z", "Bazaviy klassda", "Hosilada"],
          [["`abstract`", "Tanasi yo'q", "`override` majburiy"],
           ["`virtual`", "Standart amalga oshirish bor", "`override` ixtiyoriy"],
           ["(oddiy metod)", "Tanasi bor", "O'zgartirilmaydi"],
           ["`new`", "—", "Yashiradi, almashtirmaydi"]],
          widths=[3.6, 5.6, 5.3])

    para(d, "`new` bilan yashirish polimorfizmni buzadi — qaysi versiya "
            "ishlashi o'zgaruvchining e'lon qilingan turiga bog'liq bo'lib "
            "qoladi. Bu deyarli har doim xato, shuning uchun undan "
            "qochaman.")

    h2(d, "base bilan bazaviy versiyani chaqirish")

    code(d, """public override async Task SendAsync(string recipient, string body, CancellationToken ct)
{
    _logger.LogInformation("SMS yuborilmoqda: {Recipient}", recipient);
    await base.SendAsync(recipient, body, ct);
}""")

    # ───────────────────────────────────────────
    h1(d, "4. Constructor overloading")

    para(d, "Konstruktorlar ham overload qilinadi va bu obyektni turli "
            "yo'llar bilan yaratish imkonini beradi:")

    code(d, """public sealed class DateRange
{
    public DateRange(DateOnly from, DateOnly to)
    {
        if (to < from) throw new ArgumentException("Oxiri boshidan oldin bo'lmaydi");
        From = from;
        To = to;
    }

    public DateRange(DateOnly from, int days)
        : this(from, from.AddDays(days)) { }

    public DateRange(int year, int month)
        : this(new DateOnly(year, month, 1),
               new DateOnly(year, month, DateTime.DaysInMonth(year, month))) { }

    public DateOnly From { get; }
    public DateOnly To { get; }
}""")

    para(d, "Validatsiya faqat bitta konstruktorda. Qolganlari `this` bilan "
            "unga yo'naltiradi, shuning uchun qoida chetlab o'tilmaydi.")

    h2(d, "Fabrika metodlari — ko'pincha aniqroq")

    para(d, "Konstruktorlar soni ko'payganda ularning ma'nosi "
            "tushunarsiz bo'lib qoladi. Nomlangan statik metod aniqroq:")

    code(d, """// Qaysi biri nima? Chaqiruvda tushunarsiz
var a = new DateRange(from, 30);
var b = new DateRange(2026, 11);

// Fabrika bilan — niyat ko'rinadi
var c = DateRange.FromStart(from, days: 30);
var d = DateRange.ForMonth(2026, 11);
var e = DateRange.CurrentWeek(clock);""")

    para(d, "Fabrika metodining yana bir foydasi — u `null` qaytarishi yoki "
            "`Result<T>` bilan xatoni ifodalashi mumkin. Konstruktor esa "
            "faqat exception tashlaydi.")

    # ───────────────────────────────────────────
    h1(d, "5. Interfeys orqali polimorfizm")

    para(d, "Meros shart emas — polimorfizmni interfeys ham beradi va amalda "
            "ko'pincha shu yo'lni tanlayman:")

    code(d, """public interface IPriceRule
{
    decimal Apply(decimal amount);
}

public sealed class SeasonalDiscount : IPriceRule
{
    public decimal Apply(decimal amount) => amount * 0.9m;
}

public sealed class LoyaltyDiscount(int years) : IPriceRule
{
    public decimal Apply(decimal amount) => amount * (1 - Math.Min(years, 5) * 0.02m);
}""")

    code(d, """// Hamma qoida ketma-ket qo'llanadi
var final = rules.Aggregate(amount, (current, rule) => rule.Apply(current));""")

    para(d, "DI container'da bir interfeysga bir nechta amalga oshirish "
            "ro'yxatga olinsa, ularni `IEnumerable<IPriceRule>` sifatida "
            "olish mumkin — yangi qoida qo'shish faqat bitta ro'yxatga "
            "olish qatorini talab qiladi.")

    note(d, "Xulosa",
         "Overloading — qulaylik uchun, bir xil ishni turli kirish bilan "
         "bajarish. Overriding — kengaytirish uchun, yangi variant "
         "qo'shishda mavjud kodni o'zgartirmaslik. Ikkinchisi arxitektura "
         "uchun muhimroq.")

    sources(d, [
        ("Polymorphism — C# programming guide",
         "https://learn.microsoft.com/en-us/dotnet/csharp/fundamentals/object-oriented/polymorphism"),
        ("Member overloading",
         "https://learn.microsoft.com/en-us/dotnet/standard/design-guidelines/member-overloading"),
        ("override — C# reference",
         "https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/keywords/override"),
        ("Constructors",
         "https://learn.microsoft.com/en-us/dotnet/csharp/programming-guide/classes-and-structs/constructors"),
    ])
