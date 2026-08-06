# API Key Authentication — Junior A

## 1. Nima? (Ta'rif)

**API Key** — service-to-service (yoki oddiy client-server)
autentifikatsiya uchun ishlatiladigan **oddiy, statik token** —
JWT'dan farqli, **structure/claims**ga ega emas, faqat **noyob
satr**.

## 2. Nima uchun kerak?

Webhook, tashqi integratsiya (masalan hamkor tizim ERP'ga
ma'lumot yuboradi) — bu holatlarda to'liq OAuth/JWT oqimi **ortiqcha
murakkab**. API Key — **oddiy, tez sozlanadigan** himoya usuli.

## 3. Ichida nima sodir bo'ladi? (Mexanizm)

### 3.1 JWT'dan farqi

```
JWT:                              API Key:
Stateless (o'z ichida claims)      Stateless YOKI DB'da SAQLANADI
Muddati BOR (exp claim)             ODATDA muddatsiz (yoki QO'LDA belgilanadi)
Bekor qilish QIYIN (stateless)      Bekor qilish OSON (DB'dan O'CHIRISH yetarli)
Foydalanuvchi identiteti (claims)   ODATDA faqat "kim" (service nomi)
```

### 3.2 API Key qayerda yuboriladi

```
Header (TAVSIYA ETILADI):
  X-Api-Key: abc123def456

Query string (KAMROQ xavfsiz — URL log'larda ko'rinishi mumkin):
  GET /api/data?api_key=abc123

Request body (kamdan-kam, faqat POST so'rovlarda):
  { "apiKey": "abc123", "data": {...} }
```

### 3.3 ASP.NET Core'da implementatsiya — Custom AuthenticationHandler

```csharp
public class ApiKeyAuthenticationHandler : AuthenticationHandler<AuthenticationSchemeOptions>
{
    private readonly IApiKeyValidator _validator;

    public ApiKeyAuthenticationHandler(
        IOptionsMonitor<AuthenticationSchemeOptions> options, ILoggerFactory logger,
        UrlEncoder encoder, IApiKeyValidator validator) : base(options, logger, encoder)
        => _validator = validator;

    protected override async Task<AuthenticateResult> HandleAuthenticateAsync()
    {
        if (!Request.Headers.TryGetValue("X-Api-Key", out var apiKeyHeader))
            return AuthenticateResult.Fail("API Key topilmadi");

        var apiKey = apiKeyHeader.ToString();
        var client = await _validator.ValidateAsync(apiKey);
        if (client is null)
            return AuthenticateResult.Fail("API Key yaroqsiz");

        var claims = new[] { new Claim(ClaimTypes.Name, client.Name), new Claim("scope", client.Scope) };
        var identity = new ClaimsIdentity(claims, "ApiKey");
        var principal = new ClaimsPrincipal(identity);
        var ticket = new AuthenticationTicket(principal, "ApiKey");

        return AuthenticateResult.Success(ticket);
    }
}

// Program.cs
builder.Services.AddAuthentication("ApiKey")
    .AddScheme<AuthenticationSchemeOptions, ApiKeyAuthenticationHandler>("ApiKey", null);
```

### 3.4 `IApiKeyValidator` service

```csharp
public interface IApiKeyValidator { Task<ApiClient?> ValidateAsync(string apiKey); }

public class ApiKeyValidator : IApiKeyValidator
{
    private readonly AppDbContext _context;
    public async Task<ApiClient?> ValidateAsync(string apiKey)
    {
        var hash = ComputeHash(apiKey); // API Key'ni HASH qilib SAQLASH (parol kabi)
        return await _context.ApiClients
            .FirstOrDefaultAsync(c => c.KeyHash == hash && c.IsActive && c.ExpiresAt > DateTime.UtcNow);
    }
}
```

```
⚠️ API Key'ni DB'da PLAIN TEXT saqlash — XAVFLI! Parol kabi —
   HASH qilib saqlash TAVSIYA ETILADI (SHA256 yetarli, chunki
   API Key — ODATDA TASODIFIY, uzun, brute-force'ga CHIDAMLI
   generatsiya qilinadi — BCrypt SHART EMAS, lekin ZARARSIZ ham).
```

### 3.5 appsettings'da API Key saqlash (xavfli)

```json
// ❌ appsettings.json'da API Key saqlash — DB'DA saqlashdan KO'RA
//    KAM MOSLASHUVCHAN (rotation, revocation QIYIN)
{ "ApiKeys": { "PartnerX": "hardcoded-key-123" } }
```

```
✅ TAVSIYA: DB'da saqlash — MUNTAZAM ROTATSIYA, ALOHIDA client
   uchun ALOHIDA key, VAQTINCHA/DOIMIY BEKOR QILISH imkoniyati bilan.
```

### 3.6 API Key xavfsizligi

```
✅ HTTPS MAJBURIY — API Key ochiq HTTP orqali yuborilsa, TARMOQDA
   O'QILISHI mumkin
✅ Rate Limiting — bitta API Key uchun so'rov SONI cheklash
✅ Scope — API Key FAQAT MA'LUM endpointlarga RUXSAT beradi
   (masalan "faqat /webhook uchun", "/employees uchun EMAS")
✅ Expiry — muddatli API Key (masalan 1 yil), keyin YANGILASH kerak
✅ Rotation — eski Key'ni ASTA-SEKIN (grace period bilan) ALMASHTIRISH
```

### 3.7 API Key vs JWT — qachon qaysi

```
API Key:
  ✅ Service-to-service, oddiy webhook
  ✅ Tashqi hamkor integratsiyasi (murakkab OAuth SETUP shart emas)
  ❌ Foydalanuvchi identiteti (kim, qanday rol) — YO'Q

JWT:
  ✅ Foydalanuvchi autentifikatsiyasi, rol/huquq claims'lar bilan
  ✅ Microservices, stateless, QISQA muddatli
  ❌ Oddiy service-to-service uchun — ORTIQCHA MURAKKAB bo'lishi mumkin
```

## 4. Kod — real misol: webhook, third-party integration

```csharp
[ApiController]
[Route("api/webhooks")]
[Authorize(AuthenticationSchemes = "ApiKey")]
public class WebhookController : ControllerBase
{
    [HttpPost("payment-notification")]
    public async Task<IActionResult> HandlePaymentNotification(PaymentNotificationDto dto)
    {
        // Faqat TO'G'RI API Key BILAN kelgan so'rov shu YERGA yetib keladi
        await _paymentService.ProcessNotificationAsync(dto);
        return Ok();
    }
}
```

## 5. Qachon ishlatish kerak?

| Vaziyat | Yechim |
|---|---|
| Tashqi hamkor webhook yuboradi | API Key |
| Service-to-service, ichki microservice | API Key yoki mTLS |
| Foydalanuvchi login qiladi | JWT |
| Enterprise SSO | OAuth2/OIDC |

## 6. Muhim nuqtalar

- API Key — DB'da **hash** qilib saqlanishi tavsiya etiladi (parol
  kabi).
- Query string orqali API Key yuborish — **URL log'lariga** tushib
  qolishi mumkin, Header afzal.
- Rotation strategiyasi — kalitni **birdaniga** emas, **grace
  period** bilan almashtirish (eski + yangi bir muddat ISHLASHI).

## 7. Imtihon savollari

1. API Key va JWT orasidagi asosiy farq nima?
2. API Key qayerda yuborilishi mumkin va qaysi usul xavfsizroq?
3. API Key'ni DB'da qanday saqlash tavsiya etiladi?
4. API Key uchun "scope" tushunchasi nima uchun kerak?
5. Credential Rotation nima va u API Key kontekstida qanday
   amalga oshiriladi?
6. Qachon API Key, qachon JWT tanlanadi?
