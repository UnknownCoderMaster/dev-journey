# Hashing, Symmetric va Asymmetric Encryption, Digital Signing — Middle D

## 1. Nima? (Ta'rif)

**Hashing** — ma'lumotni **bir tomonlama** (qaytarib bo'lmaydigan)
qisqa "iz"ga (hash) aylantirish. **Symmetric Encryption** — bitta
kalit bilan **shifrlash ham, ochish ham** amalga oshiriladigan
shifrlash. **Asymmetric (Public-Key) Encryption** — ikkita bog'liq
kalit (public/private) asosidagi shifrlash.

## 2. Nima uchun kerak?

Parolni **plain text** saqlash — DB o'g'irlansa, barcha
foydalanuvchi parollari OSHKOR bo'ladi. Hashing — bu xavfni yo'qotadi
(hash'dan parolni **QAYTARIB olib bo'lmaydi**). Encryption — maxfiy
ma'lumotni (masalan, DB ustidagi shaxsiy ma'lumot) uchinchi shaxs
o'qiy olmasligini ta'minlaydi.

## 3. Ichida nima sodir bo'ladi? (Mexanizm)

### 3.1 Hashing — bir tomonlama funksiya

```
parol → HASH FUNKSIYA → hash (masalan 64 belgi)

"12345"  → SHA256 → "5994471abb01112afcc18159f6cc74b4f511b99..."

⚠️ Hash'dan "12345"ga QAYTIB BO'LMAYDI (matematik jihatdan
   BIR TOMONLAMA) — lekin BIR XIL kirish — DOIM BIR XIL hash beradi
   (deterministik).
```

### 3.2 SHA256, SHA512, MD5 — farqlari

```
MD5     — 128 bit, ESKIRGAN — collision (ikki xil matn bir xil hash)
          topilgan, XAVFSIZLIK uchun ISHLATILMASIN
SHA256  — 256 bit, hozircha xavfsiz, KENG ishlatiladi
SHA512  — 512 bit, SHA256'dan xavfsizroq (kattaroq), sekinroq

⚠️ MUHIM: SHA256/SHA512 — parol uchun TO'G'RIDAN ishlatilmasligi
   kerak! Ular ATAYLAB TEZ ishlaydigan hash — bu parol uchun ZARARLI
   (hujumchi millionlab parolni TEZ sinab ko'ra oladi — brute force).
```

### 3.3 Salt — nima va nima uchun kerak

```
Salt YO'Q holatda:
  "12345" → HASH → "5994471a..." (HAR DOIM BIR XIL!)

  ❌ Rainbow Table hujumi: hujumchi OLDINDAN millionlab parol uchun
     hash'larni hisoblab qo'yadi (jadval), keyin DB'dagi hash'ni
     shu jadval bilan SOLISHTIRIB, asl parolni TOPADI!

Salt BOR holatda:
  "12345" + salt1 ("x7Yq") → HASH → "a3f5..."
  "12345" + salt2 ("k9Lp") → HASH → "b8e2..." (BOSHQACHA!)

  ✅ Har foydalanuvchi uchun ALOHIDA, TASODIFIY salt — bir xil parol
     HAR XIL hash beradi — Rainbow Table BEFOYDA bo'lib qoladi!
```

### 3.4 BCrypt — salt avtomatik, parol uchun eng yaxshi

```csharp
// NuGet: BCrypt.Net-Next
string hash = BCrypt.Net.BCrypt.HashPassword("MyPassword123");
// → "$2a$11$N9qo8uLOickgx2ZMRZoMy.../salt+hash BIRGALIKDA saqlanadi"

bool isValid = BCrypt.Net.BCrypt.Verify("MyPassword123", hash); // → true
```

```
BCrypt ICHKARIDA:
  1. Har chaqiruvda TASODIFIY salt AVTOMATIK generatsiya qilinadi
  2. Salt hash bilan BIRGA (bitta stringda) saqlanadi — alohida
     ustun kerak emas
  3. "Work factor" (cost) — necha marta takrorlanishini belgilaydi
     (masalan 11 — 2^11 marta) — ATAYLAB SEKIN, brute force'ni
     QIYINLASHTIRADI
  4. Kompyuterlar tezlashgani sari — cost'ni OSHIRISH mumkin
     (kelajakka moslashuvchan)
```

### 3.5 PBKDF2, Argon2 — alternativalar

```
PBKDF2 — NIST standarti, .NET'da BUILT-IN (Rfc2898DeriveBytes),
         ko'p marta takrorlangan HMAC
Argon2 — 2015 Password Hashing Competition g'olibi, ENG ZAMONAVIY,
         xotira-intensiv (GPU/ASIC hujumlariga chidamli)

Barchasi — "sekin, ataylab qimmat" tamoyiliga asoslangan
(SHA256'dan farqli — u ATAYLAB TEZ)
```

### 3.6 Symmetric Encryption — AES

```csharp
using var aes = Aes.Create();
aes.GenerateKey();
aes.GenerateIV(); // Initialization Vector — har shifrlashda TURLI bo'lishi kerak

using var encryptor = aes.CreateEncryptor();
using var ms = new MemoryStream();
using (var cs = new CryptoStream(ms, encryptor, CryptoStreamMode.Write))
using (var sw = new StreamWriter(cs))
{
    sw.Write("Maxfiy ma'lumot");
}
byte[] encrypted = ms.ToArray();

// Ochish — BIR XIL kalit va IV kerak
using var decryptor = aes.CreateDecryptor(aes.Key, aes.IV);
```

```
Symmetric (AES):
  ✅ TEZ — katta hajmdagi ma'lumot uchun mos
  ❌ Kalitni IKKALA TARAF HAM bilishi kerak — xavfsiz almashish muammosi

Qachon ishlatiladi: DB'da maxfiy ustun shifrlash, fayl shifrlash
```

### 3.7 Asymmetric (RSA) — ikki kalit

```csharp
using var rsa = RSA.Create(2048);
var publicKey = rsa.ExportRSAPublicKey();
var privateKey = rsa.ExportRSAPrivateKey();

// Shifrlash — PUBLIC key bilan (istalgan kishi shifrlashi mumkin)
byte[] encrypted = rsa.Encrypt(Encoding.UTF8.GetBytes("Salom"), RSAEncryptionPadding.OaepSHA256);

// Ochish — FAQAT PRIVATE key bilan (faqat egasi ocha oladi)
byte[] decrypted = rsa.Decrypt(encrypted, RSAEncryptionPadding.OaepSHA256);
```

```
Asymmetric (RSA):
  ✅ Kalit almashish MUAMMOSI YO'Q (public key — OCHIQ tarqatiladi)
  ❌ SEKIN — katta ma'lumot uchun mos EMAS

Amalda: TLS handshake'da FAQAT session key almashish uchun
        ishlatiladi (keyin AES — asosiy trafik uchun)
```

### 3.8 Digital Signing — JWT bilan bog'liqlik

```
Signing — teskari yo'nalish: PRIVATE key bilan IMZOLASH,
          PUBLIC key bilan TEKSHIRISH

signature = Sign(data, privateKey)
IsValid = Verify(data, signature, publicKey)

JWT (RS256) da:
  Keycloak — PRIVATE key bilan token'ni IMZOLAYDI
  ASP.NET Core API — PUBLIC key bilan signature'ni TEKSHIRADI
  (API hech qachon PRIVATE key'ga ega bo'lmaydi — xavfsizroq!)
```

### 3.9 HMACSHA256 — JWT signature (simmetrik variant)

```csharp
using var hmac = new HMACSHA256(secretKeyBytes);
byte[] signature = hmac.ComputeHash(Encoding.UTF8.GetBytes(header + "." + payload));
```

`HMAC` — hash + maxfiy kalit birlashmasi — signing uchun ishlatiladi,
lekin **symmetric** (bitta kalit ikkala tarafda). JWT'da HS256
ishlatilsa — API'ning O'ZI ham signing kalitiga ega bo'lishi kerak
(RS256'dan farqli).

### 3.10 System.Security.Cryptography — asosiy klasslar

```
SHA256, SHA512, MD5          — hash funksiyalar
HMACSHA256                    — kalit bilan hash (signing)
Aes                           — symmetric encryption
RSA                           — asymmetric encryption/signing
RandomNumberGenerator         — kriptografik xavfsiz random
```

## 4. Kod — parolni to'liq boshqarish

```csharp
public class PasswordService
{
    public string HashPassword(string password)
        => BCrypt.Net.BCrypt.HashPassword(password, workFactor: 12);

    public bool VerifyPassword(string password, string hash)
        => BCrypt.Net.BCrypt.Verify(password, hash);
}

// Registratsiya
var hash = _passwordService.HashPassword(dto.Password);
_context.Employees.Add(new Employee { PasswordHash = hash });

// Login
var valid = _passwordService.VerifyPassword(dto.Password, employee.PasswordHash);
```

## 5. Qachon ishlatish kerak?

| Ehtiyoj | Yechim |
|---|---|
| Parol saqlash | BCrypt (yoki Argon2) |
| Fayl butunligini tekshirish (checksum) | SHA256 |
| DB ustunini shifrlash (qayta o'qish kerak) | AES (Symmetric) |
| Kalit almashish, JWT (RS256) | RSA (Asymmetric) |
| JWT signature (bitta server) | HMACSHA256 |

## 6. Muhim nuqtalar

- **Hech qachon** parolni oddiy hash (SHA256) bilan saqlamang —
  salt'siz va tez bo'lgani uchun brute-force'ga zaif.
- AES kalitini kodga hardcode qilmang — Key Vault/Environment
  variable orqali saqlang.
- RSA — katta ma'lumot uchun juda sekin, faqat kichik ma'lumot
  (masalan, symmetric kalitning o'zi) uchun ishlatiladi.

## 7. Imtihon savollari

1. Hashing va Encryption orasidagi asosiy farq nima (qaytarib
   bo'lish-bo'lmasligi nuqtai nazaridan)?
2. Salt nima muammoni (Rainbow Table) hal qiladi?
3. Nima uchun SHA256 parol saqlash uchun TAVSIYA ETILMAYDI, BCrypt
   esa tavsiya etiladi?
4. Symmetric va Asymmetric encryption orasidagi farqni tezlik va
   kalit almashish nuqtai nazaridan tushuntiring.
5. TLS nima uchun ikkalasini (RSA + AES) birga ishlatadi?
6. HMACSHA256 (HS256) va RSA (RS256) — JWT signing'da qanday farq
   qiladi, xavfsizlik nuqtai nazaridan qaysi biri afzalroq (masalan
   Keycloak kabi tashqi Identity Provider bilan)?
