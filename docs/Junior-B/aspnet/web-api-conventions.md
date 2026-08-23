# Web API Conventions — Junior B

## 1. What (Nima?)

**Web API Conventions** — REST API dizaynida rioya qilinadigan
**yozilmagan (yoki rasmiy) qoidalar to'plami**: URL nomlash, HTTP
verb tanlash, status kod ishlatish, javob strukturasi — bularning
BARCHASI **BASHORAT QILINADIGAN, BIR XIL** bo'lishi uchun.
ASP.NET Core'da `ApiConventionMethod`/`ApiConventionType`
ATRIBUTLARI — bu QOIDALARNI **KOD DARAJASIDA** DEKLARATIV
tarzda BELGILASH imkonini beradi.

## 2. Real hayot analogiyasi

**API Conventions — YO'L HARAKATI QOIDALARI.** Har mamlakatda —
"QIZIL — TO'XTA, YASHIL — YUR" degan QOIDA **BIR XIL** (yoki
KONSISTENT). Agar HAR SHAHAR (HAR API) O'ZINING QOIDASINI
O'YLAB TOPSA — HAYDOVCHI (API iste'molchisi) HAR SAFAR YANGI
QOIDA O'RGANISHGA MAJBUR bo'lardi. Konvensiyalar — bu XAOSNI
OLDINI OLADI: `GET /employees` — HAR DOIM "RO'YXAT OLISH"NI
ANGLATADI, `DELETE /employees/5` — HAR DOIM "5-XODIMNI O'CHIRISH".

## 3. Why (Nega kerak?)

Konvensiyalarsiz — HAR DASTURCHI, HAR API'NI **O'ZICHA** loyihalaydi
(`getEmployee?id=5` vs `employees/5` vs `employee/find/5`) — bu,
API'DAN FOYDALANUVCHI (frontend, mobil, boshqa servis) uchun
**BASHORAT QILIB BO'LMAYDIGAN**, O'RGANISH VAQTI KO'PROQ SARFLANADIGAN
tajriba BERADI. Konvensiyalar — **KOGNITIV YUKNI KAMAYTIRADI**:
BIR API'NI O'RGANGAN DASTURCHI — BOSHQA, XUDDI SHU KONVENSIYAGA
RIOYA QILGAN API'NI HAM TEZ TUSHUNADI.

## 4. Internals (Ichki mexanizm)

### Resurs nomlash — KO'PLIK, OT (NOUN), FE'L EMAS

```
✅ GET /api/employees          — RO'YXAT
✅ GET /api/employees/5        — BITTA RESURS
✅ POST /api/employees         — YARATISH
✅ PUT /api/employees/5        — TO'LIQ YANGILASH
✅ DELETE /api/employees/5     — O'CHIRISH

❌ GET /api/getEmployees       — FE'L URL'da — REST KONVENSIYASI BUZILGAN
❌ POST /api/createEmployee    — HTTP VERB (POST) ALLAQACHON "YARATISH"NI
                                  ANGLATADI, URL'da TAKRORLASH SHART EMAS
```

### Nested resurslar — MUNOSABATNI KO'RSATISH

```
GET /api/departments/3/employees  — 3-BO'LIMNING XODIMLARI
POST /api/departments/3/employees — 3-BO'LIMGA YANGI XODIM QO'SHISH

⚠️ 2-3 DARAJADAN CHUQURROQ NESTING — O'QILISHINI QIYINLASHTIRADI:
❌ /api/departments/3/employees/5/documents/10/comments/2
✅ /api/comments/2 (agar comment — MUSTAQIL RESURS bo'lsa)
```

### Status kod KONVENSIYASI

```
200 OK              — GET, PUT muvaffaqiyatli
201 Created          — POST muvaffaqiyatli (+ Location header)
204 No Content        — DELETE muvaffaqiyatli (javob TANASI YO'Q)
400 Bad Request        — Validatsiya XATOSI
404 Not Found           — Resurs TOPILMADI
409 Conflict             — Holat ZIDDIYATI (masalan UNIQUE buzilishi)
```

### `[ApiConventionMethod]` — ASP.NET Core'ning DEKLARATIV mexanizmi

```csharp
[ApiConventionMethod(typeof(DefaultApiConventions), nameof(DefaultApiConventions.Get))]
[HttpGet("{id}")]
public IActionResult GetById(int id) { /* ... */ }
```

```
DefaultApiConventions — ASP.NET Core'NING BUILT-IN "STANDART"
KONVENSIYASI — HAR HTTP VERB UCHUN QAYSI STATUS KODLAR QAYTARILISHI
KUTILISHINI BELGILAYDI (masalan Get() — 200 va 404 KUTADI). Bu —
Swagger/OpenAPI SCHEMA'da TO'G'RI STATUS KODLARNI KO'RSATISH
uchun ISHLATILADI, XATTI-HARAKATNI O'ZI o'ZGARTIRMAYDI (FAQAT
METADATA).

[ApiController] atributi bo'lgan Controller'lar — DEFAULT holda
DefaultApiConventions'ni AVTOMATIK QO'LLAYDI.
```

### Pagination KONVENSIYASI

```
GET /api/employees?page=2&pageSize=20

Response:
{
  "data": [...],
  "page": 2,
  "pageSize": 20,
  "totalCount": 145,
  "totalPages": 8
}
```

### Versioning KONVENSIYASI

```
Batafsil: docs/Middle-D/18-api-versioning

/api/v1/employees — URL orqali VERSIYALASH (ENG KENG TARQALGAN)
```

## 5. Code (Amaliy kod)

```csharp
[ApiController]
[Route("api/[controller]")] // KO'PLIK, RESURS NOMI (Employees → employees)
public class EmployeesController : ControllerBase
{
    [HttpGet]
    public async Task<ActionResult<PagedResult<EmployeeDto>>> GetAll(
        [FromQuery] int page = 1, [FromQuery] int pageSize = 20)
    {
        var (items, totalCount) = await _service.GetPagedAsync(page, pageSize);
        return Ok(new PagedResult<EmployeeDto>(items, page, pageSize, totalCount));
    }

    [HttpGet("{id:int}")]
    public async Task<ActionResult<EmployeeDto>> GetById(int id)
    {
        var employee = await _service.GetByIdAsync(id);
        return employee is null ? NotFound() : Ok(employee);
    }

    [HttpPost]
    public async Task<ActionResult<EmployeeDto>> Create(CreateEmployeeDto dto)
    {
        var created = await _service.CreateAsync(dto);
        // 201 + Location header — KONVENSIYAGA MOS
        return CreatedAtAction(nameof(GetById), new { id = created.Id }, created);
    }

    [HttpDelete("{id:int}")]
    public async Task<IActionResult> Delete(int id)
    {
        await _service.DeleteAsync(id);
        return NoContent(); // 204 — javob TANASI YO'Q
    }
}

public record PagedResult<T>(List<T> Data, int Page, int PageSize, int TotalCount)
{
    public int TotalPages => (int)Math.Ceiling(TotalCount / (double)PageSize);
}
```

```csharp
// Custom API Convention YARATISH
public static class ErpApiConventions
{
    [ApiConventionNameMatch(ApiConventionNameMatchBehavior.Prefix)]
    public static void Get(
        [ApiConventionNameMatch(ApiConventionNameMatchBehavior.Suffix)] int id) { }
}

[ApiConventionType(typeof(ErpApiConventions))] // BUTUN CONTROLLER'GA QO'LLASH
public class EmployeesController : ControllerBase { }
```

## 6. Keng tarqalgan xatolar / noto'g'ri tushunchalar

```
❌ "URL'da FE'L (getEmployees, createEmployee) ISHLATISH — ODATIY"
   — REST KONVENSIYASINI BUZADI. HTTP VERB (GET, POST) ALLAQACHON
   "AMAL"NI IFODALAYDI — URL — FAQAT RESURS (OT) BO'LISHI KERAK.

❌ "DELETE — HAR DOIM 200 QAYTARISHI KERAK" — KONVENSIYA — 204
   No Content (javob TANASI YO'Q), CHUNKI RESURS ENDI MAVJUD
   EMAS, QAYTARADIGAN NARSA YO'Q.

❌ "GET so'rovda BODY ishlatish MUMKIN" — HTTP SPETSIFIKATSIYASI
   BO'YICHA — TEXNIK JIHATDAN RUXSAT ETILGAN, LEKIN KO'P
   KUTUBXONA/PROXY — GET BODY'NI QO'LLAB-QUVVATLAMAYDI —
   QUERY PARAMETRLARI ISHLATILISHI KERAK.

❌ "BARCHA XATOLAR — 400 BILAN QAYTARILISHI MUMKIN" — NOTO'G'RI!
   404 (topilmadi), 409 (ziddiyat), 422 (semantik xato) — HAR
   BIRI O'ZINING ANIQ MA'NOSIGA EGA — 400'NI "HAMMA XATO UCHUN"
   ISHLATISH — API'NI TUSHUNARSIZ QILADI.

❌ "[ApiConventionMethod] XATTI-HARAKATNI O'ZGARTIRADI" — YO'Q!
   Bu — FAQAT Swagger/OpenAPI METADATASI UCHUN, RUNTIME
   XATTI-HARAKATGA HECH QANDAY TA'SIR QILMAYDI.
```

## 7. Exam (Interview savollari)

**1. Nima uchun REST API URL'larida FE'L (masalan `/getEmployees`)
ISHLATISH TAVSIYA ETILMAYDI?**
HTTP verb (GET, POST, DELETE) ALLAQACHON AMALNI (fe'lni)
IFODALAYDI. URL — RESURSNI (ot, ko'plikda) IFODALASHI KERAK.
`GET /employees` — "xodimlarni OLISH" DEGANI ALLAQACHON ANIQ,
`/getEmployees` — TAKRORLANISH.

**2. `POST` va `PUT` uchun QAYSI STATUS KODLAR KONVENSIYA
BO'YICHA QAYTARILADI?**
`POST` (yaratish) — 201 Created (+ Location header). `PUT`
(to'liq yangilash) — 200 OK (agar javob TANASI qaytarilsa) yoki
204 No Content (agar QAYTARILMASA).

**3. `[ApiConventionMethod]` atributi NIMA VAZIFANI BAJARADI?**
BU — Swagger/OpenAPI hujjatlashtirish uchun, ACTION METOD QAYSI
STATUS KODLARNI QAYTARISHI MUMKINLIGINI DEKLARATIV tarzda
BELGILAYDI. Bu — RUNTIME xatti-harakatga TA'SIR QILMAYDI, FAQAT
API HUJJATI (schema) TO'G'RI GENERATSIYA QILINISHI uchun.

**4. Nested resurslarni (masalan `/departments/3/employees`)
QACHON ISHLATISH VA QACHON QOCHISH KERAK?**
Munosabatni (bo'lim → xodim) ANIQ KO'RSATISH kerak bo'lganda —
FOYDALI. LEKIN 2-3 DARAJADAN CHUQURROQ NESTING — URL'ni
TUSHUNARSIZ QILADI — MUSTAQIL resurslar (masalan comment) —
O'ZINING ALOHIDA, TOP-LEVEL endpoint'iga EGA BO'LISHI TAVSIYA
ETILADI.

**5. Pagination'da `data`, `page`, `pageSize`, `totalCount`
konvensiyasi NIMA UCHUN MUHIM?**
API iste'molchisi (frontend) — QANCHA SAHIFA MAVJUDLIGINI,
JORIY QAYERDA EKANINI BILISHI KERAK — KONSISTENT STRUKTURA
(BARCHA endpoint'larda BIR XIL) — FRONTEND KODINI QAYTA
ISHLATILADIGAN (reusable) QILADI.
