# JWT-ga asoslangan Autentifikatsiya — ASP.NET Core — Middle D

## 1. Nima? (Ta'rif)

**JWT (JSON Web Token)** — foydalanuvchi haqidagi ma'lumotni (claims)
xavfsiz tarzda, **raqamli imzo** bilan tasdiqlangan holda, taraflar
orasida uzatish uchun ochiq standart (**RFC 7519**). JWT — bu
**self-contained** (o'z-o'zini tasdiqlovchi) token: serverga har
so'rovda DB'ga murojaat qilmasdan, tokenning o'zidan foydalanuvchi
ekanligini va uning huquqlarini bilib olish mumkin.

**Asosiy tushunchalar:**
- **Claim** — foydalanuvchi haqidagi bitta "da'vo" (key-value juft):
  `sub: "123"`, `role: "Admin"`
- **Access Token** — API'ga kirish uchun ishlatiladigan, **qisqa
  muddatli** JWT
- **Refresh Token** — Access Token muddati tugaganda, yangisini
  olish uchun ishlatiladigan, **uzoq muddatli** token
- **Bearer Token** — "kim ushlab tursa — shu egasi" tamoyili bilan
  ishlaydigan token turi (`Authorization: Bearer <token>`)

## 2. Nima uchun kerak? (Muammo va yechim)

An'anaviy **Session-based** autentifikatsiyada — server har
foydalanuvchi uchun **session ID**ni xotirada (yoki DB'da) saqlaydi,
va client cookie orqali shu ID'ni yuboradi. Bu **stateful** (holatli)
yondashuv — muammosi:

```
❌ Session bilan (stateful):
   Load Balancer ortida 3 ta server bo'lsa — foydalanuvchi Server-1 da
   login qilgan bo'lsa, keyingi so'rov Server-2 ga tushib qolsa —
   Server-2 bu session'ni BILMAYDI! (agar sticky session yoki shared
   session store bo'lmasa)

✅ JWT bilan (stateless):
   Token o'zida barcha kerakli ma'lumotni olib yuradi — QAYSI server
   qabul qilsa ham, tokenni imzo orqali TEKSHIRIB, ICHIDAGI claims'ni
   O'QIY OLADI. DB yoki shared session store SHART EMAS.
```

**Real hayot analogiyasi:** Session — bu **mehmonxona kaliti** (faqat
mehmonxonaning o'zi bu kalit kimga tegishli ekanini biladi, tashqarida
hech kim tekshira olmaydi). JWT — bu **imzolangan pasport**: istalgan
chegara nazorati (server) uni ko'rib, hukumat (Issuer) imzosini
tekshirib, egasi kim ekanini **mustaqil** bila oladi — hech kimga
qo'ng'iroq qilish shart emas.

Agar JWT bo'lmaganida — microservice arxitekturada har bir servis
har so'rovda Auth-service'ga "bu token to'g'rimi?" deb so'rashga
majbur bo'lardi — bu qo'shimcha tarmoq so'rovi va tezlik yo'qotishi.

## 3. Ichida nima sodir bo'ladi? (Mexanizm)

### 3.1 JWT tuzilishi — 3 qism

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9
.
eyJzdWIiOiIxMjMiLCJuYW1lIjoiT3J6aWJlayIsImV4cCI6MTcwMDAwMDAwMH0
.
SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c

└────────── HEADER ──────────┘.└──────────── PAYLOAD ────────────┘.└──── SIGNATURE ────┘
```

Har bir qism **Base64Url** bilan encode qilingan (oddiy Base64 dan
farqli — `+`, `/` o'rniga `-`, `_` ishlatadi, URL'da xavfsiz
bo'lishi uchun, `=` padding olib tashlanadi).

**Header** — algoritm va token turi:
```json
{ "alg": "HS256", "typ": "JWT" }
```

**Payload** — claims (foydalanuvchi ma'lumotlari):
```json
{
  "sub": "123",           // Subject — foydalanuvchi ID
  "name": "Orzibek",
  "role": "Admin",
  "iat": 1700000000,      // Issued At — yaratilgan vaqt (Unix timestamp)
  "exp": 1700003600,      // Expiration — muddati tugash vaqti
  "iss": "https://erp.example.com",  // Issuer — kim chiqargan
  "aud": "erp-api"        // Audience — kim uchun mo'ljallangan
}
```

**Signature** — Header va Payload'ning **o'zgartirilmaganligini**
tasdiqlash uchun:
```
HMACSHA256(
    base64UrlEncode(header) + "." + base64UrlEncode(payload),
    secret_key
)
```

```
⚠️ MUHIM: Header va Payload — FAQAT encode qilingan, SHIFRLANMAGAN!
   Istalgan kishi ularni Base64 decode qilib O'QIY OLADI.
   Signature FAQAT "o'zgartirilmaganligini" kafolatlaydi,
   MAXFIYLIKNI (confidentiality) EMAS!

❌ XATO TASAVVUR: "JWT shifrlangan, hech kim ichini o'qiy olmaydi"
✅ TO'G'RI: JWT faqat IMZOLANGAN — parol, kredit karta raqami kabi
   maxfiy ma'lumotlarni payload'ga qo'shmaslik kerak!
```

### 3.2 Signature qanday yaratiladi — HMACSHA256 batafsil

```
1. header + "." + payload — bitta string sifatida birlashtiriladi
   (masalan: "eyJhbGc...eyJzdWI...")

2. Server o'zining MAXFIY kaliti (secret key) bilan HMAC-SHA256
   hash funksiyasini hisoblaydi:

   signature = HMAC-SHA256(header.payload, SECRET_KEY)

3. Bu signature Base64Url bilan encode qilinib, tokenning 3-qismi
   sifatida qo'shiladi
```

`HMAC` (Hash-based Message Authentication Code) — bu oddiy hash
(masalan SHA256) dan farqli, **maxfiy kalit** bilan birlashtirilgan
hash. Faqat kalitni bilgan taraf **to'g'ri** signature yasay oladi —
hatto kimdir header/payload'ni o'zgartirsa, signature mos kelmay
qoladi.

### 3.3 JWT qanday tekshiriladi — server tomonida bosqichma-bosqich

```
1. Client so'rov yuboradi: Authorization: Bearer <token>

2. Server tokenni "." bo'yicha 3 qismga ajratadi

3. Server O'ZINING SECRET KEY'i bilan header.payload'dan
   YANGI signature hisoblaydi

4. Yangi hisoblangan signature — token ichidagi signature bilan
   SOLISHTIRILADI:

   ┌─────────────────────┐        ┌──────────────────────┐
   │ Token'dagi signature │  ==?  │ Server hisoblagan     │
   └─────────────────────┘        │ signature              │
                                   └──────────────────────┘

   MOS KELSA → Token o'zgartirilmagan, ASL holida ✅
   MOS KELMASA → Token o'zgartirilgan yoki soxta ❌ (401 Unauthorized)

5. Signature to'g'ri bo'lsa — qo'shimcha tekshiruvlar:
   - exp (muddati tugamaganmi?)
   - nbf (not before — hali kuchga kirmaganmi?)
   - iss (kutilgan Issuer'danmi?)
   - aud (kutilgan Audience uchunmi?)

6. Barcha tekshiruvlar o'tsa — payload'dagi claims
   HttpContext.User (ClaimsPrincipal) ga o'rnatiladi
```

```
XAVFSIZLIK NUQTAI: Signature tekshiruvi — Base64 DECODE qilishdan
KEYIN emas, balki HAR SAFAR qayta HASH HISOBLASH orqali amalga
oshadi. Shuning uchun kimdir payload'dagi "role": "User" ni
"role": "Admin" ga qo'lda o'zgartirsa — signature MOS KELMAY QOLADI,
chunki server qayta hisoblagan hash boshqacha chiqadi.
```

### 3.4 Access Token va Refresh Token — nima uchun ikkalasi kerak?

```
Faqat Access Token (uzoq muddatli, masalan 7 kun) bilan ishlasa:
  ❌ Token o'g'irlansa — 7 kun davomida hujumchi TO'LIQ huquq bilan ishlaydi
  ❌ Foydalanuvchi huquqi (role) o'zgarsa — eski token hali ESKI
     huquq bilan 7 kun ishlayveradi (chunki server DB'ga qarab
     TEKSHIRMAYDI — bu JWT ning "stateless" xususiyati)

✅ Ikki tokenli strategiya:
   Access Token — QISQA muddatli (5-15 daqiqa)
     → O'g'irlansa ham, tez orada FOYDASIZ bo'lib qoladi
   Refresh Token — UZOQ muddatli (7-30 kun), FAQAT DB'da saqlanadi
     → Har safar YANGI Access Token olish uchun ishlatiladi
     → DB'da saqlangani uchun — SERVER XOHLAGAN VAQTDA BEKOR QILA OLADI
       (Access Token'dan farqli, uni "bekor qilib" bo'lmaydi — u
       stateless!)
```

```
Vaqt chizig'i:

t=0min    Login → Access Token (15 daqiqa) + Refresh Token (30 kun) beriladi
t=14min   API so'rovlar — Access Token bilan
t=15min   Access Token MUDDATI TUGADI (exp)
t=15min   Client: "/refresh" so'rov, Refresh Token yuboradi
t=15min   Server: Refresh Token DB'da bormi va bekor qilinmaganmi tekshiradi
t=15min   Server: YANGI Access Token (yana 15 daqiqa) qaytaradi
t=15-30min Davom etadi...
```

### 3.5 Claims — standart va custom

```
sub (Subject)     — foydalanuvchi noyob identifikatori
iat (Issued At)   — token qachon yaratilgani (Unix timestamp)
exp (Expiration)  — token qachon tugashi
nbf (Not Before)  — token qachongacha KUCHGA KIRMASLIGI
iss (Issuer)      — tokenni kim chiqargan (masalan Keycloak realm URL)
aud (Audience)    — token KIM UCHUN mo'ljallangan (masalan "erp-api")
jti (JWT ID)      — tokenning o'zi uchun noyob ID (revoke qilish uchun foydali)

Custom claims:
role              — foydalanuvchi roli
department_id     — ERP'da qaysi bo'limga tegishli
permissions       — aniq huquqlar ro'yxati
```

### 3.6 JWT vs Session — taqqoslash

| | JWT | Session |
|---|---|---|
| Holat (state) | Stateless — server hech narsa saqlamaydi | Stateful — server session store'da saqlaydi |
| Scalability | Oson — istalgan server tekshira oladi | Qiyinroq — sticky session yoki shared store kerak |
| Bekor qilish (revoke) | Qiyin (stateless bo'lgani uchun) | Oson — session'ni o'chirish kifoya |
| Hajmi | Kattaroq (har so'rovda to'liq token yuboriladi) | Kichik (faqat session ID) |
| Microservices uchun mos | ✅ Juda mos | ❌ Har servis uchun murakkab |
| Monolit uchun | Ishlaydi, lekin ortiqcha bo'lishi mumkin | ✅ Oddiy va yetarli |

## 4. Kod — to'liq implementatsiya

### NuGet paketlar

```bash
dotnet add package Microsoft.AspNetCore.Authentication.JwtBearer --version 8.0.0
dotnet add package System.IdentityModel.Tokens.Jwt --version 7.0.3
```

### appsettings.json

```json
{
  "Jwt": {
    "Issuer": "https://erp.example.com",
    "Audience": "erp-api",
    "SecretKey": "REPLACE_WITH_ENV_VARIABLE_NOT_HARDCODED",
    "AccessTokenExpirationMinutes": 15,
    "RefreshTokenExpirationDays": 30
  }
}
```

```
⚠️ SecretKey HECH QACHON appsettings.json ichida hardcode qilinmasin!
   Production'da: Environment Variable yoki Azure Key Vault / HashiCorp Vault
```

### Program.cs — AddAuthentication + AddJwtBearer

```csharp
var builder = WebApplication.CreateBuilder(args);

var jwtSettings = builder.Configuration.GetSection("Jwt");
var secretKey = Environment.GetEnvironmentVariable("JWT_SECRET_KEY")
    ?? jwtSettings["SecretKey"]!; // Fallback faqat local dev uchun

builder.Services.AddAuthentication(options =>
{
    options.DefaultAuthenticateScheme = JwtBearerDefaults.AuthenticationScheme;
    options.DefaultChallengeScheme = JwtBearerDefaults.AuthenticationScheme;
})
.AddJwtBearer(options =>
{
    options.TokenValidationParameters = new TokenValidationParameters
    {
        ValidateIssuer = true,
        ValidIssuer = jwtSettings["Issuer"],

        ValidateAudience = true,
        ValidAudience = jwtSettings["Audience"],

        ValidateIssuerSigningKey = true,
        IssuerSigningKey = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(secretKey)),

        ValidateLifetime = true,
        ClockSkew = TimeSpan.Zero // Default 5 daqiqa "tolerantlik"ni OLIB TASHLASH — aniqroq exp tekshiruvi
    };

    // Debugging uchun — production'da o'chirish kerak
    options.Events = new JwtBearerEvents
    {
        OnAuthenticationFailed = context =>
        {
            Console.WriteLine($"Auth failed: {context.Exception.Message}");
            return Task.CompletedTask;
        }
    };
});

builder.Services.AddAuthorization();

var app = builder.Build();

// ⚠️ TARTIB MUHIM: Authentication OLDIN, Authorization KEYIN!
app.UseAuthentication();
app.UseAuthorization();

app.MapControllers();
app.Run();
```

### `TokenValidationParameters` — barcha parametrlar

```csharp
new TokenValidationParameters
{
    ValidateIssuer = true,           // "iss" claim tekshirilsinmi?
    ValidIssuer = "...",              // Kutilgan issuer qiymati

    ValidateAudience = true,          // "aud" claim tekshirilsinmi?
    ValidAudience = "...",            // Kutilgan audience qiymati

    ValidateIssuerSigningKey = true,  // Signature kaliti tekshirilsinmi?
    IssuerSigningKey = securityKey,   // Signature tekshirish uchun kalit

    ValidateLifetime = true,          // "exp"/"nbf" tekshirilsinmi?
    ClockSkew = TimeSpan.Zero,        // Server soatlari orasidagi "tolerantlik" (default 5 daq)

    RequireExpirationTime = true,     // "exp" claim MAJBURIY bo'lsinmi?
    RequireSignedTokens = true        // Token IMZOLANGAN bo'lishi SHART
}
```

### Token yaratish — `JwtSecurityTokenHandler`

```csharp
public class TokenService : ITokenService
{
    private readonly IConfiguration _config;
    private readonly string _secretKey;

    public TokenService(IConfiguration config)
    {
        _config = config;
        _secretKey = Environment.GetEnvironmentVariable("JWT_SECRET_KEY")
            ?? config["Jwt:SecretKey"]!;
    }

    public string GenerateAccessToken(Employee user)
    {
        var claims = new List<Claim>
        {
            new(JwtRegisteredClaimNames.Sub, user.Id.ToString()),
            new(JwtRegisteredClaimNames.Jti, Guid.NewGuid().ToString()),
            new(ClaimTypes.Name, user.FullName),
            new(ClaimTypes.Role, user.Role),
            new("department_id", user.DepartmentId.ToString())
        };

        var key = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(_secretKey));
        var creds = new SigningCredentials(key, SecurityAlgorithms.HmacSha256);

        var token = new JwtSecurityToken(
            issuer: _config["Jwt:Issuer"],
            audience: _config["Jwt:Audience"],
            claims: claims,
            expires: DateTime.UtcNow.AddMinutes(
                double.Parse(_config["Jwt:AccessTokenExpirationMinutes"]!)),
            signingCredentials: creds
        );

        return new JwtSecurityTokenHandler().WriteToken(token);
    }

    public string GenerateRefreshToken()
    {
        var randomBytes = RandomNumberGenerator.GetBytes(64);
        return Convert.ToBase64String(randomBytes); // Kriptografik xavfsiz random
    }
}
```

### Refresh Token — DB entity va logika

```csharp
public class RefreshToken
{
    public int Id { get; set; }
    public string Token { get; set; } = null!;
    public int EmployeeId { get; set; }
    public DateTime ExpiresAt { get; set; }
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    public DateTime? RevokedAt { get; set; }  // NULL — hali amalda, qiymat bo'lsa — bekor qilingan
    public bool IsActive => RevokedAt is null && ExpiresAt > DateTime.UtcNow;
}
```

```csharp
[ApiController]
[Route("api/auth")]
public class AuthController : ControllerBase
{
    private readonly ITokenService _tokenService;
    private readonly AppDbContext _context;

    [HttpPost("login")]
    public async Task<IActionResult> Login(LoginDto dto)
    {
        var user = await _context.Employees
            .FirstOrDefaultAsync(e => e.Email == dto.Email);

        if (user is null || !VerifyPassword(dto.Password, user.PasswordHash))
            return Unauthorized(new { message = "Email yoki parol noto'g'ri" });

        var accessToken = _tokenService.GenerateAccessToken(user);
        var refreshTokenValue = _tokenService.GenerateRefreshToken();

        _context.RefreshTokens.Add(new RefreshToken
        {
            Token = refreshTokenValue,
            EmployeeId = user.Id,
            ExpiresAt = DateTime.UtcNow.AddDays(30)
        });
        await _context.SaveChangesAsync();

        // ✅ HttpOnly cookie — JavaScript orqali O'QIB BO'LMAYDI (XSS himoyasi)
        Response.Cookies.Append("refreshToken", refreshTokenValue, new CookieOptions
        {
            HttpOnly = true,
            Secure = true,       // Faqat HTTPS orqali yuboriladi
            SameSite = SameSiteMode.Strict, // CSRF himoyasi
            Expires = DateTimeOffset.UtcNow.AddDays(30)
        });

        return Ok(new { accessToken });
    }

    [HttpPost("refresh")]
    public async Task<IActionResult> Refresh()
    {
        var refreshTokenValue = Request.Cookies["refreshToken"];
        if (string.IsNullOrEmpty(refreshTokenValue))
            return Unauthorized();

        var storedToken = await _context.RefreshTokens
            .Include(rt => rt.Employee)
            .FirstOrDefaultAsync(rt => rt.Token == refreshTokenValue);

        if (storedToken is null || !storedToken.IsActive)
            return Unauthorized(new { message = "Refresh token yaroqsiz" });

        // Rotation — eski token bekor qilinadi, yangisi beriladi (xavfsizlik uchun)
        storedToken.RevokedAt = DateTime.UtcNow;

        var newAccessToken = _tokenService.GenerateAccessToken(storedToken.Employee);
        var newRefreshTokenValue = _tokenService.GenerateRefreshToken();

        _context.RefreshTokens.Add(new RefreshToken
        {
            Token = newRefreshTokenValue,
            EmployeeId = storedToken.EmployeeId,
            ExpiresAt = DateTime.UtcNow.AddDays(30)
        });
        await _context.SaveChangesAsync();

        Response.Cookies.Append("refreshToken", newRefreshTokenValue, new CookieOptions
        {
            HttpOnly = true, Secure = true, SameSite = SameSiteMode.Strict,
            Expires = DateTimeOffset.UtcNow.AddDays(30)
        });

        return Ok(new { accessToken = newAccessToken });
    }

    [HttpPost("logout")]
    [Authorize]
    public async Task<IActionResult> Logout()
    {
        var refreshTokenValue = Request.Cookies["refreshToken"];
        var storedToken = await _context.RefreshTokens
            .FirstOrDefaultAsync(rt => rt.Token == refreshTokenValue);

        if (storedToken is not null)
        {
            storedToken.RevokedAt = DateTime.UtcNow; // DB'da BEKOR QILINADI
            await _context.SaveChangesAsync();
        }

        Response.Cookies.Delete("refreshToken");
        return Ok();
    }
}
```

### `[Authorize]` va middleware tartibi

```csharp
// ⚠️ TARTIB MUHIM — noto'g'ri tartibda [Authorize] ISHLAMAYDI:
app.UseAuthentication();  // 1. "Kim ekanligini" aniqlaydi (token tekshiradi, User'ni o'rnatadi)
app.UseAuthorization();   // 2. "Nima qila olishini" tekshiradi ([Authorize] shu yerda ishlaydi)

// ❌ Teskari tartib — Authorization ishga tushganda User HALI aniqlanmagan!
app.UseAuthorization();
app.UseAuthentication(); // ❌ Juda kech!
```

```csharp
[ApiController]
[Route("api/employees")]
[Authorize] // Butun controller uchun — token SHART
public class EmployeesController : ControllerBase
{
    [HttpGet]
    [AllowAnonymous] // Bu action uchun ISTISNO — token SHART emas
    public IActionResult GetPublicList() => Ok(_publicData);

    [HttpGet("{id}")]
    public IActionResult GetById(int id)
    {
        var userId = User.FindFirst(JwtRegisteredClaimNames.Sub)?.Value;
        var role = User.FindFirst(ClaimTypes.Role)?.Value;
        return Ok(new { userId, role });
    }
}
```

### Keycloak bilan integratsiya

Keycloak ishlatilganda — token yaratish (`login`) **Keycloak**
tomonidan amalga oshiriladi, ASP.NET Core esa faqat **tekshiruvchi**
(Resource Server) rolini o'ynaydi:

```csharp
builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddJwtBearer(options =>
    {
        options.Authority = "https://keycloak.example.com/realms/erp"; // Keycloak realm URL
        options.Audience = "erp-api";
        options.RequireHttpsMetadata = true; // Production'da HAR DOIM true

        // Keycloak — .well-known/openid-configuration orqali public key'ni
        // AVTOMATIK oladi — IssuerSigningKey qo'lda ko'rsatish shart emas!
    });
```

```
Keycloak bilan ishlash jarayoni:

1. Client → Keycloak: login (username/password yoki OAuth flow)
2. Keycloak: JWT (o'z PRIVATE key'i bilan imzolangan, RS256 algoritmi) qaytaradi
3. Client → ASP.NET Core API: so'rov + Bearer token
4. ASP.NET Core: Keycloak'ning PUBLIC key'ini (JWKS endpoint orqali,
   avtomatik keshlanadi) olib, signature'ni TEKSHIRADI
5. Signature to'g'ri bo'lsa — so'rov davom etadi
```

Keycloak — **RS256** (asimmetrik, RSA) ishlatadi, o'z-o'zi yozgan
oddiy JWT implementatsiyasi ko'pincha **HS256** (simmetrik, HMAC)
ishlatadi. RS256'da — Keycloak PRIVATE key bilan imzolaydi, ASP.NET
Core esa faqat PUBLIC key bilan tekshiradi — bu ASP.NET Core'ga
**hech qachon** imzolash kalitiga ega bo'lish shart emasligini
anglatadi (xavfsizroq — API server buzilsa ham, soxta token
yasab bo'lmaydi).

## 5. Qachon va qanday ishlatish kerak?

| Vaziyat | Yechim |
|---|---|
| Microservices, ko'p server orasida stateless auth | JWT |
| Monolit, oddiy web-sayt | Session (cookie) ham yetarli |
| SPA (React/Angular) + alohida API | JWT + Refresh Token, HttpOnly cookie |
| Enterprise SSO (bir nechta ilova, bitta login) | Keycloak/OAuth2/OpenID Connect |
| Mobil ilova | JWT (Access + Refresh), Secure Storage'da saqlash |

**Best practices:**
- Access Token — 5-15 daqiqa
- Refresh Token — DB'da saqlash, **rotation** (har ishlatilganda yangisi beriladi)
- Refresh Token — HttpOnly, Secure, SameSite cookie orqali (LocalStorage'da EMAS)
- Secret key — Environment variable / Key Vault, HECH QACHON git'ga commit qilinmasin

**Anti-patternlar:**

```
❌ Access Token'ni juda uzoq muddatli qilish (masalan 30 kun)
   → O'g'irlansa, uzoq vaqt xavf ostida qoladi

❌ JWT'ni LocalStorage'da saqlash
   → XSS hujumi orqali JavaScript token'ni O'QIY OLADI!

❌ Payload'ga parol yoki maxfiy ma'lumot qo'shish
   → JWT faqat ENCODE qilingan, istalgan kishi Base64 decode qila oladi

❌ Secret key'ni appsettings.json ga hardcode qilish va git'ga commit qilish
   → Repo public bo'lsa — butun tizim xavfsizligi buziladi
```

## 6. Xavfsizlik va muhim nuqtalar

### XSS va CSRF — Cookie vs LocalStorage

```
LocalStorage'da JWT saqlash:
  ❌ XSS zaif — agar saytda biror joyda XSS zaiflik bo'lsa, hujumchi
     JavaScript orqali localStorage.getItem("token") bilan TOKENNI
     O'QIY OLADI va o'z serveriga yuborishi mumkin
  ✅ CSRF'dan HIMOYALANGAN (chunki token qo'lda Authorization header'ga
     qo'shiladi, brauzer avtomatik yubormaydi)

HttpOnly Cookie'da saqlash:
  ✅ XSS'dan HIMOYALANGAN (JavaScript document.cookie orqali HttpOnly
     cookie'ni O'QIY OLMAYDI)
  ⚠️ CSRF zaif bo'lishi mumkin (brauzer cookie'ni AVTOMATIK yuboradi) —
     SameSite=Strict/Lax bilan bu xavf KAMAYTIRILADI
```

**Tavsiya:** Access Token — xotirada (JS memory, masalan React state),
Refresh Token — HttpOnly + Secure + SameSite cookie'da.

### Token hijacking — qanday oldini olish

- **HTTPS majburiy** — token ochiq tarmoqda o'qilmasligi uchun
- **Qisqa Access Token muddati** — o'g'irlangan token tezda foydasiz bo'ladi
- **Refresh Token rotation** — har ishlatilganda eskisi bekor qilinadi;
  agar eski (allaqachon ishlatilgan) Refresh Token qayta ishlatilishga
  urinilsa — bu **o'g'irlanganlik belgisi**, shu foydalanuvchining
  BARCHA tokenlari bekor qilinishi kerak
- **`jti` (JWT ID) + blacklist** — juda muhim tokenlar uchun (masalan,
  Admin) qo'shimcha bekor qilish mexanizmi

### Short-lived + long-lived strategiyasi — nima uchun ishlaydi

Bu strategiya — **xavfni ikkiga bo'lish**: Access Token tez-tez
ishlatiladi (har API so'rovda) — shuning uchun uni **qisqa** qilib,
xavfni minimallashtiramiz. Refresh Token kamdan-kam ishlatiladi (faqat
Access Token tugaganda) — shuning uchun uni **DB'da nazorat qilish**
imkoniyati bilan **uzoqroq** qilishimiz mumkin.

### Secret key saqlash

```
❌ appsettings.json ichida hardcode
❌ Git repo ichida (hatto private repo bo'lsa ham!)

✅ Environment variable:
   export JWT_SECRET_KEY="..." (production serverda)

✅ Azure Key Vault / HashiCorp Vault / AWS Secrets Manager:
   builder.Configuration.AddAzureKeyVault(...)

✅ appsettings.Development.json — FAQAT local dev, .gitignore ga qo'shilgan
```

## 7. Imtihon savollari

1. JWT'ning 3 qismini ayting va har birining vazifasini tushuntiring.
2. JWT signature qanday yaratiladi va u nimani KAFOLATLAYDI, nimani
   KAFOLATLAMAYDI (masalan, maxfiylik haqida)?
3. Nima uchun Access Token va Refresh Token — ikkita alohida token
   ishlatiladi? Faqat bittasi bilan ishlash nima uchun xavfli?
4. Server JWT'ni qanday tekshiradi — signature tekshiruvi ichki
   jarayonini bosqichma-bosqich tushuntiring.
5. `ClockSkew` parametri nima uchun kerak va uni `TimeSpan.Zero`
   qilish qanday oqibatga olib kelishi mumkin?
6. LocalStorage va HttpOnly Cookie'da JWT saqlash orasidagi xavfsizlik
   farqini XSS va CSRF nuqtai nazaridan tushuntiring.
7. Refresh Token Rotation nima va u qanday hujumni aniqlash imkonini
   beradi?
8. `UseAuthentication()` va `UseAuthorization()` middleware'lari
   nima uchun aynan shu tartibda chaqirilishi SHART?
9. Keycloak bilan integratsiyada nima uchun ASP.NET Core API
   `IssuerSigningKey`ni qo'lda ko'rsatishi shart emas (RS256 va
   JWKS nuqtai nazaridan)?
10. Agar hujumchi JWT payload'idagi `"role": "User"` ni `"role":
    "Admin"` ga qo'lda o'zgartirsa, nima sodir bo'ladi?
