# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "Cron pattern (kunlik, soatlik, haftalik, oylik, aniq davomiylik)"
CATEGORY = "Hangfire / Quartz"
TITLE = "Cron Ifodalari"
SUBTITLE = "Rejalashtirilgan vazifalar vaqtini belgilash"
FILENAME = "Cron pattern (kunlik, soatlik, haftalik, oylik, aniq davomiylik).docx"


def build(d):
    h1(d, "1. Cron ifodasi tuzilmasi")

    para(d, "Cron ifodasi — bo'shliq bilan ajratilgan maydonlar to'plami "
            "bo'lib, har biri vaqtning bir qismini belgilaydi.")

    code(d, """┌───────────── daqiqa        (0 - 59)
│ ┌─────────── soat          (0 - 23)
│ │ ┌───────── oy kuni       (1 - 31)
│ │ │ ┌─────── oy            (1 - 12)
│ │ │ │ ┌───── hafta kuni    (0 - 6, 0 = yakshanba)
│ │ │ │ │
* * * * *""")

    note(d, "Maydonlar soni muhim:",
         "Standart Unix cron beshta maydondan iborat. Quartz esa oltita "
         "yoki yettitasini ishlatadi — birinchi maydon soniya bo'ladi. "
         "Shuning uchun bir tizimda ishlagan ifoda boshqasida butunlay "
         "boshqa vaqtda ishga tushishi mumkin. Bu juda ko'p xatoga sabab "
         "bo'ladi.")

    table(d, ["Tizim", "Maydonlar", "Birinchi maydon"],
          [["Unix cron", "5", "Daqiqa"],
           ["Hangfire", "5 (yoki 6)", "Daqiqa (yoki soniya)"],
           ["Quartz.NET", "6 yoki 7", "Soniya"]],
          widths=[4.0, 5.0, 6.5])

    # ───────────────────────────────────────────
    h1(d, "2. Maxsus belgilar")

    table(d, ["Belgi", "Ma'nosi", "Misol"],
          [["`*`", "Har qanday qiymat", "`* * * * *` — har daqiqa"],
           ["`,`", "Ro'yxat", "`0 9,13,17 * * *` — 9:00, 13:00, 17:00"],
           ["`-`", "Oraliq", "`0 9-17 * * *` — 9 dan 17 gacha har soat"],
           ["`/`", "Qadam", "`*/15 * * * *` — har 15 daqiqada"],
           ["`?`", "Belgilanmagan (Quartz)", "`0 0 12 ? * MON`"],
           ["`L`", "Oxirgi (Quartz)", "`0 0 0 L * ?` — oyning oxirgi kuni"],
           ["`#`", "N-chi (Quartz)", "`0 0 0 ? * MON#2` — ikkinchi dushanba"]],
          widths=[2.2, 4.8, 8.5])

    # ───────────────────────────────────────────
    h1(d, "3. Keng tarqalgan ifodalar")

    h2(d, "3.1 Daqiqalik va soatlik")

    code(d, """*/5 * * * *      # har 5 daqiqada
*/30 * * * *     # har 30 daqiqada
0 * * * *        # har soat boshida
30 * * * *       # har soatning 30-daqiqasida
0 */4 * * *      # har 4 soatda""")

    h2(d, "3.2 Kunlik")

    code(d, """0 0 * * *        # har kuni yarim tunda
0 3 * * *        # har kuni 03:00 da
30 2 * * *       # har kuni 02:30 da
0 9,18 * * *     # har kuni 09:00 va 18:00 da""")

    h2(d, "3.3 Haftalik")

    code(d, """0 0 * * 0        # har yakshanba yarim tunda
0 9 * * 1        # har dushanba 09:00
0 18 * * 5       # har juma 18:00
0 8 * * 1-5      # ish kunlari 08:00
0 10 * * 6,0     # dam olish kunlari 10:00""")

    h2(d, "3.4 Oylik va yillik")

    code(d, """0 0 1 * *        # har oy 1-sanada
0 3 1 * *        # har oyning 1-sanasi 03:00 da
0 0 15 * *       # har oyning 15-sanasida
0 0 1 1 *        # har yil 1-yanvarda
0 0 1 */3 *      # har chorakda (yanvar, aprel, iyul, oktyabr)""")

    note(d, "Oyning oxirgi kuni — standart cron da muammo:",
         "`0 0 31 * *` deb yozsam, u faqat 31 kunlik oylarda ishlaydi — "
         "fevralda umuman ishga tushmaydi. Quartz da `L` belgisi bor va "
         "u muammoni hal qiladi. Hangfire da esa men vazifani har kuni "
         "ishga tushirib, kod ichida \"bugun oyning oxirgi kunimi\" deb "
         "tekshiraman.")

    code(d, """// Hangfire uchun yechim
RecurringJob.AddOrUpdate("monthly-report",
    () => _service.RunIfLastDayOfMonth(), "0 3 * * *");

public async Task RunIfLastDayOfMonth()
{
    var today = DateTime.UtcNow.Date;
    var lastDay = new DateTime(today.Year, today.Month,
        DateTime.DaysInMonth(today.Year, today.Month));

    if (today != lastDay) return;
    await GenerateMonthlyReportAsync();
}""")

    # ───────────────────────────────────────────
    h1(d, "4. Hangfire da ishlatish")

    code(d, """builder.Services.AddHangfire(config => config
    .SetDataCompatibilityLevel(CompatibilityLevel.Version_180)
    .UseSimpleAssemblyNameTypeSerializer()
    .UseRecommendedSerializerSettings()
    .UsePostgreSqlStorage(options =>
        options.UseNpgsqlConnection(connectionString)));

builder.Services.AddHangfireServer();""")

    code(d, """// Takrorlanuvchi vazifa
RecurringJob.AddOrUpdate<IReportService>(
    "daily-sales-report",
    service => service.GenerateDailyReportAsync(CancellationToken.None),
    "0 3 * * *",
    new RecurringJobOptions
    {
        TimeZone = TimeZoneInfo.FindSystemTimeZoneById("Asia/Tashkent")
    });""")

    code(d, """// Oldindan belgilangan ifodalar
Cron.Minutely()
Cron.Hourly()
Cron.Hourly(minute: 30)
Cron.Daily(hour: 3)
Cron.Weekly(DayOfWeek.Monday, hour: 9)
Cron.Monthly(day: 1, hour: 3)
Cron.Yearly()""")

    note(d, "Vaqt mintaqasi — eng ko'p chalkashlik manbai:",
         "Hangfire sukut bo'yicha UTC da ishlaydi. `0 3 * * *` deb "
         "yozsam, vazifa Toshkent vaqti bilan 08:00 da ishga tushadi. "
         "Agar men kechasi ishlashini kutayotgan bo'lsam, bu sezilarli "
         "farq. Shuning uchun `TimeZone` ni aniq ko'rsatish kerak.")

    note(d, "Yoz/qish vaqti haqida ham o'ylash kerak:",
         "Vaqt mintaqasi belgilangan bo'lsa va u yozgi vaqtga o'tsa, "
         "vazifa o'tkazib yuborilishi yoki ikki marta bajarilishi mumkin. "
         "O'zbekistonda bu muammo yo'q, lekin xalqaro loyihalarda UTC da "
         "qolish xavfsizroq.")

    # ───────────────────────────────────────────
    h1(d, "5. Quartz.NET da")

    code(d, """builder.Services.AddQuartz(q =>
{
    var jobKey = new JobKey("daily-report");

    q.AddJob<DailyReportJob>(opts => opts.WithIdentity(jobKey));

    q.AddTrigger(opts => opts
        .ForJob(jobKey)
        .WithIdentity("daily-report-trigger")
        .WithCronSchedule("0 0 3 * * ?",
            x => x.InTimeZone(TimeZoneInfo.FindSystemTimeZoneById("Asia/Tashkent"))));
});

builder.Services.AddQuartzHostedService(
    opts => opts.WaitForJobsToComplete = true);""")

    note(d, "Quartz da `?` belgisi majburiy:",
         "Oy kuni va hafta kuni maydonlarining ikkalasini bir vaqtda "
         "belgilab bo'lmaydi — bittasida `?` turishi kerak. "
         "`0 0 3 * * *` yozsam, Quartz xatolik beradi; to'g'ri shakli "
         "`0 0 3 * * ?` bo'ladi. Unix cron dan o'tganda bu birinchi "
         "to'siq bo'ladi.")

    code(d, """// Oddiy intervalli jadval — cron kerak emas
q.AddTrigger(opts => opts
    .ForJob(jobKey)
    .WithSimpleSchedule(x => x
        .WithIntervalInMinutes(15)
        .RepeatForever()));""")

    # ───────────────────────────────────────────
    h1(d, "6. Amaliy maslahatlar")

    h2(d, "6.1 Ifodani tekshirish")

    para(d, "Cron ifodasini yozgandan keyin uni albatta tekshirish kerak. "
            "Buning uchun onlayn vositalar yoki kutubxonaning o'zi "
            "ishlatiladi:")

    code(d, """// Hangfire ishlatadigan kutubxona
var schedule = CrontabSchedule.Parse("0 3 * * *");
var next = schedule.GetNextOccurrence(DateTime.UtcNow);
Console.WriteLine($"Keyingi ishga tushish: {next}");""")

    h2(d, "6.2 Vazifalarni vaqt bo'yicha tarqatish")

    note(d, "Barcha vazifalarni yarim tunga qo'ymaslik kerak:",
         "`0 0 * * *` eng tabiiy tanlovdek tuyuladi, lekin o'nta vazifa "
         "shu paytda birga ishga tushsa, server yuki keskin ko'tariladi. "
         "Men ularni tarqataman: biri 02:00, ikkinchisi 02:15, uchinchisi "
         "03:00. Natijada har biri bemalol bajariladi.")

    code(d, """RecurringJob.AddOrUpdate("cleanup-temp",   ..., "0 2 * * *");
RecurringJob.AddOrUpdate("daily-report",   ..., "15 2 * * *");
RecurringJob.AddOrUpdate("sync-external",  ..., "30 2 * * *");
RecurringJob.AddOrUpdate("refresh-views",  ..., "0 3 * * *");""")

    h2(d, "6.3 Idempotentlik")

    note(d, "Vazifa ikki marta bajarilishi mumkinligini hisobga olish kerak:",
         "Server qayta ishga tushsa, ikkita nusxa ishlasa yoki vazifa "
         "uzilib qayta urinsa — u takrorlanadi. Shuning uchun "
         "\"hisobotni yaratish\" emas, \"hisobot yo'q bo'lsa yaratish\" "
         "deb yozaman. Bu kichik farq, lekin takroriy ma'lumotdan "
         "qutqaradi.")

    code(d, """[DisableConcurrentExecution(timeoutInSeconds: 300)]
public async Task GenerateDailyReportAsync(CancellationToken ct)
{
    var date = DateOnly.FromDateTime(DateTime.UtcNow.AddDays(-1));

    if (await _db.Reports.AnyAsync(r => r.Date == date, ct))
        return;    // allaqachon yaratilgan

    ...
}""")

    h2(d, "6.4 Uzoq davom etadigan vazifalar")

    code(d, """// Agar vazifa 1 soat davom etsa, lekin har 30 daqiqada
// ishga tushsa — ular bir-birining ustiga chiqadi
[DisableConcurrentExecution(timeoutInSeconds: 3600)]""")

    # ───────────────────────────────────────────
    h1(d, "7. Tez-tez kerak bo'ladigan ifodalar jadvali")

    table(d, ["Ifoda", "Qachon ishga tushadi"],
          [["`*/10 * * * *`", "Har 10 daqiqada"],
           ["`0 * * * *`", "Har soat boshida"],
           ["`0 */6 * * *`", "Har 6 soatda"],
           ["`0 2 * * *`", "Har kuni 02:00"],
           ["`0 9 * * 1-5`", "Ish kunlari 09:00"],
           ["`0 0 * * 1`", "Har dushanba yarim tunda"],
           ["`0 3 1 * *`", "Har oy 1-sanasi 03:00"],
           ["`0 0 1 1 *`", "Har yil 1-yanvar"]],
          widths=[3.8, 11.7])

    # ───────────────────────────────────────────
    h1(d, "8. Xulosa")

    bullets(d, [
        "Cron ifodasi maydonlardan iborat: daqiqa, soat, oy kuni, oy, "
        "hafta kuni.",
        "Quartz qo'shimcha soniya maydonini talab qiladi — ifodalar mos "
        "kelmaydi.",
        "Quartz da oy kuni yoki hafta kuni maydonlaridan birida `?` "
        "bo'lishi shart.",
        "Hangfire sukut bo'yicha UTC da ishlaydi — `TimeZone` ni aniq "
        "ko'rsatish kerak.",
        "`0 0 31 * *` qisqa oylarda ishga tushmaydi; `L` yoki kod ichida "
        "tekshiruv kerak.",
        "Vazifalarni vaqt bo'yicha tarqatish server yukini tekislaydi.",
        "Vazifa idempotent bo'lishi va takroriy bajarilishga tayyor "
        "turishi lozim.",
        "`DisableConcurrentExecution` bir-biriga ustma-ust tushishni "
        "oldini oladi.",
    ])

    sources(d, [
        ("Recurring jobs — Hangfire hujjati",
         "https://docs.hangfire.io/en/latest/background-methods/performing-recurrent-tasks.html"),
        ("CronTrigger Tutorial — Quartz.NET",
         "https://www.quartz-scheduler.net/documentation/quartz-3.x/tutorial/crontriggers.html"),
        ("crontab(5) — Linux manual page",
         "https://man7.org/linux/man-pages/man5/crontab.5.html"),
    ])
