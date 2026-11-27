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

    # ───────────────────────────────────────────
    h1(d, "7. Amaliyotdan: holat o'tishlari jadvali switch ifodasida")

    para(d, "Ish joyimdagi MAD ERP tizimida hujjatlar hayot davri bo'ylab o'tadi: "
            "yaratildi, yuborildi, tasdiqlandi, imzolandi, arxivlandi va boshqalar. "
            "Yigirmadan ortiq holat bor, va har bir holatdan har qanday holatga "
            "o'tish mumkin emas — masalan \"o'chirilgan\" hujjatni tasdiqlab bo'lmaydi.")

    para(d, "Bu qoidalar bitta sof funksiyada jamlangan va u 2-bo'limdagi `switch` "
            "ifodasining menga ko'rgan eng aniq ishlatilishi bo'ldi:")

    code(d, """public static bool CanApplyStatus(int currentStatusId, int newStatusId)
{
    return newStatusId switch
    {
        ARCHIVED       => new[] { ACCEPTED }.Contains(currentStatusId),
        NOT_ACCEPTED   => new[] { SENT }.Contains(currentStatusId),
        DELETED        => CanDeleteStatus.Contains(currentStatusId),
        MODIFIED       => CanModifyStatus.Contains(currentStatusId),
        ACCEPTED       => CanAcceptStatus.Contains(currentStatusId),
        CANCELED       => CanCancelStatus.Contains(currentStatusId),
        APPROVED       => CanApproveStatus.Contains(currentStatusId),
        SENT           => CanSentStatus.Contains(currentStatusId),
        SENT_FOR_SIGN  => CanSentForSignStatus.Contains(currentStatusId),
        SIGNED         => CanSignedStatus.Contains(currentStatusId),
        REJECTED       => CanRejectStatus.Contains(currentStatusId),
        SEND_TO_UZASBO => CanSendToUzAsboStatus.Contains(currentStatusId),
        IN_TESTING     => CanInTestingStatus.Contains(currentStatusId),
        COMPLETED      => CanCompletedStatus.Contains(currentStatusId),
        _              => false,
    };
}""", caption="Erp.Core/Constants/StatusIdConst.cs, qisqartirilgan")

    para(d, "Ishlatilishi — har bir ishlovchida, holatni o'zgartirishdan oldin:")

    code(d, """if (!StatusIdConst.CanApplyStatus(entity.StatusId, StatusIdConst.APPROVED))
    throw new WbClientException()
        .WithVisibility(WbExceptionVisibility.CLIENT_VISIBLE)
        .WithErrors(new WbFailure { Key = "INVALID_STATUS", ErrorMessage = message });""")

    h2(d, "7.1 Nega bu switch ifodasi, switch bloki emas")

    para(d, "Bu yerda 2-bo'limda sanab o'tgan hamma yutuq bir vaqtda ishlaydi:")

    bullets(d, [
        "**Hammasi bitta ifoda.** Metod `return newStatusId switch` dan boshlanadi "
        "va shu bilan tugaydi. Oraliq o'zgaruvchi, `break`, bir nechta `return` yo'q.",
        "**`_ => false` majburiy.** Kompilyator har bir yo'lda qiymat qaytarilishini "
        "talab qiladi. Ro'yxatga yangi holat qo'shilsa va uning qatori yozilmasa, "
        "u jimgina \"ruxsat yo'q\" ga tushadi — bu xavfsiz standart. Teskari tanlov "
        "(`_ => true`) bir qator unutilganda butun tekshiruvni teshib qo'yardi.",
        "**Ustunma-ustun o'qiladi.** Yigirma qator bir xil shaklda turganda ro'yxatni "
        "jadval kabi ko'rish mumkin. `switch` bloki bo'lsa har bir holat uchta qator "
        "(`case`, `return`, `break`) olardi va bu o'qishni ancha qiyinlashtirardi.",
    ])

    h2(d, "7.2 Lekin bu pattern matching ning o'zi emas")

    para(d, "Halol aytish kerak: bu yerda hech qanday naqsh yo'q. Holatlar `int` "
            "konstantalar, shuning uchun bu oddiy constant pattern — 3-bo'limdagi "
            "eng sodda tur. Type pattern, property pattern yoki `when` sharti "
            "ishlatilmagan.")

    para(d, "Agar holatlar `enum` bo'lganida ham shakl o'zgarmasdi. Agar hujjat "
            "turlari sinflar bo'lganida esa type pattern ishlatilardi:")

    code(d, """// Shunday bo'lishi mumkin edi, lekin loyihada bunday emas
bool canApply = document switch
{
    Commission { StatusId: SENT } => newStatus is APPROVED or NOT_ACCEPTED,
    StudentPayment { Amount: > 0 } => newStatus is ACCEPTED,
    _ => false,
};""")

    note(d, "Shundan chiqargan xulosam:",
         "`switch` ifodasining asosiy foydasi pattern larda emas, **shaklda** — "
         "u qoidalar ro'yxatini kodda jadval sifatida ko'rsatish imkonini beradi. "
         "Yigirmadan ortiq qoidani `if-else` zanjiri bilan yozsam, hech kim uni "
         "oxirigacha o'qib chiqmasdi. Shuning uchun bu mavzuni o'rganishda men "
         "avval murakkab naqshlarga qiziqqan edim, amalda esa eng ko'p foyda "
         "beradigan narsa — eng oddiy shakl bo'lib chiqdi.")

    para(d, "6-bo'limda e'tibor beradigan narsalarim sifatida aytganlarimga shuni "
            "qo'shardim: `_` tarmog'ida qaysi qiymat qaytishini tanlash xavfsizlik "
            "qarori. Bu yerda u `false`, ya'ni \"bilmasam — ruxsat bermayman\".")

    sources(d, [
        ("Pattern matching — C# reference",
         "https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/operators/patterns"),
        ("switch expression",
         "https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/operators/switch-expression"),
        ("Pattern matching tutorial",
         "https://learn.microsoft.com/en-us/dotnet/csharp/fundamentals/functional/pattern-matching"),
    ])
