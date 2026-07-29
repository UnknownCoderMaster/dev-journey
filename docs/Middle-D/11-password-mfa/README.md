# Password-based Authentication, Multi-Factor Authentication (MFA) — Middle D

## 1. Nima? (Ta'rif)

**Password-based Authentication** — login/parol orqali foydalanuvchini
tanish. **MFA (Multi-Factor Authentication)** — bitta faktor (parol)
yetarli emasligini hisobga olib, **qo'shimcha tasdiqlash qatlami**
qo'shuvchi xavfsizlik mexanizmi.

## 2. Nima uchun kerak?

Parol — **yagona** himoya qatlami bo'lsa, u sizib chiqsa (phishing,
data breach, kuchsiz parol) — hisob **to'liq** buzilishi mumkin.
MFA — hujumchi parolni bilsa ham, **ikkinchi faktorsiz** kira
olmasligini kafolatlaydi.

## 3. Ichida nima sodir bo'ladi? (Mexanizm)

### 3.1 Password-based auth oqimi

```
1. Foydalanuvchi email + parol yuboradi
2. Server DB'dan hash'ni oladi
3. BCrypt.Verify(kiritilgan_parol, saqlangan_hash)
4. Mos kelsa → token beriladi, mos kelmasa → 401
```

### 3.2 Nima uchun aniq xato xabari berilmasligi kerak

```
❌ "Bunday email topilmadi" / "Parol noto'g'ri" (ALOHIDA xabarlar)
   → Hujumchi email BOR-YO'QLIGINI BILIB OLADI (User Enumeration
     hujumi) — keyin faqat parolni brute-force qilishi kifoya

✅ "Email yoki parol noto'g'ri" (BIR XIL, UMUMIY xabar)
   → Hujumchi email mavjud yoki yo'qligini BILA OLMAYDI
```

### 3.3 Brute force himoyasi

```
Rate Limiting — bitta IP/foydalanuvchidan DAQIQASIGA cheklangan urinish:

builder.Services.AddRateLimiter(options =>
{
    options.AddFixedWindowLimiter("login", opt =>
    {
        opt.PermitLimit = 5;
        opt.Window = TimeSpan.FromMinutes(1);
    });
});

Account Lockout — N marta noto'g'ri urinishdan keyin hisobni
VAQTINCHA (masalan 15 daqiqaga) BLOKLASH:

if (failedAttempts >= 5)
{
    user.LockoutEnd = DateTime.UtcNow.AddMinutes(15);
}
```

### 3.4 MFA — uch faktor toifasi

```
1. Bilish (Knowledge)  — parol, PIN
2. Ega bo'lish (Possession) — telefon, hardware token, TOTP ilova
3. Bo'lish (Inherence) — barmoq izi, Face ID (biometrika)

MFA = kamida IKKITA turli TOIFADAN faktor (masalan parol + TOTP kod)
```

### 3.5 TOTP (Time-based One-Time Password) — qanday ishlaydi

```
Umumiy MAXFIY KALIT (secret) — LOGIN paytida QR kod orqali
foydalanuvchi ilovasiga (Google Authenticator) BERILADI.

TOTP kod = HMAC-SHA1(secret, floor(current_unix_time / 30)) → 6 xonali son

Har 30 soniyada — vaqt blogi (time step) o'zgaradi → YANGI kod
generatsiya bo'ladi. Server HAM bir xil secret + vaqt bilan hisoblab,
foydalanuvchi kiritgan kod bilan SOLISHTIRADI.

Vaqt sinxronizatsiyasi MUHIM — server va telefon soati BIR-BIRIGA
YAQIN bo'lishi kerak (odatda ±1 vaqt blogi tolerantlik beriladi).
```

```
Client (telefon)                    Server
  secret (bir marta, QR orqali) ──────► secret (DB'da saqlanadi)
     │                                      │
     ▼ (har 30s)                            ▼ (har so'rovda)
  TOTP(secret, vaqt) = 123456        TOTP(secret, vaqt) = 123456
     │                                      │
     └──────── SOLISHTIRISH (mos!) ─────────┘
```

### 3.6 OtpNet bilan implementatsiya

```bash
dotnet add package Otp.NET
```

```csharp
// Ro'yxatdan o'tishda — secret yaratish
var secretKey = KeyGeneration.GenerateRandomKey(20);
var base32Secret = Base32Encoding.ToString(secretKey);

// QR kod uchun URI (Google Authenticator skanerlaydi)
var qrUri = $"otpauth://totp/ERP:{user.Email}?secret={base32Secret}&issuer=ERP";

// Tasdiqlashda
var totp = new Totp(secretKey);
bool isValid = totp.VerifyTotp(userEnteredCode, out _, VerificationWindow.RfcSpecifiedNetworkDelay);
```

### 3.7 SMS OTP vs TOTP

```
SMS OTP:
  ✅ Foydalanuvchi uchun QULAY (ilova o'rnatish shart emas)
  ❌ SIM Swapping hujumi — hujumchi operator orqali SIM'ni O'ZIGA
     KO'CHIRISHI mumkin (ijtimoiy muhandislik orqali)
  ❌ Tarmoq kechikishi, yetkazilmaslik xavfi

TOTP:
  ✅ SIM Swapping'dan HIMOYALANGAN (telefon raqamiga bog'liq EMAS)
  ✅ Internetsiz ishlaydi (faqat vaqt + secret kerak)
  ❌ Ilova o'rnatish talab qiladi

Xavfsizlik nuqtai nazaridan — TOTP SMS OTP'dan AFZALROQ.
```

### 3.8 MFA to'liq oqimi

```
1. POST /login (email, parol) → parol TO'G'RI
2. Server: "MFA kerak" javobi (token HALI berilmaydi, MAXSUS
   "mfa_pending" holat qaytariladi)
3. POST /login/mfa (mfa_pending_token, totp_code)
4. Server: TOTP kodni tekshiradi
5. TO'G'RI bo'lsa → TO'LIQ Access Token + Refresh Token beriladi
```

## 4. Kod — ASP.NET Core MFA implementatsiya

```csharp
[HttpPost("login")]
public async Task<IActionResult> Login(LoginDto dto)
{
    var user = await _repo.GetByEmailAsync(dto.Email);
    if (user is null || !BCrypt.Net.BCrypt.Verify(dto.Password, user.PasswordHash))
        return Unauthorized(new { message = "Email yoki parol noto'g'ri" });

    if (user.MfaEnabled)
    {
        var pendingToken = _tokenService.GenerateMfaPendingToken(user.Id); // Qisqa muddatli, MAXSUS
        return Ok(new { requiresMfa = true, pendingToken });
    }

    return Ok(new { accessToken = _tokenService.GenerateAccessToken(user) });
}

[HttpPost("login/mfa")]
public async Task<IActionResult> VerifyMfa(MfaVerifyDto dto)
{
    var userId = _tokenService.ValidateMfaPendingToken(dto.PendingToken);
    var user = await _repo.GetByIdAsync(userId);

    var totp = new Totp(Base32Encoding.ToBytes(user.MfaSecret));
    if (!totp.VerifyTotp(dto.Code, out _, VerificationWindow.RfcSpecifiedNetworkDelay))
        return Unauthorized(new { message = "MFA kod noto'g'ri" });

    return Ok(new { accessToken = _tokenService.GenerateAccessToken(user) });
}
```

## 5. Qachon ishlatish kerak?

| Vaziyat | Yechim |
|---|---|
| Oddiy foydalanuvchi tizimi | Password + BCrypt yetarli |
| Admin/moliyaviy huquqli hisoblar | MFA (TOTP) MAJBURIY qilish |
| Foydalanuvchiga qulaylik + xavfsizlik balansi | TOTP (App orqali) |
| Telefon raqami orqali tasdiqlash zarur | SMS OTP (lekin TOTP'dan kamroq xavfsiz) |

## 6. Muhim nuqtalar

- Parolni HECH QACHON plain text saqlamang — BCrypt/Argon2.
- Login xato xabari — HAR DOIM umumiy ("email yoki parol noto'g'ri").
- Rate limiting + Account Lockout — brute force'ga qarshi MAJBURIY.
- TOTP secret — DB'da **shifrlangan** holda saqlanishi tavsiya
  etiladi (agar DB o'g'irlansa, MFA secret'lar HAM oshkor bo'lmasin).

## 7. Imtihon savollari

1. Nima uchun login xato xabari "Email yoki parol noto'g'ri" tarzida
   umumiy bo'lishi kerak?
2. Brute force hujumidan himoyalanishning ikki asosiy usulini ayting.
3. TOTP kod qanday hisoblanadi — formula asosida tushuntiring.
4. SMS OTP va TOTP orasidagi xavfsizlik farqi nima (SIM Swapping
   nuqtai nazaridan)?
5. MFA faktorlarining 3 toifasini ayting va har biriga misol
   keltiring.
6. To'liq MFA login oqimini (2 bosqichli so'rov) tushuntiring.
