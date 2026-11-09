# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "SQL injection attacks and Defence"
CATEGORY = "Cybersecurity"
TITLE = "SQL Injection va Undan Himoya"
SUBTITLE = "Hujum qanday ishlaydi va uni qanday to'liq yopish mumkin"
FILENAME = "SQL injection attacks and Defence.docx"


def build(d):
    h1(d, "1. Hujumning mohiyati")

    para(d, "SQL injection — foydalanuvchi kiritgan matnni SQL so'rovining bir qismi "
            "sifatida bajarishga majburlash. Muammoning ildizi oddiy: so'rov matn "
            "sifatida yig'ilsa, baza qayerda buyruq, qayerda ma'lumot ekanini ajrata "
            "olmaydi.")

    code(d, """// Zaif kod
var sql = $"SELECT * FROM Users WHERE Email = '{email}'";
var users = await connection.QueryAsync<User>(sql);""")

    para(d, "Agar `email` qiymati oddiy matn bo'lsa, hammasi joyida. Lekin "
            "foydalanuvchi quyidagini kiritsa:")

    code(d, """' OR '1'='1""")

    para(d, "Natijada bajariladigan so'rov butunlay boshqacha bo'ladi:")

    code(d, """SELECT * FROM Users WHERE Email = '' OR '1'='1'""")

    para(d, "Shart har doim rost bo'lgani uchun barcha foydalanuvchilar qaytadi.")

    note(d, "Bu hujum nega hamon dolzarb:",
         "SQL injection birinchi marta 1998-yilda tasvirlangan, lekin u hali ham "
         "OWASP ro'yxatining yuqori qismida. Sababi — himoya texnikasi yetarli "
         "emasligida emas, balki uni bitta joyda qo'llashni unutish yetarliligida. "
         "Yuzta so'rovning to'qson to'qqiztasi to'g'ri yozilgan bo'lsa ham, bittasi "
         "butun bazani ochib beradi.")

    # ───────────────────────────────────────────
    h1(d, "2. Hujum turlari")

    h2(d, "2.1 Klassik — ma'lumot chiqarish")

    code(d, """' UNION SELECT Email, PasswordHash, NULL, NULL FROM Users --""")

    para(d, "`UNION` orqali tajovuzkor o'ziga kerakli jadvaldan ma'lumot qo'shib "
            "oladi. `--` esa so'rovning qolgan qismini izohga aylantiradi.")

    h2(d, "2.2 Ko'r (blind) injection")

    para(d, "Agar natija ko'rinmasa ham, javobning farqiga qarab ma'lumot ajratib "
            "olish mumkin:")

    code(d, """' AND SUBSTRING((SELECT PasswordHash FROM Users WHERE Id=1), 1, 1) = 'a' --""")

    para(d, "Sahifa boshqacha javob bersa — taxmin to'g'ri. Shu tarzda parol hash i "
            "belgi-belgi tiklanadi.")

    h2(d, "2.3 Vaqtga asoslangan")

    code(d, """'; SELECT CASE WHEN (1=1) THEN pg_sleep(5) ELSE pg_sleep(0) END --""")

    para(d, "Javob mazmuni umuman o'zgarmasa ham, javob vaqti axborot manbai "
            "bo'ladi.")

    h2(d, "2.4 Buzuvchi")

    code(d, """'; DROP TABLE Users; --
'; UPDATE Users SET Role = 'Admin' WHERE Email = 'hacker@example.com'; --""")

    # ───────────────────────────────────────────
    h1(d, "3. Asosiy himoya — parametrlangan so'rovlar")

    para(d, "Yagona ishonchli yechim — qiymatni so'rov matnidan ajratish. "
            "Parametrlangan so'rovda baza avval so'rov tuzilmasini tahlil qiladi, "
            "keyin qiymatni qo'yadi — demak qiymat hech qachon buyruqqa aylana "
            "olmaydi.")

    code(d, """// ADO.NET
await using var cmd = new NpgsqlCommand(
    "SELECT * FROM users WHERE email = @email", connection);

cmd.Parameters.AddWithValue("email", email);""")

    code(d, """// Dapper — parametrlar avtomatik
var users = await connection.QueryAsync<User>(
    "SELECT * FROM users WHERE email = @Email",
    new { Email = email });""")

    note(d, "Parametr — bu qochirish (escaping) emas:",
         "Ko'pchilik parametrlangan so'rov maxsus belgilarni qochiradi deb "
         "o'ylaydi. Aslida mexanizm boshqacha — so'rov va ma'lumot bazaga "
         "**alohida** yuboriladi. Baza so'rov rejasini ma'lumotni ko'rmasdan "
         "turib quradi. Shuning uchun qiymatda nima bo'lishidan qat'i nazar, u "
         "faqat qiymat bo'lib qoladi.")

    # ───────────────────────────────────────────
    h1(d, "4. EF Core da")

    para(d, "LINQ so'rovlari har doim parametrlangan SQL hosil qiladi — bu yerda "
            "injection mumkin emas:")

    code(d, """var users = await db.Users
    .Where(u => u.Email == email)
    .ToListAsync(ct);

// SELECT ... FROM users WHERE email = @__email_0""")

    h2(d, "4.1 Xom SQL bilan ishlashda")

    code(d, """// Xavfsiz — FormattableString avtomatik parametrlashtiriladi
var users = await db.Users
    .FromSql($"SELECT * FROM users WHERE email = {email}")
    .ToListAsync(ct);""")

    code(d, """// Xavfli — satr birlashtirilgan
var sql = "SELECT * FROM users WHERE email = '" + email + "'";
var users = await db.Users.FromSqlRaw(sql).ToListAsync(ct);""")

    code(d, """// FromSqlRaw ishlatilsa, parametr aniq berilishi kerak
var users = await db.Users
    .FromSqlRaw("SELECT * FROM users WHERE email = {0}", email)
    .ToListAsync(ct);""")

    note(d, "`FromSql` va `FromSqlRaw` farqini eslab qolish oson:",
         "`FromSql` interpolyatsiyalangan satrni `FormattableString` sifatida "
         "qabul qiladi va uni o'zi parametrga aylantiradi. `FromSqlRaw` esa oddiy "
         "`string` oladi va hech narsa qilmaydi. Nomdagi \"Raw\" aynan shuni "
         "ogohlantiradi — bu yerda men o'zim javobgarman.")

    note(d, "Bitta jiddiy tuzoq bor:",
         "`FromSqlRaw($\"...{email}...\")` deb yozsam, kompilyator xatolik "
         "bermaydi — interpolyatsiya oddiy `string` ga aylanadi va parametr "
         "yo'qoladi. Ya'ni kod xavfsiz ko'rinadi, lekin emas. Shuning uchun "
         "loyihada `FromSqlRaw` ni qidirib chiqish — xavfsizlik tekshiruvining "
         "birinchi qadami.")

    # ───────────────────────────────────────────
    h1(d, "5. Parametr yordam bermaydigan joylar")

    para(d, "Parametr faqat **qiymat** o'rnida ishlaydi. Jadval nomi, ustun nomi "
            "yoki saralash yo'nalishi parametr bo'la olmaydi:")

    code(d, """// Ishlamaydi
"SELECT * FROM users ORDER BY @column"    // @column parametr bo'la olmaydi""")

    para(d, "Bunday holatlarda yagona yechim — oq ro'yxat:")

    code(d, """private static readonly Dictionary<string, string> SortColumns = new()
{
    ["name"] = "full_name",
    ["email"] = "email",
    ["created"] = "created_at"
};

public async Task<List<User>> SearchAsync(
    string sortBy, bool descending, CancellationToken ct)
{
    if (!SortColumns.TryGetValue(sortBy, out var column))
        throw new ArgumentException("Noma'lum saralash maydoni", nameof(sortBy));

    var direction = descending ? "DESC" : "ASC";
    var sql = $"SELECT * FROM users ORDER BY {column} {direction}";

    return await _db.Users.FromSqlRaw(sql).ToListAsync(ct);
}""")

    para(d, "Bu yerda satr birlashtirish ishlatilgan, lekin u xavfsiz — chunki "
            "`column` qiymati foydalanuvchidan emas, oldindan belgilangan "
            "lug'atdan olinadi.")

    # ───────────────────────────────────────────
    h1(d, "6. Qo'shimcha himoya qatlamlari")

    para(d, "Parametrlangan so'rov asosiy himoya, lekin yagonasi bo'lmasligi "
            "kerak. Chuqurlashtirilgan himoya quyidagi qatlamlarni qo'shadi:")

    h2(d, "6.1 Eng kam huquq tamoyili")

    code(d, """-- Ilova uchun alohida foydalanuvchi
CREATE USER app_user WITH PASSWORD '...';

GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_user;

-- Lekin sxemani o'zgartirishga ruxsat yo'q
REVOKE CREATE ON SCHEMA public FROM app_user;""")

    note(d, "Bu qatlam zararni cheklaydi:",
         "Agar injection baribir yuzaga kelsa, `DROP TABLE` bajarilmaydi — "
         "chunki ilova foydalanuvchisida bunday huquq yo'q. Migratsiyalar esa "
         "alohida, yuqori huquqli foydalanuvchi bilan bajariladi. Men buni "
         "himoya emas, zararni kamaytirish chorasi deb qarayman.")

    h2(d, "6.2 Kiruvchi ma'lumotni tekshirish")

    code(d, """public class SearchRequest
{
    [Required]
    [MaxLength(100)]
    [RegularExpression(@"^[\\p{L}\\p{N}\\s'\\-]+$")]
    public string Query { get; set; } = string.Empty;

    [Range(1, 100)]
    public int Size { get; set; } = 20;
}""")

    para(d, "Validatsiya SQL injection ni to'xtatmaydi, lekin u hujum "
            "maydonini kichraytiradi va boshqa muammolarni ham oldini oladi.")

    h2(d, "6.3 Xatolik xabarlarini yashirish")

    para(d, "Baza xatolik matnini foydalanuvchiga ko'rsatish jadval va ustun "
            "nomlarini ochib beradi — bu tajovuzkorga so'rovni to'g'rilashda "
            "yordam beradi.")

    code(d, """// Production da
app.UseExceptionHandler();      // umumiy xabar
// Development da esa batafsil ma'lumot ko'rinadi""")

    h2(d, "6.4 Kuzatuv")

    bullets(d, [
        "Noodatiy uzun so'rov parametrlarini logga yozish.",
        "Bir xil IP dan ketma-ket xatolik beradigan so'rovlarni kuzatish.",
        "`pg_stat_statements` orqali kutilmagan so'rov shakllarini aniqlash.",
    ])

    # ───────────────────────────────────────────
    h1(d, "7. Tekshirish ro'yxati")

    bullets(d, [
        "Loyihada `FromSqlRaw`, `ExecuteSqlRaw` va `new SqlCommand(...)` "
        "ishlatilgan barcha joylarni ko'rib chiqish.",
        "Satr birlashtirish yoki interpolyatsiya bilan qurilgan SQL yo'qligini "
        "tekshirish.",
        "Saralash va filtr maydonlari oq ro'yxatdan olinayotganini tasdiqlash.",
        "Ilova baza foydalanuvchisining huquqlarini ko'rib chiqish.",
        "Saqlangan protseduralar ichida ham dinamik SQL yo'qligini tekshirish.",
    ])

    code(d, """-- Saqlangan protsedurada ham xavf bor
CREATE FUNCTION search_users(term text) RETURNS SETOF users AS $$
BEGIN
    -- Xavfli
    RETURN QUERY EXECUTE 'SELECT * FROM users WHERE name LIKE ''%' || term || '%''';

    -- Xavfsiz
    RETURN QUERY EXECUTE 'SELECT * FROM users WHERE name LIKE $1'
        USING '%' || term || '%';
END;
$$ LANGUAGE plpgsql;""")

    # ───────────────────────────────────────────
    h1(d, "8. Xulosa")

    bullets(d, [
        "SQL injection — foydalanuvchi matnini so'rov buyrug'iga aylantirish.",
        "Parametrlangan so'rov so'rov va ma'lumotni alohida yuboradi — bu "
        "qochirish emas, tuzilma darajasidagi ajratish.",
        "EF Core dagi LINQ so'rovlari avtomatik parametrlanadi.",
        "`FromSql` xavfsiz, `FromSqlRaw` esa javobgarlikni dasturchiga "
        "yuklaydi.",
        "Interpolyatsiyalangan satrni `FromSqlRaw` ga berish — jimgina "
        "xavfsizlik nuqsoni.",
        "Jadval va ustun nomlari parametr bo'la olmaydi — oq ro'yxat kerak.",
        "Ilova baza foydalanuvchisiga eng kam huquq berish zararni cheklaydi.",
        "Xatolik tafsilotlarini production da yashirish lozim.",
    ])

    sources(d, [
        ("OWASP SQL Injection Prevention Cheat Sheet",
         "https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html"),
        ("OWASP Top 10 — A03:2021 Injection",
         "https://owasp.org/Top10/A03_2021-Injection/"),
        ("Raw SQL Queries — EF Core",
         "https://learn.microsoft.com/en-us/ef/core/querying/sql-queries"),
    ])
