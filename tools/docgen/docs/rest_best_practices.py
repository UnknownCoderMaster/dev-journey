# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "REST API best practices (versioning, pagination, HATEOAS)"
CATEGORY = "Web"
TITLE = "REST API Yaxshi Amaliyotlari"
SUBTITLE = "Nomlash, sahifalash, versiyalash va HATEOAS"
FILENAME = "REST API best practices (versioning, pagination, HATEOAS).docx"


def build(d):
    h1(d, "1. REST ning asoslari")

    para(d, "REST — bu protokol emas, arxitektura uslubi. U HTTP ning mavjud "
            "imkoniyatlaridan to'liq foydalanishni taklif qiladi: metodlar amalni, "
            "status kodlar natijani, URL esa resursni bildiradi.")

    table(d, ["Metod", "Ma'nosi", "Idempotentmi"],
          [["`GET`", "O'qish", "Ha"],
           ["`POST`", "Yangi yaratish", "Yo'q"],
           ["`PUT`", "To'liq almashtirish", "Ha"],
           ["`PATCH`", "Qisman yangilash", "Odatda yo'q"],
           ["`DELETE`", "O'chirish", "Ha"]],
          widths=[3.0, 7.0, 5.5])

    para(d, "Idempotentlik — bir xil so'rovni bir necha marta yuborish natijani "
            "o'zgartirmasligi. Bu tarmoq uzilishida qayta urinish uchun muhim: "
            "`PUT` ni ikki marta yuborish xavfsiz, `POST` ni esa yo'q.")

    note(d, "Bu tafsilot amalda ko'p ishga yaraydi:",
         "Agar mijoz javob olmasa, u so'rovni qayta yuboradi. `POST` bilan bu "
         "ikkita buyurtma yaratilishiga olib keladi. Shuning uchun yaratish "
         "so'rovlariga idempotentlik kalitini qo'shaman — mijoz bir xil kalit "
         "bilan ikki marta yuborsa, ikkinchisida avvalgi natija qaytadi.")

    code(d, """POST /orders
Idempotency-Key: 7f3a9c12-...""")

    # ───────────────────────────────────────────
    h1(d, "2. Status kodlar")

    table(d, ["Kod", "Qachon"],
          [["200 OK", "Muvaffaqiyatli o'qish yoki yangilash"],
           ["201 Created", "Yangi resurs yaratildi; `Location` sarlavhasi bilan"],
           ["204 No Content", "Bajarildi, qaytaradigan tana yo'q"],
           ["400 Bad Request", "So'rov formati yoki qiymatlari noto'g'ri"],
           ["401 Unauthorized", "Kim ekani aniqlanmadi"],
           ["403 Forbidden", "Kim ekani aniq, lekin ruxsat yo'q"],
           ["404 Not Found", "Resurs topilmadi"],
           ["409 Conflict", "Joriy holat bilan ziddiyat"],
           ["422 Unprocessable", "Format to'g'ri, lekin biznes qoidasi buzildi"],
           ["429 Too Many Requests", "So'rov chegarasi oshdi"]],
          widths=[4.2, 11.3])

    note(d, "401 va 403 ni chalkashtirish keng tarqalgan:",
         "401 — \"sen kimligingni bilmayman, tanishtir\". 403 — \"kimligingni "
         "bilaman, lekin bunga haqqing yo'q\". Birinchisida mijoz tizimga kirishga "
         "urinishi mantiqiy, ikkinchisida esa qayta urinish hech narsani "
         "o'zgartirmaydi.")

    code(d, """[HttpPost]
public async Task<IActionResult> Create(CreateBookDto dto)
{
    var book = await _service.CreateAsync(dto);
    return CreatedAtAction(nameof(GetById), new { id = book.Id }, book);
    // 201 + Location: /api/books/42
}""")

    # ───────────────────────────────────────────
    h1(d, "3. Sahifalash")

    para(d, "Katta to'plamni to'liq qaytarish mumkin emas — u ham serverni, ham "
            "mijozni bosadi. Ikki yondashuv mavjud.")

    h2(d, "3.1 Offset bo'yicha")

    code(d, """GET /books?page=3&size=20""")

    code(d, """var total = await query.CountAsync(ct);
var items = await query
    .OrderBy(b => b.Id)
    .Skip((page - 1) * size)
    .Take(size)
    .ToListAsync(ct);

return Ok(new
{
    items,
    page,
    size,
    total,
    totalPages = (int)Math.Ceiling(total / (double)size)
});""")

    para(d, "Afzalligi — sahifa raqamiga to'g'ridan-to'g'ri o'tish mumkin. "
            "Kamchiligi ikkita: `OFFSET` kattalashganda baza baribir tashlab "
            "yuboriladigan satrlarni o'qiydi, va yangi yozuv qo'shilsa, sahifalar "
            "siljib ketadi.")

    h2(d, "3.2 Kursor bo'yicha")

    code(d, """GET /books?after=eyJpZCI6NDJ9&size=20""")

    code(d, """var items = await query
    .Where(b => b.Id > lastSeenId)
    .OrderBy(b => b.Id)
    .Take(size)
    .ToListAsync(ct);""")

    para(d, "Bu usulda `OFFSET` umuman ishlatilmaydi — shart indeks bo'yicha "
            "bajariladi va sahifa qanchalik uzoq bo'lsa ham tezlik o'zgarmaydi. "
            "Yangi yozuvlar ham natijani siljitmaydi.")

    note(d, "Qaysi birini qachon tanlayman:",
         "Agar foydalanuvchi sahifa raqamlarini bosadigan bo'lsa — offset. Agar "
         "cheksiz aylantirish (infinite scroll) bo'lsa yoki ro'yxat katta bo'lsa — "
         "kursor. Yuz mingdan ortiq yozuvda offset sezilarli sekinlashadi va bu "
         "faqat ma'lumot ko'payganda bilinadi.")

    h2(d, "3.3 Chegaralarni majburlash")

    code(d, """size = Math.Clamp(size, 1, 100);   // mijoz 100000 so'ramasin""")

    para(d, "Bu kichik satr himoya vazifasini bajaradi — usiz bitta so'rov butun "
            "jadvalni o'qib, xotirani to'ldirishi mumkin.")

    # ───────────────────────────────────────────
    h1(d, "4. Filtrlash va saralash")

    code(d, """GET /books?category=fiction&minPrice=50000&sort=-publishedAt,title""")

    code(d, """// Saralashda faqat ruxsat etilgan maydonlar
private static readonly Dictionary<string, Expression<Func<Book, object>>> Sortable =
    new()
    {
        ["title"] = b => b.Title,
        ["publishedAt"] = b => b.PublishedAt,
        ["price"] = b => b.Price
    };""")

    note(d, "Oq ro'yxat shart:",
         "Saralash maydonini to'g'ridan-to'g'ri mijozdan olib ishlatish xavfli — "
         "bu ichki ustun nomlarini ochadi va indekssiz ustun bo'yicha og'ir so'rov "
         "yuborish imkonini beradi. Ruxsat etilganlar ro'yxati bu ikkala xavfni "
         "ham yopadi.")

    # ───────────────────────────────────────────
    h1(d, "5. Versiyalash")

    para(d, "API chop etilgandan keyin undan foydalanuvchilar paydo bo'ladi va "
            "buzuvchi o'zgarish ularni sindiradi. Versiyalash bu muammoni hal "
            "qiladi.")

    code(d, """/api/v1/books                    # URL segmenti — eng keng tarqalgan
X-Api-Version: 1.0                # sarlavha
Accept: application/json;v=1.0    # media tip""")

    bullets(d, [
        "Maydon qo'shish — buzuvchi emas, yangi versiya kerak emas.",
        "Maydonni o'chirish, nomini yoki tipini o'zgartirish — buzuvchi.",
        "Bir vaqtda ikkitadan ortiq versiyani qo'llab-quvvatlamaslik.",
        "Eskirgan versiyani o'chirish muddatini oldindan e'lon qilish.",
    ])

    note(d, "Eng yaxshi versiya — chiqarilmagan versiya:",
         "Har bir yangi versiya — ikki barobar test, ikki barobar hujjat va ikki "
         "barobar xatolik tuzatish. Shuning uchun o'zgarishni mavjud versiyaga "
         "qo'shimcha sifatida kiritish imkonini oxirigacha izlayman. Ko'p hollarda "
         "yangi ixtiyoriy maydon yetarli bo'ladi.")

    # ───────────────────────────────────────────
    h1(d, "6. HATEOAS")

    para(d, "HATEOAS — Hypermedia as the Engine of Application State. G'oya shundaki, "
            "javob nafaqat ma'lumotni, balki keyingi mumkin bo'lgan amallarni "
            "havolalar shaklida ham qaytaradi.")

    code(d, """{
  "id": 42,
  "status": "Pending",
  "total": 150000,
  "_links": {
    "self":   { "href": "/api/orders/42", "method": "GET" },
    "pay":    { "href": "/api/orders/42/payment", "method": "POST" },
    "cancel": { "href": "/api/orders/42", "method": "DELETE" }
  }
}""")

    para(d, "Buyurtma to'langandan keyin javobdagi havolalar o'zgaradi — `pay` va "
            "`cancel` yo'qoladi, o'rniga `refund` paydo bo'ladi. Shunda mijoz qaysi "
            "amal mumkinligini o'zi hisoblamaydi, server aytadi.")

    h2(d, "6.1 Amalda qanchalik ishlatiladi")

    para(d, "HATEOAS Roy Fielding ning REST ta'rifida majburiy shart sifatida "
            "ko'rsatilgan, lekin amalda kam qo'llaniladi. Sabablar:")

    bullets(d, [
        "Javob hajmi sezilarli oshadi.",
        "Mijoz ilovalari baribir manzillarni kodga yozib qo'yadi.",
        "Frontend jamoalari odatda havolalardan foydalanmaydi.",
        "Qo'shimcha kod yozish va uni qo'llab-quvvatlash kerak.",
    ])

    note(d, "Mening munosabatim:",
         "To'liq HATEOAS ni deyarli hech qachon ishlatmayman. Lekin uning bitta "
         "g'oyasini olaman — javobda **qaysi amallar mumkinligini** ko'rsatish. "
         "Bu havola shaklida bo'lishi shart emas, oddiy ro'yxat ham bo'ladi. "
         "Shunda frontend tugmalarni yoqish-o'chirishni o'zi hisoblamaydi va "
         "biznes qoidasi bir joyda qoladi.")

    code(d, """{
  "id": 42,
  "status": "Pending",
  "allowedActions": ["pay", "cancel"]
}""")

    # ───────────────────────────────────────────
    h1(d, "7. Qolgan muhim nuqtalar")

    bullets(d, [
        "**Entity emas, DTO qaytarish** — ichki maydonlar tashqariga chiqmasin.",
        "**Xatolikni standart formatda berish** — `ProblemDetails` (RFC 9457).",
        "**Sanalarni UTC va ISO 8601 da uzatish** — `2026-10-31T14:30:00Z`.",
        "**Pul miqdorini `decimal` da va valyuta bilan birga berish.**",
        "**`PATCH` uchun aniq semantika tanlash** — JSON Merge Patch yoki "
        "JSON Patch.",
        "**So'rov chegarasini qo'yish** va `429` bilan birga `Retry-After` "
        "sarlavhasini qaytarish.",
        "**Keshlash sarlavhalarini ishlatish** — `ETag`, `Cache-Control`.",
    ])

    code(d, """// ETag bilan shartli so'rov
var etag = $"\\"{book.RowVersion}\\"";
if (Request.Headers.IfNoneMatch == etag)
    return StatusCode(StatusCodes.Status304NotModified);

Response.Headers.ETag = etag;
return Ok(dto);""")

    # ───────────────────────────────────────────
    h1(d, "8. Xulosa")

    bullets(d, [
        "HTTP metodlari amalni, status kodlar natijani bildiradi — ularni "
        "to'g'ri ishlatish REST ning asosi.",
        "`PUT` va `DELETE` idempotent, `POST` esa yo'q — qayta urinishda bu "
        "muhim.",
        "401 — kim ekani noma'lum, 403 — ruxsat yo'q.",
        "Offset sahifalash sahifa raqamlari uchun, kursor sahifalash katta "
        "to'plamlar uchun.",
        "Sahifa hajmini majburan cheklash kerak.",
        "Saralash maydonlari oq ro'yxatdan olinishi shart.",
        "Yangi versiyani faqat buzuvchi o'zgarishda chiqarish.",
        "To'liq HATEOAS kam ishlatiladi, lekin \"mumkin bo'lgan amallar\" "
        "g'oyasi foydali.",
    ])

    sources(d, [
        ("Web API design best practices — Azure Architecture Center",
         "https://learn.microsoft.com/en-us/azure/architecture/best-practices/api-design"),
        ("RFC 9110 — HTTP Semantics",
         "https://www.rfc-editor.org/rfc/rfc9110.html"),
        ("RFC 9457 — Problem Details for HTTP APIs",
         "https://www.rfc-editor.org/rfc/rfc9457.html"),
        ("Architectural Styles and the Design of Network-based Software "
         "Architectures — Roy Fielding",
         "https://ics.uci.edu/~fielding/pubs/dissertation/rest_arch_style.htm"),
    ])
