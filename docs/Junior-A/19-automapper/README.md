# AutoMapper — ProjectTo, Conditional Mapping, Inheritance — Junior A

## 1. Nima? (Ta'rif)

**AutoMapper** — bir obyekt (masalan Entity) dan ikkinchisiga
(masalan DTO) **mapping**ni (property'larni ko'chirishni) avtomatik
bajaradigan .NET kutubxonasi.

## 2. Nima uchun kerak?

Har DTO↔Entity mapping'ni **qo'lda** (`dto.Name = entity.Name; dto.Age
= entity.Age; ...`) yozish — takrorlanuvchi va **xato qilish oson**
(bitta maydonni unutish). AutoMapper — bu **boilerplate**ni
avtomatlashtiradi.

## 3. Ichida nima sodir bo'ladi? (Mexanizm)

### 3.1 Profile klass — mapping konfiguratsiya

```csharp
public class EmployeeMappingProfile : Profile
{
    public EmployeeMappingProfile()
    {
        CreateMap<Employee, EmployeeDto>();
        CreateMap<CreateEmployeeDto, Employee>();
    }
}
```

```
AutoMapper — DEFAULT holda, BIR XIL NOMLI propertylarni AVTOMATIK
moslashtiradi (Convention-based) — masalan `Employee.FullName` →
`EmployeeDto.FullName` — HECH QANDAY qo'shimcha kod SHART EMAS.
```

### 3.2 `IMapper` — inject va ishlatish

```csharp
builder.Services.AddAutoMapper(typeof(Program).Assembly); // Profile'larni AVTOMATIK topadi

public class EmployeeService
{
    private readonly IMapper _mapper;
    public EmployeeService(IMapper mapper) => _mapper = mapper;

    public EmployeeDto GetDto(Employee entity) => _mapper.Map<EmployeeDto>(entity);
}
```

### 3.3 `ForMember()` — custom property mapping

```csharp
CreateMap<Employee, EmployeeDto>()
    .ForMember(dest => dest.DepartmentName, opt => opt.MapFrom(src => src.Department.Name))
    .ForMember(dest => dest.FullAge, opt => opt.MapFrom(src => DateTime.Now.Year - src.BirthYear));
```

### 3.4 `ReverseMap()` — teskari mapping

```csharp
CreateMap<Employee, EmployeeDto>().ReverseMap(); // EmployeeDto → Employee HAM AVTOMATIK yaratiladi
```

### 3.5 `Ignore()` — mapping'dan chiqarib tashlash

```csharp
CreateMap<CreateEmployeeDto, Employee>()
    .ForMember(dest => dest.Id, opt => opt.Ignore()) // Id — DB AVTOMATIK generatsiya qiladi
    .ForMember(dest => dest.PasswordHash, opt => opt.Ignore());
```

### 3.6 `ProjectTo<T>()` — EF Core bilan, SQL darajasida mapping

```csharp
// ❌ Map<T>() — BUTUN Entity DB'DAN YUKLANADI, KEYIN C#'da mapping qilinadi
var employees = await _context.Employees.ToListAsync();
var dtos = _mapper.Map<List<EmployeeDto>>(employees); // BARCHA ustunlar YUKLANDI!

// ✅ ProjectTo<T>() — SQL SELECT'ning O'ZI faqat KERAKLI ustunlarni SO'RAYDI!
var dtos2 = await _context.Employees
    .ProjectTo<EmployeeDto>(_mapper.ConfigurationProvider)
    .ToListAsync();
// SQL: SELECT e.id, e.full_name FROM employees e (FAQAT DTO'da BOR maydonlar!)
```

```
Map<T>() vs ProjectTo<T>() — XOTIRA VA TEZLIK farqi:

Map<T>():
  1. DB'dan BUTUN Entity (BARCHA ustun) YUKLANADI
  2. C# xotirasida — HAR PROPERTY'GA property KO'CHIRILADI
  3. Keraksiz ustunlar HAM tarmoqdan O'TADI (behuda)

ProjectTo<T>():
  1. AutoMapper — DTO'da QAYSI propertylar BORLIGINI biladi
  2. EF Core'ga FAQAT O'SHA ustunlarni SO'RASHNI "AYTADI"
  3. SQL SELECT — FAQAT kerakli ustunlar (N+1 muammosini HAM
     KAMAYTIRISHI mumkin, chunki nested mapping — JOIN'GA
     TARJIMA QILINADI)
```

### 3.7 Conditional Mapping — `Condition()`, `PreCondition()`

```csharp
CreateMap<Employee, EmployeeDto>()
    .ForMember(dest => dest.Bonus, opt => opt.Condition(src => src.YearsOfService > 1)) // Faqat shart BAJARILSA property KO'CHIRILADI
    .ForMember(dest => dest.Salary, opt => opt.PreCondition(src => src.IsActive)); // Mapping BOSHLANISHIDAN OLDIN tekshiriladi
```

```
Condition()    — HAR PROPERTY uchun, MAPPING VAQTIDA tekshiriladi
PreCondition() — property EVALUATE qilinishidan OLDIN (masalan,
                 og'ir hisoblashni O'TKAZIB YUBORISH uchun)
```

### 3.8 Mapping Inheritance — meros olgan klasslar

```csharp
public abstract class Employee { public string FullName { get; set; } = null!; }
public class Manager : Employee { public int TeamSize { get; set; } }

CreateMap<Employee, EmployeeDto>()
    .Include<Manager, ManagerDto>(); // Sub-klass mapping'ini "ULASH"

CreateMap<Manager, ManagerDto>()
    .IncludeBase<Employee, EmployeeDto>(); // Bazaviy mapping'ni "MEROS OLISH"
```

### 3.9 `AssertConfigurationIsValid()` — validation

```csharp
var mapperConfig = new MapperConfiguration(cfg => cfg.AddProfile<EmployeeMappingProfile>());
mapperConfig.AssertConfigurationIsValid(); // BARCHA CreateMap'lar TO'G'RI mos KELISHINI TEKSHIRADI
```

```
Bu — ODATDA UNIT TEST'da chaqiriladi — agar DTO'da mapping
qilinmagan (ignore QILINMAGAN) property BO'LSA — TEST MUVAFFAQIYATSIZ
bo'ladi, XATO DEPLOY'DAN OLDIN ANIQLANADI.
```

### 3.10 Profil Assembly'dan ro'yxatga olish

```csharp
builder.Services.AddAutoMapper(Assembly.GetExecutingAssembly()); // BUTUN assembly'dagi Profile'larni QIDIRADI

// Bir nechta assembly
builder.Services.AddAutoMapper(typeof(EmployeeMappingProfile).Assembly, typeof(OrderMappingProfile).Assembly);
```

### 3.11 Mapster — alternativa, tezroq

```
Mapster — AutoMapper'GA MUQOBIL, ODATDA TEZROQ (compile-time
kod generatsiya QILISH imkoniyati BOR — AutoMapper esa RUNTIME'da
Reflection-asosli). Sintaksis biroz FARQ QILADI, lekin g'oya BIR XIL.
```

## 4. Kod — real ERP misolida to'liq AutoMapper

```csharp
public class EmployeeMappingProfile : Profile
{
    public EmployeeMappingProfile()
    {
        CreateMap<Employee, EmployeeDto>()
            .ForMember(d => d.DepartmentName, opt => opt.MapFrom(s => s.Department.Name));

        CreateMap<CreateEmployeeCommand, Employee>()
            .ForMember(d => d.Id, opt => opt.Ignore())
            .ForMember(d => d.CreatedAt, opt => opt.MapFrom(_ => DateTime.UtcNow));
    }
}

public class GetEmployeesHandler : IRequestHandler<GetEmployeesQuery, List<EmployeeDto>>
{
    private readonly AppDbContext _context;
    private readonly IMapper _mapper;

    public async Task<List<EmployeeDto>> Handle(GetEmployeesQuery query, CancellationToken ct)
        => await _context.Employees
            .ProjectTo<EmployeeDto>(_mapper.ConfigurationProvider)
            .ToListAsync(ct);
}
```

## 5. Qachon ishlatish kerak?

| Vaziyat | Yechim |
|---|---|
| Entity → DTO, oddiy mapping | `CreateMap` + Convention |
| DB'dan kelayotgan LIST, faqat kerakli maydonlar | `ProjectTo<T>()` |
| Shartli mapping (masalan bonus faqat aniq holatda) | `Condition()` |
| Sub-klass mapping'lari | `Include`/`IncludeBase` |
| Configuration to'g'riligini TEST qilish | `AssertConfigurationIsValid()` |

## 6. Muhim nuqtalar

- `ProjectTo<T>()` — **EF Core so'rovlari** uchun **HAR DOIM**
  `Map<T>()`dan afzal (N+1 va keraksiz ma'lumot yuklashni oldini
  oladi).
- Murakkab, ko'p shartli mapping — AutoMapper'ning **"sehri"**
  o'qilishini **qiyinlashtirishi** mumkin — juda murakkab holatlarda
  **oddiy extension method** (`ToDto()`) ko'proq **tushunarli**
  bo'lishi mumkin.
- `AssertConfigurationIsValid()` — CI/CD pipeline'da **unit test**
  sifatida ishga tushirilishi tavsiya etiladi.

## 7. Imtihon savollari

1. `Map<T>()` va `ProjectTo<T>()` orasidagi farq nima — SQL so'rov
   nuqtai nazaridan?
2. `Condition()` va `PreCondition()` orasidagi farq nima?
3. `Include`/`IncludeBase` mapping inheritance'da qanday ishlaydi?
4. `AssertConfigurationIsValid()` nima uchun foydali?
5. Nima uchun `ProjectTo<T>()` N+1 muammosini kamaytirishga yordam
   berishi mumkin?
6. Mapster AutoMapper'dan qanday farq qiladi?
