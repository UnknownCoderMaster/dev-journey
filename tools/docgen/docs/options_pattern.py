# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "Options Pattern"
CATEGORY = "Design pattern"
TITLE = "Options Naqshi"
SUBTITLE = "Konfiguratsiyani tipli obyektlar orqali olish"
FILENAME = "Options Pattern.docx"


def build(d):
    h1(d, "1. Muammo")

    para(d, "Konfiguratsiyani to'g'ridan-to'g'ri `IConfiguration` orqali o'qish "
            "ishlaydi, lekin bir nechta kamchilikka ega:")

    code(d, """// Shunday yozish mumkin, lekin...
var apiKey = _configuration["Payment:ApiKey"];
var timeout = int.Parse(_configuration["Payment:TimeoutSeconds"]!);""")

    bullets(d, [
        "Kalit nomi matn — harf xatosi kompilyatsiyada aniqlanmaydi.",
        "Tip aylantirish qo'lda bajariladi.",
        "Qiymat yo'qligi faqat ish vaqtida bilinadi.",
        "Klass butun konfiguratsiyaga bog'lanadi, aslida unga faqat bir nechta "
        "qiymat kerak.",
    ])

    para(d, "Options naqshi bu muammolarni konfiguratsiya bo'limini oddiy C# "
            "klassiga bog'lash orqali hal qiladi.")

    # ───────────────────────────────────────────
    h1(d, "2. Asosiy ishlatilishi")

    code(d, """// appsettings.json
{
  "Payment": {
    "ApiKey": "...",
    "BaseUrl": "https://pay.example.com",
    "TimeoutSeconds": 30,
    "RetryCount": 3
  }
}""")

    code(d, """public class PaymentOptions
{
    public const string SectionName = "Payment";

    public string ApiKey { get; set; } = string.Empty;
    public string BaseUrl { get; set; } = string.Empty;
    public int TimeoutSeconds { get; set; } = 30;
    public int RetryCount { get; set; } = 3;
}""")

    code(d, """builder.Services.Configure<PaymentOptions>(
    builder.Configuration.GetSection(PaymentOptions.SectionName));""")

    code(d, """public class PaymentService
{
    private readonly PaymentOptions _options;

    public PaymentService(IOptions<PaymentOptions> options)
        => _options = options.Value;

    public async Task ChargeAsync(decimal amount, CancellationToken ct)
    {
        using var client = new HttpClient
        {
            BaseAddress = new Uri(_options.BaseUrl),
            Timeout = TimeSpan.FromSeconds(_options.TimeoutSeconds)
        };
        ...
    }
}""")

    # ───────────────────────────────────────────
    h1(d, "3. Uch xil interfeys")

    table(d, ["Interfeys", "Hayot davri", "Yangilanadimi"],
          [["`IOptions<T>`", "Singleton", "Yo'q — bir marta o'qiladi"],
           ["`IOptionsSnapshot<T>`", "Scoped", "Har so'rovda qayta o'qiladi"],
           ["`IOptionsMonitor<T>`", "Singleton", "O'zgarishni kuzatadi, hodisa beradi"]],
          widths=[4.6, 4.4, 6.5])

    h2(d, "3.1 IOptions")

    para(d, "Eng oddiy variant. Qiymat ilova ishga tushganda bir marta o'qiladi va "
            "keyin o'zgarmaydi. Ulanish satri, API manzili kabi statik sozlamalar "
            "uchun mos.")

    h2(d, "3.2 IOptionsSnapshot")

    para(d, "Har bir so'rov boshida qayta o'qiladi. Konfiguratsiya fayli o'zgarsa, "
            "keyingi so'rov yangi qiymatni ko'radi. Lekin u `Scoped` bo'lgani uchun "
            "`Singleton` xizmatga inyeksiya qilib bo'lmaydi.")

    h2(d, "3.3 IOptionsMonitor")

    code(d, """public class FeatureService
{
    private readonly IOptionsMonitor<FeatureOptions> _monitor;

    public FeatureService(IOptionsMonitor<FeatureOptions> monitor)
    {
        _monitor = monitor;

        _monitor.OnChange(options =>
            _logger.LogInformation("Sozlamalar yangilandi"));
    }

    public bool IsEnabled(string name)
        => _monitor.CurrentValue.Enabled.Contains(name);
}""")

    note(d, "Qaysi birini tanlash — oddiy qoida:",
         "Agar sozlama ilova ishlab turganda o'zgarishi kerak bo'lmasa — "
         "`IOptions`. Agar o'zgarishi mumkin bo'lsa va xizmat `Scoped` bo'lsa — "
         "`IOptionsSnapshot`. Agar xizmat `Singleton` bo'lsa va sozlama "
         "o'zgarishi kerak bo'lsa — `IOptionsMonitor`. Men ko'pincha "
         "`IOptions` bilan cheklanaman, chunki sozlamani o'zgartirish odatda "
         "qayta joylashtirish bilan birga keladi.")

    note(d, "Bitta tez-tez uchraydigan xato:",
         "`IOptionsSnapshot` ni `Singleton` xizmatga inyeksiya qilish "
         "`InvalidOperationException` beradi — \"Cannot consume scoped service "
         "from singleton\". Bu xatolik ilova ishga tushishida chiqadi, bu yaxshi. "
         "Yomoni shundaki, agar `Singleton` ichida `IServiceProvider` orqali "
         "qo'lda olinsa, xatolik chiqmaydi va qiymat hech qachon yangilanmaydi.")

    # ───────────────────────────────────────────
    h1(d, "4. Validatsiya")

    para(d, "Konfiguratsiya noto'g'ri bo'lsa, buni ish vaqtida emas, ilova ishga "
            "tushishida bilish ancha yaxshi.")

    code(d, """public class PaymentOptions
{
    [Required]
    [MinLength(20)]
    public string ApiKey { get; set; } = string.Empty;

    [Required]
    [Url]
    public string BaseUrl { get; set; } = string.Empty;

    [Range(1, 300)]
    public int TimeoutSeconds { get; set; } = 30;
}""")

    code(d, """builder.Services
    .AddOptions<PaymentOptions>()
    .Bind(builder.Configuration.GetSection(PaymentOptions.SectionName))
    .ValidateDataAnnotations()
    .ValidateOnStart();""")

    note(d, "`ValidateOnStart()` eng muhim qism:",
         "Usiz validatsiya faqat `IOptions.Value` birinchi marta o'qilganda "
         "ishlaydi. Agar bu kod faqat to'lov qilinganda bajarilsa, noto'g'ri "
         "konfiguratsiya haqida men birinchi mijoz to'lov qilmoqchi bo'lganda "
         "bilaman. `ValidateOnStart` esa ilovani umuman ishga tushirmaydi — bu "
         "ancha xavfsiz.")

    h2(d, "4.1 Murakkab qoidalar")

    code(d, """builder.Services
    .AddOptions<PaymentOptions>()
    .Bind(section)
    .Validate(o => o.RetryCount <= 5,
              "RetryCount 5 dan oshmasligi kerak")
    .Validate(o => !o.BaseUrl.StartsWith("http://") || o.AllowInsecure,
              "HTTP manzilga AllowInsecure kerak")
    .ValidateOnStart();""")

    h2(d, "4.2 Alohida validator klassi")

    code(d, """public class PaymentOptionsValidator : IValidateOptions<PaymentOptions>
{
    public ValidateOptionsResult Validate(string? name, PaymentOptions options)
    {
        var errors = new List<string>();

        if (string.IsNullOrWhiteSpace(options.ApiKey))
            errors.Add("ApiKey bo'sh");

        if (options.TimeoutSeconds < 1)
            errors.Add("TimeoutSeconds musbat bo'lishi kerak");

        return errors.Count > 0
            ? ValidateOptionsResult.Fail(errors)
            : ValidateOptionsResult.Success;
    }
}

builder.Services.AddSingleton<
    IValidateOptions<PaymentOptions>, PaymentOptionsValidator>();""")

    # ───────────────────────────────────────────
    h1(d, "5. Nomlangan options")

    para(d, "Bir xil tipdagi bir nechta sozlama to'plami kerak bo'lsa:")

    code(d, """{
  "Storage": {
    "Documents": { "Bucket": "docs", "MaxSizeMb": 50 },
    "Images":    { "Bucket": "images", "MaxSizeMb": 5 }
  }
}""")

    code(d, """builder.Services.Configure<StorageOptions>(
    "Documents", config.GetSection("Storage:Documents"));

builder.Services.Configure<StorageOptions>(
    "Images", config.GetSection("Storage:Images"));""")

    code(d, """public class UploadService
{
    private readonly StorageOptions _documents;
    private readonly StorageOptions _images;

    public UploadService(IOptionsSnapshot<StorageOptions> options)
    {
        _documents = options.Get("Documents");
        _images = options.Get("Images");
    }
}""")

    # ───────────────────────────────────────────
    h1(d, "6. Qo'shimcha imkoniyatlar")

    h2(d, "6.1 Kodda o'zgartirish")

    code(d, """builder.Services.Configure<PaymentOptions>(options =>
{
    options.TimeoutSeconds = 60;    // fayldagi qiymat ustiga yoziladi
});""")

    h2(d, "6.2 Post-configure")

    code(d, """builder.Services.PostConfigure<PaymentOptions>(options =>
{
    // Barcha sozlamalardan keyin ishlaydi
    options.BaseUrl = options.BaseUrl.TrimEnd('/');
});""")

    h2(d, "6.3 Testda ishlatish")

    code(d, """var options = Options.Create(new PaymentOptions
{
    ApiKey = "test-key",
    BaseUrl = "https://localhost",
    TimeoutSeconds = 5
});

var service = new PaymentService(options);""")

    note(d, "Bu naqshning testlash uchun qulayligi ham muhim sabab:",
         "`IConfiguration` ni testda to'ldirish uchun lug'at qurish va uni "
         "konfiguratsiya quruvchiga berish kerak. Options bilan esa oddiy "
         "obyekt yarataman — bu ancha qisqa va o'qiladigan bo'ladi.")

    # ───────────────────────────────────────────
    h1(d, "7. Xulosa")

    bullets(d, [
        "Options naqshi konfiguratsiya bo'limini tipli C# klassiga bog'laydi.",
        "`IOptions` — o'zgarmas, `IOptionsSnapshot` — har so'rovda, "
        "`IOptionsMonitor` — kuzatuvchi.",
        "`IOptionsSnapshot` ni `Singleton` xizmatga inyeksiya qilib bo'lmaydi.",
        "`ValidateDataAnnotations` va `ValidateOnStart` noto'g'ri "
        "konfiguratsiyani ilova ishga tushishida aniqlaydi.",
        "Murakkab qoidalar uchun `Validate` yoki `IValidateOptions<T>` "
        "ishlatiladi.",
        "Nomlangan options bir xil tipdagi bir nechta to'plamni ajratadi.",
        "Testda `Options.Create(...)` bilan oddiy obyekt yaratish mumkin.",
    ])

    sources(d, [
        ("Options pattern in .NET",
         "https://learn.microsoft.com/en-us/dotnet/core/extensions/options"),
        ("Options pattern in ASP.NET Core",
         "https://learn.microsoft.com/en-us/aspnet/core/fundamentals/configuration/options"),
        ("Options validation — .NET",
         "https://learn.microsoft.com/en-us/dotnet/core/extensions/options-library-authors"),
    ])
