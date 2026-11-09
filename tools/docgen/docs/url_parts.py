# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "URL (origin, port, path, resource, query) query vs path"
CATEGORY = "Web"
TITLE = "URL Tuzilmasi"
SUBTITLE = "Origin, path, query — va qachon qaysi birini tanlash kerak"
FILENAME = "URL (origin, port, path, resource, query) query vs path.docx"


def build(d):
    h1(d, "1. URL ning qismlari")

    para(d, "URL resursning manzilini bildiradi va bir nechta qismdan iborat. Quyidagi "
            "misolda barcha qismlar ko'rsatilgan:")

    code(d, """https://api.example.com:8443/v1/books/42?lang=uz&full=true#reviews
└─┬─┘  └───────┬────────┘└─┬─┘└────┬──────┘└───────┬────────┘└──┬───┘
scheme      host         port    path           query       fragment

└──────────── origin ──────────┘""")

    table(d, ["Qism", "Vazifasi"],
          [["Scheme", "Qaysi protokol ishlatiladi: `https`, `http`, `ws`, `ftp`"],
           ["Host", "Qaysi serverga murojaat qilinadi"],
           ["Port", "Serverning qaysi xizmatiga; standart bo'lsa yozilmaydi"],
           ["Path", "Server ichida qaysi resurs"],
           ["Query", "Resursga qo'shimcha parametrlar"],
           ["Fragment", "Sahifa ichidagi joy; serverga **umuman yuborilmaydi**"]],
          widths=[3.0, 12.5])

    note(d, "Fragment haqidagi tafsilot ko'pchilikka noma'lum:",
         "`#reviews` qismini brauzer serverga yubormaydi — u faqat brauzer ichida "
         "ishlatiladi. Shuning uchun server loglarida uni hech qachon ko'rmaysiz va "
         "server mantiqida unga tayanib bo'lmaydi. Buni bilmasdan turib bir marta "
         "fragment orqali ma'lumot uzatmoqchi bo'lgandim.")

    # ───────────────────────────────────────────
    h1(d, "2. Origin")

    para(d, "Origin — scheme, host va portning birikmasi. U brauzer xavfsizlik "
            "modelidagi asosiy tushuncha hisoblanadi.")

    code(d, """https://api.example.com:8443   →  origin

Bir xil origin:
  https://api.example.com/books
  https://api.example.com/users

Boshqa origin:
  http://api.example.com     (scheme boshqa)
  https://www.example.com    (host boshqa)
  https://api.example.com:9000  (port boshqa)""")

    para(d, "Brauzer bir origin dagi sahifaga boshqa origin ga so'rov yuborishni "
            "cheklaydi. Buni ochish uchun server CORS sarlavhalarini qaytarishi kerak:")

    code(d, """builder.Services.AddCors(options =>
{
    options.AddPolicy("frontend", policy =>
        policy.WithOrigins("https://app.example.com")
              .AllowAnyHeader()
              .AllowAnyMethod()
              .AllowCredentials());
});

app.UseCors("frontend");""")

    note(d, "CORS haqida eng ko'p tarqalgan tushunmovchilik:",
         "CORS — bu serverni himoya qilish emas, brauzerni cheklash. Server baribir "
         "so'rovni qabul qiladi; brauzer esa javobni JavaScript ga ko'rsatmaydi. "
         "Shuning uchun `curl` yoki Postman orqali so'rov muammosiz ishlaydi, "
         "brauzerda esa xatolik chiqadi. Bu farqni bilmasdan turib \"API ishlayapti-ku\" "
         "deb vaqt yo'qotish oson.")

    # ───────────────────────────────────────────
    h1(d, "3. Path va resurs")

    para(d, "Path serverdagi resursni ko'rsatadi. REST yondashuvida path ierarxik "
            "tuzilmani aks ettiradi:")

    code(d, """/books                 # barcha kitoblar
/books/42              # 42-raqamli kitob
/books/42/reviews      # o'sha kitobning izohlari
/books/42/reviews/7    # aniq bitta izoh""")

    bullets(d, [
        "Resurs nomlari **ot** shaklida va **ko'plikda** yoziladi: `/books`, `/users`.",
        "Fe'l ishlatilmaydi — amalni HTTP metodi bildiradi: `GET /books`, "
        "`DELETE /books/42`.",
        "Pastki chiziq o'rniga defis ishlatiladi: `/order-items`, `/order_items` emas.",
        "Kichik harf ishlatiladi — ba'zi serverlarda path registrga sezgir.",
    ])

    code(d, """// Noto'g'ri
GET  /getBooks
POST /createBook
POST /deleteBook?id=42

// To'g'ri
GET    /books
POST   /books
DELETE /books/42""")

    # ───────────────────────────────────────────
    h1(d, "4. Query")

    para(d, "Query qismi `?` dan keyin boshlanadi va `&` bilan ajratilgan "
            "kalit-qiymat juftliklaridan iborat:")

    code(d, """/books?category=fiction&page=2&size=20&sort=title""")

    h2(d, "4.1 Kodlash")

    para(d, "Query qiymatida maxsus belgilar bo'lsa, ular kodlanishi shart:")

    code(d, """/books?title=Alisher%20Navoiy&tag=she%27riyat

bo'shliq  →  %20 yoki +
&         →  %26
?         →  %3F
'         →  %27""")

    code(d, """// .NET da
var url = QueryHelpers.AddQueryString("/books", new Dictionary<string, string?>
{
    ["title"] = "Alisher Navoiy",
    ["page"] = "2"
});""")

    # ───────────────────────────────────────────
    h1(d, "5. Query va path — qachon qaysi biri")

    para(d, "Bu eng ko'p savol tug'diradigan masala. Oddiy qoida quyidagicha:")

    table(d, ["Path ishlatiladi", "Query ishlatiladi"],
          [["Resursni **aniqlash**", "Natijani **o'zgartirish**"],
           ["Majburiy qism", "Ixtiyoriy qism"],
           ["Ierarxiyaning bir bo'g'ini", "Filtrlash, saralash, sahifalash"],
           ["`/books/42`", "`/books?category=fiction`"],
           ["`/users/7/orders`", "`/orders?status=paid&page=3`"]],
          widths=[7.7, 7.8])

    para(d, "Boshqacha aytganda: path savolning \"nima?\" qismiga, query esa "
            "\"qanday ko'rinishda?\" qismiga javob beradi.")

    h2(d, "5.1 Tekshirish usuli")

    para(d, "Qaysi birini tanlashda o'zimga ikkita savol beraman:")

    bullets(d, [
        "**Bu qismsiz manzil ma'noga egami?** `/books/42` dan `42` ni olib tashlasam, "
        "boshqa resurs bo'ladi — demak bu path. `/books?page=2` dan `page` ni olib "
        "tashlasam, baribir kitoblar ro'yxati qoladi — demak bu query.",
        "**Bu qiymat bitta resursni ko'rsatadimi yoki to'plamni filtrlaydimi?** "
        "Birinchisi — path, ikkinchisi — query.",
    ], numbered=True)

    note(d, "Chegaraviy holatlar ham bor:",
         "`/books/search?q=navoiy` degan manzilda `search` aslida resurs emas, "
         "amal. Qat'iy REST nuqtai nazaridan bu noto'g'ri va `/books?q=navoiy` "
         "yozilishi kerak. Lekin amalda `search` ni alohida ajratish tushunarliroq "
         "bo'lishi mumkin. Men bunday holatlarda qoidaga emas, o'qiladigan "
         "ko'rinishga ustunlik beraman — asosiysi, butun API bo'ylab izchil "
         "bo'lsin.")

    h2(d, "5.2 Keshlash va xavfsizlikka ta'siri")

    bullets(d, [
        "Ikkalasi ham to'liq URL ning qismi sifatida keshlanadi — `/books?page=1` va "
        "`/books?page=2` alohida keshlanadi.",
        "Parametrlar tartibi ahamiyatsiz bo'lsa ham, kesh uchun turli URL hisoblanadi. "
        "Shuning uchun mijoz tomonida tartibni izchil saqlash foydali.",
        "**Query ga sezgir ma'lumot yozmaslik kerak** — u server loglariga, proxy "
        "loglariga va brauzer tarixiga tushadi.",
    ])

    note(d, "Oxirgi punkt jiddiy:",
         "Token yoki parolni query da uzatish — keng tarqalgan xato. U Referer "
         "sarlavhasi orqali uchinchi saytga ham ketib qolishi mumkin. Bunday "
         "ma'lumot sarlavhada yoki so'rov tanasida bo'lishi kerak.")

    # ───────────────────────────────────────────
    h1(d, "6. ASP.NET Core da ishlash")

    code(d, """[HttpGet("books/{id:int}")]
public async Task<IActionResult> GetById(
    int id,                                  // path dan
    [FromQuery] bool includeReviews = false) // query dan
{ ... }

[HttpGet("books")]
public async Task<IActionResult> Search(
    [FromQuery] string? category,
    [FromQuery] int page = 1,
    [FromQuery] int size = 20)
{ ... }""")

    h2(d, "6.1 Route cheklovlari")

    code(d, """[HttpGet("books/{id:int:min(1)}")]      // faqat musbat butun son
[HttpGet("users/{id:guid}")]            // faqat Guid
[HttpGet("reports/{date:datetime}")]    // sana""")

    para(d, "Cheklov mos kelmasa, so'rov bu endpoint ga umuman tushmaydi va 404 "
            "qaytariladi — kontroller ichida qo'shimcha tekshiruv yozish shart emas.")

    h2(d, "6.2 URL ni tahlil qilish")

    code(d, """var uri = new Uri("https://api.example.com:8443/v1/books/42?lang=uz#reviews");

uri.Scheme     // https
uri.Host       // api.example.com
uri.Port       // 8443
uri.AbsolutePath  // /v1/books/42
uri.Query      // ?lang=uz
uri.Fragment   // #reviews

var q = QueryHelpers.ParseQuery(uri.Query);
var lang = q["lang"];   // uz""")

    # ───────────────────────────────────────────
    h1(d, "7. Xulosa")

    bullets(d, [
        "URL qismlari: scheme, host, port, path, query, fragment.",
        "Fragment serverga yuborilmaydi — u faqat brauzer ichida ishlaydi.",
        "Origin = scheme + host + port; u CORS siyosatining asosi.",
        "CORS serverni emas, brauzerni cheklaydi — `curl` orqali so'rov baribir "
        "ishlaydi.",
        "Path resursni aniqlaydi, query natijani o'zgartiradi.",
        "Resurs nomlari ot va ko'plikda; amal HTTP metodi bilan bildiriladi.",
        "Query ga token yoki parol yozmaslik kerak — u loglarga va brauzer "
        "tarixiga tushadi.",
        "Route cheklovlari noto'g'ri formatdagi so'rovni kontrollerga "
        "yetkazmasdan rad etadi.",
    ])

    sources(d, [
        ("RFC 3986 — Uniform Resource Identifier (URI): Generic Syntax",
         "https://www.rfc-editor.org/rfc/rfc3986"),
        ("URL — MDN Web Docs",
         "https://developer.mozilla.org/en-US/docs/Web/URI"),
        ("Routing in ASP.NET Core",
         "https://learn.microsoft.com/en-us/aspnet/core/fundamentals/routing"),
        ("Enable CORS in ASP.NET Core",
         "https://learn.microsoft.com/en-us/aspnet/core/security/cors"),
    ])
