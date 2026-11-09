# -*- coding: utf-8 -*-
import os
from docbuild import *

TOPIC = "Change Tracking (AsNoTracking, Attached, Detached)"
CATEGORY = "EF Core"
TITLE = "Change Tracking"
SUBTITLE = "EF Core entity o'zgarishlarini qanday kuzatadi va buni qachon o'chirish kerak"
FILENAME = "Change Tracking (AsNoTracking, Attached, Detached).docx"

FIG = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "figures", "out", "entity_states.png")


def build(d):
    h1(d, "1. Change tracking nima")

    para(d, "Change tracking — `DbContext` ning o'zi bilgan entity larning holatini kuzatib "
            "borish mexanizmi. So'rov natijasida olingan yoki kontekstga qo'shilgan har bir "
            "obyekt kontekstning ichki ro'yxatiga joylashtiriladi va unga ma'lum bir holat "
            "(state) biriktiriladi.")

    para(d, "Kuzatuvning amaliy ma'nosi shundaki, `SaveChanges()` chaqirilganda EF Core "
            "qaysi obyektlar o'zgarganini mustaqil aniqlaydi. Dasturchi qaysi maydon "
            "o'zgarganini aytishi shart emas — kontekst buni dastlabki qiymatlar bilan "
            "taqqoslab o'zi topadi.")

    code(d, """var book = await db.Books.FirstAsync(b => b.Id == 5);
book.Price = 45_000;

// Hech qanday Update() chaqirilmagan, lekin o'zgarish saqlanadi
await db.SaveChangesAsync();""", caption="Kuzatuv tufayli Update() chaqirish shart emas")

    note(d, "Birinchi qaraganda sehrga o'xshaydi:",
         "Kod hech qayerda \"bu obyektni yangila\" demaydi, lekin baza yangilanadi. Sabab — "
         "kontekst obyektni o'qiganda uning barcha maydonlarining nusxasini (original values) "
         "saqlab qo'ygan. `SaveChanges()` paytida u joriy qiymatlarni o'sha nusxaga "
         "taqqoslaydi va farq topilgan maydonlarnigina `UPDATE` ga kiritadi.")

    # ───────────────────────────────────────────
    h1(d, "2. Entity holatlari")

    para(d, "EF Core da har bir kuzatilayotgan entity beshta holatdan birida bo'ladi. "
            "Holat `EntityState` sanab o'tiluvchi turi bilan ifodalanadi.")

    image(d, FIG, caption="Entity holatlari va ular orasidagi o'tishlar (o'zim tayyorlagan sxema)")

    table(d, ["Holat", "Ma'nosi", "SaveChanges natijasi"],
          [["`Detached`", "Kontekst bu obyektni kuzatmaydi", "Hech narsa"],
           ["`Added`", "Yangi obyekt, bazada hali yo'q", "`INSERT`"],
           ["`Unchanged`", "Bazadan o'qilgan, o'zgarmagan", "Hech narsa"],
           ["`Modified`", "Kamida bitta maydon o'zgargan", "`UPDATE`"],
           ["`Deleted`", "O'chirish uchun belgilangan", "`DELETE`"]],
          widths=[3.2, 6.3, 5.0])

    para(d, "Entity ning joriy holatini dasturiy tarzda ham tekshirish mumkin:")

    code(d, """var entry = db.Entry(book);

Console.WriteLine(entry.State);                    // Modified
Console.WriteLine(entry.Property(b => b.Price).IsModified);          // True
Console.WriteLine(entry.Property(b => b.Price).OriginalValue);       // eski qiymat
Console.WriteLine(entry.Property(b => b.Price).CurrentValue);        // yangi qiymat""")

    # ───────────────────────────────────────────
    h1(d, "3. AsNoTracking")

    para(d, "`AsNoTracking()` operatori so'rov natijasida olingan entity larni kuzatuvdan "
            "chiqaradi. Bunday obyektlar `Detached` holatida qoladi va ularga kiritilgan "
            "o'zgarishlar `SaveChanges()` tomonidan e'tiborga olinmaydi.")

    code(d, """var books = await db.Books
    .AsNoTracking()
    .Where(b => b.Price > 50_000)
    .ToListAsync();""")

    h2(d, "3.1 Nima uchun kerak")

    para(d, "Kuzatuv bepul emas. Har bir entity uchun kontekst uning dastlabki qiymatlari "
            "nusxasini xotirada saqlaydi — ya'ni amalda har bir obyekt ikki marta "
            "joylashadi. Bundan tashqari `SaveChanges()` har bir kuzatilayotgan obyektni "
            "ko'rib chiqadi, shuning uchun ularning soni ortgani sari bu amal sekinlashadi.")

    para(d, "Faqat o'qish uchun mo'ljallangan so'rovlarda — masalan ro'yxat ko'rsatadigan "
            "endpoint larda — bu xarajatning hech qanday foydasi yo'q.")

    note(d, "Amaliy qoida:",
         "Agar so'rov natijasini o'zgartirib saqlamoqchi bo'lmasangiz, `AsNoTracking()` "
         "qo'shing. Men o'zim uchun shunday belgilab olganman: `GET` endpoint larda deyarli "
         "har doim kerak, `POST` va `PUT` da esa kerak emas. Farq kichik so'rovlarda "
         "sezilmaydi, lekin yuzlab yozuv qaytaradigan ro'yxatlarda ancha seziladi.")

    h2(d, "3.2 Butun kontekst uchun o'chirish")

    para(d, "Agar kontekst asosan o'qish uchun ishlatilsa, kuzatuvni default holda "
            "o'chirib qo'yish mumkin:")

    code(d, """protected override void OnConfiguring(DbContextOptionsBuilder optionsBuilder)
{
    optionsBuilder.UseQueryTrackingBehavior(QueryTrackingBehavior.NoTracking);
}""")

    para(d, "Bunday sozlanganda kerakli so'rovlarda kuzatuvni qaytadan yoqish uchun "
            "`AsTracking()` ishlatiladi.")

    h2(d, "3.3 AsNoTrackingWithIdentityResolution")

    para(d, "Oddiy `AsNoTracking()` bir xil yozuvni bir nechta marta uchratganda har safar "
            "yangi obyekt yaratadi. Masalan 100 ta kitob bitta muallifga tegishli bo'lsa, "
            "xotirada 100 ta alohida `Author` obyekti paydo bo'ladi.")

    code(d, """// Bir xil muallif bir nechta nusxada bo'ladi
var books = await db.Books.Include(b => b.Author).AsNoTracking().ToListAsync();

// Bir xil muallif uchun bitta obyekt ishlatiladi
var books2 = await db.Books.Include(b => b.Author)
    .AsNoTrackingWithIdentityResolution()
    .ToListAsync();""")

    para(d, "Ikkinchi variant xotirani tejaydi, lekin buning evaziga EF Core takrorlarni "
            "aniqlash uchun ichki lug'at yuritadi. Shuning uchun u to'liq kuzatuvdan "
            "arzonroq, oddiy `AsNoTracking()` dan esa qimmatroq.")

    # ───────────────────────────────────────────
    h1(d, "4. Attach va bog'lanmagan obyektlar")

    para(d, "Web API larda tez-tez uchraydigan vaziyat: klient o'zgartirilgan obyektni "
            "JSON ko'rinishida yuboradi. Bu obyekt hech qanday kontekst tomonidan "
            "kuzatilmaydi, ya'ni `Detached` holatida bo'ladi. Uni saqlash uchun avval "
            "kontekstga tanishtirish kerak.")

    h2(d, "4.1 Update")

    code(d, """public async Task<IActionResult> Update(int id, BookDto dto)
{
    var book = new Book { Id = id, Title = dto.Title, Price = dto.Price };

    db.Books.Update(book);          // holat → Modified
    await db.SaveChangesAsync();

    return NoContent();
}""")

    para(d, "Bu usulning kamchiligi bor: `Update()` obyektning **barcha** maydonlarini "
            "o'zgargan deb belgilaydi. Natijada `UPDATE` buyrug'iga hamma ustun kiradi, "
            "shu jumladan klient umuman yubormagan maydonlar ham. Agar DTO da biror maydon "
            "bo'lmasa, u `null` yoki nol qiymat bilan yozib yuboriladi.")

    note(d, "Mana bu yerda ehtiyot bo'lish kerak:",
         "Bu muammo juda jim kechadi. Klient faqat narxni o'zgartirmoqchi bo'ladi, lekin "
         "DTO da `Title` bo'lmagani uchun kitob nomi `null` ga aylanadi. Test ma'lumotlarida "
         "ko'pincha hamma maydon to'ldirilgan bo'lgani uchun bu xatolik testdan o'tib ketadi "
         "va faqat production da ochiladi.")

    h2(d, "4.2 Xavfsizroq usul — mavjud obyektni yuklab, ustiga yozish")

    code(d, """var book = await db.Books.FindAsync(id);
if (book is null) return NotFound();

book.Title = dto.Title;
book.Price = dto.Price;

await db.SaveChangesAsync();   // faqat haqiqatan o'zgargan ustunlar UPDATE ga kiradi""")

    para(d, "Bu variant bazaga bitta qo'shimcha `SELECT` yuboradi, lekin buning evaziga "
            "`UPDATE` ga faqat o'zgargan maydonlar kiradi va tasodifan ma'lumot "
            "yo'qolishining oldi olinadi.")

    h2(d, "4.3 Attach")

    para(d, "`Attach()` obyektni `Unchanged` holatida kontekstga qo'shadi. Undan keyin "
            "qaysi maydon o'zgarganini aniq ko'rsatish mumkin:")

    code(d, """db.Books.Attach(book);
db.Entry(book).Property(b => b.Price).IsModified = true;

await db.SaveChangesAsync();   // UPDATE faqat Price ustunini o'zgartiradi""")

    # ───────────────────────────────────────────
    h1(d, "5. Kuzatuvni tozalash va tekshirish")

    para(d, "Uzoq ishlaydigan amallarda kontekst juda ko'p entity to'plab qolishi mumkin. "
            "Kuzatuv ro'yxatini tozalash uchun:")

    code(d, """db.ChangeTracker.Clear();""")

    para(d, "Joriy holatda nima kuzatilayotganini ko'rish uchun diagnostika metodi mavjud:")

    code(d, """// Kuzatilayotgan barcha entity lar va ularning holati
Console.WriteLine(db.ChangeTracker.DebugView.ShortView);

// Maydon qiymatlari bilan birga
Console.WriteLine(db.ChangeTracker.DebugView.LongView);""")

    note(d, "Bu juda foydali narsa:",
         "\"Nega bu UPDATE ishlamayapti?\" yoki \"Nega bu obyekt ikki marta saqlanyapti?\" "
         "degan savollar paydo bo'lganda `DebugView` ni chop etish ko'pincha javobni "
         "bir zumda ko'rsatadi. Kontekst nimani qanday holatda ko'rayotgani ro'yxat "
         "bo'lib chiqadi.")

    # ───────────────────────────────────────────
    h1(d, "6. Xulosa")

    bullets(d, [
        "Change tracking tufayli `Update()` ni qo'lda chaqirish shart emas — kontekst "
        "o'zgarishni dastlabki qiymatlar nusxasiga taqqoslab o'zi aniqlaydi.",
        "Kuzatuv xotira va `SaveChanges()` vaqti hisobidan amalga oshadi. O'qish uchun "
        "mo'ljallangan so'rovlarda `AsNoTracking()` shu xarajatni olib tashlaydi.",
        "`Update()` barcha ustunlarni o'zgargan deb belgilaydi — bu DTO da bo'lmagan "
        "maydonlarning yo'qolishiga olib kelishi mumkin.",
        "Bog'lanmagan obyektni saqlashda mavjud yozuvni yuklab, ustiga yozish eng xavfsiz yo'l.",
        "`ChangeTracker.DebugView` — kuzatuv bilan bog'liq muammolarni aniqlashning "
        "eng tez usuli.",
    ])

    sources(d, [
        ("Change Tracking in EF Core",
         "https://learn.microsoft.com/en-us/ef/core/change-tracking/"),
        ("Tracking vs. No-Tracking Queries",
         "https://learn.microsoft.com/en-us/ef/core/querying/tracking"),
        ("Disconnected Entities — EF Core",
         "https://learn.microsoft.com/en-us/ef/core/saving/disconnected-entities"),
        ("Change Tracker Debugging",
         "https://learn.microsoft.com/en-us/ef/core/change-tracking/debug-views"),
    ])
