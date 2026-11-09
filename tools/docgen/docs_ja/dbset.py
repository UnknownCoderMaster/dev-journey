# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "DbSet"
CATEGORY = "EF CORE"
TITLE = "DbSet"
SUBTITLE = "Entity to'plami bilan ishlash"
FILENAME = "DbSet.docx"


def build(d):
    h1(d, "1. DbSet nima")

    para(d, "`DbSet<T>` — ma'lum entity turi bilan ishlash uchun kirish "
            "nuqtasi. U jadvalga emas, **entity to'plamiga** ishora qiladi: "
            "bazadagi satrlar va change tracker'dagi o'zgarishlar birgalikda.")

    code(d, """public sealed class AppDbContext(DbContextOptions<AppDbContext> options)
    : DbContext(options)
{
    public DbSet<Order> Orders => Set<Order>();
    public DbSet<Customer> Customers => Set<Customer>();
    public DbSet<Product> Products => Set<Product>();
}""")

    para(d, "Yozish shakli ikki xil bo'lishi mumkin:")

    code(d, """// Klassik: EF o'zi to'ldiradi
public DbSet<Order> Orders { get; set; } = null!;

// Yangi: Set<T>() ga yo'naltirish
public DbSet<Order> Orders => Set<Order>();""")

    para(d, "Ikkinchisini afzal ko'raman: `null!` yozish kerak emas va "
            "xossa faqat o'qish uchun bo'ladi, ya'ni tashqaridan "
            "almashtirib bo'lmaydi.")

    note(d, "Muhim",
         "`DbSet<T>` e'lon qilinishi entity'ni modelga qo'shadi. Lekin "
         "`DbSet` bo'lmasa ham entity modelga tushishi mumkin — masalan "
         "navigatsiya orqali bog'langan bo'lsa yoki "
         "`OnModelCreating` da e'lon qilinsa.")

    # ───────────────────────────────────────────
    h1(d, "2. So'rov yuborish")

    code(d, """// IQueryable — hali bazaga bormaydi
var query = db.Orders.Where(o => o.Status == OrderStatus.Paid);

// Bu chaqiruvlar so'rovni bajaradi
var list  = await query.ToListAsync(ct);
var first = await query.FirstOrDefaultAsync(ct);
var count = await query.CountAsync(ct);
var any   = await query.AnyAsync(ct);""")

    para(d, "`DbSet<T>` `IQueryable<T>` ni amalga oshiradi, shuning uchun "
            "LINQ ifodalari SQL ga tarjima qilinadi. So'rov **kechiktirilgan** "
            "(deferred): u faqat natija so'ralganda bajariladi.")

    h2(d, "Kechiktirilganlikning amaliy natijasi")

    code(d, """// So'rovni qismlab qurish mumkin
IQueryable<Order> query = db.Orders;

if (status is not null)
    query = query.Where(o => o.Status == status);

if (from is not null)
    query = query.Where(o => o.CreatedAt >= from);

var result = await query
    .OrderByDescending(o => o.CreatedAt)
    .Take(50)
    .ToListAsync(ct);""")

    para(d, "Bu yerda bazaga faqat bitta so'rov ketadi va unda hamma "
            "filtr birlashgan bo'ladi. Agar oraliqda `ToList()` "
            "chaqirilsa, qolgan filtrlar xotirada bajariladi — ya'ni "
            "butun jadval tortib olinadi.")

    # ───────────────────────────────────────────
    h1(d, "3. Find va FirstOrDefault farqi")

    code(d, """var a = await db.Orders.FindAsync([id], ct);
var b = await db.Orders.FirstOrDefaultAsync(o => o.Id == id, ct);""")

    para(d, "Farq muhim: `FindAsync` avval **change tracker'ni** "
            "tekshiradi. Agar entity allaqachon xotirada bo'lsa, bazaga "
            "umuman bormaydi. `FirstOrDefaultAsync` esa har safar so'rov "
            "yuboradi.")

    bullets(d, [
        "`FindAsync` — faqat birlamchi kalit bo'yicha, `Include` "
        "ishlatilmaydi, tracker'dan qaytishi mumkin.",
        "`FirstOrDefaultAsync` — har qanday shart, `Include` bilan "
        "ishlaydi, har doim bazaga boradi.",
    ])

    para(d, "Shuning uchun kalit bo'yicha oddiy qidiruvda `FindAsync`, "
            "navigatsiya bilan o'qishda `FirstOrDefaultAsync` + `Include` "
            "ishlataman.")

    h2(d, "Single va First")

    code(d, """// Bittadan ko'p topilsa exception — invariantni tekshiradi
var one = await db.Orders.SingleOrDefaultAsync(o => o.Number == number, ct);

// Birinchisini oladi, qolganiga qaramaydi
var any = await db.Orders.FirstOrDefaultAsync(o => o.Number == number, ct);""")

    para(d, "`Single` bazaga `LIMIT 2` yuboradi — ikkinchisi borligini "
            "tekshirish uchun. Shuning uchun u sal qimmatroq, lekin "
            "ma'lumotdagi xatoni aniqlaydi.")

    # ───────────────────────────────────────────
    h1(d, "4. Qo'shish, o'zgartirish, o'chirish")

    code(d, """// Qo'shish
db.Orders.Add(order);
db.Orders.AddRange(orders);
await db.SaveChangesAsync(ct);

// O'zgartirish — tracked entity'ni shunchaki o'zgartirish yetarli
var order = await db.Orders.FindAsync([id], ct);
order!.Status = OrderStatus.Paid;
await db.SaveChangesAsync(ct);

// O'chirish
db.Orders.Remove(order);
await db.SaveChangesAsync(ct);""")

    para(d, "`Add` bazaga yozmaydi — u faqat entity'ni `Added` holatiga "
            "o'tkazadi. Haqiqiy `INSERT` `SaveChangesAsync()` da sodir "
            "bo'ladi va hamma o'zgarish bitta tranzaksiyada ketadi.")

    h2(d, "AddAsync qachon kerak")

    para(d, "Deyarli hech qachon. `AddAsync` faqat `HiLo` yoki shunga "
            "o'xshash kalit generatori ishlatilganda ma'noga ega — unda "
            "kalit olish uchun bazaga murojaat kerak bo'ladi. Qolgan "
            "hollarda oddiy `Add` ishlatiladi.")

    # ───────────────────────────────────────────
    h1(d, "5. Bulk operatsiyalar (EF Core 7+)")

    code(d, """// Bazada to'g'ridan-to'g'ri UPDATE — entity'lar o'qilmaydi
await db.Orders
    .Where(o => o.CreatedAt < cutoff && o.Status == OrderStatus.New)
    .ExecuteUpdateAsync(s => s
        .SetProperty(o => o.Status, OrderStatus.Expired)
        .SetProperty(o => o.UpdatedAt, DateTimeOffset.UtcNow), ct);

// Bazada to'g'ridan-to'g'ri DELETE
await db.OutboxMessages
    .Where(m => m.ProcessedAt < cutoff)
    .ExecuteDeleteAsync(ct);""")

    para(d, "Bu metodlar bitta SQL buyrug'i yuboradi va minglab satrni "
            "tez o'zgartiradi. Lekin ularning muhim cheklovlari bor:")

    bullets(d, [
        "Change tracker'dan **o'tmaydi** — ya'ni `SaveChanges` "
        "interceptor'lari, audit mantiqi va `SaveChanges` override'i "
        "ishlamaydi.",
        "Darhol bajariladi — `SaveChangesAsync()` kutmaydi. Shuning uchun "
        "boshqa o'zgarishlar bilan bir tranzaksiyada bo'lishi uchun "
        "tranzaksiyani qo'lda ochish kerak.",
        "Xotiradagi entity'lar eskirib qoladi: baza o'zgardi, lekin "
        "tracker buni bilmaydi.",
    ])

    note(d, "Amaliy xulosa",
         "Audit trigger'i yoki `SaveChanges` ichidagi mantiqqa tayangan "
         "loyihada `ExecuteUpdate` ni ishlatish jim xatolarga olib "
         "keladi. Shuning uchun uni faqat texnik tozalash ishlarida "
         "(eskirgan yozuvlarni o'chirish, holat yangilash) ishlataman.")

    # ───────────────────────────────────────────
    h1(d, "6. Set<T>() va keyless entity")

    para(d, "`DbSet` xossasi e'lon qilinmagan entity bilan ishlash uchun "
            "`Set<T>()` ishlatiladi. Bu generic repozitoriy yozganda "
            "kerak bo'ladi:")

    code(d, """public sealed class EfRepository<T>(AppDbContext db) where T : class
{
    public Task<T?> FindAsync(object key, CancellationToken ct)
        => db.Set<T>().FindAsync([key], ct).AsTask();
}""")

    para(d, "View yoki `SELECT` natijasini map qilish uchun kalitsiz "
            "entity ishlatiladi:")

    code(d, """modelBuilder.Entity<DailySales>()
    .HasNoKey()
    .ToView("daily_sales");""")

    code(d, """public DbSet<DailySales> DailySales => Set<DailySales>();""")

    para(d, "Kalitsiz entity'lar faqat o'qish uchun — ularni "
            "o'zgartirib `SaveChanges` qilib bo'lmaydi, chunki EF "
            "qaysi satrni yangilashni bilmaydi.")

    # ───────────────────────────────────────────
    h1(d, "7. Nimaga e'tibor beraman")

    bullets(d, [
        "**O'qishda `AsNoTracking()`.** Ro'yxat qaytaradigan so'rovlarda "
        "tracking kerak emas va u xotira sarflaydi.",
        "**Chegaralanmagan so'rov yozmaslik.** `db.Orders.ToListAsync()` "
        "bugun 100 satr qaytarsa, bir yildan keyin 2 million qaytaradi. "
        "Har doim filtr va `Take` qo'yaman.",
        "**Projeksiya.** Butun entity kerak bo'lmasa, `Select` bilan "
        "faqat kerakli ustunlarni olaman — bu tarmoq va xotirani "
        "tejaydi.",
        "**`IQueryable` ni qatlamdan chiqarmaslik.** Repozitoriydan "
        "`IQueryable` qaytarilsa, so'rov qayerda bajarilayotgani "
        "noma'lum bo'lib qoladi va `DbContext` yopilgandan keyin "
        "chaqirilishi mumkin.",
    ])

    sources(d, [
        ("DbSet<TEntity> Class",
         "https://learn.microsoft.com/en-us/dotnet/api/microsoft.entityframeworkcore.dbset-1"),
        ("Querying data — EF Core",
         "https://learn.microsoft.com/en-us/ef/core/querying/"),
        ("ExecuteUpdate and ExecuteDelete",
         "https://learn.microsoft.com/en-us/ef/core/saving/execute-insert-update-delete"),
        ("Keyless entity types",
         "https://learn.microsoft.com/en-us/ef/core/modeling/keyless-entity-types"),
    ])
