# ControllerBase, Attributes, [ApiController], Model Binding — Junior C

## 1. Nima?

**Controller** — HTTP so'rovlarini qabul qilib, mos javob (response)
qaytaruvchi ASP.NET Core klassi. **`ControllerBase`** — API (JSON/XML)
qaytaruvchi controllerlar uchun bazaviy klass. **`[ApiController]`** —
REST API'lar uchun bir qancha qulaylik va qat'iy xatti-harakatlarni
avtomatik yoquvchi atribut.

## 2. Nima uchun kerak?

MVC (View qaytaruvchi) va Web API (JSON qaytaruvchi) — turli
ehtiyojlarga ega. `Controller` klassi View bilan ishlash uchun keraksiz
og'irlik (ViewBag, TempData va h.k.) qo'shadi. `ControllerBase` — bu
og'irliksiz, faqat API uchun kerakli narsalarni beradi.

`[ApiController]` bo'lmasa — har bir controller'da qo'lda validation
tekshirish, `[FromBody]` yozish kerak bo'lardi — bu ko'p takrorlanuvchi
(boilerplate) kod.

## 3. Ichida nima sodir bo'ladi? (Mexanizm)

### 3.1 `Controller` vs `ControllerBase`

```csharp
// Controller — MVC uchun, View bilan ishlash imkoniyati bor
public class HomeController : Controller
{
    public IActionResult Index() => View(); // Razor View'ni render qiladi (HTML)
}

// ControllerBase — API uchun, View imkoniyati YO'Q
public class EmployeesController : ControllerBase
{
    public IActionResult Get() => Ok(data); // JSON qaytaradi
}
```

```
Controller : ControllerBase
    │
    └── + View(), PartialView(), ViewBag, TempData  (Razor rendering uchun)

ControllerBase — faqat:
    + Ok(), BadRequest(), NotFound() kabi ActionResult helper'lar
    + ModelState, User, HttpContext, Request, Response
```

Agar API loyihasida `Controller`dan meros olsangiz — hech qanday
funksional farq sezilmaydi, lekin **semantik jihatdan noto'g'ri**:
kod o'quvchisi "bu yerda View render qilinishi mumkin" deb
o'ylashi mumkin.

### 3.2 `[ApiController]` avtomatik qiladigan 3 ta narsa

```csharp
[ApiController]
[Route("api/[controller]")]
public class EmployeesController : ControllerBase { }
```

**1. Avtomatik Model Validation (400 Bad Request):**

Ichkarida ASP.NET Core `ApiControllerAttribute` — Action filter sifatida
`ActionContext.ModelState.IsValid` ni HAR bir so'rov uchun avtomatik
tekshiradi. Agar `false` bo'lsa — Action metodi **umuman
chaqirilmasdan**, avtomatik `400 Bad Request` + `ProblemDetails`
qaytariladi.

```csharp
// [ApiController] YO'Q holatda — qo'lda tekshirish kerak
public IActionResult Create(EmployeeDto dto)
{
    if (!ModelState.IsValid)
        return BadRequest(ModelState); // Bu QATOR har metodda takrorlanardi

    // ...
}

// [ApiController] BOR holatda — bu tekshiruv AVTOMATIK, yozish shart emas
[HttpPost]
public IActionResult Create(EmployeeDto dto)
{
    // Bu yerga faqat validatsiyadan O'TGAN so'rov yetib keladi
}
```

**2. Binding Source Parameter Inference:**

`[ApiController]` bilan — parametr turi asosida binding manbasi
**avtomatik xulosa qilinadi** (aniq atribut yozish shart emas):

```csharp
public IActionResult Create(EmployeeDto dto)
// [ApiController] complex tur (class/record) uchun avtomatik [FromBody] deb hisoblaydi

public IActionResult Get(int id)
// Route'da {id} bo'lsa — avtomatik [FromRoute]

public IActionResult Search(string name)
// Route'da {name} bo'lmasa — avtomatik [FromQuery]
```

**3. Automatic HTTP 400 va ProblemDetails formatı (RFC 7807):**

```json
{
  "type": "https://tools.ietf.org/html/rfc7807",
  "title": "One or more validation errors occurred.",
  "status": 400,
  "errors": {
    "Name": ["The Name field is required."]
  },
  "traceId": "00-abc123..."
}
```

Bu — barcha xatolar uchun **standart, mashina o'qiy oladigan** format
— client tomonida bir xil parsing logikasi ishlaydi.

**Qo'shimcha 4-chi xususiyat:** Multipart/form-data uchun avtomatik
inference qo'llanmaydi — bu holatda `[FromForm]` aniq yozilishi kerak.

### 3.3 Model Binding — manbalar

```csharp
[HttpGet("{id}")]
public IActionResult Get(
    int id,                            // [FromRoute] — URL segmentidan: /api/employees/42
    [FromQuery] string? search,        // ?search=orzibek — query string dan
    [FromHeader] string? authHeader,   // HTTP header dan
    [FromBody] UpdateDto dto,          // Request body (JSON) dan — faqat BITTA parametr FromBody bo'la oladi!
    [FromForm] IFormFile? file,        // multipart/form-data dan
    [FromServices] IEmailService email) // DI konteynerdan to'g'ridan olish
```

Model binding jarayoni ichkarida **`IValueProvider`** va
**`ModelBinderProvider`** zanjiri orqali ishlaydi: ASP.NET Core
so'rovni tahlil qiladi, mos binder'ni tanlaydi (route, query, body,
header, form uchun turli binderlar bor), va reflection orqali C#
obyektini to'ldiradi.

```
❌ Bir metodda 2 ta [FromBody] parametr — RUNTIME xato beradi:
public IActionResult Update([FromBody] Dto1 a, [FromBody] Dto2 b) // ❌ InvalidOperationException!
// Sabab: HTTP request body FAQAT bir marta o'qilishi mumkin (stream)
```

### 3.4 Model Validation — DataAnnotations

```csharp
public class CreateEmployeeDto
{
    [Required(ErrorMessage = "Ism majburiy")]
    [StringLength(100, MinimumLength = 2)]
    public string Name { get; set; } = null!;

    [Range(18, 65)]
    public int Age { get; set; }

    [EmailAddress]
    public string Email { get; set; } = null!;

    [RegularExpression(@"^\+998\d{9}$")]
    public string? Phone { get; set; }
}
```

`ModelState` — ASP.NET Core so'rovni bind qilishda **har bir property**
uchun validatsiya atributlarini avtomatik tekshiradi va xatolarni
`ModelStateDictionary`ga yig'adi (`[ApiController]` bo'lsa — bu
avtomatik 400 javobga aylanadi).

### 3.5 Routing — Convention-based vs Attribute-based

```csharp
// Attribute-based (Web API standart yondashuvi)
[Route("api/[controller]")]  // → api/employees ([controller] = klass nomidan "Controller" olib tashlanadi)
public class EmployeesController : ControllerBase
{
    [HttpGet]                 // GET /api/employees
    [HttpGet("{id}")]          // GET /api/employees/42
    [HttpGet("{id}/details")]  // GET /api/employees/42/details
    [HttpPost]                 // POST /api/employees
    [HttpPut("{id}")]          // PUT /api/employees/42
    [HttpDelete("{id}")]       // DELETE /api/employees/42
}

// Convention-based (odatda MVC/Razor Pages'da, Program.cs da)
app.MapControllerRoute(
    name: "default",
    pattern: "{controller=Home}/{action=Index}/{id?}");
```

Web API'larda deyarli har doim **attribute-based routing** ishlatiladi
— chunki har bir endpoint uchun aniq, mustaqil marshrut belgilash
imkonini beradi.

## 4. Kod — ActionResult turlari

```csharp
return Ok(data);              // 200 + data
return Ok();                   // 200, body yo'q
return Created(url, data);    // 201 + Location header (URL)
return CreatedAtAction(nameof(GetById), new { id = emp.Id }, emp); // 201 + action nomiga asoslangan URL
return Accepted();             // 202 — qabul qilindi, hali qayta ishlanmoqda (async job)
return NoContent();            // 204 — muvaffaqiyatli, javob tanasi yo'q (odatda DELETE/PUT)
return BadRequest("xato");     // 400
return BadRequest(ModelState); // 400 + validation errors
return Unauthorized();         // 401 — autentifikatsiya kerak
return Forbid();               // 403 — autentifikatsiya bor, lekin ruxsat yo'q
return NotFound();             // 404
return Conflict();             // 409 — masalan, unique constraint buzilgan
return StatusCode(500, msg);   // Ixtiyoriy status kod
```

### `IActionResult` vs `ActionResult<T>`

```csharp
// IActionResult — istalgan ActionResult turini qaytarish mumkin, lekin Swagger
// aniq javob turini bila olmaydi (faqat runtime da ma'lum bo'ladi)
public IActionResult Get(int id)
{
    var emp = _repo.GetById(id);
    if (emp is null) return NotFound();
    return Ok(emp);
}

// ActionResult<T> — Swagger/OpenAPI schema'da ANIQ tur ko'rsatiladi (Employee)
// implicit conversion orqali T yoki ActionResult qaytarish mumkin
public ActionResult<Employee> Get(int id)
{
    var emp = _repo.GetById(id);
    if (emp is null) return NotFound(); // ActionResult
    return emp;                          // T → implicit ActionResult<T> ga aylanadi
}
```

`ActionResult<T>` — Swagger UI'da response schema'sini **aniq** ko'rsatadi
(masalan `Employee` klassining barcha propertylari), `IActionResult`
bilan esa Swagger buni bilolmaydi — client generatorlar (masalan
NSwag/Refit) uchun bu muhim farq.

### `CreatedAtAction` — nima qaytaradi va nima uchun

```csharp
[HttpPost]
public async Task<ActionResult<Employee>> Create(CreateEmployeeDto dto)
{
    var emp = await _service.CreateAsync(dto);
    return CreatedAtAction(nameof(GetById), new { id = emp.Id }, emp);
}

[HttpGet("{id}")]
public async Task<ActionResult<Employee>> GetById(int id) { /* ... */ }
```

Javob:
```
HTTP/1.1 201 Created
Location: /api/employees/42
{ "id": 42, "name": "Orzibek", ... }
```

REST konvensiyasiga ko'ra, resurs yaratilganda (`POST`) — javobda
**yangi resursga havola** (`Location` header) bo'lishi kerak.
`CreatedAtAction` — bu header'ni `GetById` action nomi va route
parametrlaridan **avtomatik generatsiya** qiladi — URL'ni qo'lda
string sifatida yozish shart emas (refactoring xavfsizroq bo'ladi).

### `[Consumes]`, `[Produces]` — content negotiation

```csharp
[Consumes("application/json")]  // Faqat JSON body qabul qilinadi
[Produces("application/json")]  // Har doim JSON qaytariladi (Accept header'dan qat'i nazar)
[HttpPost]
public IActionResult Create([FromBody] CreateEmployeeDto dto) { /* ... */ }
```

## 5. Qachon ishlatish kerak?

| Vaziyat | Yechim |
|---|---|
| REST/Web API loyihasi | `ControllerBase` + `[ApiController]` |
| Razor View qaytaradigan MVC sahifa | `Controller` |
| Swagger'da aniq response turi kerak | `ActionResult<T>` |
| Turli xil javob turlari (Ok/NotFound aralash) oddiy holatlar | `IActionResult` yetarli |
| Resurs yaratish (POST) | `CreatedAtAction` (201 + Location) |
| Resurs o'chirish (DELETE), javob tanasi kerak emas | `NoContent()` (204) |
| Validatsiya xatosi | Avtomatik (`[ApiController]`), qo'lda `ModelState.IsValid` tekshirish SHART emas |

**Anti-patternlar:**

```csharp
// ❌ Har bir action da qo'lda ModelState tekshirish (agar [ApiController] bor bo'lsa — ortiqcha)
if (!ModelState.IsValid) return BadRequest(ModelState); // Allaqachon avtomatik bajariladi!

// ❌ GET so'rovda ma'lumot o'zgartirish (semantik buzilish, idempotent emas bo'lib qoladi)
[HttpGet("delete/{id}")]
public IActionResult DeleteViaGet(int id) { _repo.Delete(id); return Ok(); }
// ✅ HTTP semantikaga mos: [HttpDelete("{id}")]

// ❌ Controller ichida to'g'ridan DbContext bilan ishlash (Fat Controller)
public IActionResult Get() => Ok(_context.Employees.ToList());
// ✅ Service/Handler qatlami orqali (CQRS/MediatR pattern)
```

## 6. Qo'shimcha — chuqur nuqtalar

- **`ProblemDetails` — RFC 7807 standarti:** bu — barcha .NET
  xatolari uchun bir xil struktura beruvchi standart. Custom xato
  javoblari yozish o'rniga, shu formatga rioya qilish — client
  kutubxonalar bilan yaxshiroq moslashadi.

- **Model Binding tartibida ustuvorlik:** agar bir nomdagi parametr
  bir nechta manbada (masalan, route va query) mavjud bo'lsa —
  ASP.NET Core aniq belgilangan atribut (`[FromRoute]`) ni ustun
  qo'yadi, aks holda ichki qoidalar (route → query → body) asosida
  hal qiladi.

- **`[ApiController]` — Controller darajasida yoqiladi, lekin
  butun loyiha uchun ham sozlash mumkin:**
  ```csharp
  builder.Services.Configure<ApiBehaviorOptions>(options =>
  {
      options.SuppressModelStateInvalidFilter = true; // Avtomatik 400 ni O'CHIRISH
  });
  ```

- **C# versiyalaridagi o'zgarishlar:** .NET 6+ — **Minimal API** paydo
  bo'ldi (`app.MapGet(...)`) — Controller'siz, yengilroq yondashuv,
  lekin katta loyihalarda Controller'lar ko'proq tuzilma beradi.

- **Real loyihada uchraydigan xato:** `[FromBody]` bilan `GET` so'rovda
  ishlatish — GET so'rovlarda **body bo'lmasligi kerak** (HTTP
  semantikasiga ko'ra) — buning o'rniga `[FromQuery]` ishlatilishi kerak.

- **MediatR bilan CQRS integratsiyasi (loyihaning real stack'i):**
  ```csharp
  [ApiController]
  [Route("api/[controller]")]
  public class EmployeesController : ControllerBase
  {
      private readonly IMediator _mediator;
      public EmployeesController(IMediator mediator) => _mediator = mediator;

      [HttpGet("{id}")]
      public async Task<ActionResult<EmployeeDto>> GetById(int id)
      {
          var result = await _mediator.Send(new GetEmployeeQuery(id));
          return result is null ? NotFound() : Ok(result);
      }

      [HttpPost]
      public async Task<ActionResult<EmployeeDto>> Create(CreateEmployeeCommand command)
      {
          var result = await _mediator.Send(command);
          return CreatedAtAction(nameof(GetById), new { id = result.Id }, result);
      }
  }
  ```
  Bu yondashuvda Controller — **faqat** HTTP qatlami bo'lib qoladi,
  biznes mantiq `Handler`larda joylashadi (Thin Controller pattern).

## 7. Imtihon savollari

1. `Controller` va `ControllerBase` orasidagi farq nima, va API
   loyihasida qaysi birini ishlatish tavsiya etiladi?
2. `[ApiController]` avtomatik qiladigan 3 (yoki 4) ta narsani sanab
   bering.
3. `[FromQuery]`, `[FromRoute]`, `[FromBody]` orasidagi farq nima, va
   `[ApiController]` ular orasida qanday avtomatik tanlov qiladi?
4. `IActionResult` va `ActionResult<T>` orasidagi farq — Swagger/OpenAPI
   nuqtai nazaridan qanday ta'sir qiladi?
5. `CreatedAtAction` nima qaytaradi va bu qaysi REST konvensiyasiga
   mos keladi?
6. Bitta action metodida ikkita `[FromBody]` parametr bo'lsa nima
   sodir bo'ladi? Nima uchun?
7. `ProblemDetails` (RFC 7807) nima va u nima uchun standart xato
   formati sifatida tavsiya etiladi?
8. "Fat Controller" anti-patterni nima va uni CQRS/MediatR qanday
   hal qiladi?
