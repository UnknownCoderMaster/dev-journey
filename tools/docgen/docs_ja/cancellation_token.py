# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "CancellationToken"
CATEGORY = ".NET / C#"
TITLE = "CancellationToken"
SUBTITLE = "Operatsiyani bekor qilishni uzatish"
FILENAME = "CancellationToken.docx"


def build(d):
    h1(d, "1. Nima uchun kerak")

    para(d, "Foydalanuvchi sahifani yopdi, lekin server uning so'rovini "
            "bajarishda davom etadi: baza so'rovi ketadi, tashqi API "
            "chaqiriladi, hisobot yasaladi. Natija hech kimga kerak emas, "
            "lekin resurs sarflanadi.")

    para(d, "`CancellationToken` — bu \"bu ishni to'xtatish kerak\" degan "
            "signalni kod bo'ylab uzatish usuli. U majburlamaydi: kod o'zi "
            "signalni tekshirib, ishni to'xtatishi kerak. Ya'ni bu "
            "**hamkorlikdagi** (cooperative) bekor qilish.")

    # ───────────────────────────────────────────
    h1(d, "2. Ikki tomoni: Source va Token")

    para(d, "`CancellationTokenSource` — signal beradigan tomon. "
            "`CancellationToken` — signalni kutadigan tomon. Token "
            "source'dan olinadi va u faqat o'qish uchun.")

    code(d, """using var cts = new CancellationTokenSource();
CancellationToken token = cts.Token;

var task = DoWorkAsync(token);

cts.Cancel();          // signal berildi

await task;            // OperationCanceledException kutiladi""")

    para(d, "Vaqt bo'yicha avtomatik bekor qilish ham mumkin:")

    code(d, """using var cts = new CancellationTokenSource(TimeSpan.FromSeconds(5));""")

    h2(d, "Bir nechta manbani birlashtirish")

    para(d, "Amalda ko'p uchraydigan holat: so'rov bekor qilinsa **yoki** "
            "belgilangan vaqt o'tsa to'xtash kerak. Buning uchun bog'langan "
            "source yasaladi:")

    code(d, """using var timeout = new CancellationTokenSource(TimeSpan.FromSeconds(10));
using var linked = CancellationTokenSource.CreateLinkedTokenSource(
    requestToken, timeout.Token);

await _api.SendAsync(request, linked.Token);""")

    para(d, "Bog'langan token ikki manbadan biri signal bergan paytda "
            "bekor bo'ladi.")

    # ───────────────────────────────────────────
    h1(d, "3. Token'ni qanday tekshiraman")

    para(d, "Uch xil usul bor va ular turli holatlarga mos.")

    h2(d, "ThrowIfCancellationRequested")

    code(d, """foreach (var row in rows)
{
    ct.ThrowIfCancellationRequested();
    Process(row);
}""")

    para(d, "Eng ko'p ishlatiladigan shakl. Bekor qilingan bo'lsa "
            "`OperationCanceledException` tashlaydi.")

    h2(d, "IsCancellationRequested")

    code(d, """while (!ct.IsCancellationRequested)
{
    await PollAsync(ct);
}""")

    para(d, "Exception tashlamasdan, tartibli to'xtash kerak bo'lganda — "
            "masalan background servisning asosiy tsiklida.")

    h2(d, "Register — callback")

    code(d, """using var registration = ct.Register(() => _connection.Abort());""")

    para(d, "Bekor qilish signalida biror resursni majburan yopish kerak "
            "bo'lsa. Ro'yxatga olishni `Dispose` qilishni unutmaslik kerak, "
            "aks holda token uzoq yashasa callback'lar to'planib ketadi.")

    # ───────────────────────────────────────────
    h1(d, "4. Token'ni oxirigacha uzatish")

    para(d, "Eng ko'p qilinadigan xato — token'ni parametrga qabul qilib, "
            "keyin undan foydalanmaslik:")

    code(d, """// XATO: token qabul qilindi, lekin uzatilmadi
public async Task<List<Order>> GetAsync(CancellationToken ct)
{
    return await _db.Orders.ToListAsync();       // ct yo'q
}

// TO'G'RI
public async Task<List<Order>> GetAsync(CancellationToken ct)
{
    return await _db.Orders.ToListAsync(ct);
}""")

    para(d, "Token zanjirning oxirigacha — baza drayveri yoki HTTP "
            "mijoziga — yetib borishi kerak. Faqat shundagina haqiqiy "
            "I/O operatsiyasi to'xtaydi. O'rtada tashlab ketilsa, bekor "
            "qilish shunchaki ishlamaydi.")

    note(d, "Konvensiya",
         "`CancellationToken` har doim parametrlar ro'yxatining **oxirida** "
         "turadi va `ct` yoki `cancellationToken` deb nomlanadi. "
         "Standart qiymat (`= default`) faqat ommaviy API da, "
         "mijozni majburlamaslik uchun beriladi.")

    # ───────────────────────────────────────────
    h1(d, "5. ASP.NET Core da qayerdan keladi")

    para(d, "Controller action yoki minimal API handler'i `CancellationToken` "
            "parametrini e'lon qilsa, framework uni o'zi to'ldiradi. Bu "
            "token mijoz ulanishni uzganda bekor bo'ladi:")

    code(d, """[HttpGet]
public async Task<ActionResult<List<OrderDto>>> Get(CancellationToken ct)
{
    var orders = await _service.ListAsync(ct);
    return Ok(orders);
}""")

    para(d, "Uni qo'lda olish ham mumkin — `HttpContext.RequestAborted` aynan "
            "shu token.")

    para(d, "Background servisda esa token ilova to'xtatilganda bekor "
            "bo'ladi:")

    code(d, """protected override async Task ExecuteAsync(CancellationToken stoppingToken)
{
    while (!stoppingToken.IsCancellationRequested)
    {
        try
        {
            await ProcessBatchAsync(stoppingToken);
            await Task.Delay(TimeSpan.FromMinutes(1), stoppingToken);
        }
        catch (OperationCanceledException) when (stoppingToken.IsCancellationRequested)
        {
            break;      // normal to'xtash
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Batch xatosi, keyingi tsiklda qayta urinaman");
        }
    }
}""")

    # ───────────────────────────────────────────
    h1(d, "6. Exception bilan ishlash")

    para(d, "Bekor qilinganda `OperationCanceledException` chiqadi. "
            "`TaskCanceledException` esa uning hosilasi, shuning uchun "
            "bazaviy turni ushlash yetarli.")

    para(d, "Muhim ajratish: bu exception **xato emas**, bu kutilgan natija. "
            "Shuning uchun uni `LogError` bilan yozish log'ni keraksiz "
            "shovqinga to'ldiradi:")

    code(d, """try
{
    await _service.ProcessAsync(ct);
}
catch (OperationCanceledException) when (ct.IsCancellationRequested)
{
    _logger.LogInformation("Operatsiya foydalanuvchi tomonidan bekor qilindi");
}
catch (OperationCanceledException)
{
    // ct bekor qilinmagan — bu timeout, ya'ni haqiqiy muammo
    _logger.LogWarning("Operatsiya vaqt tugashi bo'yicha to'xtadi");
    throw;
}""")

    para(d, "`when` filtri bu yerda ikki holatni ajratadi: foydalanuvchi "
            "bekor qildimi yoki o'zim qo'ygan timeout ishladimi. Ikkisi "
            "turli xulosalar talab qiladi.")

    note(d, "Diqqat",
         "`HttpClient` timeout bo'lganda ham `TaskCanceledException` "
         "tashlaydi, token bekor qilinmagan bo'lsa ham. Shuning uchun "
         "yuqoridagi ikki `catch` ni ajratish amalda kerak bo'ladi.")

    # ───────────────────────────────────────────
    h1(d, "7. Nozik joylar")

    bullets(d, [
        "**Bekor qilish darhol bo'lmaydi.** Signal berilgandan keyin ish "
        "keyingi tekshiruv nuqtasiga yetguncha davom etadi. Shuning uchun "
        "uzun tsiklda tekshiruvni yetarlicha tez-tez qo'yish kerak.",
        "**Tranzaksiyani yarim yo'lda tashlab ketmaslik.** Bekor qilish "
        "`SaveChanges` o'rtasida kelsa, tranzaksiya rollback bo'ladi — bu "
        "to'g'ri. Lekin bir nechta `SaveChanges` bo'lsa, qismi saqlanib "
        "qolishi mumkin.",
        "**Tozalash kodini bekor qilinadigan qilmaslik.** `finally` ichida "
        "resursni yopayotganda allaqachon bekor qilingan token'ni "
        "uzatsam, tozalash ham bekor bo'ladi. Bunday joyda "
        "`CancellationToken.None` ishlataman.",
        "**`Task.Delay` ni token bilan chaqirish.** Token'siz `Delay` "
        "to'liq kutib turadi va ilovaning to'xtashini sekinlashtiradi.",
    ])

    # ───────────────────────────────────────────
    h1(d, "8. Amaliyotdan: tokenni oxirigacha uzatish qanchalik keng tarqalgani")

    para(d, "Ish joyimdagi MAD ERP tizimida `CancellationToken` ni ataylab sanab "
            "ko'rdim: u uch mingdan ortiq faylda uchraydi. Amalda har bir metod "
            "imzosida bor. Bu 4-bo'limdagi \"oxirigacha uzatish\" qoidasining eng "
            "izchil ko'rinishi va u menga ikki narsani ko'rsatdi.")

    h2(d, "8.1 Zanjir kontrollerdan bazagacha uzilmaydi")

    para(d, "Tizim CQRS bo'yicha qurilgan, shuning uchun zanjir uzun: kontroller → "
            "MediatR → pipeline behaviour → ishlovchi → EF Core so'rovi. Token "
            "hammasidan o'tadi:")

    code(d, """// Kontroller — token ASP.NET Core dan keladi
public async Task<IActionResult> GetListAsync([FromBody] CommissionGetListQuery query)
    => Ok(await Mediator.Send(query));

// Pipeline behaviour — validatorlarga uzatiladi
var validationResults = await Task.WhenAll(
    _validators.Select(v => v.ValidateAsync(context, cancellationToken)));

// Ishlovchi — EF Core ga uzatiladi
var entity = await dbContext.Commissions
    .Include(x => x.MemberTables)
    .FirstOrDefaultAsync(x => x.Id == request.Id, cancellationToken);

// Hatto SaveChanges ham
await dbContext.SaveChangesAsync(cancellationToken);""")

    para(d, "Diqqat qiladigan narsa — kontroller tokenni o'zi yozmaydi. MediatR uning "
            "`Send` metodida tokenni oladi, lekin bu yerda u berilmagan. 5-bo'limda "
            "aytilganidek `HttpContext.RequestAborted` ni olish uchun uni parametr "
            "sifatida e'lon qilish kerak. Ya'ni bu zanjirda eng birinchi bo'g'in "
            "yetishmaydi: kontroller token olmagani uchun MediatR ga `default` "
            "ketadi va mijoz ulanishni uzsa, so'rov baribir oxirigacha bajariladi.")

    note(d, "Bu meni qiziqtirgan narsa bo'ldi:",
         "Uch ming joyda token to'g'ri uzatilgan, lekin zanjirning boshida uzilgan. "
         "Natijada butun bu mehnat faqat bitta holatda ish beradi — ichki bekor "
         "qilishlarda, masalan `Task.WhenAll` dagi birinchi xatodan keyin. Mijozning "
         "ketishi esa sezilmaydi. Bundan chiqardim: oxirigacha uzatish zanjirning "
         "**eng boshidan** boshlanmasa, qolgan hammasi bekorga ketadi. Kontrollerga "
         "`CancellationToken cancellationToken` parametrini qo'shish — bitta qator, "
         "lekin uni qo'shmaslik butun zanjirni ma'nosiz qiladi.")

    h2(d, "8.2 Istisno filtri bilan bekor qilishni ajratish")

    para(d, "6-bo'limda `OperationCanceledException` bilan ishlash haqida gapirgandim. "
            "Shu tizimda juda yoqqan bir misolni ko'rdim. Bosh sahifadagi statistika "
            "paneli o'n ikkita og'ir `COUNT` so'rovidan iborat. Agar bittasi yiqilsa, "
            "butun panel 500 qaytarishi kerak emas — o'sha raqam o'rnida chiziqcha "
            "chiqsin:")

    code(d, """async Task<int?> Count(Func<Task<int>> count)
{
    try
    {
        return await count();
    }
    catch (Exception) when (!cancellationToken.IsCancellationRequested)
    {
        return null;
    }
}""", caption="GetLoginStatisticsQueryHandler")

    para(d, "Shart ichidagi `when (!cancellationToken.IsCancellationRequested)` — "
            "mana shu qismi muhim. U bo'lmasa `catch (Exception)` hamma narsani, "
            "shu jumladan bekor qilish istisnosini ham yutib yuborardi. Natijada "
            "mijoz allaqachon ketgan bo'lsa ham, kod qolgan o'n bir so'rovni "
            "bajarib, natijani keshga yozib qo'yardi.")

    bullets(d, [
        "Filtr bilan: mijoz uzsa, `OperationCanceledException` `catch` ga "
        "**tushmaydi** va yuqoriga chiqadi — qolgan so'rovlar bajarilmaydi.",
        "Filtrsiz: bekor qilish oddiy xato bilan bir xil qabul qilinardi va "
        "6-bo'limda aytilgan \"bekor qilishni xatodan farqlash\" qoidasi buzilardi.",
        "`Exception` ni ushlash odatda yomon amaliyot, lekin bu yerda maqsad aniq: "
        "bitta ko'rsatkich butun panelni yiqitmasligi kerak. Filtr esa bu keng "
        "ushlashni xavfsiz qiladi.",
    ])

    para(d, "7-bo'limda nozik joylar sifatida aytganlarimga shuni qo'shardim: "
            "`catch (Exception)` yozilgan har bir joyda \"bu bekor qilishni ham "
            "yutib yubormaydimi\" degan savolni berish kerak. Javob \"ha\" bo'lsa, "
            "istisno filtri qo'shiladi.")

    sources(d, [
        ("CancellationToken Struct",
         "https://learn.microsoft.com/en-us/dotnet/api/system.threading.cancellationtoken"),
        ("Cancellation in managed threads",
         "https://learn.microsoft.com/en-us/dotnet/standard/threading/cancellation-in-managed-threads"),
        ("Recommended patterns for CancellationToken",
         "https://learn.microsoft.com/en-us/dotnet/standard/parallel-programming/task-cancellation"),
    ])
