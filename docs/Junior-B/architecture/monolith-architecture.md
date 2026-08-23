# Monolith Architecture — Junior B

## 1. What (Nima?)

**Monolith Architecture** — butun ilova (barcha modul: xodimlar,
buyurtmalar, hisobotlar) — **BITTA DEPLOY QILINADIGAN BIRLIK**
(bitta process, bitta binary/executable, bitta DB) sifatida
QURILADI. Bu — Microservices'ning **TESKARISI** (u yerda HAR MODUL
— MUSTAQIL, ALOHIDA DEPLOY QILINADIGAN SERVIS).

## 2. Real hayot analogiyasi

**Monolith — YAGONA, KATTA UNIVERMAG.** Kiyim, oziq-ovqat,
elektronika — HAMMASI **BITTA BINODA**, BITTA BOSHQARUV OSTIDA.
Xarid qilish OSON (BIR JOYGA BORASIZ). LEKIN AGAR ELEKTR TA'MINOTI
(infratuzilma) O'CHIB QOLSA — **BUTUN UNIVERMAG** ISHLAMAY QOLADI
(bitta modul — MASALAN HISOBOT MODULI — QULASA, BUTUN ILOVA
YIQILISHI MUMKIN).

**Microservices — MUSTAQIL DO'KONLAR MAJMUASI (SAVDO MARKAZI).**
Har bir do'kon (SERVIS) — O'ZINING ELEKTR TA'MINOTI, XODIMLARI
BILAN MUSTAQIL ISHLAYDI. BITTA DO'KON YOPILSA (crash) — QOLGANLARI
DAVOM ETADI. LEKIN BUNI BOSHQARISH (KOORDINATSIYA, XAVFSIZLIK)
— ANCHA MURAKKAB.

## 3. Why (Nega kerak?)

Monolith — KO'P LOYIHA UCHUN **BOSHLANG'ICH NUQTA** SIFATIDA
TO'G'RI TANLOV, chunki:

1. **DEPLOY SODDA** — BITTA ARTEFAKT (masalan bitta Docker image)
2. **DEBUG QILISH OSON** — BARCHA KOD BITTA PROCESS'DA, STACK
   TRACE BUTUN OQIMNI KO'RSATADI (Microservices'da — DISTRIBUTED
   TRACING KERAK)
3. **TRANZAKSIYALAR SODDA** — BITTA DB'da, ACID KAFOLATLANADI
   (Microservices'da — DISTRIBUTED TRANSACTION MURAKKAB MUAMMO)
4. **KICHIK JAMOA UCHUN TEZROQ** — MICROSERVICES'ning
   KOORDINATSIYA OVERHEAD'I YO'Q

**Netflix/Amazon bilan solishtirish:** Bu KOMPANIYALAR HAM
DASTLAB Monolith bilan BOSHLAGAN — Microservices'GA FAQAT
JAMOA/TRAFIK KATTALASHGANDA O'TGAN. "Monolith First" — KO'P
ARXITEKTOR TOMONIDAN TAVSIYA ETILADIGAN STRATEGIYA.

## 4. Internals (Ichki mexanizm)

### Monolith ICHIDA — modullar QANDAY TASHKIL QILINADI

```
ErpMonolith/
├── Modules/
│   ├── Employees/       — Controller, Service, Repository
│   ├── Payroll/          — Controller, Service, Repository
│   └── Reports/          — Controller, Service, Repository
├── Shared/
│   └── AppDbContext.cs   — BARCHA MODULLAR UCHUN BITTA DbContext
└── Program.cs            — BITTA ASP.NET Core ILOVA
```

```
Modullar — BIR XIL PROCESS ICHIDA, TO'G'RIDAN METOD CHAQIRUVI
(in-process call) ORQALI ALOQA QILADI — TARMOQ (HTTP/gRPC) SHART
EMAS, LATENCY DEYARLI NOL.
```

### "Modular Monolith" — ZAMONAVIY YONDASHUV

```
Modular Monolith — Monolith'ning "TARTIBGA SOLINGAN" VERSIYASI:
BITTA DEPLOY BIRLIGI (Monolith'ning AFZALLIGI), LEKIN MODULLAR
ORASIDA QAT'IY CHEGARALAR (internal klasslar, ALOHIDA namespace
— docs/Junior-A/12-mvc-nlayer-architecture'dagi N-Layer'ga
O'XSHASH prinsip, LEKIN modullar orasida).

Bu — KELAJAKDA Microservices'GA O'TISHNI OSONLASHTIRADI (chunki
CHEGARALAR ALLAQACHON ANIQ).
```

### Deploy jarayoni — QANDAY ISHLAYDI

```
1. BUTUN kod BAZASI — BITTA build JARAYONIDAN O'TADI
2. BITTA artefakt (masalan .dll/.exe YOKI Docker image) YARATILADI
3. BU artefakt — BIR NECHTA server'GA (Load Balancer ORTIDA)
   NUSXALANADI (horizontal scaling — BUTUN ILOVA NUSXALANADI,
   FAQAT BITTA MODUL EMAS)
```

### Scaling MUAMMOSI — nima uchun Microservices AYRIM HOLLARDA AFZAL

```
Monolith'da — AGAR FAQAT "Reports" MODULI KO'P CPU TALAB QILSA
(masalan og'ir hisobot generatsiyasi), SIZ BUTUN ILOVANI (Employees,
Payroll HAM) SKALALASH kerak — bu RESURS ISROFI.

Microservices'da — FAQAT "Reports" SERVISINI ALOHIDA SKALALASH
mumkin — LEKIN bu — QO'SHIMCHA INFRATUZILMA MURAKKABLIGI (Service
Discovery, API Gateway, Distributed Logging) HISOBIGA KELADI.
```

## 5. Code (Amaliy kod)

```csharp
// Monolith'da — bitta DbContext, BARCHA modullar UCHUN
public class AppDbContext : DbContext
{
    public DbSet<Employee> Employees => Set<Employee>();
    public DbSet<Payroll> Payrolls => Set<Payroll>();
    public DbSet<Report> Reports => Set<Report>();
}

// Modullar ORASIDA — TO'G'RIDAN metod CHAQIRUVI (in-process, TEZ)
public class PayrollService
{
    private readonly AppDbContext _context;

    public async Task<decimal> CalculateTotalPayrollAsync()
    {
        // "Employees" MODULIGA TO'G'RIDAN MUROJAAT — TARMOQ SO'ROVI SHART EMAS
        var employees = await _context.Employees.ToListAsync();
        return employees.Sum(e => e.Salary);
    }
}
```

```csharp
// Modular Monolith — MODULLAR ORASIDA CHEGARA (internal orqali)
namespace ErpMonolith.Modules.Payroll;

// internal — FAQAT "Payroll" MODULI ICHIDA ko'rinadi, BOSHQA
// MODULLAR (masalan Reports) TO'G'RIDAN MUROJAAT QILA OLMAYDI!
internal class PayrollRepository { /* ... */ }

// public — MODULLAR ORASIDAGI "RASMIY" INTERFEYS
public interface IPayrollService
{
    Task<decimal> CalculateTotalPayrollAsync();
}
```

## 6. Keng tarqalgan xatolar / noto'g'ri tushunchalar

```
❌ "Monolith — ESKI, KEYINGI ARXITEKTURA" — NOTO'G'RI! Monolith —
   HALI HAM KO'P MUVAFFAQIYATLI KOMPANIYA (Shopify, Stack Overflow
   TARIXIY DAVRLARDA) TOMONIDAN ISHLATILADI — TO'G'RI KONTEKSTDA,
   BU — MUKAMMAL YECHIM.

❌ "Kichik jamoa — DARHOL Microservices BILAN BOSHLASHI KERAK" —
   XAVFLI! Microservices — DISTRIBUTED SYSTEMS MURAKKABLIGINI
   (network latency, eventual consistency, DISTRIBUTED
   TRANSACTIONS) OLIB KELADI — KICHIK JAMOA UCHUN BU — SEKINLASHTIRUVCHI
   OMIL.

❌ "Monolith — SKALALANMAYDI" — QISMAN NOTO'G'RI! Monolith'ni
   HAM HORIZONTAL SKALALASH mumkin (BIR NECHA NUSXA, Load Balancer
   ORTIDA) — FAQAT "SELEKTIV" (faqat bitta MODUL) SKALALASH
   QIYINROQ.

❌ "Monolith — HAR DOIM 'SPAGHETTI CODE'GA AYLANADI" — Bu —
   ARXITEKTURA MUAMMOSI EMAS, DIZAYN INTIZOMI MUAMMOSI — Modular
   Monolith — SHU MUAMMONI HAL QILADI (docs 4-bo'limga qarang).
```

## 7. Exam (Interview savollari)

**1. Monolith va Microservices orasidagi ASOSIY farq nima?**
Monolith — BUTUN ilova BITTA DEPLOY BIRLIGI (process), BITTA DB
sifatida ISHLAYDI. Microservices — HAR MODUL — MUSTAQIL, ALOHIDA
DEPLOY QILINADIGAN SERVIS, ODATDA O'ZINING DB'siga EGA, HTTP/gRPC
ORQALI ALOQA QILADI.

**2. Nima uchun ko'p ekspert "Monolith First" strategiyasini
TAVSIYA QILADI?**
Monolith — TEZROQ ISHLAB CHIQISH, SODDA DEBUG, SODDA TRANZAKSIYA
BOSHQARUVI BERADI. Microservices — DISTRIBUTED SYSTEMS
MURAKKABLIGINI TALAB QILADI — BU MURAKKABLIK, LOYIHA/JAMOA
KATTALASHGANDA GINA "TO'LASHGA ARZIYDI".

**3. "Modular Monolith" nima va u qanday muammoni HAL QILADI?**
Modular Monolith — BITTA DEPLOY BIRLIGI (Monolith AFZALLIGI),
LEKIN MODULLAR ORASIDA QAT'IY CHEGARALAR (masalan `internal`
access modifier orqali) O'RNATILGAN ARXITEKTURA. Bu — Monolith'ning
"HAMMA NARSA ARALASHIB KETADI" MUAMMOSINI HAL QILADI, VA KELAJAKDA
Microservices'GA O'TISHNI OSONLASHTIRADI.

**4. Monolith'da BITTA MODUL (masalan Reports) ko'proq CPU
talab qilsa, NIMA MUAMMO YUZAGA KELADI?**
Monolith'ni FAQAT "SELEKTIV" ravishda SKALALASH MUMKIN EMAS —
AGAR FAQAT Reports MODULI KO'PROQ RESURS TALAB QILSA, BUTUN
ILOVANI (Employees, Payroll bilan BIRGA) SKALALASH KERAK BO'LADI
— bu RESURS ISROFIGA olib keladi.

**5. Monolith'da MODULLAR orasidagi ALOQA Microservices'DAN
QANDAY FARQ QILADI?**
Monolith'da — MODULLAR ORASIDAGI ALOQA — TO'G'RIDAN METOD
CHAQIRUVI (IN-PROCESS), LATENCY DEYARLI NOL. Microservices'da —
SERVISLAR ORASIDAGI ALOQA — TARMOQ ORQALI (HTTP/gRPC/message
broker) — LATENCY, TARMOQ XATOLARI, VA "PARTIAL FAILURE" (bitta
servis ISHLAMAY QOLISHI) XAVFLARI PAYDO BO'LADI.
