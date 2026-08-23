# NUnit (Unit Test) — Junior B

## 1. What (Nima?)

**NUnit** — .NET EKOSISTEMASIDAGI, xUnit'dan **QADIMIYROQ**
(2002-yildan buyon MAVJUD, JUnit'DAN "PORT" QILINGAN),
LEKIN HALI HAM KENG QO'LLANILADIGAN UNIT TEST FREYMVORKI.
NUnit — xUnit BILAN, ASOSIY MAQSAD (test yozish, avtomatlash-
tirish) BO'YICHA BIR XIL, LEKIN **ATRIBUTLAR NOMLANISHI VA
TEST LIFECYCLE (hayot sikli) BOSHQARUVI JIHATIDAN FARQ
QILADI**.

## 2. Real hayot analogiyasi

**NUnit va xUnit — IKKI XIL "SINOV STENDI" ISHLAB
CHIQARUVCHISI.** Ikkalasi HAM, "MASHINA DETALLARINI SINASH"
(unit testing) MAQSADIGA XIZMAT QILADI, LEKIN, ULARNING
BOSHQARUV PANELLARI (atributlar, sintaksis) — BIROZ FARQ
QILADI. Masalan, NUnit — "HAR SINOVDAN OLDIN, STENDNI QAYTA
SOZLASH" (SetUp) UCHUN, ALOHIDA, ANIQ TUGMA (atribut) TAQDIM
ETADI, xUnit ESA — BUNI, "HAR SAFAR YANGI STEND QURISH"
(constructor) ORQALI, BOSHQACHA YO'L BILAN AMALGA OSHIRADI.

## 3. Why (Nega kerak?)

NUnit — **KO'PROQ, ANIQ VA EXPLICIT (ochiq) LIFECYCLE
ATRIBUTLARI** (`[SetUp]`, `[TearDown]`, `[OneTimeSetUp]`)
TAQDIM ETADI — bu, TEST TAYYORLASH/TOZALASH MANTIG'INI, YAQQOL
KO'RINADIGAN, ALOHIDA METODLARGA AJRATISH IMKONINI BERADI.
KO'PLAB, ESKI, YOKI **JAVA/JUnit BILAN TANISH DASTURCHILAR**
UCHUN, NUnit'ning SINTAKSISI, TANISHROQ VA TUSHUNARLIROQ
BO'LISHI MUMKIN. Bundan TASHQARI, NUnit — BA'ZI MURAKKAB
SSENARIYLARDA (masalan, PARAMETRLASHTIRILGAN TEST FIXTURE'LAR)
— KO'PROQ, TAYYOR ATRIBUTLARGA EGA.

## 4. Internals (Ichki mexanizm)

### `[SetUp]`/`[TearDown]` — HAR TEST OLDIDAN/KEYIN AVTOMATIK BAJARILISH

```csharp
[TestFixture]
public class CalculatorTests
{
    private Calculator _calculator;

    [SetUp]
    public void Setup() => _calculator = new Calculator(); // HAR TEST OLDIDAN chaqiriladi

    [TearDown]
    public void Cleanup() => _calculator = null; // HAR TEST TUGAGANDAN KEYIN chaqiriladi

    [Test]
    public void Add_TwoNumbers_ReturnsSum()
    {
        var result = _calculator.Add(2, 3);
        Assert.That(result, Is.EqualTo(5));
    }
}
```

```
NUnit TEST RUNNER — `[TestFixture]` ATRIBUTI BILAN
BELGILANGAN KLASSNI TOPADI, VA HAR `[Test]` METODI ISHGA
TUSHIRILISHIDAN OLDIN, `[SetUp]` METODINI, KEYIN ESA,
`[TearDown]` METODINI, AVTOMATIK, REFLECTION ORQALI ANIQLAB,
CHAQIRADI — bu, xUnit'ning CONSTRUCTOR/IDisposable ORQALI
AMALGA OSHIRILADIGAN "TOZA HOLAT" MEXANIZMIGA, FUNKSIONAL
JIHATDAN TENG, LEKIN, EXPLICIT (aniq nomlangan METODLAR
orqali) YONDASHUV.
```

### `[OneTimeSetUp]`/`[OneTimeTearDown]` — BUTUN KLASS UCHUN, BIR MARTA

```csharp
[TestFixture]
public class DatabaseTests
{
    private AppDbContext _context;

    [OneTimeSetUp]
    public void ClassSetup() => _context = CreateExpensiveDbContext(); // BIR MARTA, BUTUN KLASS uchun

    [OneTimeTearDown]
    public void ClassCleanup() => _context.Dispose();
}
```

```
[OneTimeSetUp] — QIMMAT RESURSLARNI (DB connection, IN-
MEMORY server), BUTUN TEST KLASSI UCHUN, FAQAT **BIR MARTA**
YARATISH IMKONINI BERADI (xUnit'dagi IClassFixture<T>ga
FUNKSIONAL JIHATDAN TENG) — [SetUp]dan FARQLI O'LAROQ, HAR
TEST UCHUN EMAS, BALKI BUTUN KLASS UCHUN, FAQAT BIR MARTA
BAJARILADI.
```

### `Assert.That()` — Constraint-Based Assertion Model

```csharp
Assert.That(result, Is.EqualTo(5));
Assert.That(result, Is.GreaterThan(0));
Assert.That(list, Has.Count.EqualTo(3));
Assert.That(() => calculator.Divide(10, 0), Throws.TypeOf<DivideByZeroException>());
```

```
NUnit'ning ZAMONAVIY ASSERTION SINTAKSISI — "CONSTRAINT-
BASED MODEL" DEB ATALADI: `Assert.That(actual, constraint)`
— BU, INGLIZ TILIGA YAQIN, O'QILISHI OSON SINTAKSIS TAQDIM
ETADI ("Assert that result IS EqualTo 5" — "Tasdiqla, natija
5ga teng"). Bu, xUnit'ning `Assert.Equal(expected, actual)`
KABI, "CLASSIC" (klassik, alohida metod nomli) MODELIGA
NISBATAN, KO'PROQ MOSLASHUVCHAN VA KENGAYTIRILADIGAN
(extensible) ARXITEKTURAGA EGA.
```

## 5. Code (Amaliy kod)

```csharp
// NuGet: NUnit, NUnit3TestAdapter, Microsoft.NET.Test.Sdk

[TestFixture]
public class CalculatorTests
{
    private Calculator _calculator;

    [SetUp]
    public void Setup()
    {
        _calculator = new Calculator(); // Har test oldidan — toza holat
    }

    [Test]
    public void Add_TwoPositiveNumbers_ReturnsCorrectSum()
    {
        // Arrange
        int a = 5, b = 3;

        // Act
        var result = _calculator.Add(a, b);

        // Assert
        Assert.That(result, Is.EqualTo(8));
    }

    [TestCase(10, 2, 5)]
    [TestCase(9, 3, 3)]
    [TestCase(-6, 2, -3)]
    public void Divide_VariousInputs_ReturnsExpectedResult(int a, int b, int expected)
    {
        var result = _calculator.Divide(a, b);
        Assert.That(result, Is.EqualTo(expected));
    }

    [Test]
    public void Divide_ByZero_ThrowsDivideByZeroException()
    {
        Assert.That(() => _calculator.Divide(10, 0), Throws.TypeOf<DivideByZeroException>());
    }

    [Test]
    public async Task GetEmployeeAsync_ExistingId_ReturnsEmployee()
    {
        var service = new EmployeeService(CreateInMemoryDbContext());
        var employee = await service.GetEmployeeAsync(1);
        Assert.That(employee, Is.Not.Null);
    }
}
```

```bash
# Testlarni ishga tushirish
dotnet test
```

## 6. Keng tarqalgan xatolar / noto'g'ri tushunchalar

```
❌ "NUnit va xUnit — ATRIBUTLAR NOMI FARQ QILADI, XOLOS,
   BOSHQA HECH QANDAY FARQ YO'Q" — TO'LIQ TO'G'RI EMAS!
   LIFECYCLE BOSHQARUVI HAM FARQ QILADI: xUnit, HAR TEST
   UCHUN, YANGI KLASS INSTANSIYASI YARATADI (constructor
   orqali "setup"). NUnit — BITTA KLASS INSTANSIYASINI,
   BARCHA TESTLAR UCHUN QAYTA ISHLATISHI MUMKIN (test
   parallellashtirish sozlamalariga qarab), [SetUp] METODI
   ORQALI "TOZALAYDI".

❌ "[SetUp] va [OneTimeSetUp] — BIR XIL, FARQ YO'Q" — YO'Q!
   [SetUp] — HAR TEST METODI OLDIDAN, QAYTA-QAYTA
   BAJARILADI. [OneTimeSetUp] — BUTUN TEST KLASSI UCHUN,
   FAQAT BIR MARTA BAJARILADI (birinchi test ishga tushishidan
   oldin).

❌ "NUnit'da, xUnit'dagi kabi, [Theory]/[InlineData] MAVJUD
   EMAS" — YO'Q, NUnit'da, XUDDI SHU MAQSAD UCHUN, `[TestCase]`
   ATRIBUTI MAVJUD — FUNKSIONALLIK BIR XIL, FAQAT NOM VA
   SINTAKSIS FARQ QILADI.

❌ "Assert.That() va Assert.AreEqual() — bir xil, ULARNI
   ARALASH ISHLATISH XAVFSIZ" — TEXNIK JIHATDAN, IKKALASI HAM
   ISHLAYDI (NUnit — ESKI, "CLASSIC" MODEL — Assert.AreEqual()
   NI HAM QO'LLAB-QUVVATLAYDI), LEKIN, BITTA LOYIHADA, IZCHIL-
   LIK UCHUN, FAQAT BITTA USLUBNI (odatda Constraint-Based —
   Assert.That()) TANLASH TAVSIYA ETILADI.
```

## 7. Exam (Interview savollari)

**1. NUnit va xUnit orasidagi ASOSIY, LIFECYCLE (hayot sikli)
DARAJASIDAGI FARQ nima?**
xUnit — HAR TEST METODI UCHUN, TEST KLASSINING YANGI
INSTANSIYASINI YARATADI (constructor — "setup" vazifasini
bajaradi). NUnit — EXPLICIT `[SetUp]`/`[TearDown]`
ATRIBUTLARI ORQALI, HAR TEST OLDIDAN/KEYIN, ALOHIDA METODLARNI
CHAQIRADI — LIFECYCLE BOSHQARUVI, ANIQROQ, ALOHIDA
NOMLANGAN METODLAR ORQALI AMALGA OSHIRILADI.

**2. `[SetUp]` va `[OneTimeSetUp]` orasidagi FARQ nima?**
`[SetUp]` — HAR TEST METODI OLDIDAN, QAYTA-QAYTA BAJARILADI
(har test — "toza holat"da boshlanadi). `[OneTimeSetUp]` —
BUTUN TEST KLASSI UCHUN, FAQAT BIR MARTA (BIRINCHI TEST
ISHGA TUSHISHIDAN OLDIN) BAJARILADI — QIMMAT RESURSLARNI
BIR MARTA YARATISH UCHUN ISHLATILADI.

**3. NUnit'ning "Constraint-Based" Assertion modeli
(`Assert.That(actual, constraint)`), "Classic" modeldan
(`Assert.AreEqual(expected, actual)`) NIMASI BILAN FARQ
QILADI?**
Constraint-Based model — INGLIZ TILIGA YAQIN, O'QILISHI OSON
SINTAKSIS TAQDIM ETADI, VA KO'PROQ MOSLASHUVCHAN,
KENGAYTIRILADIGAN (custom constraint yozish mumkin)
ARXITEKTURAGA EGA. Classic model — ODDIY, ALOHIDA-ALOHIDA
NOMLANGAN METODLAR (`Assert.AreEqual`, `Assert.IsTrue`) ORQALI
ISHLAYDI.

**4. NUnit'da, xUnit'ning `[Theory]`/`[InlineData]`
FUNKSIONALLIGIGA MOS KELUVCHI ATRIBUT QAYSI, va u qanday
ISHLATILADI?**
`[TestCase]` — BIR XIL TEST MANTIG'INI, TURLI KIRISH
QIYMATLARI BILAN, BIR NECHA MARTA BAJARISH IMKONINI BERADI —
HAR `[TestCase(...)]` QATORI, TEST METODI PARAMETRLARIGA MOS
QIYMATLARNI UZATADI.

**5. Nima uchun, BITTA LOYIHADA, xUnit va NUnit'NI, ODDIY
HOLLARDA, ARALASH ISHLATISH TAVSIYA ETILMAYDI?**
Chunki, IKKI FREYMVORK — TURLI TEST RUNNER, TURLI LIFECYCLE
BOSHQARUVI, VA TURLI ASSERTION SINTAKSISIGA EGA — ULARNI
ARALASH ISHLATISH, LOYIHANING TEST INFRATUZILMASINI
MURAKKABLASHTIRADI, KONFIGURATSIYA (NuGet paketlari, CI/CD
sozlamalari) IKKI XIL FREYMVORKGA MOS BO'LISHI KERAK BO'LADI,
VA JAMOA A'ZOLARI UCHUN, IZCHIL BO'LMAGAN KODBAZA YARATADI.
