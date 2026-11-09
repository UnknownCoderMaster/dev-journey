# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "Backing Fields"
CATEGORY = "EF CORE"
TITLE = "Backing Field"
SUBTITLE = "EF ni xossa o'rniga maydon bilan ishlatish"
FILENAME = "Backing Fields.docx"


def build(d):
    h1(d, "1. Muammo: inkapsulyatsiya va EF talablari")

    para(d, "Domen obyektini to'g'ri yozsam, uning holatini tashqaridan "
            "o'zgartirib bo'lmaydi — ochiq `set` bo'lmaydi:")

    code(d, """public sealed class Order
{
    private readonly List<OrderItem> _items = [];

    public IReadOnlyList<OrderItem> Items => _items;
    public OrderStatus Status { get; private set; }

    public void AddItem(OrderItem item) { /* qoidalar tekshiriladi */ }
}""")

    para(d, "Lekin EF Core bazadan o'qiganda qiymatlarni biror joyga "
            "yozishi kerak. `Items` faqat o'qish uchun, "
            "`IReadOnlyList<T>` ga element qo'shib bo'lmaydi.")

    para(d, "Backing field aynan shu muammoni yechadi: EF xossani "
            "chetlab o'tib, ostidagi **maydonga** to'g'ridan-to'g'ri "
            "yozadi.")

    # ───────────────────────────────────────────
    h1(d, "2. Convention bo'yicha aniqlanishi")

    para(d, "EF Core maydonni nom bo'yicha o'zi topadi. `Status` "
            "xossasi uchun qidiriladigan nomlar:")

    bullets(d, [
        "`_status`",
        "`_Status`",
        "`m_status`",
        "`m_Status`",
    ])

    para(d, "Shuning uchun ko'p holatda hech narsa sozlash kerak emas — "
            "oddiy nomlash konvensiyasiga amal qilish yetarli.")

    code(d, """public sealed class Order
{
    private readonly List<OrderItem> _items = [];      // topiladi
    public IReadOnlyList<OrderItem> Items => _items;
}""")

    note(d, "Eslatma",
         "Maydon `readonly` bo'lsa ham ishlaydi, chunki EF ro'yxatning "
         "o'ziga element qo'shadi — havolani almashtirmaydi. Lekin oddiy "
         "qiymat (`int`, `string`) uchun `readonly` bo'lsa EF yoza "
         "olmaydi.")

    # ───────────────────────────────────────────
    h1(d, "3. Aniq sozlash")

    code(d, """modelBuilder.Entity<Order>()
    .Property(o => o.Status)
    .HasField("_orderStatus");          // nom konvensiyaga mos emas""")

    para(d, "Xossasi umuman bo'lmagan maydonni ham map qilish mumkin:")

    code(d, """modelBuilder.Entity<Order>()
    .Property("_internalNote")
    .HasColumnName("internal_note");""")

    para(d, "Bu holda maydon butunlay yopiq qoladi — tashqaridan uni "
            "o'qish ham mumkin emas, lekin bazada saqlanadi. Ichki "
            "texnik ma'lumot uchun qulay.")

    # ───────────────────────────────────────────
    h1(d, "4. PropertyAccessMode — kim nimani ishlatadi")

    para(d, "EF qaysi holatda maydonni, qaysi holatda xossani "
            "ishlatishini boshqarish mumkin:")

    table(d, ["Rejim", "O'qish", "Yozish"],
          [["`Field`", "Maydon", "Maydon"],
           ["`Property`", "Xossa", "Xossa"],
           ["`FieldDuringConstruction`", "Xossa", "Maydon (o'qishda)"],
           ["`PreferField`", "Maydon bo'lsa — maydon", "Maydon bo'lsa — maydon"]],
          widths=[5.4, 4.5, 4.6])

    code(d, """modelBuilder.Entity<Order>()
    .Property(o => o.Status)
    .UsePropertyAccessMode(PropertyAccessMode.Field);""")

    para(d, "Standart rejim — `PreferFieldDuringConstruction`: bazadan "
            "o'qiganda maydon, qolgan hollarda xossa ishlatiladi. Bu "
            "mantiqiy, chunki o'qish paytida validatsiya ishlashi kerak "
            "emas — ma'lumot allaqachon tekshirilgan.")

    para(d, "Butun modelga bir joyda qo'yish ham mumkin:")

    code(d, """modelBuilder.UsePropertyAccessMode(PropertyAccessMode.Field);""")

    # ───────────────────────────────────────────
    h1(d, "5. Amaliy misol: himoyalangan agregat")

    code(d, """public sealed class Order
{
    private readonly List<OrderItem> _items = [];

    private Order() { }        // EF uchun — parametrsiz konstruktor

    public Guid Id { get; private init; }
    public OrderStatus Status { get; private set; }
    public DateTimeOffset CreatedAt { get; private init; }

    public IReadOnlyList<OrderItem> Items => _items;
    public decimal Total => _items.Sum(i => i.Quantity * i.UnitPrice);

    public static Order Create(TimeProvider clock) => new()
    {
        Id = Guid.CreateVersion7(),
        Status = OrderStatus.New,
        CreatedAt = clock.GetUtcNow()
    };

    public void AddItem(Guid productId, int quantity, decimal price)
    {
        if (Status is not OrderStatus.New)
            throw new DomainException("Faqat yangi buyurtmaga qator qo'shiladi");

        _items.Add(new OrderItem(productId, quantity, price));
    }

    public void MarkPaid()
    {
        if (_items.Count == 0)
            throw new DomainException("Bo'sh buyurtma to'lanmaydi");

        Status = OrderStatus.Paid;
    }
}""")

    code(d, """modelBuilder.Entity<Order>(b =>
{
    b.HasKey(o => o.Id);
    b.Property(o => o.Status).HasConversion<string>();

    // Navigatsiyani maydon orqali sozlash
    b.Metadata.FindNavigation(nameof(Order.Items))!
        .SetPropertyAccessMode(PropertyAccessMode.Field);

    b.HasMany(o => o.Items).WithOne().HasForeignKey("OrderId");

    b.Ignore(o => o.Total);     // hisoblanadigan — saqlanmaydi
});""")

    para(d, "Natijada domen qoidalari to'liq himoyalangan, lekin EF "
            "bazadan obyektni muammosiz tiklaydi. Bu ikki talabni "
            "birlashtirishning standart yo'li.")

    note(d, "Parametrsiz konstruktor",
         "EF obyektni yaratish uchun parametrsiz konstruktorga "
            "ehtiyoj sezadi, lekin u `private` bo'lishi mumkin. "
            "Shuning uchun tashqi kod uni ishlatmaydi va fabrika "
            "metodidan o'tishga majbur bo'ladi.")

    # ───────────────────────────────────────────
    h1(d, "6. Nimaga e'tibor beraman")

    bullets(d, [
        "**Hisoblanadigan xossani `Ignore` qilish.** `Total` kabi "
        "xossalarni EF ustun deb o'ylaydi va migratsiyaga qo'shadi. "
        "Buni `Ignore` bilan to'xtataman, yoki agar bazada "
        "hisoblanishini xohlasam — `HasComputedColumnSql`.",
        "**Maydon nomini o'zgartirish migratsiyaga ta'sir qilishi.** "
        "Maydon map qilingan bo'lsa, uning nomi model qismiga aylanadi. "
        "Refactoring bilan nom o'zgarsa, kutilmagan migratsiya paydo "
        "bo'ladi.",
        "**Navigatsiya uchun alohida sozlash.** Oddiy xossalar "
        "convention bilan topiladi, lekin kolleksiya navigatsiyasida "
        "ba'zan `SetPropertyAccessMode` ni aniq qo'yish kerak bo'ladi.",
        "**`AsNoTracking` bilan ham ishlaydi.** Backing field tracking'ga "
        "bog'liq emas — o'qish ikki holatda ham maydon orqali ketadi.",
    ])

    sources(d, [
        ("Backing Fields — EF Core",
         "https://learn.microsoft.com/en-us/ef/core/modeling/backing-field"),
        ("Constructors with parameters",
         "https://learn.microsoft.com/en-us/ef/core/modeling/constructors"),
        ("Encapsulated collections",
         "https://learn.microsoft.com/en-us/ef/core/modeling/relationships/navigations"),
    ])
