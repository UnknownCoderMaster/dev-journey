# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "Client vs. Server Evaluation"
CATEGORY = "EF Core"
TITLE = "Client va Server Tomonida Hisoblash"
SUBTITLE = "So'rovning qaysi qismi bazada, qaysi qismi ilovada bajariladi"
FILENAME = "Client vs. Server Evaluation.docx"


def build(d):
    h1(d, "1. Tushunchaning mohiyati")

    para(d, "LINQ so'rovi yozilganda uning ayrim qismlari SQL ga tarjima qilinib bazada "
            "bajariladi, ayrim qismlari esa natija olingandan keyin ilova xotirasida "
            "hisoblanadi. Birinchisi server-side evaluation, ikkinchisi client-side "
            "evaluation deb ataladi.")

    para(d, "Chegara qayerdan o'tishi muhim, chunki u uzatiladigan ma'lumot hajmini va "
            "so'rov tezligini belgilaydi. Bazada bajarilgan filtr ortiqcha satrlarni "
            "umuman jo'natmaydi; ilovada bajarilgan filtr esa avval hamma narsani "
            "tortib olib, keyin ortiqchasini tashlab yuboradi.")

    note(d, "Bu mavzu nega men uchun muhim bo'ldi:",
         "Bir so'rovim juda sekin ishlayotgan edi va men indeks qo'shish bilan ovora "
         "bo'ldim. Keyin loglarni yoqib ko'rsam, generatsiya qilingan SQL da `WHERE` "
         "umuman yo'q ekan — EF Core mening shartimni tarjima qila olmagan va butun "
         "jadvalni o'qib, keyin C# da filtrlagan. Indeks bunday holatda hech narsani "
         "o'zgartirmaydi, chunki baza baribir hamma satrni qaytaryapti.")

    # ───────────────────────────────────────────
    h1(d, "2. Oddiy misol")

    code(d, """// Server tomonida — SQL ga tarjima bo'ladi
var a = await db.Orders
    .Where(o => o.Total > 100_000)
    .ToListAsync();
// SELECT ... FROM "Orders" WHERE "Total" > 100000""")

    code(d, """// Client tomonida — SQL ga tarjima bo'lmaydi
var b = await db.Orders
    .ToListAsync();
var filtered = b.Where(o => IsSuspicious(o)).ToList();
// SELECT ... FROM "Orders"        — butun jadval o'qiladi""")

    para(d, "Ikkinchi holatda `IsSuspicious` — oddiy C# metodi. EF Core uning ichida nima "
            "borligini bilmaydi va uni SQL ga aylantira olmaydi, shuning uchun hisoblash "
            "ilovaga qoladi.")

    # ───────────────────────────────────────────
    h1(d, "3. EF Core 3.0 dagi muhim o'zgarish")

    para(d, "EF Core 2.x versiyalarida tarjima qilib bo'lmaydigan shart uchrasa, so'rov "
            "jimgina ikkiga bo'linardi: bazadan hamma narsa olinib, qolgan qismi ilovada "
            "bajarilardi. Faqat ogohlantirish logi chiqarilardi.")

    para(d, "Bu xatti-harakat juda ko'p unumdorlik muammosiga sabab bo'lgani uchun "
            "EF Core 3.0 da o'zgartirildi. Endi `Where`, `OrderBy`, `Join` va shunga "
            "o'xshash operatorlar ichidagi ifoda tarjima qilinmasa, EF Core **xatolik "
            "beradi**:")

    code(d, """InvalidOperationException: The LINQ expression
'DbSet<Order>().Where(o => IsSuspicious(o))'
could not be translated. Either rewrite the query in a form that can be
translated, or switch to client evaluation explicitly by inserting a call
to 'AsEnumerable', 'AsAsyncEnumerable', 'ToList', or 'ToListAsync'.""")

    note(d, "Bu o'zgarish menga ma'qul:",
         "Avvalgi xatti-harakat xavfli edi — kod ishlardi, testlar o'tardi, muammo "
         "faqat ma'lumot ko'payganda, ya'ni production da ko'rinardi. Hozirgi usulda "
         "esa men xatoni darhol, kodni yozayotgan paytda ko'raman va ongli qaror "
         "qabul qilaman.")

    h2(d, "3.1 Istisno: yakuniy proyeksiya")

    para(d, "Xatolik faqat filtrlash va saralash operatorlariga tegishli. Eng oxirgi "
            "`Select` ichida esa client-side hisoblash hamon ruxsat etiladi:")

    code(d, """var result = await db.Orders
    .Where(o => o.Total > 100_000)          // bazada
    .Select(o => new
    {
        o.Id,
        Label = FormatLabel(o.Total)        // ilovada — ruxsat
    })
    .ToListAsync();""")

    para(d, "Bu mantiqiy: filtrlash qancha satr uzatilishini belgilaydi, proyeksiyadagi "
            "formatlash esa allaqachon olingan satrlar ustida ishlaydi va qo'shimcha "
            "yuk tug'dirmaydi.")

    # ───────────────────────────────────────────
    h1(d, "4. Nimalar tarjima qilinmaydi")

    bullets(d, [
        "O'z yozgan metodlarim — `IsSuspicious(o)`, `o.GetDisplayName()`.",
        "Hisoblangan xossalar — `public string Full => First + \" \" + Last;`",
        "`string` ning ayrim metodlari, masalan `Split`, `Normalize`.",
        "Value converter qo'yilgan ustun ustida murakkab shart.",
        "`DateTime` ning ba'zi formatlash metodlari.",
        "Provayder qo'llab-quvvatlamaydigan funksiyalar — har bir baza uchun ro'yxat "
        "farq qiladi.",
    ])

    note(d, "Hisoblangan xossalar meni bir necha marta chalg'itgan:",
         "`FullName => FirstName + \" \" + LastName` degan xossa kodda juda tabiiy "
         "ko'rinadi, lekin `Where(u => u.FullName.Contains(\"Ali\"))` deb yozsam, "
         "EF Core uni tarjima qila olmaydi. Chunki bu xossa bazada ustun emas — u "
         "faqat C# da mavjud. Yechim ikkita: yo shartni ustunlar orqali qayta yozaman, "
         "yo bazada hisoblangan ustun yarataman.")

    # ───────────────────────────────────────────
    h1(d, "5. Yechimlar")

    h2(d, "5.1 Shartni ustunlar orqali qayta yozish")

    code(d, """// Ishlamaydi
.Where(u => u.FullName.Contains(term))

// Ishlaydi
.Where(u => (u.FirstName + " " + u.LastName).Contains(term))""")

    h2(d, "5.2 Bazada hisoblangan ustun")

    code(d, """modelBuilder.Entity<User>()
    .Property(u => u.FullName)
    .HasComputedColumnSql("\\"FirstName\\" || ' ' || \\"LastName\\"", stored: true);""")

    para(d, "Endi `FullName` bazada haqiqiy ustun bo'ladi, unga indeks ham qo'yish "
            "mumkin va so'rovda bemalol ishlatiladi.")

    h2(d, "5.3 Client evaluation ni ongli ravishda yoqish")

    code(d, """var result = await db.Orders
    .Where(o => o.CreatedAt >= from)   // bazada — avval qisqartiramiz
    .AsEnumerable()                    // shu nuqtadan keyin ilovada
    .Where(o => IsSuspicious(o))
    .ToList();""")

    para(d, "Muhim qoida — `AsEnumerable()` dan oldin iloji boricha ko'proq filtr "
            "qo'yish. Shunda ilovaga kichik to'plam keladi va client-side hisoblash "
            "arzon bo'ladi.")

    h2(d, "5.4 Provayder funksiyalaridan foydalanish")

    code(d, """// PostgreSQL ning ILIKE operatori
.Where(u => EF.Functions.ILike(u.Email, "%@gmail.com"))

// Sana farqi
.Where(o => EF.Functions.DateDiffDay(o.CreatedAt, now) < 7)""")

    para(d, "`EF.Functions` orqali chaqirilgan metodlar faqat so'rov ichida ishlaydi — "
            "ularni oddiy C# kodida chaqirib bo'lmaydi, chunki ular SQL ga tarjima "
            "qilish uchun belgi vazifasini bajaradi.")

    h2(d, "5.5 O'z funksiyamni bazaga bog'lash")

    para(d, "Agar bazada saqlangan funksiya bo'lsa, uni EF Core ga tanishtirish mumkin:")

    code(d, """[DbFunction("calculate_discount", "public")]
public static decimal CalculateDiscount(int customerId, decimal total)
    => throw new NotSupportedException();   // faqat so'rov ichida ishlaydi

// Endi so'rovda ishlatsa bo'ladi
var discounted = await db.Orders
    .Where(o => AppDbContext.CalculateDiscount(o.CustomerId, o.Total) > 0)
    .ToListAsync();""")

    # ───────────────────────────────────────────
    h1(d, "6. Yashirin client evaluation ni aniqlash")

    para(d, "Eng ishonchli usul — generatsiya qilingan SQL ni ko'rish:")

    code(d, """var query = db.Orders.Where(o => o.Total > 100_000);
Console.WriteLine(query.ToQueryString());""")

    para(d, "Agar kutilgan `WHERE` sharti SQL da yo'q bo'lsa, demak u ilovada "
            "bajarilyapti. Loglarni yoqib, so'rov natijasida nechta satr qaytganini "
            "kuzatish ham yaxshi belgi beradi.")

    para(d, "Qo'shimcha himoya sifatida ogohlantirishni xatolikka aylantirish mumkin:")

    code(d, """options.ConfigureWarnings(w =>
    w.Throw(RelationalEventId.MultipleCollectionIncludeWarning));""")

    # ───────────────────────────────────────────
    h1(d, "7. Xulosa")

    bullets(d, [
        "Server-side hisoblash bazada, client-side hisoblash ilova xotirasida "
        "bajariladi.",
        "EF Core 3.0 dan boshlab `Where` va `OrderBy` ichidagi tarjima qilinmaydigan "
        "ifoda xatolik beradi — avvalgi jimgina sekinlashish o'rniga.",
        "Eng oxirgi `Select` ichida client-side hisoblash ruxsat etiladi.",
        "Hisoblangan xossalar va o'z metodlarim tarjima qilinmaydi — bu eng ko'p "
        "uchraydigan sabab.",
        "`AsEnumerable()` chegarani ongli belgilaydi; undan oldin iloji boricha "
        "ko'proq filtrlash kerak.",
        "`EF.Functions`, hisoblangan ustun va `DbFunction` — shartni bazaga "
        "qaytarishning asosiy vositalari.",
    ])

    sources(d, [
        ("Client vs. Server Evaluation — EF Core",
         "https://learn.microsoft.com/en-us/ef/core/querying/client-eval"),
        ("Breaking changes in EF Core 3.0 — LINQ queries",
         "https://learn.microsoft.com/en-us/ef/core/what-is-new/ef-core-3.x/breaking-changes#linq-queries-are-no-longer-evaluated-on-the-client"),
        ("Database functions — EF Core",
         "https://learn.microsoft.com/en-us/ef/core/querying/user-defined-function-mapping"),
    ])
