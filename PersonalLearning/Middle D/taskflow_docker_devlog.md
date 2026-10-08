# TaskFlow API — Docker Muhitini Sozlash: Muammolar va Yechimlar

**Loyiha:** TaskFlow API (Middle D o'quv loyihasi)  
**Sana:** 2026-yil 7-oktabr  
**Muallif:** Orzibek  

---

## 1. Loyiha haqida

TaskFlow API — Middle D darajasidagi texnologiyalarni amalda o'rganish maqsadida qurilgan o'quv loyihasi. Maqsad: bir loyiha ichida RabbitMQ, Docker, SignalR, Hangfire, MinIO, IMemoryCache va NSubstitute texnologiyalarini birga ishlatib ko'rish.

**Texnologiyalar to'plami:**

| Texnologiya | Maqsad |
|---|---|
| ASP.NET Core 8 | Asosiy backend framework |
| PostgreSQL | Relatsion ma'lumotlar bazasi |
| RabbitMQ | Message broker (hodisalar uzatish) |
| MinIO | Object storage (fayl saqlash) |
| Hangfire | Background jobs (Deadline reminder) |
| SignalR | Real-time xabarlar |
| JWT | Autentifikatsiya |
| Docker | Servislarni izolyatsiyalash |

**Papka joyi:** `C:\ExtraWork\dev-journey\projects\Middle-D\TaskFlowApi\`

---

## 2. Docker Compose Tuzilmasi

Loyiha uchun to'rtta servis docker orqali ishga tushirildi: PostgreSQL, RabbitMQ, MinIO va API o'zi.

**`docker-compose.yml` (yakuniy ishchi versiya):**

```yaml
services:
  postgres:
    image: postgres:15
    container_name: taskflow_postgres
    environment:
      POSTGRES_DB: taskflow_db
      POSTGRES_USER: taskflow_user
      POSTGRES_PASSWORD: taskflow_pass
    ports:
      - "5433:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - taskflow_network

  rabbitmq:
    image: rabbitmq:3-management
    container_name: taskflow_rabbitmq
    environment:
      RABBITMQ_DEFAULT_USER: taskflow_user
      RABBITMQ_DEFAULT_PASS: taskflow_pass
    ports:
      - "5672:5672"
      - "15672:15672"
    volumes:
      - rabbitmq_data:/var/lib/rabbitmq
    networks:
      - taskflow_network

  minio:
    image: myminio:latest
    container_name: taskflow_minio
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: taskflow_user
      MINIO_ROOT_PASSWORD: taskflow_pass123
      MINIO_VOLUMES: "/data"
    ports:
      - "9000:9000"
      - "9001:9001"
    volumes:
      - minio_data:/data
    networks:
      - taskflow_network

volumes:
  postgres_data:
  rabbitmq_data:
  minio_data:

networks:
  taskflow_network:
    driver: bridge
```

---

## 3. Muammolar va Yechimlar

Muhitni sozlash jarayonida bir qancha muammolar yuzaga keldi. Har bir muammo texnologiya haqida yangi bilim berdi.

---

### Muammo 1: `version` atributi haqida ogohlantirish

**Xatolik xabari:**
```
the attribute `version` is obsolete, it will be ignored,
please remove it to avoid potential confusion
```

**Sababi:**  
Docker Compose v2 dan boshlab `version: '3.8'` kabi qator eskirgan (deprecated) hisoblanadi. Docker uni e'tiborsiz qoldiradi, lekin ogohlantirish chiqaradi.

**Yechimi:**  
`docker-compose.yml` faylining birinchi qatoridagi `version: '3.8'` ni o'chirib tashlash kifoya. Fayl shu holda ham to'g'ri ishlaydi.

---

### Muammo 2: `minio/minio` Docker Hub dan o'chirilgan

**Xatolik xabari:**
```
pull access denied for minio/minio, repository does not exist
or may require 'docker login'
```

**Sababi:**  
MinIO Community Edition 2025-yil dekabrda maintenance modega o'tdi va 2026-yil sentabrda `minio/minio` hamda `minio/mc` repositorylari Docker Hub dan butunlay o'chirildi. Bu holat MinIO ning enterprise mahsulot — AIStor ga to'liq o'tishini bildiradi.

**O'rganilgan narsa:**  
Docker image lari registrylarga bog'liq — kompaniya o'z image larini istalgan vaqt o'chirishi yoki ko'chirishi mumkin. Shuning uchun production muhitda image versiyalarini pin qilib qo'yish va o'zingizning private registry (masalan, Harbor, Nexus) ga nusxalab olish tavsiya etiladi.

**Sinab ko'rilgan alternativlar:**

| Variant | Natija | Sababi |
|---|---|---|
| `minio/minio` | ❌ | Docker Hub dan o'chirilgan |
| `quay.io/minio/minio` | ❌ | 401 UNAUTHORIZED — login talab qiladi |
| `quay.io/minio/aistor/minio:RELEASE.2026-09-19T17-05-25Z` | ⚠️ | Pull bo'ldi, lekin enterprise license talab qildi |
| `quay.io/minio/minio:RELEASE.2025-09-07T16-13-09Z` | ❌ | 401 UNAUTHORIZED |
| `bitnami/minio` | ❌ | Tarmoq cheklovlari |

**Yakuniy yechim:**  
MinIO GitHub reposi ([github.com/minio/minio](https://github.com/minio/minio)) dan source kodni yuklab, Linux binary yasab, o'z Docker image imizni qurishdan iborat bo'ldi.

---

### Muammo 3: `quay.io/minio/aistor/minio` — License xatoligi

**Xatolik xabari (brauzerda):**
```
Invalid Login
Access denied. No license is installed.
Please install a valid license using 'mc license update' to enable service.
```

**[Screenshot — 1]**

**Sababi:**  
`quay.io/minio/aistor/minio` — bu MinIO AIStor, enterprise versiya. Bepul foydalanib bo'lmaydi, tijoriy litsenziya talab qiladi. Biz kerakli Community Edition emas edi.

**O'rganilgan narsa:**  
Bir xil loyiha nomi ostida ham bepul, ham pullik versiyalar mavjud bo'lishi mumkin. Image nomiga e'tibor berish kerak: `aistor` so'zi enterprise ekanligini bildiradi.

---

### Muammo 4: MinIO source dan Docker image yasash — `FROM minio/minio:latest` xatoligi

**Xatolik xabari:**
```
ERROR: failed to build: failed to solve: minio/minio:latest:
failed to resolve source metadata for docker.io/minio/minio:latest:
pull access denied
```

**Sababi:**  
MinIO ning GitHub reposidagi `Dockerfile` o'zi ham `FROM minio/minio:latest` bilan boshlanadi — ya'ni Docker Hub dagi o'chirilgan imageni base sifatida ishlatadi. Bu Dockerfile ham endi ishlamaydi.

**Yechim:**  
Eski `Dockerfile` ni o'chirib, o'zimiz yangi `Dockerfile` yozdik. Bu yerda muhim tushuncha: **multi-stage build** yoki **scratch/distroless image** dan foydalanish — binary faylni to'g'ridan-to'g'ri minimal Linux image ga joylash.

**Yangi `Dockerfile` (o'zimiz yozgan):**
```dockerfile
FROM debian:bookworm-slim

RUN apt-get update && apt-get install -y \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY minio /usr/local/bin/minio

RUN chmod +x /usr/local/bin/minio

EXPOSE 9000 9001

ENTRYPOINT ["/usr/local/bin/minio"]
```

**O'rganilgan narsa:**  
Docker image yaratish uchun albatta boshqa image dan meros olish shart emas. `debian:bookworm-slim` kabi minimal base image yetarli. Muhimi — binary fayl to'g'ri arxitektura uchun (linux/amd64) build qilingan bo'lishi kerak.

---

### Muammo 5: Windows da build qilingan binary Linux containerda ishlamaydi

**Sababi:**  
`go build -o minio.exe .` buyrug'i Windows uchun `.exe` fayl yaratadi. Linux container esa Windows executable faylini bajara olmaydi — ikki xil operatsion tizim uchun ikki xil binary kerak.

**Yechim — Cross-compilation:**  
Go tilining kuchli tomonlaridan biri — bir platformada boshqa platform uchun binary yasab berish imkoniyati (cross-compilation).

```powershell
# Windows terminalida Linux uchun binary yasash
$env:GOOS="linux"
$env:GOARCH="amd64"
go build -o minio .
```

Bu yerda:
- `GOOS=linux` — maqsad operatsion tizim Linux
- `GOARCH=amd64` — maqsad protsessor arxitekturasi x86-64
- `-o minio` — chiquvchi fayl nomi (`.exe` siz)

Natijada `minio` nomli Linux binary yaratildi va uni Docker image ga joylash mumkin bo'ldi.

**O'rganilgan narsa:**  
Go dasturlash tili cross-compilation uchun kuchli qo'llab-quvvatlash beradi. `GOOS` va `GOARCH` muhit o'zgaruvchilari orqali istalgan platforma uchun binary yasash mumkin. Bu CI/CD pipeline larda juda foydali.

---

### Muammo 6: `Storage resources are insufficient` — Erasure Coding xatoligi

**Xatolik xabari (docker logs):**
```
Error: Unable to initialize backend: Storage resources are insufficient
for the read operation .minio.sys/pool.bin, retrying in 1.9s
```

**[Screenshot — 2]**

**Sababi:**  
MinIO ning zamonaviy versiyalarida **Erasure Coding** mode default holda yoqilgan. Bu mode ma'lumotlarni bir nechta diskka bo'lib saqlaydi va kamida **4 ta disk (yoki 4 ta node)** talab qiladi. Biz esa faqat bitta `/data` volume berdik.

**Erasure Coding nima?**  
Ma'lumotlarni bir necha bo'lakka bo'lib, har birini alohida joyga saqlash usuli. Agar ba'zi disklar ishdan chiqsa ham, ma'lumotlarni tiklash mumkin. Production uchun juda foydali, lekin rivojlanish muhiti uchun ortiqcha.

**Yechim:**  
`MINIO_VOLUMES` environment variable ni aniq ko'rsatib, single-node rejimda ishlatish:

```yaml
environment:
  MINIO_VOLUMES: "/data"
```

Shuningdek, eski buzilgan volume ni tozalash kerak edi:
```bash
docker-compose down
docker volume rm taskflowapi_minio_data
docker-compose up -d
```

**O'rganilgan narsa:**  
Docker volume lari persistent (doimiy) saqlashni ta'minlaydi — container o'chirilsa ham ma'lumot yo'qolmaydi. Lekin agar volume da noto'g'ri yoki buzilgan ma'lumot bo'lsa, uni qayta yaratish kerak. `docker volume rm` buyrug'i volumeni butunlay o'chiradi.

---

## 4. MinIO Image Yaratish — To'liq Jarayon

### 4.1 Go o'rnatish

MinIO source kodni compile qilish uchun Go 1.24+ kerak:

1. [go.dev/dl](https://go.dev/dl/) saytidan `go1.24.x.windows-amd64.msi` yuklab o'rnatish
2. Tekshirish: `go version`

### 4.2 MinIO source kodni olish

```bash
git clone https://github.com/minio/minio.git
cd minio
```

### 4.3 Linux binary yasash

```powershell
$env:GOOS="linux"
$env:GOARCH="amd64"
go build -o minio .
```

> ⚠️ Bu jarayon biroz vaqt olishi mumkin — MinIO katta loyiha.

### 4.4 Yangi Dockerfile yozish

`D:\minio\Dockerfile` faylini quyidagi matn bilan to'liq almashtiring:

```dockerfile
FROM debian:bookworm-slim

RUN apt-get update && apt-get install -y \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

COPY minio /usr/local/bin/minio

RUN chmod +x /usr/local/bin/minio

EXPOSE 9000 9001

ENTRYPOINT ["/usr/local/bin/minio"]
```

### 4.5 Docker image yasash

```bash
docker build -t myminio:latest .
```

---

## 5. Erishilgan Natija

```
[+] up 4/4
 ✔ Network taskflowapi_taskflow_network  Created
 ✔ Container taskflow_rabbitmq           Started
 ✔ Container taskflow_postgres           Started
 ✔ Container taskflow_minio              Started
```

**[Screenshot — 3: `docker ps` natijasi]**

Ishga tushirilgan servislar:

| Servis | Manzil | Login |
|---|---|---|
| PostgreSQL | `localhost:5433` | taskflow_user / taskflow_pass |
| RabbitMQ Management UI | http://localhost:15672 | taskflow_user / taskflow_pass |
| MinIO Console | http://localhost:9001 | taskflow_user / taskflow_pass123 |
| MinIO S3 API | http://localhost:9000 | — |

**[Screenshot — 4: RabbitMQ UI]**  
**[Screenshot — 5: MinIO Console]**

---

## 6. O'rganilgan Asosiy Darslar

### Docker haqida
- Docker image lari tashqi registry larga bog'liq — kompaniya istalgan vaqt o'zgartirishi mumkin. Production uchun private registry yoki image versiyalarini pin qilish tavsiya etiladi.
- `docker volume rm` buyrug'i volume ichidagi barcha ma'lumotlarni o'chiradi — ehtiyotkorlik bilan ishlatish kerak.
- `docker logs <container_name>` — muammo chiqganda birinchi qaraladigan joy.

### Go haqida
- Go cross-compilation uchun `GOOS` va `GOARCH` environment variable larini o'rnatish kifoya — boshqa hech qanday sozlama kerak emas.
- Go ning bu xususiyati CI/CD pipeline larda juda qimmatli: Linux serverlar uchun Mac yoki Windows mashinalarda binary yasash mumkin.

### MinIO haqida
- MinIO Community Edition 2026-yilda arxivlandi — endi yangi rivojlanish yo'q.
- Yangi loyihalarda MinIO o'rniga **SeaweedFS** yoki **Garage** kabi alternativalarni ko'rib chiqish mumkin.
- `MINIO_VOLUMES` environment variable ni aniq ko'rsatish — single-node rivojlanish muhiti uchun zarur.
- Erasure Coding — ma'lumotlar xavfsizligi uchun production da foydali, lekin kamida 4 disk talab qiladi.

### Umumiy
- Muammo chiqganda avval `docker logs` ni tekshirish — xatolik xabari ko'pincha aniq yechimni ko'rsatadi.
- Open source loyihalarning `Dockerfile` lari ham eskirishi mumkin — har doim ishonch bilan ishlatib bo'lmaydi.
- Rivojlanish muhitida tez harakat qilish uchun `docker-compose down && docker-compose up -d` — eng ko'p ishlatiladigan buyruq.
