# HTTP Request, Response, Headers — Junior A

## 1. Nima? (Ta'rif)

**HTTP Request** — client'dan serverga yuboriladigan so'rov,
**Request Line + Headers + (ixtiyoriy) Body**dan iborat. **HTTP
Response** — serverdan client'ga qaytariladigan javob, **Status
Line + Headers + Body**dan iborat.

## 2. Nima uchun kerak?

HTTP — **standartlashtirilgan** formatga ega bo'lgani uchun —
istalgan client (brauzer, mobil ilova, boshqa server) va istalgan
server — **bir xil "til"da** gaplasha oladi.

## 3. Ichida nima sodir bo'ladi? (Mexanizm)

### 3.1 HTTP Request tuzilmasi

```
POST /api/employees HTTP/1.1          ← Request Line: Method, URL, Version
Host: api.example.com                  ← Header
Content-Type: application/json         ← Header
Authorization: Bearer eyJhbGc...       ← Header
Content-Length: 45                     ← Header

{"fullName": "Orzibek", "age": 25}     ← Body (ixtiyoriy)
```

### 3.2 HTTP Response tuzilmasi

```
HTTP/1.1 201 Created                   ← Status Line: Version, Status Code, Reason
Content-Type: application/json         ← Header
Location: /api/employees/42            ← Header

{"id": 42, "fullName": "Orzibek"}      ← Body
```

### 3.3 Muhim Request Headers

```
Authorization    — Bearer <token> (JWT), Basic <base64>
Content-Type     — application/json, multipart/form-data, application/xml
Accept           — Client QANDAY format KUTAYOTGANI (application/json)
Content-Length   — Body HAJMI (bayt)
User-Agent       — Client identifikatsiyasi ("Mozilla/5.0 ...")
X-Request-Id     — Distributed tracing uchun NOYOB ID (mikroservislarda so'rovni KUZATISH)
Cache-Control    — Keshlash direktivalari (no-cache, max-age)
Cookie           — Session identifikatori
```

### 3.4 Muhim Response Headers

```
Content-Type              — Javob FORMATI (application/json)
Location                  — 201 Created'da, YANGI resurs URL'i
WWW-Authenticate          — 401 da, QAYSI auth SCHEME kerakligi (Bearer, Basic)
Set-Cookie                — Server → Client, COOKIE o'rnatish
ETag                       — Resurs VERSIYASI (caching/concurrency uchun)
Access-Control-Allow-Origin — CORS — QAYSI origin'ga RUXSAT etilgan
```

### 3.5 Content Negotiation — Accept header asosida

```
Client: Accept: application/json     → Server JSON qaytaradi
Client: Accept: application/xml      → Server XML qaytaradi (agar qo'llab-quvvatlasa)

Server — Accept header'ni TEKSHIRIB, MOS formatter'ni TANLAYDI —
agar HECH BIRI mos kelmasa — 406 Not Acceptable qaytarilishi mumkin.
```

### 3.6 ASP.NET Core'da header o'qish va yozish

```csharp
[HttpPost]
public IActionResult Create([FromBody] CreateEmployeeDto dto)
{
    var userAgent = Request.Headers.UserAgent.ToString();
    var authHeader = Request.Headers.Authorization.ToString();
    var requestId = Request.Headers["X-Request-Id"].ToString();

    Response.Headers.Append("X-Custom-Header", "MyValue");
    Response.Headers.Location = "/api/employees/42";

    return Created("/api/employees/42", dto);
}
```

`HttpContext.Request`, `HttpContext.Response` — HAR HTTP so'rov
uchun **Scoped** (yoki request-lifetime) obyekt, request'ning
BARCHA ma'lumotiga (header, body, query, route) kirish imkonini
beradi.

### 3.7 ETag — versioning

```csharp
[HttpGet("{id}")]
public IActionResult Get(int id)
{
    var employee = _repo.GetById(id);
    var etag = $"\"{employee.RowVersion}\"";

    if (Request.Headers.IfNoneMatch == etag)
        return StatusCode(304); // "Not Modified" — client'ning KESHI hali AKTUAL

    Response.Headers.ETag = etag;
    return Ok(employee);
}
```

```
ETag — resurs "VERSIYASI"ni ifodalaydi. Client — KEYINGI so'rovda
`If-None-Match: <etag>` yuboradi — agar SERVER'DAGI qiymat BIR
XIL bo'lsa — 304 (body YUBORILMAYDI, TARMOQ trafigi TEJALADI).
```

### 3.8 Curl bilan misollar

```bash
# GET
curl https://api.example.com/employees

# Header bilan
curl -H "Authorization: Bearer eyJhbGc..." https://api.example.com/employees/42

# POST + JSON body
curl -X POST https://api.example.com/employees \
  -H "Content-Type: application/json" \
  -d '{"fullName": "Orzibek", "age": 25}'

# Faqat response header'larni ko'rish
curl -I https://api.example.com/employees

# Verbose (to'liq handshake/header'larni ko'rish)
curl -v https://api.example.com/employees
```

## 4. Kod — real ERP misoli: to'liq request/response oqimi

```csharp
[HttpPost]
public async Task<IActionResult> Create(CreateEmployeeDto dto)
{
    // Request'dan o'qish
    var correlationId = Request.Headers["X-Correlation-Id"].FirstOrDefault() ?? Guid.NewGuid().ToString();

    var employee = await _service.CreateAsync(dto);

    // Response'ga yozish
    Response.Headers.Append("X-Correlation-Id", correlationId);
    return CreatedAtAction(nameof(GetById), new { id = employee.Id }, employee);
    // ↑ Bu — AVTOMATIK: 201 status, Location header, JSON body
}
```

## 5. Qachon ishlatish kerak?

| Vaziyat | Yechim |
|---|---|
| Autentifikatsiya | `Authorization` header |
| Ma'lumot formatini bildirish | `Content-Type` |
| Kutilgan javob formati | `Accept` |
| Distributed tracing | `X-Request-Id`/`X-Correlation-Id` |
| Resurs versiyasini tekshirish | `ETag` + `If-None-Match` |

## 6. Muhim nuqtalar

- `Content-Type` va `Accept` — **turli** maqsad: biri "MEN
  YUBORAYOTGAN format", ikkinchisi "MEN KUTAYOTGAN format".
- `Location` header — FAQAT `201 Created` javobida **kutiladi**
  (REST konvensiyasi).
- Custom header'lar (`X-*` prefiksi) — **standart bo'lmagan**,
  loyihaga xos ma'lumot uchun ishlatiladi.

## 7. Imtihon savollari

1. HTTP Request va Response tuzilmasining asosiy qismlarini
   ayting.
2. `Content-Type` va `Accept` header'lari orasidagi farq nima?
3. `Location` header qaysi status kodda ishlatiladi va nima
   uchun?
4. ETag qanday ishlaydi va u qanday amaliy foyda beradi (304
   status kod nuqtai nazaridan)?
5. `X-Request-Id`/Correlation ID nima uchun microservices
   arxitekturasida muhim?
6. Content Negotiation qanday jarayon?
