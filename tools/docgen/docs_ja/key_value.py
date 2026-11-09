# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "Key Value Pair structures (IDictionary, Dictionary, Hashtable)"
CATEGORY = "Data structure"
TITLE = "Kalit-Qiymat Tuzilmalari"
SUBTITLE = "Dictionary, Hashtable va ularning tanlovi"
FILENAME = "Key Value Pair structures (IDictionary, Dictionary, Hashtable).docx"


def build(d):
    h1(d, "1. Hash jadvali qanday ishlaydi")

    para(d, "`Dictionary<TKey, TValue>` ichida hash jadvali bor. "
            "Kalit qo'shilganda uning `GetHashCode()` qiymati "
            "hisoblanadi va shu qiymatdan **bucket** indeksi "
            "topiladi. Qiymat shu bucket'ga joylanadi.")

    para(d, "Shuning uchun kalit bo'yicha qidiruv o'rtacha **O(1)** "
            "— elementlar soniga bog'liq emas. Ro'yxatda qidiruv "
            "esa O(n).")

    para(d, "Ikki kalit bir xil bucket'ga tushsa — bu **collision**. "
            "Bunda `Equals()` bilan taqqoslanadi va zanjir ko'rinishida "
            "saqlanadi. Collision juda ko'p bo'lsa, qidiruv O(n) ga "
            "yaqinlashadi va samaradorlik yo'qoladi.")

    note(d, "Muhim shart",
         "`GetHashCode()` va `Equals()` izchil bo'lishi kerak: teng "
         "obyektlar bir xil hash berishi shart. Aks holda kalit "
         "bo'yicha qiymat topilmaydi — hech qanday xato chiqmaydi, "
         "shunchaki `TryGetValue` `false` qaytaradi.")

    # ───────────────────────────────────────────
    h1(d, "2. Dictionary — asosiy ishlatilishi")

    code(d, """var rates = new Dictionary<string, decimal>
{
    ["USD"] = 12650m,
    ["EUR"] = 13800m,
    ["RUB"] = 135m
};

// Qo'shish — kalit mavjud bo'lsa exception
rates.Add("GBP", 16000m);

// Qo'shish yoki almashtirish — exception yo'q
rates["GBP"] = 16100m;

// Faqat yo'q bo'lsa qo'shish
var added = rates.TryAdd("JPY", 85m);       // bool qaytaradi

// O'qish — eng to'g'ri shakl
if (rates.TryGetValue("USD", out var usd))
    Console.WriteLine(usd);

// Mavjud bo'lmagan kalitni indeks bilan o'qish — KeyNotFoundException
var missing = rates["XXX"];""")

    para(d, "`TryGetValue` ni afzal ko'raman: u bitta hash "
            "hisoblashda ikki ishni bajaradi — mavjudligini "
            "tekshiradi va qiymatni oladi. "
            "`ContainsKey` + indeks esa ikki marta qidiradi.")

    code(d, """// Ortiqcha: ikki marta qidiruv
if (rates.ContainsKey(code))
    total += rates[code];

// To'g'ri: bitta qidiruv
if (rates.TryGetValue(code, out var rate))
    total += rate;""")

    # ───────────────────────────────────────────
    h1(d, "3. Dictionary va Hashtable")

    table(d, ["", "`Dictionary<K,V>`", "`Hashtable`"],
          [["Tiplar", "Generic — kompilyator tekshiradi", "`object` — cast kerak"],
           ["Boxing", "Yo'q (qiymat turlari uchun)", "Ha — har bir element"],
           ["Yo'q kalit", "`KeyNotFoundException`", "`null` qaytaradi"],
           ["Tartib", "Kafolatlanmagan", "Kafolatlanmagan"],
           ["Thread xavfsizligi", "Yo'q", "O'qish uchun qisman"],
           ["Qachon ishlatiladi", "Doimo", "Faqat legacy kod"]],
          widths=[4.0, 5.4, 5.1])

    code(d, """// Hashtable — eski kod
var old = new Hashtable();
old["USD"] = 12650m;
var value = (decimal)old["USD"]!;       // cast majburiy
var missing = old["XXX"];               // null, exception yo'q

// Dictionary — yangi kod
var modern = new Dictionary<string, decimal> { ["USD"] = 12650m };
var typed = modern["USD"];              // cast kerak emas""")

    para(d, "`Hashtable` ni yangi kodda ishlatmayman. U .NET "
            "Framework 1.0 davridan qolgan va generic turlar paydo "
            "bo'lgandan keyin ma'nosini yo'qotgan. Uning "
            "\"yo'q kalitda `null` qaytarish\" xatti-harakati esa "
            "xatoni yashiradi.")

    # ───────────────────────────────────────────
    h1(d, "4. IDictionary va interfeys tanlash")

    code(d, """// Metod parametrida — eng kichik yetarli interfeys
public decimal Total(IReadOnlyDictionary<string, decimal> rates) => ...;

// O'zgartirish kerak bo'lsa
public void Merge(IDictionary<string, decimal> target) => ...;

// Faqat aylanib o'tish kerak bo'lsa
public void Log(IEnumerable<KeyValuePair<string, decimal>> pairs) => ...;""")

    para(d, "Parametrda `Dictionary<K,V>` ni aniq so'rash chaqiruvchini "
            "cheklaydi — u `ImmutableDictionary` yoki "
            "`ConcurrentDictionary` bera olmaydi. Shuning uchun "
            "interfeys so'rashni afzal ko'raman.")

    # ───────────────────────────────────────────
    h1(d, "5. Boshqa variantlar")

    table(d, ["Tur", "Qachon ishlataman"],
          [["`Dictionary<K,V>`", "Standart tanlov, bitta thread"],
           ["`ConcurrentDictionary<K,V>`", "Bir nechta thread'dan yoziladi"],
           ["`ImmutableDictionary<K,V>`", "O'zgarmas, ulashiladigan holat"],
           ["`FrozenDictionary<K,V>`", "Bir marta quriladi, juda ko'p o'qiladi"],
           ["`SortedDictionary<K,V>`", "Kalit bo'yicha tartib kerak, O(log n)"],
           ["`Lookup<K,V>`", "Bitta kalitga bir nechta qiymat"]],
          widths=[5.4, 9.1])

    h2(d, "ConcurrentDictionary")

    code(d, """private readonly ConcurrentDictionary<string, decimal> _cache = new();

public decimal GetOrFetch(string code)
    => _cache.GetOrAdd(code, key => FetchFromApi(key));

// Atomik yangilash
_cache.AddOrUpdate(code,
    addValue: newRate,
    updateValueFactory: (key, existing) => Math.Max(existing, newRate));""")

    note(d, "Nozik joy",
         "`GetOrAdd` ning fabrika funksiyasi bir nechta thread'da "
         "**bir necha marta** chaqirilishi mumkin — faqat bittasining "
         "natijasi saqlanadi. Shuning uchun fabrika yon ta'sirga ega "
         "bo'lmasligi kerak, masalan API ga qo'ng'iroq qilmasligi.")

    h2(d, "FrozenDictionary (.NET 8+)")

    code(d, """private static readonly FrozenDictionary<string, int> CurrencyPrecision =
    new Dictionary<string, int>
    {
        ["UZS"] = 2, ["USD"] = 2, ["JPY"] = 0
    }.ToFrozenDictionary();""")

    para(d, "Qurish sekinroq, lekin o'qish `Dictionary` dan ham "
            "tezroq. Ishga tushishda bir marta quriladigan va keyin "
            "faqat o'qiladigan sozlamalar uchun ideal.")

    # ───────────────────────────────────────────
    h1(d, "6. Custom kalit")

    para(d, "Kalit sifatida o'z turini ishlatish uchun `Equals` va "
            "`GetHashCode` to'g'ri bo'lishi kerak:")

    code(d, """// record o'zi to'g'ri amalga oshiradi — eng xavfsiz yo'l
public readonly record struct CurrencyPair(string From, string To);

var rates = new Dictionary<CurrencyPair, decimal>
{
    [new("USD", "UZS")] = 12650m,
    [new("EUR", "UZS")] = 13800m
};""")

    code(d, """// Klass bilan — qo'lda yozish kerak
public sealed class CurrencyPair : IEquatable<CurrencyPair>
{
    public string From { get; }
    public string To { get; }

    public bool Equals(CurrencyPair? other)
        => other is not null && From == other.From && To == other.To;

    public override bool Equals(object? obj) => Equals(obj as CurrencyPair);
    public override int GetHashCode() => HashCode.Combine(From, To);
}""")

    para(d, "Shuning uchun kompozit kalit kerak bo'lsa "
            "`readonly record struct` ni tanlayman — tenglik va hash "
            "avtomatik to'g'ri bo'ladi va heap'da obyekt "
            "yaratilmaydi.")

    h2(d, "Eng xavfli xato: o'zgaruvchan kalit")

    code(d, """var key = new MutableKey { Id = 1 };
dict[key] = "qiymat";

key.Id = 2;                  // hash o'zgardi

dict.TryGetValue(key, out var found);     // false — element topilmaydi
""")

    para(d, "Kalit hash'i o'zgarsa, element noto'g'ri bucket'da "
            "qolib ketadi va unga yetib bo'lmaydi. Shuning uchun "
            "kalit **o'zgarmas** bo'lishi kerak.")

    # ───────────────────────────────────────────
    h1(d, "7. Amaliy maslahatlar")

    bullets(d, [
        "**Hajmni oldindan berish.** `new Dictionary<K,V>(1000)` — "
        "qayta o'lchamlashni oldini oladi. Hajm taxminan ma'lum "
        "bo'lsa sezilarli tejaydi.",
        "**Satr kaliti uchun comparer.** Katta-kichik harfga sezgir "
        "bo'lmasligi kerak bo'lsa, "
        "`StringComparer.OrdinalIgnoreCase` ni konstruktorga "
        "beraman — `ToLower()` chaqirish o'rniga, chunki u har "
        "safar yangi satr yasaydi.",
        "**Tartibga tayanmaslik.** `Dictionary` elementlar tartibini "
        "kafolatlamaydi. Amalda u ko'pincha qo'shilish tartibida "
        "ko'rinadi, lekin bu hujjatlashtirilmagan — element "
        "o'chirilgandan keyin tartib o'zgaradi.",
        "**Aylanish paytida o'zgartirmaslik.** `foreach` ichida "
        "element qo'shish yoki o'chirish "
        "`InvalidOperationException` beradi. Kalitlar nusxasini "
        "olib aylanish kerak: `foreach (var key in dict.Keys.ToList())`.",
    ])

    sources(d, [
        ("Dictionary<TKey,TValue> Class",
         "https://learn.microsoft.com/en-us/dotnet/api/system.collections.generic.dictionary-2"),
        ("Collections and Data Structures",
         "https://learn.microsoft.com/en-us/dotnet/standard/collections/"),
        ("ConcurrentDictionary<TKey,TValue>",
         "https://learn.microsoft.com/en-us/dotnet/api/system.collections.concurrent.concurrentdictionary-2"),
        ("FrozenDictionary<TKey,TValue>",
         "https://learn.microsoft.com/en-us/dotnet/api/system.collections.frozen.frozendictionary-2"),
    ])
