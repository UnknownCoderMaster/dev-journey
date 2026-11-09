# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "Spatial Data, NetTopologySuite, Longitude and Latitude"
CATEGORY = "EF Core"
TITLE = "Fazoviy Ma'lumotlar va NetTopologySuite"
SUBTITLE = "Koordinatalar bilan ishlash, masofa hisoblash va geografik so'rovlar"
FILENAME = "Spatial Data, NetTopologySuite, Longitude and Latitude.docx"


def build(d):
    h1(d, "1. Fazoviy ma'lumot nima")

    para(d, "Fazoviy (spatial) ma'lumot — bu fazoda joylashuvni ifodalovchi qiymatlar: "
            "nuqta, chiziq, ko'pburchak. Eng keng tarqalgan holati — geografik "
            "koordinata, ya'ni yer yuzidagi aniq joy.")

    para(d, "Bunday ma'lumotni ikkita oddiy `double` ustunida saqlash ham mumkin, lekin "
            "u holda \"shu nuqtadan 5 kilometr radiusda nima bor\" kabi savollarga javob "
            "berish murakkablashadi. Fazoviy tiplar aynan shunday so'rovlar uchun "
            "mo'ljallangan.")

    note(d, "Nima uchun men bu mavzuga alohida to'xtaldim:",
         "Boshida koordinatalarni ikkita `double` ustun sifatida saqlab, masofani "
         "C# da hisoblardim. Bu ishlaydi, lekin faqat kichik ma'lumotda — chunki "
         "\"yaqin joylashgan nuqtalarni top\" degan so'rov uchun butun jadvalni o'qib "
         "chiqishga to'g'ri keladi. Baza tomonidagi fazoviy indeks esa shu ishni "
         "o'nlab marta tezroq bajaradi.")

    # ───────────────────────────────────────────
    h1(d, "2. NetTopologySuite")

    para(d, ".NET da fazoviy tiplar `NetTopologySuite` kutubxonasi orqali beriladi. "
            "EF Core uning tiplarini to'g'ridan-to'g'ri qo'llab-quvvatlaydi — alohida "
            "konverter yozish shart emas.")

    table(d, ["Tip", "Nimani ifodalaydi"],
          [["`Point`", "Bitta nuqta — koordinata"],
           ["`LineString`", "Nuqtalar ketma-ketligi — yo'l, marshrut"],
           ["`Polygon`", "Yopiq soha — tuman chegarasi, yetkazib berish zonasi"],
           ["`MultiPolygon`", "Bir nechta aloqasiz soha"],
           ["`Geometry`", "Yuqoridagilarning barchasi uchun umumiy bazaviy tip"]],
          widths=[3.6, 11.9])

    h2(d, "2.1 O'rnatish")

    code(d, """dotnet add package Npgsql.EntityFrameworkCore.PostgreSQL.NetTopologySuite""",
         caption="PostgreSQL uchun")

    code(d, """options.UseNpgsql(connectionString, o => o.UseNetTopologySuite());""")

    para(d, "PostgreSQL tomonida PostGIS kengaytmasi yoqilgan bo'lishi kerak:")

    code(d, """CREATE EXTENSION IF NOT EXISTS postgis;""")

    para(d, "SQL Server uchun esa `Microsoft.EntityFrameworkCore.SqlServer.NetTopologySuite` "
            "paketi va `UseNetTopologySuite()` chaqiruvi ishlatiladi; bazada qo'shimcha "
            "kengaytma kerak emas.")

    # ───────────────────────────────────────────
    h1(d, "3. Longitude va Latitude — tartib masalasi")

    para(d, "Geografik koordinata ikki sondan iborat:")

    bullets(d, [
        "**Latitude (kenglik)** — ekvatordan shimol yoki janubga og'ish, −90 dan +90 gacha.",
        "**Longitude (uzunlik)** — Grinvich meridianidan sharq yoki g'arbga og'ish, "
        "−180 dan +180 gacha.",
    ])

    para(d, "NetTopologySuite da `Point` konstruktori `(x, y)` tartibida qiymat oladi. "
            "Geografik kontekstda `x` — longitude, `y` — latitude:")

    code(d, """// To'g'ri: avval longitude, keyin latitude
var tashkent = new Point(69.2401, 41.2995) { SRID = 4326 };

// Noto'g'ri — nuqta butunlay boshqa joyga tushadi
var wrong = new Point(41.2995, 69.2401) { SRID = 4326 };""")

    note(d, "Bu eng ko'p uchraydigan xato:",
         "Odamlar odatda koordinatani \"41.2995, 69.2401\" shaklida — ya'ni latitude "
         "birinchi bo'lib — yozadi. Xaritalar, GPS, Google Maps hammasi shu tartibda. "
         "NetTopologySuite esa teskari tartibda kutadi. Agar men bunga e'tibor bermasam, "
         "Toshkent o'rniga Hindiston okeanidagi nuqta hosil bo'ladi va kod hech qanday "
         "xatolik bermaydi — shunchaki natija noto'g'ri chiqadi.")

    note(d, "O'zimni himoyalash usuli:",
         "Men `Point` ni to'g'ridan-to'g'ri yaratmayman, balki nomlangan parametrli "
         "kichik yordamchi metod yozaman. Shunda chaqirish joyida tartib aniq ko'rinadi "
         "va adashish imkoni qolmaydi.")

    code(d, """public static Point CreateLocation(double latitude, double longitude)
    => new Point(longitude, latitude) { SRID = 4326 };

// Chaqirish — tartib nomidan ko'rinib turibdi
var p = CreateLocation(latitude: 41.2995, longitude: 69.2401);""")

    h2(d, "3.1 SRID nima")

    para(d, "`SRID` — koordinata tizimining identifikatori. `4326` qiymati WGS 84 "
            "tizimini bildiradi; bu GPS va deyarli barcha xarita xizmatlari ishlatadigan "
            "standart. SRID ko'rsatilmasa, hisoblashlar noto'g'ri tizimda bajarilishi "
            "mumkin.")

    # ───────────────────────────────────────────
    h1(d, "4. Modelda ishlatish")

    code(d, """public class Branch
{
    public int Id { get; set; }
    public string Name { get; set; }
    public Point Location { get; set; }
}""")

    code(d, """modelBuilder.Entity<Branch>(e =>
{
    e.Property(b => b.Location)
     .HasColumnType("geography (point, 4326)");

    e.HasIndex(b => b.Location)
     .HasMethod("gist");          // fazoviy indeks
});""")

    para(d, "`gist` indeksi fazoviy so'rovlar uchun zarur — usiz radius bo'yicha qidiruv "
            "butun jadvalni skan qiladi.")

    h2(d, "4.1 geography va geometry farqi")

    para(d, "PostGIS ikki xil tipni taklif qiladi. `geometry` tekislikdagi hisoblash "
            "qiladi — tez, lekin katta masofalarda xato beradi. `geography` yerning "
            "sharsimon shaklini hisobga oladi — biroz sekinroq, lekin masofalar haqiqiy "
            "metrlarda chiqadi.")

    para(d, "Shahar ichidagi ob'ektlar uchun farq sezilmaydi, lekin mamlakat miqyosidagi "
            "masofalarda `geography` ni tanlagan ma'qul.")

    # ───────────────────────────────────────────
    h1(d, "5. Fazoviy so'rovlar")

    h2(d, "5.1 Masofa bo'yicha qidiruv")

    code(d, """var me = CreateLocation(latitude: 41.3111, longitude: 69.2797);

var nearby = await db.Branches
    .Where(b => b.Location.Distance(me) < 3000)   // 3 km
    .OrderBy(b => b.Location.Distance(me))
    .Take(10)
    .ToListAsync();""")

    para(d, "`geography` tipida `Distance` natijasi metrlarda qaytadi. Bu so'rov bazada "
            "`ST_Distance` funksiyasiga aylanadi va fazoviy indeksdan foydalanadi.")

    h2(d, "5.2 Soha ichidami")

    code(d, """var zone = new Polygon(new LinearRing(new[]
{
    new Coordinate(69.20, 41.28),
    new Coordinate(69.30, 41.28),
    new Coordinate(69.30, 41.35),
    new Coordinate(69.20, 41.35),
    new Coordinate(69.20, 41.28),   // yopilishi shart
})) { SRID = 4326 };

var inside = await db.Branches
    .Where(b => zone.Contains(b.Location))
    .ToListAsync();""")

    para(d, "Ko'pburchakning birinchi va oxirgi nuqtasi bir xil bo'lishi shart — aks "
            "holda u yopiq shakl deb hisoblanmaydi va xatolik beriladi.")

    h2(d, "5.3 Boshqa foydali metodlar")

    table(d, ["Metod", "Vazifasi"],
          [["`Distance(other)`", "Ikki geometriya orasidagi masofa"],
           ["`Contains(other)`", "Boshqa geometriyani to'liq o'z ichiga oladimi"],
           ["`Intersects(other)`", "Kesishadimi"],
           ["`Buffer(radius)`", "Atrofida berilgan radiusli soha hosil qiladi"],
           ["`Within(other)`", "O'zi boshqasining ichidami"]],
          widths=[4.6, 10.9])

    # ───────────────────────────────────────────
    h1(d, "6. Amaliy maslahatlar")

    bullets(d, [
        "Fazoviy indeksni unutmaslik — usiz radius qidiruvi butun jadvalni o'qiydi.",
        "`SRID` ni har doim aniq belgilash; aralash SRID li geometriyalarni taqqoslash "
        "xatolikka olib keladi.",
        "Migration yaratishdan oldin PostGIS kengaytmasi yoqilganiga ishonch hosil qilish.",
        "`Distance` ni `Where` ichida ishlatganda uni hisoblangan ustunga aylantirmaslik "
        "— EF Core uni bazada hisoblashi kerak.",
    ])

    note(d, "Eslab qoladigan asosiy narsa:",
         "Fazoviy ma'lumot bilan ishlashdagi aksariyat muammolar koordinata tartibidan "
         "yoki tushib qolgan SRID dan kelib chiqadi. Ikkalasi ham xatolik bermaydi — "
         "shunchaki noto'g'ri natija beradi. Shuning uchun men birinchi so'rovni "
         "yozganimda natijani albatta xaritada tekshirib ko'raman.")

    # ───────────────────────────────────────────
    h1(d, "7. Xulosa")

    bullets(d, [
        "Fazoviy tiplar EF Core ga NetTopologySuite orqali qo'shiladi.",
        "PostgreSQL da PostGIS kengaytmasi va `UseNetTopologySuite()` kerak.",
        "`Point(x, y)` da `x` — longitude, `y` — latitude; bu odatdagi yozuvga teskari.",
        "`SRID = 4326` — GPS va xarita xizmatlari uchun standart koordinata tizimi.",
        "`geography` haqiqiy masofalarni, `geometry` tekislikdagi hisoblashni beradi.",
        "`gist` indeksi fazoviy so'rovlar uchun majburiy hisoblanadi.",
    ])

    sources(d, [
        ("Spatial Data — EF Core",
         "https://learn.microsoft.com/en-us/ef/core/modeling/spatial"),
        ("NetTopologySuite — rasmiy sayt",
         "https://nettopologysuite.github.io/NetTopologySuite/"),
        ("Spatial Data — Npgsql EF Core provayderi",
         "https://www.npgsql.org/efcore/mapping/nts.html"),
        ("PostGIS — hujjat",
         "https://postgis.net/documentation/"),
    ])
