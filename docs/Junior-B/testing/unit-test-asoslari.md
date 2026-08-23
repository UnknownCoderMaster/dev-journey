# Unit Test Asoslari — Junior B

## 1. What (Nima?)

**Unit Test** — DASTUR KODINING **ENG KICHIK, MUSTAQIL
QISMINI** ("unit" — odatda BITTA METOD YOKI KLASS), **QOLGAN
TIZIMDAN IZOLATSIYA QILINGAN HOLDA** (tashqi dependencylar —
DB, FAYL TIZIMI, TARMOQ — MOCK/FAKE QILINGAN HOLDA) TEKSHIRISH
JARAYONI. Unit Test'ning ASOSIY MAQSADI — "BU KICHIK KOD
QISMI, BERILGAN KIRISH MA'LUMOTLARIDA, KUTILGAN NATIJANI
QAYTARADIMI?" DEGAN SAVOLGA, **AVTOMATIK, TEZKOR** JAVOB
BERISH.

## 2. Real hayot analogiyasi

**Unit Test — SANOAT KONVEYERIDA, HAR BIR MAYDA VINTNI,
ALOHIDA, TASHQI TA'SIRLARSIZ SINASH.** Mashina ZAVODI — MOTOR
YIG'ISHDAN OLDIN, HAR BIR MAYDA DETALNI (vint, prujina) —
"AGAR MEN UNGA MA'LUM KUCH QO'LLASAM, U KUTILGANDEK
BUKILADIMI?" DEB, ALOHIDA, BOSHQA DETALLARDAN AJRATIB
(izolatsiyada) TEKSHIRADI — BUTUN MOTORNI YIG'IB, KEYIN
SINASH (integration test) — MUAMMONI, QAYSI ANIQ VINTDA
EKANINI TOPISHNI QIYINLASHTIRADI.

## 3. Why (Nega kerak?)

Unit Test'lar — **REGRESSIYANI (avval ishlagan kodning
buzilishi) DARHOL ANIQLASH**, **REFACTORING'GA ISHONCH BERISH**
(kod tuzilishini o'zgartirganda, funksionallik buzilmaganini
kafolatlash), VA **DOKUMENTATSIYA VAZIFASINI BAJARISH**
(test — kod QANDAY ISHLASHI KERAKLIGINING, ISHLAYDIGAN,
TEKSHIRILGAN MISOLI) UCHUN ZARUR. Ular, MANUAL (QO'LDA)
TEKSHIRISHGA NISBATAN, **YUZLAB MARTA TEZROQ** VA **HAR SAFAR,
BIR XIL, ISHONCHLI TARZDA** BAJARILADI.

## 4. Internals (Ichki mexanizm)

### AAA Pattern — Arrange, Act, Assert

```csharp
[Fact]
public void CalculateDiscount_PremiumCustomer_Returns20PercentOff()
{
    // Arrange — test uchun boshlang'ich holatni tayyorlash
    var customer = new Customer { Type = CustomerType.Premium };
    var orderTotal = 100_000m;

    // Act — test qilinayotgan amalni bajarish
    var discount = DiscountCalculator.Calculate(customer, orderTotal);

    // Assert — natijani kutilgan qiymat bilan solishtirish
    Assert.Equal(20_000m, discount);
}
```

```
AAA PATTERN — HAR BIR TEST METODINI, UCH ANIQ QISMGA
BO'LISHNI TAVSIYA QILADI: Arrange (tayyorlash) — TEST UCHUN
KERAKLI OBYEKTLAR/MA'LUMOTLARNI YARATISH. Act (harakat) —
TEKSHIRILAYOTGAN METODNI CHAQIRISH. Assert (tasdiqlash) —
NATIJANI, KUTILGAN QIYMAT BILAN SOLISHTIRISH. Bu STRUKTURA,
TESTNI, O'QISH VA TUSHUNISHNI SEZILARLI OSONLASHTIRADI.
```

### Mock, Stub, Fake — DEPENDENCY ISOLATION USULLARI

```csharp
public interface IEmailService
{
    Task SendAsync(string to, string subject, string body);
}

// Test — MOCK OBYEKTI orqali, HAQIQIY EMAIL YUBORMASDAN, TEKSHIRADI
[Fact]
public async Task RegisterUser_ValidData_SendsWelcomeEmail()
{
    var mockEmailService = new Mock<IEmailService>(); // Moq kutubxonasi
    var userService = new UserService(mockEmailService.Object);

    await userService.RegisterAsync("ali@mail.com", "Ali");

    mockEmailService.Verify(x => x.SendAsync("ali@mail.com", It.IsAny<string>(), It.IsAny<string>()), Times.Once);
}
```

```
Mock — DEPENDENCY'NING (masalan IEmailService) "SOXTA"
IMPLEMENTATSIYASI — HAQIQIY EMAIL YUBORMAYDI, LEKIN, "QANDAY
CHAQIRILGANI" (parametrlar, chaqirilish soni) NI KUZATIB
BORADI VA TEKSHIRISH IMKONINI BERADI. Stub — OLDINDAN
BELGILANGAN, "SOXTA" QIYMAT QAYTARADIGAN OBYEKT (masalan,
"IsValid() — HAR DOIM TRUE QAYTARSIN"). Fake — SODDALASHTIRIL-
GAN, LEKIN HAQIQIY MANTIQQA EGA IMPLEMENTATSIYA (masalan,
IN-MEMORY "SOXTA" DATABASE). Bularning HAMMASI — "TEST
DOUBLE" (test o'rinbosari) DEB UMUMIY NOM BILAN ATALADI.
```

### F.I.R.S.T. Prinsiplari — YAXSHI UNIT TEST'NING XUSUSIYATLARI

```
Fast (Tezkor)        — Unit test, MILLISEKUNDLARDA bajarilishi
                         kerak (DB/tarmoq — YO'Q).
Independent (Mustaqil) — HAR TEST, BOSHQA TESTLARDAN MUSTAQIL,
                         ISTALGAN TARTIBDA BAJARILA OLISHI KERAK.
Repeatable (Takrorlanuvchi) — HAR SAFAR, BIR XIL MUHITDA, BIR
                         XIL NATIJA BERISHI KERAK (tasodifiy
                         qiymatlar, joriy vaqt — MUAMMO
                         MANBAI).
Self-Validating (O'z-o'zini tasdiqlovchi) — TEST, "PASS"/
                         "FAIL" DEB, AVTOMATIK, ANIQ NATIJA
                         BERISHI KERAK (qo'lda tekshirish
                         SHART bo'lmasligi kerak).
Timely (O'z vaqtida)  — TEST, KOD BILAN BIRGA (yoki undan
                         OLDIN — TDD), YOZILISHI KERAK, KEYIN
                         EMAS.
```

### Test Pyramid — Unit/Integration/E2E NISBATI

```
        /\
       /E2E\        ← Kam sonli, sekin, qimmat (butun tizim)
      /------\
     /Integr. \     ← O'rtacha son, o'rtacha tezlik
    /----------\
   /  Unit Test \   ← Ko'p sonli, tez, arzon (asosiy qism)
  /--------------\
```

```
TEST PYRAMID — TAVSIYA ETILGAN STRATEGIYA: KO'PCHILIK
TESTLAR — TEZKOR, ARZON UNIT TESTLAR (piramidaning ASOSI)
BO'LISHI KERAK, KAMROQ SONDA — INTEGRATION TESTLAR (bir
nechta komponent birgalikda), ENG KAM SONDA — E2E (End-to-
End, butun tizim) TESTLAR (SEKIN, QIMMAT, LEKIN ENG
REALISTIK).
```

## 5. Code (Amaliy kod)

```csharp
// Test qilinadigan biznes logika
public class DiscountCalculator
{
    public static decimal Calculate(Customer customer, decimal orderTotal)
    {
        if (orderTotal <= 0) throw new ArgumentException("Summa musbat bo'lishi kerak");

        return customer.Type switch
        {
            CustomerType.Premium => orderTotal * 0.20m,
            CustomerType.Regular => orderTotal * 0.05m,
            _ => 0m
        };
    }
}

// AAA pattern bilan yozilgan, to'liq unit test to'plami
public class DiscountCalculatorTests
{
    [Fact]
    public void Calculate_PremiumCustomer_Returns20Percent()
    {
        // Arrange
        var customer = new Customer { Type = CustomerType.Premium };

        // Act
        var result = DiscountCalculator.Calculate(customer, 1000m);

        // Assert
        Assert.Equal(200m, result);
    }

    [Fact]
    public void Calculate_NegativeTotal_ThrowsArgumentException()
    {
        var customer = new Customer { Type = CustomerType.Regular };
        Assert.Throws<ArgumentException>(() => DiscountCalculator.Calculate(customer, -100m));
    }

    [Theory]
    [InlineData(CustomerType.Premium, 1000, 200)]
    [InlineData(CustomerType.Regular, 1000, 50)]
    [InlineData(CustomerType.New, 1000, 0)]
    public void Calculate_DifferentCustomerTypes_ReturnsCorrectDiscount(
        CustomerType type, decimal total, decimal expected)
    {
        var customer = new Customer { Type = type };
        var result = DiscountCalculator.Calculate(customer, total);
        Assert.Equal(expected, result);
    }
}
```

```csharp
// Dependency Injection + Mock — HAQIQIY LOYIHADAGI SERVIS TESTI
public class OrderServiceTests
{
    [Fact]
    public async Task PlaceOrder_ValidOrder_CallsPaymentGatewayOnce()
    {
        var mockPaymentGateway = new Mock<IPaymentGateway>();
        mockPaymentGateway.Setup(x => x.ChargeAsync(It.IsAny<decimal>())).ReturnsAsync(true);

        var orderService = new OrderService(mockPaymentGateway.Object);
        await orderService.PlaceOrderAsync(new Order { Total = 500_000m });

        mockPaymentGateway.Verify(x => x.ChargeAsync(500_000m), Times.Once);
    }
}
```

## 6. Keng tarqalgan xatolar / noto'g'ri tushunchalar

```
❌ "Unit Test, REAL DB'ga ULANIB, YOZISH — TO'G'RI YONDASHUV"
   — YO'Q! Bu, TESTNI, "SEKIN", "TASHQI HOLATGA BOG'LIQ", VA
   "INDEPENDENT" PRINSIPINI BUZUVCHI QILADI — HAQIQIY UNIT
   TEST — DEPENDENCYLARNI (DB, TARMOQ) MOCK/FAKE QILISHI
   KERAK.

❌ "Testlar, KOD YOZIB BO'LGANDAN KEYIN, VAQT QOLSA, YOZILISHI
   KERAK" — F.I.R.S.T. prinsiplaridagi "Timely" — TESTLARNI,
   KOD BILAN BIRGA (yoki undan OLDIN, TDD YONDASHUVIDA)
   YOZISHNI TAVSIYA QILADI — "KEYINROQ" YOZISH, KO'PINCHA,
   UMUMAN YOZILMASLIKKA OLIB KELADI.

❌ "100% CODE COVERAGE (kod qamrovi) — SIFATLI TEST
   SUITE'NING KAFOLATI" — YO'Q! CODE COVERAGE — FAQAT, "QANCHA
   QATOR KOD, KAMIDA BIR MARTA, TEST TOMONIDAN BAJARILGANI"NI
   O'LCHAYDI — BU, TEST'LARNING HAQIQATDA, TO'G'RI, MA'NOLI
   ASSERTIONLARGA EGA EKANLIGINI KAFOLATLAMAYDI (masalan,
   ASSERTIONSIZ, FAQAT KODNI "CHAQIRUVCHI" TEST — 100%
   COVERAGE BERADI, LEKIN HECH NARSANI TEKSHIRMAYDI).

❌ "Mock va Stub — BIR XIL NARSA, SINONIM" — QISMAN
   NOTO'G'RI: Mock — "QANDAY CHAQIRILGANI"NI KUZATADI VA
   TEKSHIRISH IMKONINI BERADI (Verify). Stub — SHUNCHAKI,
   OLDINDAN BELGILANGAN QIYMAT QAYTARADI, CHAQIRILISHINI
   ALOHIDA TEKSHIRISH ODATDA TALAB QILINMAYDI.
```

## 7. Exam (Interview savollari)

**1. AAA Pattern (Arrange, Act, Assert) NIMANI ANGLATADI, va
u NIMA UCHUN FOYDALI?**
Arrange — TEST UCHUN BOSHLANG'ICH HOLATNI TAYYORLASH. Act —
TEKSHIRILAYOTGAN AMALNI BAJARISH. Assert — NATIJANI, KUTILGAN
QIYMAT BILAN SOLISHTIRISH. Bu STRUKTURA, HAR TEST METODINI,
ANIQ, UCH QISMGA BO'LIB, O'QISH VA TUSHUNISHNI OSONLASHTIRADI.

**2. Mock, Stub, va Fake orasidagi FARQNI TUSHUNTIRING.**
Mock — DEPENDENCY'NING "QANDAY CHAQIRILGANI"NI KUZATIB
BORADI VA TEKSHIRISH (Verify) IMKONINI BERADI. Stub —
OLDINDAN BELGILANGAN, "SOXTA" QIYMAT QAYTARADI. Fake —
SODDALASHTIRILGAN, LEKIN HAQIQIY MANTIQQA EGA
IMPLEMENTATSIYA (masalan in-memory database). Barchasi — 
umumiy "Test Double" tushunchasiga kiradi.

**3. F.I.R.S.T. prinsiplaridagi 5 ta xususiyatni sanang va
qisqacha tushuntiring.**
Fast (tezkor bajarilish), Independent (boshqa testlardan
mustaqil), Repeatable (har safar bir xil natija), Self-
Validating (avtomatik pass/fail), Timely (kod bilan birga
yoziladi).

**4. 100% Code Coverage, NIMA UCHUN, YAGONA O'ZI, TEST
SUITE'NING SIFATINI KAFOLATLAMAYDI?**
Chunki Code Coverage — FAQAT, "QANCHA QATOR KOD BAJARILGANI"NI
O'LCHAYDI, ASSERTIONLARNING MA'NOLI, TO'G'RI EKANLIGINI EMAS
— ASSERTIONSIZ, FAQAT METODNI CHAQIRUVCHI TEST HAM, YUQORI
COVERAGE BERISHI MUMKIN, LEKIN HECH QANDAY HAQIQIY XATONI
TOPMAYDI.

**5. Test Pyramid nima, va u NIMA UCHUN, KO'PCHILIK
TESTLARNI, UNIT TEST DARAJASIDA (E2E emas) YOZISHNI
TAVSIYA QILADI?**
Test Pyramid — Unit (ko'p, tez, arzon), Integration (o'rtacha),
E2E (kam, sekin, qimmat) TESTLAR NISBATINI TAVSIYA QILUVCHI
STRATEGIYA. Unit Testlar — TEZKOR VA ARZON BO'LGANI UCHUN,
KO'P SONDA YOZISH, TEZKOR FIDBEK BERADI. E2E Testlar — SEKIN,
QIMMAT, VA MO'RT (fragile) BO'LGANI UCHUN, FAQAT, ENG MUHIM,
"UCHTAN-UCHGA" (end-to-end) STSENARIYLAR UCHUN SAQLANADI.
