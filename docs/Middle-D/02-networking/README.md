# Networking — OSI, TCP/UDP, DNS, NAT, Subnetting — Middle D

## 1. Nima? (Ta'rif)

**Networking** — kompyuterlar orasidagi ma'lumot almashinuvini
ta'minlovchi protokollar va infratuzilma majmuasi. **OSI modeli** —
tarmoq aloqasini 7 mavhum qatlamga bo'luvchi kontseptual freymvork.

## 2. Nima uchun kerak?

Backend developer sifatida "nega API sekin ishlayapti", "nega
connection timeout bo'lyapti", "nega Docker konteynerlar bir-birini
ko'rmayapti" kabi muammolarni networking asoslarisiz diagnostika
qilib bo'lmaydi.

## 3. Ichida nima sodir bo'ladi? (Mexanizm)

### 3.1 OSI modeli — 7 qatlam

```
7. Application  — HTTP, FTP, SMTP (foydalanuvchi ilova protokollari)
6. Presentation — Shifrlash, kompressiya, format (TLS shu yerda)
5. Session      — Ulanishni boshqarish, sessiya
4. Transport    — TCP, UDP (port, ishonchlilik)
3. Network      — IP (manzillash, routing)
2. Data Link    — MAC manzil, Ethernet (fizik segment ichida)
1. Physical     — Kabel, signal, bit oqimi
```

Amalda ko'proq ishlatiladigan **TCP/IP modeli** (4 qatlam):
`Application → Transport → Internet → Network Access` — OSI'ning
soddalashtirilgan versiyasi.

### 3.2 TCP vs UDP

```
TCP (Transmission Control Protocol):
  ✅ Ishonchli — yetkazilishi KAFOLATLANADI (ACK, qayta yuborish)
  ✅ Tartibli — paketlar TO'G'RI tartibda yetib boradi
  ❌ Sekinroq — handshake, ACK overhead

UDP (User Datagram Protocol):
  ❌ Ishonchsiz — paket YO'QOLISHI mumkin, kafolat yo'q
  ❌ Tartibsiz — paketlar boshqa tartibda yetib borishi mumkin
  ✅ Tezroq — overhead yo'q

Qachon qaysi:
  TCP — HTTP, DB ulanish, fayl uzatish (ANIQLIK muhim)
  UDP — video stream, DNS, gaming (TEZLIK muhim, ozgina yo'qotish OK)
```

### 3.3 TCP 3-way handshake

```
Client                              Server
  │──────── SYN (seq=x) ──────────►│   "Ulanmoqchiman"
  │◄─── SYN-ACK (seq=y, ack=x+1) ──│   "Roziman, sen ham tasdiqla"
  │──────── ACK (ack=y+1) ────────►│   "Tasdiqladim"
  │                                  │
  │  ═══════ ULANISH OCHIQ ════════  │
```

Ulanishni yopish esa **4-way handshake** (FIN/ACK) orqali — har
tomon mustaqil ravishda "men tugatdim" deb bildiradi.

### 3.4 DNS — qanday ishlaydi

```
1. Brauzer: "api.example.com" IP manzili KERAK
2. Local DNS cache tekshiriladi — topilmasa:
3. Resolver → Root DNS server → ".com" uchun qayerga borish
4. Resolver → TLD (.com) server → "example.com" uchun qayerga borish
5. Resolver → Authoritative DNS server (example.com) → ANIQ IP qaytaradi
6. Natija KESHLANADI (TTL muddatigacha)
7. Brauzer endi shu IP'ga TCP ulanish ochadi
```

```
A record     — domain → IPv4 manzil
AAAA record  — domain → IPv6 manzil
CNAME        — domain → boshqa domain (alias)
MX record    — email server manzili
TXT record   — tekst ma'lumot (masalan domain tasdiqlash)
```

### 3.5 NAT (Network Address Translation)

```
Uy tarmog'ida 5 ta qurilma — HAMMASI bitta PUBLIC IP orqali internetga chiqadi:

192.168.1.10 ─┐
192.168.1.11 ─┼── Router (NAT) ── Public IP: 203.0.113.5 ── Internet
192.168.1.12 ─┘

Router — har bir ICHKI (private) manzil + portni TASHQI (public)
IP + boshqa port bilan ALMASHTIRADI, va javob kelganda TESKARI
YO'NALTIRADI (NAT table orqali kuzatadi).
```

NAT — IPv4 manzillar yetishmasligini "yumshatadi" (bitta public IP —
minglab qurilmaga xizmat qiladi).

### 3.6 Subnet Mask va CIDR notation

```
IP: 192.168.1.0/24
                 └─ CIDR — birinchi 24 bit "network" qismi,
                    qolgan 8 bit "host" qismi

Subnet mask: 255.255.255.0 (24 ta "1" bit)

192.168.1.0/24  → 192.168.1.0 dan 192.168.1.255 gacha (256 ta manzil)
192.168.1.0/28  → faqat 16 ta manzil (kichikroq subnet)
```

Docker Compose'da har bir `network` — o'z subnet'iga ega bo'ladi,
konteynerlar shu ichida bir-birini nomi orqali topadi.

### 3.7 HTTP/1.1 vs HTTP/2 vs HTTP/3

```
HTTP/1.1 — Keep-Alive, lekin Head-of-Line blocking
HTTP/2   — Multiplexing, Header compression (HPACK), Server Push
HTTP/3   — UDP (QUIC) asosida, TCP head-of-line blocking'ni HAM yo'qotadi
```

### 3.8 Well-known portlar jadvali

```
20/21   FTP (data/control)
22      SSH
25      SMTP
53      DNS
80      HTTP
110     POP3
143     IMAP
443     HTTPS
465/587 SMTP (SSL/TLS)
993     IMAPS
995     POP3S
1433    SQL Server
5432    PostgreSQL
5672    RabbitMQ (AMQP)
6379    Redis
6672    RabbitMQ (cluster)
15672   RabbitMQ Management UI
9000    Minio API
9001    Minio Console
```

### 3.9 Socket — C# da NetworkStream

```csharp
using var client = new TcpClient();
await client.ConnectAsync("example.com", 80);

using NetworkStream stream = client.GetStream();
var request = Encoding.ASCII.GetBytes("GET / HTTP/1.1\r\nHost: example.com\r\n\r\n");
await stream.WriteAsync(request);

var buffer = new byte[4096];
int bytesRead = await stream.ReadAsync(buffer);
Console.WriteLine(Encoding.ASCII.GetString(buffer, 0, bytesRead));
```

`Socket` — eng past darajadagi tarmoq abstraksiyasi; `TcpClient`/
`NetworkStream` — bu ustidagi qulayroq wrapper.

### 3.10 0.0.0.0 vs 127.0.0.1 vs localhost

```
127.0.0.1 — Loopback IP, faqat SHU mashinaning ICHIDAN
localhost — 127.0.0.1 (yoki ::1) ga hal qilinadigan HOSTNAME
0.0.0.0   — server BOG'LANISHI uchun "barcha interfeyslar" — kelayotgan
            so'rovlarni TASHQI tarmoqdan HAM qabul qilish uchun ishlatiladi
```

```csharp
// Kestrel — Docker konteynerda 0.0.0.0 ga bog'lash SHART
// (aks holda tashqi host konteyner ichidagi serverga ulana olmaydi)
builder.WebHost.UseUrls("http://0.0.0.0:5000");
```

## 4. Kod — diagnostika misollari

```csharp
// DNS lookup
var addresses = await Dns.GetHostAddressesAsync("api.example.com");

// Ping
using var ping = new Ping();
var reply = await ping.SendPingAsync("google.com", 3000);
Console.WriteLine($"{reply.Status}, {reply.RoundtripTime}ms");

// Port ochiqligini tekshirish
using var tcpClient = new TcpClient();
try
{
    await tcpClient.ConnectAsync("db-server", 5432);
    Console.WriteLine("Port ochiq");
}
catch (SocketException)
{
    Console.WriteLine("Port yopiq yoki server javob bermayapti");
}
```

## 5. Qachon ishlatish kerak?

| Vaziyat | Yechim |
|---|---|
| Ishonchli ma'lumot uzatish (API, DB) | TCP |
| Tezlik muhim, ozgina yo'qotish OK | UDP |
| Docker konteynerlar orasida aloqa | Compose network, service nomi orqali DNS |
| Serverni tashqi tarmoqqa ochish | `0.0.0.0` ga bind qilish |
| Faqat local test | `127.0.0.1`/`localhost` |

## 6. Muhim nuqtalar

- Docker'da konteynerlar bir-birini **service nomi** orqali topadi
  (Compose ichki DNS orqali) — `localhost` konteyner ICHIDAGI o'zini
  bildiradi, boshqa konteynerni EMAS.
- Firewall qoidalari — port ochiq bo'lsa ham, firewall bloklashi
  mumkin (bu holatda "timeout", "connection refused" emas).
- HTTP/3 — hali hamma joyda qo'llab-quvvatlanmaydi, lekin tez o'sib
  bormoqda (CDN'lar, yirik platformalar).

## 7. Imtihon savollari

1. TCP va UDP orasidagi asosiy farqlarni ayting va har biriga real
   ishlatilish holatini keltiring.
2. TCP 3-way handshake bosqichlarini tartib bilan tushuntiring.
3. DNS lookup jarayonini boshidan oxirigacha tushuntiring.
4. NAT nima muammoni hal qiladi?
5. `192.168.1.0/24` CIDR yozuvi nimani anglatadi?
6. `0.0.0.0` va `127.0.0.1` orasidagi farqni Docker konteyner
   kontekstida tushuntiring.
7. HTTP/2 ning HTTP/1.1'dan asosiy ustunligi nima?
