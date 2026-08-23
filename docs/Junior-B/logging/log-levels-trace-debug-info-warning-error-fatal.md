# Log Levellar (Trace, Debug, Info, Warning, Error, Fatal) — Junior B

## 1. What (Nima?)

**Log Level** (jurnal darajasi) — HAR BIR LOG YOZUVINING
**JIDDIYLIK DARAJASINI** BELGILOVCHI KLASSIFIKATSIYA. .NET'da,
`Microsoft.Extensions.Logging` — 6 TA ASOSIY DARAJANI TAQDIM
ETADI (ENG PASTDAN ENG YUQORIGA): **Trace → Debug →
Information → Warning → Error → Critical**. Har DARAJA — LOG
YOZUVINING "QANCHALIK MUHIM/JIDDIY" EKANINI, VA UNI **QAYSI
MUHITDA (dev/production) YOZISH KERAKLIGINI** ANIQLAYDI.

## 2. Real hayot analogiyasi

**Log Level — SHIFOXONADAGI SHOSHILINCH YORDAM TRIAGE
TIZIMI.** Kasalxonaga KELGAN HAR BIR BEMOR — DARAJALASHTIRIB
BELGILANADI: "OZ ANIQ MA'LUMOT KERAK" (Trace — masalan tana
harorati kunlik yozuvi), "ODATIY TEKSHIRUV" (Debug — muntazam
ko'rik), "NORMAL HOLAT" (Information — sog'lom bemor), "OGOH-
LANTIRISH" (Warning — bosim biroz yuqori, kuzatish kerak),
"JIDDIY MUAMMO" (Error — operatsiya kerak), "HAYOTGA XAVF"
(Critical/Fatal — REANIMATSIYA, DARHOL ARALASHUV SHART). HAR
DARAJA — TURLI DARAJADA E'TIBOR VA TEZKORLIKNI TALAB QILADI.

## 3. Why (Nega kerak?)

Agar BARCHA LOG YOZUVLARI (mayda tafsilotlardan tortib,
KRITIK XATOLARGACHA) **BIR XIL DARAJADA** SAQLANSA — PRODUCTION
LOG FAYLLARI, **KUNIGA GIGABAYTLAB "SHOVQIN"** BILAN TO'LIB
KETADI, VA HAQIQIY, JIDDIY MUAMMONI (Error/Critical) TOPISH —
"IGNANI PICHAN UYIDAN QIDIRISH" KABI QIYINLASHADI. Log Level —
**FILTRLASH IMKONINI BERADI**: DEV MUHITIDA — HAMMASI (Trace
DAN)Ko'RSATILADI (chuqur DEBUG uchun), PRODUCTION'DA — FAQAT
Warning'DAN YUQORI (shovqinni kamaytirish, MUHIM narsalarni
ajratib olish uchun).

## 4. Internals (Ichki mexanizm)

### `LogLevel` enum — RAQAMLI QIYMATLAR VA FILTRLASH MANTIG'I

```csharp
public enum LogLevel
{
    Trace = 0,
    Debug = 1,
    Information = 2,
    Warning = 3,
    Error = 4,
    Critical = 5,
    None = 6 // Hech narsa log qilinmaydi
}
```

```
LOGGER'GA "MinimumLevel = Warning" DEB SOZLANSA — FAQAT
RAQAMLI QIYMATI 3 VA UNDAN YUQORI (Warning, Error, Critical)
BO'LGAN YOZUVLAR — FAKTIK JURNALGA (Console/File/DB) YOZILADI.
Trace/Debug/Information (0-2) — SHUNCHAKI E'TIBORSIZ
QOLDIRILADI (HATTO LOG CHAQIRUVI KOD ICHIDA MAVJUD BO'LSA HAM
— FAQAT FILTRLASH DARAJASIDA "O'TKAZIB YUBORILADI").
```

### Har DARAJANING AMALIY MA'NOSI

```
Trace       — ENG MAYDA TAFSILOT (masalan "metod X chaqirildi,
              parametr Y=5") — ODATDA FAQAT KESKIN DEBUG
              QILINAYOTGANDA YOQILADI, PRODUCTION'DA DEYARLI
              HECH QACHON YOQILMAYDI (JUDA KO'P HAJM).

Debug       — DASTURCHIGA FOYDALI, LEKIN ISHLAB CHIQARISHDA
              KERAKSIZ MA'LUMOT (masalan "SQL so'rov: SELECT *
              FROM...") — ODATDA FAQAT DEV/STAGING MUHITIDA
              YOQILADI.

Information — ODATIY, KUTILGAN "ILOVA OQIMI" HAQIDA MA'LUMOT
              (masalan "Foydalanuvchi tizimga kirdi", "Buyurtma
              yaratildi") — PRODUCTION'DA ODATDA YOQILGAN.

Warning     — KUTILMAGAN, LEKIN ILOVANI TO'XTATMAYDIGAN HOLAT
              (masalan "API javob berish vaqti 3 soniyadan
              oshdi", "Deprecated metod ishlatildi").

Error       — OPERATSIYA MUVAFFAQIYATSIZ TUGADI (masalan
              "To'lov amalga oshmadi"), LEKIN ILOVA O'ZI
              ISHLASHDA DAVOM ETADI (foydalanuvchiga xatolik
              qaytariladi, dastur qulamaydi).

Critical/   — TIZIM DARAJASIDAGI, DARHOL ARALASHUV TALAB
Fatal         QILADIGAN JIDDIY MUAMMO (masalan "DB'ga
              ULANIB BO'LMAYAPTI", "Diskda joy qolmadi") —
              KO'PINCHA, BUTUN ILOVA YOKI XIZMAT ISHLAY
              OLMAY QOLADI.
```

### Structured Logging — MATN O'RNIGA, MA'LUMOT sifatida LOG YOZISH

```csharp
_logger.LogInformation("Foydalanuvchi {UserId} tizimga kirdi", userId);
```

```
BU YERDA "{UserId}" — ODDIY STRING INTERPOLATION EMAS!
Microsoft.Extensions.Logging — BU YOZUVNI, ALOHIDA "TEMPLATE"
(shablon) VA "PARAMETRLAR" (userId) sifatida SAQLAYDI — LOG
PROVIDER (masalan Seq, Elasticsearch) — KEYINCHALIK, "UserId
= 5 BO'LGAN BARCHA LOGLARNI TOP" KABI STRUKTURALI QIDIRUVNI,
MATN ICHIDAN QIDIRISHGA NISBATAN, ANCHA TEZROQ VA ANIQROQ
AMALGA OSHIRISHI MUMKIN.
```

## 5. Code (Amaliy kod)

```csharp
public class OrderService
{
    private readonly ILogger<OrderService> _logger;

    public OrderService(ILogger<OrderService> logger) => _logger = logger;

    public async Task<Order> CreateOrderAsync(CreateOrderDto dto)
    {
        _logger.LogTrace("CreateOrderAsync chaqirildi, dto: {@Dto}", dto);
        _logger.LogDebug("Mijoz {CustomerId} uchun buyurtma yaratilmoqda", dto.CustomerId);

        try
        {
            var order = new Order { CustomerId = dto.CustomerId, Total = dto.Total };
            // ... saqlash logikasi

            _logger.LogInformation("Buyurtma {OrderId} muvaffaqiyatli yaratildi", order.Id);

            if (dto.Total > 10_000_000)
                _logger.LogWarning("Katta summadagi buyurtma: {OrderId}, summa: {Total}", order.Id, dto.Total);

            return order;
        }
        catch (DbUpdateException ex)
        {
            _logger.LogError(ex, "Buyurtma yaratishda DB xatoligi, mijoz: {CustomerId}", dto.CustomerId);
            throw;
        }
        catch (Exception ex)
        {
            _logger.LogCritical(ex, "Kutilmagan, jiddiy xatolik buyurtma yaratishda");
            throw;
        }
    }
}
```

```json
// appsettings.json — muhitga qarab log darajasini sozlash
{
  "Logging": {
    "LogLevel": {
      "Default": "Information",
      "Microsoft.EntityFrameworkCore": "Warning"
    }
  }
}
```

```json
// appsettings.Development.json — dev muhitida ko'proq tafsilot
{
  "Logging": {
    "LogLevel": {
      "Default": "Debug",
      "Microsoft.EntityFrameworkCore": "Information"
    }
  }
}
```

## 6. Keng tarqalgan xatolar / noto'g'ri tushunchalar

```
❌ "Production'da HAM, Trace/Debug darajasini YOQIB QO'YISH —
   ZARARSIZ, KO'PROQ MA'LUMOT — YAXSHI" — YO'Q! Bu, LOG
   HAJMINI KATASTROFIK OSHIRADI (disk to'lib ketishi, log
   provayder xarajatlarining oshishi), VA HAQIQIY MUAMMOLARNI
   "SHOVQIN" ICHIDA YASHIRADI.

❌ "String interpolation (`$"Foydalanuvchi {userId}"`) va
   Structured Logging (`"Foydalanuvchi {UserId}", userId`) —
   BIR XIL NARSA" — YO'Q! String interpolation — LOG
   YOZILISHIDAN OLDIN, MATNGA "QOTIB QOLADI" — Log provayder,
   `userId` QIYMATINI ALOHIDA MAYDON SIFATIDA QIDIRA OLMAYDI.
   Structured Logging — PARAMETRLARNI ALOHIDA SAQLAYDI.

❌ "Error va Critical — BIR XIL DARAJA, FARQ YO'Q" — YO'Q!
   Error — OPERATSIYA MUVAFFAQIYATSIZ, LEKIN ILOVA ISHLASHDA
   DAVOM ETADI. Critical — TIZIM DARAJASIDAGI, KO'PINCHA
   BUTUN XIZMATNI ISHLATMAY QO'YADIGAN MUAMMO.

❌ "LogError(ex.Message)" — EXCEPTION OBYEKTINI TO'G'RI
   LOG QILISH — Faqat `ex.Message`ni yozish, STACK TRACE'NI
   YO'QOTADI — TO'G'RISI: `_logger.LogError(ex, "xabar")` —
   EXCEPTION OBYEKTINI ALOHIDA PARAMETR SIFATIDA UZATISH,
   Logger — STACK TRACE'NI TO'LIQ SAQLAYDI.
```

## 7. Exam (Interview savollari)

**1. .NET'dagi 6 ta LogLevel'ni, ENG PASTDAN ENG YUQORIGA
QARAB SANANG, VA HAR BIRINING QISQA MA'NOSINI TUSHUNTIRING.**
Trace (eng mayda tafsilot) → Debug (dasturchi uchun foydali
diagnostika) → Information (odatiy ilova oqimi) → Warning
(kutilmagan, lekin ilovani to'xtatmaydigan holat) → Error
(operatsiya muvaffaqiyatsiz, ilova davom etadi) → Critical
(tizim darajasidagi, darhol aralashuv talab qiluvchi muammo).

**2. Structured Logging (`LogInformation("User {UserId}",
userId)`) va oddiy string interpolation orasidagi FARQ nima?**
Structured Logging — PARAMETRNI (UserId) ALOHIDA MAYDON
SIFATIDA SAQLAYDI, LOG PROVIDER (Seq, Elasticsearch) UNI
STRUKTURALI QIDIRISH/FILTRLASH UCHUN ISHLATA OLADI. String
interpolation — QIYMATNI, LOG YOZILISHIDAN OLDIN, MATNGA
"QOTIB QOLDIRADI" — KEYINCHALIK STRUKTURALI QIDIRISH IMKONI
YO'Q.

**3. Production muhitida, ODATDA QAYSI MINIMAL LOG LEVEL
TAVSIYA ETILADI, VA NIMA UCHUN?**
Odatda Information yoki Warning — Trace/Debug — JUDA KO'P
HAJM VA "SHOVQIN" YARATADI, DISK/XARAJAT MUAMMOSIGA OLIB
KELISHI VA HAQIQIY MUAMMOLARNI TOPISHNI QIYINLASHTIRISHI
MUMKIN.

**4. `_logger.LogError(ex, "xabar")` va `_logger.LogError
(ex.Message)` orasidagi FARQ nima, va NIMA UCHUN BIRINCHISI
TO'G'RI USUL?**
`LogError(ex, "xabar")` — EXCEPTION OBYEKTINI ALOHIDA
PARAMETR SIFATIDA UZATADI — Logger, STACK TRACE, INNER
EXCEPTION KABI TO'LIQ MA'LUMOTNI SAQLAYDI. `LogError
(ex.Message)` — FAQAT XATOLIK MATNINI SAQLAYDI, STACK
TRACE'NI YO'QOTADI — MUAMMONI DIAGNOSTIKA QILISHNI
QIYINLASHTIRADI.

**5. appsettings.json'da "Microsoft.EntityFrameworkCore":
"Warning" KABI, ALOHIDA NAMESPACE UCHUN LOG LEVEL BELGILASH
NIMA UCHUN FOYDALI?**
Bu, TURLI QISM (kutubxona/modul)LAR UCHUN, ALOHIDA-ALOHIDA
LOG DARAJASI SOZLASH imkonini beradi — masalan, EF Core'ning
"chiqarilgan SQL so'rovlari" (Information darajasida, juda
ko'p) — Warning'ga cheklab, LEKIN O'Z ILOVA KODINGIZ UCHUN
Information darajasini YOQIB QOLDIRISH mumkin — bu, "SHOVQIN"NI
KAMAYTIRIB, MUHIM LOGLARNI AJRATIB OLISHGA YORDAM BERADI.
