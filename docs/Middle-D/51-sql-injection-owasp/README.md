# SQL Injection, Safe Credentials, OWASP Top 10 — Middle D

## 1. Nima? (Ta'rif)

**SQL Injection** — hujumchi tomonidan **maxsus tayyorlangan
kirish** orqali, ilova SQL so'roviga **begona SQL kod**ni
"in'ektsiya qilish" (kiritish) hujumi. **OWASP Top 10** — veb
ilovalarda eng ko'p uchraydigan 10 ta xavfsizlik zaifligi ro'yxati
(OWASP tashkiloti tomonidan muntazam yangilanadi).

## 2. Nima uchun kerak?

SQL Injection — **eng eski, lekin hali ham eng xavfli** hujum
turlaridan biri — bir necha qatorlik zaif kod orqali **butun DB**
o'g'irlanishi yoki o'chirilishi mumkin. OWASP Top 10'ni bilish —
xavfsiz kod yozishning **minimal talab darajasi**.

## 3. Ichida nima sodir bo'ladi? (Mexanizm)

### 3.1 SQL Injection — qanday ishlaydi

```csharp
// ❌ XAVFLI — string concatenation
var sql = $"SELECT * FROM employees WHERE name = '{userInput}'";

// Agar userInput = "x'; DROP TABLE employees; --"
// Yakuniy SQL:
// SELECT * FROM employees WHERE name = 'x'; DROP TABLE employees; --'
// 💥 BUTUN JADVAL O'CHIRILADI!
```

### 3.2 SQL Injection turlari

```
In-band (Classic) — Xato xabari yoki natija to'g'ridan JAVOBDA ko'rinadi
                     (eng oson aniqlanadigan/ekspluatatsiya qilinadigan)

Blind SQL Injection — Xato/natija KO'RINMAYDI, lekin ILOVA XATTI-
                       HARAKATI (masalan javob vaqti, true/false)
                       orqali MA'LUMOT "chiqarib olinadi":
  ' OR (SELECT COUNT(*) FROM users) > 10 --  (agar TRUE bo'lsa —
                                                boshqacha javob/vaqt)

Out-of-band — Natija BOSHQA KANAL orqali (masalan DNS so'rov) olinadi
              — kamdan-kam, murakkab tarmoq sozlamalarida
```

### 3.3 Himoya — parametrlangan so'rovlar

```csharp
// ✅ XAVFSIZ — parametr sifatida yuboriladi (SQL KOD emas, DATA sifatida)
var employees = await _context.Employees
    .Where(e => e.Name == userInput) // EF Core AVTOMATIK parametrlashtiradi
    .ToListAsync();

// ADO.NET'da qo'lda
command.Parameters.AddWithValue("@name", userInput);
```

Parametrlangan so'rovda — DB driver `userInput`ni **hech qachon SQL
kodi** deb talqin qilmaydi, u FAQAT **qiymat** sifatida uzatiladi —
istalgan maxsus belgi (`'`, `;`, `--`) **zararsizlanadi**.

### 3.4 ORM (EF Core, Dapper) — SQL Injection himoyasimi?

```
EF Core LINQ — AVTOMATIK ravishda PARAMETRLANGAN SQL generatsiya
qiladi — LINQ ishlatilganda SQL Injection XAVFI DEYARLI YO'Q.

⚠️ LEKIN: RAW SQL (FromSqlRaw, ExecuteSqlRaw) — string
CONCATENATION bilan ishlatilsa, XAVF QAYTARILADI!
```

```csharp
// ❌ XAVFLI — FromSqlRaw + string interpolation
var sql = $"SELECT * FROM employees WHERE name = '{userInput}'";
var employees = await _context.Employees.FromSqlRaw(sql).ToListAsync(); // 💥 INJECTION MUMKIN!

// ✅ XAVFSIZ — FromSqlInterpolated (AVTOMATIK parametrlashtiradi)
var employees2 = await _context.Employees
    .FromSqlInterpolated($"SELECT * FROM employees WHERE name = {userInput}")
    .ToListAsync();
```

### 3.5 `FromSqlRaw` vs `FromSqlInterpolated` — farqi

```
FromSqlRaw           — string PARAMETR sifatida qabul qiladi, QO'LDA
                        parametrlashtirish (@p0) SIZGA BOG'LIQ
FromSqlInterpolated  — C# 6+ string interpolation ($"...") ISHLATADI,
                        EF Core ICHKARIDA AVTOMATIK parametrlarga
                        AYLANTIRADI — XAVFSIZROQ va QULAYROQ
```

### 3.6 Safe Credentials — connection string saqlash

```
❌ appsettings.json'da hardcode + git'ga commit
✅ User Secrets (Development) — loyihadan TASHQARIDA saqlanadi
✅ Environment Variables (Production)
✅ Azure Key Vault / AWS Secrets Manager / HashiCorp Vault (Enterprise)
```

### 3.7 Parol hashing — BCrypt

```csharp
string hash = BCrypt.Net.BCrypt.HashPassword(password);
```

Parol — HECH QACHON plain text yoki oddiy hash (SHA256) bilan
saqlanmasligi kerak — batafsil [05-hashing-encryption](../05-hashing-encryption/README.md)da.

### 3.8 API key saqlash va Credential Rotation

```
API key — connection string kabi, Environment Variable/Key Vault'da
saqlanishi kerak.

Credential Rotation — MUNTAZAM (masalan har 90 kunda) parol/kalitlarni
YANGILASH strategiyasi — agar kalit SIZIB CHIQQAN bo'lsa ham, uzoq
vaqt AMALDA QOLMASLIGINI ta'minlaydi.
```

### 3.9 OWASP Top 10 (2021) — har biri qisqacha

```
1. Broken Access Control
   — Foydalanuvchi O'ZIGA TEGISHLI BO'LMAGAN resursga kirishi mumkin
   — Himoya: har so'rovda RESURS EGALIGINI tekshirish (IDOR himoyasi)

2. Cryptographic Failures
   — Maxfiy ma'lumot SHIFRLANMAGAN yoki KUCHSIZ algoritm bilan saqlangan
   — Himoya: HTTPS majburiy, BCrypt/AES, TLS 1.2+

3. Injection (SQL, Command, LDAP)
   — Foydalanuvchi kirishi KOD sifatida BAJARILADI
   — Himoya: parametrlangan so'rovlar, INPUT validatsiya

4. Insecure Design
   — Arxitektura DARAJASIDA xavfsizlik E'TIBORGA OLINMAGAN
   — Himoya: Threat Modeling, xavfsizlikni DIZAYN bosqichida REJALASHTIRISH

5. Security Misconfiguration
   — DEFAULT parollar, ORTIQCHA ochiq portlar, batafsil xato xabarlari
   — Himoya: xavfsiz DEFAULT sozlamalar, muntazam AUDIT

6. Vulnerable and Outdated Components
   — ESKI, ZAIFLIGI MA'LUM kutubxona/framework ishlatilishi
   — Himoya: muntazam DEPENDENCY UPDATE, `dotnet list package --vulnerable`

7. Identification and Authentication Failures
   — Kuchsiz parol siyosati, MFA yo'qligi, session boshqaruvi zaif
   — Himoya: BCrypt, MFA, qisqa Access Token muddati

8. Software and Data Integrity Failures
   — CI/CD pipeline yoki YANGILANISH jarayoni TEKSHIRILMAGAN manbadan
   — Himoya: imzolangan paketlar, ishonchli CI/CD

9. Security Logging and Monitoring Failures
   — Hujum/xato SEZILMAYDI (log yo'q yoki YETARSIZ)
   — Himoya: Structured logging, Serilog+Seq, alerting

10. Server-Side Request Forgery (SSRF)
    — Server FOYDALANUVCHI bergan URL'ga ICHKI tarmoq nomidan SO'ROV
      YUBORISHGA MAJBUR QILINADI
    — Himoya: tashqi URL'larni WHITELIST orqali cheklash
```

## 4. Kod — himoya misollari

```csharp
// ✅ Broken Access Control himoyasi
[HttpGet("{id}/salary")]
public async Task<IActionResult> GetSalary(int id)
{
    if (id != _currentUser.UserId && _currentUser.Role != "HR")
        return Forbid();
    return Ok(await _repo.GetSalaryAsync(id));
}

// ✅ SSRF himoyasi
private static readonly HashSet<string> AllowedHosts = new() { "api.trusted-partner.com" };
public bool IsUrlAllowed(Uri url) => AllowedHosts.Contains(url.Host);
```

## 5. Qachon ishlatish kerak?

| Vaziyat | Yechim |
|---|---|
| DB so'rovi (har doim) | Parametrlangan so'rov/LINQ |
| Raw SQL zarur | `FromSqlInterpolated` |
| Connection string, API key | Environment Variable/Key Vault |
| Har API loyihasi | OWASP Top 10 checklist bilan audit |

## 6. Muhim nuqtalar

- ORM ishlatish — SQL Injection'dan **avtomatik** himoya bermaydi,
  agar Raw SQL noto'g'ri ishlatilsa.
- OWASP Top 10 — statik ro'yxat EMAS, **muntazam yangilanadi** —
  eng so'nggi versiyani kuzatib borish tavsiya etiladi.
- Xavfsizlik — **bir martalik** ish emas, balki **davomiy** jarayon
  (dependency yangilash, log kuzatish, audit).

## 7. Imtihon savollari

1. SQL Injection qanday ishlaydi va parametrlangan so'rov uni
   qanday oldini oladi?
2. `FromSqlRaw` va `FromSqlInterpolated` orasidagi xavfsizlik farqi
   nima?
3. In-band va Blind SQL Injection orasidagi farq nima?
4. OWASP Top 10'dan 3 ta zaiflikni tanlab, har biriga qarshi
   himoya usulini tushuntiring.
5. Broken Access Control va IDOR orasidagi bog'liqlik nima?
6. Credential Rotation nima va u nima uchun muhim?
