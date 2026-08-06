# ASP.NET Core Configuration — Junior A

## 1. Nima? (Ta'rif)

**Configuration** — ilova sozlamalarini (connection string, API
kalit, feature flag) **turli manbalardan** (fayl, environment
variable, komanda qatori) yig'ib, **birlashtiruvchi** ASP.NET Core
tizimi — markaziy interfeys: `IConfiguration`.

## 2. Nima uchun kerak?

Sozlamalarni kodga **hardcode** qilish — har muhitda (dev/staging/prod)
qayta **kompilyatsiya** talab qiladi. Configuration tizimi —
sozlamalarni **kod tashqarisida**, muhitga qarab **almashtiriladigan**
qiladi.

## 3. Ichida nima sodir bo'ladi? (Mexanizm)

### 3.1 `appsettings.json` — asosiy fayl

```json
{
  "ConnectionStrings": { "DefaultConnection": "Host=localhost;Database=erp" },
  "Jwt": { "Issuer": "erp.example.com", "AccessTokenExpirationMinutes": 15 }
}
```

### 3.2 Configuration hierarchiyasi — qaysi manba ustunlik qiladi

```
1. appsettings.json                    (ENG PAST ustuvorlik)
2. appsettings.{Environment}.json
3. User Secrets (FAQAT Development)
4. Environment Variables
5. Command-line arguments               (ENG YUQORI ustuvorlik)

Har KEYINGI manba — OLDINGISINI USTIDAN YOZADI (agar BIR XIL
kalit BO'LSA).
```

```bash
dotnet run --Jwt:AccessTokenExpirationMinutes=30 # Command-line — ENG KUCHLI
```

### 3.3 `GetValue<T>()`, `GetSection()`, `GetConnectionString()`

```csharp
var builder = WebApplication.CreateBuilder(args);

string? issuer = builder.Configuration["Jwt:Issuer"]; // Indexer — ":" bilan NESTED kalit
int expiryMinutes = builder.Configuration.GetValue<int>("Jwt:AccessTokenExpirationMinutes");
var jwtSection = builder.Configuration.GetSection("Jwt");
string? connStr = builder.Configuration.GetConnectionString("DefaultConnection"); // "ConnectionStrings:DefaultConnection" QISQARTMASI
```

### 3.4 `IOptions<T>` bilan strongly-typed

```csharp
public class JwtSettings
{
    public string Issuer { get; set; } = null!;
    public int AccessTokenExpirationMinutes { get; set; }
}

builder.Services.Configure<JwtSettings>(builder.Configuration.GetSection("Jwt"));

public class TokenService
{
    private readonly JwtSettings _settings;
    public TokenService(IOptions<JwtSettings> options) => _settings = options.Value;
}
```

### 3.5 `IOptionsSnapshot<T>` vs `IOptionsMonitor<T>`

```
IOptions<T>          — Singleton, BIR MARTA (start'da) o'qiladi
IOptionsSnapshot<T>  — Scoped, HAR HTTP so'rov boshida QAYTA o'qiladi
IOptionsMonitor<T>   — Singleton, RUNTIME'da .CurrentValue orqali
                        HAR DOIM ENG YANGI qiymatni beradi, OnChange()
                        callback bilan
```

### 3.6 Configuration Validation

```csharp
builder.Services.AddOptions<JwtSettings>()
    .Bind(builder.Configuration.GetSection("Jwt"))
    .ValidateDataAnnotations()
    .ValidateOnStart(); // Ilova NOTO'G'RI konfiguratsiya bilan ISHGA TUSHMAYDI
```

### 3.7 User Secrets — development uchun

```bash
dotnet user-secrets init
dotnet user-secrets set "ConnectionStrings:DefaultConnection" "Host=localhost;Password=dev123"
```

```
Saqlanadi LOYIHA papkasi TASHQARISIDA (%APPDATA%\Microsoft\UserSecrets)
— git'ga TASODIFAN commit qilinmaydi.
```

### 3.8 Environment variables — `ASPNETCORE_ENVIRONMENT`

```bash
export ASPNETCORE_ENVIRONMENT=Production
export ConnectionStrings__DefaultConnection="Host=prod-db;..." # "__" — NESTED kalit ajratuvchisi
```

### 3.9 Azure App Configuration (qisqacha)

```csharp
builder.Configuration.AddAzureAppConfiguration(options =>
    options.Connect(connectionString).UseFeatureFlags());
```

Enterprise loyihalarda — sozlamalarni **markazlashgan**, **audit
qilinadigan**, **real-time yangilanadigan** joyda saqlash uchun.

### 3.10 Nima appsettings'da SAQLANMAYDI

```
❌ Connection string PAROL bilan (production uchun)
❌ JWT secret key
❌ API kalitlar, tashqi servis credentiallari
❌ Shifrlash kalitlari

✅ appsettings.json — FAQAT strukturaviy "shablon" (bo'sh yoki
   placeholder qiymat bilan), HAQIQIY MAXFIY qiymat — Environment
   Variable/Key Vault orqali.
```

## 4. Kod — to'liq misol

```csharp
var builder = WebApplication.CreateBuilder(args);

builder.Services.AddOptions<JwtSettings>()
    .Bind(builder.Configuration.GetSection("Jwt"))
    .ValidateDataAnnotations()
    .ValidateOnStart();

builder.Services.AddDbContext<AppDbContext>(options =>
    options.UseNpgsql(builder.Configuration.GetConnectionString("DefaultConnection")));
```

## 5. Qachon ishlatish kerak?

| Vaziyat | Yechim |
|---|---|
| Umumiy, muhitdan qat'i nazar bir xil sozlama | `appsettings.json` |
| Muhitga xos sozlama | `appsettings.{Environment}.json` |
| Local dev, maxfiy ma'lumot | User Secrets |
| Production, maxfiy ma'lumot | Environment Variables/Key Vault |
| Strongly-typed, DI orqali kirish | `IOptions<T>` |

## 6. Muhim nuqtalar

- Configuration hierarchiyasi — **oxirgi qo'shilgan manba** g'olib
  chiqadi (Command-line — eng kuchli).
- `ValidateOnStart()` — noto'g'ri konfiguratsiyani **deploy vaqtida**
  aniqlash imkonini beradi, runtime'da emas.
- Nested kalitlar — Environment Variable'da `__` (ikki pastki chiziq)
  orqali ifodalanadi.

## 7. Imtihon savollari

1. Configuration manbalarining ustuvorlik tartibini ayting.
2. `IOptions<T>`, `IOptionsSnapshot<T>`, `IOptionsMonitor<T>`
   orasidagi farq nima?
3. User Secrets qayerda saqlanadi va u nima uchun xavfsizroq?
4. Nested konfiguratsiya kalit Environment Variable'da qanday
   ifodalanadi?
5. `ValidateOnStart()` qanday muammoni oldini oladi?
6. appsettings.json'da nima saqlanmasligi kerak?
