# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "abstraction"
CATEGORY = "OOP"
TITLE = "Abstraksiya"
SUBTITLE = "Muhimni ko'rsatish, tafsilotni yashirish"
FILENAME = "abstraction.docx"


def build(d):
    h1(d, "1. Abstraksiya nima")

    para(d, "Abstraksiya — tizimni **nima qilishi** bo'yicha tasvirlash, "
            "**qanday qilishini** yashirish. Chaqiruvchi natijani biladi, "
            "lekin uning qanday olinganini bilmaydi va bilishi ham kerak "
            "emas.")

    para(d, "Inkapsulyatsiya bilan chalkashtirmaslik kerak: "
            "inkapsulyatsiya **holatni** himoya qiladi, abstraksiya esa "
            "**murakkablikni** yashiradi. Ikkisi birga ishlaydi, lekin "
            "maqsadi boshqa.")

    code(d, """// Nima qilishini bildiradi — qanday qilishini aytmaydi
public interface IFileStorage
{
    Task<string> SaveAsync(Stream content, string fileName, CancellationToken ct);
    Task<Stream> OpenReadAsync(string key, CancellationToken ct);
    Task DeleteAsync(string key, CancellationToken ct);
}""")

    para(d, "Bu interfeysni ishlatadigan kod fayl diskda, MinIO'da yoki "
            "Azure Blob'da saqlanayotganini bilmaydi. Shuning uchun "
            "saqlash joyini almashtirish chaqiruvchi kodga tegmaydi.")

    # ───────────────────────────────────────────
    h1(d, "2. interface va abstract class")

    table(d, ["", "`interface`", "`abstract class`"],
          [["Nechta meros", "Cheklanmagan", "Faqat bitta"],
           ["Holat (maydon)", "Yo'q", "Bo'lishi mumkin"],
           ["Konstruktor", "Yo'q", "Bor"],
           ["Kirish modifikatori", "Hamma a'zo ochiq", "Har xil bo'lishi mumkin"],
           ["Standart amalga oshirish", "C# 8+ da mumkin", "Tabiiy"],
           ["Nimani ifodalaydi", "Qobiliyat (nima qila oladi)",
            "Tur (nima ekanligi)"]],
          widths=[4.4, 5.0, 5.1])

    para(d, "Tanlov qoidam shunday. Agar \"bu narsa shu ishni qila "
            "oladi\" degan gapni ifodalamoqchi bo'lsam — interfeys "
            "(`IFileStorage`, `IDisposable`, `IValidator`). Agar \"bu "
            "narsa shu turdagi narsa\" bo'lsa va umumiy kod ham kerak "
            "bo'lsa — abstrakt klass.")

    code(d, """// Abstrakt klass: umumiy kod + majburiy qism
public abstract class ReportGenerator
{
    // shablon metod — umumiy oqim shu yerda
    public async Task<byte[]> GenerateAsync(ReportRequest request, CancellationToken ct)
    {
        Validate(request);
        var data = await LoadDataAsync(request, ct);
        return Render(data);
    }

    protected virtual void Validate(ReportRequest request)
    {
        if (request.To < request.From)
            throw new ArgumentException("Sana oralig'i noto'g'ri");
    }

    protected abstract Task<ReportData> LoadDataAsync(
        ReportRequest request, CancellationToken ct);

    protected abstract byte[] Render(ReportData data);
}""")

    para(d, "Bu yerda umumiy ketma-ketlik bazaviy klassda, farq "
            "qiladigan qadamlar esa hosilalarda. Hosila faqat o'z "
            "qismini yozadi — oqimni qayta yozishi mumkin emas.")

    # ───────────────────────────────────────────
    h1(d, "3. Abstraksiyaning darajasini to'g'ri tanlash")

    para(d, "Eng ko'p uchraydigan muammo — abstraksiya **noto'g'ri "
            "darajada** qilinishi. Ikki tomonga ham xato bo'lishi mumkin.")

    h2(d, "Juda past daraja — tafsilot oqib chiqadi")

    code(d, """// Interfeys SQL haqida gapiryapti — abstraksiya ishlamayapti
public interface IOrderRepository
{
    Task<DataTable> ExecuteQueryAsync(string sql, SqlParameter[] parameters);
}""")

    para(d, "Bu interfeysni ishlatadigan kod baribir SQL yozishi kerak, "
            "ya'ni bazadan ajralmaydi. Abstraksiya nomi bor, foydasi yo'q.")

    h2(d, "Juda yuqori daraja — foydasiz umumiylik")

    code(d, """// Nimani bildiradi? Hech narsani
public interface IManager
{
    Task<object> ProcessAsync(object input);
}""")

    para(d, "Bunday interfeys hech narsani kafolatlamaydi va har bir "
            "chaqiruvda cast kerak bo'ladi. U mavjud bo'lsa ham kod "
            "tushunarli bo'lmaydi.")

    h2(d, "To'g'ri daraja — domen tilida")

    code(d, """public interface IOrderRepository
{
    Task<Order?> FindWithItemsAsync(Guid id, CancellationToken ct);
    Task<IReadOnlyList<Order>> ListOverdueAsync(DateOnly asOf, CancellationToken ct);
    void Add(Order order);
}""")

    para(d, "Interfeys **domen tilida** gapiradi: \"muddati o'tgan "
            "buyurtmalar\" — bu biznes tushunchasi, SQL emas. Shuning "
            "uchun chaqiruvchi kod bazani bilmaydi va interfeys o'zini "
            "tushuntiradi.")

    # ───────────────────────────────────────────
    h1(d, "4. Qachon abstraksiya qo'shmaslik kerak")

    para(d, "Har bir klassga interfeys yasash keng tarqalgan odat, lekin u "
            "ko'pincha foyda bermaydi:")

    code(d, """// Bitta amalga oshirish, hech qachon almashtirilmaydi
public interface IOrderMapper
{
    OrderDto ToDto(Order order);
}

public sealed class OrderMapper : IOrderMapper { /* ... */ }""")

    para(d, "Agar amalga oshirish bitta bo'lsa, almashtirish rejasi "
            "bo'lmasa va u sof funksiya bo'lsa (tashqi dunyoga murojaat "
            "qilmasa) — interfeys faqat qo'shimcha fayl va bir "
            "qadam qo'shadi. Testda ham uni mock qilish kerak emas, "
            "chunki haqiqiy versiyasi tez va deterministik.")

    note(d, "Mening o'lchovim",
         "Abstraksiya qo'shishdan oldin savol beraman: **buning "
         "ikkinchi amalga oshirilishi bo'ladimi, yoki uni testda "
         "almashtirishim kerakmi?** Ikkisiga ham \"yo'q\" bo'lsa, "
         "interfeysni keyinroq — haqiqatan kerak bo'lganda — "
         "qo'shaman. IDE buni bir necha sekundda qiladi.")

    para(d, "Tashqi dunyoga chiqadigan narsalar esa deyarli har doim "
            "abstraksiyaga arziydi: baza, HTTP, fayl tizimi, navbat, "
            "vaqt, tasodifiy son. Ular testni sekin va nobarqaror "
            "qiladi, shuning uchun almashtirilishi kerak.")

    # ───────────────────────────────────────────
    h1(d, "5. Oqib chiqadigan abstraksiya")

    para(d, "Abstraksiya ostidagi tafsilot baribir sezilib turadigan "
            "holat. Klassik misol — `IQueryable` qaytaradigan "
            "repozitoriy:")

    code(d, """public interface IRepository<T>
{
    IQueryable<T> Query();
}""")

    para(d, "Ko'rinishdan baza yashirilgan, lekin amalda yo'q: "
            "chaqiruvchi `Include`, `AsSplitQuery` kabi EF Core "
            "metodlarini ishlatadi va qaysi ifoda SQL ga tarjima "
            "bo'lishini bilishi kerak. Ya'ni u EF ni biladi — abstraksiya "
            "shunchaki qo'shimcha qatlam bo'lib qoladi.")

    para(d, "Bunday holatda ikki yo'ldan birini tanlayman: yoki "
            "abstraksiyani aniq metodlar bilan yopiq qilaman, yoki "
            "umuman abstraksiya qo'ymasdan `DbContext` bilan "
            "to'g'ridan-to'g'ri ishlayman — ikkinchisi ko'pincha "
            "halolroq, chunki bog'liqlik ko'rinib turadi.")

    # ───────────────────────────────────────────
    h1(d, "6. Nima foyda beradi")

    bullets(d, [
        "**Almashtirish imkoni.** Fayl saqlashni diskdan MinIO'ga "
        "o'tkazish bitta ro'yxatga olish qatorini o'zgartirish bilan "
        "bo'ladi.",
        "**Testda izolyatsiya.** Tashqi servisni stub bilan almashtirib, "
        "testni tez va barqaror qilish mumkin.",
        "**Parallel ishlash.** Interfeys kelishilgandan keyin ikki odam "
        "ikki tomonni bir vaqtda yozishi mumkin.",
        "**Murakkablikni cheklash.** Kodning bir qismini o'qiyotganda "
        "butun tizimni tushunish shart bo'lmaydi.",
    ])

    para(d, "Lekin har bir abstraksiya bitta bilvosita qatlam "
            "(indirection) qo'shadi — kod o'qiganda \"bu aslida qayerda "
            "bajariladi\" degan savol paydo bo'ladi. Shuning uchun "
            "abstraksiya **narxga ega** va u foydadan kam bo'lishi "
            "kerak.")

    sources(d, [
        ("Object-oriented programming in C#",
         "https://learn.microsoft.com/en-us/dotnet/csharp/fundamentals/object-oriented/"),
        ("Interfaces — C# programming guide",
         "https://learn.microsoft.com/en-us/dotnet/csharp/fundamentals/types/interfaces"),
        ("When to use interfaces and abstract classes",
         "https://learn.microsoft.com/en-us/dotnet/standard/design-guidelines/choosing-between-class-and-interface"),
    ])
