# LIMIT, OFFSET — Junior B

## 1. What (Nima?)

**`LIMIT`** — SO'ROV NATIJASIDAGI **QATORLAR SONINI
CHEKLOVCHI** BAND (masalan "FAQAT 20 TA QATOR QAYTAR").
**`OFFSET`** — NATIJANING **BOSHIDAN NECHTA QATORNI
"O'TKAZIB YUBORISH"** KERAKLIGINI BELGILOVCHI BAND (masalan
"BIRINCHI 40 TA QATORNI O'TKAZIB YUBOR"). BIRGALIKDA
ISHLATILGANDA — ULAR, **PAGINATSIYA** (sahifalash, masalan
"2-sahifa, har sahifada 20 ta natija") NI AMALGA OSHIRISHNING
ENG ODDIY YO'LI.

## 2. Real hayot analogiyasi

**LIMIT/OFFSET — KITOB DO'KONIDA, "2-SAHIFA" GA O'TISH.**
Agar DO'KONDA 1000 TA MAHSULOT BO'LSA-YU, SIZ EKRANDA FAQAT
20 TASINI KO'RSATMOQCHI BO'LSANGIZ (LIMIT 20), VA SIZ
2-SAHIFANI KO'RMOQCHI BO'LSANGIZ — SIZ, AVVALGI 20 TA
MAHSULOTNI "VARAQLAB O'TASIZ" (OFFSET 20), KEYIN, KEYINGI
20 TASINI (LIMIT 20) KO'RASIZ.

## 3. Why (Nega kerak?)

Agar WEB SAHIFA, HAR SO'ROVDA, JADVALDAGI **BARCHA
MILLIONLAB QATORNI** QAYTARSA — BU, TARMOQ TRAFIGI, XOTIRA,
VA FOYDALANUVCHI TAJRIBASI (UI) UCHUN **AMALIY EMAS**.
LIMIT/OFFSET — DB SERVERIGA, **FAQAT KERAKLI, KICHIK
QISMNI** QAYTARISHNI BUYURADI — QOLGAN QATORLAR, UMUMAN
TARMOQ ORQALI UZATILMAYDI. Bu, HAR QANDAY REAL LOYIHADAGI
"SAHIFALASH" (PAGINATION) UI PATTERN'NING ASOSI.

## 4. Internals (Ichki mexanizm)

### `LIMIT`/`OFFSET` — DB DARAJASIDA QANDAY BAJARILADI

```sql
SELECT * FROM employees ORDER BY id LIMIT 20 OFFSET 40;
```

```
MUHIM: OFFSET — POSTGRESQL'GA, "BIRINCHI 40 TA QATORNI
HISOBLA, SO'NG TASHLAB YUBOR" DEB BUYURADI — YA'NI, DB,
BARIBIR, O'SHA 40 TA QATORNI **DASTLAB "SKANERLASHI" (yoki
INDEKSDAN O'TISHI)** KERAK, KEYINGINA, ULARNI TASHLAB, 20 TA
KEYINGI QATORNI QAYTARADI. Bu, OFFSET QIYMATI KATTALASHGAN
SARI (masalan OFFSET 1000000), **SO'ROV SEKINLASHA
BORADI** DEGANI — CHUNKI DB, HAR SAFAR, TASHLAB YUBORILADIGAN
QATORLARNI HAM "O'QISHI" KERAK.
```

### "Deep Pagination Problem" — KATTA OFFSET'NING SEKINLIGI

```
OFFSET 0    → DB, 0 ta qatorni tashlab, 20 tasini oladi (TEZ)
OFFSET 1000000 → DB, 1,000,000 ta qatorni "hisoblab" (yoki
                  indeksdan o'tib), TASHLAB YUBORISHI KERAK,
                  KEYINGINA 20 TASINI QAYTARADI (SEKIN!)

BU MUAMMO — "DEEP PAGINATION PROBLEM" (chuqur sahifalash
muammosi) DEB ATALADI — KO'P LOYIHALARDA (masalan, IJTIMOIY
TARMOQ "FEED"LARI), UNI YECHISH UCHUN, OFFSET/LIMIT O'RNIGA,
**KEYSET PAGINATION** (yoki "CURSOR-BASED PAGINATION")
ISHLATILADI.
```

### Keyset Pagination — OFFSET'GA ALTERNATIVA

```sql
-- OFFSET/LIMIT o'rniga — "oxirgi ko'rilgan ID'dan keyingilarni ol"
SELECT * FROM employees WHERE id > 12345 ORDER BY id LIMIT 20;
```

```
KEYSET PAGINATION — "OXIRGI SAHIFADA KO'RINGAN ENG SO'NGGI
QATOR"NING ID'SINI (yoki SARALASH KALITINI) "KURSOR" SIFATIDA
SAQLAYDI VA KEYINGI SO'ROVDA, `WHERE id > kursor_qiymati`
FILTRINI ISHLATADI. Bu — INDEKS ORQALI, TO'G'RIDAN-TO'G'RI,
TO'G'RI JOYDAN BOSHLAB O'QISHNI AMALGA OSHIRADI — OFFSET
QANCHA KATTA BO'LMASIN, TEZLIK O'ZGARMAYDI (O(log n) +
LIMIT), LEKIN "5-SAHIFAGA TO'G'RIDAN-TO'G'RI SAKRASH" KABI
FUNKSIONALLIKNI QO'LLAB-QUVVATLAMAYDI (faqat "keyingi/
oldingi" navigatsiya).
```

### `ORDER BY` — LIMIT/OFFSET bilan HAR DOIM BIRGA ISHLATILISHI SHART

```
AGAR `ORDER BY` YOZILMASA — POSTGRESQL, QATORLARNI, HECH
QANDAY KAFOLATLANGAN TARTIBDA QAYTARMAYDI (FIZIK DISK
TARTIBI, QUERY PLANNER QARORIGA QARAB, HAR SAFAR TURLICHA
BO'LISHI MUMKIN) — bu, "2-SAHIFA"DA, 1-SAHIFADAGI QATORLAR
QAYTA PAYDO BO'LISHI (yoki BA'ZI QATORLAR UMUMAN
KO'RINMASLIGI) KABI XATOLARGA OLIB KELISHI MUMKIN.
```

## 5. Code (Amaliy kod)

```sql
-- Oddiy sahifalash — 3-sahifa, har sahifada 20 ta natija
SELECT * FROM employees ORDER BY id LIMIT 20 OFFSET 40; -- (3-1)*20 = 40

-- Keyset pagination — katta jadvallarda, "deep pagination" muammosini oldini olish uchun
SELECT * FROM employees WHERE id > 12345 ORDER BY id LIMIT 20;

-- Umumiy qatorlar sonini bilish — UI'da "jami sahifalar soni" ko'rsatish uchun
SELECT COUNT(*) FROM employees;
```

```csharp
// EF Core — Offset-based pagination
public async Task<List<Employee>> GetPagedEmployeesAsync(int pageNumber, int pageSize)
{
    return await dbContext.Employees
        .OrderBy(e => e.Id)          // ⚡ ORDER BY — HAR DOIM SHART!
        .Skip((pageNumber - 1) * pageSize) // → SQL OFFSET
        .Take(pageSize)                     // → SQL LIMIT
        .ToListAsync();
}

// EF Core — Keyset (cursor-based) pagination
public async Task<List<Employee>> GetNextPageAsync(int? lastSeenId, int pageSize)
{
    var query = dbContext.Employees.OrderBy(e => e.Id).AsQueryable();

    if (lastSeenId.HasValue)
        query = query.Where(e => e.Id > lastSeenId.Value); // Kursor filtri

    return await query.Take(pageSize).ToListAsync();
}
```

```csharp
// Umumiy Response DTO — pagination bilan
public record PagedResult<T>(List<T> Items, int TotalCount, int PageNumber, int PageSize);

public async Task<PagedResult<Employee>> GetPagedAsync(int pageNumber, int pageSize)
{
    var totalCount = await dbContext.Employees.CountAsync();
    var items = await dbContext.Employees
        .OrderBy(e => e.Id)
        .Skip((pageNumber - 1) * pageSize)
        .Take(pageSize)
        .ToListAsync();

    return new PagedResult<Employee>(items, totalCount, pageNumber, pageSize);
}
```

## 6. Keng tarqalgan xatolar / noto'g'ri tushunchalar

```
❌ "LIMIT/OFFSET, ORDER BY'siz HAM, HAR DOIM BIR XIL, 
   KAFOLATLANGAN NATIJA BERADI" — YO'Q! ORDER BY'siz, DB
   QATORLARNI, HECH QANDAY KAFOLATLANGAN TARTIBDA QAYTARMAYDI
   — SAHIFALAR ORASIDA DUPLIKAT/YETISHMAYDIGAN QATORLAR
   PAYDO BO'LISHI MUMKIN.

❌ "OFFSET, QANCHA KATTA BO'LMASIN, SO'ROV TEZLIGI
   O'ZGARMAYDI" — YO'Q! KATTA OFFSET QIYMATLARIDA (masalan
   1,000,000), DB, TASHLAB YUBORILADIGAN QATORLARNI HAM
   "O'QISHI" KERAK — bu, "DEEP PAGINATION PROBLEM"GA OLIB
   KELADI, SO'ROV SEZILARLI SEKINLASHADI.

❌ "Keyset Pagination, HAR DOIM, Offset/Limit'dan YAXSHIROQ,
   HAMMA HOLATDA ISHLATILISHI KERAK" — YO'Q! Keyset
   Pagination, "5-sahifaga to'g'ridan-to'g'ri sakrash" KABI
   FUNKSIONALLIKNI QO'LLAB-QUVVATLAMAYDI (faqat "keyingi/
   oldingi") — AGAR UI'DA SAHIFA RAQAMLARI (1,2,3...) KO'RSATISH
   KERAK BO'LSA, Offset/Limit ODDIYROQ YECHIM.

❌ "COUNT(*) — LIMIT/OFFSET bilan bir vaqtda, BIR SO'ROVDA
   OLINADI" — YO'Q, ODATDA, "JAMI QATORLAR SONI" (UI'da
   sahifalar sonini ko'rsatish uchun) — ALOHIDA, IKKINCHI
   `SELECT COUNT(*)` SO'ROVI ORQALI OLINADI (BA'ZAN, WINDOW
   FUNCTION — `COUNT(*) OVER()` — ORQALI, BIR SO'ROVDA HAM
   OLISH MUMKIN, LEKIN BU KAMROQ KENG TARQALGAN).
```

## 7. Exam (Interview savollari)

**1. `LIMIT` va `OFFSET` bandlarining vazifasini
TUSHUNTIRING.**
`LIMIT` — NATIJADAGI QATORLAR SONINI CHEKLAYDI (masalan
"faqat 20 ta"). `OFFSET` — NATIJANING BOSHIDAN, NECHTA
QATORNI "O'TKAZIB YUBORISH" KERAKLIGINI BELGILAYDI (masalan
"birinchi 40 tasini tashlab yubor"). Birgalikda —
PAGINATSIYA (sahifalash) ni amalga oshiradi.

**2. Nima uchun `ORDER BY`, `LIMIT`/`OFFSET` bilan BIRGA,
HAR DOIM ISHLATILISHI SHART?**
Chunki `ORDER BY`siz, DB, QATORLARNI, HECH QANDAY
KAFOLATLANGAN TARTIBDA QAYTARMAYDI — SAHIFALAR ORASIDA,
QATORLAR DUPLIKATLANISHI YOKI YETISHMAY QOLISHI MUMKIN
(natija — muhitga/query planner qaroriga qarab TURLICHA
bo'lishi mumkin).

**3. "Deep Pagination Problem" (chuqur sahifalash muammosi)
nima, va u NIMA UCHUN YUZAGA KELADI?**
Katta OFFSET QIYMATLARIDA (masalan OFFSET 1000000), DB,
TASHLAB YUBORILADIGAN QATORLARNI HAM O'QISHI/HISOBLASHI
KERAK — OFFSET QANCHA KATTA BO'LSA, SO'ROV SHUNCHA SEKIN
BAJARILADI. Bu, MASALAN, IJTIMOIY TARMOQ FEED'LARIDA, CHUQUR
SAHIFALARGA O'TISHDA, SEZILARLI SEKINLASHISHGA OLIB KELADI.

**4. Keyset (Cursor-based) Pagination, Offset/Limit'dan
QANDAY FARQ QILADI, VA U QANDAY MUAMMONI YECHADI?**
Keyset Pagination — OFFSET O'RNIGA, "OXIRGI KO'RINGAN
QATORNING ID'SI" NI KURSOR SIFATIDA ISHLATIB, `WHERE id >
kursor` FILTRINI QO'LLAYDI — bu, INDEKS ORQALI, TO'G'RIDAN-
TO'G'RI, TO'G'RI JOYDAN BOSHLAB O'QISHNI TA'MINLAYDI —
OFFSET QANCHA KATTA BO'LMASIN, TEZLIK DEYARLI O'ZGARMAYDI.

**5. Keyset Pagination'ning QANDAY CHEKLOVI (kamchiligi) BOR,
Offset/Limit'ga NISBATAN?**
Keyset Pagination — "5-sahifaga to'g'ridan-to'g'ri sakrash"
KABI FUNKSIONALLIKNI QO'LLAB-QUVVATLAMAYDI — FAQAT "KEYINGI"/
"OLDINGI" (NAVBATDAGI/OLDINGI SAHIFA) NAVIGATSIYASINI
QO'LLAYDI, CHUNKI U, HAR DOIM, "OLDINGI KO'RINGAN QATOR"GA
NISBATAN ISHLAYDI.
