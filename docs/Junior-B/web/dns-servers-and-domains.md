# DNS Servers and Domains — Junior B

## 1. What (Nima?)

**DNS (Domain Name System)** — INTERNETNING **"TELEFON
KITOBI"** — U, INSON UCHUN OSON ESLAB QOLINADIGAN **DOMEN
NOMLARINI** (masalan `google.com`), KOMPYUTERLAR ULANISHDA
ISHLATADIGAN **IP MANZILLARGA** (masalan `142.250.187.14`)
"TARJIMA QILUVCHI", TAQSIMLANGAN (distributed), IYERARXIK
NOMLASH TIZIMI. **Domain (domen)** — BU TIZIMDAGI, INSON O'QIY
OLADIGAN, "MANZIL" YOZUVI.

## 2. Real hayot analogiyasi

**DNS — TELEFON SPRAVOCHNIGI (kontaktlar ro'yxati).** Siz,
DO'STINGIZGA QO'NG'IROQ QILMOQCHI BO'LGANINGIZDA, UNING
**RAQAMINI (IP manzil) YODLAB YURMAYSIZ** — TELEFONINGIZDAGI
KONTAKT RO'YXATIDA, "Ali" (domen nomi) DEB QIDIRASIZ, VA
TELEFON, O'ZI, TEGISHLI RAQAMNI (IP manzil) TOPIB, QO'NG'IROQ
QILADI. DNS — XUDDI SHUNDAY, `google.com` DEGAN "ISM"NI,
BROWSER UCHUN, HAQIQIY "RAQAM" (IP manzil)GA AYLANTIRADI.

## 3. Why (Nega kerak?)

Kompyuterlar, TARMOQDA, BIR-BIRI BILAN, **FAQAT IP MANZILLAR**
(masalan `142.250.187.14`) ORQALI GAPLASHADI — LEKIN, BU
RAQAMLARNI, **INSON UCHUN YODLAB QOLISH — DEYARLI IMKONSIZ**
(minglab SAYT UCHUN, MINGLAB RAQAM). DNS — BU MUAMMONI,
"ODAM UCHUN NOM, KOMPYUTER UCHUN RAQAM" DEGAN, IKKI TOMONLAMA
QULAYLIKNI TA'MINLASH ORQALI YECHADI. Bundan TASHQARI, DNS —
SERVERNING IP MANZILI O'ZGARGANDA HAM (masalan, XIZMAT KO'RSA-
TUVCHINI ALMASHTIRISHDA), FOYDALANUVCHI, DOMEN NOMINI
O'ZGARTIRMASDAN, YANGI SERVERGA "AVTOMATIK" YO'NALTIRILADI.

## 4. Internals (Ichki mexanizm)

### DNS Resolution — QADAM-BAQADAM JARAYON

```
Browser'da "google.com" YOZILGANDA, quyidagi ZANJIR ISHGA
TUSHADI:

1. Browser Cache — Avval, BROWSER, O'ZINING XOTIRASIDA, BU
   DOMEN UCHUN, ALLAQACHON SAQLANGAN IP BOR-YO'QLIGINI
   TEKSHIRADI (bor bo'lsa — DARHOL ISHLATADI, QOLGAN
   QADAMLAR O'TKAZIB YUBORILADI).

2. OS Cache — Agar Browser'da yo'q bo'lsa, OPERATSION TIZIM
   (Windows/Linux) O'ZINING DNS CACHE'INI TEKSHIRADI.

3. Recursive Resolver (ISP yoki 8.8.8.8 kabi) — Agar HALI
   HAM TOPILMASA, SO'ROV, INTERNET PROVAYDERI (ISP) YOKI
   PUBLIC DNS (Google 8.8.8.8, Cloudflare 1.1.1.1) SERVERIGA
   YUBORILADI — bu SERVER, "REKURSIV" RAVISHDA, KEYINGI
   QADAMLARNI, FOYDALANUVCHI O'RNIGA, BAJARADI.

4. Root DNS Server — Recursive Resolver, AVVAL, ROOT (ildiz)
   SERVERGA MUROJAAT QILADI — U, "com" DOMENLAR UCHUN, QAYSI
   SERVERGA MUROJAAT QILISH KERAKLIGINI (TLD server manzilini)
   AYTADI.

5. TLD (Top-Level Domain) Server — ".com" SERVERI — "google.
   com" UCHUN, QAYSI AUTHORITATIVE (rasmiy) SERVERGA MUROJAAT
   QILISH KERAKLIGINI AYTADI.

6. Authoritative Nameserver — "google.com" NING ASL, RASMIY
   DNS SERVERI — HAQIQIY IP MANZILNI (masalan
   142.250.187.14) QAYTARADI.

7. Natija, ZANJIR BO'YLAB, TESKARI YO'NALISHDA, HAR
   BOSQICHDA CACHE'GA SAQLANIB, BROWSER'GA QAYTARILADI.
```

### DNS Record TURLARI — A, AAAA, CNAME, MX, TXT, NS

```
A Record     — Domen nomini, IPv4 manzilga bog'laydi
               (masalan google.com → 142.250.187.14).

AAAA Record  — Domen nomini, IPv6 manzilga bog'laydi.

CNAME Record — Bir domen nomini, BOSHQA DOMEN NOMIGA
               "ALIAS" (taxallus) sifatida bog'laydi
               (masalan www.mysite.com → mysite.com).

MX Record    — Domenga tegishli, EMAIL QABUL QILUVCHI
               SERVERLARNI belgilaydi (email marshrutlash
               uchun).

TXT Record   — Erkin, matn ko'rinishidagi ma'lumot (ko'pincha,
               DOMEN EGALIGINI TASDIQLASH, YOKI SPF/DKIM kabi
               email xavfsizlik sozlamalari uchun).

NS Record    — Domen uchun, QAYSI AUTHORITATIVE NAMESERVER
               (rasmiy DNS server) JAVOBGAR EKANINI ko'rsatadi.
```

### TTL (Time To Live) — CACHE MUDDATI

```
HAR DNS RECORD — TTL QIYMATIGA EGA (masalan 3600 sekund =
1 soat) — bu, RESOLVER'LARGA (browser, OS, ISP), "BU
YOZUVNI, ANIQ SHU MUDDAT DAVOMIDA, QAYTA SO'ROVSIZ,
CACHE'DAN ISHLATISH MUMKIN" DEB AYTADI. TTL — TEZKORLIK
(katta TTL — kamroq DNS so'rov, tezroq) va MOSLASHUVCHANLIK
(kichik TTL — server IP o'zgarganda, tezroq TARQALADI)
ORASIDAGI TRADEOFF.
```

## 5. Code (Amaliy kod)

```bash
# nslookup — domen uchun DNS yozuvlarini so'rash
nslookup google.com
nslookup -type=MX google.com  # Email serverlarini ko'rish
nslookup -type=TXT google.com # TXT yozuvlarni ko'rish

# dig — batafsilroq DNS diagnostikasi (Linux/macOS)
dig google.com A
dig google.com +trace # Butun DNS resolution zanjirini ko'rsatadi (root'dan boshlab)
```

```csharp
// C# — DNS so'rovlarini dasturiy ravishda bajarish
using System.Net;

var addresses = await Dns.GetHostAddressesAsync("google.com");
foreach (var address in addresses)
{
    Console.WriteLine($"IP: {address}");
}

// Reverse DNS — IP manzildan domen nomini topish
var hostEntry = await Dns.GetHostEntryAsync("142.250.187.14");
Console.WriteLine($"Hostname: {hostEntry.HostName}");
```

```
# BFF/microservice arxitekturada — Docker Compose ichida, DNS
# service-discovery vazifasini bajaradi:
# "http://auth-service:5001" — "auth-service" — Docker'ning
# ICHKI DNS TIZIMI orqali, tegishli konteynerning ICHKI IP
# manziliga AVTOMATIK hal qilinadi (resolve qilinadi).
```

## 6. Keng tarqalgan xatolar / noto'g'ri tushunchalar

```
❌ "DNS — FAQAT DOMEN NOMINI IP MANZILGA (A Record) AYLAN-
   TIRADI" — YO'Q! DNS — BUNDAN TASHQARI, EMAIL MARSHRUT-
   LASH (MX), DOMEN ALIASLARI (CNAME), XAVFSIZLIK
   TASDIQLASH (TXT — SPF/DKIM) KABI, KO'PLAB BOSHQA
   FUNKSIYALARNI HAM BAJARADI.

❌ "DNS o'zgarishi (masalan yangi A Record), DARHOL, BUTUN
   DUNYODA KO'RINADI" — YO'Q! TTL SABABLI, ESKI QIYMAT,
   TURLI JOYLARDAGI CACHE'LARDA (browser, ISP), TTL MUDDATI
   TUGAGUNCHA, HALI HAM "SAQLANIB QOLISHI" MUMKIN — BU JARAYON
   "DNS PROPAGATION" (tarqalish) DEB ATALADI, VA SOATLAB
   DAVOM ETISHI MUMKIN.

❌ "CNAME va A Record — BIR XIL, ULARNI ALMASHTIRIB
   ISHLATSA BO'LADI" — YO'Q! A Record — TO'G'RIDAN-TO'G'RI,
   IP MANZILGA ISHORA QILADI. CNAME — BOSHQA DOMEN NOMIGA
   "ALIAS" SIFATIDA ISHORA QILADI (keyin, O'SHA DOMEN, O'Z
   NAVBATIDA, A RECORD ORQALI, IP'GA HAL QILINADI) — CNAME'NI,
   ROOT DOMENGA (masalan `example.com`, "www" siz) QO'LLASH —
   ODATDA TEXNIK CHEKLOVLARGA UCHRAYDI.

❌ "Public DNS (8.8.8.8, 1.1.1.1) ishlatish — SHUNCHAKI,
   ODDIY TANLOV, HECH QANDAY AMALIY FARQ BERMAYDI" — 
   AMALDA, PUBLIC DNS PROVIDERLAR — KO'PINCHA, ISP'NING
   O'Z DNS SERVERIGA NISBATAN, TEZROQ JAVOB VAQTIGA VA
   YAXSHIROQ XAVFSIZLIK/MAXFIYLIK SIYOSATIGA EGA BO'LISHI
   MUMKIN.
```

## 7. Exam (Interview savollari)

**1. DNS Resolution jarayonining ASOSIY QADAMLARINI, QISQACHA
SANANG.**
Browser Cache → OS Cache → Recursive Resolver (ISP/Public
DNS) → Root DNS Server → TLD Server → Authoritative
Nameserver — VA NATIJA, ZANJIR BO'YLAB, HAR BOSQICHDA CACHE'GA
SAQLANIB, QAYTARILADI.

**2. A Record va CNAME Record orasidagi FARQ nima?**
A Record — DOMEN NOMINI, TO'G'RIDAN-TO'G'RI, IPv4 MANZILGA
BOG'LAYDI. CNAME Record — DOMEN NOMINI, BOSHQA BIR DOMEN
NOMIGA, "ALIAS" SIFATIDA BOG'LAYDI — U DOMEN, O'Z NAVBATIDA,
YANA BIR DNS QIDIRUVI ORQALI, HAQIQIY IP MANZILGA HAL
QILINADI.

**3. TTL (Time To Live) nima, va u QANDAY TRADEOFF'NI
BOSHQARADI?**
TTL — DNS YOZUVINING, CACHE'DA, QANCHA VAQT (masalan 3600
sekund) "AMAL QILISHI" KERAKLIGINI BELGILAYDI. TRADEOFF: KATTA
TTL — KAMROQ DNS SO'ROV (tezroq), LEKIN, SERVER IP O'ZGARSA,
YANGI QIYMAT SEKINROQ "TARQALADI" (propagate). KICHIK TTL —
TESKARISI.

**4. MX Record NIMA VAZIFANI BAJARADI?**
MX (Mail Exchange) Record — DOMENGA TEGISHLI, EMAIL QABUL
QILUVCHI SERVERLARNI BELGILAYDI — masalan, `@company.com`
MANZILIGA YUBORILGAN EMAIL, QAYSI SERVERGA YETKAZILISHI
KERAKLIGINI, DNS'DAGI MX RECORD ORQALI ANIQLAYDI.

**5. Nima uchun DNS PROPAGATION (yangi DNS o'zgarishining
butun dunyoga tarqalishi), DARHOL EMAS, SOATLAB DAVOM
ETISHI MUMKIN?**
Chunki, DNS — TAQSIMLANGAN, KO'P DARAJALI CACHE TIZIMIGA
EGA (browser, OS, ISP resolver) — HAR BIR CACHE DARAJASI,
ESKI QIYMATNI, TEGISHLI TTL MUDDATI TUGAGUNCHA, "SAQLAB
QOLISHI" MUMKIN — YANGI QIYMAT, FAQAT, HAR JOYDAGI CACHE,
TTL BO'YICHA "ESKIRGANDAN" KEYIN, QAYTA SO'RALIB, YANGILANADI.
