# Integration Testing — ASP.NET Core — Middle D

## 1. Nima? (Ta'rif)

**Integration Test** — bir nechta komponentni (Controller, Handler,
DbContext, middleware pipeline) **BIRGA**, haqiqiy (yoki
haqiqiyga yaqin) muhitda test qilish. Unit test'dan farqli —
bu yerda **mock kamroq**, haqiqiy HTTP so'rov, haqiqiy (yoki
konteynerlashtirilgan) DB ishlatiladi.

## 2. Nima uchun kerak?

Unit test — har komponentni **alohida** to'g'ri ishlashini
tekshiradi, lekin ular **BIRGA** to'g'ri ishlashini KAFOLATLAMAYDI
(masalan, DI ro'yxatdan noto'g'ri o'tkazilgan, middleware tartibi
noto'g'ri). Integration Test — **butun so'rov oqimini** (HTTP
so'rovdan DB'gacha) tekshiradi.

## 3. Ichida nima sodir bo'ladi? (Mexanizm)

### 3.1 `WebApplicationFactory<T>` — test server yaratish

```bash
dotnet add package Microsoft.AspNetCore.Mvc.Testing
```

```csharp
public class EmployeeApiTests : IClassFixture<WebApplicationFactory<Program>>
{
    private readonly HttpClient _client;

    public EmployeeApiTests(WebApplicationFactory<Program> factory)
    {
        _client = factory.CreateClient(); // TO'LIQ ilova, XOTIRADA (in-memory server) ishga tushadi
    }

    [Fact]
    public async Task GetEmployees_ReturnsOk()
    {
        var response = await _client.GetAsync("/api/employees");
        response.EnsureSuccessStatusCode();
    }
}
```

`WebApplicationFactory<T>` — **butun ASP.NET Core pipeline**ni
(middleware, DI, routing) **xotirada** ishga tushiradi — haqiqiy
port/server kerak emas, lekin **HAMMA** narsa (Middleware, Filter,
Authentication) **haqiqiy** ishlaydi.

### 3.2 Test DB — In-Memory vs Testcontainers

```
EF Core InMemory provider:
  ✅ TEZ, o'rnatish OSON
  ❌ HAQIQIY PostgreSQL xatti-harakatini TO'LIQ TAQLID QILMAYDI
     (masalan, real SQL constraint, transaction xatti-harakati,
     JSON/Array operatorlar — ISHLAMAYDI yoki BOSHQACHA ishlaydi)

Testcontainers.PostgreSql:
  ✅ HAQIQIY PostgreSQL (Docker konteynerda), TO'LIQ ISHONCHLI
  ❌ SEKINROQ (konteyner ishga tushishi vaqt oladi)
```

```bash
dotnet add package Testcontainers.PostgreSql --version 3.7.0
```

```csharp
public class DatabaseFixture : IAsyncLifetime
{
    private readonly PostgreSqlContainer _container = new PostgreSqlBuilder()
        .WithImage("postgres:16")
        .WithDatabase("testdb")
        .Build();

    public string ConnectionString => _container.GetConnectionString();

    public async Task InitializeAsync() => await _container.StartAsync(); // Docker konteyner ISHGA TUSHADI
    public async Task DisposeAsync() => await _container.DisposeAsync();  // Testdan KEYIN O'CHIRILADI
}
```

**Tavsiya:** Integration Test'lar uchun — **Testcontainers**
(haqiqiy PostgreSQL) — chunki EF Core InMemory — production DB
xatti-harakatini **to'liq** taqlid qila olmaydi (masalan, PostgreSQL
`CHECK` constraint, `ON DELETE CASCADE` — InMemory'da BOSHQACHA
yoki UMUMAN ishlamaydi).

### 3.3 DB seed — test ma'lumotlari

```csharp
public class CustomWebApplicationFactory : WebApplicationFactory<Program>
{
    protected override void ConfigureWebHost(IWebHostBuilder builder)
    {
        builder.ConfigureServices(services =>
        {
            var descriptor = services.SingleOrDefault(
                d => d.ServiceType == typeof(DbContextOptions<AppDbContext>));
            if (descriptor != null) services.Remove(descriptor);

            services.AddDbContext<AppDbContext>(options =>
                options.UseNpgsql(_testConnectionString));

            using var scope = services.BuildServiceProvider().CreateScope();
            var context = scope.ServiceProvider.GetRequiredService<AppDbContext>();
            context.Database.Migrate();
            context.Employees.Add(new Employee { FullName = "Test Employee" });
            context.SaveChanges();
        });
    }
}
```

### 3.4 Authentication bypass — test'da JWT

```csharp
public class TestAuthHandler : AuthenticationHandler<AuthenticationSchemeOptions>
{
    protected override Task<AuthenticateResult> HandleAuthenticateAsync()
    {
        var claims = new[] { new Claim(ClaimTypes.Name, "TestUser"), new Claim(ClaimTypes.Role, "Admin") };
        var identity = new ClaimsIdentity(claims, "Test");
        var principal = new ClaimsPrincipal(identity);
        var ticket = new AuthenticationTicket(principal, "Test");
        return Task.FromResult(AuthenticateResult.Success(ticket));
    }
}

// Test setup — HAQIQIY JWT o'rniga soxta scheme
builder.ConfigureTestServices(services =>
{
    services.AddAuthentication("Test")
        .AddScheme<AuthenticationSchemeOptions, TestAuthHandler>("Test", options => { });
});
```

Bu — har testda **haqiqiy JWT token generatsiya qilish** o'rniga,
"men allaqachon autentifikatsiyadan o'tganman" deb **soxta**
qiluvchi handler — Integration Test'ni **soddalashtiradi**.

### 3.5 `CustomWebApplicationFactory` — servislarni override qilish

```csharp
public class CustomWebApplicationFactory : WebApplicationFactory<Program>
{
    protected override void ConfigureWebHost(IWebHostBuilder builder)
    {
        builder.ConfigureTestServices(services =>
        {
            // Tashqi (masalan email) servisni MOCK bilan ALMASHTIRISH
            services.RemoveAll<IEmailService>();
            services.AddSingleton<IEmailService>(Substitute.For<IEmailService>());
        });
    }
}
```

### 3.6 Transaction per test — rollback

```csharp
public class EmployeeIntegrationTests : IAsyncLifetime
{
    private IDbContextTransaction _transaction = null!;

    public async Task InitializeAsync()
        => _transaction = await _context.Database.BeginTransactionAsync();

    public async Task DisposeAsync()
        => await _transaction.RollbackAsync(); // HAR TEST tugagach — BARCHA o'zgarish BEKOR qilinadi!
}
```

Bu pattern — har test **BOSHIDA** transaction ochadi, **OXIRIDA**
ROLLBACK qiladi — shu tarzda testlar **DB holatini "iflos"**
qoldirmaydi (keyingi test HAR DOIM toza holatdan boshlanadi).

### 3.7 Parallel Integration Tests — muammo va yechim

```
❌ MUAMMO: Bir nechta test PARALLEL ishga tushsa, BIR XIL DB'ga
   YOZSA — bir-biriga XALAQIT berishi mumkin (masalan, Test A
   yaratgan yozuvni Test B "kutilmagan" deb topadi)

✅ Yechimlar:
   1. Har test uchun ALOHIDA (Testcontainers orqali) DB instance
   2. Transaction per test (yuqorida ko'rsatilgan)
   3. xUnit'da [Collection] atributi orqali PARALLEL bo'lmasligini
      belgilash:

[Collection("Sequential")]
public class EmployeeIntegrationTests { }
```

## 4. Kod — to'liq misol

```csharp
public class EmployeesControllerTests : IClassFixture<CustomWebApplicationFactory>
{
    private readonly HttpClient _client;

    public EmployeesControllerTests(CustomWebApplicationFactory factory)
        => _client = factory.CreateClient();

    [Fact]
    public async Task CreateEmployee_ReturnsCreated()
    {
        var dto = new CreateEmployeeDto { FullName = "Yangi Xodim", Age = 25 };
        var response = await _client.PostAsJsonAsync("/api/employees", dto);

        response.StatusCode.Should().Be(HttpStatusCode.Created);
        var result = await response.Content.ReadFromJsonAsync<EmployeeDto>();
        result!.FullName.Should().Be("Yangi Xodim");
    }
}
```

## 5. Qachon ishlatish kerak?

| Vaziyat | Yechim |
|---|---|
| Butun HTTP pipeline'ni tekshirish (routing, middleware, auth) | `WebApplicationFactory` |
| Haqiqiy PostgreSQL xatti-harakati kerak | Testcontainers |
| Tashqi servis (email, SMS) chaqirilmasin | Mock bilan override |
| Har test toza DB holatidan boshlanishi kerak | Transaction rollback |

## 6. Muhim nuqtalar

- Integration Test — Unit Test'dan **SEKINROQ**, shuning uchun
  odatda **kamroq sonda**, faqat **kritik oqimlar** uchun yoziladi.
- Testcontainers — CI/CD pipeline'da Docker mavjudligini talab
  qiladi.
- Parallel testlar — DB holatini **to'g'ri izolyatsiya qilmasa**,
  "flaky" (ba'zan o'tadigan, ba'zan yo'q) bo'lib qolishi mumkin.

## 7. Imtihon savollari

1. Unit Test va Integration Test orasidagi asosiy farq nima?
2. `WebApplicationFactory<T>` nima vazifani bajaradi?
3. EF Core InMemory provider va Testcontainers orasidagi farqni
   ishonchlilik nuqtai nazaridan tushuntiring.
4. Test'da JWT autentifikatsiyasini qanday "bypass" qilish mumkin?
5. Transaction per test pattern qanday muammoni hal qiladi?
6. Parallel integration testlar qanday muammoga olib kelishi mumkin
   va uni qanday oldini olish mumkin?
