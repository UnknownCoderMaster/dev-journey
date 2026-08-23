# OOP — Encapsulation, Inheritance, Polymorphism, Abstraction — Junior A

## 1. Nima? (Ta'rif)

**OOP (Object-Oriented Programming)** — dasturni **obyektlar**
(ma'lumot + xatti-harakat birligi) atrofida quruvchi paradigma.
To'rtta ustuni: **Encapsulation** (inkapsulyatsiya), **Inheritance**
(meros), **Polymorphism** (ko'p shakllilik), **Abstraction**
(abstraksiya).

## 2. Nima uchun kerak?

OOP'siz — ma'lumot va uni qayta ishlovchi funksiyalar **ajralgan**
holda bo'ladi (procedural dasturlash), bu katta loyihalarda
**tartibsizlik**ka olib keladi. OOP — real dunyodagi obyektlarni
(Employee, Department) **tabiiy** modellashtirish, kodni **qayta
ishlatish** va **kengaytirish**ni osonlashtiradi.

## 3. Ichida nima sodir bo'ladi? (Mexanizm)

### 3.1 Encapsulation — ma'lumotni yashirish

```csharp
// ❌ XAVFLI — public field, hech qanday nazorat yo'q
public class Employee
{
    public decimal Salary; // Istalgan joydan, ISTALGAN qiymatga o'zgartirilishi mumkin!
}

var emp = new Employee();
emp.Salary = -5000; // ❌ Mantiqsiz, lekin COMPILE bo'ladi!
```

```csharp
// ✅ TO'G'RI — property orqali nazorat
public class Employee
{
    private decimal _salary; // Backing field — HAQIQIY ma'lumot shu yerda saqlanadi

    public decimal Salary
    {
        get => _salary;
        set
        {
            if (value < 0) throw new ArgumentException("Maosh manfiy bo'lishi mumkin emas");
            _salary = value;
        }
    }
}
```

**Property vs Field:**
```
Field    — TO'G'RIDAN xotiraga murojaat, NAZORAT yo'q
Property — get/set METODLARI orqali (compiler buni "yashiradi"),
           validatsiya/logika QO'SHISH mumkin

Auto-property: public string Name { get; set; }
  Compiler ICHKARIDA — AVTOMATIK backing field yaratadi
  (masalan <Name>k__BackingField) — buni SIZ ko'rmaysiz, lekin
  IL darajasida MAVJUD.
```

**Access modifiers:**
```
public              — HAMMA joydan ko'rinadi
private             — FAQAT shu klass ichida
protected           — shu klass VA undan meros olganlar
internal            — FAQAT shu assembly (loyiha) ichida
protected internal  — protected YOKI internal (ikkalasi HAM)
private protected   — protected VA internal (ikkalasi BIRGA)
```

Nima uchun `public field` xavfli: **invariant**larni (masalan
"Salary hech qachon manfiy bo'lmasligi kerak") **kafolatlab
bo'lmaydi** — istalgan tashqi kod to'g'ridan o'zgartirishi mumkin.

### 3.2 Inheritance — meros olish

```csharp
public class Employee
{
    public string FullName { get; set; } = null!;
    protected decimal BaseSalary { get; set; }

    public Employee(string fullName, decimal baseSalary)
    {
        FullName = fullName;
        BaseSalary = baseSalary;
    }

    public virtual decimal CalculateSalary() => BaseSalary;
}

public class Manager : Employee
{
    public decimal Bonus { get; set; }

    public Manager(string fullName, decimal baseSalary, decimal bonus)
        : base(fullName, baseSalary) // ✅ Constructor chaining — BAZAVIY constructor CHAQIRILADI
    {
        Bonus = bonus;
    }

    public override decimal CalculateSalary() => base.CalculateSalary() + Bonus; // base. — ASL implementatsiyani chaqirish
}
```

**`sealed` klass** — meros olishni **taqiqlash**:
```csharp
public sealed class FinalReport { } // Hech kim BUNDAN meros OLA OLMAYDI

// sealed override — metodni KEYINGI merosda QAYTA override qilishni TAQIQLASH
public class Manager : Employee
{
    public sealed override decimal CalculateSalary() => base.CalculateSalary() + Bonus;
}
```

**Multiple Inheritance muammosi:** C# — klasslar uchun **faqat
bitta** bazaviy klassga ruxsat beradi (`class B : A` — YETARLI,
`class C : A, B` — MUMKIN EMAS). Sabab — **"Diamond Problem"**:
agar ikkita bazaviy klass BIR XIL metodga ega bo'lsa, qaysi biri
chaqirilishi **noaniq**. C# — bu muammoni **interfeys** orqali
(bir nechta interfeys implement qilish MUMKIN) hal qiladi.

### 3.3 Polymorphism — ko'p shakllilik

**Method Overloading** — bir xil nom, turli parametr, **compile-time**da hal qilinadi:
```csharp
public class Calculator
{
    public int Add(int a, int b) => a + b;
    public double Add(double a, double b) => a + b;
    public int Add(int a, int b, int c) => a + b + c;
}
// Compiler — chaqiruv paytida QAYSI metod TO'G'RI kelishini ANIQLAYDI (signature bo'yicha)
```

**Method Overriding** — `virtual` + `override`, **runtime**da hal qilinadi:
```csharp
Employee emp = new Manager("Orzibek", 5000000, 1000000); // Statik tur: Employee, DINAMIK tur: Manager
Console.WriteLine(emp.CalculateSalary()); // → Manager'ning CalculateSalary() chaqiriladi (runtime dispatch)!
```

### 3.4 CLR'da virtual method dispatch — vtable mexanizmi

```
HAR virtual metodga ega klass — o'zining "Virtual Method Table"
(vtable) ga ega — bu METOD POINTERLARIDAN iborat massiv.

Manager obyekti Heap'da:
┌─────────────────────┐
│ Method Table pointer │──────► Manager'ning vtable:
│ (type handle)         │         [0]: CalculateSalary → Manager.CalculateSalary()
│ FullName: "Orzibek"   │         [1]: ToString → Object.ToString()
│ BaseSalary: 5000000   │
│ Bonus: 1000000        │
└─────────────────────┘

emp.CalculateSalary() chaqirilganda:
1. CLR — obyektning METHOD TABLE POINTER'iga qaraydi (bu — RUNTIME
   turini bildiradi, Manager, garchi o'zgaruvchi turi Employee bo'lsa ham)
2. vtable'dan CalculateSalary() UCHUN mos YOZUVNI TOPADI
3. O'sha METODGA "SAKRAYDI" (jump)

Bu — "virtual dispatch" yoki "late binding" deb ataladi — QAYSI
metod chaqirilishi FAQAT RUNTIME'da (obyektning HAQIQIY turi
asosida) ANIQLANADI, compile-time'da EMAS.
```

Oddiy (non-virtual) metod — **compile-time**da to'g'ridan manzilga
"bog'lanadi" (early binding) — tezroq, lekin polimorfizm
ISHLAMAYDI.

### 3.5 `virtual` vs `abstract` farqi

```csharp
public abstract class Shape
{
    public abstract double Area();          // ❌ IMPLEMENTATSIYA YO'Q, sub-klass MAJBURIY override qilishi kerak
    public virtual string GetDescription()   // ✅ DEFAULT implementatsiya BOR, override IXTIYORIY
        => $"Shakl, maydoni: {Area()}";
}

public class Circle : Shape
{
    public double Radius { get; set; }
    public override double Area() => Math.PI * Radius * Radius; // MAJBURIY
}
```

```
virtual  — DEFAULT implementatsiya BOR, override QILISH IXTIYORIY
abstract — implementatsiya YO'Q, override MAJBURIY (aks holda
           klass ham abstract bo'lishi kerak)
abstract klass — O'ZI instansiyalanib BO'LMAYDI (new Shape() ❌ XATO)
```

### 3.6 Abstraction — murakkablikni yashirish

```csharp
// Interfeys — FAQAT "NIMA qilinishi", "QANDAY" emas
public interface IPayrollCalculator
{
    decimal Calculate(Employee employee);
}

public class StandardPayrollCalculator : IPayrollCalculator
{
    public decimal Calculate(Employee employee) => employee.CalculateSalary() * 0.88m; // Soliqdan keyin
}
```

Chaqiruvchi kod — FAQAT `IPayrollCalculator.Calculate()` ni biladi,
**qanday** hisoblanishini (ICHKI mantiqni) BILISHI SHART EMAS —
bu **abstraction**ning mohiyati.

**Abstract klass vs Interfeys:**
```
Abstract klass — "IS-A" munosabat, HOLAT (field) SAQLASHI MUMKIN,
                  BITTA bazaviy klass CHEKLOVI bor
Interfeys      — "CAN-DO" munosabat, HOLAT SAQLAY OLMAYDI (C# 8+
                  gacha), BIR NECHTA interfeys IMPLEMENT qilish MUMKIN
```

## 4. Kod — real ERP misolida OOP

```csharp
public abstract class Employee
{
    public string FullName { get; protected set; }
    protected decimal BaseSalary { get; set; }

    protected Employee(string fullName, decimal baseSalary)
    {
        FullName = fullName;
        BaseSalary = baseSalary;
    }

    public abstract decimal CalculateSalary();
    public virtual string GetSummary() => $"{FullName}: {CalculateSalary():C}";
}

public class FullTimeEmployee : Employee
{
    public FullTimeEmployee(string fullName, decimal baseSalary) : base(fullName, baseSalary) { }
    public override decimal CalculateSalary() => BaseSalary;
}

public class Contractor : Employee
{
    public int HoursWorked { get; set; }
    public decimal HourlyRate { get; set; }

    public Contractor(string fullName, decimal hourlyRate) : base(fullName, 0) => HourlyRate = hourlyRate;
    public override decimal CalculateSalary() => HourlyRate * HoursWorked;
}

// Polimorfik ishlatish
List<Employee> employees = new() { new FullTimeEmployee("Orzibek", 5000000), new Contractor("Dilnoza", 50000) { HoursWorked = 160 } };
foreach (var emp in employees)
    Console.WriteLine(emp.GetSummary()); // Har biri O'ZINING CalculateSalary()'ini ishlatadi
```

## 5. Qachon ishlatish kerak?

| Vaziyat | Yechim |
|---|---|
| Ma'lumotni tashqi o'zgartirishdan himoyalash | Encapsulation (private + property) |
| Umumiy xatti-harakatni bo'lishish | Inheritance |
| Bir xil interfeys, turli implementatsiya | Polymorphism |
| Faqat "nima", "qanday"ni yashirish | Abstraction (interfeys/abstract klass) |
| Klassni kengaytirishni taqiqlash | `sealed` |

**Anti-patternlar:**
```csharp
// ❌ "God class" — hamma narsani BITTA klassda qilish (Encapsulation/SRP buzilishi)
// ❌ Chuqur inheritance zanjiri (A → B → C → D → E) — tushunish QIYINLASHADI
// ✅ "Composition over inheritance" — ko'p holatda INTERFEYS/composition MEROSDAN afzal
```

## 6. Muhim nuqtalar

- `sealed` metod/klass — performance uchun HAM foydali (JIT — virtual
  dispatch'ni **devirtualizatsiya** qilishi mumkin, chunki override
  bo'lishi IMKONSIZ).
- Constructor chaining (`base(...)`) — BAZAVIY klass constructor
  **HAR DOIM** avval bajariladi (hatto `base()` yozilmasa ham,
  DEFAULT parametrsiz constructor CHAQIRILADI).
- Interfeysda default implementatsiya (C# 8+) — abstract klass bilan
  chegara **loyqalashtirildi**, lekin HOLAT (field) saqlash hali
  ham FAQAT klassda mumkin.

## 7. Imtihon savollari

1. Encapsulation nima uchun `public field` o'rniga `property`
   ishlatishni talab qiladi?
2. `virtual` va `abstract` orasidagi farq nima?
3. CLR'da virtual method dispatch (vtable) qanday ishlaydi?
4. Nima uchun C# klasslar uchun multiple inheritance'ga ruxsat
   bermaydi, lekin interfeyslar uchun beradi?
5. Method Overloading (compile-time) va Method Overriding (runtime)
   orasidagi farqni tushuntiring.
6. `sealed` klass/metod nima uchun kerak va u qanday performance
   foyda beradi?
7. Abstract klass va Interfeys orasidagi asosiy farqlarni ayting.
8. Constructor chaining (`base()`) qanday ishlaydi?

---

## 8. Mohiyat — Restoran analogiyasi orqali tushuntirish

OOP prinsiplarini koddan oldin haqiqiy hayot orqali tushunish muhim.
Kod yozayotganda har safar "Bu restoran qoidalariga mos keladimi?" deb
o'ylang — shu yetarli.

---

### Encapsulation — "Har narsa o'z joyida, tashqariga faqat keraklisi ko'rinadi"

Oshxonada oshpaz ovqat tayyorlaydi. Mehmon faqat menyuni ko'radi va
buyurtma beradi. Oshxona ichida nima bo'layotgani — qaysi ingredientlar
ishlatilayapti, qaysi texnologiya bilan tayyorlanayapti — mehmonni
qiziqtirmaydi va qiziqtirmasligi kerak.

Agar mehmon oshxonaga kirib, o'zi pishirsa — bu tartibsizlik. Kimdir
noto'g'ri narsani qo'shishi mumkin, jarayon buzilishi mumkin.

**Mohiyat:** Ichki jarayonlar yashiriladi. Tashqariga faqat "buyurtma
ber" va "ovqatni ol" imkoniyati beriladi. Bu yashirish — himoya ham,
tartib ham.

```
Tashqariga ko'rinadigan:        Yashirilgan:
─────────────────────────       ─────────────────────────
Menyu ko'rish                    Ingredientlar tarkibi
Buyurtma berish                  Tayyorlash jarayoni
Ovqatni olish                    Oshxona jihozlari
To'lov qilish                    Ichki hisob-kitob
```

---

### Inheritance — "Umumiy narsani bir joyda yoz, takrorlama"

Restoranda bir nechta xodim bor: ofitsiant, kassir, menejer. Bularning
hammasi "Xodim" — barchasi ish vaqtiga ega, barchasi maosh oladi,
barchasi kartochka bilan kiradi. Bu umumiy narsalar.

Lekin ofitsiant stol xizmat qiladi, kassir pul qabul qiladi, menejer
smena boshqaradi — bu esa har birining o'ziga xos vazifasi.

Agar siz har bir lavozim uchun "maosh hisoblash" qoidasini
alohida-alohida yozsangiz, ertaga maosh miqdori o'zgarganda hammasini
topib o'zgartirishingiz kerak. Lekin umumiy "Xodim" qoidasida bir
joyda yozsangiz — bir yerda o'zgartirish yetarli.

**Mohiyat:** Takrorlanuvchi narsalarni bir joyga jam qiling. O'zgarish
kerak bo'lsa — bitta joyda o'zgartiring.

```
     XODIM (umumiy)
     ─────────────
     Ish vaqti
     Maosh
     Kartochka
          │
┌─────────┼─────────┐
│         │         │
Ofitsiant Kassir  Menejer
(stol)    (pul)   (smena)
```

---

### Polymorphism — "Bir xil buyruq, har xil natija"

Menejer barcha xodimlarga "Ish boshlang!" deydi. Ofitsiant stollarga
boradi, kassir kassaga o'tiradi, oshpaz oshxonaga kiradi. Hammasi bir
xil buyruqni eshitdi, lekin har biri o'zicha harakat qildi.

Menejer "ofitsiant ish boshlang", "kassir ish boshlang" deb
alohida-alohida buyruq bermaydi. "Hammaga: ish boshlang!" — shu yetarli.
Kim nima qilishini o'zi biladi.

**Mohiyat:** Bitta buyruq — ko'p xulq. Yangi lavozim qo'shsangiz,
faqat o'sha lavozimning "ish boshlash" qoidasini yozsangiz yetarli.
Menejer kodini o'zgartirishning hojati yo'q.

```
        Menejer: "Ish boshlang!"
                  │
      ┌───────────┼───────────┐
      ▼           ▼           ▼
  Ofitsiant     Kassir      Oshpaz
  stollarga     kassaga     oshxonaga
  boradi        o'tiradi    kiradi

  (Bir xil buyruq — har xil natija)
```

---

### Abstraction — "Murakkablikni yashir, oddiyini ko'rsat"

Mehmon menyudan "Qozon kabob" tanlaydi va tugmani bosadi. U go't
yoqilishini, idishlar yuvilishini, ingredientlar tayyorlanishini
bilmaydi — bilishi ham shart emas. U faqat "buyurtma" va "tayyor
ovqat" ko'radi.

Yoki yanada soddaroq: siz mashinada gaz pedalini bosasiz — mashina
ilgari ketadi. Motor qanday ishlashi, benzin qanday yonishi — siz
buni bilmasangiz ham bo'ladi. Pedal — bu abstraktsiya.

**Mohiyat:** Foydalanuvchiga faqat kerakli narsani ko'rsat. Ichki
murakkablikni yashir. Bu ishni osonlashtiradi va xatolarni kamaytiradi.

```
Mehmon ko'radigan:      Yashirilgan murakkablik:
──────────────────      ───────────────────────
Menyu                    Go't yoqish jarayoni
Buyurtma tugmasi          Ingredientlar o'lchovi
"Tayyor" xabari           Idish yuvish
                          Tayyorlash vaqti hisoblash
```

---

### Hammasi birgalikda

```
                    RESTORAN
                       │
    ├── Mehmon faqat menyu ko'radi          ← Abstraction
    │   (oshxona ichini bilmaydi)
    │
    ├── Oshxona jarayoni yashirilgan         ← Encapsulation
    │   (mehmon to'g'ridan kirolmaydi)
    │
    ├── Xodimlar — hammasi "Xodim"           ← Inheritance
    │   (maosh, vaqt — bir joyda)
    │   lekin har biri o'z ishini qiladi
    │
    └── "Ish boshlang!" — bir buyruq         ← Polymorphism
        har biri o'zicha tushunadi
```

---

### Nima uchun bu muhim?

Bu prinsiplar ixtiro qilinmagan — **haqiqiy hayotdan olingan.** Dunyo
allaqachon shu tarzda ishlaydi: kasalxonada shifokor va hamshiraning
vazifalari ajratilgan, zavodda har sex o'z ishini qiladi, davlatda
har vazirlik o'z sohasini boshqaradi.

Kod ham xuddi shunday tashkil etilishi kerak. Chunki tartibli
tashkil etilgan narsa — o'zgarishga chidamli, tushunishga oson va
kengaytirishga qulay.

> **Eslab qolish uchun bitta savol:**
> "Bu kod o'zgarsa yoki kengaysa, qancha joy o'zgartiraman?"
> Agar javob "ko'p joy" bo'lsa — OOP prinsiplari buzilgan.

---

### O'z-o'zini tekshirish savollari

1. Encapsulation qaysi muammoni hal qiladi? Restoran misolida
   kim nima ko'radi va nima yashiriladi?
2. Inheritance bo'lmasa nima bo'ladi? Maosh foizi o'zgarganda
   qancha joy o'zgartirish kerak bo'lardi?
3. Polymorphism nima uchun kerak? Yangi lavozim qo'shilganda
   menejer kodi o'zgaradimi?
4. Abstraction va Encapsulation o'xshash ko'rinadi — ularning
   asosiy farqi nima?
5. Restoran misolida OOP buzilgan holat tasavvur qiling —
   nima noto'g'ri bo'lar edi?
