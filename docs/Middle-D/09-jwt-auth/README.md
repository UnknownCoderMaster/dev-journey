# JWT Authentication — ASP.NET Core — Middle D

> Bu fayl — `docs/Middle-D/01-jwt-authentication/README.md` da avval
> yozilgan chuqur JWT hujjatining **55-mavzulik to'liq curriculum**
> ichidagi rasmiy o'rni. To'liq tafsilotlar (Signature mexanizmi,
> Access/Refresh Token strategiyasi, Keycloak integratsiyasi, XSS/CSRF
> himoyasi) uchun o'sha faylga qarang — bu yerda ASOSIY mazmun qisqa
> shaklda takrorlanadi va curriculum tuzilmasiga moslashtirilgan.

## 1. Nima? (Ta'rif)

**JWT (JSON Web Token, RFC 7519)** — foydalanuvchi claims'ini
raqamli imzo bilan tasdiqlangan holda uzatish standarti. 3 qismdan
iborat: `Header.Payload.Signature` (Base64Url encoded, nuqta bilan
ajratilgan).

## 2. Nima uchun kerak?

Stateless autentifikatsiya — server har so'rovda DB/session store'ga
murojaat qilmasdan, token imzosini tekshirib foydalanuvchini
tanib oladi. Bu microservice arxitekturada **gorizontal masshtablash**ni
osonlashtiradi.

## 3. Ichida nima sodir bo'ladi? (Mexanizm)

```
eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjMiLCJleHAiOjE3MDAwMDB9.HMACSHA256_hash
└──────── Header ────────┘└─────────── Payload ───────────┘└─ Signature ─┘

Signature = HMACSHA256(base64(header) + "." + base64(payload), SECRET_KEY)
```

**Tekshirish jarayoni:** server o'z kalitini bilib, header+payload'dan
QAYTA hash hisoblaydi va token ichidagi signature bilan solishtiradi.
Mos kelmasa — token o'zgartirilgan yoki soxta (401).

**Access Token (qisqa, 15 daq) + Refresh Token (uzoq, 30 kun, DB'da)**
— access token o'g'irlansa tez foydasiz bo'ladi, refresh token esa
server tomonidan **bekor qilinishi** mumkin (chunki DB'da saqlanadi).

## 4. Kod — asosiy implementatsiya

```bash
dotnet add package Microsoft.AspNetCore.Authentication.JwtBearer
```

```csharp
builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddJwtBearer(options =>
    {
        options.TokenValidationParameters = new TokenValidationParameters
        {
            ValidateIssuer = true, ValidIssuer = config["Jwt:Issuer"],
            ValidateAudience = true, ValidAudience = config["Jwt:Audience"],
            ValidateIssuerSigningKey = true,
            IssuerSigningKey = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(secretKey)),
            ValidateLifetime = true,
            ClockSkew = TimeSpan.Zero
        };
    });

app.UseAuthentication(); // ⚠️ TARTIB: Authentication OLDIN
app.UseAuthorization();  //          Authorization KEYIN
```

```csharp
var token = new JwtSecurityToken(
    issuer: issuer, audience: audience, claims: claims,
    expires: DateTime.UtcNow.AddMinutes(15),
    signingCredentials: new SigningCredentials(key, SecurityAlgorithms.HmacSha256));
var jwt = new JwtSecurityTokenHandler().WriteToken(token);
```

Refresh Token — DB'da `RefreshToken` entity sifatida saqlanadi,
`RevokedAt` maydoni orqali logout/bekor qilish amalga oshiriladi
(to'liq kod — [01-jwt-authentication](../01-jwt-authentication/README.md)da).

## 5. Qachon ishlatish kerak?

Microservices, SPA + API, mobil ilova — JWT. Oddiy monolit sayt —
Session ham yetarli. Enterprise SSO — Keycloak (RS256).

## 6. Muhim nuqtalar

- Refresh Token — **HttpOnly + Secure + SameSite** cookie'da, LocalStorage'da
  EMAS (XSS himoyasi).
- Secret key — Environment variable/Key Vault, HECH QACHON kodga
  hardcode/git'ga commit qilinmasin.
- Keycloak (RS256) ishlatilganda — API faqat **public key** bilan
  tekshiradi, imzolash kalitiga umuman ega bo'lmaydi.

## 7. Imtihon savollari

1. JWT'ning 3 qismini va har birining vazifasini ayting.
2. Access va Refresh Token nima uchun ikkalasi kerak?
3. Signature qanday tekshiriladi va u nimani kafolatlaydi?
4. `UseAuthentication()`/`UseAuthorization()` tartibi nima uchun muhim?
5. LocalStorage va HttpOnly Cookie orasidagi xavfsizlik farqi nima?
6. HS256 va RS256 orasidagi farq, Keycloak konteksida.
