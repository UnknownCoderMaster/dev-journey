# xUnit (Unit Test) — Junior B

## 1. What (Nima?)

**xUnit** — .NET EKOSISTEMASIDA, ENG KENG TARQALGAN, **ZAMONAVIY,
OCHIQ MANBALI (open-source) UNIT TEST FREYMVORKI**. U,
"xUnit" NOMINI, TEST FREYMVORKLARINING UMUMIY OILASIDAN
(JUnit, NUnit — barchasi "xUnit arxitekturasi" DEB ATALUVCHI
UMUMIY PATTERNGA ASOSLANGAN) OLADI. xUnit.net — MICROSOFT'NING
.NET Core/.NET 5+ LOYIHALARI UCHUN, RASMIY TAVSIYA ETILGAN,
DEFAULT TANLOV.

## 2. Real hayot analogiyasi

**Unit Test — MASHINA ZAVODIDAGI, HAR BIR DETALNI, YIG'ISHDAN
OLDIN, ALOHIDA TEKSHIRISH.** Zavod, MOTORNI (bitta "unit" —
metod/klass) YIG'IB BO'LGACH, UNI, BUTUN MASHINAGA
O'RNATISHDAN OLDIN, ALOHIDA STENDDA, "TO'G'RI ISHLAYDIMI?"
DEB SINAYDI. xUnit — BU SINOVLARNI, **AVTOMATIK, TAKRORLA-
NUVCHI, VA TEZKOR** TARZDA, HAR SAFAR KOD O'ZGARTIRILGANDA,
QAYTA-QAYTA O'TKAZISH IMKONINI BERUVCHI "SINOV STENDI"
INFRATUZILMASI.

## 3. Why (Nega kerak?)

Kod O'ZGARTIRILGANDA (masalan REFACTORING, YANGI FUNKSIYA
QO'SHISH), **AVVAL ISHLAGAN FUNKSIONALLIKNING BUZILISHI**
(regression) — REAL LOYIHALARDA ENG KENG TARQALGAN MUAMMOLARDAN
BIRI. QO'LDA, HAR SAFAR, BUTUN ILOVANI QAYTA TEKSHIRISH —
**VAQT TALAB QILADI VA XATOGA MOYIL**. Unit Test — HAR BIR
KICHIK FUNKSIYANI (metod), **AVTOMATIK, SEKUNDLAR ICHIDA**
QAYTA TEKSHIRISH IMKONINI BERADI — bu, DASTURCHIGA,
O'ZGARISH KIRITISHDA, **ISHONCH VA TEZKOR FIDBEK (feedback)**
BERADI.

## 4. Internals (Ichki mexanizm)

### xUnit — TEST DISCOVERY (test'larni AVTOMATIK TOPISH)

```csharp
public class CalculatorTests
{
    [Fact]
    public void Add_TwoPositiveNumbers_ReturnsSum()
    {
        var result = Calculator.Add(2, 3);
        Assert.Equal(5, result);
    }
}
```

```
xUnit TEST RUNNER — ASSEMBLY'NI (.dll) SKANERLAB, `[Fact]`
YOKI `[Theory]` ATRIBUTI BILAN BELGILANGAN, **PUBLIC, VOID
(yoki Task) QAYTARUVCHI, PARAMETRSIZ METODLARNI**, REFLECTION
ORQALI, AVTOMATIK ANIQLAYDI VA BAJARADI — DASTURCHI, TESTLARNI
"RO'YXATDAN O'TKAZISH" UCHUN, HECH QANDAY QO'SHIMCHA
KONFIGURATSIYA YOZMAYDI.
```

### `[Fact]` vs `[Theory]` — BITTA HOLAT vs KO'P HOLAT

```csharp
[Theory]
[InlineData(2, 3, 5)]
[InlineData(-1, 1, 0)]
[InlineData(0, 0, 0)]
public void Add_VariousInputs_ReturnsExpectedSum(int a, int b, int expected)
{
    var result = Calculator.Add(a, b);
    Assert.Equal(expected, result);
}
```

```
[Fact] — BITTA, ANIQ, PARAMETRSIZ TEST HOLATINI IFODALAYDI.
[Theory] — BIR XIL TEST MANTIG'INI, TURLI KIRISH
QIYMATLARI BILAN (`[InlineData]`) QAYTA-QAYTA BAJARISH
IMKONINI BERADI — xUnit RUNNER, HAR `[InlineData]` QATORI
UCHUN, ALOHIDA, MUSTAQIL TEST NATIJASINI (pass/fail)
GENERATSIYA QILADI.
```

### Test Isolation — HAR TEST, YANGI KLASS INSTANSIYASIDA

```
xUnit — HAR BIR [Fact]/[Theory] METODI UCHUN, TEST KLASSINING
**YANGI, ALOHIDA INSTANSIYASINI** YARATADI (constructor — 
HAR TEST OLDIDAN, QAYTA CHAQIRILADI) — bu, TESTLAR ORASIDA,
"HOLAT SIZIB O'TISHI" (shared mutable state) MUAMMOSINING
OLDINI OLADI — HAR TEST, BOSHQA TESTLARDAN MUSTAQIL, "TOZA"
HOLATDA BOSHLANADI.
```

### `IClassFixture<T>` — TESTLAR ORASIDA RESURS "BO'LISHISH"

```csharp
public class DatabaseFixture : IDisposable
{
    public AppDbContext Context { get; }
    public DatabaseFixture() => Context = CreateInMemoryContext();
    public void Dispose() => Context.Dispose();
}

public class EmployeeServiceTests : IClassFixture<DatabaseFixture>
{
    private readonly DatabaseFixture _fixture;
    public EmployeeServiceTests(DatabaseFixture fixture) => _fixture = fixture;
    // Testlar, _fixture.Context'ni ISHLATADI — BIR MARTA yaratiladi, BARCHA testlar orasida BO'LISHILADI
}
```

```
IClassFixture<T> — QIMMAT RESURSLARNI (masalan DB CONNECTION,
IN-MEMORY DATABASE) — HAR TEST UCHUN QAYTA YARATISH O'RNIGA,
**BIR MARTA YARATIB, BUTUN TEST KLASSI DOIRASIDA "BO'LISHISH"**
IMKONINI BERADI — bu, TEST ISOLATION'NING ANIQ EMASLIGI
XAVFINI, RESURS YARATISH TEZLIGI FOYDASIGA, ONGLI RAVISHDA
"ALMASHTIRISH" (tradeoff).
```

## 5. Code (Amaliy kod)

```csharp
// Test qilinadigan kod
public class Calculator
{
    public int Add(int a, int b) => a + b;
    public int Divide(int a, int b)
    {
        if (b == 0) throw new DivideByZeroException("Nolga bo'lish mumkin emas");
        return a / b;
    }
}

// xUnit testlari
public class CalculatorTests
{
    private readonly Calculator _calculator = new(); // Har test uchun — yangi instansiya

    [Fact]
    public void Add_TwoPositiveNumbers_ReturnsCorrectSum()
    {
        // Arrange
        int a = 5, b = 3;

        // Act
        var result = _calculator.Add(a, b);

        // Assert
        Assert.Equal(8, result);
    }

    [Theory]
    [InlineData(10, 2, 5)]
    [InlineData(9, 3, 3)]
    public void Divide_ValidInputs_ReturnsCorrectResult(int a, int b, int expected)
    {
        var result = _calculator.Divide(a, b);
        Assert.Equal(expected, result);
    }

    [Fact]
    public void Divide_ByZero_ThrowsDivideByZeroException()
    {
        // Exception'ni tekshirish — Assert.Throws orqali
        Assert.Throws<DivideByZeroException>(() => _calculator.Divide(10, 0));
    }

    [Fact]
    public async Task GetEmployeeAsync_ExistingId_ReturnsEmployee()
    {
        // Async metodlarni test qilish
        var service = new EmployeeService(CreateInMemoryDbContext());
        var employee = await service.GetEmployeeAsync(1);
        Assert.NotNull(employee);
    }
}
```

```bash
# Testlarni ishga tushirish
dotnet test
dotnet test --filter "FullyQualifiedName~CalculatorTests" # Faqat ma'lum klass testlari
```

## 6. Keng tarqalgan xatolar / noto'g'ri tushunchalar

```
❌ "Unit Test — BAZAGA (real DB) ulanib, TO'LIQ INTEGRATSIYANI
   TEKSHIRISHI KERAK" — YO'Q! HAQIQIY UNIT TEST — FAQAT BITTA
   "UNIT"NI (metod/klass), IZOLATSIYADA (dependencylar mock/
   fake qilingan holda) TEKSHIRADI — REAL DB'GA ULANISH —
   INTEGRATION TEST HISOBLANADI, xUnit ESA — IKKALASINI HAM
   YOZISH UCHUN ISHLATILISHI MUMKIN, LEKIN FARQNI TUSHUNISH
   MUHIM.

❌ "[Theory] va [InlineData] — [Fact]'dan KO'RA YOMONROQ,
   MURAKKABROQ" — YO'Q! [Theory] — AKSINCHA, BIR NECHTA
   O'XSHASH [Fact] YOZISHNI, BITTA, PARAMETRLASHTIRILGAN
   TESTGA "SIQIB", KOD TAKRORLANISHINI (DRY) KAMAYTIRADI.

❌ "Test klassidagi FIELD'LAR, BARCHA TESTLAR ORASIDA
   BO'LISHILADI" — YO'Q! xUnit, HAR TEST UCHUN, YANGI KLASS
   INSTANSIYASINI YARATADI — CONSTRUCTOR'DA INITSIALLASHTIRILGAN
   FIELD'LAR, HAR TEST UCHUN, "TOZA" HOLATDA QAYTA YARATILADI
   (IClassFixture ISHLATILMASA).

❌ "Assert.Equal(expected, actual) va Assert.Equal(actual,
   expected) — PARAMETRLAR TARTIBI MUHIM EMAS" — TEXNIK
   JIHATDAN, NATIJA (pass/fail) BIR XIL, LEKIN, XATOLIK
   XABARI (masalan "Expected: 5, Actual: 3") — PARAMETRLAR
   TARTIBIGA QARAB O'ZGARADI — TO'G'RI TARTIB (expected,
   actual) — DEBUG QILISHNI OSONLASHTIRADI.
```

## 7. Exam (Interview savollari)

**1. `[Fact]` va `[Theory]` orasidagi FARQ nima?**
`[Fact]` — BITTA, ANIQ, PARAMETRSIZ TEST HOLATINI IFODALAYDI.
`[Theory]` — BIR XIL TEST MANTIG'INI, `[InlineData]` ORQALI
BERILGAN, TURLI KIRISH QIYMATLARI BILAN, BIR NECHTA MARTA
BAJARISH IMKONINI BERADI.

**2. xUnit, HAR TEST METODI UCHUN, TEST KLASSINING YANGI
INSTANSIYASINI YARATISHI, NIMA UCHUN MUHIM (Test Isolation)?**
Bu, TESTLAR ORASIDA, "HOLAT SIZIB O'TISHI" (shared mutable
state) MUAMMOSINING OLDINI OLADI — HAR TEST, BOSHQA
TESTLARNING NATIJASIGA TA'SIR QILMAYDIGAN, MUSTAQIL, "TOZA"
HOLATDA BOSHLANADI — bu, TESTLARNING BAJARILISH TARTIBIGA
BOG'LIQ BO'LMAGAN, ISHONCHLI NATIJALARNI TA'MINLAYDI.

**3. `IClassFixture<T>` nima uchun ISHLATILADI, va u QANDAY
TRADEOFF BILAN KELADI?**
`IClassFixture<T>` — QIMMAT RESURSLARNI (masalan DB
CONNECTION), HAR TEST UCHUN QAYTA YARATISH O'RNIGA, BIR
MARTA YARATIB, BUTUN TEST KLASSI DOIRASIDA "BO'LISHISH"
IMKONINI BERADI. TRADEOFF — TEST ISOLATION KAMROQ QAT'IY
BO'LADI (agar bir test, resurs holatini o'zgartirsa, boshqa
testga ta'sir qilishi mumkin), LEKIN RESURS YARATISH TEZLIGI
YUTADI.

**4. Unit Test va Integration Test orasidagi ASOSIY FARQNI
TUSHUNTIRING.**
Unit Test — BITTA "UNIT"NI (metod/klass), IZOLATSIYADA
(dependencylar — mock/fake qilingan holda) TEKSHIRADI, TEZKOR
BAJARILADI. Integration Test — BIR NECHTA KOMPONENTNING
(masalan REAL/IN-MEMORY DB bilan) BIRGALIKDA ISHLASHINI
TEKSHIRADI, ODATDA SEKINROQ, LEKIN REALROQ STSENARIYNI
QAMRAB OLADI.

**5. Async metodlarni (masalan `Task<T>` qaytaruvchi) xUnit
bilan TEST QILISHDA, NIMA E'TIBORGA OLINISHI KERAK?**
Test metodi O'ZI, `async Task` (yoki `async Task<T>`) sifatida
YOZILISHI KERAK (void EMAS) — xUnit, `Task` QAYTARUVCHI TEST
METODLARINI, TO'G'RI, `await` ORQALI KUTIB, ASINXRON
OPERATSIYA TUGAGUNCHA, TEST NATIJASINI (pass/fail) ANIQLAYDI.
`async void` ISHLATILSA — xUnit, EXCEPTION'LARNI TO'G'RI
USHLAY OLMASLIGI MUMKIN.
