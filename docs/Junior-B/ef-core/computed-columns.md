# Computed Columns — Junior B

## 1. What (Nima?)

**Computed Column** (hisoblanadigan ustun) — QIYMATI QO'LDA
KIRITILMAYDIGAN, BALKI **BIR NECHTA BOSHQA USTUN ASOSIDA,
FORMULA ORQALI AVTOMATIK HISOBLAB CHIQARILADIGAN** USTUN
(masalan `total_price = quantity * unit_price`). PostgreSQL'da
BU — `GENERATED ALWAYS AS (...) STORED` SINTAKSISI ORQALI
AMALGA OSHIRILADI.

## 2. Real hayot analogiyasi

**Computed Column — CHEKDAGI "JAMI SUMMA" QATORI.** Ofitsiant
(dastur) — HAR BIR TAOM NARXINI VA MIQDORINI (boshqa ustunlar)
QO'LDA KIRITADI, LEKIN **"JAMI SUMMA"NI HECH KIM QO'LDA
YOZMAYDI** — U, AVTOMATIK, BOSHQA QATORLAR YIG'INDISI SIFATIDA
HISOBLANADI. Agar TAOM NARXI YOKI MIQDORI O'ZGARSA — "JAMI
SUMMA" HAM AVTOMATIK YANGILANADI, HECH KIM UNI QAYTA QO'LDA
HISOBLAMAYDI.

## 3. Why (Nega kerak?)

Agar `total_price`NI ILOVA KODIDA (C#) HAR SAFAR HISOBLASH
KERAK BO'LSA — **HAR BIR JOYDA** (backend, admin panel, report
generator) BU FORMULA TAKRORLANADI — BIRORTASIDA XATO
QILINSA, MA'LUMOTLAR NOMOSLIGI (data inconsistency) YUZAGA
KELADI. Computed Column — FORMULANI **DB DARAJASIDA, BIR
MARTA** BELGILAYDI — QAYSI YO'L BILAN QATOR O'QILMASIN, NATIJA
HAR DOIM TO'G'RI VA IZCHIL.

## 4. Internals (Ichki mexanizm)

### `STORED` vs Virtual (PostgreSQL FAQAT STORED'ni QO'LLAB-QUVVATLAYDI)

```sql
CREATE TABLE order_items (
    quantity INT NOT NULL,
    unit_price NUMERIC(10,2) NOT NULL,
    total_price NUMERIC(10,2) GENERATED ALWAYS AS (quantity * unit_price) STORED
);
```

```
STORED — QIYMAT, HAR INSERT/UPDATE'DA QAYTA HISOBLANIB,
FIZIK DISKKA (jadval sahifasiga) YOZILADI — BU, O'QISH
(SELECT) TEZLIGINI OSHIRADI (qayta hisoblash SHART EMAS),
LEKIN DISK JOYINI (STORAGE) KO'PROQ ISHLATADI.

BOSHQA DB DVIGATELLARIDA (masalan SQL Server) — "VIRTUAL"
COMPUTED COLUMN HAM MAVJUD (qiymat SAQLANMAYDI, HAR SO'ROVDA
QAYTA HISOBLANADI) — PostgreSQL 12-16'da FAQAT STORED
QO'LLAB-QUVVATLANADI.
```

### Computed Column — YOZISHGA (INSERT/UPDATE) CHEKLOV

```sql
INSERT INTO order_items (quantity, unit_price, total_price) VALUES (5, 10.00, 100.00);
-- ❌ ERROR: column "total_price" is a generated column
```

```
GENERATED ALWAYS AS (...) COLUMN — TO'G'RIDAN-TO'G'RI YOZISHGA
UMUMAN RUXSAT BERMAYDI — INSERT SO'ROVIDA UNI TILGA OLISH
XATOLIKKA OLIB KELADI. Bu, DATA INTEGRITY'NI KAFOLATLAYDI:
HECH KIM (hatto XATO YOKI QASDDAN) FORMULAGA ZID QIYMAT
KIRITA OLMAYDI.
```

### Computed Column va INDEKSLASH

```sql
CREATE INDEX idx_order_items_total ON order_items (total_price);
```

```
STORED COMPUTED COLUMN — ODDIY USTUN KABI INDEKSLANISHI MUMKIN
(chunki QIYMAT HAQIQATDA DISKKA YOZILGAN) — bu, "total_price >
1000000" KABI SO'ROVLARNI, HAR SAFAR FORMULANI QAYTA
HISOBLAMASDAN, TEZ BAJARISHGA IMKON BERADI.
```

### EF Core'da Computed Column — `HasComputedColumnSql`

```
EF Core, MODEL DARAJASIDA COMPUTED COLUMN'NI TANIYDI, LEKIN
UNI HECH QACHON INSERT/UPDATE SO'ROVIGA QO'SHMAYDI (chunki DB
UNI O'ZI HISOBLAYDI) — SaveChanges'DAN KEYIN, EF Core, DB'DAN
HISOBLANGAN QIYMATNI O'QIB, C# OBYEKTGA QAYTARIB YOZADI
(xuddi Identity/Default qiymatlar kabi — RETURNING bandi
orqali).
```

## 5. Code (Amaliy kod)

```sql
-- SQL — Computed Column yaratish
CREATE TABLE employees (
    id SERIAL PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    full_name VARCHAR(101) GENERATED ALWAYS AS (first_name || ' ' || last_name) STORED
);

INSERT INTO employees (first_name, last_name) VALUES ('Ali', 'Valiyev');
SELECT full_name FROM employees; -- → 'Ali Valiyev' (avtomatik!)

UPDATE employees SET first_name = 'Vali' WHERE id = 1;
SELECT full_name FROM employees WHERE id = 1; -- → 'Vali Valiyev' (avtomatik YANGILANDI)
```

```csharp
// EF Core Fluent API — Computed Column
public class AppDbContext : DbContext
{
    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.Entity<Employee>()
            .Property(e => e.FullName)
            .HasComputedColumnSql("first_name || ' ' || last_name", stored: true);
    }
}

public class Employee
{
    public int Id { get; set; }
    public string FirstName { get; set; } = null!;
    public string LastName { get; set; } = null!;
    public string FullName { get; set; } = null!; // ⚡ EF Core — bu propertyga HECH QACHON YOZMAYDI (INSERT/UPDATE'da)
}
```

```csharp
// Foydalanish — FullName'ga qo'lda qiymat berish MA'NOSIZ (DB baribir override qiladi)
var employee = new Employee { FirstName = "Ali", LastName = "Valiyev" };
dbContext.Employees.Add(employee);
await dbContext.SaveChangesAsync();
Console.WriteLine(employee.FullName); // → "Ali Valiyev" — DB hisoblab, EF Core o'qib oldi
```

## 6. Keng tarqalgan xatolar / noto'g'ri tushunchalar

```
❌ "Computed Column'ga INSERT so'rovida QIYMAT BERISH MUMKIN,
   DB uni SHUNCHAKI E'TIBORSIZ QOLDIRADI" — YO'Q! PostgreSQL —
   GENERATED ALWAYS COLUMN'GA YOZISHGA URINISHDA, XATOLIK
   (ERROR) QAYTARADI — SO'ROV UMUMAN BAJARILMAYDI.

❌ "PostgreSQL'da Computed Column — HAR SO'ROVDA QAYTA
   HISOBLANADI (Virtual)" — YO'Q, PostgreSQL FAQAT STORED'NI
   QO'LLAB-QUVVATLAYDI — QIYMAT DISKKA YOZILADI, INSERT/UPDATE'DA
   HISOBLANADI, SELECT'DA ESA SHUNCHAKI O'QILADI.

❌ "Computed Column — faqat oddiy arifmetik amallar
   (quantity * price) uchun ishlatiladi" — YO'Q, STRING
   BIRLASHTIRISH (full_name), SHART OPERATORLARI (CASE WHEN),
   HATTO JSON FUNKSIYALARI HAM ISHLATILISHI MUMKIN.

❌ "EF Core, Computed Column'ni C# tomonda HAM HISOBLASHI
   KERAK (masalan validatsiya uchun)" — ODATDA YO'Q — DB
   YAGONA "MANBA HAQIQAT" (source of truth) BO'LISHI KERAK,
   C# tomonda DUBLIKAT MANTIQ YOZISH — SINXRONIZATSIYA
   MUAMMOSIGA OLIB KELISHI MUMKIN.
```

## 7. Exam (Interview savollari)

**1. Computed Column nima, va u ODDIY USTUNDAN NIMASI BILAN
FARQ QILADI?**
Computed Column — QIYMATI QO'LDA KIRITILMAYDIGAN, BALKI BOSHQA
USTUNLAR ASOSIDA, FORMULA ORQALI DB TOMONIDAN AVTOMATIK
HISOBLANADIGAN USTUN. Oddiy USTUNGA — QO'LDA, ISTALGAN QIYMAT
YOZISH MUMKIN, Computed Column'GA ESA — YO'Q (DB XATOLIK
BERADI).

**2. PostgreSQL'da `STORED` va boshqa DB DVIGATELLARIDAGI
"Virtual" Computed Column orasidagi FARQ nima?**
`STORED` — QIYMAT HAR INSERT/UPDATE'DA QAYTA HISOBLANIB,
FIZIK DISKKA YOZILADI (o'qish tezroq, saqlash joyi ko'proq
ishlatiladi). "Virtual" — QIYMAT SAQLANMAYDI, HAR SO'ROVDA
QAYTA HISOBLANADI (saqlash joyi tejaladi, o'qish sekinroq
bo'lishi mumkin). PostgreSQL 16'gacha FAQAT STORED'NI
QO'LLAB-QUVVATLAYDI.

**3. Computed Column'ni NIMA UCHUN INDEKSLASH MUMKIN
(agar STORED bo'lsa)?**
STORED Computed Column — QIYMATI HAQIQATDA DISKKA YOZILGANI
UCHUN, ODDIY USTUN KABI B-Tree INDEKS QURISH MUMKIN — bu,
FORMULA NATIJASI BO'YICHA FILTRLASH/SARALASHNI TEZLASHTIRADI.

**4. EF Core'da `HasComputedColumnSql` ISHLATILGANDA, C# ENTITY
KLASSIDAGI TEGISHLI PROPERTY'GA EF Core NIMA UCHUN HECH QACHON
YOZMAYDI (INSERT/UPDATE'da)?**
Chunki QIYMAT — DB TOMONIDAN HISOBLANADI, EF Core BUNI
BILADI (Model konfiguratsiyasi orqali) VA SHU SABABLI, U
PROPERTYNI INSERT/UPDATE SQL SO'ROVIGA UMUMAN QO'SHMAYDI —
FAQAT SaveChanges'DAN KEYIN, DB'DAN HISOBLANGAN QIYMATNI
O'QIB, C# OBYEKTGA QAYTARIB YOZADI.

**5. Computed Column ISHLATISHNING ASOSIY AFZALLIGI nima,
ILOVA KODIDA (C#) FORMULANI QAYTA-QAYTA YOZISHGA NISBATAN?**
FORMULA — BIR MARTA, DB DARAJASIDA BELGILANADI — QAYSI YO'L
BILAN QATOR O'QILMASIN YOKI YOZILMASIN (turli mikroservicelar,
raw SQL, admin panel), NATIJA HAR DOIM TO'G'RI VA IZCHIL —
ILOVA KODIDAGI TAKRORLANISH VA SINXRONIZATSIYA XATOLARI
OLDINI OLADI.
