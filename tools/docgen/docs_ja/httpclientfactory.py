# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "Make HTTP requests using IHttpClientFactory"
CATEGORY = "ASP.NET"
TITLE = "IHttpClientFactory bilan HTTP So'rovlar"
SUBTITLE = "Socket boshqaruvi, nomlangan va tipik mijozlar"
FILENAME = "Make HTTP requests using IHttpClientFactory.docx"


def build(d):
    h1(d, "1. Ikki qarama-qarshi xato")

    para(d, "`HttpClient` ni to'g'ri ishlatish ko'rinishdan sodda, lekin ikki "
            "tomonda ham tuzoq bor.")

    h2(d, "Har so'rovda yangi HttpClient")

    code(d, """// XATO: socket oqadi
using var client = new HttpClient();
var json = await client.GetStringAsync(url, ct);""")

    para(d, "`HttpClient` `IDisposable` bo'lgani uchun uni `using` bilan "
            "o'rash mantiqiy ko'rinadi. Lekin `Dispose` dan keyin ham TCP "
            "soket `TIME_WAIT` holatida bir necha daqiqa qoladi. Yuklama "
            "ostida ephemeral portlar tugaydi va shunday xato chiqadi:")

    code(d, """SocketException: Only one usage of each socket address
(protocol/network address/port) is normally permitted""")

    h2(d, "Bitta statik HttpClient")

    code(d, """// Socket muammosi yo'q, lekin boshqa muammo bor
private static readonly HttpClient Client = new();""")

    para(d, "Bu holda soket qayta ishlatiladi, lekin mijoz **DNS "
            "o'zgarishini ko'rmaydi**: ulanish bir marta yechilgan IP ga "
            "qotib qoladi. Blue-green deploy yoki failover'dan keyin ilova "
            "eski, allaqachon o'chgan IP ga urishda davom etadi.")

    # ───────────────────────────────────────────
    h1(d, "2. IHttpClientFactory qanday hal qiladi")

    para(d, "Fabrika `HttpClient` ni emas, uning ostidagi "
            "`HttpMessageHandler` ni pool'da saqlaydi. Handler belgilangan "
            "muddatdan keyin (standart 2 daqiqa) eskiradi va yangisi "
            "yaratiladi — ya'ni DNS qayta yechiladi. `HttpClient` obyektining "
            "o'zi arzon, shuning uchun uni har safar yangi olish muammo emas.")

    code(d, """builder.Services.AddHttpClient();""")

    code(d, """public sealed class RateService(IHttpClientFactory factory)
{
    public async Task<decimal> GetAsync(string code, CancellationToken ct)
    {
        var client = factory.CreateClient();
        return await client.GetFromJsonAsync<decimal>($"/rate/{code}", ct);
    }
}""")

    note(d, "Eslatma",
         "Fabrikadan olingan `HttpClient` ni `Dispose` qilish shart emas va "
         "kerak ham emas — handler fabrika nazoratida qoladi. `using` bilan "
         "o'rash zarar keltirmaydi, lekin ma'nosiz.")

    # ───────────────────────────────────────────
    h1(d, "3. Nomlangan mijoz")

    para(d, "Har bir tashqi servis uchun o'z sozlamasi kerak bo'ladi — "
            "bazaviy manzil, timeout, header'lar:")

    code(d, """builder.Services.AddHttpClient("rates", client =>
{
    client.BaseAddress = new Uri("https://cbu.uz/");
    client.Timeout = TimeSpan.FromSeconds(10);
    client.DefaultRequestHeaders.Add("Accept", "application/json");
});""")

    code(d, """var client = factory.CreateClient("rates");""")

    para(d, "Nom matn bo'lgani uchun harf xatosi ish vaqtida chiqadi — "
            "shuning uchun nomlarni konstantada saqlayman yoki tipik "
            "mijozga o'taman.")

    # ───────────────────────────────────────────
    h1(d, "4. Tipik mijoz — eng toza yechim")

    para(d, "Bu shaklda interfeys va uning amalga oshirilishi ro'yxatga "
            "olinadi, `HttpClient` esa konstruktorga o'zi keladi:")

    code(d, """public interface IRateApi
{
    Task<decimal> GetRateAsync(string code, CancellationToken ct);
}

public sealed class RateApi(HttpClient client) : IRateApi
{
    public async Task<decimal> GetRateAsync(string code, CancellationToken ct)
    {
        var response = await client.GetAsync($"rate/{code}", ct);

        if (!response.IsSuccessStatusCode)
        {
            var body = await response.Content.ReadAsStringAsync(ct);
            throw new RateApiException(
                $"Kurs olinmadi: {(int)response.StatusCode} {body}");
        }

        var dto = await response.Content.ReadFromJsonAsync<RateDto>(ct);
        return dto!.Value;
    }
}""")

    code(d, """builder.Services.AddHttpClient<IRateApi, RateApi>(client =>
{
    client.BaseAddress = new Uri(builder.Configuration["Rates:BaseUrl"]!);
    client.Timeout = TimeSpan.FromSeconds(10);
});""")

    para(d, "Buning foydasi — chaqiruvchi kod `HttpClient` ni ko'rmaydi, "
            "faqat `IRateApi` ni biladi. Shuning uchun test yozishda "
            "interfeysni almashtirish yetarli.")

    h2(d, "BaseAddress bilan ehtiyotkorlik")

    code(d, """// BaseAddress: https://api.example.com/v1/

client.GetAsync("orders");    // https://api.example.com/v1/orders  — to'g'ri
client.GetAsync("/orders");   // https://api.example.com/orders     — v1 yo'qoldi""")

    para(d, "Ikki qoida: `BaseAddress` oxirida `/` bo'lishi kerak, nisbiy "
            "yo'l esa `/` bilan **boshlanmasligi** kerak. Bu juda ko'p vaqt "
            "yeydigan detal.")

    # ───────────────────────────────────────────
    h1(d, "5. Timeout va qayta urinish")

    para(d, "`HttpClient` ning standart timeout'i 100 soniya — bu juda uzoq. "
            "Tashqi servis osilsa, mening thread'larim ham kutib turadi va "
            "so'rovlar to'planadi.")

    code(d, """builder.Services.AddHttpClient<IRateApi, RateApi>(client =>
{
    client.Timeout = TimeSpan.FromSeconds(10);
})
.AddStandardResilienceHandler();""")

    para(d, "`AddStandardResilienceHandler()` "
            "(`Microsoft.Extensions.Http.Resilience` paketi) tayyor "
            "to'plamni beradi: qayta urinish, circuit breaker, so'rov "
            "bo'yicha timeout va umumiy timeout.")

    note(d, "Muhim",
         "Qayta urinishni faqat **idempotent** so'rovlarga qo'yish kerak. "
         "`POST` ni qayta yuborish ikki marta to'lov qilishi mumkin. "
         "Kerak bo'lsa idempotency key ishlatiladi.")

    # ───────────────────────────────────────────
    h1(d, "6. Middleware qo'shish — DelegatingHandler")

    para(d, "Har bir so'rovga token qo'shish yoki log yozish kerak bo'lsa, "
            "buni har bir metodda takrorlamaslik uchun handler yoziladi:")

    code(d, """public sealed class AuthHeaderHandler(ITokenProvider tokens) : DelegatingHandler
{
    protected override async Task<HttpResponseMessage> SendAsync(
        HttpRequestMessage request, CancellationToken ct)
    {
        var token = await tokens.GetAsync(ct);
        request.Headers.Authorization = new AuthenticationHeaderValue("Bearer", token);

        return await base.SendAsync(request, ct);
    }
}""")

    code(d, """builder.Services.AddTransient<AuthHeaderHandler>();

builder.Services.AddHttpClient<IRateApi, RateApi>()
    .AddHttpMessageHandler<AuthHeaderHandler>();""")

    para(d, "Handler'lar zanjir bo'lib ishlaydi — qo'shilgan tartibda. "
            "Ular `DelegatingHandler` dan meros bo'lib, `base.SendAsync` ni "
            "chaqirmasa zanjir uziladi.")

    # ───────────────────────────────────────────
    h1(d, "7. Testda almashtirish")

    code(d, """public sealed class StubHandler(HttpStatusCode code, string body) : HttpMessageHandler
{
    protected override Task<HttpResponseMessage> SendAsync(
        HttpRequestMessage request, CancellationToken ct)
        => Task.FromResult(new HttpResponseMessage(code)
        {
            Content = new StringContent(body, Encoding.UTF8, "application/json")
        });
}""")

    code(d, """var handler = new StubHandler(HttpStatusCode.OK, """ + '"""' + """{"value":12650}""" + '"""' + """);
var client = new HttpClient(handler) { BaseAddress = new Uri("https://test/") };

var api = new RateApi(client);
var rate = await api.GetRateAsync("USD", CancellationToken.None);

Assert.Equal(12650m, rate);""")

    para(d, "`HttpClient` ni mock qilish o'rniga `HttpMessageHandler` ni "
            "almashtiraman — chunki `HttpClient` ning metodlari virtual "
            "emas va mock kutubxonasi ularni ushlab qola olmaydi. "
            "Handler esa abstrakt klass, shuning uchun uni meros olish "
            "oson.")

    # ───────────────────────────────────────────
    h1(d, "8. Amaliyotdan: Refit va oltita handler")

    para(d, "Ish joyimdagi MAD ERP tizimida yigirmaga yaqin servis bir-biriga HTTP "
            "orqali murojaat qiladi. `HttpClient` hech qayerda qo'lda yozilmaydi — "
            "har bir servis o'z API sini Refit interfeysi sifatida e'lon qiladi, "
            "iste'molchi esa shu interfeysni inject qiladi.")

    para(d, "Refit 4-bo'limdagi tipik mijoz g'oyasini oxirigacha olib boradi: "
            "interfeys e'lon qilinadi, amalga oshirishni kutubxona generatsiya "
            "qiladi. Ro'yxatga olish esa bitta umumiy metodda:")

    code(d, """public static void RegisterApiClient<T>(this IServiceCollection services,
                                        SdkConfig config,
                                        RefitSettings refitSettings = null)
    where T : class
{
    var builder = services.AddRefitClient<T>(refitSettings)
        .ConfigureHttpClient(c => c.BaseAddress = new Uri(config.BaseUrl))
        .AddHttpMessageHandler<LanguageHeaderHandler>()
        .AddHttpMessageHandler<UserHeaderHandler>()
        .AddHttpMessageHandler<PersonHeaderHandler>()
        .AddHttpMessageHandler<LegalHeaderHandler>()
        .AddHttpMessageHandler<ApiErrorHandler>()
        .AddHttpMessageHandler<AppHeaderHandler>();

    if (!string.IsNullOrWhiteSpace(config.ServiceKey))
        builder.AddHttpMessageHandler(sp => new ServiceKeyHeaderHandler(sp, config.ServiceKey));
}""", caption="Erp.Core.Sdk/Extensions/ServiceCollectionExtensions.cs")

    para(d, "`AddRefitClient` ichida `IHttpClientFactory` ishlaydi, ya'ni 2-bo'limda "
            "aytilgan socket va DNS muammolari avtomatik hal bo'ladi.")

    h2(d, "8.1 Oltita handler nima qiladi")

    para(d, "6-bo'limda `DelegatingHandler` haqida gapirgandim. Bu yerda ular bir "
            "vaqtda ishlaydigan oltita qatlam:")

    bullets(d, [
        "`LanguageHeaderHandler` — joriy so'rovning til sarlavhasini keyingi servisga "
        "uzatadi.",
        "`UserHeaderHandler`, `PersonHeaderHandler`, `LegalHeaderHandler` — uch xil "
        "foydalanuvchi turining ma'lumotini uzatadi (xodim, jismoniy shaxs, "
        "yuridik shaxs).",
        "`AppHeaderHandler` — qaysi modul chaqirganini bildiradi.",
        "`ApiErrorHandler` — teskari yo'nalishda ishlaydi: javobni ko'rib, xato "
        "holat kodini domen istisnosiga aylantiradi.",
    ])

    para(d, "Til uzatadigan handler ichi shunday ko'rinadi:")

    code(d, """protected override async Task<HttpResponseMessage> SendAsync(
    HttpRequestMessage request, CancellationToken cancellationToken)
{
    var httpContext = _serviceProvider.GetService<IHttpContextAccessor>()?.HttpContext;

    if (httpContext != null)
    {
        // 1. Headerdan olishga urining (frontend yuborganda)
        var langValue = GetLanguageFromHeader(httpContext)
                     // 2. Yo'q bo'lsa query parametrdan ol (boshqa service yuborganda)
                     ?? GetLanguageFromQuery(httpContext);

        if (!string.IsNullOrEmpty(langValue))
        {
            // Duplicate bo'lmasligi uchun
            if (request.Headers.Contains(ApplicationHeaderConst.Language))
                request.Headers.Remove(ApplicationHeaderConst.Language);

            request.Headers.Add(ApplicationHeaderConst.Language, langValue);
        }
    }

    return await base.SendAsync(request, cancellationToken);
}""")

    para(d, "Ikki nozik joy bor. Birinchisi — `IHttpContextAccessor` konstruktorda "
            "emas, `IServiceProvider` orqali olinadi. Sababi 2-bo'limda aytilgan "
            "handler keshlanishi: handler `HttpClient` bilan birga saqlanadi, ya'ni "
            "uning umri so'rovdan uzun. Scoped xizmatni konstruktorda ushlab qolish "
            "captive dependency bo'lardi va birinchi so'rovning konteksti hamma "
            "keyingi so'rovlarda qolib ketardi.")

    para(d, "Ikkinchisi — sarlavha qo'shishdan oldin o'chiriladi. Chidamlilik qatlami "
            "so'rovni qayta yuborganda bir xil `HttpRequestMessage` qayta ishlanishi "
            "mumkin, va sarlavha ikki marta qo'shilib qolardi.")

    note(d, "Mana bu tuzoqni esda saqlab qoldim:",
         "`ConfigureHttpClient` ichidagi `new Uri(config.BaseUrl)` — lambda. U DI "
         "ro'yxatga olinganda emas, `HttpClient` birinchi marta yaratilganda "
         "bajariladi. Natijada `BaseUrl` noto'g'ri bo'lsa servis muammosiz ishga "
         "tushadi, health check yashil bo'ladi — va faqat o'sha SDK ni inject "
         "qiladigan kontroller 500 qaytaradi. Stack trace da esa shunchaki "
         "`UriFormatException`, qaysi SDK aybli ekani yozilmaydi. Ya'ni tez "
         "ishga tushish lazy ishga tushirishning narxi bilan keladi.")

    sources(d, [
        ("IHttpClientFactory with .NET",
         "https://learn.microsoft.com/en-us/dotnet/core/extensions/httpclient-factory"),
        ("Make HTTP requests using IHttpClientFactory in ASP.NET Core",
         "https://learn.microsoft.com/en-us/aspnet/core/fundamentals/http-requests"),
        ("Build resilient HTTP apps",
         "https://learn.microsoft.com/en-us/dotnet/core/resilience/http-resilience"),
    ])
