# HttpClient, IHttpClientFactory, Polly, Refit — Middle D

## 1. Nima? (Ta'rif)

**HttpClient** — .NET'da tashqi HTTP so'rovlar yuborish uchun ishlatiladigan
klass. **IHttpClientFactory** — `HttpClient` obyektlarini to'g'ri
boshqarish (yaratish, qayta ishlatish, lifecycle) uchun mo'ljallangan
factory abstraksiyasi. **Refit** — HTTP so'rovlarni **deklarativ
interfeys** orqali yozish imkonini beruvchi kutubxona.

## 2. Nima uchun kerak?

`HttpClient`ni **noto'g'ri** ishlatish (masalan, har so'rovda `new
HttpClient()`) — **Socket Exhaustion** degan jiddiy production
muammoga olib keladi. `IHttpClientFactory` — bu muammoni **tizimli**
hal qiladi.

## 3. Ichida nima sodir bo'ladi? (Mexanizm)

### 3.1 HttpClient vs WebClient

`WebClient` — **eskirgan** (obsolete, .NET 5+ da belgilangan), faqat
sinxron/oddiy API. `HttpClient` — zamonaviy, async-first, kengaytiriladigan
(`DelegatingHandler` orqali middleware qo'shish mumkin). Yangi loyihalarda
faqat `HttpClient` (yoki undan yuqori — `IHttpClientFactory`/Refit)
ishlatilishi kerak.

### 3.2 Socket Exhaustion muammosi

```csharp
// ❌ XAVFLI PATTERN
public async Task<string> GetData()
{
    using var client = new HttpClient(); // Har chaqiriqda YANGI!
    return await client.GetStringAsync("https://api.example.com");
}
```

```
Muammo: HttpClient — IDisposable, lekin uning ICHIDAGI TCP socket
(HttpClientHandler orqali) `using`dan keyin DARHOL yopilmaydi —
u TIME_WAIT holatida ~240 soniya "band" bo'lib qoladi (TCP standarti).

Yuqori trafikda (masalan soniyasiga 100 so'rov):
  100 so'rov/soniya × 240 soniya = 24,000 ta "band" socket
  → OS'ning ochiq socket LIMITI tugaydi
  → SocketException: "Only one usage of each socket address..."
```

`HttpClient`ni **Singleton** qilib qayta ishlatish — bu muammoni hal
qiladi (bitta socket pool qayta ishlatiladi), lekin bu holda **DNS
o'zgarishi** kuzatilmay qoladi (agar server IP'si o'zgarsa,
Singleton `HttpClient` ESKI IP'ga ulanaverishi mumkin) — shu sababli
`IHttpClientFactory` yaratildi.

### 3.3 IHttpClientFactory — qanday ishlaydi

```
IHttpClientFactory ICHKARIDA:
  - HttpMessageHandler'larni POOL sifatida boshqaradi
  - Har HttpClient CreateClient() chaqiruvida — YANGI HttpClient
    obyekti (yengil "wrapper"), lekin ICHKI HttpMessageHandler
    QAYTA ISHLATILADI (pool'dan)
  - Handler'lar DAVRIY ravishda (default 2 daqiqa) ESKIRADI va
    YANGILANADI — bu DNS o'zgarishini KUZATISH imkonini beradi
```

```csharp
// Program.cs
builder.Services.AddHttpClient(); // Asosiy factory

// Named client
builder.Services.AddHttpClient("KeycloakClient", client =>
{
    client.BaseAddress = new Uri("https://keycloak.example.com");
    client.Timeout = TimeSpan.FromSeconds(10);
});

// Typed client — eng tavsiya etiladigan yondashuv
builder.Services.AddHttpClient<IEmployeeApiClient, EmployeeApiClient>(client =>
{
    client.BaseAddress = new Uri("https://api.example.com");
});
```

```csharp
public class EmployeeApiClient : IEmployeeApiClient
{
    private readonly HttpClient _httpClient;
    public EmployeeApiClient(HttpClient httpClient) => _httpClient = httpClient;

    public async Task<Employee?> GetByIdAsync(int id)
        => await _httpClient.GetFromJsonAsync<Employee>($"employees/{id}");
}
```

### 3.4 DelegatingHandler — Middleware (logging, retry)

```csharp
public class LoggingHandler : DelegatingHandler
{
    private readonly ILogger<LoggingHandler> _logger;
    public LoggingHandler(ILogger<LoggingHandler> logger) => _logger = logger;

    protected override async Task<HttpResponseMessage> SendAsync(
        HttpRequestMessage request, CancellationToken ct)
    {
        _logger.LogInformation("So'rov: {Method} {Url}", request.Method, request.RequestUri);
        var response = await base.SendAsync(request, ct); // Zanjirda KEYINGI handler'ga o'tadi
        _logger.LogInformation("Javob: {StatusCode}", response.StatusCode);
        return response;
    }
}

builder.Services.AddTransient<LoggingHandler>();
builder.Services.AddHttpClient<IEmployeeApiClient, EmployeeApiClient>()
    .AddHttpMessageHandler<LoggingHandler>();
```

```
So'rov oqimi (Handler zanjiri):
Client kodi → LoggingHandler → RetryHandler → ... → HttpClientHandler (haqiqiy tarmoq)
```

### 3.5 Polly — Retry va Circuit Breaker

```bash
dotnet add package Microsoft.Extensions.Http.Polly
```

```csharp
builder.Services.AddHttpClient<IEmployeeApiClient, EmployeeApiClient>()
    .AddPolicyHandler(Policy<HttpResponseMessage>
        .Handle<HttpRequestException>()
        .OrResult(r => (int)r.StatusCode >= 500)
        .WaitAndRetryAsync(3, retryAttempt =>
            TimeSpan.FromSeconds(Math.Pow(2, retryAttempt)))) // Exponential backoff
    .AddPolicyHandler(Policy<HttpResponseMessage>
        .Handle<HttpRequestException>()
        .CircuitBreakerAsync(
            handledEventsAllowedBeforeBreaking: 5,
            durationOfBreak: TimeSpan.FromSeconds(30)));
```

```
Circuit Breaker holatlari:

Closed (yopiq)  → so'rovlar ODATDAGIDEK yuboriladi
     │  5 marta ketma-ket xato
     ▼
Open (ochiq)    → 30 soniya davomida BARCHA so'rovlar DARHOL rad etiladi
                  (tashqi servisga QO'SHIMCHA yuklama BERILMAYDI)
     │  30 soniya o'tgach
     ▼
Half-Open       → BITTA sinov so'rov yuboriladi
     │
     ├─ Muvaffaqiyatli → Closed'ga qaytadi
     └─ Xato          → Open'ga qaytadi (yana 30 soniya)
```

### 3.6 Proxy va NetworkCredential

```csharp
var handler = new HttpClientHandler
{
    Proxy = new WebProxy("http://proxy.company.com:8080")
    {
        Credentials = new NetworkCredential("username", "password")
    },
    UseProxy = true
};
var client = new HttpClient(handler);
```

### 3.7 Auth header qo'shish

```csharp
client.DefaultRequestHeaders.Authorization =
    new AuthenticationHeaderValue("Bearer", accessToken);

// Basic Auth
var byteArray = Encoding.ASCII.GetBytes($"{username}:{password}");
client.DefaultRequestHeaders.Authorization =
    new AuthenticationHeaderValue("Basic", Convert.ToBase64String(byteArray));
```

### 3.8 Refit — deklarativ HTTP client

```bash
dotnet add package Refit.HttpClientFactory
```

```csharp
public interface IEmployeeApi
{
    [Get("/employees/{id}")]
    Task<Employee> GetByIdAsync(int id);

    [Post("/employees")]
    Task<Employee> CreateAsync([Body] CreateEmployeeDto dto);
}

// Program.cs — IHttpClientFactory bilan BIRGA ishlaydi
builder.Services.AddRefitClient<IEmployeeApi>()
    .ConfigureHttpClient(c => c.BaseAddress = new Uri("https://api.example.com"))
    .AddPolicyHandler(retryPolicy); // Polly ham qo'shilishi mumkin

// Ishlatish — HTTP so'rov yozish SHART emas, interfeys chaqiriladi
public class EmployeeService
{
    private readonly IEmployeeApi _api;
    public EmployeeService(IEmployeeApi api) => _api = api;
    public Task<Employee> GetEmployee(int id) => _api.GetByIdAsync(id);
}
```

Refit — HTTP so'rov yaratish, JSON serialize/deserialize qilish
kodini **yashiradi** — interfeys metodini chaqirish, xuddi oddiy
C# metodini chaqirishdek ko'rinadi.

## 4. Kod — timeout sozlash

```csharp
builder.Services.AddHttpClient<IEmployeeApiClient, EmployeeApiClient>(client =>
{
    client.Timeout = TimeSpan.FromSeconds(30); // Butun so'rov uchun umumiy timeout
});

// Alohida so'rov uchun CancellationToken bilan
using var cts = new CancellationTokenSource(TimeSpan.FromSeconds(5));
var response = await client.GetAsync(url, cts.Token);
```

## 5. Qachon ishlatish kerak?

| Vaziyat | Yechim |
|---|---|
| Yangi loyiha, oddiy HTTP so'rov | `IHttpClientFactory` + Typed Client |
| Deklarativ, kam boilerplate API client | Refit |
| Tashqi servis noaniq/beqaror | Polly Retry + Circuit Breaker |
| Har so'rovni logging/monitoring | `DelegatingHandler` |
| Legacy kod | `WebClient` ISHLATMANG — migratsiya qiling |

## 6. Muhim nuqtalar

- Singleton `HttpClient` (factory'siz) — DNS o'zgarishlarini
  KUZATMAYDI, uzoq ishlaydigan servislarda muammo yaratishi mumkin.
- `using var client = new HttpClient()` — HAR SO'ROVDA — Socket
  Exhaustion'ning ASOSIY sababi, ANTI-PATTERN.
- Polly Circuit Breaker — tashqi servisni **himoya qiladi**, sizning
  servisingizni EMAS — lekin natijada sizning servisingiz ham tezroq
  javob beradi (kutish o'rniga darhol xato).

## 7. Imtihon savollari

1. Socket Exhaustion nima va u qanday yuzaga keladi?
2. `IHttpClientFactory` bu muammoni qanday hal qiladi?
3. Named va Typed HttpClient orasidagi farq nima?
4. `DelegatingHandler` zanjiri qanday ishlaydi?
5. Circuit Breaker'ning 3 holatini (Closed, Open, Half-Open) tushuntiring.
6. Refit oddiy `HttpClient`dan qanday farq qiladi va qachon ishlatiladi?
7. Nima uchun Singleton `HttpClient` DNS o'zgarishini kuzata olmaydi?
