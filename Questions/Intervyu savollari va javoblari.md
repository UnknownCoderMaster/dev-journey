# Middle D — intervyu savollari va javoblari

Daraja belgilash ro'yxatidagi Middle D mavzulari asosida tuzilgan savollar.
Har bir savol ostida to'liq javob bor: nafaqat "nima", balki "nega shunday" va
"qachon boshqacha qilish kerak" degan qismlar ham.

Savollar mavzu bo'limlari bo'yicha guruhlangan — ketma-ket o'qish shart emas.

**Bo'limlar:** [EF Core](#ef-core) · [ASP.NET](#aspnet) · [Web](#web) ·
[Auth](#auth) · [Design pattern](#design-pattern) · [Testing](#testing) ·
[Caching](#caching) · [Cybersecurity](#cybersecurity) · [SQL](#sql) ·
[Database design](#database-design-principles) · [Architecture](#architecture) ·
[Postgres](#postgres) · [Infratuzilma](#infratuzilma) · [.NET / C#](#net--c)

---

## EF Core

### 1. `DbContext` ning tavsiya etilgan hayot davri qanday va nega?

Web ilovada — **so'rov davomiyligi** (scoped). `AddDbContext()` ni standart
chaqirsak, aynan shu bo'ladi.

Sabablari:

- `DbContext` ichida Change Tracker bor va u xotirada entity'larni saqlaydi.
  Agar context uzoq yashasa, tracker shishib boradi: har bir o'qilgan entity
  xotirada qoladi, `SaveChanges()` sekinlashadi, xotira oqib ketadi.
- `DbContext` **thread-safe emas**. Bitta instance'ni ikki thread'dan ishlatish
  `InvalidOperationException: A second operation was started on this context`
  xatosini beradi.
- So'rov chegarasi — tabiiy tranzaksiya chegarasi. Bitta so'rov = bitta
  o'zgarishlar to'plami = bitta `SaveChanges()`.

Nozik joylar:

**Singleton servis ichida scoped context'ga bog'lanib qolish.**
`BackgroundService` singleton, shuning uchun unda `DbContext` ni konstruktorga
olib bo'lmaydi. To'g'ri yo'l — `IServiceScopeFactory`:

```csharp
public sealed class ReportWorker(IServiceScopeFactory scopeFactory) : BackgroundService
{
    protected override async Task ExecuteAsync(CancellationToken ct)
    {
        while (!ct.IsCancellationRequested)
        {
            using var scope = scopeFactory.CreateScope();
            var db = scope.ServiceProvider.GetRequiredService<AppDbContext>();
            await ProcessBatchAsync(db, ct);
            await Task.Delay(TimeSpan.FromMinutes(5), ct);
        }
    }
}
```

**Parallel so'rovlar.** `await Task.WhenAll(db.A.ToListAsync(), db.B.ToListAsync())`
ishlamaydi. Haqiqatan parallel kerak bo'lsa — `IDbContextFactory<T>` dan har bir
vazifa uchun alohida context olish kerak.

**Pooling.** `AddDbContextPool()` context instance'larini qayta ishlatadi. Juda
yuqori RPS'da yordam beradi, lekin context'da o'z holatini saqlaydigan maydon
(masalan `_currentUserId`) bo'lsa — u keyingi so'rovga oqib o'tadi.

### 2. `AsNoTracking()` nima qiladi va qachon ishlatmaslik kerak?

Entity'ni Change Tracker'ga yozmaydi. Natijada:

- Identity resolution yo'q — bir xil kalitli ikki satr ikki alohida obyekt bo'ladi.
- Snapshot olinmaydi, shuning uchun xotira kamroq va o'qish tezroq.
- `SaveChanges()` bu obyektlarni ko'rmaydi.

O'qish uchun (ro'yxat, hisobot, `GET` endpoint) — deyarli har doim kerak.

Ishlatmaslik kerak bo'lgan hollar:

- Obyektni o'qib, keyin o'zgartirib, `SaveChanges()` qilmoqchi bo'lsangiz.
  Tracking'siz o'zgarish saqlanmaydi.
- Graf ichida bir xil obyektga ko'p murojaat bo'lsa va ularning aynanligi
  muhim bo'lsa. 100 ta buyurtma bitta mijozga tegishli bo'lsa, tracking bilan
  1 ta `Customer` obyekti, tracking'siz — 100 ta. Bu yerda
  `AsNoTrackingWithIdentityResolution()` o'rtacha yechim.

Loyihada standart holatni teskari qilish mumkin:

```csharp
optionsBuilder.UseQueryTrackingBehavior(QueryTrackingBehavior.NoTracking);
```

Keyin o'zgartirish kerak bo'lgan joylarda `.AsTracking()` yoziladi. "O'qish ko'p,
yozish kam" API'lari uchun qulay — lekin jamoadagi hamma shuni bilishi kerak,
aks holda "nega update ishlamaydi" degan savol muqarrar.

### 3. Entity holatlari orasida qanday o'tadi? Disconnected scenariyda qanday xato qilinadi?

- `Detached` — tracker bilmaydi. Yangi `new Order()` yoki `AsNoTracking()` natijasi.
- `Added` — `db.Add()` dan keyin, `SaveChanges()` da `INSERT`.
- `Unchanged` — bazadan tracking bilan o'qilgan, hech narsa o'zgarmagan.
- `Modified` — tracked obyektning xossasi snapshot'dan farq qiladi, yoki qo'lda
  `Entry(x).State = Modified` qo'yilgan.
- `Deleted` — `db.Remove()` dan keyin, `SaveChanges()` da `DELETE`.

`SaveChanges()` dan keyin `Added` va `Modified` → `Unchanged`, `Deleted` →
`Detached`.

Eng ko'p xato qilinadigan joy — API'ga DTO kelib, undan entity yasab `Update()`
chaqirilishi:

```csharp
db.Update(order);   // butun grafni Modified qiladi
```

Bu **hamma ustunni** `UPDATE` ga qo'shadi, hatto o'zgarmaganini ham. Natijalari:
concurrency token bo'lmasa boshqa foydalanuvchining o'zgarishi yo'qoladi, audit
trigger'lar har safar ishga tushadi, `rowversion` bejiz o'sadi. To'g'rirog'i —
avval o'qib, keyin ko'chirish:

```csharp
var entity = await db.Orders.FindAsync([dto.Id], ct)
             ?? throw new NotFoundException(nameof(Order), dto.Id);
entity.Apply(dto);              // faqat haqiqatan o'zgarganlar Modified bo'ladi
await db.SaveChangesAsync(ct);
```

Bitta qo'shimcha so'rov narxi — aniqlik va xavfsizlik evaziga.

### 4. Client va server evaluation farqi nimada?

LINQ ifodasining bir qismi SQL ga tarjima qilinsa — server evaluation.
Tarjima qilinmasa va natija .NET tomonida hisoblansa — client evaluation.

EF Core 3.0 dan boshlab `Where()` ichidagi tarjima qilinmaydigan ifoda **xato
beradi**, jimgina client'ga o'tmaydi. Bu ataylab qilingan: ilgari
`Where(x => MyHelper(x.Name))` butun jadvalni tortib olib, keyin xotirada
filtrlardi — va buni odam sezmasligi mumkin edi.

Hozir client evaluation faqat eng tashqi `Select()` da ruxsat etiladi:

```csharp
// ishlaydi: Format() natija ustida, SQL dan keyin chaqiriladi
var list = await db.Users
    .Select(u => new { u.Id, Label = Format(u.FirstName, u.LastName) })
    .ToListAsync();

// xato: Where ichida tarjima qilinmaydigan metod
var bad = await db.Users
    .Where(u => Format(u.FirstName, u.LastName) == "X")
    .ToListAsync();
```

To'g'rilash yo'llari: ifodani SQL ga tushadigan shaklga keltirish; bazada
computed column yoki funksiya yasab `HasComputedColumnSql()` / `DbFunction`
bilan map qilish; yoki ataylab xotiraga olish — lekin **ataylab**,
`AsEnumerable()` yozib, kodni o'qiydigan odam buni ko'rib turadigan qilib.

### 5. Mapping da convention, data annotation va Fluent API orasida qanday tanlaysiz?

Ustuvorlik tartibi: Fluent API > data annotation > convention.

Amaliy qoidam:

- **Convention** — nomlash standartga tushsa, hech narsa yozmaslik eng yaxshisi.
  `Id` yoki `OrderId` — kalit; `CustomerId` + `Customer` navigatsiyasi — FK.
- **Data annotation** — domenga tegishli, texnologiyadan qat'i nazar to'g'ri
  qoidalar: `[Required]`, `[MaxLength(200)]`. Bular validatsiyada ham ishlatiladi.
- **Fluent API** — bazaga tegishli hamma narsa: indekslar, composite kalit,
  `OnDelete`, `HasConversion`, precision, filtrlangan indeks, schema nomi.
  Bularni atribut sifatida entity'ga yopishtirish domenni infratuzilma bilan
  aralashtiradi.

Fluent konfiguratsiyani bitta `OnModelCreating` ichiga to'plash 30 ta entity'da
500 qatorli metodga aylanadi. Shuning uchun `IEntityTypeConfiguration<T>`:

```csharp
public sealed class OrderConfiguration : IEntityTypeConfiguration<Order>
{
    public void Configure(EntityTypeBuilder<Order> b)
    {
        b.ToTable("orders");
        b.Property(x => x.Total).HasPrecision(18, 2);
        b.HasIndex(x => new { x.CustomerId, x.CreatedAt });
        b.HasMany(x => x.Items).WithOne().OnDelete(DeleteBehavior.Cascade);
    }
}
```

va bitta joyda:

```csharp
modelBuilder.ApplyConfigurationsFromAssembly(typeof(AppDbContext).Assembly);
```

### 6. TPH, TPT va TPC orasida qanday tanlaysiz?

**TPH** (standart) — bitta jadval, `Discriminator` ustuni turni aytib turadi.

- Yutuq: `JOIN` yo'q, eng tez o'qish, polimorf so'rov arzon.
- Yo'qotish: subclass'ning majburiy maydoni ham NULLable bo'lishi kerak, chunki
  boshqa turdagi satrlarda u bo'sh. Baza darajasida "karta to'lovida karta
  raqami bo'lishi shart" degan qoidani qo'ya olmaysiz. Yechim — `CHECK`:

```csharp
b.ToTable(t => t.HasCheckConstraint(
    "ck_payment_card_number",
    "payment_type <> 'card' OR card_number IS NOT NULL"));
```

**TPT** — har bir tur uchun alohida jadval, bazaviy jadval bilan 1:1 FK.

- Yutuq: NOT NULL ishlaydi, sxema normal ko'rinadi.
- Yo'qotish: har bir o'qish `JOIN`. Polimorf so'rov hamma subclass jadvaliga
  `LEFT JOIN` qiladi — 6 ta subclass bo'lsa 6 ta join. `INSERT` ikki jadvalga.

**TPC** (EF Core 7+) — har bir konkret tur uchun to'liq jadval, abstrakt bazaviy
jadval yo'q.

- Yutuq: bitta turni o'qish bitta jadvaldan, join yo'q, NOT NULL ishlaydi.
- Yo'qotish: polimorf so'rov `UNION ALL`. Kalit generatsiyasi muammo — jadvallar
  alohida, shuning uchun identity har birida 1 dan boshlanadi va ID'lar
  takrorlanadi. Shuning uchun umumiy sequence yoki `Guid`:

```csharp
modelBuilder.HasSequence<long>("payment_ids");
modelBuilder.Entity<Payment>()
    .UseTpcMappingStrategy()
    .Property(x => x.Id).HasDefaultValueSql("nextval('payment_ids')");
```

Yana: boshqa jadval `Payment` ga FK qo'ya olmaydi, chunki `Payment` jadvali yo'q.

Qoidam: **standart TPH**. Subclass'larda majburiy maydon ko'p bo'lsa va baza
darajasidagi qoida kerak bo'lsa — TPC. TPT ni faqat sxema allaqachon shunday
bo'lsa yoki boshqa tizim shu sxemani kutsa ishlataman.

### 7. Table splitting va entity splitting farqi?

Qarama-qarshi yo'nalishlar.

**Table splitting** — bitta jadval, bir nechta entity. Odatda og'ir ustunni
ajratish uchun: `Document` va `DocumentContent` bitta jadvalda, lekin
`byte[] Content` ni faqat kerak bo'lganda o'qiymiz.

**Entity splitting** — bitta entity, bir nechta jadval. Legacy sxemada ma'lumot
ikki jadvalga tarqalgan, lekin domen uchun bu bitta tushuncha.

```csharp
// table splitting
modelBuilder.Entity<Document>().ToTable("documents")
    .HasOne(d => d.Content).WithOne().HasForeignKey<DocumentContent>(c => c.Id);
modelBuilder.Entity<DocumentContent>().ToTable("documents");

// entity splitting (EF Core 7+)
modelBuilder.Entity<Customer>()
    .SplitToTable("customer_contacts", t => t.Property(c => c.Phone));
```

Table splitting'da nozik joy: ajratilgan entity'ni alohida o'chirish mumkin emas,
satr umumiy. Va navigatsiya `Required` bo'lsa — har safar ikkisi ham o'qiladi,
ya'ni optimallashtirish yo'qoladi.

### 8. Model bulk configuration qachon kerak?

Qoida hamma entity'ga yoki hamma ma'lum turdagi xossaga tegishli bo'lganda:
hamma `decimal` 18,2 bo'lsin; hamma `string` max 256; hamma jadval nomi
snake_case bo'lsin.

**`ConfigureConventions`** — eng toza, tur bo'yicha:

```csharp
protected override void ConfigureConventions(ModelConfigurationBuilder b)
{
    b.Properties<decimal>().HavePrecision(18, 2);
    b.Properties<string>().HaveMaxLength(256);
    b.Properties<DateOnly>().HaveConversion<DateOnlyConverter>();
}
```

**Metadata bo'ylab yurish** — shart murakkabroq bo'lsa (nom bo'yicha, interfeys
bo'yicha):

```csharp
foreach (var entity in modelBuilder.Model.GetEntityTypes())
{
    if (typeof(ISoftDeletable).IsAssignableFrom(entity.ClrType))
        entity.AddIndex(entity.FindProperty(nameof(ISoftDeletable.DeletedAt))!);

    entity.SetTableName(ToSnakeCase(entity.GetTableName()!));
}
```

Tartib muhim: `ConfigureConventions` `OnModelCreating` dan **oldin** ishlaydi,
shuning uchun aniq konfiguratsiya umumiysini bosib keta oladi.

### 9. EF Core qanday SQL yuborayotganini qanday ko'rasiz?

Log'da:

```csharp
options.UseNpgsql(cs)
       .LogTo(Console.WriteLine, LogLevel.Information)
       .EnableSensitiveDataLogging()   // faqat Development
       .EnableDetailedErrors();
```

`EnableSensitiveDataLogging()` parametr qiymatlarini ham ko'rsatadi — shuning
uchun production'da **hech qachon** yoqilmaydi, aks holda log'ga parol va
shaxsiy ma'lumot tushadi.

Bitta so'rovni tekshirish uchun `ToQueryString()` qulay, bazaga bormaydi:

```csharp
var sql = db.Orders.Where(o => o.Total > 100).ToQueryString();
```

Keyin shu SQL ni Postgres'da `EXPLAIN ANALYZE` bilan o'lchayman. Og'irroq tahlil
kerak bo'lsa — interceptor yozib, 200 ms dan oshgan so'rovlarni alohida
log qilaman.

### 10. N+1 muammosi qanday paydo bo'ladi va qanday yechiladi?

1 ta so'rov ro'yxatni oladi, keyin har bir element uchun yana 1 ta so'rov ketadi.
100 ta buyurtma = 101 ta so'rov.

```csharp
var orders = await db.Orders.ToListAsync();
foreach (var o in orders)
    Console.WriteLine(o.Customer.Name);   // har safar yangi SELECT
```

Yechimlar:

- `Include()` — bitta so'rovda `JOIN`.
- Faqat kerakli maydonlar kerak bo'lsa — projeksiya, eng arzoni:

```csharp
await db.Orders.Select(o => new { o.Id, Customer = o.Customer.Name }).ToListAsync();
```

- Bir nechta kolleksiya `Include` qilinganda cartesian explosion bo'ladi: 3 ta
  item × 4 ta to'lov = 12 satr, ma'lumot takrorlanadi. Bunda `AsSplitQuery()`
  har bir kolleksiyani alohida so'rovda oladi — satr kam, so'rov bir nechta.
  Tanlov: tarmoq hajmi vs so'rov soni.

Lazy loading'ni umuman yoqmaslikni afzal ko'raman: uni o'chirib qo'yish N+1 ni
darhol ko'rinadigan xatoga aylantiradi, jim sekinlashuvga emas.

### 11. Spatial data bilan ishlaganda nimaga e'tibor berish kerak?

`NetTopologySuite` + PostGIS. Ikki tuzoq bor.

**Koordinata tartibi.** `new Point(x, y)` da `x` = longitude, `y` = latitude.
Odamlar "latitude, longitude" deb gapirishga o'rgangan, shuning uchun teskari
yozish juda ko'p uchraydi — natijada nuqta Toshkent o'rniga okeanda chiqadi.

**SRID va masofa birligi.** Standart `4326` — gradusdagi geografik koordinata.
`Distance()` ni `geometry` ustida chaqirsak natija **gradusda** chiqadi, metrda
emas. Metr kerak bo'lsa ustun `geography` bo'lishi kerak:

```csharp
b.Property(x => x.Location).HasColumnType("geography (point)");
```

```csharp
var point = new Point(69.2401, 41.2995) { SRID = 4326 };
var near = await db.Branches
    .Where(b => b.Location.Distance(point) < 5000)   // metr
    .ToListAsync();
```

Va indeks: `CREATE INDEX ... USING GIST (location)` — bo'lmasa har so'rov to'liq
skanlash.

---

## ASP.NET

### 12. Bir nechta environment qanday boshqariladi?

`ASPNETCORE_ENVIRONMENT` o'zgaruvchisi `IHostEnvironment.EnvironmentName` ga
tushadi. Standart uchtasi: `Development`, `Staging`, `Production`. O'z nomimni
ham qo'yish mumkin (`QA`), lekin `IsDevelopment()` kabi yordamchi metodlar faqat
standart uchtasini biladi.

Konfiguratsiya ustma-ust yuklanadi: `appsettings.json` →
`appsettings.{Environment}.json` → User Secrets (faqat Development) →
environment variables → komanda qatori argumentlari. Keyingisi oldingisini
bosadi.

```csharp
if (app.Environment.IsDevelopment())
{
    app.UseDeveloperExceptionPage();
    app.MapOpenApi();
}
else
{
    app.UseExceptionHandler();
    app.UseHsts();
}
```

O'zim e'tibor beradigan narsa: Development va Production orasidagi farq imkon
qadar kichik bo'lishi kerak. Agar faqat production'da yoqiladigan middleware ko'p
bo'lsa, u hech qachon sinalmaydi va birinchi deploy'da "ishlamaydi" bo'lib
chiqadi. Shuning uchun Staging'ni Production'ning aniq nusxasi qilishga harakat
qilaman.

### 13. Logging provider nima va Serilog nega ishlatiladi?

`ILogger<T>` — abstraksiya, provider — log'ni qayerga yozishni bilgan amalga
oshiruvchi. Standartda Console, Debug, EventSource, EventLog (Windows).

Serilog'ga o'tishning sababi — **strukturali log**. Standart provider'da xabar
satr bo'lib yoziladi; Serilog'da xossalar alohida maydon bo'lib qoladi, shuning
uchun Seq yoki Elastic'da `OrderId = 42` bo'yicha filtrlash mumkin.

Shuning uchun log'da string interpolatsiya ishlatilmaydi:

```csharp
logger.LogInformation("Buyurtma {OrderId} yaratildi, summa {Total}", id, total);  // to'g'ri
logger.LogInformation($"Buyurtma {id} yaratildi");                                // noto'g'ri
```

Ikkinchisida `OrderId` maydon bo'lib saqlanmaydi, qidirib bo'lmaydi. Ustiga —
log darajasi o'chirilgan bo'lsa ham interpolatsiya baribir hisoblanadi.

Daraja tanlash bo'yicha qoidam:

- `Trace`/`Debug` — faqat ishlab chiqishda.
- `Information` — biznes hodisasi (buyurtma yaratildi, to'lov o'tdi).
- `Warning` — kutilmagan, lekin tizim ishlashda davom etadi (retry bo'ldi).
- `Error` — operatsiya bajarilmadi.
- `Critical` — tizim yoki uning qismi ishlamaydi.

Va `Scope` — bitta so'rov bo'yicha hamma log'ni bog'lash uchun:

```csharp
using (logger.BeginScope("{CorrelationId}", correlationId)) { ... }
```

### 14. Xatolarni markazlashgan tarzda qanday boshqarasiz?

.NET 8+ da `IExceptionHandler` eng toza yo'l:

```csharp
public sealed class DomainExceptionHandler(IProblemDetailsService svc) : IExceptionHandler
{
    public async ValueTask<bool> TryHandleAsync(
        HttpContext ctx, Exception ex, CancellationToken ct)
    {
        var (status, title) = ex switch
        {
            NotFoundException   => (StatusCodes.Status404NotFound, "Topilmadi"),
            ValidationException => (StatusCodes.Status400BadRequest, "Validatsiya xatosi"),
            _                   => (0, "")
        };

        if (status is 0) return false;       // keyingi handler ko'rsin

        ctx.Response.StatusCode = status;
        return await svc.TryWriteAsync(new ProblemDetailsContext
        {
            HttpContext    = ctx,
            ProblemDetails = new ProblemDetails { Title = title, Status = status }
        });
    }
}
```

```csharp
builder.Services.AddProblemDetails();
builder.Services.AddExceptionHandler<DomainExceptionHandler>();
builder.Services.AddExceptionHandler<FallbackExceptionHandler>();
app.UseExceptionHandler();
```

Handler'lar ro'yxatga qo'shilgan tartibda chaqiriladi; `false` qaytarsa
keyingisiga o'tadi, hech kim ushlamasa standart 500 ketadi.

Javob formati — **ProblemDetails (RFC 9457)**: `type`, `title`, `status`,
`detail`, `instance`. Bu standart, shuning uchun mijoz tomoni har bir API uchun
alohida xato formatini o'rganmaydi.

Ikki qoidam:

1. **Exception xabari mijozga chiqmaydi.** `ex.Message` ichida ulanish satri yoki
   SQL bo'lishi mumkin. Mijozga umumiy xabar, log'ga to'liq stack trace.
2. **Har bir xatoga `traceId` qo'shiladi.** Foydalanuvchi "xato chiqdi" deb
   murojaat qilganda, shu ID bilan log'dan aniq so'rovni topaman.

### 15. OpenAPI va Swagger — bir narsa emasmi?

Yo'q, va bu chalkashlik juda keng tarqalgan.

- **OpenAPI** — spetsifikatsiya, API ni JSON/YAML da tasvirlash standarti. Ilgari
  "Swagger Specification" deb atalgan, 2015 da OpenAPI Initiative'ga o'tib nomi
  o'zgargan.
- **Swagger** — SmartBear'ning asboblar to'plami: Swagger UI, Swagger Editor,
  Swagger Codegen.
- **Swashbuckle** — .NET uchun kutubxona, OpenAPI hujjatini generatsiya qiladi va
  Swagger UI ni ulaydi.

Ya'ni "Swagger hujjati" emas — **OpenAPI hujjati**; uni ko'rsatadigan sahifa —
Swagger UI.

Amaliy tomoni: .NET 9 dan boshlab Web API shabloniga Swashbuckle
**qo'shilmaydi**, o'rniga `Microsoft.AspNetCore.OpenApi` keladi:

```csharp
builder.Services.AddOpenApi();
app.MapOpenApi();                    // /openapi/v1.json
```

Bu faqat hujjatni generatsiya qiladi, UI bermaydi. UI kerak bo'lsa alohida
qo'shiladi — Swashbuckle, Scalar yoki boshqa. .NET 10 da standart chiqish
formati OpenAPI 3.1.

### 16. API ni versiyalashning qanday usullari bor va qaysi birini tanlaysiz?

| Usul | Ko'rinishi | Fikr |
|---|---|---|
| URL segment | `/api/v2/orders` | Ko'rinadigan, keshlanadigan, brauzerdan sinash oson |
| Query string | `/api/orders?api-version=2` | URL iflos emas, lekin ko'zga tashlanmaydi |
| Custom header | `X-Api-Version: 2` | URL toza, lekin sinash qiyin, kesh murakkab |
| Media type | `Accept: application/json;v=2` | HTTP bo'yicha eng to'g'ri, amalda eng noqulay |

Men **URL segment** ni tanlayman: hamma ko'radi, log'da ko'rinadi, CDN keshlaydi,
Postman'da qo'lda o'zgartirish oson.

```csharp
builder.Services.AddApiVersioning(o =>
{
    o.DefaultApiVersion = new ApiVersion(1);
    o.AssumeDefaultVersionWhenUnspecified = true;
    o.ReportApiVersions = true;             // api-supported-versions header
}).AddApiExplorer(o => o.GroupNameFormat = "'v'V");
```

Muhimrog'i — **qachon versiya oshirish kerak**. Faqat buzuvchi o'zgarishda:
maydonni o'chirish, nomini yoki tipini o'zgartirish, majburiy parametr qo'shish,
status kodni o'zgartirish. Yangi ixtiyoriy maydon qo'shish buzmaydi — v2 kerak
emas. Eski versiyani `Deprecated = true` va `Sunset` header bilan oldindan
belgilab qo'yish kerak.

### 17. SignalR qanday transport'lardan foydalanadi?

Uchtasi, ustuvorlik bo'yicha:

1. **WebSockets** — ikki tomonlama, bitta TCP ulanish, eng kam ortiqcha yuk.
2. **Server-Sent Events** — faqat serverdan mijozga; mijozdan serverga alohida
   HTTP so'rov ketadi.
3. **Long Polling** — so'rov javobni kutib turadi, javob kelsa darhol yangi
   so'rov yuboriladi.

Ulanish `POST /hub/negotiate` bilan boshlanadi: server `connectionId` va
qo'llab-quvvatlanadigan transport ro'yxatini qaytaradi, mijoz eng yaxshisini
tanlaydi va ishlamasa pastga tushadi.

Amalda muhim bo'lgan narsalar:

**Reverse proxy WebSocket upgrade'ni o'tkazishi kerak.** Nginx'da
`proxy_set_header Upgrade $http_upgrade;` va `Connection "upgrade"` bo'lmasa,
SignalR jimgina long polling'ga tushadi va hamma "nega sekin" deb hayron bo'ladi.

**Sticky session yoki backplane.** Bir nechta instance bo'lsa, long polling va
SSE da mijozning har bir so'rovi bitta serverga tushishi kerak:

```csharp
builder.Services.AddSignalR().AddStackExchangeRedis(redisConnectionString);
```

Backplane har bir instance'dagi xabarni boshqalariga tarqatadi. Lekin bu "scale
out" muammosini to'liq yechmaydi: har bir instance baribir hamma xabarni oladi.

### 18. Hub'da mijozlarga qanday murojaat qilinadi va `Hub<T>` nega yaxshiroq?

```csharp
await Clients.All.SendAsync("ReceiveMessage", user, text);
await Clients.Caller.SendAsync(...);
await Clients.Others.SendAsync(...);
await Clients.Client(connectionId).SendAsync(...);
await Clients.Group("room-5").SendAsync(...);
await Clients.User(userId).SendAsync(...);        // bir foydalanuvchining hamma qurilmasi
```

`SendAsync` da metod nomi — satr. Xato yozilsa kompilyator jim, mijoz xabarni
olmaydi va buni faqat ishga tushirganda bilib olasiz.

`Hub<T>` buni to'g'rilaydi:

```csharp
public interface IChatClient
{
    Task ReceiveMessage(string user, string text);
}

public sealed class ChatHub : Hub<IChatClient>
{
    public Task Send(string text) =>
        Clients.All.ReceiveMessage(Context.UserIdentifier!, text);
}
```

Endi nomni kompilyator tekshiradi. .NET mijozida ham `nameof()` bilan shunga
yaqin ishonch olish mumkin:

```csharp
connection.On<string, string>(nameof(IChatClient.ReceiveMessage),
    (user, text) => Console.WriteLine($"{user}: {text}"));
```

Yana bir muhim narsa: `Hub` transient — har bir chaqiruv uchun yangi instance.
Shuning uchun hub'da holat saqlanmaydi, `Context` ni saqlab keyinroq ishlatish
ham mumkin emas.

### 19. Formatter nima? `System.Text.Json` va `Newtonsoft.Json` orasidagi tanlov.

Input formatter so'rov tanasini obyektga, output formatter obyektni javob
tanasiga aylantiradi. Tanlov `Content-Type` va `Accept` header'lari bo'yicha
content negotiation orqali bo'ladi.

Standart — `System.Text.Json`: tezroq, kam xotira, lekin qattiqqo'l.

`Newtonsoft.Json` ga o'tish kerak bo'ladigan holatlar:

- `JsonPatchDocument` (`PATCH` uchun) — rasmiy qo'llab-quvvatlash Newtonsoft'da.
- `TypeNameHandling`, murakkab custom contract resolver.
- Legacy mijoz juda kechirimli parsing kutadi (izohli JSON, oxirgi vergul).

```csharp
builder.Services.AddControllers()
    .AddNewtonsoftJson()
    .AddXmlSerializerFormatters();
```

`System.Text.Json` da ko'p uchraydigan sozlamalar:

```csharp
builder.Services.ConfigureHttpJsonOptions(o =>
{
    o.SerializerOptions.PropertyNamingPolicy = JsonNamingPolicy.CamelCase;
    o.SerializerOptions.DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull;
    o.SerializerOptions.Converters.Add(new JsonStringEnumConverter());
});
```

Enum'ni satr sifatida yuborish bo'yicha fikrim: raqam API shartnomasini mo'rt
qiladi — enum'ga yangi qiymat o'rtaga qo'shilsa raqamlar siljiydi. Satr esa
o'zini tushuntiradi.

---

## Web

### 20. Web server nima qiladi? Kestrel va IIS/Nginx qanday birga ishlaydi?

Web server TCP portni tinglaydi, HTTP so'rovini parse qiladi va javob qaytaradi.
Kestrel — ASP.NET Core ning o'z serveri, cross-platform va juda tez.

Kestrel to'g'ridan-to'g'ri internetga qarashi mumkin, lekin odatda oldiga reverse
proxy qo'yiladi. Sabablari: TLS sertifikatini markazlashgan boshqarish, bir
necha ilovani bitta 443 portda host qilish, statik faylni ilovaga bormasdan
berish, sekin mijozdan (slowloris) himoya, request buffering.

Bunda muhim detal — **forwarded header'lar**. Proxy orqasida `HttpContext`
mijozning IP'si o'rniga proxy IP'sini ko'radi va sxema `http` bo'lib qoladi:

```csharp
app.UseForwardedHeaders(new ForwardedHeadersOptions
{
    ForwardedHeaders = ForwardedHeaders.XForwardedFor | ForwardedHeaders.XForwardedProto
});
```

Buni `UseForwardedHeaders` ni **eng boshida** chaqirish kerak, aks holda
keyingi middleware noto'g'ri IP ko'radi. Va `KnownProxies` ni to'ldirish kerak —
aks holda har qanday mijoz `X-Forwarded-For` ni o'zi yozib IP'ni soxtalashtiradi.

### 21. IPv4 va IPv6 farqi, local/intranet/global IP nima?

IPv4 — 32 bit, ~4.3 mlrd manzil, nuqta bilan ajratilgan 4 oktet. IPv6 — 128 bit,
ikki nuqta bilan ajratilgan 8 guruh, NAT'ga ehtiyoj yo'q.

Diapazonlar (RFC 1918 — xususiy):

- `10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16` — intranet, internetga
  marshrutlanmaydi.
- `127.0.0.0/8` — loopback, faqat o'z mashinasi.
- `169.254.0.0/16` — link-local, DHCP ishlamaganda.
- Qolgani — global.

IPv6 da: `::1` — loopback, `fe80::/10` — link-local, `fc00::/7` — unique local.

Amaliy tomoni: `localhost` ikki manzilga yechilishi mumkin — `127.0.0.1` va
`::1`. Shuning uchun server faqat IPv4 da tinglaydigan bo'lsa, `localhost:5000`
ba'zan ulanmaydi. `0.0.0.0` — hamma IPv4 interfeys, `[::]` — hammasi, IPv6 ham.
Docker konteyner ichida `127.0.0.1` ga bog'lash tashqaridan ulanishni butunlay
to'sadi — bu eng ko'p uchraydigan "konteynerda ishlamaydi" sababi.

### 22. Portlar qanday taqsimlangan? Qaysilarini ishlatish mumkin?

- `0–1023` — well-known. Linux'da bunga bog'lanish uchun root yoki
  `CAP_NET_BIND_SERVICE` kerak.
- `1024–49151` — registered, IANA'da ro'yxatga olingan (5432 Postgres,
  5672 RabbitMQ, 6379 Redis).
- `49152–65535` — dynamic/ephemeral, chiquvchi ulanishlar uchun OS beradi.

O'z ilovam uchun 1024 dan yuqorisini tanlayman va ephemeral diapazonga
tushmaydigan qilaman — aks holda OS shu portni boshqa chiquvchi ulanishga berib
yuborgan paytda ilova ko'tarilmaydi.

Bilish kerak bo'lgan amaliy muammo — **ephemeral port exhaustion**. `HttpClient`
ni har so'rovda `new` qilsak, har bir socket `TIME_WAIT` da bir necha daqiqa
qoladi va portlar tugaydi: `SocketException: Only one usage of each socket
address is normally permitted`. Shuning uchun `IHttpClientFactory`.

### 23. URL qismlari qanday nomlanadi? Query va path orasida qanday tanlaysiz?

```
https://api.example.com:8443/v1/orders/42/items?page=2&sort=name#top
\___/   \_____________/ \__/ \_________________/ \_____________/ \_/
scheme      host        port        path             query      fragment
```

**Origin** = scheme + host + port. Uchtasidan biri farq qilsa boshqa origin —
CORS aynan shu bo'yicha ishlaydi. `https://a.com` va `https://a.com:8443` boshqa
origin, `http` va `https` ham boshqa.

Fragment serverga **yuborilmaydi** — faqat brauzerda qoladi. Shuning uchun
fragment'ga hech qachon ma'lumot joylashtirmaydilar... aniqrog'i, OAuth implicit
flow aynan shu xossadan foydalangan, lekin bu endi tavsiya etilmaydi.

Path va query orasidagi tanlov qoidam:

- **Path** — resursni aniqlaydi, ierarxiya: `/orders/42/items`. Resurs o'zgarsa
  URL o'zgaradi.
- **Query** — bir xil resurs to'plamini filtrlaydi, saralaydi, sahifalaydi:
  `?status=paid&page=2`. Query'ni olib tashlasak ham so'rov mantiqan to'g'ri
  qoladi, faqat kengroq natija beradi.

Ya'ni `/orders/paid` emas, `/orders?status=paid` — chunki `paid` resurs emas,
filtr.

### 24. Cookie, localStorage va sessionStorage orasidagi farq?

| | Cookie | localStorage | sessionStorage |
|---|---|---|---|
| Hajm | ~4 KB | ~5–10 MB | ~5–10 MB |
| Avtomatik yuborish | Ha, har so'rovda | Yo'q | Yo'q |
| JS o'qishi | `HttpOnly` bo'lmasa — ha | Ha | Ha |
| Yashash muddati | `Expires`/`Max-Age` | Doimiy | Tab yopilguncha |

Token saqlash bo'yicha fikrim: **`HttpOnly` + `Secure` + `SameSite` cookie**
afzalroq, chunki XSS orqali o'qib bo'lmaydi. localStorage'dagi JWT'ni esa
sahifaga tushgan har qanday skript o'qiydi — bitta zaif npm paketi yetarli.

Cookie'ning o'z muammosi — CSRF, chunki brauzer uni avtomatik yuboradi. Yechim:
`SameSite=Lax` (standart) yoki `Strict`, va holat o'zgartiradigan so'rovlarga
anti-forgery token.

`SameSite=None` qo'yish kerak bo'lsa (frontend boshqa domenda) — `Secure`
majburiy va CSRF himoyasi qo'lda qilinadi.

Server tomonidagi session — bu cookie'da faqat `SessionId` yuborib, ma'lumotni
serverda (Redis) saqlash. Bu stateless API uchun mos emas, lekin sessionni
darhol bekor qilish kerak bo'lsa JWT'dan ustun.

### 25. User-Agent nima uchun ishonchsiz? Client Hints nima?

`User-Agent` — mijoz o'zi yuboradigan satr, ya'ni **har qanday qiymat yozishi
mumkin**. Tarixan brauzerlar bir-birini "taqlid" qilgani uchun u butunlay
chalkash bo'lib ketdi: Chrome ham `Mozilla/5.0`, ham `Safari`, ham `Chrome` deb
yozadi.

Shuning uchun:

- Xavfsizlik qarori UA ga asoslanmaydi.
- Funksional qarorlar ham UA ga emas, **feature detection** ga asoslanadi.
- UA faqat analitika va diagnostika uchun yaxshi.

Hozirgi yo'nalish — **User-Agent Client Hints**: UA satri qisqartiriladi
(reduced UA), batafsil ma'lumot alohida header'lar bilan va faqat server
so'rasa beriladi:

```
Sec-CH-UA: "Chromium";v="128", "Not;A=Brand";v="24"
Sec-CH-UA-Mobile: ?0
Sec-CH-UA-Platform: "Windows"
```

Batafsilrog'i (`Sec-CH-UA-Platform-Version`, `Sec-CH-UA-Model`) uchun server
`Accept-CH` header'i bilan so'rashi kerak. Maqsad — fingerprinting'ni
kamaytirish.

### 26. Reverse proxy nima qiladi? Forward proxy'dan farqi?

**Forward proxy** mijoz tomonida: mijoz uning orqasiga yashiringan.
**Reverse proxy** server tomonida: serverlar yashiringan, mijoz faqat proxy'ni
ko'radi.

Reverse proxy beradigan narsalar: TLS termination, load balancing, statik fayl
keshi, siqish, rate limiting, sekin mijozdan himoya, bir nechta ilovani bitta
domenda birlashtirish, canary/blue-green yo'naltirish.

Nginx'da minimal to'g'ri konfiguratsiya:

```nginx
location /api/ {
    proxy_pass         http://127.0.0.1:5000;
    proxy_http_version 1.1;
    proxy_set_header   Upgrade $http_upgrade;
    proxy_set_header   Connection "upgrade";
    proxy_set_header   Host $host;
    proxy_set_header   X-Real-IP $remote_addr;
    proxy_set_header   X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header   X-Forwarded-Proto $scheme;
}
```

`proxy_http_version 1.1` bo'lmasa WebSocket va keep-alive ishlamaydi — bu
standart xato.

.NET ichida reverse proxy kerak bo'lsa **YARP** bor; u konfiguratsiyani
`appsettings.json` dan oladi va dinamik marshrutlash uchun kod yozish imkonini
beradi.

### 27. API Gateway va reverse proxy — bir xil narsa emasmi?

Reverse proxy — transport darajasidagi vazifa: so'rovni to'g'ri backend'ga
uzatish. API Gateway esa undan yuqorida turadi va **API mantiqini** biladi:

- Autentifikatsiya va avtorizatsiyani markazlashtirish (token bir joyda
  tekshiriladi).
- Rate limiting va kvota — mijoz/tarif bo'yicha.
- So'rov va javobni o'zgartirish, protokol tarjimasi (REST → gRPC).
- Bir nechta servis javobini birlashtirish (aggregation).
- Markazlashgan OpenAPI hujjati.

Har bir reverse proxy gateway emas, lekin har bir gateway reverse proxy
vazifasini ham bajaradi.

**BFF** (Backend for Frontend) — gateway'ning alohida ko'rinishi: har bir mijoz
turi (web, mobil) uchun alohida gateway, chunki ularning ehtiyoji boshqacha.
Mobilga kam maydonli, bitta so'rovli javob kerak; web'ga boshqacha.

Gateway'ning xavfi — **u yangi monolitga aylanib qolishi**. Biznes mantiqini
gateway'ga ko'chirish boshlansa, har bir o'zgarish uchun gateway'ni deploy qilish
kerak bo'ladi va u hamma jamoaning yo'lida turadi.

### 28. SSH qanday ishlaydi? Parol o'rniga kalit nega yaxshiroq?

Uch qatlam: transport (kalit almashinuvi, shifrlangan kanal), autentifikatsiya,
keyin kanal(lar).

Kalit asosidagi autentifikatsiyada yopiq kalit **tarmoqdan o'tmaydi**: server
tasodifiy ma'lumot yuboradi, mijoz uni yopiq kaliti bilan imzolaydi, server ochiq
kalit bilan tekshiradi. Shuning uchun brute force ham, parolni ushlab olish ham
ishlamaydi.

```bash
ssh-keygen -t ed25519 -C "orzibek@laptop"
ssh-copy-id -i ~/.ssh/id_ed25519.pub user@server
```

Server tomonida `/etc/ssh/sshd_config` da men qo'yadigan sozlamalar:

```
PasswordAuthentication no
PermitRootLogin no
PubkeyAuthentication yes
```

Birinchi ulanishda chiqadigan "host key fingerprint" so'rovi — MITM'ga qarshi
himoya. Uni o'ylamasdan `yes` qilish odat bo'lib ketgan, lekin keyin fingerprint
o'zgarsa ogohlantirish chiqadi va bunga jiddiy qarash kerak.

Amalda ko'p ishlatadigan narsalarim: `ssh -L 5433:localhost:5432 user@server` —
serverdagi Postgres'ni mahalliy portga tunnel qilish; `~/.ssh/config` da host
alias; `ssh-agent` bilan parolli kalitni bir marta ochish.

### 29. REST API best practice'lari: pagination'ni qanday qilasiz?

Ikki yondashuv.

**Offset-based** (`?page=2&size=20` → `LIMIT 20 OFFSET 20`):

- Oson, sahifa raqamiga o'tish mumkin, umumiy sonni ko'rsatish mumkin.
- Katta offset'da sekin: `OFFSET 100000` baza baribir 100 000 satrni o'qib
  tashlaydi.
- Ma'lumot o'zgarsa sahifalar siljiydi — yangi element qo'shilsa, 2-sahifada
  1-sahifaning oxirgi elementi takrorlanadi.

**Cursor-based** (`?after=eyJpZCI6NDJ9&size=20`):

- Barqaror, katta ma'lumotda ham tez, chunki `WHERE (created_at, id) < (...)`
  indeksdan foydalanadi.
- Sahifa raqamiga o'tib bo'lmaydi, umumiy sonni berish qiyin.

Men infinite scroll va katta jadval uchun cursor, admin panel uchun offset
tanlayman. Cursor'ni **opaque** qilaman (base64) — aks holda mijozlar uning
ichki tuzilishiga bog'lanib qoladi.

Boshqa best practice'lar: resurs nomlari ko'plikda va ot (`/orders`, `/orders/42`),
harakatlar HTTP metodida (`POST /orders/42/cancel` kabi istisnolar bo'ladi),
to'g'ri status kodlar (201 + `Location`, 204, 409, 422), filtr query'da,
javobda envelope'dan ko'ra toza resurs, xatolarda ProblemDetails.

**HATEOAS** — javobda keyingi mumkin bo'lgan harakatlar havolasi:

```json
{ "id": 42, "status": "paid",
  "_links": { "self": "/orders/42", "refund": "/orders/42/refund" } }
```

Nazariyada mijozni URL tuzilishidan ajratadi. Amalda kam uchraydi, chunki
mijozlar baribir URL'ni qattiq yozadi va javob hajmi oshadi. Lekin bitta foydasi
real: `_links` da `refund` bo'lmasa, mijoz tugmani ko'rsatmaydi — ya'ni ruxsat
mantiqi serverda qoladi.

### 30. WebSocket protokoli qanday ishlaydi? Qachon SignalR emas, toza WebSocket?

Ulanish oddiy HTTP `GET` bilan boshlanadi va **upgrade** qilinadi:

```
GET /ws HTTP/1.1
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==
Sec-WebSocket-Version: 13
```

Server `101 Switching Protocols` qaytaradi va `Sec-WebSocket-Accept` ni kalitdan
hisoblab yuboradi. Shundan keyin bitta TCP ulanish ustida ikki tomonlama frame
almashinuvi boradi — HTTP header'lari qayta yuborilmaydi, shuning uchun ortiqcha
yuk juda kam.

Bilish kerak bo'lgan detallar:

- Frame turlari: text, binary, close, ping, pong. **Ping/pong** — ulanish
  tirikligini tekshirish uchun; proxy'lar jim ulanishni 60 soniyada uzib
  qo'yishi mumkin, shuning uchun keep-alive interval muhim.
- Mijozdan serverga frame'lar **masking** qilinadi (xavfsizlik uchun, keshlovchi
  proxy'larni chalg'itmaslik maqsadida).
- `wss://` — TLS ustida; production'da faqat shu.
- CORS WebSocket'ga **qo'llanmaydi**. Shuning uchun `Origin` header'ini server
  o'zi tekshirishi kerak, aks holda boshqa sayt sizning socket'ingizga ulanadi.

SignalR — WebSocket ustidagi qatlam: fallback, reconnect, RPC, guruhlar,
serializatsiya. Toza WebSocket'ni men mijoz .NET bo'lmaganda va protokol
allaqachon belgilanganda (masalan birja ma'lumoti, tashqi tizim talabi)
ishlataman. Qolgan hollarda SignalR qo'lda yozishim kerak bo'lgan narsalarni
allaqachon bergan.

---

## Auth

### 31. Parolni bazada qanday saqlaysiz?

Hashlash, lekin umumiy maqsadli hash bilan emas. SHA-256 **juda tez** — aynan
shuning uchun u parol uchun yaroqsiz: GPU sekundda milliardlab variantni
sinaydi.

Parol uchun maxsus, ataylab sekin funksiyalar ishlatiladi:

- **Argon2id** — bugungi tavsiya; xotira talab qiladi, shuning uchun GPU/ASIC
  hujumini qimmatlashtiradi.
- **bcrypt** — eski, lekin ishonchli; work factor sozlanadi.
- **PBKDF2** — FIPS talab qilinsa; ASP.NET Core Identity standart shuni
  ishlatadi.

Har bir parolga **unikal salt** kerak — bo'lmasa bir xil parollar bir xil hash
beradi va rainbow table ishlaydi. Zamonaviy kutubxonalar salt'ni hash satrining
ichiga o'zi joylaydi.

Taqqoslash **doimiy vaqtda** bo'lishi kerak:

```csharp
CryptographicOperations.FixedTimeEquals(computed, stored);
```

Oddiy `==` baytlarni birinchi farqda to'xtatadi va vaqt orqali ma'lumot oqadi.

Boshqa amaliy qoidalar: parol uzunligi muhim, murakkablik talabi emas — minimal
8–12, maksimal chegara 64+ (qisqa maksimal menejer parollarini buzadi);
ma'lum buzilgan parollar ro'yxatiga tekshirish; login xatosida "parol xato"
emas, "login yoki parol xato" deyish (user enumeration); muvaffaqiyatsiz
urinishlarga rate limiting.

### 32. MFA qanday ishlaydi? TOTP ning ichida nima bor?

MFA — kamida ikki xil **turdagi** omil: bilgan narsa (parol), egasi bo'lgan
narsa (telefon, kalit), o'zi bo'lgan narsa (barmoq izi). Ikki parol MFA emas.

TOTP (RFC 6238): server va mijoz umumiy maxfiy kalitni bilishadi; kod
`HMAC(secret, current_time / 30)` dan hisoblanadi va 6 raqamga qisqartiriladi.
Tarmoqdan hech narsa o'tmaydi, shuning uchun ushlab olish mumkin emas.

Amalda e'tibor beradigan narsalar:

- **Vaqt siljishi.** Mijoz soati bir oz adashishi mumkin, shuning uchun server
  ±1 oyna (jami 90 soniya) qabul qiladi.
- **Qayta ishlatishni to'sish.** Ishlatilgan kodni 30 soniya davomida eslab
  qolish kerak, aks holda ushlab olingan kod bir necha marta ishlatiladi.
- **Recovery kodlari.** Telefon yo'qolsa foydalanuvchi qulfda qoladi. Bir marta
  ishlatiladigan 8–10 ta kod yaratib, ularni ham hashlab saqlaymiz.
- **Secret'ni shifrlab saqlash.** Baza oqib ketsa, TOTP secret'i parol
  hash'idan ko'ra xavfliroq, chunki uni qaytarib bo'lmaydigan shaklda saqlash
  mumkin emas — kerak bo'lganda ishlatish uchun ochiq bo'lishi kerak.

SMS — eng kuchsiz omil (SIM swap, SS7), lekin hech qanday MFA'dan ko'ra
yaxshiroq. WebAuthn/passkey — eng kuchlisi, phishing'ga ham qarshi.

### 33. OAuth 2.0 va OpenID Connect farqi nimada?

**OAuth 2.0 — avtorizatsiya protokoli**: uchinchi tomon ilovasiga mening nomimdan
resursga kirish ruxsatini berish. U "bu kim" degan savolga javob bermaydi.

**OpenID Connect — OAuth 2.0 ustidagi autentifikatsiya qatlami**: `id_token`
(JWT) qo'shadi va "bu kim" degan savolga javob beradi, `UserInfo` endpoint va
standart `scope`/`claim` lar bilan.

Shuning uchun "OAuth bilan login qilish" aslida noto'g'ri ibora — login uchun
OIDC kerak. OAuth'ning `access_token` i foydalanuvchi haqida hech narsa
kafolatlamaydi.

Hozirgi tavsiya etilgan flow — **Authorization Code + PKCE**, hamma mijoz turi
uchun (SPA, mobil, server). Implicit flow eskirgan, Resource Owner Password
Credentials ham tavsiya etilmaydi.

PKCE nima uchun kerak: mobil/SPA mijozda `client_secret` ni yashirib bo'lmaydi.
Shuning uchun mijoz tasodifiy `code_verifier` yaratadi, uning SHA-256 hash'ini
(`code_challenge`) avtorizatsiya so'rovi bilan yuboradi, keyin token almashinuvida
asl `code_verifier` ni ko'rsatadi. Authorization code'ni o'g'irlagan hujumchi
`code_verifier` ni bilmaydi, shuning uchun uni ishlata olmaydi.

Yana: `state` — CSRF uchun, `nonce` — `id_token` ni so'rovga bog'lash uchun.

### 34. JWT tuzilishi qanday va uni qanday to'g'ri tekshirasiz?

Uch qism, nuqta bilan ajratilgan, har biri base64url:

```
header.payload.signature
```

- Header: `alg`, `typ`, ba'zan `kid`.
- Payload: claim'lar — `iss`, `sub`, `aud`, `exp`, `nbf`, `iat`, `jti` va o'z
  claim'larim.
- Signature: birinchi ikki qismning imzosi.

Juda muhim: **payload shifrlanmagan, faqat kodlangan**. Har kim uni o'qiydi.
Shuning uchun JWT'ga maxfiy ma'lumot solinmaydi.

Tekshirishda minimal to'plam:

```csharp
options.TokenValidationParameters = new TokenValidationParameters
{
    ValidateIssuer           = true,
    ValidIssuer              = cfg["Jwt:Issuer"],
    ValidateAudience         = true,
    ValidAudience            = cfg["Jwt:Audience"],
    ValidateLifetime         = true,
    ClockSkew                = TimeSpan.FromSeconds(30),
    ValidateIssuerSigningKey = true,
    IssuerSigningKey         = new SymmetricSecurityKey(key),
    ValidAlgorithms          = ["HS256"]
};
```

Klassik hujumlar va ularga qarshi himoya:

- **`alg: none`** — imzo yo'q deb e'lon qilish. `ValidAlgorithms` ni aniq
  belgilash yechadi.
- **Algoritm almashtirish** (RS256 → HS256): hujumchi ochiq kalitni HMAC siri
  sifatida ishlatadi. Yana shu — ruxsat etilgan algoritmni qattiq belgilash.
- **`ClockSkew` standart 5 daqiqa** — ya'ni muddati tugagan token yana 5 daqiqa
  ishlaydi. Buni kamaytirish kerak.

JWT'ning tub muammosi — uni **bekor qilib bo'lmaydi**. Foydalanuvchini bloklasam
ham, uning tokeni `exp` gacha ishlaydi. Shuning uchun: access token qisqa
(5–15 daqiqa), refresh token uzoq va **bazada saqlanadi** (demak bekor
qilinadi), kritik harakatlarda holat qayta tekshiriladi.

### 35. RBAC, ABAC, PBAC, DAC, MAC — bu modellar qanday farq qiladi?

- **RBAC** — ruxsat rolga beriladi, rol foydalanuvchiga. Tushunarli, auditga
  qulay. Muammosi — **role explosion**: "filial-1 menejeri", "filial-2 menejeri"
  kabi rollar ko'payib ketadi.
- **ABAC** — qaror atributlar bo'yicha: kim (bo'lim, lavozim), nima (egasi,
  maxfiylik darajasi), kontekst (vaqt, IP). Moslashuvchan, lekin "bu odam nimaga
  kira oladi" degan savolga javob berish qiyinlashadi.
- **PBAC** — ABAC'ning markazlashgan siyosat tili bilan ko'rinishi (XACML,
  OPA/Rego). Siyosat koddan ajratilgan va alohida boshqariladi.
- **DAC** — resurs egasi ruxsat beradi (fayl tizimi, Google Docs'da "share").
- **MAC** — tizim markazlashgan yorliqlar bo'yicha majburlaydi, ega o'zgartira
  olmaydi (SELinux, harbiy maxfiylik darajalari).

ASP.NET Core'da amalda RBAC va ABAC aralash bo'ladi. Rol tekshiruvi:

```csharp
[Authorize(Roles = "Manager")]
```

Lekin men **policy** ni afzal ko'raman, chunki u rolni koddan ajratadi:

```csharp
builder.Services.AddAuthorizationBuilder()
    .AddPolicy("CanApprove", p => p.RequireClaim("permission", "order:approve"));
```

Resursga bog'liq qaror (masalan "faqat o'z buyurtmasini ko'rsin") atributda
ifodalanmaydi, shuning uchun resource-based avtorizatsiya kerak:

```csharp
var result = await authorizationService.AuthorizeAsync(User, order, "OrderOwner");
if (!result.Succeeded) return Forbid();
```

Qoidam: rolni **nima qilishi mumkinligiga** emas, **kimligiga** qarab beraman;
tekshiruvni esa har doim ruxsat (`permission`) bo'yicha qilaman. Shunda yangi rol
qo'shish kodni o'zgartirmaydi.

---

## Design pattern

### 36. Repository pattern'ning maqsadi nima? EF Core ustida u kerakmi?

Maqsadi — domen kodini ma'lumot manbasidan ajratish: domen "buyurtmani ID bo'yicha
ber" deydi, bu SQL, HTTP yoki fayl bo'lishi uni qiziqtirmaydi.

Lekin `DbSet<T>` allaqachon repository, `DbContext` allaqachon Unit of Work.
Shuning uchun ustiga yana generic repository yozish ko'pincha **sof zarar**:

```csharp
public interface IRepository<T>
{
    Task<T?> GetByIdAsync(int id);
    Task<IEnumerable<T>> GetAllAsync();   // butun jadval — xavfli
    Task AddAsync(T entity);
}
```

Muammolari: `Include`, projeksiya, `AsSplitQuery`, `IQueryable` kompozitsiyasi
yo'qoladi; `GetAllAsync()` kimdir albatta ishlatadi; natijada interfeys
`IQueryable` qaytaradigan bo'lib ketadi — va u holda abstraksiyadan ma'no
qolmaydi, chunki chaqiruvchi baribir EF semantikasini biladi.

Men ishlatadigan shakl — **domen tilida, aniq metodlari bor repository**:

```csharp
public interface IOrderRepository
{
    Task<Order?> FindWithItemsAsync(OrderId id, CancellationToken ct);
    Task<IReadOnlyList<Order>> ListOverdueAsync(DateOnly asOf, CancellationToken ct);
    void Add(Order order);
}
```

Bu yerda abstraksiya haqiqatan foyda beradi: so'rov mantiqi bir joyda, test
qilish oson, chaqiruvchi EF'ni bilmaydi.

Repository kerak bo'lmaydigan hollar: CQRS'ning o'qish tomoni (query handler
to'g'ridan-to'g'ri `DbContext` bilan ishlashi toza bo'ladi), oddiy CRUD API.

### 37. Unit of Work nima va `SaveChanges` undan nimasi bilan farq qiladi?

Unit of Work — bir nechta o'zgarishni bitta mantiqiy tranzaksiyaga jamlash:
hammasi birga saqlanadi yoki hech biri saqlanmaydi.

`DbContext` **o'zi** Unit of Work: `SaveChanges()` hamma kuzatilgan o'zgarishni
bitta tranzaksiyada yuboradi.

Shuning uchun `IUnitOfWork` interfeysini qo'shishning ma'nosi faqat bitta
holatda bor — domen qatlami `DbContext` ni ko'rmasligi kerak bo'lsa:

```csharp
public interface IUnitOfWork
{
    Task<int> SaveChangesAsync(CancellationToken ct = default);
}
```

Nima **noto'g'ri** bo'ladi: har bir repository o'z ichida `SaveChanges()`
chaqirsa. Unda ikki repository'ni ketma-ket chaqirgan handler yarim holatda
qolishi mumkin — birinchisi saqlandi, ikkinchisi xato berdi. `SaveChanges()`
har doim eng tashqi qatlamda, bitta joyda chaqirilishi kerak.

Bir nechta `SaveChanges()` chaqiruvi haqiqatan kerak bo'lsa (masalan generatsiya
qilingan ID keyingi qadamga kerak), ularni aniq tranzaksiyaga o'raymiz:

```csharp
await using var tx = await db.Database.BeginTransactionAsync(ct);
// ...
await tx.CommitAsync(ct);
```

Va `TransactionScope` emas — u async bilan muammoli va distributed tranzaksiyaga
olib boradi.

### 38. Options pattern nima? `IOptions`, `IOptionsSnapshot`, `IOptionsMonitor` farqi?

Konfiguratsiyani satr kaliti bilan emas, tipik klass bilan olish:

```csharp
public sealed class SmtpOptions
{
    public const string Section = "Smtp";

    [Required] public string Host { get; init; } = "";
    [Range(1, 65535)] public int Port { get; init; } = 587;
}
```

```csharp
builder.Services.AddOptions<SmtpOptions>()
    .BindConfiguration(SmtpOptions.Section)
    .ValidateDataAnnotations()
    .ValidateOnStart();            // xato bo'lsa ilova ko'tarilmaydi
```

`ValidateOnStart()` muhim: aks holda noto'g'ri konfiguratsiya faqat birinchi
ishlatilganda — ya'ni allaqachon production'da — chiqadi.

Uchta interfeys:

| Interfeys | Lifetime | `reloadOnChange` ni ko'radimi |
|---|---|---|
| `IOptions<T>` | Singleton | Yo'q, bir marta o'qiydi |
| `IOptionsSnapshot<T>` | Scoped | Ha, so'rov boshida yangilanadi |
| `IOptionsMonitor<T>` | Singleton | Ha, `CurrentValue` har safar yangi |

Qoidam: odatda `IOptions<T>`. Konfiguratsiya ishlab turganda o'zgarishi kerak
bo'lsa — so'rov ichida `IOptionsSnapshot<T>`, singleton/background servisda
`IOptionsMonitor<T>`.

Named options bir xil tipdan bir nechta konfiguratsiya kerak bo'lganda:

```csharp
builder.Services.Configure<SmtpOptions>("primary", cfg.GetSection("Smtp:Primary"));
// IOptionsSnapshot<SmtpOptions>.Get("primary")
```

---

## Testing

### 39. Method mocking nima? Nimani mock qilish kerak, nimani yo'q?

Mock — haqiqiy bog'liqlik o'rniga test boshqaradigan obyekt. Maqsad —
sinalayotgan kodni tashqi dunyodan ajratish.

Mock qilaman: tashqi HTTP servis, to'lov provayderi, email yuborish, vaqt,
tasodifiy son, fayl tizimi, navbat.

Mock **qilmayman**:

- **Sinalayotgan klassning o'zini** (partial mock) — bu testni amalga oshirishga
  bog'laydi.
- **Domen obyektlarini** — ular toza, ularni shunchaki yaratish arzon.
- **DbContext'ni** — in-memory provider LINQ'ni boshqacha bajaradi va haqiqiy
  bazada chiqadigan xatolarni yashiradi. Baza uchun integration test.
- **Boshqa birovning kutubxonasini chuqur** — `HttpClient` ni mock qilish
  o'rniga `HttpMessageHandler` ni almashtirish to'g'riroq.

Vaqt bo'yicha: `DateTime.UtcNow` ni to'g'ridan-to'g'ri ishlatish kodni
sinalmaydigan qiladi. .NET 8+ da `TimeProvider` bor:

```csharp
public sealed class SubscriptionService(TimeProvider clock)
{
    public bool IsExpired(Subscription s) => s.ExpiresAt < clock.GetUtcNow();
}

// testda
var clock = new FakeTimeProvider(new DateTimeOffset(2026, 1, 1, 0, 0, 0, TimeSpan.Zero));
clock.Advance(TimeSpan.FromDays(31));
```

Umumiy qoidam: **mock soni testning sifat ko'rsatkichi**. Bitta testda 5 ta mock
bo'lsa, bu klassning juda ko'p narsaga bog'langanini aytadi — muammo testda emas,
dizaynda.

### 40. NSubstitute bilan qanday ishlaydi? Moq'dan farqi?

Sintaksis. NSubstitute lambda'siz, "tabiiy" o'qiladi:

```csharp
var repo = Substitute.For<IOrderRepository>();

repo.FindAsync(42, Arg.Any<CancellationToken>()).Returns(order);

var result = await sut.GetAsync(42);

await repo.Received(1).FindAsync(42, Arg.Any<CancellationToken>());
await repo.DidNotReceive().DeleteAsync(Arg.Any<int>());
```

Ketma-ket chaqiruvlarga turli javob, exception, va callback:

```csharp
repo.FindAsync(42, default).Returns(order, null);                    // 1-chi, 2-chi
repo.When(r => r.Delete(Arg.Any<int>())).Do(_ => throw new DbException());
repo.AddAsync(Arg.Do<Order>(o => captured = o));                     // argumentni ushlash
```

Moq'da bu `mock.Setup(x => x.FindAsync(42, It.IsAny<CancellationToken>()))
.ReturnsAsync(order)` bo'ladi va `.Object` orqali instance olinadi.

Amaliy farqlar: NSubstitute'da `.Object` yo'q, substitute o'zi interfeys bo'lib
ishlatiladi; sozlanmagan metod exception bermaydi, standart qiymat (`null`, `0`,
bo'sh kolleksiya) qaytaradi — bu qulay, lekin xatoni yashiraydi ham.

Ikkisi ham `virtual` bo'lmagan metodni mock qila olmaydi. Shuning uchun
interfeysga bog'lanish kerak — yoki kutubxonani o'z adapter'im bilan o'rab olaman.

### 41. Integration test'ni qanday tashkil qilasiz?

`WebApplicationFactory<T>` ilovani xotirada ko'taradi, haqiqiy DI, middleware
va marshrutlash bilan:

```csharp
public sealed class ApiFactory : WebApplicationFactory<Program>, IAsyncLifetime
{
    private readonly PostgreSqlContainer _db = new PostgreSqlBuilder()
        .WithImage("postgres:16-alpine").Build();

    protected override void ConfigureWebHost(IWebHostBuilder builder)
    {
        builder.UseSetting("ConnectionStrings:Default", _db.GetConnectionString());
        builder.ConfigureTestServices(s =>
        {
            s.RemoveAll<IPaymentGateway>();
            s.AddSingleton<IPaymentGateway>(Substitute.For<IPaymentGateway>());
        });
    }

    public async Task InitializeAsync()
    {
        await _db.StartAsync();
        using var scope = Services.CreateScope();
        await scope.ServiceProvider.GetRequiredService<AppDbContext>()
                   .Database.MigrateAsync();
    }

    public new async Task DisposeAsync() => await _db.DisposeAsync();
}
```

Asosiy tanlovlarim:

- **Testcontainers** — haqiqiy Postgres konteynerda. In-memory provider yoki
  SQLite emas: ular `JSONB`, `ILIKE`, sequence, tranzaksiya izolyatsiyasi kabi
  narsalarni boshqacha bajaradi va testlar "yashil, lekin yolg'on" bo'ladi.
- **Faqat tashqi dunyo mock'lanadi** — to'lov, SMS, email. Baza haqiqiy.
- **Testlar orasida ma'lumotni tozalash.** Har safar migratsiya qilish sekin;
  `Respawn` jadvallarni FK tartibida tozalaydi va bu tezroq.

```csharp
await respawner.ResetAsync(connection);
```

- **Testlar bir-biriga bog'liq bo'lmasligi.** Har bir test o'z ma'lumotini
  yaratadi. "Avval A testi ishlashi kerak" degan holat — buzilgan test to'plami.

Nimani integration test bilan qoplayman: autentifikatsiya va avtorizatsiya
(unit test bunga ishonchli javob bermaydi), baza bilan ishlagan so'rovlar,
validatsiya va status kodlar, migratsiyalarning haqiqatan qo'llanishi.

---

## Caching

### 42. `IMemoryCache` qanday ishlaydi va qanday xatolar qilinadi?

Process ichidagi, `object` saqlaydigan kesh. Juda tez, chunki serializatsiya yo'q
va tarmoq yo'q.

```csharp
var branches = await cache.GetOrCreateAsync("branches", async entry =>
{
    entry.AbsoluteExpirationRelativeToNow = TimeSpan.FromMinutes(10);
    entry.SetSize(1);
    return await db.Branches.AsNoTracking().ToListAsync(ct);
});
```

Eng ko'p uchraydigan xatolar:

1. **Chegara qo'ymaslik.** `SizeLimit` belgilanmasa kesh cheksiz o'sadi va
   OutOfMemory keladi. `SizeLimit` qo'yilsa esa **har bir** yozuvda `SetSize()`
   bo'lishi shart, aks holda exception.
2. **Faqat sliding expiration.** `SlidingExpiration` yolg'iz qo'yilsa, doimiy
   so'raladigan yozuv **hech qachon** eskirmaydi. Shuning uchun ikkisi birga:
   sliding + absolute.
3. **Cache stampede.** Kesh eskirgan paytda 100 ta so'rov birdan bazaga uradi.
   `GetOrCreateAsync` bunga qarshi kafolat bermaydi. Yechim — kalit bo'yicha
   `SemaphoreSlim`, yoki `HybridCache` (.NET 9+) — u stampede himoyasini o'zi
   beradi.
4. **Tracked entity'ni keshlash.** Keshga `DbContext` dan tracking bilan o'qilgan
   obyekt solinsa, u o'lgan context'ga bog'langan holda qoladi va
   `ObjectDisposedException` yoki g'alati xatolar beradi. Keshga faqat
   `AsNoTracking()` natijasi yoki DTO.

Bir nechta instance bo'lsa, `IMemoryCache` har birida alohida — ya'ni
ma'lumot nomuvofiq bo'ladi. Unda distributed kesh (Redis) yoki `HybridCache`
kerak: u L1 (xotira) va L2 (Redis) ni birlashtiradi.

Nimani keshlaymiz: kam o'zgaradigan, ko'p so'raladigan ma'lumot (viloyatlar,
valyuta kursi, sozlamalar). Nimani keshlamaymiz: foydalanuvchiga xos maxfiy
ma'lumot (xato kalit = boshqa odamning ma'lumoti), tez o'zgaradigan hisob
qoldig'i.

---

## Cybersecurity

### 43. SQL injection qanday ishlaydi? EF Core ishlatganda ham xavf bormi?

Hujum foydalanuvchi kiritgan matn SQL kodining qismiga aylanganda sodir bo'ladi:

```csharp
var sql = $"SELECT * FROM users WHERE name = '{name}'";
// name = "x' OR '1'='1"  →  hamma satr qaytadi
// name = "x'; DROP TABLE users--"  →  ...
```

Yechim — **parametrlangan so'rov**. Parametr qiymat sifatida uzatiladi va hech
qachon kod bo'lib tahlil qilinmaydi.

EF Core LINQ har doim parametrlaydi, shuning uchun xavfsiz. Lekin xom SQL
ishlatilsa farq bor:

```csharp
// xavfsiz: interpolatsiya FormattableString sifatida olinadi va parametrlanadi
db.Users.FromSql($"SELECT * FROM users WHERE name = {name}");

// xavfli: satr allaqachon birlashtirilgan holda keladi
db.Users.FromSqlRaw($"SELECT * FROM users WHERE name = '{name}'");

// xavfsiz: aniq parametr
db.Users.FromSqlRaw("SELECT * FROM users WHERE name = {0}", name);
```

`FromSql` va `FromSqlRaw` farqi aynan shunda — nomi chalg'ituvchi, `Raw`
"xom satr" degani, ya'ni siz parametrni o'zingiz qo'yishingiz kerak.

Parametrlab bo'lmaydigan joylar bor — jadval nomi, ustun nomi, `ORDER BY`
yo'nalishi. Dinamik saralash kerak bo'lsa, ro'yxatdan tanlash (allowlist)
ishlatiladi, satrni birlashtirish emas:

```csharp
var column = sort switch
{
    "name"  => "name",
    "date"  => "created_at",
    _       => "id"
};
```

Qo'shimcha himoya qatlamlari: ilova foydalanuvchisiga minimal huquq (DDL yo'q),
validatsiya, xato xabarlarini mijozga bermaslik (xato matni sxemani oshkor
qiladi), WAF.

### 44. Maxfiy ma'lumotlarni (parol, kalit, token) qanday saqlaysiz?

Qoidalar ustuvorlik tartibida:

1. **Hech qachon kodda va git'da.** `appsettings.json` repozitoriyda, ya'ni u ham
   maxfiy joy emas. Git'ga tushgan sirni "o'chirib tashlash" yetarli emas — u
   tarixda qoladi va rotatsiya qilish kerak.
2. **Development** — User Secrets. Fayl loyiha papkasidan tashqarida saqlanadi:

```bash
dotnet user-secrets set "ConnectionStrings:Default" "Host=localhost;..."
```

3. **Production** — environment variable (minimal), yoki maxsus saqlagich:
   Azure Key Vault, AWS Secrets Manager, HashiCorp Vault. Ular rotatsiya, audit
   va kirish nazoratini beradi.
4. **Konteynerda** — `ENV` emas, chunki `docker inspect` va `/proc` orqali
   ko'rinadi. Docker secrets yoki fayl orqali mount.

Boshqa amaliy narsalar: log'ga sir tushmasligi (`EnableSensitiveDataLogging` ni
o'chirish, exception'ni to'liq log qilganda ulanish satri chiqib ketishi);
sirlarni muntazam rotatsiya; CI/CD'da sirlar faqat secret store'da va log'da
maskalangan; repozitoriyga `gitleaks` kabi skaner qo'yish.

### 45. OWASP Top 10 dan qaysilari .NET backend'da eng ko'p uchraydi?

Eng ko'p ko'rganlarim va men nima qilaman:

**A01 — Broken Access Control.** Birinchi o'rinda, va eng ko'p uchraydigani
**IDOR**: `GET /api/orders/42` — token to'g'ri, lekin bu buyurtma boshqa odamga
tegishli. Autentifikatsiya bor, avtorizatsiya yo'q. Shuning uchun har bir
resursga kirishda egalik tekshiriladi, UI'da tugma yo'qligi himoya emas.

**A02 — Cryptographic Failures.** Parolni SHA-256 bilan hashlash, TLS'siz
ichki trafik, shifrlash kalitini konfiguratsiyada ochiq saqlash.

**A03 — Injection.** SQL injection kamaygan (ORM'lar sabab), lekin shu oilaga
kiradigan boshqalari bor: komanda injection (`Process.Start` ga foydalanuvchi
kiritgan argument), LDAP, va path traversal (`../../etc/passwd`).

**A04 — Insecure Design.** Masalan parolni tiklash jarayonida token'ning
muddati yo'q yoki bir martalik emas. Bu kod xatosi emas, dizayn xatosi —
shuning uchun uni skaner topmaydi.

**A05 — Security Misconfiguration.** Production'da `UseDeveloperExceptionPage`,
Swagger UI ochiq, CORS'da `AllowAnyOrigin` + `AllowCredentials` (bu ikkisi
birga umuman ishlamaydi, lekin odamlar urinadi), standart parollar.

**A07 — Identification and Authentication Failures.** Rate limiting yo'qligi,
sessiyani logout'da bekor qilmaslik, JWT'da `exp` tekshirmaslik.

**A08 — Software and Data Integrity Failures.** Deserializatsiyada
`TypeNameHandling.All` — bu masofadan kod bajarishga olib keladi.

**A09 — Logging and Monitoring Failures.** Hujumni hech kim sezmaydi, chunki
muvaffaqiyatsiz loginlar log qilinmaydi yoki ularga hech kim qaramaydi.

---

## SQL

### 46. ACID nima? Izolyatsiya darajalari qanday muammolarni yechadi?

- **Atomicity** — tranzaksiya to'liq bajariladi yoki butunlay bekor qilinadi.
- **Consistency** — tranzaksiya bazani bir to'g'ri holatdan boshqa to'g'ri
  holatga o'tkazadi (constraint'lar buzilmaydi).
- **Isolation** — parallel tranzaksiyalar bir-biriga aralashmaydi.
- **Durability** — commit bo'lgandan keyin ma'lumot elektr uzilsa ham qoladi
  (WAL).

Izolyatsiya darajalari va ular to'sadigan anomaliyalar:

| Daraja | Dirty read | Non-repeatable read | Phantom read |
|---|---|---|---|
| Read Uncommitted | mumkin | mumkin | mumkin |
| Read Committed | yo'q | mumkin | mumkin |
| Repeatable Read | yo'q | yo'q | mumkin |
| Serializable | yo'q | yo'q | yo'q |

Postgres'da nozik farqlar bor: Read Uncommitted amalda Read Committed bo'lib
ishlaydi, Repeatable Read esa snapshot izolyatsiyasi orqali phantom read'ni ham
to'sadi. Buning evaziga Postgres'da Repeatable Read va Serializable'da
`could not serialize access due to concurrent update` xatosi chiqadi — ya'ni
ilova **retry** qilishga tayyor bo'lishi kerak.

Standart Read Committed. Yuqoriga ko'tarish o'rniga ko'pincha aniqroq yechim
bor: `SELECT ... FOR UPDATE` (pessimistik) yoki `rowversion`/`xmin` bilan
optimistik concurrency.

### 47. Trigger va sequence qachon ishlatiladi, qachon ishlatilmaydi?

**Sequence** — ketma-ket raqam generatori. Tranzaksiyadan tashqarida ishlaydi,
shuning uchun rollback bo'lsa raqam **qaytmaydi** va bo'shliq paydo bo'ladi.
Buni "xato" deb hisoblash ko'p uchraydigan tushunmovchilik — sequence
uzluksizlikni kafolatlamaydi, faqat unikallikni.

Shuning uchun hujjat raqami kabi uzluksiz bo'lishi kerak narsalar uchun
sequence yaramaydi — alohida jadval va qulflash kerak.

```sql
CREATE SEQUENCE order_no_seq START 1000 INCREMENT 1 CACHE 1;
SELECT nextval('order_no_seq');
```

`CACHE` > 1 bo'lsa har bir ulanish bir blok raqamni oldindan oladi — tezroq,
lekin bo'shliq kattaroq va tartib buziladi.

**Trigger** — DML hodisasida avtomatik bajariladigan funksiya.

Men ishlataman: audit log (kim, qachon, nimani o'zgartirdi), `updated_at` ni
avtomatik qo'yish, bir nechta ilova yozadigan jadvalda invariantni majburlash.

Ishlatmaslikka harakat qilaman, chunki: trigger **ko'rinmas** — kodni o'qigan
odam nega qiymat o'zgarganini tushunmaydi; debug qilish qiyin; har bir satrga
ishlaydi, shuning uchun bulk insert sekinlashadi; biznes mantiqi ikki joyga
(ilova va baza) tarqaydi.

Qoidam: trigger **ma'lumot butunligi** uchun, biznes mantiqi uchun emas.

### 48. N+1 ni SQL darajasida qanday aniqlaysiz?

Uchta signal:

1. Log'da bir xil shakldagi `SELECT` ning ko'p takrorlanishi, faqat parametri
   farq qiladi.
2. `pg_stat_statements` da `calls` ustuni juda katta, lekin `mean_exec_time`
   kichik — ya'ni so'rov tez, lekin juda ko'p marta ketgan.
3. APM'da bitta so'rov ichida yuzlab baza chaqiruvi.

```sql
SELECT query, calls, total_exec_time, mean_exec_time
FROM pg_stat_statements
ORDER BY calls DESC
LIMIT 20;
```

Keyin shu so'rov qaysi koddan kelganini topish kerak. Buning uchun EF Core'da
so'rovga tag qo'yish juda yordam beradi:

```csharp
db.Orders.TagWith("OrderList: dashboard").ToListAsync();
```

Tag SQL'ga izoh bo'lib tushadi va `pg_stat_statements` da ko'rinadi.

---

## Database Design Principles

### 49. Atomiklik printsipi (1NF) nima? ACID'dagi atomicity bilan bir xilmi?

Yo'q, ikki butunlay boshqa narsa, lekin bir xil so'z bilan ataladi.

- **ACID atomicity** — tranzaksiya bo'linmas.
- **1NF atomicity** — **ustundagi qiymat** bo'linmas, ya'ni bitta katakda bitta
  fakt turadi.

1NF buziladigan tipik holatlar:

- `phones = "+998901234567, +998911234567"` — vergul bilan ajratilgan ro'yxat.
- `full_name = "Salohiddinov Orzibek"` — agar familiya bo'yicha qidirish kerak
  bo'lsa, bu bo'linmas emas.
- `address = "Toshkent, Chilonzor, 5-uy"` — viloyat bo'yicha filtr kerak bo'lsa.

Nega muhim: bo'linmagan qiymatni indekslab bo'lmaydi (`LIKE '%...%'` to'liq
skanlash), validatsiya qilib bo'lmaydi, FK qo'yib bo'lmaydi, `JOIN` qilib
bo'lmaydi.

Shuning uchun ro'yxat — alohida jadval:

```sql
CREATE TABLE customer_phones (
    customer_id bigint NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    phone       text   NOT NULL,
    is_primary  boolean NOT NULL DEFAULT false,
    PRIMARY KEY (customer_id, phone)
);
```

Lekin "atomik" **kontekstga bog'liq**. Agar manzil faqat chekda chop etilsa va
hech qachon qism bo'yicha qidirilmasa — bitta `text` butunlay yetarli. Ortiqcha
normalizatsiya ham xarajat: har bir qism uchun jadval = har bir o'qishda `JOIN`.

Shuning uchun savol "bu qiymatni bo'laklab qidirishim yoki tekshirishim kerakmi?"
Javob "ha" bo'lsa — ajrataman.

### 50. Referentsial butunlik nima? `ON DELETE` variantlari orasida qanday tanlaysiz?

FK qiymati yo `NULL`, yo mavjud PK ga ishora qilishi kerak. Baza buni majburlab
turadi — ilova koddagi xato ham ma'lumotni buzolmaydi.

`ON DELETE` variantlari:

- `NO ACTION` / `RESTRICT` — ota satrni o'chirishga ruxsat yo'q. Farqi: `RESTRICT`
  darhol tekshiradi, `NO ACTION` tranzaksiya oxirida (deferrable bo'lsa).
- `CASCADE` — bolalar ham o'chadi.
- `SET NULL` — FK `NULL` bo'ladi (ustun NULLable bo'lishi kerak).
- `SET DEFAULT` — standart qiymatga o'tadi.

Tanlovim:

- **Kompozitsiya** (bola otasidan tashqarida ma'nosiz): `CASCADE`.
  `OrderItem` → `Order` — buyurtma o'chsa satrlari ham ketadi.
- **Assotsiatsiya** (bola mustaqil mavjud): `RESTRICT`. `Order` → `Customer` —
  mijozni o'chirish uchun avval buyurtmalarini hal qilish kerak.

`CASCADE` xavfi: zanjir uzun bo'lsa bitta `DELETE` kutilmaganda yuz minglab
satrni o'chirib yuborishi mumkin, va bu jim bo'ladi. Shuning uchun muhim
jadvallarda `RESTRICT` qo'yib, o'chirishni aniq kodda bajarishni afzal ko'raman.

Amalda esa ko'pincha umuman o'chirmaymiz — **soft delete** (`deleted_at`).
Buning narxi bor: FK soft-delete'ni bilmaydi, ya'ni o'chirilgan mijozga yangi
buyurtma yozish mumkin bo'lib qoladi; hamma so'rovga filtr qo'shish kerak
(`HasQueryFilter`); unikal indeks `WHERE deleted_at IS NULL` bo'lishi kerak.

### 51. Indeks qanday ishlaydi? Composite indeksda ustun tartibi nega muhim?

Postgres'da standart — B-tree, saralangan daraxt. Shuning uchun u tenglik,
diapazon va `ORDER BY` ga yordam beradi.

**Composite indeksda tartib** — eng muhim amaliy bilim. `(a, b)` indeksi:

- `WHERE a = 1` — ishlaydi.
- `WHERE a = 1 AND b = 2` — ishlaydi, eng yaxshi.
- `WHERE b = 2` — **ishlamaydi** (yoki faqat index-only scan sifatida, sekin).

Ya'ni indeks faqat **chapdan boshlab** ishlatiladi — telefon kitobiga o'xshash:
familiya bo'yicha saralangan ro'yxatdan ismni topib bo'lmaydi.

Shuning uchun tartib qoidasi: avval tenglik bo'yicha filtrlanadigan ustunlar,
keyin diapazon, oxirida `ORDER BY` uchun kerak bo'lgani.

Indeks ishlamaydigan holatlar:

- Ustun ustida funksiya: `WHERE lower(email) = 'x'` — oddiy indeks yaramaydi,
  expression index kerak: `CREATE INDEX ... ON users (lower(email))`.
- `LIKE '%abc'` — boshida wildcard. `LIKE 'abc%'` esa ishlaydi.
- Tip mos kelmasligi — implicit cast indeksni o'chiradi.
- Tanlanuvchanlik past: `WHERE is_active = true` va 95% satr active bo'lsa,
  planner seq scan'ni tanlaydi va bu to'g'ri qarordir.

Foydali turlari: **partial index** (`WHERE deleted_at IS NULL` — kichik va tez),
**covering index** (`INCLUDE (...)` — index-only scan), **GIN** (JSONB, to'liq
matn), **GiST** (spatial).

Narxi: har bir `INSERT`/`UPDATE`/`DELETE` indekslarni ham yangilaydi. 10 ta
indeksli jadvalga yozish sezilarli sekin. Shuning uchun ishlatilmaydigan
indekslarni topib o'chirish kerak:

```sql
SELECT relname, indexrelname, idx_scan
FROM pg_stat_user_indexes
WHERE idx_scan = 0;
```

Va qaror har doim `EXPLAIN (ANALYZE, BUFFERS)` bilan tekshiriladi — taxmin
bilan emas.

---

## Architecture

### 52. Taqsimlangan tizimda ACID'ni qanday ta'minlaysiz?

Qisqa javob: to'liq ACID'ni ta'minlamaymiz, undan ataylab voz kechamiz.

**CAP teoremasi**: tarmoq bo'linishi (P) muqarrar, shuning uchun amalda tanlov
C va A orasida. Ko'p biznes holatlarida availability muhimroq, demak
consistency'ni **eventual** qilib qabul qilamiz (BASE).

**2PC** (two-phase commit) — nazariy yechim: koordinator avval hammadan "tayyormisan"
deb so'raydi, keyin "commit" deydi. Muammosi: koordinator ikki faza orasida
o'lsa, qatnashchilar qulflangan holda qoladi (blocking protocol). Microservice
muhitida deyarli ishlatilmaydi.

Amalda ishlatiladigan naqshlar:

**Saga** — bitta katta tranzaksiya o'rniga ketma-ket lokal tranzaksiyalar, har
biri uchun **compensating action**. To'lov o'tdi, ombor zaxira qila olmadi →
to'lovni qaytarish. Muhim: compensation "rollback" emas — o'tgan holat
ko'rinadigan bo'lib qoldi, uni biznes darajasida orqaga qaytaramiz.

**Outbox** — eng ko'p kerak bo'ladigani. Muammo: bazaga yozib, keyin navbatga
xabar yuborish atomik emas. Yozildi, xabar ketmadi → ma'lumot nomuvofiq.
Yechim: xabarni **bir xil tranzaksiyada** `outbox` jadvaliga yozamiz, alohida
jarayon uni o'qib navbatga yuboradi va belgilaydi.

```sql
CREATE TABLE outbox_messages (
    id            uuid        PRIMARY KEY,
    type          text        NOT NULL,
    payload       jsonb       NOT NULL,
    occurred_at   timestamptz NOT NULL DEFAULT now(),
    processed_at  timestamptz
);
```

**Idempotentlik** — Outbox "at least once" beradi, ya'ni xabar takrorlanishi
mumkin. Shuning uchun qabul qiluvchi bir xil xabarni ikki marta qayta ishlaganda
natija bir xil bo'lishi kerak: `message_id` ni saqlab, ko'rilganini tashlab
yuborish.

Bu uchtasi (Saga + Outbox + idempotentlik) amalda taqsimlangan tizimda
"tranzaksiya" so'zining o'rnini bosadi.

### 53. N-tier arxitektura nima? Layer va tier farqi?

**Layer** — mantiqiy ajratish (kod tashkiloti). **Tier** — jismoniy ajratish
(alohida mashina/jarayon). 3-layer ilova bitta serverda ishlashi mumkin — u
holda 3 layer, 1 tier.

Klassik qatlamlar: Presentation (API) → Application/Business → Data Access →
Database.

Asosiy qoida — **bog'liqlik faqat pastga qaraydi**. API biznesni biladi, biznes
API'ni bilmaydi.

Muammosi: bu qoidaga qattiq amal qilsak, domen Data Access qatlamiga bog'lanadi
— ya'ni eng muhim kod eng o'zgaruvchan koddan bog'liq bo'ladi.

**Clean/Onion architecture** buni **dependency inversion** bilan teskari qiladi:
interfeys (`IOrderRepository`) domen qatlamida e'lon qilinadi, uni amalga
oshiruvchi esa infratuzilmada. Natijada bog'liqlik o'qlari ichkariga,
domenga qaraydi.

Mening amaliy pozitsiyam: qatlam soni loyiha hajmiga mos bo'lishi kerak. Kichik
CRUD servisga 4 qatlam + mapper + DTO + interfeys = foydasiz murakkablik. Har
bir qatlam faqat qo'shni qatlamga nimanidir uzatish bilan shug'ullansa
("anemic pass-through"), u qatlam kerak emas. Vertical slice yoki ikki qatlam
yetarli.

Qatlam **nimadan himoya qilayotganini** aytib berolmasam, u qatlam bejiz.

### 54. SOLID printsiplaridan arxitektura qarorida qaysi biri eng ko'p ishlatiladi?

Amalda eng ko'p ishlatadiganlarim **D** va **S**.

**S — Single Responsibility.** To'g'ri ta'rifi "bitta ish qiladi" emas, balki
**"o'zgarishning bitta sababi bor"**. `OrderService` ichida narx hisoblash, PDF
chek yasash va email yuborish bo'lsa — uchta turli sabab (buxgalteriya, dizayn,
marketing) bir faylni o'zgartiradi, jamoada konflikt bo'ladi.

**O — Open/Closed.** Yangi funksiyani mavjud kodni o'zgartirmasdan qo'shish.
Amalda: `switch` har yangi tur qo'shilganda o'zgaradi → strategiya
interfeysi va DI orqali ro'yxatga olish:

```csharp
builder.Services.AddKeyedScoped<IPaymentHandler, CardHandler>("card");
builder.Services.AddKeyedScoped<IPaymentHandler, CashHandler>("cash");
```

Lekin buni oldindan qilish ham xato — ikkinchi variant paydo bo'lmaguncha
abstraksiya qurish bo'sh mehnat.

**L — Liskov.** Subclass bazaviy turning shartnomasini buzmasligi kerak. Klassik
buzilish: `ReadOnlyList : List` da `Add()` exception beradi. Shuning uchun
kompozitsiyani merosdan afzal ko'raman.

**I — Interface Segregation.** 15 metodli `IRepository` dan mijozga 2 tasi
kerak bo'lsa — interfeysni bo'lish kerak. Kichik interfeyslar test qilishni
ham osonlashtiradi.

**D — Dependency Inversion.** Eng ko'p foyda beradigani: yuqori daraja ham
quyi daraja ham abstraksiyaga bog'lanadi. ASP.NET Core DI butunlay shu
printsipga qurilgan.

Muhim ogohlik: SOLID — **asbob, maqsad emas**. "SOLID bo'lsin" deb har klassga
interfeys yasash, har metodga factory qo'shish kodni o'qishni qiyinlashtiradi.
Men SOLID'ni muammo **paydo bo'lganda** qo'llayman: test yozolmayapmanmi?
Yangi variant qo'shish uchun 5 joyni o'zgartirish kerakmi? O'sha paytda tegishli
printsip javobni aytadi.

---

## Postgres

### 55. PL/pgSQL da function va procedure farqi nimada?

| | Function | Procedure |
|---|---|---|
| Chaqirish | `SELECT f()` | `CALL p()` |
| Qiymat qaytarish | Ha | `INOUT` orqali |
| Tranzaksiya boshqarish | Yo'q | `COMMIT`/`ROLLBACK` mumkin |
| So'rov ichida | Ha | Yo'q |

Eng muhim farq — **tranzaksiya boshqaruvi**. Function chaqirilgan tranzaksiya
ichida ishlaydi va uni commit qila olmaydi. Procedure (PG 11+) esa ichida
`COMMIT` qilishi mumkin — bu katta ma'lumotni bo'lak-bo'lak qayta ishlashda
kerak bo'ladi.

```sql
CREATE OR REPLACE FUNCTION order_total(p_order_id bigint)
RETURNS numeric
LANGUAGE plpgsql
STABLE
AS $$
DECLARE
    v_total numeric;
BEGIN
    SELECT COALESCE(SUM(quantity * unit_price), 0)
      INTO v_total
      FROM order_items
     WHERE order_id = p_order_id;

    RETURN v_total;
END;
$$;
```

Volatility belgisi muhim: `IMMUTABLE` (faqat argumentga bog'liq — indeks
ifodasida ishlatish mumkin), `STABLE` (bitta so'rov ichida o'zgarmaydi — bazani
o'qiydi), `VOLATILE` (standart, har safar qayta hisoblanadi). To'g'ri belgi
planner'ga optimallashtirish imkonini beradi.

Xatolarni ushlash:

```sql
BEGIN
    INSERT INTO ...;
EXCEPTION
    WHEN unique_violation THEN
        RAISE NOTICE 'Allaqachon mavjud';
END;
```

`EXCEPTION` bloki ichki savepoint yaratadi — ya'ni narxi bor. Loop ichida har
iteratsiyada `EXCEPTION` bo'lsa, sezilarli sekinlashadi.

### 56. View va materialized view farqi? MV ni qachon ishlatasiz?

**View** — saqlangan so'rov, o'z ma'lumoti yo'q. Har murojaatda asosiy so'rov
qayta bajariladi. Foydasi: murakkab so'rovga nom berish, huquqni cheklash
(ustunlarning bir qismini ko'rsatish), legacy sxemani yashirish.

**Materialized view** — natija **diskda saqlanadi**. O'qish tez, lekin ma'lumot
eskiradi va `REFRESH` kerak:

```sql
CREATE MATERIALIZED VIEW daily_sales AS
SELECT date_trunc('day', created_at) AS day,
       count(*) AS orders,
       sum(total) AS revenue
FROM orders
GROUP BY 1;

CREATE UNIQUE INDEX ON daily_sales (day);

REFRESH MATERIALIZED VIEW CONCURRENTLY daily_sales;
```

`CONCURRENTLY` ni ishlatish uchun **unikal indeks shart**. Usiz `REFRESH` butun
MV ni eksklyuziv qulflaydi va shu vaqtda hech kim o'qiy olmaydi — ishlab turgan
tizimda bu sezilarli uzilish.

MV ni ishlataman: og'ir agregatsiya (hisobot, dashboard), ma'lumotning bir necha
daqiqa/soat eskirishi qabul qilinadigan hollarda. Ishlatmayman: real vaqt
kerak bo'lganda, yoki asosiy jadval juda tez o'zgarganda — `REFRESH` ning o'zi
yukning asosiy qismiga aylanib qoladi.

Oddiy view'ni EF Core'da keyless entity sifatida map qilish mumkin:

```csharp
modelBuilder.Entity<DailySales>().HasNoKey().ToView("daily_sales");
```

### 57. PL/pgSQL da shart va takrorlash operatorlari qanday yoziladi?

```sql
IF v_total > 1000 THEN
    v_discount := 0.1;
ELSIF v_total > 500 THEN
    v_discount := 0.05;
ELSE
    v_discount := 0;
END IF;

CASE v_status
    WHEN 'new', 'pending' THEN v_label := 'Kutilmoqda';
    WHEN 'paid'           THEN v_label := 'To''langan';
    ELSE RAISE EXCEPTION 'Noma''lum status: %', v_status;
END CASE;
```

`CASE` da mos variant topilmasa va `ELSE` bo'lmasa — `CASE_NOT_FOUND` xatosi
chiqadi. `IF` da esa shunchaki hech narsa bo'lmaydi. Bu farq bexosdan xato
yashirilishiga olib keladi.

`NULL` bilan ishlaganda: `IF v_x = NULL` **hech qachon** rost bo'lmaydi,
`IS NULL` kerak.

Takrorlash:

```sql
FOR i IN 1..10 LOOP ... END LOOP;
FOR i IN REVERSE 10..1 BY 2 LOOP ... END LOOP;

FOR r IN SELECT id, name FROM customers LOOP
    RAISE NOTICE '%: %', r.id, r.name;
END LOOP;

WHILE v_count > 0 LOOP
    v_count := v_count - 1;
END LOOP;

LOOP
    EXIT WHEN v_done;
    CONTINUE WHEN v_skip;
END LOOP;
```

Eng muhim amaliy fikr: **loop'dan imkon qadar qochish kerak**. 100 000 satrni
loop'da bittalab `UPDATE` qilish, bitta to'plamli `UPDATE ... FROM` dan
o'nlab marta sekin. SQL to'plam bilan ishlashga qurilgan.

Loop haqiqatan kerak bo'lsa (masalan juda katta `UPDATE` ni bo'laklab qilish —
qulflanish va WAL o'sishini kamaytirish uchun), unda procedure ichida bo'lak
oxirida `COMMIT` qilish to'g'ri yondashuv bo'ladi.

---

## Infratuzilma

### 58. `.dockerignore` nima uchun kerak? Nima yoziladi?

Build context — `docker build` ga yuboriladigan papka. `.dockerignore` bo'lmasa,
unga `bin/`, `obj/`, `node_modules/`, `.git/` hammasi kiradi: context yuzlab
megabayt bo'ladi, build sekinlashadi.

Ikki jiddiyroq sababi bor:

1. **Kesh buzilishi.** `COPY . .` dan oldin har qanday faylning o'zgarishi
   (hatto `README.md`) keshni buzadi va to'liq qayta build bo'ladi.
2. **Sir oqishi.** `.env`, `appsettings.Development.json`, `*.pfx`, `.git/`
   image ichiga tushadi. Multi-stage build'da ham bu xavf qoladi — oraliq
   qatlamdagi fayl image tarixida ko'rinadi.

.NET loyihasi uchun minimal to'plam:

```
**/bin/
**/obj/
**/.vs/
**/.git/
**/node_modules/
**/*.user
**/.env
**/appsettings.Development.json
**/*.pfx
Dockerfile*
docker-compose*
README.md
tests/
```

Muhim detal: `.dockerignore` **kontekst ildizida** bo'lishi kerak, Dockerfile
yonida emas. `docker build -f api/Dockerfile .` da ildiz — joriy papka, shuning
uchun `.dockerignore` ham shu yerda bo'lishi kerak.

### 59. Linux'da eng ko'p ishlatadigan buyruqlar va chmod qanday o'qiladi?

Navigatsiya va ko'rish: `pwd`, `cd`, `ls -lah`, `cat`, `less`, `tail -f`
(log kuzatish), `df -h` (disk), `du -sh *` (papka hajmi), `free -h` (xotira).

`chmod` raqamlari: har bir raqam — bir toifa huquqi (egasi, guruh, boshqalar),
qiymat `r=4`, `w=2`, `x=1` yig'indisi.

- `755` = `rwxr-xr-x` — egasi hammasi, qolganlar o'qish+bajarish. Papkalar va
  skriptlar uchun.
- `644` = `rw-r--r--` — oddiy fayllar uchun.
- `600` = `rw-------` — faqat egasi. Maxfiy fayllar, `.env`, kalitlar.
- `700` — `~/.ssh` papkasi uchun.

SSH kalitiga `644` qo'yilsa SSH ishlashdan bosh tortadi — bu juda ko'p
uchraydigan muammo.

Papkada `x` — "ichiga kirish" degani, `r` — "ro'yxatini ko'rish". Shuning uchun
`x` siz papkaga `cd` qilib bo'lmaydi.

`777` — hech qachon. "Ishlamayapti, 777 qo'yib ko'raman" eng xavfli odat; haqiqiy
sabab odatda egalik (`chown`) yoki SELinux.

Tahrirlash: `nano` oddiy (`Ctrl+O` saqlash, `Ctrl+X` chiqish), `vim` tez lekin
rejimli (`i` — kiritish, `Esc`, `:wq` — saqlab chiqish, `:q!` — saqlamasdan).
Serverda ko'pincha faqat `vi` bor, shuning uchun `:wq` va `:q!` ni bilish
majburiy minimum.

`sudo` bo'yicha qoidam: `sudo -i` bilan root bo'lib o'tirmaslik — har bir kerakli
buyruqni alohida `sudo` bilan bajarish. Shunda log'da kim nima qilgani qoladi va
tasodifiy `rm -rf` xavfi kamayadi.

### 60. MinIO ga qanday ulanasiz? Presigned URL nima uchun kerak?

MinIO — S3-mos obyekt saqlagich, shuning uchun AWS SDK yoki `Minio` .NET
kutubxonasi bilan ishlaydi.

```csharp
builder.Services.AddSingleton<IMinioClient>(_ => new MinioClient()
    .WithEndpoint(cfg["Minio:Endpoint"])
    .WithCredentials(cfg["Minio:AccessKey"], cfg["Minio:SecretKey"])
    .WithSSL(true)
    .Build());
```

Bucket operatsiyalari:

```csharp
var exists = await client.BucketExistsAsync(new BucketExistsArgs().WithBucket(name), ct);
if (!exists)
    await client.MakeBucketAsync(new MakeBucketArgs().WithBucket(name), ct);
```

Bucket'ni o'chirish uchun u **bo'sh** bo'lishi kerak — avval obyektlarni
o'chirish kerak.

**Presigned URL** — vaqtincha, imzolangan havola. Nima uchun muhim: faylni
backend orqali o'tkazmaslik.

Backend orqali yuklash muammolari: ilova trafik va xotira sarflaydi, so'rov uzoq
davom etadi, `maxRequestBodySize` chegarasi, gorizontal scale qiyinlashadi.

Presigned bilan backend faqat havola beradi, fayl **to'g'ridan-to'g'ri** mijoz va
MinIO orasida ketadi:

```csharp
var url = await client.PresignedPutObjectAsync(new PresignedPutObjectArgs()
    .WithBucket("documents").WithObject(key).WithExpiry(600));
```

Xavfsizlik tomoni: muddat qisqa bo'lishi kerak (daqiqalar), kalit nomini
server belgilaydi (mijoz bergan nom path traversal yoki boshqa foydalanuvchining
faylini ustiga yozish imkonini beradi), va yuklangandan keyin server faylni
tekshirishi kerak (hajm, MIME, antivirus) — chunki presigned URL bilan mijoz
nima yuklaganini server ko'rmaydi.

**Lifecycle** qoidasi vaqtinchalik ma'lumotni avtomatik tozalaydi:

```json
{ "Rules": [ { "ID": "tmp-7d", "Status": "Enabled",
  "Filter": { "Prefix": "tmp/" }, "Expiration": { "Days": 7 } } ] }
```

Bu "temp bucket" ni qo'lda tozalashdan ancha ishonchli.

### 61. RabbitMQ management UI da nimaga qarash kerak?

`15672` portdagi veb-interfeys. Men qaraydigan narsalar, muhimlik tartibida:

**Queues → Ready va Unacked.** `Ready` o'sib borayotgan bo'lsa — consumer
yetishmaydi yoki sekin. `Unacked` katta va o'zgarmasa — consumer xabarni olgan,
lekin `ack` qilmagan: ya'ni osilib qolgan yoki `prefetch` juda katta.

**Message rates.** Publish va deliver grafiklari. Publish > deliver bo'lsa,
navbat to'planadi.

**Connections va Channels.** Soni doimiy o'sib borayotgan bo'lsa — ulanish
oqmoqda (`IConnection` har safar yangi yaratilgan va yopilmagan). Ulanish qimmat,
kanal arzon: qoida — ulanish uzoq yashaydi, kanal har bir thread uchun alohida.

**Exchanges va Bindings.** Xabar yetib bormasa, birinchi tekshiradigan narsa —
binding haqiqatan borligi va routing key mos kelishi.

UI'dan qiladigan amaliy ishlarim: navbat yaratish/o'chirish, `Get messages`
bilan xabar tanasini ko'rish (lekin bu xabarni navbatdan oladi — `Requeue: Yes`
qo'yish kerak), `Purge` bilan navbatni tozalash (faqat dev), foydalanuvchi va
permission boshqarish, `Publish message` bilan qo'lda test xabari yuborish.

Production'da e'tibor beradigan narsalar: `guest` foydalanuvchini o'chirish;
management UI'ni internetga ochmaslik; har bir ilovaga alohida vhost;
DLX (dead letter exchange) sozlanganini tekshirish — aks holda qayta ishlanmagan
xabarlar jimgina yo'qoladi.

### 62. Cron ifodasini qanday o'qiysiz? Hangfire'da nimaga e'tibor berasiz?

Besh maydon: `daqiqa soat kun oy hafta_kuni`. Hangfire va Quartz'da olti
maydonli (sekund bilan) variant ham bor.

| Ifoda | Ma'nosi |
|---|---|
| `*/15 * * * *` | Har 15 daqiqada |
| `0 * * * *` | Har soat boshida |
| `0 3 * * *` | Har kuni 03:00 |
| `0 3 * * 1` | Har dushanba 03:00 |
| `0 3 1 * *` | Har oyning 1-kuni 03:00 |
| `0 3 L * *` | Har oyning oxirgi kuni (Quartz) |

Chalkashtiradigan joy: kun (`3-maydon`) va hafta kuni (`5-maydon`) **ikkisi ham**
belgilansa, klassik cron'da ular **OR** bilan birlashadi — `0 3 1 * 1` "oyning
1-kuni **yoki** dushanba" degani, "1-kuni dushanba bo'lsa" emas.

```csharp
RecurringJob.AddOrUpdate<IReportJob>(
    "daily-report",
    job => job.RunAsync(CancellationToken.None),
    "0 3 * * *",
    new RecurringJobOptions { TimeZone = TimeZoneInfo.FindSystemTimeZoneById("Asia/Tashkent") });
```

Amalda e'tibor beradigan narsalar:

- **Vaqt zonasi.** Hangfire standart UTC ishlatadi. "Har kuni 03:00" deganda
  mijoz mahalliy vaqtni tushunadi — aniq `TimeZone` berish kerak.
- **Idempotentlik.** Ish ikki marta ishga tushishi mumkin (deploy paytida, ikki
  instance'da). Shuning uchun ishning o'zi takroriy bajarilishga chidamli
  bo'lishi kerak, yoki distributed lock kerak.
- **Bir-birining ustiga tushish.** 10 daqiqalik ish har 5 daqiqada ishga
  tushirilsa, nusxalar to'planadi. `DisableConcurrentExecution` atributi bor.
- **Uzoq ishni cron'ga bermaslik.** Cron ishni **boshlaydi**; og'ir ishni
  navbatga qo'yib, alohida worker bajarishi to'g'riroq.

### 63. GitHub Actions'da CI pipeline'ini qanday qurasiz?

```yaml
name: ci
on:
  push:
    branches: [main]
  pull_request:

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-dotnet@v4
        with:
          dotnet-version: '9.0.x'
      - run: dotnet restore
      - run: dotnet build --no-restore -c Release
      - run: dotnet test --no-build -c Release --logger trx
```

Tushunish kerak bo'lgan tuzilma: workflow → job → step. Job'lar standart holda
**parallel**, `needs:` bilan ketma-ket qilinadi. Har bir job **toza** runner'da
ishlaydi, ya'ni job'lar orasida fayl o'z-o'zidan o'tmaydi — `actions/upload-artifact`
kerak.

Mening e'tibor beradigan narsalarim:

- **Kesh.** `setup-dotnet` ga `cache: true` yoki `actions/cache` bilan NuGet
  paketlarini keshlash build vaqtini sezilarli qisqartiradi.
- **Sirlar.** `${{ secrets.X }}` — log'da avtomatik maskalanadi. Lekin
  `pull_request` trigger'i fork'dan kelganda sirlar **berilmaydi** — bu ataylab,
  xavfsizlik uchun. Fork PR'ida deploy kerak bo'lsa `pull_request_target` bor,
  lekin u xavfli, chunki fork kodini ishonchli kontekstda ishga tushiradi.
- **Action versiyasini qattiq belgilash.** `@v4` emas, commit SHA — supply chain
  hujumiga qarshi.
- **`permissions`** ni minimal qilish: standart token ko'p huquqga ega.

```yaml
permissions:
  contents: read
```

- **Matritsa** bir nechta versiyada sinash uchun:

```yaml
strategy:
  matrix:
    dotnet: ['8.0.x', '9.0.x']
```

### 64. GitLab CI va GitHub Actions orasidagi asosiy farqlar?

| | GitHub Actions | GitLab CI |
|---|---|---|
| Fayl | `.github/workflows/*.yml` | `.gitlab-ci.yml` |
| Tuzilma | workflow → job → step | pipeline → stage → job |
| Qayta ishlatish | Marketplace action'lar | `include`, `extends`, template |
| Konteyner | `container:` yoki `runs-on` | `image:` har bir job'da |
| Artifact | `upload/download-artifact` | `artifacts:` va `dependencies:` |

```yaml
stages: [build, test, deploy]

variables:
  DOTNET_CLI_TELEMETRY_OPTOUT: '1'

build:
  stage: build
  image: mcr.microsoft.com/dotnet/sdk:9.0
  script:
    - dotnet restore
    - dotnet build --no-restore -c Release
  artifacts:
    paths: [ '**/bin/Release/' ]
    expire_in: 1 day

test:
  stage: test
  image: mcr.microsoft.com/dotnet/sdk:9.0
  services:
    - name: postgres:16-alpine
      alias: db
  variables:
    POSTGRES_PASSWORD: test
  script:
    - dotnet test -c Release
```

GitLab'da menga qulay ko'ringan narsalar: `services:` bilan baza ko'tarish
tabiiyroq; `stage` tushunchasi pipeline'ni o'qishni osonlashtiradi; `rules:` va
`only/except` bilan shart yozish moslashuvchan; `environment:` va manual job
bilan deploy approval qurish oson.

GitHub'da qulayrog'i: Marketplace juda katta, shuning uchun tayyor qadam topish
oson; `composite action` yozish `include` dan ko'ra toza.

Ikkisida ham bir xil qoida: **CI pipeline'ini mahalliy ishga tushirib sinash
qiyin**, shuning uchun uni imkon qadar yupqa qilaman — haqiqiy mantiq skriptda
(`build.sh`, `Makefile`, yoki `dotnet` buyruqlari) bo'lishi kerak, YAML'da emas.
Shunda mahalliy va CI'da bir xil narsa ishlaydi.

### 65. Windows Firewall va papka huquqlarini qanday boshqarasiz?

Firewall PowerShell orqali:

```powershell
New-NetFirewallRule -DisplayName "API 5000" -Direction Inbound `
    -Protocol TCP -LocalPort 5000 -Action Allow -Profile Domain,Private

Get-NetFirewallRule | Where-Object Enabled -eq 'True' |
    Select-Object DisplayName, Direction, Action
```

`-Profile` muhim: `Public` profilga qoida qo'shish serverni ochiq tarmoqda ham
ochib qo'yadi. Va `-RemoteAddress` bilan manbani cheklash har doim yaxshi:

```powershell
-RemoteAddress 10.0.0.0/8
```

Papka huquqlari — NTFS ACL. Grafik interfeys (Properties → Security) bor, lekin
skriptda `icacls`:

```powershell
icacls "D:\App\logs" /grant "IIS AppPool\MyApp:(OI)(CI)M"
icacls "D:\App\config" /inheritance:r /grant:r "Administrators:(OI)(CI)F"
```

`(OI)` — object inherit (fayllarga), `(CI)` — container inherit (papkalarga),
`M` — modify, `F` — full. `/inheritance:r` merosni uzadi — maxfiy papkada
kerak, aks holda yuqoridan kelgan `Users` huquqi qoladi.

Qoidam: huquq **guruhga** beriladi, foydalanuvchiga emas; `Everyone` va `Users`
ga yozish huquqi berilmaydi; ilova ishlaydigan hisob (`IIS AppPool\<name>` yoki
alohida service account) faqat o'ziga kerakli papkaga `Modify` oladi.

Audit kerak bo'lsa: `Get-Acl` bilan hozirgi holatni olib, uni Git'da saqlangan
etalon bilan taqqoslash — qo'lda o'zgartirilgan huquqni shunday topaman.

### 66. Windows Server'da komponentlarni qanday qo'shasiz? `hosts` fayli nima uchun kerak?

Rol va funksiyalar PowerShell orqali:

```powershell
Install-WindowsFeature -Name Web-Server -IncludeManagementTools
Install-WindowsFeature -Name Web-Asp-Net45, Web-Net-Ext45
Install-WindowsFeature -Name Hyper-V -IncludeManagementTools -Restart

Get-WindowsFeature | Where-Object InstallState -eq 'Installed'
```

Klient Windows'da (10/11) boshqa cmdlet:

```powershell
Enable-WindowsOptionalFeature -Online -FeatureName IIS-WebServerRole
Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Windows-Subsystem-Linux
```

ASP.NET Core uchun IIS dan tashqari **ASP.NET Core Module** (Hosting Bundle)
alohida o'rnatiladi — bu `Install-WindowsFeature` bilan kelmaydi va eng ko'p
uchraydigan "502.5" xatosining sababi.

Telnet mijozi (`Telnet-Client`) — men uni port tekshirish uchun ishlataman,
lekin PowerShell'da yaxshiroq varianti bor:

```powershell
Test-NetConnection -ComputerName db.internal -Port 5432
```

`hosts` fayli — `C:\Windows\System32\drivers\etc\hosts`. DNS'dan **oldin**
ko'riladi, shuning uchun:

- Domen DNS'ga yozilmasdan oldin mahalliy sinash.
- Production domenini test serveriga yo'naltirib, haqiqiy TLS sertifikati bilan
  sinash.
- Tashqi servisni vaqtincha bloklash (`127.0.0.1 analytics.example.com`).

Xavfi ham shunda: `hosts` da qolib ketgan qator keyinchalik tushunarsiz muammo
beradi — "mening mashinamda boshqa serverga ketadi". Shuning uchun o'zgartirish
kiritganimda izoh bilan sana yozib qo'yaman.

### 67. PowerShell va CMD orasidagi asosiy farq nimada?

CMD matn bilan ishlaydi, PowerShell **obyekt** bilan. Bu eng muhim farq:
`Get-Process` natijasi satr emas, `Process` obyektlari — shuning uchun ularning
xossalariga to'g'ridan-to'g'ri murojaat qilish mumkin, matnni parse qilish
kerak emas.

```powershell
Get-Process | Where-Object WorkingSet -gt 500MB |
    Sort-Object WorkingSet -Descending |
    Select-Object Name, Id, @{n='MB';e={[int]($_.WorkingSet/1MB)}}
```

Buni CMD'da qilish uchun `tasklist` chiqishini matn sifatida kesish kerak bo'ladi.

Bilish kerak bo'lgan amaliy farqlar:

- **Versiya.** Windows PowerShell 5.1 (`powershell.exe`) va PowerShell 7+
  (`pwsh.exe`) — bu ikki boshqa narsa. 5.1 da `&&`, `||`, ternary va `??`
  operatorlari **yo'q**; 7+ da bor. Skript yozganda qaysi biri uchun yozilgani
  muhim.
- **Execution policy.** Skript ishlamasa birinchi sabab shu:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

- **Kodlash.** 5.1 da `Out-File` va `Set-Content` standart holda ANSI yoki
  BOM bilan UTF-8 yozadi. Boshqa asbob o'qiydigan fayl yozsam, `-Encoding utf8`
  ni aniq ko'rsataman.
- **Masofaviy ishlash.** `Invoke-Command -ComputerName srv1, srv2 -ScriptBlock { ... }`
  — bir nechta serverga bir vaqtda. CMD'da bunga teng narsa yo'q.

CMD'ni hali ham ishlataman: juda oddiy `.bat` fayllar, eski o'rnatuvchilar,
PowerShell mavjud bo'lmagan muhit. Qolgan hamma holatda PowerShell.

---

## .NET / C#

### 68. TCP va UDP farqi? Socket darajasida qanday ishlaydi?

**TCP** — ulanishga asoslangan, tartibni va yetib borishni kafolatlaydi,
oqimni boshqaradi. Narxi: 3-way handshake (RTT), qayta yuborish kutilishi
(head-of-line blocking), ko'proq ortiqcha yuk.

**UDP** — datagram, kafolat yo'q: yetib bormasligi, tartibsiz kelishi,
ikki marta kelishi mumkin. Buning evaziga kechikish kam va broadcast/multicast
mumkin.

TCP: HTTP, baza ulanishi, SMTP. UDP: DNS, video oqim, o'yin, metrika
(StatsD), QUIC/HTTP3 (ustida ishonchlilikni o'zi quradi).

```csharp
using var listener = new TcpListener(IPAddress.Any, 9000);
listener.Start();
using var client = await listener.AcceptTcpClientAsync(ct);
await using var stream = client.GetStream();
```

Socket bilan ishlaganda eng ko'p qilinadigan xato — **TCP oqim ekanini
unutish**. `Read()` siz so'ragan hajmni emas, mavjud hajmni qaytaradi; bir
`Send()` ikki `Read()` bo'lib kelishi mumkin yoki teskarisi. Shuning uchun
protokolning o'zida chegara bo'lishi kerak: uzunlik prefiksi yoki ajratuvchi.

```csharp
var lengthBytes = new byte[4];
await stream.ReadExactlyAsync(lengthBytes, ct);     // .NET 7+
var length = BinaryPrimitives.ReadInt32BigEndian(lengthBytes);
var payload = new byte[length];
await stream.ReadExactlyAsync(payload, ct);
```

`ReadExactly` paydo bo'lgunga qadar buni qo'lda loop bilan yozish kerak edi va
aynan shu joyda ko'p xato bo'lardi.

### 69. `HttpClient` ni qanday to'g'ri ishlatasiz?

Ikki qarama-qarshi xato bor.

1. **Har so'rovda `new HttpClient()`** — socket oqadi. Har bir instance o'z
   ulanish pool'iga ega; `Dispose` dan keyin ham socket `TIME_WAIT` da qoladi.
   Yuqori yuklamada ephemeral port tugaydi.
2. **Bitta statik `HttpClient`** — socket muammosi yo'q, lekin DNS o'zgarishini
   **ko'rmaydi**: ulanish bir marta yechilgan IP'ga qotib qoladi. Blue-green
   deploy yoki failover'dan keyin eski IP'ga urishda davom etadi.

Yechim — `IHttpClientFactory`. U `HttpMessageHandler` larni pool'da saqlaydi va
ularni belgilangan muddatdan keyin (standart 2 daqiqa) yangilaydi, ya'ni DNS
qayta yechiladi.

```csharp
builder.Services.AddHttpClient<IPaymentApi, PaymentApi>(c =>
{
    c.BaseAddress = new Uri(cfg["Payment:BaseUrl"]!);
    c.Timeout = TimeSpan.FromSeconds(10);
})
.AddStandardResilienceHandler();     // Microsoft.Extensions.Http.Resilience
```

E'tibor beradigan boshqa narsalar:

- **Timeout.** Standart 100 soniya — juda uzoq. Tashqi servis osilsa, mening
  thread'larim ham kutib turadi. Har bir mijozga aniq timeout qo'yaman.
- **`BaseAddress` va nisbiy URL.** `BaseAddress = "https://api.com/v1/"` da
  oxirgi `/` bo'lishi shart, va nisbiy yo'l `/` bilan **boshlanmasligi** kerak —
  aks holda `v1` yo'qoladi.
- **`EnsureSuccessStatusCode()`** javob tanasini o'qimaydi, shuning uchun xato
  haqidagi ma'lumot yo'qoladi. Men status'ni o'zim tekshirib, xato tanasini ham
  log qilaman.
- **Retry'ni ehtiyotkorlik bilan.** Faqat idempotent so'rovlarga (`GET`,
  `PUT`) va faqat vaqtinchalik xatolarga. `POST` ni retry qilish ikki marta
  to'lov qilib yuborishi mumkin — unda idempotency key kerak.

Proxy va credential:

```csharp
var handler = new HttpClientHandler
{
    Proxy       = new WebProxy("http://proxy.local:3128"),
    Credentials = new NetworkCredential(user, password)
};
```

`WebClient` esa eskirgan (`[Obsolete]` .NET 6+) — yangi kodda ishlatilmaydi.

### 70. Simmetrik va asimmetrik shifrlash qanday farq qiladi? Qachon qaysi biri?

**Simmetrik** (AES) — bitta kalit shifrlash va ochish uchun. Tez, katta
ma'lumotga mos. Muammosi — kalitni qanday uzatish.

**Asimmetrik** (RSA, ECC) — ochiq/yopiq kalit jufti. Ochiq kalit bilan
shifrlangan narsani faqat yopiq kalit ochadi. Sekin va hajm chegarasi bor
(RSA-2048 bilan ~200 bayt).

Shuning uchun amalda **ikkisi birga**: asimmetrik bilan tasodifiy simmetrik
kalit almashiladi, keyin ma'lumot simmetrik bilan shifrlanadi. TLS aynan shunday
ishlaydi.

Imzolash teskari yo'nalish: **yopiq** kalit bilan imzolanadi, **ochiq** kalit
bilan tekshiriladi. Bu autentiklik va butunlikni beradi, maxfiylikni emas.

.NET'da:

```csharp
using var aes = Aes.Create();
aes.Key = key;                 // 32 bayt = AES-256
aes.GenerateIV();              // har safar yangi, ma'lumot bilan birga saqlanadi
```

Muhim: **IV ni qayta ishlatmaslik**. Bir xil kalit + bir xil IV = bir xil
shifrmatn, ya'ni ma'lumot oqadi. IV maxfiy emas, lekin unikal bo'lishi shart.

Va yana muhimrog'i — **shifrlash butunlikni bermaydi**. CBC rejimida hujumchi
shifrmatnni o'zgartirib, ochilgan matnni boshqarishi mumkin (padding oracle).
Shuning uchun **AEAD** rejimi kerak:

```csharp
using var aes = new AesGcm(key, tagSizeInBytes: 16);
aes.Encrypt(nonce, plaintext, ciphertext, tag);
```

`AesGcm` shifrlash bilan birga autentifikatsiya tegini beradi — o'zgartirilgan
ma'lumot ochilmaydi.

Umumiy qoidam: kriptografiyani o'zim qurmaslik. `AesGcm`, `RandomNumberGenerator`,
`CryptographicOperations.FixedTimeEquals`, `Rfc2898DeriveBytes` — tayyor va to'g'ri.
"O'zim o'ylab topgan sxema" deyarli har doim buzilgan bo'lib chiqadi.

### 71. SMTP orqali xat yuborishda nimaga e'tibor berasiz?

`SmtpClient` eskirgan (`[Obsolete]`) — rasmiy tavsiya **MailKit**.

```csharp
var message = new MimeMessage();
message.From.Add(new MailboxAddress("Hisobot xizmati", "no-reply@example.com"));
message.To.Add(MailboxAddress.Parse(recipient));
message.Subject = subject;
message.Body = new BodyBuilder { HtmlBody = html, TextBody = text }.ToMessageBody();

using var client = new SmtpClient();
await client.ConnectAsync(host, 587, SecureSocketOptions.StartTls, ct);
await client.AuthenticateAsync(user, password, ct);
await client.SendAsync(message, ct);
await client.DisconnectAsync(true, ct);
```

Portlar va shifrlash chalkashadi:

- `25` — serverlar orasida; provayderlar ko'pincha bloklaydi.
- `587` — **STARTTLS**: ulanish ochiq boshlanadi va shifrlangan holatga o'tadi.
  Bugungi standart.
- `465` — **implicit TLS**: darhol shifrlangan. Eskirgan deb e'lon qilingan edi,
  lekin qaytib keng ishlatiladi.

`SecureSocketOptions.Auto` ni ishlatish qulay, lekin aniq qiymat berish
ishonchliroq — `Auto` noto'g'ri tanlasa, xato tushunarsiz bo'ladi.

Amalda muhim bo'lgan narsalar:

- **Xatni so'rov ichida yubormaslik.** SMTP sekin va ishonchsiz; foydalanuvchi
  javobni kutib turmasligi kerak. Navbatga qo'yib, background worker yuboradi.
- **Yetib borish (deliverability).** SPF, DKIM, DMARC sozlanmasa xat spam'ga
  tushadi. Bu kod muammosi emas, DNS muammosi, lekin backend ishlab chiquvchi
  buni bilishi kerak.
- **Plain text va HTML ikkisi ham.** Faqat HTML yuborish spam bahosini oshiradi.
- **Parolni konfiguratsiyadan, app password bilan.** Gmail'da oddiy parol
  ishlamaydi.

IMAP/POP3 bilan o'qish — xatni olish uchun. Farqi: POP3 xatni yuklab olib
serverdan o'chiradi va faqat inbox'ni biladi; IMAP server bilan sinxronlashadi,
papkalar, qidiruv va bir nechta qurilma bilan ishlaydi. Yangi integratsiyada
IMAP.

### 72. FTP, FTPS va SFTP farqi? .NET'da nima ishlatasiz?

- **FTP** — shifrlanmagan. Parol va ma'lumot ochiq ketadi. Ishlatmaslik kerak.
- **FTPS** — FTP + TLS. Ikki rejimi bor: explicit (`AUTH TLS`, port 21) va
  implicit (port 990).
- **SFTP** — FTP'ga umuman aloqasi yo'q: SSH ustidagi fayl protokoli, port 22.

Nomlari o'xshash, lekin FTPS va SFTP butunlay boshqa protokollar — bu eng ko'p
chalkashtiriladigan joy.

.NET'da `FtpWebRequest` eskirgan. Men ishlataman:

- **FluentFTP** — FTP/FTPS uchun.
- **SSH.NET** — SFTP uchun.

```csharp
using var sftp = new SftpClient(host, 22, user, new PrivateKeyFile(keyPath));
sftp.Connect();
await using var fs = File.OpenRead(localPath);
sftp.UploadFile(fs, remotePath);
```

FTP'ning alohida muammosi — **aktiv va passiv rejim**. Aktiv rejimda *server*
mijozga ulanadi, shuning uchun mijozning NAT/firewall'i orqasida ishlamaydi.
Passiv rejimda mijoz ulanadi — shuning uchun deyarli har doim passiv tanlanadi.
FluentFTP'da bu `config.DataConnectionType`.

Imkoni bo'lsa umuman FTP ishlatmaslikni tanlayman: obyekt saqlagich (S3/MinIO)
presigned URL bilan ancha yaxshi — huquq nazorati aniq, audit bor, port ochish
kerak emas. FTP/SFTP odatda tashqi tizim talab qilganda qoladi.

### 73. Open XML SDK va ClosedXML orasida qanday tanlaysiz?

**Open XML SDK** — OOXML formatining to'g'ridan-to'g'ri aks ettirilishi. Hamma
narsa mumkin, lekin oddiy ish ham ko'p kod talab qiladi: Excel'da matn
`SharedStringTable` da saqlanadi, katak ustunni harf bilan ataydi (`A1`),
uslub `CellFormat` indekslari orqali beriladi.

**ClosedXML** — Open XML ustidagi qulay qatlam:

```csharp
using var wb = new XLWorkbook();
var ws = wb.AddWorksheet("Hisobot");

ws.Cell("A1").Value = "Mijoz";
ws.Cell("B1").Value = "Summa";
ws.Range("A1:B1").Style.Font.Bold = true;

ws.Cell("A2").InsertData(rows);
ws.Column(2).Style.NumberFormat.Format = "#,##0.00";
ws.Columns().AdjustToContents();

wb.SaveAs(path);
```

Tanlovim: hisobot generatsiyasi, oddiy va o'rtacha murakkablikdagi Excel —
**ClosedXML**. Shablonli to'ldirish, juda katta fayl (yuz minglab satr), yoki
SDK'da bo'lgan nozik imkoniyat kerak bo'lsa — **Open XML SDK**.

Katta hajmda e'tibor beradigan narsa: ClosedXML butun workbook'ni **xotirada**
quradi. 500 000 satrlik fayl bir necha gigabayt xotira olishi mumkin. Bunday
holatda Open XML SDK'ning `OpenXmlWriter` bilan oqim rejimida yozish kerak.

Ikki umumiy maslahat: server tomonda Excel generatsiyasini **Microsoft.Office.Interop**
bilan qilmaslik (u Office o'rnatilishini talab qiladi va serverda qo'llab
quvvatlanmaydi); va foydalanuvchi yuklagan Excel'ni o'qiganda formulalar va
tashqi havolalarga ishonmaslik.

### 74. Memory-mapped fayl nima va qachon kerak?

Fayl virtual xotiraga map qilinadi: ko'rsatkich orqali murojaat qilaman, OS
kerakli sahifani o'zi diskdan yuklaydi. `Read`/`Write` chaqiruvlari va ularning
buferga nusxalashi yo'q.

```csharp
using var mmf = MemoryMappedFile.CreateFromFile(path, FileMode.Open);
using var accessor = mmf.CreateViewAccessor(offset: 0, size: 1024);
var value = accessor.ReadInt32(0);
```

Qachon haqiqatan foyda beradi:

- **Juda katta faylning kichik qismiga tasodifiy murojaat.** 10 GB faylning
  o'rtasidagi 4 KB kerak bo'lsa, map qilish butun faylni o'qimaydi.
- **Jarayonlar orasida umumiy xotira** (`CreateNew` nomlangan map bilan) — IPC
  uchun eng tez usul.
- Fayl bir necha marta o'qiladigan bo'lsa — OS sahifa keshi orqali qayta
  foydalanadi.

Qachon kerak emas: faylni boshidan oxirigacha bir marta o'qish. Bunda oddiy
`FileStream` (yoki `PipeReader`) sodda va teng darajada tez.

Bilish kerak bo'lgan nozikliklar:

- 32-bit jarayonda manzil maydoni chegarasi bor, shuning uchun katta faylni
  bo'lak-bo'lak map qilish kerak.
- Diskdagi I/O xatosi odatiy exception emas, `AccessViolation` ko'rinishida
  kelishi mumkin.
- Map qilingan fayl boshqa jarayon tomonidan qisqartirilsa, murojaat qilinganda
  jarayon qulashi mumkin.
- Yozishni diskka majburlash uchun `accessor.Flush()`, lekin bu ham darhol
  fizik diskka tushishini kafolatlamaydi.

Shuning uchun uni faqat o'lchov natijasi oddiy yechim yetarli emasligini
ko'rsatganda ishlataman.

### 75. Python'ni backend ishlab chiquvchi sifatida nima uchun bilish kerak?

Men uni asosiy til sifatida emas, **asbob** sifatida ishlataman:

- Ma'lumotni bir martalik ko'chirish, tozalash, tekshirish skriptlari.
- Hisobot va hujjat generatsiyasi (`openpyxl`, `python-docx`).
- Log va CSV tahlili.
- CI'dagi kichik yordamchi skriptlar.

C# dan keyin e'tibor beradigan farqlar:

- **Dinamik tiplash.** Xato ishga tushganda chiqadi. Shuning uchun type hint va
  `mypy` jiddiy skriptda majburiy deb bilaman.
- **Indentatsiya sintaksis.** Blok qavs bilan emas, bo'shliq bilan belgilanadi.
- **Virtual muhit.** `python -m venv .venv` — global `pip install` qilmaslik
  kerak, aks holda loyihalar bir-birining bog'liqligini buzadi.
- **GIL.** CPU-bound ishni thread bilan tezlashtirib bo'lmaydi;
  `multiprocessing` yoki native kutubxona kerak. I/O-bound ishda `asyncio`
  yoki thread ishlaydi.

```python
from pathlib import Path
import csv

def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))
```

Bu yerda `utf-8-sig` — Excel'dan eksport qilingan CSV BOM bilan keladi va oddiy
`utf-8` da birinchi ustun nomi buzilgan bo'lib chiqadi. Bu kichik, lekin amalda
juda ko'p vaqt yeydigan detal.

Umuman, Python'ni bilish qiymati — **to'g'ri asbobni tanlash imkoni**. 200 qatorli
C# konsol loyihasi o'rniga 20 qatorli skript yetarli bo'lsa, ikkinchisini
tanlayman.
