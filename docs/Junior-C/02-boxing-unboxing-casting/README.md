# Boxing/Unboxing, Casting, is/as, Checked/Unchecked, Variable Scopes — Junior C

## 1. Nima?

**Boxing** — Value type (`int`, `struct`, `enum` va h.k.) qiymatini
**Heap**ga ko'chirib, `object` (yoki interfeys) sifatida o'rash jarayoni.

**Unboxing** — Heap dagi boxed obyektdan asl Value type qiymatini
qaytarib olish jarayoni.

**Casting** — bir C# turini boshqasiga aylantirish: `implicit` (avtomatik,
xavfsiz) va `explicit` (qo'lda, xavfli, ma'lumot yo'qolishi mumkin).

**`is`/`as`** — runtime da tur tekshirish operatorlari. **`checked`/
`unchecked`** — arifmetik overflow ustidan nazorat. **Variable scope** —
o'zgaruvchining "ko'rinish hududi" — qaysi kod blokida u mavjud bo'la oladi.

Bularning barchasi bitta umumiy mavzuga birlashadi: **CLR turlar tizimida
(CTS — Common Type System) qiymat qanday saqlanadi va bir turdan
ikkinchisiga o'tganda nima sodir bo'ladi.**

---

## 2. Nima uchun kerak?

C# ikkita tur oilasiga ega: **Value Type** (Stack) va **Reference Type**
(Heap). Lekin .NET dagi **hamma narsa** — hatto `int` ham — tub-tubida
`System.Object`dan meros bo'ladi. Bu paradoksni hal qilish uchun CLR
**Boxing** mexanizmini ixtiro qildi.

Agar Boxing bo'lmaganida:

```
❌ object obj = 42;  // MUMKIN BO'LMAS EDI
❌ ArrayList list = new ArrayList(); list.Add(42); // int'ni saqlab bo'lmasdi
```

Bo'lmaganida — har bir Value type uchun alohida `object`-mos versiya
yozish kerak bo'lardi (C++ da shunga o'xshash template muammolari bor).

**Casting** kerak, chunki compile-time da bitta tur bo'lgan qiymat,
runtime da boshqacha tur sifatida ishlatilishi kerak bo'ladi — masalan
`object` qaytaruvchi eski API dan aniq turni olish.

**`checked`/`unchecked`** kerak, chunki .NET default holda **overflow
xatosini sukut biladi** — bu moliyaviy hisob-kitoblarda (masalan, ERP
tizimida `salary` hisoblashda) sezilmagan xatolarga olib kelishi mumkin.

**Variable scope** tushunish kerak, chunki noto'g'ri scope tushunish —
"nega bu o'zgaruvchi bu yerda ko'rinmayapti" kabi eng ko'p uchraydigan
boshlang'ich xatolarga sabab bo'ladi.

---

## 3. Ichida nima sodir bo'ladi? (Mexanizm)

### 3.1 Boxing — CLR va xotira darajasida

```csharp
int a = 42;       // Stack: a = 42
object obj = a;   // BOXING sodir bo'ladi
```

CLR ichida bu quyidagi IL kodga aylanadi:

```il
ldloc.0     // Stack'dan a ni yukla
box int32   // Boxing — Heap'da yangi obyekt yaratadi
stloc.1     // obj ga reference'ni saqla
```

Xotirada:

```
OLDIN:                        KEYIN (box IL buyrug'idan so'ng):

STACK                         STACK                    HEAP
┌─────────┐                   ┌─────────┐              ┌──────────────────┐
│ a = 42  │                   │ a = 42  │              │ Method Table ptr │ ← tur haqida meta-ma'lumot
└─────────┘                   │ obj ──┐ │              │ SyncBlockIndex    │ ← lock/hashcode uchun
                               └───────┼─┘              │ 42 (nusxa!)       │ ← qiymat KO'CHIRILGAN
                                       └───────────────► └──────────────────┘
```

Boxing paytida 3 ta narsa sodir bo'ladi:
1. **Heap**da yangi obyekt uchun joy ajratiladi (Method Table pointer +
   SyncBlockIndex + qiymat uchun joy)
2. Value type **qiymati** (nusxa sifatida) shu joyga ko'chiriladi
3. Stack (yoki boshqa reference o'zgaruvchi) — shu Heap manziliga
   ishora qiladigan **reference** oladi

Muhim: `a` va `obj` endi **mustaqil** — `a`ni o'zgartirish `obj`ga
ta'sir qilmaydi, chunki boxing paytida **nusxa** olingan:

```csharp
int a = 42;
object obj = a;
a = 100;
Console.WriteLine(obj); // → 42 (o'zgarmadi! obj alohida Heap nusxasi)
```

### 3.2 Unboxing — teskari jarayon va xavfsizlik tekshiruvi

```csharp
object obj = 42;   // Boxing (int)
int x = (int)obj;  // Unboxing
```

IL darajasida:

```il
ldloc.0        // obj reference'ni yukla
unbox.any int32 // Tur tekshiriladi, qiymat Stack'ga NUSXALANADI
stloc.1        // x ga saqla
```

`unbox.any` CLR runtime da ikkita tekshiruv o'tkazadi:
1. `obj == null` emasmi?
2. Obyektning **haqiqiy** (boxed) turi — kutilgan turga **aniq** mos
   keladimi? (implicit numeric conversion ham ishlamaydi!)

```csharp
object obj = 42;         // boxed int
long x = (long)obj;      // ❌ InvalidCastException!
// Sabab: unboxing FAQAT aniq turga ruxsat beradi.
// int → long implicit cast bo'lsa ham, unboxing bunga rioya qilmaydi.

long x = (long)(int)obj; // ✅ Avval unbox qil (int), keyin cast (long)
```

```
❌ XATO STsenariy:
object obj = "salom";
int x = (int)obj; // InvalidCastException — string int emas!

❌ XATO STsenariy:
object obj = null;
int x = (int)obj; // NullReferenceException!
```

### 3.3 Performance muammosi — ArrayList vs List\<T\>

```csharp
// ❌ ArrayList — object[] saqlaydi, har Add() da BOXING
var list = new ArrayList();
for (int i = 0; i < 1_000_000; i++)
    list.Add(i); // int → object (boxing, Heap allocation!)

int sum = 0;
foreach (int i in list)   // har elementda UNBOXING
    sum += i;
```

```
1,000,000 marta Boxing = 1,000,000 ta Heap allocation!
→ Garbage Collector bosimi ortadi (Gen0 collection tez-tez ishga tushadi)
→ Cache locality yomon (har element alohida Heap joyida)
```

```csharp
// ✅ List<int> — Generic, ICHKI T[] massiv — boxing YO'Q
var list = new List<int>();
for (int i = 0; i < 1_000_000; i++)
    list.Add(i); // int TO'G'RIDAN saqlanadi, Heap allocation yo'q (faqat massiv o'sganda)

int sum = 0;
foreach (int i in list)  // Boxing yo'q — to'g'ridan int
    sum += i;
```

`List<T>` generic bo'lgani uchun — JIT compiler har value type uchun
**alohida maxsuslashtirilgan** (specialized) native kod generatsiya
qiladi (`List<int>`, `List<double>` — har biri o'z IL/machine code'iga
ega). Shu sababli boxing kerak emas.

| | `ArrayList` | `List<int>` |
|---|---|---|
| Ichki saqlash | `object[]` | `int[]` |
| Har `Add()`da | Boxing | Yo'q |
| Har o'qishda | Unboxing | Yo'q |
| Type safety | Compile-time yo'q | ✅ Compile-time bor |
| Tezlik (1M element) | Sekin | ~10x tezroq |

---

## 4. Kod — asosiy sintaksis

### Implicit casting — avtomatik, xavfsiz

```csharp
int x = 42;
long l = x;    // ✅ Implicit — int → long, kattaroq, ma'lumot yo'qolmaydi
double d = x;  // ✅ Implicit — int → double
float f = 10L; // ✅ Implicit — long → float (aniqlik yo'qolishi mumkin, lekin runtime xato bermaydi)

// Class ierarxiyasida:
class Employee { }
class Manager : Employee { }

Manager m = new Manager();
Employee e = m;  // ✅ Implicit — Manager IS-A Employee (upcasting)
```

**Qoida:** kichik hajm/diapazon → katta hajm/diapazon (numeric), yoki
**derived → base** (reference type larda) — har doim xavfsiz.

### Explicit casting — qo'lda, xavfli

```csharp
double d = 3.99;
int x = (int)d;    // ✅ Explicit — natija: 3 (KASR QISM KESILADI, yaxlitlanmaydi!)

int big = 300;
byte b = (byte)big; // ✅ Compile o'tadi, lekin natija: 44 (overflow — 300 % 256 = 44)

Employee e = new Employee();
Manager m = (Manager)e; // ⚠️ Compile o'tadi, lekin runtime: InvalidCastException!
                          // (e HAQIQATDA Manager bo'lmagani uchun)

Employee e2 = new Manager();
Manager m2 = (Manager)e2; // ✅ Runtime OK — e2 haqiqatda Manager edi (downcasting)
```

```
❌ NOTO'G'RI TASAVVUR: "(int)d yaxlitlaydi"
✅ TO'G'RI: (int)d — KESADI (truncate), Math.Round(d) — YAXLITLAYDI

double d = 3.99;
int a = (int)d;         // → 3
int b = (int)Math.Round(d); // → 4
```

### `is` — tur tekshirish va pattern matching evolyutsiyasi

```csharp
// C# 1-6: klassik
object obj = "salom";
if (obj is string)
{
    string s = (string)obj; // qo'shimcha cast kerak edi
}

// C# 7+: pattern matching — cast avtomatik
if (obj is string s)
{
    Console.WriteLine(s.Length); // s to'g'ridan ishlatiladi
}

// C# 8+: pattern combinators (and, or, not)
if (obj is string and not null)
{
    Console.WriteLine("bo'sh bo'lmagan string");
}

// C# 9+: property pattern
if (obj is Employee { Age: > 18, Department.Name: "IT" } emp)
{
    Console.WriteLine($"{emp.Name} IT bo'limida va voyaga yetgan");
}

// switch expression bilan (C# 8+)
string category = obj switch
{
    int n when n < 0  => "Manfiy son",
    int n              => $"Musbat son: {n}",
    string { Length: 0 } => "Bo'sh string",
    string s           => $"String: {s}",
    null               => "Null",
    _                  => "Noma'lum tur"
};
```

### `as` — xavfsiz cast

```csharp
object obj = "salom";

string s1 = obj as string;   // ✅ → "salom"
int? n = obj as int?;        // ✅ → null (obj string, int emas — lekin exception YO'Q)

// Farqi (cast) bilan:
string s2 = (string)obj;     // Mos kelmasa → InvalidCastException
string s3 = obj as string;   // Mos kelmasa → null qaytaradi (xavfsizroq)

// as + null check — klassik pattern
var emp = obj as Employee;
if (emp is null)
{
    throw new InvalidOperationException("obj Employee emas");
}
```

**Muhim cheklov:** `as` faqat **reference type** yoki **Nullable\<T\>**
bilan ishlaydi:

```csharp
int x = obj as int;  // ❌ Compile xatosi! int — value type, nullable emas
int? x = obj as int?; // ✅ int? — Nullable<int>, ruxsat etilgan
```

### `checked`/`unchecked` — overflow nazorati

```csharp
// Default (unchecked) — overflow SEZILMAYDI
int max = int.MaxValue;        // 2,147,483,647
int result = max + 1;          // → -2,147,483,648 (wrap-around, XATO SEZILMAYDI!)

// checked bloki — overflow topilsa OverflowException
checked
{
    int max2 = int.MaxValue;
    int result2 = max2 + 1;    // 💥 OverflowException!
}

// Bitta ifoda uchun
int r = checked(int.MaxValue + 1); // 💥 OverflowException

// unchecked — checked kontekst ichida overflow ni ataylab o'chirish
checked
{
    int safe = unchecked(int.MaxValue + 1); // Overflow ruxsat etiladi bu yerda
}

// Loyiha darajasida yoqish (.csproj):
// <CheckForOverflowUnderflow>true</CheckForOverflowUnderflow>
```

**ERP misoli — moliyaviy hisobda `checked` muhimligi:**

```csharp
public decimal CalculateTotalSalary(int[] departmentSalaries)
{
    checked
    {
        int total = 0;
        foreach (var salary in departmentSalaries)
            total += salary; // Agar summa int.MaxValue dan oshsa — DARHOL xato beradi
                              // (jimgina noto'g'ri natija chiqarish o'rniga)
        return total;
    }
}
```

### Variable Scopes

```csharp
public class EmployeeService
{
    private int _classField = 1; // Class scope — butun klass ichida ko'rinadi

    public void Process()
    {
        int methodVar = 2; // Method scope — butun metod ichida ko'rinadi

        if (true)
        {
            int blockVar = 3; // Block scope — faqat shu {} ichida ko'rinadi
            Console.WriteLine(methodVar); // ✅ tashqi scope ko'rinadi
        }

        Console.WriteLine(blockVar); // ❌ Compile xatosi! blockVar bu yerda yo'q
    }

    public void Shadowing(int _classField) // ⚠️ Parametr klass fieldini "yashiradi"
    {
        Console.WriteLine(_classField);       // Parametr qiymati chiqadi
        Console.WriteLine(this._classField);  // Class field kerak bo'lsa — this. bilan
    }
}
```

```
❌ C# da bloklararo variable shadowing (ichma-ich bir xil nom) — TAQIQLANGAN:

int x = 5;
if (true)
{
    int x = 10; // ❌ Compile xatosi! "x" allaqachon shu scope zanjirida bor
}
```

---

## 5. Qachon ishlatish kerak?

| Vaziyat | Tavsiya |
|---|---|
| Value type'ni `object`/interfeys sifatida saqlash kerak | Iloji boricha **Generic** (`List<T>`) ishlating, boxing'dan qoching |
| Tur ma'lum, aniq mos kelishiga ishonch 100% | `(Type)cast` — tezroq, lekin exception xavfi bor |
| Tur noaniq, mos kelmasligi mumkin | `is`/`as` — xavfsiz, `null` yoki `false` qaytaradi |
| Faqat tur tekshirish, qiymat kerak emas | `is Type` (pattern matching’siz) |
| Tur + qiymat bir yo'la kerak | `is Type variable` |
| Moliyaviy/kritik arifmetika | `checked` bloki yoki loyiha darajasida yoqish |
| Performance-critical loop (millionlab element) | `unchecked` (default) — checked qo'shimcha CPU sarflaydi |

**Anti-patternlar:**

```csharp
// ❌ Keraksiz boxing — Generic o'rniga object ishlatish
void Print(object value) { Console.WriteLine(value); }
Print(42); // Boxing sodir bo'ladi!

void Print<T>(T value) { Console.WriteLine(value); } // ✅ Boxing yo'q

// ❌ Cast'ni try-catch bilan "tur tekshirish" o'rniga ishlatish
try { var m = (Manager)emp; }
catch { /* Manager emas ekan */ } // ❌ Exception - sekin va noaniq

if (emp is Manager m) { /* ... */ } // ✅ Tez va aniq

// ❌ as dan keyin null tekshirmasdan ishlatish
var m = obj as Manager;
m.DoWork(); // 💥 NullReferenceException agar obj Manager bo'lmasa!
```

---

## 6. Qo'shimcha — chuqur nuqtalar

- **Boxing struct larni ham o'zgartirmaydi (immutability illyuziyasi):**
  Boxed struct ustida metod chaqirilsa, u nusxada ishlaydi — asl struct
  o'zgarmaydi (agar qayta unbox qilib saqlamasangiz).

- **Nullable\<T\> maxsus boxing xatti-harakati:** `int?` boxing qilinganda,
  agar `HasValue == false` bo'lsa — natija `null` bo'ladi (Nullable\<int\>
  emas!). Agar `HasValue == true` — `int` sifatida box qilinadi
  (`Nullable<int>` emas, to'g'ridan `int`):
  ```csharp
  int? x = null;
  object obj = x;           // obj == null (Nullable<int> emas!)
  Console.WriteLine(obj is int); // → False, chunki obj null

  int? y = 5;
  object obj2 = y;          // obj2 — boxed int (5), Nullable<int> emas
  Console.WriteLine(obj2 is int); // → True
  ```

- **Enum boxing** — enum ham value type, shuning uchun `object` ga
  aylantirilganda boxing sodir bo'ladi. `Enum.ToString()` chaqirilganda
  ichkarida reflection + boxing bor — hot pathlarda sekin.

- **C# versiyalaridagi o'zgarishlar:**
  - C# 7.0 — `is` pattern matching (`obj is string s`)
  - C# 7.1 — `default` literal (`Employee e = default;`)
  - C# 8.0 — switch expressions, property patterns, `and`/`or`/`not`
  - C# 9.0 — record types, pattern matching yanada kengaydi (`is > 5`)
  - C# 11.0 — `required` (nullable bilan bog'liq, lekin cast emas)

- **Real loyihalarda uchraydigan xato:** EF Core'da `object` qaytaruvchi
  dynamic SQL natijalarini keraksiz `(int)` bilan cast qilib,
  `NULL` qiymat kelganda `NullReferenceException` olish. Yechim:
  `reader["age"] as int?`.

- **Downcasting xavfi Dependency Injection'da:** `IEmployeeRepository`
  ni ba'zan `(EmployeeRepository)repo` deb concrete klassga cast qilish —
  bu DI/interfeys prinsipini buzadi va test qilishni qiyinlashtiradi.
  Bunday cast kodni ko'rsangiz — dizayn muammosi belgisi.

---

## 7. Imtihon savollari

1. Boxing sodir bo'lganda Heap'da nechta va qanday ma'lumot yaratiladi?
   IL darajasida qaysi buyruq ishlatiladi?
2. Nima uchun `long x = (long)obj;` — agar `obj` boxed `int` bo'lsa —
   `InvalidCastException` tashlaydi? Buni qanday tuzatish kerak?
3. `ArrayList` bilan `List<int>` orasidagi performance farqining
   asosiy sababini tushuntiring (Generic va boxing nuqtai nazaridan).
4. `(int)3.99` va `Math.Round(3.99)` orasidagi farq nima?
5. `is` va `as` operatorlari orasidagi asosiy 2 ta farqni ayting.
   Qaysi holatda qaysi birini tanlaysiz?
6. `checked` va `unchecked` nima uchun kerak? Default holatda C#
   qaysi rejimda ishlaydi?
7. `int? x = null; object obj = x;` qatoridan keyin `obj == null`
   natija beradimi yoki `Nullable<int>` obyekt yaratiladimi? Nima uchun?
8. Variable shadowing nima va C# unga qaysi holatlarda ruxsat beradi,
   qaysilarida bermaydi?
