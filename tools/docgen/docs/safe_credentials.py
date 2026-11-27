# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "Safe credentials"
CATEGORY = "Cybersecurity"
TITLE = "Maxfiy Ma'lumotlarni Xavfsiz Saqlash"
SUBTITLE = "Parollar, kalitlar va ulanish satrlari qayerda turishi kerak"
FILENAME = "Safe credentials.docx"


def build(d):
    h1(d, "1. Muammo nimada")

    para(d, "Har bir ilovaga sirlar kerak bo'ladi: baza paroli, API kalitlari, "
            "shifrlash kalitlari, tashqi xizmatlarning token lari. Savol — ular "
            "qayerda saqlanishi kerak.")

    para(d, "Eng oson yo'l — konfiguratsiya fayliga yozib qo'yish. Va aynan shu "
            "eng keng tarqalgan xavfsizlik nuqsoni hisoblanadi.")

    code(d, """// appsettings.json — git da turadi
{
  "ConnectionStrings": {
    "Default": "Host=prod-db;Database=app;Username=app;Password=Qwerty123!"
  }
}""")

    note(d, "Nega bu shunchaki \"noqulay\" emas, balki xavfli:",
         "Git ga tushgan sir butun tarixda qoladi. Keyingi commit da uni "
         "o'chirsam ham, u avvalgi commit lar ichida yashayveradi. Repozitoriy "
         "biror marta nusxalangan bo'lsa yoki ochiq bo'lib qolgan bo'lsa — sir "
         "allaqachon tarqalgan. GitHub ni avtomatik skanerlaydigan botlar "
         "yangi kalitni daqiqalar ichida topadi.")

    # ───────────────────────────────────────────
    h1(d, "2. Sirlarni saqlash joylari")

    table(d, ["Joy", "Qachon", "Xavfsizligi"],
          [["Konfiguratsiya fayli", "Hech qachon", "Yo'q"],
           ["User Secrets", "Faqat lokal ishlab chiqish", "O'rtacha"],
           ["Atrof-muhit o'zgaruvchilari", "Konteyner, oddiy joylashtirish", "O'rtacha"],
           ["Docker/Kubernetes secrets", "Konteyner orkestratsiyasi", "Yaxshi"],
           ["Sir omborlari (vault)", "Production", "Eng yaxshi"]],
          widths=[4.4, 6.0, 5.1])

    # ───────────────────────────────────────────
    h1(d, "3. User Secrets — lokal ishlab chiqish uchun")

    para(d, "`.NET` da lokal sirlarni loyihadan tashqarida saqlash uchun maxsus "
            "mexanizm bor. Fayl foydalanuvchi profilida yotadi va git ga "
            "tushmaydi.")

    code(d, """dotnet user-secrets init
dotnet user-secrets set "ConnectionStrings:Default" "Host=localhost;..."
dotnet user-secrets set "Jwt:Key" "..."
dotnet user-secrets list""")

    code(d, """# Fayl qayerda saqlanadi
Windows:  %APPDATA%\\Microsoft\\UserSecrets\\<id>\\secrets.json
Linux:    ~/.microsoft/usersecrets/<id>/secrets.json""")

    para(d, "`Development` muhitida bu manba avtomatik o'qiladi va "
            "`appsettings.json` ustiga qo'yiladi — kodda hech narsa o'zgarmaydi.")

    note(d, "Muhim cheklovni bilish kerak:",
         "User Secrets fayli **shifrlanmagan**. U faqat loyiha papkasidan "
         "tashqarida turadi, ya'ni tasodifan git ga tushmaydi. Mashinaga "
         "kirgan odam uni bemalol o'qiydi. Shuning uchun u faqat lokal "
         "ishlab chiqish uchun — production sirlari u yerda bo'lmasligi kerak.")

    # ───────────────────────────────────────────
    h1(d, "4. Atrof-muhit o'zgaruvchilari")

    code(d, """# Ikki nuqta o'rniga ikkita pastki chiziq
export ConnectionStrings__Default="Host=db;Database=app;Password=..."
export Jwt__Key="..."
""")

    code(d, """services:
  api:
    image: myapp:latest
    environment:
      - ASPNETCORE_ENVIRONMENT=Production
    env_file:
      - .env.production        # git da emas""")

    para(d, "`.NET` konfiguratsiya tizimi atrof-muhit o'zgaruvchilarini avtomatik "
            "o'qiydi va ierarxiyani `__` orqali tiklaydi.")

    note(d, "Atrof-muhit o'zgaruvchilarining ham chegarasi bor:",
         "Ular jarayonlar ro'yxatida ko'rinishi, xatolik hisobotlariga tushishi "
         "va bola jarayonlarga meros bo'lib o'tishi mumkin. Agar ilova xatolik "
         "paytida butun muhitni logga yozsa, barcha sirlar o'sha yerda bo'ladi. "
         "Shuning uchun bu — konfiguratsiya faylidan yaxshiroq, lekin eng yaxshi "
         "emas.")

    # ───────────────────────────────────────────
    h1(d, "5. Docker va Kubernetes secrets")

    code(d, """# Docker Swarm / Compose
services:
  api:
    secrets:
      - db_password
    environment:
      - DB_PASSWORD_FILE=/run/secrets/db_password

secrets:
  db_password:
    file: ./secrets/db_password.txt""")

    para(d, "Sir fayl sifatida konteyner ichiga ulanadi, atrof-muhit "
            "o'zgaruvchisiga tushmaydi. Ilova uni fayldan o'qiydi:")

    code(d, """var passwordFile = Environment.GetEnvironmentVariable("DB_PASSWORD_FILE");
var password = passwordFile is not null
    ? await File.ReadAllTextAsync(passwordFile)
    : Environment.GetEnvironmentVariable("DB_PASSWORD");""")

    code(d, """# Kubernetes
apiVersion: v1
kind: Secret
metadata:
  name: app-secrets
type: Opaque
stringData:
  ConnectionStrings__Default: "Host=db;Password=..."
""")

    note(d, "Kubernetes Secret haqida keng tarqalgan yanglishish:",
         "U Base64 da saqlanadi va buni ba'zan \"shifrlangan\" deb o'ylashadi. "
         "Base64 — bu kodlash, shifrlash emas; uni bir buyruq bilan ochish "
         "mumkin. Haqiqiy himoya uchun `etcd` darajasida shifrlash yoki tashqi "
         "sir ombori kerak bo'ladi.")

    # ───────────────────────────────────────────
    h1(d, "6. Sir omborlari")

    para(d, "Production uchun eng to'g'ri yechim — maxsus sir ombori. Ular "
            "quyidagilarni beradi: shifrlangan saqlash, kirish nazorati, audit "
            "jurnali va kalitlarni avtomatik aylantirish.")

    bullets(d, [
        "**HashiCorp Vault** — platformadan mustaqil, keng imkoniyatli.",
        "**Azure Key Vault** — Azure ekotizimi uchun.",
        "**AWS Secrets Manager** — AWS uchun.",
        "**Google Secret Manager** — GCP uchun.",
    ])

    code(d, """builder.Configuration.AddAzureKeyVault(
    new Uri($"https://{vaultName}.vault.azure.net/"),
    new DefaultAzureCredential());

// Keyin odatdagidek o'qiladi
var connectionString = builder.Configuration.GetConnectionString("Default");""")

    note(d, "Sir omborining eng qimmatli xususiyati — audit:",
         "Kim, qachon, qaysi sirni o'qiganini bilish mumkin. Agar sir sizib "
         "chiqsa, uning qayerdan ketganini aniqlash imkoni bo'ladi. "
         "Konfiguratsiya faylida esa bunday ma'lumot umuman yo'q.")

    # ───────────────────────────────────────────
    h1(d, "7. Sir tasodifan git ga tushsa")

    para(d, "Agar sir commit qilingan bo'lsa, uni faylni tahrirlash bilan "
            "yo'qotib bo'lmaydi. To'g'ri ketma-ketlik quyidagicha:")

    bullets(d, [
        "**Avval sirni bekor qilish** — parolni o'zgartirish, kalitni qayta "
        "yaratish. Bu eng muhim va eng birinchi qadam.",
        "Keyin kodni tuzatish va yangi sirni xavfsiz joyga ko'chirish.",
        "Repozitoriy tarixini tozalash — lekin bu sirni allaqachon olgan "
        "odamga ta'sir qilmaydi.",
        "Kirish loglarini tekshirish — sir ishlatilganmi.",
    ], numbered=True)

    code(d, """# Tarixdan o'chirish (git-filter-repo tavsiya etiladi)
git filter-repo --path appsettings.Production.json --invert-paths""")

    note(d, "Tartib shu bo'lishi kerak:",
         "Ko'pchilik birinchi navbatda tarixni tozalashga kirishadi. Lekin bu "
         "vaqt oladi, va o'sha vaqt davomida sir hamon amal qiladi. Birinchi "
         "qadam har doim — sirni **ishlamaydigan qilish**. Qolgani shundan "
         "keyin.")

    # ───────────────────────────────────────────
    h1(d, "8. Oldini olish choralari")

    h2(d, "8.1 .gitignore")

    code(d, """appsettings.Production.json
appsettings.*.Local.json
.env
.env.*
*.pfx
*.key
secrets/""")

    h2(d, "8.2 Avtomatik skanerlash")

    code(d, """# Pre-commit hook sifatida
gitleaks protect --staged --verbose""")

    code(d, """# GitHub Actions
- name: Secret scanning
  uses: gitleaks/gitleaks-action@v2""")

    h2(d, "8.3 Kodda tekshiruv")

    code(d, """var key = config["Jwt:Key"];

if (string.IsNullOrWhiteSpace(key) || key.Length < 32)
    throw new InvalidOperationException(
        "Jwt:Key sozlanmagan yoki juda qisqa");

if (app.Environment.IsProduction() && key.StartsWith("dev-"))
    throw new InvalidOperationException(
        "Production da ishlab chiqish kaliti ishlatilyapti");""")

    note(d, "Oxirgi tekshiruv menga bir marta yordam bergan:",
         "Staging muhitiga chiqarishda konfiguratsiya to'liq ko'chirilmagan edi "
         "va ilova lokal kalit bilan ishga tushmoqchi bo'ldi. Bu tekshiruv "
         "bo'lmasa, u jimgina ishlab ketardi va muammo ancha keyin — "
         "tokenlar mos kelmaganda ko'rinardi.")

    # ───────────────────────────────────────────
    h1(d, "9. Umumiy qoidalar")

    bullets(d, [
        "Sirni hech qachon kodga yoki git ga tushadigan faylga yozmaslik.",
        "Har bir muhit uchun alohida sir ishlatish — lokal kalit production da "
        "ishlamasin.",
        "Sirlarni muntazam aylantirish (rotate).",
        "Eng kam huquq tamoyili — har bir xizmatga faqat kerakli ruxsat.",
        "Sirlarni logga, xatolik hisobotiga va javob tanasiga chiqarmaslik.",
        "Jamoadan odam ketganda u bilgan sirlarni almashtirish.",
    ])

    # ───────────────────────────────────────────
    # ───────────────────────────────────────────
    h1(d, "10. Amaliyotdan: o'rin egalari va CI dagi qo'riqchi")

    para(d, "Ish joyimdagi MAD ERP tizimida qirqqa yaqin servis bor va har birining o'z "
            "konfiguratsiya fayli. 4-bo'limda aytilgan atrof-muhit o'zgaruvchilari "
            "yondashuvi tanlangan, lekin uni amalga oshirish usuli odatdagidan boshqacha.")

    h2(d, "10.1 Fayl tuzilishi qoladi, qiymatlar ketadi")

    para(d, "ASP.NET Core ning standart yo'li — `Redis__Password` ko'rinishidagi "
            "o'zgaruvchi berish, u fayldagi qiymatni ustidan yozadi. Bu yerda esa fayl "
            "o'z tuzilishini saqlab qoladi va qiymat o'rniga nom turadi:")

    code(d, """{
  "Idp": {
    "BaseUrl": "${idp_baseurl}",
    "ClientId": "${idp_clientid}",
    "ClientSecret": "${idp_clientsecret}"
  }
}""", caption="appsettings.Production.json")

    para(d, "Almashtirishni o'z kodimiz bajaradi — hech qanday `envsubst`, entrypoint "
            "skripti yoki tashqi paket yo'q. Devops faqat o'zgaruvchilarni o'rnatadi:")

    code(d, """foreach (var kvp in configuration.AsEnumerable())
{
    if (kvp.Value != null && kvp.Value.Contains("${"))
    {
        var updatedValue = kvp.Value;

        foreach (var env in Environment.GetEnvironmentVariables().Cast<DictionaryEntry>())
        {
            var placeholder = $"${{{env.Key}}}";

            if (updatedValue.Contains(placeholder))
                updatedValue = updatedValue.Replace(placeholder, env.Value?.ToString());
        }

        if (updatedValue != kvp.Value)
            configuration[kvp.Key] = updatedValue;
    }
}""", caption="Erp.Core/Extensions/ConfigurationExtensions.cs")

    para(d, "Standart usulga nisbatan yutug'i — hujjatlilik. Faylga qarab qaysi qiymat "
            "tashqaridan kelishini darhol ko'rish mumkin. Standart usulda fayldagi "
            "qiymat aldamchi bo'ladi: ko'rinib turgani amalda ishlatilmayotgan bo'lishi "
            "mumkin.")

    para(d, "Narxi ham bor. Agar o'zgaruvchi topilmasa, o'rin egasi o'z holida qoladi — "
            "hech qanday xato, ogohlantirish yoki log yo'q. Ilova ko'tariladi va muammo "
            "faqat o'sha qiymat ishlatilganda ochiladi. Linux da o'zgaruvchi nomi harf "
            "registriga sezgir, shuning uchun hamma o'rin egasi kichik harfda yozilgan.")

    h2(d, "10.2 Gitleaks — 8-bo'limdagi qoidaning amalga oshirilishi")

    para(d, "Sir git ga tushmasligini CI tekshiradi. `main` va `dev` ga yuborilgan har "
            "bir PR da Gitleaks o'z qoidalari bilan, ustiga `Password`, `ClientSecret` "
            "va `Key` naqshlari bo'yicha oddiy `git grep` ishga tushadi. Tekshiruv "
            "yiqilsa merge bloklanadi.")

    para(d, "O'rin egalari yondashuvi bu tekshiruv bilan yaxshi yarashadi: "
            "repozitoriyda `${idp_clientsecret}` satri turadi, u hech qanday naqshga "
            "tushmaydi, haqiqiy parol esa faqat devops registrida yashaydi.")

    note(d, "Lekin halol aytish kerak:",
         "`appsettings.Development.json` fayllarining ko'pida hali ham haqiqiy "
         "development parollari turadi. Ular Gitleaks ishga tushirilishidan oldin "
         "commit qilingan va hozir \"legacy\" deb qabul qilingan — tekshiruv faqat yangi "
         "o'zgarishlarni ushlaydi. 7-bo'limda aytilganidek, bir marta git ga tushgan "
         "sirni butunlay tozalash tarixni qayta yozishni talab qiladi, bu esa ko'p odam "
         "ishlaydigan repozitoriyda qimmat amal. Natijada ular o'z joyida qolgan. Men "
         "buni to'g'ri yechim deb hisoblamayman, lekin real loyihada shunday vaziyat "
         "uchrashini bilib qo'yish kerak: qoida kiritilgan sana va kod yozilgan sana "
         "bir xil emas.")

    h2(d, "10.3 Hamma narsani sir deb hisoblash ham xato")

    para(d, "Bir vaqt MinIO bucket nomi \"sozlamani markazlashtiramiz\" degan niyat "
            "bilan umumiy `${minio_bucket}` o'rin egasiga o'tkazildi. Natijada har bir "
            "servis o'z bucket iga yozishi kerak bo'lgan tizimda hamma bitta bucket ga "
            "ko'rsatib qoldi va Production da fayllar topilmay qoldi.")

    para(d, "Endpoint va bucket nomi — sir emas, ular manzil. Ularni yashirish hech "
            "narsa himoya qilmaydi, faqat servislar orasidagi farqni yo'q qiladi. "
            "Shundan keyin sir deb faqat `AccessKey` va `SecretKey` qoldirildi. "
            "Ya'ni \"nima sir, nima shunchaki sozlama\" degan savolni oldindan hal qilib "
            "qo'yish kerak — aks holda himoya choralari ishonchlilikni pasaytiradi.")

    h1(d, "11. Xulosa")

    bullets(d, [
        "Git ga tushgan sir butun tarixda qoladi — uni faqat bekor qilish "
        "bilan zararsizlantirish mumkin.",
        "User Secrets faqat lokal ishlab chiqish uchun; u shifrlanmagan.",
        "Atrof-muhit o'zgaruvchilari jarayonlar ro'yxatida va loglarda "
        "ko'rinishi mumkin.",
        "Kubernetes Secret Base64 da saqlanadi — bu shifrlash emas.",
        "Production uchun sir ombori eng to'g'ri yechim; u audit ham beradi.",
        "Sir sizib chiqsa, birinchi qadam — tarixni tozalash emas, sirni "
        "bekor qilish.",
        "`gitleaks` kabi vositalar sirni commit dan oldin aniqlaydi.",
        "Ilova ishga tushishida konfiguratsiya to'g'riligini tekshirish "
        "foydali.",
    ])

    sources(d, [
        ("Safe storage of app secrets in development in ASP.NET Core",
         "https://learn.microsoft.com/en-us/aspnet/core/security/app-secrets"),
        ("OWASP Secrets Management Cheat Sheet",
         "https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html"),
        ("Azure Key Vault configuration provider in ASP.NET Core",
         "https://learn.microsoft.com/en-us/aspnet/core/security/key-vault-configuration"),
        ("Removing sensitive data from a repository — GitHub Docs",
         "https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/removing-sensitive-data-from-a-repository"),
    ])
