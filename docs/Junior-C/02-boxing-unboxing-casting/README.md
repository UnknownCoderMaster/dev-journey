# Boxing/Unboxing, Implicit/Explicit Casting, is/as, Checked/Unchecked — Junior C

## 1. Nima?

**Boxing** — Value type ni Reference type ga (object) aylantirish.
**Unboxing** — Reference type dan Value type ni qaytarib olish.
**Casting** — bir turni boshqa turga aylantirish.

## 2. Nima uchun kerak?

Ba'zida Value type ni object sifatida saqlash kerak bo'ladi
(eski kolleksiyalar, `object` parametrli metodlar):

```csharp
ArrayList list = new ArrayList(); // eski .NET kolleksiyasi
list.Add(42);         // Boxing — int → object
int x = (int)list[0]; // Unboxing — object → int
```

## 3. Ichida nima sodir bo'ladi?

### Boxing — xotirada nima bo'ladi?

```csharp
int a = 42;
object obj = a; // Boxing
```

```
OLDIN (Stack):        KEYIN:
┌──────────┐         Stack:     Heap:
│ a = 42   │    →   obj →[ref]→ ┌──────────┐
└──────────┘                    │ type ptr  │
                                │ 42        │ ← Heap ga ko'chirildi!
                                └──────────┘
```

Boxing paytida:
1. Heap da yangi joy ajratiladi
2. Value type qiymati Heap ga **ko'chiriladi** (nusxa)
3. Stack da reference saqlanadi

**Boxing sekin** — Heap allokationi + GC bosimi.

### Unboxing — faqat to'g'ri tur bilan

```csharp
object obj = 42;        // Boxing (int)
int x = (int)obj;       // ✅ Unboxing — to'g'ri tur
double d = (double)obj; // ❌ InvalidCastException — noto'g'ri tur!
```

Unboxing paytida CLR tekshiradi:
1. `obj` null emasmi?
2. `obj` ichidagi tur mos keladi mi?
Mos kelmasa — **runtime exception**.

### Performance muammosi

```csharp
// ❌ Boxing/Unboxing — sekin
ArrayList list = new ArrayList();
for (int i = 0; i < 1000000; i++)
    list.Add(i); // Har safar boxing!

// ✅ Generic — boxing yo'q
List<int> list = new List<int>();
for (int i = 0; i < 1000000; i++)
    list.Add(i); // Boxing YO'Q — int sifatida saqlanadi
```

## 4. Casting turlari

### Implicit casting — avtomatik, xavfsiz

```csharp
int x = 42;
double d = x;  // ✅ Implicit — kichikdan kattaga, ma'lumot yo'qolmaydi
long l = x;    // ✅ Implicit
```

Qoida: kichik tur → katta tur (xavfsiz, ma'lumot yo'qolmaydi)

### Explicit casting — qo'lda, xavfli

```csharp
double d = 3.99;
int x = (int)d;   // ✅ Explicit — 3 (kasriy qism yo'qoladi!)

int big = 300;
byte b = (byte)big; // ✅ Compile o'tadi, lekin → 44 (overflow!)
```

Qoida: katta tur → kichik tur (ma'lumot yo'qolishi mumkin)

### `is` — tur tekshirish

```csharp
object obj = "salom";

if (obj is string s)  // ✅ Pattern matching (C# 7+)
{
    Console.WriteLine(s.Length); // s avtomatik string ga cast qilingan
}

if (obj is int)  // ❌ false — string, int emas
{
    // Bu blok ishlamaydi
}
```

### `as` — xavfsiz cast

```csharp
object obj = "salom";

string s = obj as string;  // ✅ → "salom"
int? n = obj as int?;      // ✅ → null (exception yo'q!)

// Farqi:
string s1 = (string)obj;   // Exception tashlaydi — mos kelmasa
string s2 = obj as string; // null qaytaradi — mos kelmasa
```

`as` faqat **reference type** va **nullable** lar bilan ishlaydi.

### Checked/Unchecked — overflow nazorati

```csharp
// Unchecked (default) — overflow e'tiborga olinmaydi
int max = int.MaxValue; // 2,147,483,647
int overflow = max + 1; // → -2,147,483,648 (silent overflow!)

// Checked — overflow da exception
checked
{
    int max = int.MaxValue;
    int overflow = max + 1; // OverflowException tashlaydi!
}

// Yoki bitta ifoda uchun
int result = checked(int.MaxValue + 1); // OverflowException
```

## 5. Kod — amalda

```csharp
public class CastingExamples
{
    // is bilan pattern matching
    public static string Describe(object obj) => obj switch
    {
        int i    => $"Int: {i}",
        string s => $"String: {s}",
        null     => "Null",
        _        => $"Boshqa: {obj.GetType().Name}"
    };

    // as bilan xavfsiz cast
    public static void Process(object obj)
    {
        if (obj is Employee emp)
        {
            Console.WriteLine(emp.Name);
            return;
        }
        Console.WriteLine("Employee emas");
    }

    // Generic orqali boxing oldini olish
    public static T GetFirst<T>(List<T> items) where T : struct
    {
        return items[0]; // Boxing yo'q!
    }
}
```

## 6. Qo'shimcha nuqtalar

- **Generic lar** — Boxing/Unboxing muammosini hal qildi.
  `List<int>` da int sifatida saqlanadi, boxing yo'q.
- **Pattern matching (C# 8+)** — `is` ning kuchli versiyasi:
  ```csharp
  if (obj is { Name: "Orzibek", Age: > 18 } emp) { ... }
  ```
- **`Convert` sinfi** — `(int)` dan farqli, string dan ham konvertatsiya:
  ```csharp
  int x = Convert.ToInt32("42"); // string → int
  ```
- **`as` va null check** — birga ishlatiladi:
  ```csharp
  var emp = obj as Employee ?? throw new InvalidCastException();
  ```
- **Variable Scopes** — o'zgaruvchi e'lon qilingan blok ichida ko'rinadi:
  ```csharp
  if (true) { int x = 5; }
  Console.WriteLine(x); // ❌ Compile xatosi — x bu yerda ko'rinmaydi
  ```

## 7. Imtihon savollari

1. Boxing paytida xotirada nima sodir bo'ladi?
2. `(int)obj` va `obj as int?` orasidagi farq nima?
3. Nima uchun `List<int>` — `ArrayList` dan tezroq?
4. `checked` bloki qachon kerak?
5. `is` va `as` kalit so'zlarining farqi nima?
