# NSubstitute — Middle D

## 1. Nima? (Ta'rif)

**NSubstitute** — .NET uchun **tabiiy, o'qilishi oson** sintaksisga
ega mocking kutubxonasi — mock metodini **to'g'ridan chaqirib**,
keyin uning ustiga `.Returns()` qo'shish orqali ishlaydi (Moq'ning
`Setup(x => x.Method())` uslubidan farqli).

## 2. Nima uchun kerak?

Testda tashqi bog'liqliklarni (Repository, HTTP Client, Email
Service) **soxta** versiya bilan almashtirish kerak — NSubstitute
buni **eng kam boilerplate** bilan amalga oshiradi.

## 3. Ichida nima sodir bo'ladi? (Mexanizm)

### 3.1 `Substitute.For<T>()` — mock yaratish

```csharp
var repo = Substitute.For<IEmployeeRepository>();
```

Ichkarida — `Castle.Core` (Dynamic Proxy) yordamida, RUNTIME'da
`IEmployeeRepository` interfeysini **implement qiluvchi** yangi
klass generatsiya qilinadi, har metod chaqiruvi **NSubstitute
tomonidan** ushlab qolinadi (interception).

### 3.2 `Returns()` — qiymat qaytarish

```csharp
repo.GetByIdAsync(1).Returns(new Employee { Id = 1, FullName = "Orzibek" });

var result = await repo.GetByIdAsync(1); // → Employee { Id = 1, FullName = "Orzibek" }
```

### 3.3 `Returns(x => ...)` — lambda bilan

```csharp
repo.GetByIdAsync(Arg.Any<int>()).Returns(callInfo =>
{
    int id = callInfo.Arg<int>();
    return new Employee { Id = id, FullName = $"Employee-{id}" };
});
```

### 3.4 `ReturnsForAnyArgs()` — har qanday argument uchun

```csharp
repo.GetByIdAsync(default).ReturnsForAnyArgs(new Employee { FullName = "Har qanday ID uchun" });
```

`Returns(Arg.Any<int>())` bilan farqi — `ReturnsForAnyArgs` —
argument turi/qiymatidan **umuman qat'i nazar** BIR XIL natija
qaytaradi, `Arg.Any<T>()` esa **argument matching** ning bir qismi.

### 3.5 `Throws<T>()` — exception tashlash

```csharp
repo.GetByIdAsync(999).Returns<Task<Employee?>>(x => throw new NotFoundException("Topilmadi"));

// Yoki oddiy metodlar uchun
repo.When(r => r.Delete(999)).Throw(new InvalidOperationException());
```

### 3.6 `Arg.Any<T>()`, `Arg.Is<T>()` — argument matching

```csharp
repo.GetByIdAsync(Arg.Any<int>()).Returns(defaultEmployee); // ISTALGAN int uchun

repo.GetByIdAsync(Arg.Is<int>(id => id > 100)).Returns(specialEmployee); // FAQAT shart bajarilsa
```

### 3.7 `Received(n)` — n marta chaqirilganligini tekshirish

```csharp
await repo.Received(1).GetByIdAsync(1);       // ANIQ 1 marta chaqirilgan bo'lishi kerak
await repo.Received().SaveAsync();             // Kamida 1 marta (parametr KO'RSATILMASA)
await repo.DidNotReceive().DeleteAsync(1);     // HECH QACHON chaqirilmagan
await repo.ReceivedWithAnyArgs().GetByIdAsync(default); // Argumentdan QAT'I NAZAR, chaqirilganmi
```

### 3.8 Async mock

```csharp
repo.GetByIdAsync(1).Returns(Task.FromResult<Employee?>(new Employee { Id = 1 }));
// YOKI qulayroq:
repo.GetByIdAsync(1).Returns(new Employee { Id = 1 }); // NSubstitute AVTOMATIK Task'ga O'RAYDI
```

NSubstitute — `async Task<T>` metodlar uchun **avtomatik**
`Task.FromResult()` bilan o'rab beradi — qo'lda `Task.FromResult`
yozish **shart emas** (ko'p holatlarda).

## 4. Kod — to'liq misol (xUnit bilan)

```csharp
public class EmployeeServiceTests
{
    [Fact]
    public async Task CreateEmployee_SendsWelcomeEmail()
    {
        // Arrange
        var mockRepo = Substitute.For<IEmployeeRepository>();
        var mockEmail = Substitute.For<IEmailService>();
        mockRepo.CreateAsync(Arg.Any<Employee>()).Returns(1);

        var service = new EmployeeService(mockRepo, mockEmail);
        var dto = new CreateEmployeeDto { Name = "Orzibek", Email = "o@mail.com" };

        // Act
        await service.CreateEmployeeAsync(dto);

        // Assert
        await mockEmail.Received(1).SendAsync(dto.Email, Arg.Any<string>());
        await mockRepo.Received(1).CreateAsync(Arg.Is<Employee>(e => e.FullName == "Orzibek"));
    }

    [Fact]
    public async Task GetById_WhenNotFound_ThrowsNotFoundException()
    {
        var mockRepo = Substitute.For<IEmployeeRepository>();
        mockRepo.GetByIdAsync(999).Returns((Employee?)null);
        var service = new EmployeeService(mockRepo, Substitute.For<IEmailService>());

        await Assert.ThrowsAsync<NotFoundException>(() => service.GetByIdAsync(999));
    }
}
```

## 5. Qachon ishlatish kerak?

| Vaziyat | Yechim |
|---|---|
| Interfeys metodini "soxta" qilib qaytarish | `Returns()` |
| Argumentga qarab turli natija | `Returns(callInfo => ...)` |
| Faqat ma'lum argument bilan chaqirilganda | `Arg.Is<T>()` |
| Metod chaqirilganini tasdiqlash | `Received(n)` |
| Xato holatini simulyatsiya qilish | `Throws`/`throw` lambda ichida |

## 6. Muhim nuqtalar

- NSubstitute — faqat **interfeys/virtual metod**larni mock qiladi
  (`sealed`/non-virtual — mumkin emas).
- `Received()` — parametrsiz "kamida bir marta" degani, `Received(0)`
  — `DidNotReceive()` bilan bir xil ma'noni beradi (aniqlik uchun
  `DidNotReceive()` afzal).
- Async metodlar uchun NSubstitute — ko'p holatda `Task.FromResult`
  yozishni shart qilmaydi, bu kodni qisqartiradi.

## 7. Imtihon savollari

1. `Substitute.For<T>()` ichkarida qanday mexanizm orqali ishlaydi?
2. `Returns()` va `ReturnsForAnyArgs()` orasidagi farq nima?
3. `Arg.Any<T>()` va `Arg.Is<T>()` orasidagi farq nima?
4. `Received(1)` va `DidNotReceive()` nima uchun kerak?
5. NSubstitute async metodlarni mock qilishda qanday qulaylik
   beradi?
