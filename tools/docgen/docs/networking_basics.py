# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "Networking, Network Architecture, Addresses and Ports"
CATEGORY = ".NET / C#"
TITLE = "Tarmoq Asoslari va .NET da Soketlar"
SUBTITLE = "Qatlamlar, protokollar va TCP/UDP bilan ishlash"
FILENAME = "Networking, Network Architecture, Addresses and Ports.docx"


def build(d):
    h1(d, "1. Tarmoq qatlamlari")

    para(d, "Tarmoq aloqasi qatlamlarga bo'lingan. Har bir qatlam o'z "
            "vazifasini bajaradi va quyidagisiga tayanadi.")

    table(d, ["Qatlam", "Vazifasi", "Misol"],
          [["Ilova", "Ma'lumot formati", "HTTP, SMTP, DNS"],
           ["Transport", "Yetkazish usuli", "TCP, UDP"],
           ["Tarmoq", "Marshrutlash", "IP"],
           ["Kanal", "Fizik uzatish", "Ethernet, Wi-Fi"]],
          widths=[3.0, 5.0, 7.5])

    para(d, "Dasturchi odatda ilova va transport qatlamlari bilan "
            "ishlaydi. Quyi qatlamlar operatsion tizim zimmasida.")

    # ───────────────────────────────────────────
    h1(d, "2. TCP va UDP")

    table(d, ["Jihat", "TCP", "UDP"],
          [["Ulanish", "O'rnatiladi", "O'rnatilmaydi"],
           ["Yetkazish kafolati", "Bor", "Yo'q"],
           ["Tartib", "Saqlanadi", "Saqlanmaydi"],
           ["Tezlik", "Sekinroq", "Tezroq"],
           ["Qo'llanishi", "HTTP, SMTP, baza", "DNS, video oqim, o'yinlar"]],
          widths=[3.6, 6.0, 5.9])

    h2(d, "2.1 TCP uch bosqichli qo'l berish")

    code(d, """Mijoz                          Server
  │                              │
  │ ────── SYN ────────────────► │   ulanmoqchiman
  │                              │
  │ ◄───── SYN-ACK ───────────── │   roziman, men ham
  │                              │
  │ ────── ACK ────────────────► │   tasdiqlandi
  │                              │
  │ ═══ ma'lumot almashinuvi ═══ │""")

    note(d, "Bu uch bosqich har bir yangi ulanishda takrorlanadi:",
         "Shuning uchun ko'p qisqa ulanish ochish samarasiz — har biri "
         "ma'lumot uzatilishidan oldin uch marta tarmoq murojaatini "
         "talab qiladi. Aynan shu sababli `HttpClient` ni qayta "
         "ishlatish va ulanish hovuzlari muhim.")

    # ───────────────────────────────────────────
    h1(d, "3. Manzil va port")

    para(d, "To'liq manzil ikki qismdan iborat: IP manzil qaysi "
            "qurilmaga, port esa o'sha qurilmadagi qaysi dasturga "
            "borishni bildiradi.")

    code(d, """var endpoint = new IPEndPoint(IPAddress.Parse("10.0.1.20"), 5432);

Console.WriteLine(endpoint.Address);   // 10.0.1.20
Console.WriteLine(endpoint.Port);      // 5432""")

    code(d, """// Domen nomini yechish
var addresses = await Dns.GetHostAddressesAsync("example.com");

foreach (var address in addresses)
    Console.WriteLine($"{address} ({address.AddressFamily})");""")

    h2(d, "3.1 Maxsus manzillar")

    table(d, ["Manzil", "Ma'nosi"],
          [["`IPAddress.Loopback`", "`127.0.0.1` — o'ziga"],
           ["`IPAddress.Any`", "`0.0.0.0` — barcha interfeyslar"],
           ["`IPAddress.IPv6Loopback`", "`::1`"],
           ["`IPAddress.IPv6Any`", "`::`"]],
          widths=[5.0, 10.5])

    # ───────────────────────────────────────────
    h1(d, "4. TCP server")

    code(d, """using System.Net;
using System.Net.Sockets;
using System.Text;

var listener = new TcpListener(IPAddress.Any, 9100);
listener.Start();

Console.WriteLine("9100 portda kutilmoqda...");

while (!cancellationToken.IsCancellationRequested)
{
    var client = await listener.AcceptTcpClientAsync(cancellationToken);

    // Har bir mijozni alohida qayta ishlash
    _ = HandleClientAsync(client, cancellationToken);
}

static async Task HandleClientAsync(TcpClient client, CancellationToken ct)
{
    using (client)
    await using (var stream = client.GetStream())
    {
        var buffer = new byte[4096];
        var read = await stream.ReadAsync(buffer, ct);

        var message = Encoding.UTF8.GetString(buffer, 0, read);
        Console.WriteLine($"Qabul qilindi: {message}");

        var response = Encoding.UTF8.GetBytes($"Echo: {message}");
        await stream.WriteAsync(response, ct);
    }
}""")

    note(d, "`HandleClientAsync` ni kutmasdan chaqirish ataylab:",
         "Agar `await` qo'ysam, server bitta mijozni qayta ishlab "
         "bo'lgunicha keyingisini qabul qilmaydi. Kutmasdan chaqirsam, "
         "u fonda ishlaydi va sikl darhol keyingi ulanishni kutadi. "
         "Lekin bu holda istisnolarni ushlashni unutmaslik kerak — aks "
         "holda ular yo'qoladi.")

    # ───────────────────────────────────────────
    h1(d, "5. TCP mijoz")

    code(d, """using var client = new TcpClient();

await client.ConnectAsync("localhost", 9100, cancellationToken);

await using var stream = client.GetStream();

var message = Encoding.UTF8.GetBytes("Salom");
await stream.WriteAsync(message, cancellationToken);

var buffer = new byte[4096];
var read = await stream.ReadAsync(buffer, cancellationToken);

Console.WriteLine(Encoding.UTF8.GetString(buffer, 0, read));""")

    h2(d, "5.1 Xabar chegarasi muammosi")

    note(d, "TCP — oqim, xabar emas:",
         "Men bitta `WriteAsync` bilan 1000 bayt yuborsam, qabul "
         "qiluvchi uni ikki marta — 600 va 400 bayt bo'lib olishi "
         "mumkin. Yoki aksincha, ikkita alohida xabar bitta `Read` da "
         "kelishi mumkin. TCP bayt oqimini kafolatlaydi, xabar "
         "chegaralarini emas.")

    para(d, "Shuning uchun protokol darajasida chegara belgilash kerak:")

    code(d, """// Uzunlik prefiksi bilan
static async Task SendAsync(NetworkStream stream, byte[] payload, CancellationToken ct)
{
    var length = BitConverter.GetBytes(payload.Length);
    await stream.WriteAsync(length, ct);
    await stream.WriteAsync(payload, ct);
}

static async Task<byte[]> ReceiveAsync(NetworkStream stream, CancellationToken ct)
{
    var lengthBuffer = new byte[4];
    await stream.ReadExactlyAsync(lengthBuffer, ct);

    var length = BitConverter.ToInt32(lengthBuffer);
    var payload = new byte[length];
    await stream.ReadExactlyAsync(payload, ct);

    return payload;
}""")

    note(d, "`ReadExactlyAsync` — .NET 7 dan qo'shilgan foydali metod:",
         "Oddiy `ReadAsync` so'ralgan miqdordan kamroq o'qishi mumkin va "
         "buni qo'lda sikl bilan hal qilish kerak edi. "
         "`ReadExactlyAsync` esa aniq shuncha bayt o'qiguncha kutadi — "
         "bu ko'p xatoni oldini oladi.")

    # ───────────────────────────────────────────
    h1(d, "6. UDP")

    code(d, """// Yuborish
using var sender = new UdpClient();
var data = Encoding.UTF8.GetBytes("holat: ok");
await sender.SendAsync(data, "10.0.1.50", 9200);

// Qabul qilish
using var receiver = new UdpClient(9200);

while (!ct.IsCancellationRequested)
{
    var result = await receiver.ReceiveAsync(ct);
    var text = Encoding.UTF8.GetString(result.Buffer);

    Console.WriteLine($"{result.RemoteEndPoint}: {text}");
}""")

    note(d, "UDP qachon mos keladi:",
         "Agar bir nechta paket yo'qolishi muammo bo'lmasa va tezlik "
         "muhim bo'lsa. Masalan har soniyada yuboriladigan metrika — "
         "bittasi yo'qolsa, keyingisi baribir keladi. Buyurtma "
         "ma'lumoti uchun esa UDP mutlaqo yaramaydi.")

    # ───────────────────────────────────────────
    h1(d, "7. Soket sozlamalari")

    code(d, """var socket = new Socket(AddressFamily.InterNetwork,
                        SocketType.Stream, ProtocolType.Tcp);

// Nagle algoritmini o'chirish — kichik paketlar darhol yuboriladi
socket.NoDelay = true;

// Kutish vaqtlari
socket.ReceiveTimeout = 30_000;
socket.SendTimeout = 30_000;

// Keep-alive
socket.SetSocketOption(SocketOptionLevel.Socket,
                       SocketOptionName.KeepAlive, true);

// Portni qayta ishlatish
socket.SetSocketOption(SocketOptionLevel.Socket,
                       SocketOptionName.ReuseAddress, true);""")

    note(d, "`NoDelay` haqida:",
         "Nagle algoritmi kichik paketlarni to'plab, birga yuboradi — "
         "bu tarmoq samaradorligini oshiradi, lekin kechikish qo'shadi. "
         "Interaktiv protokollarda (o'yin, chat) bu seziladi. Katta "
         "ma'lumot uzatishda esa uni o'chirish zarar qiladi.")

    # ───────────────────────────────────────────
    h1(d, "8. Tarmoq diagnostikasi")

    code(d, """// Mavjud interfeyslar
foreach (var ni in NetworkInterface.GetAllNetworkInterfaces())
{
    if (ni.OperationalStatus != OperationalStatus.Up) continue;

    Console.WriteLine($"{ni.Name} — {ni.NetworkInterfaceType}");

    foreach (var addr in ni.GetIPProperties().UnicastAddresses)
        Console.WriteLine($"   {addr.Address}");
}""")

    code(d, """// Band portlarni ko'rish
var properties = IPGlobalProperties.GetIPGlobalProperties();

var listeners = properties.GetActiveTcpListeners();
foreach (var listener in listeners.OrderBy(l => l.Port))
    Console.WriteLine($"{listener.Address}:{listener.Port}");""")

    code(d, """// Ping
using var ping = new Ping();
var reply = await ping.SendPingAsync("example.com", TimeSpan.FromSeconds(5));

Console.WriteLine($"{reply.Status} — {reply.RoundtripTime} ms");""")

    # ───────────────────────────────────────────
    h1(d, "9. Amaliy maslahatlar")

    bullets(d, [
        "Soketlarni `using` bilan yopish — ochiq qolgan soket resurs "
        "egallaydi.",
        "Har bir amalga kutish vaqti qo'yish — usiz ulanish abadiy "
        "osilib qolishi mumkin.",
        "`CancellationToken` ni barcha asinxron amallarga uzatish.",
        "Xom soket o'rniga yuqori darajadagi abstraksiyalarni afzal "
        "ko'rish — `HttpClient`, SignalR, gRPC.",
    ])

    note(d, "Oxirgi punkt eng muhimi:",
         "Men xom TCP bilan ishlashni o'rgandim, lekin amalda uni "
         "kamdan-kam ishlataman. Chunki qayta ulanish, xabar "
         "chegaralari, serializatsiya, xavfsizlik — bularning hammasini "
         "noldan yozish kerak bo'ladi. Tayyor kutubxona esa buni "
         "allaqachon hal qilgan. Xom soket faqat mavjud, lekin "
         "standart bo'lmagan protokol bilan ishlashda kerak bo'ladi.")

    # ───────────────────────────────────────────
    h1(d, "10. Xulosa")

    bullets(d, [
        "Tarmoq qatlamlarga bo'lingan; dasturchi ilova va transport "
        "qatlamlari bilan ishlaydi.",
        "TCP ulanishli va kafolatli, UDP ulanishsiz va tez.",
        "TCP ulanishi uch bosqichli qo'l berish bilan boshlanadi — "
        "shuning uchun ulanishni qayta ishlatish muhim.",
        "`IPEndPoint` manzil va portni birlashtiradi.",
        "TCP bayt oqimini kafolatlaydi, xabar chegaralarini emas — "
        "uzunlik prefiksi kerak.",
        "`ReadExactlyAsync` qisman o'qish muammosini hal qiladi.",
        "`NoDelay` kechikishni kamaytiradi, lekin tarmoq "
        "samaradorligini pasaytiradi.",
        "Amalda xom soket o'rniga yuqori darajadagi abstraksiyalar "
        "afzal.",
    ])

    sources(d, [
        ("Network programming in .NET",
         "https://learn.microsoft.com/en-us/dotnet/fundamentals/networking/"),
        ("Sockets — .NET",
         "https://learn.microsoft.com/en-us/dotnet/fundamentals/networking/sockets/sockets-overview"),
        ("TcpClient Class — .NET API",
         "https://learn.microsoft.com/en-us/dotnet/api/system.net.sockets.tcpclient"),
        ("RFC 9293 — Transmission Control Protocol",
         "https://www.rfc-editor.org/rfc/rfc9293"),
    ])
