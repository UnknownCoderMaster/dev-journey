# Access Modifiers — Junior D

## 1. Nima?

Access modifier — klass, metod, property kim tomonidan ko'rinishi va
ishlatilishi mumkinligini belgilaydi.

```csharp
public class Employee
{
    private string _ssn;         // Faqat shu klass ichida
    public string Name;           // Hamma joydan
    protected int Salary;         // Shu klass + meros olganlar
    internal string Department;   // Faqat shu assembly (.dll) ichida
}
```

## 2. Nima uchun kerak?

**Encapsulation** (yashirish) prinsipi — har kim har narsaga
aralashmasligi kerak:

```csharp
public class BankAccount
{
    private decimal _balance;  // Tashqaridan to'g'ridan o'zgartirib bo'lmaydi

    public void Deposit(decimal amount)
    {
        if (amount <= 0) throw new ArgumentException("Noto'g'ri summa");
        _balance += amount;
    }
}
```

## 3. Ichida nima sodir bo'ladi?

Access modifier tekshiruvi **compile-time** da bo'ladi, runtime da emas.

```
Siz yozasiz: _balance ni tashqaridan chaqirasiz
       ↓
Kompilyator: "Bu private — ruxsat yo'q!"
       ↓
CS0122 xatosi — Compile vaqtida to'xtaydi
       ↓
.dll/.exe hech qachon yaratilmaydi
```

Bu C# da Java dagidan farqli — access modifier buzilishi runtime
exception emas, balki **compile xatosi**.

Reflection orqali texnik jihatdan "chetlab o'tish" mumkin
(`BindingFlags.NonPublic`), lekin bu maxsus va yomon amaliyot
hisoblanadi, oddiy kodda ishlatilmaydi.

## 4. Barcha access modifierlar — jadval

| Modifier | Shu klass | Meros olgan (boshqa assembly) | Shu assembly | Boshqa assembly |
|---|---|---|---|---|
| `public` | ✅ | ✅ | ✅ | ✅ |
| `private` | ✅ | ❌ | ❌ | ❌ |
| `protected` | ✅ | ✅ | ❌ | ❌ |
| `internal` | ✅ | ❌ | ✅ | ❌ |
| `protected internal` | ✅ | ✅ | ✅ | ❌ |
| `private protected` | ✅ | ✅ (faqat shu assembly) | ❌ | ❌ |

### Combo modifierlar mantiqi

**`protected internal` — OR mantiqi** (kengroq ochiqlik):
```
Ruxsat = protected EDI YOKI internal EDI
Ikkisidan BIRI yetarli
```

**`private protected` — AND mantiqi** (torroq ochiqlik):
```
Ruxsat = private(assembly) EDI VA protected EDI (bir vaqtda)
Ikkisi BIRGALIKDA kerak
```

C# da boshqa kombinatsiya yo'q (jami 6 ta access modifier: 4 yakka + 2
combo). Boshqa kombinatsiyalar mantiqsiz bo'lardi (masalan `public
private` — "hammaga ochiq VA hech kimga ochiq emas" — ziddiyat).

## 5. Kod — amalda

```csharp
public class Employee
{
    public int Id { get; private set; }
    public string Name { get; set; }
    protected decimal BaseSalary;
    internal string InternalNotes { get; set; }
    private List<string> _auditLog = new();

    public void AddAuditLog(string message) => _auditLog.Add(message);
}

public class Manager : Employee
{
    public void GiveRaise(decimal amount)
    {
        BaseSalary += amount;  // ✅ protected — meros olgan klass kira oladi
    }
}
```

## 6. Qo'shimcha — e'tiborga olinishi kerak bo'lgan nuqtalar

- **`file` access modifier (C# 11+)**: faqat shu `.cs` fayl ichida
  ko'rinadi — source generator larda ishlatiladi.
- **Default access modifier**: agar hech narsa yozmasangiz, klass uchun
  default `internal`, klass ichidagi a'zolar uchun default `private`.
- **Top-level klass** (`internal class X {}`) `public` bo'lmasa, faqat
  shu loyiha (assembly) ichida ishlatiladi — bu kutubxona yozishda muhim
  (tashqi foydalanuvchilarga faqat kerakli klasslarni `public` qilish).
- **Nested klasslar** uchun `private` ham mumkin — tashqi klass ichida
  yashirin yordamchi klass yaratish uchun.

## 7. Imtihon savollari

1. `protected` va `internal` orasidagi asosiy farq nima?
2. Quyidagi holatda compile xatosi bo'ladimi?
   ```csharp
   // Assembly A
   public class Employee { protected internal string Notes; }
   // Assembly B (meros OLMAGAN holda)
   var emp = new Employee();
   emp.Notes = "test";
   ```
3. Nima uchun `private protected` kamdan-kam ishlatiladi?
4. Default access modifier klass uchun va klass a'zolari uchun nima?
