# SOLID Principles — SRP, OCP, LSP, ISP, DIP — Junior A

## 1. Nima? (Ta'rif)

**SOLID** — obyektga yo'naltirilgan dizaynning 5 ta tamoyili:
**S**ingle Responsibility, **O**pen/Closed, **L**iskov Substitution,
**I**nterface Segregation, **D**ependency Inversion — Robert C.
Martin (Uncle Bob) tomonidan tizimlashtirilgan.

## 2. Nima uchun kerak?

SOLID'siz kod — **o'zgarishga chidamsiz**: bitta o'zgartirish
kutilmagan joylarni buzadi, test qilish qiyinlashadi. SOLID —
kodni **moslashuvchan, testlanadigan, tushunarli** qiladi.

## 3. Ichida nima sodir bo'ladi? (Mexanizm)

### 3.1 SRP — Single Responsibility Principle

"Klass — faqat **BITTA o'zgarish sababiga** ega bo'lishi kerak."

```csharp
// ❌ Buzilgan — bitta klass BIR NECHTA "o'zgarish sababi"ga ega
public class EmployeeController : ControllerBase
{
    public IActionResult Create(CreateEmployeeDto dto)
    {
        if (string.IsNullOrEmpty(dto.Name)) return BadRequest(); // Validatsiya
        var employee = new Employee { FullName = dto.Name };
        _context.Employees.Add(employee);
        _context.SaveChanges(); // DB logikasi
        _smtpClient.Send(...); // Email logikasi
        return Ok();
    }
}

// ✅ To'g'ri — MediatR Handler, HAR biri BITTA mas'uliyat
public class CreateEmployeeHandler : IRequestHandler<CreateEmployeeCommand, EmployeeDto>
{
    public async Task<EmployeeDto> Handle(CreateEmployeeCommand cmd, CancellationToken ct)
    {
        // FAQAT xodim yaratish mantig'i — validatsiya (FluentValidation), email (alohida event) — TASHQARIDA
        var employee = new Employee { FullName = cmd.Name };
        _context.Employees.Add(employee);
        await _context.SaveChangesAsync(ct);
        return _mapper.Map<EmployeeDto>(employee);
    }
}
```

"O'zgarish sababi" — masalan, "email yuborish mantig'i o'zgarsa"
— BU klass o'zgarishi KERAK EMAS (agar EmailService alohida bo'lsa).

### 3.2 OCP — Open/Closed Principle

"Kengaytirish uchun **OCHIQ**, o'zgartirish uchun **YOPIQ**."

```csharp
// ❌ Buzilgan — YANGI hisoblash turi qo'shish uchun MAVJUD kod O'ZGARTIRILADI
public class PayrollService
{
    public decimal Calculate(string employeeType, decimal baseSalary)
    {
        if (employeeType == "FullTime") return baseSalary;
        else if (employeeType == "Contractor") return baseSalary * 0.9m;
        // YANGI TUR qo'shilsa — BU METOD o'zgartirilishi SHART!
        throw new NotSupportedException();
    }
}

// ✅ To'g'ri — Strategy pattern, interfeys orqali KENGAYTIRISH
public interface ISalaryStrategy { decimal Calculate(decimal baseSalary); }
public class FullTimeSalaryStrategy : ISalaryStrategy { public decimal Calculate(decimal b) => b; }
public class ContractorSalaryStrategy : ISalaryStrategy { public decimal Calculate(decimal b) => b * 0.9m; }
// YANGI tur — YANGI KLASS, MAVJUD kod TEGILMAYDI!
```

### 3.3 LSP — Liskov Substitution Principle

"Sub-klass — bazaviy klass **O'RNIDA** ishlatilsa, dastur **TO'G'RI**
ishlashi kerak."

```csharp
// ❌ Buzilgan — Contractor'ning "BaseSalary" tushunchasi YO'Q, lekin MAJBURAN meros oladi
public class Employee { public virtual decimal MonthlySalary { get; set; } }
public class Contractor : Employee
{
    public override decimal MonthlySalary
    {
        get => throw new NotSupportedException(); // ❌ LSP BUZILDI! Employee o'rnida ISHLATILSA — CRASH!
        set => throw new NotSupportedException();
    }
}

// ✅ To'g'ri — umumiy ABSTRAKSIYA (CalculateSalary), HAR TUR o'ZIGA XOS implement qiladi
public abstract class Employee { public abstract decimal CalculateSalary(); }
public class Contractor : Employee { public override decimal CalculateSalary() => HourlyRate * Hours; }
```

**Preconditions/Postconditions:** sub-klass — bazaviy klassning
**shartlarini KUCHAYTIRMASLIGI** (masalan qo'shimcha talab
qo'shmasligi) va **natijaviy kafolatlarini KAMAYTIRMASLIGI** kerak.

### 3.4 ISP — Interface Segregation Principle

"Katta 'FAT' interfeys o'rniga — **KICHIK, MAQSADGA YO'NALTIRILGAN**
interfeyslar."

```csharp
// ❌ Buzilgan — "FAT INTERFACE"
public interface IEmployeeRepository
{
    Task<Employee> GetByIdAsync(int id);
    Task CreateAsync(Employee e);
    void GenerateAnnualReport();
    void SendBulkEmail();
}
// Faqat "GetById" kerak bo'lgan klass — BOSHQA metodlarni ham IMPLEMENT qilishga MAJBUR!

// ✅ To'g'ri — AJRATILGAN interfeyslar
public interface IEmployeeReader { Task<Employee> GetByIdAsync(int id); }
public interface IEmployeeWriter { Task CreateAsync(Employee e); }
public interface IReportGenerator { void GenerateAnnualReport(); }
```

### 3.5 DIP — Dependency Inversion Principle

"Yuqori daraja modul — past daraja modulga **TO'G'RIDAN** bog'liq
bo'lmasligi kerak — IKKALASI HAM **abstraksiyaga** bog'liq bo'lishi
kerak."

```csharp
// ❌ Buzilgan — TO'G'RIDAN konkret klassga bog'liqlik
public class EmployeeService
{
    private readonly SmtpEmailService _email = new(); // ❌ Konkret klass, TEST qilib bo'lmaydi!
}

// ✅ To'g'ri — interfeysga (abstraksiya) bog'liqlik, DI orqali INJECT qilinadi
public class EmployeeService
{
    private readonly IEmailService _email;
    public EmployeeService(IEmailService email) => _email = email; // ✅ Mock bilan TEST qilish mumkin
}
```

**IoC (Inversion of Control)** — obyektlarni yaratish/bog'lash
mas'uliyati **klassning o'zidan** **tashqi konteyner**ga
"o'tkaziladi" (invert qilinadi). DI (Dependency Injection) — IoC'ni
amalga oshirish **mexanizmi**.

## 4. Kod — SOLID + CQRS/MediatR

```csharp
public class CreateEmployeeHandler : IRequestHandler<CreateEmployeeCommand, EmployeeDto>
{
    private readonly AppDbContext _context; // DIP — abstraksiyaga (DbContext — bir turdagi abstraksiya) bog'liq
    private readonly IMapper _mapper;
    private readonly IPublishEndpoint _publisher; // DIP — RabbitMQ konkret klassga EMAS

    // SRP — BU Handler FAQAT "xodim yaratish" bilan shug'ullanadi
    public async Task<EmployeeDto> Handle(CreateEmployeeCommand cmd, CancellationToken ct)
    {
        var employee = new Employee { FullName = cmd.FullName };
        _context.Employees.Add(employee);
        await _context.SaveChangesAsync(ct);
        await _publisher.Publish(new EmployeeCreatedEvent(employee.Id), ct); // OCP — YANGI subscriber qo'shilsa, BU KOD o'zgarmaydi
        return _mapper.Map<EmployeeDto>(employee);
    }
}
```

Har bir Command/Query — **SRP**ning tabiiy amaliyoti (bitta
operatsiya = bitta Handler). **OCP** — yangi Command/Query = yangi
fayl, mavjud Handler'lar o'zgarmaydi.

### IoC Container — Circular Reference muammosi va yechimi

```csharp
public class ServiceA { public ServiceA(ServiceB b) { } }
public class ServiceB { public ServiceB(ServiceA a) { } } // 💥 Circular dependency!
```

```
DI Container — ServiceA yaratish uchun ServiceB, ServiceB yaratish
uchun ServiceA kerak — CHEKSIZ TSIKL, runtime XATOSI.

Yechim:
1. Dizaynni QAYTA KO'RIB CHIQISH (odatda BU — SRP buzilgani belgisi)
2. Umumiy mantiqni UCHINCHI (ServiceC) klassga CHIQARISH
3. Event/MediatR orqali BOG'LIQLIKNI "bo'shashtirish"
```

### DI Lifetimes — Scoped, Transient, Singleton

```
Singleton — BUTUN ilova umri davomida BITTA instance
             ✅ Holatsiz servislar (masalan IEmailService)
             ❌ DbContext (thread-safety buziladi!)

Scoped — HAR HTTP so'rov uchun YANGI instance
          ✅ DbContext, request-scoped ma'lumot

Transient — HAR inject so'ralganda YANGI instance
             ✅ Yengil, holatsiz obyektlar (validatorlar)

⚠️ "Captive Dependency": Singleton ICHIGA Scoped inject qilinsa —
   Scoped servis BIR MARTA yaratilib, "QAMALIB" qoladi (hech qachon
   yangilanmaydi) — bu XAVFLI antipattern.
```

### YAGNI, KISS, DRY — qisqacha

```
YAGNI (You Aren't Gonna Need It) — "kelajakda kerak BO'LISHI MUMKIN"
  deb HOZIR ORTIQCHA FUNKSIONALLIK QO'SHMASLIK

KISS (Keep It Simple, Stupid) — MURAKKAB yechim o'RNIGA ODDIY
  yechimni TANLASH

DRY (Don't Repeat Yourself) — BIR XIL mantiqni BIR NECHTA joyda
  TAKRORLAMASLIK (extract method/klass orqali)
```

## 5. Qachon ishlatish kerak?

| Tamoyil | Amaliy qo'llanish |
|---|---|
| SRP | Handler/Service dizayni — har doim |
| OCP | To'lov turi, notification kanali kabi kengayadigan tizimlar |
| LSP | Inheritance ishlatilganda — HAR DOIM tekshirish |
| ISP | Katta interfeysni bo'lish, mock qilish osonlashadi |
| DIP | Har doim — testability uchun MAJBURIY |

## 6. Muhim nuqtalar

- SOLID — **qat'iy qonun emas**, balki yo'l-yo'riq — har doim 100%
  rioya qilish shart emas, ayniqsa kichik/prototip kodda.
- DIP va DI (Dependency Injection) — BIR XIL narsa EMAS — DIP
  tamoyil, DI — uni amalga oshirish mexanizmi.
- "Fat interface" muammosi — ko'pincha ISP'ni buzadi, lekin BUNI
  aniqlashning belgisi — klass INTERFEYSNING FAQAT bir qismini
  IMPLEMENT qilishga MAJBUR bo'lishi.

## 7. Imtihon savollari

1. SRP'da "o'zgarish sababi" nimani anglatadi?
2. OCP qanday amalga oshiriladi — misol bilan tushuntiring.
3. LSP buzilgan holatni qanday aniqlash mumkin?
4. ISP nima muammoni (fat interface) hal qiladi?
5. DIP va Dependency Injection orasidagi farq nima?
6. "Captive Dependency" muammosi qanday yuzaga keladi?
7. IoC Container'da circular dependency qanday hal qilinadi?
8. YAGNI, KISS, DRY tamoyillarini qisqacha tushuntiring.
