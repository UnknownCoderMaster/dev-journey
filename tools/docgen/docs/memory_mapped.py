# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "Memory-Mapped Files"
CATEGORY = ".NET / C#"
TITLE = "Memory-Mapped Fayllar"
SUBTITLE = "Faylni xotira sifatida ko'rish va jarayonlar aro almashish"
FILENAME = "Memory-Mapped Files.docx"


def build(d):
    h1(d, "1. Tushunchaning mohiyati")

    para(d, "Odatiy fayl bilan ishlashda ma'lumot diskdan bufer orqali "
            "o'qiladi va nusxalanadi. Memory-mapped faylda esa fayl "
            "to'g'ridan-to'g'ri jarayonning virtual xotira fazosiga "
            "bog'lanadi.")

    para(d, "Natijada fayl bilan ishlash oddiy xotira bilan ishlashga "
            "aylanadi. Operatsion tizim kerakli sahifalarni avtomatik "
            "yuklaydi va o'zgarishlarni diskka yozadi.")

    code(d, """Odatiy o'qish:
    Disk → OT buferi → Ilova buferi → Ishlov

Memory-mapped:
    Disk → Virtual xotira → Ishlov""")

    note(d, "Asosiy foyda — nusxalashning yo'qligi:",
         "Katta faylni o'qiyotganimda har bir bayt kamida ikki marta "
         "nusxalanadi. Memory-mapped da esa nusxalash umuman "
         "bo'lmaydi — men xotiraga murojaat qilaman, OT esa kerakli "
         "sahifani diskdan o'zi keltiradi.")

    # ───────────────────────────────────────────
    h1(d, "2. Qachon ishlatiladi")

    table(d, ["Stsenariy", "Nima uchun"],
          [["Juda katta fayl", "Butun faylni xotiraga yuklamasdan ishlash"],
           ["Tasodifiy murojaat", "Fayl o'rtasiga tez o'tish"],
           ["Jarayonlar aro almashish", "Umumiy xotira sohasi"],
           ["Tez-tez o'qish", "OT sahifa keshidan foydalanish"]],
          widths=[4.6, 10.9])

    note(d, "Lekin u universal yechim emas:",
         "Ketma-ket o'qish uchun oddiy `FileStream` ko'pincha tezroq "
         "va ancha soddaroq. Memory-mapped ning afzalligi aynan "
         "tasodifiy murojaat va jarayonlar aro almashishda ko'rinadi. "
         "Shuning uchun men uni \"katta fayl\" degani uchun emas, "
         "aniq ehtiyoj bo'lganda ishlataman.")

    # ───────────────────────────────────────────
    h1(d, "3. Fayldan bog'lash")

    code(d, """using System.IO.MemoryMappedFiles;

using var mmf = MemoryMappedFile.CreateFromFile(
    path: "large-data.bin",
    mode: FileMode.Open,
    mapName: null,
    capacity: 0,                     // fayl hajmi
    access: MemoryMappedFileAccess.Read);

using var accessor = mmf.CreateViewAccessor(
    offset: 0,
    size: 0,
    access: MemoryMappedFileAccess.Read);

// Ixtiyoriy pozitsiyadan o'qish
var value = accessor.ReadInt64(1_000_000);""")

    h2(d, "3.1 Qismiy ko'rinish")

    para(d, "Katta faylning faqat kerakli qismini bog'lash mumkin — bu "
            "virtual manzil fazosini tejaydi:")

    code(d, """const long windowSize = 64 * 1024 * 1024;   // 64 MB

using var mmf = MemoryMappedFile.CreateFromFile(path, FileMode.Open);

for (long offset = 0; offset < fileLength; offset += windowSize)
{
    var size = Math.Min(windowSize, fileLength - offset);

    using var accessor = mmf.CreateViewAccessor(
        offset, size, MemoryMappedFileAccess.Read);

    ProcessWindow(accessor, size);
}""")

    note(d, "32 bitli jarayonda bu majburiy:",
         "32 bit da virtual manzil fazosi 2 GB bilan cheklangan, "
         "shuning uchun 4 GB li faylni to'liq bog'lab bo'lmaydi. "
         "64 bit da bunday muammo yo'q, lekin oynali yondashuv "
         "baribir xotira bosimini kamaytiradi.")

    # ───────────────────────────────────────────
    h1(d, "4. Tez o'qish — ViewStream")

    code(d, """using var mmf = MemoryMappedFile.CreateFromFile(path, FileMode.Open);
using var stream = mmf.CreateViewStream(0, 0, MemoryMappedFileAccess.Read);

using var reader = new BinaryReader(stream);

while (stream.Position < stream.Length)
{
    var id = reader.ReadInt32();
    var timestamp = reader.ReadInt64();
    var value = reader.ReadDouble();

    Process(id, timestamp, value);
}""")

    para(d, "`ViewStream` odatiy `Stream` interfeysini beradi, shuning "
            "uchun mavjud kod bilan ishlaydi.")

    # ───────────────────────────────────────────
    h1(d, "5. Jarayonlar aro almashish")

    para(d, "Diskdagi faylsiz, faqat xotirada mavjud bo'lgan nomlangan "
            "soha yaratish mumkin. Uni bir nechta jarayon ochib, umumiy "
            "ma'lumot bilan ishlashi mumkin.")

    code(d, """// Birinchi jarayon — yaratuvchi
using var mmf = MemoryMappedFile.CreateNew(
    mapName: "MyApp.SharedCounter",
    capacity: 1024);

using var accessor = mmf.CreateViewAccessor();

accessor.Write(0, 42L);
Console.WriteLine("Qiymat yozildi, boshqa jarayon o'qishi mumkin");
Console.ReadLine();     // soha jarayon yashaguncha mavjud""")

    code(d, """// Ikkinchi jarayon — o'quvchi
using var mmf = MemoryMappedFile.OpenExisting("MyApp.SharedCounter");
using var accessor = mmf.CreateViewAccessor();

var value = accessor.ReadInt64(0);
Console.WriteLine($"O'qildi: {value}");""")

    note(d, "Nomlangan soha faqat Windows da to'liq ishlaydi:",
         "Linux va macOS da `CreateNew` nomlangan soha yaratish "
         "qo'llab-quvvatlanmaydi — `PlatformNotSupportedException` "
         "chiqadi. Kross-platforma yechim kerak bo'lsa, diskdagi "
         "faylga asoslangan variant ishlatiladi.")

    code(d, """// Kross-platforma — vaqtinchalik faylga asoslangan
var sharedPath = Path.Combine(Path.GetTempPath(), "myapp-shared.dat");

using var mmf = MemoryMappedFile.CreateFromFile(
    sharedPath, FileMode.OpenOrCreate, null, 1024);""")

    # ───────────────────────────────────────────
    h1(d, "6. Sinxronlash")

    note(d, "Umumiy xotira sinxronlashni o'zi ta'minlamaydi:",
         "Ikki jarayon bir vaqtda bir joyga yozsa, natija "
         "aniqlanmagan bo'ladi. Bu oddiy ko'p oqimli kodga "
         "o'xshash muammo, lekin `lock` bu yerda ishlamaydi — u "
         "faqat bitta jarayon ichida amal qiladi.")

    code(d, """// Jarayonlar aro qulf — nomlangan Mutex
using var mutex = new Mutex(false, "Global\\\\MyApp.SharedData");

if (mutex.WaitOne(TimeSpan.FromSeconds(5)))
{
    try
    {
        var current = accessor.ReadInt64(0);
        accessor.Write(0, current + 1);
    }
    finally
    {
        mutex.ReleaseMutex();
    }
}""")

    code(d, """// Atomar amallar uchun — Interlocked
unsafe
{
    byte* pointer = null;
    accessor.SafeMemoryMappedViewHandle
        .AcquirePointer(ref pointer);

    try
    {
        Interlocked.Increment(ref *(long*)pointer);
    }
    finally
    {
        accessor.SafeMemoryMappedViewHandle.ReleasePointer();
    }
}""")

    note(d, "`unsafe` kodga o'tish haqida:",
         "Bu loyihada `AllowUnsafeBlocks` yoqilishini talab qiladi va "
         "xatolikka yo'l qo'yish osonlashadi. Men unga faqat "
         "unumdorlik haqiqatan kritik bo'lganda va o'lchov buni "
         "tasdiqlaganda o'taman.")

    # ───────────────────────────────────────────
    h1(d, "7. Diskka yozish")

    code(d, """using var mmf = MemoryMappedFile.CreateFromFile(
    path, FileMode.OpenOrCreate, null, 1024 * 1024);

using var accessor = mmf.CreateViewAccessor();

accessor.Write(0, 12345L);

// O'zgarishlarni diskka majburlash
accessor.Flush();""")

    note(d, "`Flush` ni chaqirmasam ham ma'lumot yo'qolmaydi:",
         "Operatsion tizim sahifalarni o'zi yozadi. Lekin bu qachon "
         "sodir bo'lishi kafolatlanmaydi — server to'satdan o'chsa, "
         "oxirgi o'zgarishlar yo'qolishi mumkin. Muhim ma'lumotda "
         "`Flush` ni aniq chaqirish kerak.")

    # ───────────────────────────────────────────
    h1(d, "8. Amaliy misol — katta log faylini qidirish")

    code(d, """public static long FindPattern(string path, byte[] pattern)
{
    using var mmf = MemoryMappedFile.CreateFromFile(
        path, FileMode.Open, null, 0, MemoryMappedFileAccess.Read);

    var length = new FileInfo(path).Length;
    const long chunkSize = 16 * 1024 * 1024;

    for (long offset = 0; offset < length; offset += chunkSize - pattern.Length)
    {
        var size = Math.Min(chunkSize, length - offset);

        using var accessor = mmf.CreateViewAccessor(
            offset, size, MemoryMappedFileAccess.Read);

        var buffer = new byte[size];
        accessor.ReadArray(0, buffer, 0, (int)size);

        var index = buffer.AsSpan().IndexOf(pattern);
        if (index >= 0)
            return offset + index;
    }

    return -1;
}""")

    note(d, "Bo'laklar chegarasiga e'tibor berish kerak:",
         "Qidirilayotgan naqsh ikki bo'lak chegarasida joylashgan "
         "bo'lishi mumkin. Shuning uchun keyingi bo'lak oldingisining "
         "oxiridan `pattern.Length` bayt oldin boshlanadi — kodda "
         "`chunkSize - pattern.Length` aynan shu uchun.")

    # ───────────────────────────────────────────
    h1(d, "9. Cheklovlar va xavflar")

    bullets(d, [
        "Bog'langan faylni boshqa jarayon o'chira olmaydi yoki "
        "o'zgartira olmaydi.",
        "Fayl hajmi bog'langandan keyin o'zgartirilmaydi.",
        "Nomlangan sohalar Linux va macOS da qo'llab-quvvatlanmaydi.",
        "Sahifa xatosi (page fault) kutilmagan kechikish berishi "
        "mumkin.",
        "Diskdagi fayl o'chirilsa, murojaat `IOException` beradi.",
        "32 bitli jarayonda manzil fazosi cheklangan.",
    ])

    note(d, "Eng muhim maslahat:",
         "Memory-mapped fayl — maxsus vosita. Agar men faylni ketma-ket "
         "o'qib, qayta ishlayotgan bo'lsam, `FileStream` yoki "
         "`PipeReader` ancha sodda va ko'pincha tezroq. Uni "
         "tanlashdan oldin o'zimdan so'rayman: menga haqiqatan "
         "tasodifiy murojaat yoki umumiy xotira kerakmi?")

    # ───────────────────────────────────────────
    h1(d, "10. Xulosa")

    bullets(d, [
        "Memory-mapped fayl diskdagi faylni virtual xotiraga "
        "bog'laydi va nusxalashni yo'qotadi.",
        "`CreateViewAccessor` tasodifiy murojaat, `CreateViewStream` "
        "oqim interfeysini beradi.",
        "Katta fayllarda qismiy ko'rinish — oyna yondashuvi "
        "ishlatiladi.",
        "`CreateNew` nomlangan soha yaratadi, lekin faqat Windows "
        "da ishlaydi.",
        "Jarayonlar aro sinxronlash uchun nomlangan `Mutex` kerak — "
        "`lock` yetarli emas.",
        "`Flush` o'zgarishlarni diskka majburlaydi.",
        "Bo'laklab qidirishda naqsh uzunligi hisobga olinishi kerak.",
        "Ketma-ket o'qish uchun oddiy `FileStream` soddaroq va "
        "ko'pincha tezroq.",
    ])

    sources(d, [
        ("Memory-Mapped Files — .NET",
         "https://learn.microsoft.com/en-us/dotnet/standard/io/memory-mapped-files"),
        ("MemoryMappedFile Class — .NET API",
         "https://learn.microsoft.com/en-us/dotnet/api/system.io.memorymappedfiles.memorymappedfile"),
        ("File and stream I/O — .NET",
         "https://learn.microsoft.com/en-us/dotnet/standard/io/"),
    ])
