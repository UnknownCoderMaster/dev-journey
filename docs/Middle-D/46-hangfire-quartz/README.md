# Hangfire / Quartz.NET — Background Jobs, Cron Pattern — Middle D

## 1. Nima? (Ta'rif)

**Background Job** — HTTP so'rov oqimidan **tashqarida**, alohida
bajariladigan vazifa (masalan, kunlik hisobot, email yuborish).
**Hangfire** va **Quartz.NET** — .NET'da background job'larni
rejalashtirish va bajarish uchun ikkita eng mashhur kutubxona.

## 2. Nima uchun kerak?

"Har kuni soat 00:00 da barcha xodimlarning oylik maoshini
hisoblash" kabi vazifa — HTTP so'rov ichida bajarilishi **mumkin
emas** (hech kim shu vaqtda so'rov yubormaydi). Background Job
kutubxonasi — **vaqt jadvali (schedule)** asosida, avtomatik
ishga tushiruvchi mexanizm taqdim etadi.

## 3. Ichida nima sodir bo'ladi? (Mexanizm)

### 3.1 Hangfire vs Quartz.NET

| | Hangfire | Quartz.NET |
|---|---|---|
| Persistence | DB (SQL Server, PostgreSQL, Redis) | DB yoki xotira (RAMJobStore) |
| Dashboard | ✅ Built-in vizual UI | ❌ Yo'q (qo'shimcha kerak) |
| O'rnatish qulayligi | ✅ Juda oson | O'rtacha |
| Murakkab job workflow | Oddiy | ✅ Kuchli (Trigger/Job/Scheduler ajratilgan) |
| .NET ekotizimida holati | ✅ Juda mashhur | Java'dan portlangan, keng qo'llaniladi |

### 3.2 Cron pattern — sintaksisi

```
* * * * *
│ │ │ │ │
│ │ │ │ └── Hafta kuni (0-6, 0=Yakshanba)
│ │ │ └──── Oy (1-12)
│ │ └────── Kun (1-31)
│ └──────── Soat (0-23)
└────────── Daqiqa (0-59)
```

```
Kunlik (har kuni soat 00:00):        0 0 * * *
Soatlik (har soat boshida):           0 * * * *
Haftalik (har yakshanba, 00:00):      0 0 * * 0
Oylik (har oyning 1-kuni, 00:00):     0 0 1 * *
Har 15 daqiqada:                      */15 * * * *
Ish kunlari, soat 9:00 da:             0 9 * * 1-5
```

### 3.3 Hangfire o'rnatish — PostgreSQL bilan

```bash
dotnet add package Hangfire.AspNetCore
dotnet add package Hangfire.PostgreSql
```

```csharp
builder.Services.AddHangfire(config => config
    .UsePostgreSqlStorage(builder.Configuration.GetConnectionString("DefaultConnection")));
builder.Services.AddHangfireServer();

var app = builder.Build();
app.UseHangfireDashboard("/hangfire");
```

### 3.4 `RecurringJob`, `BackgroundJob`, `Schedule`

```csharp
// Takrorlanuvchi (cron asosida)
RecurringJob.AddOrUpdate<PayrollService>(
    "monthly-payroll",
    service => service.CalculateMonthlyPayroll(),
    Cron.Monthly);

// Bir martalik, DARHOL fon rejimida
BackgroundJob.Enqueue<EmailService>(service => service.SendWelcomeEmail(employeeId));

// Bir martalik, KECHIKTIRILGAN
BackgroundJob.Schedule<ReportService>(
    service => service.GenerateReport(),
    TimeSpan.FromHours(1));

// Zanjir — bir job tugagach, keyingisi ishga tushadi
var jobId = BackgroundJob.Enqueue(() => Step1());
BackgroundJob.ContinueJobWith(jobId, () => Step2());
```

### 3.5 Hangfire Dashboard — sozlash va himoya

```csharp
app.UseHangfireDashboard("/hangfire", new DashboardOptions
{
    Authorization = new[] { new HangfireAuthorizationFilter() } // Faqat Admin kirishi mumkin
});

public class HangfireAuthorizationFilter : IDashboardAuthorizationFilter
{
    public bool Authorize(DashboardContext context)
        => context.GetHttpContext().User.IsInRole("Admin");
}
```

```
⚠️ Dashboard'ni HIMOYASIZ qoldirish — istalgan kishi BARCHA job'larni
   ko'rishi, HATTO qo'lda ishga TUSHIRISHI mumkin (xavfsizlik xatari)!
```

### 3.6 Quartz.NET o'rnatish

```bash
dotnet add package Quartz
dotnet add package Quartz.Extensions.Hosting
```

```csharp
public class PayrollJob : IJob
{
    private readonly IServiceProvider _serviceProvider;
    public async Task Execute(IJobExecutionContext context)
    {
        using var scope = _serviceProvider.CreateScope();
        var service = scope.ServiceProvider.GetRequiredService<PayrollService>();
        await service.CalculateMonthlyPayrollAsync();
    }
}

builder.Services.AddQuartz(q =>
{
    var jobKey = new JobKey("PayrollJob");
    q.AddJob<PayrollJob>(opts => opts.WithIdentity(jobKey));
    q.AddTrigger(opts => opts
        .ForJob(jobKey)
        .WithIdentity("PayrollTrigger")
        .WithCronSchedule("0 0 1 * * ?")); // Quartz cron — 6/7 QISM (soniya QO'SHILGAN)!
});
builder.Services.AddQuartzHostedService();
```

```
⚠️ Quartz.NET cron formati — ODDIY cron'dan FARQ QILADI:
   Quartz: soniya daqiqa soat kun oy haftakuni [yil]
   Oddiy:          daqiqa soat kun oy haftakuni
```

### 3.7 `IJob`, `ITrigger`, `IScheduler`

```
IJob       — BAJARILADIGAN ISH (Execute metodi)
ITrigger   — QACHON bajarilishini belgilaydi (cron, interval)
IScheduler — Job va Trigger'larni BOSHQARUVCHI markaziy komponent

Hangfire'dan farqli — Quartz.NET bularni ANIQ AJRATADI (bitta Job'ga
BIR NECHTA Trigger biriktirish MUMKIN).
```

### 3.8 Job retry — xato bo'lganda

```csharp
// Hangfire — AVTOMATIK retry (default: 10 marta, exponential backoff)
[AutomaticRetry(Attempts = 3)]
public class PayrollJobHandler
{
    public void Execute() { /* xato bo'lsa, Hangfire AVTOMATIK qayta urinadi */ }
}
```

## 4. Kod — DI bilan integratsiya

```csharp
RecurringJob.AddOrUpdate<IPayrollService>(
    "monthly-payroll",
    service => service.CalculateAsync(),
    "0 0 1 * *"); // Hangfire — DI orqali IPayrollService'ni AVTOMATIK resolve qiladi
```

## 5. Qachon ishlatish kerak?

| Vaziyat | Yechim |
|---|---|
| Oddiy, tez o'rnatiladigan, vizual dashboard kerak | Hangfire |
| Murakkab, ko'p Trigger/Job kombinatsiyasi | Quartz.NET |
| Bir martalik, kechiktirilgan vazifa | `BackgroundJob.Schedule` |
| Muntazam, cron asosida | `RecurringJob` |

## 6. Muhim nuqtalar

- Hangfire Dashboard — HAR DOIM **Authorization** bilan himoyalanishi
  kerak.
- Job ichida `IServiceProvider` orqali **Scope** yaratish — Scoped
  servislar (DbContext) uchun MAJBURIY (job — Singleton kontekstda
  ishlaydi).
- Quartz cron format — Hangfire/standart cron'dan **farq qiladi**
  (soniya qismi qo'shilgan).

## 7. Imtihon savollari

1. Hangfire va Quartz.NET orasidagi asosiy farqlarni ayting.
2. Cron pattern'da `*/15 * * * *` nimani anglatadi?
3. `RecurringJob`, `BackgroundJob.Enqueue` va `BackgroundJob.Schedule`
   orasidagi farq nima?
4. Hangfire Dashboard nima uchun himoyalanishi kerak?
5. Quartz.NET'da `IJob`, `ITrigger`, `IScheduler` qanday
   birlashadi?
