# FTP, SFTP, FTPS — Middle D

## 1. Nima? (Ta'rif)

**FTP (File Transfer Protocol)** — fayllarni tarmoq orqali uzatish
uchun eski, keng tarqalgan protokol (port 21). **SFTP** — SSH ustida
ishlaydigan, xavfsiz fayl uzatish. **FTPS** — FTP + SSL/TLS
(shifrlangan FTP).

## 2. Nima uchun kerak?

ERP tizimida — hisobot fayllarini tashqi hamkor serveriga yuborish,
legacy tizimlardan fayl olish kabi integratsiyalarda FTP hali ham
uchraydi (garchi zamonaviy tizimlarda S3/Minio ko'proq tavsiya
etilsa ham).

## 3. Ichida nima sodir bo'ladi? (Mexanizm)

### 3.1 FTP protokoli — Active vs Passive

```
FTP — IKKITA alohida ulanish ishlatadi:
  Control connection (port 21) — buyruqlar uchun (LOGIN, LIST, RETR)
  Data connection             — HAQIQIY fayl ma'lumoti uchun

Active mode:
  Client → Server: "Men PORT 5000 da tinglayapman"
  Server → Client: Server client'ning 5000-portiga ULANADI
  ❌ Muammo: Client FIREWALL ortida bo'lsa — server unga ULANOLMAYDI!

Passive mode:
  Client → Server: "PASV" buyrug'i
  Server → Client: "Men PORT 40123 da tinglayapman"
  Client → Server: Client serverning 40123-portiga ULANADI
  ✅ Client tomonidan BOSHLANADI — firewall ortida ISHLAYDI
```

### 3.2 FTP vs SFTP vs FTPS

| | FTP | FTPS | SFTP |
|---|---|---|---|
| Shifrlash | ❌ Yo'q (ochiq matn) | ✅ SSL/TLS | ✅ SSH orqali |
| Protokol asosi | O'ziga xos | FTP + TLS | SSH (butunlay boshqa protokol) |
| Port | 21 | 21 (yoki 990) | 22 (SSH bilan bir xil) |
| Xavfsizlik | ❌ Eng past | ✅ Yaxshi | ✅✅ Eng yaxshi |

**Tavsiya:** Zamonaviy tizimlarda — **SFTP** (yoki umuman Object
Storage — Minio/S3) ishlatilishi kerak, oddiy FTP — parol va
ma'lumotni **ochiq matn** holida yuboradi (tarmoqda tinglovchi bo'lsa,
parol OCHIQ ko'rinadi).

### 3.3 `FtpWebRequest` (eski, .NET'da obsolete)

```csharp
var request = (FtpWebRequest)WebRequest.Create("ftp://ftp.example.com/report.pdf");
request.Method = WebRequestMethods.Ftp.UploadFile;
request.Credentials = new NetworkCredential("user", "password");

using var fileStream = File.OpenRead("report.pdf");
using var requestStream = await request.GetRequestStreamAsync();
await fileStream.CopyToAsync(requestStream);

using var response = (FtpWebResponse)await request.GetResponseAsync();
Console.WriteLine(response.StatusDescription);
```

`FtpWebRequest` — .NET 6+ da **Obsolete** deb belgilangan, yangi
loyihalarda ishlatish tavsiya etilmaydi.

### 3.4 FluentFTP — zamonaviy yondashuv

```bash
dotnet add package FluentFTP --version 49.0.1
```

```csharp
using var client = new FtpClient("ftp.example.com", "user", "password");
await client.Connect();

// Upload
await client.UploadFile("local/report.pdf", "/remote/report.pdf");

// Download
await client.DownloadFile("local/downloaded.pdf", "/remote/report.pdf");

// Papka yaratish
await client.CreateDirectory("/remote/reports");

// Ro'yxat olish
var items = await client.GetListing("/remote");
foreach (var item in items)
    Console.WriteLine($"{item.Name} ({item.Type})");

// O'chirish
await client.DeleteFile("/remote/old-report.pdf");
```

FluentFTP — **SFTP, FTPS, FTP** uchun yagona, zamonaviy, async-first
API taqdim etadi — `FtpWebRequest`ga TAVSIYA ETILADIGAN o'rinbosar.

### 3.5 Passive mode sozlash

```csharp
client.Config.DataConnectionType = FtpDataConnectionType.PASV;
```

Production serverlar (ayniqsa firewall/NAT ortida) — deyarli har
doim **Passive mode** talab qiladi.

### 3.6 Async operatsiyalar

```csharp
public async Task UploadReportAsync(string localPath, string remotePath)
{
    using var client = new FtpClient("ftp.example.com", "user", "password");
    await client.Connect();

    var status = await client.UploadFile(localPath, remotePath, FtpRemoteExists.Overwrite);
    if (status == FtpStatus.Failed)
        throw new InvalidOperationException("FTP upload muvaffaqiyatsiz");
}
```

## 4. Kod — SFTP (SSH.NET bilan, ko'proq tavsiya etiladigan yo'l)

```bash
dotnet add package SSH.NET --version 2023.0.1
```

```csharp
using var sftp = new SftpClient("sftp.example.com", "user", "password");
sftp.Connect();

using var fileStream = File.OpenRead("report.pdf");
sftp.UploadFile(fileStream, "/remote/report.pdf");

using var downloadStream = File.Create("downloaded.pdf");
sftp.DownloadFile("/remote/report.pdf", downloadStream);

sftp.Disconnect();
```

## 5. Qachon ishlatish kerak?

| Vaziyat | Yechim |
|---|---|
| Legacy hamkor tizim, faqat FTP qo'llab-quvvatlaydi | FluentFTP |
| Xavfsizlik muhim, tashqi hamkor SSH qo'llab-quvvatlaydi | SFTP (SSH.NET) |
| Yangi loyiha, fayl saqlash | Minio/S3 (Object Storage) — FTP EMAS |
| Firewall/NAT ortidagi client | Passive mode |

## 6. Muhim nuqtalar

- Oddiy FTP — parolni **ochiq matn** holida yuboradi — tarmoqda
  MITM (Man-in-the-Middle) hujumiga OCHIQ.
- `FtpWebRequest` — .NET'da eskirgan, yangi kodda ISHLATILMASIN.
- Zamonaviy arxitekturada — fayl almashinuvi uchun ko'pincha
  **Object Storage** (Minio/S3) yoki **API** (upload endpoint)
  FTP'ni almashtiradi.

## 7. Imtihon savollari

1. FTP Active va Passive mode orasidagi farqni tushuntiring — nima
   uchun Passive mode firewall ortida ishlaydi?
2. FTP, FTPS va SFTP orasidagi xavfsizlik farqini tushuntiring.
3. Nima uchun `FtpWebRequest` yangi loyihalarda ishlatilmasligi kerak?
4. FluentFTP qanday afzalliklar taqdim etadi?
5. Zamonaviy arxitekturada FTP o'rniga qanday alternativalar
   ishlatiladi?
