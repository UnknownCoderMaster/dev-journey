# REST vs SOAP (JSON vs XML) — Junior A

## 1. Nima? (Ta'rif)

**REST (Representational State Transfer)** — HTTP protokoli
tamoyillariga asoslangan, **resurs-markazli** arxitektura uslubi.
**SOAP (Simple Object Access Protocol)** — **XML-asoslangan**,
**protokol** darajasidagi qat'iy standart.

## 2. Nima uchun kerak?

Turli davr, turli ehtiyoj uchun yaratilgan: SOAP — 2000-yillar
boshida **enterprise, xavfsizlik-kritik** integratsiyalar uchun;
REST — **soddalik, yengillik** talab qiluvchi zamonaviy web/mobil
API'lar uchun.

## 3. Ichida nima sodir bo'ladi? (Mexanizm)

### 3.1 REST Principles

```
Stateless        — HAR SO'ROV — MUSTAQIL, server SO'ROVLAR ORASIDA
                     "holat" SAQLAMAYDI (token/session — CLIENT
                     tomonda saqlanadi)
Client-Server    — UI va DATA STORAGE — AJRATILGAN
Cacheable        — Javoblar — KESHLANISHI mumkin (Cache-Control)
Uniform Interface — BIR XIL HTTP verb/status kod semantikasi
                     BARCHA resurslar uchun
```

### 3.2 HTTP verb semantika

```
GET    — o'qish, safe, idempotent
POST   — yaratish
PUT    — to'liq yangilash, idempotent
PATCH  — qisman yangilash
DELETE — o'chirish, idempotent
```

### 3.3 Resource-based URL

```
✅ REST — RESURS (ot) markazlashgan:
GET /api/employees/42
POST /api/employees

❌ RPC uslubi (REST EMAS):
POST /api/getEmployee?id=42
POST /api/createEmployee
```

### 3.4 JSON format

```json
{ "id": 42, "fullName": "Orzibek", "department": "IT" }
```

### 3.5 Stateless — session yo'q, token

```
REST API — HAR so'rovda CLIENT — KERAKLI barcha ma'lumotni
(masalan JWT token) YUBORADI. Server — OLDINGI so'rovlarni
"ESLAB QOLMAYDI" — bu, GORIZONTAL MASSHTABLASHNI OSONLASHTIRADI
(istalgan server SO'ROVGA JAVOB bera oladi).
```

### 3.6 SOAP — XML envelope

```xml
<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope">
  <soap:Header>
    <AuthToken>abc123</AuthToken>
  </soap:Header>
  <soap:Body>
    <GetEmployeeRequest>
      <EmployeeId>42</EmployeeId>
    </GetEmployeeRequest>
  </soap:Body>
</soap:Envelope>
```

```
Header — METADATA (autentifikatsiya, tranzaksiya ma'lumoti)
Body   — HAQIQIY so'rov/javob ma'lumoti
```

### 3.7 WSDL — service description

```
WSDL (Web Services Description Language) — SOAP servisining
"KONTRAKT"i — QAYSI metodlar MAVJUD, QANDAY parametr qabul
qiladi, QANDAY natija qaytaradi — XML formatda, MASHINA-O'QIY
OLADIGAN tarzda TASVIRLANADI (REST'dagi OpenAPI/Swagger'ga
O'XSHASH, LEKIN QAT'IYROQ).
```

### 3.8 WS-Security, WS-ReliableMessaging

```
WS-Security          — XABAR darajasida SHIFRLASH/imzolash
                         (transport darajasidagi HTTPS'dan TASHQARI,
                         QO'SHIMCHA qatlam)
WS-ReliableMessaging  — XABAR YETKAZILISHINI KAFOLATLASH (hatto
                         tarmoq muammosi bo'lsa ham)

Bu standartlar — BANK, HARBIY, davlat tizimlarida hali HAM
ISHLATILADI (qat'iy kafolat TALAB qilinganda).
```

### 3.9 .NET'da `System.ServiceModel`

```csharp
// WCF (Windows Communication Foundation) — .NET'ning SOAP implementatsiyasi
[ServiceContract]
public interface IEmployeeService
{
    [OperationContract]
    Employee GetEmployee(int id);
}
```

`.NET Core`/`.NET 5+` — WCF'ni **to'liq qo'llab-quvvatlamaydi**
(faqat client tomoni, `CoreWCF` community loyihasi orqali server
ham mumkin) — bu, .NET ekotizimining **REST/gRPC**ga siljiganini
ko'rsatadi.

### 3.10 REST vs SOAP taqqoslash jadvali

| | REST | SOAP |
|---|---|---|
| Format | JSON (odatda) | FAQAT XML |
| Protokol | HTTP (asosan) | HTTP, SMTP, TCP va boshqalar |
| Xavfsizlik | HTTPS, OAuth/JWT | WS-Security (murakkabroq, kuchliroq) |
| Tezlik | ✅ Tez, yengil | Sekinroq (XML overhead) |
| Murakkablik | Oddiy | Murakkab, qat'iy |
| Kontrakt | OpenAPI (ixtiyoriy) | WSDL (MAJBURIY) |
| Transaction support | Yo'q (o'zi) | ✅ WS-* standartlari orqali |

### 3.11 JSON vs XML

```
JSON:
  ✅ Yengil, tez PARSE qilinadi, human-readable
  ✅ JavaScript bilan TABIIY (native) mos
  ❌ SCHEMA validatsiyasi — ZAIFROQ (JSON Schema — ixtiyoriy)

XML:
  ✅ Kuchli SCHEMA (XSD) — QAT'IY validatsiya
  ✅ NAMESPACE — nom to'qnashuvidan HIMOYA
  ❌ OG'IR, KO'P "boilerplate" belgi (<tag></tag>)
```

### 3.12 gRPC — zamonaviy alternativa

```
gRPC — Google'ning, Protocol Buffers (BINARY format) asosidagi,
HTTP/2 ustida ishlaydigan, YUQORI PERFORMANCE RPC freymvorki.

REST'dan TEZROQ (binary, HTTP/2 multiplexing), LEKIN brauzer
to'g'ridan qo'llab-quvvatlamaydi (gRPC-Web kerak) — ko'proq
MICROSERVICE'lar ORASIDA (server-to-server) ishlatiladi.
```

### 3.13 REST best practices

```
Versioning:  /api/v1/employees
Pagination:  ?page=2&pageSize=20
HATEOAS:     Response ichida bog'liq resurslarga HAVOLALAR
```

### 3.14 Qachon REST, qachon SOAP

```
REST — Zamonaviy web/mobil API, microservices, PUBLIC API'lar
SOAP — Legacy ENTERPRISE tizimlar (bank, sug'urta), QAT'IY
        transaction/xavfsizlik STANDARTI talab qilinganda,
        ESKI tizimlar bilan INTEGRATSIYA
```

## 4. Kod — REST API misoli (ERP)

```csharp
[ApiController]
[Route("api/v1/[controller]")]
public class EmployeesController : ControllerBase
{
    [HttpGet]
    public async Task<ActionResult<List<EmployeeDto>>> GetAll([FromQuery] int page = 1, [FromQuery] int pageSize = 20)
        => Ok(await _service.GetPagedAsync(page, pageSize));

    [HttpGet("{id}")]
    public async Task<ActionResult<EmployeeDto>> GetById(int id) => Ok(await _service.GetByIdAsync(id));
}
```

## 5. Qachon ishlatish kerak?

| Vaziyat | Yechim |
|---|---|
| Yangi API, mobil/web frontend | REST + JSON |
| Legacy bank/enterprise integratsiya | SOAP |
| Microservices, yuqori performance | gRPC |
| Dokumentatsiya OpenAPI orqali | REST + Swagger |

## 6. Muhim nuqtalar

- SOAP — hozir **yangi loyihalarda kamdan-kam** ishlatiladi, lekin
  **legacy integratsiya**larda hali ham uchraydi.
- REST — **rasmiy standart EMAS**, balki **uslub** (constraints
  to'plami) — shuning uchun "REST-ful" darajasi loyihadan loyihaga
  farq qiladi.
- .NET Core — WCF'ni to'liq qo'llab-quvvatlamaydi, bu **REST/gRPC**
  tomon **strategik siljish**ni ko'rsatadi.

## 7. Imtihon savollari

1. REST'ning asosiy tamoyillarini (Stateless, Client-Server va
   h.k.) ayting.
2. SOAP'da Header va Body qismlari nima uchun ajratilgan?
3. WSDL nima vazifani bajaradi va u OpenAPI'ga qanday o'xshaydi?
4. JSON va XML orasidagi asosiy tradeoff'lar nima?
5. gRPC REST'dan qanday farq qiladi va qachon afzal?
6. Qachon REST, qachon SOAP tanlanadi?
