# SOLID-based Architecture Decisions — Middle D

## 1. Nima? (Ta'rif)

**SOLID** — obyektga yo'naltirilgan dizaynning 5 ta asosiy tamoyili:
**S**ingle Responsibility, **O**pen/Closed, **L**iskov Substitution,
**I**nterface Segregation, **D**ependency Inversion.

## 2. Nima uchun kerak?

SOLID'ga rioya qilmagan kod — **o'zgarishga chidamsiz**: bitta
o'zgarish butun tizimni buzadi, test qilish qiyinlashadi, yangi
funksiya qo'shish mavjud kodni **o'zgartirishni** talab qiladi
(yangi kod qo'shish o'rniga).

## 3. Ichida nima sodir bo'ladi? (Mexanizm)

### 3.1 SRP — Single Responsibility Principle

```csharp
// ❌ Buzilgan — bitta klass BIR NECHTA mas'uliyatga ega
public class EmployeeService
{
    public void CreateEmployee(Employee e) { /* DB saqlash */ }
    public void SendWelcomeEmail(Employee e) { /* SMTP */ }
    public void GeneratePdfContract(Employee e) { /* PDF yaratish */ }
    public void ValidateEmployee(Employee e) { /* validatsiya */ }
}

// ✅ To'g'ri — HAR klass BITTA mas'uliyat
public class EmployeeRepository { public void Create(Employee e) { } }
public class EmailService { public void SendWelcome(Employee e) { } }
public class ContractPdfGenerator { public byte[] Generate(Employee e) => ...; }
public class EmployeeValidator { public bool IsValid(Employee e) => ...; }
```

MediatR Handler'lar — SRP'ning tabiiy amaliyoti: **har Handler —
bitta Command/Query uchun bitta mas'uliyat**.

### 3.2 OCP — Open/Closed Principle

```csharp
// ❌ Buzilgan — YANGI to'lov turi qo'shish uchun MAVJUD kodni O'ZGARTIRISH kerak
public class PaymentProcessor
{
    public void Process(string type, decimal amount)
    {
        if (type == "CreditCard") { /* ... */ }
        else if (type == "PayPal") { /* ... */ }
        // YANGI tur qo'shilsa — bu METOD O'ZGARTIRILISHI kerak!
    }
}

// ✅ To'g'ri — interfeys orqali KENGAYTIRISH, MAVJUD kod O'ZGARMAYDI
public interface IPaymentMethod { void Process(decimal amount); }
public class CreditCardPayment : IPaymentMethod { public void Process(decimal amount) { } }
public class PayPalPayment : IPaymentMethod { public void Process(decimal amount) { } }
// YANGI tur — YANGI KLASS, mavjud kod TEGILMAYDI!
```

"Open for extension, closed for modification" — kengaytirishga
**ochiq**, o'zgartirishga **yopiq**.

### 3.3 LSP — Liskov Substitution Principle

```csharp
// ❌ Buzilgan — sub-klass BAZAVIY klass "shartnomasini" BUZADI
public class Rectangle
{
    public virtual int Width { get; set; }
    public virtual int Height { get; set; }
    public int Area => Width * Height;
}

public class Square : Rectangle
{
    public override int Width { set { base.Width = base.Height = value; } }
    public override int Height { set { base.Width = base.Height = value; } }
    // Square — Rectangle "o'rnida" ishlatilsa, KUTILMAGAN xatti-harakat!
}

// Test:
Rectangle r = new Square();
r.Width = 5; r.Height = 10;
Console.WriteLine(r.Area); // Rectangle bo'lsa 50 kutiladi, lekin Square'da 100!
```

LSP — sub-klass **bazaviy klass o'rnida ishlatilsa ham**, dastur
**to'g'ri** ishlashi kerak degan tamoyil.

### 3.4 ISP — Interface Segregation Principle

```csharp
// ❌ Buzilgan — KATTA, HAMMA narsani o'z ichiga olgan interfeys
public interface IEmployeeOperations
{
    void Create(Employee e);
    void Delete(int id);
    void GenerateReport();
    void SendNotification();
}
// Faqat "Create" kerak bo'lgan klass ham BOSHQA metodlarni IMPLEMENT qilishga MAJBUR!

// ✅ To'g'ri — KICHIK, MAQSADGA YO'NALTIRILGAN interfeyslar
public interface IEmployeeWriter { void Create(Employee e); void Delete(int id); }
public interface IReportGenerator { void GenerateReport(); }
public interface INotifier { void SendNotification(); }
```

### 3.5 DIP — Dependency Inversion Principle

```csharp
// ❌ Buzilgan — YUQORI daraja KONKRET (past daraja) klassga TO'G'RIDAN bog'liq
public class EmployeeService
{
    private readonly SmtpEmailService _emailService = new(); // KONKRET klass!
}

// ✅ To'g'ri — ABSTRAKSIYAGA (interfeys) bog'liqlik
public class EmployeeService
{
    private readonly IEmailService _emailService; // Interfeys!
    public EmployeeService(IEmailService emailService) => _emailService = emailService; // DI orqali
}
```

"Yuqori daraja modullar past daraja modullarga bog'liq bo'lmasligi
kerak — IKKALASI HAM abstraksiyaga bog'liq bo'lishi kerak."

### 3.6 SOLID va CQRS/MediatR

```
SRP — Har Handler = bitta operatsiya (Command/Query)
OCP — Yangi Command/Query = YANGI Handler, mavjudlarga TEGILMAYDI
ISP — IRequestHandler<TRequest, TResponse> — KICHIK, aniq interfeys
DIP — Controller — IMediator'ga (abstraksiya) bog'liq, Handler'larga
      TO'G'RIDAN EMAS
```

### 3.7 IoC Container — Circular Reference muammosi

```csharp
public class ServiceA { public ServiceA(ServiceB b) { } }
public class ServiceB { public ServiceB(ServiceA a) { } } // 💥 Circular dependency!
```

```
DI Container — ServiceA'ni yaratish uchun ServiceB kerak, ServiceB'ni
yaratish uchun ServiceA kerak — CHEKSIZ TSIKL!

Yechim:
  1. Dizaynni QAYTA KO'RIB CHIQISH (odatda BU — dizayn XATOSI belgisi)
  2. Umumiy mantiqni UCHINCHI klassga (ServiceC) CHIQARISH
  3. Lazy<T> orqali KECHIKTIRILGAN resolve (KAMDAN-KAM tavsiya etiladi)
```

### 3.8 DI Container — Scoped, Transient, Singleton

```
Singleton — BUTUN ilova umri davomida BITTA instance
Scoped    — HAR HTTP so'rov uchun YANGI instance
Transient — HAR INJECT so'ralganda YANGI instance

Qoida: Singleton — Scoped'ga BOG'LIQ BO'LMASLIGI kerak ("Captive
Dependency" muammosi — Singleton BIR MARTA yaratilganda, Scoped
servis ICHIGA "QAMALIB" qoladi, hech qachon yangilanmaydi)
```

## 4. Kod — DI lifetime to'g'ri tanlash

```csharp
builder.Services.AddSingleton<IEmailService, SmtpEmailService>(); // Holatsiz, xavfsiz Singleton
builder.Services.AddScoped<AppDbContext>();                        // Har so'rov uchun
builder.Services.AddTransient<IValidator<CreateEmployeeDto>, CreateEmployeeValidator>(); // Yengil, holatsiz
```

## 5. Qachon ishlatish kerak?

| Tamoyil | Qachon eng ko'p qo'llaniladi |
|---|---|
| SRP | Har doim — Handler/Service dizaynida |
| OCP | Yangi turlar tez-tez qo'shiladigan tizimlarda (to'lov, bildirishnoma) |
| LSP | Meros olish (inheritance) ishlatilganda |
| ISP | Katta interfeyslarni bo'lib, moslashuvchan qilishda |
| DIP | Har doim — testability va moslashuvchanlik uchun |

## 6. Muhim nuqtalar

- SOLID — **qat'iy qoida emas**, balki **yo'l ko'rsatuvchi
  tamoyillar** — har doim 100% rioya qilish shart emas, ayniqsa
  kichik/vaqtinchalik kodda.
- DIP — Dependency Injection bilan **bir xil narsa emas** — DIP
  tamoyil, DI esa uni amalga oshirish **mexanizmi**.
- Captive Dependency — Singleton ichiga Scoped inject qilish — DI
  Container **runtime xatosi** beradi (agar validatsiya yoqilgan
  bo'lsa) yoki **sokin** noto'g'ri ishlaydi.

## 7. Imtihon savollari

1. SRP nima va MediatR Handler'lar bu tamoyilga qanday mos keladi?
2. OCP'ni buzuvchi va unga rioya qiluvchi ikki kod misolini
   solishtiring.
3. LSP nima va uni buzadigan klassik misol (Rectangle/Square) nima
   uchun muammoli?
4. ISP qanday muammoni (katta interfeys) hal qiladi?
5. DIP va Dependency Injection orasidagi farq nima?
6. "Captive Dependency" muammosi nima va u qaysi DI lifetime
   kombinatsiyasida yuzaga keladi?
