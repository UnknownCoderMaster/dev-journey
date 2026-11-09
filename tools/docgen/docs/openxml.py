# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "Open XML SDK for Office"
CATEGORY = ".NET / C#"
TITLE = "Open XML SDK"
SUBTITLE = "Office hujjatlarini Office o'rnatmasdan yaratish"
FILENAME = "Open XML SDK for Office.docx"


def build(d):
    h1(d, "1. Office fayl formati")

    para(d, "Zamonaviy Office fayllari — `.docx`, `.xlsx`, `.pptx` — "
            "aslida ZIP arxivlardir. Ular ichida XML fayllar, rasmlar "
            "va ular orasidagi bog'lanishlar saqlanadi.")

    code(d, """document.docx
├── [Content_Types].xml
├── _rels/
│   └── .rels
├── word/
│   ├── document.xml        ← asosiy matn
│   ├── styles.xml          ← uslublar
│   ├── numbering.xml       ← ro'yxatlar
│   ├── media/              ← rasmlar
│   └── _rels/
│       └── document.xml.rels
└── docProps/
    ├── core.xml
    └── app.xml""")

    note(d, "Buni bilish amaliy foyda beradi:",
         "Hujjat bilan bog'liq muammo chiqqanda men uni `.zip` ga "
         "qayta nomlab, ochib ko'raman. Ichidagi `document.xml` ni "
         "o'qib, nima noto'g'ri ekanini aniqlash mumkin. Bu ba'zan "
         "kodda soatlab izlashdan tezroq javob beradi.")

    # ───────────────────────────────────────────
    h1(d, "2. Open XML SDK")

    code(d, """dotnet add package DocumentFormat.OpenXml""")

    para(d, "Bu kutubxona Office fayllarini to'g'ridan-to'g'ri, "
            "Microsoft Office o'rnatilmagan holda yaratish va o'qish "
            "imkonini beradi. Shuning uchun u serverda ishlaydi.")

    note(d, "Serverda Office avtomatlashtirish ishlatilmaydi:",
         "COM orqali Word yoki Excel ni boshqarish texnik jihatdan "
         "mumkin, lekin Microsoft buni server muhitida aniq "
         "qo'llab-quvvatlamaydi. U barqaror ishlamaydi, jarayonlar "
         "osilib qoladi va litsenziya talab qiladi. Open XML SDK bu "
         "muammolarning hech birini keltirib chiqarmaydi.")

    # ───────────────────────────────────────────
    h1(d, "3. Word hujjati yaratish")

    code(d, """using DocumentFormat.OpenXml;
using DocumentFormat.OpenXml.Packaging;
using DocumentFormat.OpenXml.Wordprocessing;

using var document = WordprocessingDocument.Create(
    path, WordprocessingDocumentType.Document);

var mainPart = document.AddMainDocumentPart();
mainPart.Document = new Document(new Body());

var body = mainPart.Document.Body!;

// Sarlavha
var heading = new Paragraph(
    new ParagraphProperties(
        new ParagraphStyleId { Val = "Heading1" }),
    new Run(new Text("Hisobot")));

body.AppendChild(heading);

// Oddiy matn
body.AppendChild(new Paragraph(
    new Run(new Text("Bu hisobot avtomatik yaratilgan."))));

mainPart.Document.Save();""")

    h2(d, "3.1 Formatlash")

    code(d, """var run = new Run(new Text("Muhim matn"));

run.RunProperties = new RunProperties(
    new Bold(),
    new Color { Val = "1F4E79" },
    new FontSize { Val = "28" },        // yarim punktlarda — 14pt
    new RunFonts { Ascii = "Segoe UI" });

body.AppendChild(new Paragraph(run));""")

    note(d, "`FontSize` qiymati yarim punktlarda beriladi:",
         "Ya'ni 14pt shrift uchun `28` yoziladi. Bu Open XML "
         "formatining o'ziga xosligi va birinchi marta juda "
         "chalkashtiradi. Xuddi shunday, masofalar twip larda — "
         "bir dyuymning 1440 dan bir qismi.")

    h2(d, "3.2 Jadval")

    code(d, """var table = new Table();

table.AppendChild(new TableProperties(
    new TableBorders(
        new TopBorder { Val = BorderValues.Single, Size = 6 },
        new BottomBorder { Val = BorderValues.Single, Size = 6 },
        new LeftBorder { Val = BorderValues.Single, Size = 6 },
        new RightBorder { Val = BorderValues.Single, Size = 6 },
        new InsideHorizontalBorder { Val = BorderValues.Single, Size = 6 },
        new InsideVerticalBorder { Val = BorderValues.Single, Size = 6 })));

foreach (var order in orders)
{
    var row = new TableRow();

    row.Append(
        CreateCell(order.Id.ToString()),
        CreateCell(order.CustomerName),
        CreateCell(order.Total.ToString("N2")));

    table.AppendChild(row);
}

body.AppendChild(table);

static TableCell CreateCell(string text) =>
    new(new Paragraph(new Run(new Text(text))));""")

    # ───────────────────────────────────────────
    h1(d, "4. Excel fayli yaratish")

    code(d, """using DocumentFormat.OpenXml.Spreadsheet;

using var document = SpreadsheetDocument.Create(
    path, SpreadsheetDocumentType.Workbook);

var workbookPart = document.AddWorkbookPart();
workbookPart.Workbook = new Workbook();

var worksheetPart = workbookPart.AddNewPart<WorksheetPart>();
var sheetData = new SheetData();
worksheetPart.Worksheet = new Worksheet(sheetData);

var sheets = workbookPart.Workbook.AppendChild(new Sheets());
sheets.Append(new Sheet
{
    Id = workbookPart.GetIdOfPart(worksheetPart),
    SheetId = 1,
    Name = "Hisobot"
});

// Sarlavha qatori
var header = new Row();
header.Append(
    CreateTextCell("Id"),
    CreateTextCell("Mijoz"),
    CreateTextCell("Summa"));
sheetData.AppendChild(header);

// Ma'lumot
foreach (var order in orders)
{
    var row = new Row();
    row.Append(
        CreateNumberCell(order.Id),
        CreateTextCell(order.CustomerName),
        CreateNumberCell(order.Total));
    sheetData.AppendChild(row);
}

workbookPart.Workbook.Save();""")

    code(d, """static Cell CreateTextCell(string text) => new()
{
    DataType = CellValues.InlineString,
    InlineString = new InlineString(new Text(text))
};

static Cell CreateNumberCell(decimal value) => new()
{
    DataType = CellValues.Number,
    CellValue = new CellValue(value)
};""")

    note(d, "Bu kodning hajmiga e'tibor bering:",
         "Oddiy jadval yaratish uchun o'ttizga yaqin qator kerak "
         "bo'ldi. Open XML SDK formatning to'liq nazoratini beradi, "
         "lekin juda batafsil. Agar menga faqat Excel kerak bo'lsa, "
         "`ClosedXML` ancha qisqa kod yozish imkonini beradi.")

    # ───────────────────────────────────────────
    h1(d, "5. Shablon asosida ishlash")

    para(d, "Hujjatni noldan yaratishdan ko'ra, tayyor shablonni to'ldirish "
            "ancha amaliy. Dizayner Word da chiroyli shablon tayyorlaydi, "
            "men esa faqat qiymatlarni almashtiraman.")

    code(d, """// Shablon nusxasini olish
File.Copy(templatePath, outputPath, overwrite: true);

using var document = WordprocessingDocument.Open(outputPath, isEditable: true);
var body = document.MainDocumentPart!.Document.Body!;

var replacements = new Dictionary<string, string>
{
    ["{{CustomerName}}"] = order.CustomerName,
    ["{{OrderNumber}}"] = order.Number,
    ["{{Total}}"] = order.Total.ToString("N2"),
    ["{{Date}}"] = DateTime.Now.ToString("dd.MM.yyyy")
};

foreach (var text in body.Descendants<Text>())
{
    foreach (var (placeholder, value) in replacements)
    {
        if (text.Text.Contains(placeholder))
            text.Text = text.Text.Replace(placeholder, value);
    }
}

document.MainDocumentPart.Document.Save();""")

    note(d, "Bu yerda nozik muammo bor:",
         "Word matnni ichkarida bir nechta `Run` ga bo'lib tashlashi "
         "mumkin — masalan avtomatik imlo tekshiruvi tufayli. "
         "`{{CustomerName}}` to'rtta qismga bo'linib ketsa, mening "
         "almashtirishim ishlamaydi. Shuning uchun shablon yozganda "
         "o'rin egallovchini bir marta, to'xtamasdan yozish kerak.")

    note(d, "Amaliy maslahat:",
         "Shablonni tayyorlaganimdan keyin uni `.zip` sifatida ochib, "
         "`document.xml` dan o'rin egallovchilarni qidiraman. Agar "
         "ular bo'lingan bo'lsa, Word da o'sha joyni o'chirib, "
         "qaytadan yozaman. Bu bir necha daqiqa oladi, lekin keyin "
         "kod ishonchli ishlaydi.")

    # ───────────────────────────────────────────
    h1(d, "6. Hujjatni o'qish")

    code(d, """using var document = WordprocessingDocument.Open(path, isEditable: false);

var body = document.MainDocumentPart!.Document.Body!;

// Butun matn
var text = body.InnerText;

// Paragraflar bo'yicha
foreach (var paragraph in body.Descendants<Paragraph>())
{
    var style = paragraph.ParagraphProperties?.ParagraphStyleId?.Val;
    Console.WriteLine($"[{style}] {paragraph.InnerText}");
}

// Jadvallar
foreach (var table in body.Descendants<Table>())
{
    foreach (var row in table.Descendants<TableRow>())
    {
        var cells = row.Descendants<TableCell>()
            .Select(c => c.InnerText);

        Console.WriteLine(string.Join(" | ", cells));
    }
}""")

    # ───────────────────────────────────────────
    h1(d, "7. Oqim bilan ishlash")

    code(d, """// Faylga yozmasdan, to'g'ridan-to'g'ri javobga
[HttpGet("report")]
public async Task<IActionResult> GetReport(CancellationToken ct)
{
    var stream = new MemoryStream();

    using (var document = WordprocessingDocument.Create(
        stream, WordprocessingDocumentType.Document, autoSave: true))
    {
        BuildDocument(document, await GetDataAsync(ct));
    }

    stream.Position = 0;

    return File(stream,
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        $"report-{DateTime.Now:yyyyMMdd}.docx");
}""")

    note(d, "`using` blokini yopish muhim:",
         "Hujjat `Dispose` qilinmaguncha ZIP arxivi yakunlanmaydi va "
         "oqimdagi ma'lumot to'liq bo'lmaydi. Shuning uchun "
         "`stream.Position = 0` ni blokdan **keyin** yozish kerak.")

    # ───────────────────────────────────────────
    h1(d, "8. Muqobillar")

    table(d, ["Kutubxona", "Nima uchun", "Litsenziya"],
          [["Open XML SDK", "To'liq nazorat, Word va Excel", "MIT"],
           ["ClosedXML", "Faqat Excel, qulay API", "MIT"],
           ["DocX", "Faqat Word, qulay API", "MIT"],
           ["EPPlus", "Excel, keng imkoniyat", "Tijorat (5.x+)"]],
          widths=[3.6, 7.4, 4.5])

    note(d, "Tanlash mezonim:",
         "Agar menga faqat Excel kerak bo'lsa — `ClosedXML`, chunki "
         "kod bir necha barobar qisqa bo'ladi. Agar Word shablonini "
         "to'ldirish kerak bo'lsa yoki formatning nozik tomonlarini "
         "boshqarish zarur bo'lsa — Open XML SDK. EPPlus ni esa "
         "litsenziya sababli yangi loyihalarda ishlatmayman.")

    # ───────────────────────────────────────────
    h1(d, "9. Xulosa")

    bullets(d, [
        "Office fayllari — ichida XML saqlanadigan ZIP arxivlar.",
        "Open XML SDK Office o'rnatilmagan serverda ham ishlaydi.",
        "Serverda COM orqali Office avtomatlashtirish "
        "qo'llab-quvvatlanmaydi.",
        "`FontSize` yarim punktlarda, masofalar twip larda beriladi.",
        "Shablonni to'ldirish noldan yaratishdan amaliyroq.",
        "Word o'rin egallovchini bir nechta `Run` ga bo'lib "
        "yuborishi mumkin.",
        "Oqim bilan ishlashda hujjatni `Dispose` qilgandan keyin "
        "o'qish kerak.",
        "Faqat Excel kerak bo'lsa, `ClosedXML` ancha qisqa kod "
        "beradi.",
    ])

    sources(d, [
        ("Open XML SDK for Office — Microsoft Learn",
         "https://learn.microsoft.com/en-us/office/open-xml/open-xml-sdk"),
        ("DocumentFormat.OpenXml — GitHub",
         "https://github.com/dotnet/Open-XML-SDK"),
        ("ECMA-376 — Office Open XML File Formats",
         "https://ecma-international.org/publications-and-standards/standards/ecma-376/"),
        ("Considerations for server-side Automation of Office",
         "https://learn.microsoft.com/en-us/office/troubleshoot/office-developer/considerations-for-server-side-automation-of-office"),
    ])
