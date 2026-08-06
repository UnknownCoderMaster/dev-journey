# Input Validation va Sanitization — Junior A

## 1. Nima? (Ta'rif)

**Input Validation** — foydalanuvchidan kelgan ma'lumotning
**to'g'ri format/qiymatga** ega ekanligini tekshirish. **Sanitization**
— zararli (masalan, XSS) ma'lumotni **zararsizlantirish/tozalash**.

## 2. Nima uchun kerak?

Tekshirilmagan kirish — **SQL Injection, XSS, biznes mantiq
buzilishi** kabi jiddiy muammolarga olib keladi. Validation —
"ishonchsiz" tashqi ma'lumotni **ishonchli** qilishning birinchi
himoya chizig'i.

## 3. Ichida nima sodir bo'ladi? (Mexanizm)

### 3.1 Data Annotations

```csharp
public class CreateEmployeeDto
{
    [Required(ErrorMessage = "Ism majburiy")]
    [MaxLength(100)]
    public string FullName { get; set; } = null!;

    [Range(18, 65, ErrorMessage = "Yosh 18-65 oralig'ida bo'lishi kerak")]
    public int Age { get; set; }

    [RegularExpression(@"^\+998\d{9}$")]
    public string? Phone { get; set; }

    [EmailAddress]
    public string Email { get; set; } = null!;

    [Url]
    public string? Website { get; set; }
}
```

### 3.2 ModelState — `[ApiController]` avtomatik

```csharp
[ApiController] // ✅ AVTOMATIK ModelState.IsValid TEKSHIRUVI (400 qaytaradi agar NOTO'G'RI bo'lsa)
public class EmployeesController : ControllerBase
{
    [HttpPost]
    public IActionResult Create(CreateEmployeeDto dto)
    {
        // Bu YERGA faqat VALIDATSIYADAN O'TGAN so'rov YETIB KELADI
        return Ok();
    }
}
```

### 3.3 FluentValidation — kuchli, kengaytiriladigan

```bash
dotnet add package FluentValidation.AspNetCore
```

```csharp
public class CreateEmployeeValidator : AbstractValidator<CreateEmployeeDto>
{
    public CreateEmployeeValidator()
    {
        RuleFor(x => x.FullName).NotEmpty().MaximumLength(100);
        RuleFor(x => x.Age).InclusiveBetween(18, 65);
        RuleFor(x => x.Email).EmailAddress();

        RuleFor(x => x.Phone)
            .Matches(@"^\+998\d{9}$")
            .When(x => !string.IsNullOrEmpty(x.Phone)); // FAQAT qiymat BO'LSA tekshiriladi

        RuleFor(x => x.Salary)
            .Must(salary => salary > 0)
            .WithMessage("Maosh musbat bo'lishi kerak");
    }
}
```

```csharp
// DI ga qo'shish
builder.Services.AddValidatorsFromAssemblyContaining<CreateEmployeeValidator>();
builder.Services.AddFluentValidationAutoValidation(); // Avtomatik ModelState'ga INTEGRATSIYA
```

```
FluentValidation — Data Annotations'dan AFZAL, chunki:
  ✅ MURAKKAB shartlar (Must, When, DependentRules)
  ✅ VALIDATSIYA logikasi DTO'dan AJRATILGAN (klass "toza" qoladi)
  ✅ TEST QILISH oson (Validator — ALOHIDA klass)
```

### 3.4 Sanitization — HTML encode

```csharp
using System.Text.Encodings.Web;

string userInput = "<script>alert('XSS')</script>";
string safe = HtmlEncoder.Default.Encode(userInput);
// → "&lt;script&gt;alert('XSS')&lt;/script&gt;" — BRAUZER buni SKRIPT sifatida BAJARMAYDI
```

```
XSS (Cross-Site Scripting) — hujumchi FOYDALANUVCHI kiritgan
matnga JAVASCRIPT kodini "yashirsa", va bu matn BOSHQA foydalanuvchi
sahifasida TO'G'RIDAN (encode QILINMASDAN) ko'rsatilsa — BOSHQA
foydalanuvchi BRAUZERIDA HUJUMCHI kodi BAJARILADI!

HTML Encode — <, >, ', " kabi belgilarni "MAXSUS entity"larga
(&lt;, &gt; va h.k.) AYLANTIRIB, brauzerga ularni KOD emas, ODDIY
MATN sifatida KO'RSATISHNI buyuradi.
```

### 3.5 Client-side vs Server-side validation

```
Client-side (JavaScript) — FOYDALANUVCHI TAJRIBASI uchun (DARHOL
                             xato ko'rsatish, so'rov YUBORILMASDAN)
Server-side              — XAVFSIZLIK uchun MAJBURIY (client-side
                             OSON CHETLAB O'TILADI — masalan curl
                             orqali to'g'ridan so'rov yuborish)

⚠️ Faqat client-side validatsiya — HECH QANDAY XAVFSIZLIK bermaydi!
   Server HAR DOIM, MUSTAQIL RAVISHDA tekshirishi SHART.
```

### 3.6 Whitelist vs Blacklist

```
Blacklist — "MANA BU belgilar TAQIQLANGAN" (masalan <script>)
  ❌ XAVFLI — hujumchi YANGI, RO'YXATDA YO'Q usul TOPISHI mumkin
     (masalan <ScRiPt>, encoding trikleri)

Whitelist — "FAQAT MANA BU belgilar RUXSAT ETILGAN" (masalan
             faqat harflar, raqamlar)
  ✅ XAVFSIZROQ — HAR NARSA DEFAULT holda TAQIQLANGAN, FAQAT
     ANIQ RUXSAT ETILGANLAR o'tadi
```

### 3.7 File upload validation

```csharp
public IActionResult UploadFile(IFormFile file)
{
    var allowedExtensions = new[] { ".jpg", ".png", ".pdf" };
    var extension = Path.GetExtension(file.FileName).ToLowerInvariant();

    if (!allowedExtensions.Contains(extension))
        return BadRequest("Ruxsat etilmagan fayl turi");

    if (file.Length > 5 * 1024 * 1024) // 5MB
        return BadRequest("Fayl hajmi juda katta");

    // ⚠️ Extension'ga ISHONMANG — HAQIQIY Content-Type/magic bytes'ni TEKSHIRING
    using var stream = file.OpenReadStream();
    var buffer = new byte[8];
    stream.Read(buffer, 0, 8);
    if (!IsValidImageSignature(buffer)) // Fayl SARLAVHASI (magic number) TEKSHIRUVI
        return BadRequest("Fayl mazmuni ruxsat etilmagan turga mos emas");

    return Ok();
}
```

```
⚠️ Fayl KENGAYTMASI (extension) — OSON "SOXTALASHTIRILISHI"
   mumkin (masalan zararli.exe → zararli.jpg deb NOMLANISHI). Haqiqiy
   xavfsizlik uchun — fayl MAGIC BYTES (sarlavha imzosi) TEKSHIRILISHI
   kerak.
```

## 4. Kod — real ERP misolida validatsiya

```csharp
public class CreateEmployeeValidator : AbstractValidator<CreateEmployeeDto>
{
    private readonly AppDbContext _context;

    public CreateEmployeeValidator(AppDbContext context)
    {
        _context = context;

        RuleFor(x => x.FullName).NotEmpty().MaximumLength(100);
        RuleFor(x => x.Email)
            .EmailAddress()
            .MustAsync(async (email, ct) => !await _context.Employees.AnyAsync(e => e.Email == email, ct))
            .WithMessage("Bu email allaqachon ro'yxatdan o'tgan");
        RuleFor(x => x.DepartmentId)
            .MustAsync(async (id, ct) => await _context.Departments.AnyAsync(d => d.Id == id, ct))
            .WithMessage("Bo'lim mavjud emas");
    }
}
```

## 5. Qachon ishlatish kerak?

| Vaziyat | Yechim |
|---|---|
| Oddiy, statik qoidalar | Data Annotations |
| Murakkab, DB'ga bog'liq, shartli qoidalar | FluentValidation |
| Foydalanuvchi kiritgan matn HTML'da ko'rsatiladi | HTML Encode |
| Fayl yuklash | Extension + Content-Type + Magic Bytes tekshiruvi |

## 6. Muhim nuqtalar

- Server-side validatsiya — **HECH QACHON o'tkazib yuborilmasin**,
  hatto client-side validatsiya BO'LSA HAM.
- Whitelist yondashuvi — Blacklist'dan **doim xavfsizroq**.
- SQL Injection'ga qarshi — Input Validation **QO'SHIMCHA** himoya,
  ASOSIY himoya — **parametrlangan so'rovlar** (docs/Middle-D/51-sql-injection-owasp'da).

## 7. Imtihon savollari

1. Data Annotations va FluentValidation orasidagi asosiy farq
   nima?
2. HTML Encode nima muammoni (XSS) hal qiladi?
3. Client-side va Server-side validatsiya nima uchun IKKALASI HAM
   kerak?
4. Whitelist va Blacklist yondashuvlari orasidagi xavfsizlik farqi
   nima?
5. Fayl yuklashda faqat extension'ni tekshirish nima uchun
   yetarli emas?
6. `[ApiController]` atributi ModelState tekshiruvini qanday
   avtomatlashtiradi?
