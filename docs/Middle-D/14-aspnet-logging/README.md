# Logging Providers — ASP.NET Core, Serilog — Middle D

## 1. Nima? (Ta'rif)

**Logging** — ilova ishlash jarayonidagi hodisalarni yozib borish.
**`ILogger<T>`** — ASP.NET Core'ning built-in logging abstraksiyasi.
**Serilog** — structured logging'ga ixtisoslashgan, keng qo'llaniladigan
uchinchi tomon kutubxonasi.

## 2. Nima uchun kerak?

Production'da xatoni "jonli" ko'rish (debugger) imkoni yo'q — log
yozuvlari **yagona** dalil manbasi. Yaxshi loglanmagan tizimda —
"nega buyurtma yaratilmadi" degan savolga javob topish **imkonsiz**.

## 3. Ichida nima sodir bo'ladi? (Mexanizm)

### 3.1 `ILogger<T>` — nima uchun Generic

```csharp
public class EmployeeService
{
    private readonly ILogger<EmployeeService> _logger; // T = EmployeeService

    public EmployeeService(ILogger<EmployeeService> logger) => _logger = logger;

    public void Process()
    {
        _logger.LogInformation("Xodim qayta ishlanmoqda");
    }
}
```

`ILogger<T>` — ICHKARIDA `T`ning **to'liq nomi** (`Category`) log
yozuviga avtomatik qo'shiladi (masalan `MyApp.Services.EmployeeService`)
— bu qaysi klass logladi ekanini **filterlash va qidirishda** ishlatish
imkonini beradi.

### 3.2 Log darajalari

```
Trace       — ENG batafsil, hatto method kirish/chiqishlarigacha (odatda O'CHIRILGAN)
Debug       — Debugging uchun foydali ma'lumot (development'da yoqilgan)
Information — Umumiy oqim ma'lumoti ("Buyurtma yaratildi: ID=42")
Warning     — Kutilmagan, lekin ilovani TO'XTATMAYDIGAN holat
Error       — Amal MUVAFFAQIYATSIZ bo'ldi (exception, xato)
Critical    — Butun ilova ISHDAN CHIQISHIGA yaqin jiddiy xato
```

### 3.3 appsettings.json da LogLevel filtrlash

```json
{
  "Logging": {
    "LogLevel": {
      "Default": "Information",
      "Microsoft.AspNetCore": "Warning",
      "MyApp.Services": "Debug"
    }
  }
}
```

```
Bu sozlama: "MyApp.Services" nomlangan barcha klasslar — Debug va
yuqori darajadagi loglarni yozadi, boshqa hammasi (default) —
faqat Information va yuqori.
```

### 3.4 Structured Logging — nima va nima uchun muhim

```csharp
// ❌ String interpolation — log MATN sifatida saqlanadi, QIDIRISH QIYIN
_logger.LogInformation($"Xodim {employeeId} yaratildi");

// ✅ Structured — {EmployeeId} ALOHIDA MAYDON sifatida saqlanadi
_logger.LogInformation("Xodim {EmployeeId} yaratildi", employeeId);
```

```
Farqi:
❌ "Xodim 42 yaratildi" — FAQAT matn, "employeeId=42" bo'yicha
    QIDIRISH/FILTRLASH QIYIN (regex kerak)

✅ Structured log — Seq/ElasticSearch kabi tizimlarda:
    { "Message": "Xodim {EmployeeId} yaratildi", "EmployeeId": 42,
      "Timestamp": "...", "Level": "Information" }
    → EmployeeId=42 BO'YICHA TO'G'RIDAN QIDIRISH mumkin!
```

### 3.5 Serilog — o'rnatish va sink'lar

```bash
dotnet add package Serilog.AspNetCore
dotnet add package Serilog.Sinks.Console
dotnet add package Serilog.Sinks.File
dotnet add package Serilog.Sinks.Seq
```

```csharp
Log.Logger = new LoggerConfiguration()
    .MinimumLevel.Information()
    .WriteTo.Console()
    .WriteTo.File("logs/log-.txt", rollingInterval: RollingInterval.Day) // Rolling file — kunlik
    .WriteTo.Seq("http://localhost:5341")
    .Enrich.FromLogContext()
    .CreateLogger();

builder.Host.UseSerilog();
```

**Sink** — log yozuvi qayerga YO'NALTIRILISHINI bildiradi (Console,
File, Seq, Elasticsearch va h.k.) — bitta log yozuvi **BIR NECHTA
sink**ga BIR VAQTDA yuborilishi mumkin.

### 3.6 Rolling File — kunlik fayl

```
logs/log-20260722.txt
logs/log-20260723.txt
logs/log-20260724.txt

Har kun — YANGI fayl avtomatik yaratiladi (RollingInterval.Day),
eski fayllar diskni to'ldirmasligi uchun `retainedFileCountLimit`
bilan CHEKLANISHI mumkin.
```

### 3.7 Seq UI — log qidirish

Seq — structured loglarni **vizual, filtrlanadigan** interfeysda
ko'rish imkonini beradi:

```
SQL'ga o'xshash so'rov: EmployeeId = 42 && Level = 'Error'
```

### 3.8 Production'da Debug log nima uchun yomon

```
❌ Production'da Debug/Trace darajasi YOQILGAN bo'lsa:
   - DISK TEZ TO'LADI (juda ko'p log yozuvi)
   - Performance PASAYADI (har amal uchun log yozish — I/O)
   - MAXFIY ma'lumot TASODIFAN loglanishi xavfi ORTADI
     (masalan, SQL parametrlari, request body)

✅ Production: Information/Warning DEFAULT, faqat MUAMMO paytida
   VAQTINCHA Debug'ga o'tkazish (dynamic reconfiguration bilan)
```

### 3.9 Middleware va Action Filter'da logging

```csharp
public class RequestLoggingMiddleware
{
    private readonly RequestDelegate _next;
    private readonly ILogger<RequestLoggingMiddleware> _logger;

    public async Task InvokeAsync(HttpContext context)
    {
        var sw = Stopwatch.StartNew();
        await _next(context);
        sw.Stop();

        _logger.LogInformation("HTTP {Method} {Path} → {StatusCode} ({Elapsed}ms)",
            context.Request.Method, context.Request.Path,
            context.Response.StatusCode, sw.ElapsedMilliseconds);
    }
}
```

```csharp
public class LoggingActionFilter : IActionFilter
{
    private readonly ILogger<LoggingActionFilter> _logger;

    public void OnActionExecuting(ActionExecutingContext context)
        => _logger.LogInformation("Action boshlandi: {Action}", context.ActionDescriptor.DisplayName);

    public void OnActionExecuted(ActionExecutedContext context)
        => _logger.LogInformation("Action tugadi: {Action}", context.ActionDescriptor.DisplayName);
}
```

## 4. Kod — to'liq misol

```csharp
public class OrderService
{
    private readonly ILogger<OrderService> _logger;

    public async Task<Order> CreateAsync(CreateOrderDto dto)
    {
        _logger.LogInformation("Buyurtma yaratilmoqda: {CustomerId}", dto.CustomerId);

        try
        {
            var order = await _repo.CreateAsync(dto);
            _logger.LogInformation("Buyurtma yaratildi: {OrderId}", order.Id);
            return order;
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Buyurtma yaratishda xato: {CustomerId}", dto.CustomerId);
            throw;
        }
    }
}
```

## 5. Qachon ishlatish kerak?

| Vaziyat | Yechim |
|---|---|
| Oddiy, kichik loyiha | Built-in `ILogger` + Console/Debug provider |
| Production, kerakli qidiruv/filtrlash | Serilog + Seq/Elasticsearch |
| Kunlik audit/tahlil | Rolling file sink |
| Har so'rov vaqtini kuzatish | Middleware logging |

## 6. Muhim nuqtalar

- Structured logging — `$"..."` EMAS, `{PropertyName}` placeholder
  ishlatilishi SHART (aks holda "structured" bo'lish afzalligi
  yo'qoladi).
- Log darajasini **runtime**da o'zgartirish (`LoggerFilterOptions`)
  — production muammosini debug qilishda foydali.
- Maxfiy ma'lumotlarni (parol, token) HECH QACHON to'g'ridan
  loglamang.

## 7. Imtihon savollari

1. `ILogger<T>` nima uchun generic va bu qanday amaliy foyda beradi?
2. Structured logging oddiy string interpolation'dan qanday farq
   qiladi va nima uchun muhim?
3. `LogLevel` iyerarxiyasini (Trace → Critical) tartib bilan ayting.
4. Production'da Debug darajasini yoqish nima uchun muammoli?
5. Serilog'da "Sink" tushunchasi nima?
6. Middleware va Action Filter'da logging qo'shishning farqi
   (qamrov nuqtai nazaridan) qanday?
