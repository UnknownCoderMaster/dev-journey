# Column Collations — Junior B

## 1. What (Nima?)

**Collation (kollatsiya)** — MATN USTUNLARIDA (VARCHAR/TEXT),
**SOLISHTIRISH VA SARALASH QOIDALARINI** (harflar tartibi, katta-
kichik harf sezgirligi, milliy alifbo qoidalari) BELGILOVCHI
SOZLAMA. U, `ORDER BY`, `=`, `<`, `LIKE` KABI OPERATSIYALARDA,
MATNLAR **QANDAY TARTIBLANISHI VA SOLISHTIRILISHI** kerakligini
DB DVIGATELIGA "AYTIB BERADI".

## 2. Real hayot analogiyasi

**Collation — LUG'ATDA SO'ZLARNI TARTIBLASH QOIDASI.** O'ZBEK
LUG'ATIDA "SH" — ALOHIDA HARF SIFATIDA, "S" VA "H"DAN KEYIN
ALOHIDA JOYDA TURADI. ANGLIYA LUG'ATIDA ESA — "SH" SHUNCHAKI
"S"+"H" KETMA-KETLIGI, ALOHIDA HARF EMAS. AGAR SIZ O'ZBEK
SO'ZLARINI ANGLIYA QOIDASI BILAN TARTIBLASANGIZ — NOTO'G'RI,
KUTILMAGAN TARTIB OLASIZ. Collation — DB'GA "QAYSI LUG'AT
QOIDASINI ISHLATISH KERAK" DEB AYTADI.

## 3. Why (Nega kerak?)

Turli TILLAR — TURLICHA ALIFBO TARTIBIGA EGA (masalan, o'zbek
"o'" harfi, rus "ё" harfi). Agar COLLATION NOTO'G'RI TANLANSA —
`ORDER BY full_name` — FOYDALANUVCHI KUTGANDAN BUTUNLAY BOSHQA
TARTIBDA NATIJA BERISHI MUMKIN. Bundan TASHQARI, COLLATION —
**CASE SENSITIVITY**NI HAM BOSHQARADI: `"Ali" = "ali"` — BA'ZI
COLLATION'LARDA TRUE, BOSHQALARIDA FALSE.

**PostgreSQL nima uchun COLLATION'NI USTUN DARAJASIDA
QO'LLAB-QUVVATLAYDI:** REAL LOYIHALARDA, BIR JADVALDA HAM
"case-sensitive" (masalan parol HASH'I) HAM "case-insensitive"
(masalan email) USTUNLAR BO'LISHI MUMKIN — COLLATION'NI
USTUN DARAJASIDA SOZLASH, BUNGA IMKON BERADI.

## 4. Internals (Ichki mexanizm)

### PostgreSQL'da Collation QANDAY ISHLAYDI — libc/ICU

```
PostgreSQL — COLLATION QOIDALARINI, ODATDA OPERATSION TIZIM
KUTUBXONASI (libc) YOKI ICU (International Components for
Unicode — XALQARO STANDART KUTUBXONA) ORQALI OLADI. HAR
COLLATION — "LOCALE" (masalan "en_US", "uz_UZ", "C") BILAN
BOG'LANGAN — LOCALE, TIL VA MINTAQAGA XOS SOLISHTIRISH
QOIDALARINI BELGILAYDI.

"C" COLLATION — ENG "ODDIY": FAQAT BYTE QIYMATLARI BO'YICHA
SOLISHTIRADI (ASCII TARTIBI) — TIL QOIDALARIGA E'TIBOR
BERMAYDI, LEKIN ENG TEZKOR (chunki HECH QANDAY MURAKKAB LOCALE
MANTIQ ISHLATILMAYDI).
```

### Collation va INDEX — B-Tree TARTIBI

```
INDEKS (B-Tree) — MA'LUMOTLARNI TARTIBLANGAN HOLDA SAQLAYDI.
INDEKS YARATILGANDA, USTUNNING COLLATION'I "QOTIB QOLADI" —
INDEKS SHU COLLATION BO'YICHA QURILADI. Agar KEYINCHALIK SO'ROV
BOSHQA COLLATION BILAN YOZILSA — POSTGRESQL, INDEKSDAN
FOYDALANA OLMAY QOLISHI MUMKIN (INDEX SCAN O'RNIGA, SEKINROQ
SEQUENTIAL SCAN'GA "TUSHIB QOLADI").
```

### Case-Insensitive qidiruv — COLLATION vs LOWER()

```sql
-- Variant 1: LOWER() funksiyasi (indeks uchun maxsus FUNCTIONAL INDEX kerak)
SELECT * FROM users WHERE LOWER(email) = LOWER('Ali@Mail.com');
CREATE INDEX idx_users_email_lower ON users (LOWER(email));

-- Variant 2: Case-insensitive COLLATION (PostgreSQL 12+, ICU orqali)
CREATE COLLATION case_insensitive (provider = icu, locale = 'und-u-ks-level2', deterministic = false);
ALTER TABLE users ALTER COLLATE case_insensitive;
```

```
ICU COLLATION — "DETERMINISTIK BO'LMAGAN" (deterministic=false)
COLLATION YARATISHGA IMKON BERADI — "Ali" va "ali" — BIR XIL
DEB HISOBLANADI, LEKIN BAYT DARAJASIDA FARQLI QOLADI (original
qiymat SAQLANIB QOLADI, FAQAT SOLISHTIRISH QOIDASI O'ZGARADI).
```

## 5. Code (Amaliy kod)

```sql
-- Ustun darajasida COLLATION belgilash
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) COLLATE "C",         -- Tez, byte-based (masalan API key kabi)
    full_name VARCHAR(100) COLLATE "und-x-icu" -- Tabiiy til tartibida saralash uchun
);

-- Saralashda COLLATE'ni SO'ROV DARAJASIDA o'zgartirish
SELECT full_name FROM users ORDER BY full_name COLLATE "en_US";

-- Mavjud DB'ning default collation'ini ko'rish
SHOW lc_collate;
```

```csharp
// EF Core — ustun darajasida collation belgilash (Fluent API)
public class AppDbContext : DbContext
{
    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.Entity<User>()
            .Property(u => u.Username)
            .UseCollation("C"); // Tez, byte-based solishtirish

        modelBuilder.Entity<User>()
            .Property(u => u.FullName)
            .UseCollation("und-x-icu"); // Tabiiy tartib

        // Butun DB uchun default collation
        modelBuilder.UseCollation("en_US");
    }
}
```

```csharp
// C# tomonda case-insensitive solishtirish — DB collation'iga ISHONMASLIK
var user = await dbContext.Users
    .FirstOrDefaultAsync(u => u.Email.ToLower() == email.ToLower());
// ⚠️ Bu — SQL'da LOWER(email) = LOWER(@email) ga tarjima qilinadi —
// agar email ustunida FUNCTIONAL INDEX bo'lmasa, SEKIN ishlaydi!
```

## 6. Keng tarqalgan xatolar / noto'g'ri tushunchalar

```
❌ "Collation — faqat SARALASHGA (ORDER BY) ta'sir qiladi" — YO'Q!
   Collation — SOLISHTIRISHGA (=, <, >, LIKE) HAM TA'SIR QILADI —
   MASALAN, case-sensitivity ("Ali" = "ali"?) — COLLATION
   ORQALI BOSHQARILADI.

❌ "Bitta DB'da BARCHA USTUNLAR bir xil COLLATION'GA EGA BO'LISHI
   SHART" — YO'Q, PostgreSQL — USTUN DARAJASIDA HAR XIL COLLATION
   BELGILASHGA RUXSAT BERADI (masalan, parol HASH — "C", ism —
   TABIIY TIL COLLATION).

❌ "COLLATION'NI JADVAL YARATILGANDAN KEYIN, INDEKSGA TA'SIR
   QILMASDAN, ERKIN O'ZGARTIRISH MUMKIN" — XAVFLI! COLLATION
   O'ZGARTIRILSA, MAVJUD INDEKSLAR "ESKIRGAN" (STALE) BO'LIB
   QOLISHI MUMKIN — REINDEX QILISH TALAB ETILADI.

❌ "LOWER(column) = LOWER(value)" — HAR DOIM TO'G'RI YECHIM" —
   BU, FUNCTIONAL INDEX (`CREATE INDEX ON table (LOWER(column))`)
   BO'LMASA — TO'LIQ JADVAL SKANERINI (Sequential Scan) KELTIRIB
   CHIQARADI — KATTA JADVALLARDA SEKIN.
```

## 7. Exam (Interview savollari)

**1. Collation nima, va u qanday OPERATSIYALARGA TA'SIR
QILADI?**
Collation — MATN USTUNLARIDA SOLISHTIRISH VA SARALASH
QOIDALARINI BELGILAYDI. U, `ORDER BY` (SARALASH TARTIBI), `=`/
`<`/`>` (SOLISHTIRISH, jumladan CASE SENSITIVITY), va `LIKE`
KABI OPERATSIYALARGA TA'SIR QILADI.

**2. "C" collation nima, va u NIMA UCHUN TEZROQ?**
"C" collation — FAQAT BYTE QIYMATLARI BO'YICHA (ASCII TARTIBI)
SOLISHTIRADI, TIL-SPECIFIK QOIDALARGA E'TIBOR BERMAYDI. U TEZROQ,
CHUNKI MURAKKAB LOCALE-BASED MANTIQ (turli til qoidalari)
ISHGA TUSHIRILMAYDI — TO'G'RIDAN-TO'G'RI BAYT SOLISHTIRISH.

**3. Collation INDEKSGA QANDAY TA'SIR QILADI?**
INDEKS (B-Tree) — MA'LUM BIR COLLATION BO'YICHA TARTIBLANGAN
HOLDA QURILADI. Agar SO'ROVDA BOSHQA COLLATION ISHLATILSA —
PostgreSQL INDEKSDAN FOYDALANA OLMASLIGI MUMKIN, natijada
SEKINROQ Sequential Scan ISHLATILADI.

**4. Case-insensitive qidiruvni AMALGA OSHIRISHNING IKKI
USULINI TUSHUNTIRING.**
(1) `LOWER(column) = LOWER(value)` + FUNCTIONAL INDEX
(`CREATE INDEX ON table (LOWER(column))`) — ESKI, KENG
TARQALGAN USUL. (2) ICU'ga ASOSLANGAN "deterministic=false"
CASE-INSENSITIVE COLLATION YARATISH (PostgreSQL 12+) — USTUNGA
TO'G'RIDAN-TO'G'RI QO'LLASH MUMKIN, QO'SHIMCHA FUNCTIONAL
INDEX TALAB QILMAYDI.

**5. Nima uchun BIR JADVALDA TURLI USTUNLAR TURLI COLLATION'GA
EGA BO'LISHI MANTIQAN TO'G'RI BO'LISHI MUMKIN?**
Masalan, `password_hash` USTUNI — ANIQ, BYTE-DARAJASIDA
SOLISHTIRISH TALAB QILADI ("C" collation TO'G'RI), `full_name`
USTUNI ESA — FOYDALANUVCHI UCHUN TABIIY, TIL QOIDALARIGA MOS
SARALASH TALAB QILADI (masalan "und-x-icu"). Har ikki holat HAM
— BITTA JADVALDA, TURLI MAQSADLAR uchun MANTIQIY.
