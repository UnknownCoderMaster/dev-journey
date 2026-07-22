# Mocking, Testing — xUnit, Fact, Theory, Assert — Junior C

## 1. Nima?

**Unit test** — kodni kichik bo'laklarga bo'lib, har birini
alohida tekshirish.
**Mocking** — bog'liq komponentlarni "soxta" versiyasi bilan
almashtirish.

## 2. Nima uchun kerak?

```csharp
// Bu metodda DB bor — uni test qilish uchun haqiqiy DB kerakmi?
public async Task<Employee> GetByIdAsync(int id)
{
    return await _context.Employees.FindAsync(id);
}
// Yechim: _context ni mock qilamiz — haqiqiy DB shart emas!
```

## 3. xUnit — asosiy atributlar

```csharp
public class EmployeeServiceTests
{
    // Fact — parametrsiz, bitta test
    [Fact]
    public void GetFullName_ReturnsCorrectName()
    {
        // Arrange — tayyorlov
        var emp = new Employee { FirstName = "Orzibek", LastName = "Toshmatov" };
        var service = new EmployeeService();

        // Act — amal
        var result = service.GetFullName(emp);

        // Assert — tekshirish
        Assert.Equal("Orzibek Toshmatov", result);
    }

    // Theory — parametrli, bir nechta test
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
}
```

## 4. Assert metodlari

```csharp
Assert.Equal(expected, actual);
Assert.NotEqual(expected, actual);
Assert.True(condition);
Assert.False(condition);
Assert.Null(obj);
Assert.NotNull(obj);
Assert.Throws<Exception>(() => action());
Assert.Contains(item, collection);
Assert.Empty(collection);
Assert.IsType<T>(obj);
```

## 5. Mocking — NSubstitute

```csharp
// NuGet: NSubstitute
using NSubstitute;

[Fact]
public async Task GetById_ReturnsEmployee_WhenExists()
{
    // Arrange
    var mockRepo = Substitute.For<IEmployeeRepository>();
    var expected = new Employee { Id = 1, Name = "Orzibek" };
    mockRepo.GetByIdAsync(1).Returns(expected);

    var service = new EmployeeService(mockRepo);

    // Act
    var result = await service.GetByIdAsync(1);

    // Assert
    Assert.Equal(expected.Name, result.Name);
    await mockRepo.Received(1).GetByIdAsync(1); // 1 marta chaqirildi
}
```

## 6. Object Mocking — nima?

```csharp
// Haqiqiy — SMTP serverga ulanadi
IEmailService realEmail = new SmtpEmailService();

// Mock — hech qayerga ulanmaydi
IEmailService mockEmail = Substitute.For<IEmailService>();
mockEmail.SendAsync(Arg.Any<string>(), Arg.Any<string>())
         .Returns(Task.CompletedTask);
```

Mock qilish uchun **interfeys** kerak — shuning uchun
`IEmployeeRepository`, `IEmailService` muhim!

## 7. Qo'shimcha nuqtalar

- **AAA Pattern** (Arrange, Act, Assert) — test strukturasi standarti.
- **Test izolyatsiyasi** — har bir test boshqasiga ta'sir qilmasin.
- **`IClassFixture<T>`** — bir marta yaratib, barcha testlarda ishlatish.
- **`[Skip]`** — testni vaqtincha o'chirish:
  ```csharp
  [Fact(Skip = "Hali tayyor emas")]
  ```

## 8. Imtihon savollari

1. `Fact` va `Theory` orasidagi farq nima?
2. Nima uchun haqiqiy DB o'rniga mock ishlatiladi?
3. Mocking uchun nima uchun interfeys kerak?
4. AAA pattern nima?
5. `Assert.Throws<T>` qachon ishlatiladi?
