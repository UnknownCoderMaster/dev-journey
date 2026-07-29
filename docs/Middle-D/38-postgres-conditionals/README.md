# PostgreSQL Shart Operatorlari (IF ELSE, CASE) — Middle D

## 1. Nima? (Ta'rif)

Shart operatorlari — SQL/PL/pgSQL kodida **shartga qarab** turli
yo'l tanlash imkonini beruvchi konstruksiyalar: `IF/ELSIF/ELSE`
(PL/pgSQL), `CASE` (SQL va PL/pgSQL), `COALESCE`, `NULLIF`,
`GREATEST`, `LEAST`.

## 2. Nima uchun kerak?

Ma'lumotni **shartga qarab** turlicha ko'rsatish yoki hisoblash —
oddiy `SELECT` bilan ifodalab bo'lmaydi. Bu operatorlar — SQL
darajasida **shartli mantiq** yozish imkonini beradi.

## 3. Ichida nima sodir bo'ladi? (Mexanizm)

### 3.1 PL/pgSQL'da `IF ... THEN ... ELSIF ... ELSE ... END IF`

```sql
CREATE OR REPLACE FUNCTION get_employee_category(age INT)
RETURNS TEXT AS $$
BEGIN
    IF age < 25 THEN
        RETURN 'Yosh mutaxassis';
    ELSIF age BETWEEN 25 AND 40 THEN
        RETURN 'Tajribali';
    ELSE
        RETURN 'Yuqori tajribali';
    END IF;
END;
$$ LANGUAGE plpgsql;
```

### 3.2 `CASE` — SQL va PL/pgSQL'da

```sql
-- Oddiy CASE (bitta ustunni qiymatlar bilan solishtirish)
SELECT full_name,
    CASE department_id
        WHEN 1 THEN 'IT'
        WHEN 2 THEN 'HR'
        ELSE 'Boshqa'
    END AS department_name
FROM employees;

-- Qidiruv CASE (istalgan shart)
SELECT full_name,
    CASE
        WHEN age < 25 THEN 'Yosh'
        WHEN age BETWEEN 25 AND 40 THEN 'O''rta'
        ELSE 'Tajribali'
    END AS category
FROM employees;
```

`CASE` — **SQL ifodasi** sifatida `SELECT`, `WHERE`, `ORDER BY`
ichida ISHLATILISHI mumkin; `IF/ELSE` — faqat **PL/pgSQL** funksiya
tanasida ISHLATILADI (bevosita oddiy SQL'da EMAS).

### 3.3 `COALESCE` — null handling

```sql
SELECT COALESCE(nick_name, full_name, 'Noma''lum') AS display_name FROM employees;
```

`COALESCE(a, b, c, ...)` — chapdan o'ngga, **birinchi NULL bo'lmagan**
qiymatni qaytaradi.

### 3.4 `NULLIF` — null qaytarish

```sql
SELECT NULLIF(department_id, 0) FROM employees; -- Agar department_id = 0 bo'lsa → NULL
SELECT salary / NULLIF(hours_worked, 0) AS rate FROM employees; -- 0'ga bo'linish XATOSINI oldini oladi
```

`NULLIF(a, b)` — agar `a == b` bo'lsa `NULL` qaytaradi, aks holda
`a`ni qaytaradi.

### 3.5 `GREATEST`, `LEAST`

```sql
SELECT GREATEST(salary, 1000000) FROM employees; -- Minimal maosh KAFOLATI
SELECT LEAST(bonus, 5000000) FROM employees;      -- Maksimal chegara
```

### 3.6 Boolean ifodalar — AND, OR, NOT

```sql
SELECT * FROM employees WHERE (age > 25 AND is_active = true) OR department_id = 1;
SELECT * FROM employees WHERE NOT is_active;
```

```
PostgreSQL'da BOOLEAN — three-valued logic (TRUE, FALSE, NULL):
  NULL AND TRUE  → NULL (noaniq!)
  NULL OR TRUE   → TRUE
  NOT NULL       → NULL

⚠️ `WHERE column = NULL` — HECH QACHON true bo'lmaydi (yuqoridagi
   sababga ko'ra) — `IS NULL` ishlatilishi SHART.
```

### 3.7 Funksiya ichida shartlar — to'liq misol

```sql
CREATE OR REPLACE FUNCTION calculate_tax(salary DECIMAL)
RETURNS DECIMAL AS $$
DECLARE
    tax_rate DECIMAL;
BEGIN
    IF salary <= 3000000 THEN
        tax_rate := 0.0;
    ELSIF salary <= 10000000 THEN
        tax_rate := 0.12;
    ELSE
        tax_rate := 0.20;
    END IF;

    RETURN salary * tax_rate;
END;
$$ LANGUAGE plpgsql;
```

### 3.8 `IIF` — SQL Server bilan farqi

```
SQL Server: SELECT IIF(age > 18, 'Kattalar', 'Bola') FROM employees;
PostgreSQL: IIF FUNKSIYASI YO'Q — CASE ISHLATILADI:
  SELECT CASE WHEN age > 18 THEN 'Kattalar' ELSE 'Bola' END FROM employees;
```

PostgreSQL'da `IIF` **mavjud emas** — bu SQL Server'ga xos
qulaylik funksiyasi, PostgreSQL'da har doim `CASE` ishlatiladi.

## 4. Kod — real ERP misoli (bonus hisoblash)

```sql
SELECT
    full_name,
    salary,
    CASE
        WHEN years_of_service >= 10 THEN salary * 0.2
        WHEN years_of_service >= 5 THEN salary * 0.1
        ELSE 0
    END AS loyalty_bonus,
    COALESCE(performance_bonus, 0) AS performance_bonus
FROM employees;
```

## 5. Qachon ishlatish kerak?

| Vaziyat | Yechim |
|---|---|
| SELECT ichida shartli qiymat | `CASE` |
| Funksiya/procedure ichida murakkab mantiq | `IF/ELSIF/ELSE` |
| NULL bo'lsa default qiymat | `COALESCE` |
| Nolga bo'linishdan himoya | `NULLIF` |
| Min/Max chegara qo'yish | `GREATEST`/`LEAST` |

## 6. Muhim nuqtalar

- `= NULL` — HECH QACHON ishlamaydi, `IS NULL`/`IS NOT NULL`
  ishlatilishi SHART.
- `CASE` — SQL ifodasi ichida, `IF/ELSE` — faqat PL/pgSQL funksiya
  tanasida ishlaydi — bu ikkalasini CHALKASHTIRMASLIK kerak.
- PostgreSQL'da `IIF` YO'Q — har doim `CASE` ishlatiladi.

## 7. Imtihon savollari

1. `CASE` va PL/pgSQL `IF/ELSE` qayerda ishlatiladi — farqini
   tushuntiring.
2. `COALESCE` va `NULLIF` orasidagi farq nima?
3. Nima uchun `WHERE column = NULL` hech qachon ishlamaydi?
4. PostgreSQL'da `IIF` mavjudmi? SQL Server'dan qanday farq bor?
5. `GREATEST`/`LEAST` qachon foydali bo'ladi?
