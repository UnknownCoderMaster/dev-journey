# Null Values (Database Design) — Junior B

## 1. What (Nima?)

**NULL** — DB'da "QIYMAT YO'QLIGI" (yoki "NOMA'LUM") holatini
ifodalovchi MAXSUS BELGI — bu **0**, **bo'sh string ("")**, YOKI
**false**dan TUBDAN FARQLI: NULL — "BU YERDA HECH NARSA YO'Q, YOKI
BILMAYMIZ" DEGANI, ULAR ESA — **KONKRET, MA'LUM QIYMATLAR**.

## 2. Real hayot analogiyasi

**NULL — ANKETADAGI "JAVOB BERILMAGAN" MAYDON.** Anketada
(qator) "O'RTA ISM" MAYDONI BO'SH QOLDIRILGAN BO'LISHI MUMKIN —
BU, "O'RTA ISM — BO'SH STRING (\"\")" DEGANI EMAS, "BU
SAVOLGA JAVOB YO'Q/NOMA'LUM" DEGANI. AGAR SIZ IKKI ANKETANI
SOLISHTIRSANGIZ (`WHERE middle_name = ''`), IKKALASIDA HAM
"JAVOB BERILMAGAN" BO'LSA — ULARNI **BIR XIL** DEB HISOBLASH
MANTIQAN NOTO'G'RI (chunki BIRI — HAQIQATDA O'RTA ISMI YO'Q
BO'LISHI MUMKIN, IKKINCHISI — SHUNCHAKI TO'LDIRISHNI
"UNUTGAN").

## 3. Why (Nega kerak?)

NULL — REAL DUNYODAGI **"NOMA'LUMLIK"NI** TO'G'RI MODELLASHTIRISH
uchun ZARUR: HAR BIR XODIM — TELEFON RAQAMIGA EGA BO'LMASLIGI
MUMKIN — BUNI "0000000000" (SOXTA QIYMAT) DEB YOZISH — DASTUR
MANTIG'INI CHALKASHTIRADI (BU — HAQIQIY RAQAMMI, YO'Q, "JAVOB
YO'Q" ISHORASIMI?). NULL — BU AMBIGUITY'NI (noaniqlik) YO'QOTADI.

**"NULL — ZARARLI" DEGAN QARASH:** Ba'zi DB EKSPERTLARI (masalan
C.J. Date) — NULL'ning **THREE-VALUED LOGIC** (uch qiymatli
mantiq — TRUE/FALSE/UNKNOWN) KELTIRIB CHIQARADIGAN
MURAKKABLIKLARI TUFAYLI, UNI IMKON QADAR CHEKLASHNI TAVSIYA
QILADI (masalan `NOT NULL DEFAULT` bilan).

## 4. Internals (Ichki mexanizm)

### Three-Valued Logic — SQL'da BOOLEAN NATIJALAR

```sql
SELECT * FROM employees WHERE salary > 5000000; -- salary NULL bo'lsa — NA TRUE, NA FALSE, "UNKNOWN"!
```

```
SQL'da HAR SOLISHTIRISH (=, >, <) — NULL bilan ISHTIROK ETSA —
NATIJA "UNKNOWN" (Noma'lum) bo'ladi, TRUE HAM, FALSE HAM EMAS.
WHERE bandi — FAQAT "TRUE" natijali qatorlarni QAYTARADI —
"UNKNOWN" natijali qatorlar — AVTOMATIK CHIQARIB TASHLANADI
(garchi "yolg'on" DEB AYTILMAGAN BO'LSA HAM)!

WHERE salary > 5000000     — NULL salary'li qatorlar — YO'Q
WHERE salary <= 5000000    — NULL salary'li qatorlar — YO'Q (bu ham!)
WHERE salary IS NULL       — FAQAT ANIQ NULL qatorlar — YO'Q, BOR!
```

### `NULL = NULL` — NIMA UCHUN FALSE (aslida UNKNOWN)

```sql
SELECT NULL = NULL; -- → NULL (UNKNOWN), TRUE EMAS!
```

```
MANTIQIY SABAB: NULL — "NOMA'LUM QIYMAT" — IKKI "NOMA'LUM"
QIYMATNI SOLISHTIRISH — "ULAR BIR XILMI?" DEGAN SAVOLGA HAM
"NOMA'LUM" JAVOB BERADI (SIZ IKKI KISHINING "SIRLI YOSHI"NI
BILMASANGIZ, "ULAR BIR XIL YOSHDAMI?" DEB SO'RASA — "BILMAYMAN"
DEYSIZ, "HA" YOKI "YO'Q" EMAS).

Shuning uchun NULL TEKSHIRUVI UCHUN — MAXSUS OPERATOR:
IS NULL / IS NOT NULL
```

### NOT NULL constraint — INDEKS/STORAGE'GA TA'SIRI

```
NOT NULL constraint — PostgreSQL'ga "BU USTUN HECH QACHON NULL
BO'LMAYDI" DEB "KAFOLAT" BERADI — bu, QUERY PLANNER'GA (SQL
so'rov REJALASHTIRUVCHISI) QO'SHIMCHA OPTIMALLASHTIRISH
IMKONIYATINI BERADI (masalan, IS NULL TEKSHIRUVINI umuman
BAJARMASLIK MUMKINLIGINI BILADI).
```

### `COALESCE`, `NULLIF` — NULL bilan ISHLASH FUNKSIYALARI

```sql
SELECT COALESCE(phone, 'Kiritilmagan') FROM employees; -- BIRINCHI NULL BO'LMAGAN qiymat
SELECT NULLIF(bonus, 0) FROM employees; -- Agar bonus = 0 bo'lsa — NULL QAYTARADI
```

### EF Core'da NULL — Nullable Reference Types bilan BOG'LIQLIK

```
EF Core — C# `string?` (nullable) va `string` (non-nullable)
propertylarini, DB darajasidagi `NULL`/`NOT NULL` USTUNGA
AVTOMATIK MOSLASHTIRADI (Nullable Reference Types YOQILGAN
bo'lsa) — batafsil docs/Junior-C/04-nullable'da.
```

## 5. Code (Amaliy kod)

```sql
CREATE TABLE employees (
    id SERIAL PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,     -- HECH QACHON NULL EMAS
    phone VARCHAR(20),                    -- NULL BO'LISHI MUMKIN (default)
    manager_id INT REFERENCES employees(id), -- NULL — "MENEJERI YO'Q" (masalan BOSH DIREKTOR)
    resigned_at TIMESTAMPTZ               -- NULL — "HALI ISHDAN KETMAGAN"
);

-- TO'G'RI NULL tekshiruvi
SELECT * FROM employees WHERE phone IS NULL;
SELECT * FROM employees WHERE resigned_at IS NOT NULL; -- ISHDAN KETGANLAR

-- ❌ XATO — hech qachon TRUE bo'lmaydi
SELECT * FROM employees WHERE phone = NULL;

-- COALESCE — DEFAULT qiymat berish
SELECT full_name, COALESCE(phone, 'Noma''lum') AS phone FROM employees;
```

```csharp
// EF Core — Nullable Reference Types bilan
public class Employee
{
    public int Id { get; set; }
    public string FullName { get; set; } = null!; // NOT NULL — DB'da HAM NOT NULL
    public string? Phone { get; set; }              // NULL BO'LISHI MUMKIN
    public int? ManagerId { get; set; }              // Nullable value type — NULL BO'LISHI MUMKIN
    public DateTime? ResignedAt { get; set; }
}

// LINQ'da NULL tekshiruvi
var activeEmployees = await _context.Employees
    .Where(e => e.ResignedAt == null) // SQL'da: WHERE resigned_at IS NULL
    .ToListAsync();
```

```csharp
// C#'da NULL bilan ishlash — DB'dagi mantiqqa PARALLEL
string? phone = employee.Phone;
string displayPhone = phone ?? "Kiritilmagan"; // ?? — COALESCE'ga TENG
```

## 6. Keng tarqalgan xatolar / noto'g'ri tushunchalar

```
❌ "WHERE column = NULL — TO'G'RI ISHLAYDI" — HECH QACHON TRUE
   BO'LMAYDI! `IS NULL` ISHLATILISHI SHART.

❌ "NOT IN subquery'da NULL — MUAMMO KELTIRIB CHIQARMAYDI" —
   XAVFLI! Agar subquery NATIJASIDA NULL BO'LSA — BUTUN NOT IN
   IFODASI "UNKNOWN" bo'lib, HECH QANDAY QATOR QAYTARILMAYDI
   (KUTILMAGAN, BO'SH NATIJA):

   SELECT * FROM employees WHERE department_id NOT IN
       (SELECT department_id FROM archived_departments); -- Agar
   BU RO'YXATDA BITTA NULL bo'lsa — NATIJA UMUMAN BO'SH BO'LADI!

❌ "COUNT(column) — NULL qiymatlarni HAM SANAYDI" — YO'Q!
   COUNT(*) — BARCHA qatorlarni sanaydi, COUNT(column) — FAQAT
   NOT NULL qiymatlarni.

❌ "Bo'sh string ('') va NULL — BIR XIL narsa" — YO'Q! Bo'sh
   string — KONKRET, MA'LUM QIYMAT (uzunligi 0). NULL —
   "QIYMAT UMUMAN YO'Q" holati.

❌ "NULL — HAR DOIM YOMON DIZAYN BELGISI" — YO'Q, LEKIN
   HADDAN ORTIQ NULL'GA RUXSAT BERISH (har ustunda NULL) —
   DEFAULT/NOT NULL BILAN ANIQROQ IFODALASH mumkin bo'lgan
   HOLATLARDA — CHALKASHLIK KELTIRIB CHIQARADI.
```

## 7. Exam (Interview savollari)

**1. `WHERE column = NULL` nima uchun HECH QACHON TRUE
BO'LMAYDI?**
SQL — Three-Valued Logic ISHLATADI: `=` operatori NULL bilan
ISHLATILSA — NATIJA "UNKNOWN" (na TRUE, na FALSE) BO'LADI.
`WHERE` bandi — FAQAT TRUE natijali qatorlarni QAYTARADI, shuning
uchun `IS NULL`/`IS NOT NULL` MAXSUS OPERATORLARI ISHLATILISHI
KERAK.

**2. `COUNT(*)` va `COUNT(column)` orasidagi FARQ nima?**
`COUNT(*)` — BARCHA qatorlarni SANAYDI (NULL BOR-YO'QLIGIDAN
QAT'I NAZAR). `COUNT(column)` — FAQAT O'SHA USTUNDA NOT NULL
QIYMATGA EGA qatorlarni SANAYDI.

**3. NOT IN subquery'da NULL nima uchun KUTILMAGAN, BO'SH
NATIJAGA olib KELISHI MUMKIN?**
Agar subquery NATIJASIDA (masalan `department_id`) HATTO BITTA
NULL BO'LSA — `NOT IN` ning ICHKI MANTIG'I (`value <> NULL AND
value <> NULL AND ...`) — BUTUN IFODANI "UNKNOWN"GA AYLANTIRADI
— natijada HECH QANDAY QATOR QAYTARILMAYDI. `NOT EXISTS`
ISHLATISH — BU MUAMMONI OLDINI OLADI.

**4. `NULL` va bo'sh string (`''`) orasidagi KONSEPTUAL FARQ
nima?**
NULL — "QIYMAT MAVJUD EMAS/NOMA'LUM" holati. Bo'sh string —
KONKRET, MA'LUM QIYMAT (uzunligi nol MATN). Masalan, "O'rta
ism yo'q" — NULL bo'lishi kerak, "O'rta ism — SHUNCHAKI BO'SH
qoldirildi (LEKIN mavjud, faqat qiymatsiz)" — bu KAMDAN-KAM
holat, ODATDA NULL TO'G'RIROQ TANLOV.

**5. `COALESCE` funksiyasi NIMA VAZIFANI BAJARADI, va u qanday
AMALIY HOLATDA ISHLATILADI?**
`COALESCE(a, b, c, ...)` — CHAPDAN O'NGGA, BIRINCHI NULL
BO'LMAGAN qiymatni QAYTARADI. Amaliy holat: agar `phone` NULL
bo'lsa, "Kiritilmagan" DEB KO'RSATISH (`COALESCE(phone,
'Kiritilmagan')`) — bu, C#'dagi `??` (null coalescing)
operatoriga TO'G'RIDAN-TO'G'RI MOS KELADI.
