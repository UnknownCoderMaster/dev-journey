# Class, Object — Junior D

## 1. Nima?

**Class** — bu obyekt yaratish uchun shablon (qolip). Klassning o'zi xotirada
joy egallamaydi — u faqat "qanday bo'lishi kerak"ligini belgilaydi.

**Object** — class asosida yaratilgan, xotirada haqiqiy joy egallagan
ko'rinish (instance).

```csharp
class Employee     // Qolip
{
    public string Name { get; set; }
    public int Age { get; set; }
}
Employee emp = new Employee();  // Obyekt — xotirada joy bor
```

## 2. Nima uchun kerak?

Bir xil turdagi ko'p narsalarni modellashtirish uchun. Masalan 100 ta xodim
bor — har birini alohida o'zgaruvchi sifatida yozish o'rniga, bitta
`Employee` classi orqali 100 ta object yaratiladi.

## 3. Ichida nima sodir bo'ladi? (CLR darajasida)

`new Employee()` yozilganda bosqichma-bosqich:

1. CLR ishga tushadi
2. Heap xotirasida Employee uchun joy ajratiladi
3. Barcha maydonlar default qiymat oladi (`string` → `null`, `int` → `0`,
   `bool` → `false`)
4. Constructor chaqiriladi (yozilmagan bo'lsa, CLR default constructor
   qo'shadi)
5. Heap dagi manzil Stack dagi o'zgaruvchiga yoziladi

```
STACK                    HEAP
─────────                ──────────────────
emp → [0x0A4F]    →     [0x0A4F]
                         ┌─────────────────┐
                         │ Name: null      │
                         │ Age:  0         │
                         └─────────────────┘
```

### Stack vs Heap

| | Stack | Heap |
|---|---|---|
| Tezlik | Tez | Sekinroq |
| Tozalash | Avtomatik (metod tugaganda) | Garbage Collector orqali |
| Nima saqlanadi | Qiymat turlar (int, bool), referencelar | Obyektlar, massivlar |
| Hajm | Kichik | Katta |

### Reference type — muhim tushuncha

```csharp
var emp1 = new Employee { Name = "Orzibek" };
var emp2 = emp1;  // Nusxa EMAS — bir xil Heap manzili!
emp2.Name = "Dilnoza";
Console.WriteLine(emp1.Name); // → "Dilnoza" (!) chunki bir xil obyektga ishora qiladi
```

Haqiqiy nusxa olish uchun yangi obyekt yaratish kerak:

```csharp
var emp2 = new Employee { Name = emp1.Name, Age = emp1.Age };
```

## 4. Kod — amalda

```csharp
public class Employee
{
    private string _name;
    public string Name
    {
        get { return _name; }
        set { _name = value; }
    }
    public int Age { get; set; }
    public string Position { get; set; }

    public Employee(string name, int age)
    {
        Name = name;
        Age = age;
    }

    public string GetInfo() => $"{Name}, {Age} yosh, {Position}";
}

var emp1 = new Employee("Orzibek", 25) { Position = "Backend Developer" };
Console.WriteLine(emp1.GetInfo());
// → Orzibek, 25 yosh, Backend Developer
```

## 5. Qo'shimcha — e'tiborga olinishi kerak bo'lgan nuqtalar

- **Value type vs Reference type**: `class` — reference type (Heapda),
  `struct` — value type (Stackda, kichik strukturalar uchun, masalan
  `Point`, `DateTime`).
- **Garbage Collector**: Heap dagi obyektlar hech kim ishora qilmay
  qolganda (no reference), GC ularni avtomatik tozalaydi. Bu .NET ning
  avtomatik xotira boshqaruvi.
- **Default constructor**: Agar siz birorta constructor yozmasangiz, C#
  parametrsiz (`public Employee() {}`) constructorni avtomatik qo'shadi.
  Lekin siz birorta parametrli constructor yozsangiz, default
  constructor avtomatik QO'SHILMAYDI — kerak bo'lsa qo'lda yozish kerak.
- **`this` kalit so'zi**: Constructor yoki metod ichida joriy obyektga
  ishora qiladi, parametr nomi maydon nomi bilan bir xil bo'lganda
  ishlatiladi: `this.Name = name;`

## 6. Imtihon savollari (o'z-o'zini tekshirish uchun)

1. `new` kalit so'zi xotirada aniq nima qiladi?
2. Quyidagi kodda natija nima va nima uchun?
   ```csharp
   var a = new Employee("Ali", 20);
   var b = a;
   b.Age = 30;
   Console.WriteLine(a.Age);
   ```
3. CLR constructor ni chaqirishdan oldin nima qiladi?
4. `class` va `struct` orasidagi asosiy farq nima (xotira nuqtai
   nazaridan)?
