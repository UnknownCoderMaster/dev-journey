# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "Using FTP"
CATEGORY = ".NET / C#"
TITLE = "FTP bilan Ishlash"
SUBTITLE = "Protokol, uning cheklovlari va .NET dagi amalga oshirish"
FILENAME = "Using FTP.docx"


def build(d):
    h1(d, "1. FTP qanday ishlaydi")

    para(d, "FTP (File Transfer Protocol) — fayl uzatish uchun eski, "
            "lekin hamon keng tarqalgan protokol. Uning o'ziga xos "
            "jihati shundaki, u **ikkita ulanish** ishlatadi.")

    code(d, """Boshqaruv ulanishi (21-port)  — buyruqlar: LIST, RETR, STOR
Ma'lumot ulanishi (alohida)   — fayl mazmuni""")

    h2(d, "1.1 Faol va passiv rejim")

    code(d, """Faol (Active) rejim:
  Mijoz → Server: "men 50000-portda kutaman"
  Server → Mijoz: ma'lumot ulanishini OCHADI

Passiv (Passive) rejim:
  Mijoz → Server: "PASV"
  Server → Mijoz: "60000-portga ulan"
  Mijoz → Server: ma'lumot ulanishini ochadi""")

    note(d, "Passiv rejim deyarli har doim kerak bo'ladi:",
         "Faol rejimda server mijozga ulanishga urinadi. Lekin mijoz "
         "odatda NAT yoki firewall ortida bo'ladi va bunday ulanish "
         "bloklanadi. Shuning uchun FTP ishlamayotganda birinchi "
         "tekshiriladigan narsa — passiv rejim yoqilganmi.")

    # ───────────────────────────────────────────
    h1(d, "2. Xavfsizlik muammosi")

    note(d, "Oddiy FTP hamma narsani ochiq matnda uzatadi:",
         "Foydalanuvchi nomi, parol va fayl mazmuni — hammasi "
         "shifrlanmagan ketadi. Tarmoqni tinglayotgan har kim ularni "
         "o'qiy oladi. Shuning uchun oddiy FTP ni internet orqali "
         "ishlatish qabul qilinmaydi.")

    table(d, ["Protokol", "Shifrlash", "Asosi"],
          [["FTP", "Yo'q", "FTP"],
           ["FTPS", "TLS", "FTP + TLS"],
           ["SFTP", "SSH", "Butunlay boshqa protokol"]],
          widths=[3.4, 4.0, 8.1])

    note(d, "SFTP va FTPS ni chalkashtirmaslik kerak:",
         "Nomlari o'xshash, lekin ular umuman boshqa narsalar. FTPS — "
         "bu FTP ustiga TLS qo'shilgan versiya, u hamon ikkita ulanish "
         "ishlatadi. SFTP esa SSH protokolining bir qismi va bitta "
         "ulanishda ishlaydi. Amalda SFTP ancha qulayroq, chunki u "
         "firewall bilan muammo tug'dirmaydi.")

    # ───────────────────────────────────────────
    h1(d, "3. .NET dagi holat")

    para(d, "`FtpWebRequest` klassi `.NET` da mavjud, lekin `.NET 6` dan "
            "boshlab eskirgan deb belgilangan. Microsoft yangi kodda "
            "uchinchi tomon kutubxonasidan foydalanishni tavsiya qiladi.")

    code(d, """// Eskirgan — faqat ma'lumot uchun
var request = (FtpWebRequest)WebRequest.Create("ftp://server/file.txt");
request.Method = WebRequestMethods.Ftp.DownloadFile;
request.Credentials = new NetworkCredential("user", "password");
request.UsePassive = true;

using var response = (FtpWebResponse)request.GetResponse();
using var stream = response.GetResponseStream();""")

    note(d, "Nima uchun u eskirgan:",
         "`FtpWebRequest` eski `WebRequest` modeliga asoslangan, "
         "asinxron ishlashi noqulay va zamonaviy FTPS imkoniyatlarini "
         "to'liq qo'llab-quvvatlamaydi. Yangi loyihada `FluentFTP` "
         "ishlatiladi.")

    # ───────────────────────────────────────────
    h1(d, "4. FluentFTP")

    code(d, """dotnet add package FluentFTP""")

    code(d, """using FluentFTP;

await using var client = new AsyncFtpClient(
    host: "ftp.example.com",
    user: "username",
    pass: "password",
    port: 21);

client.Config.EncryptionMode = FtpEncryptionMode.Explicit;   // FTPS
client.Config.ValidateAnyCertificate = false;
client.Config.DataConnectionType = FtpDataConnectionType.AutoPassive;
client.Config.ConnectTimeout = 15_000;
client.Config.RetryAttempts = 3;

await client.Connect(ct);""")

    h2(d, "4.1 Fayl yuklash va olish")

    code(d, """// Yuklash
await client.UploadFile(
    localPath: @"C:\\reports\\monthly.pdf",
    remotePath: "/reports/2026/monthly.pdf",
    existsMode: FtpRemoteExists.Overwrite,
    createRemoteDir: true,
    token: ct);

// Olish
await client.DownloadFile(
    localPath: @"C:\\downloads\\data.csv",
    remotePath: "/exports/data.csv",
    existsMode: FtpLocalExists.Overwrite,
    token: ct);

// Oqim orqali — xotirada saqlamasdan
await using var stream = File.Create(localPath);
await client.DownloadStream(stream, "/exports/large.csv", token: ct);""")

    h2(d, "4.2 Papka bilan ishlash")

    code(d, """// Ro'yxat olish
foreach (var item in await client.GetListing("/reports", ct))
{
    Console.WriteLine($"{item.Type}  {item.Name}  " +
                      $"{item.Size} bayt  {item.Modified:yyyy-MM-dd}");
}

// Papka yaratish
await client.CreateDirectory("/reports/2026/11", ct);

// Mavjudligini tekshirish
if (await client.FileExists("/reports/monthly.pdf", ct)) { ... }

// O'chirish va qayta nomlash
await client.DeleteFile("/temp/old.csv", ct);
await client.Rename("/temp/a.csv", "/archive/a.csv", ct);""")

    h2(d, "4.3 Papkani sinxronlash")

    code(d, """var results = await client.UploadDirectory(
    localFolder: @"C:\\publish",
    remoteFolder: "/www/myapp",
    mode: FtpFolderSyncMode.Update,
    existsMode: FtpRemoteExists.Overwrite,
    token: ct);

foreach (var result in results.Where(r => r.IsFailed))
    _logger.LogError("Yuklanmadi: {Name} — {Error}",
        result.Name, result.Exception?.Message);""")

    note(d, "Natijalarni tekshirish shart:",
         "Metod istisno otmasligi mumkin, lekin ayrim fayllar "
         "yuklanmagan bo'ladi. Agar men natijani tekshirmasam, "
         "joylashtirish \"muvaffaqiyatli\" deb hisoblanadi, lekin "
         "serverda yarim yangilangan ilova qoladi — bu eng yomon "
         "holat.")

    # ───────────────────────────────────────────
    h1(d, "5. SFTP — tavsiya etiladigan muqobil")

    code(d, """dotnet add package SSH.NET""")

    code(d, """using Renci.SshNet;

using var client = new SftpClient("server.example.com", 22, "user", "password");
client.Connect();

// Yuklash
await using (var file = File.OpenRead(localPath))
    client.UploadFile(file, "/home/user/upload.pdf", canOverride: true);

// Olish
await using (var file = File.Create(localPath))
    client.DownloadFile("/home/user/data.csv", file);

// Ro'yxat
foreach (var item in client.ListDirectory("/home/user"))
{
    if (item.Name is "." or "..") continue;
    Console.WriteLine($"{item.Name}  {item.Length}  {item.LastWriteTime}");
}

client.Disconnect();""")

    code(d, """// Kalit bilan autentifikatsiya — paroldan xavfsizroq
var keyFile = new PrivateKeyFile(@"C:\\keys\\id_ed25519", passphrase);
using var client = new SftpClient("server.example.com", 22, "user", keyFile);""")

    note(d, "Imkon bo'lsa men SFTP ni tanlayman:",
         "Bitta port (22), bitta ulanish, firewall bilan muammo yo'q, "
         "kalit bilan autentifikatsiya mavjud va hammasi shifrlangan. "
         "FTP ni esa faqat qarshi tomon boshqasini "
         "qo'llab-quvvatlamaganda ishlataman — bu odatda eski "
         "korporativ tizimlar bilan integratsiyada uchraydi.")

    # ───────────────────────────────────────────
    h1(d, "6. Amaliy masalalar")

    h2(d, "6.1 Yarim yozilgan fayl muammosi")

    note(d, "Bu klassik integratsiya muammosi:",
         "Men faylni yuklayapman, qarshi tomondagi dastur esa papkani "
         "kuzatib turadi. U faylni to'liq yuklanmasidan oldin ko'rib, "
         "qayta ishlashni boshlashi mumkin — natijada yarim fayl "
         "o'qiladi.")

    code(d, """// Yechim — vaqtinchalik nom bilan yuklab, keyin qayta nomlash
var tempName = $"/incoming/{fileName}.tmp";
var finalName = $"/incoming/{fileName}";

await client.UploadFile(localPath, tempName,
    FtpRemoteExists.Overwrite, token: ct);

await client.Rename(tempName, finalName, ct);""")

    para(d, "Qayta nomlash — atomar amal, shuning uchun qarshi tomon "
            "faylni faqat to'liq holatda ko'radi.")

    h2(d, "6.2 Chidamlilik")

    code(d, """client.Config.RetryAttempts = 3;
client.Config.ConnectTimeout = 15_000;
client.Config.ReadTimeout = 30_000;
client.Config.DataConnectionConnectTimeout = 15_000;

// Uzilgan yuklashni davom ettirish
await client.DownloadFile(localPath, remotePath,
    FtpLocalExists.Resume, token: ct);""")

    h2(d, "6.3 Sirlarni saqlash")

    code(d, """public class FtpOptions
{
    [Required] public string Host { get; set; } = "";
    [Range(1, 65535)] public int Port { get; set; } = 21;
    [Required] public string Username { get; set; } = "";
    [Required] public string Password { get; set; } = "";
    public bool UseFtps { get; set; } = true;
}""")

    note(d, "FTP parollari ayniqsa ehtiyotkorlikni talab qiladi:",
         "Ular ko'pincha eski tizimlardan keladi va murakkab "
         "bo'lmaydi. Bundan tashqari, bitta hisob odatda butun "
         "papkaga kirish huquqiga ega. Shuning uchun uni "
         "konfiguratsiya faylida emas, sir omborida saqlash muhim.")

    # ───────────────────────────────────────────
    h1(d, "7. Nosozlikni topish")

    code(d, """// Batafsil log
client.Config.LogToConsole = true;

client.Logger = new FtpLogAdapter((level, message) =>
    _logger.Log(MapLevel(level), "FTP: {Message}", message));""")

    table(d, ["Xatolik", "Odatdagi sabab"],
          [["530 Login incorrect", "Noto'g'ri hisob ma'lumotlari"],
           ["425 Can't open data connection", "Faol rejim; passivga o'tish "
                                              "kerak"],
           ["550 Permission denied", "Papkaga yozish huquqi yo'q"],
           ["421 Timeout", "Ulanish uzoq jim turgan"],
           ["Sertifikat xatosi", "O'z imzolangan sertifikat"]],
          widths=[5.6, 9.9])

    # ───────────────────────────────────────────
    h1(d, "8. Xulosa")

    bullets(d, [
        "FTP ikkita ulanish ishlatadi: boshqaruv va ma'lumot.",
        "NAT ortidagi mijozlar uchun passiv rejim zarur.",
        "Oddiy FTP hamma narsani ochiq matnda uzatadi.",
        "FTPS — FTP + TLS, SFTP — SSH ning bir qismi; ular turli "
        "protokollar.",
        "`FtpWebRequest` eskirgan — `FluentFTP` yoki `SSH.NET` "
        "ishlatiladi.",
        "Papka sinxronlashda har bir faylning natijasini tekshirish "
        "kerak.",
        "Vaqtinchalik nom bilan yuklab, keyin qayta nomlash yarim "
        "fayl muammosini hal qiladi.",
        "Imkon bo'lsa FTP o'rniga SFTP tanlash afzal.",
    ])

    sources(d, [
        ("FluentFTP — GitHub",
         "https://github.com/robinrodricks/FluentFTP"),
        ("SSH.NET — GitHub",
         "https://github.com/sshnet/SSH.NET"),
        ("RFC 959 — File Transfer Protocol",
         "https://www.rfc-editor.org/rfc/rfc959"),
        ("RFC 4217 — Securing FTP with TLS",
         "https://www.rfc-editor.org/rfc/rfc4217"),
    ])
