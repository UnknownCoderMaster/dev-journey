# PostgreSQL View, Materialized View — Middle D

## 1. Nima? (Ta'rif)

**View** — SQL so'rovni **nomlangan, virtual jadval** sifatida
saqlash (haqiqiy ma'lumot saqlanmaydi, har so'rovda **qayta
hisoblanadi**). **Materialized View** — View'ga o'xshash, lekin
natija **haqiqatda diskda saqlanadi** (keshlanadi).

## 2. Nima uchun kerak?

Murakkab, ko'p JOIN'li so'rov (masalan, "har bo'lim uchun xodimlar
soni va o'rtacha maosh") — har safar to'liq yozib bo'lmaydi. View —
bu so'rovni **bir marta belgilab**, keyin oddiy jadvaldek
ishlatish imkonini beradi.

## 3. Ichida nima sodir bo'ladi? (Mexanizm)

### 3.1 Oddiy View — har so'rovda qayta hisoblanadi

```sql
CREATE VIEW department_stats AS
SELECT d.id, d.name, COUNT(e.id) AS employee_count, AVG(e.salary) AS avg_salary
FROM departments d
LEFT JOIN employees e ON e.department_id = d.id
GROUP BY d.id, d.name;

SELECT * FROM department_stats WHERE employee_count > 10;
```

```
View — HAQIQIY MA'LUMOT SAQLAMAYDI! `SELECT * FROM department_stats`
chaqirilganda — ICHKARIDA HAR SAFAR ASL SO'ROV (JOIN + GROUP BY)
QAYTA BAJARILADI. Bu — SQL'ni "QAYTA ISHLATISH" (DRY) uchun QULAY,
lekin PERFORMANCE FOYDASI YO'Q (murakkab so'rov HAR DOIM QAYTA
HISOBLANADI).
```

### 3.2 Updatable View

```sql
CREATE VIEW active_employees AS
SELECT id, full_name, salary FROM employees WHERE is_active = true;

UPDATE active_employees SET salary = 6000000 WHERE id = 1; -- ISHLAYDI!
-- Ichkarida — ASL "employees" jadvaliga UPDATE YO'NALTIRILADI
```

```
View — UPDATE/INSERT/DELETE'ga RUXSAT beradi, AGAR:
  - FAQAT BITTA jadvaldan (JOIN YO'Q)
  - GROUP BY, DISTINCT, aggregate funksiya YO'Q
  - Oddiy, "to'g'ridan" mapping bo'lsa
```

### 3.3 Materialized View — natija saqlanadi

```sql
CREATE MATERIALIZED VIEW department_stats_mv AS
SELECT d.id, d.name, COUNT(e.id) AS employee_count, AVG(e.salary) AS avg_salary
FROM departments d
LEFT JOIN employees e ON e.department_id = d.id
GROUP BY d.id, d.name;

SELECT * FROM department_stats_mv; -- TEZ! (natija DISKDA SAQLANGAN, QAYTA hisoblanmaydi)
```

### 3.4 `REFRESH MATERIALIZED VIEW`

```sql
REFRESH MATERIALIZED VIEW department_stats_mv; -- Ma'lumotni YANGILAYDI (qayta hisoblab, qayta saqlaydi)

-- Concurrently — REFRESH davomida ESKI ma'lumot O'QISH UCHUN mavjud (bloklanmaydi)
REFRESH MATERIALIZED VIEW CONCURRENTLY department_stats_mv; -- UNIQUE INDEX talab qiladi!
```

```
⚠️ Materialized View — REFRESH qilinmaguncha ESKI ma'lumotni
   ko'rsatadi (asl jadvallar o'zgarsa ham, Materialized View
   AVTOMATIK yangilanMAYDI)! Odatda CRON job (Hangfire/pg_cron)
   orqali MUNTAZAM (masalan har soat) REFRESH qilinadi.
```

### 3.5 View vs Materialized View — farqi

| | View | Materialized View |
|---|---|---|
| Ma'lumot saqlanishi | ❌ Yo'q (har so'rovda hisoblanadi) | ✅ Ha (diskda) |
| Tezlik | Sekin (murakkab so'rov uchun) | Tez |
| Har doim aktual | ✅ Ha | ❌ Yo'q (REFRESH kerak) |
| Indeks qo'yish | ❌ Mumkin emas | ✅ Mumkin |
| Qachon ishlatiladi | Kichik/tez so'rov, DOIM aktual bo'lishi kerak | Katta, murakkab, "hisobot" tipidagi so'rov |

### 3.6 EF Core'da View — `ToView()`, `[Keyless]`

```csharp
[Keyless] // View'da odatda "Primary Key" yo'q
public class DepartmentStats
{
    public int Id { get; set; }
    public string Name { get; set; } = null!;
    public int EmployeeCount { get; set; }
    public decimal AvgSalary { get; set; }
}

protected override void OnModelCreating(ModelBuilder modelBuilder)
{
    modelBuilder.Entity<DepartmentStats>().ToView("department_stats").HasNoKey();
}

// So'rov — oddiy DbSet kabi
var stats = await _context.Set<DepartmentStats>().ToListAsync();
```

`[Keyless]` — View'lar odatda **noyob identifikator**ga ega bo'lmasa
ham EF Core orqali so'ralishi mumkin (lekin bu holda entity —
**faqat o'qish** uchun, `Update`/`SaveChanges` ISHLAMAYDI).

### 3.7 Index on Materialized View

```sql
CREATE UNIQUE INDEX idx_dept_stats_id ON department_stats_mv (id);
```

`REFRESH ... CONCURRENTLY` ishlashi uchun **UNIQUE INDEX** MAJBURIY.
Bundan tashqari, Materialized View'da **oddiy indeks** ham — tez-tez
so'raladigan ustunlarda (masalan `employee_count`) qo'shilishi
mumkin, chunki bu haqiqiy jadval kabi ishlaydi.

## 4. Kod — CRON bilan avtomatik REFRESH

```csharp
// Hangfire orqali — har soat Materialized View'ni yangilash
RecurringJob.AddOrUpdate("refresh-dept-stats",
    () => _context.Database.ExecuteSqlRawAsync("REFRESH MATERIALIZED VIEW department_stats_mv"),
    Cron.Hourly);
```

## 5. Qachon ishlatish kerak?

| Vaziyat | Yechim |
|---|---|
| Murakkab SQL'ni qayta ishlatish, DOIM aktual bo'lishi kerak | View |
| Og'ir hisobot, "biroz eski" ma'lumot QABUL QILINADI | Materialized View |
| Dashboard, analytics (tez-tez o'qiladi, kamdan-kam o'zgaradi) | Materialized View + CRON refresh |
| Oddiy, tez so'rov | View yoki to'g'ridan LINQ/SQL |

## 6. Muhim nuqtalar

- Materialized View — **eskirgan ma'lumot** ko'rsatishi mumkin,
  REFRESH strategiyasi (qachon, qanday chastota bilan) aniq
  belgilanishi kerak.
- View — performance FOYDA BERMAYDI (faqat SQL'ni qayta ishlatish
  qulayligini beradi).
- `REFRESH CONCURRENTLY` — UNIQUE INDEX talab qiladi, aks holda xato
  beradi.

## 7. Imtihon savollari

1. View va Materialized View orasidagi asosiy farq nima?
2. Updatable View qanday shartlarda ishlaydi?
3. `REFRESH MATERIALIZED VIEW CONCURRENTLY` uchun nima talab
   qilinadi va nima uchun?
4. EF Core'da View'ni ifodalash uchun `[Keyless]` nima uchun kerak?
5. Qachon oddiy View, qachon Materialized View tanlanadi?
