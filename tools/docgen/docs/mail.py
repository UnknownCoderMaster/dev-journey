# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "Sending Mail with SmtpClient, Receiving POP3 Mail with TCP"
CATEGORY = ".NET / C#"
TITLE = "Elektron Pochta Bilan Ishlash"
SUBTITLE = "SMTP orqali yuborish va POP3/IMAP orqali o'qish"
FILENAME = "Sending Mail with SmtpClient, Receiving POP3 Mail with TCP.docx"


def build(d):
    h1(d, "1. Pochta protokollari")

    table(d, ["Protokol", "Vazifasi", "Standart portlar"],
          [["SMTP", "Yuborish", "25, 465 (SSL), 587 (STARTTLS)"],
           ["POP3", "Yuklab olish", "110, 995 (SSL)"],
           ["IMAP", "Serverdan boshqarish", "143, 993 (SSL)"]],
          widths=[3.0, 5.0, 7.5])

    note(d, "POP3 va IMAP farqi:",
         "POP3 xatni serverdan yuklab oladi va odatda o'chiradi — u "
         "bitta qurilma uchun mo'ljallangan. IMAP esa xatlarni serverda "
         "qoldiradi va holatni sinxronlashtiradi. Bugungi ko'p "
         "qurilmali dunyoda IMAP deyarli har doim to'g'riroq tanlov.")

    # ───────────────────────────────────────────
    h1(d, "2. SmtpClient va uning holati")

    para(d, "`System.Net.Mail.SmtpClient` `.NET` da mavjud, lekin "
            "Microsoft hujjatining o'zida u eskirgan deb belgilangan va "
            "yangi kod uchun tavsiya etilmaydi.")

    code(d, """// Mavjud, lekin tavsiya etilmaydi
using var client = new SmtpClient("smtp.example.com", 587)
{
    EnableSsl = true,
    Credentials = new NetworkCredential("user@example.com", password)
};

var message = new MailMessage("from@example.com", "to@example.com")
{
    Subject = "Salom",
    Body = "<h1>Xabar</h1>",
    IsBodyHtml = true
};

await client.SendMailAsync(message);""")

    note(d, "Nega u tavsiya etilmaydi:",
         "`SmtpClient` zamonaviy protokol imkoniyatlarini to'liq "
         "qo'llab-quvvatlamaydi — ayniqsa OAuth2 autentifikatsiyasini. "
         "Gmail va Outlook kabi xizmatlar esa oddiy parol bilan "
         "kirishni asta-sekin yopmoqda. Shuning uchun yangi loyihada "
         "`MailKit` ishlatiladi.")

    # ───────────────────────────────────────────
    h1(d, "3. MailKit — tavsiya etiladigan kutubxona")

    code(d, """dotnet add package MailKit""")

    code(d, """using MailKit.Net.Smtp;
using MailKit.Security;
using MimeKit;

public class EmailSender : IEmailSender
{
    private readonly SmtpOptions _options;

    public async Task SendAsync(
        string to, string subject, string htmlBody, CancellationToken ct)
    {
        var message = new MimeMessage();

        message.From.Add(new MailboxAddress(
            _options.SenderName, _options.SenderEmail));
        message.To.Add(MailboxAddress.Parse(to));
        message.Subject = subject;

        var builder = new BodyBuilder
        {
            HtmlBody = htmlBody,
            TextBody = StripHtml(htmlBody)
        };

        message.Body = builder.ToMessageBody();

        using var client = new SmtpClient();

        await client.ConnectAsync(
            _options.Host, _options.Port,
            SecureSocketOptions.StartTls, ct);

        await client.AuthenticateAsync(
            _options.Username, _options.Password, ct);

        await client.SendAsync(message, ct);
        await client.DisconnectAsync(quit: true, ct);
    }
}""")

    note(d, "`TextBody` ni ham qo'shish yaxshi amaliyot:",
         "Ba'zi pochta mijozlari HTML ni ko'rsatmaydi yoki foydalanuvchi "
         "uni o'chirib qo'ygan bo'ladi. Ikkala variantni ham yuborsam, "
         "xat har qanday holatda o'qiladi. Bundan tashqari, faqat HTML "
         "bo'lgan xat spam filtrlarida yuqoriroq ball oladi.")

    h2(d, "3.1 Ilova bilan")

    code(d, """var builder = new BodyBuilder { HtmlBody = html };

// Fayl biriktirish
await builder.Attachments.AddAsync("invoice.pdf", stream, ct);

// HTML ichidagi rasm
var image = builder.LinkedResources.Add("logo.png", logoBytes);
image.ContentId = MimeUtils.GenerateMessageId();

builder.HtmlBody = $@"<img src=""cid:{image.ContentId}"" /> {html}";""")

    h2(d, "3.2 Xavfsiz ulanish turlari")

    table(d, ["Variant", "Port", "Qanday ishlaydi"],
          [["`StartTls`", "587", "Oddiy ulanish, keyin shifrlashga o'tadi"],
           ["`SslOnConnect`", "465", "Darhol shifrlangan ulanish"],
           ["`None`", "25", "Shifrlanmagan — ishlatilmaydi"],
           ["`Auto`", "—", "Server imkoniyatiga qarab tanlaydi"]],
          widths=[3.4, 2.4, 9.7])

    # ───────────────────────────────────────────
    h1(d, "4. Fon vazifasi sifatida yuborish")

    note(d, "Xatni so'rov ichida yubormaslik kerak:",
         "SMTP serveri sekin javob berishi yoki umuman javob bermasligi "
         "mumkin. Agar men xatni so'rov ichida yuborsam, foydalanuvchi "
         "o'sha vaqt davomida kutadi va ba'zan kutish vaqti tugab, "
         "butun amal muvaffaqiyatsiz bo'ladi — garchi asosiy ish "
         "bajarilgan bo'lsa ham.")

    code(d, """// Navbatga qo'yish
public async Task<IActionResult> Register(RegisterDto dto, CancellationToken ct)
{
    var user = await _users.CreateAsync(dto, ct);

    // Xat fon vazifasida yuboriladi
    _backgroundJobs.Enqueue<IEmailSender>(sender =>
        sender.SendWelcomeAsync(user.Email, CancellationToken.None));

    return Ok();
}""")

    code(d, """// Yoki outbox orqali
_db.OutboxMessages.Add(new OutboxMessage
{
    Type = "SendWelcomeEmail",
    Payload = JsonSerializer.Serialize(new { user.Email, user.FullName })
});

await _db.SaveChangesAsync(ct);   // foydalanuvchi va xabar atomar""")

    # ───────────────────────────────────────────
    h1(d, "5. Xat qabul qilish")

    h2(d, "5.1 POP3")

    code(d, """using MailKit.Net.Pop3;

using var client = new Pop3Client();

await client.ConnectAsync("pop.example.com", 995,
    SecureSocketOptions.SslOnConnect, ct);
await client.AuthenticateAsync(username, password, ct);

for (int i = 0; i < client.Count; i++)
{
    var message = await client.GetMessageAsync(i, ct);

    Console.WriteLine($"Kimdan: {message.From}");
    Console.WriteLine($"Mavzu: {message.Subject}");
    Console.WriteLine($"Sana: {message.Date}");

    foreach (var attachment in message.Attachments)
    {
        if (attachment is MimePart part)
        {
            await using var file = File.Create(part.FileName);
            await part.Content.DecodeToAsync(file, ct);
        }
    }
}

await client.DisconnectAsync(quit: true, ct);""")

    h2(d, "5.2 IMAP — moslashuvchanroq")

    code(d, """using MailKit;
using MailKit.Net.Imap;
using MailKit.Search;

using var client = new ImapClient();

await client.ConnectAsync("imap.example.com", 993,
    SecureSocketOptions.SslOnConnect, ct);
await client.AuthenticateAsync(username, password, ct);

var inbox = client.Inbox;
await inbox.OpenAsync(FolderAccess.ReadWrite, ct);

// O'qilmagan xatlarni qidirish
var uids = await inbox.SearchAsync(SearchQuery.NotSeen, ct);

foreach (var uid in uids)
{
    var message = await inbox.GetMessageAsync(uid, ct);
    await ProcessAsync(message, ct);

    // O'qilgan deb belgilash
    await inbox.AddFlagsAsync(uid, MessageFlags.Seen, silent: true, ct);
}

await client.DisconnectAsync(quit: true, ct);""")

    note(d, "IMAP ning afzalligi aniq ko'rinadi:",
         "Men serverda qidiruv yozaman — \"o'qilmaganlar\", \"shu "
         "sanadan keyin\", \"shu jo'natuvchidan\". POP3 da esa hamma "
         "xatni yuklab olib, keyin o'zim filtrlashim kerak. Minglab "
         "xat bo'lsa, bu farq juda sezilarli.")

    code(d, """// Murakkab qidiruv
var query = SearchQuery.NotSeen
    .And(SearchQuery.FromContains("noreply@bank.uz"))
    .And(SearchQuery.DeliveredAfter(DateTime.UtcNow.AddDays(-7)));

var uids = await inbox.SearchAsync(query, ct);""")

    # ───────────────────────────────────────────
    h1(d, "6. Amaliy masalalar")

    h2(d, "6.1 Spam filtriga tushmaslik")

    bullets(d, [
        "SPF, DKIM va DMARC yozuvlarini DNS da sozlash.",
        "Jo'natuvchi manzil domeni haqiqiy bo'lishi.",
        "Matn versiyasini ham qo'shish.",
        "Obunani bekor qilish havolasini ko'rsatish.",
        "Katta hajmli yuborishda maxsus xizmatdan foydalanish.",
    ])

    note(d, "O'z serveringizdan ommaviy xat yubormaslik kerak:",
         "Yangi IP manzil obro'siz bo'ladi va xatlar spam ga tushadi. "
         "Obro' yig'ish oylar talab qiladi. Shuning uchun ommaviy "
         "yuborish uchun maxsus xizmatlar ishlatiladi — ular "
         "allaqachon ishonchli IP larga ega.")

    h2(d, "6.2 Sinov muhitida")

    code(d, """// Development da xatni konsolga chiqarish
if (builder.Environment.IsDevelopment())
    builder.Services.AddSingleton<IEmailSender, ConsoleEmailSender>();
else
    builder.Services.AddSingleton<IEmailSender, SmtpEmailSender>();""")

    code(d, """# Yoki lokal SMTP sinov serveri
docker run -d -p 1080:1080 -p 1025:1025 maildev/maildev""")

    note(d, "`maildev` kabi vosita juda qulay:",
         "U SMTP serverini taqlid qiladi va kelgan xatlarni brauzerda "
         "ko'rsatadi. Shunday qilib men HTML shablonni haqiqiy "
         "ko'rinishda tekshiraman, lekin hech kimga xat ketmaydi. "
         "Tasodifan mijozga sinov xati yuborish xavfi butunlay "
         "yo'qoladi.")

    h2(d, "6.3 Shablonlar")

    code(d, """// Razor shablonlarini HTML ga aylantirish
public async Task<string> RenderAsync<TModel>(string view, TModel model)
{
    var html = await _razorRenderer.RenderAsync(view, model);
    return html;
}

await _email.SendAsync(user.Email, "Xush kelibsiz",
    await RenderAsync("Emails/Welcome", new WelcomeModel(user.FullName)),
    ct);""")

    # ───────────────────────────────────────────
    h1(d, "7. Xatoliklarni qayta ishlash")

    code(d, """try
{
    await client.ConnectAsync(host, port, SecureSocketOptions.StartTls, ct);
    await client.AuthenticateAsync(username, password, ct);
    await client.SendAsync(message, ct);
}
catch (AuthenticationException)
{
    _logger.LogError("SMTP autentifikatsiyasi muvaffaqiyatsiz");
    throw;
}
catch (SmtpCommandException ex)
{
    _logger.LogError("SMTP xatosi: {Code} — {Message}",
        ex.StatusCode, ex.Message);
    throw;
}
catch (SmtpProtocolException ex)
{
    _logger.LogError(ex, "SMTP protokol xatosi");
    throw;
}
finally
{
    if (client.IsConnected)
        await client.DisconnectAsync(quit: true, ct);
}""")

    # ───────────────────────────────────────────
    h1(d, "8. Xulosa")

    bullets(d, [
        "SMTP yuborish, POP3 yuklab olish, IMAP serverdan boshqarish "
        "uchun.",
        "`System.Net.Mail.SmtpClient` eskirgan — `MailKit` tavsiya "
        "etiladi.",
        "`StartTls` (587) yoki `SslOnConnect` (465) ishlatiladi; "
        "shifrlanmagan ulanish qabul qilinmaydi.",
        "HTML bilan birga matn versiyasini ham yuborish kerak.",
        "Xatni so'rov ichida emas, fon vazifasida yuborish lozim.",
        "IMAP serverda qidirish imkonini beradi — bu POP3 dan "
        "sezilarli afzallik.",
        "Spam filtridan o'tish uchun SPF, DKIM va DMARC sozlanishi "
        "kerak.",
        "Sinov muhitida `maildev` kabi taqlid server ishlatish "
        "xavfsizroq.",
    ])

    sources(d, [
        ("MailKit — rasmiy hujjat",
         "https://github.com/jstedfast/MailKit"),
        ("SmtpClient Class — .NET API (obsolete note)",
         "https://learn.microsoft.com/en-us/dotnet/api/system.net.mail.smtpclient"),
        ("RFC 5321 — Simple Mail Transfer Protocol",
         "https://www.rfc-editor.org/rfc/rfc5321"),
        ("RFC 3501 — Internet Message Access Protocol",
         "https://www.rfc-editor.org/rfc/rfc3501"),
    ])
