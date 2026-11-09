# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "Use multiple environments"
CATEGORY = "ASP.NET"
TITLE = "Bir Nechta Muhit Bilan Ishlash"
SUBTITLE = "Development, Staging va Production uchun alohida sozlamalar"
FILENAME = "Use multiple environments.docx"


def build(d):
    h1(d, "1. Muhit tushunchasi")

    para(d, "Bitta ilova turli sharoitlarda ishlaydi: dasturchining kompyuterida, sinov "
            "serverida va real foydalanuvchilar uchun ochilgan serverda. Bu sharoitlarning "
            "har biri muhit (environment) deb ataladi va ularda ilovaning xatti-harakati "
            "turlicha bo'lishi kerak.")

    para(d, "ASP.NET Core joriy muhitni `ASPNETCORE_ENVIRONMENT` atrof-muhit o'zgaruvchisi "
            "orqali aniqlaydi. Uch nomli qiymat ramka tomonidan maxsus qo'llab-quvvatlanadi:")

    table(d, ["Qiymat", "Odatdagi vazifasi"],
          [["`Development`", "Dasturchi mashinasi: batafsil xatoliklar, API hujjati ochiq"],
           ["`Staging`", "Production ga yaqin sinov muhiti"],
           ["`Production`", "Real foydalanuvchilar; sukutdagi qiymat"]],
          widths=[3.6, 11.9])

    note(d, "Bu yerdagi eng muhim tafsilot:",
         "Agar `ASPNETCORE_ENVIRONMENT` umuman belgilanmasa, ilova o'zini `Production` "
         "deb hisoblaydi. Bu ataylab shunday qilingan — xavfsiz tomonga og'ish. "
         "Ya'ni serverga chiqarishda o'zgaruvchini qo'yishni unutsam, eng yomoni "
         "batafsil xatoliklar ko'rinmay qoladi, lekin sirlar ochilib ketmaydi.")

    # ───────────────────────────────────────────
    h1(d, "2. Muhitni belgilash")

    h2(d, "2.1 launchSettings.json")

    para(d, "Lokal ishga tushirishda muhit `Properties/launchSettings.json` faylidan "
            "o'qiladi. Bu fayl faqat dasturchi mashinasida ishlatiladi va serverga "
            "chiqmaydi.")

    code(d, """{
  "profiles": {
    "http": {
      "commandName": "Project",
      "applicationUrl": "http://localhost:5080",
      "environmentVariables": {
        "ASPNETCORE_ENVIRONMENT": "Development"
      }
    },
    "staging-local": {
      "commandName": "Project",
      "applicationUrl": "http://localhost:5081",
      "environmentVariables": {
        "ASPNETCORE_ENVIRONMENT": "Staging"
      }
    }
  }
}""")

    h2(d, "2.2 Atrof-muhit o'zgaruvchisi")

    code(d, """# Linux / macOS
export ASPNETCORE_ENVIRONMENT=Staging
dotnet MyApp.dll

# Windows PowerShell
$env:ASPNETCORE_ENVIRONMENT = "Staging"
dotnet MyApp.dll""")

    h2(d, "2.3 Docker va Compose")

    code(d, """services:
  api:
    image: myapp:latest
    environment:
      - ASPNETCORE_ENVIRONMENT=Production
      - ASPNETCORE_URLS=http://+:8080""")

    h2(d, "2.4 Buyruq qatori argumenti")

    code(d, """dotnet run --environment Staging""")

    # ───────────────────────────────────────────
    h1(d, "3. Muhitga bog'liq konfiguratsiya fayllari")

    para(d, "ASP.NET Core konfiguratsiyani bir nechta manbadan ketma-ket o'qiydi va "
            "keyingi manba oldingisini qayta yozadi:")

    bullets(d, [
        "`appsettings.json` — barcha muhitlar uchun umumiy qiymatlar.",
        "`appsettings.{Environment}.json` — faqat shu muhit uchun ustun keladigan qiymatlar.",
        "User secrets — faqat `Development` muhitida.",
        "Atrof-muhit o'zgaruvchilari.",
        "Buyruq qatori argumentlari.",
    ], numbered=True)

    code(d, """// appsettings.json
{
  "ConnectionStrings": { "Default": "Host=localhost;Database=app_dev" },
  "Logging": { "LogLevel": { "Default": "Information" } },
  "Features": { "EnableDetailedErrors": false }
}

// appsettings.Production.json
{
  "Logging": { "LogLevel": { "Default": "Warning" } }
}""")

    para(d, "Production muhitida log darajasi `Warning` bo'ladi, qolgan qiymatlar esa "
            "umumiy fayldan olinadi. Butun faylni takrorlash shart emas — faqat farq "
            "qiladigan kalitlar yoziladi.")

    note(d, "Birinchi paytlarda qilgan xatoyim:",
         "Men `appsettings.Production.json` ga butun konfiguratsiyani nusxalab "
         "qo'yardim. Natijada umumiy faylga yangi sozlama qo'shsam, uni production "
         "faylida ham qo'shishim kerak bo'lardi va bir necha marta buni unutdim. "
         "Hozir qoidam oddiy — muhit faylida faqat haqiqatan farq qiladigan kalitlar "
         "turadi.")

    note(d, "Parollar haqida:",
         "`appsettings.Production.json` ni git ga qo'yish — eng keng tarqalgan xavfsizlik "
         "xatosi. Production parollari konfiguratsiya faylida emas, atrof-muhit "
         "o'zgaruvchilarida yoki sir saqlovchi xizmatda bo'lishi kerak. Lokal ishlashda "
         "esa `dotnet user-secrets` bor — u faylni loyihadan tashqarida saqlaydi.")

    code(d, """dotnet user-secrets init
dotnet user-secrets set "ConnectionStrings:Default" "Host=localhost;Password=..." """)

    # ───────────────────────────────────────────
    h1(d, "4. Kodda muhitni tekshirish")

    code(d, """var builder = WebApplication.CreateBuilder(args);

if (builder.Environment.IsDevelopment())
{
    builder.Services.AddDbContext<AppDbContext>(o =>
        o.UseNpgsql(cs).EnableSensitiveDataLogging());
}
else
{
    builder.Services.AddDbContext<AppDbContext>(o => o.UseNpgsql(cs));
}

var app = builder.Build();

if (app.Environment.IsDevelopment())
{
    app.MapOpenApi();
    app.UseDeveloperExceptionPage();
}
else
{
    app.UseExceptionHandler("/error");
    app.UseHsts();
}""")

    h2(d, "4.1 Mavjud metodlar")

    table(d, ["Metod", "Tekshiradi"],
          [["`IsDevelopment()`", "Muhit `Development` mi"],
           ["`IsStaging()`", "Muhit `Staging` mi"],
           ["`IsProduction()`", "Muhit `Production` mi"],
           ["`IsEnvironment(\"QA\")`", "Ixtiyoriy nomli muhit"]],
          widths=[4.6, 10.9])

    para(d, "Nom taqqoslash registr hisobga olinmagan holda bajariladi, shuning uchun "
            "`development` va `Development` bir xil ishlaydi.")

    h2(d, "4.2 O'z muhitlarim")

    para(d, "Uchta standart nom bilan cheklanish shart emas. Masalan `QA` yoki `Demo` "
            "nomli muhit yaratish mumkin:")

    code(d, """if (app.Environment.IsEnvironment("QA"))
{
    app.UseMiddleware<FakePaymentMiddleware>();
}""")

    para(d, "Mos ravishda `appsettings.QA.json` fayli ham avtomatik o'qiladi.")

    # ───────────────────────────────────────────
    h1(d, "5. Muhitga bog'liq xizmat ro'yxatdan o'tkazish")

    para(d, "Ko'pincha muhitga qarab bir xil interfeysning turli amalga oshirilishi "
            "ulanadi:")

    code(d, """if (builder.Environment.IsDevelopment())
    builder.Services.AddSingleton<IEmailSender, ConsoleEmailSender>();
else
    builder.Services.AddSingleton<IEmailSender, SmtpEmailSender>();""")

    note(d, "Bu juda qulay yondashuv:",
         "Development da xat yuborish o'rniga uni konsolga chiqaradigan amalga oshirish "
         "ishlatiladi. Shunda sinov paytida hech kimga tasodifan xat ketib qolmaydi va "
         "SMTP server ham kerak emas. Lekin bunday almashtirishlar ko'payib ketmasligi "
         "kerak — aks holda lokal muhit production dan juda uzoqlashadi va u yerda "
         "ishlagan narsa serverda ishlamay qoladi.")

    # ───────────────────────────────────────────
    h1(d, "6. Amaliy maslahatlar")

    bullets(d, [
        "Staging ni Production ga iloji boricha yaqin tutish — bir xil baza turi, bir "
        "xil konfiguratsiya tuzilmasi.",
        "Muhitga bog'liq `if` larni `Program.cs` da to'plash; ular biznes mantiqqa "
        "tarqalmasligi kerak.",
        "Faqat `Development` da ochilishi kerak bo'lgan narsalarni (API hujjati, "
        "batafsil xatoliklar, sezgir loglar) aniq shart ichiga olish.",
        "Serverda muhit qiymati to'g'ri o'rnatilganini ishga tushgandan keyin tekshirish.",
    ])

    code(d, """app.MapGet("/health/env", (IWebHostEnvironment env) =>
    Results.Ok(new { env.EnvironmentName }));""",
         caption="Muhitni tez tekshirish uchun kichik endpoint")

    # ───────────────────────────────────────────
    h1(d, "7. Xulosa")

    bullets(d, [
        "Muhit `ASPNETCORE_ENVIRONMENT` o'zgaruvchisi bilan belgilanadi; belgilanmasa "
        "`Production` deb olinadi.",
        "`appsettings.{Environment}.json` umumiy faylning ustiga qo'yiladi — unda faqat "
        "farqlar yoziladi.",
        "`launchSettings.json` faqat lokal ishga tushirishda ishlaydi, serverga chiqmaydi.",
        "Production sirlari konfiguratsiya faylida emas, atrof-muhit o'zgaruvchilarida "
        "saqlanishi kerak.",
        "`IsDevelopment()`, `IsProduction()`, `IsEnvironment()` metodlari bilan kodda "
        "muhit tekshiriladi.",
        "O'z nomli muhitlar yaratish mumkin va ular uchun mos konfiguratsiya fayli "
        "avtomatik o'qiladi.",
    ])

    sources(d, [
        ("Use multiple environments in ASP.NET Core",
         "https://learn.microsoft.com/en-us/aspnet/core/fundamentals/environments"),
        ("Configuration in ASP.NET Core",
         "https://learn.microsoft.com/en-us/aspnet/core/fundamentals/configuration/"),
        ("Safe storage of app secrets in development",
         "https://learn.microsoft.com/en-us/aspnet/core/security/app-secrets"),
    ])
