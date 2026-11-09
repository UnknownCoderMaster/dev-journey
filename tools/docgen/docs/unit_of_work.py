# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "UnitOfWork (Database Pattern)"
CATEGORY = "Design pattern"
TITLE = "Unit of Work Naqshi"
SUBTITLE = "Bir nechta o'zgarishni yagona tranzaksiyada saqlash"
FILENAME = "UnitOfWork (Database Pattern).docx"


def build(d):
    h1(d, "1. Naqshning maqsadi")

    para(d, "Unit of Work — biznes amali davomida qilingan barcha o'zgarishlarni "
            "kuzatib borib, oxirida ularni bitta tranzaksiyada saqlaydigan naqsh.")

    para(d, "Asosiy g'oya shundaki, o'zgarishlar darhol bazaga yozilmaydi. Ular "
            "yig'iladi va faqat amal to'liq muvaffaqiyatli yakunlanganda "
            "qo'llaniladi. Agar o'rtada xatolik chiqsa, hech narsa saqlanmaydi.")

    note(d, "Nima uchun bu muhim — oddiy misol:",
         "Buyurtma yaratish uchta o'zgarishni talab qiladi: buyurtma yozuvi "
         "qo'shiladi, omborda miqdor kamaytiriladi, mijozning bonus balli "
         "yangilanadi. Agar ikkinchi qadam muvaffaqiyatli, uchinchisi xato bo'lsa "
         "va men har birini alohida saqlagan bo'lsam — ombor miqdori kamaygan, "
         "lekin buyurtma yarim holatda qolgan bo'ladi. Ma'lumot butunligi "
         "buziladi.")

    # ───────────────────────────────────────────
    h1(d, "2. EF Core da u allaqachon bor")

    para(d, "`DbContext` — bu Unit of Work ning tayyor amalga oshirilishi. U "
            "o'zgarishlarni change tracker orqali kuzatadi va `SaveChanges` "
            "chaqirilganda hammasini bitta tranzaksiyada yuboradi.")

    code(d, """// Uchta o'zgarish kuzatiladi, lekin bazaga hech narsa ketmaydi
db.Orders.Add(order);
product.Stock -= order.Quantity;
customer.BonusPoints += 10;

// Shu yerda bitta tranzaksiyada hammasi saqlanadi
await db.SaveChangesAsync(ct);""")

    para(d, "`SaveChanges` ichkarida tranzaksiya ochadi, barcha `INSERT`, `UPDATE` "
            "va `DELETE` larni yuboradi va birortasi muvaffaqiyatsiz bo'lsa, "
            "hammasini bekor qiladi.")

    note(d, "Buni bilish ko'p ortiqcha koddan qutqaradi:",
         "Ko'pchilik `DbContext` ustiga yana bir `IUnitOfWork` qatlami quradi. "
         "Lekin agar u faqat `SaveChangesAsync` ni chaqirsa, bu shunchaki "
         "boshqa nom bilan atalgan bir xil narsa bo'ladi.")

    # ───────────────────────────────────────────
    h1(d, "3. Qachon alohida abstraksiya kerak")

    para(d, "Shunga qaramay, ba'zi holatlarda alohida interfeys asoslanadi:")

    bullets(d, [
        "Biznes qatlami `DbContext` ga, ya'ni EF Core ga bog'lanmasligi kerak "
        "bo'lganda.",
        "Testda saqlash chaqirilganini tekshirish zarur bo'lganda.",
        "Bir nechta repozitoriy bitta tranzaksiyada ishlashi kerak bo'lganda.",
        "Saqlashdan oldin yoki keyin umumiy mantiq bajarilishi kerak bo'lganda — "
        "audit, hodisalarni e'lon qilish.",
    ])

    code(d, """public interface IUnitOfWork
{
    IBookRepository Books { get; }
    IAuthorRepository Authors { get; }

    Task<int> SaveChangesAsync(CancellationToken ct = default);
}""")

    code(d, """public class UnitOfWork : IUnitOfWork
{
    private readonly AppDbContext _db;

    public UnitOfWork(AppDbContext db)
    {
        _db = db;
        Books = new BookRepository(db);
        Authors = new AuthorRepository(db);
    }

    public IBookRepository Books { get; }
    public IAuthorRepository Authors { get; }

    public Task<int> SaveChangesAsync(CancellationToken ct = default)
        => _db.SaveChangesAsync(ct);
}""")

    code(d, """builder.Services.AddScoped<IUnitOfWork, UnitOfWork>();""")

    note(d, "`Scoped` bo'lishi shart:",
         "Agar `Singleton` qilib ro'yxatdan o'tkazsam, barcha so'rovlar bitta "
         "`DbContext` ni bo'lishadi va bu ikki muammo tug'diradi — u oqim uchun "
         "xavfsiz emas, va bir foydalanuvchining kuzatilayotgan obyektlari "
         "boshqasining so'roviga aralashadi.")

    # ───────────────────────────────────────────
    h1(d, "4. Ishlatilishi")

    code(d, """public class CreateOrderHandler
{
    private readonly IUnitOfWork _uow;

    public CreateOrderHandler(IUnitOfWork uow) => _uow = uow;

    public async Task<int> HandleAsync(CreateOrderCommand cmd, CancellationToken ct)
    {
        var book = await _uow.Books.GetByIdAsync(cmd.BookId, ct)
                   ?? throw new NotFoundException("Kitob", cmd.BookId);

        if (book.AvailableCopies < cmd.Quantity)
            throw new ConflictException("Yetarli nusxa yo'q");

        var order = new Order(cmd.CustomerId, cmd.BookId, cmd.Quantity);
        await _uow.Orders.AddAsync(order, ct);

        book.AvailableCopies -= cmd.Quantity;

        await _uow.SaveChangesAsync(ct);   // yagona nuqtada saqlanadi
        return order.Id;
    }
}""")

    para(d, "Diqqat qilinadigan jihat — butun metod davomida saqlash faqat bir "
            "marta chaqiriladi. Bu Unit of Work ning asosiy qoidasi.")

    # ───────────────────────────────────────────
    h1(d, "5. Aniq tranzaksiya")

    para(d, "`SaveChanges` o'zi tranzaksiya ochadi, lekin ba'zan bir nechta "
            "saqlashni bitta tranzaksiyaga birlashtirish kerak bo'ladi:")

    code(d, """await using var transaction = await _db.Database.BeginTransactionAsync(ct);
try
{
    await _uow.SaveChangesAsync(ct);

    await _externalService.NotifyAsync(order.Id, ct);

    order.Status = OrderStatus.Confirmed;
    await _uow.SaveChangesAsync(ct);

    await transaction.CommitAsync(ct);
}
catch
{
    await transaction.RollbackAsync(ct);
    throw;
}""")

    note(d, "Lekin bu yerda nozik xavf bor:",
         "Tranzaksiya ichida tashqi xizmatga murojaat qilish — yomon amaliyot. "
         "Agar o'sha xizmat sekin javob bersa, baza tranzaksiyasi ochiq turadi "
         "va qulflar saqlanib qoladi. Bu boshqa so'rovlarni ham sekinlashtiradi. "
         "To'g'riroq yechim — tranzaksiyani tez yopib, tashqi chaqiruvni "
         "keyinroq, masalan xabar navbati orqali bajarish.")

    h2(d, "5.1 Tranzaksiya izolyatsiya darajasi")

    code(d, """await using var tx = await _db.Database.BeginTransactionAsync(
    IsolationLevel.Serializable, ct);""")

    para(d, "Yuqori izolyatsiya darajasi ma'lumot butunligini kuchaytiradi, lekin "
            "parallel ishlashni kamaytiradi va deadlock ehtimolini oshiradi.")

    # ───────────────────────────────────────────
    h1(d, "6. Repository bilan munosabati")

    para(d, "Ikki naqsh birga ishlaydi va mas'uliyatlari aniq ajratilgan:")

    table(d, ["Repository", "Unit of Work"],
          [["Nimani o'qish va qanday topish", "Qachon saqlash"],
           ["Entity ni qo'shish/o'chirish uchun belgilash",
            "Belgilanganlarni bazaga yuborish"],
           ["Har bir agregat uchun alohida", "Butun amal uchun bitta"],
           ["So'rov mantiqini biladi", "Tranzaksiyani biladi"]],
          widths=[7.7, 7.8])

    note(d, "Bu ajratish buzilganini qanday payqayman:",
         "Agar repozitoriy metodi ichida `SaveChangesAsync` ko'rsam — demak "
         "chegara buzilgan. O'shanda har bir chaqiruv o'z tranzaksiyasida ketadi "
         "va bir nechta o'zgarishni atomar qilib bo'lmaydi. Bu xatolik ko'pincha "
         "keyinroq, ma'lumot nomuvofiqligi shaklida chiqadi.")

    # ───────────────────────────────────────────
    h1(d, "7. Tanqid va muqobil")

    para(d, "Unit of Work naqshi EF Core kontekstida ortiqcha deb tez-tez "
            "tanqid qilinadi. Asosiy argumentlar:")

    bullets(d, [
        "`DbContext` allaqachon shu vazifani bajaradi — qo'shimcha qatlam "
        "hech narsa qo'shmaydi.",
        "`IUnitOfWork` barcha repozitoriylarni o'z ichiga olsa, u katta va "
        "o'zgarishi qiyin interfeysga aylanadi.",
        "Oddiy o'qish amallarida u faqat halaqit beradi.",
    ])

    para(d, "Muqobil yondashuv — CQRS, ya'ni o'qish va yozishni ajratish. O'qish "
            "uchun to'g'ridan-to'g'ri `DbContext` va proyeksiya ishlatiladi, yozish "
            "uchun esa domen modeli va `SaveChanges`.")

    code(d, """// O'qish — abstraksiyasiz, tez
var items = await _db.Books
    .Where(b => b.AuthorId == authorId)
    .Select(b => new BookListItemDto(b.Id, b.Title, b.Price))
    .ToListAsync(ct);

// Yozish — domen orqali
var book = await _db.Books.FirstAsync(b => b.Id == id, ct);
book.ChangePrice(newPrice);
await _db.SaveChangesAsync(ct);""")

    note(d, "Mening hozirgi fikrim:",
         "Kichik va o'rta loyihalarda `DbContext` ni to'g'ridan-to'g'ri ishlatish "
         "yetarli va soddaroq. `IUnitOfWork` ni men faqat domen qatlami "
         "infratuzilmadan qat'iy ajratilishi kerak bo'lgan loyihalarda qo'shaman. "
         "\"Hamma shunday qilyapti\" degani yetarli asos emas.")

    # ───────────────────────────────────────────
    h1(d, "8. Xulosa")

    bullets(d, [
        "Unit of Work o'zgarishlarni yig'ib, ularni bitta tranzaksiyada "
        "saqlaydi.",
        "`DbContext` allaqachon shu naqshning amalga oshirilishi hisoblanadi.",
        "Alohida interfeys domen qatlamini EF Core dan ajratish kerak bo'lganda "
        "asoslanadi.",
        "Bitta biznes amalida `SaveChanges` faqat bir marta chaqirilishi kerak.",
        "Repozitoriy ichida saqlash chaqirilishi — chegara buzilganining belgisi.",
        "Tranzaksiya ichida tashqi xizmatga murojaat qilmaslik lozim.",
        "`IUnitOfWork` `Scoped` bo'lishi shart.",
        "CQRS yondashuvi o'qish uchun bu qatlamni butunlay chetlab o'tadi.",
    ])

    sources(d, [
        ("Unit of Work — Martin Fowler",
         "https://martinfowler.com/eaaCatalog/unitOfWork.html"),
        ("Implementing the infrastructure persistence layer with EF Core",
         "https://learn.microsoft.com/en-us/dotnet/architecture/microservices/microservice-ddd-cqrs-patterns/infrastructure-persistence-layer-implementation-entity-framework-core"),
        ("Transactions — EF Core",
         "https://learn.microsoft.com/en-us/ef/core/saving/transactions"),
    ])
