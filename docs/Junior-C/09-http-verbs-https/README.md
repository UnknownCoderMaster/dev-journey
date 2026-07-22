# HTTP Verbs, Request/Response, HTTP va HTTPS — Junior C

## 1. Nima?

**HTTP (HyperText Transfer Protocol)** — client va server orasidagi
so'rov-javob (request-response) protokoli. **HTTP Verb** (method) —
so'rovning **maqsadini** bildiruvchi so'z (`GET`, `POST` va h.k.).
**HTTPS** — HTTP + **TLS** (Transport Layer Security) — trafikni
shifrlaydigan qatlam.

## 2. Nima uchun kerak?

HTTP verblari bo'lmaganida — server har bir so'rovning "nima qilish
kerakligini" URL yoki body mazmunidan taxmin qilishga majbur bo'lardi.
Verb — bu **standartlashtirilgan niyat bildirish** usuli — proxy,
cache, load balancer, va boshqa vositalar so'rov nima qilishini
(masalan, "bu so'rov xavfsizmi, qayta-qayta yuborsa bo'ladimi")
oldindan bilishlari mumkin.

HTTPS bo'lmaganida — parol, token, shaxsiy ma'lumotlar **ochiq matn**
holida tarmoq orqali o'tadi — har qanday oraliq nuqta (Wi-Fi
router, ISP, proxy) ularni o'qiy oladi (Man-in-the-Middle hujumi).

## 3. Ichida nima sodir bo'ladi? (Mexanizm)

### 3.1 HTTP versiyalari

```
HTTP/1.0 (1996):
  Har bir so'rov uchun YANGI TCP ulanish, keyin yopiladi

HTTP/1.1 (1997, hozirgacha keng ishlatiladi):
  Keep-Alive — bitta TCP ulanish qayta ishlatiladi
  Lekin: Head-of-Line blocking — bitta ulanishda so'rovlar KETMA-KET
         bajarilishi kerak (parallel emas)

HTTP/2 (2015):
  Bitta TCP ulanish ustida MULTIPLEXING — bir nechta so'rov PARALLEL
  Binary protokol (matn emas)
  Header compression (HPACK)
  Server Push

HTTP/3 (2022, QUIC asosida):
  TCP o'rniga UDP (QUIC) — TCP head-of-line blocking muammosi TUZATILDI
  TLS 1.3 protokolga BUILT-IN (ajratilgan handshake shart emas)
```

### 3.2 HTTP so'rov (Request) tuzilishi

```
POST /api/employees HTTP/1.1          ← Method, Path, HTTP versiya
Host: api.example.com                  ← Header
Content-Type: application/json         ← Header
Authorization: Bearer eyJhbGc...       ← Header
Content-Length: 45                     ← Header

{"name": "Orzibek", "age": 25}         ← Body
```

### 3.3 HTTP javob (Response) tuzilishi

```
HTTP/1.1 201 Created                   ← Status kod, ibora
Content-Type: application/json         ← Header
Location: /api/employees/42            ← Header

{"id": 42, "name": "Orzibek", "age": 25}  ← Body
```

### 3.4 HTTP Verbs — to'liq semantika

| Verb | Maqsad | Idempotent? | Safe? | Body? |
|---|---|---|---|---|
| `GET` | Ma'lumot olish | ✅ | ✅ | ❌ |
| `POST` | Yangi resurs yaratish / amal bajarish | ❌ | ❌ | ✅ |
| `PUT` | To'liq resursni almashtirish | ✅ | ❌ | ✅ |
| `PATCH` | Resursning bir qismini yangilash | ❌* | ❌ | ✅ |
| `DELETE` | Resursni o'chirish | ✅ | ❌ | ❌ |
| `HEAD` | Faqat header (body yo'q) | ✅ | ✅ | ❌ |
| `OPTIONS` | Qaysi metodlar qo'llab-quvvatlanishini bilish (CORS preflight) | ✅ | ✅ | ❌ |

**\*PATCH** — texnik jihatdan idempotent bo'lishi ham mumkin (agar
"butun qiymatni o'rnatish" operatsiyasi bo'lsa), lekin ko'pincha
(masalan `{"increment": 1}` kabi) idempotent EMAS.

**Safe method** — server holatini **o'zgartirmaydigan** metod (`GET`,
`HEAD`, `OPTIONS`). Bu — brauzerlarga "prefetch" qilish, qidiruv
tizimlariga sahifalarni indekslash imkonini beradi (chunki bu safe
metodlar hech qanday nojo'ya ta'sir qilmasligiga ishonch bor).

**Idempotent** — bir xil so'rov **necha marta yuborilsa ham**, server
holati **birinchi so'rovdan keyingi holat bilan bir xil** bo'lib
qoladi:

```
DELETE /api/employees/42  → 204 (o'chirildi)
DELETE /api/employees/42  → 404 (allaqachon yo'q) — LEKIN server holati o'zgarmadi (hali ham yo'q)
→ Bu IDEMPOTENT hisoblanadi (natija turlicha ko'rinsa ham, SERVER HOLATI bir xil)

POST /api/employees {"name": "X"} → 201 (yaratildi, id=1)
POST /api/employees {"name": "X"} → 201 (YANA yaratildi, id=2!)
→ Bu IDEMPOTENT EMAS — har chaqiriqda YANGI resurs paydo bo'ladi
```

**Nima uchun muhim:** tarmoq uzilishi tufayli client javobni ololmasa
va so'rovni **qayta yuborsa** — `PUT`/`DELETE` xavfsiz qayta yuborilishi
mumkin, `POST` esa **ikki marta yaratish** xavfini tug'diradi (shuning
uchun ba'zi API'lar `Idempotency-Key` header qo'llaydi).

### 3.5 Status kodlari — to'liq

```
1xx — Informational (kamdan-kam ko'rinadi):
  100 Continue           → Server body qabul qilishga tayyor

2xx — Muvaffaqiyatli:
  200 OK                 → Oddiy muvaffaqiyat, body bor
  201 Created             → Yangi resurs yaratildi (Location header bilan)
  202 Accepted             → Qabul qilindi, hali qayta ishlanmoqda (async)
  204 No Content           → Muvaffaqiyatli, javob tanasi yo'q

3xx — Redirect:
  301 Moved Permanently    → Resurs boshqa URL ga KO'CHDI (doimiy)
  302 Found                → Vaqtincha boshqa URL ga yo'naltirish
  304 Not Modified          → Cache hali ham amal qiladi (If-None-Match bilan)

4xx — Client xatosi:
  400 Bad Request           → Noto'g'ri so'rov (validatsiya)
  401 Unauthorized           → Autentifikatsiya YO'Q yoki noto'g'ri (kim ekanligi noma'lum)
  403 Forbidden              → Autentifikatsiya BOR, lekin ruxsat yo'q (kim ekanligi ma'lum, huquq yo'q)
  404 Not Found              → Resurs topilmadi
  405 Method Not Allowed     → Bu resurs uchun bu method qo'llab-quvvatlanmaydi
  409 Conflict                → Holat ziddiyati (masalan, unique constraint)
  422 Unprocessable Entity    → Sintaksis to'g'ri, lekin semantik xato

5xx — Server xatosi:
  500 Internal Server Error   → Kutilmagan server xatosi
  502 Bad Gateway              → Gateway/proxy orqadagi serverdan noto'g'ri javob oldi
  503 Service Unavailable      → Server vaqtincha ishlamayapti (yuklama, maintenance)
  504 Gateway Timeout          → Orqadagi server javob bermadi
```

**401 vs 403 farqi — muhim tushunish:**
```
401 Unauthorized: "Sen kimligingni bilmayapman (token yo'q/yaroqsiz)"
403 Forbidden:    "Sen kimligingni bilaman, lekin senga bu ishni qilishga RUXSAT yo'q"
```

### 3.6 Content-Type, Accept, Content-Length

```
Request:
  Content-Type: application/json     → "Men JSON yuboryapman"
  Accept: application/json           → "Menga JSON qaytar"
  Content-Length: 128                → Body necha baytligi

Response:
  Content-Type: application/json; charset=utf-8
```

**Content negotiation** — server bir xil resurs uchun `Accept` header
asosida turli format (JSON, XML) qaytarishi mumkin.

### 3.7 HTTPS — TLS Handshake batafsil

```
1. CLIENT HELLO
   Client → Server: "Mana men qo'llab-quvvatlaydigan TLS versiyalari
                      va cipher suite'lar ro'yxati"

2. SERVER HELLO + CERTIFICATE
   Server → Client: "Men tanlagan cipher suite + mening SSL sertifikatim
                      (server public key + CA imzosi bilan)"

3. SERTIFIKAT TEKSHIRUVI
   Client: Sertifikatni ishonchli CA (Certificate Authority) orqali
           tekshiradi — "Bu server haqiqatan aytgan kim ekanini
           tasdiqlaydi"

4. KEY EXCHANGE
   Client: "Session key" (simmetrik shifrlash uchun) generatsiya qiladi,
           uni server'ning PUBLIC key'i bilan shifrlab yuboradi

5. SERVER DECRYPT
   Server: O'z PRIVATE key'i bilan session key'ni ochadi

6. SIMMETRIK SHIFRLASH BOSHLANADI
   Ikkala taraf ham endi SESSION KEY (simmetrik) bilan barcha
   trafikni shifrlaydi — bu tezroq, chunki asimmetrik shifrlash
   qimmat (CPU sarflaydi)
```

**Nima uchun ikki xil shifrlash (asimmetrik + simmetrik) ishlatiladi?**

```
Asimmetrik (RSA/ECDHE):
  ✅ Xavfsiz key almashish (public/private key juftligi)
  ❌ SEKIN — katta ma'lumot uchun mos emas

Simmetrik (AES):
  ✅ TEZ — katta hajmdagi trafikni shifrlash uchun ideal
  ❌ Ikkala tomon HAM bir xil kalitni bilishi kerak (xavfsiz almashish muammosi)

Yechim: Asimmetrik — FAQAT session key'ni xavfsiz almashish uchun,
        Simmetrik — QOLGAN BARCHA trafik uchun (tezlik uchun)
```

```
HTTP (shifrlanmagan):
  Client → [ochiq matn: "password=12345"] → Server
  Hacker WiFi'da o'rtada TURIB buni O'QIY OLADI!

HTTPS (shifrlangan):
  Client → [AES bilan shifrlangan bайtlar] → Server
  Hacker faqat "tasodifiy" ko'rinadigan baytlarni ko'radi
```

### 3.8 HTTP/2 — Multiplexing va Header Compression

```
HTTP/1.1 muammosi (Head-of-Line blocking):
  So'rov1 → [kutish] → Javob1
  So'rov2 → [1 tugagach boshlanadi] → Javob2
  (yoki bir nechta parallel TCP ulanish ochish kerak — browserlar 6 tagacha ruxsat beradi)

HTTP/2 yechimi (Multiplexing):
  Bitta TCP ulanish ustida:
  So'rov1 →→
  So'rov2  →→→  Barchasi PARALLEL, "stream ID" orqali ajratiladi
  So'rov3   →→
  Javob1, Javob2, Javob3 — istalgan tartibda qaytishi mumkin
```

**HPACK (Header compression)** — HTTP/1.1 da har so'rovda bir xil
headerlar (`User-Agent`, `Cookie`) qayta-qayta to'liq yuboriladi.
HTTP/2 — bu headerlarni **kompressiya** qiladi va **takrorlanuvchi**
headerlarni faqat bir marta to'liq, keyingi safar **indeks** orqali
yuboradi.

**Server Push** — server, client so'ramasdan turib, kerakli bo'lishi
mumkin bo'lgan resurslarni (masalan, `style.css`) oldindan yuboradi.

## 4. Kod — ASP.NET Core misoli

```csharp
[HttpGet]                         // Safe, Idempotent
public ActionResult<List<Employee>> GetAll() => Ok(_repo.GetAll());

[HttpPost]                        // Not Idempotent — har chaqiriqda yangi resurs
public ActionResult<Employee> Create(CreateEmployeeDto dto)
{
    var emp = _repo.Create(dto);
    return CreatedAtAction(nameof(GetById), new { id = emp.Id }, emp); // 201
}

[HttpPut("{id}")]                 // Idempotent — to'liq almashtirish
public IActionResult Update(int id, UpdateEmployeeDto dto)
{
    _repo.Update(id, dto);
    return NoContent();           // 204
}

[HttpPatch("{id}")]               // Qisman yangilash
public IActionResult PartialUpdate(int id, JsonPatchDocument<Employee> patch)
{
    var emp = _repo.GetById(id);
    patch.ApplyTo(emp);
    _repo.Save();
    return NoContent();
}

[HttpDelete("{id}")]              // Idempotent
public IActionResult Delete(int id)
{
    _repo.Delete(id);
    return NoContent();           // 204
}
```

## 5. Qachon ishlatish kerak?

| Vaziyat | Verb |
|---|---|
| Ma'lumot o'qish, hech narsa o'zgartirmaslik | `GET` |
| Yangi resurs yaratish | `POST` |
| Resursni butunlay almashtirish (barcha maydonlar) | `PUT` |
| Resursning faqat bir qismini yangilash | `PATCH` |
| Resursni o'chirish | `DELETE` |
| Faqat headerlarni bilish (fayl hajmi, mavjudligi) | `HEAD` |
| CORS preflight yoki qo'llab-quvvatlanadigan metodlarni bilish | `OPTIONS` |

**Anti-patternlar:**

```
❌ GET so'rovda ma'lumot o'zgartirish (masalan /delete-employee?id=5)
   — brauzer prefetch qilib, TASODIFAN o'chirib yuborishi mumkin!

❌ Har doim 200 qaytarish (xato bo'lsa ham) va xabarni body ichiga yozish
   — HTTP semantikasi buziladi, client status kodga qarab avtomatik
     qaror qabul qila olmaydi

❌ Muvaffaqiyatli DELETE uchun 200 + body qaytarish
   — 204 No Content ko'proq to'g'ri (body yo'qligi kutiladi)
```

## 6. Qo'shimcha — chuqur nuqtalar

- **CORS (Cross-Origin Resource Sharing)** — brauzer xavfsizligi
  siyosati — bir domendan (`https://app.com`) boshqa domenga
  (`https://api.com`) so'rov yuborilganda, server ruxsat berishi
  kerak:
  ```csharp
  builder.Services.AddCors(options =>
      options.AddPolicy("AllowFrontend", policy =>
          policy.WithOrigins("https://app.com")
                .AllowAnyMethod()
                .AllowAnyHeader()));
  ```
  Murakkab so'rovlar uchun brauzer avval `OPTIONS` (preflight) so'rov
  yuboradi — server qaysi metod/header larga ruxsat berishini so'raydi.

- **Idempotency-Key header** — `POST` so'rovlarni ham xavfsiz qayta
  yuborish uchun (masalan to'lov tizimlarida) — client noyob key
  yuboradi, server bir xil key bilan ikkinchi marta kelgan so'rovni
  "birinchi natijani qaytarish" bilan javob beradi (yangi yozuv
  yaratmasdan).

- **ETag va cache invalidation** — server resurs versiyasini
  `ETag` header orqali beradi; client keyingi so'rovda
  `If-None-Match` yuboradi — agar mos kelsa, server `304 Not
  Modified` qaytaradi (body qayta yubormasdan, tarmoq trafigini
  tejaydi).

- **HTTP/3 va QUIC** — TCP o'rniga UDP asosida ishlaydi, bu TCP'ning
  "head-of-line blocking" muammosini network darajasida ham hal
  qiladi (HTTP/2 faqat application darajasida hal qilgan edi).

- **Real loyihada uchraydigan xato:** `PUT` so'rovni **qisman**
  ma'lumot bilan (faqat 2 ta maydon) yuborish — bu boshqa maydonlarni
  **default/null** qilib qo'yishi mumkin, chunki `PUT` semantikasi
  "to'liq almashtirish"ni anglatadi. Qisman yangilash uchun `PATCH`
  ishlatilishi kerak.

## 7. Imtihon savollari

1. `PUT` va `PATCH` orasidagi farq nima?
2. Idempotent nima degani? `DELETE` idempotent bo'lsa-yu, `POST`
   bo'lmasa — buni misol bilan tushuntiring.
3. Safe method nima va bu qanday amaliy foyda beradi (masalan,
   brauzer prefetch nuqtai nazaridan)?
4. TLS handshake bosqichlarini tartib bilan ayting.
5. Nima uchun HTTPS'da ham asimmetrik, ham simmetrik shifrlash
   ishlatiladi?
6. HTTP/2 ning HTTP/1.1 dan asosiy 2 ta ustunligini ayting va
   tushuntiring.
7. 401 va 403 status kodlari orasidagi farq nima?
8. CORS preflight so'rovi qaysi HTTP verb orqali yuboriladi va
   nima uchun kerak?
