# IHttpClientFactory bilan HTTP So'rovlar — Junior A

> Bu mavzu chuqurroq shaklda [Middle-D/03-http-client](../../Middle-D/03-http-client/README.md)da
> yoritilgan (Socket Exhaustion, Polly, DelegatingHandler). Bu fayl
> — Junior A darajasiga mos, **asosiy tushunchalarga** e'tibor
> qaratadi.

## 1. Nima? (Ta'rif)

**`IHttpClientFactory`** — `HttpClient` obyektlarini **to'g'ri
yaratish, boshqarish va qayta ishlatish** uchun ASP.NET Core'ning
markazlashgan fabrika (factory) xizmati.

## 2. Nima uchun kerak?

`HttpClient`ni **noto'g'ri** ishlatish (har so'rovda `new HttpClient()`)
— **Socket Exhaustion** (TCP portlari tugab qolishi) degan jiddiy
production muammosiga olib keladi. `IHttpClientFactory` — bu
muammoni **connection pooling** orqali hal qiladi.

## 3. Ichida nima sodir bo'ladi? (Mexanizm)

### 3.1 HttpClient muammosi — socket exhaustion, DNS refresh

```csharp
// ❌ XAVFLI — har chaqiriqda YANGI HttpClient
public async Task<string> GetData()
{
    using var client = new HttpClient();
    return await client.GetStringAsync("https://api.example.com");
}
```

```
`using`dan keyin — HttpClient DISPOSE bo'ladi, LEKIN ICHIDAGI TCP
socket — DARHOL yopilmaydi, ~240 soniya "TIME_WAIT" holatida
QOLADI (TCP standarti). Yuqori trafikda — bu OS SOCKET LIMITINI
TUGATIB, SocketException keltirib chiqaradi.

Muqobil yechim — Singleton HttpClient — DNS o'zgarishini KUZATA
OLMAYDI (agar tashqi server IP'si o'zgarsa, Singleton client ESKI
IP'ga ULANAVERADI).
```

### 3.2 `AddHttpClient()` — DI ga qo'shish

```csharp
builder.Services.AddHttpClient(); // Asosiy, nomlanmagan factory
```

### 3.3 Named HttpClient

```csharp
builder.Services.AddHttpClient("LmsApi", client =>
{
    client.BaseAddress = new Uri("https://lms.example.com/");
    client.Timeout = TimeSpan.FromSeconds(10);
});

// Ishlatish
public class LmsService
{
    private readonly IHttpClientFactory _factory;
    public async Task<string> GetCoursesAsync()
    {
        var client = _factory.CreateClient("LmsApi"); // NOM orqali
        return await client.GetStringAsync("courses");
    }
}
```

### 3.4 Typed HttpClient

```csharp
public interface ILmsApiClient { Task<List<Course>> GetCoursesAsync(); }

public class LmsApiClient : ILmsApiClient
{
    private readonly HttpClient _httpClient;
    public LmsApiClient(HttpClient httpClient) => _httpClient = httpClient; // Factory AVTOMATIK inject qiladi
    public async Task<List<Course>> GetCoursesAsync()
        => await _httpClient.GetFromJsonAsync<List<Course>>("courses") ?? new();
}

builder.Services.AddHttpClient<ILmsApiClient, LmsApiClient>(client =>
    client.BaseAddress = new Uri("https://lms.example.com/"));
```

Typed Client — Named Client'dan **tavsiya etiladigan**, chunki
**compile-time xavfsiz** (nom string emas, interfeys orqali).

### 3.5 DelegatingHandler — middleware, logging, retry

```csharp
public class LoggingHandler : DelegatingHandler
{
    protected override async Task<HttpResponseMessage> SendAsync(HttpRequestMessage request, CancellationToken ct)
    {
        Console.WriteLine($"So'rov: {request.RequestUri}");
        var response = await base.SendAsync(request, ct);
        Console.WriteLine($"Javob: {response.StatusCode}");
        return response;
    }
}

builder.Services.AddTransient<LoggingHandler>();
builder.Services.AddHttpClient<ILmsApiClient, LmsApiClient>()
    .AddHttpMessageHandler<LoggingHandler>();
```

### 3.6 Polly bilan integration

```csharp
builder.Services.AddHttpClient<ILmsApiClient, LmsApiClient>()
    .AddPolicyHandler(Policy<HttpResponseMessage>
        .Handle<HttpRequestException>()
        .WaitAndRetryAsync(3, i => TimeSpan.FromSeconds(Math.Pow(2, i))));
```

### 3.7 `BaseAddress`, `DefaultRequestHeaders`

```csharp
client.BaseAddress = new Uri("https://api.example.com/");
client.DefaultRequestHeaders.Add("X-Api-Key", "mykey");
client.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", token);
```

### 3.8 Timeout

```csharp
client.Timeout = TimeSpan.FromSeconds(30); // Butun so'rov uchun UMUMIY chegara
```

### 3.9 Refit — interface-based HTTP client (sizning stackingizda)

```csharp
public interface ILmsApi
{
    [Get("/courses")]
    Task<List<Course>> GetCoursesAsync();

    [Post("/enrollments")]
    Task<Enrollment> EnrollAsync([Body] EnrollRequest request);
}

builder.Services.AddRefitClient<ILmsApi>()
    .ConfigureHttpClient(c => c.BaseAddress = new Uri("https://lms.example.com/"));
```

Refit — HTTP so'rov yozish/JSON serialize qilish kodini **butunlay
yashiradi** — interfeys chaqiruvi, xuddi oddiy C# metodidek ko'rinadi.

### 3.10 `HttpResponseMessage`, JSON deserialization

```csharp
using var response = await client.GetAsync("employees/1");
response.EnsureSuccessStatusCode(); // Muvaffaqiyatsiz bo'lsa — Exception

var employee = await response.Content.ReadFromJsonAsync<Employee>();
// yoki qisqa yo'l:
var employee2 = await client.GetFromJsonAsync<Employee>("employees/1");
```

## 4. Kod — real ERP misol: BFF'dan microservice'ga so'rov

```csharp
public interface IEmployeeMicroserviceClient
{
    Task<EmployeeDto?> GetEmployeeAsync(int id, CancellationToken ct);
}

public class EmployeeMicroserviceClient : IEmployeeMicroserviceClient
{
    private readonly HttpClient _httpClient;
    public EmployeeMicroserviceClient(HttpClient httpClient) => _httpClient = httpClient;

    public async Task<EmployeeDto?> GetEmployeeAsync(int id, CancellationToken ct)
    {
        var response = await _httpClient.GetAsync($"api/employees/{id}", ct);
        if (response.StatusCode == HttpStatusCode.NotFound) return null;
        response.EnsureSuccessStatusCode();
        return await response.Content.ReadFromJsonAsync<EmployeeDto>(cancellationToken: ct);
    }
}

builder.Services.AddHttpClient<IEmployeeMicroserviceClient, EmployeeMicroserviceClient>(client =>
    client.BaseAddress = new Uri("http://employee-service:8080/"));
```

## 5. Qachon ishlatish kerak?

| Vaziyat | Yechim |
|---|---|
| Yangi loyiha, oddiy HTTP so'rov | `IHttpClientFactory` + Typed Client |
| Kam boilerplate, deklarativ API client | Refit |
| Retry/Circuit Breaker kerak | Polly bilan `AddPolicyHandler` |
| Har so'rovni log qilish | `DelegatingHandler` |

## 6. Muhim nuqtalar

- `new HttpClient()` — HAR SO'ROVDA — ANTI-PATTERN, Socket
  Exhaustion'ga olib keladi.
- Typed Client — Named Client'dan **compile-time xavfsizroq** (nom
  yozishda xatolik ehtimoli yo'q).
- Refit — `IHttpClientFactory` bilan **BIRGA** ishlaydi (uni
  ALMASHTIRMAYDI, USTIGA quriladi).

## 7. Imtihon savollari

1. Socket Exhaustion nima va u qanday yuzaga keladi?
2. `IHttpClientFactory` bu muammoni qanday hal qiladi?
3. Named va Typed HttpClient orasidagi farq nima?
4. `DelegatingHandler` qanday vazifa bajaradi?
5. Refit oddiy `HttpClient`dan qanday farq qiladi?
6. `client.Timeout` qachon ishlatiladi?
