# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "IP4 and IP6 (Local and intranet and Global IPs)"
CATEGORY = "Web"
TITLE = "IPv4 va IPv6 Manzillari"
SUBTITLE = "Lokal, ichki tarmoq va global manzillar farqi"
FILENAME = "IP4 and IP6 (Local and intranet and Global IPs).docx"


def build(d):
    h1(d, "1. IP manzil nima uchun kerak")

    para(d, "Tarmoqdagi har bir qurilma boshqalar unga murojaat qila olishi uchun "
            "manzilga ega bo'lishi kerak. IP manzil shu vazifani bajaradi — u paketning "
            "qayerga borishi kerakligini bildiradi.")

    para(d, "Ikki versiya mavjud: IPv4 va IPv6. Ular bir vaqtda ishlaydi va ko'p "
            "qurilmalarda ikkalasi ham faol bo'ladi.")

    # ───────────────────────────────────────────
    h1(d, "2. IPv4")

    para(d, "IPv4 manzil 32 bitdan iborat va odatda nuqta bilan ajratilgan to'rtta son "
            "shaklida yoziladi. Har bir son 0 dan 255 gacha bo'ladi:")

    code(d, """192.168.1.10
10.0.0.5
203.0.113.42""")

    para(d, "32 bit jami 4 294 967 296 ta manzil beradi. Bu 1980-yillarda juda ko'p "
            "tuyulgan, lekin hozirgi qurilmalar soni uchun yetarli emas. Aynan shu "
            "sababli IPv6 yaratilgan.")

    h2(d, "2.1 Tarmoq niqobi va CIDR")

    para(d, "Manzilning bir qismi tarmoqni, qolgani esa qurilmani bildiradi. Chegara "
            "CIDR yozuvida ko'rsatiladi:")

    code(d, """192.168.1.0/24

  /24  →  birinchi 24 bit tarmoq, oxirgi 8 bit qurilma
         ya'ni 192.168.1.1 dan 192.168.1.254 gacha, 254 ta qurilma""")

    table(d, ["Prefiks", "Qurilmalar soni"],
          [["`/30`", "2"],
           ["`/24`", "254"],
           ["`/16`", "65 534"],
           ["`/8`", "16 777 214"]],
          widths=[3.4, 12.1])

    # ───────────────────────────────────────────
    h1(d, "3. Manzil turlari")

    h2(d, "3.1 Loopback — o'ziga murojaat")

    code(d, """127.0.0.1        # IPv4
::1              # IPv6
localhost        # ikkalasiga ham ishora qilishi mumkin""")

    para(d, "Loopback manzili paketni tarmoqqa umuman chiqarmaydi — u shu qurilmaning "
            "o'ziga qaytadi. Shuning uchun bu manzilga bog'langan xizmat tashqaridan "
            "ko'rinmaydi.")

    note(d, "Bu meni bir marta chalkashtirgan:",
         "`localhost` ba'zi tizimlarda avval `::1` ga, ya'ni IPv6 loopback ga "
         "aylantiriladi. Agar xizmatim faqat `127.0.0.1` ni tinglayotgan bo'lsa, "
         "`localhost` orqali ulanish ishlamasligi mumkin. Bunday holatda `127.0.0.1` "
         "ni to'g'ridan-to'g'ri yozib ko'rish — birinchi tekshiruv.")

    h2(d, "3.2 Xususiy (ichki tarmoq) manzillar")

    para(d, "Ba'zi diapazonlar ataylab internetda marshrutlanmaydi. Ular faqat ichki "
            "tarmoqda ishlaydi va har bir tashkilotda takrorlanishi mumkin:")

    table(d, ["Diapazon", "CIDR", "Qayerda uchraydi"],
          [["10.0.0.0 – 10.255.255.255", "`10.0.0.0/8`", "Yirik korporativ tarmoqlar"],
           ["172.16.0.0 – 172.31.255.255", "`172.16.0.0/12`", "Docker tarmoqlari"],
           ["192.168.0.0 – 192.168.255.255", "`192.168.0.0/16`", "Uy routerlari"]],
          widths=[5.6, 3.9, 6.0])

    para(d, "Shu sababli uyingizdagi kompyuter ham, qo'shningizniki ham "
            "`192.168.1.10` bo'lishi mumkin — ular turli tarmoqlarda.")

    h2(d, "3.3 Global (ommaviy) manzillar")

    para(d, "Global manzil internetda noyob bo'ladi va uni provayder beradi. Aynan shu "
            "manzil orqali tashqi dunyo qurilmani ko'radi.")

    para(d, "Ichki manzildan internetga chiqishda NAT mexanizmi ishlaydi — router "
            "barcha ichki qurilmalarni o'zining bitta global manzili ortida "
            "yashiradi.")

    note(d, "NAT shuning uchun muhim:",
         "Ichki tarmoqdagi qurilma internetga o'zi murojaat qila oladi, lekin "
         "tashqaridan unga to'g'ridan-to'g'ri ulanib bo'lmaydi — chunki uning global "
         "manzili yo'q. Serverni uyda joylashtirmoqchi bo'lganda aynan shu muammoga "
         "duch kelinadi va uni port forwarding orqali hal qilish kerak bo'ladi.")

    h2(d, "3.4 Boshqa maxsus diapazonlar")

    bullets(d, [
        "`0.0.0.0` — \"barcha interfeyslar\"; xizmat shu manzilga bog'langanda "
        "u har qanday tarmoq kartasidan kelgan so'rovni qabul qiladi.",
        "`169.254.0.0/16` — DHCP ishlamaganda qurilma o'ziga beradigan manzil; "
        "odatda tarmoq nosozligining belgisi.",
        "`255.255.255.255` — tarmoqdagi hammaga broadcast.",
    ])

    # ───────────────────────────────────────────
    h1(d, "4. IPv6")

    para(d, "IPv6 manzil 128 bitdan iborat va o'n oltilik sanoq sistemasida, ikki "
            "nuqta bilan ajratilgan sakkizta guruh shaklida yoziladi:")

    code(d, """2001:0db8:85a3:0000:0000:8a2e:0370:7334""")

    h2(d, "4.1 Qisqartirish qoidalari")

    code(d, """2001:0db8:85a3:0000:0000:8a2e:0370:7334

# 1. Guruh boshidagi nollar tashlanadi
2001:db8:85a3:0:0:8a2e:370:7334

# 2. Ketma-ket nol guruhlar :: bilan almashtiriladi (faqat bir marta)
2001:db8:85a3::8a2e:370:7334""")

    para(d, "`::` butun manzilda faqat bir marta ishlatilishi mumkin — aks holda nechta "
            "guruh yashiringanini aniqlab bo'lmaydi.")

    h2(d, "4.2 IPv6 manzil turlari")

    table(d, ["Prefiks", "Turi", "IPv4 dagi o'xshashi"],
          [["`::1`", "Loopback", "`127.0.0.1`"],
           ["`fe80::/10`", "Link-local — faqat shu tarmoq segmentida", "`169.254.x.x`"],
           ["`fc00::/7`", "Unique local — ichki tarmoq", "`192.168.x.x`"],
           ["`2000::/3`", "Global unicast — internetda", "Ommaviy IPv4"]],
          widths=[3.2, 7.0, 5.3])

    note(d, "IPv6 da NAT deyarli kerak emas:",
         "Manzillar shunchalik ko'pki, har bir qurilmaga global manzil berish mumkin. "
         "Bu aslida internetning dastlabki g'oyasiga qaytish — har bir qurilma "
         "to'g'ridan-to'g'ri murojaat qilinadigan bo'lishi. Lekin bu xavfsizlik "
         "masalasini ham o'zgartiradi: endi himoyani NAT emas, firewall ta'minlaydi.")

    h2(d, "4.3 Port bilan yozilishi")

    para(d, "IPv6 manzilida ikki nuqta ko'p bo'lgani uchun port bilan yozishda manzil "
            "kvadrat qavsga olinadi:")

    code(d, """http://[2001:db8::1]:8080/api/books
http://192.168.1.10:8080/api/books""")

    # ───────────────────────────────────────────
    h1(d, "5. .NET da IP manzillar bilan ishlash")

    code(d, """// Matndan manzilga
var ip = IPAddress.Parse("192.168.1.10");
Console.WriteLine(ip.AddressFamily);   // InterNetwork (IPv4)

var v6 = IPAddress.Parse("2001:db8::1");
Console.WriteLine(v6.AddressFamily);   // InterNetworkV6

// Loopback ekanini tekshirish
Console.WriteLine(IPAddress.IsLoopback(ip));

// Xavfsiz tahlil
if (IPAddress.TryParse(input, out var parsed)) { ... }""")

    h2(d, "5.1 So'rov kelgan manzilni olish")

    code(d, """app.MapGet("/whoami", (HttpContext ctx) =>
{
    var ip = ctx.Connection.RemoteIpAddress;

    // IPv4 ko'rinishiga keltirish (IPv6 ga o'ralgan bo'lsa)
    if (ip is not null && ip.IsIPv4MappedToIPv6)
        ip = ip.MapToIPv4();

    return Results.Ok(new { ip = ip?.ToString() });
});""")

    note(d, "Bu yerda tez-tez uchraydigan hodisa:",
         "IPv4 manzil `::ffff:192.168.1.10` ko'rinishida kelishi mumkin — bu IPv6 "
         "ichiga o'ralgan IPv4. Agar men IP manzilni bazaga yozayotgan yoki ro'yxat "
         "bilan solishtirayotgan bo'lsam, avval uni oddiy ko'rinishga keltirishim kerak. "
         "Aks holda bir xil manzil ikki xil yozuvda saqlanib qoladi.")

    h2(d, "5.2 Diapazonga tekshirish")

    code(d, """var network = IPNetwork.Parse("10.0.0.0/8");
var client = IPAddress.Parse("10.1.2.3");

if (network.Contains(client))
{
    // ichki tarmoqdan kelgan so'rov
}""")

    # ───────────────────────────────────────────
    h1(d, "6. Amaliy tekshiruv buyruqlari")

    code(d, """ipconfig /all          # Windows: barcha interfeyslar
ip addr show           # Linux

ping 8.8.8.8           # IPv4 ulanish bormi
ping -6 2001:4860:4860::8888   # IPv6 ulanish bormi

nslookup example.com   # domen qaysi manzilga ishora qilyapti
tracert example.com    # paket qaysi yo'ldan ketyapti""")

    # ───────────────────────────────────────────
    h1(d, "7. Xulosa")

    bullets(d, [
        "IPv4 — 32 bit, IPv6 — 128 bit; ikkalasi parallel ishlaydi.",
        "`127.0.0.1` va `::1` — loopback, paket tarmoqqa chiqmaydi.",
        "`10.x`, `172.16–31.x`, `192.168.x` — xususiy diapazonlar, internetda "
        "marshrutlanmaydi.",
        "`0.0.0.0` — barcha interfeyslarni tinglash; konteynerda shu kerak bo'ladi.",
        "NAT ichki manzillarni bitta global manzil ortida yashiradi.",
        "IPv6 da nol guruhlar `::` bilan qisqartiriladi, lekin faqat bir marta.",
        "IPv6 manzil port bilan yozilganda kvadrat qavsga olinadi.",
        "`::ffff:` prefiksli manzil — IPv6 ga o'ralgan IPv4; uni "
        "`MapToIPv4()` bilan normallashtirish kerak.",
    ])

    sources(d, [
        ("RFC 1918 — Address Allocation for Private Internets",
         "https://www.rfc-editor.org/rfc/rfc1918"),
        ("RFC 4291 — IP Version 6 Addressing Architecture",
         "https://www.rfc-editor.org/rfc/rfc4291"),
        ("IPAddress Class — .NET API",
         "https://learn.microsoft.com/en-us/dotnet/api/system.net.ipaddress"),
    ])
