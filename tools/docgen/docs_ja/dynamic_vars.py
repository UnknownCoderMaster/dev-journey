# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "dynamic variables (dynamic, var , object)"
CATEGORY = ".NET / C#"
TITLE = "dynamic, var va object"
SUBTITLE = "Uchta o'xshash ko'rinadigan, lekin butunlay boshqa narsa"
FILENAME = "dynamic variables (dynamic, var, object).docx"


def build(d):
    h1(d, "1. Nega bu uchtasi chalkashtiriladi")

    para(d, "`var`, `object` va `dynamic` — uchtasi ham \"tipni aniq "
            "yozmaslik\" ko'rinishini beradi. Lekin ular uch xil bosqichda "
            "ishlaydi va shuning uchun oqibatlari ham boshqacha.")

    table(d, ["", "Tip qachon aniqlanadi", "Kompilyator tekshiradimi"],
          [["`var`", "Kompilyatsiyada", "Ha — to'liq"],
           ["`object`", "Kompilyatsiyada (`object` sifatida)",
            "Ha, lekin faqat `object` a'zolarini"],
           ["`dynamic`", "Ish vaqtida", "Yo'q"]],
          widths=[2.6, 6.0, 6.0])

    # ───────────────────────────────────────────
    h1(d, "2. var — qisqartma, boshqa hech narsa emas")

    para(d, "`var` tipni o'ng tomondan aniqlab oladi va natijada **aniq "
            "tip** qoladi. Ya'ni `var` o'zgaruvchi hech qanday "
            "moslashuvchanlik bermaydi:")

    code(d, """var count = 42;              // int
var name = "Orzibek";        // string
var orders = new List<Order>();   // List<Order>

count = "matn";              // kompilyatsiya xatosi: int ga string berilmaydi""")

    para(d, "Shuning uchun `var int count = 42;` deb yozilgan IL kodi "
            "`int count = 42;` dan farq qilmaydi. Tezlik, xavfsizlik, "
            "IntelliSense — hammasi bir xil.")

    para(d, "`var` ishlatib bo'lmaydigan joylar bor:")

    bullets(d, [
        "Boshlang'ich qiymat berilmasa — `var x;` noto'g'ri, chunki tipni "
        "aniqlashga asos yo'q.",
        "`null` berilsa — `var x = null;` ham noto'g'ri.",
        "Maydon (field) e'lonida — faqat lokal o'zgaruvchida ishlaydi.",
        "Metod parametri yoki qaytish turida.",
    ])

    h2(d, "Qachon ishlataman")

    para(d, "Tip o'ng tomondan ko'rinib turgan bo'lsa — `var`. Takrorlash "
            "faqat shovqin qo'shadi:")

    code(d, """var repository = new OrderRepository(context);          // toza
OrderRepository repository = new OrderRepository(context);  // takror""")

    para(d, "Tip ko'rinmasa — aniq yozaman. Masalan metod nomidan nima "
            "qaytishi tushunarsiz bo'lsa, `var` kod o'qishni "
            "qiyinlashtiradi:")

    code(d, """var result = _service.Process(order);     // nima qaytdi? bilinmaydi
Result<Invoice> result = _service.Process(order);   // tushunarli""")

    para(d, "Anonim tip bilan esa `var` dan boshqa yo'l yo'q:")

    code(d, """var summary = orders.Select(o => new { o.Id, o.Total });""")

    # ───────────────────────────────────────────
    h1(d, "3. object — hamma turning bazasi")

    para(d, ".NET da hamma tur `object` dan meros bo'ladi, shuning uchun "
            "`object` o'zgaruvchisiga istalgan narsani berish mumkin. Lekin "
            "undan foydalanish uchun qaytib aniq turga keltirish kerak:")

    code(d, """object value = 42;

// int metodlariga kira olmaymiz
// var doubled = value * 2;     // kompilyatsiya xatosi

int number = (int)value;        // unboxing
var doubled = number * 2;""")

    h2(d, "Boxing va unboxing")

    para(d, "Qiymat turi (`int`, `struct`) `object` ga berilganda u heap da "
            "o'ralgan obyektga aylanadi — bu **boxing**. Teskari jarayon — "
            "**unboxing**. Ikkisi ham xotira va vaqt sarflaydi.")

    code(d, """object boxed = 42;              // boxing: heap da yangi obyekt
int unboxed = (int)boxed;       // unboxing: tip tekshiriladi va nusxa olinadi""")

    para(d, "Tsikl ichida minglab marta boxing bo'lsa, bu sezilarli yuk "
            "beradi. Generic turlar aynan shu sababdan paydo bo'lgan: "
            "`List<int>` boxing qilmaydi, eski `ArrayList` esa har bir "
            "element uchun qiladi.")

    h2(d, "Xavfsiz cast")

    code(d, """// InvalidCastException beradi agar tip mos bo'lmasa
int a = (int)value;

// null qaytaradi (faqat reference va nullable turlar uchun)
string? b = value as string;

// eng aniq shakl — pattern matching
if (value is int number && number > 0) { }""")

    note(d, "Eslatma",
         "`as` qiymat turlari bilan ishlamaydi — `value as int` kompilyatsiya "
         "xatosi beradi. `value as int?` esa ishlaydi.")

    # ───────────────────────────────────────────
    h1(d, "4. dynamic — tekshiruvni ish vaqtiga ko'chirish")

    para(d, "`dynamic` kompilyatorga \"bu o'zgaruvchini tekshirma\" deydi. "
            "A'zo mavjudligi faqat chaqiruv paytida aniqlanadi:")

    code(d, """dynamic value = 42;
var doubled = value * 2;            // kompilyatsiya o'tadi, ish vaqtida 84

dynamic text = "salom";
var upper = text.ToUpper();         // ishlaydi
var wrong = text.Fly();             // kompilyatsiya o'tadi,
                                    // ish vaqtida RuntimeBinderException""")

    para(d, "Ichida bu DLR (Dynamic Language Runtime) orqali amalga "
            "oshiriladi: har bir chaqiruvda a'zo reflection bilan topiladi va "
            "keshlanadi. Shuning uchun `dynamic` oddiy chaqiruvdan sezilarli "
            "sekinroq.")

    h2(d, "Qachon haqiqatan foydali")

    bullets(d, [
        "COM interop — Office avtomatlashtirish kabi, tip ma'lumoti to'liq "
        "bo'lmagan API bilan ishlashda.",
        "Python yoki JavaScript kabi dinamik tillardan kelgan obyektlar bilan.",
        "Tuzilishi oldindan ma'lum bo'lmagan JSON bilan ishlashda — lekin bu "
        "yerda ham yaxshiroq variant bor.",
    ])

    para(d, "Oxirgi holatda men `dynamic` o'rniga `JsonNode` yoki "
            "`JsonDocument` ni tanlayman, chunki ular kutilmagan tuzilishda "
            "tushunarli xato beradi:")

    code(d, """// dynamic bilan — xato tushunarsiz
dynamic data = JsonConvert.DeserializeObject(json)!;
var city = data.address.city;

// JsonNode bilan — aniq va tekshirib olish mumkin
var node = JsonNode.Parse(json);
var city = node?["address"]?["city"]?.GetValue<string>();""")

    note(d, "Mening pozitsiyam",
         "`dynamic` ni backend kodda deyarli ishlatmayman. U kompilyatorning "
         "eng katta foydasini — xatoni ishga tushirishdan oldin topishni — "
         "yo'qotadi. Agar tipni bilmasam, buni `JsonNode`, interfeys yoki "
         "pattern matching bilan aniq ifodalash yaxshiroq.")

    # ───────────────────────────────────────────
    h1(d, "5. Uchtasini bir misolda taqqoslash")

    code(d, """var    a = "salom";      // string: hamma string metodi bor
object b = "salom";      // object: cast kerak
dynamic c = "salom";     // dynamic: metod bor deb ishoniladi

a.ToUpper();             // ishlaydi
b.ToUpper();             // KOMPILYATSIYA XATOSI
((string)b).ToUpper();   // ishlaydi
c.ToUpper();             // ishlaydi (ish vaqtida tekshiriladi)
c.ToUpperCase();         // kompilyatsiya o'tadi, ish vaqtida qulaydi""")

    para(d, "Uchalasi ham bir xil `string` ni saqlaydi. Farq — xato qachon "
            "topilishida. Men esa xatoni imkon qadar erta topishni afzal "
            "ko'raman, shuning uchun tartib shunday: avval aniq tip yoki "
            "`var`, keyin `object` (va albatta pattern matching bilan), "
            "`dynamic` esa boshqa yo'l qolmaganda.")

    sources(d, [
        ("var — implicitly typed local variables",
         "https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/statements/declarations#implicitly-typed-local-variables"),
        ("dynamic type",
         "https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/builtin-types/reference-types#the-dynamic-type"),
        ("Boxing and unboxing",
         "https://learn.microsoft.com/en-us/dotnet/csharp/programming-guide/types/boxing-and-unboxing"),
    ])
