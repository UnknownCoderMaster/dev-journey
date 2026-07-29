# Safe Credentials — Amaliyot — Middle D

## 1. Nima? (Ta'rif)

**Safe Credentials** — parol, API kalit, connection string kabi
maxfiy ma'lumotlarni **kod bazasidan tashqarida**, xavfsiz
saqlash va boshqarish amaliyotlari majmuasi.

## 2. Nima uchun kerak?

Git repo — **abadiy tarix** saqlaydi. Bir marta commit qilingan
parol — hatto keyinroq o'chirilsa ham, **git history**da
QOLAVERADI (agar tarix qayta yozilmasa). Public repo bo'lsa —
bu parol **butun dunyoga** oshkor bo'ladi.

## 3. Ichida nima sodir bo'ladi? (Mexanizm)

### 3.1 Secret Manager (User Secrets) — development'da

```bash
dotnet user-secrets init
dotnet user-secrets set "ConnectionStrings:DefaultConnection" "Host=localhost;Password=devpass"
dotnet user-secrets list
```

```
Saqlanadi: %APPDATA%\Microsoft\UserSecrets\{guid}\secrets.json
           (LOYIHA PAPKASI TASHQARISIDA — git'ga TASODIFAN
           COMMIT QILINMAYDI!)
```

### 3.2 Environment Variables — production'da

```bash
export ConnectionStrings__DefaultConnection="Host=prod-db;Password=..."
```

```yaml
# Docker Compose
environment:
  - ConnectionStrings__DefaultConnection=${DB_CONNECTION_STRING}
```

### 3.3 Azure Key Vault / HashiCorp Vault — enterprise

```csharp
builder.Configuration.AddAzureKeyVault(
    new Uri("https://myvault.vault.azure.net/"),
    new DefaultAzureCredential());
```

```
Key Vault — MARKAZLASHGAN, AUDIT qilinadigan (kim, qachon
o'qiganini KUZATIB BORADI), ROTATSIYA (avtomatik yangilash)
imkoniyatiga ega maxfiy ma'lumot saqlash xizmati — bir nechta
ilova/server BIR XIL manbadan xavfsiz o'qiydi.
```

### 3.4 Connection string shifrlash

```
Agar Key Vault ISHLATILMASA — connection string'ni DB/config
faylida SHIFRLANGAN holda saqlash (masalan Windows DPAPI orqali)
— QO'SHIMCHA himoya qatlami, lekin Key Vault'ga QARAGANDA
KAMROQ QULAY (kalitni QAYERDA saqlash muammosi hali ham QOLADI).
```

### 3.5 `.gitignore` da nozik fayllar

```
# .gitignore
appsettings.Development.json
appsettings.*.local.json
*.pfx
.env
secrets.json
```

```
⚠️ MUHIM: .gitignore FAQAT KELAJAKDAGI commit'larni oldini oladi!
   Agar fayl ALLAQACHON commit qilingan bo'lsa — .gitignore'ga
   qo'shish YETARLI EMAS, `git filter-branch` yoki BFG Repo-Cleaner
   bilan TARIXDAN HAM o'chirish, VA kalitni ALMASHTIRISH (rotate)
   kerak!
```

### 3.6 GitHub/GitLab Secrets — CI/CD'da

```yaml
# GitHub Actions
- name: Deploy
  env:
    DB_PASSWORD: ${{ secrets.DB_PASSWORD }} # Repo Settings → Secrets orqali qo'shiladi
  run: ./deploy.sh
```

```
CI/CD Secrets — REPO sozlamalarida SAQLANADI (kod ICHIDA EMAS),
workflow LOG'larida AVTOMATIK "***" bilan MASKALANADI (tasodifiy
oshkor bo'lishning oldi olinadi).
```

### 3.7 Rotation — kalitlarni yangilash strategiyasi

```
Muntazam (masalan 90 kunda) parol/API key'ni ALMASHTIRISH:

1. YANGI kalit yaratiladi
2. Ilova IKKALA (eski + yangi) kalitni QABUL QILADIGAN qilib
   YANGILANADI (grace period)
3. Barcha servis YANGI kalitga O'TKAZILADI
4. ESKI kalit BEKOR QILINADI

Bu — agar kalit SIZIB CHIQQAN bo'lsa (bilinmasdan) ham, uning
"amal qilish muddati" CHEKLANGAN bo'lishini ta'minlaydi.
```

### 3.8 Least Privilege — minimal ruxsat prinsipi

```
❌ Ilova DB foydalanuvchisi — "superuser" (BARCHA jadval, BARCHA
   amal) huquqiga ega

✅ Ilova DB foydalanuvchisi — FAQAT kerakli jadvallarga, FAQAT
   kerakli amallarga (SELECT/INSERT/UPDATE, lekin DROP TABLE EMAS)
   ruxsatga ega

GRANT SELECT, INSERT, UPDATE ON employees TO erp_app_user;
-- REVOKE DROP, TRUNCATE FROM erp_app_user; (yoki umuman BERILMASIN)
```

Agar ilova **buzilgan** (compromised) taqdirda ham — Least
Privilege tufayli hujumchi **faqat cheklangan** amal qila oladi
(butun DB'ni yo'q qila olmaydi).

### 3.9 appsettings.json'da HECH QACHON credential saqlamaslik

```json
// ❌ HECH QACHON
{ "ConnectionStrings": { "Default": "Host=prod;Password=RealPassword123!" } }

// ✅ Placeholder, haqiqiy qiymat Environment Variable orqali OVERRIDE qilinadi
{ "ConnectionStrings": { "Default": "" } }
```

## 4. Kod — to'liq amaliyot

```csharp
var builder = WebApplication.CreateBuilder(args);

// Konfiguratsiya ustuvorlik tartibi:
// appsettings.json (bo'sh/placeholder qiymatlar)
// → Environment Variables (haqiqiy qiymatlar, faqat serverda)
// → Azure Key Vault (production, enterprise)

if (builder.Environment.IsProduction())
{
    builder.Configuration.AddAzureKeyVault(
        new Uri(builder.Configuration["KeyVault:Uri"]!),
        new DefaultAzureCredential());
}
```

## 5. Qachon ishlatish kerak?

| Muhit | Yechim |
|---|---|
| Local Development | User Secrets |
| CI/CD Pipeline | GitHub/GitLab Secrets |
| Production, oddiy server | Environment Variables |
| Production, enterprise/audit talab qilinadi | Azure Key Vault/HashiCorp Vault |

## 6. Muhim nuqtalar

- Git tarixiga TUSHGAN maxfiy ma'lumot — `.gitignore` bilan
  KELAJAKDA oldini olinadi, lekin **ESKI** commit'lardan o'chirish
  UCHUN maxsus vosita (BFG) va kalitni **ALMASHTIRISH** shart.
- Least Privilege — DB foydalanuvchisi darajasida ham qo'llanilishi
  kerak, faqat application kodida emas.
- CI/CD Secret'lar — log'larda AVTOMATIK maskalanadi, lekin
  ATAYLAB `echo $SECRET` qilinsa — OSHKOR bo'lishi mumkin (buni
  HECH QACHON qilmaslik kerak).

## 7. Imtihon savollari

1. Nima uchun `.gitignore`ga qo'shish, allaqachon commit qilingan
   maxfiy faylni "xavfsiz" qilmaydi?
2. User Secrets qayerda saqlanadi va bu nima uchun git'ga tasodifan
   commit qilinishining oldini oladi?
3. Azure Key Vault oddiy Environment Variable'dan qanday
   afzalliklarga ega?
4. Credential Rotation nima va u qanday xavfni kamaytiradi?
5. Least Privilege prinsipi DB foydalanuvchisi darajasida qanday
   qo'llaniladi?
