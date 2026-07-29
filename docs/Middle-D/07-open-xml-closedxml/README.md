# Open XML SDK, ClosedXML — Excel va Word bilan ishlash — Middle D

## 1. Nima? (Ta'rif)

**Open XML SDK** — Microsoft'ning `.docx`/`.xlsx`/`.pptx` fayllar
bilan **dasturiy** ishlash uchun rasmiy kutubxonasi. **ClosedXML** —
Open XML SDK ustiga qurilgan, **Excel** bilan ishlashni ANCHA
soddalashtiruvchi ochiq kodli wrapper.

## 2. Nima uchun kerak?

ERP tizimida — xodimlar ro'yxatini Excel formatida eksport qilish,
shartnomani Word shablonidan avtomatik generatsiya qilish kabi
vazifalar tez-tez uchraydi. Bu fayllarni **qo'lda XML yozib** yaratish
juda murakkab — ClosedXML/Open XML SDK bu murakkablikni yashiradi.

## 3. Ichida nima sodir bo'ladi? (Mexanizm)

### 3.1 `.docx`/`.xlsx` fayl tuzilishi — ZIP ichida XML

```
company-report.xlsx — bu ASLIDA ZIP arxiv!

report.xlsx (ZIP)
├── [Content_Types].xml
├── _rels/
├── xl/
│   ├── workbook.xml         ← Worksheet ro'yxati
│   ├── worksheets/
│   │   └── sheet1.xml       ← Har bir katak, qiymat
│   ├── styles.xml           ← Formatlash (rang, shrift)
│   └── sharedStrings.xml    ← Takrorlanuvchi matn (optimallashtirish)
└── docProps/
```

`.xlsx` faylni `.zip`ga nomini o'zgartirib, arxiv dasturi bilan
ochsangiz — ICHIDA aynan shu XML fayllarni ko'rasiz. Open XML SDK —
bu ZIP+XML strukturasini **to'g'ridan** boshqaradi (past darajada);
ClosedXML — bu ustidagi **qulay obyekt modelini** taqdim etadi.

### 3.2 ClosedXML — Excel yaratish

```bash
dotnet add package ClosedXML --version 0.104.1
```

```csharp
using var workbook = new XLWorkbook();
var worksheet = workbook.Worksheets.Add("Xodimlar");

// Header
worksheet.Cell(1, 1).Value = "ID";
worksheet.Cell(1, 2).Value = "Ism";
worksheet.Cell(1, 3).Value = "Maosh";
worksheet.Row(1).Style.Font.Bold = true;
worksheet.Row(1).Style.Fill.BackgroundColor = XLColor.LightBlue;

// Ma'lumot
var employees = await _context.Employees.ToListAsync();
for (int i = 0; i < employees.Count; i++)
{
    var row = i + 2;
    worksheet.Cell(row, 1).Value = employees[i].Id;
    worksheet.Cell(row, 2).Value = employees[i].FullName;
    worksheet.Cell(row, 3).Value = employees[i].Salary;
    worksheet.Cell(row, 3).Style.NumberFormat.Format = "#,##0.00";
}

// Formula
worksheet.Cell(employees.Count + 2, 3).FormulaA1 = $"SUM(C2:C{employees.Count + 1})";

worksheet.Columns().AdjustToContents(); // Ustunlarni AVTO kenglikka moslash

using var stream = new MemoryStream();
workbook.SaveAs(stream);
```

### 3.3 Excel fayldan ma'lumot o'qish

```csharp
using var workbook = new XLWorkbook("employees.xlsx");
var worksheet = workbook.Worksheet(1);

foreach (var row in worksheet.RowsUsed().Skip(1)) // 1-qatorni (header) o'tkazib yuborish
{
    var name = row.Cell(2).GetString();
    var salary = row.Cell(3).GetValue<decimal>();
    Console.WriteLine($"{name}: {salary}");
}
```

### 3.4 Word hujjat yaratish — Open XML SDK

```bash
dotnet add package DocumentFormat.OpenXml --version 3.0.1
```

```csharp
using var doc = WordprocessingDocument.Create("contract.docx", WordprocessingDocumentType.Document);
var mainPart = doc.AddMainDocumentPart();
mainPart.Document = new Document();
var body = mainPart.Document.AppendChild(new Body());

// Sarlavha
var heading = new Paragraph(new Run(new Text("XODIM SHARTNOMASI")));
heading.ParagraphProperties = new ParagraphProperties(
    new Justification { Val = JustificationValues.Center });
body.AppendChild(heading);

// Oddiy paragraf
body.AppendChild(new Paragraph(new Run(new Text("Ushbu shartnoma quyidagilar orasida tuzildi:"))));

// Jadval
var table = new Table();
var row = new TableRow();
row.Append(new TableCell(new Paragraph(new Run(new Text("Ism")))));
row.Append(new TableCell(new Paragraph(new Run(new Text("Lavozim")))));
table.Append(row);
body.AppendChild(table);

mainPart.Document.Save();
```

Open XML SDK — Word/PowerPoint uchun ClosedXML kabi **soddalashtirilgan
wrapper YO'Q** (ba'zi community kutubxonalar bor, lekin keng
tarqalmagan) — shuning uchun Word generatsiyasi ko'proq **boilerplate**
talab qiladi.

### 3.5 Headers, Footers, Images (Word)

```csharp
var headerPart = mainPart.AddNewPart<HeaderPart>();
headerPart.Header = new Header(new Paragraph(new Run(new Text("ERP Kompaniya"))));

var imagePart = mainPart.AddImagePart(ImagePartType.Png);
using (var stream = File.OpenRead("logo.png"))
    imagePart.FeedData(stream);
```

### 3.6 Katta hajmli Excel — performance

```
❌ 100,000+ qatorli Excel — worksheet.Cell(i,j).Value = ... har birida
   sekin bo'lishi mumkin agar STYLE har safar QAYTA hisoblansa

✅ Tavsiyalar:
   - Style'larni BIR MARTA yarating, QAYTA ISHLATING (Style obyekti sifatida)
   - InsertData() metodi — collection'ni TO'G'RIDAN worksheet'ga
     "quyish" uchun (har katak alohida yozishdan TEZROQ)
   - SaveAs() faqat OXIRIDA, bir marta chaqiring
```

```csharp
// InsertData — TEZ usul (har katakka alohida yozishdan farqli)
worksheet.Cell(2, 1).InsertData(employees); // Butun collection'ni BIR YO'LA joylaydi
```

### 3.7 ASP.NET Core'da fayl yuklab olish

```csharp
[HttpGet("export")]
public async Task<IActionResult> ExportEmployees()
{
    using var workbook = new XLWorkbook();
    var ws = workbook.Worksheets.Add("Xodimlar");
    var employees = await _context.Employees.ToListAsync();
    ws.Cell(1, 1).InsertTable(employees.Select(e => new { e.Id, e.FullName, e.Salary }));

    using var stream = new MemoryStream();
    workbook.SaveAs(stream);
    stream.Position = 0;

    return File(stream.ToArray(),
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "employees.xlsx");
}
```

`FileStreamResult`/`File()` — ASP.NET Core'ga **stream'ni to'g'ridan
Response body'ga** yozishni buyuradi, `Content-Type` va
`Content-Disposition` (fayl nomi) headerlarini avtomatik o'rnatadi.

## 4. Kod — worksheet, cell, styles, formula

```csharp
worksheet.Cell("A1").Value = "Sarlavha";
worksheet.Range("A1:C1").Merge(); // Kataklarni birlashtirish
worksheet.Cell("B2").Style.Alignment.Horizontal = XLAlignmentHorizontalValues.Center;
worksheet.Cell("C10").FormulaA1 = "=AVERAGE(C2:C9)";
```

## 5. Qachon ishlatish kerak?

| Vaziyat | Yechim |
|---|---|
| Excel eksport/import (oddiy, murakkab formatlash) | ClosedXML |
| Word shablon asosida hujjat generatsiyasi | Open XML SDK (yoki DocX kabi wrapper) |
| Faqat oddiy CSV eksport | `CsvHelper` (soddaroq, yengilroq) |
| Katta hajm (yuz minglab qator) | ClosedXML `InsertData`, style optimallashtirish |

## 6. Muhim nuqtalar

- `.xlsx` — ZIP+XML bo'lgani uchun, fayl **yuqori kompressiya**ga ega —
  hajmi kutilganidan kichikroq bo'lishi mumkin.
- ClosedXML — **faqat** Excel uchun; Word/PowerPoint uchun Open XML
  SDK'ni to'g'ridan (yoki boshqa kutubxona) ishlatish kerak.
- Fayl yaratishda `using` (yoki `Dispose()`) SHART — ichkarida ochiq
  fayl handle/stream resurslari bor.

## 7. Imtihon savollari

1. `.xlsx` fayl "aslida" nima va uni qanday tekshirish mumkin?
2. ClosedXML Open XML SDK'dan qanday farq qiladi?
3. Katta hajmli Excel generatsiyasida qanday performance
   optimallashtirishlar qilinishi mumkin?
4. ASP.NET Core'da generatsiya qilingan Excel faylni qanday
   qaytarish kerak (`FileStreamResult`)?
5. Word hujjat generatsiyasi Excel'dan nima uchun ko'proq
   boilerplate talab qiladi?
6. `sharedStrings.xml` nima vazifani bajaradi (xlsx tuzilishida)?
