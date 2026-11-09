# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "GitHub Actions basics"
CATEGORY = "CI/CD"
TITLE = "GitHub Actions Asoslari"
SUBTITLE = "Avtomatik qurilish, test va joylashtirish"
FILENAME = "GitHub Actions basics.docx"


def build(d):
    h1(d, "1. CI/CD nima beradi")

    para(d, "Uzluksiz integratsiya (CI) — har bir o'zgarish avtomatik "
            "qurilishi va sinovdan o'tishi. Uzluksiz yetkazish (CD) — "
            "sinovdan o'tgan kod avtomatik joylashtirilishi.")

    para(d, "Asosiy foyda — xatolik imkon qadar erta aniqlanadi. Kod "
            "birlashtirilganda emas, pull request yaratilganda "
            "tekshiriladi.")

    note(d, "Men bu farqni amalda sezganman:",
         "CI yo'q paytda \"menda ishlayapti\" degan holat tez-tez "
         "uchrardi — kimdir paketni qo'shishni unutgan yoki fayl "
         "commit qilinmagan bo'lardi. CI toza muhitda quradi, shuning "
         "uchun bunday xatolar darhol ko'rinadi.")

    # ───────────────────────────────────────────
    h1(d, "2. Asosiy tushunchalar")

    table(d, ["Tushuncha", "Ma'nosi"],
          [["Workflow", "Butun jarayon; `.github/workflows/` dagi YAML fayl"],
           ["Event", "Nima ishga tushiradi — `push`, `pull_request`"],
           ["Job", "Mustaqil bajariladigan qadamlar guruhi"],
           ["Step", "Bitta amal — buyruq yoki tayyor action"],
           ["Runner", "Jarayon bajariladigan mashina"],
           ["Action", "Qayta ishlatiladigan qadam"]],
          widths=[3.4, 12.1])

    # ───────────────────────────────────────────
    h1(d, "3. Oddiy workflow")

    code(d, """# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: .NET o'rnatish
        uses: actions/setup-dotnet@v4
        with:
          dotnet-version: '10.0.x'

      - name: Paketlarni tiklash
        run: dotnet restore

      - name: Qurish
        run: dotnet build --no-restore --configuration Release

      - name: Testlar
        run: dotnet test --no-build --configuration Release --verbosity normal""")

    note(d, "`--no-restore` va `--no-build` bayroqlari muhim:",
         "Ularsiz har bir qadam oldingisini qaytadan bajaradi — `test` "
         "buyrug'i o'zi qurishni ham boshlaydi. Natijada bir xil ish "
         "uch marta qilinadi va quvur bir necha daqiqa uzayadi.")

    # ───────────────────────────────────────────
    h1(d, "4. Keshlash")

    para(d, "NuGet paketlarini har safar yuklab olish vaqt oladi. Keshlash "
            "buni sezilarli tezlashtiradi.")

    code(d, """      - name: NuGet keshi
        uses: actions/cache@v4
        with:
          path: ~/.nuget/packages
          key: ${{ runner.os }}-nuget-${{ hashFiles('**/*.csproj') }}
          restore-keys: |
            ${{ runner.os }}-nuget-""")

    para(d, "`setup-dotnet` action ning o'zida ham keshlash mavjud:")

    code(d, """      - uses: actions/setup-dotnet@v4
        with:
          dotnet-version: '10.0.x'
          cache: true
          cache-dependency-path: '**/packages.lock.json'""")

    note(d, "Kesh kaliti to'g'ri tanlanishi kerak:",
         "`hashFiles('**/*.csproj')` — loyiha fayllari o'zgarmasa, kesh "
         "ishlatiladi. Agar kalitni doimiy qilsam, yangi paket "
         "qo'shilganda ham eski kesh olinadi va qurilish buziladi. "
         "`restore-keys` esa aniq moslik topilmasa, eng yaqinini "
         "ishlatadi — bu qisman tezlashtirish beradi.")

    # ───────────────────────────────────────────
    h1(d, "5. Xizmatlar bilan test")

    para(d, "Integratsiya testlari uchun baza kerak bo'ladi. Uni workflow "
            "ichida konteyner sifatida ko'tarish mumkin:")

    code(d, """jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:17-alpine
        env:
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
          POSTGRES_DB: testdb
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-dotnet@v4
        with:
          dotnet-version: '10.0.x'

      - name: Integratsiya testlari
        run: dotnet test
        env:
          ConnectionStrings__Default: >-
            Host=localhost;Port=5432;Database=testdb;Username=test;Password=test""")

    note(d, "`health-cmd` ni yozishni unutmaslik kerak:",
         "Konteyner ishga tushgani bilan baza hali ulanishga tayyor "
         "bo'lmasligi mumkin. Sog'liq tekshiruvisiz testlar baza "
         "tayyor bo'lgunicha ishga tushadi va tasodifiy xatolar beradi. "
         "Bunday nosozlikni topish juda qiyin, chunki u faqat ba'zan "
         "chiqadi.")

    # ───────────────────────────────────────────
    h1(d, "6. Sirlar bilan ishlash")

    code(d, """      - name: Docker Hub ga kirish
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKERHUB_USERNAME }}
          password: ${{ secrets.DOCKERHUB_TOKEN }}""")

    bullets(d, [
        "Sirlar repozitoriy sozlamalarida yoki tashkilot darajasida "
        "saqlanadi.",
        "Ular loglarda avtomatik yashiriladi — qiymat o'rniga `***` "
        "chiqadi.",
        "Fork dan kelgan pull request larda sirlar berilmaydi.",
    ])

    note(d, "Oxirgi punkt ataylab shunday qilingan:",
         "Agar sirlar fork dan kelgan PR da mavjud bo'lsa, har kim "
         "repozitoriyni fork qilib, sirlarni chop etadigan workflow "
         "yozishi mumkin bo'lardi. Shuning uchun bunday PR lar uchun "
         "alohida, sirlarsiz quvur tuziladi.")

    # ───────────────────────────────────────────
    h1(d, "7. Docker tasvir qurish")

    code(d, """  docker:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'

    steps:
      - uses: actions/checkout@v4

      - uses: docker/setup-buildx-action@v3

      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - name: Qurish va yuborish
        uses: docker/build-push-action@v6
        with:
          context: .
          push: true
          tags: |
            ghcr.io/${{ github.repository }}:latest
            ghcr.io/${{ github.repository }}:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max""")

    note(d, "`needs: test` bog'liqlikni belgilaydi:",
         "Usiz `docker` vazifasi `test` bilan parallel ishlaydi va "
         "testlar yiqilsa ham tasvir qurilib, yuborilib ketadi. "
         "`needs` esa ketma-ketlikni ta'minlaydi.")

    note(d, "Teg sifatida `latest` bilan birga `sha` ni ham qo'yaman:",
         "`latest` qulay, lekin u o'zgarib turadi — ikki kun oldin "
         "joylashtirilgan `latest` bugungisidan boshqa. `sha` tegi esa "
         "aniq commit ni ko'rsatadi va orqaga qaytarish kerak bo'lganda "
         "qaysi versiyaga qaytishni aniq bilish imkonini beradi.")

    # ───────────────────────────────────────────
    h1(d, "8. Matritsali qurilish")

    code(d, """jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, windows-latest]
        dotnet: ['8.0.x', '10.0.x']

    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-dotnet@v4
        with:
          dotnet-version: ${{ matrix.dotnet }}
      - run: dotnet test""")

    para(d, "Bu konfiguratsiya to'rtta kombinatsiyani parallel sinaydi. "
            "`fail-fast: false` birortasi yiqilsa ham qolganlarini davom "
            "ettiradi.")

    # ───────────────────────────────────────────
    h1(d, "9. Foydali qo'shimchalar")

    h2(d, "9.1 Zaif paketlarni tekshirish")

    code(d, """      - name: Zaifliklarni tekshirish
        run: |
          dotnet list package --vulnerable --include-transitive 2>&1 | tee out.txt
          ! grep -q "has the following vulnerable packages" out.txt""")

    h2(d, "9.2 Formatlashni tekshirish")

    code(d, """      - run: dotnet format --verify-no-changes""")

    h2(d, "9.3 Test natijalarini chop etish")

    code(d, """      - name: Testlar
        run: dotnet test --logger "trx;LogFileName=results.trx"

      - name: Natijalarni chop etish
        uses: dorny/test-reporter@v1
        if: always()
        with:
          name: Test natijalari
          path: '**/results.trx'
          reporter: dotnet-trx""")

    para(d, "`if: always()` sharti testlar yiqilganda ham hisobot "
            "chop etilishini ta'minlaydi — aks holda eng kerakli "
            "paytda u ko'rinmaydi.")

    # ───────────────────────────────────────────
    h1(d, "10. Amaliy maslahatlar")

    bullets(d, [
        "Action versiyalarini aniq belgilash — `@v4`, `@main` emas.",
        "Uzoq vazifalarni ajratish va `needs` bilan bog'lash.",
        "Keshlashni ishlatish — quvur vaqti sezilarli qisqaradi.",
        "`main` shoxiga to'g'ridan-to'g'ri push ni cheklash va CI ni "
        "majburiy qilish.",
        "Sirlarni hech qachon workflow fayliga yozmaslik.",
        "`workflow_dispatch` qo'shish — qo'lda ishga tushirish imkonini "
        "beradi.",
    ])

    code(d, """on:
  push:
    branches: [main]
  workflow_dispatch:        # qo'lda ishga tushirish tugmasi""")

    # ───────────────────────────────────────────
    h1(d, "11. Xulosa")

    bullets(d, [
        "Workflow `.github/workflows/` papkasidagi YAML fayl.",
        "Job lar sukut bo'yicha parallel; ketma-ketlik `needs` bilan "
        "beriladi.",
        "`--no-restore` va `--no-build` takroriy ishni oldini oladi.",
        "Keshlash quvur vaqtini sezilarli qisqartiradi; kalit loyiha "
        "fayllari hash iga bog'lanadi.",
        "`services` bloki integratsiya testlari uchun baza ko'taradi — "
        "sog'liq tekshiruvi bilan.",
        "Sirlar loglarda yashiriladi va fork dan kelgan PR larda "
        "berilmaydi.",
        "Tasvirga `latest` bilan birga `sha` tegini ham qo'yish orqaga "
        "qaytarishni osonlashtiradi.",
        "Action versiyalarini aniq belgilash kerak.",
    ])

    sources(d, [
        ("GitHub Actions documentation",
         "https://docs.github.com/en/actions"),
        ("Building and testing .NET — GitHub Docs",
         "https://docs.github.com/en/actions/tutorials/build-and-test-code/net"),
        ("Using secrets in GitHub Actions",
         "https://docs.github.com/en/actions/concepts/security/secrets"),
        ("Caching dependencies to speed up workflows",
         "https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/cache-dependencies"),
    ])
