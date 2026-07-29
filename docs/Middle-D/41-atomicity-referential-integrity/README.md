# Atomicity Principle, Referential Integrity — Middle D

> ACID'ning umumiy nazariyasi [29-acid](../29-acid/README.md)da
> yoritilgan. Bu fayl — **DB dizayn darajasida** Atomicity va
> Referential Integrity'ni qanday qo'llash (soft delete, circular FK,
> normalization tradeoff) masalalariga e'tibor qaratadi.

## 1. Nima? (Ta'rif)

**Atomicity (DB dizaynida)** — bitta mantiqiy operatsiya bir nechta
jadval o'zgarishini o'z ichiga olsa ham, **bo'linmas birlik**
sifatida ko'rilishi. **Referential Integrity** — Foreign Key orqali
jadvallar orasidagi bog'liqlikning **har doim izchil** bo'lishi
(masalan, mavjud bo'lmagan Department'ga ishora qiluvchi Employee
bo'lmasligi).

## 2. Nima uchun kerak?

Agar Referential Integrity ta'minlanmasa — `employees.department_id
= 999` bo'lib, lekin `departments` jadvalida ID=999 **umuman
bo'lmasa** — bu **"orphan record"** (yetim yozuv) — dastur bu
yozuvni ko'rsatishga urinsa, **NullReferenceException** yoki noto'g'ri
natija beradi.

## 3. Ichida nima sodir bo'ladi? (Mexanizm)

### 3.1 Atomicity DB dizaynida — bo'linmas operatsiya

```
Misol: "Xodimni boshqa bo'limga ko'chirish" — BIR NECHTA jadvalga
ta'sir qiladi:

1. employees.department_id YANGILANADI
2. departments.employee_count (eski bo'lim) KAMAYADI
3. departments.employee_count (yangi bo'lim) OSHADI

Agar 2-QADAM bajarilib, 3-QADAM XATOGA uchrasa — MA'LUMOT
NOIZCHIL bo'lib qoladi (eski bo'lim SONI kamaygan, yangisiga
QO'SHILMAGAN)!

✅ Yechim — BARCHASINI BITTA transaction ichiga OLISH:
```

```csharp
using var transaction = await _context.Database.BeginTransactionAsync();
try
{
    employee.DepartmentId = newDepartmentId;
    oldDepartment.EmployeeCount--;
    newDepartment.EmployeeCount++;
    await _context.SaveChangesAsync();
    await transaction.CommitAsync();
}
catch { await transaction.RollbackAsync(); throw; }
```

### 3.2 Referential Integrity — Foreign Key constraint

```sql
ALTER TABLE employees ADD CONSTRAINT fk_department
    FOREIGN KEY (department_id) REFERENCES departments(id);
```

Bu — DB darajasida **kafolat** beradi: `employees.department_id` —
FAQAT **mavjud** `departments.id` qiymatiga ishora qila oladi
(yoki `NULL`, agar ustun nullable bo'lsa).

### 3.3 Cascade delete — qachon xavfli

```sql
FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE CASCADE
```

```
⚠️ XAVF: Agar "departments" jadvalidan BITTA yozuv o'chirilsa —
   O'SHA bo'limga tegishli BARCHA xodim yozuvlari HAM AVTOMATIK
   o'chadi! Agar bu — administrator TASODIFIY xatosi bo'lsa —
   YUZLAB xodim ma'lumoti QAYTARIB BO'LMAYDIGAN tarzda YO'QOLADI.

✅ ERP kabi KRITIK tizimlarda — CASCADE o'rniga RESTRICT (o'chirishni
   BLOKLASH) yoki SET NULL (bog'liqlikni UZISH, lekin yozuvni
   SAQLASH) TAVSIYA ETILADI.
```

### 3.4 Soft Delete — `IsDeleted` flag

```csharp
public class Employee
{
    public bool IsDeleted { get; set; }
    public DateTime? DeletedAt { get; set; }
}

// Haqiqiy DELETE o'rniga — FAQAT belgilash
public async Task SoftDeleteAsync(int id)
{
    var emp = await _context.Employees.FindAsync(id);
    emp.IsDeleted = true;
    emp.DeletedAt = DateTime.UtcNow;
    await _context.SaveChangesAsync();
}

// Global Query Filter — Soft-deleted yozuvlar AVTOMATIK yashiriladi
modelBuilder.Entity<Employee>().HasQueryFilter(e => !e.IsDeleted);
```

```
Soft Delete + Referential Integrity:
  ✅ Yozuv "o'chirilgan" deb BELGILANADI, lekin FIZIK saqlanadi
  ✅ Bog'liq (Foreign Key) yozuvlar — BUZILMAYDI (chunki asl
     yozuv HALI MAVJUD)
  ✅ Audit/tarix uchun QIMMATLI (nima o'chirilgani, qachon —
     KUZATIB BORISH mumkin)
  ❌ Har SO'ROVDA `WHERE is_deleted = false` (yoki Query Filter)
     ESLAB QOLISH kerak
```

### 3.5 Circular FK — muammo va yechim

```sql
-- ❌ AYLANMA bog'liqlik: Employee → Department (manager) → Employee?
CREATE TABLE departments (
    id SERIAL PRIMARY KEY,
    manager_id INT REFERENCES employees(id) -- Department MANAGER Employee'ga ishora qiladi
);
CREATE TABLE employees (
    id SERIAL PRIMARY KEY,
    department_id INT REFERENCES departments(id) -- Employee Department'ga ishora qiladi
);
-- 💥 XATO: departments yaratishda employees KERAK, employees yaratishda departments KERAK!
```

```
✅ Yechim: BITTA Foreign Key'ni NULLABLE qilib, KEYINROQ (ikkinchi
   jadval yaratilgandan SO'NG) UPDATE qilish, YOKI DEFERRABLE
   constraint ishlatish:

ALTER TABLE departments
    ADD CONSTRAINT fk_manager FOREIGN KEY (manager_id)
    REFERENCES employees(id) DEFERRABLE INITIALLY DEFERRED;
-- Bu FK — TRANSACTION OXIRIGACHA tekshirilmaydi, ikkalasini BIRGA INSERT qilish MUMKIN
```

### 3.6 Denormalization vs Normalization — tradeoff

```
Normalization (3NF va yuqori):
  ✅ Ma'lumot TAKRORLANMAYDI, IZCHILLIK OSON saqlanadi
  ❌ Ko'p JOIN kerak (murakkab so'rov, biroz SEKINROQ)

Denormalization (ataylab TAKRORLASH):
  ✅ SO'ROV SODDA va TEZ (JOIN kamroq)
  ❌ Ma'lumot TAKRORLANADI — YANGILASH bir nechta joyda BAJARILISHI
     kerak (Atomicity/Consistency XAVFI ORTADI!)

Misol: employees.department_name (denormalized nusxa) — agar
department NOMI o'zgarsa, BARCHA employees YOZUVLARI HAM YANGILANISHI
kerak (aks holda NOIZCHIL bo'lib qoladi)!
```

### 3.7 DB level vs Application level constraint

```
DB level (FOREIGN KEY, CHECK, NOT NULL):
  ✅ HAR DOIM ta'minlanadi (application'dan qat'i nazar, hatto
     to'g'ridan SQL orqali kiritilsa ham)
  ❌ Xato xabari — odatda TEXNIK (developer-friendly, lekin
     foydalanuvchi-friendly EMAS)

Application level (C# validatsiya):
  ✅ Foydalanuvchiga TUSHUNARLI xato xabari BERISH OSON
  ❌ Agar biror YO'L bilan (masalan boshqa servis, migratsiya
     skripti) CHETLAB O'TILSA — TEKSHIRUV BAJARILMAYDI

✅ ENG YAXSHI AMALIYOT: IKKALASINI HAM ishlatish — Application
   darajasida FOYDALANUVCHIGA tushunarli xabar, DB darajasida
   SO'NGGI himoya chizig'i (defense in depth)
```

## 4. Kod — DeleteBehavior sozlash

```csharp
modelBuilder.Entity<Employee>()
    .HasOne(e => e.Department)
    .WithMany(d => d.Employees)
    .HasForeignKey(e => e.DepartmentId)
    .OnDelete(DeleteBehavior.Restrict); // Bo'limda xodim bo'lsa — O'CHIRISHGA RUXSAT BERILMAYDI
```

## 5. Qachon ishlatish kerak?

| Vaziyat | Yechim |
|---|---|
| Bir nechta jadval o'zgarishi — bitta mantiqiy amal | Transaction |
| Tarixiy ma'lumot saqlash kerak | Soft Delete |
| Bola yozuvlar mavjud bo'lganda ota o'chirilmasin | `RESTRICT` |
| Ikki jadval bir-biriga bog'liq (circular) | Nullable FK yoki `DEFERRABLE` |
| Tez-tez o'qiladigan, kam o'zgaradigan hisoblangan qiymat | Denormalization (ehtiyotkorlik bilan) |

## 6. Muhim nuqtalar

- `ON DELETE CASCADE` — ERP/moliyaviy tizimlarda **KAMDAN-KAM**
  tavsiya etiladi — tasodifiy ma'lumot yo'qotish xavfi yuqori.
- Soft Delete — Query Filter **unutilsa**, "o'chirilgan" ma'lumot
  tasodifan ko'rsatilishi mumkin.
- DB va Application darajasidagi constraint — **BIRGA** ishlatilishi
  eng xavfsiz yondashuv.

## 7. Imtihon savollari

1. Atomicity DB dizaynida qanday amaliy muammoni (bir nechta jadval
   yangilanishi) hal qiladi?
2. `ON DELETE CASCADE` nima uchun ERP tizimida xavfli bo'lishi
   mumkin?
3. Soft Delete qanday ishlaydi va u Referential Integrity'ni qanday
   saqlaydi?
4. Circular Foreign Key muammosi qanday yuzaga keladi va qanday
   hal qilinadi?
5. Denormalization qanday tradeoff keltirib chiqaradi?
6. DB darajasidagi va Application darajasidagi constraint'lar
   nima uchun BIRGA ishlatilishi tavsiya etiladi?
