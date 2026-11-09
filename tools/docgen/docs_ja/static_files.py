# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "Serve static files"
CATEGORY = "ASP.NET"
TITLE = "Statik Fayllarni Berish"
SUBTITLE = "wwwroot, keshlash va xavfsizlik"
FILENAME = "Serve static files.docx"


def build(d):
    h1(d, "1. wwwroot va UseStaticFiles")

    para(d, "ASP.NET Core statik fayllarni standart holda **bermaydi** — "
            "buni aniq yoqish kerak. Yoqilganda `wwwroot` papkasi ildiz "
            "bo'lib xizmat qiladi:")

    code(d, """app.UseStaticFiles();""")

    code(d, """wwwroot/
  css/site.css      ->  GET /css/site.css
  js/app.js         ->  GET /js/app.js
  images/logo.png   ->  GET /images/logo.png""")

    para(d, "Muhim xavfsizlik jihati: `wwwroot` dan tashqaridagi fayllar "
            "**hech qachon** berilmaydi. Shuning uchun `appsettings.json` "
            "yoki DLL fayllari tashqariga chiqmaydi — bu ataylab shunday.")

    h2(d, "Middleware tartibi")

    code(d, """app.UseStaticFiles();      // avval — arzon, tez
app.UseRouting();
app.UseAuthentication();
app.UseAuthorization();
app.MapControllers();""")

    para(d, "`UseStaticFiles()` ni zanjirning boshida qo'yaman: statik fayl "
            "so'rovi routing va avtorizatsiyadan o'tmasdan darhol javob "
            "oladi. Bu tezroq, lekin bir natijasi bor — **statik fayllar "
            "avtorizatsiyadan o'tmaydi**.")

    # ───────────────────────────────────────────
    h1(d, "2. Qo'shimcha papkani ulash")

    para(d, "`wwwroot` dan boshqa papkani ham berish mumkin — masalan "
            "yuklangan fayllar uchun:")

    code(d, """app.UseStaticFiles(new StaticFileOptions
{
    FileProvider = new PhysicalFileProvider(
        Path.Combine(builder.Environment.ContentRootPath, "uploads")),
    RequestPath = "/files"
});""")

    para(d, "Endi `uploads/invoice.pdf` fayli `GET /files/invoice.pdf` "
            "orqali ochiladi. Lekin bu yerda ehtiyot bo'lish kerak: "
            "foydalanuvchilar yuklagan fayllar hamma uchun ochiq bo'lib "
            "qoladi. Agar fayllar maxfiy bo'lsa, bu yondashuv mos emas.")

    # ───────────────────────────────────────────
    h1(d, "3. Himoyalangan fayllarni berish")

    para(d, "Faylni faqat ruxsati bor foydalanuvchiga berish kerak bo'lsa, "
            "statik fayl middleware'i yaramaydi. O'rniga endpoint yozaman:")

    code(d, """[Authorize]
[HttpGet("documents/{id:guid}")]
public async Task<IActionResult> Download(Guid id, CancellationToken ct)
{
    var document = await _service.FindAsync(id, ct);
    if (document is null) return NotFound();

    if (!await _authorization.CanReadAsync(User, document, ct))
        return Forbid();

    var stream = await _storage.OpenReadAsync(document.StorageKey, ct);
    return File(stream, document.ContentType, document.FileName);
}""")

    para(d, "`File()` yordamchisi `Content-Disposition` header'ini "
            "qo'yadi va oqimni to'g'ri uzatadi — butun faylni xotiraga "
            "o'qimaydi.")

    note(d, "Muhim",
         "Fayl nomini mijoz bergan qiymatdan olmaslik kerak. "
         "`document.FileName` bazadan keladi va u yuklash paytida "
         "tozalangan bo'lishi kerak, aks holda header'ga yot belgilar "
         "yoki yo'l tushib qolishi mumkin.")

    para(d, "Katta fayllar uchun esa eng yaxshi yechim — faylni ilovadan "
            "umuman o'tkazmaslik: obyekt saqlagichdan (S3, MinIO) "
            "presigned URL berish. Unda ilova faqat ruxsatni tekshiradi va "
            "qisqa muddatli havola qaytaradi.")

    # ───────────────────────────────────────────
    h1(d, "4. Keshlash")

    para(d, "Statik fayllar standart holda keshlanmaydi, ya'ni brauzer "
            "ularni har safar qayta so'raydi. Bu ortiqcha trafik:")

    code(d, """app.UseStaticFiles(new StaticFileOptions
{
    OnPrepareResponse = ctx =>
    {
        ctx.Context.Response.Headers.CacheControl = "public,max-age=31536000,immutable";
    }
});""")

    para(d, "Bir yillik kesh agressiv ko'rinadi, lekin fayl nomida versiya "
            "bo'lsa to'g'ri yechim. Versiyalanmagan fayl uzoq keshlansa, "
            "yangilanish foydalanuvchiga yetib bormaydi.")

    h2(d, "Cache busting")

    code(d, """<link rel="stylesheet" href="~/css/site.css" asp-append-version="true" />""")

    para(d, "`asp-append-version` fayl mazmunidan hash hisoblab URL ga "
            "qo'shadi: `/css/site.css?v=K1nZx...`. Fayl o'zgarsa hash "
            "o'zgaradi, demak URL ham o'zgaradi va brauzer yangisini oladi.")

    # ───────────────────────────────────────────
    h1(d, "5. MIME tur va noma'lum kengaytmalar")

    para(d, "Middleware fayl kengaytmasiga qarab `Content-Type` qo'yadi. "
            "Agar kengaytma noma'lum bo'lsa, fayl **berilmaydi** — bu "
            "xavfsizlik uchun qilingan standart:")

    code(d, """var provider = new FileExtensionContentTypeProvider();
provider.Mappings[".webmanifest"] = "application/manifest+json";
provider.Mappings[".avif"] = "image/avif";

app.UseStaticFiles(new StaticFileOptions
{
    ContentTypeProvider = provider,
    // ServeUnknownFileTypes = true    -- bundan qochaman
});""")

    para(d, "`ServeUnknownFileTypes = true` qo'yishdan qochaman: u har qanday "
            "faylni `application/octet-stream` bilan berishga ruxsat beradi, "
            "ya'ni papkaga tasodifan tushgan fayl ham tashqariga chiqadi. "
            "Aniq mapping qo'shish ancha xavfsiz.")

    # ───────────────────────────────────────────
    h1(d, "6. Boshqa tegishli middleware'lar")

    table(d, ["Middleware", "Vazifasi"],
          [["`UseStaticFiles()`", "Faylni berish"],
           ["`UseDefaultFiles()`", "Papka so'ralganda `index.html` ni topish"],
           ["`UseDirectoryBrowser()`", "Papka tarkibini ro'yxat qilib ko'rsatish"],
           ["`UseFileServer()`", "Yuqoridagi uchtasini birlashtiradi"]],
          widths=[5.4, 9.1])

    code(d, """app.UseDefaultFiles();     // UseStaticFiles dan OLDIN turishi kerak
app.UseStaticFiles();""")

    para(d, "Tartib muhim: `UseDefaultFiles()` so'rov yo'lini o'zgartiradi "
            "(`/` → `/index.html`) va keyin statik fayl middleware'i uni "
            "topadi. Teskari tartibda ishlamaydi.")

    note(d, "Diqqat",
         "`UseDirectoryBrowser()` ni production'da yoqmaslik kerak — u "
         "papka tarkibini oshkor qiladi va hujumchiga qanday fayllar "
         "borligini ko'rsatadi.")

    # ───────────────────────────────────────────
    h1(d, "7. SPA bilan birga ishlash")

    para(d, "React yoki Angular ilovasi bilan birga ishlaganda muammo "
            "shunday: `/orders/42` so'rovi brauzerda mijoz tomonidagi "
            "marshrut, lekin serverga ham yetib keladi va u bunday faylni "
            "topmaydi.")

    code(d, """app.UseStaticFiles();

app.MapControllers();

// API bo'lmagan hamma narsa index.html ga ketadi
app.MapFallbackToFile("index.html");""")

    para(d, "`MapFallbackToFile` eng oxirida turadi va faqat boshqa hech "
            "qanday endpoint mos kelmaganda ishlaydi. Shuning uchun API "
            "marshrutlari buzilmaydi — ular oldinroq topiladi.")

    # ───────────────────────────────────────────
    h1(d, "8. Production'da statik fayllarni kim beradi")

    para(d, "Kestrel statik fayllarni yaxshi beradi, lekin oldida reverse "
            "proxy bo'lsa (Nginx, IIS), bu ishni unga topshirish "
            "samaraliroq: fayl so'rovi .NET jarayoniga umuman yetib "
            "bormaydi.")

    code(d, """# Nginx
location /css/ {
    alias /var/www/app/wwwroot/css/;
    expires 1y;
    add_header Cache-Control "public, immutable";
}""")

    para(d, "Trafik katta bo'lsa keyingi qadam — CDN. Unda fayllar "
            "foydalanuvchiga eng yaqin tugundan beriladi va mening "
            "serverim faqat dinamik so'rovlar bilan shug'ullanadi.")

    sources(d, [
        ("Static files in ASP.NET Core",
         "https://learn.microsoft.com/en-us/aspnet/core/fundamentals/static-files"),
        ("Response caching in ASP.NET Core",
         "https://learn.microsoft.com/en-us/aspnet/core/performance/caching/response"),
        ("FileExtensionContentTypeProvider",
         "https://learn.microsoft.com/en-us/dotnet/api/microsoft.aspnetcore.staticfiles.fileextensioncontenttypeprovider"),
    ])
