# SignalR — Real-time Communication — Middle D

## 1. Nima? (Ta'rif)

**SignalR** — ASP.NET Core'da **real-time, ikki tomonlama**
(server↔client) aloqani soddalashtiruvchi kutubxona. **Hub** —
SignalR'ning markaziy klassi, client va server o'rtasida metod
chaqiruvlarini boshqaradi.

## 2. Nima uchun kerak?

Oddiy HTTP — faqat client so'rov yuborganda ishlaydi (server o'zi
"boshlab" xabar yubora olmaydi). Chat, live dashboard, notification
kabi funksiyalar uchun **server client'ga o'zi murojaat qilishi**
kerak — bu SignalR'ning asosiy vazifasi.

## 3. Ichida nima sodir bo'ladi? (Mexanizm)

### 3.1 Transport turlari — SignalR qanday tanlaydi

```
SignalR — AVTOMATIK ravishda ENG YAXSHI mavjud transport'ni tanlaydi:

1. WebSocket    — ENG YAXSHI (ikki tomonlama, doimiy ulanish)
2. Server-Sent Events (SSE) — faqat SERVER → CLIENT (fallback)
3. Long Polling — ENG YOMON, lekin ENG universal (eski brauzer/proxy)

Client birinchi so'rovda "negotiate" so'rov yuboradi — server
qo'llab-quvvatlaydigan transportlarni aytadi, client ENG YAXSHISINI
tanlaydi.
```

### 3.2 Hub — asosiy mexanizm

```csharp
public class ChatHub : Hub
{
    // Client → Server chaqiruv
    public async Task SendMessage(string user, string message)
    {
        // Server → BARCHA ulangan client'larga yuborish
        await Clients.All.SendAsync("ReceiveMessage", user, message);
    }
}
```

```
Client (JS)                          Server (ChatHub)
  connection.invoke("SendMessage",  ──────►  SendMessage(user, message) bajariladi
    "Orzibek", "Salom")
                                     ◄────── Clients.All.SendAsync("ReceiveMessage", ...)
  connection.on("ReceiveMessage",
    (user, msg) => { ... })          ← BARCHA ulangan client'lar OLADI
```

### 3.3 Groups — foydalanuvchilarni guruhlash

```csharp
public class NotificationHub : Hub
{
    public async Task JoinDepartment(string departmentId)
    {
        await Groups.AddToGroupAsync(Context.ConnectionId, $"dept-{departmentId}");
    }
}

// Boshqa joydan (masalan Controller/Handler'dan) — faqat shu guruhga xabar
await _hubContext.Clients.Group("dept-5").SendAsync("NewAnnouncement", data);
```

Guruhlar — "faqat IT bo'limi xodimlariga bildirishnoma" kabi
**segmentlangan** yuborish uchun ishlatiladi.

### 3.4 Connection ID

Har bir ulanish (brauzer tab, mobil ilova instansi) — noyob
`ConnectionId` oladi. Bitta foydalanuvchi bir nechta qurilmadan
ulangan bo'lsa — bir nechta `ConnectionId`ga ega bo'ladi.

### 3.5 Typed Hub — `IHubContext<T>`

```csharp
public interface IChatClient
{
    Task ReceiveMessage(string user, string message);
}

public class ChatHub : Hub<IChatClient> // Typed — compile-time xavfsizlik
{
    public async Task SendMessage(string user, string message)
        => await Clients.All.ReceiveMessage(user, message); // "sehrli string" YO'Q!
}

// Controller/Handler'dan Hub'ga murojaat
public class NotificationService
{
    private readonly IHubContext<ChatHub, IChatClient> _hubContext;
    public NotificationService(IHubContext<ChatHub, IChatClient> hubContext) => _hubContext = hubContext;

    public Task NotifyAsync(string message) => _hubContext.Clients.All.ReceiveMessage("System", message);
}
```

`IHubContext<T>` — Hub'ga **tashqaridan** (masalan MediatR Handler'dan,
BackgroundService'dan) murojaat qilish uchun ishlatiladi (Hub'ning
o'zi faqat client chaqirganda ishlaydi).

## 4. Kod — to'liq sozlash

### Program.cs

```csharp
builder.Services.AddSignalR();

builder.Services.AddCors(options =>
    options.AddPolicy("SignalRPolicy", policy =>
        policy.WithOrigins("https://frontend.example.com")
              .AllowAnyHeader()
              .AllowAnyMethod()
              .AllowCredentials())); // SignalR uchun MAJBURIY (credentials bilan)

var app = builder.Build();
app.UseCors("SignalRPolicy");
app.UseAuthentication();
app.UseAuthorization();

app.MapHub<ChatHub>("/hubs/chat");
```

### Authentication bilan birga

```csharp
[Authorize]
public class ChatHub : Hub
{
    public override async Task OnConnectedAsync()
    {
        var userId = Context.User?.FindFirst(JwtRegisteredClaimNames.Sub)?.Value;
        await Groups.AddToGroupAsync(Context.ConnectionId, $"user-{userId}");
        await base.OnConnectedAsync();
    }
}
```

JWT'ni SignalR bilan ishlatishda — WebSocket handshake'da
`Authorization` header yubora olmaydi, shuning uchun query string
orqali beriladi:

```csharp
builder.Services.AddAuthentication().AddJwtBearer(options =>
{
    options.Events = new JwtBearerEvents
    {
        OnMessageReceived = context =>
        {
            var accessToken = context.Request.Query["access_token"];
            if (!string.IsNullOrEmpty(accessToken) &&
                context.HttpContext.Request.Path.StartsWithSegments("/hubs"))
            {
                context.Token = accessToken;
            }
            return Task.CompletedTask;
        }
    };
});
```

### JavaScript client

```javascript
const connection = new signalR.HubConnectionBuilder()
    .withUrl("/hubs/chat", { accessTokenFactory: () => localStorage.getItem("token") })
    .withAutomaticReconnect()
    .build();

connection.on("ReceiveMessage", (user, message) => {
    console.log(`${user}: ${message}`);
});

await connection.start();
await connection.invoke("SendMessage", "Orzibek", "Salom hammaga!");
```

### C# client

```csharp
var connection = new HubConnectionBuilder()
    .WithUrl("https://api.example.com/hubs/chat")
    .Build();

connection.On<string, string>("ReceiveMessage", (user, message) =>
    Console.WriteLine($"{user}: {message}"));

await connection.StartAsync();
await connection.InvokeAsync("SendMessage", "Orzibek", "Salom!");
```

### Scale-out — Redis backplane

```
Bitta server — barcha ulanishlarni O'ZI boshqaradi. Bir nechta
server (load balanced) bo'lsa — Server-1'dagi client Server-2'dagi
client bilan TO'G'RIDAN aloqa qila OLMAYDI!

Yechim — Redis Backplane:
Server-1 ─┐
Server-2 ─┼── Redis Pub/Sub ── barcha serverlar XABARNI oladi
Server-3 ─┘

builder.Services.AddSignalR().AddStackExchangeRedis("localhost:6379");
```

## 5. Qachon ishlatish kerak?

| Vaziyat | Yechim |
|---|---|
| Chat, live dashboard, notification | SignalR |
| Bir martalik, oddiy so'rov-javob | Oddiy HTTP API |
| Ko'p server (load balanced), real-time | SignalR + Redis Backplane |
| Faqat serverdan client'ga (bir tomonlama stream) | SSE ham yetarli bo'lishi mumkin |

## 6. Muhim nuqtalar

- CORS — SignalR uchun `AllowCredentials()` bilan **aniq** origin
  ko'rsatilishi kerak (`AllowAnyOrigin()` + credentials BIRGA
  ISHLAMAYDI).
- WebSocket — statefull, load balancer **sticky session** yoki Redis
  backplane talab qilishi mumkin.
- `OnDisconnectedAsync` — ulanish uzilganda tozalash (masalan, "online
  users" ro'yxatidan olib tashlash) uchun override qilinadi.

## 7. Imtihon savollari

1. SignalR transport tanlashda qaysi ustuvorlikni (WebSocket → SSE →
   Long Polling) ishlatadi?
2. Hub nima va u client-server aloqasini qanday boshqaradi?
3. `IHubContext<T>` nima uchun kerak — Hub'ning o'zidan farqi nima?
4. Groups nima vazifani bajaradi va qachon ishlatiladi?
5. SignalR bilan JWT autentifikatsiyasini ishlatishda nima uchun
   query string orqali token yuborish kerak bo'ladi?
6. Redis Backplane nima muammoni (ko'p server bilan) hal qiladi?
