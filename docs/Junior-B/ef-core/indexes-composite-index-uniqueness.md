# Indexes, Composite Index, Index Uniqueness — Junior B

## 1. What (Nima?)

**Index (indeks)** — JADVALDAGI MA'LUMOTLARNI **TEZROQ TOPISH**
UCHUN, ALOHIDA, TARTIBLANGAN DATA STRUKTURA (ODATDA B-Tree)
sifatida SAQLANADIGAN "QO'SHIMCHA XARITA". **Composite Index**
(kompozit indeks) — **BIR NECHTA USTUN BIRGALIKDA** INDEKSLANGAN
HOLAT. **Index Uniqueness** — INDEKSGA `UNIQUE` CHEKLOVI
QO'SHILGANDA, U — FAQAT QIDIRUVNI TEZLASHTIRMASDAN, BALKI
**TAKRORLANMASLIKNI HAM DB DARAJASIDA KAFOLATLAYDI**.

## 2. Real hayot analogiyasi

**Index — KITOB OXIRIDAGI "INDEKS" (mundarija) SAHIFASI.**
Agar SIZ KITOBDA "PostgreSQL" SO'ZI QAYERDA TILGA OLINGANINI
TOPMOQCHI BO'LSANGIZ — KITOBNI BOSHIDAN OXIRIGACHA O'QIB
CHIQISH (Sequential Scan) O'RNIGA, OXIRIDAGI INDEKS
SAHIFASIGA QARAYSIZ — U YERDA, ALFABET TARTIBIDA, "PostgreSQL
— 45, 78, 120-betlarda" DEB YOZILGAN. **Composite Index — 
"ISM VA FAMILIYA BO'YICHA BIRGALIKDA TARTIBLANGAN" TELEFON
DAFTARI** — FAQAT FAMILIYA BO'YICHA QIDIRISH TEZ, LEKIN FAQAT
ISM BO'YICHA QIDIRISH — DAFTARNI BOSHIDAN OXIRIGACHA VARAQLASH
KABI SEKIN.

## 3. Why (Nega kerak?)

INDEKSSIZ, HAR QANDAY `WHERE` YOKI `JOIN` SO'ROVI —
**SEQUENTIAL SCAN** (jadvalni BOSHIDAN OXIRIGACHA, QATOR-
QATOR TEKSHIRISH) TALAB QILADI — MILLIONLAB QATORLI JADVALDA,
BU **SEKUNDLAR, HATTO DAQIQALAR** DAVOM ETISHI MUMKIN. Index
— QIDIRUVNI, O(n) DAN **O(log n)**GA (B-Tree DARAXT
CHUQURLIGI) TUSHIRADI — MILLIONLAB QATOR ORASIDAN, BIR NECHTA
MILLISEKUNDDA TOPISH MUMKIN BO'LADI.

## 4. Internals (Ichki mexanizm)

### B-Tree Index — TUZILISHI

```
PostgreSQL'ning DEFAULT INDEX TURI — B-Tree (Balanced Tree):
                    [50]
                   /    \
              [20,35]   [70,90]
              /  |  \    /  |  \
           ...  ... ... ... ... ...

HAR "TUGUN" (node) — TARTIBLANGAN QIYMATLAR VA "BOLA" TUGUN-
LARGA KO'RSATKICHLARNI SAQLAYDI. QIDIRUV — ILDIZDAN (root)
BOSHLAB, HAR QADAMDA YARMI KAMROQ MAYDONNI QOLDIRIB, PASTGA
TUSHADI — DARAXT "BALANSLANGAN" (barcha barglar bir xil
chuqurlikda) bo'lgani uchun, QIDIRUV VAQTI KAFOLATLANGAN
LOGARIFMIK (O(log n)).
```

### Composite Index — USTUNLAR TARTIBI MUHIM (Leftmost Prefix Rule)

```sql
CREATE INDEX idx_employees_dept_salary ON employees (department_id, salary);
```

```
COMPOSITE INDEX (department_id, salary) — B-Tree DARAXTDA,
AVVAL department_id BO'YICHA, KEYIN HAR BIR department_id
ICHIDA salary BO'YICHA TARTIBLANADI. "LEFTMOST PREFIX RULE"
(chapdan boshlab mos kelish qoidasi):

WHERE department_id = 5                       → INDEKS ISHLAYDI (to'liq)
WHERE department_id = 5 AND salary > 1000000   → INDEKS ISHLAYDI (to'liq)
WHERE salary > 1000000                         → INDEKS ISHLAMAYDI!
                                                  (department_id "chap" ustun,
                                                   u FILTRLANMASA, DARAXTDA
                                                   TO'G'RI JOYNI TOPIB
                                                   BO'LMAYDI)
```

### UNIQUE Index — QANDAY QILIB CHEKLOVNI HAM TA'MINLAYDI

```
UNIQUE INDEX — ODDIY INDEKS BILAN BIR XIL B-Tree STRUKTURA,
LEKIN HAR INSERT/UPDATE'DA, POSTGRESQL, YANGI QIYMATNI
DARAXTGA QO'SHISHDAN OLDIN, "BUNDAY QIYMAT ALLAQACHON
MAVJUDMI?" DEB TEKSHIRADI (BU TEKSHIRUV, AYNAN INDEKS
TUFAYLI, TEZKOR — SEQUENTIAL SCAN TALAB QILINMAYDI). AGAR
MAVJUD BO'LSA — `23505 unique_violation` XATOLIGI QAYTARILADI.

MUHIM: PostgreSQL'da PRIMARY KEY — ICHKARIDA, AVTOMATIK
RAVISHDA UNIQUE INDEX + NOT NULL sifatida IMPLEMENTATSIYA
QILINADI — PK YARATISH, HAQIQATDA, UNIQUE INDEX YARATISHNING
"MAXSUS HOLATI".
```

### Index — YOZISH (INSERT/UPDATE) TEZLIGIGA SALBIY TA'SIRI

```
HAR INDEKS — QO'SHIMCHA DATA STRUKTURA BO'LGANI UCHUN, HAR
INSERT/UPDATE/DELETE'DA, DB — NAFAQAT ASOSIY JADVALNI, BALKI
BARCHA TEGISHLI INDEKSLARNI HAM YANGILASHI KERAK. Ko'p
indekslar — O'QISHNI TEZLASHTIRADI, LEKIN YOZISHNI SEKINLASH-
TIRADI VA DISK JOYINI KO'PROQ ISHLATADI — bu, HAR LOYIHADA
"O'QISH vs YOZISH" NISBATIGA QARAB, ONGLI TANLASH KERAK
BO'LGAN TRADEOFF.
```

## 5. Code (Amaliy kod)

```sql
-- Oddiy indeks
CREATE INDEX idx_employees_email ON employees (email);

-- Composite index — tartib MUHIM! (department_id, so'ngra salary bo'yicha filtr uchun)
CREATE INDEX idx_employees_dept_salary ON employees (department_id, salary);

-- Unique index — qiymat takrorlanmasligini KAFOLATLAYDI
CREATE UNIQUE INDEX idx_employees_email_unique ON employees (email);

-- Indeksni ISHLATILAYOTGANINI TEKSHIRISH — EXPLAIN ANALYZE
EXPLAIN ANALYZE SELECT * FROM employees WHERE department_id = 5 AND salary > 1000000;
-- → "Index Scan using idx_employees_dept_salary" — indeks ISHLADI
-- → "Seq Scan on employees" — indeks ISHLAMADI (yo'q yoki noto'g'ri tartib)
```

```csharp
// EF Core Fluent API — Index yaratish
public class AppDbContext : DbContext
{
    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.Entity<Employee>()
            .HasIndex(e => e.Email)
            .IsUnique(); // UNIQUE index — email takrorlanmaydi

        modelBuilder.Entity<Employee>()
            .HasIndex(e => new { e.DepartmentId, e.Salary }); // Composite index — tartib MUHIM
    }
}
```

```csharp
// LINQ so'rov — Composite Index'dan TO'LIQ foydalanadi (leftmost prefix)
var employees = await dbContext.Employees
    .Where(e => e.DepartmentId == 5 && e.Salary > 1000000)
    .ToListAsync();

// ⚠️ Bu so'rov — YUQORIDAGI indeksdan FOYDALANA OLMAYDI (department_id yo'q)
var byOnlySalary = await dbContext.Employees
    .Where(e => e.Salary > 1000000)
    .ToListAsync();
```

## 6. Keng tarqalgan xatolar / noto'g'ri tushunchalar

```
❌ "Har ustunga INDEKS QO'YISH — HAR DOIM YAXSHI" — YO'Q!
   HAR INDEKS — YOZISH TEZLIGINI SEKINLASHTIRADI VA DISK
   JOYINI KO'PROQ ISHLATADI — FAQAT TEZ-TEZ FILTR/JOIN/ORDER
   BY'DA ISHLATILADIGAN USTUNLARGA INDEKS QO'YISH KERAK.

❌ "Composite Index (A, B) — WHERE B = ... so'rovida HAM
   TO'LIQ ISHLAYDI" — YO'Q! Leftmost Prefix Rule tufayli,
   FAQAT A BO'YICHA (yoki A+B BO'YICHA) FILTRLASHDA TO'LIQ
   ISHLAYDI — FAQAT B BO'YICHA FILTRLASHDA — INDEKS UMUMAN
   ISHLATILMAYDI (yoki SAMARASIZ ISHLATILADI).

❌ "PRIMARY KEY va UNIQUE INDEX — TURLI MEXANIZMLAR" — YO'Q,
   PostgreSQL'da PRIMARY KEY — ICHKARIDA, AYNAN UNIQUE INDEX +
   NOT NULL CONSTRAINT SIFATIDA IMPLEMENTATSIYA QILINADI.

❌ "Indeks qo'shsam, EXPLAIN ANALYZE bilan TEKSHIRMASAM HAM,
   DB UNI AVTOMATIK ISHLATADI" — HAR DOIM EMAS! Query Planner
   — BA'ZAN, KICHIK JADVALLARDA YOKI SO'ROV NATIJASI JADVAL-
   NING KATTA QISMINI QAYTARSA, Sequential Scan'ni INDEX
   SCAN'DAN TEZROQ DEB HISOBLAB, INDEKSNI E'TIBORSIZ
   QOLDIRISHI MUMKIN.
```

## 7. Exam (Interview savollari)

**1. Index nima, va u qidiruvni QANDAY TEZLASHTIRADI?**
Index — JADVAL MA'LUMOTLARINI TEZ TOPISH UCHUN, ALOHIDA,
TARTIBLANGAN DATA STRUKTURA (odatda B-Tree). U, QIDIRUV
MURAKKABLIGINI, Sequential Scan'ning O(n)'dan, B-Tree'ning
O(log n)GA TUSHIRADI.

**2. Composite Index'da "Leftmost Prefix Rule" nima degani?**
Composite Index (A, B, C) — FAQAT A, (A,B), YOKI (A,B,C)
BO'YICHA FILTRLASHDA TO'LIQ ISHLAYDI — FAQAT B YOKI FAQAT C
BO'YICHA FILTRLASHDA, INDEKS ISHLATILMAYDI (yoki SAMARASIZ),
CHUNKI B-Tree DARAXTDA MA'LUMOT, AVVALO A BO'YICHA, KEYIN B,
KEYIN C BO'YICHA TARTIBLANGAN.

**3. UNIQUE Index, ODDIY INDEKSDAN TASHQARI, YANA NIMANI
TA'MINLAYDI?**
UNIQUE Index — QIDIRUVNI TEZLASHTIRISHDAN TASHQARI, HAR
INSERT/UPDATE'DA, YANGI QIYMATNING ALLAQACHON MAVJUD
EMASLIGINI TEKSHIRADI VA KAFOLATLAYDI (takroriy qiymat
kiritilsa, `23505 unique_violation` xatoligi beradi).

**4. Nima uchun HAR USTUNGA INDEKS QO'YISH — YOMON AMALIYOT
DEB HISOBLANADI?**
Chunki HAR INDEKS — QO'SHIMCHA DATA STRUKTURA BO'LGANI UCHUN,
HAR INSERT/UPDATE/DELETE'DA QAYTA YANGILANISHI KERAK — bu,
YOZISH OPERATSIYALARINI SEKINLASHTIRADI VA DISK JOYINI
KO'PROQ ISHLATADI. Indeks — FAQAT HAQIQATDA TEZ-TEZ
FILTR/JOIN'DA ISHLATILADIGAN USTUNLARGA QO'YILISHI KERAK.

**5. PostgreSQL'da PRIMARY KEY va UNIQUE INDEX orasidagi
BOG'LIQLIK nima?**
PostgreSQL'da PRIMARY KEY — ICHKARIDA, AVTOMATIK RAVISHDA
UNIQUE INDEX + NOT NULL CONSTRAINT KOMBINATSIYASI sifatida
IMPLEMENTATSIYA QILINADI — PK YARATISH, TEXNIK JIHATDAN,
UNIQUE INDEX YARATISHNING MAXSUS (NOT NULL bilan
kuchaytirilgan) HOLATI HISOBLANADI.
