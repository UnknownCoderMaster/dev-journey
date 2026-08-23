# PerEntityDto, ILinkToEntity Pattern — Junior B

## 1. What (Nima?)

**PerEntityDto** — HAR BIR ENTITY (masalan `Employee`) uchun
**O'ZINING ALOHIDA DTO klassini** yaratish YONDASHUVI (masalan
`EmployeeDto`, `EmployeeListDto`, `EmployeeDetailDto` — HAR BIRI
BOSHQA MAQSAD UCHUN). **`ILinkToEntity<T>`** — DTO klassni
**QAYSI ENTITY'GA "BOG'LANGANI"NI** interfeys ORQALI ANIQ
BELGILAYDIGAN, va AutoMapper KONFIGURATSIYASINI **AVTOMATLASHTIRISH**
uchun ISHLATILADIGAN PATTERN (masalan bir NECHTA DTO uchun
`CreateMap<T, TDto>()` ni QO'LDA TAKRORLASH O'RNIGA, REFLECTION
ORQALI AVTOMATIK TOPISH).

## 2. Real hayot analogiyasi

**PerEntityDto — BIR ODAMNING TURLI HUJJATLARI.** BIR ODAM
(Entity — `Employee`) — TURLI VAZIYATLARDA TURLI HUJJATGA EGA:
PASPORTDA (DetailDto) — TO'LIQ MA'LUMOT (tug'ilgan sana, manzil),
VIZIT KARTOCHKASIDA (ListDto) — FAQAT ISM VA LAVOZIM. HAR HUJJAT
— BIR XIL ODAM HAQIDA, LEKIN TURLI MAQSAD UCHUN, TURLI DARAJADA
BATAFSIL.

**ILinkToEntity — HUJJATNING "USTIGA YOZILGAN YORLIQ".** Har
HUJJATDA (DTO) — "BU KIMNING HUJJATI" degan YORLIQ (interfeys
belgisi) BOR — bu, ARXIV XODIMIGA (AutoMapper konfiguratsiyasiga)
HAR HUJJATNI QAYSI ODAM (Entity) BILAN AVTOMATIK BOG'LASHNI
AYTIB BERADI, QO'LDA "BU — SHU ODAMNIKI" DEB YOZIB O'TIRISH
SHART EMAS.

## 3. Why (Nega kerak?)

Katta ERP tizimida — BITTA Entity (`Employee`) uchun O'NLAB
DTO KERAK BO'LISHI MUMKIN (List uchun QISQA, Detail uchun
TO'LIQ, Export uchun BOSHQA FORMAT). Agar HAR DTO uchun
AutoMapper Profile'da QO'LDA `CreateMap<Employee, XxxDto>()`
YOZILSA — bu **TAKRORLANUVCHI, UNUTILISHI OSON** kod. `ILinkToEntity<T>`
PATTERNI — REFLECTION ORQALI, LOYIHADAGI **BARCHA** DTO
klasslarni TOPIB, AVTOMATIK `CreateMap` KONFIGURATSIYASINI
GENERATSIYA QILADI — bu, YANGI DTO QO'SHILGANDA, Profile faylini
O'ZGARTIRISHNI **UMUMAN SHART EMAS** QILADI.

## 4. Internals (Ichki mexanizm)

### `ILinkToEntity<T>` interfeysi — DIZAYN

```csharp
public interface ILinkToEntity<TEntity> { }

public class EmployeeListDto : ILinkToEntity<Employee>
{
    public int Id { get; set; }
    public string FullName { get; set; } = null!;
}

public class EmployeeDetailDto : ILinkToEntity<Employee>
{
    public int Id { get; set; }
    public string FullName { get; set; } = null!;
    public decimal Salary { get; set; }
    public string DepartmentName { get; set; } = null!;
}
```

```
Interfeys — MARKER (belgi) sifatida ISHLATILADI, HECH QANDAY
METOD TALAB QILMAYDI — FAQAT "BU DTO — Employee ENTITY'GA
BOG'LANGAN" DEGAN MA'LUMOTNI TASHIYDI. TypeScript'dagi "brand
type"larga O'XSHASH G'OYA.
```

### Reflection ORQALI AVTOMATIK Profile GENERATSIYASI

```csharp
public class AutoRegisteredMappingProfile : Profile
{
    public AutoRegisteredMappingProfile()
    {
        // Assembly'DAGI BARCHA ILinkToEntity<T> IMPLEMENT QILGAN
        // klasslarni REFLECTION orqali TOPISH
        var dtoTypes = Assembly.GetExecutingAssembly()
            .GetTypes()
            .Where(t => t.GetInterfaces().Any(i =>
                i.IsGenericType && i.GetGenericTypeDefinition() == typeof(ILinkToEntity<>)));

        foreach (var dtoType in dtoTypes)
        {
            var entityType = dtoType.GetInterfaces()
                .First(i => i.IsGenericType && i.GetGenericTypeDefinition() == typeof(ILinkToEntity<>))
                .GetGenericArguments()[0];

            // Entity -> DTO va DTO -> Entity — IKKALASI HAM AVTOMATIK
            CreateMap(entityType, dtoType);
            CreateMap(dtoType, entityType);
        }
    }
}
```

```
Bu — REFLECTION'ning "STARTUP VAQTIDA BIR MARTA BAJARILISHI"
tamoyiliga TAYANADI: AutoMapper KONFIGURATSIYASI — ILOVA
ISHGA TUSHGANDA (BIR MARTA) QURILADI, RUNTIME'DA (HAR SO'ROVDA)
QAYTA REFLECTION BAJARILMAYDI — shuning uchun bu YONDASHUV,
"HAR MAP() CHAQIRUVIDA REFLECTION" bilan CHALKASHTIRILMASLIGI
KERAK (PERFORMANCE JIHATIDAN — XAVFSIZ).
```

### `PerEntityDto` — nima uchun BITTA "UMUMIY" DTO EMAS

```
❌ BITTA "UniversalEmployeeDto" — BARCHA MAYDONLARNI O'Z ICHIGA
   OLADI (List UCHUN HAM, Detail UCHUN HAM) — bu:
   - Over-fetching — List so'ralganda HAM, KERAKSIZ MAYDONLAR
     (masalan TO'LIQ TARIX) YUKLANADI/UZATILADI
   - Xavfsizlik XAVFI — List endpoint'i, TASODIFAN MAXFIY
     MA'LUMOTNI (masalan PasswordHash) OSHKOR QILISHI mumkin

✅ PerEntityDto — HAR ENDPOINT — FAQAT O'ZIGA KERAKLI MAYDONLARNI
   O'Z ICHIGA OLGAN, ALOHIDA DTO ISHLATADI — ANIQ KONTRAKT,
   MINIMAL MA'LUMOT UZATISH.
```

## 5. Code (Amaliy kod)

```csharp
// Marker interfeys
public interface ILinkToEntity<TEntity> { }

// Entity
public class Employee
{
    public int Id { get; set; }
    public string FullName { get; set; } = null!;
    public decimal Salary { get; set; }
    public string PasswordHash { get; set; } = null!; // MAXFIY — DTO'larga UMUMAN QO'SHILMAYDI!
    public Department Department { get; set; } = null!;
}

// HAR MAQSAD UCHUN ALOHIDA DTO — ILinkToEntity<Employee> ORQALI BOG'LANGAN
public class EmployeeListItemDto : ILinkToEntity<Employee>
{
    public int Id { get; set; }
    public string FullName { get; set; } = null!;
}

public class EmployeeDetailDto : ILinkToEntity<Employee>
{
    public int Id { get; set; }
    public string FullName { get; set; } = null!;
    public decimal Salary { get; set; }
    public string DepartmentName { get; set; } = null!;
}

public class CreateEmployeeDto : ILinkToEntity<Employee>
{
    public string FullName { get; set; } = null!;
    public decimal Salary { get; set; }
}
```

```csharp
// AVTOMATIK Profile — YANGI DTO QO'SHILSA, PROFILE FAYLI O'ZGARTIRILMAYDI!
public class LinkedEntityMappingProfile : Profile
{
    public LinkedEntityMappingProfile()
    {
        var linkedTypes = typeof(Employee).Assembly.GetTypes()
            .SelectMany(t => t.GetInterfaces()
                .Where(i => i.IsGenericType && i.GetGenericTypeDefinition() == typeof(ILinkToEntity<>))
                .Select(i => new { Dto = t, Entity = i.GetGenericArguments()[0] }));

        foreach (var pair in linkedTypes)
        {
            CreateMap(pair.Entity, pair.Dto);
            CreateMap(pair.Dto, pair.Entity)
                .ForAllMembers(opt => opt.Condition((src, dest, srcMember) => srcMember != null));
        }
    }
}
```

```csharp
// Ishlatish — Controller'da
[HttpGet]
public async Task<List<EmployeeListItemDto>> GetAll()
    => await _context.Employees.ProjectTo<EmployeeListItemDto>(_mapper.ConfigurationProvider).ToListAsync();

[HttpGet("{id}")]
public async Task<EmployeeDetailDto> GetById(int id)
    => await _context.Employees
        .ProjectTo<EmployeeDetailDto>(_mapper.ConfigurationProvider)
        .FirstAsync(e => e.Id == id);
```

## 6. Keng tarqalgan xatolar / noto'g'ri tushunchalar

```
❌ "BITTA DTO — BARCHA ENDPOINT'LAR uchun ISHLATILISHI MUMKIN,
   VAQT TEJASH uchun" — KO'RINISHDA TEZROQ, LEKIN OVER-FETCHING
   VA XAVFSIZLIK MUAMMOLARIGA (masalan MAXFIY maydon TASODIFAN
   API JAVOBIDA CHIQIB QOLISHI) OLIB KELISHI MUMKIN.

❌ "ILinkToEntity — AutoMapper'ning O'ZINING BUILT-IN interfeysi"
   — YO'Q! Bu — LOYIHA DARAJASIDA YARATILADIGAN, KUSTOM (custom)
   KONVENSIYA/PATTERN, AutoMapper KUTUBXONASINING O'ZIDA MAVJUD
   EMAS.

❌ "Reflection orqali Profile GENERATSIYASI — HAR SO'ROVDA
   BAJARILADI, SEKIN" — NOTO'G'RI! Bu — FAQAT ILOVA STARTUP'IDA,
   BIR MARTA BAJARILADI (MapperConfiguration YARATILGANDA) —
   RUNTIME PERFORMANCE'GA TA'SIR QILMAYDI.

❌ "PerEntityDto — KO'P FAYL, KO'P KOD DEGANI, YOMON" — TO'G'RI,
   BOSHLANG'ICH DTO SONI ORTADI, LEKIN HAR DTO — ANIQ, KICHIK,
   TUSHUNARLI MAQSADGA EGA — BU, UZOQ MUDDATDA, XAVFSIZLIK VA
   PERFORMANCE JIHATDAN FOYDA BERADI.
```

## 7. Exam (Interview savollari)

**1. PerEntityDto YONDASHUVI qanday MUAMMONI HAL QILADI?**
Bitta Entity uchun BITTA "universal" DTO ishlatish — OVER-FETCHING
(keraksiz ma'lumot uzatish) va XAVFSIZLIK XAVFI (maxfiy maydon
tasodifan oshkor bo'lishi) keltirib chiqarishi mumkin.
PerEntityDto — har endpoint uchun ANIQ, MINIMAL kontraktni
ta'minlaydi.

**2. `ILinkToEntity<T>` interfeysi qanday VAZIFANI BAJARADI, va
u METOD talab qiladimi?**
Bu — MARKER INTERFEYS (hech qanday METOD talab qilmaydi) —
FAQAT DTO klassni QAYSI Entity bilan "bog'liq" ekanini
BELGILAYDI. Bu ma'lumot — REFLECTION orqali, AutoMapper
konfiguratsiyasini AVTOMATIK generatsiya qilishda ISHLATILADI.

**3. Reflection orqali AVTOMATIK CreateMap generatsiyasi — QACHON
BAJARILADI, va bu PERFORMANCE'GA QANDAY TA'SIR QILADI?**
Bu — ILOVA STARTUP paytida, `MapperConfiguration` yaratilganda,
BIR MARTA bajariladi. Runtime'da (har `Map()` chaqiruvida) QAYTA
REFLECTION bajarilmaydi — shuning uchun bu, so'rovlar davomida
PERFORMANCE'GA TA'SIR QILMAYDI.

**4. Nima uchun MAXFIY maydon (masalan PasswordHash) — DTO
klasslarga UMUMAN QO'SHILMASLIGI kerak, `[JsonIgnore]` bilan
YASHIRISH O'RNIGA?**
`[JsonIgnore]` — FAQAT JSON SERIALIZATSIYADA yashiradi, lekin
maydon C# obyektida HALI HAM MAVJUD (debug, logging, boshqa
serializer orqali TASODIFAN oshkor BO'LISHI mumkin). DTO'da
UMUMAN YO'QLIGI — ENG XAVFSIZ YECHIM (defense in depth).

**5. `ProjectTo<T>()` PerEntityDto pattern bilan BIRGA
ISHLATILGANDA qanday AFZALLIK BERADI?**
`ProjectTo<T>()` — EF Core SQL so'roviga, FAQAT DTO'da MAVJUD
bo'lgan ustunlarni SO'RASHNI "AYTADI". PerEntityDto BILAN
BIRGA — bu, HAR ENDPOINT UCHUN, DB DARAJASIDA HAM MINIMAL,
ANIQ MA'LUMOT SO'RALISHINI TA'MINLAYDI (masalan List DTO'da
faqat 2 ustun bo'lsa, SQL ham FAQAT o'sha 2 ustunni SELECT qiladi).
