# -*- coding: utf-8 -*-
import os
from docbuild import *

TOPIC = "Entity type hierarchy mapping"
CATEGORY = "EF Core"
TITLE = "Entity Ierarxiyasini Mapping Qilish"
SUBTITLE = "Meros olgan klasslarni relyatsion jadvallarga joylash strategiyalari"
FILENAME = "Entity type hierarchy mapping.docx"

FIG = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "figures", "out", "inheritance_strategies.png")


def build(d):
    h1(d, "1. Muammoning mohiyati")

    para(d, "Obyektga yo'naltirilgan dasturlashda meros olish tabiiy tushuncha: `Payment` "
            "bazaviy klassi bo'lib, undan `CardPayment` va `CashPayment` kelib chiqadi. "
            "Relyatsion ma'lumotlar bazasida esa meros tushunchasi umuman mavjud emas — "
            "u faqat jadval, ustun va kalitlarni biladi.")

    para(d, "Ikki model orasidagi bu nomuvofiqlik obyekt-relyatsion tafovut deb ataladi. "
            "EF Core uni hal qilish uchun uchta mapping strategiyasini taklif qiladi va "
            "ularning har biri boshqacha jadval sxemasi hosil qiladi.")

    note(d, "Nega bu masala muhim:",
         "Bu tanlov bir martalik. Loyiha boshida qaysi strategiyani tanlasam, keyinchalik "
         "uni o'zgartirish jadval sxemasini butunlay qayta qurish va mavjud ma'lumotni "
         "ko'chirish demakdir. Shuning uchun men buni \"keyin ko'ramiz\" deb qoldirmaslikka "
         "harakat qilaman.")

    # ───────────────────────────────────────────
    h1(d, "2. Misol model")

    code(d, """public abstract class Payment
{
    public int Id { get; set; }
    public decimal Amount { get; set; }
    public DateTime CreatedAt { get; set; }
}

public class CardPayment : Payment
{
    public string MaskedCardNumber { get; set; }
    public string BankName { get; set; }
}

public class CashPayment : Payment
{
    public string CashierName { get; set; }
}""")

    para(d, "Quyidagi barcha strategiyalar shu bitta model uchun ko'rib chiqiladi — "
            "farq faqat hosil bo'ladigan jadvallarda.")

    # ───────────────────────────────────────────
    h1(d, "3. Uchta strategiya")

    if os.path.exists(FIG):
        image(d, FIG, "Bitta ierarxiya uchun uch xil jadval sxemasi")

    h2(d, "3.1 TPH — Table per Hierarchy")

    para(d, "Butun ierarxiya bitta jadvalga joylashtiriladi. Qaysi satr qaysi tipga "
            "tegishli ekanini alohida diskriminator ustuni ko'rsatadi. Bir tipga tegishli "
            "bo'lmagan ustunlar o'sha satrda `NULL` bo'lib qoladi.")

    para(d, "Bu EF Core dagi sukutdagi strategiya — hech narsa sozlanmasa, TPH qo'llanadi.")

    h2(d, "3.2 TPT — Table per Type")

    para(d, "Ierarxiyaning har bir tipi uchun alohida jadval yaratiladi. Bazaviy jadval "
            "umumiy ustunlarni, hosila jadvallar esa faqat o'z ustunlarini saqlaydi va "
            "bazaviy jadvalga tashqi kalit orqali bog'lanadi.")

    h2(d, "3.3 TPC — Table per Concrete type")

    para(d, "Faqat konkret (abstrakt bo'lmagan) tiplar uchun jadval yaratiladi. Har bir "
            "jadval o'z ichida umumiy ustunlarni ham takrorlaydi. Bazaviy tip uchun jadval "
            "umuman bo'lmaydi. Bu strategiya EF Core 7 dan boshlab qo'llab-quvvatlanadi.")

    # ───────────────────────────────────────────
    h1(d, "4. Taqqoslash")

    table(d, ["Mezon", "TPH", "TPT", "TPC"],
          [["Jadvallar soni", "1", "1 + hosilalar soni", "Konkret tiplar soni"],
           ["Bitta tipni o'qish", "Tez", "JOIN kerak", "Eng tez"],
           ["Barcha tiplarni o'qish", "Eng tez", "Ko'p JOIN", "UNION kerak"],
           ["Ma'lumot takrorlanishi", "Yo'q", "Yo'q", "Bor"],
           ["NOT NULL cheklov", "Qo'yib bo'lmaydi", "Qo'yish mumkin", "Qo'yish mumkin"],
           ["Yangi tip qo'shish", "Ustun qo'shiladi", "Jadval qo'shiladi", "Jadval qo'shiladi"],
           ["Baza sxemasi tozaligi", "Past", "Yuqori", "O'rtacha"]],
          widths=[4.2, 3.6, 3.9, 3.8])

    para(d, "Jadvaldan ko'rinib turibdiki, bironta strategiya hamma mezon bo'yicha "
            "g'olib emas. TPH unumdorlikni, TPT sxema tozaligini, TPC esa ikkalasining "
            "o'rtasidagi muvozanatni tanlaydi.")

    # ───────────────────────────────────────────
    h1(d, "5. Qaysi birini qachon tanlayman")

    para(d, "O'zim uchun quyidagi oddiy qoidalarni shakllantirdim:")

    bullets(d, [
        "**Hosila tiplarda kam sondagi qo'shimcha maydon bo'lsa** — TPH. Bir nechta "
        "`NULL` ustun muammo emas, lekin JOIN larning yo'qligi sezilarli yutuq.",
        "**Har bir tipda ko'p va majburiy maydonlar bo'lsa** — TPT yoki TPC. TPH da "
        "ularni `NOT NULL` qilib bo'lmaydi, chunki boshqa tiplar uchun o'sha ustun bo'sh.",
        "**Tiplar deyarli hech qachon birgalikda so'ralmasa** — TPC. Har bir so'rov "
        "faqat bitta jadvalga tegadi.",
        "**Baza boshqa tizimlar bilan ham bo'lishilsa** — TPT. Uning sxemasi tashqaridan "
        "qaraganda eng tushunarli.",
    ])

    note(d, "Ko'pincha men TPH ni tanlayman:",
         "Sababi sodda — hosila tiplar odatda bir-ikkita qo'shimcha maydon bilan farq "
         "qiladi, JOIN esa har bir so'rovda narxini oladi. Lekin agar hosila tiplarning "
         "maydonlari 5-6 tadan oshsa va ular majburiy bo'lsa, TPH jadvali bo'sh "
         "kataklar to'plamiga aylanadi — o'shanda TPT ga o'taman.")

    note(d, "Bitta nozik jihat:",
         "TPH da `NOT NULL` qo'yib bo'lmasligi shunchaki noqulaylik emas — bu baza "
         "darajasidagi himoyani yo'qotish demak. Ya'ni karta to'lovida bank nomi albatta "
         "bo'lishi kerakligini endi faqat ilova kodim nazorat qiladi. Agar bazaga boshqa "
         "yo'ldan ham yozuv tushsa, bu cheklov ishlamaydi.")

    # ───────────────────────────────────────────
    h1(d, "6. Strategiyani tanlash kodi")

    code(d, """// TPH — sukutdagi holat, qo'shimcha sozlama shart emas
modelBuilder.Entity<Payment>()
    .HasDiscriminator<string>("PaymentType")
    .HasValue<CardPayment>("card")
    .HasValue<CashPayment>("cash");

// TPT — har bir tipga jadval nomi beriladi
modelBuilder.Entity<Payment>().ToTable("payments");
modelBuilder.Entity<CardPayment>().ToTable("card_payments");
modelBuilder.Entity<CashPayment>().ToTable("cash_payments");

// TPC
modelBuilder.Entity<Payment>().UseTpcMappingStrategy();
modelBuilder.Entity<CardPayment>().ToTable("card_payments");
modelBuilder.Entity<CashPayment>().ToTable("cash_payments");""")

    para(d, "Uchala holatda ham C# kodidagi so'rovlar bir xil yoziladi — strategiya "
            "faqat generatsiya qilinadigan SQL ga ta'sir qiladi:")

    code(d, """// Barcha to'lovlar
var all = await db.Payments.ToListAsync();

// Faqat karta to'lovlari
var cards = await db.Payments.OfType<CardPayment>().ToListAsync();

// Yoki to'g'ridan-to'g'ri
var cards2 = await db.Set<CardPayment>().ToListAsync();""")

    # ───────────────────────────────────────────
    h1(d, "7. Umumiy cheklovlar")

    bullets(d, [
        "Bitta ierarxiya ichida strategiyalarni aralashtirib bo'lmaydi — butun ierarxiya "
        "uchun bittasi tanlanadi.",
        "Hosila tiplarning navigatsiya xossalari uchala strategiyada ham ishlaydi, lekin "
        "TPC da bazaviy tipga tashqi kalit qo'yib bo'lmaydi.",
        "Abstrakt bazaviy tipni `DbSet` sifatida e'lon qilish shart emas — hosila tiplar "
        "orqali ham modelga tushadi.",
    ])

    # ───────────────────────────────────────────
    h1(d, "8. Xulosa")

    bullets(d, [
        "Relyatsion bazada meros yo'q, shuning uchun ierarxiya albatta biror strategiya "
        "bilan jadvallarga yoyiladi.",
        "TPH — bitta jadval, diskriminator ustuni, eng tez o'qish, lekin `NOT NULL` yo'q.",
        "TPT — har tipga jadval, toza sxema, lekin har so'rovda JOIN.",
        "TPC — konkret tiplarga jadval, ustunlar takrorlanadi, bitta tipni o'qish eng tez.",
        "Tanlov loyihaning boshida qilinishi kerak — keyin o'zgartirish ma'lumot "
        "migratsiyasini talab qiladi.",
    ])

    sources(d, [
        ("Inheritance — EF Core",
         "https://learn.microsoft.com/en-us/ef/core/modeling/inheritance"),
        ("What's New in EF Core 7.0: TPC inheritance mapping",
         "https://learn.microsoft.com/en-us/ef/core/what-is-new/ef-core-7.0/whatsnew#table-per-concrete-type-tpc-inheritance-mapping"),
    ])
