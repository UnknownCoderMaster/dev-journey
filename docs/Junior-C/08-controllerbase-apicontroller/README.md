# ControllerBase, Attributes, ApiController — Junior C

## 1. Nima?

**ControllerBase** — HTTP so'rovlarini qayta ishlovchi klass.
**[ApiController]** — REST API uchun maxsus xatti-harakatlarni
yoquvchi atribut.

## 2. Controller vs ControllerBase

```csharp
// Controller — MVC uchun (View qaytaradi)
public class HomeController : Controller
{
    public IActionResult Index() => View(); // HTML qaytaradi
}

// ControllerBase — API uchun (JSON qaytaradi)
public class EmployeesController : ControllerBase
{
    public IActionResult Get() => Ok(data); // JSON qaytaradi
}
```

## 3. [ApiController] nima qiladi?

```csharp
[ApiController]
[Route("api/[controller]")]
public class EmployeesController : ControllerBase { }
```

**1. Model validation avtomatik:**
```csharp
// [ApiController] bo'lmasa — qo'lda
if (!ModelState.IsValid) return BadRequest(ModelState);

// [ApiController] bilan — avtomatik 400 qaytaradi
```

**2. [FromBody] avtomatik:**
```csharp
// [ApiController] bilan — [FromBody] yozmasak ham bo'ladi
public IActionResult Create(Employee emp) { }
```

**3. ProblemDetails formati:**
```json
{
  "type": "https://tools.ietf.org/html/rfc7807",
  "title": "Bad Request",
  "status": 400,
  "errors": { "Name": ["Name is required"] }
}
```

## 4. Routing atributlari

```csharp
[Route("api/[controller]")]  // api/employees
[HttpGet]                    // GET /api/employees
[HttpGet("{id}")]            // GET /api/employees/42
[HttpGet("{id}/details")]    // GET /api/employees/42/details
[HttpPost]                   // POST /api/employees
[HttpPut("{id}")]            // PUT /api/employees/42
[HttpDelete("{id}")]         // DELETE /api/employees/42
```

## 5. Parametr manbalari

```csharp
[HttpGet("{id}")]
public IActionResult Get(
    int id,                           // [FromRoute] — URL dan
    [FromQuery] string? search,       // ?search=orzibek
    [FromHeader] string? authHeader,  // Header dan
    [FromBody] UpdateDto dto,         // Request body dan
    [FromForm] IFormFile? file)       // Form data dan
```

## 6. ActionResult turlari

```csharp
return Ok(data);              // 200 + data
return Created(url, data);    // 201 + Location header
return CreatedAtAction(...);  // 201 + action URL
return NoContent();           // 204
return BadRequest("xato");    // 400
return Unauthorized();        // 401
return Forbid();              // 403
return NotFound();            // 404
return StatusCode(500, msg);  // Ixtiyoriy status kod
```

## 7. Qo'shimcha nuqtalar

- **`[Consumes]` va `[Produces]`**:
  ```csharp
  [Consumes("application/json")]
  [Produces("application/json")]
  ```
- **`ActionResult<T>`** — Swagger avtomatik schema ko'rsatadi:
  ```csharp
  public ActionResult<Employee> Get() => Ok(new Employee());
  ```

## 8. Imtihon savollari

1. `Controller` va `ControllerBase` orasidagi farq nima?
2. `[ApiController]` avtomatik qiladigan 3 ta narsa?
3. `[FromQuery]` va `[FromRoute]` orasidagi farq nima?
4. `IActionResult` va `ActionResult<T>` orasidagi farq nima?
5. `CreatedAtAction` nima qaytaradi va nima uchun ishlatiladi?
