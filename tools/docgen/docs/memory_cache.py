# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "In-Memory Cache (IMemoryCache)"
CATEGORY = "Caching"
TITLE = "IMemoryCache"
SUBTITLE = "Ilova xotirasida keshlash va uning chegaralari"
FILENAME = "In-Memory Cache (IMemoryCache).docx"


def build(d):
    h1(d, "1. Keshlashning maqsadi")

    para(d, "Kesh — qimmat operatsiya natijasini saqlab qo'yib, keyingi safar uni "
            "qayta hisoblamaslik usuli. \"Qimmat\" deganda bazaga so'rov, tashqi "
            "API chaqiruvi yoki og'ir hisoblash tushuniladi.")

    para(d, "`IMemoryCache` eng oddiy variant — ma'lumot ilovaning o'z xotirasida "
            "saqlanadi. Hech qanday tarmoq yoki serializatsiya yo'q, shuning uchun "
            "u juda tez ishlaydi.")

    note(d, "Lekin asosiy cheklovni boshidan bilish kerak:",
         "Kesh ilova jarayoniga bog'langan. Ilova qayta ishga tushsa, kesh "
         "bo'shaydi. Ikkita nusxa ishlasa, ularning keshlari bir-biridan "
         "mustaqil bo'ladi. Bu ko'p holatda muammo emas, lekin ba'zan juda "
         "chalkash nosozlikka olib keladi — foydalanuvchi sahifani yangilaganda "
         "goh eski, goh yangi ma'lumot ko'radi.")

    # ───────────────────────────────────────────
    h1(d, "2. Ishlatilishi")

    code(d, """builder.Services.AddMemoryCache();""")

    code(d, """public class CategoryService
{
    private readonly IMemoryCache _cache;
    private readonly AppDbContext _db;

    private const string CacheKey = "categories:all";

    public CategoryService(IMemoryCache cache, AppDbContext db)
    {
        _cache = cache;
        _db = db;
    }

    public async Task<IReadOnlyList<CategoryDto>> GetAllAsync(CancellationToken ct)
    {
        if (_cache.TryGetValue(CacheKey, out IReadOnlyList<CategoryDto>? cached))
            return cached!;

        var items = await _db.Categories
            .Select(c => new CategoryDto(c.Id, c.Name))
            .ToListAsync(ct);

        _cache.Set(CacheKey, items, TimeSpan.FromMinutes(10));
        return items;
    }
}""")

    h2(d, "2.1 GetOrCreate bilan qisqaroq")

    code(d, """public Task<IReadOnlyList<CategoryDto>> GetAllAsync(CancellationToken ct)
    => _cache.GetOrCreateAsync(CacheKey, async entry =>
    {
        entry.AbsoluteExpirationRelativeToNow = TimeSpan.FromMinutes(10);

        return (IReadOnlyList<CategoryDto>)await _db.Categories
            .Select(c => new CategoryDto(c.Id, c.Name))
            .ToListAsync(ct);
    })!;""")

    # ───────────────────────────────────────────
    h1(d, "3. Muddat turlari")

    table(d, ["Sozlama", "Ma'nosi"],
          [["`AbsoluteExpiration`", "Aniq vaqtda eskiradi"],
           ["`AbsoluteExpirationRelativeToNow`", "Qo'yilganidan N vaqtdan keyin"],
           ["`SlidingExpiration`", "Oxirgi murojaatdan N vaqtdan keyin"]],
          widths=[6.0, 9.5])

    code(d, """var options = new MemoryCacheEntryOptions
{
    AbsoluteExpirationRelativeToNow = TimeSpan.FromHours(1),
    SlidingExpiration = TimeSpan.FromMinutes(10),
    Priority = CacheItemPriority.High,
    Size = 1
};

_cache.Set(key, value, options);""")

    note(d, "Ikkalasini birga ishlatish foydali:",
         "Faqat `SlidingExpiration` qo'yilsa, tez-tez so'raladigan element "
         "hech qachon eskirmaydi va ma'lumot eskirib qolishi mumkin. "
         "`AbsoluteExpiration` bilan birga qo'ysam, element faol ishlatilayotgan "
         "bo'lsa ham bir soatda bir marta yangilanadi.")

    # ───────────────────────────────────────────
    h1(d, "4. Xotira chegarasi")

    para(d, "Sukut bo'yicha `IMemoryCache` hajm chegarasiga ega emas — u xotira "
            "tugaguncha o'sishi mumkin. Chegara qo'yish uchun hajm hisobi "
            "yoqiladi:")

    code(d, """builder.Services.AddMemoryCache(options =>
{
    options.SizeLimit = 1024;                  // shartli birliklarda
    options.CompactionPercentage = 0.25;       // to'lganda 25% tozalanadi
});""")

    note(d, "`SizeLimit` yoqilsa, bitta qoida majburiy bo'ladi:",
         "Har bir elementga `Size` ko'rsatilishi **shart**. Agar birortasini "
         "unutsam, `InvalidOperationException` chiqadi. Bu boshida bezovta "
         "qiladi, lekin aslida to'g'ri — aks holda chegaraning ma'nosi "
         "qolmaydi.")

    para(d, "`Size` birligi ixtiyoriy — men odatda elementlar sonini hisoblayman "
            "va har biriga `Size = 1` beraman. Katta obyektlar uchun taxminiy "
            "bayt hajmini ishlatish ham mumkin.")

    # ───────────────────────────────────────────
    h1(d, "5. Cache stampede muammosi")

    para(d, "Kesh elementi eskirgan paytda bir vaqtda ko'p so'rov kelsa, "
            "ularning hammasi keshda topa olmaydi va hammasi bazaga boradi. "
            "Bu bazaga to'satdan yuk tushishiga olib keladi.")

    code(d, """private static readonly SemaphoreSlim _lock = new(1, 1);

public async Task<T> GetOrCreateSafeAsync<T>(
    string key, Func<Task<T>> factory, TimeSpan ttl, CancellationToken ct)
{
    if (_cache.TryGetValue(key, out T? cached))
        return cached!;

    await _lock.WaitAsync(ct);
    try
    {
        // Qayta tekshirish — kutish paytida boshqa oqim to'ldirgan bo'lishi mumkin
        if (_cache.TryGetValue(key, out cached))
            return cached!;

        var value = await factory();
        _cache.Set(key, value, ttl);
        return value;
    }
    finally
    {
        _lock.Release();
    }
}""")

    note(d, "Qo'shaloq tekshiruv shu yerda muhim:",
         "Birinchi oqim qulfni oladi va ma'lumotni yuklaydi. Qolganlari kutib "
         "turadi. Qulf bo'shaganda ular navbat bilan kiradi — va agar qayta "
         "tekshirmasam, har biri yana bazaga boradi. Ikkinchi `TryGetValue` "
         "aynan shuni oldini oladi.")

    para(d, "`HybridCache` (.NET 9 dan) bu muammoni o'zi hal qiladi va qo'lda "
            "qulf yozishni kerak qilmaydi.")

    # ───────────────────────────────────────────
    h1(d, "6. Keshni bekor qilish")

    h2(d, "6.1 To'g'ridan-to'g'ri o'chirish")

    code(d, """public async Task UpdateAsync(Category category, CancellationToken ct)
{
    _db.Categories.Update(category);
    await _db.SaveChangesAsync(ct);

    _cache.Remove("categories:all");
    _cache.Remove($"category:{category.Id}");
}""")

    h2(d, "6.2 Bog'liq elementlarni birga bekor qilish")

    code(d, """private CancellationTokenSource _categoriesCts = new();

_cache.Set(key, value, new MemoryCacheEntryOptions()
    .AddExpirationToken(new CancellationChangeToken(_categoriesCts.Token)));

// Barcha bog'liq elementlarni bir yo'la bekor qilish
public void InvalidateCategories()
{
    var old = Interlocked.Exchange(_categoriesCts, new CancellationTokenSource());
    old.Cancel();
    old.Dispose();
}""")

    note(d, "Bekor qilish — keshdagi eng qiyin qism:",
         "Elementni qo'yish oson, lekin uni **qachon** o'chirish kerakligini "
         "aniqlash qiyin. Agar men kesh kalitlarini kod bo'ylab tarqatib "
         "yuborsam, bir joyda yangilaganda boshqasini o'chirishni unutaman. "
         "Shuning uchun kalitlarni bitta statik klassda to'playman va kesh bilan "
         "ishlash faqat bitta xizmat orqali ketadi.")

    code(d, """public static class CacheKeys
{
    public const string AllCategories = "categories:all";
    public static string Category(int id) => $"category:{id}";
    public static string BooksByAuthor(int authorId) => $"books:author:{authorId}";
}""")

    # ───────────────────────────────────────────
    h1(d, "7. Nimani keshlash kerak va kerakmas")

    table(d, ["Keshlash mantiqiy", "Keshlash xavfli"],
          [["Kam o'zgaradigan ma'lumotnoma ro'yxatlari",
            "Foydalanuvchiga xos ma'lumotlar"],
           ["Og'ir hisobot natijalari", "To'lov va buyurtma holati"],
           ["Tashqi API javoblari", "Ruxsat va rol ma'lumotlari"],
           ["Konfiguratsiya qiymatlari", "Tez-tez o'zgaradigan hisoblar"]],
          widths=[7.7, 7.8])

    note(d, "O'ng ustun haqida alohida:",
         "Ruxsat ma'lumotini keshlash — xavfli joy. Foydalanuvchining huquqini "
         "olib tashlasam, u kesh eskirgunicha eski huquq bilan ishlayveradi. "
         "Agar baribir keshlashim kerak bo'lsa, muddatni juda qisqa qilaman va "
         "huquq o'zgarganda keshni aniq bekor qilaman.")

    # ───────────────────────────────────────────
    h1(d, "8. Qachon IMemoryCache yetmaydi")

    para(d, "Bir nechta ilova nusxasi bo'lganda har biri o'z keshini saqlaydi. "
            "Bu ikki muammoga olib keladi: xotira takrorlanadi va ma'lumot "
            "nusxalar orasida farq qiladi.")

    code(d, """// Taqsimlangan kesh
builder.Services.AddStackExchangeRedisCache(options =>
{
    options.Configuration = "localhost:6379";
    options.InstanceName = "myapp:";
});""")

    code(d, """// HybridCache — ikkalasini birlashtiradi (.NET 9+)
builder.Services.AddHybridCache(options =>
{
    options.DefaultEntryOptions = new HybridCacheEntryOptions
    {
        Expiration = TimeSpan.FromMinutes(10),
        LocalCacheExpiration = TimeSpan.FromMinutes(2)
    };
});""")

    code(d, """var categories = await _hybrid.GetOrCreateAsync(
    "categories:all",
    async token => await LoadFromDbAsync(token),
    cancellationToken: ct);""")

    para(d, "`HybridCache` avval lokal xotiradan qaraydi, topmasa Redis ga "
            "boradi, u yerda ham bo'lmasa manbadan yuklaydi. Cache stampede "
            "himoyasi ham o'z ichida bor.")

    # ───────────────────────────────────────────
    h1(d, "9. Xulosa")

    bullets(d, [
        "`IMemoryCache` ma'lumotni ilova xotirasida saqlaydi — eng tez, lekin "
        "jarayonga bog'langan.",
        "Ilova qayta ishga tushsa kesh bo'shaydi; nusxalar keshni bo'lishmaydi.",
        "`AbsoluteExpiration` va `SlidingExpiration` ni birga ishlatish "
        "ma'lumotning eskirib qolishini oldini oladi.",
        "`SizeLimit` yoqilsa, har bir elementga `Size` berish majburiy.",
        "Cache stampede — eskirish paytidagi bir vaqtli so'rovlar; qulf yoki "
        "`HybridCache` bilan hal qilinadi.",
        "Kesh kalitlarini bitta joyda to'plash bekor qilishni ishonchli qiladi.",
        "Ruxsat va to'lov holati kabi ma'lumotlarni keshlashdan ehtiyot bo'lish "
        "kerak.",
        "Bir nechta nusxa bo'lsa — Redis yoki `HybridCache`.",
    ])

    sources(d, [
        ("Cache in-memory in ASP.NET Core",
         "https://learn.microsoft.com/en-us/aspnet/core/performance/caching/memory"),
        ("Distributed caching in ASP.NET Core",
         "https://learn.microsoft.com/en-us/aspnet/core/performance/caching/distributed"),
        ("HybridCache library in ASP.NET Core",
         "https://learn.microsoft.com/en-us/aspnet/core/performance/caching/hybrid"),
    ])
