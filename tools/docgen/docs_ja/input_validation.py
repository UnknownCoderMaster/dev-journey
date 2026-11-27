# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "Input Validation va Sanitization"
CATEGORY = "Cybersecurity"
TITLE = "Input Validation va Sanitization"
SUBTITLE = "Kiruvchi ma'lumotni tekshirish va xavfsiz ishlatish"
FILENAME = "Input Validation va Sanitization.docx"


def build(d):
    h1(d, "1. Validation va sanitization farqi")

    para(d, "Ikki atama aralashtiriladi, lekin ular turli vazifani "
            "bajaradi va turli joyda qo'llanadi.")

    bullets(d, [
        "**Validation** — ma'lumot **qabul qilinadigan** ekanini "
        "tekshirish. Natija ikki xil: mos yoki mos emas. Mos "
        "bo'lmasa — rad etiladi.",
        "**Sanitization** — ma'lumotni **ishlatish joyiga** xavfsiz "
        "qilib tayyorlash. Masalan HTML ga chiqarishdan oldin "
        "maxsus belgilarni kodlash.",
    ])

    para(d, "Eng muhim tamoyil: validation **kirishda**, sanitization "
            "esa **chiqishda** bo'ladi. Ya'ni ma'lumotni kirishda "
            "\"tozalab\" saqlash emas, balki har bir ishlatish "
            "kontekstiga mos ravishda kodlash kerak.")

    note(d, "Nega kirishda tozalamaslik kerak",
         "Kirishda HTML belgilarini olib tashlasam, foydalanuvchining "
         "haqiqiy ismi `O'Brien` buziladi. Ustiga bir xil ma'lumot "
         "turli joyda turlicha kodlanishi kerak — HTML, JSON, SQL, "
         "URL, CSV uchun qoidalar boshqa. Shuning uchun asl "
         "ma'lumotni saqlab, chiqishda kodlash to'g'ri.")

    # ───────────────────────────────────────────
    h1(d, "2. Allowlist va denylist")

    para(d, "Validation ikki yondashuvdan birini tanlaydi:")

    bullets(d, [
        "**Denylist** — \"bu belgilar yomon\" ro'yxati. Ishonchsiz: "
        "hujumchi ro'yxatda yo'q variantni topadi. `<script>` ni "
        "to'ssam, `<ScRiPt>`, `<img onerror=...>` yoki kodlangan "
        "variant qoladi.",
        "**Allowlist** — \"faqat bu ruxsat etiladi\" ro'yxati. "
        "Ishonchli, chunki kutilmagan narsa avtomatik rad etiladi.",
    ])

    code(d, """// YOMON: denylist
if (input.Contains("<script>")) throw new ValidationException("Xavfli kirish");

// YAXSHI: allowlist
if (!Regex.IsMatch(input, @"^[a-zA-Z0-9\\s\\-']{1,100}$"))
    throw new ValidationException("Faqat harf, raqam va chiziqcha ruxsat etiladi");""")

    para(d, "Allowlist'ni tanlash — xavfsizlikdagi eng muhim "
            "umumiy qoidalardan biri. U faqat validationda emas, "
            "fayl turlari, saralash ustunlari, redirect URL'lari "
            "uchun ham qo'llanadi.")

    # ───────────────────────────────────────────
    h1(d, "3. ASP.NET Core da validation")

    h2(d, "Data annotation")

    code(d, """public sealed class CreateCustomerRequest
{
    [Required(ErrorMessage = "Ism majburiy")]
    [StringLength(100, MinimumLength = 2)]
    public string Name { get; init; } = "";

    [Required]
    [EmailAddress]
    public string Email { get; init; } = "";

    [RegularExpression(@"^\\+998\\d{9}$", ErrorMessage = "Format: +998XXXXXXXXX")]
    public string Phone { get; init; } = "";

    [Range(18, 120)]
    public int Age { get; init; }
}""")

    para(d, "`[ApiController]` atributi qo'yilgan bo'lsa, validatsiya "
            "avtomatik ishlaydi: noto'g'ri so'rovda action **umuman "
            "chaqirilmaydi** va `400` + ProblemDetails qaytadi.")

    h2(d, "FluentValidation")

    code(d, """public sealed class CreateCustomerValidator : AbstractValidator<CreateCustomerRequest>
{
    public CreateCustomerValidator(ICustomerRepository repository)
    {
        RuleFor(x => x.Name)
            .NotEmpty().WithMessage("Ism majburiy")
            .MaximumLength(100)
            .Matches(@"^[\\p{L}\\s\\-']+$").WithMessage("Faqat harflar");

        RuleFor(x => x.Email)
            .NotEmpty()
            .EmailAddress()
            .MustAsync(async (email, ct) => !await repository.EmailExistsAsync(email, ct))
            .WithMessage("Bu email allaqachon ro'yxatdan o'tgan");

        RuleFor(x => x.BirthDate)
            .LessThan(_ => DateOnly.FromDateTime(DateTime.UtcNow))
            .WithMessage("Tug'ilgan sana kelajakda bo'lmaydi");
    }
}""")

    para(d, "FluentValidation'ni murakkab qoidalar uchun afzal "
            "ko'raman: shartli validatsiya, maydonlar orasidagi "
            "bog'liqlik, bazaga murojaat qiladigan tekshiruvlar. "
            "Atributlar esa oddiy, mustaqil qoidalar uchun qulay.")

    # ───────────────────────────────────────────
    h1(d, "4. Har bir kontekst uchun o'z kodlashi")

    para(d, "Bu sanitization'ning asosiy qoidasi. Bir xil ma'lumot "
            "turli joyda turlicha kodlanishi kerak:")

    table(d, ["Kontekst", "Xavf", "Yechim"],
          [["HTML tanasi", "XSS", "HTML encoding"],
           ["HTML atributi", "XSS", "Atribut encoding"],
           ["JavaScript", "XSS", "JS encoding yoki JSON"],
           ["SQL", "SQL injection", "Parametrlangan so'rov"],
           ["Shell buyrug'i", "Command injection", "Argument massivi"],
           ["Fayl yo'li", "Path traversal", "Yo'lni normallashtirish"],
           ["URL", "Open redirect", "Allowlist"],
           ["CSV", "Formula injection", "Prefiks qo'shish"],
           ["Log", "Log injection", "Yangi qator belgilarini olib tashlash"]],
          widths=[3.4, 4.4, 6.7])

    h2(d, "HTML — Razor o'zi kodlaydi")

    code(d, """@* Avtomatik HTML-encode qilinadi — xavfsiz *@
<p>@Model.CustomerName</p>

@* Kodlanmaydi — faqat ishonchli HTML uchun *@
<div>@Html.Raw(Model.Description)</div>""")

    para(d, "`Html.Raw` ishlatishim kerak bo'lsa (masalan boy matn "
            "muharriri natijasi), HTML ni tozalaydigan kutubxona "
            "ishlataman — `HtmlSanitizer` kabi. O'zim regex bilan "
            "HTML tozalashga urinmayman, bu deyarli har doim "
            "chetlab o'tiladi.")

    h2(d, "SQL — parametrlangan so'rov")

    code(d, """// Xavfsiz: interpolatsiya FormattableString sifatida parametrlanadi
db.Customers.FromSql($"SELECT * FROM customers WHERE name = {name}");

// Xavfli: satr allaqachon birlashtirilgan
db.Customers.FromSqlRaw($"SELECT * FROM customers WHERE name = '{name}'");""")

    h2(d, "Fayl yo'li — path traversal")

    code(d, """// ZAIF: ../../etc/passwd
var path = Path.Combine(uploadDir, fileName);

// XAVFSIZ: natijani tekshirish
var fullPath = Path.GetFullPath(Path.Combine(uploadDir, fileName));
if (!fullPath.StartsWith(Path.GetFullPath(uploadDir), StringComparison.Ordinal))
    throw new SecurityException("Yo'l ruxsat etilgan papkadan tashqarida");""")

    para(d, "Eng ishonchli yechim — mijoz bergan fayl nomini umuman "
            "ishlatmaslik: serverda yangi nom (`Guid`) generatsiya "
            "qilib, asl nomni alohida metadata sifatida saqlash.")

    h2(d, "CSV — formula injection")

    code(d, """// Excel =, +, -, @ bilan boshlanadigan katakni formula deb o'qiydi
static string SafeCsvCell(string value)
    => value.Length > 0 && value[0] is '=' or '+' or '-' or '@'
        ? "'" + value
        : value;""")

    para(d, "Bu kam ma'lum, lekin real zaiflik: foydalanuvchi "
            "ismiga `=HYPERLINK(...)` yozsa va hisobot Excel'da "
            "ochilsa, formula bajariladi.")

    # ───────────────────────────────────────────
    h1(d, "5. Validation qayerda bo'lishi kerak")

    para(d, "Javob — **bir nechta qatlamda**, va bu takrorlanish "
            "emas, chunki har biri turli maqsadga xizmat qiladi:")

    bullets(d, [
        "**Mijoz tomonida** — foydalanuvchi qulayligi uchun. "
        "Xavfsizlik uchun emas: uni chetlab o'tish oson.",
        "**API chegarasida** — so'rov shakli va asosiy qoidalar. "
        "Birinchi haqiqiy himoya qatlami.",
        "**Domen ichida** — biznes invariantlari. Bu qatlam qaysi "
        "yo'ldan ma'lumot kelganidan qat'i nazar ishlaydi.",
        "**Bazada** — `NOT NULL`, `CHECK`, `UNIQUE`, FK. Oxirgi "
        "himoya: ilova kodidagi xato ham ma'lumotni buzolmaydi.",
    ])

    note(d, "Mening qoidam",
         "Mijoz tomonidagi validatsiyani **hech qachon** xavfsizlik "
         "chorasi deb hisoblamayman. Har qanday mijoz so'rovni "
         "qo'lda yasashi mumkin — brauzer, Postman yoki `curl` "
         "bilan. Shuning uchun server tomonida har doim qayta "
         "tekshiriladi.")

    # ───────────────────────────────────────────
    h1(d, "6. Ko'p e'tibordan chetda qoladigan joylar")

    bullets(d, [
        "**Mass assignment.** DTO da `IsAdmin` maydoni bo'lsa va u "
        "mapping orqali entity'ga tushsa, foydalanuvchi o'ziga admin "
        "huquqini bera oladi. Shuning uchun so'rov modelida faqat "
        "o'zgartirish ruxsat etilgan maydonlar bo'lishi kerak.",
        "**Fayl turi.** Kengaytmaga ishonmaslik kerak — `.jpg` "
        "nomli fayl ichida bajariladigan kod bo'lishi mumkin. "
        "Haqiqiy turni magic bytes bo'yicha tekshiraman.",
        "**Hajm chegarasi.** Fayl, massiv uzunligi, satr uzunligi, "
        "sahifa hajmi — hammasiga chegara kerak. Chegarasiz "
        "`size=1000000` so'rovi xizmatni to'xtatishi mumkin.",
        "**Raqam chegaralari.** Manfiy miqdor, nol bo'luvchi, "
        "`int` to'lib ketishi.",
        "**Unicode nozikliklari.** Bir xil ko'rinadigan turli "
        "belgilar (homoglif) orqali foydalanuvchi nomini soxtalashtirish. "
        "Normalizatsiya (`string.Normalize()`) yordam beradi.",
    ])

    # ───────────────────────────────────────────
    h1(d, "7. Amaliyotdan: validatsiya pipeline ga chiqarilganda")

    para(d, "Ish joyimdagi MAD ERP tizimida FluentValidation mingdan ortiq faylda "
            "uchraydi — amalda har bir komanda va so'rov uchun validator bor. 5-bo'limda "
            "validatsiya qayerda bo'lishi kerakligi haqida gapirgandim; bu yerda u "
            "kontrollerda ham, ishlovchida ham emas, ularning orasida joylashgan.")

    h2(d, "7.1 ValidationBehaviour — bitta joyda, hamma uchun")

    para(d, "Tizim CQRS bo'yicha qurilgan: kontroller faqat komandani yuboradi, "
            "ishlovchi uni bajaradi. Validatsiya esa MediatR pipeline behaviour "
            "sifatida ikkisining orasiga qo'yilgan:")

    code(d, """public class ValidationBehaviour<TRequest, TResponse> : IPipelineBehavior<TRequest, TResponse>
     where TRequest : notnull
{
    private readonly IEnumerable<IValidator<TRequest>> _validators;

    public async Task<TResponse> Handle(TRequest request,
                                        RequestHandlerDelegate<TResponse> next,
                                        CancellationToken cancellationToken)
    {
        if (_validators.Any())
        {
            var context = new ValidationContext<TRequest>(request);

            var validationResults = await Task.WhenAll(
                _validators.Select(v => v.ValidateAsync(context, cancellationToken)));

            var failures = validationResults
                .Where(r => r.Errors.Any())
                .SelectMany(r => r.Errors)
                .ToList();

            if (failures.Any())
                throw new WbValidationException()
                    .WithCategory("Validation")
                    .WithVisibility(WbExceptionVisibility.CLIENT_VISIBLE)
                    .WithErrors(failures.Select(x => new WbFailure
                    {
                        Key = x.PropertyName,
                        ErrorMessage = x.ErrorMessage
                    }).ToArray());
        }

        return await next();
    }
}""", caption="Erp.Core.Service.Application/ValidationBehaviour.cs")

    para(d, "Validatorlar assembly skaneri bilan ro'yxatga olinadi, ya'ni yangi "
            "validator yozilsa u o'z-o'zidan ishga tushadi — hech qayerda qo'lda "
            "ulash kerak emas. Bu 5-bo'limdagi \"validatsiyani unutib qo'yish\" "
            "xatarini sezilarli kamaytiradi.")

    bullets(d, [
        "`IEnumerable<IValidator<TRequest>>` — bitta komanda uchun bir nechta "
        "validator bo'lishi mumkin va hammasi ishlaydi.",
        "`Task.WhenAll` — ular parallel bajariladi. Agar validatorlar bazaga "
        "murojaat qilsa bu sezilarli tezlik beradi.",
        "Hamma xato **bir vaqtda** qaytariladi, birinchisida to'xtab qolmaydi. "
        "Foydalanuvchi uchun bu muhim: formadagi hamma xato bir ko'rinishda chiqadi.",
        "`next()` faqat xato bo'lmaganda chaqiriladi, ya'ni ishlovchi noto'g'ri "
        "ma'lumotni umuman ko'rmaydi.",
    ])

    h2(d, "7.2 Validator qanday ko'rinadi")

    code(d, """public class AnnouncementCreateCommandValidator : AbstractValidator<AnnouncementCreateCommand>
{
    public AnnouncementCreateCommandValidator()
    {
        RuleFor(x => x.DocNumber)
            .NotEmpty().WithMessage("Hujjat raqami kiritilishi shart!")
            .MaximumLength(30).WithMessage("Hujjat raqami 30 belgidan oshmasligi kerak!");

        RuleFor(x => x.Title)
            .NotEmpty().WithMessage("Sarlavha kiritilishi shart!")
            .MaximumLength(100).WithMessage("Sarlavha 100 belgidan oshmasligi kerak!");

        RuleFor(x => x.EndAt)
            .GreaterThan(x => x.StartAt)
            .When(x => x.StartAt.HasValue && x.EndAt.HasValue)
            .WithMessage("Tugash sanasi boshlanish sanasidan keyin bo'lishi kerak!");

        RuleFor(x => x.Apps)
            .NotEmpty().WithMessage("Kamida bitta modul tanlanishi shart!");
    }
}""")

    para(d, "Oxirgi ikkita qoida 2-bo'limdagi allowlist tamoyilining ko'rinishi. "
            "`GreaterThan` — bu \"nima noto'g'ri\" emas, \"nima to'g'ri\" "
            "degan shart. `MaximumLength(30)` esa bazadagi ustun uzunligi bilan "
            "aynan bir xil, ya'ni validatsiya baza cheklovini takrorlaydi va xato "
            "`DbUpdateException` ga aylanib ketmaydi.")

    note(d, "Bu yerda bir muammoni payqadim:",
         "Xato xabarlari validator ichida to'g'ridan-to'g'ri o'zbek tilida yozilgan. "
         "Tizim esa to'rt tilni qo'llab-quvvatlaydi va boshqa joylarda "
         "`localizationBuilder.For(\"KEY\")` orqali tarjima olinadi. Ya'ni "
         "validatsiya xabarlari tarjima tizimidan tashqarida qolgan. Buni "
         "`WithMessage` o'rniga tarjima kalitini berib tuzatish mumkin, lekin "
         "mingdan ortiq validatorni o'zgartirish kerak bo'ladi. Shuning uchun "
         "o'zim uchun qoida chiqardim: ko'p tilli tizimda birinchi validatordan "
         "boshlab tarjima kalitini ishlatish kerak — keyinroq o'tish juda qimmat.")

    h2(d, "7.3 Sanitizatsiya qayerda")

    para(d, "1-bo'limda validatsiya va sanitizatsiya farqi aytilgan. Bu tizimda "
            "sanitizatsiya deyarli yo'q va bu to'g'ri qaror: ma'lumot bazaga xom "
            "holida saqlanadi, chiqishda esa har bir kontekst o'zini himoya qiladi.")

    para(d, "Lekin 4-bo'limdagi \"har bir kontekst uchun o'z kodlashi\" qoidasi "
            "buzilgan bitta joy uchradi: fayl yuklab berish kodi `Content-Disposition` "
            "sarlavhasini qo'lda qurgan edi. HTTP sarlavhalari faqat ASCII qabul "
            "qiladi, o'zbekcha fayl nomlarida esa `o'`, `g'` va `‘`, `’` belgilari "
            "bor. Natijada Kestrel to'g'ridan-to'g'ri yiqilardi:")

    code(d, """Invalid non-ASCII or control character in header: 0x2018""")

    para(d, "Yechim sanitizatsiya yozish emas edi — ASP.NET Core ning "
            "`FileDownloadName` xossasini ishlatish yetarli bo'ldi, u sarlavhani "
            "RFC 6266 bo'yicha o'zi quradi. Ya'ni to'g'ri javob: kontekstni "
            "biladigan kutubxona funksiyasini topish, o'zi tozalashga urinmaslik.")

    sources(d, [
        ("Model validation in ASP.NET Core",
         "https://learn.microsoft.com/en-us/aspnet/core/mvc/models/validation"),
        ("OWASP Input Validation Cheat Sheet",
         "https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html"),
        ("OWASP XSS Prevention Cheat Sheet",
         "https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html"),
        ("FluentValidation documentation",
         "https://docs.fluentvalidation.net/"),
    ])
