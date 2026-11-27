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
    h1(d, "6. Amaliyotdan: ChangeTracker orqali yopilgan davrni qo'riqlash")

    para(d, "Ish joyimdagi MAD ERP tizimida hujjatlarning deyarli hammasi o'quv yiliga "
            "bog'langan. Yil yakunlanib hisobotlar topshirilgandan keyin u \"yopiladi\" — "
            "`std.info_school_year` jadvalidagi `is_process_allowed` ustuni `false` ga "
            "o'tadi. Shundan keyin o'sha yilga tegishli biror hujjatni qo'shish, "
            "o'zgartirish yoki o'chirish mumkin emas, aks holda allaqachon topshirilgan "
            "hisobot bilan baza bir-biriga mos kelmay qoladi.")

    para(d, "Muammo shundaki, bunday hujjat turlari yigirmadan ortiq va ular turli "
            "xizmatlarga tarqalgan: `Commission`, `StudentPayment`, `SchoolDiplom`, "
            "`MusicTeacherSalary`, `StudentTransferApplication` va boshqalar. Tekshiruvni "
            "har bir komanda ishlovchisiga qo'lda yozish — bir xil shartni yigirma joyda "
            "takrorlash va ertaga qo'shiladigan yangi hujjatda uni unutish degani.")

    h2(d, "6.1 Yechim — tekshiruvni SaveChanges ga ko'chirish")

    para(d, "Hujjatning o'zi faqat bitta atribut bilan belgilanadi. Atributda qaysi "
            "property o'quv yili id sini saqlashi ko'rsatiladi:")

    code(d, """[Table("doc_commission", Schema = "com")]
[SchoolYearProcessGuard(nameof(SchoolYearId))]
public class Commission : BaseEntity<long>, IAuditTrackEntity
{
    [Column("school_year_id")]
    public int SchoolYearId { get; set; }
    // ...
}""", caption="Hujjat turi o'zini qo'riqlanadigan deb e'lon qiladi")

    para(d, "Qolgan hamma ish `ApplicationDbContext` ichida, `SaveChanges` ustidagi "
            "override da bajariladi. U `ChangeTracker` ni aylanib, shu amalda ta'sirga "
            "tushadigan o'quv yillari to'plamini yig'adi:")

    code(d, """private HashSet<int> CollectGuardedSchoolYearIds()
{
    var schoolYearIds = new HashSet<int>();

    foreach (var entry in ChangeTracker.Entries())
    {
        if (entry.State is not (EntityState.Added or EntityState.Modified or EntityState.Deleted))
            continue;

        // Metadata.ClrType — proxy emas, haqiqiy entity turi.
        var propertyName = SchoolYearGuardProperties.GetOrAdd(
            entry.Metadata.ClrType,
            clrType => clrType.GetCustomAttribute<SchoolYearProcessGuardAttribute>()
                ?.SchoolYearPropertyName ?? string.Empty);

        if (propertyName.Length == 0)
            continue;

        var property = entry.Property(propertyName);

        if (property.CurrentValue is int currentSchoolYearId && currentSchoolYearId > 0)
            schoolYearIds.Add(currentSchoolYearId);

        // Yil o'zgartirilgan bo'lsa eskisi ham tekshiriladi — aks holda hujjatni
        // yopiq yildan "olib chiqib" tahrirlash yo'li ochiq qolardi.
        if (entry.State == EntityState.Modified && property.IsModified
            && property.OriginalValue is int originalSchoolYearId && originalSchoolYearId > 0)
            schoolYearIds.Add(originalSchoolYearId);
    }

    return schoolYearIds;
}""", caption="ApplicationDbContext, SchoolYearProcessGuard bo'limidan")

    para(d, "Agar to'plam bo'sh bo'lmasa, yopilgan yillar ro'yxati bir marta o'qiladi va "
            "mos tushgani bo'lsa mijozga ko'rinadigan xato tashlanadi:")

    code(d, """public override async Task<int> SaveChangesAsync(
    bool acceptAllChangesOnSuccess, CancellationToken cancellationToken = default)
{
    var schoolYearIds = CollectGuardedSchoolYearIds();

    if (schoolYearIds.Count > 0)
    {
        _blockedSchoolYears ??= await SchoolYears.AsNoTracking()
            .Where(x => !x.IsProcessAllowed)
            .ToDictionaryAsync(x => x.Id, x => x.FullName, cancellationToken);

        EnsureSchoolYearProcessAllowed(schoolYearIds);
    }

    return await base.SaveChangesAsync(acceptAllChangesOnSuccess, cancellationToken);
}""")

    h2(d, "6.2 Bu yerda change tracking ning qaysi xususiyati ishlatilgan")

    bullets(d, [
        "**`entry.State` bo'yicha filtr.** Kontekst yuzlab entity ni kuzatayotgan bo'lishi "
        "mumkin, lekin ularning ko'pi `Unchanged`. Faqat uch holat tekshiriladi, qolgani "
        "darhol tashlab ketiladi.",
        "**`entry.Metadata.ClrType`.** Obyektning `GetType()` i lazy loading proxy si "
        "bo'lib chiqishi mumkin — unda atribut topilmaydi. Metadata esa EF Core ning "
        "modelidagi haqiqiy turni beradi.",
        "**`property.OriginalValue`.** Eng muhim nuqta. Agar faqat joriy qiymat "
        "tekshirilsa, hujjatni yopiq yildan ochiq yilga ko'chirib, keyin xohlagancha "
        "tahrirlash yo'li ochiq qolardi. Dastlabki qiymatlar nusxasi — ya'ni 1-bo'limda "
        "aytilgan o'sha \"sehr\" ning asosi — shu teshikni yopadi.",
        "**Tekshiruv `base.SaveChanges` dan oldin.** Shuning uchun bazaga hech narsa "
        "tushmaydi va yuqorida tranzaksiya bor-yo'qligi ahamiyatsiz bo'ladi.",
    ])

    h2(d, "6.3 Narxi va chetlab o'tish yo'llari")

    para(d, "Reflection har bir entity uchun chaqirilsa qimmat bo'lardi. Shuning uchun "
            "natija statik lug'atda keshlanadi, va atributi **yo'q** turlar ham bo'sh satr "
            "bilan keshlanadi — ya'ni har bir tur uchun reflection umumiy hisobda bir marta "
            "ishlaydi:")

    code(d, """private static readonly ConcurrentDictionary<Type, string> SchoolYearGuardProperties = new();""")

    para(d, "Yopilgan yillar lug'ati esa `??=` bilan faqat zarur bo'lganda o'qiladi. "
            "Kontekst scoped bo'lgani uchun bu bitta so'rov davomida ko'pi bilan bitta "
            "qo'shimcha `SELECT`. Ochiq yillar umuman yuklanmaydi — odatda yopilganlari "
            "bir necha qator.")

    note(d, "Mana bu cheklovni bilib qo'yish kerak:",
         "Bu himoya faqat EF Core orqali o'tgan yozuvni ko'radi. `ExecuteUpdate()`, "
         "`ExecuteDelete()` va xom SQL `ChangeTracker` ni butunlay chetlab o'tadi, "
         "shuning uchun ularda guard ishlamaydi. Bu ongli murosa: qo'riqlanadigan "
         "hujjatlar odatda bitta-bitta tahrirlanadi, ommaviy amallar esa ularga "
         "qo'llanilmaydi. Lekin ertaga kimdir shu jadvalga `ExecuteDelete()` yozsa, "
         "tekshiruv jimgina chetlab o'tiladi — shuni yodda tutish kerak.")

    # ───────────────────────────────────────────
    h1(d, "7. Xulosa")

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
