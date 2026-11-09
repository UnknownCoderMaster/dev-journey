# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "Mapping Inheritance"
CATEGORY = "AutoMapper/Mapster"
TITLE = "Mapping Inheritance"
SUBTITLE = "Ierarxiyadagi turlarni map qilish"
FILENAME = "Mapping Inheritance.docx"


def build(d):
    h1(d, "1. Muammo")

    para(d, "Manba va maqsad tomonida ierarxiya bo'lsa, mapping "
            "noaniq bo'lib qoladi. Qaysi konkret turga map qilish "
            "kerak — bazaviy turgami yoki hosilagami?")

    code(d, """// Manba ierarxiyasi
public abstract class Payment
{
    public Guid Id { get; set; }
    public decimal Amount { get; set; }
    public DateTimeOffset CreatedAt { get; set; }
}

public sealed class CardPayment : Payment
{
    public string CardLast4 { get; set; } = "";
    public string AuthCode { get; set; } = "";
}

public sealed class CashPayment : Payment
{
    public string CashierName { get; set; } = "";
}""")

    code(d, """// Maqsad ierarxiyasi
public abstract class PaymentDto
{
    public Guid Id { get; init; }
    public decimal Amount { get; init; }
}

public sealed class CardPaymentDto : PaymentDto
{
    public string CardLast4 { get; init; } = "";
}

public sealed class CashPaymentDto : PaymentDto
{
    public string CashierName { get; init; } = "";
}""")

    para(d, "Agar faqat `CreateMap<Payment, PaymentDto>()` yozsam, "
            "ro'yxatdagi hamma to'lov `PaymentDto` sifatida map "
            "qilinadi va hosila maydonlari yo'qoladi.")

    # ───────────────────────────────────────────
    h1(d, "2. Include va IncludeBase")

    para(d, "AutoMapper'da ierarxiyani ikki tomondan e'lon qilish "
            "mumkin.")

    h2(d, "Bazaviy turdan: Include")

    code(d, """CreateMap<Payment, PaymentDto>()
    .Include<CardPayment, CardPaymentDto>()
    .Include<CashPayment, CashPaymentDto>();

CreateMap<CardPayment, CardPaymentDto>();
CreateMap<CashPayment, CashPaymentDto>();""")

    para(d, "Endi `mapper.Map<PaymentDto>(payment)` chaqirilganda "
            "AutoMapper manba obyektining **haqiqiy turini** tekshiradi "
            "va mos DTO ni yasaydi.")

    h2(d, "Hosiladan: IncludeBase")

    code(d, """CreateMap<Payment, PaymentDto>()
    .ForMember(d => d.Amount, o => o.MapFrom(s => s.Amount));

CreateMap<CardPayment, CardPaymentDto>().IncludeBase<Payment, PaymentDto>();
CreateMap<CashPayment, CashPaymentDto>().IncludeBase<Payment, PaymentDto>();""")

    para(d, "Ikkisi bir xil natija beradi, lekin `IncludeBase` ni "
            "afzal ko'raman: yangi hosila tur qo'shilganda bazaviy "
            "konfiguratsiyaga tegish kerak emas. `Include` bilan esa "
            "har yangi tur uchun bazaviy map'ni tahrirlash kerak — "
            "ya'ni OCP buziladi.")

    note(d, "Nozik joy",
         "`IncludeBase` bazaviy konfiguratsiyadagi `ForMember` "
         "sozlamalarini ham meros qiladi. Shuning uchun umumiy "
         "maydonlar qoidasini bir joyda yozish yetarli — har bir "
         "hosilada takrorlash kerak emas.")

    # ───────────────────────────────────────────
    h1(d, "3. Avtomatik aniqlash")

    code(d, """// AutoMapper 11+ — ierarxiyani o'zi topadi
cfg.CreateMap<Payment, PaymentDto>().IncludeAllDerived();""")

    para(d, "`IncludeAllDerived()` bazaviy turning hamma hosilasi uchun "
            "mapping'ni avtomatik qo'llaydi. Qulay, lekin bir shartda: "
            "hosila turlarning mapping'lari ham ro'yxatga olingan "
            "bo'lishi kerak.")

    para(d, "Yangi to'lov turi qo'shilganda endi mapping "
            "konfiguratsiyasiga tegish kerak emas — bu ierarxiya tez "
            "o'sadigan loyihada sezilarli yutuq.")

    # ───────────────────────────────────────────
    h1(d, "4. ProjectTo bilan ishlaganda")

    para(d, "Bu eng ko'p muammo keltiradigan joy. `ProjectTo` ifodaga "
            "aylanishi kerak, lekin polimorf mapping ish vaqtida tur "
            "tekshirishni talab qiladi — SQL buni bajara olmaydi.")

    code(d, """// Ishlamaydi yoki faqat bazaviy turga map qiladi
var dtos = await db.Payments
    .ProjectTo<PaymentDto>(mapper.ConfigurationProvider)
    .ToListAsync(ct);""")

    para(d, "TPH strategiyasida barcha turlar bitta jadvalda bo'lgani "
            "uchun bu ba'zan ishlaydi, lekin ishonchli emas. Shuning "
            "uchun ikki yondashuvdan birini tanlayman.")

    h2(d, "1. Turlarni alohida so'rash")

    code(d, """var cards = await db.Payments.OfType<CardPayment>()
    .ProjectTo<CardPaymentDto>(mapper.ConfigurationProvider)
    .ToListAsync(ct);

var cash = await db.Payments.OfType<CashPayment>()
    .ProjectTo<CashPaymentDto>(mapper.ConfigurationProvider)
    .ToListAsync(ct);""")

    h2(d, "2. Yassi (flat) DTO ishlatish")

    code(d, """public sealed class PaymentListItemDto
{
    public Guid Id { get; init; }
    public decimal Amount { get; init; }
    public PaymentMethod Method { get; init; }

    // hamma turning maydonlari, kerak bo'lmaganlari null
    public string? CardLast4 { get; init; }
    public string? CashierName { get; init; }
}""")

    para(d, "Ro'yxat uchun ikkinchi variantni afzal ko'raman: bitta "
            "so'rov, bitta DTO, ierarxiya murakkabligi yo'q. "
            "API javobida ham mijoz uchun shunday yassi struktura "
            "ko'pincha qulayroq bo'ladi — u `method` maydoniga qarab "
            "nimani ko'rsatishni hal qiladi.")

    # ───────────────────────────────────────────
    h1(d, "5. Mapster'da")

    code(d, """TypeAdapterConfig<Payment, PaymentDto>.NewConfig()
    .Include<CardPayment, CardPaymentDto>()
    .Include<CashPayment, CashPaymentDto>();""")

    para(d, "Mapster'da sintaksis juda o'xshash. Uning afzalligi — "
            "kod generatsiyasi: `Mapster.Tool` bilan mapping kodi "
            "kompilyatsiya vaqtida yasaladi, shuning uchun "
            "noto'g'ri konfiguratsiya **kompilyatsiyada** aniqlanadi.")

    # ───────────────────────────────────────────
    h1(d, "6. Alternativa: polimorfizmdan voz kechish")

    para(d, "Mapping ierarxiyasini sozlash har doim biror darajada "
            "mo'rt bo'ladi. Shuning uchun ba'zan eng oddiy yechim — "
            "har bir turni aniq map qilish:")

    code(d, """public static PaymentDto ToDto(this Payment payment) => payment switch
{
    CardPayment c => new CardPaymentDto
    {
        Id = c.Id,
        Amount = c.Amount,
        CardLast4 = c.CardLast4
    },

    CashPayment h => new CashPaymentDto
    {
        Id = h.Id,
        Amount = h.Amount,
        CashierName = h.CashierName
    },

    _ => throw new NotSupportedException($"Qo'llanmaydi: {payment.GetType().Name}")
};""")

    para(d, "Kod uzunroq, lekin uchta aniq foydasi bor. Birinchisi — "
            "kompilyator tekshiradi: yangi maydon qo'shilsa va "
            "ko'chirilmasa, bu ko'rinadi. Ikkinchisi — yangi tur "
            "qo'shilganda `default` tarmoqda darhol xato chiqadi, jim "
            "noto'g'ri map bo'lmaydi. Uchinchisi — debug qilish oson, "
            "chunki hech qanday reflection yo'q.")

    note(d, "Mening tanlovim",
         "Ierarxiya kichik va barqaror bo'lsa — qo'lda yozaman. "
         "Ierarxiya katta va o'xshash maydonlar ko'p bo'lsa — "
         "`IncludeAllDerived()` bilan mapping kutubxonasi. Lekin har "
         "ikki holatda `AssertConfigurationIsValid()` testi albatta "
         "bo'ladi.")

    sources(d, [
        ("Mapping Inheritance — AutoMapper",
         "https://docs.automapper.org/en/stable/Mapping-inheritance.html"),
        ("Queryable Extensions — AutoMapper",
         "https://docs.automapper.org/en/stable/Queryable-Extensions.html"),
        ("Inheritance mapping — EF Core",
         "https://learn.microsoft.com/en-us/ef/core/modeling/inheritance"),
        ("Mapster — inheritance",
         "https://github.com/MapsterMapper/Mapster/wiki/Custom-mapping"),
    ])
