# try-catch-finally — chuqurroq — Junior C

## 1. Exception ierarxiyasi

```
Exception
├── SystemException
│   ├── NullReferenceException
│   ├── InvalidCastException
│   ├── IndexOutOfRangeException
│   ├── OverflowException
│   └── IOException
│       └── FileNotFoundException
└── ApplicationException (custom uchun)
    └── AppException (o'zimizniki)
```

## 2. Exception Filter — `when`

```csharp
try
{
    await _httpClient.GetAsync(url);
}
catch (HttpRequestException ex) when (ex.StatusCode == HttpStatusCode.NotFound)
{
    throw new NotFoundException("Resurs topilmadi");
}
catch (HttpRequestException ex) when (ex.StatusCode == HttpStatusCode.Unauthorized)
{
    throw new UnauthorizedException("Ruxsat yo'q");
}
catch (HttpRequestException ex)
{
    _logger.LogError(ex, "HTTP xatosi");
    throw;
}
```

## 3. `throw` vs `throw ex`

```csharp
try { ... }
catch (Exception ex)
{
    throw;    // ✅ Stack trace SAQLANADI
    throw ex; // ❌ Stack trace YO'QOLADI
}
```

## 4. Custom Exception

```csharp
public class AppException : Exception
{
    public int StatusCode { get; }

    public AppException(string message, int statusCode = 500)
        : base(message)
    {
        StatusCode = statusCode;
    }
}

public class NotFoundException : AppException
{
    public NotFoundException(string message)
        : base(message, 404) { }
}

public class ValidationException : AppException
{
    public IEnumerable<string> Errors { get; }

    public ValidationException(IEnumerable<string> errors)
        : base("Validatsiya xatosi", 400)
    {
        Errors = errors;
    }
}
```

## 5. Exception Middleware bilan birgalikda

```csharp
catch (NotFoundException ex)
{
    context.Response.StatusCode = 404;
    await context.Response.WriteAsJsonAsync(new { ex.Message });
}
catch (ValidationException ex)
{
    context.Response.StatusCode = 400;
    await context.Response.WriteAsJsonAsync(new { ex.Errors });
}
```

## 6. using — finally ning qisqa yo'li

```csharp
// Uzun yo'l
var conn = new NpgsqlConnection(str);
try { ... }
finally { conn.Dispose(); }

// Qisqa yo'l (C# 8+)
using var conn = new NpgsqlConnection(str);
```

## 7. AggregateException — parallel xatolar

```csharp
try
{
    await Task.WhenAll(task1, task2, task3);
}
catch (AggregateException aex)
{
    foreach (var ex in aex.InnerExceptions)
        Console.WriteLine(ex.Message);
}
```

## 8. Qo'shimcha nuqtalar

- **`finally` va `return`** — `finally` har doim ishlaydi:
  ```csharp
  try { return 1; }
  finally { Console.WriteLine("Bu ham chiqadi!"); }
  ```
- **`ExceptionDispatchInfo`** — exception ni boshqa threadda qayta
  tashlash, stack trace saqlanadi.
- **`Environment.FailFast`** — jiddiy xatoda dasturni darhol to'xtatish,
  `finally` ham ishlamaydi.

## 9. Imtihon savollari

1. `throw` va `throw ex` orasidagi farq nima?
2. Exception filter (`when`) qachon kerak?
3. `finally` bloki `return` dan keyin ham ishlaydi. Nima uchun?
4. Custom exception yaratishda nima uchun `AppException` dan meros olish kerak?
5. `AggregateException` qachon yuzaga keladi?
