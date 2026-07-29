# SMTP Email Yuborish, POP3 Qabul Qilish — Middle D

## 1. Nima? (Ta'rif)

**SMTP (Simple Mail Transfer Protocol)** — email **YUBORISH**
protokoli. **POP3 (Post Office Protocol v3)** va **IMAP** — email
**QABUL QILISH/O'QISH** protokollari.

## 2. Nima uchun kerak?

ERP tizimida — xodim qabul qilinganda xush kelibsiz emaili, parolni
tiklash havolasi, hisobot yuborish kabi vazifalar SMTP orqali amalga
oshiriladi.

## 3. Ichida nima sodir bo'ladi? (Mexanizm)

### 3.1 SMTP protokoli va portlar

```
Port 25   — server-serverga (relay), ISP'lar ko'pincha BLOKLAYDI
Port 587  — Submission — client'dan serverga, STARTTLS bilan (TAVSIYA ETILADI)
Port 465  — SMTPS — boshidanoq SSL/TLS bilan shifrlangan
```

```
Client                          SMTP Server
  │── EHLO client.com ─────────►│
  │◄── 250 OK ──────────────────│
  │── AUTH LOGIN ──────────────►│
  │◄── 334 (username so'raladi) │
  │── (base64 username) ───────►│
  │── MAIL FROM:<a@x.com> ─────►│
  │── RCPT TO:<b@y.com> ───────►│
  │── DATA ────────────────────►│
  │── (email tanasi) ──────────►│
  │── . (yakunlash) ────────────►│
  │◄── 250 Message accepted ────│
```

### 3.2 SmtpClient sozlash

```
⚠️ System.Net.Mail.SmtpClient — .NET'da OBSOLETE deb belgilangan
   (Microsoft MailKit'ni tavsiya qiladi), lekin hali ishlaydi va
   ko'p loyihalarda uchraydi.
```

```csharp
using var client = new SmtpClient("smtp.gmail.com", 587)
{
    EnableSsl = true,
    Credentials = new NetworkCredential("user@gmail.com", appPassword)
};

var message = new MailMessage
{
    From = new MailAddress("user@gmail.com", "ERP System"),
    Subject = "Xush kelibsiz!",
    Body = "<h1>Salom, Orzibek!</h1>",
    IsBodyHtml = true
};
message.To.Add("employee@example.com");
message.CC.Add("hr@example.com");
message.Attachments.Add(new Attachment("contract.pdf"));

await client.SendMailAsync(message);
```

**App Password (Gmail)** — Gmail 2FA yoqilgan hisoblarda oddiy
parol bilan SMTP orqali kirishga RUXSAT BERMAYDI — buning o'rniga
Google Account sozlamalarida **App Password** (16 belgili maxsus
parol) generatsiya qilinadi, faqat shu ilova uchun ishlatiladi va
istalgan vaqt bekor qilinishi mumkin (asosiy parolni oshkor
qilmasdan).

### 3.3 POP3 protokoli

```
Port 110  — oddiy (shifrlanmagan)
Port 995  — POP3S (SSL/TLS bilan)
```

```
Client                          POP3 Server
  │── USER user@example.com ───►│
  │◄── +OK ─────────────────────│
  │── PASS parol ───────────────►│
  │◄── +OK ─────────────────────│
  │── STAT ─────────────────────►│  "Nechta xat bor?"
  │◄── +OK 3 1024 ──────────────│  3 ta xat, 1024 bayt
  │── RETR 1 ───────────────────►│  1-chi xatni OL
  │◄── (xat matni) ─────────────│
  │── DELE 1 ───────────────────►│  Serverdan O'CHIRISH belgisi
  │── QUIT ─────────────────────►│  Yakunlash (shu yerda haqiqatda o'chadi)
```

**POP3 xarakteristikasi:** xat ODATDA serverdan **client'ga
KO'CHIRILADI va serverdan O'CHIRILADI** (yoki sozlamaga qarab
nusxasi qoladi) — ko'p qurilmada bir xil pochta ko'rish uchun mos
EMAS.

### 3.4 POP3 vs IMAP

| | POP3 | IMAP |
|---|---|---|
| Xat qayerda saqlanadi | Client (yuklab olingach) | Server (doim serverda) |
| Ko'p qurilma sinxronizatsiyasi | ❌ Yo'q | ✅ Bor |
| Papka strukturasi | ❌ Yo'q (faqat Inbox) | ✅ Bor |
| Oflayn ishlash | ✅ Yaxshi | Cheklangan |

Zamonaviy email client'lar (Gmail, Outlook) — deyarli har doim
**IMAP** ishlatadi, POP3 — legacy tizimlar yoki oddiy skript uchun.

### 3.5 TcpClient bilan qo'lda POP3 (protokolni tushunish uchun)

```csharp
using var client = new TcpClient("pop.example.com", 110);
using var stream = client.GetStream();
using var reader = new StreamReader(stream);
using var writer = new StreamWriter(stream) { AutoFlush = true };

Console.WriteLine(await reader.ReadLineAsync()); // +OK server ready

await writer.WriteLineAsync("USER user@example.com");
Console.WriteLine(await reader.ReadLineAsync());

await writer.WriteLineAsync("PASS mypassword");
Console.WriteLine(await reader.ReadLineAsync());

await writer.WriteLineAsync("STAT");
Console.WriteLine(await reader.ReadLineAsync());

await writer.WriteLineAsync("QUIT");
```

### 3.6 MailKit — zamonaviy yondashuv

```bash
dotnet add package MailKit
```

```csharp
// SMTP yuborish — MailKit bilan
using var message = new MimeMessage();
message.From.Add(new MailboxAddress("ERP System", "user@gmail.com"));
message.To.Add(new MailboxAddress("Orzibek", "employee@example.com"));
message.Subject = "Xush kelibsiz";
message.Body = new TextPart("html") { Text = "<h1>Salom!</h1>" };

using var smtp = new MailKit.Net.Smtp.SmtpClient();
await smtp.ConnectAsync("smtp.gmail.com", 587, MailKit.Security.SecureSocketOptions.StartTls);
await smtp.AuthenticateAsync("user@gmail.com", appPassword);
await smtp.SendAsync(message);
await smtp.DisconnectAsync(true);

// IMAP o'qish — MailKit bilan
using var imap = new MailKit.Net.Imap.ImapClient();
await imap.ConnectAsync("imap.gmail.com", 993, MailKit.Security.SecureSocketOptions.SslOnConnect);
await imap.AuthenticateAsync("user@gmail.com", appPassword);
await imap.Inbox.OpenAsync(MailKit.FolderAccess.ReadOnly);

for (int i = 0; i < imap.Inbox.Count; i++)
{
    var msg = await imap.Inbox.GetMessageAsync(i);
    Console.WriteLine(msg.Subject);
}
```

MailKit — POP3, IMAP va SMTP uchun **yagona, zamonaviy** kutubxona —
`System.Net.Mail` o'rniga TAVSIYA ETILADIGAN yechim.

### 3.7 IEmailService pattern

```csharp
public interface IEmailService
{
    Task SendAsync(string to, string subject, string htmlBody);
}

public class SmtpEmailService : IEmailService
{
    private readonly EmailSettings _settings;
    public SmtpEmailService(IOptions<EmailSettings> options) => _settings = options.Value;

    public async Task SendAsync(string to, string subject, string htmlBody)
    {
        using var message = new MimeMessage();
        message.From.Add(new MailboxAddress(_settings.SenderName, _settings.SenderEmail));
        message.To.Add(MailboxAddress.Parse(to));
        message.Subject = subject;
        message.Body = new TextPart("html") { Text = htmlBody };

        using var smtp = new MailKit.Net.Smtp.SmtpClient();
        await smtp.ConnectAsync(_settings.Host, _settings.Port, MailKit.Security.SecureSocketOptions.StartTls);
        await smtp.AuthenticateAsync(_settings.SenderEmail, _settings.Password);
        await smtp.SendAsync(message);
        await smtp.DisconnectAsync(true);
    }
}

// DI ga qo'shish
builder.Services.Configure<EmailSettings>(builder.Configuration.GetSection("Email"));
builder.Services.AddSingleton<IEmailService, SmtpEmailService>();
```

**Nima uchun Singleton?** `SmtpClient` — har chaqiruvda YANGI
ulanish ochadi/yopadi (`using` bilan), shuning uchun `IEmailService`
implementatsiyasining o'zi **holatsiz** (stateless) — Singleton
qilib DI overhead'ini kamaytirish xavfsiz. Agar ichida DbContext
kabi Scoped bog'liqlik bo'lsa — Scoped qilish kerak bo'lardi.

## 4. Kod — HTML email va attachment

```csharp
var builder = new BodyBuilder
{
    HtmlBody = "<h1>Hisobot</h1><p>Ilova qilingan faylni ko'ring.</p>"
};
builder.Attachments.Add("report.pdf", File.ReadAllBytes("report.pdf"),
    ContentType.Parse("application/pdf"));

message.Body = builder.ToMessageBody();
```

## 5. Qachon ishlatish kerak?

| Vaziyat | Yechim |
|---|---|
| Email yuborish (bildirishnoma, hisobot) | SMTP (MailKit) |
| Ko'p qurilmada bir xil pochta ko'rish | IMAP |
| Oddiy, bir marta yuklab olish | POP3 |
| Yangi loyiha | MailKit (`System.Net.Mail` emas) |

## 6. Muhim nuqtalar

- Gmail'da App Password — 2FA yoqilganda MAJBURIY, asosiy parolni
  uchinchi tomon ilovalarga bermaslik uchun xavfsizlik chorasi.
- SMTP credential'larni HECH QACHON kodga hardcode qilmang —
  `appsettings.json` + Environment variable/Secret Manager.
- Email yuborish — **asosiy jarayonni bloklamasligi** kerak (masalan,
  buyurtma yaratilgandan keyin email RabbitMQ orqali **asinxron**
  yuborilishi tavsiya etiladi, HTTP so'rovni ushlab turmasin).

## 7. Imtihon savollari

1. SMTP va POP3 orasidagi asosiy vazifa farqi nima?
2. Port 587 va 465 orasidagi farq nima?
3. POP3 va IMAP orasidagi farqni ko'p qurilmali foydalanish
   nuqtai nazaridan tushuntiring.
4. Gmail App Password nima uchun kerak?
5. Nima uchun `System.Net.Mail.SmtpClient` o'rniga MailKit tavsiya
   etiladi?
6. `IEmailService`ni Singleton qilib ro'yxatdan o'tkazish qachon
   xavfsiz, qachon emas?
