# ACID Properties, Atomicity, Referential Integrity — Middle D

## 1. Nima? (Ta'rif)

**ACID** — relatsion ma'lumotlar bazasi transactionlarining 4 ta
fundamental xususiyati: **Atomicity** (bo'linmaslik), **Consistency**
(izchillik), **Isolation** (izolyatsiya), **Durability** (barqarorlik).

## 2. Nima uchun kerak?

Bank o'tkazmasi — "hisobdan pul yechish" + "boshqa hisobga qo'shish"
— IKKI amal. Agar birinchisi bajarilib, ikkinchisi **xato** tufayli
bajarilmasa — pul **yo'qoladi**! ACID — bunday holatlarning oldini
oladi.

## 3. Ichida nima sodir bo'ladi? (Mexanizm)

### 3.1 Atomicity — "hammasi yoki hech narsa"

```sql
BEGIN;
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
UPDATE accounts SET balance = balance + 100 WHERE id = 2;
COMMIT; -- IKKALASI HAM saqlanadi, YOKI hech qaysi biri saqlanmaydi

-- Agar 2-chi UPDATE'da xato bo'lsa:
ROLLBACK; -- 1-chi UPDATE HAM bekor qilinadi (hattoki U muvaffaqiyatli bo'lsa ham!)
```

### 3.2 Consistency — integrity constraints saqlanishi

```
Transaction TUGAGANDA — DB HAR DOIM "to'g'ri" (barcha constraint,
trigger, cascading rule bajarilgan) holatda bo'lishi kerak.

Masalan: agar CHECK (balance >= 0) constraint bo'lsa — transaction
BALANCE'ni MANFIY qilishga URINSA, BUTUN transaction ROLLBACK
qilinadi.
```

### 3.3 Isolation — parallel transactionlar

```
Ikki transaction BIR VAQTDA ishlaganda — ular BIR-BIRIGA qanchalik
"KO'RINADI" — bu Isolation Level orqali belgilanadi.
```

**Isolation Level'lar:**

```
Read Uncommitted — BOSHQA transaction'ning HALI COMMIT QILINMAGAN
                    o'zgarishini HAM ko'radi (Dirty Read MUMKIN)

Read Committed   — FAQAT COMMIT QILINGAN ma'lumotni ko'radi
                    (PostgreSQL DEFAULT'i) — lekin BIR TRANSACTION
                    ICHIDA IKKI marta o'qilsa, NATIJA O'ZGARISHI
                    mumkin (Non-Repeatable Read)

Repeatable Read  — Transaction BOSHLANGANDA "suratga olingan"
                    ma'lumot — BUTUN transaction davomida BIR XIL
                    (lekin YANGI qatorlar — Phantom Read MUMKIN)

Serializable     — ENG QATTIQ — xuddi transactionlar KETMA-KET
                    (parallel EMAS) bajarilayotgandek natija beradi
```

### 3.4 Dirty Read, Non-Repeatable Read, Phantom Read

```
Dirty Read:
  T1: UPDATE balance = 500 (HALI COMMIT QILINMAGAN)
  T2: SELECT balance → 500 ni O'QIYDI
  T1: ROLLBACK (balance ASLIGA qaytadi!)
  T2: 500 deb BILGAN qiymat — ASLIDA HECH QACHON MAVJUD BO'LMAGAN!

Non-Repeatable Read:
  T1: SELECT balance → 1000
  T2: UPDATE balance = 500; COMMIT;
  T1: SELECT balance (BIR XIL transaction ICHIDA) → 500 (BOSHQACHA!)

Phantom Read:
  T1: SELECT COUNT(*) FROM employees WHERE age > 25 → 10 ta
  T2: INSERT INTO employees (age=30); COMMIT;
  T1: SELECT COUNT(*) FROM employees WHERE age > 25 (QAYTA) → 11 ta (YANGI qator "paydo bo'ldi")
```

```
| Isolation Level  | Dirty Read | Non-Repeatable | Phantom |
|------------------|------------|----------------|---------|
| Read Uncommitted | Mumkin     | Mumkin         | Mumkin  |
| Read Committed   | Yo'q       | Mumkin         | Mumkin  |
| Repeatable Read  | Yo'q       | Yo'q           | Mumkin* |
| Serializable     | Yo'q       | Yo'q           | Yo'q    |

*PostgreSQL'da Repeatable Read — Phantom Read'dan HAM HIMOYALANGAN
 (boshqa DB'lardan farqli, PostgreSQL'ning kuchli MVCC implementatsiyasi tufayli)
```

### 3.5 Durability — commit bo'lgan ma'lumot yo'qolmasligi

```
COMMIT chaqirilgach — o'zgarish DISKKA (Write-Ahead Log — WAL)
YOZILADI. Server QUVVATI O'CHIB QOLSA HAM — WAL orqali ma'lumot
QAYTA TIKLANADI (recovery).
```

### 3.6 PostgreSQL'da transaction sintaksisi

```sql
BEGIN;
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
UPDATE accounts SET balance = balance + 100 WHERE id = 2;
COMMIT;

-- Xato bo'lsa
BEGIN;
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
-- xato yuz berdi
ROLLBACK;
```

### 3.7 EF Core'da transaction

```csharp
using var transaction = await _context.Database.BeginTransactionAsync();
try
{
    _context.Accounts.First(a => a.Id == 1).Balance -= 100;
    _context.Accounts.First(a => a.Id == 2).Balance += 100;
    await _context.SaveChangesAsync();
    await transaction.CommitAsync();
}
catch
{
    await transaction.RollbackAsync();
    throw;
}
```

```
⚠️ MUHIM: BITTA SaveChangesAsync() chaqiruvi — O'ZI-O'ZIDAN
   ALLAQACHON BITTA transaction (barcha o'zgarishlar BIRGA
   COMMIT/ROLLBACK bo'ladi). Explicit `BeginTransactionAsync()`
   FAQAT bir nechta SEPARATE SaveChangesAsync() chaqiruvini BITTA
   transaction'ga BIRLASHTIRISH kerak bo'lganda ZARUR.
```

### 3.8 Referential Integrity — Foreign Key constraint

```sql
CREATE TABLE employees (
    id INT PRIMARY KEY,
    department_id INT REFERENCES departments(id)
);

-- ❌ Mavjud bo'lmagan department_id bilan INSERT — XATO beradi
INSERT INTO employees (id, department_id) VALUES (1, 999); -- department 999 yo'q!
```

### 3.9 `ON DELETE` variantlari

```
CASCADE     — Ota o'chirilsa, BOLA yozuvlar HAM avtomatik o'chadi
RESTRICT    — Bola yozuv mavjud bo'lsa — ota O'CHIRILMAYDI (xato)
SET NULL    — Ota o'chirilsa, bola'dagi FK NULL bo'ladi
NO ACTION   — RESTRICT'ga o'xshash, lekin tekshiruv KECHIKTIRILGAN
```

## 4. Kod — savepoint bilan qisman rollback

```sql
BEGIN;
INSERT INTO employees (full_name) VALUES ('Orzibek');
SAVEPOINT sp1;
INSERT INTO employees (full_name) VALUES ('Xato yozuv');
ROLLBACK TO sp1; -- Faqat SAVEPOINT'dan KEYINGI amal bekor qilinadi!
COMMIT; -- "Orzibek" SAQLANADI, "Xato yozuv" SAQLANMAYDI
```

## 5. Qachon ishlatish kerak?

| Vaziyat | Isolation Level |
|---|---|
| Oddiy CRUD, standart holat | Read Committed (default) |
| Hisobot, bir marta o'qib, o'zgartirmaslik | Repeatable Read |
| Moliyaviy, juda kritik hisob-kitob | Serializable |
| Bir nechta amalni bitta bo'linmas birlik qilish | Explicit transaction |

## 6. Muhim nuqtalar

- Yuqori Isolation Level (Serializable) — **xavfsizroq**, lekin
  **sekinroq** va ko'proq **deadlock** xavfi bor — tradeoff.
- `ON DELETE CASCADE` — qulay, lekin **XAVFLI** (tasodifan katta
  hajmda ma'lumot yo'qotish mumkin) — ehtiyotkorlik bilan ishlatilishi
  kerak.
- EF Core'da bitta `SaveChangesAsync()` — o'zi-o'zidan ALLAQACHON
  atomik.

## 7. Imtihon savollari

1. ACID'ning 4 ta xususiyatini ayting va har birini qisqacha
   tushuntiring.
2. Dirty Read, Non-Repeatable Read va Phantom Read orasidagi farqni
   misol bilan tushuntiring.
3. PostgreSQL default Isolation Level'i qaysi va u qanday muammolarga
   yo'l qo'yishi mumkin?
4. `ON DELETE CASCADE` va `RESTRICT` orasidagi farq nima va qaysi
   qachon xavfli?
5. EF Core'da bitta `SaveChangesAsync()` chaqiruvi nima uchun
   allaqachon atomik hisoblanadi?
6. Savepoint nima va u qanday qisman rollback imkonini beradi?
