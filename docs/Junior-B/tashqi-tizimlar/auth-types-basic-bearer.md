# Auth Types — Basic, Bearer (Tashqi Tizimlar) — Junior B

## 1. What (Nima?)

**Basic Auth** — HTTP SO'ROVIDA, **FOYDALANUVCHI NOMI VA
PAROLNI, Base64 KODLANGAN HOLDA, HAR SO'ROVDA QAYTA
YUBORISH** ORQALI AUTENTIFIKATSIYA QILISH USULI. **Bearer
Auth** — HTTP SO'ROVIDA, **OLDINDAN OLINGAN, VAQTINCHALIK
TOKEN** (masalan JWT) NI YUBORISH ORQALI AUTENTIFIKATSIYA
QILISH USULI. Ikkisi HAM, `Authorization` HTTP SARLAVHASI
(header) ORQALI UZATILADI, LEKIN **XAVFSIZLIK MODELI VA
ISHLATILISH STSENARIYSI TUBDAN FARQ QILADI**.

## 2. Real hayot analogiyasi

**Basic Auth — HAR SAFAR, ESHIKDAN KIRISHDA, PASPORT VA
PAROLNI QAYTA-QAYTA KO'RSATISH.** Har GAL BINOGA KIRMOQCHI
BO'LGANINGIZDA — QO'RIQCHIGA, TO'LIQ PASPORT VA PAROLNI
(login/parol) KO'RSATASIZ. **Bearer Auth — MEHMONXONA
KALIT-KARTASI.** Siz, BIR MARTA, RESEPSHNDA (login endpoint)
RO'YXATDAN O'TASIZ, VA SIZGA, **VAQTINCHALIK KALIT-KARTA**
(TOKEN) BERILADI — SHUNDAN KEYIN, XONALARGA (himoyalangan
resurslarga) KIRISH UCHUN, FAQAT KARTANI KO'RSATASIZ,
PASPORT/PAROLNI QAYTA KO'RSATISH SHART EMAS.

## 3. Why (Nega kerak?)

Basic Auth — **SODDA, TEZKOR SOZLASH** UCHUN QULAY (masalan,
IKKI ICHKI XIZMAT ORASIDAGI SERVER-TO-SERVER MULOQOT), LEKIN
**HAR SO'ROVDA HAQIQIY PAROLNI YUBORISH** — XAVFLI (PAROL
OQIB KETSA, DOIMIY XAVF TUG'DIRADI, VA PAROLNI "EKSPIR
QILISH" YOKI "BEKOR QILISH" QIYIN). Bearer/JWT — **TOKENNI
VAQTINCHALIK, MUDDATI TUGAYDIGAN (expiry) QILIB, VA HAQIQIY
PAROLNI ALOHIDA, FAQAT BIR MARTA (login vaqtida) YUBORISH**
ORQALI, XAVFSIZLIKNI SEZILARLI OSHIRADI — bu, ZAMONAVIY
WEB API/MICROSERVICE ARXITEKTURASIDA STANDART TANLOV.

## 4. Internals (Ichki mexanizm)

### Basic Auth — HEADER FORMATI VA Base64 (ENCODING, ENCRYPTION EMAS!)

```
Authorization: Basic YWxpQG1haWwuY29tOnNlY3JldDEyMw==
```

```
"YWxpQG1haWwuY29tOnNlY3JldDEyMw==" — bu, "ali@mail.com:
secret123" MATNINI, Base64 ORQALI KODLASH NATIJASI. MUHIM:
Base64 — **SHIFRLASH (encryption) EMAS, SHUNCHAKI KODLASH
(encoding)** — HAR QANDAY KISHI, BU MATNNI, BIR NECHA
SONIYADA, ISTALGAN ONLINE Base64 DEKODER ORQALI, ASL
LOGIN/PAROLGA QAYTARIB O'QIY OLADI. Shuning uchun, Basic Auth
— **FAQAT HTTPS (TLS) BILAN BIRGA** ISHLATILISHI SHART (aks
holda, TARMOQDA "TINGLAB TURUVCHI" — PAROLNI OSON O'QIB
OLADI).
```

### Bearer/JWT Auth — HEADER FORMATI

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.SflKxw...
```

```
"Bearer" — BU, TOKEN TURINI KO'RSATUVCHI SO'Z (RFC 6750
STANDARTI). TOKEN O'ZI (masalan JWT) — ODATDA UCH QISMDAN
IBORAT (Header.Payload.Signature) — SERVER, HAR SO'ROVDA,
TOKENNING IMZOSINI (Signature) TEKSHIRIB, UNING
O'ZGARTIRILMAGANLIGINI VA MUDDATI TUGAMAGANLIGINI (exp
claim) TASDIQLAYDI — BU JARAYON, docs/Middle-D bo'limidagi
JWT hujjatlarida BATAFSIL YORITILGAN.
```

### Basic Auth — HAR SO'ROVDA, SERVER TOMONIDA QAYTA TEKSHIRUV

```
Basic Auth'da, SERVER, HAR BIR SO'ROVDA, YUBORILGAN LOGIN/
PAROLNI, DB'DAGI (yoki BOSHQA MANBADAGI) HAQIQIY QIYMAT
BILAN, QAYTA-QAYTA SOLISHTIRISHI (odatda HASH SOLISHTIRISH)
KERAK — bu, HAR SO'ROVDA, QO'SHIMCHA DB/HASH HISOBLASH
XARAJATINI TALAB QILADI. Bearer/JWT'da — TOKEN, O'ZI ICHIDA,
"IMZOLANGAN" MA'LUMOTGA EGA — SERVER, DB'GA MUROJAAT
QILMASDAN, FAQAT KRIPTOGRAFIK IMZONI TEKSHIRISH ORQALI,
TOKENNING HAQIQIYLIGINI TASDIQLASHI MUMKIN (STATELESS
TEKSHIRUV) — BU, CPU/DB YUKINI SEZILARLI KAMAYTIRADI.
```

## 5. Code (Amaliy kod)

```csharp
// Basic Auth — Custom AuthenticationHandler (ASP.NET Core)
public class BasicAuthenticationHandler : AuthenticationHandler<AuthenticationSchemeOptions>
{
    public BasicAuthenticationHandler(IOptionsMonitor<AuthenticationSchemeOptions> options,
        ILoggerFactory logger, UrlEncoder encoder) : base(options, logger, encoder) { }

    protected override Task<AuthenticateResult> HandleAuthenticateAsync()
    {
        if (!Request.Headers.ContainsKey("Authorization"))
            return Task.FromResult(AuthenticateResult.Fail("Authorization header yo'q"));

        var authHeader = Request.Headers["Authorization"].ToString();
        if (!authHeader.StartsWith("Basic ")) 
            return Task.FromResult(AuthenticateResult.Fail("Basic auth kutilgan edi"));

        var encodedCredentials = authHeader.Substring("Basic ".Length).Trim();
        var decodedBytes = Convert.FromBase64String(encodedCredentials); // ⚡ Encoding, encryption emas!
        var credentials = Encoding.UTF8.GetString(decodedBytes).Split(':', 2);

        var username = credentials[0];
        var password = credentials[1];

        // TODO: username/password'ni, HAQIQIY manba (DB) bilan tekshirish
        if (username == "admin" && password == "secret123")
        {
            var claims = new[] { new Claim(ClaimTypes.Name, username) };
            var identity = new ClaimsIdentity(claims, Scheme.Name);
            var ticket = new AuthenticationTicket(new ClaimsPrincipal(identity), Scheme.Name);
            return Task.FromResult(AuthenticateResult.Success(ticket));
        }

        return Task.FromResult(AuthenticateResult.Fail("Login yoki parol noto'g'ri"));
    }
}
```

```csharp
// Bearer/JWT Auth — ASP.NET Core built-in middleware orqali sozlash
builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddJwtBearer(options =>
    {
        options.TokenValidationParameters = new TokenValidationParameters
        {
            ValidateIssuerSigningKey = true,
            IssuerSigningKey = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(jwtSecret)),
            ValidateIssuer = true,
            ValidIssuer = "myapp",
            ValidateAudience = false,
            ValidateLifetime = true // ⚡ exp claim'ni avtomatik tekshiradi
        };
    });
```

```csharp
// Client tomonidan — har xil auth turlarini yuborish
using var client = new HttpClient();

// Basic Auth
var credentials = Convert.ToBase64String(Encoding.UTF8.GetBytes("ali@mail.com:secret123"));
client.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Basic", credentials);

// Bearer Auth
client.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", jwtToken);
```

## 6. Keng tarqalgan xatolar / noto'g'ri tushunchalar

```
❌ "Base64 kodlash — bu, ma'lumotni SHIFRLASH (encryption)"
   — YO'Q! Base64 — SHUNCHAKI KODLASH — HAR QANDAY KISHI,
   BIR NECHA SONIYADA, ASL MATNGA QAYTARIB O'QIY OLADI —
   Basic Auth, HTTPS'SIZ, JIDDIY XAVFSIZ EMAS.

❌ "Basic Auth — ESKIRGAN, HECH QACHON ISHLATILMASLIGI
   KERAK" — TO'LIQ TO'G'RI EMAS! Basic Auth — SODDALIGI
   TUFAYLI, HALI HAM, ICHKI, XAVFSIZ TARMOQDAGI SERVER-TO-
   SERVER MULOQOTDA, YOKI CI/CD TIZIMLARIDA (masalan, package
   registry'ga kirish uchun) KENG ISHLATILADI.

❌ "Bearer token — DOIM JWT'ni ANGLATADI" — YO'Q! "Bearer" —
   FAQAT, "TOKEN OLIB YURUVCHI HAR KIM, RESURSGA KIRA OLADI"
   DEGAN, UMUMIY SXEMA NOMI — TOKEN, JWT BO'LISHI HAM MUMKIN,
   YOKI OPAQUE TOKEN (server tomonda saqlanadigan, tasodifiy
   satr) BO'LISHI HAM MUMKIN.

❌ "Bearer token — hech qachon BEKOR QILIB (revoke)
   BO'LMAYDI, chunki U — STATELESS" — QISMAN TO'G'RI, LEKIN
   YECHIM MAVJUD: SERVER TOMONIDA, "BLACKLIST" (bekor
   qilingan tokenlar ro'yxati) SAQLASH, YOKI QISQA MUDDATLI
   ACCESS TOKEN + REFRESH TOKEN PATTERNI ISHLATISH ORQALI,
   BU MUAMMONI YUMSHATISH MUMKIN.
```

## 7. Exam (Interview savollari)

**1. Basic Auth va Bearer Auth orasidagi ASOSIY FARQ nima?**
Basic Auth — HAR SO'ROVDA, LOGIN/PAROLNI, Base64 KODLANGAN
HOLDA QAYTA YUBORADI. Bearer Auth — OLDINDAN OLINGAN,
VAQTINCHALIK TOKENNI (masalan JWT) YUBORADI, HAQIQIY PAROL —
FAQAT BIR MARTA (login vaqtida) YUBORILADI.

**2. Base64 kodlash, NIMA UCHUN, O'ZI ALOHIDA, XAVFSIZLIK
CHORASI HISOBLANMAYDI?**
Chunki Base64 — SHIFRLASH EMAS, SHUNCHAKI KODLASH — HAR
QANDAY KISHI, ONLINE DEKODER ORQALI, BIR NECHA SONIYADA, ASL
MATNGA QAYTARIB O'QIY OLADI. Basic Auth, XAVFSIZ BO'LISHI
UCHUN, HAR DOIM, HTTPS (TLS) BILAN BIRGA ISHLATILISHI SHART.

**3. Bearer/JWT Auth, Basic Auth'ga NISBATAN, SERVER
DARAJASIDA, QANDAY PERFORMANCE AFZALLIKKA EGA?**
JWT — O'ZI ICHIDA, "IMZOLANGAN" MA'LUMOTGA EGA — SERVER, HAR
SO'ROVDA, DB'GA MUROJAAT QILMASDAN, FAQAT KRIPTOGRAFIK
IMZONI TEKSHIRISH ORQALI, TOKENNING HAQIQIYLIGINI
TASDIQLASHI MUMKIN (STATELESS) — Basic Auth ESA, HAR
SO'ROVDA, DB/HASH SOLISHTIRISHNI TALAB QILADI.

**4. "Bearer" so'zi, HTTP `Authorization` sarlavhasida,
NIMANI ANGLATADI, va u DOIM JWT'ni BILDIRADIMI?**
"Bearer" — RFC 6750 STANDARTIGA MOS, "TOKEN OLIB YURUVCHI
HAR KIM, RESURSGA KIRA OLADI" DEGAN UMUMIY SXEMA NOMI. U,
JWT'ni HAM, YOKI SERVER TOMONDA SAQLANADIGAN "OPAQUE" (shaklsiz,
tasodifiy) TOKENNI HAM ANGLATISHI MUMKIN.

**5. Bearer/JWT Token'ni "BEKOR QILISH" (revoke) NIMA UCHUN
QIYIN MUAMMO, va uni QANDAY YUMSHATISH MUMKIN?**
JWT — STATELESS (server, tokenni "eslab qolmaydi", faqat
imzoni tekshiradi) BO'LGANI UCHUN, SERVER, "BU TOKEN ENDI
YAROQSIZ" DEB, DARHOL E'LON QILA OLMAYDI (MUDDATI TUGAMAGUNCHA).
Yechim — QISQA MUDDATLI ACCESS TOKEN (masalan 15 daqiqa) +
UZOQROQ MUDDATLI, SERVER TOMONIDA KUZATILADIGAN REFRESH
TOKEN, YOKI BLACKLIST (bekor qilingan tokenlar ro'yxati)
MEXANIZMI ISHLATISH.
