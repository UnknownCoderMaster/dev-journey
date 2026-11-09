# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "Port (qancha va qaysilarini ishlatsa bo'ladi)"
CATEGORY = "Web"
TITLE = "Portlar"
SUBTITLE = "Nechta port bor, qaysilarini ishlatish mumkin"
FILENAME = "Port (qancha va qaysilarini ishlatsa boladi).docx"


def build(d):
    h1(d, "1. Port nima")

    para(d, "IP manzil paketni qaysi qurilmaga yetkazishni bildiradi, port esa o'sha "
            "qurilmadagi qaysi dasturga topshirishni bildiradi. Bitta serverda bir "
            "vaqtda o'nlab xizmat ishlashi mumkin va ularni ajratib turadigan narsa "
            "aynan port.")

    code(d, """192.168.1.10 : 5432     →  PostgreSQL
192.168.1.10 : 6379     →  Redis
192.168.1.10 : 8080     →  mening API im""")

    para(d, "Ulanish to'liq to'rtlik bilan aniqlanadi: manba IP, manba port, maqsad IP, "
            "maqsad port. Shuning uchun bitta server portiga minglab mijoz bir vaqtda "
            "ulanishi mumkin — ularning manba portlari har xil bo'ladi.")

    note(d, "Bu savolga javob bera olmay qolgandim:",
         "\"Bitta port bitta ulanish degani emasmi?\" degan savol tug'ilgandi. Yo'q — "
         "server 8080 portini tinglaydi, lekin har bir mijoz ulanishi alohida soket "
         "sifatida qayd etiladi. Chegara port emas, operatsion tizimdagi fayl "
         "deskriptorlari va xotira.")

    # ───────────────────────────────────────────
    h1(d, "2. Nechta port bor")

    para(d, "Port raqami 16 bitli son, ya'ni **0 dan 65535 gacha**. Jami 65 536 ta "
            "qiymat, lekin `0` maxsus ma'noga ega va odatda ishlatilmaydi.")

    para(d, "IANA tashkiloti bu diapazonni uch qismga bo'lgan:")

    table(d, ["Diapazon", "Nomi", "Kim ishlatadi"],
          [["0 – 1023", "Well-known (tizim)", "Standart xizmatlar; ko'pincha "
            "administrator huquqi kerak"],
           ["1024 – 49151", "Registered", "Ro'yxatdan o'tgan ilovalar"],
           ["49152 – 65535", "Dynamic / Ephemeral", "Operatsion tizim chiquvchi "
            "ulanishlarga vaqtincha beradi"]],
          widths=[3.2, 3.8, 8.5])

    # ───────────────────────────────────────────
    h1(d, "3. Keng tarqalgan portlar")

    table(d, ["Port", "Xizmat"],
          [["22", "SSH"],
           ["53", "DNS"],
           ["80", "HTTP"],
           ["443", "HTTPS"],
           ["1433", "SQL Server"],
           ["3306", "MySQL / MariaDB"],
           ["5432", "PostgreSQL"],
           ["5672", "RabbitMQ (AMQP)"],
           ["6379", "Redis"],
           ["9000", "MinIO"],
           ["15672", "RabbitMQ boshqaruv paneli"]],
          widths=[2.6, 12.9])

    para(d, "Bu raqamlarni yodlash shart emas, lekin asosiylarini bilish nosozlikni "
            "topishda vaqt tejaydi.")

    # ───────────────────────────────────────────
    h1(d, "4. Qaysi portni tanlash kerak")

    para(d, "O'z ilovam uchun port tanlashda quyidagi qoidalarga amal qilaman:")

    bullets(d, [
        "**1024 dan past portlardan qochish.** Ular tizim portlari va Linux da ularga "
        "bog'lanish uchun root huquqi kerak bo'ladi.",
        "**Mashhur xizmatlar portlarini band qilmaslik.** 3306 yoki 5432 ni o'z "
        "ilovamga berish keyinchalik chalkashlik tug'diradi.",
        "**49152 dan yuqorisidan qochish.** Bu diapazondan operatsion tizim chiquvchi "
        "ulanishlarga port beradi va to'qnashuv bo'lishi mumkin.",
        "**Qolgan oraliqni tanlash** — amalda 5000–9999 va 10000–40000 oralig'i "
        "qulay.",
    ])

    note(d, "Oxirgi punkt bo'yicha haqiqiy voqea:",
         "Men lokal ilovamga 50000 atrofidagi portni tanlagandim va u ba'zan ishga "
         "tushmay qolardi — \"address already in use\" deb xatolik berardi, lekin "
         "o'sha portda hech qanday xizmat ko'rinmasdi. Sabab shundaki, operatsion "
         "tizim o'sha paytda o'sha portni chiquvchi ulanish uchun vaqtincha band "
         "qilgan ekan. Portni 8000-larga ko'chirganimdan keyin muammo yo'qoldi.")

    h2(d, "4.1 .NET dagi odatdagi portlar")

    para(d, "ASP.NET Core shabloni odatda 5000–5300 oralig'idan tasodifiy port tanlaydi "
            "va uni `launchSettings.json` ga yozib qo'yadi. Bu lokal ishlash uchun "
            "qulay, lekin serverda port aniq belgilangani ma'qul.")

    code(d, """ASPNETCORE_URLS=http://+:8080""")

    # ───────────────────────────────────────────
    h1(d, "5. Port to'qnashuvi")

    para(d, "Ikki dastur bitta portni bir vaqtda tinglay olmaydi. Urinish quyidagi "
            "xatolik bilan tugaydi:")

    code(d, """System.IO.IOException: Failed to bind to address http://127.0.0.1:5000:
address already in use.""")

    h2(d, "5.1 Portni kim band qilganini topish")

    code(d, """# Windows
netstat -ano | findstr :5432
tasklist /FI "PID eq 4756"

# Linux / macOS
ss -tlnp | grep 5432
lsof -i :5432""")

    note(d, "Bu tekshiruv menga bir muammoni hal qilishda juda asqotgan:",
         "Docker konteyneri va alohida o'rnatilgan xizmat bir xil portni band "
         "qilmoqchi bo'lgandi. Qiziq tomoni shundaki, Docker `0.0.0.0` ga, ikkinchi "
         "dastur esa `127.0.0.1` ga bog'langan edi — Windows bunga ruxsat beradi, "
         "lekin `localhost` orqali ulanganda aniqroq manzil, ya'ni `127.0.0.1` "
         "g'olib chiqadi. Natijada men bir xizmatga ulanyapman deb o'ylab, butunlay "
         "boshqasiga tushgandim.")

    note(d, "Shundan chiqargan xulosam:",
         "Port band bo'lsa, uni \"o'ldirish\" birinchi yechim emas. Avval kim band "
         "qilganini va nima uchun kerakligini aniqlash kerak. Ko'p holatda o'z "
         "xizmatimni boshqa portga ko'chirish xavfsizroq va tezroq yechim bo'ladi.")

    h2(d, "5.2 Bo'sh portni avtomatik olish")

    code(d, """// Port 0 — operatsion tizim bo'sh portni o'zi tanlaydi
options.Listen(IPAddress.Loopback, 0);""")

    para(d, "Bu usul avtomatlashtirilgan testlarda qulay — parallel ishlayotgan "
            "testlar bir-birining portini band qilmaydi.")

    # ───────────────────────────────────────────
    h1(d, "6. Docker da portlar")

    code(d, """services:
  api:
    ports:
      - "8080:8080"     # host:konteyner
  db:
    ports:
      - "5434:5432"     # tashqarida 5434, ichkarida 5432""")

    para(d, "Chapdagi raqam — host mashinasidagi port, o'ngdagisi — konteyner "
            "ichidagi. Ular har xil bo'lishi mumkin va bu portlar to'qnashuvini hal "
            "qilishning eng oddiy usuli.")

    para(d, "Konteynerlar bir-biri bilan gaplashganda esa host porti umuman "
            "ishlatilmaydi — ular ichki tarmoqda xizmat nomi va ichki port orqali "
            "topishadi:")

    code(d, """Host=db;Port=5432       # konteynerdan konteynerga
Host=localhost;Port=5434  # host mashinasidan konteynerga""")

    note(d, "Bu farqni tushunmaslik ko'p vaqt oladi:",
         "Men ulanish satrida host portini yozib, konteyner ichidan ulanmoqchi "
         "bo'lgandim va u ishlamasdi. Konteyner uchun tashqi port mavjud emas — "
         "u faqat host mashinasi uchun ochilgan eshik.")

    # ───────────────────────────────────────────
    h1(d, "7. Xavfsizlik")

    bullets(d, [
        "Faqat kerakli portlarni tashqariga ochish; baza portini internetga "
        "chiqarmaslik.",
        "Docker da baza uchun `ports` bo'limini umuman yozmaslik — konteynerlar "
        "bir-birini ichki tarmoqda topadi.",
        "Boshqaruv panellari (RabbitMQ 15672, MinIO konsoli) ichki tarmoqda "
        "qoldirilishi yoki parol bilan himoyalanishi kerak.",
        "Firewall da sukut bo'yicha hamma narsani yopib, kerakligini ochish "
        "tamoyiliga amal qilish.",
    ])

    code(d, """services:
  db:
    image: postgres:17
    # ports bo'limi yo'q — faqat ichki tarmoqda ko'rinadi
    networks: [backend]""")

    # ───────────────────────────────────────────
    h1(d, "8. Xulosa")

    bullets(d, [
        "Port — 16 bitli son, 0 dan 65535 gacha; jami 65 536 ta qiymat.",
        "0–1023 tizim portlari, 1024–49151 ro'yxatdan o'tganlar, 49152–65535 "
        "vaqtinchalik.",
        "O'z ilovam uchun 5000–40000 oralig'idan tanlash xavfsiz.",
        "Bitta portni ikki dastur tinglay olmaydi; `netstat`, `ss` yoki `lsof` "
        "kim band qilganini ko'rsatadi.",
        "Port 0 berilsa, operatsion tizim bo'sh portni o'zi tanlaydi — testlarda "
        "qulay.",
        "Docker da `host:konteyner` ko'rinishi ikki alohida portni bog'laydi; "
        "konteynerlar o'zaro ichki portdan foydalanadi.",
        "Baza portlarini tashqariga ochmaslik kerak.",
    ])

    sources(d, [
        ("Service Name and Transport Protocol Port Number Registry — IANA",
         "https://www.iana.org/assignments/service-names-port-numbers/service-names-port-numbers.xhtml"),
        ("RFC 6335 — IANA Procedures for Port Number Registry",
         "https://www.rfc-editor.org/rfc/rfc6335"),
        ("Configure endpoints for the ASP.NET Core Kestrel web server",
         "https://learn.microsoft.com/en-us/aspnet/core/fundamentals/servers/kestrel/endpoints"),
    ])
