# Swagger / OpenAPI — API Documentation — Middle D

## 1. Nima? (Ta'rif)

**OpenAPI** — REST API'ni tavsiflovchi **til-agnostik standart
spesifikatsiya** (JSON/YAML formatida). **Swagger** — OpenAPI
spesifikatsiyasini generatsiya qiluvchi va vizual UI orqali
ko'rsatuvchi **toolset** (Swagger — OpenAPI'dan OLDIN paydo bo'lgan,
keyin OpenAPI Foundation'ga o'tkazilgan).

## 2. Nima uchun kerak?

Frontend/mobil developer, yoki tashqi hamkor — API'ning qanday
endpoint, parametr, javob formatiga ega ekanini **bilishi** kerak.
Qo'lda yozilgan hujjat **tezda eskiradi** (kod o'zgaradi, hujjat
yangilanmaydi) — Swagger esa **koddan avtomatik** generatsiya
qilingani uchun HAR DOIM **aktual**.

## 3. Ichida nima sodir bo'ladi? (Mexanizm)

### 3.1 Swashbuckle vs NSwag

```
Swashbuckle — .NET ekotizimida ENG KENG TARQALGAN, ASP.NET Core
              shablonida DEFAULT o'rnatiladi

NSwag       — Swashbuckle'ga MUQOBIL, QO'SHIMCHA imkoniyat:
              CLIENT CODE GENERATION (TypeScript/C# client avtomatik
              yaratish)
```

### 3.2 O'rnatish va sozlash

```bash
dotnet add package Swashbuckle.AspNetCore --version 6.5.0
```

```csharp
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen(options =>
{
    options.SwaggerDoc("v1", new OpenApiInfo
    {
        Title = "ERP API", Version = "v1",
        Description = "Xodimlarni boshqarish tizimi API'si"
    });
});

var app = builder.Build();
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}
```

### 3.3 XML comments — `///` dan documentation

```csharp
/// <summary>
/// ID bo'yicha xodimni qaytaradi
/// </summary>
/// <param name="id">Xodimning noyob identifikatori</param>
/// <response code="200">Xodim topildi</response>
/// <response code="404">Xodim topilmadi</response>
[HttpGet("{id}")]
public async Task<ActionResult<Employee>> GetById(int id) { }
```

```xml
<!-- .csproj -->
<PropertyGroup>
  <GenerateDocumentationFile>true</GenerateDocumentationFile>
</PropertyGroup>
```

```csharp
options.IncludeXmlComments(Path.Combine(AppContext.BaseDirectory, "MyApi.xml"));
```

### 3.4 `[ProducesResponseType]`

```csharp
[HttpGet("{id}")]
[ProducesResponseType(typeof(Employee), StatusCodes.Status200OK)]
[ProducesResponseType(StatusCodes.Status404NotFound)]
public async Task<ActionResult<Employee>> GetById(int id) { }
```

Bu — Swagger UI'da har status kod uchun **aniq javob turini**
ko'rsatadi, client generatorlar to'g'ri tur yaratishi uchun muhim.

### 3.5 JWT Bearer token Swagger UI'da

```csharp
builder.Services.AddSwaggerGen(options =>
{
    options.AddSecurityDefinition("Bearer", new OpenApiSecurityScheme
    {
        Name = "Authorization",
        Type = SecuritySchemeType.Http,
        Scheme = "Bearer",
        BearerFormat = "JWT",
        In = ParameterLocation.Header,
        Description = "JWT token: Bearer {token}"
    });

    options.AddSecurityRequirement(new OpenApiSecurityRequirement
    {
        {
            new OpenApiSecurityScheme
            {
                Reference = new OpenApiReference { Type = ReferenceType.SecurityScheme, Id = "Bearer" }
            },
            Array.Empty<string>()
        }
    });
});
```

Bu sozlash — Swagger UI'da **"Authorize"** tugmasini qo'shadi, unga
tokenni kiritgach, barcha "Try it out" so'rovlarga **avtomatik**
`Authorization: Bearer <token>` header qo'shiladi.

### 3.6 Swagger UI endpoint himoya qilish

```csharp
// Production'da Swagger UI ochiq QOLDIRILMASLIGI kerak (yoki AUTH bilan himoyalanishi kerak)
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}
else
{
    // Agar production'da HAM kerak bo'lsa — Basic Auth yoki IP whitelist bilan himoyalash
    app.MapWhen(ctx => ctx.Request.Path.StartsWithSegments("/swagger"), appBuilder =>
    {
        appBuilder.UseMiddleware<SwaggerBasicAuthMiddleware>();
    });
}
```

### 3.7 NSwag Studio — client code generation

NSwag — OpenAPI spesifikatsiyasidan **TypeScript/C# HTTP client
kodi**ni AVTOMATIK generatsiya qilish imkonini beradi — frontend
developer API chaqiruv kodini QO'LDA yozmasdan, tayyor, TYPE-SAFE
client oladi.

### 3.8 Versioning bilan birga

```csharp
options.SwaggerDoc("v1", new OpenApiInfo { Title = "ERP API", Version = "v1" });
options.SwaggerDoc("v2", new OpenApiInfo { Title = "ERP API", Version = "v2" });

app.UseSwaggerUI(c =>
{
    c.SwaggerEndpoint("/swagger/v1/swagger.json", "V1");
    c.SwaggerEndpoint("/swagger/v2/swagger.json", "V2");
});
```

## 4. Kod — to'liq misol

```csharp
builder.Services.AddSwaggerGen(options =>
{
    options.SwaggerDoc("v1", new OpenApiInfo { Title = "ERP API", Version = "v1" });
    options.IncludeXmlComments(xmlPath);
    options.AddSecurityDefinition("Bearer", /* ... */);
    options.AddSecurityRequirement(/* ... */);
});
```

## 5. Qachon ishlatish kerak?

| Vaziyat | Yechim |
|---|---|
| Standart .NET API hujjatlash | Swashbuckle |
| Client kod avtomatik generatsiya kerak | NSwag |
| Tashqi hamkor uchun rasmiy hujjat | XML comments + `[ProducesResponseType]` |
| Production'da hujjat yashirin bo'lishi kerak | Dev'da ochiq, Prod'da o'chirilgan/himoyalangan |

## 6. Muhim nuqtalar

- Production'da Swagger UI'ni **hech qanday himoyasiz** ochiq
  qoldirish — API strukturasini oshkor qiladi (xavfsizlik riski).
- XML comments — `GenerateDocumentationFile` yoqilmasa ISHLAMAYDI.
- `[ProducesResponseType]` — Swagger UI/client generator uchun
  MUHIM, lekin runtime xatti-harakatga TA'SIR QILMAYDI (faqat
  metadata).

## 7. Imtihon savollari

1. OpenAPI va Swagger orasidagi farq nima?
2. Swashbuckle va NSwag orasidagi asosiy farq nima?
3. `[ProducesResponseType]` nima vazifani bajaradi?
4. JWT tokenni Swagger UI orqali qanday qo'shish mumkin?
5. Production'da Swagger UI'ni ochiq qoldirish nima uchun xavfli?
6. NSwag Studio orqali client code generation qanday foyda beradi?
