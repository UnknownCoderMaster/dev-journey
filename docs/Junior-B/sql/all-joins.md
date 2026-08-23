# Barcha JOIN lar (INNER, LEFT, RIGHT, FULL, CROSS, SELF) — Junior B

## 1. What (Nima?)

**JOIN** — IKKI (yoki UNDAN KO'P) JADVALDAGI QATORLARNI, **UMUMIY
USTUN (odatda FK-PK juftlik) ASOSIDA BIRLASHTIRIB, BITTA
NATIJA SIFATIDA QAYTARISH** OPERATSIYASI. SQL — BIR NECHTA
JOIN TURINI TAQDIM ETADI: **INNER, LEFT, RIGHT, FULL, CROSS,
SELF** — HAR BIRI, "QAYSI QATORLAR NATIJAGA KIRITILISHI"
BO'YICHA FARQ QILADI.

## 2. Real hayot analogiyasi

**JOIN — IKKI RO'YXATNI, UMUMIY BELGI BO'YICHA, BIRLASHTIRISH.**
Tasavvur qiling: BIR RO'YXATDA — "STUDENTLAR" (Ism, Guruh ID),
IKKINCHISIDA — "GURUHLAR" (Guruh ID, Nomi). **INNER JOIN** —
"FAQAT HAQIQIY GURUHGA BIRIKKAN STUDENTLARNI KO'RSAT" (guruhi
yo'q studentlar — TASHLAB YUBORILADI). **LEFT JOIN** — "BARCHA
STUDENTLARNI KO'RSAT, GURUHI BO'LMASA HAM — 'GURUH YO'Q' DEB
BELGILA". **CROSS JOIN** — "HAR STUDENTNI, HAR GURUH BILAN,
BARCHA MUMKIN BO'LGAN KOMBINATSIYADA JUFTLASH" (masalan,
"kim qaysi kursga YOZILISHI MUMKIN" ro'yxatini tuzishda).

## 3. Why (Nega kerak?)

RELYATSION DB'DA, MA'LUMOTLAR, **NORMALLASHTIRISH** TUFAYLI,
BIR NECHTA JADVALGA BO'LINADI (masalan, Employee va Department
— alohida jadvallarda). JOIN — BU BO'LINGAN MA'LUMOTLARNI,
**QAYTA, MANTIQIY, TO'LIQ KO'RINISHDA BIRLASHTIRISH** UCHUN
YAGONA YO'L. HAR JOIN TURI — TURLI BIZNES SAVOLGA JAVOB
BERADI: "FAQAT MOS KELGANLARINI KO'RSAT" (INNER) vs "BARCHASINI
KO'RSAT, MOS KELMASA HAM" (LEFT/RIGHT/FULL).

## 4. Internals (Ichki mexanizm)

### JOIN Algoritmlari — Query Planner QANDAY BAJARADI

```
PostgreSQL — JOIN'NI BAJARISH UCHUN, ODATDA, UCHTA
ALGORITMDAN BIRINI TANLAYDI (Query Planner, JADVAL HAJMI,
INDEKSLAR, VA STATISTIKA ASOSIDA, ENG ARZONINI TANLAYDI):

Nested Loop Join  — HAR QATORNI, IKKINCHI JADVALNING HAR
                     QATORI BILAN SOLISHTIRADI (O(n*m)) — 
                     KICHIK JADVALLAR YOKI INDEKS MAVJUD
                     BO'LGANDA SAMARALI.

Hash Join         — KICHIKROQ JADVALDAN, XOTIRADA HASH
                     JADVAL QURADI, KEYIN KATTAROQ JADVALNI
                     BIR MARTA O'QIB, HASH JADVAL BILAN
                     SOLISHTIRADI (O(n+m)) — TENGLIK (=)
                     SHARTLI JOIN'LARDA SAMARALI.

Merge Join        — IKKI JADVAL HAM, JOIN USTUNI BO'YICHA
                     OLDINDAN TARTIBLANGAN (masalan indeks
                     orqali) BO'LSA — IKKALASINI BIR VAQTDA,
                     "PARALLEL" O'QIB, BIRLASHTIRADI.
```

### INNER JOIN — FAQAT MOS KELGAN QATORLAR

```sql
SELECT e.full_name, d.name
FROM employees e
INNER JOIN departments d ON e.department_id = d.id;
```

```
INNER JOIN — FAQAT, IKKI TOMONDA HAM, JOIN SHARTI (ON) TRUE
BO'LGAN QATORLARNI QAYTARADI. Agar employee'ning
department_id'si, departments jadvalida MOS YOZUVGA EGA
BO'LMASA (masalan NULL) — BU EMPLOYEE, NATIJADA UMUMAN
KO'RINMAYDI.
```

### LEFT/RIGHT JOIN — BIR TOMONNI "TO'LIQ" SAQLASH

```sql
SELECT e.full_name, d.name
FROM employees e
LEFT JOIN departments d ON e.department_id = d.id;
-- Barcha employeelar ko'rinadi, department topilmasa — d.name = NULL
```

```
LEFT JOIN — CHAP JADVALNING (employees) BARCHA QATORLARINI
SAQLAYDI, HATTO O'NG JADVALDA (departments) MOS YOZUV
TOPILMASA HAM — BUNDAY HOLATDA, O'NG JADVAL USTUNLARI, NATIJADA
NULL BO'LADI. RIGHT JOIN — TESKARISI (o'ng jadval to'liq
saqlanadi).
```

### FULL OUTER JOIN — IKKALA TOMONNI HAM "TO'LIQ" SAQLASH

```sql
SELECT e.full_name, d.name
FROM employees e
FULL OUTER JOIN departments d ON e.department_id = d.id;
-- Departmentsiz employeelar HAM, employeesiz departmentlar HAM ko'rinadi
```

### CROSS JOIN — DEKART KO'PAYTMASI (Cartesian Product)

```sql
SELECT s.name, c.name
FROM sizes s CROSS JOIN colors c;
-- HAR size, HAR color bilan juftlashadi — N*M qator natija
```

```
CROSS JOIN — HECH QANDAY ON SHARTI TALAB QILMAYDI — IKKI
JADVALNING HAR BIR QATORINI, IKKINCHI JADVALNING HAR BIR
QATORI BILAN "MEXANIK" JUFTLAYDI (N*M QATOR NATIJA) — DIQQAT:
KATTA JADVALLARDA, BU, KATASTROFIK DARAJADA KO'P QATOR
YARATISHI MUMKIN.
```

### SELF JOIN — JADVALNI O'ZI BILAN BIRLASHTIRISH

```sql
SELECT e.full_name AS employee, m.full_name AS manager
FROM employees e
LEFT JOIN employees m ON e.manager_id = m.id;
```

```
SELF JOIN — MAXSUS "JOIN TURI" EMAS, BALKI, BIR XIL JADVALGA,
IKKI XIL "TAXALLUS" (alias — e va m) BERISH ORQALI, UNI, XUDDI
IKKI ALOHIDA JADVAL KABI, JOIN QILISH TEXNIKASI — IYERARXIK
MA'LUMOTLARNI (masalan xodim-menejer) BIR DARAJALI SO'ROVDA
KO'RSATISH UCHUN ISHLATILADI.
```

## 5. Code (Amaliy kod)

```sql
-- INNER JOIN — faqat mos kelgan qatorlar
SELECT e.full_name, d.name AS department
FROM employees e
INNER JOIN departments d ON e.department_id = d.id;

-- LEFT JOIN — barcha xodimlar, department topilmasa NULL
SELECT e.full_name, d.name AS department
FROM employees e
LEFT JOIN departments d ON e.department_id = d.id
WHERE d.id IS NULL; -- "department'i yo'q" xodimlarni topish uchun keng tarqalgan pattern

-- FULL OUTER JOIN
SELECT e.full_name, d.name AS department
FROM employees e
FULL OUTER JOIN departments d ON e.department_id = d.id;

-- SELF JOIN — xodim va uning menejeri
SELECT e.full_name AS xodim, m.full_name AS menejer
FROM employees e
LEFT JOIN employees m ON e.manager_id = m.id;
```

```csharp
// EF Core LINQ — Join metodlari (JOIN turi, LINQ operatoriga qarab belgilanadi)
// INNER JOIN — Navigation Property orqali (avtomatik)
var employeesWithDept = await dbContext.Employees
    .Where(e => e.Department != null) // Navigation orqali INNER JOIN'ga o'xshash natija
    .Select(e => new { e.FullName, DepartmentName = e.Department!.Name })
    .ToListAsync();

// LEFT JOIN — DefaultIfEmpty() orqali
var employeesLeftJoin = await (
    from e in dbContext.Employees
    join d in dbContext.Departments on e.DepartmentId equals d.Id into deptGroup
    from d in deptGroup.DefaultIfEmpty() // ⚡ LEFT JOIN semantikasi
    select new { e.FullName, DepartmentName = d != null ? d.Name : "Noma'lum" }
).ToListAsync();

// SELF JOIN — Navigation Property orqali
var employeesWithManager = await dbContext.Employees
    .Select(e => new { Employee = e.FullName, Manager = e.Manager != null ? e.Manager.FullName : "Yo'q" })
    .ToListAsync();
```

## 6. Keng tarqalgan xatolar / noto'g'ri tushunchalar

```
❌ "LEFT JOIN va RIGHT JOIN — TURLI NATIJA BERADI, ULARNI
   ALMASHTIRIB BO'LMAYDI" — QISMAN TO'G'RI, LEKIN ESLATMA:
   `A LEFT JOIN B` — `B RIGHT JOIN A` BILAN, JADVALLAR
   TARTIBI ALMASHTIRILSA, MANTIQIY JIHATDAN BIR XIL NATIJA
   BERADI — KO'PCHILIK, KODNI O'QISHNI OSONLASHTIRISH UCHUN,
   FAQAT LEFT JOIN'NI ISHLATISHNI TANLAYDI.

❌ "WHERE d.id IS NULL — INNER JOIN'da HAM TO'G'RI ISHLAYDI"
   — YO'Q! INNER JOIN — MOS KELMAGAN QATORLARNI, ALLAQACHON,
   NATIJADAN TASHLAB YUBORADI — `WHERE d.id IS NULL` PATTERN
   ("department'i yo'q xodimlarni topish") — FAQAT LEFT JOIN
   BILAN ISHLAYDI.

❌ "CROSS JOIN — KAMDAN-KAM ISHLATILADI, SHUNING UCHUN
   AHAMIYATSIZ" — DIQQAT: BA'ZAN, DASTURCHI, QASDDAN EMAS,
   JOIN SHARTI (ON) NI YOZISHNI "UNUTIB" QO'YADI — natijada,
   SO'ROV, TASODIFAN, KATASTROFIK KATTA CROSS JOIN NATIJASINI
   QAYTARADI (production'da SEKINLASHISH/CRASH SABABI).

❌ "SELF JOIN — MAXSUS SQL SINTAKSISI TALAB QILADI" — YO'Q,
   ODDIY JOIN SINTAKSISI ISHLATILADI, FAQAT BIR XIL JADVALGA
   IKKI XIL ALIAS BERISH ORQALI AMALGA OSHIRILADI.
```

## 7. Exam (Interview savollari)

**1. INNER JOIN va LEFT JOIN orasidagi ASOSIY FARQ nima?**
INNER JOIN — FAQAT, IKKI TOMONDA HAM JOIN SHARTI TRUE BO'LGAN
QATORLARNI QAYTARADI. LEFT JOIN — CHAP JADVALNING BARCHA
QATORLARINI SAQLAYDI, O'NG JADVALDA MOS TOPILMASA — O'NG
USTUNLAR NULL BO'LADI.

**2. `WHERE d.id IS NULL` bilan, LEFT JOIN'dan KEYIN
QO'LLANILADIGAN PATTERN, QANDAY BIZNES SAVOLGA JAVOB
BERADI, VA NIMA UCHUN INNER JOIN'da BUNI ISHLATIB
BO'LMAYDI?**
Bu PATTERN — "IKKINCHI JADVALDA MOS YOZUVGA EGA BO'LMAGAN
QATORLARNI TOPISH" (masalan, department'i yo'q xodimlar)
SAVOLIGA JAVOB BERADI. INNER JOIN'da BUNI ISHLATIB
BO'LMAYDI, CHUNKI INNER JOIN, MOS TOPILMAGAN QATORLARNI,
ALLAQACHON, NATIJADAN OLIB TASHLAYDI — `d.id IS NULL`
SHARTIGA TUSHADIGAN QATOR UMUMAN QOLMAYDI.

**3. CROSS JOIN nima, va u QACHON (qasddan) ISHLATILADI?**
CROSS JOIN — HECH QANDAY ON SHARTISIZ, IKKI JADVALNING HAR
QATORINI, IKKINCHI JADVALNING HAR QATORI BILAN "MEXANIK"
JUFTLAYDI (Dekart ko'paytmasi, N*M natija). U, ODATDA, BARCHA
MUMKIN BO'LGAN KOMBINATSIYALARNI GENERATSIYA QILISH KERAK
BO'LGANDA (masalan, "har o'lcham — har rang bilan"
kombinatsiyasi) QASDDAN ISHLATILADI.

**4. SELF JOIN nima, va u NIMA UCHUN ALOHIDA "JOIN TURI"
EMAS?**
SELF JOIN — JADVALNI, O'ZI BILAN, IKKI XIL ALIAS ORQALI
BIRLASHTIRISH TEXNIKASI (masalan xodim-menejer iyerarxiyasi
uchun) — U, MAXSUS SQL SINTAKSISI EMAS, ODDIY (INNER/LEFT)
JOIN, SHUNCHAKI BIR XIL JADVALGA QARATILGAN HOLDA
ISHLATILADI.

**5. PostgreSQL Query Planner, JOIN'NI BAJARISH UCHUN, QANDAY
UCH ASOSIY ALGORITMDAN BIRINI TANLAYDI, VA ULARNING QISQA
FARQI nima?**
Nested Loop Join (har qatorni ikkinchisi bilan solishtiradi —
kichik jadval/indeks bo'lganda samarali), Hash Join (kichik
jadvaldan hash jadval qurib, kattasi bilan solishtiradi —
tenglik shartida samarali), Merge Join (ikki tartiblangan
jadvalni parallel o'qib birlashtiradi — oldindan tartiblangan
ma'lumotda samarali). Planner, jadval hajmi va statistika
asosida, eng arzonini tanlaydi.
