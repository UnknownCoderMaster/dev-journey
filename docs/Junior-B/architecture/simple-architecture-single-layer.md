# Simple Architecture (1 ta Layer) — Junior B

## 1. What (Nima?)

**Simple (Single-Layer) Architecture** — ilovaning **barcha
mantig'i** (UI, biznes qoida, ma'lumotlar bazasi bilan aloqa) —
**BITTA QATLAMDA**, ko'pincha bitta yoki bir necha katta klassda
JAMLANGAN arxitektura. Qatlamlarga (Presentation/Business/Data)
**ATAYLAB AJRATILMAGAN**.

## 2. Real hayot analogiyasi

**Simple Architecture — BITTA XONALI KVARTIRA.** Yotoq, oshxona,
mehmonxona — HAMMASI **BITTA XONADA**. Kichik oilalar (kichik
loyihalar) uchun — bu QULAY, TEZ (arzon, tez qurish MUMKIN). LEKIN
OILA KATTALASHSA (loyiha O'SSA) — HAMMA NARSA ARALASHIB KETADI:
OSHXONA HIDI YOTOQXONAGA O'TADI (UI kodi DB kodi bilan aralashadi),
BITTA ODAM UYQUDA BOSHQASI OVQAT TAYYORLASHI QIYINLASHADI (bir
o'zgarish — boshqa qismni buzadi).

## 3. Why (Nega kerak?)

Har bir loyihaga **N-Layer/Clean Architecture** kabi murakkab
tuzilma qo'llash — KICHIK skript, PROTOTIP, YOKI BIR MARTALIK
UTILITY dastur uchun **ORTIQCHA MURAKKABLIK** (over-engineering).
Simple Architecture — TEZ YOZISH, TEZ TUSHUNISH imkonini beradi,
LEKIN loyiha O'SGANDA — **texnik qarz** (technical debt) TEZ
TO'PLANADI.

**Amaliyotda qachon ishlatiladi:** Console utility, kichik CLI
script, POC (Proof of Concept), yoki HACKATHON loyihasi — QATLAMLASH
uchun VAQT SARFLASH — MAQSADGA MOS EMAS.

## 4. Internals (Ichki mexanizm)

### Odatiy struktura

```
SimpleApp/
├── Program.cs          — HAMMASI SHU YERDA: HTTP handling,
│                          biznes mantiq, DB so'rovi — BIR JOYDA
├── Models/
│   └── Employee.cs
└── appsettings.json
```

```csharp
// HAMMA MANTIQ — BITTA KLASSDA (yoki HATTO Program.cs'da)
public class EmployeeController : ControllerBase
{
    private readonly NpgsqlConnection _connection;

    [HttpPost]
    public IActionResult Create(CreateEmployeeDto dto)
    {
        // VALIDATSIYA — SHU YERDA
        if (string.IsNullOrEmpty(dto.FullName)) return BadRequest();

        // BIZNES QOIDA — SHU YERDA
        var bonus = dto.Salary * 0.1m;

        // DB SO'ROVI — TO'G'RIDAN, SHU YERDA (ADO.NET)
        using var command = new NpgsqlCommand(
            "INSERT INTO employees (full_name, salary) VALUES (@name, @salary)", _connection);
        command.Parameters.AddWithValue("@name", dto.FullName);
        command.Parameters.AddWithValue("@salary", dto.Salary);
        command.ExecuteNonQuery();

        return Ok();
    }
}
```

### Nima uchun "SKALALANMAYDI" — MEXANIZM

```
Bitta klassda HAMMA MANTIQ bo'lganda:
  - TEST QILISH QIYIN — DB'siz UNIT TEST YOZIB BO'LMAYDI (HTTP,
    BIZNES QOIDA, DB — BIR-BIRIDAN AJRATIB BO'LMAYDI)
  - O'ZGARISH XAVFLI — BIR QATOR O'ZGARTIRISH, BOSHQA QISMGA
    "YASHIRIN" TA'SIR QILISHI mumkin (COUPLING YUQORI)
  - KOD TAKRORLANADI — Bir XIL DB so'rov MANTIG'I bir NECHTA
    Controller'da TAKRORLANISHI mumkin
```

### Qachon bu — TO'G'RI TANLOV (ANTI-PATTERN EMAS!)

```
YAGONA-FAYLLI script, KICHIK Azure Function, YOKI "throwaway"
(bir martalik) migratsion skript uchun — SIMPLE ARCHITECTURE —
TO'G'RI TANLOV. Muammo — BU YONDASHUVNI **KATTA, UZOQ MUDDATLI**
loyihaga QO'LLASH (masalan ERP tizimi).
```

## 5. Code (Amaliy kod)

```csharp
// TO'LIQ Minimal API — BIR FAYLDA (Program.cs), "Simple Architecture" ning
// ZAMONAVIY, LEKIN QASDDAN CHEKLANGAN ko'rinishi (kichik loyihalar uchun MOS)
var builder = WebApplication.CreateBuilder(args);
builder.Services.AddSingleton<List<Employee>>(); // "DB" o'rniga XOTIRA

var app = builder.Build();

app.MapGet("/employees", (List<Employee> store) => store);

app.MapPost("/employees", (CreateEmployeeDto dto, List<Employee> store) =>
{
    if (string.IsNullOrEmpty(dto.FullName))
        return Results.BadRequest("Ism majburiy");

    var employee = new Employee { Id = store.Count + 1, FullName = dto.FullName, Salary = dto.Salary };
    store.Add(employee);
    return Results.Created($"/employees/{employee.Id}", employee);
});

app.Run();

public record CreateEmployeeDto(string FullName, decimal Salary);
public class Employee { public int Id { get; set; } public string FullName { get; set; } = null!; public decimal Salary { get; set; } }
```

```
Bu — 30 QATORDA ISHLAYDIGAN TO'LIQ API — KICHIK PROTOTIP UCHUN
IDEAL, LEKIN ERP tizimi UCHUN — BU YONDASHUV TEZDA "GOD FILE"GA
AYLANADI.
```

## 6. Keng tarqalgan xatolar / noto'g'ri tushunchalar

```
❌ "Simple Architecture — HAR DOIM YOMON" — NOTO'G'RI! Kichik,
   qisqa muddatli loyihalar uchun — BU ENG SAMARALI YECHIM
   (YAGNI — "You Aren't Gonna Need It").

❌ "Loyiha kichik boshlangan, DEMAK doim SODDA QOLADI" — XAVFLI
   TAXMIN! Ko'p PROTOTIP — "VAQTINCHA" DEB BOSHLANIB, PRODUCTION'DA
   YILLAR DAVOMIDA ISHLAYDI — QATLAMLASHNI "KEYINROQ" QILISH —
   KO'PINCHA HECH QACHON QILINMAYDI.

❌ "Bir fayl — bir NECHTA MAS'ULIYAT bo'lsa HAM, MUAMMO EMAS,
   chunki KICHIK loyiha" — TEST QILISH VA XATO TOPISH — HALI
   HAM QIYINLASHADI, HATTO KICHIK loyihada HAM.

❌ "Simple Architecture — Clean Architecture'dan FARQLI, U
   'YOMON' amaliyot" — Bu — TO'G'RI/NOTO'G'RI EMAS, TRADEOFF:
   TEZLIK VA SODDALIK vs KENGAYTIRILUVCHANLIK VA TEST QILINISH.
```

## 7. Exam (Interview savollari)

**1. Simple Architecture qachon TO'G'RI TANLOV hisoblanadi?**
Kichik, QISQA MUDDATLI, YOKI PROTOTIP loyihalarda — QATLAMLASH
uchun QO'SHIMCHA MURAKKABLIK KIRITISH — VAQT ISROFI (over-engineering)
bo'ladi. Bunday holatlarda Simple Architecture — TEZ, TUSHUNARLI
YECHIM.

**2. Simple Architecture'ning ENG KATTA KAMCHILIGI nima?**
Test qilinishi QIYIN (HTTP, biznes MANTIQ, DB — ARALASHGAN),
O'ZGARISHLAR "YASHIRIN" TA'SIRLARGA (side effects) OLIB KELISHI
MUMKIN, VA LOYIHA KATTALASHGANDA — TEXNIK QARZ TEZ TO'PLANADI.

**3. Nima uchun "vaqtinchalik" deb boshlangan Simple Architecture
loyiha — XAVFLI bo'lishi mumkin?**
Ko'p loyihalar "VAQTINCHA PROTOTIP" sifatida BOSHLANIB, KEYINCHALIK
PRODUCTION'DA UZOQ MUDDAT ISHLAYDI — LEKIN "QAYTA QURISH"
(REFACTORING) HECH QACHON REJALASHTIRILMAGAN VAQT/BUDJETGA EGA
BO'LMAYDI, natijada MURAKKAB, TEST QILIB BO'LMAYDIGAN kod
UZOQ MUDDAT QOLIB KETADI.

**4. Minimal API (ASP.NET Core) Simple Architecture'ning ZAMONAVIY
KO'RINISHI DEB HISOBLANISHI MUMKINMI?**
Ha, agar HAMMA MANTIQ (validatsiya, biznes qoida, DB) BITTA
`Program.cs` faylida, Controller/Handler'larga AJRATILMASDAN
YOZILSA — bu, ZAMONAVIY SINTAKSISDA, XUDDI Simple Architecture'ning
O'ZI. Katta loyihalarda Minimal API'ni HAM QATLAMLARGA (Endpoint
groups, Handler klasslar) AJRATISH MUMKIN.

**5. Simple Architecture'dan N-Layer'ga O'TISH QACHON KERAK BO'LADI?**
Loyiha KATTALASHGANDA (KO'P ENDPOINT, KO'P BIZNES QOIDA), TEST
QOPLAMASI (test coverage) KERAK BO'LGANDA, YOKI BIR NECHTA
DASTURCHI PARALLEL ISHLASHI KERAK BO'LGANDA — MAS'ULIYATLARNI
AJRATISH (SEPARATION OF CONCERNS) ZARURATI TUG'ILADI.
