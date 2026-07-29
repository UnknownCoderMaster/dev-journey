# Options Pattern — ASP.NET Core — Middle D

## 1. Nima? (Ta'rif)

**Options Pattern** — `appsettings.json` konfiguratsiyasini
**strongly-typed** (kuchli tiplangan) C# klass sifatida DI orqali
olish mexanizmi. Uchta asosiy interfeys: `IOptions<T>`,
`IOptionsSnapshot<T>`, `IOptionsMonitor<T>`.

## 2. Nima uchun kerak?

`IConfiguration["Jwt:SecretKey"]` kabi **"sehrli string"** orqali
konfiguratsiya olish — **compile-time xavfsiz emas** (typo bo'lsa
ham compiler seskin bermaydi, runtime'da `null` qaytadi). Options
Pattern — konfiguratsiyani **C# klassga** bog'lab, IntelliSense va
compile-time tekshiruv imkonini beradi.

## 3. Ichida nima sodir bo'ladi? (Mexanizm)

### 3.1 `IOptions<T>` — Singleton, faqat Startup'da o'qiladi

```csharp
public class JwtSettings
{
    public string Issuer { get; set; } = null!;
    public string SecretKey { get; set; } = null!;
    public int AccessTokenExpirationMinutes { get; set; }
}

builder.Services.Configure<JwtSettings>(builder.Configuration.GetSection("Jwt"));

public class TokenService
{
    private readonly JwtSettings _settings;
    public TokenService(IOptions<JwtSettings> options) => _settings = options.Value; // .Value — BIR MARTA olinadi
}
```

```
IOptions<T> — Singleton sifatida ro'yxatdan o'tadi, qiymat ILOVA
ISHGA TUSHGANDA BIR MARTA o'qiladi. appsettings.json RUNTIME'DA
o'zgarsa ham — IOptions<T>.Value ESKI qiymatni QAYTARIB TURAVERADI
(ilova QAYTA ISHGA TUSHMAGUNCHA).
```

### 3.2 `IOptionsSnapshot<T>` — Scoped, har so'rovda yangilanadi

```csharp
public class EmailService
{
    private readonly EmailSettings _settings;
    public EmailService(IOptionsSnapshot<EmailSettings> options) => _settings = options.Value;
}
```

```
IOptionsSnapshot<T> — Scoped, HAR HTTP SO'ROV boshida QAYTA
HISOBLANADI (agar konfiguratsiya fayli o'zgargan bo'lsa — YANGI
qiymat KEYINGI so'rovda KO'RINADI, lekin BITTA so'rov davomida
O'ZGARMAYDI).
```

### 3.3 `IOptionsMonitor<T>` — Singleton, runtime'da yangilanadi

```csharp
public class FeatureFlagService
{
    private readonly IOptionsMonitor<FeatureFlags> _monitor;

    public FeatureFlagService(IOptionsMonitor<FeatureFlags> monitor)
    {
        _monitor = monitor;
        _monitor.OnChange(newFlags => Console.WriteLine("Sozlamalar o'zgardi!"));
    }

    public bool IsEnabled(string flag) => _monitor.CurrentValue.Flags.Contains(flag);
}
```

```
IOptionsMonitor<T> — Singleton, LEKIN har chaqiruvda
`.CurrentValue` — ENG YANGI qiymatni qaytaradi (fayl o'zgarsa —
DARHOL, hech kutmasdan). `.OnChange()` — o'zgarish yuz berganda
CALLBACK chaqirish imkonini beradi.
```

### 3.4 Solishtirish jadvali

| | `IOptions<T>` | `IOptionsSnapshot<T>` | `IOptionsMonitor<T>` |
|---|---|---|---|
| Lifetime | Singleton | Scoped | Singleton |
| Qachon o'qiladi | Ilova start'da (1 marta) | Har so'rov boshida | Har chaqiruvda (eng yangi) |
| BackgroundService'da ishlatish | ✅ | ❌ (Scoped, mos emas) | ✅ |
| Runtime o'zgarishni kuzatish | ❌ | Qisman (so'rovlar orasida) | ✅ To'liq (`OnChange`) |

### 3.5 Nested konfiguratsiya

```json
{
  "Email": {
    "Smtp": { "Host": "smtp.gmail.com", "Port": 587 },
    "SenderName": "ERP System"
  }
}
```

```csharp
public class EmailSettings
{
    public SmtpSettings Smtp { get; set; } = null!;
    public string SenderName { get; set; } = null!;
}
public class SmtpSettings
{
    public string Host { get; set; } = null!;
    public int Port { get; set; }
}
```

### 3.6 Validatsiya — `ValidateDataAnnotations`, `ValidateOnStart`

```csharp
public class JwtSettings
{
    [Required] public string SecretKey { get; set; } = null!;
    [Range(1, 60)] public int AccessTokenExpirationMinutes { get; set; }
}

builder.Services.AddOptions<JwtSettings>()
    .Bind(builder.Configuration.GetSection("Jwt"))
    .ValidateDataAnnotations()
    .ValidateOnStart(); // ✅ Ilova ISHGA TUSHISHDA DARHOL tekshiradi (noto'g'ri konfiguratsiya bilan ISHGA TUSHMAYDI)
```

```
⚠️ ValidateOnStart() BO'LMASA — noto'g'ri konfiguratsiya (masalan
   SecretKey bo'sh) FAQAT o'sha qiymat ISHLATILGANDA (masalan
   birinchi login so'rovida) ANIQLANADI — bu PRODUCTION'da
   "kutilmagan" vaqt xatosiga olib kelishi mumkin.

✅ ValidateOnStart() BILAN — ilova UMUMAN ISHGA TUSHMAYDI, agar
   konfiguratsiya NOTO'G'RI bo'lsa — muammo DARHOL, deploy vaqtida
   aniqlanadi.
```

### 3.7 Named Options

```csharp
builder.Services.Configure<SmtpSettings>("Primary", builder.Configuration.GetSection("Smtp:Primary"));
builder.Services.Configure<SmtpSettings>("Backup", builder.Configuration.GetSection("Smtp:Backup"));

public class EmailService
{
    public EmailService(IOptionsFactory<SmtpSettings> factory)
    {
        var primary = factory.Create("Primary");
        var backup = factory.Create("Backup");
    }
}
```

### 3.8 `PostConfigure` — override qilish

```csharp
builder.Services.PostConfigure<JwtSettings>(settings =>
{
    // BARCHA boshqa Configure() chaqiruvlaridan KEYIN, YAKUNIY o'zgartirish
    settings.Issuer = Environment.GetEnvironmentVariable("JWT_ISSUER") ?? settings.Issuer;
});
```

## 4. Kod — to'liq misol

```csharp
builder.Services.AddOptions<JwtSettings>()
    .Bind(builder.Configuration.GetSection("Jwt"))
    .ValidateDataAnnotations()
    .ValidateOnStart();

public class AuthService
{
    private readonly JwtSettings _jwtSettings;
    public AuthService(IOptions<JwtSettings> options) => _jwtSettings = options.Value;
}
```

## 5. Qachon ishlatish kerak?

| Vaziyat | Yechim |
|---|---|
| Oddiy, o'zgarmaydigan sozlama (masalan JWT) | `IOptions<T>` |
| Har so'rovda YANGILANISHI mumkin bo'lgan sozlama | `IOptionsSnapshot<T>` |
| BackgroundService/Singleton'da RUNTIME o'zgarishni kuzatish | `IOptionsMonitor<T>` |
| Kritik sozlama, noto'g'ri bo'lsa ilova ISHGA TUSHMASIN | `ValidateOnStart()` |

## 6. Muhim nuqtalar

- `IOptionsSnapshot<T>` — Scoped bo'lgani uchun **Singleton
  servisga** inject qilib bo'lmaydi (DI lifetime mismatch xatosi).
- `ValidateOnStart()` — production'da **kritik** konfiguratsiya
  (masalan connection string, secret key) uchun har doim ishlatilishi
  tavsiya etiladi.
- "Sehrli string" (`IConfiguration["Jwt:SecretKey"]`) o'rniga Options
  Pattern — kod bazasi kattalashgan sari SEZILARLI foyda beradi.

## 7. Imtihon savollari

1. `IOptions<T>`, `IOptionsSnapshot<T>` va `IOptionsMonitor<T>`
   orasidagi lifetime farqini tushuntiring.
2. `IOptionsSnapshot<T>`ni Singleton servisga inject qilishga
   urinilsa nima sodir bo'ladi va nima uchun?
3. `ValidateOnStart()` qanday muammoni oldini oladi?
4. `IOptionsMonitor<T>.OnChange()` qachon foydali bo'ladi?
5. Named Options nima va u qachon kerak bo'ladi?
