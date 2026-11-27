# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "DI Container, Service Lifetimes(Scope,Transient,Singleton)"
CATEGORY = ".NET / C#"
TITLE = "DI Container va Servis Hayot Davrlari"
SUBTITLE = "Transient, Scoped va Singleton orasidagi farq"
FILENAME = "DI Container, Service Lifetimes.docx"


def build(d):
    h1(d, "1. Dependency Injection nima muammoni hal qiladi")

    para(d, "Klass o'ziga kerakli obyektni o'zi yaratganda, u shu konkret turga "
            "bog'lanib qoladi:")

    code(d, """public class OrderService
{
    private readonly SqlOrderRepository _repository = new SqlOrderRepository();
    private readonly SmtpEmailSender _sender = new SmtpEmailSender();
}""")

    para(d, "Bu kodda uchta muammo bor. Birinchisi — `OrderService` ni test "
            "qilganda haqiqiy bazaga va haqiqiy SMTP serverga murojaat "
            "bo'ladi. Ikkinchisi — repozitoriy amalga oshirilishini "
            "o'zgartirish uchun `OrderService` kodini tahrirlash kerak. "
            "Uchinchisi — bog'liqlik konstruktorda ko'rinmaydi, shuning uchun "
            "klassning haqiqatan nimaga tayanayotganini bilish uchun butun "
            "kodni o'qish kerak bo'ladi.")

    para(d, "Dependency Injection bog'liqlikni tashqaridan beradi. Klass endi "
            "nimaga tayanayotganini e'lon qiladi, lekin uni kim yaratishini "
            "bilmaydi:")

    code(d, """public class OrderService(IOrderRepository repository, IEmailSender sender)
{
    public async Task PlaceAsync(Order order, CancellationToken ct)
    {
        await repository.AddAsync(order, ct);
        await sender.SendAsync(order.CustomerEmail, "Buyurtma qabul qilindi", ct);
    }
}""")

    # ───────────────────────────────────────────
    h1(d, "2. DI Container vazifasi")

    para(d, "Container — bu bog'liqliklar reyestri. Unda qaysi interfeys uchun "
            "qaysi amalga oshirish ishlatilishi yozib qo'yiladi, keyin "
            "container obyektlarni o'zi yaratadi va konstruktorlarga uzatadi.")

    code(d, """builder.Services.AddScoped<IOrderRepository, SqlOrderRepository>();
builder.Services.AddScoped<IEmailSender, SmtpEmailSender>();
builder.Services.AddScoped<OrderService>();""")

    para(d, "`OrderService` so'ralganda container avtomatik ravishda "
            "`SqlOrderRepository` va `SmtpEmailSender` ni yaratib, "
            "konstruktorga beradi. Bu jarayon rekursiv: agar "
            "`SqlOrderRepository` ham o'z bog'liqligiga ega bo'lsa, u ham "
            "shu tarzda to'ldiriladi.")

    note(d, "Eslatma",
         "ASP.NET Core ichida DI container allaqachon bor, qo'shimcha "
         "kutubxona o'rnatish kerak emas. Autofac yoki boshqa container "
         "faqat standart container qo'llab-quvvatlamaydigan imkoniyat "
         "kerak bo'lganda qo'shiladi.")

    # ───────────────────────────────────────────
    h1(d, "3. Uchta hayot davri")

    table(d, ["Hayot davri", "Qancha obyekt yaratiladi", "Qachon ishlatiladi"],
          [["`Transient`", "Har bir so'rovda yangi",
            "Holat saqlamaydigan, yengil servislar"],
           ["`Scoped`", "Bitta HTTP so'rov uchun bitta",
            "`DbContext`, so'rov kontekstiga bog'liq servislar"],
           ["`Singleton`", "Ilova umri uchun bitta",
            "Kesh, konfiguratsiya, qimmat va o'zgarmas obyektlar"]],
          widths=[3.4, 4.6, 6.5])

    para(d, "ASP.NET Core da \"scope\" odatda bitta HTTP so'rovga teng. So'rov "
            "boshlanganda yangi scope yaratiladi, so'rov tugaganda u "
            "`Dispose` qilinadi.")

    code(d, """builder.Services.AddTransient<IGuidGenerator, GuidGenerator>();
builder.Services.AddScoped<ICurrentUser, HttpCurrentUser>();
builder.Services.AddSingleton<IRateCache, RateCache>();""")

    # ───────────────────────────────────────────
    h1(d, "4. Farqni amalda ko'rish")

    para(d, "Hayot davrlarining farqini tushunish uchun o'zim shunday sinov "
            "qildim — har bir servis o'zining `Guid` ini saqlaydi va biz uni "
            "bitta so'rov ichida ikki marta o'qiymiz:")

    code(d, """public class IdHolder
{
    public Guid Id { get; } = Guid.NewGuid();
}

app.MapGet("/ids", (IdHolder a, IdHolder b) => new { First = a.Id, Second = b.Id });""")

    bullets(d, [
        "`Transient` bo'lsa — `First` va `Second` har xil, chunki ikki "
        "alohida obyekt yaratildi.",
        "`Scoped` bo'lsa — ikkisi bir xil, lekin sahifani qayta yuklaganda "
        "yangi qiymat chiqadi.",
        "`Singleton` bo'lsa — ikkisi bir xil va ilova qayta ishga "
        "tushirilmaguncha o'zgarmaydi.",
    ])

    # ───────────────────────────────────────────
    h1(d, "5. Captive dependency — eng ko'p uchraydigan xato")

    para(d, "Agar singleton servis scoped servisga bog'lansa, scoped obyekt "
            "singleton ichida \"qamalib\" qoladi va ilova umri davomida "
            "yashaydi. Bu `DbContext` bilan juda xavfli: bitta context hamma "
            "so'rovga xizmat qiladi, change tracker shishadi, parallel "
            "so'rovlarda xato chiqadi.")

    code(d, """// XATO: singleton ichida scoped DbContext
public class CacheWarmer(AppDbContext db)   // AddSingleton<CacheWarmer>()
{
    public async Task WarmAsync() => await db.Products.ToListAsync();
}""")

    para(d, "To'g'ri yo'l — scope ni o'zim yaratish:")

    code(d, """public class CacheWarmer(IServiceScopeFactory scopeFactory)
{
    public async Task WarmAsync(CancellationToken ct)
    {
        using var scope = scopeFactory.CreateScope();
        var db = scope.ServiceProvider.GetRequiredService<AppDbContext>();
        await db.Products.ToListAsync(ct);
    }
}""")

    note(d, "Muhim",
         "Bu xatoni ishlab chiqish muhitida ilova o'zi aytib beradi — "
         "`BuildServiceProvider` validatsiyasi `Cannot consume scoped service "
         "from singleton` xatosini beradi. Shuning uchun uni e'tiborsiz "
         "qoldirmaslik kerak.")

    para(d, "Teskari yo'nalish xavfsiz: scoped servis singleton'ga bog'lanishi "
            "mumkin, chunki singleton uzoqroq yashaydi.")

    # ───────────────────────────────────────────
    h1(d, "6. Qaysi hayot davrini tanlayman")

    para(d, "O'zim uchun chiqargan qoida ketma-ketligi shunday.")

    bullets(d, [
        "Servis holat saqlasa va bu holat bitta so'rovga tegishli bo'lsa — "
        "`Scoped`. `DbContext`, joriy foydalanuvchi, tranzaksiya konteksti.",
        "Servis umuman holat saqlamasa — `Transient` yoki `Scoped`. Ikkisi ham "
        "to'g'ri; `Scoped` bitta so'rov ichida kamroq obyekt yaratadi.",
        "Servis qimmat yaratiladigan va thread-safe bo'lsa — `Singleton`. "
        "Kesh, `HttpClient` fabrikasi, sozlamalar.",
    ], numbered=True)

    para(d, "Shubha bo'lsa `Scoped` ni tanlayman: u eng xavfsiz standart, "
            "chunki so'rov chegarasida tozalanadi va captive dependency "
            "muammosini keltirib chiqarmaydi.")

    note(d, "Diqqat",
         "`Singleton` servis bir vaqtda ko'p thread'dan chaqiriladi. "
         "Shuning uchun uning ichidagi har qanday o'zgaruvchan maydon "
         "thread-safe bo'lishi kerak — oddiy `List<T>` yoki "
         "`Dictionary<K,V>` bu yerda yetarli emas.")

    # ───────────────────────────────────────────
    h1(d, "7. Ro'yxatga olishning qo'shimcha shakllari")

    code(d, """// Fabrika orqali — yaratilish mantiqi murakkab bo'lsa
builder.Services.AddScoped<IReportBuilder>(sp =>
{
    var options = sp.GetRequiredService<IOptions<ReportOptions>>().Value;
    return new ReportBuilder(options.TemplatePath);
});

// Bir interfeysga bir nechta amalga oshirish
builder.Services.AddScoped<IValidator, EmailValidator>();
builder.Services.AddScoped<IValidator, PhoneValidator>();
// konstruktorda: IEnumerable<IValidator> validators

// Faqat ro'yxatda bo'lmasa qo'shish — kutubxona yozganda qulay
builder.Services.TryAddScoped<IClock, SystemClock>();""")

    para(d, "Bir xil interfeys ikki marta ro'yxatga olinsa va bitta nusxa "
            "so'ralsa, **oxirgi** ro'yxatga olingani qaytadi. Testda haqiqiy "
            "servisni almashtirish uchun shu xossadan foydalanish mumkin, "
            "lekin `RemoveAll` bilan aniq olib tashlash tushunarliroq.")

    # ───────────────────────────────────────────
    h1(d, "8. Service Locator — qochish kerak bo'lgan naqsh")

    code(d, """// Shunday yozish mumkin, lekin yaxshi emas
public class OrderService(IServiceProvider provider)
{
    public async Task PlaceAsync(Order order)
    {
        var repo = provider.GetRequiredService<IOrderRepository>();
        await repo.AddAsync(order);
    }
}""")

    para(d, "Bu kod ishlaydi, lekin DI ning asosiy foydasini yo'qotadi: "
            "klassning bog'liqliklari konstruktorda ko'rinmaydi. Natijada "
            "test yozish uchun butun container'ni sozlash kerak bo'ladi va "
            "bog'liqlik yo'qligi faqat ish vaqtida aniqlanadi.")

    para(d, "`IServiceProvider` ni to'g'ridan-to'g'ri olishni faqat haqiqatan "
            "dinamik holatda — masalan turga qarab handler tanlashda — "
            "ishlataman, va unda ham buni alohida fabrika klassiga yashiraman.")

    # ───────────────────────────────────────────
    h1(d, "9. Amaliyotdan: bitta joyda yig'ilgan ro'yxatga olish")

    para(d, "Ish joyimdagi MAD ERP tizimida yigirmaga yaqin servis bor va ularning "
            "hammasi bir xil asosiy xizmatlarni ishlatadi. Shuning uchun ro'yxatga "
            "olish umumiy kutubxonadagi bitta metodda yig'ilgan:")

    code(d, """public static void ConfigureServiceInfrastructure(this IServiceCollection services)
{
    // Culture
    services.AddScoped<ICultureHelper, CultureHelper>();

    // Time
    services.AddSingleton(TimeProvider.System);

    // Database
    AppContext.SetSwitch("Npgsql.EnableLegacyTimestampBehavior", true);
    services.AddDbContext<ApplicationDbContext>();
    services.AddScoped<IApplicationDbContext>(provider =>
        provider.GetRequiredService<ApplicationDbContext>());

    // User
    services.AddHttpContextAccessor();

    // configure config
    services.AddSingleton(ServiceAppSettings.ServiceInstance.Culture);
    services.AddSingleton(ServiceAppSettings.ServiceInstance.Database);

    // SequenceNextId
    services.AddScoped<ISequenceNextIdService, SequenceNextIdService>();

    // Localization
    services.AddLocalizationService();
}""", caption="Erp.Core.Service.Infrastructure/DependencyInjection.cs")

    para(d, "Bu kichik metodda 3- va 6-bo'limlarda aytilgan hamma qarorni ko'rish "
            "mumkin, shuning uchun uni qatorlab ko'rib chiqaman.")

    h2(d, "9.1 Nega DbContext scoped")

    para(d, "`AddDbContext` standart holda scoped ro'yxatga oladi — ya'ni har bir HTTP "
            "so'rovga bitta kontekst. 6-bo'limdagi mezonlar bo'yicha bu to'g'ri: "
            "kontekst holat saqlaydi (o'zgarishlarni kuzatadi) va thread-safe emas.")

    para(d, "Agar u singleton bo'lsa, ikki so'rov bir vaqtda bir xil obyektlarni "
            "kuzatib, bir-birining o'zgarishini saqlab qo'yardi. Agar transient bo'lsa, "
            "bitta so'rov ichida ikki xizmat ikki xil kontekst olib, tranzaksiya "
            "chegarasi buzilardi.")

    h2(d, "9.2 Interfeys va amalga oshirish bir xil nusxa bo'lishi")

    para(d, "Mana bu qatorga alohida e'tibor berdim:")

    code(d, """services.AddDbContext<ApplicationDbContext>();
services.AddScoped<IApplicationDbContext>(provider =>
    provider.GetRequiredService<ApplicationDbContext>());""")

    para(d, "Ikkinchi qator bo'lmasa, ishlovchilar `IApplicationDbContext` ni "
            "inject qila olmasdi. Lekin uni `AddScoped<IApplicationDbContext, "
            "ApplicationDbContext>()` deb yozish **xato** bo'lardi: unda konteyner "
            "ikkita alohida nusxa yaratardi — biri `ApplicationDbContext` so'ralganda, "
            "ikkinchisi interfeys so'ralganda.")

    para(d, "Factory lambda esa mavjud nusxani qaytaradi. 7-bo'limda ro'yxatga "
            "olishning qo'shimcha shakllari haqida gapirgandim; bu aynan o'sha "
            "shaklning eng foydali ishlatilishi — bitta obyektni ikki nom ostida "
            "ko'rsatish.")

    note(d, "Bu xatoni qilish juda oson:",
         "Ikki nusxa paydo bo'lsa, xato darhol ko'rinmaydi. Kod ishlaydi, so'rovlar "
         "bajariladi. Faqat bir xizmat `ApplicationDbContext` ni, boshqasi "
         "`IApplicationDbContext` ni olgan joyda ularning o'zgarishlari bir-birini "
         "ko'rmaydi — va bitta `SaveChanges` ikkinchisining ishini saqlamaydi. "
         "Buni topish uchun ancha vaqt ketardi, chunki bu DI xatosi bo'lib "
         "ko'rinmaydi, baza xatosi bo'lib ko'rinadi.")

    h2(d, "9.3 Singleton tanlanganlar")

    bullets(d, [
        "`TimeProvider.System` — holatsiz va thread-safe. Vaqtni `DateTime.Now` "
        "orqali o'qish o'rniga shu xizmatni inject qilish testda vaqtni almashtirish "
        "imkonini beradi. 1-bo'limdagi \"bog'liqlikni tashqaridan berish\" "
        "tamoyilining juda toza misoli.",
        "`Culture` va `Database` sozlamalari — bir marta o'qilgan, o'zgarmas "
        "obyektlar. 6-bo'limdagi mezonga to'liq mos.",
    ])

    h2(d, "9.4 Captive dependency bu tizimda qanday chetlab o'tilgan")

    para(d, "5-bo'limda captive dependency eng ko'p uchraydigan xato ekani aytilgan. "
            "Shu tizimda uning aniq misolini ko'rdim — SDK larning HTTP handler lari. "
            "Ular `HttpClient` bilan birga keshlanadi, ya'ni umri so'rovdan uzun, "
            "lekin ularga joriy so'rovning foydalanuvchisi kerak.")

    para(d, "Yechim — scoped xizmatni konstruktorda **olmaslik**, o'rniga "
            "`IServiceProvider` ni olib, kerak bo'lganda so'rash:")

    code(d, """public class LanguageHeaderHandler : DelegatingHandler
{
    private readonly IServiceProvider _serviceProvider;   // scoped emas

    protected override async Task<HttpResponseMessage> SendAsync(...)
    {
        // Har bir so'rovda yangisini olamiz
        var httpContext = _serviceProvider.GetService<IHttpContextAccessor>()?.HttpContext;
        // ...
    }
}""")

    para(d, "8-bo'limda Service Locator naqshidan qochish kerakligini yozgandim, va "
            "bu kod aynan shunga o'xshaydi. Lekin bu yerda u oqlanadi: handler ning "
            "umri bilan so'rovning umri mos kelmaydi, shuning uchun konstruktor "
            "injection texnik jihatdan mumkin emas. Ya'ni Service Locator — har doim "
            "xato emas, balki umr davrlari to'g'ri kelmaganda qoladigan oxirgi yo'l.")

    sources(d, [
        ("Dependency injection in ASP.NET Core",
         "https://learn.microsoft.com/en-us/aspnet/core/fundamentals/dependency-injection"),
        ("Dependency injection guidelines",
         "https://learn.microsoft.com/en-us/dotnet/core/extensions/dependency-injection-guidelines"),
        ("Service lifetimes",
         "https://learn.microsoft.com/en-us/dotnet/core/extensions/dependency-injection#service-lifetimes"),
    ])
