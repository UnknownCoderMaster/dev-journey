# MAD ERP Backend — Arxitektura qo'llanmasi (o'quv konspekti)

> Bu hujjat MAD ERP tizimining umumiy tuzilishini, servislararo aloqani (ayniqsa **RabbitMQ**),
> autentifikatsiyani va muhim qoidalarni jamlaydi. O'rganish va keyinchalik eslab qolish uchun.
> Sanoqlar repozitoriy tuzilmasidan olingan (CLAUDE.md'dagi eski sanoqdan yuqori bo'lishi mumkin).

---

## 1. Umumiy ko'rinish

MAD ERP — **.NET 8** asosidagi **mikroservis** ERP tizimi. Har bir servis **Clean Architecture** va
**CQRS (MediatR)** shabloniga amal qiladi. Barcha servislar **bitta PostgreSQL** bazani baham ko'radi.

| Komponent | Soni | Izoh |
|-----------|------|------|
| Backend API servis | ~25 | `erp-{domain}-service` (ITG gateway+proxy shu jumladan) |
| Web BFF | ~24 | `erp-{domain}-bff-web` |
| Mobil BFF | 4 | hrm, mlbr, myevnt, rtng |
| Job (fon) servis | 2 | `erp-adm-job-service`, `erp-logger-job-service` |
| Umumiy baza | 1 | PostgreSQL, domen bo'yicha bitta schema |
| Auth tizimi | 2 | Keycloak (xodimlar) + person-auth/OneID (tashqi klientlar) |

**Domenlar (qisqartmalar):** ADM (boshqaruv/foydalanuvchi/org), HRM (kadrlar), ORG (tashkiliy tuzilma),
STD (talabalar), FIN (moliya), COM (komissiya), MY (portal), APP (workflow), LMS, LINK, DASH,
ITG (integratsiya), MLBR (kutubxona/media), LOGGER, ART, INV, SRV, REPR, EVNT, CERT.
Migratsiyalarda MON (monitoring) va MTB (legacy) schemalari ham uchraydi.

---

## 2. Repozitoriy tuzilmasi

```
libs/dotnet/                       Umumiy kutubxonalar (har bir servis foydalanadi)
  Erp.Core, Erp.Core.Sdk/.Models
  Erp.Core.Service.{Domain|Application|Infrastructure}   <- markazlashgan ApplicationDbContext shu yerda
  Gov.Core[.Sdk]                   Davlat tizimlari integratsiyasi
services/erp/erp-{domain}-service          Backend API servis
services/erp/erp-{domain}-bff-web          Web BFF (YARP + agregatsiya)
services/erp/erp-{domain}-bff-mobile       Mobil BFF (hrm, mlbr, myevnt, rtng)
services/erp/erp-itg-service               Gateway + Proxy (servislararo va tashqi chaqiruvlar)
services/erp/erp-{adm,logger}-job-service  Fon job/messaging consumer'lari
scripts/executed/                  Bajarilgan SQL migratsiyalar (raqamli tartibda)
docs/database-naming-conventions.md   Baza dizayn qoidalari (majburiy)
```

### Har bir servis ichi
```
Erp.Service.{Domain}.sln
src/
  Erp.Service.{Domain}.WebApi/            Controllers, Program.cs, appsettings.*, Dockerfile
  libs/
    Erp.Service.{Domain}.Domain/          Entity'lar, biznes qoidalar
    Erp.Service.{Domain}.Application/      MediatR handlerlar, AutoMapper, FluentValidation
    Erp.Service.{Domain}.Infrastructure/   DbContext registratsiyasi, repozitoriy, tashqi klientlar
    shared/
      Erp.Service.{Domain}.Models/         Commands, Queries, DTO — iste'molchilar baham ko'radi
      Erp.Service.{Domain}.Sdk/            Refit interfeyslari (boshqa servislar chaqiradi)
```

**Bog'liqlik oqimi (qat'iy):** `WebApi → Infrastructure → Application → Domain`.
`Models` va `Sdk` — yuqoriga bog'liqlikka ega emas (shared shartnoma).

---

## 3. Bitta servisning ishlash oqimi (Clean Architecture + CQRS)

```
HTTP so'rov
   │
   ▼
Controller (WebApi)  ──  "yupqa": faqat  await Mediator.Send(command/query)
   │
   ▼
MediatR pipeline
   │   └─ ValidationBehaviour  (FluentValidation — avtomatik)
   ▼
Handler (Application/UseCases/{Entity}/Commands|Queries)
   ├─ AutoMapper  →  DTO / natija
   ├─ IApplicationDbContext  →  PostgreSQL
   └─ (ixtiyoriy)  Publisher.PublishAsync(...)  →  RabbitMQ (fon ish)
```

**Feature qo'shish tartibi:** Domain → Models (Commands/Queries/Dtos) → Application (handler + validator + mapping)
→ Infrastructure (odatda hech narsa) → WebApi (yupqa controller) → DB migratsiya → Sdk (agar kerak bo'lsa).

---

## 4. Ma'lumotlar bazasi

- **PostgreSQL + EF Core 8 (Npgsql).** Bitta baza, **domen bo'yicha bitta schema** (`adm`, `hrm`, `org`, ...).
- **Markazlashgan DbContext:** `ApplicationDbContext`
  (`libs/dotnet/Erp.Core.Service.Infrastructure/Database/`) — yuzlab `DbSet`. Servislar uni
  `IApplicationDbContext` interfeysi orqali ishlatadi. **Per-servis DbContext yo'q.**
- **Migratsiyalar — xom SQL fayllar:** `{NNNN}. {SCHEMA} {tavsif}.sql`, raqamli tartibda bajariladi.
  Bajarilganlari `scripts/executed/`'ga ko'chiriladi.
- **Nomlash qoidalari (majburiy) — prefikslar:**
  - `enum_` — statik lookup (qo'lda ID, audit-by yo'q)
  - `info_` — global ref (state_id bilan)
  - `hl_` — tenant ref (organization_id kerak)
  - `doc_` — biznes hujjat (status_id / doc_on / doc_number / table_id)
  - `sys_` — infratuzilma (adm'da global, boshqa joyda tenant)
- **Multi-tenancy:** domen-schema jadvallarida `organization_id` **majburiy**
  (faqat `enum_*`, `info_*` va adm'dagi global `sys_*` mustasno).
- **Maydon konvensiyalari:** `_at` (timestamp), `_on` (sana), `_by` (user FK), `_id` (FK),
  tarjima jadvali: `{table}_translate`.

---

## 5. Servislararo aloqa — SINXRON vs ASINXRON ⭐

Bu tizimning eng muhim tushunchasi. Ikki kanal bor:

| Holat | Kanal | Xususiyat |
|-------|-------|-----------|
| Natija darhol kerak (ma'lumot o'qish/yozish) | **Refit SDK (HTTP)** | Chaqiruvchi javobni **kutadi** |
| Fon ishi, natija kutilmaydi | **RabbitMQ** | Xabar navbatga tashlanadi, chaqiruvchi kutmaydi |
| Servislar bir-biridan ajratilishi kerak | **RabbitMQ** | Bir servis o'chsa ham xabar navbatda kutadi |
| Rejalashtangan/retry kerak bo'lgan ish | **RabbitMQ → Hangfire** | Birga ishlaydi |

### 5.1. Sinxron — Refit SDK
- Har servis o'z `Erp.Service.{Domain}.Sdk` (Refit interfeyslari)ni beradi.
- Iste'molchi `appsettings.json`'dagi `Sdks` bo'limida BaseUrl'ni sozlaydi.
- **BFF'lar** aynan shu SDK'larni agregatsiya qiladi (bitta frontend so'roviga bir nechta servis javobini birlashtiradi).

---

## 6. RabbitMQ — chuqur tushuntirish ⭐⭐

### 6.1. Yondashuv: Hub topologiyasi
Har bir servis consumer emas. **Job-service'lar markazlashgan consumer** bo'lib ishlaydi:

```
Har qanday servis (Producer)  ──publish──►  RabbitMQ navbat  ──consume──►  erp-adm-job-service
   (adm, org, fin, hrm...)                                                  erp-logger-job-service
```
Ya'ni og'ir/fon ishlar job-service'ga to'planadi; oddiy API servislar faqat xabar **jo'natadi**.

### 6.2. Kutubxona va qatlamlar
`WEBASE.MessageBroker.RabbitMQ` ustiga qurilgan. Har bir "message broker" 3 loyihaga bo'linadi:

| Loyiha | Vazifa | Misol |
|--------|--------|-------|
| `*.Abstraction` | Interfeys + Message (DTO) | `ICustomJobPublisher`, `CustomJobMessage` |
| `*.RabbitMQ` | Navbat ta'rifi + Publisher | `AdmQueues`, `CustomJobPublisher` |
| Consumer (job-service Infra) | Xabarni qabul qilib qayta ishlash | `CustomJobConsumer` |

### 6.3. Navbat ta'rifi (WbRabbitQueue)
Hamma joyda **Direct exchange** (bitta routing key → bitta navbat):
```csharp
public static WbRabbitQueue CustomJob = new WbRabbitQueue
{
    Name = "mad-erp-custom-job-queue",
    Exchange = "mad-erp-custom-job-exchange",
    ExchangeType = ExchangeType.Direct,
    RoutingKey = "mad-erp-custom-job-route",
    Producer = "*",                          // istalgan servis jo'natadi
    Consumer = "mad-erp-custom-job-service"  // faqat job-service qabul qiladi
};
```

### 6.4. Publisher — juda yupqa (bazaviy klassdan meros)
```csharp
public class CustomJobPublisher : WbRabbitMQPublisher<CustomJobMessage>, ICustomJobPublisher
{
    public CustomJobPublisher(...) : base(client, logger, AdmQueues.CustomJob) { }
}
```
Handler ichida ishlatilishi:
```csharp
await _documentHistoryPublisher.PublishAsync(documentHistoryMessage);
```

### 6.5. Consumer — Config + Handler
```csharp
public class CustomJobConsumerConfig : IWbConsumerConfig<CustomJobMessage>
{
    public WbRabbitQueue Queue => AdmQueues.CustomJob;
    public ushort PrefetchCount { get; set; } = 1;   // bir vaqtda 1 ta xabar
    public int WorkerCount { get; set; } = 1;         // ishchi soni
    public bool RequeueOnFailed { get; set; } = true; // xato → navbatga qayta
}

public class CustomJobConsumer : IWbConsumer<CustomJobMessage>
{
    public async Task ConsumeAsync(CustomJobMessage message, CancellationToken ct)
    {
        // ... RabbitMQ xabarni oladi, keyin Hangfire'ga uzatadi:
        BackgroundJob.Enqueue<ICustomJobServiceRunner>(s => s.ExecuteAsync(...));
    }
}
```
> **Muhim naqsh:** RabbitMQ **yetkazish** uchun, Hangfire esa **haqiqiy bajarilish + retry** uchun.

### 6.6. Ro'yxatga olish (DI)
- **Publisher tomoni** (oddiy servis): `AddRabbitMQPublisherClient()` + `.AddAdmPublishers()` + `.AddAuditPublishers()`.
- **Consumer tomoni** (job-service): qo'shimcha `AddRabbitMQConsumerClient()` + har bir `AddConsumer<Message, Config, Handler>(...)`.

### 6.7. Real use-case'lar
| Navbat | Nima uchun |
|--------|-----------|
| `doc-history` / `row-history` / `hl-history` | **Audit/tarix** — o'zgarishlarni asosiy amalni sekinlashtirmasdan yozish (barcha servislarda bor) |
| `custom-job` | **Custom Job** — og'ir ish → Hangfire'ga uzatiladi |
| `sync-user-with-employee` | **User ↔ Employee** sinxronizatsiyasi |
| `user-last-visit` | **Oxirgi kirish** — yuqori chastota, past muhimlik (har so'rovda bazaga yozmaslik uchun) |
| `cadastre-info-sync` | **org → adm-job** kadastr ma'lumot yig'ish (cross-service) |
| `external-system-task` | **Tashqi tizim** topshiriqlari (ITG proxy orqali davlat tizimlariga) |

### 6.8. Ishonchlilik (reliability)
- `PrefetchCount` — ishchi bir vaqtda nechta xabar olishi (og'ir ish uchun 1, teng yuklama).
- `WorkerCount` — parallel ishchilar soni.
- `RequeueOnFailed` — xatoда navbatga qaytarish (`CadastreInfoSync`'da `false` — takrorlanmasligi kerak).
- **DLQ (Dead Letter Queue)** — WEBASE kutubxonasi avtomatik yaratadi.
- `IWbConsumerErrorHandler` — markazlashgan xato boshqaruvi.

### 6.9. Konfiguratsiya (`appsettings.*` → `RabbitMQ` bo'limi)
`AppName`, `Host`, `Port: 5672`, `VirtualHost`, `UserName/Password`, `ClientProvidedName`,
`ConnectionTimeOutSeconds`, `HeartbeatSeconds`, va har bir consumer uchun `Consumers:{Name}` sozlamalari.

---

## 7. Autentifikatsiya — ikki mustaqil tizim

Ular **aralashmaydi**.

### 7.1. Keycloak — xodimlar (`sys_user`)
- OIDC + JWT bearer. Har servis o'z clientini `Idp` bo'limida ro'yxatdan o'tkazadi.
- Hub `erp-app-bff-web` `OAuthController` (`/oauth/authorize|callback|token|...`) — Keycloak ⇄ OneID moslashtirish (xodim logini).

### 7.2. person-auth — tashqi klientlar (`sys_person_user`)
- `erp-my-service` — o'zi **RS256 JWT** chiqaruvchi mustaqil IdP (Keycloak ishtirok etmaydi).
- **OneID** (`sso.egov.uz`) — identity provider, **hub-and-spoke** topologiyada:
  - **OneID konfiguratsiyasi FAQAT hub'da** (`erp-app-bff-web`). Spoke BFF'larda `OneId` bo'limi yo'q.
  - Hub `PersonAuthController` — OneID round-trip'ni boshqaradi (authorize → callback → `my-service.IssueAsync` → tokenни shared Redis'ga yozadi → spoke'ga qaytaradi).
  - Spoke BFF'lar faqat `/oauth/person-auth/start` va `/oauth/person-auth/exchange` beradi.
  - **Shared Redis majburiy:** hub va barcha spoke bir xil Redis'ga qarashi shart (`personauth:state:*`, `personauth:exchange:*`).
- Person endpointlar himoyasi: `[Authorize(AuthenticationSchemes = PersonAuthSchemes.Person)]`.

---

## 8. Texnologiyalar to'plami

| Soha | Texnologiya |
|------|-------------|
| Framework | .NET 8, C# 12, Nullable disabled, TreatWarningsAsErrors |
| CQRS | MediatR (+ `ValidationBehaviour` pipeline) |
| Mapping / Validatsiya | AutoMapper, FluentValidation (assembly-scan) |
| Baza | PostgreSQL, EF Core 8 (Npgsql), markazlashgan DbContext |
| Messaging | RabbitMQ (`WEBASE.Standard.MessageBroker.RabbitMQ`) |
| Fon ishlar | Hangfire (PostgreSQL storage) |
| Cache | Redis (StackExchange.Redis) |
| Fayl ombori | MinIO (`WbMinio`) |
| Xatolar | `WEBASE.AppError.PostgreSQL` (alohida log DB), `WbClientException` (foydalanuvchiga, o'zbekcha), `WbNotFoundException` |
| Excel/PDF | EPPlus + ClosedXML / QuestPDF + iText7 |
| Paketlar | Central Package Management — versiyalar `Directory.Packages.props`'da |

---

## 9. Muhim eslatmalar / gotcha'lar

- **Har bir tenant-scoped so'rov** `OrganizationId` (`_authService.CurrentOrganizationId`) bo'yicha
  filtrlanishi shart. Global filter yo'q — handler o'zi qo'shadi.
- Update/delete handlerlari mutatsiyadan oldin **egalikni** tekshiradi.
- Status o'zgarishlari `StatusIdConst.CanApplyStatus()` orqali — xom status raqami yozilmaydi.
- Konstantalardan foydalaning (`StatusIdConst`, `TableIdConst`) — ID'larni hardcode qilmang.
- **ITG** bitta loyihada `gateway` (5002, ichki) + `proxy` (5003, tashqi)ga bo'linadi, alohida build script/Dockerfile.
- Ko'p `*.UnitTest` loyihalari bo'sh (scaffold) — `dotnet test` xatti-harakatni to'liq qamramaydi.
- Portlar: 5001–5024 backend, 5201+ web BFF, 5301+ mobil BFF (oxirgi raqam mos: 5001 ADM → 5201 ADM web BFF).
- Docker image'lar: `registry.webase.uz/madaniyat/mad-erp-{domain}-{type}`.

---

## 10. Bir qarashda: qachon nima ishlatiladi?

```
Ma'lumot o'qish/yozish, darhol javob kerak     →  Refit SDK (HTTP, sinxron)
Tarix/audit yozish                              →  RabbitMQ (fon)
Og'ir/uzoq ish                                  →  RabbitMQ → Hangfire
Servislarni ajratish (decoupling)               →  RabbitMQ
Bir nechta servis javobini birlashtirish        →  BFF (SDK agregatsiyasi)
Tashqi davlat tizimi bilan aloqa                →  ITG proxy (+ RabbitMQ external-task)
```

---

*Manba: repozitoriy tuzilmasi + CLAUDE.md + kod tahlili. O'quv maqsadida tuzilgan konspekt.*
