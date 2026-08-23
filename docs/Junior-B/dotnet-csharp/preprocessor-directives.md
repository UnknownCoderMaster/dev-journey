# Preprocessor Directives — #define, #if, #endif, #region, #endregion — Junior B

## 1. What (Nima?)

**Preprocessor Directive** — C# **kompilyator ISHGA TUSHISHIDAN
OLDIN** (aslida, zamonaviy Roslyn'da — LEXICAL ANALYSIS bosqichida)
QAYTA ISHLANADIGAN, `#` belgisi bilan BOSHLANADIGAN BUYRUQLAR. Ular
KOD EMAS — ular **KOMPILYATORGA KO'RSATMA** (masalan, "BU QISMNI
KOMPILYATSIYA QIL/QILMA").

## 2. Real hayot analogiyasi

**`#if`/`#endif` — "AGAR QISH BO'LSA, ISSIQ KIYIM OL" YORLIG'I.**
Chamadonga (kod fayliga) NARSALARNI JOYLASHDAN OLDIN, SIZ
ETIKETKA (`#if WINTER`) QO'YASIZ — "BU NARSA FAQAT QISHDA
KERAK". Sayohatga CHIQISHDAN OLDIN (KOMPILYATSIYADAN OLDIN) —
QAYSI MAVSUM (KONFIGURATSIYA) TANLANGANIGA QARAB, FAQAT KERAKLI
NARSALAR CHAMADONGA (FINAL DASTURGA) SOLINADI, QOLGANLARI
UMUMAN QOLDIRILADI.

**`#region`/`#endregion` — KITOB BOB SARLAVHALARI.** Katta
KITOBDA (fayl) — O'QUVCHIGA (dasturchiga) NAVIGATSIYA QILISHNI
OSONLASHTIRISH uchun, BOBLARNI (region) "YOPIB QO'YISH" (collapse)
mumkin — kontent O'ZGARMAYDI, FAQAT KO'RINISH TARTIBGA SOLINADI.

## 3. Why (Nega kerak?)

`#if DEBUG`/`#if RELEASE` — DEVELOPMENT VAQTIDA FOYDALI (masalan
BATAFSIL LOG) KODNI, PRODUCTION BUILD'DA **UMUMAN
KOMPILYATSIYA QILINMAGAN** holda QOLDIRISH imkonini beradi — bu
runtime `if` (masalan `Environment.IsDevelopment()`)dan FARQLI,
**KOMPILYATSIYA VAQTIDA** hal qilinadi — YAKUNIY BINARY'DA O'SHA
KOD **UMUMAN MAVJUD EMAS** (performance/hajm foydasi).

`#region` — KATTA fayllarda (masalan avtomatik generatsiya qilingan
DESIGNER kodida) NAVIGATSIYANI OSONLASHTIRADI, LEKIN **KO'P
LOYIHADA** (shu jumladan Microsoft'ning O'ZINING kod uslubida)
**TAVSIYA ETILMAYDI** — sabab pastda (6-bo'lim).

## 4. Internals (Ichki mexanizm)

### Preprocessing — QACHON va QANDAY ishlaydi

```
Roslyn kompilyator — MANBA KODNI (SOURCE) LEXICAL ANALYSIS
(TOKENIZATSIYA) bosqichida O'QIYDI. Bu jarayonda, `#` BILAN
BOSHLANGAN QATORLAR — MAXSUS "DIRECTIVE TRIVIA" sifatida
ANIQLANADI va QAYTA ISHLANADI — SHARTLI QISMLAR (masalan `#if
DEBUG` FALSE bo'lsa) — **SYNTAX TREE'GA UMUMAN KIRITILMAYDI**
(compile qilingan kodda MAVJUD EMAS).

C/C++'dan FARQLI — C#'da ALOHIDA "preprocessor" DASTUR (masalan
cpp.exe) YO'Q, bu — KOMPILYATORNING O'ZINING BIR QISMI.
```

### `#define` — SYMBOL yaratish

```csharp
#define FEATURE_X   // "FEATURE_X" nomli SYMBOL yaratiladi — QIYMATSIZ, faqat "BOR/YO'Q"

#if FEATURE_X
    Console.WriteLine("Feature X yoqilgan");
#endif
```

```
⚠️ MUHIM: #define — FAYL BOSHIDA, HAR QANDAY (using DIRECTIVE
DAN HAM OLDIN) YOZILISHI KERAK. Bu — FAQAT SHU FAYL DOIRASIDA
ISHLAYDI (BOSHQA fayllarga TA'SIR QILMAYDI), AGAR csproj DARAJASIDA
(<DefineConstants>) BELGILANMAGAN BO'LSA.
```

### `.csproj` orqali SYMBOL belgilash — LOYIHA DARAJASIDA

```xml
<PropertyGroup Condition="'$(Configuration)'=='Debug'">
  <DefineConstants>DEBUG;TRACE;FEATURE_X</DefineConstants>
</PropertyGroup>
```

```
DEBUG va TRACE — Visual Studio/dotnet CLI TOMONIDAN, Configuration
(Debug/Release) ASOSIDA, AVTOMATIK belgilanadi (csproj'da ANIQ
YOZILMASA HAM).
```

### `Conditional` atributi — `#if`ning MUQOBILI

```csharp
[System.Diagnostics.Conditional("DEBUG")]
public static void LogDebug(string message) => Console.WriteLine(message);

// Chaqiruvchi kod:
LogDebug("Test"); // DEBUG YOQILMAGAN bo'lsa — BU CHAQIRUV BUTUNLAY OLIB TASHLANADI (IL'da HAM YO'Q)!
```

```
Farqi #if'dan: [Conditional] — METOD DEFINITION'I HAR DOIM
KOMPILYATSIYA QILINADI (compile-time TEKSHIRUV — TYPE SAFETY
SAQLANADI), LEKIN METODNI CHAQIRUVCHI kod — SYMBOL YOQILMAGAN
bo'lsa, IL'DA UMUMAN CHIQARILMAYDI. #if — HATTO METOD
DEFINITION'INI HAM OLIB TASHLASHI mumkin (KAMROQ TYPE-SAFE).
```

### `#region` — KOMPILYATSIYAGA TA'SIR QILMAYDI

```
#region/#endregion — FAQAT IDE (Visual Studio/VS Code) uchun
"VIZUAL COLLAPSE" belgisi. Kompilyator UCHUN BU — HECH QANDAY
AHAMIYATGA EGA EMAS, XUDDI BO'SH QATORLARDEK "e'tiborsiz
qoldiriladi" (Syntax Tree'da "trivia" sifatida SAQLANADI, LEKIN
KODNING XATTI-HARAKATIGA TA'SIR QILMAYDI).
```

### Boshqa MUHIM direktivalar

```csharp
#warning "Bu API eskirgan, keyingi versiyada o'chiriladi"  // Compile-time OGOHLANTIRISH
#error "Bu kod hali tayyor emas"                             // Compile-time XATO (build TO'XTAYDI)
#pragma warning disable CS0168   // Ma'lum WARNING'ni VAQTINCHA O'CHIRISH
#pragma warning restore CS0168   // QAYTA YOQISH
#nullable enable                 // Nullable Reference Types'ni FAYL DOIRASIDA yoqish
#line 100 "OriginalFile.cs"       // Compiler XATOLARIDA ko'rsatiladigan QATOR/FAYL nomini O'ZGARTIRISH (code generator'lar uchun)
```

## 5. Code (Amaliy kod)

```csharp
#define ENABLE_AUDIT_LOG

using System;

namespace ErpDemo;

public class EmployeeService
{
    public void UpdateSalary(int employeeId, decimal newSalary)
    {
#if DEBUG
        Console.WriteLine($"[DEBUG] UpdateSalary chaqirildi: id={employeeId}, salary={newSalary}");
#endif

#if ENABLE_AUDIT_LOG
        LogAuditTrail(employeeId, newSalary);
#endif

        // ... haqiqiy yangilash logikasi
    }

#if ENABLE_AUDIT_LOG
    private void LogAuditTrail(int employeeId, decimal newSalary)
        => Console.WriteLine($"AUDIT: Employee {employeeId} salary changed to {newSalary}");
#endif
}
```

```csharp
// Conditional atributi bilan — TYPE-SAFE muqobil
public class Logger
{
    [System.Diagnostics.Conditional("DEBUG")]
    public static void Debug(string message)
        => Console.WriteLine($"[DEBUG] {message}");
}

public class OrderService
{
    public void ProcessOrder(int orderId)
    {
        Logger.Debug($"Buyurtma qayta ishlanmoqda: {orderId}");
        // RELEASE build'da — Logger.Debug() CHAQIRUVI BUTUNLAY IL'DAN OLIB TASHLANADI
    }
}
```

```csharp
#region Employee Validation Helpers
public static class EmployeeValidators
{
    public static bool IsValidAge(int age) => age is >= 18 and <= 65;
    public static bool IsValidSalary(decimal salary) => salary > 0;
}
#endregion
```

## 6. Keng tarqalgan xatolar / noto'g'ri tushunchalar

```
❌ "#define — BOSHQA fayllarga HAM TA'SIR QILADI" — NOTO'G'RI!
   #define — FAQAT O'SHA FAYL doirasida ISHLAYDI (AGAR csproj
   darajasida belgilanmagan bo'lsa).

❌ "#region — KODNI TASHKILLASHTIRISHNING ENG YAXSHI usuli" —
   KO'P jamoa BUNI ANTI-PATTERN deb HISOBLAYDI: region'lar
   KO'PINCHA "KLASS JUDA KATTA, BO'LINISHI KERAK" degan BELGINI
   YASHIRADI. Kichik, ANIQ maqsadli klasslar — region'siz HAM
   O'QILISHI OSON bo'lishi kerak.

❌ "#if DEBUG — runtime'da TEKSHIRILADI" — NOTO'G'RI! Bu —
   COMPILE-TIME'DA hal qilinadi. Runtime'da MUHITNI (masalan
   Production/Development) TEKSHIRISH uchun
   `IWebHostEnvironment.IsDevelopment()` ISHLATILADI (bular —
   TUBDAN BOSHQA MEXANIZM).

❌ "#pragma warning disable — XAVFSIZ, chunki FAQAT OGOHLANTIRISH
   O'CHIRILADI" — EHTIYOT bo'ling: bu HAQIQIY MUAMMOLARNI (masalan
   null reference xavfi) "KO'RMAS" QILISHI mumkin — FAQAT ANIQ
   sabab BILAN, VAQTINCHA ishlatilishi kerak.

❌ "[Conditional] va #if — BIR XIL" — FARQ BOR: [Conditional] —
   METOD DEFINITION'I DOIM KOMPILYATSIYA QILINADI (TYPE CHECK
   ISHLAYDI), FAQAT CHAQIRUVLAR OLIB TASHLANADI. #if — HATTO
   METODNING O'ZINI HAM OLIB TASHLASHI MUMKIN.
```

## 7. Exam (Interview savollari)

**1. `#if DEBUG` va runtime `if (IsDevelopment())` orasidagi
FARQ nima?**
`#if DEBUG` — COMPILE-TIME'DA HAL QILINADI, YAKUNIY BINARY'DA
KOD **UMUMAN MAVJUD BO'LMASLIGI** MUMKIN (agar shart FALSE bo'lsa).
`if (IsDevelopment())` — RUNTIME'DA TEKSHIRILADI, KOD BINARY'DA
BOR, LEKIN SHART ASOSIDA BAJARILADI YOKI YO'Q.

**2. `#region`/`#endregion` KOMPILYATSIYAGA QANDAY TA'SIR QILADI?**
HECH QANDAY TA'SIR QILMAYDI — bu FAQAT IDE (Visual Studio/VS Code)
UCHUN VIZUAL "COLLAPSE" BELGISI, Syntax Tree'da "trivia" sifatida
E'TIBORSIZ QOLDIRILADI.

**3. `[Conditional("DEBUG")]` atributi `#if DEBUG` dan QANDAY
FARQ QILADI?**
`[Conditional]` — METOD DEFINITION'I HAR DOIM KOMPILYATSIYA
QILINADI (TYPE SAFETY SAQLANADI), FAQAT CHAQIRUVLAR (call sites)
SYMBOL YOQILMAGANDA IL'DAN OLIB TASHLANADI. `#if` — HATTO METOD
DEFINITION'INI HAM SHARTLI QILISHI MUMKIN, LEKIN KAMROQ TYPE-SAFE
(METOD SIGNATURE O'ZGARSA, CHAQIRUVCHI KOD BOSHQA SYMBOL
KONFIGURATSIYASIDA BUZILISHI mumkin, buni COMPILE-TIME'DA
DARHOL SEZMASLIK EHTIMOLI BOR).

**4. `DEBUG` va `TRACE` symbollari QAYERDAN KELADI?**
Visual Studio/dotnet CLI — `Configuration` (Debug/Release)
ASOSIDA, `.csproj`da ANIQ YOZILMAGAN bo'lsa HAM, AVTOMATIK
`<DefineConstants>DEBUG;TRACE</DefineConstants>` (Debug
konfiguratsiyasi uchun) QO'SHADI.

**5. Nima uchun ko'p jamoa `#region`ni ANTI-PATTERN deb HISOBLAYDI?**
Region'lar — KATTA, KO'P MAS'ULIYATLI klasslarni "TARTIBGA
SOLINGANDEK" KO'RSATIB, HAQIQIY MUAMMONI (klass SRP'ni BUZAYOTGANI,
BO'LINISHI KERAKLIGI) YASHIRADI. Yaxshiroq yechim — klassni
KICHIKROQ, ANIQ mas'uliyatli QISMLARGA AJRATISH.
