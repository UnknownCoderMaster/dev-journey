# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "Integration test"
CATEGORY = "Testing"
TITLE = "Integratsiya Testlari"
SUBTITLE = "Butun ilovani haqiqiy bog'liqliklar bilan sinash"
FILENAME = "Integration test.docx"


def build(d):
    h1(d, "1. Birlik testidan farqi")

    para(d, "Birlik testi bitta klassni izolyatsiyada tekshiradi va bog'liqliklar "
            "mock bilan almashtiriladi. Integratsiya testi esa qismlarning "
            "birgalikda ishlashini tekshiradi — HTTP so'rovdan bazagacha bo'lgan "
            "butun yo'l.")

    table(d, ["Jihat", "Birlik testi", "Integratsiya testi"],
          [["Qamrovi", "Bitta klass", "Bir nechta qatlam"],
           ["Tezligi", "Millisekundlar", "Soniyalar"],
           ["Bog'liqliklar", "Mock", "Haqiqiy yoki konteynerda"],
           ["Nimani topadi", "Mantiq xatosi", "Ulanish, sozlama, SQL xatosi"],
           ["Soni", "Ko'p", "Kamroq, lekin muhimroq"]],
          widths=[3.4, 5.6, 6.5])

    note(d, "Nega men integratsiya testiga alohida e'tibor beraman:",
         "Birlik testlari mening mantiqimni tekshiradi, lekin ular mock bilan "
         "ishlaydi — ya'ni mening **tasavvurimdagi** bog'liqliklar bilan. "
         "Haqiqiy xatolarning ko'pchiligi esa aynan chegaralarda chiqadi: "
         "noto'g'ri ulanish satri, EF Core tarjima qila olmaydigan so'rov, "
         "tushib qolgan middleware. Bularni faqat integratsiya testi topadi.")

    # ───────────────────────────────────────────
    h1(d, "2. WebApplicationFactory")

    para(d, "ASP.NET Core ilovani test jarayonida, haqiqiy tarmoq porti ochmasdan "
            "ishga tushirish imkonini beradi.")

    code(d, """dotnet add package Microsoft.AspNetCore.Mvc.Testing""")

    code(d, """public class BooksApiTests : IClassFixture<WebApplicationFactory<Program>>
{
    private readonly HttpClient _client;

    public BooksApiTests(WebApplicationFactory<Program> factory)
        => _client = factory.CreateClient();

    [Fact]
    public async Task GetById_returns_404_for_unknown_book()
    {
        var response = await _client.GetAsync("/api/books/999999");
        Assert.Equal(HttpStatusCode.NotFound, response.StatusCode);
    }
}""")

    para(d, "`Program` klassi testga ko'rinishi uchun loyihaga quyidagi satr "
            "qo'shiladi:")

    code(d, """// Program.cs oxirida
public partial class Program { }""")

    code(d, """<!-- Test loyihasining csproj faylida -->
<ItemGroup>
  <InternalsVisibleTo Include="MyApp.IntegrationTests" />
</ItemGroup>""")

    # ───────────────────────────────────────────
    h1(d, "3. Xizmatlarni almashtirish")

    para(d, "Testda ba'zi bog'liqliklarni almashtirish kerak bo'ladi — masalan "
            "haqiqiy to'lov tizimiga murojaat qilmaslik uchun:")

    code(d, """public class TestWebAppFactory : WebApplicationFactory<Program>
{
    protected override void ConfigureWebHost(IWebHostBuilder builder)
    {
        builder.UseEnvironment("Testing");

        builder.ConfigureTestServices(services =>
        {
            services.RemoveAll<IPaymentGateway>();
            services.AddSingleton<IPaymentGateway, FakePaymentGateway>();

            services.RemoveAll<IEmailSender>();
            services.AddSingleton<IEmailSender, FakeEmailSender>();
        });
    }
}""")

    note(d, "`ConfigureTestServices` ni ishlatish muhim:",
         "`ConfigureServices` ilovaning o'z ro'yxatdan o'tkazishidan **oldin** "
         "ishlaydi, shuning uchun mening almashtirishim ustiga asl xizmat qayta "
         "yozilib ketadi. `ConfigureTestServices` esa keyin ishlaydi va "
         "almashtirish kuchga kiradi. Bu farqni bilmasdan ancha vaqt "
         "yo'qotgandim.")

    # ───────────────────────────────────────────
    h1(d, "4. Haqiqiy baza bilan — Testcontainers")

    para(d, "Bazani mock qilish yoki `InMemory` provayderini ishlatish ishonchsiz. "
            "To'g'ri yechim — test davomida haqiqiy bazani konteynerda ishga "
            "tushirish.")

    code(d, """dotnet add package Testcontainers.PostgreSql""")

    code(d, """public class DatabaseFixture : IAsyncLifetime
{
    private readonly PostgreSqlContainer _container =
        new PostgreSqlBuilder()
            .WithImage("postgres:17-alpine")
            .WithDatabase("testdb")
            .WithUsername("test")
            .WithPassword("test")
            .Build();

    public string ConnectionString => _container.GetConnectionString();

    public async Task InitializeAsync()
    {
        await _container.StartAsync();

        using var scope = CreateScope();
        var db = scope.ServiceProvider.GetRequiredService<AppDbContext>();
        await db.Database.MigrateAsync();
    }

    public Task DisposeAsync() => _container.DisposeAsync().AsTask();
}""")

    code(d, """builder.ConfigureTestServices(services =>
{
    services.RemoveAll<DbContextOptions<AppDbContext>>();
    services.AddDbContext<AppDbContext>(o =>
        o.UseNpgsql(_fixture.ConnectionString));
});""")

    note(d, "InMemory provayderidan nega voz kechdim:",
         "U tez va qulay, lekin relyatsion baza emas. Unda tashqi kalit "
         "cheklovlari ishlamaydi, tranzaksiyalar taqlid qilinadi va eng muhimi — "
         "LINQ so'rovi xotirada bajariladi. Natijada `PostgreSQL` da xato "
         "beradigan so'rov testda muvaffaqiyatli o'tadi. Microsoft hujjati ham "
         "uni production kodini sinash uchun tavsiya qilmaydi.")

    note(d, "Testcontainers ning narxi ham bor:",
         "Konteyner ko'tarilishi bir necha soniya oladi va mashinada Docker "
         "bo'lishi kerak. Shuning uchun men konteynerni har bir test uchun emas, "
         "butun test sinfi yoki to'plami uchun bir marta ko'taraman.")

    # ───────────────────────────────────────────
    h1(d, "5. Testlarni izolyatsiyalash")

    para(d, "Bir test boshqasiga ta'sir qilmasligi kerak. Umumiy baza bilan bu "
            "muammoga aylanadi — birinchi test qo'shgan yozuv ikkinchisiga "
            "ko'rinadi.")

    h2(d, "5.1 Tranzaksiya bilan orqaga qaytarish")

    code(d, """public async Task InitializeAsync()
{
    _scope = _factory.Services.CreateScope();
    _db = _scope.ServiceProvider.GetRequiredService<AppDbContext>();
    _transaction = await _db.Database.BeginTransactionAsync();
}

public async Task DisposeAsync()
{
    await _transaction.RollbackAsync();
    _scope.Dispose();
}""")

    para(d, "Bu usul tez, lekin HTTP orqali ketadigan testlarda ishlamaydi — "
            "so'rov o'z `DbContext` nusxasini oladi.")

    h2(d, "5.2 Bazani tozalash")

    code(d, """dotnet add package Respawn""")

    code(d, """private Respawner _respawner = null!;

public async Task InitializeAsync()
{
    await using var conn = new NpgsqlConnection(ConnectionString);
    await conn.OpenAsync();

    _respawner = await Respawner.CreateAsync(conn, new RespawnerOptions
    {
        DbAdapter = DbAdapter.Postgres,
        SchemasToInclude = ["public"],
        TablesToIgnore = [new Table("__EFMigrationsHistory")]
    });
}

public async Task ResetAsync()
{
    await using var conn = new NpgsqlConnection(ConnectionString);
    await conn.OpenAsync();
    await _respawner.ResetAsync(conn);
}""")

    para(d, "`Respawn` jadvallarni bog'liqlik tartibida tozalaydi va migratsiya "
            "tarixiga tegmaydi — bu bazani qayta qurishdan ancha tezroq.")

    # ───────────────────────────────────────────
    h1(d, "6. Autentifikatsiyani chetlab o'tish")

    code(d, """public class TestAuthHandler : AuthenticationHandler<AuthenticationSchemeOptions>
{
    public TestAuthHandler(
        IOptionsMonitor<AuthenticationSchemeOptions> options,
        ILoggerFactory logger, UrlEncoder encoder)
        : base(options, logger, encoder) { }

    protected override Task<AuthenticateResult> HandleAuthenticateAsync()
    {
        var claims = new[]
        {
            new Claim(ClaimTypes.NameIdentifier, "7"),
            new Claim(ClaimTypes.Name, "test-user"),
            new Claim(ClaimTypes.Role, "Admin")
        };

        var identity = new ClaimsIdentity(claims, "Test");
        var ticket = new AuthenticationTicket(
            new ClaimsPrincipal(identity), "Test");

        return Task.FromResult(AuthenticateResult.Success(ticket));
    }
}""")

    code(d, """services.AddAuthentication("Test")
    .AddScheme<AuthenticationSchemeOptions, TestAuthHandler>("Test", _ => { });""")

    note(d, "Lekin avtorizatsiyani ham chetlab o'tmaslik kerak:",
         "Men foydalanuvchini soxtalashtiraman, lekin ruxsat tekshiruvi haqiqiy "
         "qoladi. Aks holda eng muhim narsalardan biri — kim nimaga haqli "
         "ekani — testdan tushib qoladi. Aksincha, men ataylab turli rollar "
         "bilan testlar yozaman.")

    # ───────────────────────────────────────────
    h1(d, "7. To'liq misol")

    code(d, """[Collection("Database")]
public class CreateOrderTests : IAsyncLifetime
{
    private readonly TestWebAppFactory _factory;
    private readonly HttpClient _client;

    public CreateOrderTests(DatabaseFixture fixture)
    {
        _factory = new TestWebAppFactory(fixture.ConnectionString);
        _client = _factory.CreateClient();
    }

    [Fact]
    public async Task Creating_order_reduces_stock_and_returns_201()
    {
        // Arrange — ma'lumot tayyorlash
        await SeedBookAsync(id: 1, copies: 10);

        // Act
        var response = await _client.PostAsJsonAsync("/api/orders",
            new { bookId = 1, quantity = 3 });

        // Assert — javob
        Assert.Equal(HttpStatusCode.Created, response.StatusCode);
        Assert.NotNull(response.Headers.Location);

        // Assert — baza holati
        using var scope = _factory.Services.CreateScope();
        var db = scope.ServiceProvider.GetRequiredService<AppDbContext>();

        var book = await db.Books.FindAsync(1);
        Assert.Equal(7, book!.AvailableCopies);
    }

    public Task InitializeAsync() => Task.CompletedTask;
    public Task DisposeAsync() { _factory.Dispose(); return Task.CompletedTask; }
}""")

    # ───────────────────────────────────────────
    h1(d, "8. Amaliy maslahatlar")

    bullets(d, [
        "Integratsiya testlarini alohida loyihaga ajratish — ular sekinroq va "
        "har commit da ishlatilmasligi mumkin.",
        "Eng muhim yo'llarni qamrab olish; hamma narsani emas.",
        "Test ma'lumotini har bir testda o'zi tayyorlashi — umumiy seed ga "
        "tayanmaslik.",
        "Javob kodini ham, baza holatini ham tekshirish.",
        "Konteynerni test to'plami uchun bir marta ko'tarish.",
        "CI da Docker mavjudligini ta'minlash.",
    ])

    # ───────────────────────────────────────────
    h1(d, "9. Xulosa")

    bullets(d, [
        "Integratsiya testi qatlamlarning birgalikda ishlashini tekshiradi.",
        "`WebApplicationFactory` ilovani port ochmasdan test jarayonida ishga "
        "tushiradi.",
        "Xizmatlarni almashtirish uchun `ConfigureTestServices` ishlatiladi — "
        "`ConfigureServices` emas.",
        "`InMemory` provayderi relyatsion baza emas; Testcontainers haqiqiy "
        "bazani beradi.",
        "Testlar izolyatsiyasi uchun tranzaksiyani qaytarish yoki `Respawn` "
        "bilan tozalash.",
        "Autentifikatsiyani soxtalashtirish mumkin, lekin avtorizatsiyani "
        "haqiqiy qoldirish kerak.",
        "Javob kodi bilan birga baza holatini ham tekshirish lozim.",
    ])

    sources(d, [
        ("Integration tests in ASP.NET Core",
         "https://learn.microsoft.com/en-us/aspnet/core/test/integration-tests"),
        ("Testing EF Core applications",
         "https://learn.microsoft.com/en-us/ef/core/testing/"),
        ("Testcontainers for .NET",
         "https://dotnet.testcontainers.org/"),
        ("Respawn — GitHub",
         "https://github.com/jbogard/Respawn"),
    ])
