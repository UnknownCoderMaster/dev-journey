# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "WebClient, HttpClient, Proxies, NetworkCredential"
CATEGORY = ".NET / C#"
TITLE = "HttpClient va Tarmoq Mijozlari"
SUBTITLE = "HTTP so'rovlar, proxy va autentifikatsiya"
FILENAME = "WebClient, HttpClient, Proxies, NetworkCredential.docx"


def build(d):
    h1(d, "1. WebClient va HttpClient")

    para(d, "`WebClient` — eski API. U `.NET 6` dan boshlab eskirgan deb "
            "belgilangan va yangi kodda ishlatilmasligi kerak.")

    code(d, """// Eskirgan
using var client = new WebClient();
var text = client.DownloadString("https://api.example.com/books");

// Zamonaviy
using var http = new HttpClient();
var text = await http.GetStringAsync("https://api.example.com/books");""")

    table(d, ["Jihat", "WebClient", "HttpClient"],
          [["Holati", "Eskirgan", "Joriy"],
           ["Asinxronlik", "Hodisaga asoslangan", "`Task` asosida"],
           ["Qayta ishlatish", "Mo'ljallanmagan", "Mo'ljallangan"],
           ["HTTP/2, HTTP/3", "Yo'q", "Bor"],
           ["Nozik sozlash", "Cheklangan", "Keng"]],
          widths=[3.6, 5.4, 6.5])

    # ───────────────────────────────────────────
    h1(d, "2. HttpClient ni to'g'ri ishlatish")

    note(d, "Bu eng mashhur `.NET` xatolaridan biri:",
         "`using var client = new HttpClient()` — intuitiv to'g'ri "
         "ko'rinadi, chunki `IDisposable` ni yopish kerak. Lekin "
         "`Dispose` dan keyin ham TCP ulanish `TIME_WAIT` holatida bir "
         "necha daqiqa qoladi. Yuqori yukda portlar tugaydi va "
         "`SocketException` chiqadi.")

    note(d, "Teskari xato ham bor:",
         "Bitta statik `HttpClient` yaratsam, port tugashi muammosi "
         "yo'qoladi, lekin DNS o'zgarishi e'tiborga olinmaydi — mijoz "
         "eski IP manzilga ulanib turaveradi. Xizmat boshqa serverga "
         "ko'chirilsa, ilovam uni ko'rmaydi.")

    para(d, "Ikkala muammoni `IHttpClientFactory` hal qiladi:")

    code(d, """builder.Services.AddHttpClient("github", client =>
{
    client.BaseAddress = new Uri("https://api.github.com/");
    client.Timeout = TimeSpan.FromSeconds(30);
    client.DefaultRequestHeaders.UserAgent.ParseAdd("MyApp/1.0");
    client.DefaultRequestHeaders.Accept.Add(
        new MediaTypeWithQualityHeaderValue("application/json"));
});""")

    code(d, """public class GitHubService
{
    private readonly HttpClient _http;

    public GitHubService(IHttpClientFactory factory)
        => _http = factory.CreateClient("github");
}""")

    h2(d, "2.1 Tipli mijoz")

    code(d, """builder.Services.AddHttpClient<IGitHubService, GitHubService>(client =>
{
    client.BaseAddress = new Uri("https://api.github.com/");
});

public class GitHubService : IGitHubService
{
    private readonly HttpClient _http;

    public GitHubService(HttpClient http) => _http = http;

    public async Task<IReadOnlyList<RepoDto>> GetReposAsync(
        string user, CancellationToken ct)
    {
        var repos = await _http.GetFromJsonAsync<List<RepoDto>>(
            $"users/{user}/repos", ct);

        return repos ?? [];
    }
}""")

    note(d, "Tipli mijozni men afzal ko'raman:",
         "Nom bilan ishlaganda mijoz nomi matn bo'ladi va harf xatosi "
         "ish vaqtida aniqlanadi. Tipli mijozda esa kompilyator "
         "tekshiradi va sozlama o'sha xizmat bilan bir joyda turadi.")

    # ───────────────────────────────────────────
    h1(d, "3. So'rovlar")

    code(d, """// GET
var books = await _http.GetFromJsonAsync<List<BookDto>>("api/books", ct);

// POST
var response = await _http.PostAsJsonAsync("api/books", newBook, ct);
response.EnsureSuccessStatusCode();
var created = await response.Content.ReadFromJsonAsync<BookDto>(ct);

// PUT va DELETE
await _http.PutAsJsonAsync($"api/books/{id}", updated, ct);
await _http.DeleteAsync($"api/books/{id}", ct);""")

    h2(d, "3.1 To'liq nazorat")

    code(d, """var request = new HttpRequestMessage(HttpMethod.Post, "api/books")
{
    Content = JsonContent.Create(newBook)
};

request.Headers.Add("X-Request-Id", Guid.NewGuid().ToString());
request.Headers.Authorization = new AuthenticationHeaderValue("Bearer", token);

using var response = await _http.SendAsync(
    request, HttpCompletionOption.ResponseHeadersRead, ct);

if (!response.IsSuccessStatusCode)
{
    var error = await response.Content.ReadAsStringAsync(ct);
    throw new HttpRequestException(
        $"{(int)response.StatusCode}: {error}");
}""")

    note(d, "`ResponseHeadersRead` katta javoblarda muhim:",
         "Sukut bo'yicha `SendAsync` butun javob tanasini xotiraga "
         "yuklaguncha kutadi. Agar javob yuz megabaytlik fayl bo'lsa, "
         "u to'liq xotiraga tushadi. `ResponseHeadersRead` esa "
         "sarlavhalar kelishi bilan qaytadi va tanani oqim sifatida "
         "o'qish imkonini beradi.")

    code(d, """// Katta faylni oqim orqali saqlash
using var response = await _http.GetAsync(
    url, HttpCompletionOption.ResponseHeadersRead, ct);

await using var source = await response.Content.ReadAsStreamAsync(ct);
await using var target = File.Create(path);

await source.CopyToAsync(target, ct);""")

    # ───────────────────────────────────────────
    h1(d, "4. Proxy sozlash")

    code(d, """builder.Services.AddHttpClient("external")
    .ConfigurePrimaryHttpMessageHandler(() => new SocketsHttpHandler
    {
        Proxy = new WebProxy("http://proxy.company.local:8080")
        {
            Credentials = new NetworkCredential("user", "password"),
            BypassProxyOnLocal = true,
            BypassList = ["*.internal.local", "10\\.0\\..*"]
        },
        UseProxy = true
    });""")

    code(d, """// Tizim proxy sozlamalarini ishlatish
var handler = new SocketsHttpHandler
{
    UseProxy = true,
    Proxy = WebRequest.GetSystemWebProxy()
};

// Proxy ni butunlay o'chirish
var handler = new SocketsHttpHandler { UseProxy = false };""")

    code(d, """# Atrof-muhit o'zgaruvchilari orqali
export HTTP_PROXY=http://proxy.local:8080
export HTTPS_PROXY=http://proxy.local:8080
export NO_PROXY=localhost,127.0.0.1,.internal.local""")

    note(d, "`BypassProxyOnLocal` ni yoqish odatda zarur:",
         "Usiz lokal xizmatlarga murojaat ham proxy orqali ketadi va "
         "ko'pincha muvaffaqiyatsiz bo'ladi. Korporativ tarmoqda "
         "ishlaganda bu birinchi tekshiradigan sozlamalardan biri.")

    # ───────────────────────────────────────────
    h1(d, "5. Autentifikatsiya")

    h2(d, "5.1 NetworkCredential")

    para(d, "`NetworkCredential` foydalanuvchi nomi va parolni saqlaydi. "
            "U asosan Windows autentifikatsiyasi va proxy uchun "
            "ishlatiladi.")

    code(d, """var handler = new HttpClientHandler
{
    Credentials = new NetworkCredential("user", "password", "DOMAIN"),
    PreAuthenticate = true
};

// Joriy Windows foydalanuvchisi
var handler = new HttpClientHandler
{
    UseDefaultCredentials = true
};""")

    h2(d, "5.2 Bearer token")

    code(d, """_http.DefaultRequestHeaders.Authorization =
    new AuthenticationHeaderValue("Bearer", token);

// Yoki har so'rovga avtomatik qo'shadigan handler
public class AuthHandler : DelegatingHandler
{
    private readonly ITokenProvider _tokens;

    protected override async Task<HttpResponseMessage> SendAsync(
        HttpRequestMessage request, CancellationToken ct)
    {
        var token = await _tokens.GetAsync(ct);

        request.Headers.Authorization =
            new AuthenticationHeaderValue("Bearer", token);

        return await base.SendAsync(request, ct);
    }
}""")

    code(d, """builder.Services.AddTransient<AuthHandler>();

builder.Services.AddHttpClient("api")
    .AddHttpMessageHandler<AuthHandler>();""")

    h2(d, "5.3 Basic autentifikatsiya")

    code(d, """var credentials = Convert.ToBase64String(
    Encoding.UTF8.GetBytes($"{user}:{password}"));

_http.DefaultRequestHeaders.Authorization =
    new AuthenticationHeaderValue("Basic", credentials);""")

    note(d, "Basic autentifikatsiya shifrlash emas:",
         "Base64 — kodlash, uni istalgan vaqtda ochish mumkin. Shuning "
         "uchun u faqat HTTPS ustida ishlatilishi kerak. HTTP orqali "
         "yuborilsa, parol amalda ochiq matnda ketadi.")

    # ───────────────────────────────────────────
    h1(d, "6. Chidamlilik")

    code(d, """dotnet add package Microsoft.Extensions.Http.Resilience""")

    code(d, """builder.Services.AddHttpClient("external")
    .AddStandardResilienceHandler(options =>
    {
        options.Retry.MaxRetryAttempts = 3;
        options.Retry.BackoffType = DelayBackoffType.Exponential;
        options.Retry.UseJitter = true;

        options.CircuitBreaker.FailureRatio = 0.5;
        options.CircuitBreaker.MinimumThroughput = 10;
        options.CircuitBreaker.BreakDuration = TimeSpan.FromSeconds(30);

        options.AttemptTimeout.Timeout = TimeSpan.FromSeconds(10);
        options.TotalRequestTimeout.Timeout = TimeSpan.FromSeconds(30);
    });""")

    note(d, "`UseJitter` kichik, lekin muhim sozlama:",
         "Agar yuzta mijoz bir vaqtda xatolik olsa va hammasi aniq "
         "ikki soniyadan keyin qayta urinsa — ular yana birga keladi "
         "va xizmatni yana bosadi. Jitter tasodifiy kechikish qo'shadi "
         "va urinishlarni tarqatadi.")

    note(d, "Circuit breaker ning mantig'i:",
         "Agar xizmat ishlamayotgan bo'lsa, unga so'rov yuborishda ma'no "
         "yo'q — faqat kutish vaqti sarflanadi. Breaker ma'lum sondagi "
         "xatodan keyin \"ochiladi\" va so'rovlarni darhol rad etadi. "
         "Bu ham mening ilovamni, ham qarshi tomonni tiklanishga imkon "
         "beradi.")

    # ───────────────────────────────────────────
    h1(d, "7. Sertifikat masalalari")

    code(d, """// Faqat ishlab chiqishda — o'z imzolangan sertifikat uchun
#if DEBUG
var handler = new HttpClientHandler
{
    ServerCertificateCustomValidationCallback =
        HttpClientHandler.DangerousAcceptAnyServerCertificateValidator
};
#endif""")

    note(d, "Bu kodni production ga chiqarmaslik kerak:",
         "U barcha sertifikatlarni qabul qiladi, ya'ni o'rtadagi odam "
         "hujumidan himoyani butunlay o'chiradi. Men uni `#if DEBUG` "
         "ichiga olaman — shunda u Release qurilishiga tushmaydi. "
         "Metod nomidagi `Dangerous` so'zi ham bejiz emas.")

    code(d, """// Mijoz sertifikati bilan autentifikatsiya
var certificate = new X509Certificate2("client.pfx", password);

var handler = new SocketsHttpHandler();
handler.SslOptions.ClientCertificates = [certificate];""")

    # ───────────────────────────────────────────
    h1(d, "8. Xulosa")

    bullets(d, [
        "`WebClient` eskirgan — `HttpClient` ishlatiladi.",
        "`HttpClient` ni har so'rovda yaratish port tugashiga, statik "
        "qilish esa DNS eskirishiga olib keladi.",
        "`IHttpClientFactory` ikkala muammoni hal qiladi.",
        "Tipli mijoz nom bilan ishlashdan ishonchliroq.",
        "`ResponseHeadersRead` katta javoblarni xotiraga yuklamasdan "
        "o'qish imkonini beradi.",
        "Proxy `SocketsHttpHandler` orqali yoki atrof-muhit "
        "o'zgaruvchilari bilan sozlanadi.",
        "Basic autentifikatsiya shifrlash emas — faqat HTTPS ustida.",
        "`AddStandardResilienceHandler` qayta urinish, kutish vaqti va "
        "circuit breaker ni bir yo'la beradi.",
    ])

    sources(d, [
        ("HttpClient Class — .NET API",
         "https://learn.microsoft.com/en-us/dotnet/api/system.net.http.httpclient"),
        ("IHttpClientFactory with .NET",
         "https://learn.microsoft.com/en-us/dotnet/core/extensions/httpclient-factory"),
        ("Build resilient HTTP apps",
         "https://learn.microsoft.com/en-us/dotnet/core/resilience/http-resilience"),
        ("HTTP proxy configuration — .NET",
         "https://learn.microsoft.com/en-us/dotnet/fundamentals/networking/http/httpclient"),
    ])
