# PostgreSQL Takrorlash (LOOP, FOR, WHILE) — Middle D

## 1. Nima? (Ta'rif)

PL/pgSQL — protsedural sikl konstruksiyalarini taqdim etadi:
`LOOP`, `WHILE`, `FOR` (raqamli va cursor), `FOREACH` (massiv
bo'yicha).

## 2. Nima uchun kerak?

Oddiy SQL — **set-based** (butun to'plam ustida ishlaydi), lekin
ba'zi holatlar (masalan, bulk generatsiya, murakkab qadam-baqadam
qayta ishlash) — **qator-qator** (row-by-row) yondashuv talab
qiladi — bu holatda PL/pgSQL sikl operatorlar kerak bo'ladi.

## 3. Ichida nima sodir bo'ladi? (Mexanizm)

### 3.1 `LOOP ... END LOOP` — cheksiz loop, `EXIT` bilan chiqish

```sql
DO $$
DECLARE
    counter INT := 0;
BEGIN
    LOOP
        counter := counter + 1;
        EXIT WHEN counter > 5; -- Shart bajarilganda chiqish
        RAISE NOTICE 'Counter: %', counter;
    END LOOP;
END $$;
```

### 3.2 `WHILE condition LOOP ... END LOOP`

```sql
DO $$
DECLARE
    counter INT := 1;
BEGIN
    WHILE counter <= 5 LOOP
        RAISE NOTICE 'Counter: %', counter;
        counter := counter + 1;
    END LOOP;
END $$;
```

### 3.3 `FOR i IN 1..10 LOOP` — oddiy for

```sql
DO $$
BEGIN
    FOR i IN 1..10 LOOP
        RAISE NOTICE 'Iteration: %', i;
    END LOOP;
END $$;

-- Teskari va qadam bilan
FOR i IN REVERSE 10..1 BY 2 LOOP
    RAISE NOTICE 'i = %', i;
END LOOP;
```

### 3.4 `FOR record IN SELECT ... LOOP` — cursor loop

```sql
DO $$
DECLARE
    emp RECORD;
BEGIN
    FOR emp IN SELECT id, full_name, salary FROM employees WHERE is_active = true LOOP
        RAISE NOTICE '% maoshi: %', emp.full_name, emp.salary;
    END LOOP;
END $$;
```

Bu — **eng ko'p ishlatiladigan** sikl turi: `SELECT` natijasidagi
har bir qatorni **BIR-BIR** qayta ishlash uchun (masalan har xodim
uchun murakkab hisob-kitob).

### 3.5 `FOREACH element IN ARRAY ... LOOP` — massiv bo'yicha

```sql
DO $$
DECLARE
    dept_ids INT[] := ARRAY[1, 2, 3, 5];
    dept_id INT;
BEGIN
    FOREACH dept_id IN ARRAY dept_ids LOOP
        RAISE NOTICE 'Bo''lim ID: %', dept_id;
    END LOOP;
END $$;
```

### 3.6 `EXIT`, `CONTINUE` — loop boshqarish

```sql
FOR i IN 1..10 LOOP
    CONTINUE WHEN i % 2 = 0; -- Juft sonlarni O'TKAZIB YUBORISH
    EXIT WHEN i > 7;          -- 7 dan katta bo'lsa TO'XTATISH
    RAISE NOTICE 'i = %', i;  -- Faqat 1, 3, 5, 7 chiqadi
END LOOP;
```

### 3.7 `RETURN NEXT` — jadval qaytaruvchi funksiyada

```sql
CREATE OR REPLACE FUNCTION get_employee_ranks()
RETURNS TABLE(id INT, full_name TEXT, rank_position INT) AS $$
DECLARE
    emp RECORD;
    position INT := 0;
BEGIN
    FOR emp IN SELECT e.id, e.full_name FROM employees e ORDER BY e.salary DESC LOOP
        position := position + 1;
        id := emp.id;
        full_name := emp.full_name;
        rank_position := position;
        RETURN NEXT; -- Bu qatorni NATIJAGA QO'SHISH (lekin FUNKSIYADAN CHIQMASLIK)
    END LOOP;
    RETURN;
END;
$$ LANGUAGE plpgsql;

SELECT * FROM get_employee_ranks();
```

`RETURN NEXT` — funksiya **bir nechta qator** qaytarishi kerak
bo'lganda, har iteratsiyada **navbatdagi qatorni** natija to'plamiga
qo'shadi (`RETURN` bilan farqli — funksiya **davom etadi**).

### 3.8 Bulk insert misoli — loop bilan

```sql
DO $$
DECLARE
    i INT;
BEGIN
    FOR i IN 1..1000 LOOP
        INSERT INTO test_data (value) VALUES (i * 2);
    END LOOP;
END $$;
```

```
⚠️ MUHIM: LOOP orqali 1000 ta ALOHIDA INSERT — SEKIN (har biri
   alohida operatsiya). Katta hajmda ma'lumot generatsiya qilish
   uchun — SET-BASED yondashuv TEZROQ:

INSERT INTO test_data (value)
SELECT i * 2 FROM generate_series(1, 1000) AS i; -- BIR SO'ROVDA, SEKINROQ EMAS!
```

## 4. Kod — real ERP misoli: oylik maoshni qadam-baqadam hisoblash

```sql
CREATE OR REPLACE PROCEDURE process_monthly_payroll()
AS $$
DECLARE
    emp RECORD;
    net_salary DECIMAL;
BEGIN
    FOR emp IN SELECT id, salary FROM employees WHERE is_active = true LOOP
        net_salary := emp.salary * 0.88; -- soliqdan keyin

        INSERT INTO payroll_history (employee_id, gross, net, processed_at)
        VALUES (emp.id, emp.salary, net_salary, NOW());
    END LOOP;

    RAISE NOTICE 'Oylik hisob-kitob yakunlandi';
END;
$$ LANGUAGE plpgsql;

CALL process_monthly_payroll();
```

## 5. Qachon ishlatish kerak?

| Vaziyat | Yechim |
|---|---|
| Har qatorni BIR-BIR qayta ishlash (murakkab mantiq) | `FOR record IN SELECT` |
| Massiv elementlarini aylanib chiqish | `FOREACH` |
| Aniq son marta takrorlash | `FOR i IN 1..N` |
| Noma'lum son marta, shartga bog'liq | `WHILE`/`LOOP` + `EXIT` |
| Sof set-based operatsiya (masalan bulk insert) | LOOP EMAS, oddiy SQL/`generate_series` |

## 6. Muhim nuqtalar

- SQL — tabiatan **set-based**, sikl (loop) — **oxirgi variant**
  bo'lishi kerak, agar oddiy SQL bilan yechish MUMKIN bo'lsa (masalan
  `generate_series`, `UPDATE ... FROM`), loop **KAMROQ SAMARALI**.
- `RETURN NEXT` — funksiyadan **bir nechta qator** qaytarishning
  standart usuli.
- Katta hajmli LOOP — HAR ITERATSIYADA transaction ICHIDA bo'ladi
  (agar `COMMIT` chaqirilmasa) — juda uzoq LOOP **lock**larni uzoq
  muddat ushlab turishi mumkin.

## 7. Imtihon savollari

1. `LOOP`, `WHILE` va `FOR` orasidagi farqni tushuntiring.
2. `FOR record IN SELECT ... LOOP` qachon ishlatiladi?
3. `RETURN NEXT` nima vazifani bajaradi va oddiy `RETURN`dan qanday
   farq qiladi?
4. Nima uchun katta hajmli bulk insert uchun LOOP o'rniga
   `generate_series` bilan set-based yondashuv tavsiya etiladi?
5. `EXIT` va `CONTINUE` orasidagi farq nima?
