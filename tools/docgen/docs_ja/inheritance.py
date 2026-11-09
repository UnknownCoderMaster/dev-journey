# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "Inheritance (constructor chaining)"
CATEGORY = "OOP"
TITLE = "Meros va Konstruktor Zanjiri"
SUBTITLE = "base chaqiruvi, initsializatsiya tartibi va merosning narxi"
FILENAME = "Inheritance (constructor chaining).docx"


def build(d):
    h1(d, "1. Meros nima beradi")

    para(d, "Meros bazaviy klassning a'zolarini hosila klassga o'tkazadi. "
            "Buning ikki maqsadi bor: umumiy kodni takrorlamaslik va "
            "**bir xil turdek muomala qilish** imkonini berish "
            "(polimorfizm).")

    code(d, """public abstract class Document
{
    public Guid Id { get; protected init; }
    public DateTimeOffset CreatedAt { get; protected init; }
    public string Number { get; protected init; } = "";

    public abstract string Title { get; }
}

public sealed class Invoice : Document
{
    public decimal Amount { get; init; }
    public override string Title => $"Hisob-faktura {Number}";
}""")

    para(d, "C# da faqat **bitta** klassdan meros olish mumkin, lekin "
            "interfeys cheklanmagan sonda bo'lishi mumkin. Bu ataylab "
            "qilingan — ko'p merosli tillarda \"olmos muammosi\" paydo "
            "bo'ladi, ya'ni ikki bazaviy klassda bir xil a'zo bo'lsa, "
            "qaysi biri ishlashi noaniq bo'lib qoladi.")

    # ───────────────────────────────────────────
    h1(d, "2. Konstruktor zanjiri")

    para(d, "Obyekt yaratilganda konstruktorlar **bazadan hosilaga** "
            "qarab ishlaydi. Hosila konstruktori o'z tanasini bajarishdan "
            "oldin bazaviy konstruktor tugallangan bo'lishi kerak:")

    code(d, """public class Entity
{
    protected Entity(Guid id)
    {
        Console.WriteLine("1. Entity konstruktori");
        Id = id;
    }

    public Guid Id { get; }
}

public class Document : Entity
{
    protected Document(Guid id, string number) : base(id)
    {
        Console.WriteLine("2. Document konstruktori");
        Number = number;
    }

    public string Number { get; }
}

public sealed class Invoice : Document
{
    public Invoice(Guid id, string number, decimal amount) : base(id, number)
    {
        Console.WriteLine("3. Invoice konstruktori");
        Amount = amount;
    }

    public decimal Amount { get; }
}""")

    para(d, "`new Invoice(...)` chaqirilganda chiqish tartibi: 1, 2, 3. "
            "Ya'ni eng chuqur bazaviy klass birinchi bajariladi.")

    h2(d, "base ni yozmasam nima bo'ladi")

    para(d, "Kompilyator `base()` ni, ya'ni **parametrsiz** bazaviy "
            "konstruktorni o'zi chaqiradi. Agar bazaviy klassda "
            "parametrsiz konstruktor bo'lmasa, kompilyatsiya xatosi "
            "chiqadi — va bu foydali, chunki unutilgan initsializatsiyani "
            "oldini oladi.")

    h2(d, "this bilan zanjir")

    para(d, "Bir xil klass ichidagi konstruktorlarni ham zanjirlash mumkin — "
            "bu takrorlanuvchi kodni kamaytiradi:")

    code(d, """public sealed class Money
{
    public Money(decimal amount) : this(amount, "UZS") { }

    public Money(decimal amount, string currency)
    {
        if (amount < 0) throw new ArgumentOutOfRangeException(nameof(amount));
        Amount = amount;
        Currency = currency;
    }

    public decimal Amount { get; }
    public string Currency { get; }
}""")

    para(d, "Validatsiya faqat bitta — asosiy — konstruktorda turadi. "
            "Qolganlari unga yo'naltiradi. Bu qoidani \"bitta haqiqat "
            "manbai\" deb bilaman.")

    # ───────────────────────────────────────────
    h1(d, "3. Initsializatsiya aniq tartibi")

    para(d, "To'liq tartib shunday:")

    bullets(d, [
        "Hosila klassning maydon initsializatorlari (`private int _x = 5;`).",
        "Bazaviy klassning maydon initsializatorlari.",
        "Bazaviy klass konstruktori tanasi.",
        "Hosila klass konstruktori tanasi.",
    ], numbered=True)

    para(d, "Bu tartib bitta jiddiy tuzoqni tushuntiradi — bazaviy "
            "konstruktordan virtual metodni chaqirish:")

    code(d, """public class Base
{
    public Base() => Initialize();          // XAVFLI
    protected virtual void Initialize() { }
}

public sealed class Derived : Base
{
    private readonly List<string> _items = [];

    protected override void Initialize()
        => _items.Add("birinchi");          // NullReferenceException
}""")

    para(d, "`Initialize()` bazaviy konstruktorda chaqiriladi, lekin o'sha "
            "paytda `Derived` ning maydonlari hali to'ldirilmagan — "
            "`_items` `null`. Shuning uchun konstruktordan virtual metod "
            "chaqirishdan qochaman.")

    note(d, "Yechim",
         "Initsializatsiyani konstruktordan keyin alohida metodga "
         "(`InitializeAsync()`) chiqarish yoki fabrika metodidan "
         "foydalanish. Fabrika obyektni to'liq yasab, keyin kerakli "
         "qadamlarni bajaradi.")

    # ───────────────────────────────────────────
    h1(d, "4. abstract, virtual, sealed")

    code(d, """public abstract class Report
{
    // Hosila MAJBURAN amalga oshiradi
    public abstract string Render();

    // Hosila XOHLASA o'zgartiradi
    public virtual string FileName => $"report-{DateTime.UtcNow:yyyyMMdd}.txt";

    // Hosila o'zgartira OLMAYDI
    public string Metadata() => $"{GetType().Name} / {FileName}";
}

public sealed class SalesReport : Report
{
    public override string Render() => "...";
    public override string FileName => "sales.csv";
}""")

    para(d, "`sealed` ni standart holat deb bilaman: klass meros olish "
            "uchun **mo'ljallangan** bo'lmasa, uni yopib qo'yaman. Bu "
            "ikki foyda beradi — kutilmagan meros xatolarini oldini oladi "
            "va JIT ga chaqiruvlarni optimallashtirish imkonini beradi.")

    h2(d, "new bilan yashirish — qochish kerak")

    code(d, """public class Base
{
    public virtual string Name => "Base";
}

public class Derived : Base
{
    public new string Name => "Derived";     // override emas, yashirish
}

Base obj = new Derived();
Console.WriteLine(obj.Name);        // "Base" — kutilmagan natija!""")

    para(d, "`new` metodni almashtirmaydi, faqat yashiradi. Natijada "
            "qaysi versiya ishlashi o'zgaruvchining **e'lon qilingan "
            "turiga** bog'liq bo'ladi — bu polimorfizmni buzadi va "
            "kutilmagan xatti-harakatga olib keladi.")

    # ───────────────────────────────────────────
    h1(d, "5. Merosning narxi va alternativasi")

    para(d, "Meros eng qattiq bog'lanish turi: hosila klass bazaviy "
            "klassning ichki tuzilishiga ham bog'lanadi. Bazaviy klassda "
            "o'zgarish bo'lsa, hamma hosila buziladi — bu \"mo'rt bazaviy "
            "klass\" muammosi.")

    para(d, "Shuning uchun amalda **kompozitsiyani** afzal ko'raman:")

    code(d, """// MEROS: ReportService Logger ning hamma a'zosini oladi
public class ReportService : LoggerBase { }

// KOMPOZITSIYA: faqat kerakli imkoniyat olinadi
public sealed class ReportService(ILogger<ReportService> logger)
{
    public void Generate() => logger.LogInformation("Hisobot yasalmoqda");
}""")

    para(d, "Kompozitsiyada bog'liqlik interfeys orqali o'tadi, shuning "
            "uchun uni testda almashtirish mumkin va amalga oshirish "
            "o'zgarsa `ReportService` tegilmaydi.")

    h2(d, "Qachon meros to'g'ri tanlov")

    bullets(d, [
        "Munosabat haqiqatan \"**bu ham bir** turdagi narsa\" bo'lsa "
        "(`Invoice` — `Document`), va hosila bazaviy turning o'rnida "
        "to'liq ishlay olsa.",
        "Framework talab qilsa — `ControllerBase`, `DbContext`, "
        "`BackgroundService`, `Exception`.",
        "Umumiy xatti-harakat va bir nechta variant bo'lsa — shablon "
        "metod naqshi.",
    ])

    para(d, "\"Kodni qayta ishlatish\" merosni tanlash uchun yetarli asos "
            "emas. Agar faqat bir nechta metodni ulashish kerak bo'lsa, "
            "yordamchi klass yoki kompozitsiya toza yechim bo'ladi.")

    sources(d, [
        ("Inheritance in C#",
         "https://learn.microsoft.com/en-us/dotnet/csharp/fundamentals/object-oriented/inheritance"),
        ("Constructors — C# programming guide",
         "https://learn.microsoft.com/en-us/dotnet/csharp/programming-guide/classes-and-structs/constructors"),
        ("Using constructors",
         "https://learn.microsoft.com/en-us/dotnet/csharp/programming-guide/classes-and-structs/using-constructors"),
        ("sealed — C# reference",
         "https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/keywords/sealed"),
    ])
