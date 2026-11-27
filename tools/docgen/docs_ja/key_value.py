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

    # ───────────────────────────────────────────
    h1(d, "8. Amaliyotdan: reflection natijasini keshlash")

    para(d, "Ish joyimdagi MAD ERP tizimida 5-bo'limda aytilgan `ConcurrentDictionary` "
            "ning aniq bir ishlatilishi bor va u menga lug'at haqida yangi narsa "
            "o'rgatdi.")

    para(d, "Vazifa shunday. Baza konteksti saqlashdan oldin har bir o'zgargan obyektni "
            "tekshirishi kerak: u maxsus atribut bilan belgilanganmi va belgilangan "
            "bo'lsa qaysi property ni o'qish kerak. Atributni topish — reflection, "
            "ya'ni qimmat amal. Saqlash esa har bir so'rovda bajariladi va o'zgargan "
            "obyektlar soni yuzlab bo'lishi mumkin.")

    code(d, """// Entity turi -> qo'riqlanadigan property nomi. Atributi yo'q turlar bo'sh satr
// bilan keshlanadi, ya'ni reflection har bir tur uchun bir marta ishlaydi.
private static readonly ConcurrentDictionary<Type, string> SchoolYearGuardProperties = new();""",
         caption="ApplicationDbContext.cs")

    para(d, "O'qish esa `GetOrAdd` bilan bajariladi:")

    code(d, """var propertyName = SchoolYearGuardProperties.GetOrAdd(
    entry.Metadata.ClrType,
    clrType => clrType.GetCustomAttribute<SchoolYearProcessGuardAttribute>()
        ?.SchoolYearPropertyName ?? string.Empty);

if (propertyName.Length == 0)
    continue;   // bu tur qo'riqlanmaydi""")

    h2(d, "8.1 Kalit sifatida Type")

    para(d, "6-bo'limda custom kalit uchun `GetHashCode` va `Equals` ni to'g'ri "
            "yozish kerakligi aytilgan. Bu yerda kalit — `System.Type`, ya'ni .NET "
            "ning o'z turi, va u shu talablarni allaqachon qondiradi: bitta tur uchun "
            "CLR da bitta `Type` nusxasi bo'ladi, shuning uchun taqqoslash "
            "havola bo'yicha ishlaydi va juda tez.")

    para(d, "Lekin `entry.Metadata.ClrType` yozilganiga e'tibor bering, "
            "`entry.Entity.GetType()` emas. Sababi lazy loading uchun EF Core "
            "obyektni proxy sinfiga o'raydi — o'sha proxy ning turi boshqa `Type` "
            "bo'ladi va unda atribut topilmaydi. Kalit sifatida noto'g'ri qiymat "
            "olinsa, lug'at ham to'g'ri javob bera olmaydi. Bu menga kalit tanlashning "
            "qanchalik nozik bo'lishini ko'rsatdi.")

    h2(d, "8.2 Salbiy natijani ham keshlash")

    para(d, "Eng qiziq tafsilot — izohda aytilgan narsa. Atributi **yo'q** turlar "
            "bo'sh satr bilan keshlanadi.")

    para(d, "Agar faqat topilgan natijalar saqlansa, atributi yo'q turlar uchun "
            "reflection har safar qaytadan ishlardi. Bunday turlar esa aksariyatni "
            "tashkil qiladi — tizimda yuzlab entity bor, qo'riqlanadigani yigirmaga "
            "yaqin. Ya'ni kesh eng ko'p uchraydigan holatda umuman yordam bermasdi.")

    code(d, """// Atribut topilmasa — null emas, bo'sh satr saqlanadi
clrType => clrType.GetCustomAttribute<SchoolYearProcessGuardAttribute>()
    ?.SchoolYearPropertyName ?? string.Empty""")

    note(d, "Bu naqsh menga alohida yoqdi:",
         "\"Javob yo'q\" ning o'zi ham javob, va uni saqlash kerak. 2-bo'limda "
         "`TryGetValue` haqida gapirganda men buni \"bor yoki yo'q\" deb oddiy "
         "qaragan edim. Bu yerda esa uch holat bor: hali tekshirilmagan, "
         "tekshirilgan va topilmagan, tekshirilgan va topilgan. Lug'atda birinchi "
         "ikkisini farqlash uchun maxsus qiymat kerak bo'ladi — bu yerda bo'sh satr. "
         "Agar property nomi `null` bo'lishi mumkin bo'lganda, bo'sh satr o'rniga "
         "boshqa belgi tanlash kerak bo'lardi.")

    h2(d, "8.3 Nega aynan ConcurrentDictionary")

    para(d, "Lug'at `static readonly`, ya'ni butun ilova uchun bitta va ko'p so'rov "
            "bir vaqtda unga murojaat qiladi. Oddiy `Dictionary` bu holatda "
            "ishlamaydi — 5-bo'limda aytilganidek, parallel yozish uning ichki "
            "tuzilmasini buzadi va natija kutilmagan bo'ladi, hatto cheksiz "
            "aylanishga tushib qolishi mumkin.")

    para(d, "`GetOrAdd` esa atomik: bir vaqtda ikki so'rov bir xil tur uchun "
            "murojaat qilsa, lambda ikki marta bajarilishi mumkin, lekin lug'atga "
            "bitta qiymat tushadi. Bu yerda bu muammo emas — reflection sof funksiya, "
            "ikki marta chaqirilsa ham bir xil natija beradi.")

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
