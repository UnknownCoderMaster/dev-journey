# NLog, Serilog — Junior A

> Serilog asoslari (LogLevel, structured logging, sink'lar) chuqurroq
> [Middle-D/14-aspnet-logging](../../Middle-D/14-aspnet-logging/README.md)da
> yoritilgan. Bu fayl — **Serilog va NLog'ni solishtirgan holda**,
> ikkalasini ham qamrab oladi.

## 1. Nima? (Ta'rif)

**ILogger<T>** — ASP.NET Core'ning built-in logging abstraksiyasi.
**Serilog** va **NLog** — bu abstraksiya ustiga qo'shimcha
imkoniyat (structured logging, ko'p sink) beruvchi **uchinchi
tomon** kutubxonalari.

## 2. Nima uchun kerak?

Built-in `ILogger` — oddiy, lekin **cheklangan** (Console/Debug
provider). Serilog/NLog — **fayl, Seq, Elasticsearch** kabi ko'p
manzilga, **structured** (qidirilishi oson) formatda log yozish
imkonini beradi.

## 3. Ichida nima sodir bo'ladi? (Mexanizm)

### 3.1 `ILogger<T>` — built-in

```csharp
public class EmployeeService
{
    private readonly ILogger<EmployeeService> _logger;
    public EmployeeService(ILogger<EmployeeService> logger) => _logger = logger;

    public void Process() => _logger.LogInformation("Xodim qayta ishlanmoqda");
}
```

### 3.2 Serilog — o'rnatish

```bash
dotnet add package Serilog.AspNetCore
dotnet add package Serilog.Sinks.File
dotnet add package Serilog.Sinks.Seq
```

```csharp
Log.Logger = new LoggerConfiguration()
    .MinimumLevel.Information()
    .MinimumLevel.Override("Microsoft", LogEventLevel.Warning)
    .Enrich.WithMachineName()
    .Enrich.WithThreadId()
    .WriteTo.Console()
    .WriteTo.File("logs/log-.txt", rollingInterval: RollingInterval.Day)
    .WriteTo.Seq("http://localhost:5341")
    .CreateLogger();

builder.Host.UseSerilog();
```

**Enricher** — har log yozuviga **avtomatik qo'shimcha kontekst**
qo'shadi:
```csharp
.Enrich.WithMachineName()  // Qaysi server yozdi
.Enrich.WithThreadId()     // Qaysi thread
.Enrich.FromLogContext()   // Qo'shimcha, qo'lda qo'shilgan property'lar
```

### 3.3 Structured log

```csharp
_logger.LogInformation("Xodim {EmployeeId} yaratildi", employeeId); // ✅ {EmployeeId} — ALOHIDA maydon
_logger.LogInformation($"Xodim {employeeId} yaratildi");            // ❌ Faqat matn, QIDIRISH qiyin
```

### 3.4 NLog — konfiguratsiya

```bash
dotnet add package NLog.Web.AspNetCore
```

```xml
<!-- nlog.config -->
<nlog xmlns="http://www.nlog-project.org/schemas/NLog.xsd">
  <targets>
    <target name="file" xsi:type="File" fileName="logs/${shortdate}.log"
            layout="${longdate} ${level} ${message} ${exception}" />
    <target name="console" xsi:type="Console" />
  </targets>
  <rules>
    <logger name="*" minlevel="Info" writeTo="file,console" />
    <logger name="Microsoft.*" maxlevel="Warning" final="true" /> <!-- Microsoft loglarini FILTRLASH -->
  </rules>
</nlog>
```

```csharp
// Program.cs
builder.Logging.ClearProviders();
builder.Host.UseNLog();
```

**Target** — qayerga yoziladi (file, console, database). **Rule**
— qaysi logger, qaysi darajada, qaysi target'ga yo'naltiriladi.

### 3.5 Serilog vs NLog — farqi

| | Serilog | NLog |
|---|---|---|
| Konfiguratsiya | Code-first (fluent API) | XML fayl (yoki code) |
| Structured logging | ✅ Tabiiy (birinchi darajali) | Qo'llab-quvvatlaydi, lekin kamroq "tabiiy" |
| Mashhurlik (.NET) | ✅ Eng ko'p ishlatiladigan | Keng tarqalgan, uzoq tarixga ega |
| Sink/Target soni | Juda ko'p (200+) | Ko'p |

Ikkalasi ham **yaxshi tanlov** — Serilog **code-first, structured**
yondashuvi tufayli zamonaviy .NET loyihalarda ko'proq tanlanadi.

### 3.6 Log darajalari

```
Trace → Debug → Information → Warning → Error → Critical
```

```json
{
  "Logging": {
    "LogLevel": {
      "Default": "Information",
      "Microsoft.AspNetCore": "Warning"
    }
  }
}
```

### 3.7 Structured logging nima uchun muhim — query, filter

```
Seq/Elasticsearch'da:
  EmployeeId = 42 AND Level = 'Error'  ← STRUKTURA orqali TO'G'RIDAN qidiruv

Oddiy matn log'da:
  grep "42" log.txt  ← REGEX/matn qidiruv, XATO-BOROQ va SEKINROQ
```

### 3.8 Seq UI — local log qidirish

Seq — Docker orqali local ishga tushiriladi (`docker run seqlog/seq`),
structured loglarni **vizual, filtrlanadigan** dashboard'da
ko'rsatadi.

### 3.9 Production'da log strategiyasi

```
✅ Information/Warning — DEFAULT daraja
✅ Error/Critical — HAR DOIM log qilinadi, ALERT bilan bog'lanadi
❌ Debug/Trace — Production'da ODATDA O'CHIRILGAN (disk/performance)
✅ Maxfiy ma'lumot (parol, token) — HECH QACHON log qilinmasin
```

## 4. Kod — to'liq misol

```csharp
var builder = WebApplication.CreateBuilder(args);

builder.Host.UseSerilog((context, config) => config
    .ReadFrom.Configuration(context.Configuration)
    .Enrich.FromLogContext()
    .WriteTo.Console()
    .WriteTo.File("logs/erp-.log", rollingInterval: RollingInterval.Day));

var app = builder.Build();
app.UseSerilogRequestLogging(); // HAR HTTP so'rovni AVTOMATIK log qiladi
```

## 5. Qachon ishlatish kerak?

| Vaziyat | Yechim |
|---|---|
| Yangi .NET loyiha | Serilog |
| Legacy loyiha, XML konfiguratsiya afzal | NLog |
| Local development, log qidirish | Seq |
| Production, katta hajm | Elasticsearch/Application Insights |

## 6. Muhim nuqtalar

- Structured logging (`{Property}`) — string interpolation
  (`$"..."`)dan **doim** afzal.
- Production'da Debug darajasini yoqish — disk va performance
  narxi bor.
- Serilog/NLog — `ILogger<T>` abstraksiyasini **almashtirmaydi**,
  balki uning **implementatsiyasini** ta'minlaydi.

## 7. Imtihon savollari

1. Structured logging nima va u nima uchun oddiy matn logdan
   yaxshiroq?
2. Serilog va NLog orasidagi asosiy farq nima?
3. Enricher nima vazifani bajaradi?
4. NLog'da Target va Rule tushunchalari nima?
5. Production'da Debug log darajasi nima uchun tavsiya etilmaydi?
6. Seq UI qanday amaliy foyda beradi?
