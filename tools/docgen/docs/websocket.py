# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "WebSocket protocol"
CATEGORY = "Web"
TITLE = "WebSocket Protokoli"
SUBTITLE = "Doimiy ikki tomonlama ulanish qanday ishlaydi"
FILENAME = "WebSocket protocol.docx"


def build(d):
    h1(d, "1. WebSocket nima uchun kerak")

    para(d, "HTTP da aloqani doim mijoz boshlaydi. Serverda yangi ma'lumot paydo "
            "bo'lsa, u mijozga o'zi xabar bera olmaydi — mijoz kelib so'rashi kerak.")

    para(d, "Bu cheklovni aylanib o'tishning eski usuli polling edi: mijoz har "
            "necha soniyada \"yangilik bormi?\" deb so'raydi. Bu keraksiz trafik "
            "hosil qiladi va baribir kechikish qoladi.")

    para(d, "WebSocket boshqacha ishlaydi — bir marta ulanish o'rnatiladi va u ochiq "
            "qoladi. Shundan keyin ikkala tomon ham istalgan vaqtda xabar yubora "
            "oladi.")

    table(d, ["Usul", "Yo'nalish", "Yuk"],
          [["Polling", "Mijoz so'raydi", "Har so'rovda to'liq HTTP sarlavhalari"],
           ["Long polling", "Mijoz kutadi", "Kamroq, lekin ulanish qayta ochiladi"],
           ["SSE", "Faqat server → mijoz", "Bitta ulanish, yengil"],
           ["WebSocket", "Ikki tomonlama", "Bitta ulanish, eng kam"]],
          widths=[3.2, 4.4, 7.9])

    # ───────────────────────────────────────────
    h1(d, "2. Ulanish qanday o'rnatiladi")

    para(d, "WebSocket ulanishi oddiy HTTP so'rovdan boshlanadi. Mijoz protokolni "
            "almashtirishni so'raydi:")

    code(d, """GET /ws HTTP/1.1
Host: api.example.com
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==
Sec-WebSocket-Version: 13""")

    para(d, "Server rozi bo'lsa, maxsus javob qaytaradi:")

    code(d, """HTTP/1.1 101 Switching Protocols
Upgrade: websocket
Connection: Upgrade
Sec-WebSocket-Accept: s3pPLMBiTxaQ9kYGzzhZRbK+xOo=""")

    para(d, "`101` status kodi — protokol almashtirildi degani. Shundan keyin bu "
            "TCP ulanishi HTTP emas, WebSocket qoidalari bo'yicha ishlaydi.")

    note(d, "`Sec-WebSocket-Accept` nima uchun kerak:",
         "Server mijoz yuborgan kalitni ma'lum bir doimiy satr bilan birlashtirib, "
         "SHA-1 hash ini qaytaradi. Bu shifrlash emas — maqsad shunchaki javob "
         "berayotgan tomon haqiqatan WebSocket ni tushunishini tasdiqlash. "
         "Shunday qilib, protokolni bilmaydigan eski proxy tasodifan ulanishni "
         "o'rnatib yubormaydi.")

    h2(d, "2.1 Sxema nomlari")

    code(d, """ws://  — shifrlanmagan   (HTTP ga mos)
wss:// — shifrlangan     (HTTPS ga mos)""")

    para(d, "Amalda deyarli har doim `wss://` ishlatiladi — nafaqat xavfsizlik "
            "uchun, balki oraliq proxy lar shifrlangan trafikka kamroq "
            "aralashgani uchun ham.")

    # ───────────────────────────────────────────
    h1(d, "3. Freym tuzilmasi")

    para(d, "Ulanish o'rnatilgandan keyin ma'lumot freym deb ataladigan bo'laklarda "
            "uzatiladi. Har bir freym kichik sarlavhaga ega:")

    table(d, ["Maydon", "Vazifasi"],
          [["FIN", "Bu oxirgi bo'lakmi"],
           ["Opcode", "Freym turi: matn, ikkilik, ping, pong, close"],
           ["Mask", "Mijozdan serverga ketayotgan freym maskalanadi"],
           ["Payload length", "Ma'lumot uzunligi"],
           ["Payload", "Ma'lumotning o'zi"]],
          widths=[4.0, 11.5])

    para(d, "Sarlavha juda kichik — odatda 2 dan 14 baytgacha. Solishtirish uchun, "
            "oddiy HTTP so'rovi sarlavhalari yuzlab bayt bo'ladi. Aynan shu "
            "WebSocket ni tez-tez yuboriladigan kichik xabarlar uchun samarali "
            "qiladi.")

    h2(d, "3.1 Boshqaruv freymlari")

    bullets(d, [
        "`ping` / `pong` — ulanish tirikligini tekshirish. Agar ping ga javob "
        "kelmasa, ulanish uzilgan deb hisoblanadi.",
        "`close` — ulanishni tartibli yopish; sabab kodi bilan birga yuboriladi.",
    ])

    note(d, "Ping-pong mexanizmi muhim:",
         "TCP ulanishi \"jimgina\" uzilishi mumkin — oraliq router yoki NAT jadvali "
         "uni tashlab yuboradi, lekin ikkala tomon ham buni bilmaydi. Muntazam ping "
         "bu holatni aniqlaydi. Agar men ping yubormasam, ulanish uzilgan bo'lsa "
         "ham ochiqdek ko'rinaveradi va xabarlar yo'qoladi.")

    # ───────────────────────────────────────────
    h1(d, "4. ASP.NET Core da WebSocket")

    code(d, """var app = builder.Build();

app.UseWebSockets(new WebSocketOptions
{
    KeepAliveInterval = TimeSpan.FromSeconds(30)
});

app.Map("/ws", async context =>
{
    if (!context.WebSockets.IsWebSocketRequest)
    {
        context.Response.StatusCode = StatusCodes.Status400BadRequest;
        return;
    }

    using var socket = await context.WebSockets.AcceptWebSocketAsync();
    await EchoAsync(socket, context.RequestAborted);
});""")

    code(d, """static async Task EchoAsync(WebSocket socket, CancellationToken ct)
{
    var buffer = new byte[4 * 1024];

    while (socket.State == WebSocketState.Open)
    {
        var result = await socket.ReceiveAsync(buffer, ct);

        if (result.MessageType == WebSocketMessageType.Close)
        {
            await socket.CloseAsync(
                WebSocketCloseStatus.NormalClosure, "Yopildi", ct);
            break;
        }

        await socket.SendAsync(
            new ArraySegment<byte>(buffer, 0, result.Count),
            result.MessageType,
            result.EndOfMessage,
            ct);
    }
}""")

    note(d, "Bu kodda yashirin kamchilik bor:",
         "`ReceiveAsync` bitta chaqiruvda butun xabarni qaytarmasligi mumkin — "
         "katta xabar bir nechta freymga bo'linadi. `result.EndOfMessage` "
         "tekshirilmasa, xabar yarim o'qilib qoladi. Oddiy misollarda bu "
         "ko'rinmaydi, chunki kichik xabarlar bitta freymga sig'adi, va aynan "
         "shuning uchun muammo faqat production da chiqadi.")

    code(d, """// To'g'riroq: to'liq xabarni yig'ish
using var ms = new MemoryStream();
WebSocketReceiveResult result;

do
{
    result = await socket.ReceiveAsync(buffer, ct);
    ms.Write(buffer, 0, result.Count);
}
while (!result.EndOfMessage);

var text = Encoding.UTF8.GetString(ms.ToArray());""")

    h2(d, "4.1 Mijoz tomoni")

    code(d, """const socket = new WebSocket("wss://api.example.com/ws");

socket.onopen = () => socket.send("Salom");
socket.onmessage = e => console.log(e.data);
socket.onerror = e => console.error(e);
socket.onclose = e => console.log("Yopildi:", e.code, e.reason);""")

    code(d, """// .NET mijozi
using var client = new ClientWebSocket();
await client.ConnectAsync(new Uri("wss://api.example.com/ws"), ct);

await client.SendAsync(
    Encoding.UTF8.GetBytes("Salom"),
    WebSocketMessageType.Text,
    endOfMessage: true,
    ct);""")

    # ───────────────────────────────────────────
    h1(d, "5. SignalR bilan solishtirish")

    para(d, "SignalR WebSocket ustida quriladi, lekin ko'p qo'shimcha narsani o'z "
            "zimmasiga oladi:")

    table(d, ["Imkoniyat", "Toza WebSocket", "SignalR"],
          [["Zaxira transportlar", "Yo'q", "Bor"],
           ["Avtomatik qayta ulanish", "Qo'lda yoziladi", "Bor"],
           ["Guruhlar", "Qo'lda yoziladi", "Bor"],
           ["Metod chaqirish modeli", "Yo'q — xabar formati o'zim", "Bor"],
           ["Bir nechta server", "Qo'lda yoziladi", "Backplane orqali"],
           ["Nazorat darajasi", "To'liq", "Cheklangan"]],
          widths=[4.6, 5.5, 5.4])

    note(d, "Qachon toza WebSocket ni tanlayman:",
         "Agar mijoz `.NET` yoki JavaScript bo'lmasa, yoki protokol allaqachon "
         "boshqa tomon tomonidan belgilangan bo'lsa — masalan birja ma'lumot "
         "oqimiga ulanish. Boshqa hollarda SignalR ni tanlayman, chunki qayta "
         "ulanish va guruhlar mantiqini noldan yozish ko'p vaqt oladi va u "
         "yerdagi chegaraviy holatlarni oldindan ko'rish qiyin.")

    # ───────────────────────────────────────────
    h1(d, "6. Amaliy masalalar")

    h2(d, "6.1 Avtorizatsiya")

    para(d, "Brauzerdagi `WebSocket` konstruktori maxsus sarlavha qo'shishga ruxsat "
            "bermaydi. Shuning uchun token odatda query parametrida uzatiladi:")

    code(d, """const socket = new WebSocket(`wss://api.example.com/ws?token=${jwt}`);""")

    para(d, "Bu token server loglariga tushishi mumkin, shuning uchun WebSocket "
            "uchun alohida, qisqa muddatli token berish xavfsizroq.")

    h2(d, "6.2 Masshtablash")

    para(d, "Har bir ochiq WebSocket ulanishi serverda xotira va fayl deskriptori "
            "egallaydi. Minglab ulanish bo'lganda operatsion tizim chegaralarini "
            "oshirish kerak bo'ladi:")

    code(d, """ulimit -n 65536                      # Linux: ochiq fayllar chegarasi""")

    h2(d, "6.3 Proxy sozlamasi")

    code(d, """location /ws {
    proxy_pass http://backend;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_read_timeout 3600s;
}""")

    para(d, "`proxy_read_timeout` ni oshirmaslik tez-tez uchraydigan xato — sukutdagi "
            "60 soniyadan keyin proxy jim turgan ulanishni uzib qo'yadi.")

    # ───────────────────────────────────────────
    h1(d, "7. Yopilish kodlari")

    table(d, ["Kod", "Ma'nosi"],
          [["1000", "Odatdagi yopilish"],
           ["1001", "Tomon ketyapti (sahifa yopildi)"],
           ["1006", "Ulanish g'ayritabiiy uzildi — close freymi kelmadi"],
           ["1009", "Xabar juda katta"],
           ["1011", "Serverda kutilmagan xatolik"]],
          widths=[2.6, 12.9])

    para(d, "`1006` eng ko'p uchraydigani — u tarmoq uzilishi, proxy timeout i yoki "
            "serverning to'satdan to'xtashini bildiradi.")

    # ───────────────────────────────────────────
    h1(d, "8. Xulosa")

    bullets(d, [
        "WebSocket bitta doimiy ulanishda ikki tomonlama aloqa beradi.",
        "Ulanish HTTP so'rovidan boshlanadi va `101 Switching Protocols` bilan "
        "almashtiriladi.",
        "Freym sarlavhasi juda kichik — bu tez-tez yuboriladigan xabarlar uchun "
        "samarali.",
        "`ping`/`pong` jimgina uzilgan ulanishni aniqlaydi.",
        "`ReceiveAsync` butun xabarni qaytarmasligi mumkin — `EndOfMessage` ni "
        "tekshirish shart.",
        "SignalR WebSocket ustiga qayta ulanish, guruhlar va zaxira transportlarni "
        "qo'shadi.",
        "Brauzer WebSocket so'roviga sarlavha qo'sha olmaydi — token query da "
        "ketadi, shuning uchun u qisqa muddatli bo'lishi kerak.",
        "Proxy da `Upgrade` sarlavhasi va uzun `read_timeout` sozlanishi lozim.",
    ])

    sources(d, [
        ("RFC 6455 — The WebSocket Protocol",
         "https://www.rfc-editor.org/rfc/rfc6455"),
        ("WebSockets support in ASP.NET Core",
         "https://learn.microsoft.com/en-us/aspnet/core/fundamentals/websockets"),
        ("The WebSocket API — MDN",
         "https://developer.mozilla.org/en-US/docs/Web/API/WebSockets_API"),
    ])
