# Handle Errors — ASP.NET Core — Middle D

## 1. Nima? (Ta'rif)

**Global Exception Handling** — butun ilova bo'yicha xatolarni
**bitta markazlashgan joyda** ushlab, mos HTTP javob qaytarish
mexanizmi.

## 2. Nima uchun kerak?

Har bir Controller/Handler ichida `try-catch` yozish — takrorlanuvchi
va **unutish oson** (bitta joyda unutilgan try-catch — unhandled
exception, 500 xatosi va xavfsizlik zaifligi — stack trace client'ga
oshkor bo'lishi).

## 3. Ichida nima sodir bo'ladi? (Mexanizm)

### 3.1 Middleware pipeline — nima uchun eng birinchi

```
app.UseExceptionHandler(...)   ← 1-BIRINCHI — pastdagi BARCHA middleware'
app.UseHsts();                    larda yuzaga kelgan xatoni USHLAYDI
app.UseHttpsRedirection();
app.UseAuthentication();
app.UseAuthorization();
app.MapControllers();

Agar ExceptionHandler OXIRIDA bo'lsa — undan OLDIN yuz bergan
xatolarni USHLAY OLMAYDI (chunki pipeline "ichma-ich" ishlaydi —
tashqi qatlam ICHKI qatlamdagi xatoni ushlaydi).
```

### 3.2 Custom Exception ierarxiyasi

```csharp
public abstract class AppException : Exception
{
    public int StatusCode { get; }
    protected AppException(string message, int statusCode) : base(message)
        => StatusCode = statusCode;
}

public class NotFoundException : AppException
{
    public NotFoundException(string message) : base(message, 404) { }
}

public class ValidationException : AppException
{
    public IEnumerable<string> Errors { get; }
    public ValidationException(IEnumerable<string> errors) : base("Validatsiya xatosi", 400)
        => Errors = errors;
}

public class ForbiddenException : AppException
{
    public ForbiddenException(string message) : base(message, 403) { }
}
```

### 3.3 Global Exception Handler (`IExceptionHandler`, .NET 8+)

```csharp
public class GlobalExceptionHandler : IExceptionHandler
{
    private readonly ILogger<GlobalExceptionHandler> _logger;

    public async ValueTask<bool> TryHandleAsync(
        HttpContext httpContext, Exception exception, CancellationToken ct)
    {
        var (statusCode, title) = exception switch
        {
            NotFoundException => (404, exception.Message),
            ValidationException => (400, exception.Message),
            ForbiddenException => (403, exception.Message),
            _ => (500, "Kutilmagan server xatosi")
        };

        _logger.LogError(exception, "Xato ushlandi: {Message}", exception.Message);

        httpContext.Response.StatusCode = statusCode;
        await httpContext.Response.WriteAsJsonAsync(new ProblemDetails
        {
            Status = statusCode,
            Title = title,
            Type = "https://tools.ietf.org/html/rfc7807"
        }, ct);

        return true; // "Men ushladim, boshqa handler kerak emas"
    }
}

// Program.cs
builder.Services.AddExceptionHandler<GlobalExceptionHandler>();
builder.Services.AddProblemDetails();
var app = builder.Build();
app.UseExceptionHandler(); // 1-BIRINCHI middleware
```

### 3.4 ProblemDetails — RFC 7807

```json
{
  "type": "https://tools.ietf.org/html/rfc7807",
  "title": "Employee topilmadi",
  "status": 404,
  "traceId": "00-abc123..."
}
```

RFC 7807 — barcha xato javoblarini **standartlashtiradi** —
client kutubxonalar bir xil formatni **KUTADI VA PARSE QILADI**.

### 3.5 `throw` vs `throw ex`

```csharp
catch (Exception ex)
{
    throw;    // ✅ Stack trace SAQLANADI
    throw ex; // ❌ Stack trace QAYTA YOZILADI (asl manba yo'qoladi)
}
```

### 3.6 Exception filter (`when`)

```csharp
catch (DbUpdateException ex) when (ex.InnerException is PostgresException { SqlState: "23505" })
{
    // Faqat UNIQUE constraint xatosi uchun MAXSUS ishlov
    throw new ValidationException(new[] { "Bu qiymat allaqachon mavjud" });
}
```

### 3.7 Status kodlari — qachon qaysi

```
400 Bad Request    — Validatsiya xatosi, noto'g'ri format
401 Unauthorized   — Token yo'q/yaroqsiz (KIM ekanligi noma'lum)
403 Forbidden      — Token to'g'ri, lekin HUQUQ yo'q
404 Not Found      — Resurs topilmadi
409 Conflict       — Holat ziddiyati (unique constraint, concurrency)
422 Unprocessable  — Sintaksis to'g'ri, semantik xato
500 Internal Error — Kutilmagan server xatosi (client aybi EMAS)
```

### 3.8 Development vs Production — batafsil vs umumiy xato

```csharp
if (app.Environment.IsDevelopment())
{
    app.UseDeveloperExceptionPage(); // Stack trace, request/response TO'LIQ ko'rsatiladi
}
else
{
    app.UseExceptionHandler("/error"); // FAQAT umumiy xabar, ICHKI tafsilot YASHIRILADI
}
```

```
⚠️ XAVFSIZLIK: Production'da to'liq stack trace ko'rsatish —
   hujumchiga ICHKI tuzilma (fayl yo'llari, SQL so'rovlar, kutubxona
   versiyalari) haqida MA'LUMOT BERADI — bu razvedka (reconnaissance)
   uchun ishlatilishi mumkin.
```

## 4. Kod — MediatR bilan integratsiya

```csharp
// Handler ichida biznes xato tashlanadi
public class GetEmployeeHandler : IRequestHandler<GetEmployeeQuery, EmployeeDto>
{
    public async Task<EmployeeDto> Handle(GetEmployeeQuery request, CancellationToken ct)
    {
        var emp = await _context.Employees.FindAsync([request.Id], ct)
            ?? throw new NotFoundException($"Employee {request.Id} topilmadi");

        return _mapper.Map<EmployeeDto>(emp);
    }
}
// Controller — try-catch YOZILMAYDI, Global Handler avtomatik ushlaydi
[HttpGet("{id}")]
public async Task<EmployeeDto> GetById(int id) => await _mediator.Send(new GetEmployeeQuery(id));
```

## 5. Qachon ishlatish kerak?

| Vaziyat | Yechim |
|---|---|
| Umumiy, barcha xatolar uchun | Global Exception Handler (Middleware) |
| Maxsus HTTP status kod kerak | Custom `AppException` ierarxiyasi |
| Faqat BITTA metodda maxsus ishlov | Lokal `try-catch` + `when` filter |
| Client'ga standart xato formati | `ProblemDetails` (RFC 7807) |

## 6. Muhim nuqtalar

- Global handler — **hamma joyni** qamrab olsa ham, ba'zi **maxsus**
  holatlar (masalan tashqi API bilan retry) uchun lokal try-catch
  hali ham kerak bo'lishi mumkin.
- `throw ex` — kod review'da doim RAD ETILISHI kerak bo'lgan pattern.
- 500 xatosi — HAR DOIM **log** qilinishi kerak (Critical/Error
  darajasida), 400/404 kabi "kutilgan" xatolar — odatda Information/
  Warning darajasida.

## 7. Imtihon savollari

1. Exception Middleware nima uchun pipeline'da ENG BIRINCHI joylashishi
   kerak?
2. `throw` va `throw ex` orasidagi farqni tushuntiring.
3. `ProblemDetails` (RFC 7807) qanday standart va u nima uchun
   foydali?
4. 401 va 403 orasidagi farq nima?
5. Development va Production muhitida xato ko'rsatish nima uchun
   FARQ QILISHI kerak?
6. Exception filter (`when`) qachon foydali bo'ladi — misol keltiring.
