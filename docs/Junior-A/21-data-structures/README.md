# Dictionary, IDictionary, Hashtable, Key-Value Structures — Junior A

## 1. Nima? (Ta'rif)

**Dictionary<TKey, TValue>** — **hash table** asosida qurilgan,
key-value juftliklarini saqlovchi generic kolleksiya, **O(1)**
o'rtacha vaqtda qidiruv/qo'shish/o'chirish imkonini beradi.

## 2. Nima uchun kerak?

`List<T>`da element qidirish — **O(n)** (har elementni tekshirish).
Dictionary — **hash function** yordamida to'g'ridan kerakli
"bucket"ga o'tib, **deyarli konstant vaqt**da topadi — katta
ma'lumot to'plamlarida bu farq **muhim**.

## 3. Ichida nima sodir bo'ladi? (Mexanizm)

### 3.1 Hash table asosida — O(1) o'rtacha, O(n) worst case

```
Dictionary ICHIDA — MASSIV (bucket'lar) + HASH FUNKSIYA:

dict["Orzibek"] = 25;

1. hash("Orzibek") HISOBLANADI (masalan → 47)
2. 47 % bucketCount = BUCKET INDEKS (masalan 7)
3. bucket[7]'ga (Key="Orzibek", Value=25) YOZILADI

dict["Orzibek"] O'QISH:
1. hash("Orzibek") = 47 → bucket[7]
2. bucket[7] ICHIDAGI key'larni SOLISHTIRISH (odatda 1 ta, TEZ)
```

```
O(1) — O'RTACHA holatda (hash YAXSHI TARQALGAN bo'lsa)
O(n) — ENG YOMON holatda (BARCHA key'lar BIR XIL bucket'ga
        TUSHSA — COLLISION zanjiri UZUN bo'lib qoladi)
```

### 3.2 Add, TryGetValue, ContainsKey, Remove

```csharp
var employees = new Dictionary<int, Employee>();

employees.Add(1, new Employee { Id = 1, FullName = "Orzibek" });
employees[2] = new Employee { Id = 2, FullName = "Dilnoza" }; // Indexer — Add YOKI Update

if (employees.TryGetValue(1, out var emp)) // ✅ TAVSIYA ETILADI — Exception TASHLAMAYDI
    Console.WriteLine(emp.FullName);

bool exists = employees.ContainsKey(1);
employees.Remove(1);

// ❌ employees[999] — agar KEY YO'Q bo'lsa — KeyNotFoundException!
```

### 3.3 Iteration — `foreach (var kvp in dict)`

```csharp
foreach (var kvp in employees)
    Console.WriteLine($"{kvp.Key}: {kvp.Value.FullName}");

foreach (var key in employees.Keys) { }
foreach (var value in employees.Values) { }
```

### 3.4 Capacity va Load Factor

```
Load Factor = elementlar soni / bucket soni

Load Factor JUDA YUQORI bo'lsa (masalan 1.0+) — COLLISION ehtimoli
OSHADI, PERFORMANCE YOMONLASHADI.

.NET Dictionary — AVTOMATIK "RESIZE" qiladi (bucket sonini
oshiradi) — LOAD FACTOR ma'lum chegaradan OSHSA.

Optimal: agar hajmi OLDINDAN MA'LUM bo'lsa —
new Dictionary<int, Employee>(capacity: 10000) — QAYTA-QAYTA
RESIZE'ni OLDINI OLADI (performance foyda).
```

### 3.5 Hash collision — chaining vs open addressing

```
Chaining (.NET Dictionary ISHLATADI):
  Bir XIL bucket'ga TUSHGAN elementlar — BOG'LANGAN RO'YXAT (yoki
  massiv) sifatida SAQLANADI

Open Addressing (BOSHQA implementatsiyalarda):
  Collision bo'lsa — KEYINGI BO'SH bucket'ni QIDIRADI ("probing")

.NET Dictionary<TKey,TValue> — ICHKARIDA "SEPARATE CHAINING"ga
O'XSHASH struktura (massiv + "next" indeks) ishlatadi — bu, .NET
Core 3+ da PERFORMANCE uchun OPTIMALLASHTIRILGAN.
```

### 3.6 `IDictionary<TKey, TValue>` — interfeys

```csharp
public void ProcessEmployees(IDictionary<int, Employee> employees) // Abstraksiya — Dictionary, SortedDictionary va h.k. QABUL qiladi
{
    foreach (var kvp in employees) { }
}
```

### 3.7 `Hashtable` — eski, non-generic

```csharp
Hashtable table = new Hashtable(); // ❌ ESKI (.NET 1.0 dan), non-generic
table.Add("key", 42); // object'ga BOXING/CAST kerak, TYPE SAFETY YO'Q

int value = (int)table["key"]; // CAST SHART!
```

```
Dictionary<object, object> va Hashtable — funksional jihatdan
O'XSHASH, LEKIN Dictionary — GENERIC (type-safe, boxing YO'Q),
Hashtable — thread-safe EMAS (ko'p threadli muhitda XAVFSIZ EMAS,
garchi ba'zi hujjatlar "READER-writer" holatida xavfsiz DEB
YOZSA HAM — zamonaviy kodlarda ISHLATILMASLIGI TAVSIYA ETILADI).
```

### 3.8 `ConcurrentDictionary` — thread-safe

```csharp
var cache = new ConcurrentDictionary<int, Employee>();

cache.AddOrUpdate(1,
    id => new Employee { Id = id },           // Agar YO'Q bo'lsa — YARATISH
    (id, existing) => existing);                // Agar BOR bo'lsa — YANGILASH (yoki QAYTARISH)

var employee = cache.GetOrAdd(1, id => LoadFromDb(id)); // Agar YO'Q bo'lsa — YARATIB, QAYTARADI
```

```
ConcurrentDictionary — ICHKARIDA "LOCK-FREE" (yoki FINE-GRAINED
lock) mexanizm ISHLATADI — bir nechta THREAD PARALLEL o'qish/yozish
qilganda, BUTUN Dictionary'ni QULFLASH O'RNIGA, FAQAT tegishli
BUCKET'ni QULFLAYDI (yoki umuman qulflashsiz, atomic operatsiyalar
orqali) — bu, oddiy Dictionary + lock'dan TEZROQ.
```

### 3.9 `SortedDictionary`, `SortedList`

```csharp
var sortedDict = new SortedDictionary<int, string>(); // BST (Binary Search Tree) asosida, O(log n)
var sortedList = new SortedList<int, string>();         // Massiv asosida, XOTIRA KAM, LEKIN INSERT O(n)
```

```
SortedDictionary — TEZ INSERT/DELETE (O(log n)), lekin XOTIRA
                    KO'PROQ (har NODE — qo'shimcha pointer)
SortedList        — XOTIRA KAM (massiv), lekin INSERT/DELETE SEKIN
                     (O(n) — elementlarni SILJITISH kerak)

Ikkalasi HAM — KEY bo'yicha TARTIBLANGAN holda ITERATSIYA qilish
imkonini beradi (oddiy Dictionary — TARTIB KAFOLATLANMAYDI!).
```

### 3.10 Qachon Dictionary vs List vs HashSet

```
Dictionary<K,V> — KEY orqali TEZ qidiruv, VA qiymat SAQLASH kerak
HashSet<T>       — FAQAT UNIKAL elementlar, qiymat SAQLASH KERAK EMAS
List<T>          — TARTIB muhim, INDEKS orqali kirish, KICHIK hajm
```

### 3.11 Custom `GetHashCode()` va `Equals()` override

```csharp
public class EmployeeKey
{
    public int DepartmentId { get; set; }
    public string Code { get; set; } = null!;

    public override bool Equals(object? obj)
        => obj is EmployeeKey other && DepartmentId == other.DepartmentId && Code == other.Code;

    public override int GetHashCode() => HashCode.Combine(DepartmentId, Code); // .NET built-in KOMBINATSIYA
}

var dict = new Dictionary<EmployeeKey, Employee>(); // Custom KEY sifatida ISHLATISH uchun IKKALASI HAM MAJBURIY!
```

```
⚠️ MUHIM QOIDA: Agar `Equals()` OVERRIDE qilinsa, `GetHashCode()`
   HAM OVERRIDE qilinishi SHART! Aks holda — Dictionary/HashSet
   NOTO'G'RI ishlaydi (ikki "TENG" obyekt — TURLI hash olib,
   TURLI bucket'ga TUSHISHI mumkin, va Dictionary ularni "TOPA
   OLMAYDI").
```

## 4. Kod — real ERP misolida Dictionary

```csharp
// Xodimlarni ID bo'yicha TEZ qidirish uchun keshlash
public class EmployeeCache
{
    private readonly Dictionary<int, Employee> _cache = new();

    public void Load(List<Employee> employees)
    {
        foreach (var emp in employees)
            _cache[emp.Id] = emp; // O(1) qo'shish
    }

    public Employee? GetById(int id) => _cache.TryGetValue(id, out var emp) ? emp : null; // O(1) qidiruv
}
```

## 5. Qachon ishlatish kerak?

| Vaziyat | Yechim |
|---|---|
| Key orqali tez qidiruv | `Dictionary<K,V>` |
| Ko'p thread'dan parallel kirish | `ConcurrentDictionary<K,V>` |
| Key bo'yicha tartiblangan iteratsiya | `SortedDictionary`/`SortedList` |
| Faqat unikal elementlar (qiymatsiz) | `HashSet<T>` |
| Tartib muhim, indeks orqali kirish | `List<T>` |

## 6. Muhim nuqtalar

- `dict[key]` — key mavjud bo'lmasa `KeyNotFoundException` tashlaydi
  — `TryGetValue` **doim** xavfsizroq.
- `Hashtable` — zamonaviy kodda ishlatilmasligi kerak, `Dictionary<K,V>`
  har doim afzal.
- Custom key klassida `Equals`/`GetHashCode` — **birga** override
  qilinishi SHART.

## 7. Imtihon savollari

1. Dictionary ichida hash collision qanday hal qilinadi (chaining)?
2. `dict[key]` va `TryGetValue` orasidagi farq nima?
3. `Hashtable` va `Dictionary<K,V>` orasidagi asosiy farqlar
   nimalar?
4. `ConcurrentDictionary` oddiy Dictionary + lock'dan qanday
   farq qiladi (performance nuqtai nazaridan)?
5. `SortedDictionary` va `SortedList` orasidagi tradeoff nima?
6. Custom key klassida `Equals()` override qilinsa, nima uchun
   `GetHashCode()` ham override qilinishi SHART?
7. Qachon `Dictionary`, qachon `HashSet` ishlatiladi?
