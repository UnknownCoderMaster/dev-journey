# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "Configuration"
CATEGORY = "ASP.NET"
TITLE = "Konfiguratsiya"
SUBTITLE = "Manbalar tartibi, bog'lash va validatsiya"
FILENAME = "Configuration.docx"


def build(d):
    h1(d, "1. Konfiguratsiya manbalari va ularning tartibi")

    para(d, "ASP.NET Core konfiguratsiyani bir nechta manbadan **ustma-ust** "
            "yuklaydi. Keyingi manba oldingisining bir xil kalitini bosib "
            "ketadi. Standart tartib shunday:")

    bullets(d, [
        "`appsettings.json`",
        "`appsettings.{Environment}.json`",
        "User Secrets (faqat Development muhitida)",
        "Environment variables",
        "Komanda qatori argumentlari",
    ], numbered=True)

    para(d, "Bu tartib amalda juda qulay: umumiy qiymatlar faylda turadi, "
            "muhitga xos qiymatlar environment variable bilan almashtiriladi "
            "va kodga tegish kerak bo'lmaydi.")

    code(d, """// appsettings.json
{
  "ConnectionStrings": {
    "Default": "Host=localhost;Database=shop;Username=dev"
  },
  "Smtp": {
    "Host": "smtp.example.com",
    "Port": 587,
    "EnableSsl": true
  },
  "Logging": {
    "LogLevel": { "Default": "Information" }
  }
}""")

    # ───────────────────────────────────────────
    h1(d, "2. Ierarxiyani tekis kalitga aylantirish")

    para(d, "Konfiguratsiya ichida JSON ierarxiya bor, lekin saqlanishi "
            "tekis — kalitlar ikki nuqta bilan birlashtiriladi:")

    code(d, """var host = configuration["Smtp:Host"];
var port = configuration.GetValue<int>("Smtp:Port");
var cs   = configuration.GetConnectionString("Default");""")

    para(d, "Environment variable'da ikki nuqta hamma OS da ishlamaydi, "
            "shuning uchun uning o'rniga ikki pastki chiziq ishlatiladi:")

    code(d, """# Linux / Docker
export Smtp__Host=smtp.gmail.com
export ConnectionStrings__Default="Host=db;Database=shop"

# Windows PowerShell
$env:Smtp__Host = "smtp.gmail.com"
""")

    para(d, "Massiv elementlari indeks bilan ko'rsatiladi:")

    code(d, """export Cors__AllowedOrigins__0=https://app.example.com
export Cors__AllowedOrigins__1=https://admin.example.com""")

    # ───────────────────────────────────────────
    h1(d, "3. Options pattern — satr kalitlardan voz kechish")

    para(d, "`configuration[\"Smtp:Host\"]` ishlaydi, lekin kalit matn "
            "bo'lgani uchun harf xatosi kompilyatsiyada aniqlanmaydi. "
            "Bir marta `\"Smpt:Host\"` deb yozilsa, qiymat `null` bo'ladi va "
            "bu faqat ish vaqtida — ba'zan oylar o'tib — seziladi.")

    para(d, "Shuning uchun konfiguratsiyani tipik klassga bog'laman:")

    code(d, """public sealed class SmtpOptions
{
    public const string Section = "Smtp";

    [Required]
    public string Host { get; init; } = "";

    [Range(1, 65535)]
    public int Port { get; init; } = 587;

    public bool EnableSsl { get; init; } = true;
}""")

    code(d, """builder.Services.AddOptions<SmtpOptions>()
    .BindConfiguration(SmtpOptions.Section)
    .ValidateDataAnnotations()
    .ValidateOnStart();""")

    para(d, "`ValidateOnStart()` eng muhim qism: konfiguratsiya noto'g'ri "
            "bo'lsa ilova **ko'tarilmaydi**. Usiz xato faqat birinchi "
            "ishlatilganda chiqadi — ya'ni allaqachon production'da.")

    code(d, """public sealed class MailSender(IOptions<SmtpOptions> options)
{
    private readonly SmtpOptions _options = options.Value;
}""")

    # ───────────────────────────────────────────
    h1(d, "4. IOptions, IOptionsSnapshot, IOptionsMonitor")

    table(d, ["Interfeys", "Hayot davri", "O'zgarishni ko'radimi"],
          [["`IOptions<T>`", "Singleton", "Yo'q — bir marta o'qiladi"],
           ["`IOptionsSnapshot<T>`", "Scoped", "Ha — so'rov boshida"],
           ["`IOptionsMonitor<T>`", "Singleton", "Ha — `CurrentValue` har safar"]],
          widths=[5.0, 3.6, 5.9])

    para(d, "Standart tanlovim — `IOptions<T>`. Konfiguratsiya ishlab "
            "turganda o'zgarishi kerak bo'lsa: so'rov ichida "
            "`IOptionsSnapshot<T>`, background servisda "
            "`IOptionsMonitor<T>`.")

    code(d, """public sealed class RateWorker(IOptionsMonitor<RateOptions> monitor)
{
    public async Task RunAsync(CancellationToken ct)
    {
        while (!ct.IsCancellationRequested)
        {
            var interval = monitor.CurrentValue.PollInterval;   // har safar yangi
            await Task.Delay(interval, ct);
        }
    }
}""")

    note(d, "Diqqat",
         "Singleton servisga `IOptionsSnapshot<T>` ni berib bo'lmaydi — u "
         "scoped, shuning uchun captive dependency xatosi chiqadi.")

    # ───────────────────────────────────────────
    h1(d, "5. Maxfiy qiymatlar")

    para(d, "`appsettings.json` repozitoriyda turadi, ya'ni u **maxfiy joy "
            "emas**. Parol, API kalit va ulanish satrlari u yerda "
            "bo'lmasligi kerak.")

    h2(d, "Development — User Secrets")

    code(d, """dotnet user-secrets init
dotnet user-secrets set "Smtp:Password" "..."
dotnet user-secrets list""")

    para(d, "Fayl loyiha papkasidan tashqarida saqlanadi, shuning uchun "
            "tasodifan commit qilinmaydi. Faqat Development muhitida "
            "yuklanadi.")

    h2(d, "Production")

    bullets(d, [
        "Environment variable — minimal yechim, ko'pchilik holatda yetarli.",
        "Maxsus saqlagich — Azure Key Vault, AWS Secrets Manager, "
        "HashiCorp Vault. Ular rotatsiya, audit va kirish nazoratini beradi.",
        "Konteynerda `ENV` o'rniga fayl orqali mount qilish xavfsizroq, "
        "chunki `docker inspect` muhit o'zgaruvchilarini ko'rsatadi.",
    ])

    # ───────────────────────────────────────────
    h1(d, "6. O'z manbasini qo'shish")

    para(d, "Konfiguratsiyani bazadan yoki boshqa joydan o'qish kerak bo'lsa, "
            "qo'shimcha manba ulanadi:")

    code(d, """builder.Configuration
    .AddJsonFile("features.json", optional: true, reloadOnChange: true)
    .AddEnvironmentVariables(prefix: "SHOP_")
    .AddCommandLine(args);""")

    para(d, "`reloadOnChange: true` fayl o'zgarganda konfiguratsiyani qayta "
            "o'qiydi. Lekin bu faqat `IOptionsSnapshot` yoki "
            "`IOptionsMonitor` bilan ishlaydi — `IOptions<T>` eski "
            "qiymatda qoladi.")

    para(d, "`prefix` bilan o'z o'zgaruvchilarimni ajratib olish qulay: "
            "`SHOP_Smtp__Host` kaliti `Smtp:Host` ga aylanadi.")

    # ───────────────────────────────────────────
    h1(d, "7. Ko'p uchraydigan muammolar")

    bullets(d, [
        "**`appsettings.Development.json` production'ga tushishi.** "
        "Docker image'ga ehtiyotsiz `COPY` qilinsa, u yerda qolib ketadi va "
        "noto'g'ri sozlamalar yuklanadi. `.dockerignore` da uni "
        "chiqarib tashlayman.",
        "**Katta-kichik harf.** Konfiguratsiya kalitlari harf regitriga "
        "sezgir emas, lekin environment variable Linux'da sezgir — shuning "
        "uchun nomni aniq yozish kerak.",
        "**Massivni ustma-ust yuklash.** Ikki manbada massiv bo'lsa, ular "
        "qo'shilmaydi — indeks bo'yicha almashtiriladi. Natijada kutilmagan "
        "aralash ro'yxat chiqishi mumkin.",
        "**`GetValue<T>` jim xatosi.** Kalit bo'lmasa yoki tip mos "
        "kelmasa, standart qiymat (`0`, `null`) qaytadi va bu sezilmaydi. "
        "Options pattern + validatsiya bu muammoni yechadi.",
    ])

    sources(d, [
        ("Configuration in ASP.NET Core",
         "https://learn.microsoft.com/en-us/aspnet/core/fundamentals/configuration/"),
        ("Options pattern in .NET",
         "https://learn.microsoft.com/en-us/dotnet/core/extensions/options"),
        ("Safe storage of app secrets in development",
         "https://learn.microsoft.com/en-us/aspnet/core/security/app-secrets"),
    ])
