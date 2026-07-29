# EF Core — Change Tracking — Middle D

## 1. Nima? (Ta'rif)

**Change Tracker** — EF Core'ning DbContext ichida yuklangan har bir
entity holatini (o'zgargan-o'zgarmaganini) kuzatib boruvchi mexanizmi.
`SaveChanges()` chaqirilganda — Change Tracker asosida **SQL
generatsiya** qilinadi.

## 2. Nima uchun kerak?

Change Tracker bo'lmasa — har bir o'zgarish uchun **qo'lda** UPDATE
SQL yozish kerak bo'lardi. EF Core esa — siz obyekt propertysini
o'zgartirasiz, `SaveChanges()` chaqirasiz, va u **avtomatik** aynan
qaysi ustunlar o'zgarganini bilib, minimal SQL yuboradi.

## 3. Ichida nima sodir bo'ladi? (Mexanizm)

### 3.1 Entity holatlari

```
Added     — YANGI, hali DB'da YO'Q (INSERT bo'ladi)
Unchanged — DB'dan YUKLANGAN, HECH narsa o'zgarmagan
Modified  — YUKLANGAN, biror property O'ZGARGAN (UPDATE bo'ladi)
Deleted   — O'CHIRISHGA belgilangan (DELETE bo'ladi)
Detached  — Change Tracker TOMONIDAN KUZATILMAYDI
```

```csharp
var employee = await _context.Employees.FindAsync(1); // Holat: Unchanged
employee.Salary = 5000000;                              // Holat: Modified (AVTOMATIK)
await _context.SaveChangesAsync();                       // UPDATE SQL yuboriladi
// SaveChanges'dan KEYIN — holat yana Unchanged'ga qaytadi
```

### 3.2 `SaveChanges` — Change Tracker'dan SQL generatsiya

```
1. SaveChanges() chaqiriladi
2. Change Tracker BARCHA kuzatilayotgan entity'larni TEKSHIRADI
3. Har bir Modified entity uchun — FAQAT o'zgargan ustunlar
   ANIQLANADI (original va current qiymatlar SOLISHTIRILADI)
4. UPDATE/INSERT/DELETE SQL generatsiya qilinadi
5. Barcha SQL — BITTA TRANSACTION ichida yuboriladi
6. Muvaffaqiyatli bo'lsa — COMMIT, xato bo'lsa — ROLLBACK
```

### 3.3 `AsNoTracking` — qachon ishlatiladi

```csharp
// ❌ Standart (tracking YOQILGAN) — FAQAT o'qish uchun bo'lsa ORTIQCHA
var employees = await _context.Employees.ToListAsync(); // Change Tracker HAR birini KUZATADI

// ✅ AsNoTracking — FAQAT o'qish (read-only) uchun TEZROQ
var employees = await _context.Employees.AsNoTracking().ToListAsync();
```

```
Tracking YOQILGAN:
  - Har entity uchun "original values" NUSXASI SAQLANADI (xotira sarfi)
  - SaveChanges() chaqirilsa — O'ZGARISHLAR aniqlanishi mumkin

AsNoTracking:
  - HECH qanday nusxa SAQLANMAYDI — XOTIRA va CPU tejaladi
  - Faqat o'QISH uchun (GET endpoint'lar) — DEFAULT bo'lishi kerak!
```

**Performance farqi:** katta ro'yxatlarni (masalan 10,000 xodim)
faqat ko'rsatish uchun so'ralganda, `AsNoTracking` — 20-30%gacha
tezroq bo'lishi mumkin (Change Tracker overhead'i yo'q).

### 3.4 `AsNoTrackingWithIdentityResolution`

```csharp
var employees = await _context.Employees
    .Include(e => e.Department)
    .AsNoTrackingWithIdentityResolution() // Bir xil Department — BIR OBYEKT sifatida
    .ToListAsync();
```

Oddiy `AsNoTracking` — bir xil Department'ga tegishli 5 ta xodim
so'ralsa, **5 ta ALOHIDA** `Department` obyekti yaratiladi (hech
biri bog'lanmagan). `AsNoTrackingWithIdentityResolution` — BIR XIL
ID'ga ega obyektlarni **BITTA** instance sifatida qaytaradi (lekin
tracking hali ham YO'Q).

### 3.5 Attach, Entry, State — qo'lda boshqarish

```csharp
var employee = new Employee { Id = 5, FullName = "Yangilangan ism" };
_context.Attach(employee);
_context.Entry(employee).State = EntityState.Modified; // BUTUN entity — Modified deb BELGILANADI

// Faqat BITTA propertyni Modified qilish (partial update)
_context.Entry(employee).Property(e => e.FullName).IsModified = true;
```

### 3.6 Detached entity — API'dan kelgan DTO → Update

```csharp
[HttpPut("{id}")]
public async Task<IActionResult> Update(int id, UpdateEmployeeDto dto)
{
    var employee = _mapper.Map<Employee>(dto); // YANGI obyekt — DbContext HALI BILMAYDI (Detached)
    employee.Id = id;

    _context.Employees.Attach(employee);          // Endi KUZATILADI, lekin Unchanged holatda
    _context.Entry(employee).State = EntityState.Modified; // BARCHA maydonlarni Modified deb BELGILAYMIZ

    await _context.SaveChangesAsync(); // BARCHA ustunlar UPDATE qilinadi (hatto o'zgarmaganlari ham!)
    return NoContent();
}
```

```
⚠️ MUAMMO: Bu usul BUTUN entity'ni UPDATE qiladi — hatto o'zgarmagan
   maydonlar ham (agar DTO ularni to'liq to'ldirmagan bo'lsa — NULL
   bilan USTIDAN YOZILISHI mumkin!)

✅ YAXSHIROQ: DB'dan MAVJUD entity'ni YUKLAB, faqat kerakli
   maydonlarni O'ZGARTIRISH:

var employee = await _context.Employees.FindAsync(id);
_mapper.Map(dto, employee); // Faqat DTO'dagi maydonlar KO'CHIRILADI
await _context.SaveChangesAsync(); // FAQAT haqiqatda O'ZGARGAN ustunlar UPDATE qilinadi
```

### 3.7 `ExecuteUpdate`, `ExecuteDelete` (EF Core 7+) — bulk operations

```csharp
// ❌ AN'ANAVIY — HAR bir entity YUKLANADI, keyin O'ZGARTIRILADI (sekin, ko'p xotira)
var employees = await _context.Employees.Where(e => e.DepartmentId == 5).ToListAsync();
foreach (var e in employees) e.IsActive = false;
await _context.SaveChangesAsync();

// ✅ EF Core 7+ — TO'G'RIDAN SQL UPDATE, entity YUKLANMAYDI!
await _context.Employees
    .Where(e => e.DepartmentId == 5)
    .ExecuteUpdateAsync(s => s.SetProperty(e => e.IsActive, false));

// Bulk delete
await _context.Employees.Where(e => e.IsActive == false).ExecuteDeleteAsync();
```

```
ExecuteUpdate/ExecuteDelete — Change Tracker'ni UMUMAN ISHLATMAYDI —
TO'G'RIDAN "UPDATE employees SET is_active = false WHERE
department_id = 5" SQL generatsiya qilinadi — MINGLAB qatorni
o'zgartirish uchun JUDA TEZ (entity'larni yuklash/kuzatish
OVERHEAD'i YO'Q).
```

### 3.8 Change Tracker performance — ko'p entity bilan

```
❌ 100,000 ta entity'ni bitta DbContext'da YUKLASH (tracking bilan)
   → Change Tracker HAR BIRI uchun "original values" saqlaydi
   → XOTIRA sarfi VA SaveChanges() TEKSHIRISH vaqti SEZILARLI oshadi

✅ Yechimlar:
   - AsNoTracking() (faqat o'qish uchun)
   - ChangeTracker.AutoDetectChangesEnabled = false (qo'lda DetectChanges() chaqirish)
   - Katta bulk operatsiyalar uchun ExecuteUpdate/ExecuteDelete
```

## 4. Kod — to'liq misol

```csharp
// Faqat o'qish — AsNoTracking
public async Task<List<EmployeeDto>> GetAllAsync()
    => await _context.Employees.AsNoTracking()
        .Select(e => new EmployeeDto(e.Id, e.FullName))
        .ToListAsync();

// Yangilash — mavjudni yuklab, DTO'ni map qilish
public async Task UpdateAsync(int id, UpdateEmployeeDto dto)
{
    var employee = await _context.Employees.FindAsync(id)
        ?? throw new NotFoundException("Xodim topilmadi");
    _mapper.Map(dto, employee);
    await _context.SaveChangesAsync();
}
```

## 5. Qachon ishlatish kerak?

| Vaziyat | Yechim |
|---|---|
| Faqat ko'rsatish (GET), o'zgartirish YO'Q | `AsNoTracking()` |
| Entity yangilanadi | Tracking YOQILGAN (default) |
| Ko'p (1000+) qatorni bir shartga ko'ra yangilash/o'chirish | `ExecuteUpdate`/`ExecuteDelete` |
| Bir xil bog'liq entity ko'p marta uchraydi, faqat o'qish | `AsNoTrackingWithIdentityResolution` |

## 6. Muhim nuqtalar

- Default GET endpoint'larda `AsNoTracking()` ISHLATILMASA —
  keraksiz xotira/CPU sarfi bo'ladi (kichik loyihada sezilmasligi
  mumkin, lekin katta trafikda MUHIM).
- `Attach` + `State = Modified` — BARCHA ustunlarni UPDATE qiladi,
  bu ba'zan **kutilmagan** ma'lumot yo'qotishga olib kelishi mumkin.
- `ExecuteUpdate`/`ExecuteDelete` — Change Tracker'ni CHETLAB o'tadi,
  shuning uchun agar entity xotirada YUKLANGAN bo'lsa, u BILAN
  SINXRON EMAS qolishi mumkin (qayta yuklash kerak bo'lishi mumkin).

## 7. Imtihon savollari

1. Entity'ning 5 ta asosiy holatini (Added, Modified va h.k.) ayting.
2. `AsNoTracking()` qachon ishlatiladi va u qanday performance
   foyda beradi?
3. `Attach` + `EntityState.Modified` bilan yangilashning nima
   xavfi bor?
4. `ExecuteUpdate`/`ExecuteDelete` (EF Core 7+) an'anaviy yondashuvdan
   nima bilan farq qiladi?
5. `AsNoTrackingWithIdentityResolution` oddiy `AsNoTracking`dan
   qanday farq qiladi?
6. Change Tracker performance muammosi ko'p entity bilan ishlashda
   qanday yuzaga keladi va qanday hal qilinadi?
