# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "OpenAPI vs. Swagger"
CATEGORY = "ASP.NET"
TITLE = "OpenAPI va Swagger — Farqi Nimada"
SUBTITLE = "Spetsifikatsiya, vositalar va nomlardagi chalkashlik"
FILENAME = "OpenAPI vs. Swagger.docx"


def build(d):
    h1(d, "1. Qisqa javob")

    para(d, "**OpenAPI** — bu spetsifikatsiya, ya'ni HTTP API ni qanday tasvirlash "
            "kerakligi haqidagi qoidalar to'plami. **Swagger** — shu spetsifikatsiya "
            "bilan ishlaydigan vositalar oilasining nomi.")

    para(d, "Boshqacha aytganda, OpenAPI — til, Swagger esa o'sha tilda yozilgan "
            "hujjatni o'qiydigan va yaratadigan dasturlar. Ularni chalkashtirish "
            "keng tarqalgan, chunki tarixan ikkalasi ham bitta nom bilan atalgan.")

    note(d, "Men buni shunday eslab qolganman:",
         "OpenAPI — bu JSON fayl ichidagi tuzilma. Swagger — o'sha faylni chiroyli "
         "sahifa qilib ko'rsatadigan vosita. Agar kimdir \"Swagger ni och\" desa, "
         "u odatda Swagger UI sahifasini nazarda tutadi, \"OpenAPI hujjati\" desa — "
         "`openapi.json` faylini.")

    # ───────────────────────────────────────────
    h1(d, "2. Nomlarning tarixi")

    para(d, "Chalkashlikning sababi tarixiy. Quyidagi bosqichlar nomlarning qanday "
            "ajralganini ko'rsatadi:")

    table(d, ["Davr", "Nima bo'lgan"],
          [["2011", "Swagger loyihasi Wordnik kompaniyasida boshlangan"],
           ["2015", "SmartBear Swagger ni sotib olgan"],
           ["2015", "Spetsifikatsiya OpenAPI Initiative ga topshirilgan"],
           ["2016", "Swagger 2.0 spetsifikatsiyasi OpenAPI 2.0 deb qayta nomlangan"],
           ["2017", "OpenAPI 3.0 chiqqan — endi \"Swagger\" nomi faqat vositalarga qoldi"],
           ["2021", "OpenAPI 3.1 chiqqan, JSON Schema bilan to'liq mos"]],
          widths=[2.6, 12.9])

    para(d, "Ya'ni 2016 yilgacha \"Swagger spetsifikatsiyasi\" degan ibora to'g'ri edi. "
            "Hozir esa spetsifikatsiya faqat OpenAPI deb ataladi.")

    # ───────────────────────────────────────────
    h1(d, "3. OpenAPI — spetsifikatsiya sifatida")

    para(d, "OpenAPI hujjati API ning to'liq tavsifini mashina o'qiy oladigan shaklda "
            "beradi: qanday yo'llar bor, ular qanday metodlarni qabul qiladi, qanday "
            "parametr va tana kutadi, qanday javob qaytaradi.")

    code(d, """{
  "openapi": "3.1.1",
  "info": { "title": "Books API", "version": "v1" },
  "paths": {
    "/api/books/{id}": {
      "get": {
        "parameters": [
          { "name": "id", "in": "path", "required": true,
            "schema": { "type": "integer" } }
        ],
        "responses": {
          "200": {
            "content": {
              "application/json": {
                "schema": { "$ref": "#/components/schemas/BookDto" }
              }
            }
          },
          "404": { "description": "Topilmadi" }
        }
      }
    }
  }
}""")

    para(d, "Bu fayl odam uchun emas, dasturlar uchun mo'ljallangan. Uning asosida "
            "hujjat sahifasi, mijoz kodi va testlar avtomatik hosil qilinadi.")

    h2(d, "3.1 Formatlar")

    para(d, "OpenAPI hujjati JSON yoki YAML da yozilishi mumkin — ikkalasi teng kuchga "
            "ega. YAML odam o'qishi uchun qulayroq, JSON esa dasturlar orasida uzatish "
            "uchun.")

    # ───────────────────────────────────────────
    h1(d, "4. Swagger — vositalar sifatida")

    table(d, ["Vosita", "Vazifasi"],
          [["Swagger UI", "OpenAPI hujjatini interaktiv sahifaga aylantiradi"],
           ["Swagger Editor", "Spetsifikatsiyani brauzerda yozish va tekshirish"],
           ["Swagger Codegen", "Hujjatdan mijoz va server kodini generatsiya qilish"],
           ["Swashbuckle", ".NET uchun OpenAPI hujjatini kod asosida yaratuvchi kutubxona"]],
          widths=[4.2, 11.3])

    para(d, "Birinchi uchtasi SmartBear mahsuloti; `Swashbuckle` esa jamoat loyihasi "
            "bo'lib, nomidan ko'rinib turganidek Swagger vositalari bilan ishlaydi.")

    note(d, "Bu joyda yana bitta chalkashlik bor:",
         "Swashbuckle `.NET` da OpenAPI hujjatini **yaratadi** va u bilan birga "
         "Swagger UI ni ham olib keladi. Shuning uchun ko'pchilik `.NET` dasturchilari "
         "\"Swagger\" deganda aslida Swashbuckle ni tushunadi. Lekin bular turli "
         "narsalar — Swashbuckle o'rniga boshqa kutubxona ishlatib, baribir Swagger UI "
         "dan foydalanish mumkin.")

    # ───────────────────────────────────────────
    h1(d, "5. OpenAPI alternativ vositalar bilan")

    para(d, "OpenAPI ochiq standart bo'lgani uchun uni ko'rsatish usuli Swagger UI bilan "
            "cheklanmaydi:")

    bullets(d, [
        "**Scalar** — zamonaviy ko'rinishli hujjat sahifasi, `.NET` bilan yaxshi "
        "integratsiyalangan.",
        "**Redoc** — uch ustunli, o'qishga mo'ljallangan hujjat ko'rinishi.",
        "**Stoplight Elements** — hujjat va sinov imkoniyatlarini birlashtiradi.",
        "**NSwag** — `.NET` va TypeScript uchun mijoz kodini generatsiya qiladi.",
    ])

    para(d, "Ularning hammasi bir xil `openapi.json` faylini o'qiydi. Ya'ni hujjat "
            "manbasi o'zgarmaydi, faqat ko'rsatish usuli almashadi.")

    # ───────────────────────────────────────────
    h1(d, "6. .NET dagi hozirgi holat")

    para(d, ".NET 9 dan boshlab vaziyat sezilarli o'zgardi. Avval Web API shabloni "
            "`Swashbuckle.AspNetCore` paketi bilan birga kelardi. .NET 9 da u shablondan "
            "olib tashlandi va o'rniga Microsoft ning o'z paketi qo'yildi:")

    code(d, """// .NET 9 va undan yuqori
builder.Services.AddOpenApi();

var app = builder.Build();
app.MapOpenApi();     // /openapi/v1.json manzilida hujjat""")

    para(d, "Muhim nuqta: `Microsoft.AspNetCore.OpenApi` faqat **hujjatni yaratadi**. "
            "U hech qanday ko'rish sahifasini o'z ichiga olmaydi. Sahifa kerak bo'lsa, "
            "uni alohida qo'shish kerak.")

    table(d, ["Versiya", "Shablondagi holat", "Sukutdagi OpenAPI versiyasi"],
          [[".NET 8 va pastroq", "Swashbuckle + Swagger UI", "3.0"],
           [".NET 9", "Microsoft.AspNetCore.OpenApi, UI yo'q", "3.0"],
           [".NET 10", "Microsoft.AspNetCore.OpenApi, UI yo'q", "3.1"]],
          widths=[3.6, 6.4, 5.5])

    note(d, "Birinchi marta duch kelganimda:",
         "Yangi loyiha yaratib, odatdagicha `/swagger` manziliga kirsam, hech narsa "
         "chiqmadi. Avvaliga nimanidir noto'g'ri qilgandek tuyuldi. Aslida esa shablon "
         "o'zgargan ekan — hujjat `/openapi/v1.json` da bor, lekin uni ko'rsatadigan "
         "sahifa yo'q. Buni bilgandan keyin hammasi joyiga tushdi.")

    note(d, "Swashbuckle o'lgan emas:",
         "Internetda \"Swashbuckle is dead\" degan sarlavhalarni ko'p uchratdim, lekin "
         "bu haqiqatga mos emas. U hali ham faol qo'llab-quvvatlanadi va 10.x "
         "versiyasi .NET 10 hamda OpenAPI 3.1 bilan ishlaydi. Shablondan olib "
         "tashlanish — bu \"endi ishlatilmaydi\" degani emas, balki \"endi sukutdagi "
         "tanlov emas\" degani.")

    # ───────────────────────────────────────────
    h1(d, "7. Qaysi atamani qachon ishlatish kerak")

    bullets(d, [
        "\"Swagger spetsifikatsiyasi\" emas — **OpenAPI spetsifikatsiyasi**.",
        "\"Swagger fayli\" emas — **OpenAPI hujjati**, ya'ni `openapi.json`.",
        "\"Swagger 3.1\" degan narsa yo'q — **OpenAPI 3.1** bor; Swagger ning "
        "oxirgi spetsifikatsiya versiyasi 2.0 bo'lgan.",
        "**Swagger UI** — aniq vositaning nomi, uni \"Swagger sahifasi\" deb "
        "umumlashtirmaslik kerak.",
    ])

    para(d, "Amaliyotda bu farqlar ko'pincha e'tiborsiz qoldiriladi va suhbatda muammo "
            "tug'dirmaydi. Lekin texnik hujjat yozayotganda yoki boshqa jamoa bilan "
            "integratsiya kelishuvini tuzayotganda aniq atama ishlatish chalkashlikni "
            "oldini oladi.")

    # ───────────────────────────────────────────
    h1(d, "8. Xulosa")

    bullets(d, [
        "OpenAPI — spetsifikatsiya, Swagger — u bilan ishlaydigan vositalar oilasi.",
        "2016 yilgacha spetsifikatsiya ham Swagger deb atalgan; shundan chalkashlik "
        "kelib chiqqan.",
        "Hozirgi spetsifikatsiya versiyalari: OpenAPI 3.0 va 3.1.",
        "Swagger UI — OpenAPI hujjatini ko'rsatuvchi vositalardan **biri**; Scalar, "
        "Redoc va boshqalar ham bor.",
        "`.NET 9` dan Web API shabloni `Microsoft.AspNetCore.OpenApi` ga o'tdi va u "
        "faqat hujjat yaratadi, sahifa bermaydi.",
        "`.NET 10` da sukutdagi chiqish formati OpenAPI 3.1 ga o'tdi.",
        "Swashbuckle hali ham qo'llab-quvvatlanadi, faqat endi sukutdagi tanlov emas.",
    ])

    sources(d, [
        ("OpenAPI Specification — rasmiy sayt",
         "https://spec.openapis.org/oas/latest.html"),
        ("OpenAPI Initiative — What is OpenAPI",
         "https://www.openapis.org/what-is-openapi"),
        ("Generate OpenAPI documents — ASP.NET Core",
         "https://learn.microsoft.com/en-us/aspnet/core/fundamentals/openapi/aspnetcore-openapi"),
        ("What's new in ASP.NET Core 10.0",
         "https://learn.microsoft.com/en-us/aspnet/core/release-notes/aspnetcore-10.0"),
        ("Swashbuckle.AspNetCore — GitHub",
         "https://github.com/domaindrivendev/Swashbuckle.AspNetCore"),
    ])
