# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "Searching Algorithms (Binary search)"
CATEGORY = "Algorithms"
TITLE = "Qidiruv Algoritmlari va Binary Search"
SUBTITLE = "Saralangan ma'lumotda logarifmik qidiruv"
FILENAME = "Searching Algorithms (Binary search).docx"


def build(d):
    h1(d, "1. Chiziqli qidiruvdan boshlaymiz")

    para(d, "Eng oddiy qidiruv — boshidan oxirigacha yurib tekshirish:")

    code(d, """static int LinearSearch(int[] items, int target)
{
    for (var i = 0; i < items.Length; i++)
        if (items[i] == target) return i;
    return -1;
}""")

    para(d, "Bu usul har qanday ma'lumotda ishlaydi va saralash talab "
            "qilmaydi. Lekin murakkabligi **O(n)**: 1 000 000 elementda eng "
            "yomon holatda 1 000 000 taqqoslash kerak bo'ladi.")

    # ───────────────────────────────────────────
    h1(d, "2. Binary search g'oyasi")

    para(d, "Agar ma'lumot **saralangan** bo'lsa, har bir taqqoslashdan "
            "keyin qidiruv maydonining yarmini tashlab yuborish mumkin. "
            "O'rtadagi element izlanayotgandan katta bo'lsa, o'ng yarmini "
            "ko'rib o'tirish ma'nosiz.")

    para(d, "Lug'atdan so'z izlashga o'xshaydi: o'rtadan ochib, qaysi "
            "yarmida borligini aniqlaymiz va shu yarmini yana o'rtadan "
            "ochamiz.")

    code(d, """static int BinarySearch(int[] sorted, int target)
{
    var low = 0;
    var high = sorted.Length - 1;

    while (low <= high)
    {
        var mid = low + (high - low) / 2;

        if (sorted[mid] == target) return mid;

        if (sorted[mid] < target) low = mid + 1;
        else                      high = mid - 1;
    }

    return -1;
}""")

    h2(d, "Nega mid shunday hisoblanadi")

    para(d, "`(low + high) / 2` ko'rinishi tabiiyroq, lekin katta "
            "massivlarda `low + high` `int` chegarasidan oshib ketishi "
            "mumkin — natijada manfiy indeks va exception. "
            "`low + (high - low) / 2` esa hech qachon oshmaydi. Bu klassik "
            "xato va uni intervyuda ko'p so'raydilar.")

    # ───────────────────────────────────────────
    h1(d, "3. Murakkablik")

    para(d, "Har bir qadamda qidiruv maydoni ikki barobar kamayadi, shuning "
            "uchun murakkablik **O(log n)**.")

    table(d, ["Elementlar soni", "Chiziqli (eng yomon)", "Binary (eng yomon)"],
          [["100", "100", "7"],
           ["10 000", "10 000", "14"],
           ["1 000 000", "1 000 000", "20"],
           ["1 000 000 000", "1 000 000 000", "30"]],
          widths=[4.6, 5.0, 4.9])

    para(d, "Bu jadvaldagi farq amalda qanchalik katta ekanini ko'rsatadi: "
            "milliard elementda 30 ta taqqoslash yetadi. Shuning uchun "
            "baza indekslari ham shunga o'xshash tamoyilga qurilgan — "
            "B-tree ham qidiruv maydonini har qadamda keskin qisqartiradi.")

    note(d, "Muhim shart",
         "Binary search faqat **saralangan** ma'lumotda to'g'ri ishlaydi. "
         "Saralanmagan massivda u xato natija qaytaradi va bu xato jim "
         "bo'ladi — exception chiqmaydi, shunchaki `-1` yoki noto'g'ri "
         "indeks keladi.")

    # ───────────────────────────────────────────
    h1(d, "4. Saralash narxini hisobga olish")

    para(d, "Agar ma'lumot saralanmagan bo'lsa, avval saralash kerak — bu "
            "**O(n log n)**. Shuning uchun bitta qidiruv uchun saralash "
            "foyda bermaydi: chiziqli qidiruv arzonroq.")

    bullets(d, [
        "Bitta qidiruv — chiziqli qidiruv (O(n)) yaxshiroq.",
        "Ko'p marta qidiruv — bir marta saralab, keyin har qidiruvda "
        "O(log n). Bu tez orada o'zini oqlaydi.",
        "Juda ko'p qidiruv va xotira muammo bo'lmasa — `Dictionary` yoki "
        "`HashSet`, ya'ni O(1).",
    ])

    # ───────────────────────────────────────────
    h1(d, "5. .NET dagi tayyor imkoniyatlar")

    code(d, """var sorted = new[] { 1, 3, 5, 7, 9, 11 };

// massivda
var index = Array.BinarySearch(sorted, 7);        // 3

// List<T> da
var list = new List<int> { 1, 3, 5, 7 };
var i = list.BinarySearch(5);                     // 2

// Span ustida (eng tez, nusxa olmaydi)
var span = sorted.AsSpan();
var j = span.BinarySearch(9);""")

    h2(d, "Topilmagan holatning foydali xossasi")

    para(d, "`Array.BinarySearch` element topilmasa manfiy son qaytaradi va "
            "bu shunchaki \"yo'q\" degani emas — undan qiymatni qo'yish "
            "kerak bo'lgan joyni hisoblash mumkin:")

    code(d, """var result = Array.BinarySearch(sorted, 8);
if (result < 0)
{
    var insertAt = ~result;        // bitwise NOT — qo'yish o'rni
    Console.WriteLine($"8 ni {insertAt} indeksga qo'yish kerak");
}""")

    para(d, "Bu xossa saralangan ro'yxatga element qo'shish yoki eng yaqin "
            "qiymatni topishda qulay.")

    h2(d, "O'z taqqoslovchisi bilan")

    code(d, """var orders = ordersSortedByDate;    // CreatedAt bo'yicha saralangan

var index = orders.BinarySearch(
    new Order { CreatedAt = target },
    Comparer<Order>.Create((a, b) => a.CreatedAt.CompareTo(b.CreatedAt)));""")

    # ───────────────────────────────────────────
    h1(d, "6. Qidiruv usullarini taqqoslash")

    table(d, ["Usul", "Vaqt", "Shart"],
          [["Chiziqli qidiruv", "O(n)", "Hech qanday shart yo'q"],
           ["Binary search", "O(log n)", "Saralangan va indeks bo'yicha kirish"],
           ["`HashSet` / `Dictionary`", "O(1) o'rtacha", "Hash va tenglik aniqlangan"],
           ["Baza indeksi (B-tree)", "O(log n)", "Indeks yaratilgan"]],
          widths=[4.8, 3.2, 6.5])

    para(d, "Amalda backend ishida binary search'ni qo'lda yozish kamdan-kam "
            "kerak bo'ladi — `Dictionary` yoki baza indeksi ishni bajaradi. "
            "Lekin uni tushunish muhim, chunki aynan shu g'oya indekslar, "
            "versiyalar orasidagi xato qidirish (`git bisect`) va ko'p "
            "boshqa joyda ishlatiladi.")

    # ───────────────────────────────────────────
    h1(d, "7. Binary search'ning kengaytirilgan ishlatilishi")

    para(d, "Binary search faqat massivda qidirish uchun emas. Agar "
            "javob \"ha\" dan \"yo'q\" ga bir marta o'tadigan bo'lsa, "
            "javobni ham shu usulda topish mumkin.")

    code(d, """// Eng kichik hajm qaysi bo'lsa, hamma element sig'adi?
static int MinCapacity(int[] items, int limit)
{
    int low = items.Max(), high = items.Sum();

    while (low < high)
    {
        var mid = low + (high - low) / 2;
        if (Fits(items, mid, limit)) high = mid;
        else                         low = mid + 1;
    }

    return low;
}""")

    para(d, "Bu yerda massiv emas, **javob maydoni** bo'ylab qidiruv "
            "ketmoqda. Shart monoton bo'lsa — ya'ni bir qiymatda to'g'ri "
            "bo'lsa, undan kattalarida ham to'g'ri bo'lsa — usul ishlaydi.")

    note(d, "E'tibor",
         "Binary search yozishda eng ko'p uchraydigan xato — cheksiz tsikl. "
         "`low` va `high` ni yangilashda `mid` ni o'z ichiga olib qolsam "
         "(`low = mid` deb yozsam), tsikl aylanib qolishi mumkin. Shuning "
         "uchun har doim `mid + 1` yoki `mid - 1` bilan siljitaman.")

    sources(d, [
        ("Array.BinarySearch Method",
         "https://learn.microsoft.com/en-us/dotnet/api/system.array.binarysearch"),
        ("List<T>.BinarySearch Method",
         "https://learn.microsoft.com/en-us/dotnet/api/system.collections.generic.list-1.binarysearch"),
        ("MemoryExtensions.BinarySearch",
         "https://learn.microsoft.com/en-us/dotnet/api/system.memoryextensions.binarysearch"),
    ])
