# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "Browser (Localstorage and Cookie and Session)"
CATEGORY = "Web"
TITLE = "Brauzerda Ma'lumot Saqlash"
SUBTITLE = "Cookie, localStorage, sessionStorage va server sessiyasi"
FILENAME = "Browser (Localstorage and Cookie and Session).docx"


def build(d):
    h1(d, "1. Nima uchun saqlash kerak")

    para(d, "HTTP holatsiz protokol — har bir so'rov mustaqil va server oldingi "
            "so'rovni eslamaydi. Lekin ilovalarga holat kerak: kim kirganini, qanday "
            "til tanlanganini, savatda nima borligini bilish zarur.")

    para(d, "Bu holatni saqlashning bir necha usuli bor va ular imkoniyatlari hamda "
            "xavfsizligi bo'yicha jiddiy farq qiladi.")

    # ───────────────────────────────────────────
    h1(d, "2. Taqqoslash")

    table(d, ["Jihat", "Cookie", "localStorage", "sessionStorage"],
          [["Hajmi", "~4 KB", "~5–10 MB", "~5–10 MB"],
           ["So'rovga qo'shiladi", "Ha, avtomatik", "Yo'q", "Yo'q"],
           ["Yashash muddati", "Belgilanadi", "Cheksiz", "Tab yopilguncha"],
           ["JS dan o'qish", "HttpOnly bo'lmasa", "Ha", "Ha"],
           ["Tablar orasida", "Bo'lishiladi", "Bo'lishiladi", "Bo'lishilmaydi"],
           ["Server o'qiy oladimi", "Ha", "Yo'q", "Yo'q"]],
          widths=[3.4, 4.2, 4.0, 3.9])

    para(d, "Eng muhim farq birinchi ikki qatorda: cookie har bir so'rovga avtomatik "
            "qo'shiladi va server uni ko'radi; `localStorage` esa faqat brauzerda "
            "qoladi va uni serverga yuborish kod yozishni talab qiladi.")

    # ───────────────────────────────────────────
    h1(d, "3. Cookie")

    code(d, """Set-Cookie: session=abc123; Path=/; Max-Age=3600;
            HttpOnly; Secure; SameSite=Strict""")

    table(d, ["Atribut", "Ma'nosi"],
          [["`HttpOnly`", "JavaScript o'qiy olmaydi"],
           ["`Secure`", "Faqat HTTPS orqali yuboriladi"],
           ["`SameSite`", "Boshqa saytdan kelgan so'rovda yuborilishini cheklaydi"],
           ["`Max-Age` / `Expires`", "Qachon eskirishi"],
           ["`Path`", "Qaysi yo'llarga yuborilishi"],
           ["`Domain`", "Qaysi domenlarga yuborilishi"]],
          widths=[4.4, 11.1])

    h2(d, "3.1 SameSite qiymatlari")

    bullets(d, [
        "`Strict` — cookie faqat o'z saytidan kelgan so'rovda yuboriladi. Eng "
        "xavfsiz, lekin tashqi havola orqali kirganda foydalanuvchi tizimdan "
        "chiqqandek ko'rinadi.",
        "`Lax` — oddiy sahifa o'tishlarida yuboriladi, lekin `POST` va fon "
        "so'rovlarida yuborilmaydi. Hozirgi brauzerlarda sukutdagi qiymat.",
        "`None` — har doim yuboriladi, lekin `Secure` bilan birga bo'lishi shart.",
    ])

    code(d, """// ASP.NET Core da
Response.Cookies.Append("theme", "dark", new CookieOptions
{
    HttpOnly = true,
    Secure = true,
    SameSite = SameSiteMode.Strict,
    MaxAge = TimeSpan.FromDays(30)
});

var theme = Request.Cookies["theme"];
Response.Cookies.Delete("theme");""")

    note(d, "`HttpOnly` nega shunchalik muhim:",
         "Agar saytda XSS zaifligi bo'lsa, tajovuzkor JavaScript kodini ishga tushira "
         "oladi. `HttpOnly` qo'yilmagan cookie ni u bir satr kod bilan o'g'irlaydi va "
         "sessiyani egallaydi. `HttpOnly` qo'yilgan bo'lsa, JavaScript uni umuman "
         "ko'rmaydi. Shuning uchun autentifikatsiya cookie sida bu atribut "
         "majburiy deb hisoblayman.")

    # ───────────────────────────────────────────
    h1(d, "4. localStorage va sessionStorage")

    code(d, """// localStorage — brauzer yopilsa ham qoladi
localStorage.setItem("lang", "uz");
const lang = localStorage.getItem("lang");
localStorage.removeItem("lang");

// sessionStorage — tab yopilsa yo'qoladi
sessionStorage.setItem("draft", JSON.stringify(form));""")

    para(d, "Ikkalasi ham faqat matn saqlaydi, shuning uchun obyektni "
            "`JSON.stringify` bilan aylantirish kerak.")

    h2(d, "4.1 Nimalarni saqlash mumkin")

    bullets(d, [
        "Interfeys sozlamalari — mavzu, til, yig'ilgan panellar.",
        "Yuborilmagan qoralama matnlar.",
        "Oxirgi tanlangan filtrlar.",
    ])

    h2(d, "4.2 Nimalarni saqlamaslik kerak")

    bullets(d, [
        "Autentifikatsiya tokeni.",
        "Shaxsiy ma'lumotlar.",
        "To'lov ma'lumotlari.",
    ])

    note(d, "Token masalasi haqida alohida:",
         "JWT ni `localStorage` da saqlash juda keng tarqalgan amaliyot, lekin u XSS "
         "ga ochiq — har qanday JavaScript uni o'qiy oladi. `HttpOnly` cookie esa "
         "bunday emas. Buning evaziga CSRF xavfi paydo bo'ladi, lekin uni "
         "`SameSite` va anti-forgery token bilan yopish mumkin. Men mijoz tomoni "
         "bir xil domenda bo'lsa, cookie ni afzal ko'raman.")

    note(d, "Yana bir tafsilot:",
         "`localStorage` sinxron ishlaydi — ya'ni undan o'qish asosiy oqimni "
         "bloklaydi. Kichik qiymatlar uchun bu sezilmaydi, lekin unga katta JSON "
         "saqlab, uni tez-tez o'qisam, interfeys sekinlashishi mumkin. Katta "
         "hajm uchun IndexedDB mo'ljallangan.")

    # ───────────────────────────────────────────
    h1(d, "5. Server sessiyasi")

    para(d, "Sessiya — bu ma'lumotni serverda saqlab, mijozga faqat identifikator "
            "berish usuli. Cookie da uzun ma'lumot emas, qisqa kalit ketadi.")

    code(d, """Brauzer                     Server
   │                           │
   │  Set-Cookie: sid=abc123   │   sid=abc123 → { userId: 7, cart: [...] }
   │ ◄─────────────────────────│   (xotirada, Redis da yoki bazada)
   │                           │
   │  Cookie: sid=abc123       │
   │ ─────────────────────────►│   kalit bo'yicha ma'lumot topiladi""")

    code(d, """builder.Services.AddDistributedMemoryCache();
builder.Services.AddSession(options =>
{
    options.IdleTimeout = TimeSpan.FromMinutes(30);
    options.Cookie.HttpOnly = true;
    options.Cookie.IsEssential = true;
    options.Cookie.SecurePolicy = CookieSecurePolicy.Always;
});

var app = builder.Build();
app.UseSession();""")

    code(d, """HttpContext.Session.SetString("lang", "uz");
HttpContext.Session.SetInt32("userId", 7);

var lang = HttpContext.Session.GetString("lang");""")

    h2(d, "5.1 Bir nechta server nusxasi bilan")

    para(d, "`AddDistributedMemoryCache` nomi chalg'ituvchi — u aslida taqsimlangan "
            "emas, oddiy xotirada saqlaydi. Bir nechta server nusxasi bo'lsa, har "
            "biri o'z sessiyalarini biladi va foydalanuvchi boshqa nusxaga tushganda "
            "sessiya yo'qolgandek ko'rinadi.")

    code(d, """builder.Services.AddStackExchangeRedisCache(options =>
{
    options.Configuration = "localhost:6379";
    options.InstanceName = "myapp:";
});""")

    note(d, "Bu nomdagi chalkashlik meni ham tutgan:",
         "\"Distributed\" so'zini ko'rib, u avtomatik taqsimlanadi deb o'ylash oson. "
         "Aslida bu shunchaki taqsimlangan kesh interfeysining xotiradagi amalga "
         "oshirilishi. Haqiqiy taqsimlanish uchun Redis yoki baza kerak.")

    # ───────────────────────────────────────────
    h1(d, "6. API uchun qaysi birini tanlash")

    para(d, "Stateless API da server sessiyasi odatda ishlatilmaydi — u miqyoslashni "
            "qiyinlashtiradi. Amalda ikkita yondashuv qoladi:")

    table(d, ["Yondashuv", "Qulaylik", "Xavf"],
          [["`HttpOnly` cookie", "XSS ga chidamli, avtomatik yuboriladi",
            "CSRF; domenlararo ishlatish murakkab"],
           ["JWT + `localStorage`", "Domenlararo oson, mobil bilan bir xil",
            "XSS ga ochiq; tokenni bekor qilish qiyin"]],
          widths=[3.8, 6.0, 5.7])

    note(d, "Mening tanlovim sharoitga bog'liq:",
         "Agar frontend va API bitta domenda bo'lsa — `HttpOnly` cookie. Agar mobil "
         "ilova ham bo'lsa yoki frontend alohida domenda tursa — JWT, lekin uni "
         "qisqa muddatli qilib, yangilash tokenini `HttpOnly` cookie da saqlayman. "
         "Shunda XSS orqali o'g'irlangan token tez eskiradi.")

    # ───────────────────────────────────────────
    h1(d, "7. Xulosa")

    bullets(d, [
        "Cookie har so'rovga avtomatik qo'shiladi va server uni ko'radi; "
        "`localStorage` esa faqat brauzerda qoladi.",
        "`HttpOnly`, `Secure` va `SameSite` — autentifikatsiya cookie si uchun "
        "majburiy atributlar.",
        "`localStorage` brauzer yopilsa ham qoladi, `sessionStorage` tab bilan "
        "birga yo'qoladi.",
        "Token va shaxsiy ma'lumotlarni `localStorage` da saqlamaslik kerak — "
        "XSS ularni ochadi.",
        "Server sessiyasi ma'lumotni serverda, mijozda esa faqat kalitni saqlaydi.",
        "`AddDistributedMemoryCache` aslida taqsimlangan emas — bir nechta nusxa "
        "uchun Redis kerak.",
        "Bir domenda — `HttpOnly` cookie; domenlararo yoki mobil bilan — qisqa "
        "muddatli JWT.",
    ])

    sources(d, [
        ("Using HTTP cookies — MDN",
         "https://developer.mozilla.org/en-US/docs/Web/HTTP/Guides/Cookies"),
        ("Window.localStorage — MDN",
         "https://developer.mozilla.org/en-US/docs/Web/API/Window/localStorage"),
        ("Session and state management in ASP.NET Core",
         "https://learn.microsoft.com/en-us/aspnet/core/fundamentals/app-state"),
        ("SameSite cookies — MDN",
         "https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Set-Cookie/SameSite"),
    ])
