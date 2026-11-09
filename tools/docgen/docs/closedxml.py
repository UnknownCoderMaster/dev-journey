# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "ClosedXML"
CATEGORY = ".NET / C#"
TITLE = "ClosedXML"
SUBTITLE = "Excel fayllari bilan qulay ishlash"
FILENAME = "ClosedXML.docx"


def build(d):
    h1(d, "1. Nima uchun ClosedXML")

    para(d, "ClosedXML — Open XML SDK ustiga qurilgan qulay qobiq. U "
            "bir xil natijani ancha qisqa kod bilan olish imkonini "
            "beradi.")

    code(d, """dotnet add package ClosedXML""")

    code(d, """// Open XML SDK — taxminan 30 qator
// ClosedXML — 5 qator
using var workbook = new XLWorkbook();
var sheet = workbook.Worksheets.Add("Hisobot");

sheet.Cell("A1").Value = "Salom";
workbook.SaveAs("report.xlsx");""")

    note(d, "Taqqoslash adolatli bo'lishi uchun:",
         "ClosedXML qulay, lekin u Open XML SDK ning hamma "
         "imkoniyatini bermaydi. Formatning nozik tomonlari kerak "
         "bo'lsa, baribir quyi darajaga tushishga to'g'ri keladi. "
         "Lekin odatiy hisobot uchun u butunlay yetarli.")

    # ───────────────────────────────────────────
    h1(d, "2. Asosiy amallar")

    h2(d, "2.1 Kataklar bilan ishlash")

    code(d, """using var workbook = new XLWorkbook();
var sheet = workbook.Worksheets.Add("Buyurtmalar");

// Turli usullar
sheet.Cell("A1").Value = "Id";
sheet.Cell(1, 2).Value = "Mijoz";
sheet.Cell("C1").Value = "Summa";

// Tiplar avtomatik aniqlanadi
sheet.Cell("A2").Value = 42;
sheet.Cell("B2").Value = "Ali Valiyev";
sheet.Cell("C2").Value = 150_000m;
sheet.Cell("D2").Value = DateTime.Now;
sheet.Cell("E2").Value = true;""")

    h2(d, "2.2 Kolleksiyadan jadval")

    code(d, """var orders = await _db.Orders
    .Select(o => new
    {
        o.Id,
        Customer = o.Customer.FullName,
        o.Total,
        o.CreatedAt
    })
    .ToListAsync(ct);

// Bitta chaqiruv bilan butun jadval
var table = sheet.Cell("A1").InsertTable(orders, "Orders", createTable: true);""")

    note(d, "`InsertTable` menga ko'p vaqt tejagan:",
         "U sarlavha qatorini xossa nomlaridan oladi, ma'lumotni "
         "to'ldiradi va Excel jadvali sifatida formatlaydi — "
         "filtrlar va chiziqli bo'yash bilan. Qo'lda yozilganda bu "
         "o'nlab qator bo'lardi.")

    h2(d, "2.3 Diapazon bilan ishlash")

    code(d, """var range = sheet.Range("A1:D1");
range.Style.Font.Bold = true;
range.Style.Fill.BackgroundColor = XLColor.LightGray;

// Ishlatilgan diapazon
var used = sheet.RangeUsed();
Console.WriteLine($"{used.RowCount()} qator, {used.ColumnCount()} ustun");""")

    # ───────────────────────────────────────────
    h1(d, "3. Formatlash")

    code(d, """var header = sheet.Range("A1:D1");

header.Style.Font.Bold = true;
header.Style.Font.FontColor = XLColor.White;
header.Style.Font.FontSize = 11;
header.Style.Fill.BackgroundColor = XLColor.FromHtml("#1F4E79");
header.Style.Alignment.Horizontal = XLAlignmentHorizontalValues.Center;
header.Style.Alignment.Vertical = XLAlignmentVerticalValues.Center;

header.Style.Border.OutsideBorder = XLBorderStyleValues.Thin;
header.Style.Border.InsideBorder = XLBorderStyleValues.Thin;""")

    h2(d, "3.1 Raqam formatlari")

    code(d, """sheet.Column("C").Style.NumberFormat.Format = "#,##0.00";
sheet.Column("D").Style.NumberFormat.Format = "dd.MM.yyyy";
sheet.Column("E").Style.NumberFormat.Format = "0.00%";

// Pul birligi bilan
sheet.Column("C").Style.NumberFormat.Format = "#,##0 \\"so'm\\"";""")

    h2(d, "3.2 Ustun kengligi va qotirish")

    code(d, """// Avtomatik kenglik
sheet.Columns().AdjustToContents();

// Qo'lda
sheet.Column("B").Width = 30;

// Sarlavhani qotirish — aylantirganda ko'rinib turadi
sheet.SheetView.FreezeRows(1);
sheet.SheetView.Freeze(1, 2);     // 1 qator va 2 ustun

// Avtomatik filtr
sheet.Range("A1:D1").SetAutoFilter();""")

    note(d, "`AdjustToContents` ni katta jadvalda ehtiyotkorlik bilan:",
         "U har bir katakning kengligini hisoblaydi va o'n minglab "
         "qatorda bu sezilarli vaqt oladi. Katta hisobotlarda men "
         "ustun kengligini qo'lda belgilayman yoki faqat birinchi "
         "yuzta qatorni hisobga olaman.")

    code(d, """// Faqat sarlavha va bir nechta qator bo'yicha
sheet.Range("A1:D100").Columns().AdjustToContents();""")

    # ───────────────────────────────────────────
    h1(d, "4. Formulalar")

    code(d, """sheet.Cell("D2").FormulaA1 = "=B2*C2";
sheet.Cell("D10").FormulaA1 = "=SUM(D2:D9)";
sheet.Cell("E2").FormulaA1 = "=IF(D2>100000,\\"Katta\\",\\"Kichik\\")";

// Hisoblangan qiymatni o'qish
var value = sheet.Cell("D10").Value;""")

    note(d, "Formula natijasini ClosedXML hisoblamaydi:",
         "U formulani faylga yozadi, hisoblashni esa Excel ochilganda "
         "bajaradi. Agar menga natija kod ichida kerak bo'lsa, uni "
         "o'zim hisoblashim kerak. Bu birinchi marta chalkashtiradi — "
         "katak bo'sh ko'rinadi, lekin Excel da ochilsa qiymat "
         "paydo bo'ladi.")

    # ───────────────────────────────────────────
    h1(d, "5. Shartli formatlash")

    code(d, """var dataRange = sheet.Range("C2:C100");

// Qiymatga qarab rang
dataRange.AddConditionalFormat()
    .WhenGreaterThan(1_000_000)
    .Fill.SetBackgroundColor(XLColor.LightGreen);

dataRange.AddConditionalFormat()
    .WhenLessThan(0)
    .Font.SetFontColor(XLColor.Red);

// Ma'lumot chizig'i
dataRange.AddConditionalFormat()
    .DataBar(XLColor.CornflowerBlue)
    .LowestValue()
    .HighestValue();""")

    # ───────────────────────────────────────────
    h1(d, "6. O'qish")

    code(d, """using var workbook = new XLWorkbook(path);
var sheet = workbook.Worksheet(1);

// Qatorlar bo'ylab
foreach (var row in sheet.RowsUsed().Skip(1))    // sarlavhani o'tkazib
{
    var id = row.Cell(1).GetValue<int>();
    var customer = row.Cell(2).GetString();
    var total = row.Cell(3).GetValue<decimal>();
    var date = row.Cell(4).GetDateTime();

    Console.WriteLine($"{id} | {customer} | {total:N2} | {date:d}");
}""")

    code(d, """// Xavfsiz o'qish — noto'g'ri tip bo'lsa ham to'xtamaydi
if (row.Cell(3).TryGetValue<decimal>(out var amount))
{
    // qiymat to'g'ri
}
else
{
    _logger.LogWarning("{Row}-qatorda noto'g'ri summa", row.RowNumber());
}""")

    note(d, "`TryGetValue` ni foydalanuvchi yuklagan fayllarda doim "
            "ishlataman:",
         "Excel da katakka istalgan narsa yozilgan bo'lishi mumkin — "
         "bo'sh, matn, xato qiymati. `GetValue<decimal>()` bunday "
         "holatda istisno otadi va butun import to'xtaydi. "
         "`TryGetValue` esa muammoli qatorni o'tkazib yuborish va "
         "oxirida hisobot berish imkonini beradi.")

    h2(d, "6.1 Import uchun tipik naqsh")

    code(d, """public async Task<ImportResult> ImportAsync(
    Stream stream, CancellationToken ct)
{
    using var workbook = new XLWorkbook(stream);
    var sheet = workbook.Worksheet(1);

    var items = new List<ProductDto>();
    var errors = new List<string>();

    foreach (var row in sheet.RowsUsed().Skip(1))
    {
        var rowNumber = row.RowNumber();

        var name = row.Cell(1).GetString().Trim();
        if (string.IsNullOrWhiteSpace(name))
        {
            errors.Add($"{rowNumber}-qator: nomi bo'sh");
            continue;
        }

        if (!row.Cell(2).TryGetValue<decimal>(out var price) || price < 0)
        {
            errors.Add($"{rowNumber}-qator: narx noto'g'ri");
            continue;
        }

        items.Add(new ProductDto(name, price));
    }

    return new ImportResult(items, errors);
}""")

    note(d, "Import natijasini shunday qaytarish foydali:",
         "Foydalanuvchi 500 qatorli fayl yuklaydi va 3 tasida xato "
         "bor. Agar men birinchi xatoda to'xtasam, u uch marta "
         "fayl yuklashga majbur bo'ladi. Barcha xatolarni bir yo'la "
         "ko'rsatsam, u hammasini bir martada tuzatadi.")

    # ───────────────────────────────────────────
    h1(d, "7. Web API dan qaytarish")

    code(d, """[HttpGet("export")]
public async Task<IActionResult> Export(CancellationToken ct)
{
    var orders = await _service.GetOrdersAsync(ct);

    using var workbook = new XLWorkbook();
    var sheet = workbook.Worksheets.Add("Buyurtmalar");

    sheet.Cell("A1").InsertTable(orders, "Orders", true);
    sheet.Columns().AdjustToContents();
    sheet.SheetView.FreezeRows(1);

    using var stream = new MemoryStream();
    workbook.SaveAs(stream);
    stream.Position = 0;

    return File(stream.ToArray(),
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        $"orders-{DateTime.Now:yyyyMMdd-HHmm}.xlsx");
}""")

    # ───────────────────────────────────────────
    h1(d, "8. Katta hajmli ma'lumot")

    note(d, "ClosedXML butun hujjatni xotirada saqlaydi:",
         "Yuz minglab qatorli fayl yaratganimda xotira sarfi juda "
         "oshdi va ba'zan `OutOfMemoryException` chiqdi. Bu "
         "kutubxonaning tabiati — u qulaylik uchun hamma narsani "
         "obyekt sifatida saqlaydi.")

    bullets(d, [
        "Katta eksportni bo'laklarga bo'lish yoki bir nechta varaqqa "
        "tarqatish.",
        "CSV formatini qarash — u oqim sifatida yoziladi va xotira "
        "talab qilmaydi.",
        "Juda katta hajm uchun `SpreadsheetLight` yoki Open XML SDK "
        "ning `OpenXmlWriter` sinfini ishlatish.",
    ])

    code(d, """// CSV — oqim orqali, xotirasiz
await using var writer = new StreamWriter(stream);
await writer.WriteLineAsync("Id,Customer,Total");

await foreach (var order in _db.Orders.AsAsyncEnumerable().WithCancellation(ct))
{
    await writer.WriteLineAsync(
        $"{order.Id},\\"{order.CustomerName}\\",{order.Total}");
}""")

    # ───────────────────────────────────────────
    h1(d, "9. Xulosa")

    bullets(d, [
        "ClosedXML — Open XML SDK ustidagi qulay qobiq; kod bir necha "
        "barobar qisqaradi.",
        "`InsertTable` kolleksiyadan formatlangan jadval yaratadi.",
        "Uslublar diapazonga bir yo'la qo'llaniladi.",
        "`AdjustToContents` katta jadvalda sekin ishlaydi.",
        "Formula natijasi faylda hisoblanmaydi — uni Excel ochganda "
        "hisoblaydi.",
        "Foydalanuvchi fayllarini o'qishda `TryGetValue` ishlatish "
        "kerak.",
        "Import xatolarini to'plab, bir yo'la ko'rsatish qulayroq.",
        "Kutubxona butun hujjatni xotirada saqlaydi — juda katta "
        "hajm uchun CSV yoki quyi darajali API afzal.",
    ])

    sources(d, [
        ("ClosedXML — GitHub",
         "https://github.com/ClosedXML/ClosedXML"),
        ("ClosedXML Wiki",
         "https://github.com/ClosedXML/ClosedXML/wiki"),
        ("Open XML SDK for Office",
         "https://learn.microsoft.com/en-us/office/open-xml/open-xml-sdk"),
    ])
