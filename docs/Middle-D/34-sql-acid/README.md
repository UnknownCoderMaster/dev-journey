# SQL — ACID (Transactions), Locking — Middle D

> ACID xususiyatlarining umumiy nazariyasi (Atomicity, Consistency,
> Isolation, Durability, Isolation Level'lar) [29-acid](../29-acid/README.md)da
> batafsil yoritilgan. Bu fayl — **PostgreSQL'ga xos amaliy
> transaction/locking texnikalari**ga (Savepoint, Advisory Locks,
> SKIP LOCKED, Optimistic Concurrency) e'tibor qaratadi.

## 1. Nima? (Ta'rif)

Bu fayl — PostgreSQL'da transactionlarni **amaliy boshqarish**
texnikalarini o'rgatadi: qisman rollback (Savepoint), qo'lda
qulflash (Advisory Locks), navbat (queue) implementatsiyasi uchun
`SKIP LOCKED`, va EF Core'da optimistic concurrency.

## 2. Nima uchun kerak?

Oddiy `BEGIN/COMMIT/ROLLBACK` — ko'p amaliy holatlar uchun yetarli
emas: "faqat oxirgi amalni bekor qilish" (Savepoint), "ikkita
parallel job bir xil vazifani bajarmasligi" (Advisory Lock/SKIP
LOCKED), "ikki foydalanuvchi bir xil yozuvni bir vaqtda o'zgartirsa
nima bo'ladi" (Optimistic Concurrency) — bularning barchasi maxsus
yechim talab qiladi.

## 3. Ichida nima sodir bo'ladi? (Mexanizm)

### 3.1 Savepoint — qisman rollback

```sql
BEGIN;
INSERT INTO employees (full_name) VALUES ('Orzibek');
SAVEPOINT before_risky_insert;
INSERT INTO employees (full_name) VALUES (NULL); -- XATO (NOT NULL constraint)!
ROLLBACK TO before_risky_insert; -- FAQAT shu SAVEPOINT'dan keyingi amal bekor qilinadi
INSERT INTO employees (full_name) VALUES ('Dilnoza'); -- Davom etadi
COMMIT;
-- Natija: "Orzibek" VA "Dilnoza" SAQLANADI, xato yozuv SAQLANMAYDI
```

### 3.2 Isolation level sozlash

```sql
BEGIN TRANSACTION ISOLATION LEVEL SERIALIZABLE;
-- ... amallar
COMMIT;
```

### 3.3 Deadlock — nima, qanday aniqlash, oldini olish

```
Deadlock — IKKI transaction BIR-BIRINI CHEKSIZ kutib qoladi:

T1: UPDATE employees SET ... WHERE id = 1; -- id=1 QULFLANDI
T2: UPDATE employees SET ... WHERE id = 2; -- id=2 QULFLANDI
T1: UPDATE employees SET ... WHERE id = 2; -- id=2 ni KUTADI (T2 band qilgan)
T2: UPDATE employees SET ... WHERE id = 1; -- id=1 ni KUTADI (T1 band qilgan)

💥 CHEKSIZ KUTISH — PostgreSQL BUNI AVTOMATIK ANIQLAYDI va BITTA
   transaction'ni "deadlock_detected" xatosi bilan MAJBURAN
   TO'XTATADI (odatda ENG KAM ish qilgani).
```

**Oldini olish:** resurslarni **BIR XIL TARTIBDA** qulflash (masalan
har doim kichik ID'dan boshlab UPDATE qilish) — bu deadlock ehtimolini
sezilarli kamaytiradi.

### 3.4 Advisory Locks

```sql
SELECT pg_advisory_lock(12345); -- Qo'lda, ILOVA DARAJASIDAGI qulf
-- ... kritik bo'lim (masalan, faqat bitta job bajarilishi kerak)
SELECT pg_advisory_unlock(12345);
```

Advisory Lock — **jadval qatoriga BOG'LIQ EMAS**, ilova o'zi
belgilagan **ixtiyoriy raqam** asosida qulflaydi — masalan
"kunlik hisobot generatsiyasi FAQAT BITTA instance'da ishlasin"
kabi holatlar uchun.

### 3.5 SKIP LOCKED — queue implementatsiyasi uchun

```sql
-- Bir nechta worker BIR XIL "navbat" jadvalidan ISHNI OLADI,
-- LEKIN bir-birining ISHINI TAKRORLAMASLIGI kerak

SELECT * FROM job_queue
WHERE status = 'pending'
ORDER BY created_at
LIMIT 1
FOR UPDATE SKIP LOCKED; -- Boshqa worker ALLAQACHON QULFLAGAN qatorlarni O'TKAZIB YUBORADI
```

```
FOR UPDATE (SKIP LOCKED'siz) — agar qator ALLAQACHON boshqa
transaction tomonidan QULFLANGAN bo'lsa — KUTADI (band bo'lguncha)

FOR UPDATE SKIP LOCKED — QULFLANGAN qatorni O'TKAZIB YUBORADI,
KEYINGI BO'SH qatorni OLADI — bu KO'P WORKER parallel ishlashi
uchun IDEAL (hech kim bir-birini KUTMAYDI)
```

### 3.6 FOR UPDATE — pessimistic locking

```sql
BEGIN;
SELECT * FROM accounts WHERE id = 1 FOR UPDATE; -- Bu qatorni QULFLAYDI
UPDATE accounts SET balance = balance - 100 WHERE id = 1;
COMMIT; -- Qulf SHU YERDA BO'SHATILADI
```

**Pessimistic locking** — "boshqa birov BU qatorni O'ZGARTIRISHI
MUMKIN" deb **oldindan taxmin qilib**, transaction BOSHIDA qulflaydi
— boshqa transaction shu qatorni **kutishga majbur** bo'ladi.

### 3.7 Optimistic Concurrency — EF Core'da RowVersion

```csharp
public class Employee
{
    public int Id { get; set; }
    public decimal Salary { get; set; }

    [Timestamp] // PostgreSQL'da xxid — har UPDATE'da AVTOMATIK o'zgaradi
    public byte[] RowVersion { get; set; } = null!;
}
```

```
Optimistic Concurrency — "ehtimol HECH KIM BOSHQA o'zgartirmaydi"
deb TAXMIN qiladi, SaveChanges() chaqirilganda TEKSHIRADI:

UPDATE employees SET salary = 5000000 WHERE id = 1 AND row_version = 'oldValue';

Agar 0 ta qator O'ZGARGAN bo'lsa (RowVersion ALLAQACHON BOSHQA
transaction tomonidan O'ZGARTIRILGAN) — EF Core
DbUpdateConcurrencyException tashlaydi!
```

```csharp
try
{
    await _context.SaveChangesAsync();
}
catch (DbUpdateConcurrencyException)
{
    // Foydalanuvchiga: "Bu yozuv sizdan OLDIN BOSHQA kishi tomonidan
    // o'zgartirilgan, iltimos qayta yuklab, qayta urinib ko'ring"
}
```

```
Pessimistic — QULF OLADI, BOSHQALAR KUTADI (yuqori ziddiyat holatida
              samarali, lekin CONCURRENCY'ni PASAYTIRADI)
Optimistic  — QULF OLMAYDI, FAQAT SaveChanges'da TEKSHIRADI (past
              ziddiyat holatida SAMARALI — ko'p parallel o'qish,
              kam yozish holatlarida IDEAL)
```

## 4. Kod — to'liq misol

```csharp
public async Task UpdateSalaryAsync(int id, decimal newSalary, byte[] originalRowVersion)
{
    var employee = await _context.Employees.FindAsync(id);
    _context.Entry(employee).Property(e => e.RowVersion).OriginalValue = originalRowVersion;
    employee.Salary = newSalary;

    try { await _context.SaveChangesAsync(); }
    catch (DbUpdateConcurrencyException)
    {
        throw new ConflictException("Ma'lumot boshqa foydalanuvchi tomonidan o'zgartirilgan");
    }
}
```

## 5. Qachon ishlatish kerak?

| Vaziyat | Yechim |
|---|---|
| Faqat oxirgi amalni bekor qilish | Savepoint |
| Faqat BITTA instance biror ishni bajarishi kerak | Advisory Lock |
| Ko'p worker, navbatdan ish olish | `SKIP LOCKED` |
| Yuqori ziddiyat ehtimoli (bir xil qatorga ko'p yozish) | Pessimistic (`FOR UPDATE`) |
| Past ziddiyat ehtimoli, ko'p o'qish | Optimistic (RowVersion) |

## 6. Muhim nuqtalar

- Deadlock'dan qochish uchun — resurslarni HAR DOIM **bir xil
  tartibda** qulflash tavsiya etiladi.
- `SKIP LOCKED` — RabbitMQ o'rniga **oddiy** DB-based job queue
  yasashda foydali texnika (kichik loyihalarda).
- Optimistic Concurrency — ko'p **parallel foydalanuvchili** ERP
  tizimlarida standart amaliyot (masalan, ikki HR xodimi bir xodim
  yozuvini bir vaqtda tahrirlashi mumkin bo'lgan holatda).

## 7. Imtihon savollari

1. Savepoint nima va u qanday qisman rollback imkonini beradi?
2. Deadlock nima va uni oldini olishning oddiy usuli qanday?
3. Advisory Lock oddiy `FOR UPDATE`dan qanday farq qiladi?
4. `SKIP LOCKED` qanday muammoni (queue implementatsiyasida) hal
   qiladi?
5. Pessimistic va Optimistic Concurrency orasidagi farqni tushuntiring
   — qaysi holatda qaysi biri afzal?
6. EF Core'da `RowVersion` qanday ishlaydi va `DbUpdateConcurrencyException`
   qachon tashlanadi?
