# SQL — Filtering, Grouping, Aggregate, Constraints — Junior C

## 1. Filtering — WHERE

```sql
SELECT * FROM employees
WHERE age > 25
  AND department_id = 3
  OR position = 'Manager';

-- IN
SELECT * FROM employees WHERE department_id IN (1, 2, 3);

-- BETWEEN
SELECT * FROM employees WHERE age BETWEEN 25 AND 35;

-- LIKE
SELECT * FROM employees WHERE full_name LIKE 'Orz%';

-- IS NULL
SELECT * FROM employees WHERE updated_at IS NULL;

-- EXISTS
SELECT * FROM departments d
WHERE EXISTS (
    SELECT 1 FROM employees e WHERE e.department_id = d.id
);
```

## 2. Tartiblash — ORDER BY

```sql
SELECT * FROM employees ORDER BY full_name ASC;
SELECT * FROM employees ORDER BY age DESC;
SELECT * FROM employees ORDER BY department_id, age;
SELECT * FROM employees ORDER BY age DESC NULLS LAST;
SELECT * FROM employees ORDER BY age ASC NULLS FIRST;
```

## 3. DISTINCT

```sql
SELECT DISTINCT department_id FROM employees;
SELECT COUNT(DISTINCT department_id) FROM employees;
```

## 4. Aggregate funksiyalar

```sql
SELECT
    COUNT(*)           AS total,
    COUNT(updated_at)  AS updated,
    SUM(salary)        AS total_salary,
    AVG(salary)        AS avg_salary,
    MIN(salary)        AS min_salary,
    MAX(salary)        AS max_salary
FROM employees;
```

## 5. GROUP BY va HAVING

```sql
SELECT department_id, COUNT(*) AS count
FROM employees
GROUP BY department_id
HAVING COUNT(*) > 5;

-- WHERE vs HAVING:
-- WHERE  → qatorlarni filtrlaydi (GROUP BY DAN OLDIN)
-- HAVING → guruhlarni filtrlaydi (GROUP BY DAN KEYIN)
```

## 6. Shart ifodalari

```sql
-- CASE
SELECT full_name,
    CASE
        WHEN age < 25 THEN 'Yosh'
        WHEN age < 40 THEN 'O''rta'
        ELSE 'Tajribali'
    END AS category
FROM employees;

-- COALESCE — birinchi null bo'lmagan qiymat
SELECT COALESCE(updated_at, created_at) AS last_modified FROM employees;

-- NULLIF — teng bo'lsa null qaytaradi
SELECT NULLIF(salary, 0) AS salary FROM employees;

-- GREATEST / LEAST
SELECT GREATEST(salary, 1000000) FROM employees;
SELECT LEAST(salary, 5000000) FROM employees;
```

## 7. Constraints

```sql
CREATE TABLE employees (
    id          SERIAL          PRIMARY KEY,
    full_name   VARCHAR(100)    NOT NULL,
    email       VARCHAR(200)    NOT NULL UNIQUE,
    age         INT             CHECK (age >= 18 AND age <= 65),
    position_id INT             NOT NULL
        REFERENCES positions(id) ON DELETE RESTRICT,
    salary      DECIMAL(15, 2)  DEFAULT 0 CHECK (salary >= 0)
);
```

## 8. Data Typing — PostgreSQL

```sql
-- Raqamlar
SMALLINT, INTEGER/INT, BIGINT
DECIMAL(p,s) / NUMERIC(p,s)  -- Moliyaviy hisob uchun
REAL, DOUBLE PRECISION        -- Float (aniqsiz)
SERIAL                        -- Avtomatik oshuvchi INT

-- Matn
VARCHAR(n), CHAR(n), TEXT

-- Sana/Vaqt
DATE, TIME, TIMESTAMP, TIMESTAMPTZ, INTERVAL

-- Boshqalar
BOOLEAN, UUID, JSONB, JSON, ARRAY
```

## 9. Imtihon savollari

1. `WHERE` va `HAVING` orasidagi farq nima?
2. `EXISTS` va `IN` orasidagi farq nima?
3. `COALESCE` va `NULLIF` nima qiladi?
4. `DECIMAL` va `FLOAT` orasidagi farq nima? Moliyaviy hisob uchun qaysi?
5. `COUNT(*)` va `COUNT(column)` orasidagi farq nima?
6. `NULLS LAST` nima uchun kerak?
