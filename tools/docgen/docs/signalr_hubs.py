# -*- coding: utf-8 -*-
import os
from docbuild import *

TOPIC = "SignalR, Transports, Hubs"
CATEGORY = "ASP.NET"
TITLE = "SignalR: Transportlar va Hub lar"
SUBTITLE = "Server tomonidan mijozga real vaqtda xabar yuborish"
FILENAME = "SignalR, Transports, Hubs.docx"

FIG = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "figures", "out", "signalr_transports.png")


def build(d):
    h1(d, "1. SignalR qanday muammoni hal qiladi")

    para(d, "An'anaviy HTTP da aloqani har doim mijoz boshlaydi: so'rov yuboradi, javob "
            "oladi. Server o'z tashabbusi bilan mijozga xabar yubora olmaydi.")

    para(d, "Bu cheklov real vaqtda yangilanishi kerak bo'lgan interfeyslarda muammo "
            "tug'diradi — chat, bildirishnomalar, jonli statistika, hamkorlikdagi "
            "tahrirlash. Yechim sifatida mijoz serverni muntazam so'rab turishi mumkin, "
            "lekin bu keraksiz trafik va kechikish demakdir.")

    para(d, "SignalR serverdan mijozga xabar yuborish imkonini beradi va buning uchun "
            "qaysi texnologiya ishlatilishini o'zi hal qiladi.")

    note(d, "Mening tushunchamda eng muhim jihat:",
         "SignalR — bu protokol emas, abstraksiya. U WebSocket ustida ishlaydi, lekin "
         "WebSocket mavjud bo'lmasa, boshqa usulga o'tadi va mening kodim buni "
         "sezmaydi. Ya'ni men bir marta kod yozaman, u esa turli sharoitlarda ishlaydi.")

    # ───────────────────────────────────────────
    h1(d, "2. Transportlar")

    para(d, "SignalR uch xil transportni qo'llab-quvvatlaydi va ular imkoniyatlari "
            "bo'yicha farq qiladi:")

    table(d, ["Transport", "Yo'nalish", "Xususiyati"],
          [["WebSockets", "Ikki tomonlama",
            "Bitta doimiy ulanish, eng kam yuk, eng kam kechikish"],
           ["Server-Sent Events", "Faqat serverdan mijozga",
            "Mijozdan serverga alohida HTTP so'rov kerak"],
           ["Long Polling", "Ikki tomonlama (taqlid)",
            "Har bir xabar uchun yangi so'rov; eng ko'p yuk"]],
          widths=[3.8, 4.2, 7.5])

    if os.path.exists(FIG):
        image(d, FIG, "Transport tanlash va zaxira variantlarga o'tish tartibi")

    h2(d, "2.1 Negotiation — kelishuv bosqichi")

    para(d, "Ulanish boshlanishida mijoz `/hubname/negotiate` manziliga POST so'rov "
            "yuboradi. Server javobida ulanish identifikatori va qo'llab-quvvatlanadigan "
            "transportlar ro'yxatini qaytaradi. Mijoz ulardan eng yaxshisini tanlaydi.")

    para(d, "Tanlangan transport ishlamasa, mijoz keyingisiga o'tadi. Bu jarayon "
            "avtomatik kechadi.")

    h2(d, "2.2 Transportni cheklash")

    code(d, """app.MapHub<NotificationHub>("/hubs/notifications", options =>
{
    options.Transports = HttpTransportType.WebSockets
                       | HttpTransportType.LongPolling;
});""")

    note(d, "Nega WebSocket har doim ham ishlamaydi:",
         "Korporativ tarmoqlarda proxy va firewall lar ko'pincha WebSocket ulanishini "
         "bloklaydi, chunki u odatdagi HTTP so'rovga o'xshamaydi. Eski brauzerlarda ham "
         "u mavjud emas. Aynan shuning uchun zaxira variantlar kerak — ular sekinroq, "
         "lekin ishlaydi.")

    note(d, "Negotiation ni o'chirish mumkin, lekin ehtiyot bo'lish kerak:",
         "Agar WebSocket albatta mavjudligiga ishonsam, `skipNegotiation` ni yoqib, "
         "bitta qo'shimcha so'rovni tejashim mumkin. Lekin u holda WebSocket ishlamasa, "
         "ulanish butunlay uzilib qoladi — zaxira variant bo'lmaydi.")

    # ───────────────────────────────────────────
    h1(d, "3. Hub — asosiy tushuncha")

    para(d, "Hub — bu mijoz va server o'rtasidagi aloqa nuqtasi. Mijoz hub dagi "
            "metodlarni chaqiradi, server esa mijozdagi metodlarni chaqiradi.")

    code(d, """public class ChatHub : Hub
{
    // Mijoz shu metodni chaqiradi
    public async Task SendMessage(string room, string text)
    {
        var user = Context.User?.Identity?.Name ?? "mehmon";

        // Server mijozdagi metodni chaqiradi
        await Clients.Group(room).SendAsync("ReceiveMessage", user, text);
    }

    public async Task JoinRoom(string room)
    {
        await Groups.AddToGroupAsync(Context.ConnectionId, room);
        await Clients.Group(room).SendAsync("UserJoined", Context.ConnectionId);
    }
}""")

    code(d, """builder.Services.AddSignalR();

var app = builder.Build();
app.MapHub<ChatHub>("/hubs/chat");""")

    h2(d, "3.1 Hub ning hayot davri")

    para(d, "Hub nusxasi **har bir chaqiruv uchun yangidan** yaratiladi va chaqiruv "
            "tugashi bilan yo'q qilinadi. Bu muhim tafsilot — hub ichidagi maydonga "
            "yozilgan qiymat keyingi chaqiruvda mavjud bo'lmaydi.")

    note(d, "Bu meni bir marta chalkashtirgan:",
         "Hub ichida `private int _counter` deb maydon e'lon qilib, uni oshirmoqchi "
         "bo'lgandim. Qiymat har safar nolga qaytaverardi. Sababi oddiy ekan — har "
         "chaqiruvda yangi obyekt yaratilyapti. Holatni saqlash kerak bo'lsa, uni "
         "singleton xizmatda yoki tashqi omborda saqlash kerak.")

    h2(d, "3.2 Context xossasi")

    table(d, ["A'zo", "Beradi"],
          [["`Context.ConnectionId`", "Joriy ulanishning noyob identifikatori"],
           ["`Context.UserIdentifier`", "Autentifikatsiyadan o'tgan foydalanuvchi id si"],
           ["`Context.User`", "To'liq `ClaimsPrincipal`"],
           ["`Context.Items`", "Shu ulanish davomida saqlanadigan ma'lumot"],
           ["`Context.Abort()`", "Ulanishni majburan uzish"]],
          widths=[5.2, 10.3])

    para(d, "`Context.Items` — hub nusxasi yo'q qilinsa ham saqlanadigan yagona joy, "
            "chunki u ulanishga bog'langan, hub ga emas.")

    h2(d, "3.3 Ulanish hodisalari")

    code(d, """public override async Task OnConnectedAsync()
{
    _logger.LogInformation("Ulandi: {Id}", Context.ConnectionId);
    await Groups.AddToGroupAsync(Context.ConnectionId, "all");
    await base.OnConnectedAsync();
}

public override async Task OnDisconnectedAsync(Exception? exception)
{
    if (exception is not null)
        _logger.LogWarning(exception, "Uzildi: {Id}", Context.ConnectionId);

    await base.OnDisconnectedAsync(exception);
}""")

    para(d, "Guruhdan chiqarish `OnDisconnectedAsync` da shart emas — SignalR uzilgan "
            "ulanishni guruhlardan avtomatik olib tashlaydi.")

    # ───────────────────────────────────────────
    h1(d, "4. Kimga yuborish")

    table(d, ["Ifoda", "Kimga boradi"],
          [["`Clients.All`", "Barcha ulangan mijozlarga"],
           ["`Clients.Caller`", "Faqat chaqiruvchiga"],
           ["`Clients.Others`", "Chaqiruvchidan boshqa hammaga"],
           ["`Clients.Client(id)`", "Bitta aniq ulanishga"],
           ["`Clients.Group(name)`", "Guruhdagi barchaga"],
           ["`Clients.OthersInGroup(name)`", "Guruhdagi, chaqiruvchidan boshqalarga"],
           ["`Clients.User(userId)`", "Foydalanuvchining barcha qurilmalariga"]],
          widths=[5.6, 9.9])

    note(d, "`Clients.User` va `Clients.Client` farqi muhim:",
         "Bitta foydalanuvchi telefon va kompyuterdan bir vaqtda ulangan bo'lishi "
         "mumkin — bu ikki alohida `ConnectionId`. Agar bildirishnomani hamma "
         "qurilmaga yuborish kerak bo'lsa, `Clients.User` ishlatiladi. `ConnectionId` "
         "ni bazaga saqlab qo'yish esa yomon fikr — u har ulanishda o'zgaradi.")

    # ───────────────────────────────────────────
    h1(d, "5. Hub tashqarisidan xabar yuborish")

    para(d, "Ko'pincha xabar yuborish kerak bo'lgan joy hub emas — fon xizmati, "
            "kontroller yoki xabar navbati iste'molchisi. Buning uchun "
            "`IHubContext<T>` ishlatiladi:")

    code(d, """public class OrderStatusWatcher : BackgroundService
{
    private readonly IHubContext<ChatHub> _hub;

    public OrderStatusWatcher(IHubContext<ChatHub> hub) => _hub = hub;

    protected override async Task ExecuteAsync(CancellationToken ct)
    {
        while (!ct.IsCancellationRequested)
        {
            var changed = await _repo.GetChangedOrdersAsync(ct);

            foreach (var order in changed)
            {
                await _hub.Clients
                    .User(order.CustomerId.ToString())
                    .SendAsync("OrderStatusChanged",
                               order.Id, order.Status, ct);
            }

            await Task.Delay(TimeSpan.FromSeconds(5), ct);
        }
    }
}""")

    # ───────────────────────────────────────────
    h1(d, "6. Avtorizatsiya")

    code(d, """[Authorize]
public class ChatHub : Hub
{
    [Authorize(Roles = "Admin")]
    public async Task BroadcastSystemMessage(string text) => ...;
}""")

    para(d, "Brauzer WebSocket so'roviga maxsus sarlavha qo'sha olmaydi, shuning uchun "
            "token query parametrida uzatiladi. Serverda uni o'qib olish kerak:")

    code(d, """options.Events = new JwtBearerEvents
{
    OnMessageReceived = context =>
    {
        var token = context.Request.Query["access_token"];
        var path = context.HttpContext.Request.Path;

        if (!string.IsNullOrEmpty(token) &&
            path.StartsWithSegments("/hubs"))
        {
            context.Token = token;
        }
        return Task.CompletedTask;
    }
};""")

    note(d, "Bu yerda xavfsizlik nuqtasi bor:",
         "Token query satrida ketganda u server loglariga va proxy loglariga tushishi "
         "mumkin. Shuning uchun SignalR uchun qisqa muddatli alohida token berish "
         "to'g'riroq bo'ladi — asosiy kirish tokenini u yerga qo'ymaslik kerak.")

    # ───────────────────────────────────────────
    h1(d, "7. Bir nechta server bilan ishlash")

    para(d, "Agar ilova bir nechta nusxada ishlasa, bir serverga ulangan mijoz "
            "boshqa serverdan yuborilgan xabarni olmaydi. Ulanishlar xotirada saqlanadi "
            "va serverlar bir-birini bilmaydi.")

    para(d, "Yechim — backplane, ya'ni serverlar o'rtasida xabar tarqatuvchi umumiy "
            "qatlam:")

    code(d, """builder.Services.AddSignalR()
    .AddStackExchangeRedis("localhost:6379", options =>
    {
        options.Configuration.ChannelPrefix =
            RedisChannel.Literal("myapp");
    });""")

    para(d, "Redis backplane har bir xabarni barcha serverlarga tarqatadi va har biri "
            "o'z mijozlariga yetkazadi. Muqobil yechim — yopishqoq sessiya (sticky "
            "session), ya'ni mijozni doim bitta serverga yo'naltirish.")

    note(d, "Buni oldindan o'ylash kerak:",
         "Bitta serverda hammasi ishlaydi va muammo ko'rinmaydi. Ikkinchi nusxa "
         "qo'shilganda esa xabarlar tasodifiy yo'qolgandek tuyuladi — chunki "
         "foydalanuvchining yarmi boshqa serverda. Bu nosozlikni topish juda qiyin, "
         "shuning uchun miqyoslash rejasi bo'lsa, backplane ni boshidan qo'ygan ma'qul.")

    # ───────────────────────────────────────────
    h1(d, "8. Xulosa")

    bullets(d, [
        "SignalR serverdan mijozga xabar yuborish imkonini beradi va transportni "
        "o'zi tanlaydi.",
        "Transportlar: WebSockets (eng yaxshi), Server-Sent Events, Long Polling.",
        "Negotiation bosqichida mijoz va server mos transportni kelishib oladi.",
        "Hub nusxasi har chaqiruvda yangidan yaratiladi — unda holat saqlanmaydi.",
        "`Context.Items` ulanish davomida saqlanadigan yagona joy.",
        "Hub tashqarisidan xabar yuborish uchun `IHubContext<T>` ishlatiladi.",
        "`ConnectionId` har ulanishda o'zgaradi — uni doimiy identifikator sifatida "
        "saqlash mumkin emas.",
        "Bir nechta server nusxasi bo'lsa, Redis backplane yoki sticky session kerak.",
    ])

    sources(d, [
        ("Introduction to ASP.NET Core SignalR",
         "https://learn.microsoft.com/en-us/aspnet/core/signalr/introduction"),
        ("Use hubs in ASP.NET Core SignalR",
         "https://learn.microsoft.com/en-us/aspnet/core/signalr/hubs"),
        ("ASP.NET Core SignalR configuration — transports",
         "https://learn.microsoft.com/en-us/aspnet/core/signalr/configuration"),
        ("Set up a Redis backplane for ASP.NET Core SignalR scale-out",
         "https://learn.microsoft.com/en-us/aspnet/core/signalr/redis-backplane"),
    ])
