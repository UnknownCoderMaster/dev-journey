# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "SignalR clients, types"
CATEGORY = "ASP.NET"
TITLE = "SignalR Mijozlari va Tipli Hub lar"
SUBTITLE = "JavaScript va .NET mijozlari, qayta ulanish, kuchli tiplash"
FILENAME = "SignalR clients, types.docx"


def build(d):
    h1(d, "1. Mavjud mijoz kutubxonalari")

    para(d, "SignalR serveriga turli platformalardan ulanish mumkin. Rasmiy "
            "qo'llab-quvvatlanadigan mijozlar:")

    table(d, ["Platforma", "Paket"],
          [["JavaScript / TypeScript", "`@microsoft/signalr`"],
           [".NET (konsol, MAUI, Blazor)", "`Microsoft.AspNetCore.SignalR.Client`"],
           ["Java", "`com.microsoft.signalr:signalr`"]],
          widths=[5.6, 9.9])

    para(d, "Uchala mijoz ham bir xil protokolda ishlaydi, shuning uchun bitta server "
            "ularning hammasiga xizmat qiladi.")

    # ───────────────────────────────────────────
    h1(d, "2. JavaScript mijozi")

    code(d, """npm install @microsoft/signalr""")

    code(d, """import * as signalR from "@microsoft/signalr";

const connection = new signalR.HubConnectionBuilder()
    .withUrl("/hubs/chat", {
        accessTokenFactory: () => localStorage.getItem("token")
    })
    .withAutomaticReconnect()
    .configureLogging(signalR.LogLevel.Information)
    .build();

// Serverdan keladigan chaqiruvlarni tinglash
connection.on("ReceiveMessage", (user, text) => {
    console.log(`${user}: ${text}`);
});

// Ulanish
await connection.start();

// Serverdagi metodni chaqirish
await connection.invoke("SendMessage", "general", "Salom");""")

    h2(d, "2.1 invoke va send farqi")

    table(d, ["Metod", "Xatti-harakati"],
          [["`invoke`", "Server javobini kutadi; xatolik bo'lsa `Promise` rad etiladi"],
           ["`send`", "Yuborib, javob kutmaydi; xatolik haqida xabar bermaydi"]],
          widths=[3.6, 11.9])

    note(d, "Qachon qaysi birini tanlayman:",
         "`invoke` — operatsiya bajarilganiga ishonch kerak bo'lganda, masalan xabar "
         "yuborishda. `send` — natijasi muhim bo'lmagan signal uchun, masalan "
         "\"foydalanuvchi yozmoqda\" indikatori. Agar `send` ishlatib, keyin xatolik "
         "nega ko'rinmayotganiga hayron bo'lsam — sabab shu.")

    h2(d, "2.2 Ulanish holatini kuzatish")

    code(d, """connection.onreconnecting(error => {
    showBanner("Aloqa uzildi, qayta ulanmoqda...");
});

connection.onreconnected(connectionId => {
    hideBanner();
    // Guruhlarga qayta qo'shilish kerak
    connection.invoke("JoinRoom", currentRoom);
});

connection.onclose(error => {
    showBanner("Aloqa to'xtadi. Sahifani yangilang.");
});""")

    note(d, "Bu eng ko'p unutiladigan tafsilot:",
         "Qayta ulanishdan keyin `ConnectionId` **yangi** bo'ladi va eski ulanish "
         "qaysi guruhlarda bo'lgani unutiladi. Ya'ni foydalanuvchi chat xonasida "
         "qolgandek ko'rinadi, lekin aslida u yerdan chiqib ketgan va xabarlar "
         "kelmaydi. Shuning uchun `onreconnected` ichida guruhlarga qayta qo'shilish "
         "shart.")

    h2(d, "2.3 Qayta ulanish siyosati")

    code(d, """// Sukutdagi: 0, 2, 10, 30 soniyadan keyin urinadi, keyin to'xtaydi
.withAutomaticReconnect()

// O'z intervallarim (millisekundda)
.withAutomaticReconnect([0, 1000, 5000, 10000, 30000])

// To'liq nazorat
.withAutomaticReconnect({
    nextRetryDelayInMilliseconds: ctx => {
        if (ctx.elapsedMilliseconds > 120000) return null;  // taslim
        return Math.min(1000 * 2 ** ctx.previousRetryCount, 30000);
    }
})""")

    para(d, "`withAutomaticReconnect` umuman chaqirilmasa, ulanish uzilganda qayta "
            "urinish bo'lmaydi.")

    # ───────────────────────────────────────────
    h1(d, "3. .NET mijozi")

    code(d, """dotnet add package Microsoft.AspNetCore.SignalR.Client""")

    code(d, """var connection = new HubConnectionBuilder()
    .WithUrl("https://api.example.com/hubs/chat", options =>
    {
        options.AccessTokenProvider = () => Task.FromResult(token);
    })
    .WithAutomaticReconnect()
    .AddMessagePackProtocol()
    .Build();

connection.On<string, string>("ReceiveMessage", (user, text) =>
{
    Console.WriteLine($"{user}: {text}");
});

await connection.StartAsync();
await connection.InvokeAsync("SendMessage", "general", "Salom");""")

    h2(d, "3.1 MessagePack protokoli")

    para(d, "Sukut bo'yicha xabarlar JSON da uzatiladi. `MessagePack` ikkilik format "
            "bo'lib, hajmi kichikroq va serializatsiyasi tezroq. Uni server tomonida "
            "ham yoqish kerak:")

    code(d, """builder.Services.AddSignalR()
    .AddMessagePackProtocol();""")

    # ───────────────────────────────────────────
    h1(d, "4. Kuchli tiplangan hub lar")

    para(d, "Oddiy hub da mijoz metodi nomi matn sifatida yoziladi. Bu xavfli — "
            "harf xatosi kompilyatsiyada aniqlanmaydi va xabar hech qayerga bormaydi.")

    code(d, """// Xato bor, lekin kompilyator buni ko'rmaydi
await Clients.All.SendAsync("ReciveMessage", user, text);""")

    para(d, "Yechim — mijoz metodlarini interfeys sifatida e'lon qilish:")

    code(d, """public interface IChatClient
{
    Task ReceiveMessage(string user, string text);
    Task UserJoined(string userName);
    Task UserLeft(string userName);
}

public class ChatHub : Hub<IChatClient>
{
    public async Task SendMessage(string room, string text)
    {
        var user = Context.User?.Identity?.Name ?? "mehmon";
        await Clients.Group(room).ReceiveMessage(user, text);
    }
}""")

    para(d, "Endi metod nomi va parametrlari kompilyator tomonidan tekshiriladi. "
            "Interfeys metodlari `Task` qaytarishi va `out`/`ref` parametrlarsiz "
            "bo'lishi kerak.")

    note(d, "Bu o'zgarishdan keyin bir xatolikni darhol topdim:",
         "Interfeysni kiritganimda kod kompilyatsiya bo'lmay qoldi — chunki bir joyda "
         "metod nomini noto'g'ri yozgan ekanman va mijoz o'sha xabarni hech qachon "
         "olmagan. Avval bu jimgina ishlamaydigan narsa edi, endi esa kompilyator "
         "xatosi. Shu sababli har doim `Hub<T>` ishlataman.")

    h2(d, "4.1 Interfeysni baham ko'rish")

    para(d, "Agar mijoz ham `.NET` da bo'lsa, interfeysni umumiy loyihaga chiqarib, "
            "ikki tomonda ham ishlatish mumkin:")

    code(d, """// Umumiy kutubxonada
public interface IChatClient { ... }
public interface IChatServer
{
    Task SendMessage(string room, string text);
    Task JoinRoom(string room);
}""")

    para(d, "Mijoz tomonida interfeys metod nomlari uchun yagona manba bo'lib xizmat "
            "qiladi — matnli nomlar `nameof` orqali olinadi:")

    code(d, """connection.On<string, string>(
    nameof(IChatClient.ReceiveMessage),
    (user, text) => Display(user, text));

await connection.InvokeAsync(
    nameof(IChatServer.SendMessage), "general", "Salom");""")

    para(d, "Shu tarzda server interfeysni o'zgartirsa, mijoz loyihasi ham "
            "kompilyatsiya bo'lmaydi va nomuvofiqlik darhol ko'rinadi.")

    # ───────────────────────────────────────────
    h1(d, "5. Oqimli uzatish")

    para(d, "Katta hajmli yoki uzoq davom etadigan natijani bir yo'la emas, bo'lib-bo'lib "
            "yuborish mumkin.")

    h2(d, "5.1 Serverdan mijozga")

    code(d, """public async IAsyncEnumerable<ProgressDto> TrackImport(
    Guid importId,
    [EnumeratorCancellation] CancellationToken ct)
{
    while (!ct.IsCancellationRequested)
    {
        var progress = await _import.GetProgressAsync(importId, ct);
        yield return progress;

        if (progress.IsCompleted)
            yield break;

        await Task.Delay(1000, ct);
    }
}""")

    code(d, """connection.stream("TrackImport", importId).subscribe({
    next: progress => updateBar(progress.percent),
    complete: () => showDone(),
    error: err => showError(err)
});""")

    h2(d, "5.2 Mijozdan serverga")

    code(d, """public async Task UploadChunks(IAsyncEnumerable<byte[]> stream)
{
    await foreach (var chunk in stream)
        await _storage.AppendAsync(chunk);
}""")

    note(d, "Oqim qachon kerak bo'ladi:",
         "Agar natija bitta xabarga sig'masa yoki uni kutish uzoq davom etsa. Masalan "
         "katta faylni qayta ishlash jarayonini ko'rsatish. Oddiy holatda esa oddiy "
         "chaqiruv yetarli — oqim kodni murakkablashtiradi.")

    # ───────────────────────────────────────────
    h1(d, "6. Tiplar va serializatsiya")

    para(d, "Hub metodlari parametrlari sukut bo'yicha `System.Text.Json` bilan "
            "serializatsiya qilinadi. Sozlash server tomonida bajariladi:")

    code(d, """builder.Services.AddSignalR()
    .AddJsonProtocol(options =>
    {
        options.PayloadSerializerOptions.PropertyNamingPolicy =
            JsonNamingPolicy.CamelCase;
        options.PayloadSerializerOptions.Converters
            .Add(new JsonStringEnumConverter());
    });""")

    note(d, "Nomlash siyosati haqida:",
         "JavaScript mijozi `camelCase` kutadi, `.NET` esa `PascalCase` da yozadi. "
         "Agar bu moslashtirilmasa, mijozda maydonlar `undefined` bo'lib chiqadi va "
         "sabab darhol tushunarli bo'lmaydi. Men buni birinchi integratsiyada "
         "boshdan kechirganman.")

    h2(d, "6.1 Xabar hajmi cheklovi")

    code(d, """builder.Services.AddSignalR(options =>
{
    options.MaximumReceiveMessageSize = 64 * 1024;     // 64 KB
    options.ClientTimeoutInterval = TimeSpan.FromSeconds(60);
    options.KeepAliveInterval = TimeSpan.FromSeconds(15);
});""")

    para(d, "Sukutdagi xabar hajmi 32 KB. Katta ma'lumotni SignalR orqali emas, oddiy "
            "HTTP yoki fayl omborlari orqali uzatgan ma'qul — SignalR qisqa xabarlar "
            "uchun mo'ljallangan.")

    # ───────────────────────────────────────────
    h1(d, "7. Xulosa")

    bullets(d, [
        "Rasmiy mijozlar: JavaScript/TypeScript, `.NET` va Java.",
        "`invoke` javobni kutadi, `send` kutmaydi va xatolikni ko'rsatmaydi.",
        "`withAutomaticReconnect` yoqilmasa, uzilgan ulanish tiklanmaydi.",
        "Qayta ulanishdan keyin `ConnectionId` o'zgaradi va guruhlarga qayta qo'shilish "
        "kerak.",
        "`Hub<TClient>` mijoz metodlarini kompilyatsiya vaqtida tekshiradi — matnli "
        "nomlardan voz kechish kerak.",
        "`IAsyncEnumerable` orqali ikki yo'nalishda oqimli uzatish mumkin.",
        "JSON nomlash siyosatini mijoz kutgan shaklga moslash kerak.",
        "Sukutdagi xabar hajmi 32 KB — katta ma'lumot uchun SignalR mos emas.",
    ])

    sources(d, [
        ("ASP.NET Core SignalR JavaScript client",
         "https://learn.microsoft.com/en-us/aspnet/core/signalr/javascript-client"),
        ("ASP.NET Core SignalR .NET Client",
         "https://learn.microsoft.com/en-us/aspnet/core/signalr/dotnet-client"),
        ("Strongly typed hubs — ASP.NET Core SignalR",
         "https://learn.microsoft.com/en-us/aspnet/core/signalr/hubs#strongly-typed-hubs"),
        ("Use streaming in ASP.NET Core SignalR",
         "https://learn.microsoft.com/en-us/aspnet/core/signalr/streaming"),
    ])
