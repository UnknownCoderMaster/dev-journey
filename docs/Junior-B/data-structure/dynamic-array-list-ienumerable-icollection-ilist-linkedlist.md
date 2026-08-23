# Dynamic Array — List, IEnumerable, ICollection, IList, LinkedList — Junior B

## 1. What (Nima?)

**Dynamic Array (dinamik massiv)** — oddiy massivdan farqli,
**hajmi runtime'da avtomatik o'sadigan** ma'lumot tuzilmasi. .NET'da
`List<T>` — dinamik massivning asosiy implementatsiyasi. `IEnumerable<T>`,
`ICollection<T>`, `IList<T>` — **abstraksiya darajasi** ortib
boruvchi interfeyslar ierarxiyasi. `LinkedList<T>` — massivga
MUQOBIL, **bog'langan tugunlar** (node) asosidagi tuzilma.

## 2. Real hayot analogiyasi

**Oddiy massiv — QATOR STULLI KINOTEATR ZALI.** Joylar SONI
OLDINDAN BELGILANGAN (masalan 100 ta) — KO'PROQ ODAM KELSA, YANGI
STUL QO'YISH UCHUN **BUTUN ZALNI QAYTA QURISH** kerak.

**`List<T>` (Dynamic Array) — "KENGAYUVCHAN" ZAL.** Zal TO'LGANDA,
ADMINISTRATSIYA **YANGI, KATTAROQ ZAL** TOPADI, BARCHA STULLARNI
(elementlarni) U YERGA KO'CHIRADI — TOMOSHABIN (dasturchi) BUNI
**SEZMAYDI HAM**, FAQAT `Add()` DEB AYTADI, QOLGANINI `List<T>`
O'ZI HAL QILADI.

**`LinkedList<T>` — POYEZD VAGONLARI.** Har VAGON (node) —
O'ZIDAN OLDINGI VA KEYINGI VAGONGA "ULANGAN" (pointer). Yangi
VAGON QO'SHISH — FAQAT IKKI ULANISHNI (link) O'ZGARTIRISH,
BOSHQA VAGONLARNI SILJITISH SHART EMAS — LEKIN "15-VAGONGA
TO'G'RIDAN O'TISH" (indeks bilan kirish) — HAR VAGONNI BIR-BIR
O'TIB, SANASH KERAK.

## 3. Why (Nega kerak?)

Oddiy massiv (`T[]`) — hajmi **O'ZGARMAS** (fixed-size) — element
QO'SHISH/O'CHIRISH kerak bo'lsa, **YANGI MASSIV** yaratib, HAMMA
NARSANI ko'chirish kerak edi. `List<T>` — bu **QO'LDA** qilinadigan
ishni **AVTOMATLASHTIRADI**, kapasita boshqaruvini ICHKI ravishda
o'ZI HAL QILADI (`docs/Junior-C/03-collections`da batafsil).

**Interfeys ierarxiyasi (`IEnumerable` → `ICollection` → `IList`)
nima uchun kerak:** METOD PARAMETRLARIDA, **ENG UMUMIY** (kam
talab qiluvchi) interfeysni ISHLATISH — CHAQIRUVCHI KODGA **KO'PROQ
MOSLASHUVCHANLIK** BERADI (masalan, `IEnumerable<T>` qabul
qiluvchi metod — `List<T>`, `T[]`, `HashSet<T>` — BARCHASI BILAN
ISHLAYDI).

## 4. Internals (Ichki mexanizm)

### Interfeys ierarxiyasi

```
IEnumerable<T>           ← ENG ASOSIY — FAQAT foreach (GetEnumerator())
    │
    ├── ICollection<T>   ← + Count, Add, Remove, Contains, Clear
    │       │
    │       └── IList<T> ← + INDEKS orqali kirish (this[int]), Insert, RemoveAt
    │               │
    │               └── List<T> ← KONKRET IMPLEMENTATSIYA
```

Batafsil: `docs/Junior-C/03-collections`da.

### `List<T>` — kapasita o'sish MEXANIZMI (2x strategiya)

```
List<T> ICHIDA — T[] massiv SAQLANADI:

Boshlang'ich Add() — Capacity: 0 → 4
4 element TO'LGANDA, 5-Add() chaqirilsa:
  1. YANGI massiv YARATILADI — Capacity 2X (4 → 8)
  2. ESKI 4 element YANGI massivga KO'CHIRILADI (Array.Copy — O(n))
  3. ESKI massiv — Garbage Collector'GA TOPSHIRILADI
  4. YANGI element QO'SHILADI

Bu — AMORTIZED O(1) — HAR Add() O'RTACHA O(1), LEKIN VAQTI-VAQTI
BILAN (kapasita to'lganda) O(n) "QIMMAT" OPERATSIYA SODIR BO'LADI.
```

```csharp
var list = new List<int>(capacity: 10_000); // OLDINDAN JOY AJRATISH — QAYTA-QAYTA "RESIZE" NI OLDINI OLADI
```

### `LinkedList<T>` — DOUBLY LINKED LIST tuzilishi

```
Har TUGUN (LinkedListNode<T>) — 3 QISMDAN IBORAT:
  Previous (oldingi tugunga POINTER)
  Value (qiymat)
  Next (keyingi tugunga POINTER)

null ← [A] ⇄ [B] ⇄ [C] → null
        ↑              ↑
      First           Last
```

```
AddAfter(node, value) — O(1) — FAQAT 2-3 TA POINTER O'ZGARTIRILADI

LEKIN linkedList[5] — INDEKS orqali kirish YO'Q! N-CHI elementga
YETISH uchun — BOSHIDAN (yoki OXIRIDAN) BOSHLAB, N MARTA
"Next"/"Previous" ORQALI O'TISH KERAK — O(n).
```

### Xotira jihatidan solishtirish — MUHIM FARQ

```
List<T> (Array asosida):
  - Elementlar — XOTIRADA KETMA-KET (contiguous) joylashadi
  - CPU CACHE-FRIENDLY (bir elementga kirish — YAQINDAGI
    elementlarni HAM CACHE'GA "OLIB KELADI" — Spatial Locality)

LinkedList<T>:
  - Har TUGUN — XOTIRADA ALOHIDA JOYDA (Heap'da TARQOQ)
  - HAR TUGUN — QO'SHIMCHA 16-24 BAYT (Previous/Next pointer +
    obyekt header) XOTIRA "OVERHEAD"IGA EGA
  - CACHE-UNFRIENDLY — HAR "Next" — YANGI XOTIRA SAHIFASIGA
    "SAKRASH" bo'lishi MUMKIN (CACHE MISS)
```

```
⚠️ AMALIYOTDA: List<T> — HATTO O'RTAGA QO'SHISH/O'CHIRISH KERAK
   bo'lgan HOLATLARDA HAM, KICHIK-O'RTA hajmli kolleksiyalarda,
   CACHE-FRIENDLY TABIATI TUFAYLI, LinkedList<T>'dan KO'PINCHA
   TEZROQ ISHLAYDI (Big O NAZARIYASI — HAQIQIY, O'LCHANGAN
   PERFORMANCE'NI DOIM TO'G'RI AKS ETTIRMAYDI).
```

## 5. Code (Amaliy kod)

```csharp
// List<T> — asosiy AMALIYOT
var employees = new List<Employee>(capacity: 100);
employees.Add(new Employee { Id = 1, FullName = "Orzibek" });
employees.Insert(0, new Employee { Id = 0, FullName = "Boshqa" }); // O(n) — SILJISH KERAK
employees.RemoveAt(0); // O(n)

// Interfeys — KAM TALAB QILUVCHI PARAMETR (KO'PROQ moslashuvchanlik)
public void PrintAll(IEnumerable<Employee> employees) // List, Array, HashSet — HAMMASI ISHLAYDI
{
    foreach (var e in employees)
        Console.WriteLine(e.FullName);
}

public void AddIfNotExists(ICollection<Employee> employees, Employee emp) // Add, Contains KERAK
{
    if (!employees.Contains(emp))
        employees.Add(emp);
}

public Employee GetFirst(IList<Employee> employees) => employees[0]; // INDEKS KERAK
```

```csharp
// LinkedList<T> — o'RTAGA TEZ QO'SHISH kerak bo'lgan holat (masalan navbat/tarix)
var recentActions = new LinkedList<string>();
recentActions.AddFirst("Login qilindi");
recentActions.AddLast("Xodim qo'shildi");
var node = recentActions.AddAfter(recentActions.First!, "Parol o'zgartirildi"); // O(1)

foreach (var action in recentActions)
    Console.WriteLine(action);
```

```csharp
// Generic Repository — ICollection<T> ABSTRAKSIYASI orqali
public interface IEmployeeCache
{
    ICollection<Employee> GetAll();
}

public class InMemoryEmployeeCache : IEmployeeCache
{
    private readonly List<Employee> _employees = new();
    public ICollection<Employee> GetAll() => _employees; // List<T> — ICollection<T>NI IMPLEMENT QILADI
}
```

## 6. Keng tarqalgan xatolar / noto'g'ri tushunchalar

```
❌ "LinkedList<T> — HAR DOIM List<T>dan TEZROQ, chunki O(1)
   insert" — FAQAT NAZARIY. AMALIYOTDA, CACHE LOCALITY TUFAYLI,
   List<T> KO'PINCHA TEZROQ, HATTO O'RTAGA QO'SHISHDA HAM (agar
   kolleksiya JUDA KATTA EMAS bo'lsa).

❌ "IEnumerable<T> parametrini metod ICHIDA BIR NECHTA MARTA
   ITERATSIYA QILISH XAVFSIZ" — AGAR bu — LAZY (deferred
   execution) LINQ SO'ROVI bo'lsa, HAR ITERATSIYA — QAYTA
   BAJARILISHI mumkin (masalan, EF Core'da — QAYTA DB SO'ROVI!).

❌ "List<T>.Capacity — Count BILAN BIR XIL" — YO'Q! Capacity —
   AJRATILGAN (LEKIN HAMMASI ISHLATILMAGAN BO'LISHI mumkin) JOY,
   Count — HAQIQIY ELEMENTLAR SONI.

❌ "Array (T[])ni List<T>ga AYLANTIRISH — QIMMAT OPERATSIYA
   emas" — `ToList()` — YANGI massiv YARATIB, BARCHA elementlarni
   NUSXALAYDI (O(n)) — TSIKL ICHIDA QAYTA-QAYTA chaqirilsa,
   PERFORMANCE MUAMMOSIGA olib kelishi mumkin.

❌ "IList<T> — HAR DOIM List<T>ga TENG" — YO'Q! `T[]` (Array) HAM
   `IList<T>`NI IMPLEMENT QILADI, LEKIN `Add()`/`Remove()` CHAQIRILSA
   — `NotSupportedException` TASHLAYDI (hajmi O'ZGARMAS BO'LGANI
   uchun).
```

## 7. Exam (Interview savollari)

**1. `List<T>`ning kapasita O'SISH MEXANIZMI (2x strategiyasi)
QANDAY ISHLAYDI, va u NIMA UCHUN "AMORTIZED O(1)" deb ATALADI?**
Kapasita TO'LGANDA — YANGI, 2 BARAVAR KATTA massiv YARATILADI,
BARCHA elementlar KO'CHIRILADI (O(n)). LEKIN bu — KAMDAN-KAM
sodir bo'ladi (HAR 2X o'sishda BIR MARTA) — shuning uchun N ta
Add() operatsiyasining O'RTACHA (AMORTIZED) VAQTI — O(1) bo'lib
CHIQADI (garchi AYRIM Add() chaqiruvlar O(n) bo'lsa ham).

**2. `IEnumerable<T>`, `ICollection<T>`, `IList<T>` orasidagi
IERARXIK farqni TUSHUNTIRING.**
`IEnumerable<T>` — FAQAT ITERATSIYA (`GetEnumerator()`).
`ICollection<T>` — + `Count`, `Add`, `Remove`, `Contains`.
`IList<T>` — + INDEKS orqali kirish (`this[int]`), `Insert`,
`RemoveAt`. Har KEYINGI interfeys — OLDINGISIDAN MEROS OLADI VA
QO'SHIMCHA IMKONIYAT BERADI.

**3. `LinkedList<T>`da element QO'SHISH O(1) bo'lsa-yu, NIMA
UCHUN AMALIYOTDA `List<T>` KO'PINCHA TEZROQ ISHLAYDI?**
`List<T>` — XOTIRADA KETMA-KET (contiguous) JOYLASHADI — bu, CPU
CACHE'NI SAMARALI ISHLATADI (Spatial Locality). `LinkedList<T>`da
— HAR TUGUN XOTIRADA TARQOQ — HAR "Next" — CACHE MISS'GA olib
kelishi mumkin — bu, Big O NAZARIYASIDA KO'RINMAYDIGAN, LEKIN
HAQIQIY PERFORMANCE'GA TA'SIR QILUVCHI OMIL.

**4. Metod parametrida `IEnumerable<T>` o'RNIGA `List<T>`
ISHLATISH — QANDAY CHEKLOVGA OLIB KELADI?**
`List<T>` — CHAQIRUVCHI KODNI, FAQAT `List<T>` (yoki UNDAN MEROS
OLGAN TUR) UZATISHGA MAJBUR QILADI — `T[]`, `HashSet<T>`, LINQ
NATIJASI (`IEnumerable<T>`) UZATISH UCHUN, QO'SHIMCHA `.ToList()`
CHAQIRISH KERAK BO'LADI (KERAKSIZ NUSXALASH — PERFORMANCE
YO'QOTISH).

**5. `Array` (`T[]`) `IList<T>`ni IMPLEMENT QILADI, LEKIN NIMA
UCHUN `array.Add()` CHAQIRIB BO'LMAYDI?**
`T[]` — HAJMI O'ZGARMAS (FIXED-SIZE) tuzilma. `IList<T>`
INTERFEYSINING `Add()`/`Remove()` METODLARI — Array TOMONIDAN
IMPLEMENT QILINGAN, LEKIN ICHKARIDA `NotSupportedException`
TASHLAYDI, CHUNKI ARRAY HAJMINI O'ZGARTIRISH — TIL/RUNTIME
DARAJASIDA MUMKIN EMAS.
