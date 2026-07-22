# SQL — Filtering, Grouping, Aggregate, Constraints, Data Types — Junior C

## 1. Nima?

**SQL (Structured Query Language)** — relatsion ma'lumotlar bazasi
bilan muloqot qilish uchun deklarativ til. Bu hujjat **PostgreSQL**
(loyihada ishlatiladigan DB) sintaksisiga asoslangan.

## 2. Nima uchun kerak?

EF Core yoki ADO.NET orqali yozilgan har qanday LINQ so'rovi —
oxir-oqibat **SQL**ga tarjima qilinadi. SQL ni chuqur bilmasdan turib:
- EF Core generatsiya qilgan **noaniq/samarasiz** SQL ni aniqlab
  bo'lmaydi
- Murakkab hisobotlar (aggregatsiya, guruhlash) uchun raw SQL yozib
  bo'lmaydi
- DB darajasidagi performance muammolarini (indekslar, N+1) tushunib
  bo'lmaydi

## 3. SELECT bajarilish tartibi — MUHIM tushuncha

SQL kodida yozish tartibi bilan **bajarilish** tartibi FARQ qiladi:

```sql
SELECT department_id, COUNT(*) AS cnt      -- 5. Ustunlarni tanlash
FROM employees                              -- 1. Jadvaldan boshlanadi
WHERE age > 25                              -- 2. Qatorlarni filtrlash
GROUP BY department_id                      -- 3. Guruhlash
HAVING COUNT(*) > 5                         -- 4. Guruhlarni filtrlash
ORDER BY cnt DESC                           -- 6. Tartiblash
LIMIT 10;                                   -- 7. Cheklash
```

```
YOZISH TARTIBI:     SELECT → FROM → WHERE → GROUP BY → HAVING → ORDER BY → LIMIT
BAJARILISH TARTIBI: FROM → WHERE → GROUP BY → HAVING → SELECT → ORDER BY → LIMIT
```

Shuning uchun `WHERE` da `SELECT`da yaratilgan alias (`cnt`) ni
ishlatib bo'lmaydi (`WHERE` `SELECT`dan OLDIN bajariladi), lekin
`ORDER BY` da bo'ladi (u `SELECT`dan KEYIN bajariladi):

```sql
-- ❌ Xato: WHERE hali "cnt" ni bilmaydi
SELECT COUNT(*) AS cnt FROM employees WHERE cnt > 5;

-- ✅ To'g'ri: ORDER BY allaqachon SELECT'dan keyin, "cnt"ni biladi
SELECT COUNT(*) AS cnt FROM employees GROUP BY department_id ORDER BY cnt DESC;
```

## 4. WHERE filtrlash — barcha operatorlar

```sql
SELECT * FROM employees
WHERE age > 25
  AND department_id = 3
  OR position = 'Manager';

-- Ustunlar orasidagi ustuvorlik uchun qavs shart!
WHERE (age > 25 AND department_id = 3) OR position = 'Manager';

-- IN — ro'yxatdan biriga teng
SELECT * FROM employees WHERE department_id IN (1, 2, 3);

-- NOT IN
SELECT * FROM employees WHERE department_id NOT IN (1, 2);

-- BETWEEN — diapazon (ikkala chegara HAM kiradi)
SELECT * FROM employees WHERE age BETWEEN 25 AND 35;

-- LIKE — pattern matching (% = istalgan belgilar, _ = bitta belgi)
SELECT * FROM employees WHERE full_name LIKE 'Orz%';   -- "Orz" bilan boshlanadi
SELECT * FROM employees WHERE full_name LIKE '%bek';    -- "bek" bilan tugaydi
SELECT * FROM employees WHERE full_name LIKE '_r%';     -- 2-harf "r"

-- IS NULL / IS NOT NULL — NULL bilan solishtirish uchun = ISHLAMAYDI!
SELECT * FROM employees WHERE updated_at IS NULL;
-- ❌ WHERE updated_at = NULL   -- HECH QACHON true bo'lmaydi!

-- EXISTS — subquery natija qaytarsa true
SELECT * FROM departments d
WHERE EXISTS (
    SELECT 1 FROM employees e WHERE e.department_id = d.id
);

-- NOT EXISTS
SELECT * FROM departments d
WHERE NOT EXISTS (
    SELECT 1 FROM employees e WHERE e.department_id = d.id
);
```

### IN vs EXISTS — qachon qaysi, performance farqi

```sql
-- IN — ichki natija KICHIK bo'lsa yaxshi
SELECT * FROM employees WHERE department_id IN (SELECT id FROM departments WHERE active = true);

-- EXISTS — ichki jadval KATTA bo'lsa yaxshiroq (birinchi mos qator topilgach TO'XTAYDI)
SELECT * FROM departments d
WHERE EXISTS (SELECT 1 FROM employees e WHERE e.department_id = d.id);
```

```
IN: ichki subquery NATIJASINI TO'LIQ hisoblab, keyin har bir tashqi
    qator uchun shu ro'yxat bilan solishtiradi

EXISTS: har bir tashqi qator uchun ichki subquery'ni ishga tushiradi,
        BIRINCHI mos qator topilishi bilan TO'XTAYDI (short-circuit)
```

Zamonaviy query plannerlar (PostgreSQL) ko'pincha ikkalasini bir xil
execution plan'ga optimallashtiradi, lekin katta, murakkab
subquery'larda `EXISTS` ko'pincha ishonchliroq.

## 5. ORDER BY — tartiblash

```sql
SELECT * FROM employees ORDER BY full_name ASC;   -- A→Z (default)
SELECT * FROM employees ORDER BY age DESC;         -- Kattadan kichikka

-- Bir nechta ustun — birinchi ustun ustuvor, teng bo'lsa ikkinchisi
SELECT * FROM employees ORDER BY department_id, age DESC;

-- NULL qiymatlar qayerda joylashishi
SELECT * FROM employees ORDER BY age DESC NULLS LAST;  -- NULL lar OXIRIDA
SELECT * FROM employees ORDER BY age ASC NULLS FIRST;   -- NULL lar BOSHIDA
```

PostgreSQL'da default: `ASC` → `NULLS LAST`, `DESC` → `NULLS FIRST`
— shuning uchun aniqlik uchun `NULLS LAST/FIRST`ni **qo'lda** yozish
tavsiya etiladi.

## 6. DISTINCT

```sql
SELECT DISTINCT department_id FROM employees;
-- Ichkarida: barcha qatorlar SORT/HASH qilinadi, TAKRORLANUVCHI qiymatlar OLIB TASHLANADI

SELECT COUNT(DISTINCT department_id) FROM employees; -- Nechta UNIKAL bo'lim bor
```

`DISTINCT` — katta jadvallarda **qimmat** operatsiya (sort/hash
kerak), shuning uchun faqat kerak bo'lganda ishlatilishi kerak.

## 7. Aggregate funksiyalar

```sql
SELECT
    COUNT(*)           AS total,        -- Barcha qatorlar (NULL larni ham hisoblaydi)
    COUNT(updated_at)  AS updated,      -- Faqat NOT NULL qiymatlar hisoblanadi!
    SUM(salary)        AS total_salary,
    AVG(salary)        AS avg_salary,
    MIN(salary)        AS min_salary,
    MAX(salary)        AS max_salary
FROM employees;
```

### `COUNT(*)` vs `COUNT(column)` farqi

```sql
-- Jadval: 5 ta qator, 2 tasida updated_at = NULL

SELECT COUNT(*) FROM employees;          -- → 5 (BARCHA qator, NULL bilan ham)
SELECT COUNT(updated_at) FROM employees; -- → 3 (faqat NOT NULL bo'lganlar)
```

## 8. GROUP BY va HAVING

```sql
SELECT department_id, COUNT(*) AS count
FROM employees
GROUP BY department_id
HAVING COUNT(*) > 5;
```

```
WHERE:  qatorlarni GROUP BY DAN OLDIN filtrlaydi (individual qatorlar ustida)
HAVING: guruhlarni GROUP BY DAN KEYIN filtrlaydi (aggregate natijalar ustida)

❌ WHERE COUNT(*) > 5   -- Compile xatosi! WHERE bajarilganda hali guruh yo'q
✅ HAVING COUNT(*) > 5  -- To'g'ri, chunki guruhlash allaqachon bajarilgan
```

```sql
-- Ikkalasini birga ishlatish
SELECT department_id, AVG(salary) AS avg_salary
FROM employees
WHERE is_active = true          -- 1. Faqat faol xodimlarni oldindan filtrlash
GROUP BY department_id           -- 2. Bo'lim bo'yicha guruhlash
HAVING AVG(salary) > 5000000;    -- 3. Faqat o'rtacha maoshi katta bo'limlar
```

**Muhim qoida:** `GROUP BY`da bo'lmagan ustunni `SELECT`da aggregate
funksiyasiz ishlatib bo'lmaydi:

```sql
-- ❌ Xato: full_name GROUP BY'da yo'q va aggregate ham emas
SELECT department_id, full_name, COUNT(*) FROM employees GROUP BY department_id;

-- ✅ To'g'ri
SELECT department_id, COUNT(*) FROM employees GROUP BY department_id;
```

## 9. Shart ifodalari

```sql
-- CASE — oddiy shakl (bitta ustunni qiymatlar bilan solishtirish)
SELECT full_name,
    CASE department_id
        WHEN 1 THEN 'IT'
        WHEN 2 THEN 'HR'
        ELSE 'Boshqa'
    END AS department_name
FROM employees;

-- CASE — qidiruv shakli (istalgan shart)
SELECT full_name,
    CASE
        WHEN age < 25 THEN 'Yosh'
        WHEN age < 40 THEN 'O''rta'   -- Apostrof ikki marta yoziladi (escape)
        ELSE 'Tajribali'
    END AS category
FROM employees;

-- COALESCE — birinchi NULL bo'lmagan qiymatni qaytaradi
SELECT COALESCE(updated_at, created_at, NOW()) AS last_modified FROM employees;

-- NULLIF — ikkinchi argument bilan teng bo'lsa NULL qaytaradi (0'ga bo'lish xatosidan qochish uchun foydali)
SELECT salary / NULLIF(hours_worked, 0) AS rate FROM employees;

-- GREATEST / LEAST — bir nechta qiymatdan eng katta/kichigi
SELECT GREATEST(salary, 1000000) FROM employees;  -- Minimal maosh kafolati
SELECT LEAST(salary, 5000000) FROM employees;      -- Maksimal chegaralash
```

## 10. Constraints

```sql
CREATE TABLE employees (
    id          SERIAL          PRIMARY KEY,                       -- Avtomatik unikal, NOT NULL
    full_name   VARCHAR(100)    NOT NULL,                          -- Bo'sh bo'lolmaydi
    email       VARCHAR(200)    NOT NULL UNIQUE,                   -- Takrorlanmasin
    age         INT             CHECK (age >= 18 AND age <= 65),   -- Qiymat cheklovi
    department_id INT           REFERENCES departments(id)
        ON DELETE RESTRICT,                                        -- Foreign Key
    salary      DECIMAL(15, 2)  DEFAULT 0 CHECK (salary >= 0),     -- Default qiymat + shart
    created_at  TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);
```

### `ON DELETE` variantlari — farqlari

```sql
ON DELETE CASCADE    -- Ota-yozuv o'chirilsa — BOLA yozuvlar HAM avtomatik o'chiriladi
ON DELETE RESTRICT   -- Agar BOLA yozuvlar mavjud bo'lsa — ota-yozuvni o'CHIRISHGA RUXSAT BERILMAYDI (xato)
ON DELETE SET NULL   -- Ota o'chirilsa — bola yozuvdagi FK ustuni NULL qilinadi
ON DELETE NO ACTION  -- RESTRICT ga o'xshash, lekin tekshiruv KECHIKTIRILGAN (transaction oxirida)
```

```
Misol: department o'chirilsa, uning employees lariga nima bo'ladi?

CASCADE:    department + BARCHA uning employees SI HAM o'chadi (XAVFLI!)
RESTRICT:   agar bo'limda xodim bo'lsa — o'CHIRISH BLOKLANADI
SET NULL:   bo'lim o'chadi, xodimlarning department_id NULL bo'lib qoladi
```

ERP tizimida odatda `RESTRICT` (yoki `SET NULL`) tavsiya etiladi —
`CASCADE` tasodifan katta hajmda ma'lumot yo'qotishga olib kelishi
mumkin.

## 11. PostgreSQL Data Types — to'liq ro'yxat

```sql
-- Raqamlar
SMALLINT              -- -32768 dan 32767 gacha
INTEGER / INT          -- ~-2 mlrd dan +2 mlrd gacha
BIGINT                 -- juda katta sonlar (masalan, jami hisob-kitob summasi)
DECIMAL(p,s) / NUMERIC(p,s)  -- ANIQ arifmetika — MOLIYAVIY hisob uchun MAJBURIY
REAL, DOUBLE PRECISION  -- Float — TAXMINIY (moliyada ISHLATILMASIN!)
SERIAL / BIGSERIAL      -- Avtomatik oshuvchi INT/BIGINT (auto-increment)

-- Matn
VARCHAR(n)   -- O'zgaruvchan uzunlik, MAKSIMAL n belgi
CHAR(n)      -- QAT'IY n belgi (kichik bo'lsa bo'sh joy bilan to'ldiriladi)
TEXT         -- Cheksiz uzunlik

-- Sana/Vaqt
DATE          -- Faqat sana (2026-07-22)
TIME          -- Faqat vaqt (14:30:00)
TIMESTAMP     -- Sana + vaqt, TIMEZONE'SIZ
TIMESTAMPTZ   -- Sana + vaqt, TIMEZONE bilan — SERVER UchUN TAVSIYA ETILADI
INTERVAL      -- Vaqt oralig'i (masalan "3 kun 2 soat")

-- Boshqalar
BOOLEAN       -- true/false
UUID          -- Universal noyob identifikator (distributed sistemalar uchun)
JSONB         -- Binary JSON — indekslanadi, TEZ so'rov qilinadi (TAVSIYA ETILADI)
JSON          -- Matn ko'rinishidagi JSON — indekslanmaydi, sekinroq
ARRAY         -- PostgreSQL'ga xos massiv turi (masalan INT[])
```

**`DECIMAL` vs `FLOAT` — moliyaviy hisobda MUHIM farq:**

```sql
-- ❌ FLOAT — binary formatda saqlanadi, YAXLITLASH XATOSI bo'lishi mumkin
SELECT 0.1::REAL + 0.2::REAL; -- → 0.30000001192092896 (aniq emas!)

-- ✅ DECIMAL — o'nlik formatda ANIQ saqlanadi
SELECT 0.1::DECIMAL + 0.2::DECIMAL; -- → 0.3 (ANIQ!)
```

ERP/moliyaviy tizimlarda maosh, narx, summalar — **HAR DOIM** `DECIMAL`
ustunlarida saqlanishi kerak, `FLOAT`/`REAL` emas.

## 12. Qachon ishlatish kerak?

| Ehtiyoj | Yechim |
|---|---|
| Katta ichki jadval, mavjudlikni tekshirish | `EXISTS` |
| Kichik, statik ro'yxat bilan solishtirish | `IN` |
| Guruh natijasini filtrlash | `HAVING` |
| Individual qatorni filtrlash | `WHERE` |
| Moliyaviy summalar | `DECIMAL(p,s)` |
| Tezkor JSON so'rovlar | `JSONB` (`JSON` emas) |
| Server vaqti/timezone bilan ishlash | `TIMESTAMPTZ` |
| Bola yozuvlarni himoyalash | `ON DELETE RESTRICT` |

## 13. Qo'shimcha — chuqur nuqtalar

- **Indekslar** — `WHERE`, `JOIN`, `ORDER BY`da tez-tez ishlatiladigan
  ustunlarga indeks qo'yish so'rovni sezilarli tezlashtiradi, lekin
  har bir indeks — `INSERT`/`UPDATE` ni biroz sekinlashtiradi (indeks
  ham yangilanishi kerak).

- **N+1 muammosi** — EF Core'da `Include()` ishlatilmasa, har bir
  parent uchun alohida SQL so'rov yuborilishi mumkin — bu SQL bilishni
  talab qiladigan eng ko'p uchraydigan performance xatosi.

- **Transaction darajasi (Isolation Level)** — `READ COMMITTED`
  (PostgreSQL default), `REPEATABLE READ`, `SERIALIZABLE` — parallel
  tranzaksiyalar bir-biriga qanday ta'sir qilishini belgilaydi.

- **`EXPLAIN ANALYZE`** — SQL so'rovning haqiqiy execution plan'ini
  ko'rish uchun PostgreSQL buyrug'i — qaysi indeks ishlatilgani,
  qancha vaqt ketganini ko'rsatadi.

- **Real loyihada uchraydigan xato:** `LIKE '%qidiruv%'` (boshida `%`
  bilan) — bu indeksdan **foydalana olmaydi**, chunki DB ustunning
  boshidan qidira olmaydi — bu katta jadvallarda **full table scan**ga
  olib keladi. Yechim: `pg_trgm` extension yoki full-text search.

## 14. Imtihon savollari

1. SQL so'rovning bajarilish tartibi (`FROM → WHERE → GROUP BY →
   HAVING → SELECT → ORDER BY`) yozish tartibidan nima uchun farq
   qiladi? Buni misol bilan tushuntiring.
2. `WHERE` va `HAVING` orasidagi farq nima?
3. `EXISTS` va `IN` orasidagi farq nima, va katta ichki jadvalda
   qaysi biri afzal?
4. `COUNT(*)` va `COUNT(column)` orasidagi farq nima?
5. `DECIMAL` va `FLOAT` orasidagi farq nima? Moliyaviy hisob-kitobda
   nima uchun `DECIMAL` majburiy?
6. `ON DELETE CASCADE`, `RESTRICT`, `SET NULL` orasidagi farqni
   real misol bilan tushuntiring.
7. `NULLS LAST` nima uchun kerak va PostgreSQL default holatda
   qanday ishlaydi?
8. `LIKE '%qidiruv%'` nima uchun performance muammosiga olib kelishi
   mumkin?
