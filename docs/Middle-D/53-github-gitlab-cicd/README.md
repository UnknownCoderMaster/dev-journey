# GitHub Actions, GitLab CI/CD — Middle D

## 1. Nima? (Ta'rif)

**CI (Continuous Integration)** — kod o'zgarishi HAR safar
repositoryga yuborilganda, **avtomatik** build+test qilinishi.
**CD (Continuous Deployment/Delivery)** — muvaffaqiyatli
build/test'dan keyin, ilova **avtomatik** deploy qilinishi.
**Pipeline** — bu jarayonlarni ifodalovchi, bosqichlarga (stage)
bo'lingan avtomatlashtirilgan oqim.

## 2. Nima uchun kerak?

Qo'lda build/test/deploy qilish — **xatoga moyil** va **sekin**.
Bitta dasturchi test o'tkazishni **unutib**, buzilgan kodni
production'ga yuborishi mumkin. CI/CD — bu jarayonni **avtomatik,
har doim bir xil tartibda** bajaradi.

## 3. Ichida nima sodir bo'ladi? (Mexanizm)

### 3.1 GitHub Actions — `.github/workflows/`

```yaml
# .github/workflows/build-and-test.yml
name: Build and Test

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

      - name: Setup .NET
        uses: actions/setup-dotnet@v4
        with:
          dotnet-version: '8.0.x'

      - name: Restore dependencies
        run: dotnet restore

      - name: Build
        run: dotnet build --no-restore --configuration Release

      - name: Test
        run: dotnet test --no-build --configuration Release --logger "trx"
```

```
on:        — QAYSI hodisada workflow ISHGA TUSHISHI (push, pull_request)
jobs:      — PARALLEL yoki KETMA-KET bajariladigan ish BLOKLARI
runs-on:   — QAYSI virtual mashinada ishga tushishi (ubuntu-latest, windows-latest)
steps:     — HAR jobning ICHIDAGI KETMA-KET bajariladigan qadamlar
uses:      — TAYYOR "Action" (Marketplace'dan) ishlatish
```

### 3.2 Actions Marketplace

```
actions/checkout@v4       — repo kodini RUNNER'GA YUKLASH
actions/setup-dotnet@v4    — .NET SDK'ni O'RNATISH
actions/upload-artifact    — build natijasini SAQLASH
docker/build-push-action   — Docker image BUILD+PUSH qilish
```

### 3.3 Secrets — `${{ secrets.KEY }}`

```yaml
- name: Deploy to server
  env:
    SSH_KEY: ${{ secrets.DEPLOY_SSH_KEY }}
  run: |
    echo "$SSH_KEY" > key.pem
    chmod 600 key.pem
    scp -i key.pem ./publish/* user@server:/var/www/
```

Secrets — GitHub repo **Settings → Secrets and variables → Actions**
orqali qo'shiladi, workflow log'ida **avtomatik maskalanadi**
(`***`).

### 3.4 ASP.NET Core build + test + publish pipeline

```yaml
jobs:
  build-test-publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-dotnet@v4
        with: { dotnet-version: '8.0.x' }
      - run: dotnet restore
      - run: dotnet build --no-restore -c Release
      - run: dotnet test --no-build -c Release
      - run: dotnet publish -c Release -o ./publish
      - uses: actions/upload-artifact@v4
        with:
          name: erp-api
          path: ./publish
```

### 3.5 Docker image build va push

```yaml
- name: Log in to Docker Hub
  uses: docker/login-action@v3
  with:
    username: ${{ secrets.DOCKER_USERNAME }}
    password: ${{ secrets.DOCKER_PASSWORD }}

- name: Build and push
  uses: docker/build-push-action@v5
  with:
    context: .
    push: true
    tags: myorg/erp-api:latest
```

### 3.6 GitLab CI/CD — `.gitlab-ci.yml`

```yaml
stages:
  - build
  - test
  - deploy

variables:
  DOTNET_VERSION: "8.0"

build:
  stage: build
  image: mcr.microsoft.com/dotnet/sdk:8.0
  script:
    - dotnet restore
    - dotnet build -c Release
  artifacts:
    paths:
      - "**/bin/Release/"

test:
  stage: test
  image: mcr.microsoft.com/dotnet/sdk:8.0
  script:
    - dotnet test -c Release

deploy:
  stage: deploy
  script:
    - echo "Deploying to production..."
    - scp -r ./publish/* user@server:/var/www/erp-api/
  only:
    - main
  environment:
    name: production
```

### 3.7 `stages`, `Runner`, `Variables`

```
stages — pipeline BOSQICHLARI (build → test → deploy), KETMA-KET
         bajariladi (agar OLDINGI bosqich MUVAFFAQIYATSIZ bo'lsa —
         KEYINGISI ISHGA TUSHMAYDI)

Runner — GitLab'ning "runner" agenti — pipeline'ni HAQIQATDA
         bajaradigan MASHINA:
  Shared Runner   — GitLab TA'MINLAYDI, HAMMA loyiha ISHLATADI
  Specific Runner — LOYIHAGA XOS, MAXSUS sozlangan (masalan Windows Runner)

Variables — $CI_REGISTRY_IMAGE, $CI_COMMIT_SHA kabi ICHKI, AVTOMATIK
            o'zgaruvchilar HAMDA foydalanuvchi belgilagan CUSTOM
            (Settings → CI/CD → Variables) o'zgaruvchilar
```

### 3.8 Artifact — build natijasi

```yaml
artifacts:
  paths:
    - publish/
  expire_in: 1 week
```

**Artifact** — bir bosqichda (masalan `build`) yaratilgan natijani
(masalan compiled DLL), **keyingi bosqich**(masalan `deploy`)ga
**uzatish** uchun saqlanadigan fayl(lar).

### 3.9 Environment — staging, production

```yaml
deploy-staging:
  stage: deploy
  script: ./deploy.sh staging
  environment:
    name: staging
  only:
    - develop

deploy-production:
  stage: deploy
  script: ./deploy.sh production
  environment:
    name: production
  only:
    - main
  when: manual # Qo'lda TASDIQLASH talab qilinadi (avtomatik EMAS)
```

`when: manual` — production deploy — **ko'pincha** avtomatik EMAS,
odam **tasdiqlashi** kerak bo'lgan qadam sifatida sozlanadi
(xavfsizlik uchun).

## 4. Kod — to'liq CI/CD misoli (GitHub Actions)

```yaml
name: CI/CD Pipeline
on:
  push:
    branches: [main]

jobs:
  build-and-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-dotnet@v4
        with: { dotnet-version: '8.0.x' }
      - run: dotnet restore
      - run: dotnet build --no-restore -c Release
      - run: dotnet test --no-build -c Release

  deploy:
    needs: build-and-test # FAQAT test MUVAFFAQIYATLI bo'lsa ISHGA TUSHADI
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Deploy
        env:
          SSH_KEY: ${{ secrets.DEPLOY_KEY }}
        run: echo "Deploying..."
```

## 5. Qachon ishlatish kerak?

| Vaziyat | Yechim |
|---|---|
| Repo GitHub'da | GitHub Actions |
| Repo GitLab'da (self-hosted yoki cloud) | GitLab CI/CD |
| Har PR'da avtomatik test | CI (build+test workflow) |
| Production deploy — qo'lda tasdiq kerak | `when: manual` / environment protection |

## 6. Muhim nuqtalar

- Secrets — HECH QACHON `run:` buyrug'i ichida **to'g'ridan** yozilmasin
  (log'ga chiqib qolishi mumkin) — har doim `${{ secrets.X }}`
  o'zgaruvchi orqali.
- `needs:`/`stages` — bosqichlar orasidagi **bog'liqlikni** to'g'ri
  belgilash, aks holda test o'tmagan kod ham deploy bo'lib qolishi
  mumkin.
- Production deploy — ko'pincha **manual approval** bilan himoyalanadi.

## 7. Imtihon savollari

1. CI va CD orasidagi farq nima?
2. GitHub Actions'da `jobs`, `steps`, `runs-on` nima vazifani
   bajaradi?
3. Secrets qanday xavfsiz saqlanadi va ishlatiladi?
4. GitLab'da Shared Runner va Specific Runner orasidagi farq nima?
5. Artifact nima va u pipeline bosqichlari orasida qanday
   ishlatiladi?
6. Production deploy uchun nima uchun `when: manual` kabi
   himoya qo'shiladi?
