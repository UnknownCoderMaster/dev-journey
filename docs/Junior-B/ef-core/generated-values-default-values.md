# Generated Values, Default Values — Junior B

## 1. What (Nima?)

**Default Value** — USTUNGA QIYMAT BERILMAGANDA, DB TOMONIDAN
AVTOMATIK QO'YILADIGAN "STANDART" QIYMAT (masalan `created_at
DEFAULT now()`). **Generated Value** — DB TOMONIDAN, **BOSHQA
USTUNLAR ASOSIDA** YOKI **MAXSUS ALGORITM** BILAN AVTOMATIK
HISOBLAB CHIQARILADIGAN QIYMAT (masalan `SERIAL`, `IDENTITY`,
YOKI GENERATED COLUMN).

## 2. Real hayot analogiyasi

**Default Value — RESTORAN MENYUSIDAGI "STANDART GARNIR".**
Agar MIJOZ ALOHIDA GARNIR SO'RAMASA — OSHXONA AVTOMATIK
"STANDART" GARNIRNI (masalan, guruch) QO'SHADI. **Generated
Value — CHEKDAGI (check) AVTOMATIK HISOBLANGAN "JAMI SUMMA"**
— BU QIYMATNI SIZ QO'LDA KIRITMAYSIZ, U — BOSHQA QATORLAR
(taomlar narxi) ASOSIDA, AVTOMATIK HISOBLANADI.

## 3. Why (Nega kerak?)

Ba'zi QIYMATLAR (masalan `id`, `created_at`) — **HAR BIR
QATOR UCHUN, ILOVA KODIDA QO'LDA YOZISH — XATOGA MOYIL VA
TAKRORLANUVCHI**. DB DARAJASIDA DEFAULT/GENERATED belgilash —
BU MANTIQNI **BIR MARTA, MARKAZLASHTIRILGAN HOLDA** YOZISHGA
IMKON BERADI — QAYSI ILOVA (C# backend, admin panel, to'g'ridan
SQL skript) QATOR QO'SHMASIN, QOIDA BUZILMAYDI.

## 4. Internals (Ichki mexanizm)

### `DEFAULT` — QACHON QO'LLANILADI

```sql
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    status VARCHAR(20) NOT NULL DEFAULT 'pending'
);
```

```
DEFAULT — FAQAT USTUN INSERT SO'ROVIDA UMUMAN "TILGA
OLINMAGANDA" (yoki ANIQ DEFAULT DEB YOZILGANDA) ISHLAYDI.
Agar INSERT'da USTUNGA NULL ANIQ YUBORILSA — DEFAULT QIYMAT
QO'LLANILMAYDI, USTUN NULL BO'LIB QOLADI (agar NOT NULL
BO'LMASA).
```

### `GENERATED ALWAYS AS IDENTITY` vs `SERIAL`

```sql
-- SERIAL — eski, "syntactic sugar" usul (SEQUENCE + DEFAULT)
id SERIAL PRIMARY KEY;

-- GENERATED ALWAYS AS IDENTITY — SQL STANDARTIGA MOS, YANGI USUL (PostgreSQL 10+)
id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY;
```

```
SERIAL — ICHKARIDA, ALOHIDA SEQUENCE OBYEKTI YARATIB, USTUNGA
"DEFAULT nextval('sequence_nomi')" BIRIKTIRADI — BU, TEXNIK
JIHATDAN, ODDIY FOYDALANUVCHI HAM SHU USTUNGA QO'LDA ISTALGAN
QIYMAT YOZIB YUBORISHI MUMKINLIGINI ANGLATADI (masalan `INSERT
... VALUES (999, ...)`.

GENERATED ALWAYS AS IDENTITY — QATʼIYROQ: ODATDA QO'LDA
QIYMAT YOZISHGA YO'L QO'YMAYDI (agar OVERRIDING SYSTEM VALUE
ANIQ KO'RSATILMASA) — bu, ID'LARNING NAZORATSIZ O'ZGARISHINING
OLDINI OLADI.
```

### Computed/Generated COLUMN — BOSHQA USTUNLAR ASOSIDA

```sql
CREATE TABLE order_items (
    quantity INT NOT NULL,
    unit_price NUMERIC(10,2) NOT NULL,
    total_price NUMERIC(10,2) GENERATED ALWAYS AS (quantity * unit_price) STORED
);
```

```
GENERATED ALWAYS AS (...) STORED — QIYMATNI, HAR INSERT/UPDATE'DA
AVTOMATIK QAYTA HISOBLAB, DISKKA "STORED" (SAQLANGAN) HOLDA
YOZADI — SO'ROVDA QAYTA HISOBLASH SHART EMAS (indekslash ham
mumkin). Bu, docs/Junior-B/ef-core/computed-columns.md'da
BATAFSILROQ YORITILGAN.
```

### EF Core — `ValueGeneratedOnAdd` vs `HasDefaultValueSql`

```
EF Core'da, DEFAULT QIYMAT IKKI XIL YO'L BILAN AMALGA
OSHIRILISHI MUMKIN: (1) DB DARAJASIDA (`HasDefaultValueSql`) —
DB HAR DOIM QIYMATNI O'ZI HISOBLAYDI (RAW SQL yoki boshqa
manba orqali INSERT qilinganda ham ISHLAYDI). (2) C# DARAJASIDA
(masalan konstruktorda `CreatedAt = DateTime.UtcNow`) — FAQAT
EF Core ORQALI SAQLANGANDA ISHLAYDI, boshqa yo'l bilan (raw SQL)
INSERT qilinsa — ISHLAMAYDI.
```

## 5. Code (Amaliy kod)

```sql
-- SQL — Default va Generated Value
CREATE TABLE orders (
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    customer_email VARCHAR(100) NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    order_uuid UUID NOT NULL DEFAULT gen_random_uuid() -- pgcrypto extension kerak
);
```

```csharp
// EF Core Fluent API — DB darajasidagi default (HAR QANDAY manba uchun ishlaydi)
public class AppDbContext : DbContext
{
    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.Entity<Order>(entity =>
        {
            entity.Property(o => o.CreatedAt)
                .HasDefaultValueSql("now()"); // DB DARAJASIDA — RAW SQL orqali ham ishlaydi

            entity.Property(o => o.Status)
                .HasDefaultValue("pending"); // ODDIY, KONSTANT default qiymat

            entity.Property(o => o.Id)
                .ValueGeneratedOnAdd(); // DB avtomatik generatsiya qiladi (Identity)
        });
    }
}

public class Order
{
    public int Id { get; set; }
    public string CustomerEmail { get; set; } = null!;
    public DateTime CreatedAt { get; set; } // EF Core — INSERT'dan KEYIN, DB'dan QIYMATNI O'QIB OLADI
    public string Status { get; set; } = null!;
}
```

```csharp
// ⚠️ MUHIM: agar C# obyektida CreatedAt = default(DateTime) (masalan yangi Order()) bo'lsa,
// EF Core buni "aniq qiymat kiritilmagan" deb hisoblab, DB DEFAULT'ni ISHGA TUSHIRADI —
// LEKIN agar siz aniq DateTime.UtcNow qiymatini bersangiz, U YUBORILADI, DB default ISHLAMAYDI!
var order = new Order { CustomerEmail = "ali@mail.com" }; // CreatedAt — DB default orqali to'ldiriladi
dbContext.Orders.Add(order);
await dbContext.SaveChangesAsync();
Console.WriteLine(order.CreatedAt); // ⚡ EF Core — SaveChanges'dan keyin, DB'dan HAQIQIY qiymatni O'QIB, C# obyektga YOZADI
```

## 6. Keng tarqalgan xatolar / noto'g'ri tushunchalar

```
❌ "C# tomonda `CreatedAt = DateTime.UtcNow` yozish — DB DEFAULT
   bilan BIR XIL" — YO'Q! C# darajasidagi default — FAQAT EF
   Core ORQALI SAQLANGANDA ISHLAYDI. Agar BOSHQA XIZMAT (raw SQL,
   boshqa mikroservice) TO'G'RIDAN-TO'G'RI DB'GA YOZSA — C#
   default ISHGA TUSHMAYDI, DB DEFAULT ESA — HAR DOIM ISHLAYDI.

❌ "SERIAL — TO'LIQ XAVFSIZ, ODDIY FOYDALANUVCHI ID'NI
   O'ZGARTIRA OLMAYDI" — NOTO'G'RI! SERIAL — ODDIY DEFAULT
   bo'lgani UCHUN, INSERT'da ANIQ QIYMAT BERISH MUMKIN
   (masalan `INSERT INTO t (id, ...) VALUES (999, ...)`) —
   GENERATED ALWAYS AS IDENTITY BUNGA YO'L QO'YMAYDI (odatiy
   holatda).

❌ "DEFAULT — NULL YUBORILGANDA HAM ISHLAYDI" — YO'Q! DEFAULT —
   FAQAT USTUN INSERT'da UMUMAN "TILGA OLINMAGANDA" ISHLAYDI.
   Agar ANIQ NULL YUBORILSA — DEFAULT QO'LLANILMAYDI (USTUN
   NULL bo'lib qoladi, agar NOT NULL bo'lmasa).

❌ "EF Core, SaveChanges'dan KEYIN, DB DEFAULT QIYMATLARINI
   AVTOMATIK O'QIB OLMAYDI" — YO'Q, TO'G'RI ISHLAYDI: EF Core
   — INSERT'dan KEYIN, DB DARAJASIDA GENERATSIYA QILINGAN
   QIYMATLARNI (id, created_at) — AVTOMATIK O'QIB, C# OBYEKTGA
   QAYTARIB YOZADI (buning uchun EF Core, INSERT SQL'ga
   `RETURNING` bandini QO'SHADI).
```

## 7. Exam (Interview savollari)

**1. `DEFAULT` va `GENERATED` orasidagi ASOSIY FARQ nima?**
`DEFAULT` — FAQAT QIYMAT BERILMAGANDA QO'LLANADIGAN "ZAXIRA"
QIYMAT (USTUN ERKIN QOLADI, XOHLASA BOSHQA QIYMAT YOZISH MUMKIN).
`GENERATED` — DB TOMONIDAN, ODATDA BOSHQA USTUNLAR/ALGORITM
ASOSIDA MAJBURIY HISOBLANADIGAN QIYMAT (ko'pincha, TO'G'RIDAN
YOZISHGA CHEKLOV QO'YILADI).

**2. `SERIAL` va `GENERATED ALWAYS AS IDENTITY` orasidagi FARQ
nima?**
`SERIAL` — ESKI USUL, ICHKARIDA SEQUENCE + DEFAULT sifatida
IMPLEMENTATSIYA QILINGAN — ODDIY FOYDALANUVCHI QO'LDA QIYMAT
YOZISHI MUMKIN. `GENERATED ALWAYS AS IDENTITY` — SQL STANDARTIGA
MOS, YANGI USUL — ODATDA QO'LDA QIYMAT YOZISHGA CHEKLOV QO'YADI
(OVERRIDING SYSTEM VALUE bo'lmasa).

**3. EF Core'da `HasDefaultValueSql` va C# darajasidagi
(masalan konstruktordagi) default qiymat berish orasidagi FARQ
nima?**
`HasDefaultValueSql` — DB DARAJASIDA ISHLAYDI, HAR QANDAY YO'L
BILAN (raw SQL, boshqa xizmat) INSERT QILINGANDA HAM QO'LLANADI.
C# darajasidagi default — FAQAT EF Core ORQALI SAQLANGANDA
ISHLAYDI.

**4. EF Core, `SaveChangesAsync()`dan KEYIN, DB TOMONIDAN
GENERATSIYA QILINGAN QIYMATLARNI (masalan `id`) QANDAY QILIB
C# OBYEKTGA "OLIB KELADI"?**
EF Core — INSERT SQL SO'ROVIGA `RETURNING` BANDINI (PostgreSQL'da)
QO'SHADI — DB, GENERATSIYA QILGAN QIYMATLARNI (id, created_at
kabi) SHU YERDA QAYTARADI, EF Core ULARNI C# OBYEKT
PROPERTYLARIGA AVTOMATIK YOZADI.

**5. Nima uchun `created_at DEFAULT now()`ni C# tomonda
`DateTime.UtcNow` bilan almashtirish, KO'PINCHA, YAXSHI
AMALIYOT EMAS deb hisoblanadi?**
Chunki DEFAULT — FAQAT EF Core ORQALI YOZILGANDA ISHLAYDI. Agar
KEYINCHALIK BOSHQA XIZMAT/SKRIPT, TO'G'RIDAN-TO'G'RI DB'GA
YOZSA — C# darajasidagi mantiq CHETLAB O'TILADI, natijada
`created_at` NOTO'G'RI (yoki NULL) BO'LISHI MUMKIN. DB
DARAJASIDAGI DEFAULT — BARCHA YO'LLAR UCHUN BIR XIL QOIDANI
KAFOLATLAYDI.
