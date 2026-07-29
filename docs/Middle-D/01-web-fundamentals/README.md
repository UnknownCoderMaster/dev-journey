# Web Fundamentals — IP, Port, URL, Storage, Proxy, Gateway, SSH, REST, WebSocket — Middle D

## 1. Nima? (Ta'rif)

Bu hujjat — web ilovalari ishlashi uchun zarur bo'lgan **infratuzilma
asoslari**: manzillash (IP, Port, URL), brauzer saqlash mexanizmlari,
server turlari (web server, reverse proxy, gateway), xavfsiz masofaviy
kirish (SSH), va zamonaviy API dizayn tamoyillari (REST, WebSocket).

## 2. Nima uchun kerak? (Muammo va yechim)

Har qanday web so'rov — client'dan serverga **qandaydir manzil**
orqali yetib borishi kerak. Bu manzillash tizimi (IP+Port+URL) va
oraliq vositalar (proxy, gateway) bo'lmasa — internet **markazlashgan,
masshtablanmaydigan, xavfsiz bo'lmagan** tizim bo'lib qolardi. Har bir
qatlam (Nginx, Gateway, SSH) — **muayyan muammoni** hal qilish uchun
qo'shilgan: load balancing, xavfsizlik, monitoring, marshrutlash.

## 3. Ichida nima sodir bo'ladi? (Mexanizm)

### 3.1 IPv4 vs IPv6

```
IPv4: 32 bit, 4 ta oktet    → 192.168.1.1        (~4.3 milliard manzil)
IPv6: 128 bit, 8 ta guruh   → 2001:0db8::1        (~340 undecillion manzil)
```

IPv4 manzillar **tugab qolgani** sababli IPv6 yaratildi. IPv6 —
`::` orqali ketma-ket nollarni qisqartiradi (`2001:0db8:0000:0000:
0000:0000:0000:0001` → `2001:0db8::1`).

**Maxsus manzillar:**
```
127.0.0.1     — Loopback (localhost) — kompyuterning O'ZINI ko'rsatadi
0.0.0.0       — "Barcha interfeyslar" — server BARCHA tarmoq
                interfeyslarida tinglashini bildiradi (bog'lash uchun),
                client tomonda esa "noma'lum manzil" degani
255.255.255.255 — Broadcast — tarmoqdagi BARCHA qurilmalarga
192.168.x.x, 10.x.x.x, 172.16-31.x.x — Private (lokal tarmoq) manzillar
```

### 3.2 Port — turlari

```
0–1023      Well-known (tizim) portlar     — 80 (HTTP), 443 (HTTPS), 22 (SSH)
1024–49151  Registered portlar              — 5432 (PostgreSQL), 5672 (RabbitMQ)
49152–65535 Dynamic/Private (ephemeral)      — client tomonidan VAQTINCHA ishlatiladi
```

Har bir TCP ulanish — `(source IP, source Port, dest IP, dest Port)`
kombinatsiyasi orqali noyob aniqlanadi — shuning uchun bitta serverga
minglab client bir vaqtda ulansa ham, ular bir-biridan **ephemeral
port** orqali farqlanadi.

### 3.3 URL tuzilishi

```
https://api.example.com:8443/employees/42?department=IT&active=true#top
└─┬──┘   └──────┬──────┘└─┬─┘└──────┬─────┘└────────┬────────┘└─┬─┘
scheme        host       port      path            query      fragment

Origin = scheme + host + port  → "https://api.example.com:8443"
```

**Path vs Query farqi:**
```
Path  — RESURSNING O'ZINI identifikatsiya qiladi: /employees/42
Query — FILTRLASH/PARAMETR uchun: ?department=IT&active=true

Qoida: agar qiymat resursni ANIQLASA — path (masalan ID),
       agar FILTRLASA/tanlasa — query (masalan sahifalash, saralash)
```

### 3.4 User-Agent

```
Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ...
```

Brauzer/klient qanday dastur ekanini bildiruvchi HTTP header.
ASP.NET Core'da o'qish:

```csharp
var userAgent = Request.Headers["User-Agent"].ToString();
```

### 3.5 Browser Storage — LocalStorage vs Cookie vs Session

| | LocalStorage | SessionStorage | Cookie |
|---|---|---|---|
| Muddat | Doimiy (o'chirilmaguncha) | Tab yopilguncha | Belgilangan `Expires` |
| Serverga avtomatik yuborilishi | ❌ Yo'q | ❌ Yo'q | ✅ Har so'rovda |
| Hajm | ~5-10MB | ~5-10MB | ~4KB |
| JS orqali o'qish | ✅ Ha | ✅ Ha | Faqat `HttpOnly` bo'lmasa |
| XSS xavfi | Yuqori | Yuqori | `HttpOnly` bilan past |

**Qachon qaysi:** Auth token — `HttpOnly` Cookie (JS o'qiy olmaydi,
XSS himoyasi). UI holati (theme, til) — LocalStorage. Vaqtinchalik
form ma'lumoti — SessionStorage.

### 3.6 Web Server — Nginx, IIS, Kestrel

```
Kestrel — .NET'ning ICHKI, kross-platform web serveri (har ASP.NET
          Core ilovasida BUILT-IN ishlaydi)
Nginx   — TASHQI, yuqori performance reverse proxy/web server
IIS     — Windows'ga xos web server (Kestrel oldida ham ishlashi mumkin)

Odatiy production sxema:
Internet → Nginx (80/443, SSL termination) → Kestrel (5000, ichki) → ASP.NET Core
```

Kestrel — o'zi to'g'ridan internetga ochilishi **tavsiya etilmaydi**
(ba'zi past darajadagi HTTP hujumlariga qarshi Nginx/IIS kabi
"tajribali" proxy kerak).

### 3.7 Reverse Proxy

```
Client → [Nginx: reverse proxy] → Backend server(lar)

Nginx vazifalari:
  - SSL Termination (HTTPS'ni shu yerda "ochadi", ichkariga HTTP)
  - Load Balancing (bir nechta backend orasida so'rovlarni bo'lish)
  - Statik fayllarni bevosita xizmat qilish (CSS/JS/rasm)
  - Compression (gzip)
```

```nginx
server {
    listen 80;
    server_name api.example.com;
    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 3.8 Gateway — API Gateway vs Reverse Proxy

```
Reverse Proxy — UMUMIY vazifa: trafikni yo'naltirish, SSL, load balancing
API Gateway   — Reverse Proxy + API'GA XOS mantiq:
                  - Autentifikatsiya/avtorizatsiya (BIR joyda)
                  - Rate limiting
                  - Request/Response transformatsiya
                  - Bir nechta MICROSERVICE'ni BITTA endpoint orqali ko'rsatish
```

.NET ekotizimida — **YARP** (Yet Another Reverse Proxy, Microsoft'ning
o'zi) yoki **Ocelot** ishlatiladi:

```csharp
// YARP — appsettings.json orqali marshrutlash
builder.Services.AddReverseProxy()
    .LoadFromConfig(builder.Configuration.GetSection("ReverseProxy"));

app.MapReverseProxy();
```

### 3.9 SSH — protokol

```
1. TCP ulanish (port 22)
2. Server host key'ini yuboradi
3. Key Exchange (Diffie-Hellman) — session key kelishiladi
4. Autentifikatsiya (parol yoki kalit juftligi)
5. Shifrlangan kanal ochiladi
```

### 3.10 REST API best practices

```
Versioning:    /api/v1/employees
Pagination:    GET /employees?page=2&pageSize=20
               Response: { "data": [...], "totalCount": 145, "page": 2 }
HATEOAS:       Response ichida BOG'LIQ resurslarga HAVOLALAR:
               { "id": 42, "_links": { "self": "/employees/42",
                                        "department": "/departments/3" } }
```

HATEOAS (Hypermedia As The Engine Of Application State) — client'ning
API strukturasini **oldindan bilishi shart emas**, javobdagi
havolalar orqali navigatsiya qiladi (amalda kam ishlatiladi, lekin
"to'liq REST" ta'rifining qismi).

### 3.11 WebSocket

```
HTTP: har so'rov uchun YANGI request-response (yoki polling)
WebSocket: BITTA ulanish ustida IKKI TOMONLAMA, DOIMIY aloqa

Handshake:
Client → GET /ws HTTP/1.1
         Upgrade: websocket
         Connection: Upgrade
Server → HTTP/1.1 101 Switching Protocols
         (Endi TCP ulanish WebSocket protokoliga "ko'tarilgan")
```

WebSocket — real-time (chat, live dashboard, notification) uchun
kerak, chunki server **client so'ramasdan turib** xabar yubora oladi
(HTTP'da bu mumkin emas — server faqat so'rovga JAVOB beradi).

## 4. Kod — implementatsiya

```csharp
// User-Agent o'qish
[HttpGet]
public IActionResult Info()
{
    var ua = Request.Headers.UserAgent.ToString();
    var origin = $"{Request.Scheme}://{Request.Host}";
    return Ok(new { ua, origin });
}

// Pagination bilan REST endpoint
[HttpGet]
public async Task<IActionResult> GetEmployees(int page = 1, int pageSize = 20)
{
    var query = _context.Employees.AsQueryable();
    var total = await query.CountAsync();
    var items = await query.Skip((page - 1) * pageSize).Take(pageSize).ToListAsync();

    return Ok(new { data = items, totalCount = total, page, pageSize });
}
```

## 5. Qachon ishlatish kerak?

| Vaziyat | Yechim |
|---|---|
| Auth token saqlash | HttpOnly Cookie |
| UI sozlamalari | LocalStorage |
| Bir nechta microservice bitta kirish nuqtasi | API Gateway (YARP/Ocelot) |
| SSL/load balancing, statik fayl | Nginx (reverse proxy) |
| Real-time chat/dashboard | WebSocket / SignalR |
| Oddiy CRUD API | REST + pagination |

## 6. Muhim nuqtalar

- `0.0.0.0` bilan bog'lash (bind) — server barcha tarmoq
  interfeyslaridan qabul qiladi; `127.0.0.1` bilan bog'lash — faqat
  shu mashinaning o'zidan kelgan so'rovlarni qabul qiladi (tashqi
  tarmoqdan yopiq).
- `localhost` — DNS orqali odatda `127.0.0.1`ga hal qilinadi, lekin
  `hosts` faylida o'zgartirilishi mumkin.
- HATEOAS'ni amalda ko'p API qo'llamaydi (murakkablik/foyda
  nisbati past), lekin intervyularda tez-tez so'raladi.
- WebSocket — statefull (ulanish davomida holat saqlanadi), bu
  load balancer orqasida **sticky session** talab qilishi mumkin.

## 7. Imtihon savollari

1. `127.0.0.1` va `0.0.0.0` orasidagi farqni tushuntiring.
2. Path parametr va Query parametr qachon ishlatiladi — qoida qanday?
3. LocalStorage'da JWT saqlash nima uchun xavfli hisoblanadi?
4. Reverse Proxy va API Gateway orasidagi farq nima?
5. WebSocket handshake jarayonini tushuntiring — u HTTP bilan qanday
   boshlanadi?
6. Well-known, registered va dynamic portlar orasidagi farqni ayting.
7. HATEOAS nima va u REST API'ni qanday "to'liqroq" qiladi?
