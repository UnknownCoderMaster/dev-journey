# ASP.NET Core — Serve Static Files — Junior A

## 1. Nima? (Ta'rif)

**Static Files** — server o'zgartirmasdan, **to'g'ridan** client'ga
yuboradigan fayllar: HTML, CSS, JS, rasm, shrift. `UseStaticFiles()`
middleware — bu fayllarni HTTP orqali **xizmat qilish** imkonini
beradi.

## 2. Nima uchun kerak?

Har bir statik fayl uchun **Controller/Action** yozish — ortiqcha
va samarasiz. `UseStaticFiles()` — bu fayllarni **avtomatik**,
to'g'ridan xizmat qiladi (Controller pipeline'ni chetlab o'tib).

## 3. Ichida nima sodir bo'ladi? (Mexanizm)

### 3.1 `UseStaticFiles()` middleware

```csharp
var app = builder.Build();
app.UseStaticFiles(); // wwwroot papkasidagi fayllarni XIZMAT qiladi
```

```
Request: GET /images/logo.png
    │
    ▼
UseStaticFiles() — wwwroot/images/logo.png FAYLINI TOPADI
    │
    ├─ TOPILDI → FAYL to'g'ridan JAVOB sifatida QAYTARILADI
    │             (Controller/Routing UMUMAN ISHGA TUSHMAYDI!)
    └─ TOPILMADI → KEYINGI middleware'ga O'TADI (masalan routing)
```

### 3.2 `wwwroot` papkasi — default static files joyi

```
MyProject/
├── wwwroot/          ← STATIK fayllar SHU YERDA (DEFAULT)
│   ├── css/
│   ├── js/
│   └── images/
├── Controllers/
└── Program.cs
```

`wwwroot` ICHIDAGI fayllar — **loyiha ildizidan NISBIY EMAS**,
`https://example.com/css/site.css` kabi **to'g'ridan** ochiladi
(`wwwroot` prefiksi URL'da KO'RSATILMAYDI).

### 3.3 Custom path — `StaticFileOptions`

```csharp
app.UseStaticFiles(new StaticFileOptions
{
    FileProvider = new PhysicalFileProvider(Path.Combine(builder.Environment.ContentRootPath, "MyFiles")),
    RequestPath = "/files" // https://example.com/files/document.pdf → MyFiles/document.pdf
});
```

### 3.4 Directory Browsing

```csharp
app.UseDirectoryBrowser(new DirectoryBrowserOptions
{
    FileProvider = new PhysicalFileProvider(Path.Combine(app.Environment.ContentRootPath, "wwwroot/files")),
    RequestPath = "/files"
});
```

```
⚠️ XAVFSIZLIK: Directory Browsing — PAPKA ICHIDAGI BARCHA fayllar
   RO'YXATINI ko'rsatadi (masalan foydalanuvchi /files ga kirsa —
   BARCHA fayl nomlarini KO'RADI) — FAQAT ehtiyotkorlik bilan,
   MAXFIY bo'lmagan papkalarda ishlatilishi kerak.
```

### 3.5 Default files — `index.html`

```csharp
app.UseDefaultFiles(); // UseStaticFiles'DAN OLDIN chaqirilishi kerak!
app.UseStaticFiles();
```

```
GET / so'rovi — wwwroot/index.html (yoki default.html) ni
AVTOMATIK topadi va QAYTARADI (URL'da FAYL nomi KO'RSATILMASA HAM).
```

### 3.6 Cache-Control headers — browser caching

```csharp
app.UseStaticFiles(new StaticFileOptions
{
    OnPrepareResponse = ctx =>
    {
        ctx.Context.Response.Headers.CacheControl = "public,max-age=604800"; // 7 kun KESHLASH
    }
});
```

```
Cache-Control — BRAUZERGA "bu faylni QAYTA-QAYTA so'ramasdan,
YERLOKAL keshdan ISHLATISHNI" buyuradi — TARMOQ trafigini SEZILARLI
kamaytiradi (CSS/JS/rasm — KAMDAN-KAM o'zgaradi).
```

### 3.7 `FileExtensionContentTypeProvider` — MIME types

```csharp
var provider = new FileExtensionContentTypeProvider();
provider.Mappings[".myext"] = "application/x-custom"; // Custom MIME type QO'SHISH

app.UseStaticFiles(new StaticFileOptions { ContentTypeProvider = provider });
```

`Content-Type` — brauzerga faylni **QANDAY ko'rsatishni** (rasm
sifatida, yuklab olish sifatida) bildiradi — noto'g'ri MIME type
— brauzerni **chalkashtirishi** mumkin.

### 3.8 SPA (Single Page App) — `UseSpaStaticFiles()`

```csharp
builder.Services.AddSpaStaticFiles(config => config.RootPath = "ClientApp/dist");

app.UseSpaStaticFiles();
app.UseSpa(spa => spa.Options.SourcePath = "ClientApp");
```

React/Angular/Vue kabi SPA'larni ASP.NET Core bilan **BIRGA**
(bitta serverdan) xizmat qilish uchun.

### 3.9 CDN bilan birga ishlatish

```
Production'da — KATTA statik fayllar (rasm, video) — ODATDA
ASP.NET Core serveridan EMAS, alohida CDN (CloudFront, Cloudflare)
orqali xizmat qilinadi — bu, ASP.NET Core serverini "OG'IRLIKDAN"
OZOD qiladi, VA CDN — geografik jihatdan YAQINROQ joydan
YETKAZADI (TEZROQ).
```

### 3.10 Xavfsizlik — faqat kerakli fayllar

```
❌ appsettings.json, .env, .git — wwwroot ICHIDA BO'LMASLIGI kerak!
   (aks holda — https://example.com/appsettings.json — ochiq
   bo'lib qolishi mumkin!)

✅ wwwroot — FAQAT haqiqatda PUBLIC bo'lishi kerak bo'lgan fayllar
   (CSS, JS, rasm, umumiy hujjatlar)
```

## 4. Kod — to'liq sozlash

```csharp
var app = builder.Build();

app.UseDefaultFiles();
app.UseStaticFiles(new StaticFileOptions
{
    OnPrepareResponse = ctx => ctx.Context.Response.Headers.CacheControl = "public,max-age=86400"
});

app.UseRouting();
app.MapControllers();
```

## 5. Qachon ishlatish kerak?

| Vaziyat | Yechim |
|---|---|
| CSS, JS, rasm, umumiy hujjat | `UseStaticFiles()` (wwwroot) |
| Custom papka, boshqa URL prefiksi | `StaticFileOptions` |
| React/Angular SPA'ni birga xizmat qilish | `UseSpaStaticFiles()` |
| Katta hajmli, global tarqatish | CDN |

## 6. Muhim nuqtalar

- Directory Browsing — **default o'chirilgan**, faqat ANIQ zarur
  bo'lganda, MAXFIY bo'lmagan joyda yoqilishi kerak.
- Cache-Control — statik fayllar uchun **muhim performance
  optimallashtirish**, lekin **muntazam o'zgaradigan** fayllar uchun
  QISQA (yoki YO'Q) muddat bilan sozlanishi kerak.
- `wwwroot` — HECH QACHON maxfiy konfiguratsiya fayllarini
  saqlashi kerak EMAS.

## 7. Imtihon savollari

1. `UseStaticFiles()` middleware qanday ishlaydi va u Controller
   pipeline'dan qanday farq qiladi?
2. `wwwroot` papkasi nima uchun DEFAULT joy hisoblanadi?
3. Directory Browsing nima uchun xavfsizlik riski tug'diradi?
4. `UseDefaultFiles()` va `UseStaticFiles()` orasidagi tartib
   nima uchun muhim?
5. Cache-Control header statik fayllar uchun qanday performance
   foyda beradi?
6. Nima uchun katta hajmli fayllar uchun CDN tavsiya etiladi?
