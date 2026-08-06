# CancellationToken — Junior A

## 1. Nima? (Ta'rif)

**CancellationToken** — asinxron (yoki uzoq davom etuvchi)
operatsiyani **"bekor qilish" signalini** uzatuvchi struktura.
**CancellationTokenSource** — bu tokenni **yaratuvchi va
boshqaruvchi** manba.

## 2. Nima uchun kerak?

HTTP so'rov client tomonidan **bekor qilinsa** (masalan, brauzer
yopilsa) yoki **timeout** yuz bersa — server hali ham DB'dan
ma'lumot o'qishda **davom etaverishi** — resurslarni **behuda
sarflaydi**. CancellationToken — bu holatlarda operatsiyani **tezkor**
to'xtatish imkonini beradi (**cooperative cancellation**).

## 3. Ichida nima sodir bo'ladi? (Mexanizm)

### 3.1 CancellationTokenSource — token yaratish va bekor qilish

```csharp
var cts = new CancellationTokenSource();
CancellationToken token = cts.Token;

// Boshqa joydan (masalan foydalanuvchi "Cancel" bosganda)
cts.Cancel(); // Token'ga "bekor qilindi" BELGISINI qo'yadi
```

### 3.2 `Cancel()`, `CancelAfter()`

```csharp
cts.Cancel(); // DARHOL bekor qilish

cts.CancelAfter(TimeSpan.FromSeconds(30)); // 30 SONIYADAN keyin AVTOMATIK bekor qilinadi (timeout)
```

### 3.3 `ThrowIfCancellationRequested()`, `IsCancellationRequested`

```csharp
public async Task ProcessLargeDataAsync(CancellationToken ct)
{
    for (int i = 0; i < 1_000_000; i++)
    {
        ct.ThrowIfCancellationRequested(); // Agar BEKOR QILINGAN bo'lsa — OperationCanceledException TASHLAYDI

        // yoki qo'lda tekshirish:
        if (ct.IsCancellationRequested)
            break; // yoki return

        DoWork(i);
    }
}
```

```
CancellationToken — MAJBURAN THREAD'ni "o'ldirmaydi"! Bu —
"COOPERATIVE" (hamkorlikdagi) mexanizm — KOD O'ZI, DAVRIY ravishda,
token holatini TEKSHIRISHI va O'ZI TO'XTASHI kerak. Agar kod
TEKSHIRMASA — operatsiya CHEKSIZ davom ETAVERADI (Cancel() chaqirilgan
bo'lsa ham)!
```

### 3.4 Linked token — bir nechta token birga

```csharp
var cts1 = new CancellationTokenSource();
var cts2 = new CancellationTokenSource();

var linkedCts = CancellationTokenSource.CreateLinkedTokenSource(cts1.Token, cts2.Token);
// linkedCts.Token — cts1 YOKI cts2 dan ISTALGANI bekor qilinsa — BEKOR QILINADI
```

### 3.5 ASP.NET Core'da — `HttpContext.RequestAborted`

```csharp
[HttpGet]
public async Task<IActionResult> GetReport(CancellationToken ct) // ✅ ASP.NET Core AVTOMATIK bog'laydi!
{
    // 'ct' — HttpContext.RequestAborted BILAN BOG'LANGAN
    // Agar CLIENT so'rovni BEKOR QILSA (brauzer yopilsa, tarmoq uzilsa) —
    // 'ct' AVTOMATIK bekor qilinadi!

    var data = await _context.Employees.ToListAsync(ct); // EF Core — ct'ni QABUL qiladi
    return Ok(data);
}
```

```
ASP.NET Core — HAR HTTP so'rov uchun ICHKI CancellationTokenSource
YARATADI. Agar CONTROLLER ACTION parametr sifatida `CancellationToken`
QABUL QILSA — MODEL BINDING orqali AVTOMATIK shu token INJECT
QILINADI (hech qanday QO'SHIMCHA sozlash SHART EMAS).
```

### 3.6 Async method'da `ct` parametr — konvensiya

```csharp
public async Task<Employee?> GetByIdAsync(int id, CancellationToken ct = default)
{
    return await _context.Employees.FirstOrDefaultAsync(e => e.Id == id, ct);
}
```

```
Konvensiya: `CancellationToken` — HAR DOIM METOD PARAMETRLARINING
ENG OXIRIDA, `= default` (default qiymat — CancellationToken.None)
BILAN — chaqiruvchi TOKEN UZATMASA HAM, metod ISHLAYDI (lekin
BEKOR QILISH imkoniyatisiz).
```

### 3.7 EF Core'da — `FindAsync`, `ToListAsync`

```csharp
var employee = await _context.Employees.FindAsync(new object[] { id }, ct);
var list = await _context.Employees.Where(e => e.IsActive).ToListAsync(ct);
await _context.SaveChangesAsync(ct);
```

Agar `ct` bekor qilingan bo'lsa — bu metodlar **DB so'rovi davomida**
`OperationCanceledException` tashlaydi (agar DB driver — Npgsql —
buni qo'llab-quvvatlasa, ODATDA HAQIQIY TCP so'rovni HAM bekor
qiladi — resurslarni tejaydi).

### 3.8 `HttpClient`da — `SendAsync(request, ct)`

```csharp
public async Task<string> FetchDataAsync(CancellationToken ct)
{
    using var response = await _httpClient.GetAsync("https://api.example.com/data", ct);
    return await response.Content.ReadAsStringAsync(ct);
}
```

### 3.9 Timeout — `CancelAfter`

```csharp
public async Task<string> FetchWithTimeoutAsync()
{
    using var cts = new CancellationTokenSource(TimeSpan.FromSeconds(10)); // 10s TIMEOUT

    try
    {
        return await _httpClient.GetStringAsync("https://slow-api.com/data", cts.Token);
    }
    catch (OperationCanceledException)
    {
        return "Timeout! So'rov 10 soniyadan uzoq davom etdi.";
    }
}
```

### 3.10 Cooperative Cancellation — nima degani

```
"Cooperative" (hamkorlikdagi) — Cancel() chaqirilishi — METOD
BAJARILISHINI MAJBURAN TO'XTATMAYDI (Thread.Abort() kabi — bu
ESKIRGAN va XAVFLI usul edi). Buning O'RNIGA:

1. Cancel() — TOKEN holatini "IsCancellationRequested = true"
   qiladi
2. BAJARILAYOTGAN kod — O'ZI, DAVRIY ravishda, buni TEKSHIRISHI
   kerak (masalan HAR LOOP iteratsiyasida)
3. Kod TOPSA — O'ZI to'xtaydi (odatda OperationCanceledException
   orqali)

Bu — RESURSLARNING TO'G'RI TOZALANISHINI (finally, using) TA'MINLAYDI
— MAJBURIY to'xtatish esa OBYEKTLARNI "yarim tayyor" holatda
QOLDIRISHI mumkin edi.
```

## 4. Kod — real ERP misoli: uzoq davom etuvchi operatsiyani bekor qilish

```csharp
public class PayrollCalculationService
{
    public async Task<PayrollResult> CalculateAllAsync(CancellationToken ct)
    {
        var employees = await _context.Employees.ToListAsync(ct);
        var results = new List<decimal>();

        foreach (var emp in employees)
        {
            ct.ThrowIfCancellationRequested(); // HAR ITERATSIYADA tekshirish

            var salary = await CalculateSalaryAsync(emp, ct); // ICHKI async chaqiruv HAM ct qabul qiladi
            results.Add(salary);
        }

        return new PayrollResult(results);
    }
}

[HttpPost("calculate-payroll")]
public async Task<IActionResult> CalculatePayroll(CancellationToken ct)
{
    try
    {
        var result = await _payrollService.CalculateAllAsync(ct);
        return Ok(result);
    }
    catch (OperationCanceledException)
    {
        return StatusCode(499, "So'rov bekor qilindi"); // 499 — noresmi "Client Closed Request"
    }
}
```

## 5. Qachon ishlatish kerak?

| Vaziyat | Yechim |
|---|---|
| HTTP so'rov client tomonidan bekor qilinishi mumkin | `ct` parametrni Controller Action'da qabul qilish |
| Tashqi API chaqiruvi uzoq davom etishi mumkin | `CancelAfter` bilan timeout |
| Katta hajmli, uzoq loop | HAR iteratsiyada `ThrowIfCancellationRequested()` |
| Bir nechta bekor qilish manbasi | Linked token |

## 6. Muhim nuqtalar

- CancellationToken — **majburiy to'xtatish EMAS** — kod O'ZI
  hamkorlik qilishi (token tekshirishi) kerak.
- ASP.NET Core'da Controller Action parametr sifatida `CancellationToken`
  qabul qilish — **avtomatik** `HttpContext.RequestAborted`ga
  bog'lanadi, qo'shimcha kod SHART EMAS.
- EF Core/HttpClient metodlariga `ct`ni **uzatishni unutish** — eng
  ko'p uchraydigan xato — bu holda bekor qilish signali **ishlamay**
  qoladi.

## 7. Imtihon savollari

1. CancellationToken "cooperative" (hamkorlikdagi) mexanizm degani
   nima anglatadi?
2. `ThrowIfCancellationRequested()` va `IsCancellationRequested`
   orasidagi farq nima?
3. ASP.NET Core Controller Action'da `CancellationToken` parametri
   qanday avtomatik ishlaydi?
4. `CancelAfter()` qanday amaliy vaziyatda (timeout) ishlatiladi?
5. Linked token nima va u qachon kerak bo'ladi?
6. EF Core so'rovlariga `ct` uzatilmasa, nima yo'qotiladi?
7. Nima uchun `Thread.Abort()` kabi "majburiy" to'xtatish yondashuvi
   xavfli hisoblanadi, `CancellationToken` esa xavfsizroq?
