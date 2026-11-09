# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "Solid (LSP)"
CATEGORY = "Principles"
TITLE = "LSP — Liskov Substitution Principle"
SUBTITLE = "Hosila tur bazaviy turning o'rnida ishlashi kerak"
FILENAME = "Solid (LSP).docx"


def build(d):
    h1(d, "1. Printsip nima deydi")

    para(d, "Agar `S` turi `T` turining hosilasi bo'lsa, `T` kutiladigan "
            "har qanday joyda `S` ni berish mumkin bo'lishi kerak — va "
            "program **to'g'ri ishlashda davom etishi** kerak.")

    para(d, "Bu kompilyator tekshiradigan narsa emas. Kompilyator uchun "
            "hosila tur har doim mos keladi; LSP esa **xatti-harakat** "
            "haqida. Shuning uchun uni buzish kompilyatsiya xatosi "
            "bermaydi — faqat ish vaqtida kutilmagan natija beradi.")

    # ───────────────────────────────────────────
    h1(d, "2. Klassik buzilish: kvadrat va to'rtburchak")

    code(d, """public class Rectangle
{
    public virtual int Width { get; set; }
    public virtual int Height { get; set; }

    public int Area => Width * Height;
}

public class Square : Rectangle
{
    public override int Width
    {
        get => base.Width;
        set { base.Width = value; base.Height = value; }   // ikkisi birga
    }

    public override int Height
    {
        get => base.Height;
        set { base.Width = value; base.Height = value; }
    }
}""")

    code(d, """// Bu metod Rectangle bilan ishlaydi
static void Resize(Rectangle rect)
{
    rect.Width = 5;
    rect.Height = 4;

    Debug.Assert(rect.Area == 20);    // Square uchun 16 — shart buziladi
}""")

    para(d, "Matematikada kvadrat to'rtburchakning turi, lekin **kodda "
            "emas**. Chunki `Rectangle` ning shartnomasida \"kenglikni "
            "o'zgartirish balandlikka ta'sir qilmaydi\" degan yashirin "
            "qoida bor va `Square` uni buzadi.")

    para(d, "Bu misoldan olinadigan asosiy xulosa: meros ierarxiyasi "
            "real dunyodagi tasnifga emas, **xatti-harakat "
            "shartnomasiga** asoslanishi kerak.")

    # ───────────────────────────────────────────
    h1(d, "3. Amalda ko'p uchraydigan buzilishlar")

    h2(d, "Metod amalga oshirilmaydi")

    code(d, """public class ReadOnlyOrderList : List<Order>
{
    public new void Add(Order item)
        => throw new NotSupportedException("Faqat o'qish uchun");
}""")

    para(d, "`List<T>` kutgan joyga bu obyekt berilsa, `Add` chaqiruvi "
            "qulaydi. Chaqiruvchi esa bunga tayyor emas — u `List<T>` "
            "shartnomasiga ishonadi. Shunga o'xshash: `Stream` dan meros "
            "olib `Seek` ni `NotSupportedException` bilan qoldirish.")

    para(d, "To'g'ri yechim — kerakli qobiliyatni aniq ifodalaydigan "
            "interfeysni ishlatish:")

    code(d, """// Chaqiruvchi faqat o'qiy olishini bilsin
public IReadOnlyList<Order> Orders { get; }""")

    h2(d, "Oldingi shart (precondition) kuchaytirilsa")

    code(d, """public class FileStorage
{
    public virtual void Save(byte[] content) { /* har qanday hajm */ }
}

public class LimitedStorage : FileStorage
{
    public override void Save(byte[] content)
    {
        if (content.Length > 1_000_000)
            throw new ArgumentException("1 MB dan katta fayl qabul qilinmaydi");

        base.Save(content);
    }
}""")

    para(d, "Hosila tur bazaviy turdan **ko'proq** talab qiladi. "
            "Chaqiruvchi `FileStorage` bilan ishlayotganini o'ylab katta "
            "fayl yuboradi va kutilmagan xato oladi.")

    h2(d, "Keyingi shart (postcondition) bo'shashtirilsa")

    code(d, """public class CustomerRepository
{
    // Shartnoma: topilmasa null, lekin hech qachon exception yo'q
    public virtual Customer? Find(Guid id) => /* ... */;
}

public class CachedCustomerRepository : CustomerRepository
{
    public override Customer? Find(Guid id)
        => _cache.Get(id) ?? throw new NotFoundException();    // shartnoma buzildi
}""")

    h2(d, "Yangi exception turi qo'shilsa")

    para(d, "Bazaviy metod faqat `ArgumentException` tashlashi "
            "hujjatlashtirilgan bo'lsa, hosila `InvalidOperationException` "
            "tashlamasligi kerak — chaqiruvchi uni ushlamaydi.")

    # ───────────────────────────────────────────
    h1(d, "4. Shartnoma qoidalari")

    table(d, ["Element", "Hosilada ruxsat etiladi"],
          [["Oldingi shart", "Bir xil yoki **bo'shashtirilgan** "
            "(kamroq talab)"],
           ["Keyingi shart", "Bir xil yoki **kuchaytirilgan** "
            "(ko'proq kafolat)"],
           ["Invariant", "Saqlanishi kerak"],
           ["Exception turlari", "Bir xil yoki kamroq"]],
          widths=[4.4, 10.1])

    para(d, "Qoida esda qolishi uchun: hosila tur **ko'proq qabul "
            "qilishi va ko'proq kafolat berishi** mumkin, lekin "
            "teskarisi emas.")

    # ───────────────────────────────────────────
    h1(d, "5. Qanday aniqlayman")

    bullets(d, [
        "**`is` yoki `GetType()` tekshiruvi.** Agar kodda "
        "`if (shape is Square) { ... }` paydo bo'lsa, bu turlar "
        "bir-birini to'liq almashtira olmasligini bildiradi.",
        "**`NotSupportedException` yoki bo'sh `override`.** Hosila "
        "bazaviy a'zoni \"bekor qilayotgan\" bo'lsa, ierarxiya noto'g'ri.",
        "**Hujjatda \"bu hosila uchun ishlamaydi\" degan izoh.** Bu "
        "LSP buzilganining to'g'ridan-to'g'ri tan olinishi.",
        "**Bazaviy tur bilan yozilgan test hosilada o'tmasligi.** Eng "
        "ishonchli tekshiruv usuli.",
    ])

    note(d, "Amaliy usul",
         "Bazaviy tur uchun test to'plami yozib, uni hamma hosila turga "
         "qo'llayman. Agar biror hosila bu testlardan o'tmasa, LSP "
         "buzilgan. xUnit'da buni abstrakt test klassi bilan qilish "
         "qulay.")

    code(d, """public abstract class FileStorageContractTests
{
    protected abstract IFileStorage CreateStorage();

    [Fact]
    public async Task SaveThenRead_ReturnsSameContent()
    {
        var storage = CreateStorage();
        var key = await storage.SaveAsync(new MemoryStream([1, 2, 3]), "a.bin", default);

        await using var read = await storage.OpenReadAsync(key, default);
        Assert.Equal(3, read.Length);
    }
}

public sealed class DiskStorageTests : FileStorageContractTests
{
    protected override IFileStorage CreateStorage() => new DiskFileStorage(TempDir);
}

public sealed class MinioStorageTests : FileStorageContractTests
{
    protected override IFileStorage CreateStorage() => new MinioFileStorage(...);
}""")

    # ───────────────────────────────────────────
    h1(d, "6. Eng ishonchli yechim: merosdan kamroq foydalanish")

    para(d, "LSP buzilishining ko'p holati meros noto'g'ri tanlangani "
            "uchun sodir bo'ladi. Kompozitsiyada bu muammo umuman "
            "paydo bo'lmaydi, chunki hech kim bazaviy turning o'rnida "
            "ishlashga majbur emas:")

    code(d, """// Meros o'rniga o'ralgan obyekt
public sealed class LimitedStorage(IFileStorage inner, int maxBytes) : IFileStorage
{
    public Task<string> SaveAsync(Stream content, string name, CancellationToken ct)
    {
        if (content.Length > maxBytes)
            throw new FileTooLargeException(maxBytes);

        return inner.SaveAsync(content, name, ct);
    }
}""")

    para(d, "Bu holda ham cheklov qo'shildi, lekin u interfeysning "
            "shartnomasining qismi bo'lib e'lon qilinadi — "
            "`FileTooLargeException` interfeys hujjatida yoziladi va "
            "chaqiruvchi unga tayyor bo'ladi.")

    para(d, "Shuning uchun yangi klass yozganda `sealed` dan boshlayman "
            "va meros faqat haqiqatan kerak bo'lganda ochaman.")

    sources(d, [
        ("Liskov substitution principle",
         "https://learn.microsoft.com/en-us/dotnet/architecture/modern-web-apps-azure/architectural-principles#liskov-substitution"),
        ("Inheritance in C#",
         "https://learn.microsoft.com/en-us/dotnet/csharp/fundamentals/object-oriented/inheritance"),
        ("Choosing between class and interface",
         "https://learn.microsoft.com/en-us/dotnet/standard/design-guidelines/choosing-between-class-and-interface"),
    ])
