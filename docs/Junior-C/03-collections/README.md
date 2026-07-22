# Collections — Array, IEnumerable, IQueryable, List, LinkedList — Junior C

## 1. Nima?

**Collection** — bir nechta elementni saqlash va ular ustida amal
bajarish uchun mo'ljallangan ma'lumot tuzilmalari.

## 2. Ierarxiya

```
IEnumerable<T>           ← eng asosiy — faqat foreach
    │
    ├── ICollection<T>   ← Count, Add, Remove, Contains
    │       │
    │       └── IList<T> ← indeks orqali [i], Insert
    │               │
    │               └── List<T> ← eng ko'p ishlatiladigan
    │
    └── IQueryable<T>    ← DB so'rovlari uchun (EF Core)
```

## 3. Ichida nima sodir bo'ladi?

### Array — o'zgarmas hajm, tez

```csharp
int[] arr = new int[5];    // 5 ta element, hajm o'zgarmaydi
int[] arr2 = { 1, 2, 3 }; // Initsializatsiya
```

```
Xotirada: [1][2][3][4][5]
           0   1   2   3   4  ← indeks
```

Array — **contiguous memory** (ketma-ket xotira bloki).
`arr[2]` → `baseAddress + 2 * sizeof(int)` — O(1) tezlik.

### List<T> — dinamik massiv

```csharp
var list = new List<int>();
list.Add(1);       // O(1) — oxiriga qo'shish
list.Add(2);
list.Insert(0, 99); // O(n) — boshiga qo'shish (barchani siljitadi)
```

List ichida — **array** saqlanadi. Kapasitesi tugasa:

```
Boshlang'ich kapasita: 4
[1][2][3][4] → to'ldi!
→ Yangi array (8 ta) yaratiladi
→ Eski elementlar ko'chiriladi
→ Eski array GC ga topshiriladi
```

Kapasiteni oldindan belgilash (performance uchun):
```csharp
var list = new List<int>(capacity: 1000); // Qayta allocate yo'q
```

### IEnumerable<T> — faqat iterate

```csharp
IEnumerable<int> nums = new List<int> { 1, 2, 3 };

foreach (var n in nums)  // ✅ foreach mumkin
    Console.WriteLine(n);

// nums[0]   ❌ indeks yo'q
// nums.Add() ❌ Add yo'q
```

`IEnumerable` — eng minimal interfeys. Faqat `GetEnumerator()` metodi bor.

### IQueryable<T> — DB so'rovlari uchun

```csharp
// IEnumerable — barcha ma'lumot xotiraga olinadi, keyin filter
IEnumerable<Employee> emps = _context.Employees
    .Where(e => e.Age > 25); // SQL: SELECT * — hammasi keladi!

// IQueryable — filter DB da bajariladi
IQueryable<Employee> emps = _context.Employees
    .Where(e => e.Age > 25); // SQL: SELECT * WHERE age > 25
```

```
IEnumerable: Barcha data → RAM → filter (sekin, ko'p xotira)
IQueryable:  Filter → DB da → faqat natija (tez, kam xotira)
```

### LinkedList<T> — bog'liq ro'yxat

```csharp
var linked = new LinkedList<int>();
linked.AddFirst(1);               // O(1)
linked.AddLast(2);                // O(1)
linked.AddAfter(linked.First, 99); // O(1)
```

```
Xotirada: [1|→][99|→][2|null]
           ↑
           First
```

LinkedList — har bir element **keyingisiga pointer** saqlaydi.
O'rtaga qo'shish O(1) — lekin indeks bilan O(n).

## 4. Qiyoslashtirma jadvali

| | Array | List<T> | LinkedList<T> |
|---|---|---|---|
| Hajm | O'zgarmas | Dinamik | Dinamik |
| Indeks [i] | O(1) | O(1) | O(n) |
| Oxiriga qo'shish | ❌ | O(1) | O(1) |
| O'rtaga qo'shish | ❌ | O(n) | O(1) |
| Xotira | Kam | O'rtacha | Ko'p (pointer lar) |

## 5. Kod — amalda

```csharp
// IEnumerable vs IQueryable — ERP da
public IQueryable<Employee> GetActive()
    => _context.Employees.Where(e => e.IsActive); // DB da filter ✅

public IEnumerable<Employee> GetActiveWrong()
    => _context.Employees.ToList().Where(e => e.IsActive); // Hammani yuklab filter ❌

// yield return — lazy IEnumerable
public IEnumerable<int> GetEven(int max)
{
    for (int i = 0; i <= max; i += 2)
        yield return i; // Bitta-bitta, hammasi xotiraga yuklanmaydi
}
```

## 6. Qo'shimcha nuqtalar

- **`ICollection<T>`** — `Count`, `Add`, `Remove`, `Contains` qo'shadi.
- **`yield return`** — Lazy evaluation, katta kolleksiyalar uchun
  xotira tejaydi.
- **`Capacity` vs `Count`** — `List` da `Capacity` — ajratilgan joy,
  `Count` — haqiqiy elementlar soni.
- **`ReadOnlyCollection<T>`** — o'qish uchun mo'ljallangan wrapper.
- **`ArraySegment<T>`** — array ning bir qismiga pointer, nusxa olmaydi.

## 7. Imtihon savollari

1. `IEnumerable` va `IQueryable` orasidagi asosiy farq nima?
   EF Core da qaysi biri to'g'ri va nima uchun?
2. `List<T>` kapasitesi tugaganda ichida nima sodir bo'ladi?
3. Qachon `LinkedList` ni `List` dan afzal ko'rasiz?
4. `yield return` nima va nima uchun ishlatiladi?
5. `arr[2]` nega O(1) tezlikda ishlaydi?
