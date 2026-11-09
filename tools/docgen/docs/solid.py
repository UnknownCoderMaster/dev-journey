# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "SOLID-based Architecture decisions"
CATEGORY = "Architecture"
TITLE = "SOLID Tamoyillari Asosidagi Qarorlar"
SUBTITLE = "Beshta tamoyil va ularning amaliy ta'siri"
FILENAME = "SOLID-based Architecture decisions.docx"


def build(d):
    h1(d, "1. SOLID nima uchun kerak")

    para(d, "SOLID — obyektga yo'naltirilgan dizayn uchun beshta tamoyil. "
            "Ularning umumiy maqsadi bitta: kodni o'zgartirish oson bo'lsin.")

    para(d, "Dastlabki yozish tezligi muhim emas — kod umri davomida u ko'p "
            "marta o'qiladi va o'zgartiriladi. SOLID aynan shu keyingi "
            "bosqichni yengillashtiradi.")

    note(d, "Tamoyillarga munosabatim:",
         "SOLID — qonun emas, mo'ljal. Ularni qat'iy qo'llash kodni "
         "ortiqcha murakkablashtirishi mumkin — har bir klass uchun "
         "interfeys, har bir funksiya uchun alohida fayl. Men ularni "
         "\"kod o'zgartirish qiyinlashsa, shu ro'yxatdan sabab izla\" degan "
         "tekshiruv vositasi sifatida ishlataman.")

    # ───────────────────────────────────────────
    h1(d, "2. S — Single Responsibility")

    para(d, "Klassning o'zgarishi uchun faqat bitta sabab bo'lishi kerak. "
            "Boshqacha aytganda, u bitta manfaatdor tomonning talabiga "
            "javob berishi lozim.")

    code(d, """// Buzilgan — uchta sabab bilan o'zgaradi
public class OrderService
{
    public async Task CreateAsync(CreateOrderCommand cmd, CancellationToken ct)
    {
        // 1. Biznes qoidasi
        if (cmd.Items.Count == 0) throw new Exception("Bo'sh buyurtma");

        // 2. Ma'lumotga kirish
        await using var conn = new NpgsqlConnection(_connectionString);
        await conn.ExecuteAsync("INSERT INTO orders ...", cmd);

        // 3. Xabarnoma formati
        var html = $"<h1>Buyurtma #{cmd.Id}</h1><p>Rahmat!</p>";
        await _smtp.SendMailAsync(new MailMessage { Body = html });
    }
}""")

    code(d, """// Ajratilgan
public class OrderService
{
    public async Task<Order> CreateAsync(
        CreateOrderCommand cmd, CancellationToken ct)
    {
        var order = Order.Create(cmd.CustomerId, cmd.Items);  // qoida domenda

        await _repository.AddAsync(order, ct);                // saqlash alohida
        await _uow.SaveChangesAsync(ct);

        await _notifier.OrderCreatedAsync(order, ct);         // xabar alohida
        return order;
    }
}""")

    note(d, "Buzilganini qanday payqayman:",
         "Klass nomida \"va\" so'zi bo'lsa yoki uni tushuntirish uchun bir "
         "necha jumla kerak bo'lsa — bu belgi. Yana bir tekshiruv: agar "
         "dizayner xabarnoma ko'rinishini o'zgartirishni so'rasa, men "
         "buyurtma yaratish kodiga tegishim kerak bo'ladimi? Agar ha — "
         "tamoyil buzilgan.")

    # ───────────────────────────────────────────
    h1(d, "3. O — Open/Closed")

    para(d, "Kod kengaytirish uchun ochiq, o'zgartirish uchun yopiq bo'lishi "
            "kerak. Yangi imkoniyat qo'shish mavjud kodni tahrirlashni talab "
            "qilmasligi lozim.")

    code(d, """// Buzilgan — har yangi usulda bu metod o'zgaradi
public decimal CalculateFee(PaymentMethod method, decimal amount)
{
    return method switch
    {
        PaymentMethod.Card => amount * 0.02m,
        PaymentMethod.Cash => 0,
        PaymentMethod.Transfer => 5000,
        _ => throw new NotSupportedException()
    };
}""")

    code(d, """// Kengaytiriladigan
public interface IFeeCalculator
{
    PaymentMethod Method { get; }
    decimal Calculate(decimal amount);
}

public class CardFeeCalculator : IFeeCalculator
{
    public PaymentMethod Method => PaymentMethod.Card;
    public decimal Calculate(decimal amount) => amount * 0.02m;
}

// Yangi usul — faqat yangi klass qo'shiladi
public class WalletFeeCalculator : IFeeCalculator
{
    public PaymentMethod Method => PaymentMethod.Wallet;
    public decimal Calculate(decimal amount) => amount * 0.01m;
}""")

    code(d, """builder.Services.AddSingleton<IFeeCalculator, CardFeeCalculator>();
builder.Services.AddSingleton<IFeeCalculator, WalletFeeCalculator>();

// Ishlatilishi
var calculator = _calculators.First(c => c.Method == method);
var fee = calculator.Calculate(amount);""")

    note(d, "Lekin bu yerda o'lchov hissi kerak:",
         "Uchta variant uchun `switch` butunlay normal va o'qiladigan. "
         "Interfeys va uchta klass esa ortiqcha murakkablik bo'ladi. Men "
         "ajratishni variantlar soni o'sib borayotganini yoki ularning har "
         "biri murakkablashayotganini ko'rganimda qilaman — oldindan emas.")

    # ───────────────────────────────────────────
    h1(d, "4. L — Liskov Substitution")

    para(d, "Bazaviy tipdan foydalanayotgan kod hosila tip bilan ham to'g'ri "
            "ishlashi kerak. Hosila tip shartlarni kuchaytirmasligi va "
            "kafolatlarni zaiflashtirmasligi lozim.")

    code(d, """// Buzilgan
public class Rectangle
{
    public virtual int Width { get; set; }
    public virtual int Height { get; set; }
    public int Area => Width * Height;
}

public class Square : Rectangle
{
    public override int Width
    {
        set { base.Width = value; base.Height = value; }
    }
    public override int Height
    {
        set { base.Width = value; base.Height = value; }
    }
}""")

    code(d, """// Bu test Rectangle uchun o'tadi, Square uchun yo'q
void Test(Rectangle r)
{
    r.Width = 5;
    r.Height = 4;
    Assert.Equal(20, r.Area);   // Square da 16 chiqadi
}""")

    note(d, "Bu klassik misol, lekin amalda boshqacha ko'rinadi:",
         "Men buni ko'proq istisno otish shaklida uchrataman. Bazaviy "
         "klassda `Save()` metodi bor, hosilasida esa u "
         "`NotSupportedException` otadi. Yoki `IReadOnlyList` qaytaradigan "
         "metod aslida o'zgartirilishi mumkin bo'lgan ro'yxatni beradi. "
         "Ikkala holatda ham chaqiruvchi kod kutilmagan xatti-harakatga "
         "duch keladi.")

    para(d, "Yechim ko'pincha merosni butunlay tark etish bo'ladi:")

    code(d, """// Meros emas, alohida tiplar
public interface IShape { int Area { get; } }

public record Rectangle(int Width, int Height) : IShape
{
    public int Area => Width * Height;
}

public record Square(int Side) : IShape
{
    public int Area => Side * Side;
}""")

    # ───────────────────────────────────────────
    h1(d, "5. I — Interface Segregation")

    para(d, "Mijoz o'ziga kerak bo'lmagan metodlarga bog'liq bo'lmasligi "
            "kerak. Katta interfeys o'rniga bir nechta kichigi afzal.")

    code(d, """// Buzilgan — hamma amalga oshiruvchi hammasini yozishi kerak
public interface IRepository<T>
{
    Task<T?> GetByIdAsync(int id, CancellationToken ct);
    Task<IReadOnlyList<T>> GetAllAsync(CancellationToken ct);
    Task AddAsync(T entity, CancellationToken ct);
    Task UpdateAsync(T entity, CancellationToken ct);
    Task DeleteAsync(int id, CancellationToken ct);
    Task<int> CountAsync(CancellationToken ct);
    Task BulkInsertAsync(IEnumerable<T> items, CancellationToken ct);
}""")

    code(d, """// Ajratilgan
public interface IReadRepository<T>
{
    Task<T?> GetByIdAsync(int id, CancellationToken ct = default);
    Task<IReadOnlyList<T>> ListAsync(CancellationToken ct = default);
}

public interface IWriteRepository<T>
{
    Task AddAsync(T entity, CancellationToken ct = default);
    void Remove(T entity);
}""")

    note(d, "Bu tamoyilning amaliy foydasi testda ko'rinadi:",
         "O'n metodli interfeysni mock qilish uchun hammasini sozlash "
         "kerakdek tuyuladi. Ikki metodli interfeys esa bir qatorda "
         "sozlanadi. Bundan tashqari, `IReadRepository` ni qabul qiladigan "
         "klass yozilsa, unga qarab turib bu kod hech narsani "
         "o'zgartirmasligini bilib olaman — bu ham qimmatli ma'lumot.")

    # ───────────────────────────────────────────
    h1(d, "6. D — Dependency Inversion")

    para(d, "Yuqori darajadagi modullar quyi darajadagilarga bog'liq "
            "bo'lmasligi kerak — ikkalasi ham abstraksiyaga bog'lanishi "
            "lozim.")

    code(d, """// Buzilgan — biznes mantiq konkret texnologiyaga bog'langan
public class OrderService
{
    private readonly SmtpClient _smtp = new("smtp.example.com");
    private readonly NpgsqlConnection _conn = new(ConnectionString);
}""")

    code(d, """// To'g'ri — abstraksiyaga bog'lanish
public class OrderService
{
    private readonly IOrderRepository _repository;
    private readonly INotificationSender _notifier;

    public OrderService(
        IOrderRepository repository,
        INotificationSender notifier)
    {
        _repository = repository;
        _notifier = notifier;
    }
}""")

    para(d, "Eng muhim tafsilot — interfeys **qayerda** e'lon qilinishida. "
            "Agar u infratuzilma loyihasida bo'lsa, bog'liqlik baribir "
            "saqlanadi. Interfeys uni **ishlatadigan** qatlamga tegishli "
            "bo'lishi kerak.")

    code(d, """MyApp.Domain/
    IOrderRepository.cs          ← interfeys bu yerda

MyApp.Infrastructure/
    OrderRepository.cs           ← amalga oshirish bu yerda
    (MyApp.Domain ga havola qiladi, teskarisi emas)""")

    # ───────────────────────────────────────────
    h1(d, "7. Tamoyillar o'rtasidagi bog'liqlik")

    para(d, "Beshta tamoyil alohida emas, bir-birini to'ldiradi:")

    bullets(d, [
        "**S** klasslarni kichik qiladi → ularni **I** bo'yicha ajratish "
        "osonlashadi.",
        "**D** abstraksiyaga bog'lanishni talab qiladi → **O** bo'yicha "
        "kengaytirish mumkin bo'ladi.",
        "**L** abstraksiyaning ishonchli bo'lishini ta'minlaydi → **D** "
        "ma'noga ega bo'ladi.",
    ])

    # ───────────────────────────────────────────
    h1(d, "8. Haddan ortiq qo'llash")

    note(d, "Bu haqida ochiq gapirish kerak:",
         "SOLID ni so'zma-so'z qo'llash kodni tanib bo'lmaydigan qiladi. "
         "Men shunday loyihalarni ko'rganman: ikki qatorlik mantiq uchun "
         "interfeys, fabrika, strategiya va DI ro'yxatdan o'tkazish. "
         "Natijada oddiy o'zgarish uchun yettita faylni ochish kerak. Bu "
         "tamoyillarning maqsadiga butunlay zid.")

    table(d, ["Belgi", "Nimani anglatadi"],
          [["Har bir klassga interfeys, lekin bitta amalga oshirish",
            "Abstraksiya hech narsa bermayapti"],
           ["Faqat bitta metodli o'nlab klasslar",
            "Haddan ortiq bo'lingan"],
           ["Mantiqni topish uchun ko'p fayl ochish",
            "Bog'liqlik zanjiri juda uzun"],
           ["Interfeys faqat test uchun yaratilgan",
            "Boshqa yechim qaralmagan"]],
          widths=[7.0, 8.5])

    note(d, "Mening amaliy mezonim:",
         "Abstraksiyani **ikkinchi** amalga oshirish paydo bo'lganda yoki "
         "chegara haqiqatan kerak bo'lganda qo'shaman. \"Ertaga kerak "
         "bo'lishi mumkin\" degan asos yetarli emas — ko'pincha o'sha "
         "\"ertaga\" kelmaydi, abstraksiya esa qoladi.")

    # ───────────────────────────────────────────
    h1(d, "9. Xulosa")

    bullets(d, [
        "SOLID ning maqsadi — kodni o'zgartirishni osonlashtirish.",
        "**S**: bitta klass — bitta o'zgarish sababi.",
        "**O**: yangi imkoniyat mavjud kodni tahrirlamasdan qo'shilsin.",
        "**L**: hosila tip bazaviy tipning kafolatlarini buzmasin.",
        "**I**: katta interfeys o'rniga bir nechta kichigi.",
        "**D**: konkret amalga oshirishga emas, abstraksiyaga bog'lanish; "
        "interfeys uni ishlatadigan qatlamda e'lon qilinadi.",
        "Tamoyillar bir-birini to'ldiradi.",
        "Haddan ortiq qo'llash kodni murakkablashtiradi — abstraksiya "
        "ehtiyoj paydo bo'lganda qo'shiladi.",
    ])

    sources(d, [
        ("Architectural principles — .NET",
         "https://learn.microsoft.com/en-us/dotnet/architecture/modern-web-apps-azure/architectural-principles"),
        ("Dependency injection in ASP.NET Core",
         "https://learn.microsoft.com/en-us/aspnet/core/fundamentals/dependency-injection"),
        ("The Principles of OOD — Robert C. Martin",
         "http://butunclebob.com/ArticleS.UncleBob.PrinciplesOfOod"),
    ])
