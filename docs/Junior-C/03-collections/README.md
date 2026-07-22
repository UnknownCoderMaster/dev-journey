# Collections — Array, IEnumerable, IQueryable, ICollection, IList, List, LinkedList — Junior C

## 1. Nima?

**Collection** — bir nechta elementni saqlash, ular ustida iteratsiya
qilish va boshqarish uchun mo'ljallangan ma'lumot tuzilmalari majmuasi.

.NET da collection lar interfeys ierarxiyasi orqali quriladi: har bir
interfeys avvalgisiga qo'shimcha imkoniyat qo'shadi — bu **Interface
Segregation Principle** ning amaliy namunasi.

Asosiy o'yinchilar: `Array`, `List<T>`, `LinkedList<T>`, `Queue<T>`,
`Stack<T>`, `HashSet<T>`, `Dictionary<TKey,TValue>`, `IEnumerable<T>`,
`IQueryable<T>`.

## 2. Nima uchun kerak?

Har bir tuzilma **turlicha vazifani optimal bajaradi**:

```
Tez indeks kerak?           → Array / List<T>
Tez qidiruv (Contains) kerak? → HashSet<T> / Dictionary<TKey,TValue>
Ko'p marta o'rtaga qo'shish kerak? → LinkedList<T>
Navbat (birinchi kirgan — birinchi chiqadi)? → Queue<T>
Stek (oxirgi kirgan — birinchi chiqadi)? → Stack<T>
DB dan lazy, SQL ga tarjima qilinadigan so'rov kerak? → IQueryable<T>
Faqat oldinga iteratsiya, minimal interfeys kerak? → IEnumerable<T>
```

Agar noto'g'ri tuzilma tanlansa — ERP tizimida 100,000 xodim ro'yxatida
`Contains()` ni `List<T>` bilan chaqirish O(n), `HashSet<T>` bilan O(1) —
bu farq ishlab chiqarishda sezilarli lag beradi.

## 3. Ichida nima sodir bo'ladi? (Mexanizm)

### 3.1 Interfeys ierarxiyasi

```
IEnumerable<T>              ← Faqat GetEnumerator() — foreach uchun minimal shart
    │
    ├── ICollection<T>      ← + Count, Add, Remove, Contains, Clear
    │       │
    │       └── IList<T>    ← + indeks bilan kirish this[int], Insert, RemoveAt
    │               │
    │               ├── List<T>          ← dinamik array
    │               └── T[] (Array)      ← IList<T> ni implement qiladi, lekin hajmi FIX
    │
    └── IQueryable<T>       ← Expression<Func<T,bool>> — SQL ga tarjima qilinadigan so'rovlar (EF Core)
```

`ICollection<T>` — `IEnumerable<T>`dan meros oladi va **o'zgartirish**
imkoniyatini qo'shadi. `IList<T>` — bundan tashqari **tartib va indeks**
qo'shadi.

### 3.2 Array — contiguous memory, O(1) indeks

```csharp
int[] arr = new int[5];      // 5 ta int uchun UZLUKSIZ joy ajratiladi
int[] arr2 = { 10, 20, 30 };
```

```
Xotirada (contiguous — ketma-ket bitta blok):
Address:  1000  1004  1008  1012  1016
Value:    [10 ][20  ][30  ][ 0  ][ 0  ]
Index:     0     1     2     3     4
```

`arr[2]` ga murojaat qilish — CLR uchun oddiy arifmetika:
```
address = baseAddress + (index * elementSize)
        = 1000 + (2 * 4)
        = 1008
```

Shuning uchun indeks bilan o'qish **O(1)** — hech qanday qidiruv shart
emas, to'g'ridan manzil hisoblanadi.

**Array cheklovi:** hajmi yaratilgandan keyin **o'zgarmaydi**. Element
qo'shish/o'chirish kerak bo'lsa — yangi array yaratib, hammasini
ko'chirish kerak (`Array.Resize` ham ichida shuni qiladi).

### 3.3 List\<T\> — dinamik array, kapasita o'sishi

```csharp
var list = new List<int>();  // Default capacity = 0, birinchi Add()da 4 bo'ladi
list.Add(1); list.Add(2); list.Add(3); list.Add(4); // Capacity: 4, Count: 4
list.Add(5); // Capacity YETMAYDI!
```

```
Capacity 4 → to'ldi:
[1][2][3][4]

Add(5) chaqirilganda:
1. Yangi array yaratiladi — capacity 2x: 8 ta joy
2. Eski 4 ta element YANGI array ga ko'chiriladi (Array.Copy)
3. Eski array — Garbage Collector'ga topshiriladi
4. Yangi element (5) qo'shiladi

Natija: [1][2][3][4][5][ ][ ][ ]   Capacity: 8, Count: 5
```

`List<T>` ichida `T[] _items` massivi bor. `Add()` — agar joy bo'lsa
O(1) (amortized), joy tugasa — O(n) (nusxalash).

```csharp
// Performance: agar taxminiy hajm ma'lum bo'lsa — oldindan belgilash
var list = new List<int>(capacity: 100_000); // Qayta-qayta re-allocate bo'lmaydi

// Capacity vs Count farqi
Console.WriteLine(list.Count);    // Haqiqiy elementlar soni
Console.WriteLine(list.Capacity); // Ajratilgan (lekin ishlatilmagan bo'lishi mumkin) joy
```

`Insert(0, x)` — boshiga qo'shish — **O(n)**, chunki barcha elementlar
1 pozitsiyaga siljitilishi kerak.

### 3.4 IEnumerable\<T\> — lazy evaluation va `yield return`

```csharp
public IEnumerable<int> GetEvenNumbers(int max)
{
    for (int i = 0; i <= max; i += 2)
        yield return i; // "Pauza" — chaqiruvchi so'raganda davom etadi
}
```

`yield return` compiler tomonidan **state machine** ga aylantiriladi
(IL darajasida — bu yashirin klass, `IEnumerator<T>` implement qiladi,
`MoveNext()` ichida `switch(state)` orqali "qayerda to'xtagani"ni eslab
qoladi).

```
foreach (var n in GetEvenNumbers(1_000_000))
{
    if (n > 10) break; // Faqat 6 ta element hisoblanadi (0,2,4,6,8,10)!
}
```

```
❌ Agar List<int> qaytarilsa:
   BARCHA 500,000 ta juft son OLDINDAN hisoblanib, RAM ga yuklanadi

✅ yield return bilan:
   Har safar foreach "keyingisini" so'raganda, BITTA element hisoblanadi
   RAM da faqat "hozirgi holat" saqlanadi
```

### 3.5 IQueryable\<T\> — Expression Tree va DB da bajarilish

```csharp
// IEnumerable — .Where() DARHOL C# kodda ishlaydi
IEnumerable<Employee> e1 = _context.Employees.ToList()
    .Where(x => x.Age > 25);
// SQL: SELECT * FROM employees  (HAMMASI keladi, keyin C# da filtrlanadi!)

// IQueryable — .Where() Expression Tree ga QO'SHILADI, hali bajarilmagan
IQueryable<Employee> e2 = _context.Employees
    .Where(x => x.Age > 25);
// SQL hali yuborilmagan!

var result = e2.ToList(); // FAQAT shu yerda SQL generatsiya va yuboriladi:
// SQL: SELECT * FROM employees WHERE age > 25
```

```
IEnumerable<T>:
  .Where(x => x.Age > 25) → Func<T,bool> (compiled delegate, C# darajasida ishlaydi)

IQueryable<T>:
  .Where(x => x.Age > 25) → Expression<Func<T,bool>> (SINTAKSIS DARAXTI sifatida saqlanadi)
                          → EF Core Provider bu daraxtni SQL ga TARJIMA qiladi
                          → Faqat .ToList()/.First()/foreach chaqirilganda ijro etiladi
```

```
IEnumerable oqimi:  DB → BARCHA qatorlar → RAM → C# da filter (sekin, ko'p xotira)
IQueryable oqimi:   C# filter → SQL ga tarjima → DB da filter → faqat kerakli qatorlar (tez)
```

**EF Core'da eng ko'p uchraydigan xato:**

```csharp
// ❌ .ToList() ERTA chaqirilgan — IQueryable IEnumerable ga aylanadi
var emps = _context.Employees.ToList()          // Hammasi DB dan keladi!
    .Where(e => e.Department.Name == "IT")        // C# da filtrlanadi
    .ToList();

// ✅ .ToList() ENG OXIRIDA — filter DB da bajariladi
var emps = _context.Employees
    .Where(e => e.Department.Name == "IT")        // SQL WHERE ga tarjima
    .ToList();                                     // Faqat shu yerda so'rov yuboriladi
```

### 3.6 LinkedList\<T\> — doubly linked list

```csharp
var linked = new LinkedList<int>();
linked.AddLast(1);
linked.AddLast(2);
var node = linked.AddLast(3);
linked.AddAfter(node, 99);
```

```
Xotirada (har bir Node — Prev, Value, Next saqlaydi):

null ← [1] ⇄ [2] ⇄ [3] ⇄ [99] → null
        ↑                  ↑
       First               Last
```

`AddAfter(node, value)` — **O(1)**, chunki faqat 2-3 ta pointer
o'zgartiriladi (Array/List da bo'lsa — barcha keyingi elementlar
siljitilishi kerak edi — O(n)).

Ammo `linked[5]`— indeks bilan kirish **yo'q**! `LinkedList<T>` ni
n-chi elementga yetish uchun boshidan (yoki oxiridan) **O(n)** qadam
bosib o'tish kerak.

### 3.7 Queue\<T\> va Stack\<T\>

```csharp
// Queue — FIFO (First In, First Out)
var queue = new Queue<string>();
queue.Enqueue("birinchi");
queue.Enqueue("ikkinchi");
Console.WriteLine(queue.Dequeue()); // → "birinchi"

// Stack — LIFO (Last In, First Out)
var stack = new Stack<string>();
stack.Push("birinchi");
stack.Push("ikkinchi");
Console.WriteLine(stack.Pop()); // → "ikkinchi"
```

ERP misolida: `Queue<T>` — background job navbati (ariza ketma-ket
qayta ishlanadi); `Stack<T>` — "Undo" funksiyasi (oxirgi amal birinchi
bekor qilinadi).

### 3.8 HashSet\<T\> — hash table asosida O(1) Contains

```csharp
var ids = new HashSet<int> { 1, 2, 3 };
bool exists = ids.Contains(2); // O(1) — hash hisoblanadi, bucket topiladi
```

```
HashSet ichida — hash table:
hash(2) = bucket #4
bucket #4: [2] → to'g'ridan topiladi, ro'yxat bo'ylab qidirish shart emas

List<int> bilan Contains(2):
[1][2][3] → 1 emasmi? 2 emasmi? TOPILDI — lekin eng yomon holatda O(n)
```

Katta kolleksiyalarda (masalan, 50,000 ta xodim ID si ichidan
qidirish) `HashSet<int>` — `List<int>`dan sezilarli tezroq.

### 3.9 Dictionary\<TKey,TValue\> — key-value, hash collision

```csharp
var employees = new Dictionary<int, Employee>();
employees[1] = new Employee { Id = 1, Name = "Orzibek" };

if (employees.TryGetValue(1, out var emp))
    Console.WriteLine(emp.Name);
```

Ichida — massiv (bucket lar) + har bir key uchun hash hisoblanadi.
Agar ikkita turli key bir xil hash (bucket) ga tushsa — **hash
collision** — .NET buni **chained list** (yoki katta yuklamada
red-black tree, .NET Core 3+) orqali hal qiladi.

```
Dictionary ichida (soddalashtirilgan):

bucket[0] → (key=5,  value=Emp5)
bucket[1] → (key=1,  value=Emp1) → (key=17, value=Emp17)  ← collision zanjiri
bucket[2] → bo'sh
```

## 4. Kod — asosiy sintaksis

```csharp
// Array
int[] arr = new int[3] { 1, 2, 3 };
Array.Sort(arr);
Array.Reverse(arr);

// List<T>
var list = new List<Employee>();
list.Add(new Employee { Name = "Orzibek" });
list.AddRange(otherEmployees);
list.RemoveAll(e => e.Age < 18);
bool has = list.Any(e => e.Name == "Orzibek");

// IEnumerable — lazy, faqat foreach uchun minimal
IEnumerable<int> nums = list.Select(e => e.Age); // hali bajarilmagan (LINQ to Objects ham lazy)

// IQueryable — EF Core bilan real misol
public IQueryable<Employee> GetActiveEmployees()
    => _context.Employees
        .Where(e => e.IsActive)
        .Include(e => e.Department); // DB da JOIN + WHERE ga tarjima qilinadi

// yield return — o'ziniki iterator
public IEnumerable<Employee> GetEmployeesInBatches(int batchSize)
{
    int skip = 0;
    List<Employee> batch;
    do
    {
        batch = _context.Employees.Skip(skip).Take(batchSize).ToList();
        foreach (var e in batch)
            yield return e;
        skip += batchSize;
    } while (batch.Count == batchSize);
}

// ❌ NOTO'G'RI — IQueryable ni List ga aylantirib keyin filtrlash
var wrong = _context.Employees.ToList().Where(e => e.Age > 25);

// ✅ TO'G'RI — filtr DB darajasida
var right = _context.Employees.Where(e => e.Age > 25).ToList();
```

## 5. Qachon ishlatish kerak?

| Ehtiyoj | Tavsiya | Nima uchun |
|---|---|---|
| Hajm oldindan ma'lum, o'zgarmaydi | `Array` | Eng tez, eng kam xotira |
| Hajm dinamik, indeks kerak | `List<T>` | Universal, tez indeks |
| Ko'p marta o'rtaga qo'shish/o'chirish | `LinkedList<T>` | O(1) insert/delete o'rtada |
| Tez `Contains`/unikal elementlar | `HashSet<T>` | O(1) qidiruv |
| Key orqali qidiruv | `Dictionary<TKey,TValue>` | O(1) key lookup |
| FIFO navbat (job queue) | `Queue<T>` | Tabiiy semantika |
| LIFO (undo, recursion emulation) | `Stack<T>` | Tabiiy semantika |
| EF Core so'rovi, DB da filtr kerak | `IQueryable<T>` | SQL ga tarjima, kam RAM |
| Faqat iteratsiya, minimal kontrakt | `IEnumerable<T>` | Eng moslashuvchan API imzosi |

**Anti-patternlar:**

```csharp
// ❌ Public metod imzosida List<T> qaytarish — chaqiruvchi ichini o'zgartirishi mumkin
public List<Employee> GetEmployees() => _employees;

// ✅ IEnumerable<T> yoki IReadOnlyList<T> — inkapsulyatsiya saqlanadi
public IReadOnlyList<Employee> GetEmployees() => _employees.AsReadOnly();

// ❌ EF Core natijasini IEnumerable sifatida saqlab, keyin bir necha marta LINQ ishlatish
IEnumerable<Employee> emps = _context.Employees; // deferred execution!
var count = emps.Count();  // 1-marta SQL so'rov
var first = emps.First();  // 2-marta SQL so'rov (yana DB ga boradi!)

// ✅ .ToList() bilan bir marta materialize qilib, keyin xotirada ishlatish
var emps = _context.Employees.ToList();
var count = emps.Count; // RAM dan
var first = emps.First(); // RAM dan
```

## 6. Qo'shimcha — chuqur nuqtalar

- **`ICollection<T>` bilan `IReadOnlyCollection<T>`** — ikkinchisi faqat
  `Count` beradi, `Add`/`Remove` yo'q — API kontraktlarini qattiqroq
  belgilash uchun foydali.
- **`foreach` ichida kolleksiyani o'zgartirish** —
  `InvalidOperationException: Collection was modified` — chunki
  enumerator versiya raqamini kuzatadi (`_version` field).
  ```csharp
  foreach (var e in list)
      if (e.Age < 18) list.Remove(e); // ❌ Exception!
  // ✅ ToList() bilan nusxa olib, asl ustida amal bajarish:
  foreach (var e in list.ToList())
      if (e.Age < 18) list.Remove(e);
  ```
- **`Span<T>`** — zamonaviy .NET da array/list bo'lagini nusxasiz
  ishlatish, GC bosimini kamaytiradi (yuqori performance kod uchun).
- **C# versiyalaridagi o'zgarishlar:** `record`/`init` kolleksiya
  elementlarini immutable qilishni osonlashtirdi; `IAsyncEnumerable<T>`
  (C# 8) — `await foreach` bilan asinxron streaming.
- **Real loyihada uchraydigan xato:** `.Count()` (LINQ metodi, IQueryable
  uchun `SELECT COUNT(*)` SQL yuboradi) bilan `.Count` (property,
  `List<T>` uchun RAM dan darhol) ni chalkashtirish — ba'zida keraksiz
  qo'shimcha DB so'rovlariga olib keladi.

## 7. Imtihon savollari

1. `IEnumerable<T>`, `ICollection<T>` va `IList<T>` orasidagi ierarxik
   farqni tushuntiring — har biri qo'shimcha nima beradi?
2. `List<T>` kapasitesi tugaganda ichida qanday jarayon (qadamma-qadam)
   sodir bo'ladi?
3. `arr[2]` nega O(1) tezlikda ishlaydi — matematik jihatdan tushuntiring.
4. `IEnumerable` va `IQueryable` orasidagi eng muhim farq nima?
   EF Core kontekstida noto'g'ri tanlov qanday performance muammosiga
   olib kelishi mumkin?
5. `yield return` compiler tomonidan qanday mexanizmga aylantiriladi?
6. Nima uchun `HashSet<T>.Contains()` — `List<T>.Contains()` dan tezroq?
7. `LinkedList<T>` da element qo'shish O(1) bo'lsa ham, nima uchun uni
   har doim `List<T>` o'rniga ishlatib bo'lmaydi?
8. `foreach` davomida kolleksiyani o'zgartirsak nima sodir bo'ladi va
   nima uchun?
