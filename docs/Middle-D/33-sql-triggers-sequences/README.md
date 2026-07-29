# SQL Trigger, Sequence — Middle D

## 1. Nima? (Ta'rif)

**Trigger** — muayyan jadval hodisasi (INSERT/UPDATE/DELETE)
yuz berganda **avtomatik** ishga tushuvchi DB kodi. **Sequence** —
ketma-ket, avtomatik oshuvchi son generatsiya qiluvchi DB obyekti
(`SERIAL`ning "qopqoq ostidagi" mexanizmi).

## 2. Nima uchun kerak?

Audit log (kim, qachon, nimani o'zgartirdi) — agar HAR BIR
application kodida qo'lda yozilsa, **unutilishi mumkin**. Trigger —
DB darajasida, **hech qanday application kodidan qat'i nazar**,
har doim ishga tushishini kafolatlaydi.

## 3. Ichida nima sodir bo'ladi? (Mexanizm)

### 3.1 BEFORE vs AFTER trigger

```
BEFORE — amal BAJARILISHIDAN OLDIN ishga tushadi (masalan, qiymatni
         O'ZGARTIRISH yoki AMALNI BEKOR QILISH mumkin)
AFTER  — amal BAJARILGANDAN KEYIN ishga tushadi (masalan, AUDIT
         yozuvi qo'shish, boshqa jadvalni YANGILASH)
```

### 3.2 `NEW` va `OLD` — trigger ichida ma'lumot

```
INSERT — faqat NEW mavjud (yangi qiymat)
UPDATE — HAM NEW (yangi), HAM OLD (eski) mavjud
DELETE — faqat OLD mavjud (o'chirilayotgan qiymat)
```

### 3.3 PostgreSQL trigger sintaksisi — to'liq misol

```sql
-- 1. Trigger FUNKSIYASI yaratiladi
CREATE OR REPLACE FUNCTION audit_employee_changes()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'UPDATE' THEN
        INSERT INTO employee_audit_log (employee_id, old_salary, new_salary, changed_at)
        VALUES (OLD.id, OLD.salary, NEW.salary, NOW());
    ELSIF TG_OP = 'DELETE' THEN
        INSERT INTO employee_audit_log (employee_id, old_salary, new_salary, changed_at)
        VALUES (OLD.id, OLD.salary, NULL, NOW());
    END IF;
    RETURN NEW; -- UPDATE/INSERT uchun; DELETE uchun OLD qaytariladi
END;
$$ LANGUAGE plpgsql;

-- 2. Trigger — funksiyani JADVAL hodisasiga BOG'LAYDI
CREATE TRIGGER trg_audit_employee
AFTER UPDATE OR DELETE ON employees
FOR EACH ROW
EXECUTE FUNCTION audit_employee_changes();
```

`TG_OP` — trigger'ni ISHGA TUSHIRGAN operatsiya turini (`INSERT`,
`UPDATE`, `DELETE`) bildiradi.

### 3.4 BEFORE trigger — qiymatni o'zgartirish misoli

```sql
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW(); -- INSERT/UPDATE'dan OLDIN, qiymat AVTOMATIK o'rnatiladi
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_set_updated_at
BEFORE UPDATE ON employees
FOR EACH ROW
EXECUTE FUNCTION set_updated_at();
```

Bu — **har UPDATE'da** `updated_at` ustunini application kodidan
qat'i nazar AVTOMATIK yangilaydi (dasturchi buni **unutsa** ham
ishlaydi).

### 3.5 Trigger vs Application code — qachon qaysi

```
Trigger:
  ✅ HAR DOIM ishlaydi (application'dan qat'i nazar — hatto to'g'ridan
     SQL orqali o'zgartirilsa ham)
  ✅ Audit, ma'lumot izchilligi (consistency) uchun IDEAL
  ❌ "YASHIRIN" mantiq — kod o'quvchisi Controller/Handler'da
     KO'RMAYDI, DEBUG QILISH QIYINROQ
  ❌ Ko'p trigger — PERFORMANCE'ga ta'sir qilishi mumkin

Application code:
  ✅ KO'RINADIGAN, TEST QILISH OSON
  ✅ Business logic BILAN birga JOYLASHGAN (bir joyda)
  ❌ Dasturchi UNUTISHI yoki BOSHQA yo'l bilan (masalan raw SQL) CHETLAB
     O'TISHI mumkin
```

**Tavsiya:** Audit log, ma'lumot IZCHILLIGINI ta'minlash — Trigger.
Biznes qoida (masalan email formatini tekshirish) — Application
code.

### 3.6 Sequence — `SERIAL` bilan farqi

```sql
CREATE SEQUENCE employee_id_seq START 1 INCREMENT 1;

CREATE TABLE employees (
    id INT DEFAULT nextval('employee_id_seq') PRIMARY KEY
);

-- SERIAL — YUQORIDAGI IKKI QATORNI "QISQARTMASI":
CREATE TABLE employees (
    id SERIAL PRIMARY KEY -- ICHKARIDA AVTOMATIK sequence yaratadi!
);
```

`SERIAL` — aslida **Sequence + Default qiymat** ning **qisqartmasi**
— PostgreSQL "qopqoq ostida" `employees_id_seq` nomli Sequence
yaratadi.

### 3.7 `NEXTVAL`, `CURRVAL`

```sql
SELECT nextval('employee_id_seq'); -- Keyingi qiymatni OLADI VA Sequence'ni OSHIRADI
SELECT currval('employee_id_seq'); -- OXIRGI olingan qiymatni (SHU SESSIYADA) qaytaradi
```

### 3.8 Sequence reset qilish

```sql
ALTER SEQUENCE employee_id_seq RESTART WITH 1;
```

### 3.9 Gap muammosi — sequence da

```
Sequence — TRANSACTION ROLLBACK bo'lsa ham, QIYMATNI QAYTARIB
OLMAYDI (chunki performance uchun sequence — TRANSACTION'DAN
MUSTAQIL ishlaydi):

BEGIN;
INSERT INTO employees ... -- id=5 OLADI
ROLLBACK; -- INSERT bekor bo'ldi, LEKIN id=5 "YO'QOLDI"!

BEGIN;
INSERT INTO employees ... -- id=6 (5 emas, 5 "GAP" bo'lib qoladi)
COMMIT;
```

```
⚠️ Bu — XATO EMAS, balki ATAYLAB QILINGAN DIZAYN qarori — agar
   Sequence TRANSACTION bilan BOG'LANGAN bo'lsa, PARALLEL
   INSERT'lar bir-birini KUTISHGA MAJBUR bo'lardi (performance
   YOMONLASHARDI). "Gap" (uzilishlar) — Primary Key uchun ODATDA
   MUAMMO EMAS (faqat NOYOBLIK muhim, KETMA-KETLIK EMAS).
```

## 4. Kod — Sequence bilan custom raqamlash (masalan buyurtma raqami)

```sql
CREATE SEQUENCE order_number_seq START 1000;

CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    order_number TEXT DEFAULT ('ORD-' || nextval('order_number_seq'))
);
```

## 5. Qachon ishlatish kerak?

| Vaziyat | Yechim |
|---|---|
| Audit log, ma'lumot izchilligi | Trigger |
| `updated_at`ni avtomatik yangilash | BEFORE trigger |
| Primary Key avtomatik oshirish | `SERIAL` (yoki `IDENTITY`) |
| Custom raqamlash (masalan buyurtma №) | Alohida Sequence |
| Biznes qoida, ko'rinadigan bo'lishi kerak | Application code |

## 6. Muhim nuqtalar

- Trigger'ni **haddan ortiq** ishlatish — "yashirin mantiq"
  ko'payishiga olib keladi, kod bazasini tushunish qiyinlashadi.
- Sequence'dagi "gap" (uzilish) — **normal holat**, muammo emas —
  Primary Key uchun faqat noyoblik muhim.
- PostgreSQL'da `SERIAL` — zamonaviy loyihalarda `GENERATED ALWAYS
  AS IDENTITY` bilan almashtirilishi tavsiya etiladi (SQL standartiga
  yaqinroq).

## 7. Imtihon savollari

1. BEFORE va AFTER trigger orasidagi farq nima?
2. `NEW` va `OLD` qachon mavjud bo'ladi (INSERT/UPDATE/DELETE
   kontekstida)?
3. Trigger va Application code'da biznes mantiq yozish orasidagi
   tradeoff'larni tushuntiring.
4. `SERIAL` aslida nima ekanini (Sequence bilan bog'liqligi)
   tushuntiring.
5. Sequence'da "gap" (uzilish) muammosi nima uchun yuzaga keladi va
   nima uchun bu odatda muammo hisoblanmaydi?
6. Audit log uchun nima uchun Trigger Application code'dan
   ishonchliroq?
