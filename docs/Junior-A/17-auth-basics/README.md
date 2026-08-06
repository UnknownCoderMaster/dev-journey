# Authentication vs Authorization — Asoslar va Turlari — Junior A

## 1. Nima? (Ta'rif)

**Authentication (Autentifikatsiya)** — foydalanuvchi **KIM
ekanligini aniqlash** jarayoni. **Authorization (Avtorizatsiya)** —
allaqachon aniqlangan foydalanuvchining **NIMA qila olishini
aniqlash** jarayoni.

## 2. Nima uchun kerak?

Har qanday **himoyalangan** resurs (masalan xodim maoshi) — FAQAT
**tegishli huquqqa ega** shaxsga ko'rsatilishi kerak. Bu ikki
bosqichli jarayon — avval "kim" (Authentication), keyin "nima qila
oladi" (Authorization) — tizimni **xavfsiz** qiladi.

## 3. Ichida nima sodir bo'ladi? (Mexanizm)

### 3.1 Authentication — jarayon

```
1. Credentials TEKSHIRISH — login/parol, token, sertifikat
2. Identity YARATISH — "Bu — Orzibek, ID=42"
3. ClaimsPrincipal to'ldirish — HttpContext.User ga O'RNATISH
```

```csharp
// Autentifikatsiyadan KEYIN, HAR KONTROLLERDA:
var userId = User.FindFirst(ClaimTypes.NameIdentifier)?.Value;
var isAuthenticated = User.Identity?.IsAuthenticated ?? false;
```

**`ClaimsPrincipal`, `ClaimsIdentity`:**
```
ClaimsPrincipal — FOYDALANUVCHINING BUTUN "shaxsiyati" (bir nechta
                   Identity'ga ega bo'lishi mumkin)
    │
    └── ClaimsIdentity — BITTA autentifikatsiya MANBASIDAN (masalan
         "Jwt" scheme) kelgan CLAIMS to'plami
             │
             ├── Claim { Type: "sub", Value: "42" }
             └── Claim { Type: "role", Value: "Admin" }
```

### 3.2 Authorization — jarayon

```csharp
[Authorize(Roles = "Admin")]        // Role asosida
[Authorize(Policy = "CanEditSalary")] // Policy asosida
```

### 3.3 Farqi — 401 vs 403

```
401 Unauthorized — "SEN KIM ekaningni BILMAYMAN" (token yo'q/yaroqsiz)
403 Forbidden    — "SEN KIM ekaningni BILAMAN, lekin RUXSATING YO'Q"
```

### 3.4 Authentication turlari

**Password-based** — eng keng tarqalgan:
```csharp
var isValid = BCrypt.Net.BCrypt.Verify(password, user.PasswordHash);
```

**Token-based (JWT, Bearer):**
```
Authorization: Bearer eyJhbGc...
```

**Cookie-based (session):**
```csharp
builder.Services.AddAuthentication(CookieAuthenticationDefaults.AuthenticationScheme)
    .AddCookie(options => options.LoginPath = "/login");
```

**Certificate-based (mTLS):**
```
Client — SSL SERTIFIKAT taqdim etadi, server BUNI TEKSHIRADI —
Server-to-Server (masalan bank tizimlarida) integratsiyalarda
ishlatiladi.
```

**OAuth 2.0** — third-party avtorizatsiya:
```
"Google orqali kirish" — Google — foydalanuvchi NOMIDAN sizning
ilovangizga CHEKLANGAN HUQUQ (token) beradi, PAROLNI HECH QACHON
sizga BERMAYDI.
```

**OpenID Connect (OIDC)** — OAuth 2.0 ustiga qurilgan **identity**
qatlami — "kim ekanligi"ni (ID Token) HAM taqdim etadi (OAuth
2.0 O'ZI faqat "nima qila oladi" haqida edi).

**API Key** — service-to-service, oddiy:
```
X-Api-Key: abc123
```

**SSO (Single Sign-On)** — Keycloak orqali:
```
Foydalanuvchi BIR MARTA login qiladi (Keycloak'da) — BARCHA bog'liq
ilovalarga (ERP, CRM, Dashboard) QAYTA login QILMASDAN kiradi.
```

**Biometric** — barmoq izi, Face ID (mobil ilovalarda ko'proq).

**MFA (Multi-Factor Authentication)** — parol + qo'shimcha faktor
(TOTP, SMS) — batafsil [Middle-D/11-password-mfa](../../Middle-D/11-password-mfa/README.md)da.

### 3.5 HTTP Authentication Schemes

```
Basic  — Authorization: Basic base64(username:password) — SHIFRLANMAGAN
         (HTTPS bilan BIRGA ISHLATILISHI SHART!)
Bearer — Authorization: Bearer <token> — JWT/OAuth uchun STANDART
Digest — Basic'dan XAVFSIZROQ (hash asosida), lekin KAMDAN-KAM ishlatiladi
```

```csharp
// Basic Auth misoli
var byteArray = Encoding.ASCII.GetBytes($"{username}:{password}");
var header = "Basic " + Convert.ToBase64String(byteArray);
```

### 3.6 Authentication Middleware — `UseAuthentication()` kerak

```csharp
app.UseAuthentication(); // 1. Token/Cookie'ni O'QIYDI, User'ni O'RNATADI
app.UseAuthorization();  // 2. [Authorize] TEKSHIRUVLARINI bajaradi

// ⚠️ TARTIB MUHIM — Authorization Authentication'dan OLDIN bo'lsa,
//    HttpContext.User HALI TO'LDIRILMAGAN bo'ladi!
```

## 4. Kod — to'liq misol

```csharp
builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddJwtBearer(options =>
    {
        options.TokenValidationParameters = new TokenValidationParameters
        {
            ValidateIssuer = true, ValidIssuer = "erp.example.com",
            ValidateAudience = true, ValidAudience = "erp-api",
            ValidateIssuerSigningKey = true,
            IssuerSigningKey = new SymmetricSecurityKey(key)
        };
    });

builder.Services.AddAuthorization(options =>
    options.AddPolicy("CanEditSalary", policy => policy.RequireRole("HR", "Admin")));

var app = builder.Build();
app.UseAuthentication();
app.UseAuthorization();
```

## 5. Qachon ishlatish kerak?

| Vaziyat | Yechim |
|---|---|
| Oddiy web app, brauzer sessiyasi | Cookie-based |
| API, SPA, mobil, microservices | Token-based (JWT) |
| Service-to-service, oddiy | API Key |
| Enterprise SSO, ko'p ilova | OAuth2/OIDC (Keycloak) |
| Bank/moliyaviy, yuqori xavfsizlik | Certificate-based (mTLS) |

## 6. Muhim nuqtalar

- Basic Auth — HAR DOIM **HTTPS** bilan BIRGA ishlatilishi kerak
  (base64 — shifrlash EMAS, oddiy encoding).
- OAuth 2.0 — **avtorizatsiya** protokoli, OpenID Connect — bu
  ustiga qurilgan **autentifikatsiya** (identity) qatlami — ular
  ko'pincha **chalkashtiriladi**.
- `UseAuthentication()` — `UseAuthorization()`dan **OLDIN** chaqirilishi
  MAJBURIY.

## 7. Imtihon savollari

1. Authentication va Authorization orasidagi farqni bitta gap
   bilan tushuntiring.
2. 401 va 403 status kodlari orasidagi farq nima?
3. `ClaimsPrincipal` va `ClaimsIdentity` orasidagi munosabat qanday?
4. OAuth 2.0 va OpenID Connect orasidagi farq nima?
5. Basic Auth nima uchun HTTPS'siz xavfli hisoblanadi?
6. SSO (Single Sign-On) qanday muammoni hal qiladi?
7. `UseAuthentication()` va `UseAuthorization()` tartibi nima
   uchun muhim?
