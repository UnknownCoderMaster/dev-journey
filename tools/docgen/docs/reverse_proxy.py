# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "Reverse proxy server"
CATEGORY = "Web"
TITLE = "Reverse Proxy"
SUBTITLE = "Serverlar oldidagi oraliq qatlam va uning vazifalari"
FILENAME = "Reverse proxy server.docx"


def build(d):
    h1(d, "1. Forward va reverse proxy farqi")

    para(d, "Proxy — bu so'rovni o'zi orqali o'tkazuvchi oraliq server. Ikki turi bor "
            "va ular kim tomonda turishiga qarab farqlanadi.")

    code(d, """Forward proxy:
    Mijoz  →  [proxy]  →  Internet
    Mijozni yashiradi. Mijoz proxy haqida biladi.

Reverse proxy:
    Internet  →  [proxy]  →  Serverlar
    Serverlarni yashiradi. Mijoz proxy haqida bilmaydi.""")

    para(d, "Forward proxy odatda tashkilot ichida ishlatiladi — xodimlarning "
            "internetga chiqishini nazorat qilish uchun. Reverse proxy esa "
            "serverlar oldida turadi va tashqi mijozlar uchun u yagona kirish "
            "nuqtasi bo'lib ko'rinadi.")

    note(d, "Nomidagi \"reverse\" shuni bildiradi:",
         "Oddiy proxy mijoz nomidan ishlaydi, reverse proxy esa server nomidan. "
         "Mijoz `api.example.com` ga murojaat qilyapman deb o'ylaydi, aslida esa "
         "proxy bilan gaplashyapti va orqada nechta server borligini bilmaydi.")

    # ───────────────────────────────────────────
    h1(d, "2. Asosiy vazifalari")

    h2(d, "2.1 TLS tugatish")

    para(d, "Proxy HTTPS ulanishini qabul qiladi, shifrni ochadi va orqadagi "
            "serverlarga oddiy HTTP orqali uzatadi. Shunda sertifikat faqat bitta "
            "joyda boshqariladi.")

    code(d, """Internet  ──HTTPS──►  [Nginx]  ──HTTP──►  Kestrel (ichki tarmoq)""")

    note(d, "Bu amaliy jihatdan juda qulay:",
         "Sertifikat yangilanishi, TLS versiyalarini sozlash, zaif shifrlarni "
         "o'chirish — hammasi bitta joyda. Orqada o'nta xizmat bo'lsa ham, ularning "
         "hech biri sertifikat haqida bilmaydi. Ichki tarmoq ishonchli bo'lsa, bu "
         "xavfsiz yondashuv.")

    h2(d, "2.2 Yuk taqsimlash")

    code(d, """upstream api_backend {
    least_conn;
    server 10.0.1.10:8080;
    server 10.0.1.11:8080;
    server 10.0.1.12:8080 backup;
}

server {
    listen 443 ssl;
    server_name api.example.com;

    location / {
        proxy_pass http://api_backend;
    }
}""")

    table(d, ["Algoritm", "Qanday taqsimlaydi"],
          [["Round-robin", "Navbat bilan, teng"],
           ["`least_conn`", "Eng kam faol ulanishi bor serverga"],
           ["`ip_hash`", "Bir mijozni doim bitta serverga"],
           ["Weighted", "Quvvatiga mos ravishda"]],
          widths=[3.6, 11.9])

    h2(d, "2.3 Bitta domenda bir nechta xizmat")

    code(d, """location /api/     { proxy_pass http://localhost:8080/; }
location /auth/    { proxy_pass http://localhost:8081/; }
location /files/   { proxy_pass http://localhost:9000/; }
location /         { root /var/www/frontend; try_files $uri /index.html; }""")

    para(d, "Mijoz uchun bularning hammasi bitta sayt bo'lib ko'rinadi. Bu CORS "
            "muammosini ham yo'qotadi — hammasi bitta origin da.")

    h2(d, "2.4 Statik fayllar va keshlash")

    code(d, """location /static/ {
    root /var/www;
    expires 30d;
    add_header Cache-Control "public, immutable";
}""")

    para(d, "Statik faylni Nginx berishi ilova serveridan ancha samaraliroq — ilova "
            "jarayoni band qilinmaydi.")

    h2(d, "2.5 Himoya qatlami")

    code(d, """limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;

location /api/ {
    limit_req zone=api burst=20 nodelay;
    limit_req_status 429;

    client_max_body_size 10m;
    proxy_pass http://api_backend;
}""")

    # ───────────────────────────────────────────
    h1(d, "3. Sarlavhalarni uzatish")

    para(d, "Proxy ortida ilova mijozni to'g'ridan-to'g'ri ko'rmaydi. Haqiqiy IP, "
            "protokol va host nomi maxsus sarlavhalarda uzatiladi:")

    code(d, """location /api/ {
    proxy_pass http://api_backend;

    proxy_set_header Host              $host;
    proxy_set_header X-Real-IP         $remote_addr;
    proxy_set_header X-Forwarded-For   $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}""")

    code(d, """app.UseForwardedHeaders(new ForwardedHeadersOptions
{
    ForwardedHeaders = ForwardedHeaders.XForwardedFor
                     | ForwardedHeaders.XForwardedProto
                     | ForwardedHeaders.XForwardedHost,

    KnownProxies = { IPAddress.Parse("10.0.1.1") }
});""")

    note(d, "`KnownProxies` ni bo'sh qoldirmaslik kerak:",
         "`X-Forwarded-For` sarlavhasini har qanday mijoz o'zi yuborishi mumkin. "
         "Agar ilova uni tekshirmasdan qabul qilsa, foydalanuvchi o'z IP sini "
         "soxtalashtirib, IP bo'yicha cheklovlarni chetlab o'ta oladi. "
         "`KnownProxies` yoki `KnownNetworks` ko'rsatilsa, faqat ishonchli "
         "proxy dan kelgan sarlavhaga ishoniladi.")

    note(d, "Bu middleware tartibi ham muhim:",
         "`UseForwardedHeaders` zanjirning eng boshida, `UseHttpsRedirection` dan "
         "oldin turishi kerak. Aks holda ilova so'rovni HTTP deb o'ylab, uni "
         "HTTPS ga yo'naltiradi va cheksiz yo'naltirish sikli hosil bo'ladi.")

    # ───────────────────────────────────────────
    h1(d, "4. WebSocket va SignalR")

    para(d, "WebSocket ulanishi oddiy HTTP so'rovdan boshlanadi va keyin protokol "
            "almashtiriladi. Proxy buni qo'llab-quvvatlashi uchun maxsus sozlama "
            "kerak:")

    code(d, """location /hubs/ {
    proxy_pass http://api_backend;

    proxy_http_version 1.1;
    proxy_set_header Upgrade    $http_upgrade;
    proxy_set_header Connection "upgrade";

    proxy_read_timeout 3600s;    # uzun ulanish uzilmasin
}""")

    note(d, "Bu sozlama tushib qolsa, nosozlikni topish qiyin:",
         "SignalR ishlaydi, lekin doim Long Polling ga tushadi va sekin bo'ladi. "
         "Xatolik chiqmaydi, chunki zaxira transport ishlayveradi. Ulanish "
         "tafsilotiga qaramaguningizcha muammo ko'rinmaydi.")

    # ───────────────────────────────────────────
    h1(d, "5. YARP — .NET dagi reverse proxy")

    para(d, "Agar proxy mantiqi murakkab bo'lsa va uni kodda yozish qulayroq bo'lsa, "
            "Microsoft ning YARP kutubxonasi ishlatiladi.")

    code(d, """dotnet add package Yarp.ReverseProxy""")

    code(d, """builder.Services.AddReverseProxy()
    .LoadFromConfig(builder.Configuration.GetSection("ReverseProxy"));

var app = builder.Build();
app.MapReverseProxy();""")

    code(d, """{
  "ReverseProxy": {
    "Routes": {
      "books": {
        "ClusterId": "booksCluster",
        "Match": { "Path": "/api/books/{**catch-all}" }
      }
    },
    "Clusters": {
      "booksCluster": {
        "LoadBalancingPolicy": "LeastRequests",
        "Destinations": {
          "d1": { "Address": "http://10.0.1.10:8080/" },
          "d2": { "Address": "http://10.0.1.11:8080/" }
        }
      }
    }
  }
}""")

    para(d, "YARP ning afzalligi — marshrutlash qoidalarini `.NET` kodida yozish "
            "va ularni ish vaqtida o'zgartirish mumkin. Kamchiligi — Nginx ga "
            "nisbatan ko'proq resurs talab qiladi.")

    # ───────────────────────────────────────────
    h1(d, "6. Xulosa")

    bullets(d, [
        "Forward proxy mijozni, reverse proxy serverlarni yashiradi.",
        "Asosiy vazifalari: TLS tugatish, yuk taqsimlash, marshrutlash, keshlash, "
        "so'rov sonini cheklash.",
        "Bir nechta xizmatni bitta domenda birlashtirish CORS muammosini yo'qotadi.",
        "Haqiqiy mijoz IP si `X-Forwarded-For` orqali keladi; uni "
        "`UseForwardedHeaders` bilan o'qish kerak.",
        "`KnownProxies` ko'rsatilmasa, IP ni soxtalashtirish mumkin bo'lib qoladi.",
        "WebSocket uchun `Upgrade` va `Connection` sarlavhalarini uzatish shart.",
        "YARP — `.NET` da yozilgan, konfiguratsiyasi kodda boshqariladigan proxy.",
    ])

    sources(d, [
        ("Host ASP.NET Core on Linux with Nginx",
         "https://learn.microsoft.com/en-us/aspnet/core/host-and-deploy/linux-nginx"),
        ("Configure ASP.NET Core to work with proxy servers and load balancers",
         "https://learn.microsoft.com/en-us/aspnet/core/host-and-deploy/proxy-load-balancer"),
        ("YARP — Yet Another Reverse Proxy",
         "https://microsoft.github.io/reverse-proxy/"),
        ("NGINX reverse proxy — hujjat",
         "https://docs.nginx.com/nginx/admin-guide/web-server/reverse-proxy/"),
    ])
