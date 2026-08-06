# ASP.NET — Routing, ActionResult, Status Codes — Junior A

## 1. Nima? (Ta'rif)

**Routing** — kelayotgan HTTP so'rovni (URL + Method) mos
Controller/Action'ga **yo'naltiruvchi** mexanizm. **ActionResult** —
Action metod natijasini **HTTP javobga** aylantiruvchi turlar
oilasi.

## 2. Nima uchun kerak?

Har bir HTTP so'rov — **qaysi kod** bajarilishi kerakligini
"bilishi" kerak. Routing — bu bog'lanishni **deklarativ** tarzda
(atribut yoki konvensiya orqali) belgilaydi.

## 3. Ichida nima sodir bo'ladi? (Mexanizm)

### 3.1 Convention-based routing

```csharp
app.MapControllerRoute(
    name: "default",
    pattern: "{controller=Home}/{action=Index}/{id?}");
```

URL `/Employees/Details/5` → `EmployeesController.Details(5)` —
**nom bo'yicha**, avtomatik moslashtiriladi.

### 3.2 Attribute routing

```csharp
[ApiController]
[Route("api/[controller]")] // → api/employees
public class EmployeesController : ControllerBase
{
    [HttpGet]                    // GET api/employees
    [HttpGet("{id}")]             // GET api/employees/42
    [HttpGet("{id}/subordinates")] // GET api/employees/42/subordinates
    [HttpPost]                    // POST api/employees
}
```

### 3.3 Route constraints

```csharp
[HttpGet("{id:int}")]          // FAQAT butun son
[HttpGet("{name:alpha}")]       // FAQAT harflar
[HttpGet("{id:int:min(1)}")]    // Butun son, MINIMUM 1
[HttpGet("{date:datetime}")]    // DateTime formatida
[HttpGet("{code:regex(^[A-Z]{{3}}$)}")] // Custom regex
```

```
Route constraint — URL segment TO'G'RI FORMATDA BO'LMASA — bu
ROUTE "mos KELMAYDI" deb hisoblanadi, va boshqa (mos keladigan)
route'ga o'tiladi, aks holda 404.
```

### 3.4 Route priority

```csharp
[HttpGet("{id:int}")]      // 1. ANIQROQ constraint — BIRINCHI tekshiriladi
[HttpGet("{name}")]         // 2. UMUMIYROQ — agar YUQORIDAGI mos kelmasa

// /employees/42  → {id:int} MOS KELADI (42 — butun son)
// /employees/abc → {name} MOS KELADI ({id:int} mos KELMAGANI uchun)
```

### 3.5 ActionResult turlari — barchasi

```csharp
return Ok(data);                    // 200 + data
return Ok();                         // 200, body yo'q
return Created(uri, data);          // 201 + Location header
return CreatedAtAction(nameof(GetById), new { id = emp.Id }, emp); // 201, URL AVTOMATIK generatsiya
return NoContent();                  // 204 — muvaffaqiyatli, body yo'q
return BadRequest("Xato");           // 400
return BadRequest(ModelState);       // 400 + validation errors
return Unauthorized();               // 401
return Forbid();                     // 403
return NotFound();                   // 404
return NotFound($"ID {id} topilmadi");
return Conflict();                   // 409
return StatusCode(500, "Server xatosi"); // Ixtiyoriy status kod
```

### 3.6 `IActionResult` vs `ActionResult<T>`

```csharp
// IActionResult — ISTALGAN ActionResult qaytarish mumkin, LEKIN
// Swagger javob TURINI ANIQ bilmaydi
public IActionResult Get(int id)
{
    var emp = _repo.GetById(id);
    return emp is null ? NotFound() : Ok(emp);
}

// ActionResult<T> — Swagger/OpenAPI SCHEMA'da ANIQ tur ko'rsatiladi
public ActionResult<Employee> Get(int id)
{
    var emp = _repo.GetById(id);
    if (emp is null) return NotFound(); // ActionResult
    return emp;                          // T → implicit ActionResult<T>
}
```

### 3.7 Synchronous vs Asynchronous action

```csharp
// ❌ Sinxron — I/O (DB) operatsiyada THREAD BLOKLANADI
public IActionResult Get(int id) => Ok(_context.Employees.Find(id));

// ✅ Asinxron — I/O kutish paytida THREAD BO'SHATILADI (boshqa so'rov XIZMAT qiladi)
public async Task<IActionResult> Get(int id) => Ok(await _context.Employees.FindAsync(id));
```

```
Qachon async ISHLATILISHI kerak: DB, HTTP, fayl — ISTALGAN I/O
operatsiya bo'lganda — HAR DOIM async/await. Sinxron I/O — THREAD
POOL'ni "band" qilib, YUQORI trafikda SERVER SIG'IMINI kamaytiradi.
```

### 3.8 HttpResults type (Minimal API)

```csharp
app.MapGet("/employees/{id}", (int id, AppDbContext db) =>
{
    var emp = db.Employees.Find(id);
    return emp is null ? Results.NotFound() : Results.Ok(emp);
});

// Typed Results (compile-time xavfsizroq, .NET 7+)
app.MapGet("/employees/{id}", Results<Ok<Employee>, NotFound> (int id, AppDbContext db) =>
{
    var emp = db.Employees.Find(id);
    return emp is null ? TypedResults.NotFound() : TypedResults.Ok(emp);
});
```

### 3.9 Model binding

```csharp
[HttpGet("{id}")]
public IActionResult Get(
    int id,                          // [FromRoute] — URL'dan
    [FromQuery] string? search,      // ?search=...
    [FromHeader] string? auth,        // HTTP header'dan
    [FromBody] UpdateDto dto)         // Request body'dan
```

### 3.10 Status kodlar jadvali

```
1xx — Informational: 100 Continue
2xx — Muvaffaqiyat: 200 OK, 201 Created, 204 No Content
3xx — Redirect: 301 Moved Permanently, 304 Not Modified
4xx — Client xatosi: 400 Bad Request, 401 Unauthorized,
       403 Forbidden, 404 Not Found, 409 Conflict
5xx — Server xatosi: 500 Internal Server Error, 503 Service Unavailable
```

## 4. Kod — to'liq CRUD Controller

```csharp
[ApiController]
[Route("api/[controller]")]
public class EmployeesController : ControllerBase
{
    [HttpGet]
    public async Task<ActionResult<List<EmployeeDto>>> GetAll()
        => Ok(await _service.GetAllAsync());

    [HttpGet("{id:int}")]
    public async Task<ActionResult<EmployeeDto>> GetById(int id)
    {
        var emp = await _service.GetByIdAsync(id);
        return emp is null ? NotFound() : Ok(emp);
    }

    [HttpPost]
    public async Task<ActionResult<EmployeeDto>> Create(CreateEmployeeDto dto)
    {
        var emp = await _service.CreateAsync(dto);
        return CreatedAtAction(nameof(GetById), new { id = emp.Id }, emp);
    }

    [HttpPut("{id:int}")]
    public async Task<IActionResult> Update(int id, UpdateEmployeeDto dto)
    {
        await _service.UpdateAsync(id, dto);
        return NoContent();
    }

    [HttpDelete("{id:int}")]
    public async Task<IActionResult> Delete(int id)
    {
        await _service.DeleteAsync(id);
        return NoContent();
    }
}
```

## 5. Qachon ishlatish kerak?

| Vaziyat | Yechim |
|---|---|
| Swagger'da aniq javob turi kerak | `ActionResult<T>` |
| Turli javob turlari aralash | `IActionResult` |
| Yangi resurs yaratish | `CreatedAtAction` (201) |
| O'chirish, javob tanasi kerak emas | `NoContent()` (204) |
| Har qanday I/O operatsiya | async/await |

## 6. Muhim nuqtalar

- Route constraint (`{id:int}`) — noto'g'ri formatdagi so'rovni
  **404**ga aylantiradi (Action ichida qo'lda tekshirish shart emas).
- `ActionResult<T>` — Swagger/NSwag/Refit client generatorlar uchun
  **muhim** — aniq tur schema beradi.
- Sinxron I/O — yuqori trafikda thread pool **charchashi**ga olib
  kelishi mumkin — har doim async tavsiya etiladi.

## 7. Imtihon savollari

1. Convention-based va Attribute routing orasidagi farq nima?
2. Route constraint (`{id:int}`) qanday ishlaydi?
3. `IActionResult` va `ActionResult<T>` orasidagi farq Swagger
   nuqtai nazaridan qanday?
4. `CreatedAtAction` nima qaytaradi va u qaysi REST konvensiyasiga
   mos keladi?
5. Nima uchun DB so'rovlarida sinxron metod o'rniga async
   ishlatilishi tavsiya etiladi?
6. 401 va 403 status kodlari orasidagi farq nima?
7. Minimal API'da `Results.Ok()` va `TypedResults.Ok()` orasidagi
   farq nima?
