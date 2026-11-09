# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "Generic"
CATEGORY = ".NET / C#"
TITLE = "Generic Turlar va Metodlar"
SUBTITLE = "Tipni parametr sifatida olish"
FILENAME = "Generic.docx"


def build(d):
    h1(d, "1. Generic bo'lmagan kodning muammosi")

    para(d, "Generic'gacha umumiy kolleksiya `object` bilan yozilgan. "
            "`ArrayList` shunday ishlaydi:")

    code(d, """var list = new ArrayList();
list.Add(42);
list.Add("salom");            // kompilyator qarshilik qilmaydi

int first = (int)list[0];     // qo'lda cast
int second = (int)list[1];    // InvalidCastException — faqat ish vaqtida""")

    para(d, "Bu yerda uchta muammo bor. Tip xatosi kompilyatsiyada emas, ish "
            "vaqtida chiqadi. Har bir o'qishda cast yozish kerak. Va qiymat "
            "turlari (`int`, `struct`) `object` ga aylantirilganda **boxing** "
            "sodir bo'ladi — ya'ni heap da qo'shimcha obyekt yaratiladi, bu "
            "esa xotira va vaqt sarflaydi.")

    para(d, "Generic uchtasini birdan yechadi:")

    code(d, """var list = new List<int>();
list.Add(42);
// list.Add("salom");         // kompilyatsiya xatosi
int first = list[0];          // cast yo'q, boxing yo'q""")

    # ───────────────────────────────────────────
    h1(d, "2. Generic klass va metod")

    para(d, "Tip parametri burchak qavsda e'lon qilinadi va klass ichida "
            "oddiy tur kabi ishlatiladi:")

    code(d, """public class Result<T>
{
    public bool IsSuccess { get; }
    public T? Value { get; }
    public string? Error { get; }

    private Result(bool ok, T? value, string? error)
        => (IsSuccess, Value, Error) = (ok, value, error);

    public static Result<T> Success(T value) => new(true, value, null);
    public static Result<T> Failure(string error) => new(false, default, error);
}""")

    code(d, """Result<Order> result = await _service.FindAsync(id);
if (!result.IsSuccess) return NotFound(result.Error);
return Ok(result.Value);""")

    para(d, "Metodning o'zi ham generic bo'lishi mumkin — klass generic "
            "bo'lishi shart emas:")

    code(d, """public static T? FirstOrDefaultSafe<T>(IEnumerable<T> source, Func<T, bool> match)
{
    foreach (var item in source)
        if (match(item)) return item;
    return default;
}

// tip parametri ko'pincha o'zi aniqlanadi
var order = FirstOrDefaultSafe(orders, o => o.Total > 1000);""")

    note(d, "Eslatma",
         "`default` generic turda ehtiyotkorlik talab qiladi: reference tur "
         "uchun `null`, qiymat turi uchun nol yoki bo'sh struct qaytadi. "
         "Shuning uchun \"topilmadi\" holatini `default` bilan ifodalash "
         "`int` da chalkashlik keltiradi — nol haqiqiy qiymat ham bo'lishi "
         "mumkin.")

    # ───────────────────────────────────────────
    h1(d, "3. Constraint — tip parametriga shart qo'yish")

    para(d, "Generic metod ichida tip parametri haqida hech narsa bilinmaydi, "
            "shuning uchun unda faqat `object` metodlarini chaqirish mumkin. "
            "Constraint shu cheklovni yumshatadi.")

    table(d, ["Constraint", "Ma'nosi"],
          [["`where T : class`", "Reference tur bo'lishi kerak"],
           ["`where T : struct`", "Qiymat turi bo'lishi kerak"],
           ["`where T : IEntity`", "Shu interfeysni amalga oshirishi kerak"],
           ["`where T : BaseEntity`", "Shu klassdan meros bo'lishi kerak"],
           ["`where T : new()`", "Parametrsiz konstruktori bo'lishi kerak"],
           ["`where T : notnull`", "`null` bo'lmasligi kerak"],
           ["`where T : IComparable<T>`", "O'zi bilan taqqoslanishi mumkin"]],
          widths=[5.4, 9.1])

    code(d, """public interface IEntity
{
    Guid Id { get; }
}

public class InMemoryStore<T> where T : class, IEntity, new()
{
    private readonly Dictionary<Guid, T> _items = [];

    public void Add(T item) => _items[item.Id] = item;   // Id ni bilamiz
    public T Create() => new();                          // new() ni bilamiz
}""")

    para(d, "Constraint'siz `item.Id` yozib bo'lmaydi, chunki kompilyator "
            "`T` da bunday xossa borligini bilmaydi. Constraint esa shu "
            "ma'lumotni beradi.")

    h2(d, "O'zi bilan bog'langan constraint")

    code(d, """public abstract class Entity<TSelf> where TSelf : Entity<TSelf>
{
    public Guid Id { get; init; }
    public bool SameAs(TSelf other) => Id == other.Id;
}

public sealed class Customer : Entity<Customer> { }""")

    para(d, "Bu shakl boshida g'alati ko'rinadi, lekin metod aniq hosila "
            "turni qaytarishi kerak bo'lganda kerak bo'ladi.")

    # ───────────────────────────────────────────
    h1(d, "4. Generic qanday ishlaydi — ichidan")

    para(d, "CLR generic turlarni ikki xil usulda qayta ishlaydi.")

    bullets(d, [
        "**Qiymat turlari** uchun har bir tip parametri uchun alohida mashina "
        "kodi yaratiladi. `List<int>` va `List<double>` — ikki alohida kod. "
        "Shuning uchun boxing bo'lmaydi va tezlik yo'qolmaydi.",
        "**Reference turlari** uchun bitta umumiy kod ishlatiladi, chunki "
        "hamma havola bir xil o'lchamda. `List<string>` va `List<Order>` "
        "bir xil kodni ishlatadi.",
    ])

    para(d, "Bu tafsilot amalda bir narsani tushuntiradi: generic ishlatish "
            "tezlikni pasaytirmaydi, aksincha `object` bilan ishlashga "
            "nisbatan tezlashtiradi.")

    # ───────────────────────────────────────────
    h1(d, "5. Kovariantlik va kontravariantlik")

    para(d, "`Order` `BaseOrder` dan meros bo'lsa, `List<Order>` ni "
            "`List<BaseOrder>` ga berib bo'lmaydi. Bu ataylab — aks holda "
            "ro'yxatga boshqa turdagi element qo'shib yuborish mumkin bo'lardi.")

    para(d, "Lekin faqat o'qiladigan interfeyslarda bu xavf yo'q, shuning "
            "uchun ularda `out` bilan kovariantlik ruxsat etiladi:")

    code(d, """IEnumerable<string> strings = new List<string>();
IEnumerable<object> objects = strings;      // ruxsat — IEnumerable<out T>

Action<object> logObject = o => Console.WriteLine(o);
Action<string> logString = logObject;       // ruxsat — Action<in T>""")

    bullets(d, [
        "`out T` — **kovariant**. Tur faqat chiqishda ishlatiladi, shuning "
        "uchun hosila turni bazaviy tur o'rniga berish xavfsiz.",
        "`in T` — **kontravariant**. Tur faqat kirishda ishlatiladi, shuning "
        "uchun bazaviy turni hosila tur o'rniga berish xavfsiz.",
    ])

    # ───────────────────────────────────────────
    h1(d, "6. Amaliy misol: generic repozitoriy va uning chegarasi")

    code(d, """public interface IRepository<T> where T : class, IEntity
{
    Task<T?> FindAsync(Guid id, CancellationToken ct);
    Task AddAsync(T entity, CancellationToken ct);
}

public class EfRepository<T>(AppDbContext db) : IRepository<T>
    where T : class, IEntity
{
    public Task<T?> FindAsync(Guid id, CancellationToken ct) =>
        db.Set<T>().FirstOrDefaultAsync(e => e.Id == id, ct);

    public async Task AddAsync(T entity, CancellationToken ct) =>
        await db.Set<T>().AddAsync(entity, ct);
}""")

    code(d, """builder.Services.AddScoped(typeof(IRepository<>), typeof(EfRepository<>));""")

    para(d, "Bu kod chiroyli ko'rinadi va bir marta yozilib hamma entity uchun "
            "ishlaydi. Lekin o'zim uchun aytib qo'yadigan chegarasi bor: "
            "generic repozitoriy faqat **umumiy** operatsiyalarni biladi. "
            "Har bir entity'ga xos so'rov — `Include`, projeksiya, filtrlangan "
            "ro'yxat — bu interfeysga sig'maydi.")

    note(d, "Xulosa",
         "Generic — takrorlanuvchi kodni kamaytirish asbobi, lekin har bir "
         "takrorlanish yomon emas. Generic abstraksiya domenga xos "
         "mantiqni yashirishga boshlasa, oddiy aniq klass tushunarliroq "
         "bo'ladi.")

    sources(d, [
        ("Generics in .NET",
         "https://learn.microsoft.com/en-us/dotnet/standard/generics/"),
        ("Constraints on type parameters",
         "https://learn.microsoft.com/en-us/dotnet/csharp/programming-guide/generics/constraints-on-type-parameters"),
        ("Covariance and contravariance",
         "https://learn.microsoft.com/en-us/dotnet/standard/generics/covariance-and-contravariance"),
    ])
