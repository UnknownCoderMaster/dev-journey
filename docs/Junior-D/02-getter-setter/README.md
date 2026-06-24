# Getter, Setter — Junior D

## 1. Nima?

**Getter** — property qiymatini o'qish uchun. **Setter** — property
qiymatini yozish/o'zgartirish uchun.

```csharp
public class Employee
{
    public string Name { get; set; }
    //            ↑      ↑
    //          getter  setter
}
```

## 2. Nima uchun kerak?

Maydonni to'g'ridan ochiq (`public`) qilsak, hech kim qiymatni nazorat
qila olmaydi:

```csharp
public class Employee
{
    public int Age;  // Hech qanday himoya yo'q
}
emp.Age = -50;  // Mantiqsiz qiymat — hech kim to'xtatmaydi
```

Property orqali validatsiya qo'shish mumkin:

```csharp
public class Employee
{
    private int _age;
    public int Age
    {
        get => _age;
        set
        {
            if (value < 0)
                throw new ArgumentException("Yosh manfiy bo'lishi mumkin emas");
            _age = value;
        }
    }
}
```

## 3. Ichida nima sodir bo'ladi?

Property — bu aslida **ikkita metod**. Siz yozgan:

```csharp
public string Name { get; set; }
```

Kompilyator orqada quyidagicha generatsiya qiladi:

```csharp
private string _name;  // "backing field" — ko'rinmas maydon
public string get_Name() => _name;
public void set_Name(string value) { _name = value; }
```

IL (Intermediate Language) darajasida property — bu `get_Name()` va
`set_Name()` metodlari. Property — **syntactic sugar** (yozishni
qulaylashtirish), lekin ichida oddiy metodlar ishlaydi.

Auto-property (`{ get; set; }`) va to'liq yozilgan property — compile
bo'lgandan keyin **bir xil IL kod** hosil qiladi.

## 4. Property turlari — kod

```csharp
// Oddiy
public string Name { get; set; }

// Faqat o'qish (constructor da bir marta o'rnatiladi)
public string Id { get; }

// Tashqaridan faqat o'qish, ichkaridan yozish
public int Age { get; private set; }

// Hisoblangan property — backing field yo'q
public string FullName => $"{FirstName} {LastName}";

// Validatsiya bilan
public decimal Salary
{
    get => _salary;
    set
    {
        if (value < 0)
            throw new ArgumentException("Salary manfiy bo'lishi mumkin emas");
        _salary = value;
    }
}
```

To'liq ERP misoli:

```csharp
public class Employee
{
    private decimal _salary;

    public string Name { get; set; }
    public DateTime CreatedAt { get; }                 // faqat o'qish
    public int Age { get; private set; }               // ichkaridan yoziladi

    public decimal Salary
    {
        get => _salary;
        set
        {
            if (value < 0)
                throw new ArgumentException("Maosh manfiy bo'lishi mumkin emas");
            _salary = value;
        }
    }

    public Employee(string name, int age)
    {
        Name = name;
        Age = age;
        CreatedAt = DateTime.UtcNow;
    }

    public void Birthday() => Age++;  // faqat klass ichida o'zgaradi
}
```

## 5. Qo'shimcha — e'tiborga olinishi kerak bo'lgan nuqtalar

- **`init` accessor (C# 9+)**: faqat obyekt yaratilayotgan paytda
  o'rnatish mumkin, keyin o'zgartirib bo'lmaydi:
  ```csharp
  public string Id { get; init; }
  var emp = new Employee { Id = "123" };  // ✅ faqat shu yerda
  // emp.Id = "456";  // ❌ keyin o'zgartirib bo'lmaydi
  ```
- **Required properties (C# 11+)**: `required` modifikatori bilan
  property majburiy ekanligini bildirish mumkin.
- **Indexer**: property ning maxsus turi, `this[]` orqali — masalan
  `list[0]` kabi.
- **Backing field nomlash**: an'anaviy ravishda `_` bilan boshlanadi
  (`_name`, `_salary`) — bu C# coding convention.

## 6. Imtihon savollari

1. Quyidagi ikki kod orasida IL darajasida qanday farq bor?
   ```csharp
   // A
   public string Name { get; set; }
   // B
   private string _name;
   public string Name { get { return _name; } set { _name = value; } }
   ```
2. Nima uchun `public int Age { get; private set; }` ishlatiladi —
   oddiy `{ get; set; }` o'rniga qaysi vaziyatda?
3. `FullName => $"{FirstName} {LastName}"` uchun backing field bormi?
   Nima uchun?
4. `init` accessor `private set` dan nimasi bilan farq qiladi?
