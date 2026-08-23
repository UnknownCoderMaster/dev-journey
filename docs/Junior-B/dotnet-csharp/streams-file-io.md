# Streams and Input/Output, File I/O — Junior B

## 1. What (Nima?)

**Stream** — ma'lumotni **KETMA-KET, BO'LAK-BO'LAK** (byte-byte
emas, ODATDA BUFFER orqali) O'QISH/YOZISH uchun ABSTRAKSIYA — MANBA
(fayl, tarmoq, xotira) NIMA EKANIDAN QAT'I NAZAR, BIR XIL API
(`Read`, `Write`) TAQDIM ETADI. **File I/O** — fayl TIZIMI bilan
(YARATISH, O'QISH, YOZISH, O'CHIRISH) ISHLASH.

## 2. Real hayot analogiyasi

**Stream — QUVUR (TRUBA).** Suv MANBAI — QUDUQ, DARYO YOKI
REZERVUAR BO'LISHI MUMKIN (fayl, tarmoq, xotira) — LEKIN QUVURNING
O'ZI (Stream API) — BIR XIL: SUV (MA'LUMOT) KETMA-KET OQADI, BIR
VAQTDA BUTUN OKEANNI (BUTUN FAYLNI) OLIB KETISH SHART EMAS —
KERAKLI MIQDORDA, BOSQICHMA-BOSQICH OQIB O'TADI.

**Buffered Stream — SUV OMBORI QUVUR OLDIDA.** Agar HAR TOMCHINI
(bayt) ALOHIDA UZATSANGIZ — BU JUDA SEKIN (ko'p KICHIK operatsiya).
Buning O'RNIGA, KICHIK "OMBOR" (BUFFER) — MA'LUM MIQDORDA SUVNI
YIG'IB, KEYIN BIR YO'LA UZATADI — BU ANCHA SAMARALI.

## 3. Why (Nega kerak?)

Agar Stream ABSTRAKSIYASI BO'LMASA — HAR TUR MANBA (fayl, tarmoq
socket, xotiradagi massiv) uchun **ALOHIDA API** o'RGANISH KERAK
BO'LARDI. Stream — BU FARQNI YASHIRADI: `FileStream`, `NetworkStream`,
`MemoryStream` — HAMMASI `Stream` ABSTRAKT KLASSIDAN MEROS OLADI,
BIR XIL `Read()`/`Write()` METODLARIGA EGA.

**KATTA FAYL BILAN ishlashda — MUHIM sabab:** 10GB faylni
`File.ReadAllBytes()` BILAN O'QISH — 10GB RAM TALAB QILADI! Stream
— faylni **QISM-QISM** (masalan 4KB BUFFER bilan) O'QISH imkonini
BERADI — XOTIRA SARFI **DOIM KICHIK** QOLADI, FAYL HAJMIDAN QAT'I
NAZAR.

## 4. Internals (Ichki mexanizm)

### Stream ierarxiyasi

```
Stream (abstract) — BAZAVIY KLASS
    │
    ├── FileStream       — FAYL bilan ISHLASH (OS FILE HANDLE ATROFIDA "WRAPPER")
    ├── MemoryStream      — XOTIRADAGI byte[] massiv ATROFIDA "WRAPPER"
    ├── NetworkStream     — TCP SOCKET ATROFIDA "WRAPPER"
    ├── GZipStream        — SIQISH/OCHISH (DECORATOR PATTERN — BOSHQA
    │                        Stream'ni "O'RAYDI")
    └── CryptoStream      — SHIFRLASH/OCHISH (DECORATOR PATTERN)
```

### Decorator Pattern — Stream'larni "ZANJIRLASH"

```csharp
using var fileStream = new FileStream("data.gz", FileMode.Open);
using var gzipStream = new GZipStream(fileStream, CompressionMode.Decompress); // fileStream'ni "O'RAYDI"
using var reader = new StreamReader(gzipStream); // gzipStream'ni "O'RAYDI"

string content = reader.ReadToEnd();
```

```
Bu — DECORATOR DIZAYN PATTERNI: HAR "QATLAM" — ICHKI Stream'ni
"O'RAB", YANGI FUNKSIONALLIK (SIQISH, SHIFRLASH, MATNGA AYLANTIRISH)
QO'SHADI, LEKIN BAZAVIY `Read()`/`Write()` INTERFEYSI SAQLANIB
QOLADI — HAR QATLAM QOLGANLARIDAN "BEXABAR" ISHLAYDI.
```

### Buffered I/O — nima uchun TEZROQ

```
Bufferlanmagan I/O:
  HAR bayt/qator uchun — OPERATSION TIZIM SYSCALL (masalan
  ReadFile/WriteFile Windows'da) — HAR SYSCALL — QIMMAT (KERNEL
  MODE'GA O'TISH, CONTEXT SWITCH)

Buffered I/O (StreamReader, BufferedStream):
  MA'LUM MIQDORDA (masalan 4KB, 8KB) MA'LUMOT — BITTA SYSCALL
  BILAN O'QILADI/YOZILADI, XOTIRADAGI BUFFER'GA JOYLASHTIRILADI —
  DASTUR BUFFER'DAN O'QIYDI (SYSCALL SHART EMAS), BUFFER
  TUGAGANDA — YANGI SYSCALL
```

### `using`/`IDisposable` bilan bog'liqlik

```
FileStream — UNMANAGED RESURS (OS FILE HANDLE) NI O'Z ICHIGA
OLADI — CLR BUNI AVTOMATIK "BILMAYDI" (docs/Junior-A/03-gc-dispose-finalize).
`using` STATEMENT — Dispose() ni KAFOLATLI CHAQIRADI, FILE HANDLE'NI
DARHOL BO'SHATADI (aks holda — BOSHQA PROSESS SHU FAYLGA MUROJAAT
QILA OLMASLIGI MUMKIN, "FILE IS IN USE" XATOSI).
```

### Synchronous vs Asynchronous File I/O

```csharp
// SYNCHRONOUS — THREAD BLOKLANADI, DISK I/O TUGAGUNCHA KUTADI
byte[] data = File.ReadAllBytes(path);

// ASYNCHRONOUS — THREAD Thread Pool'GA QAYTARILADI (docs Async/Thread fayliga qarang)
byte[] data = await File.ReadAllBytesAsync(path);
```

```
Fayl I/O — OS DARAJASIDA "I/O Completion Port" (IOCP, Windows)
YOKI EPOLL (Linux) ORQALI HAQIQATDA ASYNCHRONOUS BAJARILISHI
MUMKIN — THREAD KUTIB TURMAYDI, OS "TUGADI" DEB XABAR BERGANDA
QAYTA ISHGA TUSHIRILADI.
```

## 5. Code (Amaliy kod)

```csharp
// Oddiy — KICHIK fayllar uchun (BUTUN faylni XOTIRAGA yuklaydi)
string content = await File.ReadAllTextAsync("employees.json");
await File.WriteAllTextAsync("output.json", content);

byte[] bytes = await File.ReadAllBytesAsync("photo.jpg");
```

```csharp
// Stream — KATTA fayllar uchun (XOTIRAGA TO'LIQ YUKLAMASDAN)
public async Task CopyLargeFileAsync(string sourcePath, string destPath)
{
    using var sourceStream = new FileStream(sourcePath, FileMode.Open, FileAccess.Read);
    using var destStream = new FileStream(destPath, FileMode.Create, FileAccess.Write);

    await sourceStream.CopyToAsync(destStream); // ICHKARIDA BUFFER (default 81920 bayt) BILAN QISM-QISM NUSXALAYDI
}
```

```csharp
// StreamReader/StreamWriter — MATN uchun (encoding'ni BOSHQARADI)
using (var writer = new StreamWriter("log.txt", append: true))
{
    await writer.WriteLineAsync($"{DateTime.UtcNow}: Xodim yaratildi");
}

using (var reader = new StreamReader("log.txt"))
{
    string? line;
    while ((line = await reader.ReadLineAsync()) != null)
        Console.WriteLine(line);
}
```

```csharp
// MemoryStream — XOTIRADA "VIRTUAL FAYL" (masalan Excel generatsiyasi uchun)
public async Task<byte[]> GenerateReportAsync(List<Employee> employees)
{
    using var memoryStream = new MemoryStream();
    using (var writer = new StreamWriter(memoryStream, leaveOpen: true))
    {
        foreach (var e in employees)
            await writer.WriteLineAsync($"{e.FullName},{e.Salary}");
    }
    return memoryStream.ToArray(); // API'dan FileStreamResult sifatida QAYTARISH mumkin
}
```

```csharp
// Fayl tizimi bilan ishlash
if (!Directory.Exists("uploads"))
    Directory.CreateDirectory("uploads");

var files = Directory.GetFiles("uploads", "*.pdf");
foreach (var file in files)
{
    var info = new FileInfo(file);
    Console.WriteLine($"{info.Name}: {info.Length} bayt, {info.LastWriteTimeUtc}");
}

File.Delete("uploads/old-file.pdf");
File.Move("temp.txt", "uploads/final.txt");
```

## 6. Keng tarqalgan xatolar / noto'g'ri tushunchalar

```
❌ "File.ReadAllBytes() — HAR DOIM XAVFSIZ" — KATTA fayllar
   (GB darajasida) uchun XAVFLI — BUTUN faylni XOTIRAGA YUKLAYDI,
   OutOfMemoryException XAVFI. Stream/CopyToAsync ISHLATILISHI kerak.

❌ "using YOZMASAM HAM, GC FileStream'ni TOZALAYDI" — GC XOTIRANI
   TOZALAYDI, LEKIN OS FILE HANDLE — UNMANAGED RESURS, GC BUNI
   DARHOL BILMAYDI (FAQAT FINALIZER orqali, NOANIQ VAQTDA) — 'using'
   SHART, aks holda "too many open files" XATOSI YOKI FAYL
   BOSHQA PROSESSGA "BAND" bo'lib QOLISHI mumkin.

❌ "Stream.Read() — HAR DOIM SO'RALGAN BAYT SONINI TO'LIQ QAYTARADI"
   — NOTO'G'RI! `Read()` — QANCHA BAYT O'QIY OLGANINI QAYTARADI
   (0 dan so'ralgan songacha) — TSIKLDA CHAQIRISH KERAK, YOKI
   `ReadExactly()`/`CopyToAsync()` ISHLATISH kerak.

❌ "StreamReader/StreamWriter — Encoding'ni AVTOMATIK to'g'ri
   ANIQLAYDI" — DEFAULT holda UTF-8 (BOM tekshirilgan holda) qabul
   qilinadi, lekin MANBA fayl BOSHQA encoding'da (masalan Windows-1251)
   bo'lsa — ANIQ ko'rsatilishi kerak: `new StreamReader(path,
   Encoding.GetEncoding(1251))`.

❌ "FileStream — SYNCHRONOUS metod chaqirilsa HAM, ASYNC I/O
   ISHLATADI" — Platform/sozlamalarga BOG'LIQ — `useAsync: true`
   parametri (FileStream konstruktorida) YOKI async metodlar
   (`ReadAsync`) ANIQ ishlatilishi TAVSIYA ETILADI.
```

## 7. Exam (Interview savollari)

**1. Stream nima va u nima uchun ABSTRAKSIYA sifatida FOYDALI?**
Stream — MA'LUMOTNI KETMA-KET O'QISH/YOZISH uchun UMUMIY
INTERFEYS — MANBA (fayl, tarmoq, xotira) TURIDAN QAT'I NAZAR, BIR
XIL `Read()`/`Write()` API BILAN ISHLASH imkonini BERADI. Bu —
KODNI MANBADAN MUSTAQIL QILADI (masalan BIR XIL LOGIKA — FAYLGA
HAM, TARMOQQA HAM ISHLAYDI).

**2. `File.ReadAllBytes()` va `FileStream` + `CopyToAsync()`
orasidagi FARQ nima, va QACHON QAYSI BIRI ISHLATILADI?**
`File.ReadAllBytes()` — BUTUN faylni BIR YO'LA XOTIRAGA YUKLAYDI
— KICHIK fayllar UCHUN QULAY. `FileStream` + `CopyToAsync()` —
faylni QISM-QISM (BUFFER orqali) QAYTA ISHLAYDI — XOTIRA SARFI
DOIM KICHIK, KATTA fayllar (GB darajasida) UCHUN MAJBURIY.

**3. Decorator Pattern Stream klasslarida QANDAY QO'LLANILGAN?**
`GZipStream`, `CryptoStream` KABI klasslar — BOSHQA Stream'ni
(masalan `FileStream`) KONSTRUKTORDA QABUL QILIB, "O'RAYDI" — YANGI
FUNKSIONALLIK (SIQISH, SHIFRLASH) QO'SHADI, LEKIN ASOSIY
`Read()`/`Write()` INTERFEYSINI SAQLAB QOLADI — bu SIZGA BIR
NECHTA Stream'ni "ZANJIRLASH" (masalan fayl + siqish + shifrlash)
IMKONINI BERADI.

**4. `using` statement FileStream bilan ISHLATILMASA, NIMA XAVF
BOR?**
FileStream — OS FILE HANDLE (UNMANAGED RESURS) NI O'Z ICHIGA
OLADI. GC — XOTIRANI ERTA-KECH TOZALAYDI, LEKIN FILE HANDLE —
FAQAT FINALIZER ORQALI (NOANIQ VAQTDA) BO'SHATILADI. `using`SIZ —
FAYL UZOQ VAQT "BAND" bo'lib QOLISHI, BOSHQA PROSESS UNGA
MUROJAAT QILA OLMASLIGI ("file in use" xatosi) MUMKIN.

**5. Buffered I/O nima uchun bufferlanmagan I/O'dan TEZROQ?**
Bufferlanmagan I/O — HAR KICHIK O'QISH/YOZISH uchun ALOHIDA
OPERATSION TIZIM SYSCALL TALAB QILADI (QIMMAT — KERNEL MODE'GA
O'TISH). Buffered I/O — MA'LUM MIQDORDA MA'LUMOTNI BITTA SYSCALL
BILAN XOTIRADAGI BUFFER'GA O'QIYDI, DASTUR SHU BUFFER'DAN
FOYDALANADI — SYSCALL SONI SEZILARLI KAMAYADI.
