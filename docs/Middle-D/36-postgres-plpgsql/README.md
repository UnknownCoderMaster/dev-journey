# PL/pgSQL — Functions, Procedures — Middle D

## 1. Nima? (Ta'rif)

**PL/pgSQL** — PostgreSQL'ning **protsedural** dasturlash tili — SQL
ustiga shart (IF), sikl (LOOP), o'zgaruvchi kabi dasturlash
konstruksiyalarini qo'shadi. **Function** — qiymat qaytaradi.
**Procedure** — qiymat qaytarmaydi, lekin o'z ichida transaction
boshqarishi mumkin.

## 2. Nima uchun kerak?

Ba'zi murakkab hisob-kitoblar (masalan, oylik maosh hisoblash — bir
nechta jadval, shart, sikl kerak) — C# kodida amalga oshirilsa, DB
bilan **ko'p round-trip** kerak bo'ladi. PL/pgSQL — bu logikani
**to'g'ridan DB ichida**, bir marotaba bajarish imkonini beradi.

## 3. Ichida nima sodir bo'ladi? (Mexanizm)

### 3.1 Function vs Procedure

```
Function  — QIYMAT QAYTARADI (RETURNS), SELECT ichida ishlatilishi
             mumkin, O'ZI transaction OCHA/YOPA OLMAYDI
Procedure — QIYMAT QAYTARMAYDI (CALL orqali chaqiriladi), O'ZI
             ICHIDA COMMIT/ROLLBACK qilishi mumkin
```

### 3.2 CREATE FUNCTION sintaksisi

```sql
CREATE OR REPLACE FUNCTION calculate_bonus(employee_id INT)
RETURNS DECIMAL AS $$
DECLARE
    base_salary DECIMAL;
    years_of_service INT;
    bonus DECIMAL;
BEGIN
    SELECT salary, EXTRACT(YEAR FROM AGE(NOW(), hired_at))
    INTO base_salary, years_of_service
    FROM employees WHERE id = employee_id;

    bonus := base_salary * 0.1 * years_of_service;
    RETURN bonus;
END;
$$ LANGUAGE plpgsql;

-- Chaqirish
SELECT calculate_bonus(42);
```

### 3.3 CREATE PROCEDURE sintaksisi

```sql
CREATE OR REPLACE PROCEDURE transfer_funds(from_id INT, to_id INT, amount DECIMAL)
AS $$
BEGIN
    UPDATE accounts SET balance = balance - amount WHERE id = from_id;
    UPDATE accounts SET balance = balance + amount WHERE id = to_id;
    COMMIT; -- Procedure ICHIDA transaction boshqarish MUMKIN!
END;
$$ LANGUAGE plpgsql;

-- Chaqirish
CALL transfer_funds(1, 2, 100);
```

### 3.4 Parametrlar — IN, OUT, INOUT

```sql
CREATE OR REPLACE FUNCTION get_employee_stats(
    IN dept_id INT,
    OUT total_count INT,
    OUT avg_salary DECIMAL
) AS $$
BEGIN
    SELECT COUNT(*), AVG(salary) INTO total_count, avg_salary
    FROM employees WHERE department_id = dept_id;
END;
$$ LANGUAGE plpgsql;

SELECT * FROM get_employee_stats(5); -- total_count VA avg_salary IKKALASI qaytariladi
```

### 3.5 `RETURNS TABLE` — jadval qaytaruvchi funksiya

```sql
CREATE OR REPLACE FUNCTION get_high_earners(min_salary DECIMAL)
RETURNS TABLE(id INT, full_name TEXT, salary DECIMAL) AS $$
BEGIN
    RETURN QUERY
    SELECT e.id, e.full_name, e.salary
    FROM employees e
    WHERE e.salary > min_salary;
END;
$$ LANGUAGE plpgsql;

SELECT * FROM get_high_earners(10000000);
```

### 3.6 Exception handling — `EXCEPTION` blok

```sql
CREATE OR REPLACE FUNCTION safe_divide(a DECIMAL, b DECIMAL)
RETURNS DECIMAL AS $$
BEGIN
    RETURN a / b;
EXCEPTION
    WHEN division_by_zero THEN
        RAISE NOTICE 'Nolga bo''lish xatosi, 0 qaytarilmoqda';
        RETURN 0;
    WHEN OTHERS THEN
        RAISE EXCEPTION 'Kutilmagan xato: %', SQLERRM;
END;
$$ LANGUAGE plpgsql;
```

### 3.7 `RAISE NOTICE`, `RAISE EXCEPTION`

```sql
RAISE NOTICE 'Debug xabari: qiymat = %', some_value; -- Faqat OGOHLANTIRISH, davom etadi
RAISE EXCEPTION 'Jiddiy xato: %', error_message;       -- Funksiyani TO'XTATADI, transaction ROLLBACK
```

### 3.8 Cursor bilan ishlash

```sql
CREATE OR REPLACE FUNCTION process_all_employees()
RETURNS VOID AS $$
DECLARE
    emp_cursor CURSOR FOR SELECT id, salary FROM employees;
    emp_record RECORD;
BEGIN
    OPEN emp_cursor;
    LOOP
        FETCH emp_cursor INTO emp_record;
        EXIT WHEN NOT FOUND;
        UPDATE employees SET salary = salary * 1.1 WHERE id = emp_record.id;
    END LOOP;
    CLOSE emp_cursor;
END;
$$ LANGUAGE plpgsql;
```

Cursor — qatorlarni **BIR-BIR, qo'lda** boshqarish kerak bo'lganda
ishlatiladi (odatda oddiy `FOR ... IN SELECT` sikli YETARLI va
soddaroq).

### 3.9 EF Core'da function chaqirish

```csharp
var results = await _context.Employees
    .FromSqlInterpolated($"SELECT * FROM get_high_earners({minSalary})")
    .ToListAsync();

// Scalar function
var bonus = await _context.Database
    .SqlQueryRaw<decimal>("SELECT calculate_bonus({0})", employeeId)
    .FirstAsync();
```

## 4. Kod — real ERP misoli

```sql
CREATE OR REPLACE FUNCTION calculate_monthly_payroll(month_date DATE)
RETURNS TABLE(employee_id INT, gross_salary DECIMAL, tax DECIMAL, net_salary DECIMAL) AS $$
BEGIN
    RETURN QUERY
    SELECT
        e.id,
        e.salary,
        e.salary * 0.12, -- soliq
        e.salary * 0.88
    FROM employees e
    WHERE e.is_active = true;
END;
$$ LANGUAGE plpgsql;
```

## 5. Qachon ishlatish kerak?

| Vaziyat | Yechim |
|---|---|
| Murakkab, ko'p jadvalli hisob-kitob, DB'da bajarilishi kerak | Function/Procedure |
| Oddiy, ilova mantig'ining bir qismi | Application code (C#) |
| Transaction'ni DB ichida boshqarish kerak | Procedure |
| Jadval formatida murakkab natija qaytarish | `RETURNS TABLE` |

## 6. Muhim nuqtalar

- PL/pgSQL kodini **ortiqcha** ishlatish — biznes mantiqni "yashirin"
  qilib, C# kod bazasidan **ajratib** yuborishi mumkin — faqat
  DB-intensiv, murakkab hisob-kitoblar uchun tavsiya etiladi.
- Function/Procedure — **versiyalash** (migration bilan) qiyinroq —
  C# kod review jarayonidan farqli.
- `RAISE EXCEPTION` — transaction'ni **avtomatik ROLLBACK** qiladi.

## 7. Imtihon savollari

1. Function va Procedure orasidagi asosiy farq nima?
2. `RETURNS TABLE` qachon ishlatiladi?
3. `IN`, `OUT`, `INOUT` parametrlar orasidagi farq nima?
4. `RAISE NOTICE` va `RAISE EXCEPTION` orasidagi farq nima?
5. EF Core'dan PostgreSQL function qanday chaqiriladi?
6. Qachon biznes mantiqni PL/pgSQL'da, qachon C#'da yozish
   tavsiya etiladi?
