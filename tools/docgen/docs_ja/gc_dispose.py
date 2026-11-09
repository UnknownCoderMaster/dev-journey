# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "GC , using , Dispose, Finalize"
CATEGORY = ".NET / C#"
TITLE = "Garbage Collector, using, Dispose va Finalize"
SUBTITLE = "Xotira va resurslarni boshqarish"
FILENAME = "GC, using, Dispose, Finalize.docx"


def build(d):
    h1(d, "1. Garbage Collector nima qiladi")

    para(d, ".NET da obyektlar managed heap da yaratiladi va ularni "
            "o'chirishni Garbage Collector bajaradi. Men obyektni qo'lda "
            "o'chirmayman — GC obyektga boshqa hech qanday havola "
            "qolmaganini aniqlaydi va xotirani bo'shatadi.")

    para(d, "GC ishlash tartibi ikki bosqichdan iborat. Avval **mark** "
            "bosqichi: ildiz havolalardan (stack, statik maydonlar, CPU "
            "registrlari) boshlab yurib, yetib boriladigan hamma obyekt "
            "belgilanadi. Keyin **sweep** bosqichi: belgilanmagan obyektlar "
            "xotirasi bo'shatiladi va tirik obyektlar zichlashtiriladi.")

    h2(d, "Generatsiyalar")

    para(d, "Heap uch generatsiyaga bo'linadi va bu bo'linish samaradorlik "
            "uchun qilingan — yangi obyektlarning aksariyati tez o'ladi, "
            "shuning uchun ularni tez-tez tekshirish arzon.")

    bullets(d, [
        "**Gen 0** — yangi yaratilgan kichik obyektlar. Tez-tez va tez "
        "yig'iladi.",
        "**Gen 1** — Gen 0 dan omon qolganlar. Bufer rolini bajaradi.",
        "**Gen 2** — uzoq yashayotgan obyektlar. Kamdan-kam, lekin qimmat "
        "yig'iladi.",
        "**LOH** (Large Object Heap) — 85 000 baytdan katta obyektlar. "
        "Zichlashtirilmaydi, shuning uchun fragmentatsiyaga moyil.",
    ])

    note(d, "Eslatma",
         "GC xotirani boshqaradi, lekin fayl deskriptori, tarmoq soketi yoki "
         "baza ulanishini boshqarmaydi. Bu resurslar managed emas va ularni "
         "o'z vaqtida yopish mening vazifam.")

    # ───────────────────────────────────────────
    h1(d, "2. IDisposable va Dispose")

    para(d, "Managed bo'lmagan resursni egallagan klass `IDisposable` ni "
            "amalga oshiradi. `Dispose()` — bu \"resursni hoziroq bo'shat\" "
            "degan aniq buyruq:")

    code(d, """public sealed class ReportWriter : IDisposable
{
    private readonly FileStream _stream;
    private bool _disposed;

    public ReportWriter(string path) => _stream = File.Create(path);

    public void Write(string line) { /* ... */ }

    public void Dispose()
    {
        if (_disposed) return;
        _stream.Dispose();
        _disposed = true;
    }
}""")

    para(d, "`_disposed` bayrog'i muhim: `Dispose()` bir necha marta "
            "chaqirilishi mumkin va ikkinchi chaqiruv xato bermasligi kerak. "
            "Bu `IDisposable` shartnomasining qismi.")

    # ───────────────────────────────────────────
    h1(d, "3. using — Dispose ni kafolatlash")

    para(d, "`Dispose()` ni qo'lda chaqirish ishonchsiz: metod o'rtasida "
            "exception chiqsa, chaqiruvga yetib bormaydi. `using` aynan shu "
            "muammoni yechadi — u `try/finally` ga aylanadi:")

    code(d, """// Shu kod...
using (var writer = new ReportWriter(path))
{
    writer.Write("salom");
}

// ...kompilyatordan keyin shunga teng
var writer = new ReportWriter(path);
try
{
    writer.Write("salom");
}
finally
{
    writer?.Dispose();
}""")

    para(d, "C# 8 dan boshlab qavssiz shakl ham bor — obyekt o'zi turgan blok "
            "oxirida `Dispose` qilinadi:")

    code(d, """public async Task<string> ReadAsync(string path)
{
    using var reader = new StreamReader(path);
    return await reader.ReadToEndAsync();
}   // reader shu yerda Dispose qilinadi""")

    para(d, "Asinxron resurslar uchun `IAsyncDisposable` va `await using` "
            "ishlatiladi. Bu ayniqsa tarmoq va baza ulanishlarida muhim, "
            "chunki yopish operatsiyasi ham I/O talab qiladi:")

    code(d, """await using var connection = new NpgsqlConnection(connectionString);
await connection.OpenAsync(ct);""")

    # ───────────────────────────────────────────
    h1(d, "4. Finalizer va nega undan qochish kerak")

    para(d, "Finalizer (`~ClassName`) — GC obyektni yig'ishdan oldin "
            "chaqiradigan metod. U managed bo'lmagan resursni bo'shatishning "
            "**oxirgi chora** mexanizmi: agar kimdir `Dispose()` ni "
            "chaqirishni unutsa, resurs baribir bo'shatiladi.")

    code(d, """~ReportWriter()
{
    // faqat managed bo'lmagan resursni bo'shatish mumkin
}""")

    para(d, "Lekin finalizer qimmat va men undan deyarli har doim qochaman. "
            "Sabablari:")

    bullets(d, [
        "Finalizer'i bor obyekt darhol yig'ilmaydi — u alohida navbatga "
        "tushadi va kamida bitta qo'shimcha GC siklini kutadi.",
        "Finalizer alohida thread'da ishlaydi va qachon ishlashi "
        "kafolatlanmagan. Ilova yopilganda umuman ishlamasligi mumkin.",
        "Finalizer ichidagi xato jarayonni qulatadi.",
        "Finalizer ichida boshqa managed obyektga murojaat qilish xavfli — "
        "u allaqachon yig'ilgan bo'lishi mumkin.",
    ])

    para(d, "Amalda managed bo'lmagan resursni to'g'ridan-to'g'ri (`IntPtr` "
            "bilan) boshqarmasam, finalizer yozishga ehtiyoj qolmaydi — "
            "`SafeHandle` yoki `FileStream` kabi tayyor turlar buni "
            "o'zi hal qilgan.")

    # ───────────────────────────────────────────
    h1(d, "5. To'liq Dispose naqshi")

    para(d, "Agar klass ham managed, ham managed bo'lmagan resursga ega "
            "bo'lsa va meros olinishi kutilsa, standart naqsh shunday "
            "ko'rinadi:")

    code(d, """public class NativeBuffer : IDisposable
{
    private IntPtr _handle;        // managed bo'lmagan
    private FileStream? _log;      // managed
    private bool _disposed;

    public void Dispose()
    {
        Dispose(true);
        GC.SuppressFinalize(this);
    }

    protected virtual void Dispose(bool disposing)
    {
        if (_disposed) return;

        if (disposing)
        {
            _log?.Dispose();       // managed resurslar
        }

        if (_handle != IntPtr.Zero)
        {
            Native.Free(_handle);  // managed bo'lmagan resurs
            _handle = IntPtr.Zero;
        }

        _disposed = true;
    }

    ~NativeBuffer() => Dispose(false);
}""")

    para(d, "Ikki detalga e'tibor beraman. `GC.SuppressFinalize(this)` — "
            "`Dispose()` allaqachon ishni bajargani uchun finalizer'ni "
            "ro'yxatdan chiqaradi va qo'shimcha GC siklini oldini oladi. "
            "`disposing` parametri esa chaqiruv manbasini ajratadi: "
            "finalizer'dan kelganda managed obyektlarga tegmaslik kerak.")

    note(d, "Amaliy xulosa",
         "Bu to'liq naqsh kamdan-kam kerak bo'ladi. Oddiy holatda — faqat "
         "managed `IDisposable` maydonlar bo'lsa — klassni `sealed` qilib, "
         "oddiy `Dispose()` yozish yetarli.")

    # ───────────────────────────────────────────
    h1(d, "6. Ko'p uchraydigan xatolar")

    h2(d, "Dispose qilinmagan ulanish")

    para(d, "Yuklama ostida bu eng tez sezilarli muammo: ulanishlar pool'dan "
            "olinadi, lekin qaytarilmaydi. Natijada `Timeout expired` xatosi "
            "chiqadi — va u xatoni keltirib chiqargan kodga aloqasi "
            "yo'q joyda chiqadi, shuning uchun topish qiyin.")

    h2(d, "HttpClient ni using bilan o'rash")

    code(d, """// XATO: har so'rovda yangi HttpClient
using var client = new HttpClient();
var json = await client.GetStringAsync(url);""")

    para(d, "`HttpClient` `IDisposable` ni amalga oshirgani uchun uni `using` "
            "bilan o'rash mantiqiy ko'rinadi, lekin bu soketlar tugashiga olib "
            "keladi: `Dispose` dan keyin ham soket `TIME_WAIT` holatida bir "
            "necha daqiqa qoladi. To'g'ri yechim — `IHttpClientFactory`.")

    h2(d, "Katta obyektlarni keraksiz ushlab turish")

    para(d, "Statik kolleksiyaga obyekt qo'shib, uni hech qachon "
            "o'chirmaslik — managed tilda ham xotira oqishi. GC havola "
            "bor obyektni yig'maydi, shuning uchun \"xotira oqmaydi\" degan "
            "fikr noto'g'ri; oqadi, faqat boshqa sababdan.")

    h2(d, "GC.Collect() ni qo'lda chaqirish")

    para(d, "Buni deyarli har doim xato deb bilaman. GC o'z heuristikasiga "
            "ko'ra ishlaydi va qo'lda chaqiruv uni buzadi: Gen 2 yig'ilishi "
            "majburlanadi, bu esa eng qimmat operatsiya. Agar xotira "
            "muammosi bo'lsa, sababi odatda ushlab turilgan havolada, GC "
            "ning kamligida emas.")

    sources(d, [
        ("Fundamentals of garbage collection",
         "https://learn.microsoft.com/en-us/dotnet/standard/garbage-collection/fundamentals"),
        ("Implement a Dispose method",
         "https://learn.microsoft.com/en-us/dotnet/standard/garbage-collection/implementing-dispose"),
        ("using statement — C# reference",
         "https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/statements/using"),
        ("Cleaning up unmanaged resources",
         "https://learn.microsoft.com/en-us/dotnet/standard/garbage-collection/unmanaged"),
    ])
