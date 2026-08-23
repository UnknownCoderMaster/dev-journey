# Primary Key va Unique Identifier Principles — Junior B

## 1. What (Nima?)

**Primary Key (PK)** — jadvalning HAR QATORINI **YAGONA, NOYOB
RAVISHDA ANIQLOVCHI** ustun (yoki ustunlar kombinatsiyasi) — HAR
JADVALDA **FAQAT BITTA** PK bo'lishi mumkin. **Unique Identifier**
— UMUMIYROQ tushuncha: BIRON QIYMAT (PK bo'lishi SHART emas, masalan
Email) — jadval ICHIDA **TAKRORLANMASLIGINI** kafolatlovchi
tamoyil (`UNIQUE` constraint orqali).

## 2. Real hayot analogiyasi

**Primary Key — PASPORT SERIYA-RAQAMI.** Har FUQARO (qator) —
O'ZINING NOYOB PASPORT RAQAMIGA EGA (PK) — IKKI ODAMDA BIR XIL
PASPORT RAQAMI BO'LISHI **MUMKIN EMAS**, va BU RAQAM — DAVLAT
HUJJATLARIDA (boshqa jadvallarda, Foreign Key sifatida) SHU
ODAMNI ANIQLASH uchun ISHLATILADI.

**Unique Identifier (masalan Email) — TELEFON RAQAMI.** Telefon
raqami HAM NOYOB (IKKI ODAMDA BIR XIL bo'lmaydi), LEKIN U —
"RASMIY IDENTIFIKATOR" (pasport) EMAS — BOSHQA HUJJATLAR TELEFON
RAQAMI ORQALI EMAS, PASPORT SERIYASI ORQALI SIZGA "BOG'LANADI".

## 3. Why (Nega kerak?)

Primary Key BO'LMASA — DB **QAYSI QATOR QAYSI** EKANINI ANIQ
BILA OLMAYDI, HAM **RELATIONSHIP** (Foreign Key orqali BOG'LASH)
QURISH IMKONSIZ BO'LARDI. PK — DB'ning **B-TREE INDEKSI** ORQALI,
QATORNI **TEZ TOPISH** (O(log n)) imkonini HAM BERADI — bu, PK
bo'yicha SO'ROVLARNI SEZILARLI TEZLASHTIRADI.

**Natural Key vs Surrogate Key — MUQOBILLARNI SOLISHTIRISH:**
Natural Key (masalan Email, Passport Number) — REAL DUNYODAGI
MA'LUMOTGA ASOSLANADI (O'ZGARISHI MUMKIN, masalan Email
YANGILANISHI). Surrogate Key (masalan avtomatik `SERIAL` ID) —
BIZNES MANTIQIGA BOG'LIQ EMAS, HECH QACHON O'ZGARMAYDI —
KO'PCHILIK zamonaviy loyihalarda SURROGATE KEY TAVSIYA ETILADI.

## 4. Internals (Ichki mexanizm)

### PK va B-Tree indeks — MAJBURIY BOG'LIQLIK

```
PRIMARY KEY belgilanganda — PostgreSQL AVTOMATIK ravishda,
O'SHA ustun(lar) ustida UNIQUE B-TREE INDEKS YARATADI (batafsil
docs/Middle-D/40-indexing'da). Bu — HAR PK bo'yicha SO'ROV
(`WHERE id = 5`) — O(log n) VAQTDA BAJARILISHINI KAFOLATLAYDI.
```

### `SERIAL`/`IDENTITY` — Surrogate Key IMPLEMENTATSIYASI

```sql
CREATE TABLE employees (
    id SERIAL PRIMARY KEY,  -- Avtomatik OSHUVCHI, Sequence ASOSIDA
    full_name VARCHAR(100) NOT NULL
);
```

```
SERIAL — ICHKARIDA "Sequence" OBYEKTINI YARATADI (batafsil
docs/Junior-B/postgresql'dagi "Generated as Identity" fayliga
qarang) — HAR YANGI QATOR — Sequence'DAN KEYINGI QIYMATNI OLADI,
BU JARAYON — TRANZAKSIYADAN MUSTAQIL (PERFORMANCE uchun), shuning
uchun ID'lar ORASIDA "GAP" (uzilish) BO'LISHI MUMKIN (rollback
qilingan tranzaksiyalarda) — bu — NORMAL HOLAT.
```

### Composite Primary Key — bir NECHTA ustundan IBORAT

```sql
CREATE TABLE employee_projects (
    employee_id INT REFERENCES employees(id),
    project_id INT REFERENCES projects(id),
    PRIMARY KEY (employee_id, project_id) -- IKKALASI BIRGA — NOYOB
);
```

```
Composite PK — HAR ALOHIDA USTUN TAKRORLANISHI MUMKIN
(employee_id=1 bir necha QATORDA bo'lishi mumkin), LEKIN
KOMBINATSIYA (employee_id + project_id) — HAR DOIM NOYOB —
ODATDA MANY-TO-MANY JUNCTION jadvallarida ISHLATILADI.
```

### UNIQUE constraint — PK'DAN FARQI

```sql
CREATE TABLE employees (
    id SERIAL PRIMARY KEY,
    email VARCHAR(200) UNIQUE NOT NULL  -- UNIQUE, LEKIN PK EMAS
);
```

```
Farqlar:
  PRIMARY KEY — FAQAT BITTA (HAR JADVALDA), NULL QIYMAT
                QABUL QILMAYDI, BOSHQA jadvallar UNGA "REFERENCE"
                BERADI (Foreign Key)
  UNIQUE       — BIR NECHTA BO'LISHI MUMKIN (HAR JADVALDA), NULL
                QIYMATGA (odatda) RUXSAT BERADI (PostgreSQL'da
                BIR NECHTA NULL — TAKRORLANISHGA RUXSAT ETILADI,
                chunki NULL ≠ NULL semantikasi)
```

### GUID/UUID — Distributed sistemalar uchun ALTERNATIV

```
SERIAL — MARKAZLASHGAN (bitta DB SEQUENCE) — DISTRIBUTED
sistemalarda (bir nechta DB, offline-first mobil ilova) —
IKKI TURLI JOYDA BIR XIL ID GENERATSIYA QILINISHI MUMKIN
(KOLLIZIYA).

UUID (masalan Guid.NewGuid()) — 128-BIT, DEYARLI KOLLIZIYASIZ
GENERATSIYA QILINADI — HAR QANDAY JOYDA (MARKAZLASHMAGAN HOLDA)
YARATILISHI MUMKIN, LEKIN:
  - KATTAROQ (16 bayt, INT'ning 4 baytiga NISBATAN)
  - B-TREE INDEKSDA — TASODIFIY TARTIBDA JOYLASHGANI uchun
    "INDEX FRAGMENTATION" (parchalanish) MUAMMOSINI KELTIRIB
    CHIQARISHI MUMKIN (SERIAL — KETMA-KET, INDEKS "TARTIBLI"
    O'SADI)
```

## 5. Code (Amaliy kod)

```sql
-- Surrogate Key (TAVSIYA ETILADI) — biznes mantiqiga bog'liq EMAS
CREATE TABLE employees (
    id SERIAL PRIMARY KEY,
    email VARCHAR(200) UNIQUE NOT NULL, -- Unique Identifier, LEKIN PK EMAS
    full_name VARCHAR(100) NOT NULL
);

-- Composite Primary Key — Many-to-Many junction jadval
CREATE TABLE employee_projects (
    employee_id INT NOT NULL REFERENCES employees(id) ON DELETE CASCADE,
    project_id INT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    assigned_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    PRIMARY KEY (employee_id, project_id)
);
```

```csharp
// EF Core'da — Surrogate Key (default) va Composite Key
public class Employee
{
    public int Id { get; set; } // AVTOMATIK PK deb ANIQLANADI ("Id" konvensiyasi)
    public string Email { get; set; } = null!;
}

modelBuilder.Entity<Employee>().HasIndex(e => e.Email).IsUnique(); // UNIQUE constraint

public class EmployeeProject
{
    public int EmployeeId { get; set; }
    public int ProjectId { get; set; }
}
modelBuilder.Entity<EmployeeProject>().HasKey(ep => new { ep.EmployeeId, ep.ProjectId }); // Composite PK
```

```csharp
// GUID Primary Key — Distributed sistema uchun
public class Order
{
    public Guid Id { get; set; } = Guid.NewGuid();
}
// PostgreSQL'da — UUID turi bilan:
// modelBuilder.Entity<Order>().Property(o => o.Id).HasDefaultValueSql("gen_random_uuid()");
```

## 6. Keng tarqalgan xatolar / noto'g'ri tushunchalar

```
❌ "Email — YAXSHI Primary Key TANLOVI" — XAVFLI! Email
   O'ZGARISHI MUMKIN (foydalanuvchi almashtirishi mumkin) —
   PK esa, BOSHQA jadvallar (Foreign Key orqali) UNGA
   "REFERENCE" berganligi uchun, O'ZGARMAS BO'LISHI KERAK.
   Surrogate Key (SERIAL/UUID) TAVSIYA ETILADI.

❌ "UNIQUE constraint — Primary Key BILAN BIR XIL" — YO'Q!
   UNIQUE — NULL qiymatga RUXSAT berishi mumkin (va bir nechta
   NULL bo'lishi mumkin), BIR jadvalda BIR NECHTA UNIQUE
   constraint bo'lishi mumkin. PK — FAQAT BITTA, NULL'siz.

❌ "SERIAL ID'lar HAR DOIM KETMA-KET (1,2,3,...) bo'ladi, GAP
   bo'lmaydi" — NOTO'G'RI! Rollback qilingan tranzaksiyalar,
   yoki bekor qilingan INSERT'lar — GAP (uzilish) qoldirishi
   MUMKIN — bu, PERFORMANCE uchun ATAYLAB QILINGAN DIZAYN
   (Sequence — tranzaksiyadan MUSTAQIL).

❌ "Composite Primary Key — HAR DOIM YOMON DIZAYN" — Many-to-Many
   JUNCTION jadvallarda — Composite PK — TABIIY VA TO'G'RI
   YECHIM (qo'shimcha SURROGATE ID — ORTIQCHA bo'lishi mumkin).

❌ "GUID — SERIAL'dan HAR DOIM YAXSHIROQ, chunki 'kollizyasiz'"
   — TRADEOFF bor: GUID — KATTAROQ, VA B-TREE INDEKSDA
   "PARCHALANISH" (fragmentation) MUAMMOSINI keltirib chiqarishi
   mumkin (agar TASODIFIY GUID — masalan v4 — ishlatilsa).
```

## 7. Exam (Interview savollari)

**1. Primary Key va Unique constraint orasidagi FARQ nima?**
Primary Key — HAR jadvalda FAQAT BITTA, NULL qabul QILMAYDI, VA
Foreign Key orqali BOSHQA jadvallar UNGA "reference" beradi.
Unique — bir jadvalda BIR NECHTA bo'lishi mumkin, NULL qiymatga
(ba'zan bir nechtasiga) ruxsat beriladi.

**2. Surrogate Key va Natural Key orasidagi TRADEOFF nima?**
Natural Key (masalan Email) — biznes ma'lumotiga ASOSLANADI,
O'ZGARISHI MUMKIN — bu, Foreign Key sifatida ISHLATILGANDA
MUAMMOLI. Surrogate Key (masalan SERIAL ID) — biznes mantiqiga
BOG'LIQ EMAS, HECH QACHON O'ZGARMAYDI — shuning uchun KO'PCHILIK
zamonaviy loyihada TAVSIYA ETILADI.

**3. Nima uchun `SERIAL` (avtomatik oshuvchi) ID'larda "GAP"
(uzilish) BO'LISHI MUMKIN, va bu MUAMMO HISOBLANADIMI?**
Sequence — TRANZAKSIYADAN MUSTAQIL ishlaydi (performance uchun) —
ROLLBACK qilingan INSERT — O'ZI OLGAN ID'ni "QAYTARIB
BERMAYDI". Bu — NORMAL HOLAT, chunki Primary Key uchun FAQAT
NOYOBLIK MUHIM, KETMA-KETLIK EMAS.

**4. Composite Primary Key qachon TO'G'RI DIZAYN TANLOVI
HISOBLANADI?**
Many-to-Many JUNCTION (bog'lovchi) jadvallarda — masalan
`EmployeeProjects(EmployeeId, ProjectId)` — ikkala ustun BIRGA
NOYOB bo'lishi TABIIY talab — Composite PK, QO'SHIMCHA
SURROGATE ID YARATMASDAN, BU MUNOSABATNI TO'G'RI IFODALAYDI.

**5. GUID Primary Key ishlatishning QANDAY AFZALLIGI va
KAMCHILIGI bor?**
Afzallik: MARKAZLASHMAGAN (distributed) tizimlarda, TURLI
JOYLARDA (masalan offline mobil ilova) KOLLIZIYASIZ generatsiya
qilinishi mumkin. Kamchilik: 16 bayt (INT'ning 4 baytiga
nisbatan KATTAROQ), va agar TASODIFIY (v4) bo'lsa, B-TREE
INDEKSDA "FRAGMENTATION" (parchalanish) muammosini keltirib
chiqarishi mumkin.
