# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "Repository (Database Pattern)"
CATEGORY = "Design pattern"
TITLE = "Repository Naqshi"
SUBTITLE = "Ma'lumotga kirishni abstraksiya ortiga yashirish"
FILENAME = "Repository (Database Pattern).docx"


def build(d):
    h1(d, "1. Naqshning maqsadi")

    para(d, "Repository — ma'lumotlar omboriga kirishni kolleksiya kabi ko'rsatuvchi "
            "abstraksiya. Biznes mantiq \"bazadan `SELECT` qil\" demaydi, balki "
            "\"shu shartga mos kitoblarni ber\" deydi.")

    para(d, "Maqsad — domen mantiqini saqlash texnologiyasidan ajratish. Kod "
            "repozitoriy interfeysiga bog'lanadi, uning ortida esa EF Core, Dapper "
            "yoki umuman boshqa narsa turishi mumkin.")

    code(d, """public interface IBookRepository
{
    Task<Book?> GetByIdAsync(int id, CancellationToken ct = default);
    Task<IReadOnlyList<Book>> GetByAuthorAsync(int authorId, CancellationToken ct = default);
    Task AddAsync(Book book, CancellationToken ct = default);
    void Remove(Book book);
}""")

    # ───────────────────────────────────────────
    h1(d, "2. Amalga oshirish")

    code(d, """public class BookRepository : IBookRepository
{
    private readonly AppDbContext _db;

    public BookRepository(AppDbContext db) => _db = db;

    public Task<Book?> GetByIdAsync(int id, CancellationToken ct = default)
        => _db.Books
              .Include(b => b.Author)
              .FirstOrDefaultAsync(b => b.Id == id, ct);

    public async Task<IReadOnlyList<Book>> GetByAuthorAsync(
        int authorId, CancellationToken ct = default)
        => await _db.Books
                    .Where(b => b.AuthorId == authorId)
                    .OrderBy(b => b.Title)
                    .ToListAsync(ct);

    public async Task AddAsync(Book book, CancellationToken ct = default)
        => await _db.Books.AddAsync(book, ct);

    public void Remove(Book book) => _db.Books.Remove(book);
}""")

    code(d, """builder.Services.AddScoped<IBookRepository, BookRepository>();""")

    note(d, "E'tibor beradigan joy — `SaveChanges` bu yerda yo'q:",
         "Repozitoriy o'zgarishni **tayyorlaydi**, lekin saqlamaydi. Saqlash — "
         "alohida mas'uliyat va u Unit of Work ga tegishli. Agar har bir "
         "repozitoriy metodi o'zi `SaveChanges` chaqirsa, bitta biznes amal "
         "ichidagi bir nechta o'zgarishni yagona tranzaksiyada bajarib bo'lmaydi.")

    # ───────────────────────────────────────────
    h1(d, "3. Umumiy repozitoriy — va uning muammosi")

    para(d, "Ko'p loyihalarda umumiy, ya'ni generik repozitoriy yoziladi:")

    code(d, """public interface IRepository<T> where T : class
{
    Task<T?> GetByIdAsync(object id, CancellationToken ct = default);
    Task<IReadOnlyList<T>> ListAsync(
        Expression<Func<T, bool>> predicate, CancellationToken ct = default);
    Task AddAsync(T entity, CancellationToken ct = default);
    void Remove(T entity);
}""")

    para(d, "Bu kod takrorlanishini kamaytiradi, lekin bir nechta jiddiy "
            "kamchilikka ega.")

    bullets(d, [
        "**`Expression<Func<T, bool>>` qabul qilish abstraksiyani buzadi.** "
        "Chaqiruvchi kod baribir EF Core tarjima qila oladigan ifodalarni bilishi "
        "kerak bo'ladi.",
        "**`Include` ni ifodalab bo'lmaydi** — natijada yo hamma narsa yuklanadi, "
        "yo interfeysga qo'shimcha parametrlar qo'shiladi.",
        "**Har bir entity bir xil amallarni talab qilmaydi.** Ba'zilari hech "
        "qachon o'chirilmaydi, ba'zilari faqat o'qiladi.",
        "**Maxsus so'rovlar baribir kerak bo'ladi** va ular generik interfeysga "
        "sig'maydi.",
    ])

    note(d, "Mening tajribamdagi xulosa:",
         "Generik repozitoriy boshida juda chiroyli ko'rinadi — bitta klass bilan "
         "hamma entity ni qamrab olgandek bo'laman. Lekin bir necha oydan keyin "
         "u `GetWithIncludesAsync`, `ListPagedAsync`, `CountByAsync` kabi "
         "metodlar bilan to'lib ketadi va aslida `DbSet` ning yomonroq nusxasiga "
         "aylanadi.")

    note(d, "Shuning uchun men aniq repozitoriylarni afzal ko'raman:",
         "`IBookRepository` da faqat kitoblar uchun haqiqatan kerak bo'lgan "
         "metodlar turadi. Ularning nomi domen tilida bo'ladi — "
         "`GetAvailableForRentAsync` kabi. Shunda interfeysga qarab turib, "
         "ilova nima qilishini tushunish mumkin.")

    # ───────────────────────────────────────────
    h1(d, "4. EF Core allaqachon repozitoriy emasmi")

    para(d, "Bu haqli savol. `DbSet<T>` — bu kolleksiya kabi abstraksiya, "
            "`DbContext` esa Unit of Work. Ya'ni EF Core ikkala naqshni ham "
            "o'z ichiga olgan.")

    para(d, "Shuning uchun EF Core ustiga yana bir repozitoriy qatlami qo'shish "
            "ko'pincha ortiqcha. Lekin ba'zi holatlarda u baribir asos bo'ladi:")

    table(d, ["Repozitoriy foydali", "Repozitoriy ortiqcha"],
          [["So'rov mantiqi bir nechta joyda takrorlansa",
            "Har bir metod bitta `DbSet` chaqiruviga aylansa"],
           ["Domen tilida nomlangan so'rovlar kerak bo'lsa",
            "Interfeys `IQueryable` qaytarsa"],
           ["Bir nechta manbadan ma'lumot yig'ilsa",
            "Faqat \"qatlam bo'lishi kerak\" degani uchun qo'shilsa"],
           ["Testda almashtirish zarur bo'lsa",
            "Testda `InMemory` yoki konteyner ishlatilsa"]],
          widths=[7.7, 7.8])

    note(d, "Mening qoidam:",
         "Agar repozitoriy metodi faqat `_db.Books.FirstOrDefaultAsync(...)` "
         "ni o'rab turgan bo'lsa — u hech narsa qo'shmaydi, faqat bitta qatlam "
         "ko'paytiradi. Agar u murakkab so'rovni domen tilidagi tushunarli nom "
         "ortiga yashirgan bo'lsa — u haqiqatan foyda beryapti.")

    code(d, """// Qiymat qo'shadi
Task<IReadOnlyList<Book>> GetOverdueRentalsAsync(DateOnly asOf, CancellationToken ct);

// Qiymat qo'shmaydi
Task<List<Book>> GetAllAsync(CancellationToken ct);""")

    # ───────────────────────────────────────────
    h1(d, "5. Specification naqshi")

    para(d, "Generik repozitoriy bilan bog'liq moslashuvchanlik muammosini "
            "Specification naqshi yumshatadi. So'rov sharti alohida obyektga "
            "chiqariladi:")

    code(d, """public class AvailableBooksSpec : Specification<Book>
{
    public AvailableBooksSpec(int authorId)
    {
        Criteria = b => b.AuthorId == authorId && b.AvailableCopies > 0;
        AddInclude(b => b.Author);
        ApplyOrderBy(b => b.Title);
    }
}

var books = await _repo.ListAsync(new AvailableBooksSpec(authorId), ct);""")

    para(d, "Bu yondashuv shartlarni qayta ishlatish va ularni alohida sinovdan "
            "o'tkazish imkonini beradi. Lekin u ham qo'shimcha murakkablik — "
            "kichik loyihada ortiqcha bo'lishi mumkin.")

    # ───────────────────────────────────────────
    h1(d, "6. Nimalardan qochish kerak")

    bullets(d, [
        "**`IQueryable` qaytarish.** Bu holda so'rov repozitoriydan tashqarida "
        "yakunlanadi va abstraksiyaning ma'nosi qolmaydi.",
        "**Repozitoriy ichida biznes mantiq.** U faqat ma'lumot bilan ishlashi "
        "kerak.",
        "**Har bir entity ga repozitoriy yaratish.** Faqat agregat ildizlari "
        "uchun kerak — `OrderItem` o'z repozitoriysiga muhtoj emas, u `Order` "
        "orqali boshqariladi.",
        "**`DbContext` ni repozitoriydan tashqariga chiqarish.** Aks holda ikki "
        "yo'l paydo bo'ladi va ular bir-biriga zid ishlaydi.",
    ])

    # ───────────────────────────────────────────
    h1(d, "7. Xulosa")

    bullets(d, [
        "Repository ma'lumotga kirishni kolleksiya kabi abstraksiya ortiga "
        "yashiradi.",
        "Saqlash repozitoriyning emas, Unit of Work ning mas'uliyati.",
        "Generik repozitoriy kod takrorlanishini kamaytiradi, lekin abstraksiyani "
        "zaiflashtiradi.",
        "EF Core o'zi allaqachon Repository va Unit of Work ni amalga oshirgan.",
        "Repozitoriy faqat haqiqiy qiymat qo'shganda — murakkab so'rovni domen "
        "tiliga aylantirganda — asoslanadi.",
        "`IQueryable` qaytarish abstraksiyani buzadi.",
        "Repozitoriy agregat ildizlari uchun yaratiladi, har bir entity uchun "
        "emas.",
    ])

    sources(d, [
        ("Repository pattern — Martin Fowler",
         "https://martinfowler.com/eaaCatalog/repository.html"),
        ("Design the infrastructure persistence layer — .NET microservices",
         "https://learn.microsoft.com/en-us/dotnet/architecture/microservices/microservice-ddd-cqrs-patterns/infrastructure-persistence-layer-design"),
        ("Testing EF Core applications",
         "https://learn.microsoft.com/en-us/ef/core/testing/"),
    ])
