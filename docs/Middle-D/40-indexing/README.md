# Database Indexing — Middle D

## 1. Nima? (Ta'rif)

**Index** — jadval qatorlarini **tez topish** uchun yaratilgan
qo'shimcha ma'lumot tuzilmasi (odatda **B-Tree**) — kitobning
oxiridagi "mundarija"ga o'xshaydi: har sahifani birma-bir ko'rish
o'rniga, to'g'ridan kerakli joyga o'tish imkonini beradi.

## 2. Nima uchun kerak?

Indekssiz jadvalda — `WHERE email = 'x@y.com'` so'rovi **HAR BIR**
qatorni tekshirishga majbur (**Sequential/Full Table Scan**) — 1
million qatorli jadvalda bu **sekin**. Index — DB'ga **to'g'ridan**
kerakli qatorga o'tish imkonini beradi.

## 3. Ichida nima sodir bo'ladi? (Mexanizm)

### 3.1 B-Tree tuzilishi — nima uchun tezlashtiradi

```
Full Table Scan (indekssiz):
  [qator1][qator2][qator3]...[qator1000000] ← HAR BIRINI TEKSHIRISH kerak
  O(n) — chiziqli qidiruv

B-Tree Index:
                [50]
              /      \
          [25]        [75]
         /    \       /    \
       [10]  [40]  [60]  [90]
      
  Qidiruv — DARAXT bo'ylab, HAR QADAMDA yarmini "TASHLAB YUBORADI"
  O(log n) — 1,000,000 qator uchun — FAQAT ~20 QADAM (2^20 ≈ 1M)!
```

### 3.2 Index turlari

```
B-Tree (DEFAULT) — tenglik (=) va DIAPAZON (<, >, BETWEEN) so'rovlar uchun
Hash             — FAQAT tenglik (=) uchun, B-Tree'dan biroz tezroq (lekin kam ishlatiladi)
GiST             — Spatial (geometrik) ma'lumotlar, full-text search uchun
GIN              — Array, JSONB, full-text search (bir nechta qiymatga ega ustunlar)
BRIN             — JUDA katta, tartiblangan jadvallar (masalan vaqt bo'yicha log) uchun, KICHIK hajmda
```

### 3.3 `CREATE INDEX` sintaksisi

```sql
CREATE INDEX idx_employees_email ON employees (email);
CREATE UNIQUE INDEX idx_employees_email_unique ON employees (email); -- + UNIQUE cheklov
```

### 3.4 Partial Index — WHERE sharti bilan

```sql
CREATE INDEX idx_active_employees ON employees (department_id) WHERE is_active = true;
```

```
Faqat is_active = true bo'lgan qatorlar uchun INDEKS YARATILADI —
agar 90% xodim NOFAOL (arxivlangan) bo'lsa, index HAJMI SEZILARLI
KICHIKROQ bo'ladi, va "faol xodimlar" bo'yicha so'rovlar TEZROQ.
```

### 3.5 Composite Index — bir nechta ustun

```sql
CREATE INDEX idx_employees_dept_age ON employees (department_id, age);
```

```
⚠️ TARTIB MUHIM! Bu index:
  ✅ WHERE department_id = 5                    → ISHLATILADI
  ✅ WHERE department_id = 5 AND age > 25        → ISHLATILADI (ikkalasi ham)
  ❌ WHERE age > 25 (department_id'siz)          → ISHLATILMAYDI!

Qoida: composite index — chapdan o'ngga "PREFIX" tartibida
ISHLAYDI (kitobning mundarijasi kabi — avval "familya", keyin
"ism" bo'yicha tartiblangan bo'lsa, faqat "ism" bo'yicha qidirish
SAMARASIZ).
```

### 3.6 Unique Index

```sql
CREATE UNIQUE INDEX idx_employees_email_unique ON employees (email);
-- Endi IKKI marta bir xil email bilan INSERT qilib bo'lmaydi
```

### 3.7 Expression Index — funksiya asosida

```sql
CREATE INDEX idx_employees_lower_email ON employees (LOWER(email));

-- Endi bu so'rov INDEKSNI ISHLATADI:
SELECT * FROM employees WHERE LOWER(email) = 'orzibek@mail.com';
```

Oddiy indeks — `WHERE LOWER(email) = ...` so'rovini **ISHLATA
OLMAYDI** (chunki indeks — ustunning ASL qiymati bo'yicha,
funksiya natijasi bo'yicha EMAS). Expression Index — bu holatni
hal qiladi.

### 3.8 Index qachon ishlatilmaydi — optimizer qarorlari

```
PostgreSQL Query Planner — HAR DOIM indeks ISHLATMAYDI, agar:

1. Jadval JUDA KICHIK bo'lsa (Full Scan indeksdan TEZROQ bo'lishi
   mumkin — indeks o'qish HAM overhead)
2. So'rov NATIJASI jadvalning KATTA QISMINI (masalan 50%+) qamrab
   olsa (Full Scan — indeks + qator o'qishdan TEZROQ)
3. Statistika (ANALYZE) ESKIRGAN bo'lsa — Planner NOTO'G'RI qaror
   qabul qilishi mumkin
```

### 3.9 `EXPLAIN ANALYZE` — query plan o'qish

```sql
EXPLAIN ANALYZE SELECT * FROM employees WHERE email = 'orzibek@mail.com';
```

```
Index Scan using idx_employees_email on employees
  (cost=0.29..8.31 rows=1 width=120)
  (actual time=0.023..0.025 rows=1 loops=1)
  Index Cond: (email = 'orzibek@mail.com'::text)
Planning Time: 0.150 ms
Execution Time: 0.045 ms
```

```
"Index Scan"        — INDEKS ishlatildi ✅
"Seq Scan"           — Full Table Scan — indeks ISHLATILMADI ⚠️
"cost=0.29..8.31"    — TAXMINIY xarajat (kichikroq = yaxshiroq)
"actual time"        — HAQIQIY bajarilish vaqti
```

### 3.10 Index overhead — INSERT/UPDATE sekinlashishi

```
Har INDEKS — HAR INSERT/UPDATE/DELETE'da HAM YANGILANISHI kerak!

5 ta indeksga ega jadvalda 1 ta INSERT:
  1. Asosiy jadvalga YOZISH
  2. 5 ta indeksning HAR BIRINI YANGILASH

Ko'p indeks — O'QISH TEZ, lekin YOZISH SEKIN.
```

### 3.11 EF Core'da index — `HasIndex()`, `[Index]`

```csharp
// Fluent API
modelBuilder.Entity<Employee>().HasIndex(e => e.Email).IsUnique();
modelBuilder.Entity<Employee>().HasIndex(e => new { e.DepartmentId, e.Age }); // Composite

// Data Annotation (EF Core 5+)
[Index(nameof(Email), IsUnique = true)]
public class Employee { public string Email { get; set; } = null!; }
```

## 4. Kod — real ERP misoli

```sql
-- Tez-tez WHERE department_id VA ORDER BY hired_at bilan so'raladigan jadval
CREATE INDEX idx_employees_dept_hired ON employees (department_id, hired_at DESC);

-- Faqat faol xodimlar bo'yicha tez qidiruv
CREATE INDEX idx_active_emp_email ON employees (email) WHERE is_active = true;
```

## 5. Qachon ishlatish kerak?

| Vaziyat | Yechim |
|---|---|
| Tez-tez WHERE/JOIN'da ishlatiladigan ustun | B-Tree index |
| Faqat ma'lum shart bilan so'raladigan qism | Partial index |
| Bir nechta ustun BIRGA filtrlash | Composite index (tartibga e'tibor bilan) |
| JSONB, Array ustunlar | GIN index |
| Funksiya natijasi bo'yicha qidiruv | Expression index |

**Qachon index KERAK EMAS:**
```
❌ Juda kichik jadval (yuzlab qator)
❌ Ustun KAM ishlatiladigan so'rovlarda (WHERE/JOIN/ORDER BY'da YO'Q)
❌ Jadval ko'proq YOZISH uchun (INSERT-heavy), kam O'QISH uchun
```

## 6. Muhim nuqtalar

- Har qo'shilgan indeks — INSERT/UPDATE'ni SEKINLASHTIRADI —
  "har ustunga indeks qo'yish" ANTI-PATTERN.
- Composite index tartibi — **eng ko'p** ishlatiladigan filtr ustuni
  BIRINCHI bo'lishi kerak.
- `EXPLAIN ANALYZE` — HAR performance muammosini tekshirishning
  BIRINCHI qadami bo'lishi kerak.

## 7. Imtihon savollari

1. B-Tree index nima uchun qidiruvni O(n) dan O(log n)ga
   tezlashtiradi?
2. Composite index'da ustun tartibi nima uchun muhim?
3. Partial Index qachon foydali va u qanday afzallik beradi?
4. `EXPLAIN ANALYZE` natijasida "Seq Scan" va "Index Scan" orasidagi
   farq nima?
5. Nima uchun ko'p indeks — yozish (INSERT/UPDATE) tezligini
   pasaytiradi?
6. Expression Index qanday muammoni (masalan `LOWER(email)`
   bo'yicha qidiruv) hal qiladi?
