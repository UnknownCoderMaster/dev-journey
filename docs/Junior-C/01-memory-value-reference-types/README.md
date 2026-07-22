# Memory — Value/Reference Types, `ref`, `out`, `in`, `params` — Junior C

## 1. Nima?

C# da barcha tiplar ikki guruhga bo'linadi:

```
Value Type     → qiymat to'g'ridan Stack da saqlanadi
Reference Type → manzil Stack da, asosiy ma'lumot Heap da saqlanadi
```

## 2. Nima uchun kerak?

Xotira boshqaruvi — dastur tezligi va xavfsizligiga to'g'ridan ta'sir qiladi:

```
Value Type    → kichik, tez, avtomatik tozalanadi (metod tugaganda)
Reference Type → katta, moslashuvchan, Garbage Collector tozalaydi
```

## 3. Ichida nima sodir bo'ladi?

### Value Type — Stack da

```csharp
int a = 10;
int b = a;   // NUSXA olinadi
b = 20;

Console.WriteLine(a); // → 10 (o'zgarmadi)
Console.WriteLine(b); // → 20
```

```
STACK:
┌─────────────┐
│ a = 10      │
│ b = 20      │  ← b mustaqil nusxa
└─────────────┘
```

Value type lar: `int`, `double`, `float`, `bool`, `char`, `decimal`,
`struct`, `enum`

---

### Reference Type — Heap da

```csharp
var emp1 = new Employee { Name = "Orzibek" };
var emp2 = emp1;   // Manzil nusxalanadi, obyekt emas!
emp2.Name = "Dilnoza";

Console.WriteLine(emp1.Name); // → "Dilnoza" (!)
```

```
STACK              HEAP
─────────          ──────────────────
emp1 → [0x0A4F] → Name: "Dilnoza"
emp2 → [0x0A4F] ↗  (bir xil manzil!)
```

Reference type lar: `class`, `interface`, `string`, `array`, `delegate`

---

### struct vs class — xotira farqi

```csharp
// struct — Value Type (Stack)
struct Point { public int X; public int Y; }

Point p1 = new Point { X = 1, Y = 2 };
Point p2 = p1;   // To'liq nusxa
p2.X = 99;
Console.WriteLine(p1.X); // → 1 (o'zgarmadi!)

// class — Reference Type (Heap)
class PointClass { public int X; public int Y; }

PointClass pc1 = new PointClass { X = 1, Y = 2 };
PointClass pc2 = pc1;   // Manzil nusxalanadi
pc2.X = 99;
Console.WriteLine(pc1.X); // → 99 (o'zgardi!)
```

---

### String — maxsus Reference Type (Immutable)

`string` reference type, lekin **immutable** (o'zgarmas):

```csharp
string a = "salom";
string b = a;
b = "xayr";

Console.WriteLine(a); // → "salom" (o'zgarmadi!)
```

**Immutable** = "bir marta yaratildi — hech qachon o'zgartirib bo'lmaydi."

`b = "xayr"` yozilganda — `"salom"` o'zgartirilmaydi, **yangi obyekt** yaratiladi:

```
HEAP:
┌──────────────┐
│ "salom"      │ ← a hali shu yerga ishoraydi
└──────────────┘
┌──────────────┐
│ "xayr"       │ ← b endi shu yerga ishoradi (yangi obyekt!)
└──────────────┘
```

**String interning** — bir xil literal string lar uchun bitta Heap obyekti:

```csharp
string a = "salom";
string b = "salom";
Console.WriteLine(object.ReferenceEquals(a, b)); // → TRUE
// Ikkalasi ham bir xil Heap manzilini ko'rsatadi!
```

**Immutable bo'lgani uchun concatenation da muammo:**

```csharp
// ❌ Har birida yangi string yaratiladi — xotira isrof!
string result = "";
for (int i = 0; i < 10000; i++)
{
    result += i.ToString(); // Har safar yangi string obyekti!
}

// ✅ StringBuilder — bitta obyekt ichiga qo'shib boriladi
var sb = new StringBuilder();
for (int i = 0; i < 10000; i++)
{
    sb.Append(i);
}
string result = sb.ToString();
```

## 4. `ref`, `out`, `in`, `params` — kalit so'zlar

### `ref` — referens orqali uzatish

```csharp
void AddTen(ref int number)
{
    number += 10;  // Asl o'zgaruvchini o'zgartiradi
}

int x = 5;
AddTen(ref x);
Console.WriteLine(x); // → 15
```

**Shart:** `ref` o'zgaruvchi chaqirishdan OLDIN initsializatsiya qilingan
bo'lishi kerak.

---

### `out` — natija chiqarish

```csharp
bool TryParse(string input, out int result)
{
    if (int.TryParse(input, out result))
        return true;

    result = 0;  // out parametr metod ichida DOIM o'rnatilishi shart
    return false;
}

if (TryParse("42", out int number))
    Console.WriteLine(number); // → 42
```

**Muhim:** `out` parametrni metod ichida o'rnatishdan OLDIN o'qib bo'lmaydi:

```csharp
void Calculate(out int result)
{
    Console.WriteLine(result); // ❌ Compile xatosi! — hali o'rnatilmagan
    result = 42;
}

void Calculate(out int result)
{
    result = 42;               // ✅ Avval yozish
    Console.WriteLine(result); // ✅ Keyin o'qish
}
```

---

### `ref` vs `out` — farqi

| | `ref` | `out` |
|---|---|---|
| Chaqirishdan oldin initsializatsiya | ✅ Majburiy | ❌ Shart emas |
| Metod ichida o'rnatish | Ixtiyoriy | ✅ Majburiy |
| Metod ichida o'qish | ✅ Darhol | ❌ Avval o'rnatish kerak |

Real hayotda: `int.TryParse`, `DateTime.TryParse` — `out` ishlatadi.

---

### `in` — readonly ref

```csharp
void PrintInfo(in Employee emp)
{
    Console.WriteLine(emp.Name);  // ✅ O'qish mumkin
    // emp.Name = "boshqa";       // ❌ Compile xatosi — o'zgartirish mumkin emas
}

var emp = new Employee { Name = "Orzibek" };
PrintInfo(in emp);
```

**Qachon ishlatiladi?** Katta `struct` larni nusxa olmay, xavfsiz uzatish
uchun — performance optimallashtirish.

```
ref  → O'qish ✅  Yozish ✅
out  → O'qish ❌  Yozish ✅ (majburiy)
in   → O'qish ✅  Yozish ❌
```

---

### `params` — o'zgaruvchan sonli argumentlar

```csharp
int Sum(params int[] numbers)
{
    return numbers.Sum();
}

Console.WriteLine(Sum(1, 2, 3));        // → 6
Console.WriteLine(Sum(1, 2, 3, 4, 5)); // → 15
Console.WriteLine(Sum());               // → 0
```

`params` — massiv yaratmasdan, istalgan sonli argument uzatish imkonini
beradi. `Console.WriteLine` ham ichida `params` ishlatadi.

**Qoidalar:**
- Faqat **bitta** `params` parametr bo'lishi mumkin
- U **eng oxirgi** parametr bo'lishi shart
- `params` bilan `ref`/`out` birga ishlatib bo'lmaydi

## 5. Qo'shimcha — e'tiborga olinishi kerak bo'lgan nuqtalar

- **Garbage Collector (GC)**: Heap dagi obyektlar hech kim ishora
  qilmay qolganda, GC ularni avtomatik tozalaydi. Value type lar esa
  metod tugaganda Stack dan avtomatik o'chiriladi — GC kerak emas.

- **Boxing** (keyingi mavzu bilan bog'liq): Value type ni Reference type
  ga aylantirganda (`object obj = 42`) — qiymat Heap ga ko'chiriladi.
  Bu "boxing" deyiladi va sekin ishlaydi.

- **`struct` qachon ishlatiladi?**: Kichik, oddiy ma'lumotlar uchun
  (`Point`, `Color`, `DateTime`) — Stack da saqlanadi, tezroq. Lekin
  meros olish imkoni yo'q (faqat interfeys implement qilish mumkin).

- **`readonly struct`**: Immutable struct yaratish uchun — `in` parametr
  bilan birgalikda juda samarali.

- **`record` (C# 9+)**: Immutable reference type — `string` ga o'xshash,
  lekin custom klass uchun. Qiymat solishtirish (value equality) avtomatik.

- **`Span<T>` va `Memory<T>`**: Stack va Heap ni birgalikda boshqarish
  uchun zamonaviy yondashuv — katta massivlar bilan ishlashda GC bosimini
  kamaytiradi (keyinchalik o'rganiladi).

## 6. Imtihon savollari

1. `struct` va `class` orasidagi asosiy xotira farqi nima?
2. `ref` va `out` orasidagi 2 ta asosiy farq nima?
3. Quyidagi kodda xato bormi?
   ```csharp
   void Calculate(out int result)
   {
       Console.WriteLine(result);
       result = 42;
   }
   ```
4. Nima uchun `string` reference type bo'lsa ham immutable kabi ishlaydi?
5. `StringBuilder` nima uchun `string +=` dan samaraliroq?
6. `in` parametr qachon ishlatiladi va `ref` dan qanday farq qiladi?
