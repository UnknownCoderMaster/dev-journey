# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = ".dockerignore"
CATEGORY = "Docker"
TITLE = ".dockerignore Fayli"
SUBTITLE = "Qurilish kontekstini cheklash va nega bu muhim"
FILENAME = "dockerignore fayli.docx"


def build(d):
    h1(d, "1. Qurilish konteksti")

    para(d, "`docker build` buyrug'i bajarilganda Docker ko'rsatilgan "
            "papkadagi **barcha fayllarni** demonga yuboradi. Bu to'plam "
            "qurilish konteksti deb ataladi.")

    code(d, """docker build -t myapp:latest .
#                              ↑
#                    shu papka butunlay yuboriladi""")

    para(d, "Hatto `Dockerfile` da ishlatilmaydigan fayllar ham yuboriladi, "
            "chunki Docker oldindan qaysi fayl kerakligini bilmaydi.")

    code(d, """Sending build context to Docker daemon  487.2MB""")

    note(d, "Bu satrni birinchi marta ko'rganimda hayron bo'lgandim:",
         "Loyihamning kodi bir necha megabayt edi, lekin kontekst yarim "
         "gigabaytga yetgandi. Sababi `bin`, `obj` va `.git` papkalari "
         "ekan — ular qurilish uchun umuman kerak emas, lekin baribir "
         "yuborilayotgandi. Har bir qurilish shu tufayli o'nlab soniya "
         "uzayardi.")

    # ───────────────────────────────────────────
    h1(d, "2. .dockerignore qanday ishlaydi")

    para(d, "`.dockerignore` fayli kontekstdan nimani chiqarib tashlashni "
            "belgilaydi. U `Dockerfile` bilan bir xil papkada turishi kerak "
            "va sintaksisi `.gitignore` ga o'xshaydi.")

    code(d, """# Qurilish natijalari
**/bin/
**/obj/
**/out/

# Versiya nazorati
.git/
.gitignore
.gitattributes

# IDE
.vs/
.vscode/
.idea/
*.user
*.suo

# Konteyner fayllari
**/Dockerfile*
docker-compose*.yml
.dockerignore

# Hujjatlar
**/*.md
docs/

# Sirlar — eng muhimi
**/appsettings.*.json
!**/appsettings.json
.env
.env.*
**/*.pfx
**/*.key""")

    h2(d, "2.1 Naqsh qoidalari")

    table(d, ["Naqsh", "Mosligi"],
          [["`bin/`", "Faqat ildizdagi `bin` papkasi"],
           ["`**/bin/`", "Istalgan chuqurlikdagi `bin` papkasi"],
           ["`*.md`", "Ildizdagi `.md` fayllari"],
           ["`**/*.md`", "Barcha `.md` fayllari"],
           ["`!README.md`", "Istisno — bu fayl qoldiriladi"],
           ["`temp?`", "`temp1`, `tempA` — bitta belgi"]],
          widths=[3.6, 11.9])

    note(d, "Tartib muhim:",
         "Istisno (`!`) o'zidan oldingi naqshni bekor qiladi. Agar men avval "
         "`!README.md` yozib, keyin `*.md` yozsam, istisno ishlamaydi — "
         "oxirgi mos kelgan qoida g'olib bo'ladi.")

    # ───────────────────────────────────────────
    h1(d, "3. Uchta asosiy foyda")

    h2(d, "3.1 Qurilish tezligi")

    para(d, "Kontekst kichik bo'lsa, u tezroq yuboriladi. Katta loyihalarda "
            "bu farq o'nlab soniyadan daqiqalargacha bo'lishi mumkin.")

    h2(d, "3.2 Kesh samaradorligi")

    para(d, "Bu eng muhim, lekin eng kam ma'lum foyda. `COPY . .` qatori "
            "kontekstdagi **har qanday** fayl o'zgarganda keshni buzadi.")

    code(d, """FROM mcr.microsoft.com/dotnet/sdk:10.0 AS build
WORKDIR /src
COPY . .
RUN dotnet restore
RUN dotnet publish -c Release -o /app""")

    note(d, "Mana shu yerda `.dockerignore` yo'qligi sezilarli zarar beradi:",
         "`obj` papkasi `.dockerignore` da bo'lmasa, lokal `dotnet build` "
         "qilganimda u o'zgaradi. Keyin `docker build` qilganimda Docker "
         "kontekst o'zgarganini ko'radi va `restore` dan boshlab hammasini "
         "qaytadan bajaradi — garchi kodim umuman o'zgarmagan bo'lsa ham. "
         "Bu har bir qurilishni daqiqalarga cho'zadi.")

    para(d, "Keshdan to'liq foydalanish uchun ko'p bosqichli qurilishda "
            "avval faqat loyiha fayllari nusxalanadi:")

    code(d, """FROM mcr.microsoft.com/dotnet/sdk:10.0 AS build
WORKDIR /src

# Avval faqat csproj — bu kamdan-kam o'zgaradi
COPY ["src/MyApp.Api/MyApp.Api.csproj", "src/MyApp.Api/"]
COPY ["src/MyApp.Domain/MyApp.Domain.csproj", "src/MyApp.Domain/"]
RUN dotnet restore "src/MyApp.Api/MyApp.Api.csproj"

# Keyin qolgan kod
COPY . .
RUN dotnet publish "src/MyApp.Api" -c Release -o /app --no-restore

FROM mcr.microsoft.com/dotnet/aspnet:10.0
WORKDIR /app
COPY --from=build /app .
ENTRYPOINT ["dotnet", "MyApp.Api.dll"]""")

    para(d, "Endi faqat kod o'zgarganda `restore` qaytadan bajarilmaydi — "
            "u keshdan olinadi.")

    h2(d, "3.3 Xavfsizlik")

    note(d, "Bu eng jiddiy sabab:",
         "`.env`, `appsettings.Production.json` yoki `.pfx` sertifikat "
         "fayli kontekstga tushsa va `COPY . .` bilan tasvirga ko'chirilsa, "
         "u tasvir qatlamlarida **abadiy** qoladi. Keyingi qatlamda "
         "`RUN rm secrets.json` yozsam ham — fayl oldingi qatlamda "
         "saqlanadi va uni `docker history` orqali chiqarib olish mumkin.")

    code(d, """# Tasvir qatlamlarini ko'rish
docker history myapp:latest --no-trunc

# Qatlamlarni ochib tekshirish
docker save myapp:latest -o image.tar
tar -xf image.tar""")

    para(d, "Agar tasvir ro'yxatga yuborilgan bo'lsa, sirni "
            "zararsizlantirishning yagona yo'li — uni bekor qilish.")

    # ───────────────────────────────────────────
    h1(d, "4. .gitignore bilan farqi")

    para(d, "Ikkala fayl o'xshash sintaksisga ega, lekin turli maqsad "
            "uchun mo'ljallangan va ularning mazmuni bir xil bo'lmasligi "
            "kerak.")

    table(d, ["Fayl", "Nima uchun"],
          [["`.gitignore`", "Nimani **versiyalash kerak emas**"],
           ["`.dockerignore`", "Nimani **tasvirga yuborish kerak emas**"]],
          widths=[4.0, 11.5])

    bullets(d, [
        "`.gitignore` da yo'q, lekin `.dockerignore` da bo'lishi kerak: "
        "`.git/`, `Dockerfile`, `README.md`, testlar.",
        "`.gitignore` da bor, lekin ba'zan kerak bo'ladi: ba'zi "
        "generatsiya qilingan fayllar.",
    ])

    note(d, "`.git/` ni chiqarib tashlash alohida e'tiborga loyiq:",
         "U odatda loyihadagi eng katta papkalardan biri va qurilish uchun "
         "umuman kerak emas. Bundan tashqari, agar tarixda biror paytda sir "
         "commit qilingan bo'lsa, u `.git` ichida yashab yotadi va tasvirga "
         "ko'chib o'tadi.")

    # ───────────────────────────────────────────
    h1(d, "5. Tekshirish")

    code(d, """# Kontekst hajmini ko'rish
docker build --no-cache --progress=plain -t test . 2>&1 | head -5""")

    code(d, """# Tasvir ichida nima borligini ko'rish
docker run --rm -it myapp:latest ls -la /app

# Yoki qobiq bilan
docker run --rm -it --entrypoint sh myapp:latest""")

    code(d, """# Tasvir hajmi va qatlamlari
docker images myapp
docker history myapp:latest""")

    note(d, "Oddiy tekshiruv usuli:",
         "Men tasvirni qurgandan keyin uning ichiga kirib, `appsettings.*` "
         "fayllarini ko'rib chiqaman. U yerda faqat `appsettings.json` "
         "bo'lishi kerak — muhitga xos fayllar esa atrof-muhit "
         "o'zgaruvchilari orqali kelishi lozim.")

    # ───────────────────────────────────────────
    h1(d, "6. `.NET` loyihasi uchun tayyor namuna")

    code(d, """# Qurilish natijalari
**/bin/
**/obj/
**/out/
**/publish/
**/TestResults/

# Versiya nazorati
.git/
.gitignore
.gitattributes
.github/

# IDE
.vs/
.vscode/
.idea/
*.user
*.suo
*.userprefs

# Konteyner
**/Dockerfile*
**/docker-compose*
.dockerignore

# Sirlar
**/appsettings.Development.json
**/appsettings.Local.json
**/appsettings.Production.json
.env
.env.*
**/*.pfx
**/*.p12
**/*.key
secrets/

# Hujjat va testlar
**/*.md
docs/
tests/

# Turli
**/node_modules/
**/.DS_Store
**/Thumbs.db
**/*.log""")

    note(d, "`tests/` ni chiqarib tashlash haqida:",
         "Agar testlar konteyner ichida bajarilmasa, ular tasvirga kerak "
         "emas. Lekin agar CI quvurida testlar konteynerda ishga "
         "tushirilsa, bu qatorni olib tashlash kerak bo'ladi. Shuning "
         "uchun bu — har bir loyihada alohida qaraladigan qaror.")

    # ───────────────────────────────────────────
    h1(d, "7. Xulosa")

    bullets(d, [
        "Docker qurilishda butun papkani demonga yuboradi — bu qurilish "
        "konteksti.",
        "`.dockerignore` kontekstdan fayllarni chiqarib tashlaydi.",
        "U `Dockerfile` bilan bir papkada turishi kerak.",
        "Kichik kontekst qurilishni tezlashtiradi va keshni samarali "
        "qiladi.",
        "`obj` va `bin` chiqarilmasa, lokal qurilish Docker keshini buzadi.",
        "Sirlar tasvir qatlamlarida abadiy qoladi — ularni keyin o'chirish "
        "yordam bermaydi.",
        "`.gitignore` va `.dockerignore` mazmuni bir xil bo'lmasligi "
        "kerak — `.git/` va `Dockerfile` faqat ikkinchisida bo'ladi.",
        "Tasvirni qurgandan keyin uning ichini tekshirish yaxshi odat.",
    ])

    sources(d, [
        ("Dockerfile reference — .dockerignore file",
         "https://docs.docker.com/reference/dockerfile/#dockerignore-file"),
        ("Building best practices — Docker Docs",
         "https://docs.docker.com/build/building/best-practices/"),
        ("Containerize a .NET app",
         "https://learn.microsoft.com/en-us/dotnet/core/docker/build-container"),
    ])
