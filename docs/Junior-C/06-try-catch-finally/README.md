# try-catch-finally — chuqurroq — Junior C

## 1. Nima?

**Exception handling** — dastur bajarilishi vaqtida yuzaga keladigan
kutilmagan xatolarni (`Exception`) ushlab, dasturni "toza" holatda
davom ettirish yoki mos ravishda to'xtatish mexanizmi. `try` — xavfli
kod bloki, `catch` — xatoni ushlash, `finally` — har doim (xato
bo'lsa ham, bo'lmasa ham) bajariladigan tozalash bloki.

## 2. Nima uchun kerak?

Agar exception handling bo'lmaganida — bitta kutilmagan xato (masalan,
DB ulanish uzilishi) butun dasturni **darhol to'xtatib qo'yardi**
(crash). ERP tizimida bitta xodim yozuvini saqlashda xato bo'lsa,
butun HTTP serverning yiqilib qolishi qabul qilinmas holat.

`finally` esiz — resurslarni (fayl, connection, lock) to'g'ri
tozalash uchun har bir mumkin bo'lgan chiqish yo'lida (return, throw,
normal tugash) qo'lda kod yozish kerak bo'lardi — bu xatolarga moyil.

## 3. Ichida nima sodir bo'ladi? (Mexanizm)

### 3.1 .NET Exception ierarxiyasi

```
System.Exception
│
├── System.SystemException
│   ├── NullReferenceException
│   ├── InvalidCastException
│   ├── IndexOutOfRangeException
│   ├── ArgumentException
│   │   ├── ArgumentNullException
│   │   └── ArgumentOutOfRangeException
│   ├── InvalidOperationException
│   ├── OverflowException
│   ├── StackOverflowException      ← ushlab bo'lmaydi!
│   ├── OutOfMemoryException        ← ushlash tavsiya etilmaydi
│   └── IOException
│       ├── FileNotFoundException
│       └── DirectoryNotFoundException
│
├── System.ApplicationException     ← eskirgan, custom uchun endi tavsiya etilmaydi
│
└── (custom) AppException : Exception  ← o'z loyihangizdagi custom exception lar
    ├── NotFoundException
    ├── ValidationException
    └── UnauthorizedException
```

Har bir `Exception` obyektida:
```csharp
public class Exception
{
    public string Message { get; }
    public string? StackTrace { get; }   // Qayerda tashlanganini ko'rsatadi
    public Exception? InnerException { get; } // "Sabab bo'lgan" ichki exception
    public IDictionary Data { get; }     // Qo'shimcha ma'lumot saqlash uchun
}
```

### 3.2 try-catch-finally bajarilish tartibi — CLR darajasida

```csharp
try
{
    Console.WriteLine("1");
    throw new InvalidOperationException("xato");
    Console.WriteLine("2"); // Bu HECH QACHON bajarilmaydi
}
catch (InvalidOperationException ex)
{
    Console.WriteLine("3: " + ex.Message);
}
finally
{
    Console.WriteLine("4");
}
Console.WriteLine("5");

// Natija: 1, 3: xato, 4, 5
```

CLR ichida `try` bloki uchun **Exception Handling Table** yaratiladi
(IL metadata'da) — har bir try region uchun qaysi catch/finally
bloklari mos kelishi belgilanadi. Exception tashlanganda, CLR bu
jadvalni **stack unwinding** orqali tekshiradi — mos catch topilguncha
har bir chaqiruv darajasini (call stack frame) yuqoriga qarab
ko'tariladi.

```
Stack unwinding jarayoni:

Method C() { throw new Exception(); }  ← Xato shu yerda tashlandi
Method B() { C(); }                     ← Mos catch yo'q, yuqoriga o'tadi
Method A() { try { B(); } catch { } }    ← Mos catch TOPILDI!

CLR: C → B → A yo'nalishida "unwinding" qiladi,
     har birida finally bloklarini (agar bo'lsa) BAJARIB o'tadi
```

### 3.3 Catch bloklari tartibi — aniqdan umumga

```csharp
try
{
    // ...
}
catch (FileNotFoundException ex)   // ✅ Aniq tur — birinchi
{
    // ...
}
catch (IOException ex)             // ✅ Umumiyroq — ikkinchi
{
    // ...
}
catch (Exception ex)               // ✅ Eng umumiy — oxirida
{
    // ...
}

// ❌ Compile xatosi — umumiy tur birinchi bo'lsa, keyingi catch HECH QACHON ishlamaydi!
try { }
catch (Exception ex) { }
catch (IOException ex) { } // ❌ CS0160: "already handled by previous catch"
```

CLR runtime da catch bloklari **yuqoridan pastga** tekshiriladi —
birinchi mos keladigan (`is` orqali) blok ishga tushadi. Shuning uchun
**aniq turlar birinchi**, umumiy `Exception` — **oxirida** bo'lishi
shart.

### 3.4 `throw` vs `throw ex` — stack trace farqi

```csharp
try
{
    DoSomething();
}
catch (Exception ex)
{
    throw;     // ✅ Original stack trace SAQLANADI (qayerda birinchi tashlanganini ko'rsatadi)
}

try
{
    DoSomething();
}
catch (Exception ex)
{
    throw ex;  // ❌ Stack trace QAYTA YOZILADI — "throw ex" qatoridan boshlab ko'rsatadi!
}
```

IL darajasida farq: `throw;` — `rethrow` IL buyrug'ini ishlatadi (asl
exception obyektini stack trace bilan birga qayta tashlaydi). `throw
ex;` — oddiy `throw` IL buyrug'i — bu xuddi **yangi** joydan tashlangandek
ishlaydi, va debugging paytida "xato qayerdan boshlangani" ma'lumoti
yo'qoladi.

```
❌ throw ex; bilan stack trace:
   at Program.Catch() in Program.cs:line 15   ← faqat shu yerdan boshlab!

✅ throw; bilan stack trace:
   at Program.DoSomething() in Program.cs:line 3   ← ASL manba saqlangan!
   at Program.Catch() in Program.cs:line 10
```

### 3.5 Exception Filter — `when`

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

`when` — IL darajasida **filter block** yaratadi. Muhim farq: filter
`false` qaytarsa — CLR **keyingi catch blokka o'tadi**, lekin bu
jarayonda **stack hali unwind qilinmagan** (filter kod ustida — asl
call stack saqlanган holda ishlaydi). Bu debugging uchun foydali —
filter ichida `Debugger.Break()` qo'ysangiz, asl xato joyi hali
bekor qilinmagan bo'ladi.

```csharp
// when — try-catch zanjirsiz "if" bilan almashtirib bo'lmaydigan holat emas,
// lekin kodni ancha o'qilishli qiladi:
catch (Exception ex) when (LogAndReturnFalse(ex)) { } // filter side-effect uchun ham ishlatilishi mumkin (unusual, lekin mumkin)
```

### 3.6 Custom Exception

```csharp
public class AppException : Exception
{
    public int StatusCode { get; }

    public AppException(string message, int statusCode = 500)
        : base(message)
    {
        StatusCode = statusCode;
    }

    public AppException(string message, Exception innerException, int statusCode = 500)
        : base(message, innerException)
    {
        StatusCode = statusCode;
    }
}

public class NotFoundException : AppException
{
    public NotFoundException(string message) : base(message, 404) { }
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

**Nima uchun `Exception`dan (yoki o'z `AppException` bazasidan) meros
olish kerak, `ApplicationException`dan emas?** Microsoft
`ApplicationException`ni eskirgan (legacy) deb e'lon qilgan — u hech
qanday qo'shimcha qiymat bermaydi. Zamonaviy .NET da to'g'ridan
`Exception`dan (yoki loyihangizning umumiy `AppException` bazasidan)
meros olish tavsiya etiladi.

### 3.7 Exception Middleware bilan birgalikda (ASP.NET Core)

```csharp
public class ExceptionMiddleware
{
    private readonly RequestDelegate _next;

    public ExceptionMiddleware(RequestDelegate next) => _next = next;

    public async Task InvokeAsync(HttpContext context)
    {
        try
        {
            await _next(context);
        }
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
        catch (Exception ex)
        {
            context.Response.StatusCode = 500;
            await context.Response.WriteAsJsonAsync(new { message = "Server xatosi" });
        }
    }
}
```

Bu — har bir Controller da qayta-qayta try-catch yozishning oldini
oladi: butun so'rov "pipeline"ini bitta joydan qamrab oladi
(cross-cutting concern).

### 3.8 `using` — finally ning qisqa yo'li va IDisposable

```csharp
// Uzun yo'l — finally qo'lda
var conn = new NpgsqlConnection(str);
try
{
    conn.Open();
    // ...
}
finally
{
    conn.Dispose(); // Har doim chaqiriladi — Open() muvaffaqiyatsiz bo'lsa ham
}

// Qisqa yo'l (C# 8+) — using declaration
using var conn2 = new NpgsqlConnection(str);
conn2.Open();
// Scope tugaganda (metod oxiri yoki blok oxiri) — avtomatik Dispose() chaqiriladi
```

`using` — compiler tomonidan **try-finally** ga tarjima qilinadi.
`IDisposable.Dispose()` — **deterministik** tozalash (darhol,
predictable), Finalizer (`~ClassName()`) esa — Garbage Collector
tomonidan **noaniq vaqtda** chaqiriladi. Shuning uchun resurs egallovchi
klasslar (`Connection`, `FileStream`) — **Dispose pattern**ni
implement qilishi shart.

### 3.9 AggregateException — parallel xatolar

```csharp
try
{
    await Task.WhenAll(task1, task2, task3);
}
catch (Exception ex)
{
    // ⚠️ Task.WhenAll — faqat BIRINCHI exception ni to'g'ridan tashlaydi!
    // Barcha xatolarni ko'rish uchun:
}

try
{
    Task.WaitAll(task1, task2, task3); // Sinxron kutish
}
catch (AggregateException aex)
{
    // ✅ AggregateException — HAMMA parallel xatolarni o'z ichiga oladi
    foreach (var ex in aex.InnerExceptions)
        Console.WriteLine(ex.Message);

    // Flatten — ichma-ich AggregateException larni tekislash
    foreach (var ex in aex.Flatten().InnerExceptions)
        Console.WriteLine(ex.Message);
}
```

`Task.WhenAll` (async/await bilan) — faqat birinchi xatoni to'g'ridan
tashlaydi, lekin `Task.Exception` propertysi orqali barcha xatolarni
`AggregateException` sifatida olish mumkin:

```csharp
var allTasks = Task.WhenAll(task1, task2, task3);
try { await allTasks; }
catch { foreach (var ex in allTasks.Exception!.InnerExceptions) { /* ... */ } }
```

### 3.10 `finally` va `return` — IL darajasida

```csharp
public int Test()
{
    try
    {
        return 1;
    }
    finally
    {
        Console.WriteLine("Bu ham chiqadi!"); // ✅ HAR DOIM bajariladi
    }
}
```

IL darajasida `return` qatorida qiymat **vaqtinchalik saqlanadi**
(local slotda), so'ngra `finally` bloki bajariladi, va **eng oxirida**
qiymat qaytariladi. Shuning uchun `try` ichida `return` bo'lsa ham,
`finally` **hech qachon o'tkazib yuborilmaydi**.

```csharp
public int Tricky()
{
    try { return 1; }
    finally { return 2; } // ⚠️ ANTI-PATTERN! Natija: 2 (finally dagi return try dagini "bosib o'tadi")
}
```

## 4. Kod — asosiy sintaksis (real ASP.NET Core misol)

```csharp
public class EmployeeService
{
    public async Task<Employee> GetByIdAsync(int id)
    {
        try
        {
            var emp = await _context.Employees.FindAsync(id);
            if (emp is null)
                throw new NotFoundException($"Employee {id} topilmadi");

            return emp;
        }
        catch (NpgsqlException ex) when (ex.SqlState == "57P01")
        {
            // Connection admin tomonidan yopilgan — qayta urinish logikasi
            _logger.LogWarning(ex, "DB connection yopilgan, qayta urinilmoqda");
            throw new AppException("Ma'lumotlar bazasi vaqtincha ishlamayapti", ex, 503);
        }
        catch (DbUpdateException ex)
        {
            _logger.LogError(ex, "DB update xatosi");
            throw new AppException("Ma'lumotni saqlab bo'lmadi", ex);
        }
    }
}
```

## 5. Qachon ishlatish kerak?

| Vaziyat | Yondashuv |
|---|---|
| Kutilgan biznes xato (masalan "topilmadi") | Custom exception (`NotFoundException`) |
| Kutilmagan tizim xatosi (DB, tarmoq) | Umumiy `catch (Exception)`, log qilish, middleware ga uzatish |
| Bir nechta HTTP status kod turli xato uchun | Exception filter (`when`) yoki custom exception hierarchy |
| Resurs (connection, fayl) boshqarish | `using`/`await using` |
| Parallel tasklardan barcha xatolarni yig'ish | `Task.WaitAll` + `AggregateException` |
| Xatoni qayta tashlash (log qilib) | `throw;` (HECH QACHON `throw ex;` emas) |

**Anti-patternlar:**

```csharp
// ❌ "Swallow" — xatoni yutib yuborish, hech narsa qilmaslik
try { DoWork(); }
catch { } // Xato yo'qoladi, hech qanday iz qolmaydi!

// ❌ Exception'ni oddiy control flow uchun ishlatish (sekin!)
try { return dict[key]; }
catch (KeyNotFoundException) { return null; }
// ✅ TryGetValue — tezroq, exception yo'q
if (dict.TryGetValue(key, out var value)) return value;

// ❌ Juda umumiy catch, aniq xato turini yashiradi
catch (Exception) { throw new Exception("xato bo'ldi"); } // Original ma'lumot yo'qoladi!
```

## 6. Qo'shimcha — chuqur nuqtalar

- **`ExceptionDispatchInfo`** — exception ni boshqa thread/kontekstda
  qayta tashlash, original stack trace'ni saqlab qolgan holda:
  ```csharp
  ExceptionDispatchInfo? capturedEx = null;
  try { DoWork(); }
  catch (Exception ex) { capturedEx = ExceptionDispatchInfo.Capture(ex); }
  capturedEx?.Throw(); // Original stack trace bilan qayta tashlaydi
  ```

- **`StackOverflowException` va `OutOfMemoryException`** — bularni
  **ushlab bo'lmaydi** (yoki ushlash tavsiya etilmaydi) — CLR bu
  holatlarda darhol process'ni to'xtatadi, chunki dastur holati
  ishonchsiz bo'lib qoladi.

- **`Environment.FailFast`** — jiddiy, tuzatib bo'lmaydigan xatoda
  dasturni **darhol** to'xtatish — hatto `finally` bloklari ham
  bajarilmaydi (normal exception unwinding'dan farqli).

- **Exception qimmat (performance)** — stack trace yig'ish, unwinding
  jarayoni CPU sarflaydi. Shuning uchun exception larni **kutilmagan**
  holatlar uchun, oddiy "control flow" uchun emas ishlatish kerak
  (`TryParse` patterni shuning uchun mavjud).

- **C# versiyalaridagi o'zgarishlar:**
  - C# 6.0 — Exception filters (`when`)
  - C# 7.1 — `throw` expression sifatida (`x ?? throw new ArgumentNullException()`)
  - .NET Core 3+ — `IExceptionHandler` (yangi, .NET 8) — Middleware'ga alternativa

- **Real loyihada uchraydigan xato:** `catch (Exception ex) { throw
  ex; }` — bu ba'zan "log qilish + qayta tashlash" degan niyat bilan
  yoziladi, lekin production log'larida asl xato joyi yo'qolgani
  sababli debugging ancha qiyinlashadi.

## 7. Imtihon savollari

1. `throw;` va `throw ex;` orasidagi farqni IL/stack trace darajasida
   tushuntiring.
2. Nima uchun `catch` bloklari aniqdan umumga tartibda yozilishi
   SHART? Aks holda nima sodir bo'ladi?
3. Exception Filter (`when`) qanday ishlaydi va u oddiy `if` bilan
   nima farq qiladi (stack unwinding nuqtai nazaridan)?
4. `finally` bloki `try` ichidagi `return`dan keyin ham ishlaydimi?
   IL darajasida buni qanday tushuntirasiz?
5. Custom exception yaratishda nima uchun `ApplicationException`
   emas, `Exception`dan meros olish tavsiya etiladi?
6. `AggregateException` qachon yuzaga keladi? `Task.WhenAll` va
   `Task.WaitAll` orasida bu borada qanday farq bor?
7. `using` statement compiler tomonidan qanday IL konstruksiyasiga
   aylantiriladi?
8. Nega `StackOverflowException`ni odatiy `catch (Exception)` bilan
   ushlab bo'lmaydi?
