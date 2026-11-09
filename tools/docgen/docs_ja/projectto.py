# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "ProjectTo"
CATEGORY = "AutoMapper/Mapster"
TITLE = "ProjectTo"
SUBTITLE = "Mapping'ni bazada bajarish"
FILENAME = "ProjectTo.docx"


def build(d):
    h1(d, "1. Map va ProjectTo orasidagi farq")

    para(d, "`Map` obyektni **xotirada** aylantiradi. `ProjectTo` esa "
            "mapping konfiguratsiyasini LINQ ifodasiga aylantiradi, "
            "shuning uchun u SQL ga tarjima qilinadi.")

    code(d, """// Map: butun entity bazadan o'qiladi, keyin aylantiriladi
var orders = await db.Orders.ToListAsync(ct);
var dtos = mapper.Map<List<OrderDto>>(orders);

// ProjectTo: faqat DTO uchun kerakli ustunlar o'qiladi
var dtos = await db.Orders
    .ProjectTo<OrderDto>(mapper.ConfigurationProvider)
    .ToListAsync(ct);""")

    para(d, "Farq yasagan SQL da ko'rinadi:")

    code(d, """-- Map bilan
SELECT o.id, o.number, o.customer_id, o.total, o.status, o.created_at,
       o.updated_at, o.notes, o.internal_comment, o.version, ...
FROM orders AS o

-- ProjectTo bilan (DTO da 3 maydon bo'lsa)
SELECT o.id, o.number, o.total
FROM orders AS o""")

    # ───────────────────────────────────────────
    h1(d, "2. Nega bu muhim")

    bullets(d, [
        "**Kam ustun o'qiladi.** `notes` yoki `byte[] attachment` kabi "
        "og'ir ustunlar kerak bo'lmasa, ular umuman o'qilmaydi.",
        "**N+1 muammosi yo'q.** `ProjectTo` bog'liq ma'lumotni "
        "`Include` siz, bitta so'rovda `JOIN` yoki subquery bilan "
        "oladi.",
        "**Change tracker ishlatilmaydi.** Natija entity emas, DTO — "
        "shuning uchun snapshot olinmaydi va xotira kam sarflanadi.",
        "**Filtr va sahifalash bazada bajariladi.**",
    ])

    code(d, """// Bog'liq ma'lumot ham bitta so'rovda keladi
public sealed class OrderDto
{
    public Guid Id { get; init; }
    public string Number { get; init; } = "";
    public string CustomerName { get; init; } = "";    // Customer.Name dan
    public int ItemCount { get; init; }                // Items.Count dan
    public decimal Total { get; init; }
}""")

    code(d, """CreateMap<Order, OrderDto>()
    .ForMember(d => d.CustomerName, o => o.MapFrom(s => s.Customer.Name))
    .ForMember(d => d.ItemCount, o => o.MapFrom(s => s.Items.Count));""")

    para(d, "`Include` yozmaganim ham `Customer.Name` keladi, chunki "
            "`ProjectTo` ifodani SQL ga tarjima qilib `JOIN` qo'shadi. "
            "Bu N+1 muammosini dizayn darajasida oldini oladi.")

    # ───────────────────────────────────────────
    h1(d, "3. Ro'yxatga olish va ishlatish")

    code(d, """builder.Services.AddAutoMapper(cfg =>
    cfg.AddMaps(typeof(OrderProfile).Assembly));""")

    code(d, """public sealed class OrderQueries(AppDbContext db, IMapper mapper)
{
    public async Task<PagedResult<OrderDto>> ListAsync(
        OrderFilter filter, CancellationToken ct)
    {
        var query = db.Orders.AsNoTracking();

        if (filter.Status is not null)
            query = query.Where(o => o.Status == filter.Status);

        var total = await query.CountAsync(ct);

        var items = await query
            .OrderByDescending(o => o.CreatedAt)
            .Skip((filter.Page - 1) * filter.Size)
            .Take(filter.Size)
            .ProjectTo<OrderDto>(mapper.ConfigurationProvider)
            .ToListAsync(ct);

        return new PagedResult<OrderDto>(items, total);
    }
}""")

    note(d, "Tartib",
         "`ProjectTo` ni zanjirning **oxirida** qo'yaman — filtr va "
         "saralashdan keyin. Undan keyin qo'shilgan `Where` DTO "
         "maydonlari ustida ishlaydi, bu esa har doim tarjima "
         "qilinmaydi.")

    # ───────────────────────────────────────────
    h1(d, "4. Cheklovlar")

    para(d, "`ProjectTo` ifodaga aylanishi kerak, shuning uchun hamma "
            "mapping usuli unda ishlamaydi.")

    h2(d, "ConvertUsing va custom resolver ishlamaydi")

    code(d, """// ProjectTo bilan ishlamaydi — bu .NET kodi, SQL emas
CreateMap<Order, OrderDto>()
    .ForMember(d => d.Label, o => o.MapFrom<OrderLabelResolver>());

// Ishlaydi — ifoda sifatida yozilgan
CreateMap<Order, OrderDto>()
    .ForMember(d => d.Label, o => o.MapFrom(s => s.Number + " / " + s.Customer.Name));""")

    h2(d, "AfterMap va BeforeMap chaqirilmaydi")

    para(d, "Ular obyekt yaratilgandan keyin ishlaydi, lekin "
            "`ProjectTo` obyektni SQL natijasidan to'g'ridan-to'g'ri "
            "quradi — hech qanday hook chaqirilmaydi. Bu jim farq, "
            "shuning uchun `Map` dan `ProjectTo` ga o'tganda e'tibor "
            "berish kerak.")

    h2(d, "Tarjima qilinmaydigan metodlar")

    code(d, """// Xato: SQL ga tarjima qilinmaydi
.ForMember(d => d.Formatted, o => o.MapFrom(s => s.Total.ToString("N2")))""")

    para(d, "Formatlash kabi ishlarni DTO ichida hisoblanadigan xossa "
            "qilib qo'yaman — u natija kelgandan keyin .NET da "
            "bajariladi:")

    code(d, """public sealed class OrderDto
{
    public decimal Total { get; init; }
    public string Formatted => Total.ToString("N2");     // SQL ga tushmaydi
}""")

    # ───────────────────────────────────────────
    h1(d, "5. Mapster bilan ekvivalenti")

    code(d, """// Mapster: ProjectToType
var dtos = await db.Orders
    .ProjectToType<OrderDto>()
    .ToListAsync(ct);""")

    code(d, """// Konfiguratsiya
TypeAdapterConfig<Order, OrderDto>.NewConfig()
    .Map(d => d.CustomerName, s => s.Customer.Name)
    .Map(d => d.ItemCount, s => s.Items.Count);""")

    para(d, "Mapster'ning afzalligi — u mapping kodini kompilyatsiya "
            "vaqtida generatsiya qilishi mumkin (`Mapster.Tool`), "
            "shuning uchun reflection yo'q va tezroq. AutoMapper esa "
            "ekotizimda ancha keng tarqalgan.")

    # ───────────────────────────────────────────
    h1(d, "6. Qo'lda projeksiya — ko'pincha eng toza yechim")

    code(d, """var dtos = await db.Orders
    .AsNoTracking()
    .Where(o => o.Status == OrderStatus.Paid)
    .Select(o => new OrderDto
    {
        Id = o.Id,
        Number = o.Number,
        CustomerName = o.Customer.Name,
        ItemCount = o.Items.Count,
        Total = o.Total
    })
    .ToListAsync(ct);""")

    para(d, "Bu kod `ProjectTo` bilan bir xil SQL yasaydi, lekin "
            "qo'shimcha kutubxona talab qilmaydi va eng muhimi — "
            "**nima bo'layotgani ko'rinib turadi**. Mapping "
            "konfiguratsiyasini ochib ko'rish kerak emas.")

    para(d, "Shuning uchun o'zim uchun qoida shunday: so'rov tomonida "
            "(query/read model) qo'lda `Select` yozaman — u aniq va "
            "nazoratda. Mapping kutubxonasini esa ko'p o'xshash DTO "
            "bo'lgan va mapping haqiqatan takrorlanadigan joylarda "
            "ishlataman.")

    note(d, "Eslatma",
         "Qo'lda projeksiyaning yana bir foydasi — kompilyator "
         "tekshiradi. Mapping konfiguratsiyasidagi xato esa faqat ish "
         "vaqtida yoki `AssertConfigurationIsValid()` testida "
         "aniqlanadi.")

    sources(d, [
        ("Queryable Extensions — AutoMapper",
         "https://docs.automapper.org/en/stable/Queryable-Extensions.html"),
        ("Mapster — Queryable extensions",
         "https://github.com/MapsterMapper/Mapster/wiki/Queryable-Extensions"),
        ("Efficient Querying — EF Core",
         "https://learn.microsoft.com/en-us/ef/core/performance/efficient-querying"),
    ])
