# dynamic, var, object — Junior A

## 1. Nima? (Ta'rif)

**`var`** — compile-time **type inference** (tur avtomatik
XULOSA qilinadi, lekin QAT'IY statik tiplangan qoladi). **`object`**
— barcha turlarning **umumiy bazaviy klassi** (`System.Object`).
**`dynamic`** — turi FAQAT **runtime**da hal qilinadigan, compile-time
tekshiruvni **butunlay chetlab o'tuvchi** maxsus tur.

## 2. Nima uchun kerak?

Bu uchtasi — **turlicha muammoni** hal qiladi: `var` — **kodni
qisqartirish** (murakkab generic turlarni qayta yozmaslik); `object`
— **istalgan turni** bitta o'zgaruvchida saqlash (lekin cast kerak);
`dynamic` — **compile-time'da noma'lum** strukturaga ega ma'lumot
(masalan JSON, COM obyektlar) bilan ishlash.

## 3. Ichida nima sodir bo'ladi? (Mexanizm)

### 3.1 `var` — compile-time type inference

```csharp
var name = "Orzibek";       // Compiler — bu STRING ekanini ANIQLAYDI
var age = 25;                // int
var employees = new List<Employee>(); // List<Employee>

// name = 42; // ❌ XATO! var — TUR o'zgarmaydi, FAQAT compiler UNI o'zi ANIQLAYDI
```

```
⚠️ MUHIM: `var` — DINAMIK TIPLASH EMAS! Bu FAQAT compile-time'da
   "yozish qulayligi" — COMPILE bo'lgandan KEYIN, IL kodida `var`
   HECH QANDAY FARQ QILMAYDI — xuddi `string name = "Orzibek";`
   YOZILGANDEK.
```

**Qachon ishlatish kerak:**
```csharp
var employees = _context.Employees.Where(e => e.Age > 25).ToList(); // ✅ Tur AYON (List<Employee>)
var result = CalculateComplexThing(); // ❌ Tur NOANIQ — o'quvchi metod SIGNATURE'ni tekshirishga MAJBUR
```

### 3.2 `object` — barcha klasslar otasi

```csharp
object obj = 42;           // int → object, BOXING (Heap allocation)
object obj2 = "salom";     // string — ALLAQACHON reference type, boxing YO'Q

int x = (int)obj;          // Cast SHART — object'dan qaytarish uchun
```

```
Boxing/Unboxing — batafsil docs/Junior-C/02-boxing-unboxing-casting
faylida yoritilgan. Qisqacha: object — VALUE type'larni saqlaganda,
Heap'ga "o'rab" saqlaydi (boxing), qaytarib olishda EXPLICIT CAST
talab qiladi (unboxing).
```

**Runtime tekshiruv:**
```csharp
object obj = "salom";
if (obj is string s) // Runtime'da TUR TEKSHIRILADI
    Console.WriteLine(s.Length);
```

### 3.3 `dynamic` — runtime type resolution, DLR

```csharp
dynamic value = 42;
value = "endi string";  // ✅ RUXSAT ETILADI! Tur — RUNTIME'da o'zgarishi mumkin
value = new Employee(); // ✅ Bu ham RUXSAT ETILADI!

dynamic obj = GetSomeObject();
obj.NonExistentMethod(); // ❌ COMPILE-TIME'da XATO BERILMAYDI!
                          // 💥 RUNTIME'da RuntimeBinderException tashlaydi!
```

```
DLR (Dynamic Language Runtime) — .NET'ning `dynamic` turi bilan
ishlashini ta'minlovchi QATLAM. `dynamic` o'zgaruvchi ustida
METOD/PROPERTY chaqirilganda:

1. Compiler — HECH QANDAY tekshiruv QILMAYDI, IL kodida "CallSite"
   (dinamik chaqiruv joyi) YARATADI
2. RUNTIME'da — DLR obyektning HAQIQIY turini ANIQLAYDI (Reflection'ga
   O'XSHASH mexanizm)
3. Mos METOD/PROPERTY TOPILSA — CHAQIRILADI
4. TOPILMASA — RuntimeBinderException RUNTIME'da TASHLANADI
```

```
⚠️ IntelliSense YO'Q (compiler HECH NARSANI BILMAYDI), XATO FAQAT
   RUNTIME'da SEZILADI — bu `dynamic`ni "XAVFLI" qiladi, faqat
   ANIQ zarurat bo'lganda ishlatilishi kerak.
```

### 3.4 Uchala farqi — jadval

| | `var` | `object` | `dynamic` |
|---|---|---|---|
| Tur QACHON hal qilinadi | Compile-time | Compile-time (object), runtime (cast) | Runtime |
| Compile-time xavfsizlik | ✅ To'liq | ✅ (cast'siz cheklangan) | ❌ Yo'q |
| IntelliSense | ✅ To'liq | Cheklangan (cast'gacha) | ❌ Yo'q |
| Performance | Static (tez) | Boxing (value type uchun sekin) | DLR overhead (ENG SEKIN) |
| Xato qachon aniqlanadi | Compile-time | Compile-time (cast xato bo'lsa runtime) | FAQAT runtime |

### 3.5 `dynamic` qachon kerak — COM interop, JSON, reflection

```csharp
// COM Interop (Excel avtomatlashtirish va h.k.)
dynamic excelApp = Activator.CreateInstance(Type.GetTypeFromProgID("Excel.Application"));
excelApp.Visible = true; // COM obyekt METODLARI compile-time'da NOMA'LUM

// JSON — dinamik struktura (Newtonsoft.Json bilan)
dynamic json = JsonConvert.DeserializeObject("{\"name\":\"Orzibek\",\"age\":25}");
Console.WriteLine(json.name); // Property nomi — RUNTIME'da HAL QILINADI

// ExpandoObject — dinamik property qo'shish
dynamic person = new ExpandoObject();
person.Name = "Orzibek"; // YANGI property — RUNTIME'da YARATILADI!
person.Age = 25;
```

### 3.6 `dynamic` va Reflection farqi

```
Reflection — QO'LDA, ANIQ API orqali (GetProperty, GetMethod,
              Invoke) — MURAKKAB, lekin TO'LIQ NAZORAT

dynamic    — COMPILER "SINTAKTIK QAND"i — xuddi ODDIY metod
             chaqiruvidek YOZILADI, LEKIN ICHKARIDA DLR orqali
             Reflection'GA O'XSHASH mexanizm ISHLAYDI (aslida
             DLR — Reflection'dan HAM SAMARALI, chunki CALL SITE
             KESHLANADI — takroriy chaqiruvlar TEZROQ)
```

```csharp
// Reflection — aniq, ko'p KOD
var property = obj.GetType().GetProperty("Name");
var value = property.GetValue(obj);

// dynamic — qisqa, LEKIN runtime XATO xavfi
dynamic d = obj;
var value2 = d.Name;
```

## 4. Kod — real ERP misolida to'g'ri tanlov

```csharp
// ✅ var — tur AYON bo'lgan joyda
var employees = await _context.Employees.ToListAsync();

// ✅ object — generic bo'lmagan, ESKI API bilan ishlashda
public void LogValue(object value) => Console.WriteLine(value?.ToString());

// ✅ dynamic — FAQAT JSON/COM kabi haqiqatan ZARUR bo'lganda
dynamic externalApiResponse = JsonConvert.DeserializeObject(jsonString);
string employeeName = externalApiResponse.data.employee.name;

// ❌ dynamic — ERP domenida, KUNDALIK biznes logikada — ISHLATILMASIN!
dynamic employee = GetEmployee(); // ❌ Nima uchun object/aniq tur emas?
```

## 5. Qachon ishlatish kerak?

| Vaziyat | Yechim |
|---|---|
| Tur AYON, kod qisqarishi kerak | `var` |
| Tur NOANIQ, murakkab so'rov natijasi | `var` (LEKIN o'quvchiga aniq bo'lsin) |
| Turli xil turlarni BITTA joyda saqlash (eski API) | `object` |
| Compile-time'da NOMA'LUM struktura (JSON, COM) | `dynamic` |
| Domen logikasi, ERP biznes kod | HECH QAYSISI — ANIQ TUR ishlatilsin! |

## 6. Muhim nuqtalar

- `var` — TUR XAVFSIZLIGINI **kamaytirmaydi** — bu FAQAT sintaksis
  qulayligi, compile-time tekshiruv **TO'LIQ SAQLANADI**.
- `dynamic` — **eng sekin** variant (DLR overhead), va **eng
  xavfli** (runtime xatolar) — faqat **haqiqatan zarur** bo'lganda
  ishlatilishi kerak.
- `object` bilan **qiymat turlari** (int, struct) ishlatilganda —
  **boxing** sodir bo'ladi, bu performance narxi bor.

## 7. Imtihon savollari

1. `var` dinamik tiplashmi? Nima uchun yo'q?
2. `object` bilan ishlaganda boxing qachon sodir bo'ladi?
3. `dynamic` va oddiy `object` orasidagi asosiy farq nima?
4. DLR (Dynamic Language Runtime) nima vazifani bajaradi?
5. `dynamic` ishlatilganda IntelliSense nima uchun ishlamaydi?
6. `dynamic` va Reflection orasidagi farq nima?
7. `ExpandoObject` nima va u qachon foydali?
