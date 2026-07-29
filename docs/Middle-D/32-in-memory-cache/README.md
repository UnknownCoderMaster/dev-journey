# In-Memory Cache (IMemoryCache) — Middle D

## 1. Nima? (Ta'rif)

**Cache** — tez-tez so'raladigan, kamdan-kam o'zgaradigan ma'lumotni
**xotirada** saqlab, DB'ga qayta-qayta murojaat qilishning oldini
oluvchi mexanizm. `IMemoryCache` — ASP.NET Core'ning built-in,
**bitta server ichida** ishlaydigan cache.

## 2. Nima uchun kerak?

"Barcha bo'limlar ro'yxati" kabi **kamdan-kam o'zgaradigan** ma'lumot
uchun HAR SO'ROVDA DB'ga murojaat qilish — ortiqcha yuklama. Cache —
bu ma'lumotni **birinchi so'rovdan keyin** xotirada saqlab, keyingi
so'rovlarni **DARHOL** javob beradi.

## 3. Ichida nima sodir bo'ladi? (Mexanizm)

### 3.1 O'rnatish

```csharp
builder.Services.AddMemoryCache();
```

```csharp
public class DepartmentService
{
    private readonly IMemoryCache _cache;
    private readonly AppDbContext _context;

    public async Task<List<Department>> GetAllAsync()
    {
        if (_cache.TryGetValue("departments", out List<Department>? cached))
            return cached!; // ✅ Cache'da BOR — DB'GA UMUMAN MUROJAAT QILINMAYDI

        var departments = await _context.Departments.ToListAsync();
        _cache.Set("departments", departments, TimeSpan.FromMinutes(30));
        return departments;
    }
}
```

### 3.2 `GetOrCreate` — qulayroq pattern

```csharp
public async Task<List<Department>> GetAllAsync()
{
    return await _cache.GetOrCreateAsync("departments", async entry =>
    {
        entry.AbsoluteExpirationRelativeToNow = TimeSpan.FromMinutes(30);
        return await _context.Departments.ToListAsync();
    })!;
}
```

### 3.3 Cache options

```csharp
_cache.Set("key", value, new MemoryCacheEntryOptions
{
    AbsoluteExpiration = DateTimeOffset.UtcNow.AddHours(1), // ANIQ vaqtda TUGAYDI
    SlidingExpiration = TimeSpan.FromMinutes(10),            // Har MUROJAATDA muddat QAYTA BOSHLANADI
    Size = 1,                                                 // Cache HAJM CHEGARASI bo'lsa, "og'irligi"
    Priority = CacheItemPriority.High                          // Xotira YETISHMASA, QAYSI birinchi O'CHIRILADI
});
```

```
AbsoluteExpiration — 1 soatdan keyin, MUROJAATLAR SONIDAN qat'i
                      nazar, MUDDATI TUGAYDI

SlidingExpiration  — HAR safar ISHLATILGANDA muddat QAYTA
                      BOSHLANADI (agar 10 daqiqa ICHIDA hech kim
                      SO'RAMASA — O'CHADI)

Ikkalasini BIRGA ishlatish mumkin — "maksimal 1 soat, LEKIN agar
10 daqiqa ISHLATILMASA — ERTAROQ o'chadi"
```

### 3.4 Cache dependency — token based invalidation

```csharp
var cts = new CancellationTokenSource();
_cache.Set("departments", departments, new MemoryCacheEntryOptions
{
    ExpirationTokens = { new CancellationChangeToken(cts.Token) }
});

// Department o'zgartirilganda — QO'LDA cache'ni BEKOR QILISH
public async Task UpdateDepartmentAsync(Department dept)
{
    await _context.SaveChangesAsync();
    cts.Cancel(); // Bog'liq BARCHA cache yozuvlari DARHOL "eskirgan" deb belgilanadi
}
```

### 3.5 Thread safety

```
IMemoryCache — THREAD-SAFE — bir nechta so'rov PARALLEL ravishda
`Get`/`Set` chaqirishi mumkin, ICHKI qulflash (locking) mexanizmi
BOR.

⚠️ LEKIN: `GetOrCreate` — AGAR bir nechta THREAD BIR VAQTDA "cache
BO'SH" holatini ko'rsa — HAMMASI DB'ga MUROJAAT qilishi mumkin
(Cache Stampede, pastda ko'rib chiqiladi).
```

### 3.6 Cache-Aside pattern

```
1. Ma'lumot SO'RALADI
2. Cache TEKSHIRILADI
3. Cache'da BOR bo'lsa → QAYTARILADI (Cache Hit)
4. Cache'da YO'Q bo'lsa → DB'DAN OLINADI, Cache'GA YOZILADI, QAYTARILADI (Cache Miss)
```

Bu — Cache bilan ishlashning **ENG KENG TARQALGAN** patterni
(yuqoridagi barcha kod misollari — aynan shu patternni ifodalaydi).

### 3.7 Nima cache qilinmaydi — user-specific ma'lumotlar

```
❌ Foydalanuvchiga XOS ma'lumotni (masalan "joriy foydalanuvchi
   profili") KEY'siz yoki NOTO'G'RI KEY bilan cache qilish —
   BOSHQA foydalanuvchiga OLDINGI foydalanuvchi ma'lumoti
   KO'RSATILISHI mumkin!

✅ Agar user-specific cache kerak bo'lsa — KEY'GA userId QO'SHILISHI
   SHART: $"employee-profile-{userId}"
```

### 3.8 `IMemoryCache` vs `IDistributedCache` (Redis)

```
IMemoryCache      — BITTA server xotirasida, boshqa serverlar
                     KO'RMAYDI (load balanced tizimda MUAMMOLI!)
IDistributedCache — Redis kabi TASHQI xizmat, BARCHA serverlar
                     BIR XIL cache'ni KO'RADI
```

```
Bitta server:        IMemoryCache YETARLI
Bir nechta server:   IDistributedCache (Redis) KERAK — aks holda
                      Server-1 cache'i Server-2'da KO'RINMAYDI,
                      NOMOS (inconsistent) ma'lumot xavfi bor
```

### 3.9 Cache Stampede muammosi va yechimi

```
Muammo: Cache MUDDATI tugagan ONDA — 1000 ta PARALLEL so'rov BIR
        VAQTDA "cache BO'SH" holatini KO'RADI → 1000 ta so'rov
        BIR VAQTDA DB'GA MUROJAAT QILADI → DB OG'IRLASHADI!

Yechim — Lock (semaphore) bilan FAQAT BITTA so'rov DB'ga borsin:
```

```csharp
private static readonly SemaphoreSlim _lock = new(1, 1);

public async Task<List<Department>> GetAllAsync()
{
    if (_cache.TryGetValue("departments", out List<Department>? cached))
        return cached!;

    await _lock.WaitAsync();
    try
    {
        if (_cache.TryGetValue("departments", out cached)) // QAYTA tekshirish (Double-Check Locking)
            return cached!;

        var departments = await _context.Departments.ToListAsync();
        _cache.Set("departments", departments, TimeSpan.FromMinutes(30));
        return departments;
    }
    finally { _lock.Release(); }
}
```

## 4. Kod — to'liq misol

```csharp
public class DepartmentService
{
    private readonly IMemoryCache _cache;
    private readonly AppDbContext _context;
    private const string CacheKey = "all-departments";

    public async Task<List<Department>> GetAllAsync()
        => (await _cache.GetOrCreateAsync(CacheKey, async entry =>
        {
            entry.SetAbsoluteExpiration(TimeSpan.FromMinutes(30));
            entry.SetSlidingExpiration(TimeSpan.FromMinutes(10));
            return await _context.Departments.AsNoTracking().ToListAsync();
        }))!;

    public void InvalidateCache() => _cache.Remove(CacheKey);
}
```

## 5. Qachon ishlatish kerak?

| Vaziyat | Yechim |
|---|---|
| Kamdan-kam o'zgaradigan, umumiy ma'lumot (bo'limlar, sozlamalar) | `IMemoryCache` |
| Bitta serverdan ko'p (load balanced) tizim | `IDistributedCache` (Redis) |
| Foydalanuvchiga xos ma'lumot | Cache — LEKIN key'ga userId qo'shib |
| Doim o'zgarib turadigan ma'lumot (real-time) | Cache ISHLATILMASIN |

## 6. Muhim nuqtalar

- User-specific ma'lumotni **noto'g'ri** key bilan cache qilish —
  jiddiy **xavfsizlik zaifligi** (boshqa foydalanuvchi ma'lumotini
  ko'rish).
- `IMemoryCache` — load balanced (ko'p server) tizimda **har server
  o'zining** cache'iga ega — bu **muvofiqlik (consistency)**
  muammosi tug'dirishi mumkin.
- Cache Stampede — production'da real muammo, yuqori trafikli
  endpoint'larda lock bilan hal qilinishi kerak.

## 7. Imtihon savollari

1. Cache-Aside pattern nima va u qanday bosqichlardan iborat?
2. `AbsoluteExpiration` va `SlidingExpiration` orasidagi farq nima?
3. `IMemoryCache` va `IDistributedCache` orasidagi asosiy farq nima
   va load balanced tizimda bu qanday muammo tug'diradi?
4. Cache Stampede nima va uni qanday hal qilish mumkin?
5. User-specific ma'lumotni cache qilishda qanday xatolikka yo'l
   qo'ymaslik kerak?
6. Cache dependency (token based invalidation) qanday ishlaydi?
