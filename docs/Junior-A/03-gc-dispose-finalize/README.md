# Garbage Collector, using, Dispose, Finalize — Junior A

## 1. Nima? (Ta'rif)

**Garbage Collector (GC)** — .NET'ning **avtomatik xotira
boshqaruvi** mexanizmi — dasturchi `free()`/`delete` yozmasdan,
ishlatilmay qolgan obyektlarni **avtomatik** xotiradan tozalaydi.
**IDisposable** — **unmanaged** resurslarni (fayl, socket, DB
ulanish) **deterministik** (aniq vaqtda) tozalash uchun kontrakt.

## 2. Nima uchun kerak?

C/C++ da — dasturchi HAR bir `malloc`ga mos `free` yozishi kerak —
buni **unutish** — memory leak, **noto'g'ri vaqt**da qilish —
crash. GC — bu og'irlikni **avtomatlashtiradi**. Lekin GC — FAQAT
**managed** xotirani biladi — fayl handle, socket kabi **unmanaged**
resurslarni bilmaydi, shuning uchun `IDisposable` alohida kerak.

## 3. Ichida nima sodir bo'ladi? (Mexanizm)

### 3.1 GC qanday ishlaydi — Mark-and-Sweep

```
1. MARK (belgilash):
   GC — "root" (static field, stack o'zgaruvchi, CPU register)
   dan boshlab, BOG'LANGAN barcha obyektlarni "TIRIK" deb BELGILAYDI

2. SWEEP (tozalash):
   BELGILANMAGAN (root'dan yetib bo'lmaydigan) obyektlar —
   "O'LIK" deb hisoblanadi, XOTIRA QAYTARIB OLINADI

3. COMPACT (siqish):
   Qolgan TIRIK obyektlar — XOTIRADA yonma-yon JOYLASHTIRILADI
   (fragmentatsiyani KAMAYTIRISH uchun)
```

```
Root'lar:              Heap:
┌──────────┐           ┌─────────────────────────┐
│ static X │──────────►│ [Obj1: TIRIK]             │
│ local y  │──────────►│ [Obj2: TIRIK] → [Obj3]    │  Obj3 — Obj2 orqali TIRIK
└──────────┘           │ [Obj4: O'LIK — hech kim   │
                        │  ishora qilmaydi]          │
                        └─────────────────────────┘
```

### 3.2 GC Generations — Gen 0, Gen 1, Gen 2

```
Gen 0 — YANGI yaratilgan obyektlar. TEZ-TEZ tekshiriladi (KICHIK,
        TEZ collection)
Gen 1 — Gen 0'dan "OMON QOLGAN" obyektlar (bir necha collection
        davomida ISHLATILISHDA davom etgan)
Gen 2 — UZOQ YASHOVCHI obyektlar (Singleton, statik ma'lumot)

Nazariya: "Generational Hypothesis" — KO'PCHILIK obyektlar TEZ
"O'LADI" (masalan, metod ichidagi vaqtinchalik o'zgaruvchi).
Shuning uchun Gen 0'ni TEZ-TEZ tekshirish — SAMARALI (kam vaqt
sarflab, KO'P xotira qaytarib olinadi).

Gen 0 to'lsa → Collection → Omon qolganlar Gen 1'ga KO'CHADI
Gen 1 to'lsa → Collection → Omon qolganlar Gen 2'ga KO'CHADI
Gen 2 — KAMDAN-KAM tekshiriladi (QIMMAT operatsiya — KATTA HAJM)
```

### 3.3 Large Object Heap (LOH) — 85KB'dan katta obyektlar

```
Obyekt > 85,000 bayt → LOH'da (alohida heap segmentida) SAQLANADI

LOH xususiyati:
  - ODATDA COMPACT QILINMAYDI (fragmentatsiya XAVFI YUQORI)
  - To'g'ridan Gen 2 bilan BIRGA collect qilinadi (QIMMAT)

⚠️ Katta massiv/string'larni TEZ-TEZ yaratish — LOH FRAGMENTATSIYASI
   va OutOfMemoryException'ga olib kelishi mumkin (hatto YETARLI
   umumiy xotira bo'lsa ham — YAXLIT BLOK topilmasligi mumkin)!
```

### 3.4 IDisposable, Dispose(), Finalize()

```csharp
public class DatabaseConnection : IDisposable
{
    private IntPtr _unmanagedHandle; // Masalan native fayl handle
    private bool _disposed;

    public void Dispose()
    {
        Dispose(true);
        GC.SuppressFinalize(this); // Finalizer CHAQIRILISHI SHART EMAS (Dispose ALLAQACHON tozalagan)
    }

    protected virtual void Dispose(bool disposing)
    {
        if (_disposed) return;

        if (disposing)
        {
            // MANAGED resurslarni tozalash (masalan boshqa IDisposable obyektlar)
        }

        // UNMANAGED resurslarni tozalash (HAR DOIM, disposing'dan qat'i nazar)
        if (_unmanagedHandle != IntPtr.Zero)
        {
            NativeMethods.CloseHandle(_unmanagedHandle);
            _unmanagedHandle = IntPtr.Zero;
        }

        _disposed = true;
    }

    ~DatabaseConnection() // Finalizer (Destructor)
    {
        Dispose(false); // FAQAT unmanaged resurslar tozalanadi (managed obyektlar GC tomonidan ALLAQACHON tozalangan bo'lishi mumkin)
    }
}
```

```
Nima uchun Finalize() ISHONCHSIZ:
  ❌ QACHON chaqirilishi NOANIQ (GC o'z vaqtida ishga tushadi,
     DASTURCHI NAZORAT QILA OLMAYDI)
  ❌ Finalizer'ga EGA obyektlar — QO'SHIMCHA GC AYLANISHINI TALAB
     qiladi (birinchi collection'da FAQAT "finalization queue"ga
     o'tadi, XOTIRA DARHOL qaytarilmaydi!)
  ❌ Finalizer ICHIDA XATO — DASTURNI YIQITISHI mumkin

✅ Shuning uchun: Dispose() — ANIQ, DETERMINISTIK — Finalizer FAQAT
   "ZAXIRA" (agar dasturchi Dispose()ni CHAQIRISHNI UNUTGAN bo'lsa)
```

### 3.5 `using` statement — qisqa yo'l

```csharp
// Klassik using bloki
using (var connection = new NpgsqlConnection(connStr))
{
    connection.Open();
} // Blok TUGAGANDA — Dispose() AVTOMATIK chaqiriladi (hatto EXCEPTION bo'lsa ham!)

// C# 8+ — using declaration
using var connection = new NpgsqlConnection(connStr);
connection.Open();
// METOD (yoki BLOK) TUGAGANDA — Dispose() AVTOMATIK chaqiriladi
```

`using` — compiler tomonidan **try-finally**ga tarjima qilinadi:
```csharp
NpgsqlConnection connection = new NpgsqlConnection(connStr);
try
{
    connection.Open();
}
finally
{
    connection?.Dispose(); // HAR DOIM chaqiriladi, XATO bo'lsa HAM
}
```

### 3.6 `GC.Collect()` — nima uchun qo'lda chaqirmaslik kerak

```
❌ GC.Collect() — QO'LDA chaqirish:
  - GC'ning O'ZINI OPTIMALLASHTIRISH ALGORITMINI BUZADI (u ALLAQACHON
    ENG YAXSHI VAQTNI TANLAYDI)
  - QIMMAT operatsiya (Full GC — hatto Gen 2'ni HAM tekshiradi)
  - Obyektlar VAQTIDAN OLDIN Gen 2'ga "KO'TARILISHI" mumkin (agar
    ular hali HAM ISHLATILAYOTGAN bo'lsa)

✅ FAQAT juda MAXSUS holatlarda (masalan, KATTA hajmdagi vaqtinchalik
   ma'lumotni QAYTA ISHLAGANDAN KEYIN, aniq PROFILE qilingan bo'lsa)
```

### 3.7 `WeakReference` — GC'dan himoya QILMASLIK

```csharp
var strongRef = new Employee(); // GC "TIRIK" deb hisoblaydi
var weakRef = new WeakReference<Employee>(strongRef);

strongRef = null; // Endi HECH KIM "strong" ishora qilmaydi
GC.Collect();

if (weakRef.TryGetTarget(out var employee))
    Console.WriteLine("Hali TIRIK"); // GC hali YETIB KELMAGAN bo'lishi mumkin
else
    Console.WriteLine("GC tomonidan TOZALANGAN"); // Odatiy holat
```

`WeakReference` — obyektga ishora qiladi, LEKIN GC'ni uni
"tirik" deb hisoblashga **MAJBUR QILMAYDI** — cache implementatsiyalarida
foydali (kesh — GC bosimi ostida AVTOMATIK "bo'shashi" mumkin).

### 3.8 Memory Leak — .NET'da qanday yuzaga keladi

```csharp
// ❌ Klassik .NET memory leak — EVENT SUBSCRIPTION
public class ReportGenerator
{
    public ReportGenerator(EmployeeService service)
    {
        service.EmployeeCreated += OnEmployeeCreated; // ❌ Subscribe qildi, UNSUBSCRIBE QILMADI!
    }
    private void OnEmployeeCreated(object sender, EventArgs e) { }
}
```

```
Muammo: EmployeeService (Publisher) — ReportGenerator'ga (Subscriber)
"strong reference" SAQLAYDI (event orqali). Hatto ReportGenerator
BOSHQA HECH KIM tomonidan ISHLATILMASA HAM — EmployeeService uni
"TIRIK" deb SAQLAYDI (chunki EVENT HALI OBUNA QILINGAN) — bu
obyekt HECH QACHON GC qilinmaydi!

✅ Yechim: service.EmployeeCreated -= OnEmployeeCreated; (Dispose ichida)
```

### 3.9 `NpgsqlConnection`, `HttpClient` — nima uchun `using` kerak

```csharp
// NpgsqlConnection — UNMANAGED TCP socket'ni O'Z ICHIDA saqlaydi
using var connection = new NpgsqlConnection(connStr); // ✅ Dispose — connection pool'GA QAYTARADI

// HttpClient — Singleton bo'lishi kerak (using bilan HAR SO'ROVDA
// yaratish — Socket Exhaustion muammosiga olib keladi, alohida
// hujjatda batafsil)
```

## 4. Kod — to'liq Dispose Pattern

```csharp
public class FileProcessor : IDisposable
{
    private FileStream? _stream;
    private bool _disposed;

    public FileProcessor(string path) => _stream = new FileStream(path, FileMode.Open);

    public void Dispose()
    {
        if (_disposed) return;
        _stream?.Dispose();
        _disposed = true;
        GC.SuppressFinalize(this);
    }
}
```

## 5. Qachon ishlatish kerak?

| Vaziyat | Yechim |
|---|---|
| DB connection, fayl, socket | `IDisposable` implement qilish, `using` bilan ishlatish |
| Sinf obyektlarini yaratish/tozalash | GC'ga ISHONING, qo'lda `GC.Collect()` CHAQIRMANG |
| Cache implementatsiyasi | `WeakReference` |
| Event subscription | Dispose'da UNSUBSCRIBE qiling |

## 6. Muhim nuqtalar

- Finalizer — FAQAT unmanaged resurs to'g'ridan boshqarilganda (kam
  uchraydigan holat) kerak — ko'p klasslar UMUMAN Finalizer'ga
  MUHTOJ EMAS.
- `using` — EXCEPTION bo'lsa HAM Dispose() chaqirilishini
  KAFOLATLAYDI (try-finally'ga tarjima qilingani uchun).
- Event-based memory leak — .NET'da ENG KO'P uchraydigan "yashirin"
  leak turi.

## 7. Imtihon savollari

1. Mark-and-Sweep algoritmi qanday ishlaydi?
2. GC Generations (Gen 0, 1, 2) nima uchun mavjud?
3. Large Object Heap qanday muammoga (fragmentatsiya) olib kelishi
   mumkin?
4. Finalize() nima uchun "ishonchsiz" hisoblanadi?
5. `Dispose(bool disposing)` patternidagi `disposing` parametri
   nima uchun kerak?
6. `using` statement compiler tomonidan qanday konstruksiyaga
   tarjima qilinadi?
7. Event subscription qanday memory leak'ga olib kelishi mumkin?
8. `GC.Collect()`ni qo'lda chaqirish nima uchun tavsiya etilmaydi?
