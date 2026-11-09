# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "ACID properties of System"
CATEGORY = "Architecture"
TITLE = "Tizim Darajasidagi ACID"
SUBTITLE = "Bitta bazadan tashqarida kafolatlar qanday o'zgaradi"
FILENAME = "ACID properties of System.docx"


def build(d):
    h1(d, "1. Muammoning qo'yilishi")

    para(d, "Bitta ma'lumotlar bazasi ichida ACID kafolatlari tayyor holda "
            "beriladi — tranzaksiya ochiladi, amallar bajariladi, "
            "`COMMIT` qilinadi. Hammasi baza zimmasida.")

    para(d, "Tizim bir nechta komponentdan iborat bo'lganda vaziyat o'zgaradi: "
            "ikkita baza, baza va xabar navbati, yoki bir nechta mustaqil "
            "xizmat. Endi \"hammasi yoki hech biri\" kafolatini kim beradi?")

    note(d, "Bu savol menga mikroservislar mavzusini o'rganayotganimda tushundi:",
         "Monolit ilovada men tranzaksiya haqida deyarli o'ylamayman — "
         "`SaveChanges` hammasini hal qiladi. Tizim bo'lingan paytda esa bu "
         "eng murakkab masalaga aylanadi. Ya'ni mikroservislar tarqatilish "
         "qulayligini beradi, lekin evaziga ma'lumot butunligini men "
         "zimmamga olaman.")

    # ───────────────────────────────────────────
    h1(d, "2. Taqsimlangan tranzaksiyalar")

    para(d, "Klassik yechim — ikki fazali tasdiqlash (two-phase commit, 2PC). "
            "Koordinator barcha ishtirokchilardan avval tayyorlikni so'raydi, "
            "keyin tasdiqlash buyrug'ini beradi.")

    code(d, """1-faza (prepare):
    Koordinator → A: tayyormisan?    A → ha
    Koordinator → B: tayyormisan?    B → ha

2-faza (commit):
    Koordinator → A: tasdiqla
    Koordinator → B: tasdiqla""")

    para(d, "Agar birortasi \"yo'q\" desa, koordinator hammasiga bekor qilish "
            "buyrug'ini yuboradi.")

    h2(d, "2.1 Nega 2PC amalda kam ishlatiladi")

    bullets(d, [
        "**Bloklovchi** — ikkinchi faza kutilayotganda ishtirokchilar "
        "qulflarni ushlab turadi.",
        "**Koordinator yagona nosozlik nuqtasi** — u ikki faza orasida "
        "to'xtasa, ishtirokchilar noaniq holatda qoladi.",
        "**Sekin** — bir nechta tarmoq murojaati va diskka yozish.",
        "**Qo'llab-quvvatlash cheklangan** — ko'p zamonaviy baza va navbat "
        "tizimlari uni qo'llab-quvvatlamaydi yoki tavsiya qilmaydi.",
    ])

    note(d, "Shuning uchun amaliy yondashuv boshqacha:",
         "2PC o'rniga tizimlar odatda **yakuniy izchillikni** (eventual "
         "consistency) tanlaydi. Ya'ni qisqa vaqt davomida ma'lumot turli "
         "joylarda mos kelmasligi mumkin, lekin oxir-oqibat u tenglashadi. "
         "Bu zaifroq kafolat, lekin ancha amaliy.")

    # ───────────────────────────────────────────
    h1(d, "3. CAP teoremasi")

    para(d, "Taqsimlangan tizim bir vaqtda uchta xususiyatning faqat "
            "ikkitasini ta'minlay oladi:")

    table(d, ["Xususiyat", "Ma'nosi"],
          [["Consistency", "Barcha tugunlar bir xil ma'lumotni ko'radi"],
           ["Availability", "Har bir so'rov javob oladi"],
           ["Partition tolerance", "Tarmoq uzilishiga chidamlilik"]],
          widths=[4.6, 10.9])

    para(d, "Amalda tarmoq uzilishi muqarrar, ya'ni P ni tanlamaslik imkoni "
            "yo'q. Shuning uchun haqiqiy tanlov C va A o'rtasida bo'ladi: "
            "tarmoq uzilganda tizim eski ma'lumot bersinmi yoki umuman javob "
            "bermasinmi.")

    note(d, "Bu tanlov biznesga bog'liq:",
         "Bank hisobidagi qoldiq — eski ma'lumot berishdan ko'ra xatolik "
         "qaytargan ma'qul. Ijtimoiy tarmoqdagi izohlar soni — bir necha "
         "soniya eskirgan bo'lsa ham hech kim sezmaydi. Ya'ni savolga "
         "texnik emas, biznes javobi beriladi.")

    para(d, "Shuni ham qayd etish kerakki, ACID dagi Consistency va CAP dagi "
            "Consistency turli narsalar. Birinchisi — baza cheklovlarining "
            "buzilmasligi, ikkinchisi — tugunlar o'rtasidagi moslik.")

    # ───────────────────────────────────────────
    h1(d, "4. BASE yondashuvi")

    para(d, "ACID ga muqobil sifatida BASE tamoyili taklif qilingan:")

    bullets(d, [
        "**Basically Available** — tizim doim javob beradi, hatto qisman "
        "ma'lumot bilan bo'lsa ham.",
        "**Soft state** — holat tashqi kiritishsiz ham o'zgarishi mumkin.",
        "**Eventually consistent** — vaqt o'tishi bilan barcha nusxalar "
        "tenglashadi.",
    ])

    table(d, ["ACID", "BASE"],
          [["Qat'iy izchillik", "Yakuniy izchillik"],
           ["Mavjudlik evaziga", "Izchillik evaziga"],
           ["Bitta baza uchun tabiiy", "Taqsimlangan tizim uchun tabiiy"],
           ["Moliyaviy amallar", "Kontent, analitika, kesh"]],
          widths=[7.7, 7.8])

    # ───────────────────────────────────────────
    h1(d, "5. Saga naqshi")

    para(d, "Saga — taqsimlangan tranzaksiyani ketma-ket lokal tranzaksiyalarga "
            "bo'lish. Har bir qadam o'z bazasida odatiy ACID tranzaksiyasi "
            "bo'ladi. Xatolik yuz bersa, oldingi qadamlar kompensatsiya "
            "amallari bilan bekor qilinadi.")

    code(d, """Buyurtma yaratish sagasi:

  1. Buyurtma xizmati:  buyurtma yaratildi (Pending)
  2. Ombor xizmati:     mahsulot zahiraga olindi
  3. To'lov xizmati:    to'lov amalga oshirildi
  4. Buyurtma xizmati:  buyurtma tasdiqlandi (Confirmed)

Agar 3-qadam muvaffaqiyatsiz bo'lsa:

  3'. Ombor xizmati:    zahira bo'shatildi
  4'. Buyurtma xizmati: buyurtma bekor qilindi (Cancelled)""")

    h2(d, "5.1 Ikki tashkil etish usuli")

    table(d, ["Usul", "Qanday ishlaydi", "Qachon"],
          [["Xoreografiya", "Har bir xizmat hodisani tinglaydi va "
                            "o'zining keyingi hodisasini e'lon qiladi",
            "Kam qadamli, oddiy oqimlar"],
           ["Orkestratsiya", "Markaziy koordinator qadamlarni boshqaradi",
            "Ko'p qadamli, murakkab oqimlar"]],
          widths=[3.2, 7.3, 5.0])

    note(d, "Xoreografiya oddiy ko'rinadi, lekin tez murakkablashadi:",
         "Uchta xizmat bo'lsa, kim nimaga javob berayotganini kuzatish mumkin. "
         "Oltitaga yetganda esa butun oqimni tasavvur qilish uchun barcha "
         "xizmatlarning kodini o'qish kerak bo'ladi. Markaziy koordinatorda "
         "esa oqim bitta joyda yozilgan va o'qiladigan bo'ladi.")

    note(d, "Kompensatsiya — eng qiyin qism:",
         "\"Zahirani bo'shatish\" oson. \"To'lovni qaytarish\" ancha qiyin — "
         "komissiya ushlangan bo'lishi mumkin. \"Yuborilgan email ni "
         "qaytarish\" esa umuman imkonsiz. Shuning uchun saga loyihalashda "
         "qaytarib bo'lmaydigan qadamlarni oxiriga qo'yishga harakat "
         "qilaman.")

    # ───────────────────────────────────────────
    h1(d, "6. Outbox naqshi")

    para(d, "Tipik muammo: bazaga yozib, keyin xabar navbatiga xabar yuborish "
            "kerak. Ikkalasini bitta tranzaksiyaga o'rab bo'lmaydi.")

    code(d, """// Xavfli ketma-ketlik
await db.SaveChangesAsync(ct);            // muvaffaqiyatli
await bus.PublishAsync(orderCreated, ct); // bu yerda nosozlik bo'lsa?
// Buyurtma bazada bor, lekin hech kim bundan xabardor emas""")

    para(d, "Outbox naqshi yechimi — xabarni ham o'sha tranzaksiyada, alohida "
            "jadvalga yozish:")

    code(d, """CREATE TABLE outbox_messages (
    id           uuid PRIMARY KEY,
    type         text NOT NULL,
    payload      jsonb NOT NULL,
    created_at   timestamptz NOT NULL DEFAULT now(),
    processed_at timestamptz
);""")

    code(d, """// Bitta tranzaksiyada
db.Orders.Add(order);
db.OutboxMessages.Add(new OutboxMessage
{
    Id = Guid.NewGuid(),
    Type = nameof(OrderCreated),
    Payload = JsonSerializer.Serialize(new OrderCreated(order.Id))
});

await db.SaveChangesAsync(ct);   // ikkalasi atomar""")

    code(d, """// Alohida fon xizmati xabarlarni yuboradi
var pending = await db.OutboxMessages
    .Where(m => m.ProcessedAt == null)
    .OrderBy(m => m.CreatedAt)
    .Take(100)
    .ToListAsync(ct);

foreach (var message in pending)
{
    await bus.PublishAsync(message, ct);
    message.ProcessedAt = DateTime.UtcNow;
}

await db.SaveChangesAsync(ct);""")

    note(d, "Bu naqshning muhim xususiyati:",
         "U \"kamida bir marta\" (at-least-once) yetkazishni kafolatlaydi, "
         "\"aynan bir marta\" emas. Xabar yuborilgandan keyin, lekin belgi "
         "qo'yilishidan oldin nosozlik bo'lsa, u ikkinchi marta yuboriladi. "
         "Shuning uchun **iste'molchi idempotent bo'lishi shart** — bir xil "
         "xabarni ikki marta qayta ishlash natijani o'zgartirmasligi kerak.")

    # ───────────────────────────────────────────
    h1(d, "7. Idempotentlik")

    code(d, """public async Task HandleAsync(OrderCreated message, CancellationToken ct)
{
    // Bu xabar allaqachon qayta ishlanganmi
    var processed = await _db.ProcessedMessages
        .AnyAsync(m => m.MessageId == message.Id, ct);

    if (processed)
        return;

    await DoWorkAsync(message, ct);

    _db.ProcessedMessages.Add(new ProcessedMessage
    {
        MessageId = message.Id,
        ProcessedAt = DateTime.UtcNow
    });

    await _db.SaveChangesAsync(ct);
}""")

    para(d, "Ba'zi amallar tabiatan idempotent bo'ladi — masalan "
            "`SET status = 'paid'`. Boshqalari esa emas — "
            "`balance = balance + 100`. Ikkinchi turdagi amallar uchun "
            "yuqoridagi kabi tekshiruv kerak.")

    # ───────────────────────────────────────────
    h1(d, "8. Amaliy xulosalar")

    bullets(d, [
        "Birga o'zgarishi kerak bo'lgan ma'lumotlarni bitta bazada saqlash — "
        "eng oddiy va eng ishonchli yechim.",
        "Xizmatlar chegarasini \"nima birga o'zgaradi\" savoliga qarab "
        "belgilash.",
        "Taqsimlangan tranzaksiya kerak bo'lsa — 2PC emas, saga.",
        "Baza va xabar navbati o'rtasidagi atomiclik uchun outbox.",
        "Barcha xabar iste'molchilarini idempotent qilish.",
        "Qaysi ma'lumot qat'iy izchil, qaysi biri yakuniy izchil bo'lishi "
        "mumkinligini ongli belgilash.",
    ])

    note(d, "Eng muhim maslahat shu bo'lsa kerak:",
         "Taqsimlangan tranzaksiya muammosini hal qilishning eng yaxshi usuli — "
         "unga umuman duch kelmaslik. Agar ikki narsa doim birga o'zgarsa, "
         "ular bitta xizmatga tegishli. Mikroservislarni juda mayda bo'lib "
         "tashlash aynan shu muammoni keltirib chiqaradi.")

    # ───────────────────────────────────────────
    h1(d, "9. Xulosa")

    bullets(d, [
        "Bitta baza ichida ACID tayyor; tizim bo'lingach, kafolat dasturchi "
        "zimmasiga o'tadi.",
        "2PC bloklovchi va yagona nosozlik nuqtasiga ega — amalda kam "
        "ishlatiladi.",
        "CAP teoremasiga ko'ra tarmoq uzilganda izchillik va mavjudlik "
        "o'rtasida tanlov qilinadi.",
        "BASE — yakuniy izchillikka asoslangan muqobil tamoyil.",
        "Saga taqsimlangan amalni lokal tranzaksiyalar ketma-ketligiga "
        "bo'ladi; xatolikda kompensatsiya qo'llanadi.",
        "Outbox baza va xabar navbati o'rtasidagi atomiclikni ta'minlaydi.",
        "Outbox \"kamida bir marta\" yetkazadi — iste'molchi idempotent "
        "bo'lishi shart.",
        "Eng yaxshi yechim — chegaralarni shunday belgilashki, taqsimlangan "
        "tranzaksiya umuman kerak bo'lmasin.",
    ])

    sources(d, [
        ("Saga distributed transactions pattern — Azure Architecture Center",
         "https://learn.microsoft.com/en-us/azure/architecture/patterns/saga"),
        ("Transactional Outbox pattern",
         "https://learn.microsoft.com/en-us/azure/architecture/best-practices/transactional-outbox-cosmos"),
        ("Data consistency in microservices — .NET microservices architecture",
         "https://learn.microsoft.com/en-us/dotnet/architecture/microservices/architect-microservice-container-applications/distributed-data-management"),
        ("Idempotent Receiver — Enterprise Integration Patterns",
         "https://www.enterpriseintegrationpatterns.com/patterns/messaging/IdempotentReceiver.html"),
    ])
