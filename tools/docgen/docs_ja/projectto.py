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

    # ───────────────────────────────────────────
    h1(d, "7. Amaliyotdan: ProjectTo oddiy ro'yxatlarda, qo'lda projeksiya og'irlarida")

    para(d, "Ish joyimdagi MAD ERP tizimida `ProjectTo` o'n sakkizta joyda "
            "ishlatiladi. Shu hajmdagi kodbaza uchun bu kam, va men nega shunday "
            "ekanini tushunishga harakat qildim. Javob 4- va 6-bo'limlardagi "
            "fikrlarni tasdiqladi.")

    h2(d, "7.1 Qayerda ishlatilgan")

    para(d, "Deyarli hamma holatda — sodda ma'lumotnoma ro'yxatlari. Masalan "
            "jinslar, qarindoshlik darajalari, holatlar ro'yxati:")

    code(d, """public Task<WbPagedResult<GenderBriefDto>> Handle(GenderGetListQuery request,
                                                  CancellationToken cancellationToken)
{
    var genders = _context.Genders
        .AsNoTracking()
        .ProjectTo<GenderBriefDto>(_mapper.ConfigurationProvider);

    return genders.AsPagedResultAsync(request);
}""", caption="GenderGetListQueryHandler")

    para(d, "Bu kodda `ProjectTo` ning asosiy yutug'i to'liq ishlaydi. `AsPagedResultAsync` "
            "ustiga `Skip`/`Take` va `Count` qo'shadi, ya'ni ifoda hali ham "
            "`IQueryable` bo'lib turishi shart. 1-bo'limdagi `Map` bilan "
            "farq aynan shu: `Map` bo'lsa butun jadval xotiraga tushib, keyin "
            "sahifalanardi.")

    bullets(d, [
        "`AsNoTracking()` birinchi turadi — bu DTO ga projeksiya bo'lgani uchun "
        "kuzatuv baribir keraksiz, lekin ochiq yozilgani niyatni aniq ko'rsatadi.",
        "Metod `async` emas — `Task` qaytaradi, `await` yo'q. Kichik tafsilot, "
        "lekin ortiqcha holat mashinasini yaratmaydi.",
        "DTO nomi `Brief` bilan tugaydi: ro'yxat uchun qisqa versiya. To'liq "
        "versiya alohida DTO da.",
    ])

    h2(d, "7.2 Og'ir so'rovlarda ProjectTo ishlatilmaydi")

    para(d, "Murakkab obyektlar uchun boshqa yo'l tanlangan — o'z `MapTo` "
            "extension metodi, va unga `AsSplitQuery()` qo'shilgan:")

    code(d, """var result = await _context.Persons
    .AsNoTracking()
    .Where(x => x.Id == request.Id)
    .AsSplitQuery()
    .MapTo<PersonFullDto>(_mapper, _cultureHelper)
    .FirstOrDefaultAsync(cancellationToken);""", caption="PersonGetByIdQueryHandler")

    para(d, "Bu yerda `AsSplitQuery()` bor ekaniga e'tibor bering. 4-bo'limda "
            "`ProjectTo` ning cheklovlari haqida gapirgandim; bu real misol. "
            "`Person` obyektiga o'nlab bog'liq jadval ulangan — manzillar, "
            "hujjatlar, aloqa ma'lumotlari. Bitta `JOIN` bilan o'qilsa, natija "
            "kartezian ko'paytmasiga aylanib, minglab qator qaytarardi. "
            "`AsSplitQuery()` ularni alohida so'rovlarga bo'ladi.")

    para(d, "`MapTo` ning o'z metodi bo'lishi sababi esa — `ICultureHelper`. "
            "Tizim to'rt tilni qo'llab-quvvatlaydi va tarjimalar alohida "
            "jadvallarda yotadi. Ya'ni projeksiya joriy tilni bilishi kerak, "
            "AutoMapper profilining o'zi esa buni bilmaydi.")

    note(d, "Mana bu menga 6-bo'limdagi fikrni boshqa tomondan ko'rsatdi:",
         "6-bo'limda qo'lda projeksiya ko'pincha eng toza yechim ekanini yozgandim. "
         "Bu yerda esa uchinchi yo'l tanlangan: AutoMapper qoladi, lekin uning "
         "ustiga o'z qatlami yoziladi. Shunda profil qayta ishlatiladi, til "
         "konteksti esa tashqaridan beriladi. Narxi — bu `MapTo` nima qilayotganini "
         "bilish uchun yana bir fayl ochish kerak, ya'ni 1-bo'limdagi \"AutoMapper "
         "SQL ni yashiradi\" muammosi ikki baravar kuchayadi. Qo'lda `Select` "
         "yozilsa SQL ko'z oldida bo'lardi.")

    h2(d, "7.3 Xulosa qilib")

    para(d, "Shu kodbazadan chiqargan mezonim quyidagicha bo'ldi:")

    table(d, ["Holat", "Tanlov"],
          [["Sodda ro'yxat, sahifalash kerak", "`ProjectTo` — eng qisqa va to'g'ri"],
           ["Ko'p bog'liq jadval", "`AsSplitQuery` + o'z projeksiya metodi"],
           ["Hisoblangan maydonlar, shartli mantiq", "Qo'lda `Select` — SQL ko'rinib turadi"]],
          widths=[7.0, 8.5])

    sources(d, [
        ("Queryable Extensions — AutoMapper",
         "https://docs.automapper.org/en/stable/Queryable-Extensions.html"),
        ("Mapster — Queryable extensions",
         "https://github.com/MapsterMapper/Mapster/wiki/Queryable-Extensions"),
        ("Efficient Querying — EF Core",
         "https://learn.microsoft.com/en-us/ef/core/performance/efficient-querying"),
    ])
