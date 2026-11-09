# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = ("Delgates, Event, Anonymous functions, Lambda functions, "
         "Action, Func, Predicate")
CATEGORY = ".NET / C#"
TITLE = "Delegate, Event va Lambda Ifodalar"
SUBTITLE = "Metodni qiymat sifatida uzatish"
FILENAME = "Delegates, Event, Lambda, Action, Func, Predicate.docx"


def build(d):
    h1(d, "1. Delegate nima")

    para(d, "Delegate — metodga ishora qiluvchi tur. Oddiy o'zgaruvchi son "
            "yoki satr saqlagani kabi, delegate o'zgaruvchisi **metodni** "
            "saqlaydi va uni keyinroq chaqirish mumkin.")

    code(d, """// e'lon: imzo belgilanadi
public delegate decimal DiscountRule(decimal amount);

// metod
static decimal TenPercent(decimal amount) => amount * 0.9m;

// ishlatish
DiscountRule rule = TenPercent;
var final = rule(1000m);          // 900""")

    para(d, "Buning foydasi — xatti-harakatni parametr sifatida uzatish. "
            "Masalan chegirma qoidasini tashqaridan berish mumkin bo'ladi va "
            "hisoblash kodi har bir yangi qoida uchun o'zgarmaydi:")

    code(d, """public decimal Calculate(decimal amount, DiscountRule rule) => rule(amount);""")

    # ───────────────────────────────────────────
    h1(d, "2. Tayyor delegate turlari: Action, Func, Predicate")

    para(d, "Amalda o'z delegate turini e'lon qilishga ehtiyoj kam, chunki "
            ".NET da tayyor generik turlar bor.")

    table(d, ["Tur", "Imzo", "Qaytaradi"],
          [["`Action`", "`Action<T1, T2, ...>`", "Hech narsa (`void`)"],
           ["`Func`", "`Func<T1, ..., TResult>`", "Oxirgi parametr — natija turi"],
           ["`Predicate`", "`Predicate<T>`", "`bool`"]],
          widths=[2.8, 5.4, 6.3])

    code(d, """Action<string> log = message => Console.WriteLine(message);
Func<decimal, decimal> discount = amount => amount * 0.9m;
Func<int, int, int> sum = (a, b) => a + b;
Predicate<Order> isPaid = order => order.Status == OrderStatus.Paid;""")

    para(d, "`Func` da oxirgi generik parametr har doim natija turi, "
            "qolganlari — kirish parametrlari. `Action` hech narsa "
            "qaytarmaydi. `Predicate<T>` esa aslida `Func<T, bool>` ning "
            "eski nomi — ikkisi bir xil ishni bajaradi, lekin "
            "`Predicate<T>` LINQ da ishlatilmaydi, shuning uchun yangi "
            "kodda `Func<T, bool>` ni afzal ko'raman.")

    note(d, "Eslatma",
         "`Action` va `Func` 16 tagacha parametrni qo'llab-quvvatlaydi. "
         "Agar shunchasi kerak bo'lsa, bu parametrlarni alohida obyektga "
         "to'plash kerakligi haqidagi signal.")

    # ───────────────────────────────────────────
    h1(d, "3. Anonim metod va lambda")

    para(d, "Delegate'ga alohida nomlangan metod yozish har doim shart emas. "
            "C# tarixida buning uchta shakli paydo bo'lgan:")

    code(d, """// 1. Nomlangan metod
Func<int, int> a = Square;
static int Square(int x) => x * x;

// 2. Anonim metod (C# 2) — hozir kam ishlatiladi
Func<int, int> b = delegate (int x) { return x * x; };

// 3. Lambda ifoda (C# 3) — bugungi standart
Func<int, int> c = x => x * x;""")

    para(d, "Lambda ikki shaklda yoziladi. Bitta ifoda bo'lsa qavs kerak "
            "emas va `return` ham yozilmaydi; bir nechta qator kerak bo'lsa "
            "blok shakli ishlatiladi:")

    code(d, """Func<Order, bool> single = o => o.Total > 0;

Func<Order, bool> block = o =>
{
    if (o.Items.Count == 0) return false;
    return o.Total > 0;
};""")

    h2(d, "Closure — tashqi o'zgaruvchini ushlab qolish")

    para(d, "Lambda o'zi turgan joydagi o'zgaruvchilarni \"ushlab qoladi\". "
            "Bu qulay, lekin bir nozik joyi bor: ushlanadigan narsa "
            "o'zgaruvchining **qiymati** emas, o'zi.")

    code(d, """var actions = new List<Action>();
for (int i = 0; i < 3; i++)
{
    int copy = i;                       // nusxa olinmasa natija 3,3,3 bo'ladi
    actions.Add(() => Console.Write(copy));
}
actions.ForEach(a => a());              // 012""")

    para(d, "C# 5 dan boshlab `foreach` o'zgaruvchisi har iteratsiyada yangi "
            "bo'ladi, shuning uchun u bilan bu muammo chiqmaydi. `for` "
            "tsiklida esa yuqoridagi nusxa olish kerak.")

    # ───────────────────────────────────────────
    h1(d, "4. Multicast delegate")

    para(d, "Delegate bir nechta metodga ishora qilishi mumkin. `+=` bilan "
            "qo'shiladi, `-=` bilan olib tashlanadi va chaqirilganda hammasi "
            "ketma-ket bajariladi:")

    code(d, """Action<string> notify = m => Console.WriteLine($"Konsol: {m}");
notify += m => File.AppendAllText("log.txt", m);

notify("Buyurtma yaratildi");    // ikkisi ham ishlaydi""")

    note(d, "Diqqat",
         "`Func` multicast bo'lsa, faqat **oxirgi** metodning natijasi "
         "qaytadi — qolganlari jimgina tashlab yuboriladi. Shuning uchun "
         "multicast faqat `Action` bilan mantiqiy.")

    # ───────────────────────────────────────────
    h1(d, "5. Event — nazorat qilingan delegate")

    para(d, "Oddiy delegate maydoni ochiq bo'lsa, tashqaridan uni butunlay "
            "almashtirish yoki o'zi chaqirish mumkin. `event` kalit so'zi "
            "shuni to'sadi: tashqaridan faqat obuna bo'lish va obunani "
            "bekor qilish mumkin.")

    code(d, """public class OrderProcessor
{
    public event EventHandler<OrderPlacedEventArgs>? OrderPlaced;

    public void Place(Order order)
    {
        // ... asosiy ish
        OrderPlaced?.Invoke(this, new OrderPlacedEventArgs(order.Id));
    }
}

public class OrderPlacedEventArgs(Guid orderId) : EventArgs
{
    public Guid OrderId { get; } = orderId;
}""")

    code(d, """var processor = new OrderProcessor();
processor.OrderPlaced += (sender, e) => Console.WriteLine($"Yaratildi: {e.OrderId}");""")

    para(d, "`?.Invoke(...)` shakli muhim — hech kim obuna bo'lmagan bo'lsa "
            "`OrderPlaced` `null` bo'ladi va oddiy chaqiruv "
            "`NullReferenceException` beradi.")

    h2(d, "Standart konvensiyalar")

    bullets(d, [
        "Imzo `(object? sender, TEventArgs e)` shaklida bo'ladi — bu .NET "
        "bo'ylab bir xil, shuning uchun uni buzish kodni kutilmagan qiladi.",
        "`EventHandler<T>` ni ishlataman, o'z delegate turimni "
        "e'lon qilmayman.",
        "Hodisa nomi o'tgan zamonda bo'ladi (`OrderPlaced`), chunki u "
        "allaqachon bo'lgan narsani bildiradi. Hodisadan oldin chaqiriladigan "
        "bo'lsa — `OrderPlacing`.",
    ])

    h2(d, "Obunani bekor qilishni unutmaslik")

    para(d, "Bu event bilan ishlashda eng ko'p uchraydigan muammo. Obuna "
            "bo'lgan obyekt `-=` qilinmasa, hodisa manbai unga havolani "
            "ushlab turadi va GC uni yig'a olmaydi. Uzoq yashaydigan obyekt "
            "qisqa yashaydigan obyektga obuna bo'lganda bu aniq xotira "
            "oqishiga aylanadi.")

    code(d, """public sealed class Subscriber : IDisposable
{
    private readonly OrderProcessor _processor;

    public Subscriber(OrderProcessor processor)
    {
        _processor = processor;
        _processor.OrderPlaced += OnPlaced;
    }

    private void OnPlaced(object? sender, OrderPlacedEventArgs e) { /* ... */ }

    public void Dispose() => _processor.OrderPlaced -= OnPlaced;
}""")

    para(d, "Shu sababli lambda bilan obuna bo'lishni ehtiyot bilan "
            "ishlataman: lambda'ga havola saqlanmasa, uni keyinchalik "
            "`-=` qilib bo'lmaydi.")

    # ───────────────────────────────────────────
    h1(d, "6. Amalda qayerda ishlatiladi")

    para(d, "Delegate va lambda .NET da hamma joyda, ko'pincha ularni "
            "delegate deb o'ylamasdan ishlataman:")

    bullets(d, [
        "LINQ — `Where(x => ...)`, `Select(x => ...)` hammasi "
        "`Func<...>` qabul qiladi.",
        "DI ro'yxatga olishdagi fabrika — `AddScoped<T>(sp => ...)`.",
        "Middleware va endpoint handler'lari.",
        "Qayta urinish va keshlash kabi umumiy mantiqni o'rash:",
    ])

    code(d, """public async Task<T> WithRetryAsync<T>(Func<Task<T>> action, int attempts = 3)
{
    for (var i = 1; ; i++)
    {
        try { return await action(); }
        catch when (i < attempts) { await Task.Delay(200 * i); }
    }
}

var rate = await WithRetryAsync(() => _api.GetRateAsync("USD"));""")

    para(d, "Bu yerda `Func<Task<T>>` tufayli qayta urinish mantiqi qanday "
            "operatsiya bajarilayotganini bilmaydi — shuning uchun uni "
            "istalgan joyda ishlatish mumkin.")

    sources(d, [
        ("Delegates — C# programming guide",
         "https://learn.microsoft.com/en-us/dotnet/csharp/programming-guide/delegates/"),
        ("Lambda expressions",
         "https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/operators/lambda-expressions"),
        ("Events — C# programming guide",
         "https://learn.microsoft.com/en-us/dotnet/csharp/programming-guide/events/"),
        ("Func, Action and Predicate delegates",
         "https://learn.microsoft.com/en-us/dotnet/api/system.func-2"),
    ])
