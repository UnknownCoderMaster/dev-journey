# Nullable — Value/Reference Types, `??`, `?.`, `!`, `null!`, `default!` — Junior C

## 1. Nima?

**Nullable** — o'zgaruvchi `null` (qiymat yo'qligi) holatini qabul
qila olishini bildiruvchi mexanizm. C# da ikkita mustaqil tizim bor:

1. **Nullable Value Types** (`int?`, `bool?` va h.k.) — `Nullable<T>`
   struct asosida, **runtime**da haqiqiy null tekshiruvi qiladi.
2. **Nullable Reference Types (NRT, C# 8+)** — `string?` va h.k. —
   faqat **compile-time**da ogohlantirish beradi, runtime da hech
   qanday qo'shimcha tekshiruv YO'Q.

## 2. Nima uchun kerak?

`int`, `bool`, `struct` — Value type lar **hech qachon null bo'la
olmaydi** (Stack da har doim qandaydir qiymat bor). Lekin real hayotda
"qiymat yo'q" holatini ifodalash kerak: xodimning ish tashlab ketgan
sanasi, ixtiyoriy yosh maydoni.

`string`, `class` — Reference type lar **har doim** null bo'la oladi —
bu esa `NullReferenceException` ning eng ko'p uchraydigan sababi.
NRT (C# 8+) bu xatoni **compile-time**da oldindan ko'rsatishga yordam
beradi.

Agar bular bo'lmaganida:
```
❌ int Age; // Ixtiyoriy maydonni ifodalash uchun -1 yoki 0 kabi "sehrli qiymat" ishlatish kerak bo'lardi
❌ Har bir string ishlatishdan oldin qo'lda if (x != null) yozish, compiler yordam bermaydi
```

## 3. Ichida nima sodir bo'ladi? (Mexanizm)

### 3.1 `Nullable<T>` — ichki tuzilishi

```csharp
int? age = 25;
```

Bu aslida:

```csharp
Nullable<int> age = new Nullable<int>(25);
```

`Nullable<T>` — **struct** (Value type!), ikkita fielddan iborat:

```csharp
public struct Nullable<T> where T : struct
{
    private readonly bool hasValue; // HasValue
    private readonly T value;       // Value (agar hasValue == false bo'lsa — default(T))

    public bool HasValue => hasValue;
    public T Value => hasValue ? value : throw new InvalidOperationException("Nullable object must have a value.");
}
```

```
Stack:
┌──────────────────────┐
│ int? age              │
│  ├─ hasValue: true    │
│  └─ value: 25         │
└──────────────────────┘

int? age2 = null;
┌──────────────────────┐
│ int? age2             │
│  ├─ hasValue: false   │
│  └─ value: 0 (default)│  ← "0" saqlanadi, lekin HasValue false bo'lgani uchun e'tiborga olinmaydi
└──────────────────────┘
```

Muhim: `int?` — **struct** bo'lgani uchun Stack'da yashaydi (agar u
mahalliy o'zgaruvchi bo'lsa) — `string`dek Heap'ga muhtoj emas.

```csharp
int? age = null;
if (age.HasValue)
    Console.WriteLine(age.Value);
else
    Console.WriteLine("Yosh kiritilmagan");

Console.WriteLine(age.GetValueOrDefault());   // → 0 (agar null bo'lsa)
Console.WriteLine(age.GetValueOrDefault(18)); // → 18 (default qiymat ko'rsatilgan)
```

### 3.2 Boxing va Nullable\<T\> — maxsus xatti-harakat

```csharp
int? x = null;
object obj = x;              // BOXING — lekin natija oddiy emas!
Console.WriteLine(obj == null); // → TRUE! (Nullable<int> emas, to'g'ridan null)

int? y = 5;
object obj2 = y;              // BOXING
Console.WriteLine(obj2.GetType()); // → System.Int32 (Nullable<int> EMAS!)
```

CLR maxsus qoida qo'yadi: `Nullable<T>` box qilinganda —
- agar `HasValue == false` → natija `null` reference
- agar `HasValue == true` → faqat **T** (ichidagi qiymat) box qilinadi,
  `Nullable<T>` emas

Bu — "Nullable<T> — reference typelar bilan mos yozishmalar
uchun maxsus CLR qo'llab-quvvatlashi" deb ataladi.

### 3.3 Nullable Reference Types (NRT, C# 8+) — faqat compile-time

```csharp
#nullable enable

string name = null;   // ⚠️ CS8600 ogohlantirish — "non-nullable" ga null berilyapti
string? name2 = null;  // ✅ Aniq — bu null bo'lishi mumkinligini bildiradi

void Print(string s) { Console.WriteLine(s.Length); }
Print(name2); // ⚠️ CS8604 ogohlantirish — null bo'lishi mumkin bo'lgan argument
```

**MUHIM:** NRT — bu faqat **static analysis** (compile-time). Runtime
da hech qanday farq yo'q — `string` va `string?` bir xil IL kodga
compile bo'ladi! Bu — `int?`dan farqli o'laroq, IL/runtime darajasida
HECH QANDAY qo'shimcha tekshiruv qo'shmaydi:

```csharp
string? s = null;
Console.WriteLine(s.Length); // Compiler ogohlantiradi, LEKIN compile bo'ladi
                              // Runtime da: 💥 NullReferenceException!
```

`.csproj` da yoqiladi:
```xml
<Nullable>enable</Nullable>
```

## 4. Kod — asosiy sintaksis

### `??` — Null coalescing

```csharp
string? name = null;
string result = name ?? "Noma'lum"; // → "Noma'lum"

// Zanjirlash — birinchi null bo'lmagan qiymat qaytariladi
string? a = null, b = null, c = "topildi";
string r = a ?? b ?? c ?? "hech biri topilmadi"; // → "topildi"
```

### `??=` — Null coalescing assignment (C# 8+)

```csharp
string? name = null;
name ??= "Default"; // Faqat null bo'lsa o'rnatadi
Console.WriteLine(name); // → "Default"

// Keshlash patterni uchun juda foydali
private List<Employee>? _cache;
public List<Employee> GetEmployees()
{
    _cache ??= LoadFromDatabase(); // Faqat birinchi chaqiruvda yuklaydi
    return _cache;
}
```

### `?.` — Null conditional

```csharp
Employee? emp = null;
int? len = emp?.Name?.Length; // → null (NullReferenceException YO'Q!)

// Zanjirlash — istalgan bosqichda null bo'lsa, butun ifoda null qaytaradi
string? city = emp?.Address?.City?.ToUpper();

// Metod chaqiruvi bilan ham ishlaydi
emp?.Save();          // emp null bo'lsa — Save() chaqirilmaydi, hech qanday xato yo'q

// Indekslash bilan
var first = employees?[0];

// Event chaqirishda klassik pattern (thread-safe)
OnEmployeeAdded?.Invoke(this, EventArgs.Empty);
```

### `!` — Null forgiving operator

```csharp
string? name = GetNameFromConfig();
int len = name!.Length; // "Men KAFOLAT beraman — bu yerda null emas"
```

```
⚠️ XAVF: `!` — faqat COMPILER ogohlantirishini o'chiradi.
   Agar aslida null bo'lsa — RUNTIME da NullReferenceException baribir tashlanadi!

string? name = GetNameFromConfig(); // Aslida null qaytarishi mumkin
int len = name!.Length; // 💥 Agar name haqiqatda null bo'lsa — Exception!
```

**Qachon oqilona ishlatiladi:** siz kodning tashqi mantig'i orqali
100% aniq bilganingizda (masalan, avvalgi qatorda `if (name != null)`
tekshirilgan, lekin compiler buni "his qila olmagan" holatlarda).

### `= null!` va `default!`

```csharp
public class Employee
{
    // NRT ogohlantirishini SUKUT qildirish, lekin xavf saqlanadi:
    public string Name { get; set; } = null!;    // "Bu keyinroq to'ldiriladi (masalan EF Core orqali)"
    public string Position { get; set; } = default!;

    // ✅ ENG TO'G'RI YONDASHUV (C# 11+) — required
    public required string Name { get; set; }
}
```

`null!` va `default!` — faqat compiler ogohlantirishini bostiradi,
runtime xavfsizlik BERMAYDI. Ular ko'pincha EF Core entity klasslarida
ishlatiladi (chunki EF Core konstruktor orqali emas, reflection orqali
propertylarni to'ldiradi, compiler buni "ko'rmaydi").

## 5. Qachon ishlatish kerak?

| Vaziyat | Yechim | Nima uchun |
|---|---|---|
| Ixtiyoriy value type maydon (yosh, sana) | `int?`, `DateTime?` | Runtime da haqiqiy null tekshiruvi |
| Reference type null bo'lishi mumkinligini bildirish | `string?`, `Employee?` | Compile-time xavfsizlik |
| Default qiymat berish (agar null bo'lsa) | `??` | Qisqa, o'qilishi oson |
| Lazy-initialization / keshlash | `??=` | Faqat kerak bo'lganda hisoblash |
| Zanjir bo'ylab xavfsiz kirish | `?.` | `NullReferenceException` oldini oladi |
| 100% aniq null emasligini bilasiz | `!` | Faqat oqilona ishonch bo'lsa |
| EF Core / ORM entity propertylari | `required` (C# 11+) | `null!`dan yaxshiroq — compile-time majburiy |

**Alternativalar taqqoslash jadvali:**

| Yondashuv | Compile-time xavfsizlik | Runtime xavfsizlik | Tavsiya |
|---|---|---|---|
| `= null!` | ⚠️ Bostiradi | ❌ Yo'q | Faqat EF Core kabi frameworklar uchun |
| `required` (C# 11+) | ✅ Majburiy | ✅ Konstruktor/init da tekshiriladi | ✅ Eng yaxshi |
| `??` bilan default berish | ✅ | ✅ | Yaxshi, ammo "sokin" default yashirishi mumkin |
| Null Object Pattern | ✅ | ✅ | Murakkab domenlar uchun ideal |

**Anti-pattern:**

```csharp
// ❌ Har joyda ! ishlatib, NRT ogohlantirishlarini "jimlantirish"
var name = GetName()!;
var email = GetEmail()!;
// Bu — NRT ning butun maqsadini yo'qqa chiqaradi!

// ✅ Haqiqiy tekshiruv yoki ArgumentNullException
var name = GetName() ?? throw new InvalidOperationException("Name topilmadi");
```

## 6. Qo'shimcha — chuqur nuqtalar

- **`Null Object Pattern`** — `null` qaytarish o'rniga "bo'sh" obyekt
  qaytarish, chaqiruvchi kodni soddalashtiradi:
  ```csharp
  public class Employee
  {
      public static readonly Employee Empty = new() { Name = "Noma'lum" };
  }

  public Employee GetById(int id)
      => _repo.GetById(id) ?? Employee.Empty; // Chaqiruvchida null tekshirish shart emas
  ```

- **`ArgumentNullException.ThrowIfNull` (C# 10+)** — qisqa va standart
  null tekshiruv:
  ```csharp
  public void Process(Employee employee)
  {
      ArgumentNullException.ThrowIfNull(employee);
      // Eskicha: if (employee == null) throw new ArgumentNullException(nameof(employee));
  }
  ```

- **NRT — faqat "opt-in" tekshiruv:** eski loyihalarda `#nullable
  disable` yoki loyiha darajasida yoqilmagan bo'lishi mumkin — bunday
  kodda `string?` va `string` orasida FARQ yo'q.

- **`??` operatori qisqa tutash (short-circuit)**: agar chap taraf
  null bo'lmasa, o'ng taraf **hisoblanmaydi**:
  ```csharp
  string result = GetCachedValue() ?? ExpensiveComputation();
  // ExpensiveComputation() FAQAT GetCachedValue() null bo'lsa chaqiriladi
  ```

- **C# versiyalaridagi rivojlanish:**
  - C# 2.0 — `Nullable<T>` (`int?`) qo'shildi
  - C# 6.0 — `?.` (null conditional)
  - C# 8.0 — Nullable Reference Types, `??=`
  - C# 11.0 — `required` keyword

- **Real loyihada uchraydigan xato:** EF Core Migration'da nullable
  bo'lmagan `string` maydon uchun DB'da `NOT NULL` constraint
  qo'yilganda, agar C# kodida `= null!` bilan default berilgan bo'lsa —
  runtime da hali to'ldirilmagan holatda saqlashga urinilsa, DB darajasida
  xato chiqadi (C# darajasida esa sukut saqlanadi).

## 7. Imtihon savollari

1. `int?` xotirada qanday saqlanadi? `Nullable<T>`ning ikkita asosiy
   fieldini ayting.
2. `int? x = null; object obj = x;` bajarilgandan keyin `obj == null`
   natija beradimi? Nima uchun bu maxsus CLR xatti-harakati?
3. Nullable Reference Types (C# 8+) runtime da qo'shimcha tekshiruv
   qo'shadimi? Isbotlab bering.
4. `??` va `??=` orasidagi farq nima? Har birini qachon ishlatasiz?
5. `!` (null forgiving) operatori nima uchun "xavfli qulaylik"
   hisoblanadi?
6. `= null!` bilan `required` (C# 11+) orasidagi asosiy farq —
   xavfsizlik nuqtai nazaridan qanday?
7. Null Object Pattern nima va u qanday muammoni hal qiladi?
8. `GetCachedValue() ?? ExpensiveComputation()` qatorida
   `ExpensiveComputation()` har doim chaqiriladimi? Tushuntiring.
