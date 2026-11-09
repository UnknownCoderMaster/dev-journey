# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "Encapsulation"
CATEGORY = "OOP"
TITLE = "Inkapsulyatsiya"
SUBTITLE = "Ichki holatni yashirish va invariantni saqlash"
FILENAME = "Encapsulation.docx"


def build(d):
    h1(d, "1. Inkapsulyatsiya nima — va nima emas")

    para(d, "Inkapsulyatsiya ko'pincha \"maydonlarni `private` qilib, "
            "ularga `get`/`set` yozish\" deb tushuntiriladi. Bu ta'rif "
            "yetarli emas, chunki shu yondashuv hech narsani himoya "
            "qilmaydi:")

    code(d, """// Bu inkapsulyatsiya emas — maydon shunchaki ikki metod orqali ochilgan
public class Order
{
    private decimal _total;

    public decimal GetTotal() => _total;
    public void SetTotal(decimal value) => _total = value;
}""")

    para(d, "Haqiqiy inkapsulyatsiya — **ichki holatni tashqi dunyodan "
            "himoya qilish va obyekt qoidalarini (invariant) har doim "
            "to'g'ri ushlab turish**. Ya'ni savol \"maydon yopiqmi\" emas, "
            "balki \"obyektni noto'g'ri holatga keltirish mumkinmi\".")

    # ───────────────────────────────────────────
    h1(d, "2. Kirish modifikatorlari")

    table(d, ["Modifikator", "Kimga ko'rinadi"],
          [["`private`", "Faqat shu klass ichida (standart)"],
           ["`protected`", "Shu klass va undan meros olganlar"],
           ["`internal`", "Shu assembly ichida"],
           ["`protected internal`", "Shu assembly yoki meros olganlar"],
           ["`private protected`", "Shu assembly ichidagi meros olganlar"],
           ["`public`", "Hamma joyda"]],
          widths=[5.2, 9.3])

    para(d, "Qoidam — eng kam ko'rinadiganidan boshlash. `public` qilish "
            "oson, qaytarib olish esa buzuvchi o'zgarish bo'ladi. Shuning "
            "uchun ishonchim bo'lmasa `internal` qoldiraman.")

    # ───────────────────────────────────────────
    h1(d, "3. Invariantni himoya qilish")

    para(d, "Quyidagi klassda inkapsulyatsiya yo'q, chunki tashqaridan "
            "obyektni mantiqan noto'g'ri holatga keltirish mumkin:")

    code(d, """// HIMOYASIZ
public class Order
{
    public List<OrderItem> Items { get; set; } = [];
    public decimal Total { get; set; }
    public OrderStatus Status { get; set; }
}""")

    code(d, """var order = new Order();
order.Total = -5000;                     // manfiy summa
order.Status = OrderStatus.Shipped;      // bo'sh buyurtma yetkazildi?
order.Items.Clear();                     // summa qoldi, qatorlar yo'q""")

    para(d, "Bu yerdagi muammo `Total` hisoblanishi kerak bo'lgan qiymat "
            "ekani — u mustaqil maydon bo'lmasligi kerak. Va holat "
            "o'zgarishi qoidaga bog'liq, shuning uchun uni ochiq `set` "
            "bilan berish mumkin emas.")

    code(d, """public sealed class Order
{
    private readonly List<OrderItem> _items = [];

    public Guid Id { get; private init; }
    public OrderStatus Status { get; private set; }

    public IReadOnlyList<OrderItem> Items => _items;
    public decimal Total => _items.Sum(i => i.Quantity * i.UnitPrice);

    private Order() { }

    public static Order Create(Guid customerId)
        => new() { Id = Guid.CreateVersion7(), Status = OrderStatus.New };

    public void AddItem(Guid productId, int quantity, decimal unitPrice)
    {
        if (Status is not OrderStatus.New)
            throw new DomainException("Faqat yangi buyurtmaga qator qo'shiladi");

        if (quantity <= 0)
            throw new ArgumentOutOfRangeException(nameof(quantity));

        _items.Add(new OrderItem(productId, quantity, unitPrice));
    }

    public void Ship()
    {
        if (_items.Count == 0)
            throw new DomainException("Bo'sh buyurtma yetkazilmaydi");

        if (Status is not OrderStatus.Paid)
            throw new DomainException("To'lanmagan buyurtma yetkazilmaydi");

        Status = OrderStatus.Shipped;
    }
}""")

    para(d, "Endi obyektni noto'g'ri holatga keltirish mumkin emas. Har bir "
            "o'zgarish metod orqali o'tadi va metod qoidani tekshiradi.")

    # ───────────────────────────────────────────
    h1(d, "4. Kolleksiyani himoya qilish")

    para(d, "Eng ko'p e'tibordan chetda qoladigan joy. `List<T>` ni "
            "`get` bilan qaytarish — uni ochib qo'yish bilan barobar:")

    code(d, """// Xossa faqat o'qish uchun, lekin ro'yxat o'zi o'zgaradi
public List<OrderItem> Items { get; } = [];

order.Items.Add(...);      // invariant chetlab o'tildi
order.Items.Clear();       // hamma qator o'chdi""")

    para(d, "Shuning uchun ichki ro'yxatni yopiq saqlab, tashqariga faqat "
            "o'qish interfeysini chiqaraman:")

    code(d, """private readonly List<OrderItem> _items = [];
public IReadOnlyList<OrderItem> Items => _items;""")

    note(d, "Nozik joy",
         "`IReadOnlyList<T>` to'liq kafolat bermaydi — chaqiruvchi uni "
         "`List<T>` ga cast qilib o'zgartirishi mumkin. Haqiqiy kafolat "
         "kerak bo'lsa `_items.AsReadOnly()` yoki `[.. _items]` bilan "
         "nusxa qaytariladi. Lekin amalda interfeys qaytarish yetarli — "
         "u niyatni aniq bildiradi.")

    # ───────────────────────────────────────────
    h1(d, "5. Xossalarning turli shakllari")

    code(d, """// to'liq ochiq — DTO uchun normal, domen uchun yomon
public decimal Total { get; set; }

// faqat konstruktor yoki obyekt initsializatorida
public string Number { get; init; } = "";

// tashqaridan o'qish, ichkaridan yozish
public OrderStatus Status { get; private set; }

// hisoblanadigan — saqlanmaydi
public decimal Total => _items.Sum(i => i.Total);

// o'zgarmas maydon
private readonly IClock _clock;""")

    para(d, "Domen obyektlarida `{ get; set; }` ni ko'rsam, birinchi "
            "savolim — bu qiymat haqiqatan mustaqilmi yoki uni kimdir "
            "hisoblashi kerakmi. Ikkinchi savolim — uni o'zgartirish "
            "qanday qoidaga bog'liq.")

    # ───────────────────────────────────────────
    h1(d, "6. DTO va domen obyekti — boshqa qoidalar")

    para(d, "Inkapsulyatsiyani hamma joyga bir xil qo'llash xato. "
            "DTO ning vazifasi — ma'lumotni uzatish, shuning uchun unda "
            "himoyaga ehtiyoj yo'q:")

    code(d, """// DTO — ochiq bo'lishi normal
public sealed record CreateOrderRequest(Guid CustomerId, List<OrderLineDto> Lines);

// Domen obyekti — himoyalangan
public sealed class Order { /* yuqoridagi kabi */ }""")

    para(d, "Ikkisi orasidagi chegara aniq bo'lishi kerak: DTO API "
            "chegarasida yashaydi, domen obyekti esa ichkarida. "
            "DTO ni domen obyekti sifatida ishlatish boshlansa, "
            "invariantlar yo'qoladi.")

    # ───────────────────────────────────────────
    h1(d, "7. Nima foyda beradi")

    bullets(d, [
        "**Xato joyi aniq bo'ladi.** Agar buyurtma noto'g'ri holatda "
        "bo'lsa, sababi `Order` klassi ichida — butun loyihani qidirish "
        "kerak emas.",
        "**O'zgartirish xavfsiz bo'ladi.** Ichki tuzilma yopiq bo'lsa, uni "
        "o'zgartirish tashqi kodni buzmaydi. `Total` ni keshlashga qaror "
        "qilsam, chaqiruvchilar buni sezmaydi.",
        "**Test yozish osonlashadi.** Qoidalar bir joyda bo'lgani uchun "
        "ularni to'g'ridan-to'g'ri sinash mumkin, butun oqimni "
        "ko'tarmasdan.",
        "**Kod o'zini tushuntiradi.** Ochiq metodlar ro'yxati obyekt bilan "
        "nima qilish mumkinligini aytib turadi.",
    ])

    note(d, "Mening o'lchovim",
         "Klassni ko'rganda shu savolni beraman: **tashqaridan uni "
         "mantiqan buzilgan holatga keltirish mumkinmi?** Javob \"ha\" "
         "bo'lsa, inkapsulyatsiya yetarli emas — ochiq `set` yoki "
         "o'zgaruvchan kolleksiya bor degani.")

    sources(d, [
        ("Encapsulation in C#",
         "https://learn.microsoft.com/en-us/dotnet/csharp/fundamentals/object-oriented/"),
        ("Access modifiers — C# reference",
         "https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/keywords/access-modifiers"),
        ("Properties — C# programming guide",
         "https://learn.microsoft.com/en-us/dotnet/csharp/properties"),
    ])
