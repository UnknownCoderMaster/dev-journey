# ASP.NET Core — Multiple Environments — Middle D

## 1. Nima? (Ta'rif)

**Environment** — ilova qaysi "muhit"da ishlayotganini (Development,
Staging, Production) bildiruvchi sozlama — bu asosida turli
konfiguratsiya, middleware, va xatti-harakat qo'llaniladi.

## 2. Nima uchun kerak?

Development'da — batafsil xato sahifasi, DB migratsiyasini avtomatik
qo'llash foydali. Production'da esa bu — **xavfsizlik zaifligi**
(ichki xatolarni oshkor qilish) va **xavfli** (avtomatik migratsiya —
nazoratsiz DB o'zgarishi). Environment mexanizmi — bir xil kod bazasi
BILAN turli muhitlarda **turlicha** ishlashni ta'minlaydi.

## 3. Ichida nima sodir bo'ladi? (Mexanizm)

### 3.1 `ASPNETCORE_ENVIRONMENT` — qanday o'qiladi

```
1. Ilova ishga tushganda — ASPNETCORE_ENVIRONMENT environment
   o'zgaruvchisi O'QILADI
2. Qiymat topilmasa — DEFAULT "Production" qabul qilinadi (XAVFSIZ DEFAULT!)
3. builder.Environment.EnvironmentName — shu qiymatni saqlaydi
```

```bash
# Linux/Mac
export ASPNETCORE_ENVIRONMENT=Development

# Windows PowerShell
$env:ASPNETCORE_ENVIRONMENT = "Development"

# Docker
docker run -e ASPNETCORE_ENVIRONMENT=Production myapp
```

### 3.2 appsettings.json — qatlamli yuklash

```
Yuklash TARTIBI (har keyingi — OLDINGISINI ustidan yozadi):

1. appsettings.json                          ← Barcha muhitlar uchun UMUMIY
2. appsettings.{Environment}.json             ← Muhitga XOS (masalan appsettings.Development.json)
3. Environment Variables                      ← ENG YUQORI ustuvorlik (deyarli)
4. Command-line arguments                     ← ENG YUQORI ustuvorlik

appsettings.json:            { "Logging": { "LogLevel": { "Default": "Warning" } } }
appsettings.Development.json: { "Logging": { "LogLevel": { "Default": "Debug" } } }

Development muhitida YAKUNIY qiymat: "Debug" (2-fayl 1-faylni QISMAN ustidan yozadi)
```

### 3.3 `IsDevelopment()` va boshqalar

```csharp
if (app.Environment.IsDevelopment())
{
    app.UseDeveloperExceptionPage(); // Batafsil stack trace
    app.UseSwagger();
    app.UseSwaggerUI();
}
else
{
    app.UseExceptionHandler("/error");
    app.UseHsts(); // HTTPS majburiy qilish header'i
}

// Boshqa muhitlar
if (app.Environment.IsStaging()) { /* ... */ }
if (app.Environment.IsProduction()) { /* ... */ }
if (app.Environment.IsEnvironment("QA")) { /* Custom muhit nomi */ }
```

### 3.4 Environment specific middleware

```csharp
var app = builder.Build();

app.UseHttpsRedirection();

if (app.Environment.IsDevelopment())
{
    app.UseCors(policy => policy.AllowAnyOrigin()); // Dev'da BO'SH CORS
}
else
{
    app.UseCors("ProductionCorsPolicy"); // Prod'da QATTIQ CORS
}
```

### 3.5 `launchSettings.json`

```json
{
  "profiles": {
    "https": {
      "commandName": "Project",
      "environmentVariables": {
        "ASPNETCORE_ENVIRONMENT": "Development"
      },
      "applicationUrl": "https://localhost:7001;http://localhost:5001"
    }
  }
}
```

`launchSettings.json` — **FAQAT local development** uchun (Visual
Studio/`dotnet run` orqali ishga tushirilganda) ishlaydi — bu fayl
**production serverga hech qanday ta'sir qilmaydi** va odatda
`.gitignore`ga QO'SHILMAYDI (chunki umumiy loyiha konfiguratsiyasi).

### 3.6 Docker va server'da Environment sozlash

```dockerfile
# Dockerfile
ENV ASPNETCORE_ENVIRONMENT=Production
```

```yaml
# docker-compose.yml
services:
  api:
    environment:
      - ASPNETCORE_ENVIRONMENT=Production
      - ConnectionStrings__DefaultConnection=Host=db;Database=erp
```

```
⚠️ MUHIM: Environment Variable ichida NESTED konfiguratsiya
   `__` (ikki pastki chiziq) orqali ifodalanadi:
   "ConnectionStrings:DefaultConnection" (appsettings.json'da)
   = "ConnectionStrings__DefaultConnection" (Environment Variable'da)
```

### 3.7 Secrets — User Secrets vs Environment Variables

```bash
# Development — User Secrets (loyiha papkasidan TASHQARIDA saqlanadi!)
dotnet user-secrets init
dotnet user-secrets set "ConnectionStrings:DefaultConnection" "Host=localhost;..."
```

```
User Secrets — %APPDATA%\Microsoft\UserSecrets\{guid}\secrets.json
(yoki Linux/Mac'da ~/.microsoft/usersecrets/{guid}/secrets.json)
da saqlanadi — LOYIHA PAPKASI ICHIDA EMAS, shuning uchun GIT'GA
TASODIFAN COMMIT QILINMAYDI.

Production — Environment Variables yoki Azure Key Vault/HashiCorp Vault
```

## 4. Kod — to'liq sozlash

```csharp
var builder = WebApplication.CreateBuilder(args);

// Konfiguratsiya avtomatik qatlamli yuklanadi:
// appsettings.json → appsettings.{env}.json → env vars → user secrets (dev'da)

var app = builder.Build();

app.MapGet("/env", () => app.Environment.EnvironmentName); // Diagnostika uchun

if (app.Environment.IsDevelopment())
    app.UseDeveloperExceptionPage();
else
    app.UseExceptionHandler("/error");
```

## 5. Qachon ishlatish kerak?

| Muhit | Xarakteristikasi |
|---|---|
| Development | Batafsil xato, Swagger ochiq, DB migratsiya avtomatik |
| Staging | Production'ga o'xshash, lekin test ma'lumotlari bilan |
| Production | Umumiy xato xabari, HSTS, CORS qattiq, Swagger yopiq/himoyalangan |

## 6. Muhim nuqtalar

- `appsettings.json`da HECH QACHON parol/API kalit saqlamang — hatto
  `.gitignore`ga qo'shilsa ham, xatolik ehtimoli yuqori.
- Production'da default `ASPNETCORE_ENVIRONMENT` o'rnatilmasa —
  "Production" deb qabul qilinadi (xavfsiz default xatti-harakat).
- `launchSettings.json` — faqat lokal, `dotnet publish` bilan
  YAYINLANGAN ilovaga TA'SIR QILMAYDI.

## 7. Imtihon savollari

1. `appsettings.json` va `appsettings.Development.json` qanday
   birlashtiriladi (qatlamli yuklash tartibi)?
2. `ASPNETCORE_ENVIRONMENT` o'rnatilmasa, default qanday qiymat
   qabul qilinadi va nima uchun bu xavfsiz?
3. Nested konfiguratsiya Environment Variable orqali qanday
   ifodalanadi?
4. User Secrets nima va u nima uchun `appsettings.Development.json`dan
   xavfsizroq?
5. `launchSettings.json` production deploy'ga ta'sir qiladimi?
6. Docker konteynerda environment qanday sozlanadi?
