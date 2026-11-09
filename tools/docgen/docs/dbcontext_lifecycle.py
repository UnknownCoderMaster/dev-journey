# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "DbContext (Lifecycle)"
CATEGORY = "EF Core"
TITLE = "DbContext va Uning Hayotiy Sikli"
SUBTITLE = "EF Core da ma'lumotlar bazasi bilan ishlash sessiyasini boshqarish"
FILENAME = "DbContext (Lifecycle).docx"


def build(d):
    h1(d, "1. DbContext nima")

    para(d, "`DbContext` — Entity Framework Core ning markaziy sinfi bo'lib, u ma'lumotlar "
            "bazasi bilan ishlash sessiyasini ifodalaydi. Sinf bir vaqtning o'zida bir "
            "nechta vazifani bajaradi: ma'lumotlar bazasiga ulanishni boshqaradi, LINQ "
            "so'rovlarini SQL ga tarjima qiladi, bazadan olingan ma'lumotlarni obyektlarga "
            "aylantiradi va obyektlardagi o'zgarishlarni kuzatib boradi.")

    para(d, "Texnik jihatdan `DbContext` ikkita loyihalash naqshini birlashtiradi: "
            "Unit of Work va Repository. Unit of Work vazifasi — bir nechta o'zgarishni "
            "to'plab, ularni yagona tranzaksiya sifatida saqlash. Repository vazifasini "
            "esa `DbSet<T>` xossalari bajaradi.")

    code(d, """public class AppDbContext : DbContext
{
    public AppDbContext(DbContextOptions<AppDbContext> options)
        : base(options) { }

    public DbSet<Author> Authors => Set<Author>();
    public DbSet<Book> Books => Set<Book>();

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.Entity<Author>(e =>
        {
            e.HasKey(x => x.Id);
            e.Property(x => x.FullName).HasMaxLength(256);
        });
    }
}""", caption="Oddiy DbContext")

    note(d, "Bitta narsani boshidan aytib qo'yay:",
         "`DbContext` — bu ma'lumotlar bazasining o'zi emas, balki u bilan bo'lgan qisqa "
         "muddatli suhbat. Ko'pchilik xatolar aynan shuni unutishdan kelib chiqadi — kontekst "
         "uzoq yashasa, u o'zi bilan birga eskirgan ma'lumotni ham ko'tarib yuradi.")

    # ───────────────────────────────────────────
    h1(d, "2. Hayotiy sikli")

    para(d, "`DbContext` ning hayotiy sikli to'rt bosqichdan iborat: yaratilish, "
            "ishlatilish, o'zgarishlarni saqlash va yo'q qilinish (dispose). Har bir "
            "bosqichda kontekst o'z holatini saqlab turadi.")

    h2(d, "2.1 Yaratilish")

    para(d, "Kontekst yaratilganda u hali ma'lumotlar bazasiga ulanmaydi. Ulanish faqat "
            "birinchi so'rov bajarilganda ochiladi — bu kechiktirilgan (lazy) xatti-harakat "
            "deb ataladi.")

    h2(d, "2.2 Ishlatilish va change tracking")

    para(d, "So'rov natijasida olingan har bir entity kontekstning ichki ro'yxatiga "
            "(change tracker) qo'shiladi. Kontekst ularning dastlabki qiymatlarini "
            "eslab qoladi va keyinchalik o'zgarganini aniqlash uchun shu nusxaga taqqoslaydi.")

    h2(d, "2.3 SaveChanges")

    para(d, "`SaveChanges()` chaqirilganda kontekst kuzatilayotgan barcha entity larni "
            "ko'rib chiqadi, o'zgarganlarini aniqlaydi va mos `INSERT`, `UPDATE`, `DELETE` "
            "buyruqlarini generatsiya qiladi. Barcha buyruqlar yagona tranzaksiya ichida "
            "bajariladi — ya'ni yo hammasi muvaffaqiyatli o'tadi, yo hech biri qo'llanmaydi.")

    h2(d, "2.4 Dispose")

    para(d, "Kontekst yo'q qilinganda ochiq ulanish bazaga qaytariladi va change tracker "
            "tozalanadi. ASP.NET Core da bu jarayon avtomatik — DI konteyner so'rov "
            "tugaganda kontekstni o'zi yo'q qiladi.")

    # ───────────────────────────────────────────
    h1(d, "3. Service lifetime — qaysi birini tanlash")

    para(d, "ASP.NET Core da `AddDbContext` metodi kontekstni default holda **Scoped** "
            "umr davomiyligi bilan ro'yxatdan o'tkazadi. Ya'ni har bir HTTP so'rov uchun "
            "bitta yangi kontekst yaratiladi va so'rov tugagach yo'q qilinadi.")

    code(d, """builder.Services.AddDbContext<AppDbContext>(options =>
    options.UseNpgsql(connectionString));
// Default: ServiceLifetime.Scoped""")

    table(d, ["Umr davomiyligi", "Mosligi", "Izoh"],
          [["Scoped", "To'g'ri tanlov",
            "Har so'rovga bitta kontekst — web ilovalar uchun standart"],
           ["Transient", "Ehtiyotkorlik bilan",
            "Har injeksiyada yangi kontekst; tranzaksiya bo'linib ketadi"],
           ["Singleton", "Ishlatilmaydi",
            "Thread-safe emas va xotirada cheksiz o'sadi"]],
          widths=[4.0, 4.0, 7.5])

    h2(d, "3.1 Nega Singleton bo'lmaydi")

    para(d, "Bu savolga ikkita aniq javob bor, va ikkalasi ham jiddiy.")

    para(d, "Birinchisi — `DbContext` **thread-safe emas**. Bir nechta so'rov bir vaqtda "
            "bitta kontekstdan foydalansa, change tracker buziladi. Natijada eng yaxshi "
            "holatda `InvalidOperationException` chiqadi, eng yomon holatda esa ma'lumot "
            "aralashib ketadi.")

    para(d, "Ikkinchisi — xotira. Kontekst o'zi ko'rgan har bir entity ni eslab qoladi va "
            "hech qachon unutmaydi. Singleton kontekst ilova ishga tushganidan beri "
            "o'tgan barcha yozuvlarni xotirada ushlab turadi. Bir necha soat ishlagandan "
            "keyin bu xotira sizib ketishiga (memory leak) aylanadi.")

    note(d, "Amaliyotdan bir kuzatuv:",
         "Singleton muammosi ko'pincha bevosita emas, bilvosita paydo bo'ladi. Masalan "
         "kimdir singleton servis yozadi va unga konstruktor orqali `DbContext` ni "
         "injeksiya qiladi. DI konteyner buni ruxsat beradi, lekin kontekst o'sha "
         "singleton bilan birga abadiy yashab qoladi. ASP.NET Core bunday holatni "
         "ishga tushishda aniqlab, xatolik beradi — lekin faqat validatsiya yoqilgan bo'lsa.")

    code(d, """// Bunday xatolarni ishga tushishda ushlash uchun
builder.Host.UseDefaultServiceProvider(o =>
{
    o.ValidateScopes = true;
    o.ValidateOnBuild = true;
});""")

    # ───────────────────────────────────────────
    h1(d, "4. Fon ishlari uchun kontekst olish")

    para(d, "Hosted service va background job lar singleton sifatida ro'yxatdan o'tadi. "
            "Ularga `DbContext` ni to'g'ridan-to'g'ri injeksiya qilib bo'lmaydi — buning "
            "o'rniga `IServiceScopeFactory` orqali har bir ish uchun alohida qamrov "
            "(scope) ochiladi.")

    code(d, """public class CleanupService : BackgroundService
{
    private readonly IServiceScopeFactory _scopeFactory;

    public CleanupService(IServiceScopeFactory scopeFactory)
        => _scopeFactory = scopeFactory;

    protected override async Task ExecuteAsync(CancellationToken ct)
    {
        while (!ct.IsCancellationRequested)
        {
            using var scope = _scopeFactory.CreateScope();
            var db = scope.ServiceProvider.GetRequiredService<AppDbContext>();

            // bu yerda kontekst xavfsiz ishlatiladi
            await db.SaveChangesAsync(ct);

            await Task.Delay(TimeSpan.FromMinutes(10), ct);
        }
    }
}""", caption="BackgroundService ichida DbContext bilan ishlash")

    para(d, "Bu yerdagi asosiy qoida: **scope qancha qisqa bo'lsa, shuncha yaxshi.** "
            "Har bir ish bo'lagi uchun alohida scope ochib, darhol yopish kerak.")

    # ───────────────────────────────────────────
    h1(d, "5. DbContextFactory")

    para(d, "Ba'zi stsenariylarda bitta so'rov ichida bir nechta kontekst kerak bo'ladi — "
            "masalan parallel bajariladigan amallar yoki Blazor Server ilovalari. Bunday "
            "hollarda `AddDbContextFactory` ishlatiladi.")

    code(d, """builder.Services.AddDbContextFactory<AppDbContext>(options =>
    options.UseNpgsql(connectionString));

// Foydalanish
public class ReportService
{
    private readonly IDbContextFactory<AppDbContext> _factory;

    public ReportService(IDbContextFactory<AppDbContext> factory)
        => _factory = factory;

    public async Task<int> CountAsync()
    {
        await using var db = await _factory.CreateDbContextAsync();
        return await db.Books.CountAsync();
    }
}""")

    note(d, "Qachon kerak bo'ladi:",
         "Agar `Task.WhenAll` bilan bir nechta so'rovni parallel bajarmoqchi bo'lsangiz, "
         "ularning hammasi bitta kontekstdan foydalansa xatolik chiqadi. Factory har bir "
         "vazifaga alohida kontekst berib, bu muammoni hal qiladi.")

    # ───────────────────────────────────────────
    h1(d, "6. Tez-tez uchraydigan xatolar")

    h2(d, "6.1 Kontekstni uzoq ushlab turish")

    para(d, "Desktop yoki konsol ilovalarida kontekstni bir marta yaratib, butun ilova "
            "davomida ishlatish vasvasasi paydo bo'ladi. Bu ikki muammoga olib keladi: "
            "xotira o'sib boradi va kontekst bazadagi keyingi o'zgarishlarni ko'rmaydi — "
            "u o'zi birinchi marta o'qigan nusxani qaytaraveradi.")

    h2(d, "6.2 Sinxron metodlarni ishlatish")

    para(d, "`SaveChanges()` va `ToList()` kabi sinxron metodlar ulanish javobini kutib "
            "turgan vaqtda oqimni (thread) band qiladi. Web ilovalarda bu throughput ni "
            "sezilarli pasaytiradi. Har doim `SaveChangesAsync()` va `ToListAsync()` "
            "variantlarini tanlash kerak.")

    h2(d, "6.3 Bitta so'rovda juda ko'p ish")

    para(d, "Agar bitta kontekst minglab entity ni kuzatayotgan bo'lsa, `SaveChanges()` "
            "sekinlashadi — chunki u har bir kuzatilayotgan obyektni tekshirib chiqadi. "
            "Katta hajmli amallarni bo'laklarga bo'lish yoki `ExecuteUpdate` / "
            "`ExecuteDelete` kabi to'g'ridan-to'g'ri ishlaydigan metodlardan foydalanish "
            "to'g'riroq bo'ladi.")

    code(d, """// Change tracking ni chetlab o'tadi — ancha tez ishlaydi
await db.Books
    .Where(b => b.Price == 0)
    .ExecuteDeleteAsync();""")

    # ───────────────────────────────────────────
    h1(d, "7. Xulosa")

    bullets(d, [
        "`DbContext` — qisqa muddatli sessiya. Uni uzoq yashatish deyarli har doim xato.",
        "Web ilovalarda Scoped — to'g'ri va default tanlov. Singleton hech qachon mos kelmaydi.",
        "Fon ishlarida `IServiceScopeFactory` orqali har bir vazifaga alohida scope ochiladi.",
        "Parallel amallar uchun `IDbContextFactory` ishlatiladi — bitta kontekstni "
        "bir nechta oqimdan ishlatib bo'lmaydi.",
        "`ValidateScopes` va `ValidateOnBuild` ni yoqish umr davomiyligi xatolarini "
        "ishga tushish paytida ushlab qoladi.",
        "Katta hajmli o'zgartirishlarda `ExecuteUpdate` / `ExecuteDelete` change tracking "
        "xarajatini butunlay chetlab o'tadi.",
    ])

    sources(d, [
        ("DbContext Lifetime, Configuration, and Initialization — EF Core",
         "https://learn.microsoft.com/en-us/ef/core/dbcontext-configuration/"),
        ("Change Tracking in EF Core",
         "https://learn.microsoft.com/en-us/ef/core/change-tracking/"),
        ("Dependency injection in ASP.NET Core — service lifetimes",
         "https://learn.microsoft.com/en-us/aspnet/core/fundamentals/dependency-injection"),
    ])
