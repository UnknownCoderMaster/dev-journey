# async/await, Thread, Thread Pool — Junior B

## 1. What (Nima?)

**Thread** — operatsion tizim tomonidan boshqariladigan, **mustaqil
bajarilish yo'li** (execution path). **Thread Pool** — oldindan
yaratilgan, **qayta ishlatiladigan** thread'lar to'plami — har
vazifa uchun YANGI thread yaratish o'rniga, MAVJUD, "bo'sh" thread
ISHLATILADI. **async/await** — C#'ning **asinxron dasturlash**
kalit so'zlari — uzoq davom etuvchi operatsiyani (I/O) **thread'ni
bloklamasdan** kutish imkonini beradi.

## 2. Real hayot analogiyasi

**Thread — restoran oshxonasidagi oshpaz.** Har bir oshpaz — bir
vaqtning o'zida FAQAT bitta taomni tayyorlaydi (bir CPU core'da —
BIR VAQTDA FAQAT BITTA thread ISHLAYDI, ko'p core bo'lsa — PARALLEL).

**Thread Pool — "doimiy ishlaydigan oshpazlar jamoasi".** Restoran
har buyurtma uchun YANGI oshpaz YOLLAMAYDI (bu — SEKIN va QIMMAT) —
buning O'RNIGA, oldindan YOLLANGAN, TAYYOR turgan oshpazlardan
BIRINI ishga SOLADI. Buyurtma tugagach — oshpaz "bo'sh" holatga
QAYTADI, KEYINGI buyurtmani KUTADI.

**async/await — oshpaz pitsa PECHIGA qo'yib, KUTAYOTGANDA boshqa
ish qilishi.** Agar oshpaz pech oldida TURIB, pitsa TAYYOR bo'lguncha
HECH NARSA QILMASDAN KUTSA — bu VAQT ISROFI (SYNCHRONOUS bloklash).
Aksincha, pitsani pechga QO'YIB (`await`), oshpaz DARHOL BOSHQA
buyurtma bilan SHUG'ULLANADI — pech "tayyor!" deb XABAR BERGANDA
(callback) — oshpaz QAYTIB KELIB DAVOM ETADI.

## 3. Why (Nega kerak?)

Web serverda — bitta HTTP so'rov DB javobini **KUTAYOTGANDA** (masalan
50ms), agar THREAD **BLOKLANIB TURSA** — o'sha thread BOSHQA HECH
QANDAY so'rovga XIZMAT QILA OLMAYDI. Yuqori trafikda (soniyasiga
1000 so'rov) — HAR BIRIGA ALOHIDA, KUTIB TURGAN thread AJRATISH —
**Thread Pool'ni TEZ TUGATADI** ("Thread Pool Starvation").

`async/await` — bu muammoni HAL QILADI: DB javobini KUTISH paytida,
THREAD **Thread Pool'ga QAYTARILADI** (BOSHQA so'rovga XIZMAT
QILISHI mumkin), va DB javob BERGANDA — (ODATDA BOSHQA) thread
ISHNI DAVOM ETTIRADI. Natijada — BIR NECHTA thread bilan MINGLAB
PARALLEL so'rovga XIZMAT qilish MUMKIN.

**Node.js bilan solishtirish:** Node.js — BIR THREAD (single-threaded
event loop) bilan ASINXRON I/O'ni BOSHQARADI. .NET — Thread Pool +
async/await ORQALI, KO'P THREAD'da HAM asinxronlikni QO'LLAB-QUVVATLAYDI
— bu CPU-INTENSIV ishlarni HAM PARALLEL bajarish IMKONINI BERADI.

## 4. Internals (Ichki mexanizm)

### async/await — State Machine'ga aylanishi

```csharp
public async Task<string> GetDataAsync()
{
    var result = await _httpClient.GetStringAsync(url);
    return result.ToUpper();
}
```

Compiler bu metodni **State Machine** klassiga aylantiradi
(soddalashtirilgan):

```csharp
private class GetDataAsyncStateMachine : IAsyncStateMachine
{
    public int State; // "qayerda to'xtaganini" eslab qoladi
    public AsyncTaskMethodBuilder<string> Builder;

    public void MoveNext()
    {
        switch (State)
        {
            case 0:
                var awaiter = _httpClient.GetStringAsync(url).GetAwaiter();
                if (!awaiter.IsCompleted)
                {
                    State = 1;
                    Builder.AwaitOnCompleted(ref awaiter, ref this); // Thread QAYTARILADI!
                    return; // Metod SHU YERDA "TO'XTAYDI" (lekin thread band emas)
                }
                goto case 1;
            case 1:
                var result = awaiter.GetResult();
                Builder.SetResult(result.ToUpper());
                break;
        }
    }
}
```

```
Bu — "await" chaqirilganda:
1. Asinxron operatsiya (masalan HTTP so'rov) BOSHLANADI
2. Agar DARHOL tugamasa — METOD "TO'XTAYDI", THREAD Thread Pool'GA
   QAYTARILADI (band QILINMAYDI)
3. Operatsiya TUGAGANDA — CALLBACK orqali (SynchronizationContext
   yoki Thread Pool) METOD QOLGAN qismini BAJARISH uchun QAYTA
   CHAQIRILADI ("continuation")
```

### Thread Pool — ichki tuzilishi

```
Thread Pool — IKKI XIL "navbat"ga EGA:
  Worker Threads     — CPU-INTENSIV ishlar UCHUN
  I/O Completion Port (IOCP) Threads — I/O operatsiyalar TUGAGANDA
                                        CALLBACK BAJARISH uchun

Thread Pool — DINAMIK RAVISHDA thread SONINI BOSHQARADI:
  - Kam ISH bo'lsa — KAM thread (RESURS TEJASH)
  - Ko'p ISH kelsa — YANGI thread QO'SHILADI (LEKIN SEKIN — "Hill
    Climbing" algoritmi orqali, soniyasiga BIR NECHTA thread, DARHOL
    MINGLAB EMAS — bu "Thread Pool Starvation" xavfini TUSHUNTIRADI)
```

### `ConfigureAwait(false)` — nima uchun kerak

```csharp
await _httpClient.GetStringAsync(url).ConfigureAwait(false);
```

```
DEFAULT holatda — await'dan KEYIN, KOD "SynchronizationContext"ga
(masalan ASP.NET Core'da — ODATDA MAVJUD EMAS, lekin UI ilovalarida
— WPF/WinForms UI thread'i) QAYTISHGA "URINADI".

ConfigureAwait(false) — "QAYSI thread'da DAVOM ETISH MUHIM EMAS"
deydi — KUTUBXONA kodida (masalan NuGet paket) BU TAVSIYA ETILADI
(PERFORMANCE va DEADLOCK xavfini KAMAYTIRADI). ASP.NET Core'da —
SynchronizationContext YO'Q (allaqachon), shuning uchun BU KAMROQ
MUHIM, lekin YOMON ODAT EMAS.
```

### `Task` vs `Thread` — MUHIM farq

```
Thread   — HAQIQIY OS THREAD, QIMMAT (~1MB STACK, CONTEXT SWITCH
            OVERHEAD)
Task     — "ASINXRON OPERATSIYA"ning ABSTRAKSIYASI — HAR DOIM
            YANGI thread YARATMAYDI! Task Thread Pool'dan THREAD
            "QARZ OLADI", ISH TUGAGACH QAYTARADI.

new Thread(...) — DEYARLI HECH QACHON to'g'ridan ISHLATILMAYDI
                   zamonaviy .NET'da (Task.Run() afzal).
```

### Deadlock xavfi — `.Result`/`.Wait()`

```
❌ ASINXRON metodni SINXRON kutish (.Result yoki .Wait()) —
   SynchronizationContext MAVJUD muhitda (masalan ASP.NET Framework,
   WPF) — DEADLOCK keltirib chiqarishi MUMKIN:

1. UI thread — asyncMethod().Result CHAQIRADI, BLOKLANADI
2. asyncMethod() ICHIDA await TUGAGANDA — SynchronizationContext'ga
   (UI thread'ga) QAYTISHGA "URINADI"
3. LEKIN UI thread — HALI HAM BAND (1-qadamda BLOKLANGAN)!
4. CHEKSIZ KUTISH — DEADLOCK!
```

## 5. Code (Amaliy kod)

```csharp
// ✅ TO'G'RI — async ZANJIR OXIRIGACHA (Controller'gacha)
public async Task<IActionResult> GetEmployee(int id, CancellationToken ct)
{
    var employee = await _context.Employees.FindAsync(new object[] { id }, ct);
    return employee is null ? NotFound() : Ok(employee);
}

// ❌ XATO — .Result orqali ASINXRON metodni SINXRON kutish
public IActionResult GetEmployeeBad(int id)
{
    var employee = _context.Employees.FindAsync(id).Result; // DEADLOCK XAVFI!
    return Ok(employee);
}
```

```csharp
// Task.Run() — CPU-INTENSIV ishni Thread Pool'ga "topshirish"
public async Task<byte[]> GenerateReportAsync(List<Employee> employees)
{
    // Og'ir HISOB-KITOB — Thread Pool'ning ALOHIDA thread'ida BAJARILADI
    return await Task.Run(() => CalculateComplexReport(employees));
}

// ⚠️ I/O operatsiya (DB, HTTP) uchun Task.Run() KERAK EMAS!
// EF Core/HttpClient — O'ZI ALLAQACHON asinxron (native I/O completion) —
// Task.Run() bilan "o'rab olish" — FAQAT QO'SHIMCHA thread SARFLAYDI.
```

```csharp
// Bir nechta asinxron operatsiyani PARALLEL bajarish
public async Task<(List<Employee> Employees, List<Department> Departments)> LoadDashboardAsync(CancellationToken ct)
{
    var employeesTask = _context.Employees.ToListAsync(ct);
    var departmentsTask = _context.Departments.ToListAsync(ct);

    await Task.WhenAll(employeesTask, departmentsTask); // IKKALASI HAM BIR VAQTDA KUTILADI

    return (await employeesTask, await departmentsTask);
}
```

## 6. Keng tarqalgan xatolar / noto'g'ri tushunchalar

```
❌ "async — YANGI THREAD YARATADI" — NOTO'G'RI! async/await —
   MAVJUD thread'larni SAMARALIROQ ISHLATISH usuli, YANGI thread
   YARATISH EMAS.

❌ "Task.Run() — HAR DOIM async metodni TEZLASHTIRADI" — NOTO'G'RI!
   I/O operatsiyalarda (DB, HTTP) Task.Run() — FOYDASIZ, FAQAT
   QO'SHIMCHA thread OVERHEAD'i.

❌ "async Task Method() { ... } lekin await YOZILMAYDI" — COMPILER
   OGOHLANTIRADI (CS4014 yoki SHUNGA O'XSHASH) — bu METOD haqiqatda
   SINXRON ISHLAYDI, faqat "async" DEB BELGILANGAN.

❌ ".Result yoki .Wait() — XAVFSIZ, chunki 'tez tugaydi'" — HAR
   DOIM XAVFLI, ASP.NET (Framework)/UI kontekstida DEADLOCK
   xavfi bor — ZANJIR OXIRIGACHA async/await ISHLATILISHI kerak
   ("async all the way down").

❌ "async void — async Task bilan BIR XIL" — YO'Q! async void —
   EXCEPTION'larni to'g'ri USHLAB BO'LMAYDI, FAQAT EVENT HANDLER'lar
   uchun ISHLATILISHI kerak.
```

## 7. Exam (Interview savollari)

**1. `await` chaqirilganda thread'ga NIMA sodir bo'ladi?**
Agar kutilayotgan operatsiya DARHOL tugamasa — METOD "TO'XTAYDI"
(state machine holatini SAQLAB QOLADI), va THREAD **Thread Pool'ga
QAYTARILADI** — u BOSHQA ish bilan SHUG'ULLANISHI mumkin. Operatsiya
TUGAGANDA — (ODATDA BOSHQA) thread orqali METOD DAVOM ETTIRILADI.

**2. `Task.Run()` va to'g'ridan `await SomeAsyncMethod()` orasidagi
farq nima?**
`Task.Run()` — SINXRON (CPU-bound) kodni Thread Pool'ning ALOHIDA
thread'ida BAJARISH uchun. `await SomeAsyncMethod()` — METOD
O'ZI ALLAQACHON asinxron (I/O-bound) — QO'SHIMCHA thread KERAK
EMAS, chunki I/O — NATIVE darajada (OS) asinxron BAJARILADI.

**3. `.Result`/`.Wait()` nima uchun deadlock keltirib chiqarishi
mumkin?**
`SynchronizationContext` MAVJUD muhitda (masalan WPF/eski ASP.NET) —
`.Result` CHAQIRUVCHI thread'ni BLOKLAYDI. `await` esa, TUGAGANDAN
KEYIN, O'SHA ( band) SynchronizationContext'ga QAYTISHGA "URINADI" —
lekin u HALI BAND — CHEKSIZ kutish. ASP.NET Core'da SynchronizationContext
YO'Q, shuning uchun bu ANIQ ssenariy KAMROQ ehtimol, lekin BARIBIR
YOMON amaliyot (thread pool exhaustion xavfi qoladi).

**4. Thread Pool "starvation" nima va u qanday yuzaga keladi?**
Ko'p so'rov BIR VAQTDA thread'larni **BLOKLAYDI** (masalan `.Result`
orqali) — Thread Pool YANGI thread'larni FAQAT SEKIN (ma'lum
INTERVAL bilan) QO'SHADI — natijada BARCHA so'rovlar "navbatda"
QOLIB, JAVOB VAQTI KESKIN OSHADI (yoki timeout).

**5. `ConfigureAwait(false)` nima qiladi va u qachon kerak?**
`await`dan KEYIN, ASL SynchronizationContext'ga QAYTISHNI
"O'CHIRADI" — bu, ayniqsa KUTUBXONA kodida, PERFORMANCE
foyda beradi va DEADLOCK ehtimolini KAMAYTIRADI. ASP.NET Core'da
SynchronizationContext BO'LMAGANI uchun KAMROQ MUHIM, LEKIN
UMUMIY KUTUBXONA (masalan NuGet paket) yozayotganda YAXSHI
amaliyot hisoblanadi.
