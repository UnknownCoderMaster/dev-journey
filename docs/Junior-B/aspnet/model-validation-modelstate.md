# Model Validation, ModelState, Rerun Validation, Validation Attributes — Junior B

## 1. What (Nima?)

**Model Validation** — HTTP so'rovdan kelgan ma'lumotning (DTO)
**belgilangan qoidalarga** (majburiy maydon, uzunlik, format)
mos ekanligini TEKSHIRISH jarayoni. **ModelState** —
tekshiruv NATIJASINI (xato bor-yo'qligi, qaysi maydonda qanday
xato) saqlovchi obyekt. **Validation Attributes** — `[Required]`,
`[Range]` kabi, DTO klass PROPERTYLARIGA "yopishtiriladigan"
DEKLARATIV qoidalar.

## 2. Real hayot analogiyasi

**ModelState — CHEGARA NAZORATI PUNKTI.** Har bir SAYOHATCHI
(kelayotgan so'rov) — CHEGARADAN O'TISHDAN OLDIN, PASPORT
(DTO) TEKSHIRILADI. NAZORATCHI (ModelState) — HAR HUJJATNI
(PROPERTY) ALOHIDA TEKSHIRADI: "VIZA BOR-YO'QMI?" (`[Required]`),
"AMAL QILISH MUDDATI TUGAMAGANMI?" (`[Range]`). BIRON XATO
TOPILSA — SAYOHATCHI (SO'ROV) O'TKAZILMAYDI (400 Bad Request),
VA UNGA **ANIQ, QAYSI HUJJATDA MUAMMO BORLIGI** AYTILADI.

## 3. Why (Nega kerak?)

Validatsiyasiz — noto'g'ri (yoki ZARARLI) ma'lumot — **BIZNES
QOIDALARNI BUZISHI**, DB'da **NOTO'G'RI MA'LUMOT** SAQLANISHIGA,
YOKI XATTO **XAVFSIZLIK MUAMMOSIGA** (masalan, cheksiz uzun
matn — buffer/DB muammosi) OLIB KELISHI mumkin. ModelState —
bu tekshiruvni **AVTOMATLASHTIRADI**, HAR CONTROLLER'DA QO'LDA
`if (string.IsNullOrEmpty(...))` YOZISH SHART EMAS.

**FluentValidation bilan solishtirish:** Data Annotations
(`[Required]`) — SODDA, TEZ, LEKIN CHEKLANGAN (MURAKKAB SHART
YOZISH QIYIN). FluentValidation — KUCHLIROQ, LEKIN QO'SHIMCHA
NuGet PAKET talab qiladi (batafsil `docs/Junior-A/20-input-validation`da).

## 4. Internals (Ichki mexanizm)

### Model Binding + Validation — PIPELINE

```
HTTP Request Body (JSON)
    │
    ▼
Model Binding — JSON → C# DTO OBYEKTIGA "MOSLASHTIRILADI"
    │
    ▼
Validation — HAR PROPERTY, ATTRIBUTE'LAR ORQALI TEKSHIRILADI
    │
    ▼
ModelState.IsValid — TRUE/FALSE + ModelState.Errors (Dictionary)
    │
    ▼
[ApiController] — AGAR IsValid == FALSE, AVTOMATIK 400 QAYTARADI
                   (Controller Action HATTO CHAQIRILMAYDI!)
```

### `[ApiController]` — AVTOMATIK TEKSHIRUV MEXANIZMI

```
[ApiController] atributi — ICHKARIDA "Action Filter" (aniqrog'i,
IActionModelConvention) qo'shadi — bu FILTER, Action METOD
CHAQIRILISHIDAN OLDIN, ModelState.IsValid'ni TEKSHIRADI. AGAR
FALSE bo'lsa — AUTOMATIK RAVISHDA ProblemDetails (RFC 7807)
FORMATIDA 400 Bad Request QAYTARADI, ACTION METOD UMUMAN
BAJARILMAYDI.
```

### Validation Attributes — QANDAY ISHLAYDI (Reflection asosida)

```
ASP.NET Core Model Binder — DTO KLASSINING PROPERTYLARINI
REFLECTION ORQALI TEKSHIRADI, HAR PROPERTYDAGI VALIDATION
ATTRIBUTE'LARNI (ValidationAttribute'dan MEROS OLGAN) TOPADI,
VA HAR BIRINING IsValid(value) METODINI CHAQIRADI.

[Required] — IsValid() ICHIDA — value == null YOKI bo'sh
             string TEKSHIRADI
[Range(18, 65)] — IsValid() ICHIDA — value MIN/MAX oralig'ida
                   EKANINI TEKSHIRADI
```

### Custom Validation Attribute — QANDAY YOZILADI

```csharp
public class MinimumAgeAttribute : ValidationAttribute
{
    private readonly int _minimumAge;
    public MinimumAgeAttribute(int minimumAge) => _minimumAge = minimumAge;

    protected override ValidationResult? IsValid(object? value, ValidationContext context)
    {
        if (value is DateTime birthDate)
        {
            var age = DateTime.Today.Year - birthDate.Year;
            if (age < _minimumAge)
                return new ValidationResult($"Yosh {_minimumAge} dan katta bo'lishi kerak");
        }
        return ValidationResult.Success;
    }
}
```

### `IValidatableObject` — bir NECHTA MAYDONNI BIRGALIKDA TEKSHIRISH

```
Oddiy ValidationAttribute — FAQAT BITTA PROPERTY'NI TEKSHIRADI.
Agar IKKI MAYDON (masalan StartDate < EndDate) BIRGALIKDA
TEKSHIRILISHI KERAK bo'lsa — DTO klass `IValidatableObject`
INTERFEYSINI IMPLEMENT QILADI, `Validate()` METODI — ModelState
tekshiruvi VAQTIDA AVTOMATIK CHAQIRILADI.
```

### "Rerun Validation" — QAYTA TEKSHIRISH ZARURATI

```
Agar Controller ICHIDA, DTO'ning BIROR PROPERTYSI QO'LDA
O'ZGARTIRILSA (masalan default qiymat BERILSA) — ASL ModelState
NATIJASI ENDI "ESKIRGAN" bo'lishi mumkin. Bunday holatlarda —
`TryValidateModel(dto)` metodi orqali — VALIDATSIYANI QO'LDA
QAYTA ISHGA TUSHIRISH ("rerun") mumkin.
```

## 5. Code (Amaliy kod)

```csharp
public class CreateEmployeeDto
{
    [Required(ErrorMessage = "Ism majburiy")]
    [StringLength(100, MinimumLength = 2)]
    public string FullName { get; set; } = null!;

    [Range(18, 65, ErrorMessage = "Yosh 18-65 oralig'ida bo'lishi kerak")]
    public int Age { get; set; }

    [EmailAddress]
    public string Email { get; set; } = null!;

    [RegularExpression(@"^\+998\d{9}$", ErrorMessage = "Telefon formati: +998XXXXXXXXX")]
    public string? Phone { get; set; }
}
```

```csharp
[ApiController] // ✅ ModelState.IsValid AVTOMATIK tekshiriladi
[Route("api/[controller]")]
public class EmployeesController : ControllerBase
{
    [HttpPost]
    public IActionResult Create(CreateEmployeeDto dto)
    {
        // BU YERGA FAQAT VALIDATSIYADAN O'TGAN so'rov YETIB KELADI
        return Ok();
    }
}
```

```csharp
// [ApiController] BO'LMAGAN holatda — QO'LDA TEKSHIRISH
[HttpPost]
public IActionResult CreateManual(CreateEmployeeDto dto)
{
    if (!ModelState.IsValid)
        return BadRequest(ModelState); // XATOLAR — Dictionary<string, string[]> FORMATIDA

    return Ok();
}
```

```csharp
// IValidatableObject — BIR NECHTA MAYDON BIRGALIKDA
public class DateRangeDto : IValidatableObject
{
    public DateTime StartDate { get; set; }
    public DateTime EndDate { get; set; }

    public IEnumerable<ValidationResult> Validate(ValidationContext validationContext)
    {
        if (EndDate < StartDate)
            yield return new ValidationResult("Tugash sanasi boshlanish sanasidan OLDIN bo'lishi mumkin emas",
                new[] { nameof(EndDate) });
    }
}
```

```csharp
// TryValidateModel — QO'LDA QAYTA TEKSHIRISH ("rerun")
[HttpPost]
public IActionResult Create(CreateEmployeeDto dto)
{
    if (string.IsNullOrEmpty(dto.Phone))
        dto.Phone = "+998000000000"; // DEFAULT qiymat BERILDI

    ModelState.Clear();          // ESKI natijani TOZALASH
    if (!TryValidateModel(dto))  // QAYTA TEKSHIRISH
        return BadRequest(ModelState);

    return Ok();
}
```

## 6. Keng tarqalgan xatolar / noto'g'ri tushunchalar

```
❌ "[ApiController] BO'LMASA HAM, ModelState AVTOMATIK TEKSHIRILADI"
   — NOTO'G'RI! [ApiController]SIZ — `if (!ModelState.IsValid)`
   HAR ACTION'DA QO'LDA YOZILISHI KERAK.

❌ "ModelState — FAQAT [FromBody] uchun ISHLAYDI" — NOTO'G'RI!
   [FromQuery], [FromRoute], [FromForm] — BARCHASI ModelState
   orqali TEKSHIRILADI.

❌ "ModelState.IsValid == false bo'lsa, Action METOD BAJARILMAYDI"
   — Bu FAQAT [ApiController] BO'LGANDA TO'G'RI! Oddiy Controller'da
   (MVC, [ApiController]SIZ) — Action METOD BAJARILADI, LEKIN
   ModelState.IsValid — FALSE bo'lib QOLADI, TEKSHIRISH QO'LDA
   AMALGA OSHIRILISHI KERAK.

❌ "Client-side validatsiya — Server-side'ni ALMASHTIRA OLADI" —
   HECH QACHON! Client-side — FAQAT UX uchun, XAVFSIZLIK uchun
   EMAS (docs/Junior-A/20-input-validation'ga qarang).
```

## 7. Exam (Interview savollari)

**1. `[ApiController]` atributi Model Validation'ga QANDAY TA'SIR
QILADI?**
`[ApiController]` — AVTOMATIK ravishda `ModelState.IsValid`ni
TEKSHIRADI, AGAR FALSE bo'lsa — Action metod CHAQIRILMASDAN,
400 Bad Request + ProblemDetails (RFC 7807) FORMATIDA javob
QAYTARADI.

**2. `[Required]` va `IValidatableObject` orasidagi FARQ nima?**
`[Required]` (va boshqa `ValidationAttribute`lar) — FAQAT BITTA
PROPERTY'NI, MUSTAQIL TEKSHIRADI. `IValidatableObject` — BIR
NECHTA PROPERTY'NI BIRGALIKDA (masalan StartDate < EndDate)
TEKSHIRISH imkonini beradi.

**3. Custom `ValidationAttribute` yaratish uchun QAYSI klassdan
MEROS OLINADI, va QAYSI METOD OVERRIDE QILINADI?**
`System.ComponentModel.DataAnnotations.ValidationAttribute`dan
meros OLINADI, `IsValid(object? value, ValidationContext context)`
METODI OVERRIDE QILINADI.

**4. "Rerun Validation" (`TryValidateModel`) qachon KERAK BO'LADI?**
Controller ICHIDA DTO'ning BIROR PROPERTYSI QO'LDA O'ZGARTIRILGANDA
(masalan default qiymat BERILGANDA) — ASL Model Binding
paytidagi validatsiya NATIJASI ESKIRGAN BO'LADI. `TryValidateModel`
— MODEL'NI QAYTA, JORIY HOLATIDA TEKSHIRISH imkonini beradi.

**5. Model Validation qaysi PIPELINE bosqichida (Model Binding'dan
OLDIN yoki KEYIN) sodir bo'ladi?**
Model Binding'DAN KEYIN — AVVAL HTTP so'rov (JSON/query/route) —
C# DTO OBYEKTIGA "MOSLASHTIRILADI" (Model Binding), FAQAT SHUNDAN
KEYIN — DTO'NING PROPERTYLARI ustida VALIDATION ATTRIBUTE'LAR
TEKSHIRILADI.
