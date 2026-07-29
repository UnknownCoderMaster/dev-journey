# Method Mocking, Testing — Middle D

> Test asoslari (xUnit, Fact/Theory, AAA Pattern) chuqur tarzda
> [07-testing-mocking](../07-testing-mocking/README.md)da (Junior C)
> yoritilgan. Bu fayl — **mocking kutubxonalarini solishtirish** va
> mock turlariga (strict/loose, method/property mocking) e'tibor
> qaratadi.

## 1. Nima? (Ta'rif)

**Mock** — haqiqiy obyekt o'rniga ishlatiladigan, **oldindan
belgilangan xatti-harakatga ega** soxta obyekt. Mocking — testda
tashqi bog'liqliklarni (DB, HTTP, fayl tizimi) **nazorat qilinadigan**
soxta versiyalar bilan almashtirish jarayoni.

## 2. Nima uchun kerak?

Test — **tez, ishonchli va izolyatsiyalangan** bo'lishi kerak.
Haqiqiy DB/tarmoq bilan test qilish — bu shartlarning **hech
birini** ta'minlamaydi (sekin, beqaror, boshqa testlarga bog'liq
bo'lib qolishi mumkin).

## 3. Ichida nima sodir bo'ladi? (Mexanizm)

### 3.1 Mocking uchun nima uchun interfeys kerak

```csharp
public interface IEmployeeRepository { Task<Employee?> GetByIdAsync(int id); }
```

Mocking kutubxonalari (Moq, NSubstitute) — **runtime**da
**Dynamic Proxy** yaratadi (Reflection.Emit orqali) — bu FAQAT
**interfeys** yoki **virtual metod**lar ustidan mumkin. `sealed`
klass yoki `virtual` bo'lmagan metod — mock QILIB BO'LMAYDI.

### 3.2 Moq vs NSubstitute vs FakeItEasy

| | Moq | NSubstitute | FakeItEasy |
|---|---|---|---|
| Sintaksis | `mock.Setup(x => x.Method()).Returns(val)` | `sub.Method().Returns(val)` | `A.CallTo(() => fake.Method()).Returns(val)` |
| O'qilishi | O'rtacha (Setup/Returns) | ✅ Eng tabiiy (C# syntaxga yaqin) | Yaxshi |
| Mashhurlik | ✅ Eng ko'p ishlatiladi | Ikkinchi o'rinda | Kamroq tarqalgan |
| Licensing | MIT (ochiq) | MIT (ochiq) | MIT (ochiq) |

**NSubstitute** — sintaksisi **eng tabiiy** (mock metodini
to'g'ridan chaqirib, keyin `.Returns()` qo'shish) — ko'p jamoa
buni **o'qilishi oson** deb tanlaydi.

### 3.3 Method mocking — Returns, Throws, Callback

```csharp
// Moq misolida
var mockRepo = new Mock<IEmployeeRepository>();
mockRepo.Setup(r => r.GetByIdAsync(1)).ReturnsAsync(new Employee { Id = 1 });
mockRepo.Setup(r => r.GetByIdAsync(999)).ThrowsAsync(new NotFoundException("Topilmadi"));
mockRepo.Setup(r => r.GetByIdAsync(It.IsAny<int>()))
    .Callback<int>(id => Console.WriteLine($"Chaqirildi: {id}"))
    .ReturnsAsync((Employee?)null);
```

### 3.4 Property mocking

```csharp
var mockConfig = new Mock<IConfiguration>();
mockConfig.SetupGet(c => c["Jwt:Issuer"]).Returns("https://test.example.com");
```

### 3.5 Verify — metod chaqirilganligini tekshirish

```csharp
mockRepo.Verify(r => r.GetByIdAsync(1), Times.Once);      // ANIQ 1 marta
mockRepo.Verify(r => r.GetByIdAsync(2), Times.Never);      // HECH QACHON chaqirilmagan
mockRepo.Verify(r => r.SaveAsync(), Times.AtLeastOnce);    // Kamida 1 marta
```

### 3.6 Strict vs Loose mock

```
Loose mock (DEFAULT):
  Sozlanmagan metod chaqirilsa — DEFAULT qiymat (null, 0, false)
  QAYTARILADI, XATO BERMAYDI

Strict mock:
  Sozlanmagan metod chaqirilsa — EXCEPTION tashlanadi ("bu
  chaqiruvni KUTMAGAN edim!")

var strictMock = new Mock<IEmployeeRepository>(MockBehavior.Strict);
```

```
Loose — ODATDA yetarli, kamroq boilerplate
Strict — TEST'ning "aynan nima chaqirilishini kutayotganini" ANIQ
         belgilash kerak bo'lganda (masalan xavfsizlik-kritik kod)
```

### 3.7 AAA Pattern va Test izolyatsiyasi

Bular batafsil [07-testing-mocking](../07-testing-mocking/README.md)da
yoritilgan — qisqacha: **Arrange** (tayyorlov), **Act** (amal),
**Assert** (tekshirish); har test — mustaqil, boshqa testga bog'liq
BO'LMASLIGI kerak.

### 3.8 Test naming — `MethodName_Scenario_Expected`

```csharp
[Fact]
public async Task GetById_WhenEmployeeNotFound_ThrowsNotFoundException() { }

[Fact]
public async Task CreateEmployee_WithValidData_ReturnsCreatedEmployee() { }
```

## 4. Kod — to'liq misol (Moq bilan)

```csharp
public class EmployeeServiceTests
{
    [Fact]
    public async Task GetById_WhenExists_ReturnsEmployee()
    {
        // Arrange
        var mockRepo = new Mock<IEmployeeRepository>();
        mockRepo.Setup(r => r.GetByIdAsync(1))
            .ReturnsAsync(new Employee { Id = 1, FullName = "Orzibek" });
        var service = new EmployeeService(mockRepo.Object);

        // Act
        var result = await service.GetByIdAsync(1);

        // Assert
        Assert.Equal("Orzibek", result.FullName);
        mockRepo.Verify(r => r.GetByIdAsync(1), Times.Once);
    }
}
```

## 5. Qachon ishlatish kerak?

| Vaziyat | Yechim |
|---|---|
| Yangi loyiha, tabiiy sintaksis afzal | NSubstitute |
| Katta jamoa, ko'p namuna/community yordam kerak | Moq |
| Sozlanmagan chaqiruvni ANIQ nazorat qilish kerak | Strict mock |
| Metod chaqirilganligini tekshirish | `Verify`/`Received` |

## 6. Muhim nuqtalar

- Faqat **interfeys** yoki **virtual** metodlar mock qilinishi
  mumkin — bu, **DIP** (Dependency Inversion) tamoyiliga rioya
  qilishning yana bir amaliy sababi.
- Strict mock — testni **qattiqroq** qiladi, lekin **moslashuvchan
  emas** (kichik o'zgarish ko'p testni buzishi mumkin) — ehtiyotkorlik
  bilan ishlatilishi kerak.

## 7. Imtihon savollari

1. Mock yaratish uchun nima uchun interfeys yoki virtual metod
   kerak?
2. Moq va NSubstitute sintaksisi orasidagi asosiy farq nima?
3. Strict va Loose mock orasidagi farq nima?
4. `Verify`/`Received` nima uchun kerak va u nimani tekshiradi?
5. Property mocking qanday amalga oshiriladi?
