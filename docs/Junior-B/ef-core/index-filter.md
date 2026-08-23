# Index Filter (Filtered / Partial Index) — Junior B

## 1. What (Nima?)

**Filtered Index** (yoki PostgreSQL'da **Partial Index**) —
JADVALDAGI **BARCHA QATORLARNI EMAS**, BALKI FAQAT **MA'LUM
BIR SHARTGA MOS QATORLARNI** INDEKSLOVCHI INDEKS TURI (masalan,
FAQAT `is_deleted = false` BO'LGAN QATORLAR). Bu, INDEKS
HAJMINI SEZILARLI KICHRAYTIRADI VA FAQAT REAL SO'ROVLARDA
KERAK BO'LGAN QATORLARNI QAMRAB OLADI.

## 2. Real hayot analogiyasi

**Partial Index — FAQAT "FAOL" MIJOZLAR RO'YXATI.** Katta
DO'KON — MILLIONLAB MIJOZGA EGA, LEKIN ULARNING KO'PCHILIGI —
"ARXIVGA O'TGAN" (yopilgan hisob) YOKI "NOFAOL". Agar SIZGA
DOIM FAQAT "FAOL, HOZIRGI MIJOZLAR" RO'YXATI KERAK BO'LSA —
BARCHA MILLIONLAB MIJOZ UCHUN ALOHIDA KATALOG YURITISH
O'RNIGA, **FAQAT FAOL MIJOZLAR UCHUN KICHIKROQ, TEZKOR
KATALOG** YURITISH — QIDIRUVNI TEZLASHTIRADI VA KATALOG
HAJMINI KICHRAYTIRADI.

## 3. Why (Nega kerak?)

Real LOYIHALARDA, SO'ROVLAR KO'PINCHA **FAQAT MA'LUM BIR
SEGMENTGA** QARATILGAN BO'LADI: masalan, `WHERE is_deleted =
false` (SOFT DELETE PATTERN'DA — barcha so'rovlar shu shartni
qo'shadi), YOKI `WHERE status = 'active'`. AGAR TO'LIQ
(barcha qatorlarni qamrovchi) INDEKS YARATILSA — U, KERAKSIZ
("deleted"/"inactive") QATORLARNI HAM SAQLAYDI — DISK JOYINI
ISROF QILADI VA YOZISH (INSERT/UPDATE) TEZLIGINI KAMAYTIRADI.
Partial Index — FAQAT KERAKLI SEGMENTNI INDEKSLAB, BU
MUAMMONI YECHADI.

## 4. Internals (Ichki mexanizm)

### `WHERE` bandi bilan Partial Index yaratish

```sql
CREATE INDEX idx_orders_active ON orders (customer_id) WHERE status = 'active';
```

```
BU INDEKS — FAQAT `status = 'active'` BO'LGAN QATORLARNI
O'Z ICHIGA OLADI. AGAR JADVALDA 10 MILLION QATOR BO'LSA-YU,
FAQAT 50,000 TASI "active" BO'LSA — INDEKS HAJMI, 200 BARO-
BAR KICHIKROQ BO'LADI (10M o'rniga 50K) — bu, DISK JOYINI
TEJASH BILAN BIRGA, INDEKS B-Tree DARAXTINING CHUQURLIGINI
HAM KAMAYTIRADI (tezroq qidiruv).
```

### Query Planner — QACHON Partial Index'NI ISHLATADI

```
PostgreSQL'ning QUERY PLANNER'I — SO'ROVDAGI `WHERE` SHARTI,
PARTIAL INDEKS YARATISHDA ISHLATILGAN SHARTNI **"QAMRAB
OLGANDA"** (yoki UNGA MOS KELGANDA) GINA, INDEKSDAN
FOYDALANADI:

WHERE status = 'active' AND customer_id = 5
    → ✅ Partial Index ISHLAYDI (status='active' sharti MOS)

WHERE status = 'archived' AND customer_id = 5
    → ❌ Partial Index ISHLAMAYDI (indeks BU QATORLARNI
       UMUMAN O'Z ICHIGA OLMAYDI!)
```

### Partial UNIQUE Index — SOFT DELETE bilan BIRGA ISHLASH

```sql
-- Muammo: oddiy UNIQUE constraint, "o'chirilgan" qatorlar bilan HAM to'qnashadi
CREATE UNIQUE INDEX idx_users_email_active ON users (email) WHERE is_deleted = false;
```

```
SOFT DELETE PATTERN'DA (yozuv HAQIQATDA O'CHIRILMAYDI, FAQAT
`is_deleted = true` DEB BELGILANADI) — ODDIY UNIQUE
CONSTRAINT, "O'CHIRILGAN" FOYDALANUVCHI EMAILINI, YANGI
FOYDALANUVCHI QAYTA ISHLATISHIGA YO'L QO'YMAYDI (chunki DB
UCHUN, "o'chirilgan" qator HAM HALI MAVJUD). Partial UNIQUE
Index (`WHERE is_deleted = false`) — FAQAT FAOL
FOYDALANUVCHILAR ORASIDA UNIQUENESS'NI TEKSHIRADI — O'CHIRILGAN
YOZUVLAR — CHEKLOVGA UMUMAN TA'SIR QILMAYDI.
```

## 5. Code (Amaliy kod)

```sql
-- Soft Delete pattern bilan Partial Unique Index
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    email VARCHAR(100) NOT NULL,
    is_deleted BOOLEAN NOT NULL DEFAULT false
);

CREATE UNIQUE INDEX idx_users_email_active ON users (email) WHERE is_deleted = false;

-- Bu — MUVAFFAQIYATLI ishlaydi (eski email — "o'chirilgan" deb belgilangan)
INSERT INTO users (email, is_deleted) VALUES ('ali@mail.com', true);
INSERT INTO users (email, is_deleted) VALUES ('ali@mail.com', false); -- OK, chunki birinchisi is_deleted=true

-- Partial index — faol buyurtmalar uchun
CREATE INDEX idx_orders_pending ON orders (created_at) WHERE status = 'pending';

EXPLAIN ANALYZE SELECT * FROM orders WHERE status = 'pending' ORDER BY created_at;
-- → "Index Scan using idx_orders_pending" — kichik, tezkor indeksdan foydalaniladi
```

```csharp
// EF Core Fluent API — Filtered Index (EF Core 5+)
public class AppDbContext : DbContext
{
    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.Entity<User>()
            .HasIndex(u => u.Email)
            .IsUnique()
            .HasFilter("is_deleted = false"); // Raw SQL filter — DB darajasida

        modelBuilder.Entity<Order>()
            .HasIndex(o => o.CreatedAt)
            .HasFilter("status = 'pending'");
    }
}
```

## 6. Keng tarqalgan xatolar / noto'g'ri tushunchalar

```
❌ "Partial Index — barcha so'rovlarda AVTOMATIK ISHLAYDI" —
   YO'Q! Partial Index — FAQAT SO'ROVNING WHERE SHARTI, INDEKS
   YARATISHDA ISHLATILGAN SHARTGA "MOS KELGANDA" (yoki uni
   QAMRAB OLGANDA) ISHLAYDI. BOSHQA SHARTLI SO'ROVLARDA —
   INDEKS UMUMAN ISHLATILMAYDI.

❌ "Soft Delete pattern'da, oddiy UNIQUE constraint (WHERE
   shartisiz) YETARLI" — YO'Q! Bu, O'CHIRILGAN YOZUVLARNING
   EMAIL/USERNAME KABI QIYMATLARINI, YANGI FOYDALANUVCHI QAYTA
   ISHLATISHIGA TO'SQINLIK QILADI — Partial UNIQUE Index
   BUNI TO'G'RILAYDI.

❌ "Filtered Index — faqat PostgreSQL'ga XOS FUNKSIYA" — YO'Q,
   SQL Server'da HAM "Filtered Index" NOMI BILAN MAVJUD, LEKIN
   SINTAKSISI VA BA'ZI CHEKLOVLARI FARQ QILADI.

❌ "Partial Index — HAR DOIM to'liq indeksdan KICHIKROQ VA
   TEZROQ" — ODATDA TO'G'RI, LEKIN AGAR FILTR SHARTI, JADVAL
   QATORLARINING KATTA QISMIGA MOS KELSA (masalan 95% qator
   "active") — FARQ KAM SEZILARLI BO'LADI.
```

## 7. Exam (Interview savollari)

**1. Partial (Filtered) Index nima, va u ODDIY INDEKSDAN
NIMASI BILAN FARQ QILADI?**
Partial Index — JADVALDAGI BARCHA QATORLARNI EMAS, FAQAT
MA'LUM BIR `WHERE` SHARTIGA MOS QATORLARNI INDEKSLAYDI. Oddiy
INDEKS — BARCHA QATORLARNI QAMRAB OLADI. Partial Index —
KICHIKROQ HAJMGA EGA VA FAQAT MOS SO'ROVLARDA ISHLAYDI.

**2. Partial Index QACHON ISHLATILISHI, ODATDA QANDAY REAL
LOYIHA STSENARIYSIDA KERAK BO'LADI?**
SOFT DELETE PATTERN'DA (`is_deleted` flag), YOKI STATUS-BASED
FILTRLASHDA (masalan faqat "active"/"pending" qatorlar
tez-tez so'raladi) — BARCHA SO'ROVLAR DOIM BIR XIL SHARTNI
QO'SHGANDA, Partial Index — SHU SEGMENTNI KICHIK VA TEZKOR
QILIB SAQLASH IMKONINI BERADI.

**3. Partial UNIQUE Index, SOFT DELETE PATTERN'DAGI QANDAY
MUAMMONI YECHADI?**
Oddiy UNIQUE CONSTRAINT — "O'CHIRILGAN" (is_deleted=true)
YOZUVLARNI HAM HISOBGA OLADI, natijada O'CHIRILGAN EMAILNI
YANGI FOYDALANUVCHI QAYTA ISHLATA OLMAYDI. Partial UNIQUE
Index (`WHERE is_deleted = false`) — FAQAT FAOL YOZUVLAR
ORASIDA UNIQUENESS'NI TEKSHIRADI.

**4. Query Planner, Partial Index'ni QACHON "IGNOR" QILADI
(ishlatmaydi)?**
Agar SO'ROVNING `WHERE` SHARTI, PARTIAL INDEKS YARATISHDA
ISHLATILGAN SHARTGA MOS KELMASA (masalan indeks
`status='active'` uchun, so'rov esa `status='archived'`ni
so'rasa) — PLANNER, INDEKS BU QATORLARNI UMUMAN O'Z ICHIGA
OLMASLIGINI BILADI VA UNI ISHLATMAYDI.

**5. Partial Index ishlatishning ASOSIY AFZALLIGI, TO'LIQ
INDEKSGA NISBATAN nima?**
KICHIKROQ HAJM (disk joyi tejaladi), TEZROQ QIDIRUV (B-Tree
chuqurligi kamroq), VA TEZROQ YOZISH (faqat filtrga mos
qatorlar uchun indeks yangilanadi, boshqa qatorlar uchun
YO'Q) — bu, ayniqsa KATTA JADVALLARDA, LEKIN KICHIK "FAOL
SEGMENT" bilan ISHLAGANDA, SEZILARLI FARQ BERADI.
