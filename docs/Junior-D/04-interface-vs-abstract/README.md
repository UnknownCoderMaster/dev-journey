# Interface vs Abstract Class — Junior D

## 1. Nima?

Ikkalasi ham "qanday bo'lishi kerak"ligini belgilaydi, lekin to'liq
emas — boshqa klass to'ldirishi kerak.

```csharp
// Interface — faqat shartnoma
public interface IEmployee
{
    string GetInfo();
}

// Abstract class — qisman implementatsiya + qisman bo'sh joy
public abstract class Person
{
    public string Name { get; set; }       // to'liq amalga oshirilgan
    public abstract string GetInfo();      // bo'sh — meros olgan to'ldiradi
}
```

## 2. Nima uchun kerak?

Turli klasslar umumiy xususiyatga ega, lekin har xil ishlaydi:

```csharp
public interface IHasInfo
{
    string GetInfo();
}

public class Employee : IHasInfo { public string GetInfo() => "Employee..."; }
public class Customer : IHasInfo { public string GetInfo() => "Customer..."; }

List<IHasInfo> items = new() { new Employee(), new Customer() };
foreach (var item in items)
    Console.WriteLine(item.GetInfo());
```

## 3. Ichida nima sodir bo'ladi? (CLR/xotira darajasida)

### Nima uchun bitta abstract class, lekin ko'p interface?

**Sabab — xotira tartibida (memory layout) yotadi.**

Klass obyekti Heap da **chiziqli (linear) blok** sifatida joylashadi:

```csharp
public abstract class Animal
{
    public string Name;   // offset: 8
    public int Age;       // offset: 16
}

public class Dog : Animal
{
    public string Breed;  // offset: 20
}
```

```
Dog obyekti xotirada:
┌─────────────────┐
│ Type pointer     │ ← 0-8 byte
│ Name (Animal'dan)│ ← 8-16 byte
│ Age  (Animal'dan)│ ← 16-20 byte
│ Breed (Dog'dan)  │ ← 20-28 byte
└─────────────────┘
```

Agar 2 ta klassdan meros olish mumkin bo'lsa edi — ikkala ota klass ham
o'z maydonlarini bir xil offsetdan boshlashni "kutadi". Bu **Diamond
Problem** deyiladi va xotira joylashuvini chigallashtiradi. Shuning
uchun C# da klasslardan faqat **bitta** dan meros olish mumkin (single
inheritance).

Interface esa **hech qanday maydon, hech qanday xotira offset talab
qilmaydi.** U faqat "klass shu metodga ega bo'lishi SHART" degan
kontrakt:

```
Bird obyekti xotirada:
┌─────────────────┐
│ Type pointer     │  ← Bu pointer orqali CLR "Bird IFlyable
│ Name (Animal'dan)│     ekanligini" biladi (Interface Method
│ Age  (Animal'dan)│     Table — IMT orqali)
└─────────────────┘
   IFlyable uchun alohida joy yo'q!
```

CLR runtime da **Interface Method Table (IMT)** orqali qaysi haqiqiy
metodga borishni hal qiladi — xotira tuzilishini buzmaydi. Shuning
uchun bir klass **ko'p interfeys** implement qila oladi:

```csharp
public class Employee : IHasInfo, IComparable, IDisposable { }
```

### Xulosa — bir jumlada

```
Klass = "Men shu maydonlarga EGAMAN" (xotira band qiladi)
Interface = "Men shu metodlarni BAJARAMAN" (xotira band qilmaydi, va'da)
Xotira band qiluvchi narsalardan FAQAT BITTASI bo'lishi mumkin
Va'da beruvchi narsalardan esa XOHLAGANCHA bo'lishi mumkin
```

## 4. IS-A vs CAN-DO

```
Abstract class:
  "IS-A" munosabat — Employee IS-A Person
  Umumiy KOD bo'lishi mumkin
  Faqat BITTA dan meros olinadi

Interface:
  "CAN-DO" munosabat — Employee CAN-DO GetInfo
  Faqat SHARTNOMA (C# 8+ da default method ham bo'lishi mumkin)
  KO'P interfeys implement qilish mumkin
```

## 5. Kod — amalda ERP misoli

```csharp
public abstract class Employee
{
    public string Name { get; set; }
    public DateTime HireDate { get; set; }

    public int GetYearsOfService() => DateTime.Now.Year - HireDate.Year;
    public abstract decimal CalculateSalary();
}

public class FullTimeEmployee : Employee
{
    public decimal MonthlySalary { get; set; }
    public override decimal CalculateSalary() => MonthlySalary;
}

public class Contractor : Employee
{
    public decimal HourlyRate { get; set; }
    public int HoursWorked { get; set; }
    public override decimal CalculateSalary() => HourlyRate * HoursWorked;
}

public interface IEmailNotifiable
{
    string Email { get; }
    Task SendNotificationAsync(string message);
}

public class FullTimeEmployee : Employee, IEmailNotifiable
{
    public string Email { get; set; }
    public async Task SendNotificationAsync(string message) { /* ... */ }
}
```

## 6. Qo'shimcha — e'tiborga olinishi kerak bo'lgan nuqtalar

- **Virtual vs Abstract metod**: `virtual` metod — default implementatsiyaga
  ega, meros olgan klass `override` qilishi **majburiy emas**.
  `abstract` metod — implementatsiyasi yo'q, meros olgan klass `override`
  qilishi **majburiy**.
- **Abstract class constructor bo'la oladi**, lekin to'g'ridan
  `new AbstractClass()` qilib bo'lmaydi — faqat meros olgan klass
  konstruktor orqali chaqiradi (`base()`).
- **Interface da field (maydon) bo'lishi mumkin emas** — faqat property,
  metod, event, indexer. Lekin C# 8+ dan static field mumkin bo'ldi.
- **Sealed klass**: `sealed` bilan belgilangan klassdan boshqa meros
  olib bo'lmaydi — bu abstract classning aksi (abstract — majburan
  meros olinadi, sealed — meros olib bo'lmaydi).
- **Diamond Problem** interfeyslarda ham nazariy paydo bo'lishi mumkin
  (ikki interfeys bir xil default method nomiga ega bo'lsa, C# 8+),
  lekin bu klasslardagi xotira konfliktidan farqli — bu yerda kompilyator
  shunchaki "qaysi birini ishlatishni aniq ko'rsating" deb xato beradi,
  xotira muammosi emas.

## 7. Imtihon savollari

1. Nima uchun C# da bir nechta abstract classdan meros olib bo'lmaydi,
   lekin bir nechta interface implement qilish mumkin? (CLR/xotira
   nuqtai nazaridan javob bering)
2. "Dog", "Cat", "Bird" klasslari bor — hammasi umumiy "Animal" (Name,
   Age). Faqat "Dog" va "Bird" maxsus qobiliyatga ega bo'lishi kerak
   (har biri farqli — uchish, hurish). Qaysi yondashuvni tanlardingiz?
3. C# 8.0 dan keyin interfeys default method (kod bilan) yoza oladi.
   Bu interfeys va abstract class farqini yo'qotadimi? Qaysi farq hali
   ham saqlanadi?
4. `virtual` va `abstract` metod orasidagi farq nima?
