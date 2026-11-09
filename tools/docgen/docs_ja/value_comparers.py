# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "Value Comparers, Background, Shallow vs. deep comparison"
CATEGORY = "EF CORE"
TITLE = "Value Comparer"
SUBTITLE = "Change tracker o'zgarishni qanday aniqlaydi"
FILENAME = "Value Comparers, Shallow vs deep comparison.docx"


def build(d):
    h1(d, "1. Muammoning kelib chiqishi")

    para(d, "Change tracker entity o'qilganda uning **snapshot** ini "
            "oladi, ya'ni hamma xossa qiymatini eslab qoladi. "
            "`SaveChanges()` paytida joriy qiymatlarni snapshot bilan "
            "taqqoslaydi va farq topilgan xossalarni `UPDATE` ga "
            "qo'shadi.")

    para(d, "Oddiy turlar (`int`, `string`, `DateTime`) bilan bu muammosiz "
            "ishlaydi. Lekin **o'zgaruvchan** (mutable) tur bo'lsa, "
            "snapshot va joriy qiymat **bir xil obyektga** ishora qiladi "
            "— ya'ni ularni taqqoslash har doim \"o'zgarmagan\" deb "
            "javob beradi.")

    code(d, """// Tags — List<string>, converter bilan JSON sifatida saqlanadi
var product = await db.Products.FirstAsync(ct);

product.Tags.Add("yangi");          // ro'yxat o'zgardi
await db.SaveChangesAsync(ct);      // ... lekin UPDATE ketmaydi""")

    para(d, "Bu eng chalg'ituvchi xatolardan biri: hech qanday exception "
            "yo'q, `SaveChanges` muvaffaqiyatli tugaydi, lekin ma'lumot "
            "saqlanmaydi.")

    # ───────────────────────────────────────────
    h1(d, "2. Sayoz va chuqur taqqoslash")

    para(d, "**Sayoz (shallow) taqqoslash** — havolalarni "
            "taqqoslash: ikki o'zgaruvchi bir xil obyektga ishora "
            "qiladimi. Tez, lekin mazmun o'zgarishini ko'rmaydi.")

    para(d, "**Chuqur (deep) taqqoslash** — tarkibni element bo'yicha "
            "taqqoslash. Sekinroq, lekin haqiqiy o'zgarishni aniqlaydi.")

    table(d, ["Tur", "Standart taqqoslash", "Comparer kerakmi"],
          [["`int`, `decimal`, `bool`", "Qiymat bo'yicha", "Yo'q"],
           ["`string`", "Qiymat bo'yicha (o'zgarmas)", "Yo'q"],
           ["`byte[]`", "Havola bo'yicha", "Ha"],
           ["`List<T>`", "Havola bo'yicha", "Ha"],
           ["O'zgarmas `record`", "Qiymat bo'yicha", "Yo'q"],
           ["O'zgaruvchan klass", "Havola bo'yicha", "Ha"]],
          widths=[4.6, 5.4, 4.5])

    para(d, "Jadvaldan ko'rinadigan qoida: **o'zgarmas tur comparer "
            "talab qilmaydi**. Shuning uchun value object'larni "
            "`readonly record struct` qilib yasash bu muammoni "
            "butunlay oldini oladi.")

    # ───────────────────────────────────────────
    h1(d, "3. Value comparer yozish")

    code(d, """modelBuilder.Entity<Product>()
    .Property(p => p.Tags)
    .HasConversion(
        tags => JsonSerializer.Serialize(tags, (JsonSerializerOptions?)null),
        json => JsonSerializer.Deserialize<List<string>>(json, (JsonSerializerOptions?)null)
                ?? new List<string>(),
        new ValueComparer<List<string>>(
            (a, b) => a != null && b != null && a.SequenceEqual(b),
            list => list.Aggregate(0, (hash, item) => HashCode.Combine(hash, item.GetHashCode())),
            list => list.ToList()));""")

    para(d, "Comparer uchta funksiyadan iborat va ularning har biri "
            "aniq vazifani bajaradi:")

    bullets(d, [
        "**Equality** — ikki qiymat tengmi. Bu yerda `SequenceEqual` "
        "elementlarni tartib bilan taqqoslaydi.",
        "**Hash code** — qiymatni xeshlash. Kalit yoki guruhlashda "
        "ishlatiladi.",
        "**Snapshot** — qiymatning **nusxasini** olish. Eng muhim qism: "
        "nusxa olinmasa, snapshot asl obyektga ishora qiladi va "
        "taqqoslash hech qachon farq topmaydi.",
    ], numbered=True)

    note(d, "Eng ko'p qilinadigan xato",
         "Snapshot funksiyasida `list => list` deb yozish. Bu nusxa "
         "emas — bir xil havola. Natijada comparer qo'yilgan bo'lsa ham "
         "o'zgarish aniqlanmaydi, ya'ni muammo yechilmaydi.")

    # ───────────────────────────────────────────
    h1(d, "4. Tayyor comparer'lar")

    code(d, """// Massiv va kolleksiyalar uchun
.HasConversion(
    v => string.Join(',', v),
    v => v.Split(',', StringSplitOptions.RemoveEmptyEntries).ToList(),
    ValueComparer.CreateDefault<List<string>>(favorStructuralComparisons: true));""")

    para(d, "EF Core'ning `ValueComparer` sinfida tayyor variantlar bor. "
            "`byte[]` uchun esa `ArrayStructuralComparer` kabi maxsus "
            "comparer kerak bo'ladi — chunki standart holatda EF massivni "
            "havola bo'yicha taqqoslaydi.")

    h2(d, "rowversion uchun alohida holat")

    code(d, """modelBuilder.Entity<Order>()
    .Property(o => o.Version)
    .IsRowVersion();""")

    para(d, "Concurrency token bo'lgan `byte[]` ustunini EF Core o'zi "
            "to'g'ri taqqoslaydi — `IsRowVersion()` kerakli comparer'ni "
            "ham qo'yadi. Shuning uchun uni qo'lda sozlash kerak emas.")

    # ───────────────────────────────────────────
    h1(d, "5. Comparer kerak bo'lmaydigan dizayn")

    para(d, "Muammoni yechishdan ko'ra uni **oldini olish** yaxshiroq. "
            "Agar value object o'zgarmas bo'lsa, comparer umuman kerak "
            "emas:")

    code(d, """// O'zgaruvchan — comparer kerak
public class Money
{
    public decimal Amount { get; set; }
    public string Currency { get; set; } = "";
}

// O'zgarmas — comparer kerak emas, record tenglikni o'zi beradi
public readonly record struct Money(decimal Amount, string Currency);""")

    para(d, "Kolleksiya uchun ham shu tamoyil ishlaydi: `List<T>` "
            "o'rniga o'zgarmas kolleksiya ishlatsam, har bir o'zgarish "
            "yangi obyekt yasaydi va EF buni darhol ko'radi:")

    code(d, """public sealed class Product
{
    public ImmutableArray<string> Tags { get; private set; } = [];

    public void AddTag(string tag) => Tags = Tags.Add(tag);   // yangi obyekt
}""")

    # ───────────────────────────────────────────
    h1(d, "6. Diagnostika: o'zgarish ko'rinmayotganini tekshirish")

    para(d, "O'zgarish saqlanmayotganini shubha qilsam, change tracker'dan "
            "to'g'ridan-to'g'ri so'rayman:")

    code(d, """product.Tags.Add("test");

var entry = db.Entry(product);
Console.WriteLine(entry.State);                              // Unchanged?
Console.WriteLine(entry.Property(p => p.Tags).IsModified);   // false?

// Qo'lda majburlash — vaqtinchalik yechim
entry.Property(p => p.Tags).IsModified = true;""")

    para(d, "`IsModified = true` qo'yish muammoni yashirin tarzda "
            "yechadi, lekin bu yamoq: har bir o'zgarish joyida esdan "
            "chiqishi mumkin. To'g'ri yechim — comparer qo'yish yoki "
            "turni o'zgarmas qilish.")

    code(d, """// Butun tracker holatini ko'rish — debug uchun qulay
Console.WriteLine(db.ChangeTracker.DebugView.LongView);""")

    note(d, "Xulosa",
         "Value comparer — converter'ning \"yarmi\". Converter qiymatni "
         "qanday saqlashni aytadi, comparer esa o'zgarishni qanday "
         "aniqlashni. Mutable turga converter qo'yib, comparer "
         "qo'ymaslik — jim xato manbai.")

    sources(d, [
        ("Value Comparers — EF Core",
         "https://learn.microsoft.com/en-us/ef/core/modeling/value-comparers"),
        ("Value Conversions — EF Core",
         "https://learn.microsoft.com/en-us/ef/core/modeling/value-conversions"),
        ("Change Tracking in EF Core",
         "https://learn.microsoft.com/en-us/ef/core/change-tracking/"),
        ("Debugging change tracker state",
         "https://learn.microsoft.com/en-us/ef/core/change-tracking/debug-views"),
    ])
