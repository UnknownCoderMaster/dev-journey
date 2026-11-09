# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "GitLab CI/CD basics"
CATEGORY = "CI/CD"
TITLE = "GitLab CI/CD Asoslari"
SUBTITLE = "Quvur bosqichlari, runner lar va artefaktlar"
FILENAME = "GitLab CI-CD basics.docx"


def build(d):
    h1(d, "1. Asosiy tushunchalar")

    para(d, "GitLab CI/CD repozitoriy ildizidagi `.gitlab-ci.yml` fayli "
            "orqali sozlanadi. Fayl o'zgarishi bilan quvur ham "
            "o'zgaradi — ya'ni konfiguratsiya kod bilan birga "
            "versiyalanadi.")

    table(d, ["Tushuncha", "Ma'nosi"],
          [["Pipeline", "Butun jarayon"],
           ["Stage", "Bosqich; ichidagi vazifalar parallel bajariladi"],
           ["Job", "Bitta vazifa"],
           ["Runner", "Vazifani bajaradigan agent"],
           ["Artifact", "Vazifadan keyin saqlanadigan fayllar"],
           ["Cache", "Vazifalar orasida qayta ishlatiladigan fayllar"]],
          widths=[3.2, 12.3])

    note(d, "Stage va job munosabati muhim:",
         "Bitta bosqichdagi vazifalar bir vaqtda ishlaydi. Keyingi "
         "bosqich esa oldingisi to'liq tugagandan keyin boshlanadi. "
         "Shuning uchun bir-biriga bog'liq bo'lmagan ishlarni bitta "
         "bosqichga qo'ysam, quvur tezroq tugaydi.")

    # ───────────────────────────────────────────
    h1(d, "2. Oddiy quvur")

    code(d, """# .gitlab-ci.yml
stages:
  - build
  - test
  - package
  - deploy

variables:
  DOTNET_CLI_TELEMETRY_OPTOUT: "1"
  DOTNET_NOLOGO: "true"
  NUGET_PACKAGES: "$CI_PROJECT_DIR/.nuget/packages"

default:
  image: mcr.microsoft.com/dotnet/sdk:10.0
  cache:
    key:
      files:
        - "**/*.csproj"
    paths:
      - .nuget/packages

build:
  stage: build
  script:
    - dotnet restore
    - dotnet build --no-restore -c Release
  artifacts:
    paths:
      - "**/bin/Release/"
    expire_in: 1 hour

test:
  stage: test
  script:
    - dotnet test --no-build -c Release --logger "junit;LogFilePath=results.xml"
  artifacts:
    when: always
    reports:
      junit: "**/results.xml\"""")

    note(d, "`artifacts: when: always` — kichik, lekin muhim tafsilot:",
         "Sukut bo'yicha artefaktlar faqat vazifa muvaffaqiyatli "
         "bo'lganda saqlanadi. Lekin test natijalari aynan testlar "
         "yiqilganda kerak bo'ladi. `when: always` shuni ta'minlaydi.")

    # ───────────────────────────────────────────
    h1(d, "3. Artefaktlar va kesh farqi")

    table(d, ["Jihat", "Artifact", "Cache"],
          [["Maqsadi", "Natijani uzatish va saqlash", "Tezlashtirish"],
           ["Bosqichlar aro", "Avtomatik uzatiladi", "Kalit bo'yicha"],
           ["Quvurlar aro", "Yo'q", "Ha"],
           ["Interfeysda ko'rinadi", "Ha, yuklab olish mumkin", "Yo'q"],
           ["Yo'qolsa", "Vazifa yiqiladi", "Qaytadan yaratiladi"]],
          widths=[4.0, 6.0, 5.5])

    note(d, "Bu farqni tushunmaslik keng tarqalgan xato:",
         "Men avval NuGet paketlarini artefakt sifatida uzatardim — bu "
         "ishladi, lekin har bir vazifada ularni yuklash va chiqarish "
         "vaqt olardi. Kesh esa runner da qoladi va keyingi quvurda ham "
         "ishlatiladi. Qoida oddiy: **ishlab chiqarilgan narsa** — "
         "artefakt, **yuklab olingan narsa** — kesh.")

    # ───────────────────────────────────────────
    h1(d, "4. Xizmatlar bilan test")

    code(d, """integration-test:
  stage: test
  services:
    - name: postgres:17-alpine
      alias: postgres
  variables:
    POSTGRES_USER: test
    POSTGRES_PASSWORD: test
    POSTGRES_DB: testdb
    ConnectionStrings__Default: >-
      Host=postgres;Port=5432;Database=testdb;Username=test;Password=test
  script:
    - dotnet test tests/MyApp.IntegrationTests --no-build -c Release""")

    note(d, "Xizmat nomi host nomi bo'ladi:",
         "`Host=postgres` — bu `alias` qiymati. GitLab Actions dagi kabi "
         "`localhost` emas, chunki vazifa ham konteynerda ishlaydi va "
         "xizmat alohida konteynerda turadi. Bu ikki tizim orasidagi "
         "sezilarli farq va ko'chirishda ko'p vaqt oladi.")

    # ───────────────────────────────────────────
    h1(d, "5. Docker tasvir qurish")

    code(d, """package:
  stage: package
  image: docker:27
  services:
    - docker:27-dind
  variables:
    DOCKER_TLS_CERTDIR: "/certs"
  before_script:
    - echo "$CI_REGISTRY_PASSWORD" | docker login -u "$CI_REGISTRY_USER" \\
        --password-stdin "$CI_REGISTRY"
  script:
    - docker build -t "$CI_REGISTRY_IMAGE:$CI_COMMIT_SHORT_SHA" .
    - docker tag "$CI_REGISTRY_IMAGE:$CI_COMMIT_SHORT_SHA" \\
                 "$CI_REGISTRY_IMAGE:latest"
    - docker push "$CI_REGISTRY_IMAGE:$CI_COMMIT_SHORT_SHA"
    - docker push "$CI_REGISTRY_IMAGE:latest"
  rules:
    - if: $CI_COMMIT_BRANCH == "main\"""")

    para(d, "`CI_REGISTRY_*` o'zgaruvchilari GitLab tomonidan avtomatik "
            "beriladi — ularni qo'lda sozlash shart emas.")

    # ───────────────────────────────────────────
    h1(d, "6. Qoidalar — rules")

    code(d, """deploy-staging:
  stage: deploy
  script:
    - ./deploy.sh staging
  rules:
    - if: $CI_COMMIT_BRANCH == "develop"

deploy-production:
  stage: deploy
  script:
    - ./deploy.sh production
  rules:
    - if: $CI_COMMIT_TAG =~ /^v\\d+\\.\\d+\\.\\d+$/
      when: manual
  environment:
    name: production
    url: https://api.example.com""")

    note(d, "`when: manual` production uchun men doim qo'yaman:",
         "Quvur hamma narsani tayyorlab qo'yadi, lekin oxirgi qadamni "
         "odam bosadi. Bu avtomatlashtirishni yo'qotmaydi — hamma ish "
         "allaqachon qilingan, faqat \"ha\" deyish qoladi. Lekin "
         "tasodifan production ga chiqib ketish imkonini butunlay "
         "yopadi.")

    h2(d, "6.1 Keng tarqalgan shartlar")

    code(d, """rules:
  # Faqat merge request da
  - if: $CI_PIPELINE_SOURCE == "merge_request_event"

  # Faqat asosiy shoxda
  - if: $CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH

  # Ma'lum fayllar o'zgarganda
  - changes:
      - src/**/*
      - Dockerfile

  # Vazifani o'tkazib yuborish
  - if: $CI_COMMIT_MESSAGE =~ /\\[skip ci\\]/
    when: never""")

    # ───────────────────────────────────────────
    h1(d, "7. Runner turlari")

    table(d, ["Turi", "Xususiyati"],
          [["Shared", "GitLab tomonidan beriladi; daqiqalar cheklangan"],
           ["Group", "Guruh loyihalari uchun umumiy"],
           ["Project", "Faqat bitta loyihaga biriktirilgan"],
           ["Self-hosted", "O'z serveringizda; to'liq nazorat"]],
          widths=[3.2, 12.3])

    code(d, """# O'z runner ini o'rnatish
sudo gitlab-runner register \\
  --url https://gitlab.com/ \\
  --token glrt-... \\
  --executor docker \\
  --docker-image mcr.microsoft.com/dotnet/sdk:10.0""")

    code(d, """# Teg bo'yicha runner tanlash
build:
  tags:
    - docker
    - linux""")

    note(d, "O'z runner i qachon kerak bo'ladi:",
         "Ichki tarmoqdagi serverga joylashtirish kerak bo'lganda, yoki "
         "shared runner daqiqalari tugaganda, yoki qurilish juda ko'p "
         "resurs talab qilganda. Lekin uni saqlab turish ham ish — "
         "yangilash, disk tozalash, xavfsizlik. Shuning uchun imkon "
         "bo'lsa shared runner da qolaman.")

    # ───────────────────────────────────────────
    h1(d, "8. O'zgaruvchilar va sirlar")

    code(d, """# .gitlab-ci.yml da — ochiq qiymatlar
variables:
  ASPNETCORE_ENVIRONMENT: "Production"

# Settings → CI/CD → Variables da — sirlar
# DB_PASSWORD, API_KEY, SSH_PRIVATE_KEY""")

    bullets(d, [
        "**Masked** — qiymat loglarda yashiriladi.",
        "**Protected** — faqat himoyalangan shox va teglarda beriladi.",
        "**File** — qiymat vaqtinchalik faylga yoziladi.",
    ])

    code(d, """deploy:
  before_script:
    - mkdir -p ~/.ssh
    - cp "$SSH_PRIVATE_KEY" ~/.ssh/id_ed25519
    - chmod 600 ~/.ssh/id_ed25519
    - ssh-keyscan -H "$DEPLOY_HOST" >> ~/.ssh/known_hosts""")

    note(d, "`File` turidagi o'zgaruvchi SSH kaliti uchun juda qulay:",
         "Oddiy matn o'zgaruvchisida ko'p qatorli kalitni saqlash "
         "muammoli — qator ko'chirishlari yo'qoladi. `File` turi esa "
         "qiymatni faylga yozadi va yo'lni o'zgaruvchiga beradi.")

    # ───────────────────────────────────────────
    h1(d, "9. GitHub Actions bilan taqqoslash")

    table(d, ["Jihat", "GitLab CI", "GitHub Actions"],
          [["Fayl joyi", "`.gitlab-ci.yml` (ildizda)",
            "`.github/workflows/*.yml`"],
           ["Tuzilma", "Stage → Job", "Workflow → Job → Step"],
           ["Qayta ishlatish", "`include`, `extends`", "Action lar"],
           ["Xizmat manzili", "Alias nomi", "`localhost`"],
           ["Qo'lda tasdiqlash", "`when: manual`", "Environment approval"]],
          widths=[3.4, 6.0, 6.1])

    # ───────────────────────────────────────────
    h1(d, "10. Konfiguratsiyani bo'lish")

    code(d, """# .gitlab-ci.yml
include:
  - local: '.gitlab/ci/build.yml'
  - local: '.gitlab/ci/test.yml'
  - local: '.gitlab/ci/deploy.yml'""")

    code(d, """# Shablon orqali takrorlanishni kamaytirish
.dotnet-base:
  image: mcr.microsoft.com/dotnet/sdk:10.0
  cache:
    key:
      files: ["**/*.csproj"]
    paths: [.nuget/packages]

build:
  extends: .dotnet-base
  stage: build
  script:
    - dotnet build -c Release""")

    para(d, "Nuqta bilan boshlanadigan vazifalar (`.dotnet-base`) "
            "bajarilmaydi — ular faqat shablon sifatida ishlatiladi.")

    # ───────────────────────────────────────────
    h1(d, "11. Xulosa")

    bullets(d, [
        "Quvur `.gitlab-ci.yml` fayli orqali sozlanadi va kod bilan "
        "birga versiyalanadi.",
        "Bitta bosqichdagi vazifalar parallel, bosqichlar esa ketma-ket "
        "bajariladi.",
        "Artefakt — ishlab chiqarilgan natija, kesh — yuklab olingan "
        "bog'liqliklar.",
        "`artifacts: when: always` testlar yiqilganda ham hisobotni "
        "saqlaydi.",
        "Xizmatga ulanishda `localhost` emas, alias nomi ishlatiladi.",
        "`rules` vazifa qachon bajarilishini belgilaydi; production "
        "uchun `when: manual` xavfsizroq.",
        "Sirlar `Masked` va `Protected` sifatida belgilanishi kerak.",
        "`include` va `extends` konfiguratsiyani bo'lish va "
        "takrorlanishni kamaytirish imkonini beradi.",
    ])

    sources(d, [
        ("GitLab CI/CD documentation",
         "https://docs.gitlab.com/ci/"),
        ("`.gitlab-ci.yml` keyword reference",
         "https://docs.gitlab.com/ci/yaml/"),
        ("GitLab CI/CD variables",
         "https://docs.gitlab.com/ci/variables/"),
        ("Services — GitLab CI/CD",
         "https://docs.gitlab.com/ci/services/"),
    ])
