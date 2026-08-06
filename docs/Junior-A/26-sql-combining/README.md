# SQL — UNION, UNION ALL, EXCEPT, INTERSECT — Junior A

## 1. Nima? (Ta'rif)

**Set operators** — ikkita (yoki undan ko'p) SQL so'rov natijasini
**to'plamlar nazariyasi** mantig'i bilan birlashtiruvchi
operatorlar: **UNION** (birlashma), **EXCEPT** (ayirma), **INTERSECT**
(kesishma).

## 2. Nima uchun kerak?

Ba'zida ma'lumot **bir nechta jadval/so'rov**dan kelib, ularni
**bitta natija** sifatida ko'rsatish yoki **solishtirish** kerak
bo'ladi (masalan, "qaysi xodimlar HAR IKKI loyihada ishlagan").

## 3. Ichida nima sodir bo'ladi? (Mexanizm)

### 3.1 UNION — birlashtirish, duplicate olib tashlaydi

```sql
SELECT full_name FROM full_time_employees
UNION
SELECT full_name FROM contractors;
```

```
Shartlar: IKKALA so'rov — BIR XIL ustun SONI, MOS keluvchi TURLARGA
ega bo'lishi SHART.

Ichkarida: IKKALA natija — BIRLASHTIRILADI, KEYIN SORT + DEDUPLICATE
qilinadi (TAKRORLANUVCHI qatorlar OLIB TASHLANADI) — bu QO'SHIMCHA
ish, SEKINROQ.
```

### 3.2 UNION ALL — duplicate OLIB TASHLAMAYDI, TEZROQ

```sql
SELECT full_name FROM full_time_employees
UNION ALL
SELECT full_name FROM contractors;
```

```
UNION ALL — SORT/DEDUPLICATE QILMAYDI — IKKALA natijani SHUNCHAKI
"QO'SHIB QO'YADI". AGAR takrorlanish MUAMMO EMAS (yoki jadvallar
tabiiy ravishda BIR-BIRI bilan KESISHMAYDI) bo'lsa — UNION ALL
HAR DOIM TEZROQ.
```

### 3.3 UNION vs UNION ALL — qachon qaysi

```
UNION      — Takrorlanuvchi qatorlarni ISTAMAYSIZ (masalan UNIKAL
              ro'yxat kerak)
UNION ALL  — Takrorlanish MUHIM EMAS, yoki PERFORMANCE MUHIM
              (masalan, LOG yozuvlarini BIRLASHTIRISH — takroriy
              bo'lishi TABIIY)
```

### 3.4 EXCEPT — birinchida bor, ikkinchida yo'q

```sql
SELECT employee_id FROM all_employees
EXCEPT
SELECT employee_id FROM active_employees;
-- Natija: FAQAT nofaol (arxivlangan) xodim ID'lari
```

```
PostgreSQL: EXCEPT
SQL Server: EXCEPT (bir xil nomlangan)
Oracle:     MINUS (BOSHQA nom, LEKIN BIR XIL vazifa!)
```

### 3.5 EXCEPT ALL — duplicate saqlanadi

```sql
SELECT product_id FROM order_items -- takroriy bo'lishi mumkin
EXCEPT ALL
SELECT product_id FROM returned_items;
```

### 3.6 INTERSECT — ikkalasida ham bor

```sql
SELECT employee_id FROM project_a_team
INTERSECT
SELECT employee_id FROM project_b_team;
-- Natija: IKKALA loyihada HAM ishtirok etayotgan xodimlar
```

### 3.7 Amaliy misollar

**Bir nechta jadvaldan o'xshash ma'lumot birlashtirish:**
```sql
SELECT 'Xodim' AS type, full_name AS name FROM employees
UNION ALL
SELECT 'Mijoz' AS type, company_name AS name FROM clients;
```

**Audit: o'zgargan qatorlarni topish:**
```sql
SELECT id, salary FROM employees_current
EXCEPT
SELECT id, salary FROM employees_snapshot_yesterday;
-- Natija: KECHAGIDAN BUGUNGACHA maoshi O'ZGARGAN xodimlar
```

**Report: turli kategoriyalar birlashtirish:**
```sql
SELECT 'IT' AS category, COUNT(*) FROM employees WHERE department_id = 1
UNION ALL
SELECT 'HR' AS category, COUNT(*) FROM employees WHERE department_id = 2;
```

### 3.8 EF Core'da — LINQ

```csharp
var allNames = fullTimeEmployees.Select(e => e.FullName)
    .Union(contractors.Select(c => c.FullName)); // UNION — TAKRORLANUVCHI olib TASHLANADI

var allNamesWithDup = fullTimeEmployees.Select(e => e.FullName)
    .Concat(contractors.Select(c => c.FullName)); // UNION ALL — Concat() ga TENG

var onlyInA = teamA.Select(e => e.Id).Except(teamB.Select(e => e.Id));
var inBoth = teamA.Select(e => e.Id).Intersect(teamB.Select(e => e.Id));
```

### 3.9 Normal Formalar — qisqacha eslatma

```
1NF — Atomik qiymatlar (bir katakda BITTA qiymat)
2NF — 1NF + Partial Dependency YO'Q
3NF — 2NF + Transitive Dependency YO'Q
BCNF — 3NF'ning kuchliroq versiyasi

(To'liq tushuntirish: docs/Junior-A/22-db-normalization)
```

## 4. Kod — real ERP misoli

```sql
-- Barcha "aktiv bo'lgan yoki bo'lgan" shaxslarni (xodim + pudratchi) BIRLASHTIRISH
SELECT id, full_name, 'FullTime' AS type FROM full_time_employees
UNION ALL
SELECT id, full_name, 'Contractor' AS type FROM contractors
ORDER BY full_name;

-- Bo'limlar orasida umumiy ko'nikmaga ega xodimlarni TOPISH
SELECT employee_id FROM employees WHERE department_id = 1 AND skill = 'SQL'
INTERSECT
SELECT employee_id FROM employees WHERE department_id = 2 AND skill = 'SQL';
```

## 5. Qachon ishlatish kerak?

| Vaziyat | Yechim |
|---|---|
| Ikki manba, faqat unikal natija kerak | `UNION` |
| Ikki manba, performance muhim, takror OK | `UNION ALL` |
| "Faqat birinchida bor" | `EXCEPT` |
| "Ikkalasida ham bor" | `INTERSECT` |
| EF Core LINQ ekvivalenti | `.Union()`, `.Concat()`, `.Except()`, `.Intersect()` |

## 6. Muhim nuqtalar

- `UNION` — **sort+dedup** overhead bor, agar natija allaqachon
  **takrorsiz** ekanligiga ishonch bo'lsa — **UNION ALL** ishlatish
  tavsiya etiladi (tezroq).
- IKKALA so'rov — **ustun soni va tur** mos kelishi **SHART**.
- `EXCEPT`/`INTERSECT` — **ustun tartibi** ham natijaga ta'sir
  qiladi (barcha ustunlar birgalikda solishtiriladi).

## 7. Imtihon savollari

1. `UNION` va `UNION ALL` orasidagi asosiy farq nima?
2. `EXCEPT` va `INTERSECT` qanday farqli natija beradi?
3. Set operatorlarni ishlatish uchun qanday shart bajarilishi
   kerak (ustun soni/turi)?
4. Oracle'da `EXCEPT` o'rniga qanday operator ishlatiladi?
5. EF Core'da `.Concat()` qaysi SQL operatoriga mos keladi?
6. Nima uchun `UNION ALL` odatda `UNION`dan tezroq?
