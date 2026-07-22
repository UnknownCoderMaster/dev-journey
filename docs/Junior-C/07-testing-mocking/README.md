# Testing, Mocking — xUnit, Fact, Theory, Assert, NSubstitute — Junior C

## 1. Nima?

**Unit test** — dasturning eng kichik bo'lagini (odatda bitta metodni)
qolgan tizimdan izolyatsiya qilib, kutilgan natijani berishini
avtomatik tekshirish. **Mocking** — test qilinayotgan kod bog'liq
bo'lgan tashqi komponentlarni (DB, HTTP client, fayl tizimi) "soxta"
(sun'iy) versiyalari bilan almashtirish jarayoni.

## 2. Nima uchun kerak?

```csharp
public async Task<Employee> GetByIdAsync(int id)
{
    return await _context.Employees.FindAsync(id);
}
```

Bu metodni test qilish uchun **haqiqiy PostgreSQL** kerakmi? Yo'q —
agar shunday bo'lganida:
- Testlar **sekin** ishlaydi (DB ulanishi, tarmoq)
- Testlar **beqaror** bo'ladi (DB holati o'zgarib turadi, parallel
  testlar bir-biriga xalaqit beradi)
- CI/CD serverida DB sozlash qo'shimcha murakkablik

Mocking yordamida — `IEmployeeRepository` interfeysi "soxta" (mock)
implementatsiya bilan almashtiriladi, va biz **faqat** `EmployeeService`
mantig'ini tekshiramiz, DB ishlash-ishlamasligidan qat'i nazar.

Testsiz — har bir o'zgarish "qo'lda tekshirish" talab qiladi, va
regressiya (eski funksionallikni buzish) sezilmasdan production'ga
chiqib ketishi mumkin.

## 3. Ichida nima sodir bo'ladi? (Mexanizm)

### 3.1 xUnit vs NUnit vs MSTest

| | xUnit | NUnit | MSTest |
|---|---|---|---|
| Atribut (oddiy test) | `[Fact]` | `[Test]` | `[TestMethod]` |
| Atribut (parametrli) | `[Theory]` + `[InlineData]` | `[TestCase]` | `[DataTestMethod]` + `[DataRow]` |
| Setup/Teardown | Constructor/`IDisposable` | `[SetUp]`/`[TearDown]` | `[TestInitialize]`/`[TestCleanup]` |
| Har testda yangi instance | ✅ Ha (default) | ❌ Yo'q (shared) | ❌ Yo'q (shared) |
| .NET ekotizimida holati | Eng ko'p ishlatiladi (ASP.NET Core standart) | Keng tarqalgan | Microsoft ichki, kamroq community |

xUnit **har bir test metodida yangi klass instance yaratadi** — bu
testlar orasida **holat sizib chiqishining oldini oladi** (test
izolyatsiyasi kafolatlanadi).

### 3.2 `[Fact]` — oddiy, parametrsiz test

```csharp
public class EmployeeServiceTests
{
    [Fact]
    public void GetFullName_ReturnsCorrectName()
    {
        // Arrange — tayyorlov: obyektlarni yaratish, kirish ma'lumotlarini tayyorlash
        var emp = new Employee { FirstName = "Orzibek", LastName = "Toshmatov" };
        var service = new EmployeeService();

        // Act — tekshirilayotgan amalni bajarish
        var result = service.GetFullName(emp);

        // Assert — natijani kutilgan qiymat bilan solishtirish
        Assert.Equal("Orzibek Toshmatov", result);
    }
}
```

### 3.3 `[Theory]` — parametrli testlar

```csharp
[Theory]
[InlineData("Orzibek", "Toshmatov", "Orzibek Toshmatov")]
[InlineData("Ali", "Valiyev", "Ali Valiyev")]
[InlineData("", "Toshmatov", " Toshmatov")]
public void GetFullName_WithDifferentNames(
    string firstName, string lastName, string expected)
{
    var emp = new Employee { FirstName = firstName, LastName = lastName };
    var service = new EmployeeService();
    var result = service.GetFullName(emp);
    Assert.Equal(expected, result);
}
```

`[InlineData]` — compile-time'da belgilangan qiymatlar (faqat const
turlar). Dinamik yoki murakkab obyektlar kerak bo'lsa:

```csharp
public class EmployeeTestData : IEnumerable<object[]>
{
    public IEnumerator<object[]> GetEnumerator()
    {
        yield return new object[] { new Employee { Age = 17 }, false };
        yield return new object[] { new Employee { Age = 18 }, true };
    }
    IEnumerator IEnumerable.GetEnumerator() => GetEnumerator();
}

[Theory]
[ClassData(typeof(EmployeeTestData))]
public void IsAdult_ChecksAgeCorrectly(Employee emp, bool expected)
{
    Assert.Equal(expected, emp.Age >= 18);
}

// MemberData — static metod/property orqali
public static IEnumerable<object[]> AgeData =>
    new List<object[]> { new object[] { 17, false }, new object[] { 18, true } };

[Theory]
[MemberData(nameof(AgeData))]
public void IsAdult_WithMemberData(int age, bool expected)
{
    Assert.Equal(expected, age >= 18);
}
```

Ichkarida xUnit runner — har bir `[InlineData]`/`[MemberData]` qatorini
**alohida test case** sifatida ko'radi va alohida-alohida ishga
tushiradi (bittasi muvaffaqiyatsiz bo'lsa, qolganlariga ta'sir
qilmaydi).

### 3.4 Assert metodlari — to'liq ro'yxat

```csharp
Assert.Equal(expected, actual);          // Qiymat tengligi
Assert.NotEqual(expected, actual);
Assert.Same(obj1, obj2);                 // Reference tengligi (bir xil obyekt)
Assert.NotSame(obj1, obj2);
Assert.True(condition);
Assert.False(condition);
Assert.Null(obj);
Assert.NotNull(obj);
Assert.Contains(item, collection);
Assert.DoesNotContain(item, collection);
Assert.Empty(collection);
Assert.NotEmpty(collection);
Assert.IsType<Employee>(obj);            // Aniq tur
Assert.IsAssignableFrom<IEmployee>(obj); // Interfeys/base klass orqali
Assert.Throws<InvalidOperationException>(() => service.DoSomething());
await Assert.ThrowsAsync<NotFoundException>(() => service.GetByIdAsync(999));
Assert.InRange(value, low, high);        // Diapazonda ekanligini tekshirish
```

### 3.5 AAA Pattern — nima uchun qat'iy tuzilma?

```
Arrange — barcha kirish ma'lumotlari, mocklar, obyektlar TAYYORLANADI
Act     — FAQAT BITTA amal (tekshirilayotgan metod) chaqiriladi
Assert  — natija tekshiriladi
```

Bu tuzilma testni **o'qish** va **debug qilish** ni osonlashtiradi —
har bir bo'lim aniq vazifaga ega, va Act qismida faqat bitta chaqiruv
bo'lishi — "aynan nima test qilinayotganini" aniq ko'rsatadi.

```csharp
// ❌ AAA buzilgan — Arrange va Act aralashib ketgan
[Fact]
public void BadTest()
{
    var service = new EmployeeService();
    var result = service.Process(new Employee { Name = "X" });
    var result2 = service.Process(new Employee { Name = "Y" }); // 2-chi Act!
    Assert.Equal("X", result.Name);
    Assert.Equal("Y", result2.Name); // Bir testda 2 ta narsa tekshirilyapti!
}
```

### 3.6 Mock nima va nima uchun interfeys kerak?

```csharp
public interface IEmployeeRepository
{
    Task<Employee?> GetByIdAsync(int id);
}

public class EmployeeService
{
    private readonly IEmployeeRepository _repo; // Interfeysga BOG'LANGAN, konkret klassga emas
    public EmployeeService(IEmployeeRepository repo) => _repo = repo;

    public async Task<string> GetNameAsync(int id)
    {
        var emp = await _repo.GetByIdAsync(id);
        return emp?.Name ?? "Noma'lum";
    }
}
```

Mock yaratish uchun **runtime**da interfeysning "soxta implementatsiyasi"
generatsiya qilinadi (Dynamic Proxy pattern orqali — NSubstitute/Moq
kabi kutubxonalar buni Reflection.Emit yordamida amalga oshiradi).
Agar `EmployeeService` `EmployeeRepository` **konkret klassga**
bog'langan bo'lsa — uni mock qilib bo'lmaydi (agar metodlar
`virtual` qilinmagan bo'lsa), chunki dynamic proxy faqat interfeys
yoki virtual metodlar ustidan qurilishi mumkin.

### 3.7 NSubstitute — sintaksis

```csharp
using NSubstitute;

[Fact]
public async Task GetById_ReturnsEmployee_WhenExists()
{
    // Arrange
    var mockRepo = Substitute.For<IEmployeeRepository>();
    var expected = new Employee { Id = 1, Name = "Orzibek" };
    mockRepo.GetByIdAsync(1).Returns(expected); // "1 chaqirilsa — expected qaytar"

    var service = new EmployeeService(mockRepo);

    // Act
    var result = await service.GetNameAsync(1);

    // Assert
    Assert.Equal("Orzibek", result);
    await mockRepo.Received(1).GetByIdAsync(1); // Aynan 1 marta chaqirilganini tekshirish
}

[Fact]
public async Task GetById_ReturnsUnknown_WhenNotFound()
{
    var mockRepo = Substitute.For<IEmployeeRepository>();
    mockRepo.GetByIdAsync(Arg.Any<int>()).Returns((Employee?)null); // Har qanday ID uchun null

    var service = new EmployeeService(mockRepo);
    var result = await service.GetNameAsync(999);

    Assert.Equal("Noma'lum", result);
}

// Exception tashlashni simulyatsiya qilish
mockRepo.GetByIdAsync(1).Returns<Task<Employee?>>(x => throw new TimeoutException());

// Chaqirilmaganini tekshirish
await mockRepo.DidNotReceive().GetByIdAsync(Arg.Any<int>());
```

### 3.8 Object Mocking — haqiqiy vs mock

```csharp
// Haqiqiy — SMTP serverga tarmoq orqali ulanadi
IEmailService realEmail = new SmtpEmailService();

// Mock — hech qayerga ulanmaydi, xotirada "sohta" javob qaytaradi
IEmailService mockEmail = Substitute.For<IEmailService>();
mockEmail.SendAsync(Arg.Any<string>(), Arg.Any<string>())
         .Returns(Task.CompletedTask);
```

Test paytida **hech qanday haqiqiy tashqi effekt** (email jo'natish,
DB yozish, tarmoq so'rovi) yuz bermasligi kerak — bu unit testlarni
tez va ishonchli qiladi.

## 4. Kod — to'liq misol (ASP.NET Core + EF Core konteksti)

```csharp
public class EmployeeServiceTests
{
    private readonly IEmployeeRepository _mockRepo;
    private readonly IEmailService _mockEmail;
    private readonly EmployeeService _sut; // "System Under Test"

    public EmployeeServiceTests() // Constructor — har test uchun QAYTA chaqiriladi
    {
        _mockRepo = Substitute.For<IEmployeeRepository>();
        _mockEmail = Substitute.For<IEmailService>();
        _sut = new EmployeeService(_mockRepo, _mockEmail);
    }

    [Fact]
    public async Task CreateEmployee_SendsWelcomeEmail_WhenSuccessful()
    {
        // Arrange
        var dto = new CreateEmployeeDto { Name = "Orzibek", Email = "o@mail.com" };
        _mockRepo.CreateAsync(Arg.Any<Employee>()).Returns(1);

        // Act
        await _sut.CreateEmployeeAsync(dto);

        // Assert
        await _mockEmail.Received(1).SendAsync(dto.Email, Arg.Any<string>());
    }

    [Theory]
    [InlineData("")]
    [InlineData(null)]
    public async Task CreateEmployee_ThrowsValidationException_WhenNameIsEmpty(string? name)
    {
        var dto = new CreateEmployeeDto { Name = name!, Email = "o@mail.com" };

        await Assert.ThrowsAsync<ValidationException>(() => _sut.CreateEmployeeAsync(dto));
    }
}
```

## 5. Qachon ishlatish kerak?

| Vaziyat | Yondashuv |
|---|---|
| Sof biznes mantiq (arifmetika, validatsiya) | `[Fact]` yoki `[Theory]`, mock kerak emas |
| Bir nechta kirish qiymat kombinatsiyasi | `[Theory]` + `[InlineData]`/`[MemberData]` |
| Tashqi bog'liqlik (DB, HTTP, email) | Interfeys + Mock (NSubstitute) |
| Bir nechta test bir xil "qimmat" resursni ulashishi kerak | `IClassFixture<T>` |
| Integration test (haqiqiy DB kerak) | Alohida test toifasi — `TestContainers` yoki in-memory DB, unit test emas |

**Test naming konvensiyasi:**

```
MethodName_Condition_ExpectedResult

GetFullName_WithEmptyLastName_ReturnsNameWithTrailingSpace
CreateEmployee_WhenEmailAlreadyExists_ThrowsValidationException
GetById_WhenIdNotFound_ReturnsNull
```

Bu format — test failed bo'lganda, nomidan darhol **nima kutilgani**
va **qaysi holatda buzilgani** aniq ko'rinadi.

**Anti-patternlar:**

```csharp
// ❌ Bitta testda ko'p narsani tekshirish (Assertion Roulette)
[Fact]
public void TestEmployee()
{
    Assert.Equal("X", emp.Name);
    Assert.Equal(25, emp.Age);
    Assert.True(emp.IsActive);
    // Qaysi biri xato bo'lsa, test raporti "TestEmployee failed" deydi — aniq emas
}

// ❌ Real DB/tarmoqqa bog'liq "unit" test
[Fact]
public async Task GetEmployee_FromRealDatabase() // Bu — integration test, unit emas!
{
    var context = new AppDbContext(realConnectionString);
    // ...
}
```

## 6. Qo'shimcha — chuqur nuqtalar

- **`IClassFixture<T>`** — bir nechta test orasida **qimmat** resursni
  (masalan, WebApplicationFactory) bir marta yaratib, ulashish uchun:
  ```csharp
  public class DatabaseFixture : IDisposable
  {
      public AppDbContext Context { get; }
      public DatabaseFixture() => Context = CreateInMemoryContext();
      public void Dispose() => Context.Dispose();
  }

  public class EmployeeTests : IClassFixture<DatabaseFixture>
  {
      private readonly DatabaseFixture _fixture;
      public EmployeeTests(DatabaseFixture fixture) => _fixture = fixture;
  }
  ```

- **Test izolyatsiyasi muhim, chunki:** agar testlar bir-biriga
  bog'liq holat (masalan static field, shared DB yozuvi) orqali
  ta'sir qilsa — testlar tartibga bog'liq bo'lib qoladi, va
  parallel ishga tushirilganda "flaky" (ba'zan o'tadi, ba'zan yo'q)
  bo'lib qoladi.

- **`[Fact(Skip = "...")]`** — testni vaqtincha o'chirish (masalan,
  funksionallik hali tayyor emas), lekin CI raporti buni "Skipped"
  deb ko'rsatadi — butunlay o'chirib tashlashdan farqli, unutilmaydi.

- **Code Coverage — foydali, lekin "yolg'on xavfsizlik" berishi
  mumkin:** 100% coverage — kod bajarilganini bildiradi, lekin
  barcha edge case lar tekshirilganini KAFOLATLAMAYDI.

- **Real loyihada uchraydigan xato:** `DateTime.Now`ga bog'liq testlar
  — vaqt o'tishi bilan "flaky" bo'lib qoladi. Yechim: `IDateTimeProvider`
  interfeysi orqali vaqtni ham mock qilish.

## 7. Imtihon savollari

1. `[Fact]` va `[Theory]` orasidagi farq nima, va `[Theory]` qachon
   ishlatiladi?
2. Nima uchun testlarda haqiqiy DB o'rniga mock ishlatiladi? 3 ta
   sabab ayting.
3. Mocking qilish uchun nima uchun aynan interfeys (yoki virtual
   metod) kerak? Konkret sealed klassni mock qilib bo'ladimi?
4. AAA pattern nima va u nima uchun test o'qilishini yaxshilaydi?
5. `Assert.Throws<T>` bilan `Assert.ThrowsAsync<T>` orasidagi farq
   nima va qachon qaysi birini ishlatasiz?
6. xUnit har bir test metodi uchun nega yangi klass instance
   yaratadi? Bu qanday muammoni oldini oladi?
7. `Received(1)` va `DidNotReceive()` NSubstitute metodlari nima
   uchun kerak?
8. Test naming konvensiyasi (`MethodName_Condition_ExpectedResult`)
   nima uchun foydali?
