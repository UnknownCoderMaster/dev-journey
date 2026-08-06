# DB Normalization, Redundancy — Junior A

## 1. Nima? (Ta'rif)

**Normalization** — ma'lumotlar bazasi jadvallarini **takrorlanuvchi
ma'lumot (redundancy)** va **anomaliyalar**dan xoli qilib
loyihalash jarayoni — **Normal Form**lar (1NF, 2NF, 3NF, BCNF)
ketma-ket qoidalar to'plami orqali.

## 2. Nima uchun kerak?

Normallashmagan jadval — bir xil ma'lumotni **bir necha marta**
takrorlaydi. Bu — **Insert, Update, Delete anomaliyalari**ga olib
keladi: bitta ma'lumotni yangilashda **BARCHA nusxalarni** topib
yangilash kerak (aks holda ma'lumot **nomos** bo'lib qoladi).

## 3. Ichida nima sodir bo'ladi? (Mexanizm)

### 3.1 Anomaliyalar

```
Insert Anomaly  — YANGI ma'lumot qo'shish uchun, BOG'LIQ BO'LMAGAN
                   ma'lumot HAM MAJBURIY kiritilishi kerak bo'lishi

Update Anomaly  — bitta faktni YANGILASH uchun, KO'P QATORNI
                   yangilash kerak bo'lishi (BIRINI unutish —
                   NOMOS ma'lumot)

Delete Anomaly  — bitta yozuvni O'CHIRISH — TASODIFAN BOSHQA
                   MUHIM ma'lumotni HAM yo'qotishga olib kelishi
```

### 3.2 1NF (First Normal Form) — atomik qiymatlar

```
❌ Normallashmagan:
┌────┬──────────┬─────────────────────┐
│ Id │ Name      │ Skills               │
├────┼──────────┼─────────────────────┤
│ 1  │ Orzibek   │ "C#, SQL, Docker"    │ ← BIR KATAKDA KO'P qiymat!
└────┴──────────┴─────────────────────┘

✅ 1NF — HAR KATAK — FAQAT BITTA (atomik) qiymat:
┌────┬──────────┬────────┐
│ Id │ Name      │ Skill   │
├────┼──────────┼────────┤
│ 1  │ Orzibek   │ C#      │
│ 1  │ Orzibek   │ SQL     │
│ 1  │ Orzibek   │ Docker  │
└────┴──────────┴────────┘
```

### 3.3 2NF (Second Normal Form) — 1NF + partial dependency yo'q

```
Partial Dependency — COMPOSITE (bir nechta ustunli) PRIMARY KEY'da,
qandaydir ustun — KALIT NING FAQAT BIR QISMIGA bog'liq bo'lishi.

❌ 2NF buzilgan (PK: EmployeeId + ProjectId):
┌────────────┬───────────┬──────────────┬──────────────┐
│ EmployeeId │ ProjectId │ EmployeeName │ ProjectName  │
├────────────┼───────────┼──────────────┼──────────────┤
│ 1          │ 100        │ Orzibek      │ ERP tizimi   │
│ 1          │ 101        │ Orzibek      │ CRM tizimi   │
└────────────┴───────────┴──────────────┴──────────────┘
EmployeeName — FAQAT EmployeeId'ga bog'liq (ProjectId'ga EMAS) —
PARTIAL DEPENDENCY!

✅ 2NF — ALOHIDA jadvalga AJRATISH:
Employees(EmployeeId, EmployeeName)
Projects(ProjectId, ProjectName)
EmployeeProjects(EmployeeId, ProjectId) ← FAQAT bog'lanish
```

### 3.4 3NF (Third Normal Form) — 2NF + transitive dependency yo'q

```
Transitive Dependency — A → B → C bog'liqligi (C — TO'G'RIDAN
A'ga EMAS, B ORQALI bog'liq).

❌ 3NF buzilgan:
┌────┬──────────────┬────────────────┐
│ Id │ DepartmentId │ DepartmentName │
├────┼──────────────┼────────────────┤
│ 1  │ 5             │ IT bo'limi     │
│ 2  │ 5             │ IT bo'limi     │  ← DepartmentName TAKRORLANADI!
└────┴──────────────┴────────────────┘
DepartmentName — Employee.Id'ga EMAS, DepartmentId ORQALI bog'liq
(TRANSITIVE DEPENDENCY)!

✅ 3NF — ALOHIDA jadval:
Employees(Id, DepartmentId)
Departments(DepartmentId, DepartmentName)
```

### 3.5 BCNF (Boyce-Codd Normal Form)

```
BCNF — 3NF'ning KUCHLIROQ shakli: HAR "determinant" (BOSHQA
ustunni ANIQLOVCHI ustun) — CANDIDATE KEY bo'lishi SHART.

3NF va BCNF orasidagi farq — AMALIYOTDA KAMDAN-KAM uchraydi
(faqat MURAKKAB, KO'P candidate key'ga ega jadvallarda sezilarli).
```

### 3.6 Denormalization — qachon kerak

```
Normallashgan DB — JOIN'lar KO'P (murakkab so'rov, SEKINROQ).
Ba'zida — PERFORMANCE uchun ATAYLAB "takrorlash" kiritiladi:

❌ Doim normallashgan:
SELECT e.name, d.name FROM employees e JOIN departments d ON e.dept_id = d.id;

✅ Denormalized (performance uchun):
employees.department_name — ATAYLAB TAKRORLANGAN ustun
(TEZ o'qish, LEKIN department nomi O'ZGARSA — BARCHA yozuvni
YANGILASH kerak)
```

```
Tradeoff: Normalization — YOZISH (write) uchun YAXSHI (izchillik),
Denormalization — O'QISH (read) uchun YAXSHI (tezlik).

Analytics/Reporting DB'lar (masalan data warehouse) — ko'pincha
ATAYLAB denormalized (Star Schema) — chunki ular ASOSAN O'QISH
uchun ishlatiladi.
```

### 3.7 Avoid Redundancy — nima uchun muhim

```
Redundancy (takrorlanuvchi ma'lumot) — DISK JOYINI ISROF qiladi,
LEKIN eng jiddiy muammo — IZCHILLIK (consistency) buzilishi
XAVFI: bir joyda YANGILANGAN, boshqa joyda YANGILANMAGAN ma'lumot
— "qaysi biri TO'G'RI?" degan savolga olib keladi.
```

### 3.8 ERP'da normalization — Employee, Department, Position misoli

```sql
-- ✅ Normallashgan (3NF)
CREATE TABLE departments (id SERIAL PRIMARY KEY, name VARCHAR(100));
CREATE TABLE positions (id SERIAL PRIMARY KEY, title VARCHAR(100), department_id INT REFERENCES departments(id));
CREATE TABLE employees (
    id SERIAL PRIMARY KEY,
    full_name VARCHAR(100),
    position_id INT REFERENCES positions(id) -- position_id ORQALI, department_id TO'G'RIDAN EMAS!
);
-- Xodimning bo'limi — position.department_id ORQALI "TRANZITIV" olinadi (JOIN bilan)
```

### 3.9 Primary Key va Unique Identifier tamoyili

```
Primary Key — HAR JADVALDA, HAR QATORNI NOYOB aniqlaydigan ustun
              (yoki ustunlar kombinatsiyasi) — normalization
              UCHUN ASOS (chunki BOG'LANISH — FK orqali, PK'ga
              ISHORA qilib amalga oshiriladi).
```

## 4. Kod — EF Core'da normallashgan model

```csharp
public class Department { public int Id { get; set; } public string Name { get; set; } = null!; }
public class Position
{
    public int Id { get; set; }
    public string Title { get; set; } = null!;
    public int DepartmentId { get; set; }
    public Department Department { get; set; } = null!;
}
public class Employee
{
    public int Id { get; set; }
    public string FullName { get; set; } = null!;
    public int PositionId { get; set; }
    public Position Position { get; set; } = null!;
}
```

## 5. Qachon ishlatish kerak?

| Vaziyat | Yechim |
|---|---|
| Transaction-heavy tizim (ERP, banking) | To'liq normalization (3NF+) |
| Reporting/Analytics DB | Denormalization (Star Schema) |
| Tez-tez o'qiladigan, kamdan-kam o'zgaradigan ma'lumot | Selektiv denormalization |

## 6. Muhim nuqtalar

- Normalization — **write consistency**ni yaxshilaydi, lekin
  **JOIN sonini oshiradi** (read performance'ga ta'sir qilishi
  mumkin).
- Denormalization — **ataylab, ANIQ performance ehtiyoji** bilan
  qilinishi kerak, "chunki tezroq bo'ladi" degan **taxmin** bilan
  EMAS.
- 3NF — amaliyotda **ko'p** loyiha uchun **yetarli** darajadagi
  normalizatsiya hisoblanadi.

## 7. Imtihon savollari

1. 1NF, 2NF, 3NF orasidagi farqlarni har biriga misol bilan
   tushuntiring.
2. Insert, Update, Delete anomaliyalari nima va ular qanday
   yuzaga keladi?
3. Partial Dependency va Transitive Dependency orasidagi farq
   nima?
4. Denormalization qachon oqilona tanlov hisoblanadi?
5. Normalization va Denormalization orasidagi asosiy tradeoff
   nima?
6. BCNF 3NF'dan qanday farq qiladi?
