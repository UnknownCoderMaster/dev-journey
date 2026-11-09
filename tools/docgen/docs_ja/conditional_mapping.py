# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "Conditional Mapping"
CATEGORY = "AutoMapper/Mapster"
TITLE = "Shartli Mapping"
SUBTITLE = "Condition, PreCondition va NullSubstitute"
FILENAME = "Conditional Mapping.docx"


def build(d):
    h1(d, "1. Muammo")

    para(d, "Ba'zan maydonni faqat ma'lum shartda ko'chirish kerak. "
            "Masalan `null` yoki nol qiymat manba'dan kelsa, maqsad "
            "obyektdagi mavjud qiymat saqlanib qolishi kerak — "
            "ayniqsa mavjud obyektni yangilayotganda.")

    code(d, """// PATCH so'rovi: faqat yuborilgan maydonlar o'zgarishi kerak
public sealed class UpdateCustomerRequest
{
    public string? Name { get; init; }
    public string? Phone { get; init; }
    public string? Email { get; init; }
}""")

    para(d, "Oddiy mapping bu holatda mavjud qiymatlarni `null` bilan "
            "ustiga yozib yuboradi — ya'ni yuborilmagan maydonlar "
            "o'chib ketadi.")

    # ───────────────────────────────────────────
    h1(d, "2. Condition")

    code(d, """CreateMap<UpdateCustomerRequest, Customer>()
    .ForMember(d => d.Name, o => o.Condition(s => s.Name is not null))
    .ForMember(d => d.Phone, o => o.Condition(s => !string.IsNullOrWhiteSpace(s.Phone)))
    .ForMember(d => d.Email, o => o.Condition(s => s.Email is not null));""")

    para(d, "`Condition` manba qiymati **hisoblangandan keyin** "
            "tekshiriladi. Shart `false` bo'lsa, maqsad maydoniga "
            "yozilmaydi va undagi qiymat o'zgarmaydi.")

    para(d, "Shartda manba, maqsad va joriy qiymatlarni ham ko'rish "
            "mumkin:")

    code(d, """.ForMember(d => d.Discount, o => o.Condition(
    (src, dest, srcValue, destValue) => srcValue > destValue));""")

    para(d, "Bu shakl \"faqat qiymat oshsa yangila\" kabi qoidalarni "
            "ifodalash imkonini beradi.")

    h2(d, "Butun mapping uchun umumiy shart")

    code(d, """CreateMap<UpdateCustomerRequest, Customer>()
    .ForAllMembers(o => o.Condition((src, dest, srcValue) => srcValue is not null));""")

    para(d, "Bu PATCH semantikasi uchun eng qisqa yechim. Lekin uning "
            "kamchiligi bor: `null` ni **ataylab** qo'ymoqchi bo'lsam "
            "(masalan telefonni o'chirish), buni ifodalab bo'lmaydi.")

    note(d, "PATCH uchun to'g'ri yechim",
         "\"Yuborilmagan\" va \"ataylab null\" ni ajratish kerak bo'lsa, "
         "`Optional<T>` kabi o'ram tur yoki `JsonPatchDocument` "
         "ishlataman. Mapping sharti bu ikki holatni ajrata olmaydi.")

    # ───────────────────────────────────────────
    h1(d, "3. PreCondition")

    code(d, """.ForMember(d => d.FullAddress, o =>
{
    o.PreCondition(s => s.Address is not null);
    o.MapFrom(s => $"{s.Address!.City}, {s.Address.Street}");
});""")

    para(d, "`PreCondition` manba qiymatini hisoblashdan **oldin** "
            "tekshiriladi. Shuning uchun u ikki holatda zarur:")

    bullets(d, [
        "Qiymatni hisoblash qimmat bo'lsa — keraksiz hisoblashni "
        "oldini oladi.",
        "Hisoblash `null` da exception berishi mumkin bo'lsa — "
        "yuqoridagi misolda `s.Address.City` aynan shunday.",
    ])

    para(d, "Farqni esda saqlash uchun: `PreCondition` — \"hisoblash "
            "kerakmi?\", `Condition` — \"hisoblangan qiymatni yozish "
            "kerakmi?\"")

    # ───────────────────────────────────────────
    h1(d, "4. NullSubstitute va Ignore")

    code(d, """// null kelsa, standart qiymat qo'yiladi
.ForMember(d => d.Notes, o => o.NullSubstitute("Izoh yo'q"))
.ForMember(d => d.Rating, o => o.NullSubstitute(0))

// Maydon umuman ko'chirilmaydi
.ForMember(d => d.CreatedAt, o => o.Ignore())
.ForMember(d => d.Version, o => o.Ignore())""")

    para(d, "`Ignore` ni ko'pincha audit maydonlari uchun ishlataman — "
            "`CreatedAt`, `CreatedBy`, `Version`. Ularni tashqi so'rov "
            "boshqarmasligi kerak, shuning uchun mapping ularga "
            "tegmasligi muhim.")

    para(d, "Bu nafaqat qulaylik, balki **xavfsizlik** masalasi: agar "
            "DTO da `IsAdmin` maydoni bo'lsa va u mapping orqali "
            "entity'ga tushsa, foydalanuvchi o'ziga admin huquqini "
            "bera oladi. Bu \"mass assignment\" zaifligi deb ataladi.")

    note(d, "Mening qoidam",
         "Entity'ga yozishda `Ignore` ro'yxatiga tayanmaslikka harakat "
         "qilaman — yangi maydon qo'shilganda uni `Ignore` ga "
         "qo'shishni unutish oson. O'rniga domen metodidan o'taman: "
         "`customer.UpdateContacts(phone, email)` — unda faqat "
         "ruxsat etilgan maydonlar o'zgaradi.")

    # ───────────────────────────────────────────
    h1(d, "5. Shartli turga map qilish")

    code(d, """CreateMap<Payment, PaymentDto>()
    .ForMember(d => d.Details, o => o.MapFrom(s =>
        s.Method == PaymentMethod.Card
            ? $"**** {s.CardLast4}"
            : s.Method == PaymentMethod.Cash
                ? "Naqd"
                : s.BankAccount));""")

    para(d, "Bu ishlaydi, lekin o'qish qiyin. Shart murakkab bo'lsa, "
            "mapping ichida emas, DTO ichida hisoblanadigan xossa "
            "qilib yozishni afzal ko'raman:")

    code(d, """public sealed class PaymentDto
{
    public PaymentMethod Method { get; init; }
    public string? CardLast4 { get; init; }
    public string? BankAccount { get; init; }

    public string Details => Method switch
    {
        PaymentMethod.Card => $"**** {CardLast4}",
        PaymentMethod.Cash => "Naqd",
        _ => BankAccount ?? "—"
    };
}""")

    para(d, "Mantiq koddagi oddiy joyda turadi, uni test qilish oson va "
            "mapping konfiguratsiyasi sodda qoladi.")

    # ───────────────────────────────────────────
    h1(d, "6. Mapster'da ekvivalentlari")

    code(d, """TypeAdapterConfig<UpdateCustomerRequest, Customer>.NewConfig()
    .IgnoreNullValues(true)                            // ForAllMembers Condition
    .Map(d => d.Phone, s => s.Phone, s => s.Phone != null)   // shartli
    .Ignore(d => d.CreatedAt);""")

    para(d, "`IgnoreNullValues(true)` — PATCH uchun eng qisqa yo'l. "
            "Mapster'ning sintaksisi bu holatda ixchamroq, lekin "
            "tamoyil bir xil.")

    # ───────────────────────────────────────────
    h1(d, "7. Konfiguratsiyani sinash")

    para(d, "Shartli mapping konfiguratsiyasi o'sgan sari undagi xato "
            "ehtimoli oshadi. Shuning uchun uni test bilan "
            "qoplash kerak:")

    code(d, """[Fact]
public void MappingConfiguration_IsValid()
{
    var config = new MapperConfiguration(cfg =>
        cfg.AddMaps(typeof(CustomerProfile).Assembly));

    config.AssertConfigurationIsValid();
}""")

    para(d, "Bu test maqsad obyektidagi **map qilinmagan** maydonlarni "
            "topadi. Ya'ni DTO ga yangi maydon qo'shilib, mapping "
            "yozilmasa, test qizil bo'ladi — bu jim `null` dan "
            "ancha yaxshi.")

    code(d, """[Fact]
public void Update_WithNullPhone_KeepsExistingValue()
{
    var customer = new Customer { Phone = "+998901234567" };
    var request = new UpdateCustomerRequest { Name = "Yangi nom" };

    _mapper.Map(request, customer);

    Assert.Equal("Yangi nom", customer.Name);
    Assert.Equal("+998901234567", customer.Phone);   // o'zgarmadi
}""")

    sources(d, [
        ("Conditional Mapping — AutoMapper",
         "https://docs.automapper.org/en/stable/Conditional-mapping.html"),
        ("Null substitution — AutoMapper",
         "https://docs.automapper.org/en/stable/Null-substitution.html"),
        ("Configuration validation — AutoMapper",
         "https://docs.automapper.org/en/stable/Configuration-validation.html"),
        ("Mapster — ignore null values",
         "https://github.com/MapsterMapper/Mapster/wiki/Config"),
    ])
