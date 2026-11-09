# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "NLog , serilog"
CATEGORY = "Logging"
TITLE = "NLog va Serilog"
SUBTITLE = "Strukturali loglash va provayder sozlash"
FILENAME = "NLog, serilog.docx"


def build(d):
    h1(d, "1. Nega standart provayder yetarli emas")

    para(d, "`ILogger<T>` — abstraksiya, provayder esa log'ni "
            "qayerga yozishni biladigan amalga oshiruvchi. "
            "Standartda Console, Debug, EventSource va Windows'da "
            "EventLog bor.")

    para(d, "Ular ishlab chiqish uchun yetarli, lekin production'da "
            "uchta narsa kerak bo'ladi va standart provayderlarda "
            "yo'q: faylga yozish va rotatsiya, markazlashgan "
            "to'plovchiga yuborish (Seq, Elasticsearch, Loki), va "
            "**strukturali** log.")

    # ───────────────────────────────────────────
    h1(d, "2. Strukturali log nima")

    para(d, "Oddiy log satr bo'lib yoziladi. Strukturali log'da "
            "esa xossalar **alohida maydon** bo'lib qoladi, "
            "shuning uchun ularni filtrlash va agregatsiya qilish "
            "mumkin.")

    code(d, """// TO'G'RI: shablon va parametrlar alohida
logger.LogInformation("Buyurtma {OrderId} yaratildi, summa {Total}",
    order.Id, order.Total);

// NOTO'G'RI: interpolatsiya
logger.LogInformation($"Buyurtma {order.Id} yaratildi, summa {order.Total}");""")

    code(d, """// Birinchi variantning natijasi (JSON)
{
  "@t": "2026-11-09T08:14:22.1234567Z",
  "@l": "Information",
  "@mt": "Buyurtma {OrderId} yaratildi, summa {Total}",
  "OrderId": "7f3c9a1e-8b24-4d6f-9012-3e4f5a6b7c8d",
  "Total": 250000,
  "SourceContext": "Shop.Application.Orders.CreateOrderHandler"
}""")

    para(d, "Shuning uchun `OrderId = '7f3c...'` bo'yicha "
            "qidirish, `Total > 1000000` bo'lgan buyurtmalarni "
            "topish yoki summalar yig'indisini hisoblash mumkin. "
            "Interpolatsiya bilan bu imkoniyat butunlay "
            "yo'qoladi.")

    note(d, "Yana bir sabab",
         "Interpolatsiya log darajasi o'chirilgan bo'lsa ham "
         "**baribir hisoblanadi**. Shablon shakli esa faqat "
         "daraja yoqilgan bo'lsa formatlanadi, ya'ni "
         "`LogDebug` production'da bepul bo'ladi.")

    # ───────────────────────────────────────────
    h1(d, "3. Serilog sozlash")

    code(d, """builder.Host.UseSerilog((context, services, configuration) => configuration
    .ReadFrom.Configuration(context.Configuration)
    .ReadFrom.Services(services)
    .Enrich.FromLogContext()
    .Enrich.WithMachineName()
    .Enrich.WithEnvironmentName());""")

    code(d, """// appsettings.json
{
  "Serilog": {
    "MinimumLevel": {
      "Default": "Information",
      "Override": {
        "Microsoft.AspNetCore": "Warning",
        "Microsoft.EntityFrameworkCore.Database.Command": "Warning"
      }
    },
    "WriteTo": [
      { "Name": "Console" },
      {
        "Name": "File",
        "Args": {
          "path": "logs/app-.json",
          "rollingInterval": "Day",
          "retainedFileCountLimit": 14,
          "formatter": "Serilog.Formatting.Compact.CompactJsonFormatter, Serilog.Formatting.Compact"
        }
      }
    ]
  }
}""")

    para(d, "`Override` qismi amalda juda muhim: standart "
            "sozlamada ASP.NET Core har bir so'rov uchun bir "
            "nechta `Information` log yozadi va foydali "
            "ma'lumot shovqinda ko'rinmay qoladi. Shuning uchun "
            "framework log'larini `Warning` ga tushiraman.")

    h2(d, "Request logging")

    code(d, """app.UseSerilogRequestLogging(options =>
{
    options.MessageTemplate =
        "{RequestMethod} {RequestPath} -> {StatusCode} ({Elapsed:0.0} ms)";

    options.EnrichDiagnosticContext = (diagnostic, context) =>
    {
        diagnostic.Set("UserId", context.User.FindFirst(ClaimTypes.NameIdentifier)?.Value);
        diagnostic.Set("UserAgent", context.Request.Headers.UserAgent.ToString());
    };
});""")

    para(d, "Bu har bir so'rov uchun **bitta** yig'ma log yozadi — "
            "framework yozadigan 4-5 ta log o'rniga. Natijada "
            "log hajmi kamayadi va o'qish osonlashadi.")

    # ───────────────────────────────────────────
    h1(d, "4. NLog sozlash")

    code(d, """builder.Logging.ClearProviders();
builder.Host.UseNLog();""")

    code(d, """<!-- nlog.config -->
<nlog xmlns="http://www.nlog-project.org/schemas/NLog.xsd">
  <targets>
    <target name="file" xsi:type="File"
            fileName="logs/app-${shortdate}.json"
            archiveEvery="Day"
            maxArchiveFiles="14">
      <layout xsi:type="JsonLayout" includeEventProperties="true">
        <attribute name="time" layout="${longdate}" />
        <attribute name="level" layout="${level}" />
        <attribute name="message" layout="${message}" />
        <attribute name="exception" layout="${exception:format=ToString}" />
      </layout>
    </target>
  </targets>

  <rules>
    <logger name="Microsoft.*" maxlevel="Warning" final="true" />
    <logger name="*" minlevel="Information" writeTo="file" />
  </rules>
</nlog>""")

    para(d, "NLog XML konfiguratsiyasi kuchli, lekin Serilog'ning "
            "fluent API'si menga tushunarliroq. Ikkisi ham "
            "`ILogger<T>` orqali ishlaydi, shuning uchun ilova "
            "kodi o'zgarmaydi — faqat sozlash farq qiladi.")

    table(d, ["", "Serilog", "NLog"],
          [["Konfiguratsiya", "Kod yoki JSON", "XML yoki kod"],
           ["Strukturali log", "Asosiy dizayn printsipi", "`JsonLayout` orqali"],
           ["Chiqish joylari", "Sink'lar (juda ko'p)", "Target'lar (juda ko'p)"],
           ["Kontekst", "`Enrich`, `LogContext`", "`MappedDiagnosticsContext`"]],
          widths=[4.0, 5.4, 5.1])

    # ───────────────────────────────────────────
    h1(d, "5. Daraja tanlash")

    bullets(d, [
        "`Trace` — eng mayda tafsilot, faqat mahalliy "
        "diagnostikada.",
        "`Debug` — ishlab chiqishda foydali ma'lumot.",
        "`Information` — **biznes hodisasi**: buyurtma yaratildi, "
        "to'lov o'tdi, foydalanuvchi kirdi.",
        "`Warning` — kutilmagan holat, lekin tizim ishlashda "
        "davom etadi: retry bo'ldi, kesh bo'sh chiqdi.",
        "`Error` — operatsiya bajarilmadi, odam aralashuvi kerak "
        "bo'lishi mumkin.",
        "`Critical` — tizim yoki uning muhim qismi ishlamaydi.",
    ])

    para(d, "Eng ko'p qilinadigan xato — hamma narsani "
            "`Information` bilan yozish. Natijada log'da "
            "haqiqiy muammoni topish imkonsiz bo'ladi. Men "
            "o'zimga shu savolni beraman: **bu yozuv "
            "production'da kimga va qachon kerak bo'ladi?**")

    # ───────────────────────────────────────────
    h1(d, "6. Scope va correlation")

    code(d, """using (logger.BeginScope("{CorrelationId}", correlationId))
using (logger.BeginScope("{OrderId}", order.Id))
{
    logger.LogInformation("To'lov boshlandi");
    await _gateway.ChargeAsync(order, ct);
    logger.LogInformation("To'lov tugadi");
}""")

    para(d, "Scope ichidagi hamma log yozuvi `CorrelationId` va "
            "`OrderId` maydonlariga ega bo'ladi — ularni har "
            "bir chaqiruvda qo'lda yozish kerak emas. Bu bitta "
            "operatsiya bo'yicha hamma yozuvni bir "
            "so'rovda topish imkonini beradi.")

    # ───────────────────────────────────────────
    h1(d, "7. Nimaga e'tibor beraman")

    bullets(d, [
        "**Maxfiy ma'lumot log'ga tushmasligi.** Parol, token, "
        "karta raqami, shaxsiy ma'lumot. Butun so'rov obyektini "
        "log qilish — tez-tez uchraydigan va xavfli odat.",
        "**Exception'ni to'g'ri yozish.** Birinchi parametr "
        "exception bo'lishi kerak: "
        "`logger.LogError(ex, \"Xabar {Id}\", id)`. "
        "`ex.Message` ni shablonga qo'yish stack trace'ni "
        "yo'qotadi.",
        "**Loglash ilovani to'xtatmasligi.** Fayl yoki tarmoq "
        "sink'i sekin bo'lsa, u so'rovni bloklaydi. Shuning uchun "
        "`WriteTo.Async()` ishlataman.",
        "**Rotatsiya va saqlash muddati.** Chegarasiz log fayli "
        "diskni to'ldiradi va server to'xtaydi — bu real incident "
        "sababi.",
        "**Ilova yopilganda buferni bo'shatish:**",
    ])

    code(d, """try
{
    app.Run();
}
catch (Exception ex)
{
    Log.Fatal(ex, "Ilova kutilmaganda to'xtadi");
}
finally
{
    Log.CloseAndFlush();        // bufer diskka yoziladi
}""")

    para(d, "`CloseAndFlush()` bo'lmasa, oxirgi — eng muhim — "
            "log yozuvlari yo'qolishi mumkin. Aynan ilova "
            "qulagan paytdagi log'lar.")

    sources(d, [
        ("Logging in .NET",
         "https://learn.microsoft.com/en-us/dotnet/core/extensions/logging"),
        ("Logging providers in ASP.NET Core",
         "https://learn.microsoft.com/en-us/aspnet/core/fundamentals/logging/"),
        ("Serilog documentation",
         "https://github.com/serilog/serilog/wiki"),
        ("NLog documentation",
         "https://github.com/NLog/NLog/wiki"),
    ])
