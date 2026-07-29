# Docker, .dockerignore — Middle D

## 1. Nima? (Ta'rif)

**Docker** — ilovani **konteyner** (container) ichida, barcha
bog'liqliklari bilan birga, **istalgan muhitda bir xil** ishlaydigan
holatda o'rash texnologiyasi. **Container** — Virtual Machine'dan
farqli, host OS **kernelini bo'lishadi**, shuning uchun ancha
**yengil va tez** ishga tushadi.

## 2. Nima uchun kerak?

"Mening kompyuterimda ishlaydi" muammosi — turli muhitlarda (dev,
staging, prod) turli .NET versiyasi, kutubxona, OS sozlamalari
tufayli yuzaga keladi. Docker — ilovani **barcha bog'liqliklari
bilan birga** "muzlatib", **HAR QAYERDA bir xil** ishlashini
kafolatlaydi.

## 3. Ichida nima sodir bo'ladi? (Mexanizm)

### 3.1 Container vs Virtual Machine

```
Virtual Machine:                    Container:
┌─────────────────┐                ┌─────────────────┐
│ App              │                │ App              │
│ Bins/Libs         │                │ Bins/Libs         │
│ Guest OS (TO'LIQ!) │                │ (Guest OS YO'Q!)  │
├─────────────────┤                ├─────────────────┤
│ Hypervisor        │                │ Docker Engine     │
├─────────────────┤                ├─────────────────┤
│ Host OS           │                │ Host OS           │
└─────────────────┘                └─────────────────┘

VM — HAR BIRI o'zining TO'LIQ OS'iga ega (GB'larcha hajm, sekin
     ishga tushadi)
Container — Host OS KERNELINI BO'LISHADI (MB'larcha hajm, SONIYALARDA
            ishga tushadi)
```

### 3.2 Dockerfile — instruksiyalar

```dockerfile
FROM mcr.microsoft.com/dotnet/sdk:8.0 AS build
WORKDIR /src
COPY ["ErpApi.csproj", "./"]
RUN dotnet restore
COPY . .
RUN dotnet publish -c Release -o /app/publish

FROM mcr.microsoft.com/dotnet/aspnet:8.0 AS final
WORKDIR /app
COPY --from=build /app/publish .
EXPOSE 8080
ENTRYPOINT ["dotnet", "ErpApi.dll"]
```

```
FROM       — bazaviy IMAGE (masalan .NET SDK)
WORKDIR    — konteyner ICHIDAGI ishchi papka
COPY       — HOST'dan konteynerga fayl KO'CHIRISH
RUN        — buyruq bajarish (build vaqtida, masalan restore/build)
EXPOSE     — qaysi PORT ochiq bo'lishini HUJJATLASHTIRISH (haqiqiy
             portni ochish EMAS — bu faqat metadata)
ENTRYPOINT — konteyner ISHGA TUSHGANDA bajariladigan buyruq
CMD        — ENTRYPOINT'ga QO'SHIMCHA argument (yoki ENTRYPOINT
             bo'lmasa — asosiy buyruq)
```

### 3.3 Multi-stage build — final image kichikroq

```
❌ Bitta bosqichli build — FINAL image ICHIDA SDK (build vositalari,
   ~700MB) HAM QOLADI — production'da KERAK EMAS, faqat HAJMNI
   OSHIRADI!

✅ Multi-stage:
   1-bosqich (build) — SDK image, KOMPILYATSIYA qiladi
   2-bosqich (final) — FAQAT runtime image (~200MB), 1-bosqichdan
                        FAQAT natijaviy DLL fayllar KO'CHIRILADI

Natija: FINAL image — 700MB emas, ~200MB (SDK, source kod, build
        cache — YO'Q)
```

### 3.4 `.dockerignore` — nima o'tkazilmaydi

```
bin/
obj/
.vs/
.git/
*.md
appsettings.Development.json
```

`.dockerignore` — `COPY . .` buyrug'i bajarilganda, **kerak
bo'lmagan** (yoki **maxfiy**) fayllarning konteynerga
KO'CHIRILMASLIGINI ta'minlaydi — bu HAM **build tezligini** (kamroq
fayl), HAM **xavfsizlikni** (maxfiy fayllar tasodifan konteynerga
tushmasligi) yaxshilaydi.

### 3.5 Asosiy buyruqlar

```bash
docker build -t erp-api:latest .          # Image yaratish
docker run -p 8080:8080 erp-api:latest     # Konteyner ishga tushirish
docker ps                                   # Ishlayotgan konteynerlar
docker logs <container_id>                  # Log ko'rish
docker exec -it <container_id> /bin/bash    # Konteyner ICHIGA kirish
docker stop <container_id>                  # To'xtatish
```

### 3.6 Docker Compose — bir nechta container birga

```yaml
version: '3.8'
services:
  api:
    build: .
    ports:
      - "8080:8080"
    environment:
      - ASPNETCORE_ENVIRONMENT=Production
      - ConnectionStrings__DefaultConnection=Host=db;Database=erp;Username=postgres;Password=${DB_PASSWORD}
    depends_on:
      - db
      - rabbitmq
    networks:
      - erp-network

  db:
    image: postgres:16
    environment:
      POSTGRES_DB: erp
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - pgdata:/var/lib/postgresql/data
    networks:
      - erp-network

  rabbitmq:
    image: rabbitmq:3-management
    ports:
      - "5672:5672"
      - "15672:15672"
    networks:
      - erp-network

volumes:
  pgdata:

networks:
  erp-network:
```

### 3.7 Environment variables — `.env` fayl

```
# .env (GIT'GA COMMIT QILINMASIN!)
DB_PASSWORD=super_secret_password
```

```yaml
environment:
  - ConnectionStrings__DefaultConnection=Host=db;Password=${DB_PASSWORD}
```

Docker Compose — `.env` faylidagi qiymatlarni **avtomatik** o'qib,
`${DB_PASSWORD}` o'rniga qo'yadi.

### 3.8 Volume — ma'lumot saqlash

```
Konteyner — O'CHIRILGANDA, ICHIDAGI BARCHA ma'lumot (masalan DB
fayllari) HAM YO'QOLADI (konteyner — "vaqtinchalik" xotira)!

Volume — konteynerdan TASHQARIDA, HOST diskida SAQLANADIGAN
joy — konteyner o'chirilib, QAYTA yaratilsa ham, VOLUME'dagi
ma'lumot SAQLANIB QOLADI.

volumes:
  - pgdata:/var/lib/postgresql/data  # Named volume — Docker BOSHQARADI
  - ./logs:/app/logs                  # Bind mount — HOST papkasiga TO'G'RIDAN bog'lanadi
```

### 3.9 Network — containerlar orasida muloqot

```
Docker Compose — HAR SERVIS uchun O'ZINING nomi bilan DNS yaratadi:

api konteyneridan — "db" nomiga MUROJAAT qilsa (masalan
"Host=db;..."), Docker Compose ICHKI DNS orqali BUNI "db" servisining
KONTEYNER IP manziliga HAL QILADI — "localhost" EMAS!
```

### 3.10 Production deployment — HealthCheck, restart policy

```yaml
services:
  api:
    restart: unless-stopped # Konteyner YIQILSA — AVTOMATIK qayta ishga tushadi
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

## 4. Kod — ASP.NET Core Health Check

```csharp
builder.Services.AddHealthChecks()
    .AddNpgSql(connectionString)
    .AddRabbitMQ(rabbitConnectionString);

app.MapHealthChecks("/health");
```

## 5. Qachon ishlatish kerak?

| Vaziyat | Yechim |
|---|---|
| Ilovani turli muhitda bir xil ishlatish | Docker |
| Bir nechta bog'liq servis (API + DB + broker) | Docker Compose |
| Production'da kichik image, tez deploy | Multi-stage build |
| Konteyner yiqilsa avtomatik qayta ishga tushirish | `restart` policy |

## 6. Muhim nuqtalar

- `.dockerignore` — `bin/obj/.vs` va **maxfiy fayllar**ni HAR DOIM
  o'z ichiga olishi kerak.
- Multi-stage build — production image hajmini SEZILARLI kamaytiradi.
- Volume'siz — konteyner o'chirilganda DB ma'lumoti **YO'QOLADI**
  (bu — eng ko'p uchraydigan boshlang'ich xato).
- Konteyner ichida `localhost` — O'ZINING konteyneri, boshqa
  konteyner EMAS (service nomi orqali murojaat qilinishi kerak).

## 7. Imtihon savollari

1. Container va Virtual Machine orasidagi asosiy farq nima?
2. Multi-stage build qanday muammoni (image hajmi) hal qiladi?
3. `.dockerignore` nima uchun kerak?
4. Docker Compose'da bir konteyner boshqasiga qanday nom orqali
   murojaat qiladi?
5. Volume nima muammoni (ma'lumot yo'qolishi) hal qiladi?
6. `restart: unless-stopped` qanday amaliy foyda beradi?
