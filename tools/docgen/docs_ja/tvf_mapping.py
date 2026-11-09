# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "Table-valued function mapping"
CATEGORY = "EF CORE"
TITLE = "Table-Valued Function Mapping"
SUBTITLE = "Jadval qaytaradigan baza funksiyasini LINQ da ishlatish"
FILENAME = "Table-valued function mapping.docx"


def build(d):
    h1(d, "1. TVF nima va qachon kerak")

    para(d, "Table-valued function — bazadagi funksiya, u skalyar qiymat "
            "emas, **satrlar to'plamini** qaytaradi. Shuning uchun uni "
            "`SELECT` da jadval kabi ishlatish mumkin.")

    para(d, "EF Core uni map qilganda eng muhim xossa shu: TVF natijasi "
            "ustida **LINQ'ni davom ettirish** mumkin. Ya'ni filtr, "
            "saralash va `JOIN` bitta SQL so'rovida bazada bajariladi.")

    para(d, "Men uni shu holatlarda ishlataman:")

    bullets(d, [
        "Murakkab hisoblash SQL da ancha samarali bo'lsa (rekursiv "
        "so'rov, oyna funksiyalari).",
        "Bir xil murakkab so'rov ko'p joyda kerak bo'lsa va uni bazada "
        "markazlashtirish qulay bo'lsa.",
        "Legacy bazada allaqachon shunday funksiyalar bo'lsa.",
    ])

    # ───────────────────────────────────────────
    h1(d, "2. Postgres'da funksiya yaratish")

    code(d, """CREATE OR REPLACE FUNCTION branch_sales(p_from date, p_to date)
RETURNS TABLE (
    branch_id   bigint,
    branch_name text,
    order_count bigint,
    revenue     numeric
)
LANGUAGE sql
STABLE
AS $$
    SELECT b.id,
           b.name,
           count(o.id),
           COALESCE(sum(o.total), 0)
    FROM branches b
    LEFT JOIN orders o
           ON o.branch_id = b.id
          AND o.created_at >= p_from
          AND o.created_at <  p_to
    GROUP BY b.id, b.name;
$$;""")

    para(d, "`STABLE` belgisi muhim: funksiya bazani o'qiydi, lekin "
            "bitta so'rov ichida bir xil natija beradi. Bu planner'ga "
            "optimallashtirish imkonini beradi. `VOLATILE` (standart) "
            "bo'lsa, funksiya har bir satr uchun qayta chaqirilishi "
            "mumkin.")

    # ───────────────────────────────────────────
    h1(d, "3. EF Core'da map qilish")

    para(d, "Natija uchun kalitsiz entity e'lon qilinadi:")

    code(d, """public sealed class BranchSales
{
    public long BranchId { get; init; }
    public string BranchName { get; init; } = "";
    public long OrderCount { get; init; }
    public decimal Revenue { get; init; }
}""")

    code(d, """modelBuilder.Entity<BranchSales>().HasNoKey();""")

    para(d, "Keyin `DbContext` da funksiyani ifodalaydigan metod "
            "yoziladi:")

    code(d, """public sealed class AppDbContext(DbContextOptions<AppDbContext> options)
    : DbContext(options)
{
    public IQueryable<BranchSales> BranchSales(DateOnly from, DateOnly to)
        => FromExpression(() => BranchSales(from, to));

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.Entity<BranchSales>().HasNoKey();

        modelBuilder
            .HasDbFunction(() => BranchSales(default, default))
            .HasName("branch_sales");
    }
}""")

    para(d, "`FromExpression` EF ga \"bu metod chaqiruvi SQL "
            "funksiyasiga aylanadi\" deb aytadi. Metod tanasi hech "
            "qachon .NET da bajarilmaydi.")

    # ───────────────────────────────────────────
    h1(d, "4. Ishlatish va kompozitsiya")

    code(d, """var top = await db.BranchSales(from, to)
    .Where(s => s.OrderCount > 0)
    .OrderByDescending(s => s.Revenue)
    .Take(10)
    .ToListAsync(ct);""")

    code(d, """-- EF yasagan SQL
SELECT b.branch_id, b.branch_name, b.order_count, b.revenue
FROM branch_sales(@p_from, @p_to) AS b
WHERE b.order_count > 0
ORDER BY b.revenue DESC
LIMIT 10""")

    para(d, "Diqqat qilish kerak bo'lgan asosiy narsa shu: filtr, "
            "saralash va `LIMIT` **bazada** bajarildi. Agar funksiyani "
            "oddiy `FromSqlRaw` bilan chaqirsam, bu kompozitsiya "
            "cheklangan bo'lardi.")

    para(d, "Boshqa jadval bilan `JOIN` ham mumkin:")

    code(d, """var query = from s in db.BranchSales(from, to)
            join b in db.Branches on s.BranchId equals b.Id
            where b.IsActive
            select new { b.City, s.Revenue };""")

    # ───────────────────────────────────────────
    h1(d, "5. Skalyar funksiyani map qilish")

    para(d, "TVF bilan birga skalyar funksiyalarni ham map qilish "
            "mumkin — bu `Where` ichida baza funksiyasini ishlatish "
            "imkonini beradi:")

    code(d, """CREATE OR REPLACE FUNCTION order_age_days(p_created timestamptz)
RETURNS integer
LANGUAGE sql IMMUTABLE
AS $$ SELECT EXTRACT(DAY FROM now() - p_created)::integer; $$;""")

    code(d, """public static class DbFunctions
{
    [DbFunction("order_age_days")]
    public static int OrderAgeDays(DateTimeOffset createdAt)
        => throw new NotSupportedException("Faqat LINQ ichida ishlatiladi");
}""")

    code(d, """modelBuilder.HasDbFunction(
    typeof(DbFunctions).GetMethod(nameof(DbFunctions.OrderAgeDays))!);""")

    code(d, """var old = await db.Orders
    .Where(o => DbFunctions.OrderAgeDays(o.CreatedAt) > 30)
    .ToListAsync(ct);""")

    para(d, "Metod tanasidagi `throw` ataylab: u hech qachon "
            "chaqirilmasligi kerak. Agar chaqirilsa, bu ifoda SQL ga "
            "tarjima qilinmaganini bildiradi va xato darhol ko'rinadi.")

    # ───────────────────────────────────────────
    h1(d, "6. Migratsiyada funksiyani boshqarish")

    para(d, "EF Core funksiya kodini o'zi yaratmaydi — faqat uning "
            "mavjudligini biladi. Shuning uchun funksiyani migratsiyaga "
            "qo'lda qo'shaman:")

    code(d, """public partial class AddBranchSalesFunction : Migration
{
    protected override void Up(MigrationBuilder migrationBuilder)
    {
        migrationBuilder.Sql(
            """ + '"""' + """
            CREATE OR REPLACE FUNCTION branch_sales(p_from date, p_to date)
            RETURNS TABLE (branch_id bigint, branch_name text,
                           order_count bigint, revenue numeric)
            LANGUAGE sql STABLE
            AS $func$
                SELECT b.id, b.name, count(o.id), COALESCE(sum(o.total), 0)
                FROM branches b
                LEFT JOIN orders o ON o.branch_id = b.id
                 AND o.created_at >= p_from AND o.created_at < p_to
                GROUP BY b.id, b.name;
            $func$;
            """ + '"""' + """);
    }

    protected override void Down(MigrationBuilder migrationBuilder)
        => migrationBuilder.Sql("DROP FUNCTION IF EXISTS branch_sales(date, date);");
}""")

    note(d, "Amaliy maslahat",
         "Funksiya kodini alohida `.sql` faylda saqlab, migratsiyada "
            "shu fayldan o'qishni afzal ko'raman. Shunda SQL ni IDE "
            "to'g'ri ko'rsatadi va o'zgarishlar git'da aniq ko'rinadi.")

    # ───────────────────────────────────────────
    h1(d, "7. Cheklovlar va alternativalar")

    bullets(d, [
        "Funksiya baza bilan qattiq bog'lanish — provayderni "
        "almashtirish uni qayta yozishni talab qiladi.",
        "Funksiya kodi ilova kodidan tashqarida yashaydi, shuning "
        "uchun versiyalash va code review'dan o'tkazish qiyinroq.",
        "Testda funksiya mavjud bo'lishi kerak — ya'ni in-memory "
        "provayder ishlamaydi, haqiqiy baza kerak.",
        "Funksiya ichidagi xato diagnostikasi EF log'ida "
        "ko'rinmaydi.",
    ])

    para(d, "Shuning uchun birinchi navbatda oddiyroq variantlarni "
            "ko'rib chiqaman: LINQ bilan yozish mumkin bo'lsa — "
            "LINQ; faqat o'qish uchun agregatsiya kerak bo'lsa — "
            "**view** yoki **materialized view**; parametrsiz "
            "bo'lsa — view deyarli har doim yetarli. TVF esa "
            "parametr kerak bo'lganda va LINQ yetarli bo'lmaganda "
            "to'g'ri tanlov.")

    sources(d, [
        ("User-defined function mapping — EF Core",
         "https://learn.microsoft.com/en-us/ef/core/querying/user-defined-function-mapping"),
        ("Keyless entity types",
         "https://learn.microsoft.com/en-us/ef/core/modeling/keyless-entity-types"),
        ("CREATE FUNCTION — PostgreSQL",
         "https://www.postgresql.org/docs/current/sql-createfunction.html"),
        ("Function volatility categories",
         "https://www.postgresql.org/docs/current/xfunc-volatility.html"),
    ])
