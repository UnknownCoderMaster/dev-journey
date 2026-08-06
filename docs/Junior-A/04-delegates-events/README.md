# Delegates, Events, Lambda, Action, Func, Predicate — Junior A

## 1. Nima? (Ta'rif)

**Delegate** — **type-safe metod pointeri** — metodni **o'zgaruvchi**
sifatida saqlash, uzatish, chaqirish imkonini beruvchi tur.
**Event** — delegate asosida qurilgan, **inkapsulyatsiya qilingan**
"xabar berish" mexanizmi (Publisher-Subscriber pattern).

## 2. Nima uchun kerak?

Ba'zida metodni **o'zgaruvchi sifatida** boshqa metodga uzatish
kerak (masalan, "shu shart bajarilganda — QUYIDAGI metodni
chaqir"). Delegate — bu imkoniyatni **type-safe** (compiler
tekshiradigan) tarzda beradi — C/C++ dagi xavfli funksiya
pointerlaridan farqli.

## 3. Ichida nima sodir bo'ladi? (Mexanizm)

### 3.1 Delegate e'lon qilish, instantiate, invoke

```csharp
public delegate int MathOperation(int a, int b); // Delegate TUR e'loni

public class Calculator
{
    public static int Add(int a, int b) => a + b;
}

MathOperation op = Calculator.Add; // Instantiate — METODNI o'zgaruvchiga BIRIKTIRISH
int result = op(5, 3);              // Invoke — CHAQIRISH, xuddi ODDIY metod kabi
```

### 3.2 Multicast Delegate — bir nechta metod

```csharp
Action<string> log = Console.WriteLine;
log += msg => File.AppendAllText("log.txt", msg); // += — YANA BIR metod QO'SHILADI

log("Xabar"); // IKKALA metod HAM KETMA-KET chaqiriladi!

log -= Console.WriteLine; // -= — metodni RO'YXATDAN OLIB TASHLASH
```

```
⚠️ Agar delegate QIYMAT qaytarsa (masalan Func<int>), multicast
   holatda — FAQAT OXIRGI chaqirilgan metodning natijasi QAYTARILADI
   (oldingilarining natijasi "yo'qoladi")!
```

### 3.3 CLR'da delegate — qanday saqlanadi

```
Delegate — CLR'da MAXSUS KLASS (System.MulticastDelegate'dan meros)
sifatida IMPLEMENT qilingan. Ichida:
  - Target — QAYSI obyektga tegishli (instance metod bo'lsa)
  - Method — METOD POINTER (IntPtr)
  - Invocation List — multicast holatda, BARCHA biriktirilgan
    metodlar RO'YXATI (massiv)

op(5, 3) chaqirilganda — CLR invocation list bo'ylab, HAR bir
metodni KETMA-KET chaqiradi.
```

### 3.4 Event — delegate asosida, encapsulated

```csharp
public class EmployeeService
{
    // ❌ Public delegate — TASHQARIDAN istalgan kod = (assignment) qilib, BARCHA subscriber'larni
    //    O'CHIRIB TASHLASHI mumkin!
    public Action<Employee>? OnEmployeeCreated;

    // ✅ event — FAQAT += / -= RUXSAT ETILADI (TASHQARIDAN), Invoke FAQAT klass ICHIDA
    public event Action<Employee>? EmployeeCreated;

    public void Create(Employee emp)
    {
        // ... saqlash
        EmployeeCreated?.Invoke(emp); // ?. — HECH KIM OBUNA bo'lmasa, NullReferenceException oldini oladi
    }
}
```

```
event kalit so'zi — delegate ustiga QO'SHIMCHA "himoya" qatlami
qo'shadi: TASHQI kod FAQAT += / -= qila oladi, LEKIN:
  ❌ service.EmployeeCreated = null;      (TASHQARIDAN — MUMKIN EMAS!)
  ❌ service.EmployeeCreated.Invoke(emp); (TASHQARIDAN chaqirib bo'lmaydi!)
  ✅ service.EmployeeCreated += Handler;  (FAQAT OBUNA bo'lish mumkin)
```

### 3.5 EventHandler, EventArgs — standart pattern

```csharp
public class EmployeeCreatedEventArgs : EventArgs
{
    public int EmployeeId { get; }
    public EmployeeCreatedEventArgs(int id) => EmployeeId = id;
}

public class EmployeeService
{
    public event EventHandler<EmployeeCreatedEventArgs>? EmployeeCreated;

    public void Create(Employee emp)
    {
        EmployeeCreated?.Invoke(this, new EmployeeCreatedEventArgs(emp.Id));
        // Standart .NET konvensiyasi: (object? sender, TEventArgs e)
    }
}

// Subscriber
service.EmployeeCreated += (sender, args) =>
    Console.WriteLine($"Yangi xodim: {args.EmployeeId}");
```

### 3.6 Anonymous function va Lambda

```csharp
// Anonymous method (C# 2.0)
Func<int, int> doubleIt = delegate (int x) { return x * 2; };

// Lambda — Expression (qiymat qaytaradi, {} YO'Q)
Func<int, int> doubleLambda = x => x * 2;

// Lambda — Statement (BLOK, {} BOR)
Func<int, int> doubleStatement = x => { var result = x * 2; return result; };

// Ko'p parametrli
Func<int, int, int> add = (x, y) => x + y;
```

### 3.7 Closure — outer variable capture

```csharp
public Func<int> CreateCounter()
{
    int count = 0; // LOCAL o'zgaruvchi
    return () => ++count; // Lambda — 'count'ni "USHLAB QOLADI" (CAPTURE)
}

var counter = CreateCounter();
Console.WriteLine(counter()); // 1
Console.WriteLine(counter()); // 2 — 'count' HALI ESLAB QOLINGAN!
```

```
Mexanizm: `count` — ODATDA Stack'da bo'lishi kerak edi (metod
tugagach YO'QOLISHI kerak), LEKIN lambda uni ISHLATGANI uchun —
COMPILER `count`ni YASHIRIN KLASS (closure klassi) FIELD'IGA
KO'CHIRADI, va bu klass — HEAP'da yashaydi. Shuning uchun
CreateCounter() TUGASA HAM, `count` "TIRIK" QOLADI (chunki lambda
— Heap'dagi closure obyektiga ISHORA qiladi).
```

### 3.8 `Action<T>`, `Func<T, TResult>`, `Predicate<T>`

```csharp
Action<string> print = msg => Console.WriteLine(msg);         // VOID qaytaradi
Func<int, int, int> sum = (a, b) => a + b;                    // QIYMAT qaytaradi (OXIRGI generic parametr — natija turi)
Predicate<Employee> isAdult = emp => emp.Age >= 18;            // BOOL qaytaradi

Action noParam = () => Console.WriteLine("Salom");
Func<int> getRandom = () => new Random().Next();
```

```
Action<T>    — 0 dan 16 gacha parametr, VOID
Func<T,R>    — 0 dan 16 gacha parametr + NATIJA turi, OXIRGI generic — QAYTARILADIGAN TUR
Predicate<T> — 1 parametr, ALOHIDA "bool qaytaradi" nomlangan delegate (Func<T,bool> bilan FUNKSIONAL bir xil)
```

### 3.9 LINQ bilan birga — Where, Select, OrderBy

```csharp
List<Employee> employees = GetEmployees();

var adults = employees.Where(e => e.Age >= 18);           // Predicate<Employee> (yoki Func<T,bool>)
var names = employees.Select(e => e.FullName);              // Func<Employee, string>
var sorted = employees.OrderBy(e => e.HiredAt);              // Func<Employee, DateTime>
```

LINQ metodlari — ICHKARIDA `Func<T,...>` delegate qabul qiladi —
lambda ifodalar ularga **to'g'ridan** uzatiladi (compiler AVTOMATIK
delegate'ga aylantiradi).

### 3.10 Real misol — MediatR Notification Handler

```csharp
public record EmployeeCreatedNotification(int EmployeeId) : INotification;

public class SendWelcomeEmailHandler : INotificationHandler<EmployeeCreatedNotification>
{
    public async Task Handle(EmployeeCreatedNotification notification, CancellationToken ct)
        => await _emailService.SendAsync(notification.EmployeeId);
}

public class LogEmployeeCreatedHandler : INotificationHandler<EmployeeCreatedNotification>
{
    public Task Handle(EmployeeCreatedNotification notification, CancellationToken ct)
    {
        _logger.LogInformation("Xodim yaratildi: {Id}", notification.EmployeeId);
        return Task.CompletedTask;
    }
}

// _mediator.Publish(new EmployeeCreatedNotification(emp.Id)) chaqirilganda —
// IKKALA Handler HAM chaqiriladi — bu, MOHIYATAN, "multicast delegate/event"
// g'oyasining CQRS/MediatR'dagi KENGAYTIRILGAN ko'rinishi.
```

## 4. Kod — to'liq Publisher-Subscriber misoli

```csharp
public class OrderProcessor
{
    public event EventHandler<OrderProcessedEventArgs>? OrderProcessed;

    public void Process(Order order)
    {
        // ... qayta ishlash mantig'i
        OrderProcessed?.Invoke(this, new OrderProcessedEventArgs(order.Id));
    }
}

public class OrderProcessedEventArgs : EventArgs
{
    public int OrderId { get; }
    public OrderProcessedEventArgs(int orderId) => OrderId = orderId;
}

var processor = new OrderProcessor();
processor.OrderProcessed += (s, e) => Console.WriteLine($"Buyurtma {e.OrderId} qayta ishlandi");
processor.Process(new Order { Id = 1 });
```

## 5. Qachon ishlatish kerak?

| Vaziyat | Yechim |
|---|---|
| Metodni parametr sifatida uzatish | Delegate/`Func`/`Action` |
| "Nimadir sodir bo'ldi" xabarini bir nechta joyga | `event` |
| LINQ filter/transformatsiya | Lambda (`Func<T,bool>`, `Func<T,R>`) |
| Domenlar orasida bog'liqlikni "bo'shashtirish" | Event/MediatR Notification |

## 6. Muhim nuqtalar

- Public `Action`/`Func` field — event'dan farqli, TASHQARIDAN
  `null`ga tenglashtirilishi yoki chaqirilishi mumkin — **xavfsizlik
  uchun `event`** afzal.
- Closure — o'zgaruvchini **Heap**ga "ko'chiradi" — bu ozgina
  performance narxi bor, lekin amaliy jihatdan **muhim emas**
  (faqat juda yuqori chastotali kodda e'tiborga olinadi).
- Multicast delegate'da EXCEPTION — birinchi metodda XATO bo'lsa,
  **QOLGAN** metodlar chaqirilMAYDI (zanjir TO'XTAYDI).

## 7. Imtihon savollari

1. Delegate nima va u nima uchun "type-safe metod pointeri"
   hisoblanadi?
2. `event` kalit so'zi oddiy public delegate field'dan qanday
   himoya qo'shadi?
3. Closure qanday ishlaydi — o'zgaruvchi nima uchun Heap'ga
   "ko'chiriladi"?
4. `Action<T>`, `Func<T,R>` va `Predicate<T>` orasidagi farq nima?
5. Multicast delegate'da bitta metod EXCEPTION tashlasa, nima
   sodir bo'ladi?
6. `EventHandler<TEventArgs>` standart patterni nima uchun
   ishlatiladi?
7. MediatR Notification — event/delegate g'oyasi bilan qanday
   bog'liq?
