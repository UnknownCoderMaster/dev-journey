# API Versioning — Middle D

## 1. Nima? (Ta'rif)

**API Versioning** — API'ning turli versiyalarini **bir vaqtda**,
bir-biriga xalaqit bermasdan ishlatish imkonini beruvchi mexanizm.

## 2. Nima uchun kerak?

API'ga o'zgarish kiritilganda (masalan, `Employee` javobidan
`FullName` maydoni o'chirilib, `FirstName`+`LastName`ga bo'linsa) —
ESKI client'lar (mobil ilova, boshqa servis) **darhol buzilib
qolmasligi** kerak. Versioning — **backward compatibility**
(orqaga moslik)ni ta'minlaydi: eski va yangi client'lar **parallel**
ishlashi mumkin.

## 3. Ichida nima sodir bo'ladi? (Mexanizm)

### 3.1 Versioning strategiyalari

```
URL versioning:      GET /api/v1/employees
Header versioning:    GET /api/employees  +  Api-Version: 1.0
Query versioning:     GET /api/employees?api-version=1.0
Media Type versioning: Accept: application/json;v=1.0
```

| | Ustunlik | Kamchilik |
|---|---|---|
| URL | Oddiy, ko'rinadigan, keshlash oson | URL "chiroyliligi" buziladi |
| Header | URL toza qoladi | Ko'rinmas, debug qiyinroq |
| Query | Oddiy | URL "chiroyliligi" buziladi |

Amalda **URL versioning** — eng ko'p ishlatiladigan, eng tushunarli
yondashuv.

### 3.2 `Asp.Versioning.Mvc` paketi

```bash
dotnet add package Asp.Versioning.Mvc --version 8.1.0
dotnet add package Asp.Versioning.Mvc.ApiExplorer --version 8.1.0
```

```csharp
builder.Services.AddApiVersioning(options =>
{
    options.DefaultApiVersion = new ApiVersion(1, 0);
    options.AssumeDefaultVersionWhenUnspecified = true;
    options.ReportApiVersions = true; // Response header'da qo'llab-quvvatlanadigan versiyalarni ko'rsatadi
    options.ApiVersionReader = new UrlSegmentApiVersionReader(); // URL orqali
}).AddApiExplorer(options =>
{
    options.GroupNameFormat = "'v'VVV";
    options.SubstituteApiVersionInUrl = true;
});
```

### 3.3 URL versioning — Controller'da

```csharp
[ApiController]
[ApiVersion("1.0")]
[Route("api/v{version:apiVersion}/[controller]")]
public class EmployeesController : ControllerBase
{
    [HttpGet]
    public IActionResult GetV1() => Ok(new { fullName = "Orzibek" }); // Eski format
}

[ApiController]
[ApiVersion("2.0")]
[Route("api/v{version:apiVersion}/[controller]")]
public class EmployeesV2Controller : ControllerBase
{
    [HttpGet]
    public IActionResult GetV2() => Ok(new { firstName = "Orzibek", lastName = "Toshmatov" }); // Yangi format
}
```

Yoki bitta controller ichida bir nechta versiyani qo'llab-quvvatlash:

```csharp
[ApiVersion("1.0")]
[ApiVersion("2.0")]
[Route("api/v{version:apiVersion}/employees")]
public class EmployeesController : ControllerBase
{
    [HttpGet, MapToApiVersion("1.0")]
    public IActionResult GetV1() => Ok(/* eski format */);

    [HttpGet, MapToApiVersion("2.0")]
    public IActionResult GetV2() => Ok(/* yangi format */);
}
```

### 3.4 Header versioning

```csharp
options.ApiVersionReader = new HeaderApiVersionReader("Api-Version");
```

```
GET /api/employees
Api-Version: 2.0
```

### 3.5 Deprecated version — warning header

```csharp
[ApiVersion("1.0", Deprecated = true)]
[ApiVersion("2.0")]
public class EmployeesController : ControllerBase { }
```

`ReportApiVersions = true` bilan — response header'da:
```
api-supported-versions: 2.0
api-deprecated-versions: 1.0
```

Bu — client'ga **"v1 tez orada o'chiriladi, v2'ga o'ting"** degan
signal beradi, kod o'zgartirmasdan.

### 3.6 Swagger bilan versioning integratsiya

```csharp
builder.Services.AddSwaggerGen();
builder.Services.ConfigureOptions<ConfigureSwaggerOptions>(); // Har versiya uchun ALOHIDA Swagger doc

var app = builder.Build();
var apiVersionDescriptionProvider = app.Services.GetRequiredService<IApiVersionDescriptionProvider>();

app.UseSwaggerUI(options =>
{
    foreach (var description in apiVersionDescriptionProvider.ApiVersionDescriptions)
    {
        options.SwaggerEndpoint($"/swagger/{description.GroupName}/swagger.json",
            description.GroupName.ToUpperInvariant());
    }
});
```

## 4. Kod — to'liq misol (Minimal API bilan)

```csharp
var versionSet = app.NewApiVersionSet()
    .HasApiVersion(new ApiVersion(1, 0))
    .HasApiVersion(new ApiVersion(2, 0))
    .ReportApiVersions()
    .Build();

app.MapGet("/api/v{version:apiVersion}/employees", () => Ok(/* v1 */))
    .WithApiVersionSet(versionSet)
    .MapToApiVersion(1, 0);

app.MapGet("/api/v{version:apiVersion}/employees", () => Ok(/* v2 */))
    .WithApiVersionSet(versionSet)
    .MapToApiVersion(2, 0);
```

## 5. Qachon ishlatish kerak?

| Vaziyat | Yechim |
|---|---|
| Public API, ko'p tashqi iste'molchi | URL versioning (aniq, oddiy) |
| Ichki microservice, kam client | Header versioning (URL toza) |
| Kichik, breaking bo'lmagan o'zgarish | Versiyalash SHART emas (yangi ixtiyoriy maydon qo'shish OK) |

**Best practices — qachon yangi versiya chiqarish:**
```
✅ YANGI versiya kerak: maydon O'CHIRILSA, nomi O'ZGARSA, tur
   O'ZGARSA (masalan string → int), majburiy YANGI parametr qo'shilsa

❌ YANGI versiya SHART EMAS: yangi IXTIYORIY maydon qo'shilsa
   (mavjud client'lar buni E'TIBORSIZ QOLDIRADI, buzilmaydi)
```

## 6. Muhim nuqtalar

- Versiyalash — **kelajakni oldindan ko'zlab** loyihalash kerak
  (birinchi kunidanoq `/api/v1/` bilan boshlash — keyinchalik
  qo'shish qiyinroq).
- Eski versiyalarni **abadiy** qo'llab-quvvatlash — texnik qarz
  (technical debt) yaratadi — deprecation siyosati (masalan "v1 —
  6 oydan keyin o'chiriladi") oldindan e'lon qilinishi kerak.

## 7. Imtihon savollari

1. URL, Header va Query versioning orasidagi farqlarni va
   tradeoff'larini tushuntiring.
2. Nima uchun boshida `/api/v1/` bilan boshlash tavsiya etiladi,
   hatto hozircha faqat bitta versiya bo'lsa ham?
3. Qachon yangi API versiyasi chiqarish SHART, qachon shart emas?
4. `Deprecated = true` sozlamasi qanday amaliy foyda beradi?
5. Swagger versioning bilan qanday integratsiya qilinadi?
