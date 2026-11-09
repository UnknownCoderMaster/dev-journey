# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "Pattern Matching (C# 8+)"
CATEGORY = ".NET / C#"
TITLE = "Pattern Matching"
SUBTITLE = "Tur va tuzilishga qarab tekshirish"
FILENAME = "Pattern Matching (C# 8+).docx"


def build(d):
    h1(d, "1. Eng oddiy shakl: type pattern")

    para(d, "Pattern matching'dan oldin tipni tekshirish ikki qadamdan "
            "iborat edi — avval `is`, keyin cast:")

    code(d, """if (shape is Circle)
{
    var circle = (Circle)shape;
    area = Math.PI * circle.Radius * circle.Radius;
}""")

    para(d, "C# 7 dan boshlab ikkisi birlashdi:")

    code(d, """if (shape is Circle circle)
{
    area = Math.PI * circle.Radius * circle.Radius;
}""")

    para(d, "Bu shakl nafaqat qisqa, balki xavfsizroq ham: `circle` "
            "o'zgaruvchisi faqat tekshiruv muvaffaqiyatli bo'lganda mavjud "
            "bo'ladi, shuning uchun noto'g'ri cast qilish imkoni yo'q.")

    # ───────────────────────────────────────────
    h1(d, "2. switch ifodasi")

    para(d, "C# 8 `switch` ni ifodaga aylantirdi — ya'ni u qiymat qaytaradi "
            "va `break` yozish kerak emas:")

    code(d, """decimal CalculateArea(Shape shape) => shape switch
{
    Circle c    => Math.PI * c.Radius * c.Radius,
    Square s    => s.Side * s.Side,
    Rectangle r => r.Width * r.Height,
    _           => throw new NotSupportedException($"Noma'lum shakl: {shape}")
};""")

    para(d, "`_` — discard pattern, ya'ni \"qolgan hamma holat\". Uni "
            "yozmasam va kompilyator hamma variant qoplanmaganini ko'rsa, "
            "ogohlantirish beradi — bu foydali, chunki yangi tur "
            "qo'shilganda esdan chiqmaydi.")

    note(d, "Eslatma",
         "Tartib muhim: pattern'lar yuqoridan pastga tekshiriladi va "
         "birinchi moslashgani ishlaydi. Shuning uchun umumiy pattern'ni "
         "aniqrog'idan oldin yozsam, keyingilari hech qachon "
         "bajarilmaydi — kompilyator bunda xato beradi.")

    # ───────────────────────────────────────────
    h1(d, "3. Pattern turlari")

    h2(d, "Constant va relational pattern")

    code(d, """string Describe(int count) => count switch
{
    0        => "bo'sh",
    1        => "bitta",
    < 0      => "noto'g'ri",
    > 1000   => "juda ko'p",
    _        => "bir nechta"
};""")

    h2(d, "Logical pattern: and, or, not")

    code(d, """bool IsWorkingHour(int hour) => hour is >= 9 and < 18;

bool IsWeekend(DayOfWeek day) => day is DayOfWeek.Saturday or DayOfWeek.Sunday;

if (value is not null) { }""")

    para(d, "`is not null` ko'rinishini `!= null` dan afzal ko'raman, chunki "
            "u operator ortiqcha yuklanishiga (operator overloading) "
            "bog'liq emas — ba'zi turlarda `==` qayta ta'riflangan bo'lishi "
            "mumkin va natija kutilmagan bo'ladi.")

    h2(d, "Property pattern")

    code(d, """string Status(Order order) => order switch
{
    { IsPaid: true, IsShipped: true }  => "yetkazilgan",
    { IsPaid: true }                   => "to'langan",
    { Items.Count: 0 }                 => "bo'sh",
    _                                  => "yangi"
};""")

    para(d, "`Items.Count: 0` — ichma-ich xossaga murojaat (C# 10+). Bu "
            "`order.Items.Count == 0` bilan bir xil, lekin `null` tekshiruvini "
            "o'zi bajaradi: `Items` `null` bo'lsa pattern mos kelmaydi, "
            "exception chiqmaydi.")

    h2(d, "Positional pattern")

    para(d, "Agar turda `Deconstruct` bo'lsa (record'da avtomatik), "
            "qiymatlarni pozitsiya bo'yicha ajratish mumkin:")

    code(d, """public record Point(int X, int Y);

string Quadrant(Point p) => p switch
{
    (0, 0)           => "markaz",
    ( > 0, > 0)      => "birinchi chorak",
    ( < 0, > 0)      => "ikkinchi chorak",
    ( < 0, < 0)      => "uchinchi chorak",
    ( > 0, < 0)      => "to'rtinchi chorak",
    _                => "o'q ustida"
};""")

    h2(d, "List pattern (C# 11)")

    code(d, """string Parse(string[] parts) => parts switch
{
    []                   => "bo'sh",
    [var single]         => $"bitta: {single}",
    ["GET", var path]    => $"o'qish: {path}",
    [_, _, ..var rest]   => $"qolgani: {rest.Length}",
};""")

    para(d, "`..` — slice pattern, qolgan elementlarni oladi. Buyruq "
            "qatorini yoki protokol satrini tahlil qilishda juda qulay.")

    # ───────────────────────────────────────────
    h1(d, "4. when — qo'shimcha shart")

    para(d, "Pattern o'zi ifodalay olmaydigan shart kerak bo'lsa, `when` "
            "qo'shiladi:")

    code(d, """decimal Fee(Payment payment) => payment switch
{
    CardPayment c when c.Amount > 1_000_000 => c.Amount * 0.005m,
    CardPayment c                           => c.Amount * 0.01m,
    CashPayment                              => 0m,
    _ => throw new NotSupportedException()
};""")

    para(d, "`when` ni `catch` bilan ham ishlatish mumkin va bu juda "
            "foydali — faqat ma'lum shartdagi exception ushlanadi:")

    code(d, """try
{
    await _api.SendAsync(request, ct);
}
catch (HttpRequestException ex) when (ex.StatusCode == HttpStatusCode.TooManyRequests)
{
    await Task.Delay(TimeSpan.FromSeconds(5), ct);
}""")

    para(d, "Bu `catch` ichida `if` yozib, mos kelmaganda `throw` qilishdan "
            "yaxshiroq: `when` filtri stack'ni o'ramaydi, shuning uchun "
            "exception'ning asl konteksti saqlanadi.")

    # ───────────────────────────────────────────
    h1(d, "5. Amaliy misol: domen xatosini HTTP javobiga aylantirish")

    code(d, """public static IResult ToHttpResult(this Exception ex) => ex switch
{
    NotFoundException nf =>
        Results.Problem(nf.Message, statusCode: StatusCodes.Status404NotFound),

    ValidationException { Errors.Count: > 0 } ve =>
        Results.ValidationProblem(ve.Errors),

    UnauthorizedAccessException =>
        Results.Problem(statusCode: StatusCodes.Status403Forbidden),

    OperationCanceledException =>
        Results.StatusCode(StatusCodes.Status499ClientClosedRequest),

    _ => Results.Problem(statusCode: StatusCodes.Status500InternalServerError)
};""")

    para(d, "Bu kodni `if/else` zanjiri bilan yozsam, ikki barobar uzun va "
            "o'qish qiyinroq bo'lardi. Pattern matching bu yerda shartlarni "
            "bir xil ko'rinishda tekis saqlaydi.")

    # ───────────────────────────────────────────
    h1(d, "6. Nimaga e'tibor beraman")

    bullets(d, [
        "**`switch` ifodasi tur bo'yicha tarmoqlansa**, bu ko'pincha "
        "polimorfizm o'rniga ishlatilayotganini bildiradi. Agar turlar mening "
        "nazoratimda bo'lsa, virtual metod toza yechim bo'ladi. Pattern "
        "matching esa turlar tashqi bo'lganda yoki mantiq turning o'ziga "
        "tegishli bo'lmaganda to'g'ri tanlov.",
        "**Juda chuqur ichma-ich pattern** o'qilmaydigan bo'lib qoladi. "
        "Ikki darajadan oshsa, oraliq o'zgaruvchi ajrataman.",
        "**`_` ni ehtiyot bilan ishlataman.** U hamma yangi holatni "
        "jimgina yutib yuboradi. Enum yoki yopiq ierarxiyada `_` o'rniga "
        "hamma variantni sanab, kompilyator ogohlantirishiga tayanish "
        "xavfsizroq.",
    ])

    sources(d, [
        ("Pattern matching — C# reference",
         "https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/operators/patterns"),
        ("switch expression",
         "https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/operators/switch-expression"),
        ("Pattern matching tutorial",
         "https://learn.microsoft.com/en-us/dotnet/csharp/fundamentals/functional/pattern-matching"),
    ])
