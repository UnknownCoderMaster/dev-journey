# Virtual Method, Abstract Method — Junior B

## 1. What (Nima?)

**Virtual method** — bazaviy klassda **DEFAULT implementatsiyaga**
ega, LEKIN sub-klass tomonidan `override` orqali **QAYTA
YOZILISHI MUMKIN** bo'lgan metod. **Abstract method** —
implementatsiyaga EGA EMAS, sub-klass **MAJBURIY** ravishda
`override` QILISHI KERAK bo'lgan metod (FAQAT `abstract` klassda
BO'LISHI MUMKIN).

## 2. Real hayot analogiyasi

**Virtual method — "STANDART RETSEPT, LEKIN O'ZGARTIRISH MUMKIN".**
Restoran zanjiri (bazaviy klass) — "Osh" retseptining STANDART
VERSIYASINI BERADI (`virtual`). Har FILIAL (sub-klass) — XOHLASA,
O'Z MINTAQAVIY TA'MI bilan RETSEPTNI O'ZGARTIRISHI MUMKIN
(`override`), XOHLAMASA — STANDART RETSEPTDAN FOYDALANAVERADI.

**Abstract method — "BO'SH SHABLON, TO'LDIRISH MAJBURIY".**
"Ish boshlash protokoli" (abstract metod) — HAR YANGI FILIAL
OCHILGANDA, MENEJER **MAJBURIY** RAVISHDA O'ZINING "ISH BOSHLASH"
JARAYONINI YOZISHI KERAK — BOSH KOMPANIYA BUNGA HECH QANDAY
DEFAULT BERMAYDI, CHUNKI HAR MINTAQADA QOIDALAR TURLICHA.

## 3. Why (Nega kerak?)

Bu ikkalasi — **polimorfizm**ni AMALGA OSHIRISH uchun ASOSIY
VOSITA. Ularsiz — HAR SUB-KLASS UCHUN ALOHIDA, BOG'LANMAGAN
METOD YOZISH KERAK BO'LARDI, va CHAQIRUVCHI KOD "QAYSI SUB-KLASS
EKANINI" QO'LDA TEKSHIRISHGA (`if-else`/`switch` ZANJIRI) MAJBUR
BO'LARDI. `virtual`/`abstract` — bu QARORNI **CLR'GA** (runtime
dispatch orqali) TOPSHIRADI — YANGI SUB-KLASS QO'SHILGANDA,
CHAQIRUVCHI KOD **UMUMAN O'ZGARMAYDI** (Open/Closed Principle).

**Java bilan solishtirish:** Java'da METODLAR **DEFAULT holda
VIRTUAL** (`final` DEB BELGILANMASA), C#'da esa **DEFAULT holda
NON-VIRTUAL** — bu, C#'ning ANIQ, "IXTIYORIY" DIZAYN QARORI
(dasturchi ANIQ `virtual` DEB BELGILASHI KERAK).

## 4. Internals (Ichki mexanizm)

### vtable — virtual method dispatch mexanizmi

```
HAR virtual/abstract metodga EGA klass — "Virtual Method Table"
(vtable)ga EGA — bu METOD POINTERLARIDAN IBORAT MASSIV.

obj.Method() CHAQIRILGANDA:
1. CLR — OBYEKTNING Method Table pointer'iga QARAYDI (bu — RUNTIME
   turini KO'RSATADI)
2. vtable'DAN Method() UCHUN MOS YOZUVNI TOPADI
3. O'SHA METODGA "SAKRAYDI"

Bu — "LATE BINDING" deb ATALADI (RUNTIME'da HAL QILINADI).
```

Batafsil (to'liq misol bilan): `docs/Junior-A/01-oop-principles`
(3.4-bo'lim).

### Non-virtual metod — EARLY BINDING

```
Oddiy (non-virtual) METOD — COMPILE-TIME'DA TO'G'RIDAN MANZILGA
"BOG'LANADI" (early binding) — vtable QIDIRUVI YO'Q, TO'G'RIDAN
CHAQIRILADI — TEZROQ, LEKIN POLIMORFIZM ISHLAMAYDI.
```

### IL darajasida FARQ — `call` vs `callvirt`

```il
// Non-virtual metod chaqiruvi:
call instance void Employee::DoWork()

// Virtual/abstract metod chaqiruvi:
callvirt instance void Employee::DoWork()
```

`callvirt` — RUNTIME'da **NULL TEKSHIRUVI** HAM QILADI (agar `obj`
NULL bo'lsa — `NullReferenceException`), VA vtable ORQALI TO'G'RI
METODNI TOPADI. `call` — BUNDAY TEKSHIRUV QILMAYDI, TO'G'RIDAN
BELGILANGAN MANZILGA "SAKRAYDI".

### `new` (method hiding) vs `override` — MUHIM FARQ

```csharp
public class Base { public virtual void Show() => Console.WriteLine("Base"); }

public class Derived1 : Base { public override void Show() => Console.WriteLine("Derived1 (override)"); }
public class Derived2 : Base { public new void Show() => Console.WriteLine("Derived2 (new/hiding)"); }

Base b1 = new Derived1();
b1.Show(); // → "Derived1 (override)" — RUNTIME turi ASOSIDA (vtable)

Base b2 = new Derived2();
b2.Show(); // → "Base"! — 'new' — vtable'NI O'ZGARTIRMAYDI, FAQAT
           //   COMPILE-TIME'DA "b2 — Base turi" DEB QARALADI
```

```
override — vtable YOZUVINI ALMASHTIRADI (POLIMORFIK)
new       — YANGI, MUSTAQIL METOD YARATADI (o'zining vtable
            yozuvi BILAN), BAZAVIY METODNI "YASHIRADI" (hides),
            LEKIN ALMASHTIRMAYDI — POLIMORFIK EMAS!
```

### Devirtualizatsiya — JIT optimallashtirishi

```
Agar JIT — RUNTIME'da OBYEKTNING HAQIQIY TURI ANIQ (masalan
`sealed` klass, YOKI OBYEKT `new SomeClass()` orqali TO'G'RIDAN
YARATILGAN) EKANINI ANIQLASA — vtable QIDIRUVINI O'TKAZIB YUBORIB,
TO'G'RIDAN METODGA "SAKRASHI" MUMKIN (devirtualization) — bu
PERFORMANCE OPTIMALLASHTIRISH.
```

## 5. Code (Amaliy kod)

```csharp
public abstract class PaymentProcessor
{
    // Abstract — HAR sub-klass MAJBURIY implement QILISHI kerak
    public abstract Task<bool> ProcessAsync(decimal amount);

    // Virtual — DEFAULT implementatsiya BOR, override IXTIYORIY
    public virtual void LogTransaction(decimal amount)
        => Console.WriteLine($"Tranzaksiya: {amount:C}");
}

public class CreditCardProcessor : PaymentProcessor
{
    public override async Task<bool> ProcessAsync(decimal amount)
    {
        // Kredit karta orqali TO'LOV logikasi
        await Task.Delay(100);
        return true;
    }
    // LogTransaction() OVERRIDE QILINMAGAN — DEFAULT implementatsiya ISHLATILADI
}

public class CryptoProcessor : PaymentProcessor
{
    public override async Task<bool> ProcessAsync(decimal amount)
    {
        await Task.Delay(200);
        return true;
    }

    public override void LogTransaction(decimal amount) // XOHLASA OVERRIDE QILADI
        => Console.WriteLine($"Crypto tranzaksiya (maxsus log): {amount:C}");
}

// Polimorfik ishlatish
List<PaymentProcessor> processors = new() { new CreditCardProcessor(), new CryptoProcessor() };
foreach (var p in processors)
{
    await p.ProcessAsync(1000);
    p.LogTransaction(1000); // HAR BIRI O'ZINING (yoki DEFAULT) implementatsiyasini ISHLATADI
}
```

```csharp
// sealed override — QAYTA override QILISHNI TAQIQLASH
public class VipCreditCardProcessor : CreditCardProcessor
{
    public sealed override Task<bool> ProcessAsync(decimal amount)
    {
        // ... maxsus VIP logika
        return Task.FromResult(true);
    }
    // Bu klassdan MEROS OLGAN klasslar ENDI ProcessAsync()ni QAYTA OVERRIDE QILA OLMAYDI
}
```

## 6. Keng tarqalgan xatolar / noto'g'ri tushunchalar

```
❌ "virtual va abstract — BIR XIL narsa" — YO'Q! virtual —
   DEFAULT implementatsiya BOR (override IXTIYORIY), abstract —
   implementatsiya YO'Q (override MAJBURIY).

❌ "abstract metod — abstract KLASSSIZ ham YOZILADI" — NOTO'G'RI!
   Abstract metod FAQAT abstract KLASSDA (yoki interfeysda) BO'LISHI
   MUMKIN.

❌ "override — new BILAN BIR XIL natija BERADI" — NOTO'G'RI!
   Yuqoridagi 4-bo'limdagi misolga qarang — 'new' POLIMORFIZMNI
   BUZADI, BAZAVIY TUR ORQALI CHAQIRILGANDA BAZAVIY implementatsiya
   ISHLAYDI.

❌ "Constructor'da virtual METOD CHAQIRISH XAVFSIZ" — XAVFLI!
   Agar SUB-KLASS BU METODNI OVERRIDE QILGAN BO'LSA, BAZAVIY
   klass CONSTRUCTOR'I ISHLAGANDA — SUB-KLASSNING O'ZINING
   FIELD'LARI HALI INITIALIZATSIYA QILINMAGAN BO'LISHI MUMKIN
   (NullReferenceException YOKI KUTILMAGAN QIYMAT xavfi).

❌ "abstract klass — interfeysdan HAR DOIM YAXSHIROQ" — VAZIYATGA
   BOG'LIQ: abstract klass — HOLAT (field) SAQLASHI MUMKIN, LEKIN
   BITTA bazaviy klass CHEKLOVI BOR; interfeys — CHEKLOVSIZ,
   LEKIN (C# 8+ gacha) HOLAT SAQLAY OLMAYDI.
```

## 7. Exam (Interview savollari)

**1. `virtual` va `abstract` metodlar orasidagi ASOSIY farq nima?**
`virtual` — DEFAULT implementatsiyaga EGA, `override` IXTIYORIY.
`abstract` — implementatsiyaga EGA EMAS, `override` MAJBURIY, VA
FAQAT `abstract` klassda BO'LISHI mumkin (klassning O'ZI HAM
`abstract` bo'lishi kerak).

**2. CLR darajasida virtual method dispatch (vtable) QANDAY ISHLAYDI?**
Har virtual/abstract metodga EGA klass — "Virtual Method Table"
(vtable)ga EGA. Metod chaqirilganda, CLR OBYEKTNING (compile-time
turi EMAS, RUNTIME turi) Method Table pointer'i ORQALI vtable'ni
TOPADI va MOS METOD manziliga "SAKRAYDI" — bu "LATE BINDING".

**3. IL darajasida `call` va `callvirt` orasidagi farq nima?**
`call` — NON-VIRTUAL metod uchun, TO'G'RIDAN, COMPILE-TIME'DA
ANIQ manzilga "SAKRAYDI". `callvirt` — VIRTUAL/ABSTRACT metodlar
uchun, QO'SHIMCHA RAVISHDA NULL TEKSHIRUVI QILADI va vtable
ORQALI RUNTIME turiga MOS metodni TOPADI.

**4. `new` (method hiding) va `override` orasidagi farq nima?**
`override` — BAZAVIY klassning vtable YOZUVINI ALMASHTIRADI
(POLIMORFIK — bazaviy TUR ORQALI chaqirilsa ham, SUB-KLASS
implementatsiyasi ISHLAYDI). `new` — YANGI, MUSTAQIL metod
YARATADI, bazaviyni "YASHIRADI" — bazaviy TUR ORQALI chaqirilsa,
BAZAVIY implementatsiya ISHLAYDI (POLIMORFIK EMAS).

**5. Constructor ichida virtual metod chaqirish nima uchun XAVFLI?**
Agar SUB-KLASS bu metodni OVERRIDE QILGAN bo'lsa, BAZAVIY klass
constructor'i ISHLAGANDA (SUB-KLASS constructor'i HALI TO'LIQ
BAJARILMAGAN) — OVERRIDE QILINGAN metod ICHIDA SUB-KLASSNING
O'ZINING FIELD'LARI HALI INITIALIZATSIYA QILINMAGAN (DEFAULT
qiymatlarda) BO'LISHI MUMKIN — bu KUTILMAGAN XATOGA olib KELADI.
