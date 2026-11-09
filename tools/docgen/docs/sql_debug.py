# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "So'rovdagi sql query ni EF orqali ko'rish (Debug)"
CATEGORY = "EF Core"
TITLE = "EF Core Generatsiya Qilgan SQL ni Ko'rish"
SUBTITLE = "LINQ so'rovi qanday SQL ga aylanganini aniqlash usullari"
FILENAME = "So'rovdagi sql query ni EF orqali ko'rish (Debug).docx"


def build(d):
    h1(d, "1. Nima uchun kerak")

    para(d, "Entity Framework Core LINQ so'rovlarini SQL ga tarjima qiladi. Bu tarjima "
            "jarayoni dasturchidan yashirin kechadi, ya'ni bir xil ko'rinishdagi ikkita "
            "LINQ ifodasi butunlay boshqacha SQL hosil qilishi mumkin.")

    para(d, "Shu sababli unumdorlik bilan bog'liq har qanday tahlil generatsiya qilingan "
            "SQL ni ko'rishdan boshlanadi. Kod darajasida qilingan taxminlar ko'pincha "
            "haqiqatga mos kelmaydi.")

    note(d, "Mening tajribamdan:",
         "Bu mavzuni alohida o'rganishning ma'nosi shunda — SQL ni ko'rmaguningizcha "
         "siz EF Core bilan emas, uning haqidagi tasavvuringiz bilan ishlagan bo'lasiz. "
         "Bir marta loglarni yoqib ko'rsangiz, oddiy deb o'ylagan so'rovlaringiz "
         "aslida nima qilayotganini ko'rib hayron qolasiz.")

    # ───────────────────────────────────────────
    h1(d, "2. ToQueryString — eng tez usul")

    para(d, "EF Core 5 versiyasidan boshlab `ToQueryString()` kengaytma metodi mavjud. "
            "U so'rovni bajarmasdan, faqat SQL matnini qaytaradi.")

    code(d, """var query = db.Books
    .Where(b => b.Price > 50_000)
    .OrderBy(b => b.Title);

Console.WriteLine(query.ToQueryString());""")

    para(d, "Natija:")

    code(d, """SELECT b."Id", b."Title", b."Price", b."AuthorId"
FROM "Books" AS b
WHERE b."Price" > 50000.0
ORDER BY b."Title\"""")

    para(d, "Metod faqat `IQueryable` ustida ishlaydi. `ToList()` yoki `First()` "
            "chaqirilgandan keyin natija oddiy kolleksiyaga aylanadi va `ToQueryString()` "
            "endi mavjud bo'lmaydi.")

    note(d, "Eng qulay tomoni:",
         "Bu usul bazaga umuman murojaat qilmaydi. Ya'ni so'rov og'ir bo'lsa ham, uni "
         "bajarmasdan turib SQL ni ko'rish mumkin. Og'ir hisobot so'rovlarini tahlil "
         "qilishda juda asqotadi.")

    # ───────────────────────────────────────────
    h1(d, "3. Loglarni yoqish")

    para(d, "Barcha so'rovlarni avtomatik kuzatish uchun kontekst sozlamalarida log "
            "chiqarish yoqiladi.")

    code(d, """services.AddDbContext<AppDbContext>(options =>
{
    options.UseNpgsql(connectionString);

    if (environment.IsDevelopment())
    {
        options.LogTo(Console.WriteLine, LogLevel.Information)
               .EnableSensitiveDataLogging()
               .EnableDetailedErrors();
    }
});""")

    table(d, ["Sozlama", "Vazifasi"],
          [["`LogTo`", "Log xabarlarini ko'rsatilgan joyga yo'naltiradi"],
           ["`EnableSensitiveDataLogging`", "So'rov parametrlarining qiymatlarini ham chiqaradi"],
           ["`EnableDetailedErrors`", "Xatolik xabarlarini batafsilroq qiladi"]],
          widths=[5.5, 10.0])

    note(d, "Buni albatta e'tiborga oling:",
         "`EnableSensitiveDataLogging()` so'rovga uzatilgan barcha qiymatlarni logga "
         "yozadi — foydalanuvchi email i, telefon raqami, parol hashi, hamma narsa. "
         "Shuning uchun u yuqoridagi kabi `IsDevelopment()` sharti ichida turishi shart. "
         "Bu sozlama production ga chiqib ketsa, loglar shaxsiy ma'lumotlar omboriga aylanadi.")

    h2(d, "3.1 Faqat SQL ni ko'rsatish")

    para(d, "Default holda EF Core ancha ko'p xabar chiqaradi — tranzaksiya, ulanish, "
            "kontekst ishga tushishi va boshqalar. Faqat SQL so'rovlarini ajratib olish "
            "uchun kategoriya bo'yicha filtrlash mumkin:")

    code(d, """options.LogTo(
    Console.WriteLine,
    new[] { DbLoggerCategory.Database.Command.Name },
    LogLevel.Information);""")

    h2(d, "3.2 Faylga yozish")

    code(d, """var logStream = new StreamWriter("ef-queries.log", append: true);

options.LogTo(logStream.WriteLine,
              new[] { DbLoggerCategory.Database.Command.Name },
              LogLevel.Information);

// Kontekst yo'q qilinganda oqimni ham yopish kerak
public override async ValueTask DisposeAsync()
{
    await base.DisposeAsync();
    await logStream.DisposeAsync();
}""")

    # ───────────────────────────────────────────
    h1(d, "4. appsettings orqali boshqarish")

    para(d, "Kodga tegmasdan log darajasini o'zgartirish uchun konfiguratsiya faylidan "
            "foydalaniladi:")

    code(d, """{
  "Logging": {
    "LogLevel": {
      "Default": "Information",
      "Microsoft.EntityFrameworkCore.Database.Command": "Information",
      "Microsoft.EntityFrameworkCore.Infrastructure": "Warning"
    }
  }
}""", caption="appsettings.Development.json")

    para(d, "Bu usulning afzalligi — ilovani qayta kompilyatsiya qilmasdan log hajmini "
            "o'zgartirish mumkin. `Warning` darajasiga o'tkazilsa, so'rovlar ko'rsatilmaydi.")

    # ───────────────────────────────────────────
    h1(d, "5. Interceptor — so'rovlarni kuzatish")

    para(d, "Murakkabroq stsenariylarda, masalan sekin so'rovlarni avtomatik aniqlash "
            "uchun, `DbCommandInterceptor` ishlatiladi. U har bir so'rov bajarilishidan "
            "oldin va keyin chaqiriladi.")

    code(d, """public class SlowQueryInterceptor : DbCommandInterceptor
{
    private readonly ILogger<SlowQueryInterceptor> _logger;

    public SlowQueryInterceptor(ILogger<SlowQueryInterceptor> logger)
        => _logger = logger;

    public override ValueTask<DbDataReader> ReaderExecutedAsync(
        DbCommand command,
        CommandExecutedEventData eventData,
        DbDataReader result,
        CancellationToken ct = default)
    {
        if (eventData.Duration.TotalMilliseconds > 500)
        {
            _logger.LogWarning(
                "Sekin so'rov ({Ms} ms): {Sql}",
                eventData.Duration.TotalMilliseconds,
                command.CommandText);
        }

        return base.ReaderExecutedAsync(command, eventData, result, ct);
    }
}""")

    code(d, """options.AddInterceptors(new SlowQueryInterceptor(logger));""",
         caption="Ro'yxatdan o'tkazish")

    note(d, "Nega bu yondashuv yaxshi:",
         "Loglarni yoqib qo'yish hamma so'rovni ko'rsatadi va tez orada shovqinga "
         "aylanadi. Interceptor esa faqat muammoli so'rovlarni ajratib beradi. Uni "
         "production da ham qoldirish mumkin — chunki u faqat belgilangan chegaradan "
         "oshgan holatlarda yozadi.")

    # ───────────────────────────────────────────
    h1(d, "6. Baza tomonidan kuzatish")

    para(d, "Ilova kodiga umuman tegmasdan, ma'lumotlar bazasining o'zidan ham so'rovlarni "
            "ko'rish mumkin. PostgreSQL da joriy sessiya uchun:")

    code(d, """SET log_statement = 'all';""")

    para(d, "Yoki statistika kengaytmasi orqali eng ko'p takrorlangan va eng sekin "
            "so'rovlar ro'yxatini olish:")

    code(d, """SELECT query, calls, mean_exec_time, total_exec_time
FROM pg_stat_statements
ORDER BY total_exec_time DESC
LIMIT 20;""")

    para(d, "Bu usul ayniqsa qimmatli, chunki u ilova nimani yuborayotganini emas, baza "
            "haqiqatda nimani qabul qilganini ko'rsatadi. Ikkalasi orasida farq bo'lsa "
            "(masalan oradagi proxy tufayli), buni faqat shu yo'l bilan aniqlash mumkin.")

    # ───────────────────────────────────────────
    h1(d, "7. Nimaga e'tibor berish kerak")

    para(d, "SQL ni ko'rganda quyidagi belgilar muammoga ishora qiladi:")

    bullets(d, [
        "**Bir xil so'rov ketma-ket takrorlanyapti** — N+1 muammosi.",
        "**`SELECT` da keraksiz ustunlar ko'p** — proyeksiya ishlatilmagan.",
        "**Bir nechta `LEFT JOIN` bir darajada** — dekart ko'paytmasi xavfi bor.",
        "**`WHERE` shartida ustun funksiya ichida** (masalan `LOWER(name)`) — indeks "
        "ishlamay qolishi mumkin.",
        "**`ORDER BY` yo'q, lekin `Skip`/`Take` bor** — natija tartibi aniqlanmagan.",
    ])

    # ───────────────────────────────────────────
    h1(d, "8. Xulosa")

    bullets(d, [
        "`ToQueryString()` — bitta so'rovni tez tekshirish uchun eng qulay usul, bazaga "
        "murojaat qilmaydi.",
        "`LogTo` barcha so'rovlarni kuzatadi; kategoriya bo'yicha filtrlash shovqinni kamaytiradi.",
        "`EnableSensitiveDataLogging()` faqat development muhitida yoqilishi shart.",
        "`DbCommandInterceptor` sekin so'rovlarni avtomatik ajratib beradi va production "
        "uchun ham mos keladi.",
        "`pg_stat_statements` ilova emas, baza nuqtai nazaridan haqiqiy manzarani ko'rsatadi.",
    ])

    sources(d, [
        ("Logging, Events, and Diagnostics — EF Core",
         "https://learn.microsoft.com/en-us/ef/core/logging-events-diagnostics/"),
        ("Simple Logging — EF Core",
         "https://learn.microsoft.com/en-us/ef/core/logging-events-diagnostics/simple-logging"),
        ("Interceptors — EF Core",
         "https://learn.microsoft.com/en-us/ef/core/logging-events-diagnostics/interceptors"),
        ("pg_stat_statements — PostgreSQL hujjati",
         "https://www.postgresql.org/docs/current/pgstatstatements.html"),
    ])
