# RabbitMQ — Message Broker, Publisher va Consumer — Middle D

## 1. Nima? (Ta'rif)

**Message Broker** — turli servislar (yoki ilovalar) orasida
**asinxron** xabar almashinuvini ta'minlovchi vositachi tizim.
**RabbitMQ** — **AMQP (Advanced Message Queuing Protocol)** standarti
asosida ishlaydigan, eng ko'p ishlatiladigan open-source message
broker.

**Asosiy tushunchalar:**
- **Producer (Publisher)** — xabar yuboruvchi ilova
- **Exchange** — xabarni qabul qilib, qaysi Queue(lar)ga
  yo'naltirishni hal qiluvchi "yo'l ayirg'ich"
- **Queue** — xabarlar navbat kutib turadigan bufer
- **Consumer** — Queue'dan xabarni olib, qayta ishlovchi ilova
- **Binding** — Exchange va Queue orasidagi "bog'lanish qoidasi"
- **Routing Key** — xabar qaysi yo'nalishga tegishli ekanini
  bildiruvchi teg

## 2. Nima uchun kerak? (Muammo va yechim)

To'g'ridan-to'g'ri HTTP orqali microservicelar bir-birini chaqirsa
(**synchronous** aloqa) — quyidagi muammolar yuzaga keladi:

```
❌ Synchronous (to'g'ridan HTTP) aloqa:
   OrderService → (HTTP so'rov) → EmailService

   Agar EmailService ISHLAMASA yoki SEKIN javob bersa:
   → OrderService HAM kutib qoladi (yoki xato qaytaradi)
   → Buyurtma yaratish MUVAFFAQIYATSIZ bo'lib qolishi mumkin,
     GARCHI email yuborish — asosiy jarayon uchun KRITIK bo'lmasa ham!
```

```
✅ Asynchronous (Message Broker orqali) aloqa:
   OrderService → (xabar yuboradi, JAVOB KUTMAYDI) → RabbitMQ → EmailService

   EmailService ISHLAMASA — xabar Queue'da KUTIB TURADI, EmailService
   qayta ishga tushganda uni QAYTA ISHLAYDI. OrderService BUYURTMANI
   MUVAFFAQIYATLI YARATADI, email keyinroq yuborilsa ham bo'ladi.
```

**Real hayot analogiyasi:** Message Broker — bu **pochta bo'limi**.
Siz (Producer) xatni pochta bo'limiga (Exchange) topshirasiz, u
manzilga qarab (Routing Key) tegishli pochta qutisiga (Queue)
joylaydi. Qabul qiluvchi (Consumer) o'z vaqtida kelib qutisini
tekshiradi — siz uning **uyida turib kutib turishingiz** shart emas.

Agar Message Broker bo'lmaganida — har bir servis boshqa servisning
**doim ishlab turishiga** bog'liq bo'lib qolardi (tight coupling),
va yuk ko'paysa (masalan minglab buyurtma bir vaqtda) — sistemani
**gorizontal masshtablash** qiyinlashardi.

### RabbitMQ vs Kafka vs Azure Service Bus

| | RabbitMQ | Kafka | Azure Service Bus |
|---|---|---|---|
| Model | Traditional message broker (push) | Distributed event log (pull) | Managed cloud broker |
| Protokol | AMQP | O'ziga xos (TCP asosida) | AMQP/HTTPS |
| Xabar tartibi | Queue ichida FIFO | Partition ichida FIFO | Queue ichida FIFO |
| Throughput | Yuqori (yuz minglab/soniya) | JUDA yuqori (millionlab/soniya) | O'rtacha (cloud SLA cheklovi) |
| Xabar saqlash | Iste'mol qilingach o'chadi (odatda) | Belgilangan muddat davomida SAQLANADI | Iste'mol qilingach o'chadi |
| Ishlatish holati | Task queue, RPC, kompleks routing | Event streaming, log aggregation, katta hajm | Azure ekotizimida, enterprise integratsiya |
| Murakkab routing (Topic, Header) | ✅ Kuchli | ❌ Cheklangan (faqat partition) | ✅ O'rtacha |

RabbitMQ — **"vazifa navbati" (task queue)** va murakkab routing
(masalan turli mikroservislarga turli shartlar asosida yo'naltirish)
uchun ideal. Kafka — **katta hajmdagi event stream**larni (log,
analytics) saqlash va qayta ishlash uchun ko'proq mos.

## 3. Ichida nima sodir bo'ladi? (Mexanizm)

### 3.1 AMQP protokoli

**AMQP (Advanced Message Queuing Protocol)** — RabbitMQ tayanadigan
**tarmoq protokoli** (xuddi HTTP — web uchun bo'lgani kabi). AMQP —
binar protokol, TCP ustida ishlaydi (default port **5672**).

```
Client (Producer/Consumer)  ⇄  AMQP protokoli  ⇄  RabbitMQ Server (Broker)

TCP Connection (uzoq muddatli, "og'ir" resurs)
    │
    └── Channel 1 (yengil, virtual "yo'lak" — Connection ichida)
    └── Channel 2
    └── Channel 3 ...
```

**Connection** — TCP darajasidagi ulanish (qimmat — handshake,
autentifikatsiya). **Channel** — Connection ICHIDA ochiladigan
yengil "virtual ulanish" — har bir operatsiya (publish, consume)
odatda o'z Channel'ida bajariladi, bir nechta Channel bitta
Connection'ni **bo'lishadi** (multiplexing — xuddi HTTP/2 kabi).

### 3.2 RabbitMQ arxitekturasi — to'liq oqim

```
┌──────────┐        ┌──────────┐        ┌─────────┐        ┌──────────┐
│ Producer │──────► │ Exchange │──────► │  Queue  │──────► │ Consumer │
└──────────┘ publish└──────────┘ binding └─────────┘ consume└──────────┘
                          │  routing key       ▲
                          │                    │
                          └──── Binding ───────┘
```

**Muhim tushuncha:** Producer **hech qachon** to'g'ridan Queue'ga
xabar yubormaydi! U har doim **Exchange**'ga yuboradi, Exchange esa
**Binding** qoidalari asosida xabarni tegishli Queue(lar)ga
yo'naltiradi.

### 3.3 Exchange turlari

**Direct Exchange** — routing key **aniq mos kelsa** xabar yuboriladi:

```
Producer → Exchange (Direct) → routing_key="order.created"
                                    │
                    ┌───────────────┼───────────────┐
                    ▼               ▼               ▼
              Queue A          Queue B          Queue C
          binding key:      binding key:     binding key:
          "order.created"   "order.updated"  "order.created"
              ✅ MOS            ❌ MOS EMAS      ✅ MOS

Natija: Xabar Queue A va Queue C ga yetkaziladi (ikkalasi ham
        "order.created" bilan bog'langan)
```

**Fanout Exchange** — routing key'ga E'TIBOR BERMASDAN, BOG'LANGAN
BARCHA Queue'larga xabar yuboriladi (broadcast):

```
Producer → Exchange (Fanout) → xabar
                    │
        ┌───────────┼───────────┐
        ▼           ▼           ▼
    Queue A     Queue B     Queue C
    (BARCHASI xabarni oladi, routing key muhim emas)
```

Fanout — masalan "yangi xodim qo'shildi" hodisasi haqida BIR VAQTDA
Email service, Audit service, Notification service'ga xabar berish
uchun ideal.

**Topic Exchange** — routing key **pattern** (wildcard) orqali mos
keladi:

```
Routing key format: "so'z1.so'z2.so'z3"
* — bitta so'zni almashtiradi
# — nol yoki bir nechta so'zni almashtiradi

Producer routing_key = "erp.employee.created"

Queue A binding: "erp.employee.*"     → ✅ MOS
Queue B binding: "erp.#"               → ✅ MOS (# — hammasini qamraydi)
Queue C binding: "erp.department.*"    → ❌ MOS EMAS
```

Topic — "faqat `employee` bilan bog'liq BARCHA hodisalarni" yoki
"faqat `.created` bilan tugaydigan hodisalarni" kabi **moslashuvchan
filtrlash** kerak bo'lganda ishlatiladi.

**Headers Exchange** — routing key o'rniga message **header**laridagi
key-value juftliklar asosida yo'naltiriladi (kamdan-kam ishlatiladi,
murakkabroq shartlar uchun).

### 3.4 Message Lifecycle — to'liq jarayon

```
1. PUBLISH — Producer Exchange'ga xabar yuboradi (routing key bilan)

2. ROUTE — Exchange, Binding qoidalari asosida xabarni Queue(lar)ga
   yo'naltiradi

3. STORE — Queue xabarni SAQLAYDI (agar Durable bo'lsa — diskga ham
   yoziladi, server qayta ishga tushsa ham YO'QOLMAYDI)

4. DELIVER — Consumer ulangan bo'lsa, xabar UZATILADI (yoki Consumer
   keyinroq ulanguncha Queue'da KUTIB TURADI)

5. ACK (Acknowledgment) — Consumer xabarni MUVAFFAQIYATLI qayta
   ishlaganini tasdiqlaydi

6. Broker — ACK olgach, xabarni Queue'dan O'CHIRADI
   (agar ACK KELMASA — xabar Queue'ga QAYTARILADI, qayta yetkaziladi!)
```

### 3.5 Message Acknowledgment — manual vs automatic

```
Automatic ACK (autoAck: true):
  Broker xabarni Consumer'ga YUBORGAN ZAHOTI — "yetkazildi" deb
  hisoblab, Queue'dan O'CHIRIB YUBORADI.

  ❌ XAVF: Agar Consumer xabarni qayta ishlash JARAYONIDA (masalan,
     kod xatosi tufayli) YIQILIB TUSHSA — xabar YO'QOLGAN bo'ladi!
     (Broker allaqachon "yetkazildi" deb hisoblagan)

Manual ACK (autoAck: false):
  Consumer xabarni OLADI, QAYTA ISHLAYDI, va FAQAT MUVAFFAQIYATLI
  tugagach — channel.BasicAck() ni QO'LDA chaqiradi.

  ✅ XAVFSIZ: Agar Consumer YIQILIB TUSHSA (ACK chaqirilmasdan) —
     Broker buni SEZADI (connection uzilgani orqali) va xabarni
     BOSHQA Consumer'ga (yoki qayta ulanganda O'ZIGA) QAYTA YUBORADI
```

```
❌ ANTI-PATTERN: autoAck: true — production'da JIDDIY xabar yo'qotish
   xavfi tug'diradi, faqat "xabar yo'qolsa ham OK" holatlarida
   (masalan, metrics) ishlatiladi.

✅ TAVSIYA: Har doim manual ACK, va xabarni FAQAT DB'ga
   MUVAFFAQIYATLI yozilgandan KEYIN ACK qilish.
```

### 3.6 Durable Queue va Persistent Message

```
Durable Queue = false (default):
  RabbitMQ server QAYTA ISHGA TUSHSA — Queue'ning O'ZI HAM
  YO'QOLADI (barcha xabarlari bilan birga)!

Durable Queue = true:
  Queue METADATASI diskga yoziladi — server qayta ishga tushsa,
  Queue QAYTA YARATILADI (lekin ICHIDAGI xabarlar — bu FAQAT
  Persistent Message bilan birga ishlaydi!)

Persistent Message (deliveryMode: 2):
  Xabarning O'ZI HAM diskka yoziladi — server qayta ishga tushganda
  Queue ICHIDAGI xabarlar HAM SAQLANIB QOLADI

⚠️ Ikkalasi BIRGA ishlatilishi kerak — faqat Durable Queue,
   Persistent bo'lmagan xabarlarni SAQLAB QOLA OLMAYDI!
```

### 3.7 Dead Letter Exchange (DLX) — qayta ishlab bo'lmaydigan xabarlar

```
Consumer xabarni QAYTA-QAYTA qayta ishlashga urinadi, lekin doim
XATO chiqadi (masalan, ma'lumot noto'g'ri formatda).

Yechim — Dead Letter Exchange:

Queue "orders" ─── (DLX sozlangan) ───► Exchange "orders.dlx"
                                              │
                                              ▼
                                       Queue "orders.failed"

Xabar quyidagi holatlarda DLX'ga YO'NALTIRILADI:
  1. Consumer uni REJECT qildi (requeue=false bilan)
  2. Message TTL tugadi
  3. Queue "max-length" chegarasiga yetdi (eng eskisi chiqarib
     tashlanadi)
```

Bu — xabarlarni **butunlay yo'qotmasdan**, muammoli xabarlarni
alohida joyga (keyinchalik qo'lda tekshirish/tuzatish uchun)
yig'ish imkonini beradi.

### 3.8 Message TTL (Time To Live)

```csharp
var args = new Dictionary<string, object>
{
    { "x-message-ttl", 60000 } // 60 soniya — shu vaqtdan keyin xabar
                                 // AVTOMATIK o'chiriladi (yoki DLX'ga o'tadi)
};
channel.QueueDeclare("orders", durable: true, exclusive: false,
    autoDelete: false, arguments: args);
```

## 4. Kod — to'liq implementatsiya (RabbitMQ.Client)

### NuGet paketlar

```bash
dotnet add package RabbitMQ.Client --version 6.8.1
```

### appsettings.json

```json
{
  "RabbitMQ": {
    "HostName": "localhost",
    "Port": 5672,
    "UserName": "guest",
    "Password": "guest",
    "VirtualHost": "/",
    "QueueName": "employee-events"
  }
}
```

### Connection va Channel — nima uchun `IConnection` Singleton bo'lishi kerak

```
IConnection — TCP ulanishni ifodalaydi (QIMMAT resurs — handshake,
autentifikatsiya). Har so'rovda YANGI Connection ochish — TARMOQ
resurslarini ISROF qiladi va SEKIN.

✅ IConnection — SINGLETON (butun ilova umri davomida BITTA marta
   ochiladi)
✅ IModel (Channel) — odatda har operatsiya yoki SCOPED darajada
   yaratiladi (yengil, tez ochiladi/yopiladi)
```

```csharp
public interface IRabbitMqConnectionFactory
{
    IConnection CreateConnection();
}

public class RabbitMqConnectionFactory : IRabbitMqConnectionFactory, IDisposable
{
    private readonly ConnectionFactory _factory;
    private IConnection? _connection;
    private readonly object _lock = new();

    public RabbitMqConnectionFactory(IConfiguration config)
    {
        _factory = new ConnectionFactory
        {
            HostName = config["RabbitMQ:HostName"]!,
            Port = int.Parse(config["RabbitMQ:Port"]!),
            UserName = config["RabbitMQ:UserName"]!,
            Password = config["RabbitMQ:Password"]!,
            VirtualHost = config["RabbitMQ:VirtualHost"]!,
            AutomaticRecoveryEnabled = true,       // ✅ Ulanish uzilsa AVTOMATIK qayta ulanadi
            NetworkRecoveryInterval = TimeSpan.FromSeconds(5)
        };
    }

    public IConnection CreateConnection()
    {
        lock (_lock)
        {
            if (_connection is null || !_connection.IsOpen)
                _connection = _factory.CreateConnection();

            return _connection;
        }
    }

    public void Dispose() => _connection?.Dispose();
}

// Program.cs
builder.Services.AddSingleton<IRabbitMqConnectionFactory, RabbitMqConnectionFactory>();
```

### Publisher — xabar yuborish (BasicPublish)

```csharp
public interface IEmployeeEventPublisher
{
    void PublishEmployeeCreated(EmployeeCreatedEvent evt);
}

public class EmployeeEventPublisher : IEmployeeEventPublisher
{
    private readonly IRabbitMqConnectionFactory _connectionFactory;
    private const string ExchangeName = "employee-events-exchange";

    public EmployeeEventPublisher(IRabbitMqConnectionFactory connectionFactory)
        => _connectionFactory = connectionFactory;

    public void PublishEmployeeCreated(EmployeeCreatedEvent evt)
    {
        using var connection = _connectionFactory.CreateConnection();
        using var channel = connection.CreateModel();

        channel.ExchangeDeclare(ExchangeName, ExchangeType.Topic, durable: true);

        channel.QueueDeclare(
            queue: "employee-created-queue",
            durable: true,       // Server qayta ishga tushsa ham Queue saqlanadi
            exclusive: false,    // Boshqa connection'lar ham ishlata oladi
            autoDelete: false,   // Consumer uzilganda Queue O'CHIRILMAYDI
            arguments: null);

        channel.QueueBind("employee-created-queue", ExchangeName, "employee.created");

        var json = JsonSerializer.Serialize(evt);
        var body = Encoding.UTF8.GetBytes(json);

        var properties = channel.CreateBasicProperties();
        properties.Persistent = true;      // ✅ Xabar diskka yoziladi (Durable Queue bilan birga)
        properties.ContentType = "application/json";
        properties.MessageId = Guid.NewGuid().ToString();

        channel.BasicPublish(
            exchange: ExchangeName,
            routingKey: "employee.created",
            basicProperties: properties,
            body: body);
    }
}

public record EmployeeCreatedEvent(int Id, string FullName, DateTime CreatedAt);
```

### Consumer — `EventingBasicConsumer` (sinxron uslub)

```csharp
public class EmployeeCreatedConsumer
{
    private readonly IRabbitMqConnectionFactory _connectionFactory;

    public void StartConsuming()
    {
        var connection = _connectionFactory.CreateConnection();
        var channel = connection.CreateModel();

        channel.ExchangeDeclare("employee-events-exchange", ExchangeType.Topic, durable: true);
        channel.QueueDeclare("employee-created-queue", durable: true, exclusive: false, autoDelete: false);
        channel.QueueBind("employee-created-queue", "employee-events-exchange", "employee.created");

        channel.BasicQos(prefetchSize: 0, prefetchCount: 1, global: false);
        // prefetchCount: 1 — Consumer BIR VAQTDA faqat 1 ta xabarni oladi
        // (ACK qilmaguncha KEYINGISI YUBORILMAYDI — load balancing uchun muhim)

        var consumer = new EventingBasicConsumer(channel);
        consumer.Received += (model, ea) =>
        {
            try
            {
                var json = Encoding.UTF8.GetString(ea.Body.ToArray());
                var evt = JsonSerializer.Deserialize<EmployeeCreatedEvent>(json);

                ProcessEvent(evt!); // Biznes mantiq — masalan email yuborish

                channel.BasicAck(ea.DeliveryTag, multiple: false); // ✅ Muvaffaqiyatli
            }
            catch (Exception ex)
            {
                // requeue: true — xabar QAYTA Queue'ga qaytariladi (qayta urinish uchun)
                // requeue: false — xabar DLX'ga (agar sozlangan bo'lsa) yo'naltiriladi
                channel.BasicNack(ea.DeliveryTag, multiple: false, requeue: false);
            }
        };

        channel.BasicConsume(queue: "employee-created-queue", autoAck: false, consumer: consumer);
    }

    private void ProcessEvent(EmployeeCreatedEvent evt)
    {
        Console.WriteLine($"Yangi xodim: {evt.FullName} ({evt.CreatedAt})");
    }
}
```

### Async Consumer — `AsyncEventingBasicConsumer`

```csharp
var consumer = new AsyncEventingBasicConsumer(channel);
consumer.Received += async (model, ea) =>
{
    try
    {
        var json = Encoding.UTF8.GetString(ea.Body.ToArray());
        var evt = JsonSerializer.Deserialize<EmployeeCreatedEvent>(json);

        await ProcessEventAsync(evt!); // async DB/HTTP chaqiruv

        channel.BasicAck(ea.DeliveryTag, multiple: false);
    }
    catch
    {
        channel.BasicNack(ea.DeliveryTag, multiple: false, requeue: false);
    }
};

channel.BasicConsume(queue: "employee-created-queue", autoAck: false, consumer: consumer);
```

### `IHostedService` orqali Background Consumer

Consumer'ni ASP.NET Core ilova hayot sikliga (start/stop) mos
ravishda ishlatish uchun `BackgroundService` ishlatiladi:

```csharp
public class EmployeeCreatedConsumerService : BackgroundService
{
    private readonly IRabbitMqConnectionFactory _connectionFactory;
    private readonly IServiceProvider _serviceProvider;
    private IConnection? _connection;
    private IModel? _channel;

    public EmployeeCreatedConsumerService(
        IRabbitMqConnectionFactory connectionFactory, IServiceProvider serviceProvider)
    {
        _connectionFactory = connectionFactory;
        _serviceProvider = serviceProvider;
    }

    protected override Task ExecuteAsync(CancellationToken stoppingToken)
    {
        _connection = _connectionFactory.CreateConnection();
        _channel = _connection.CreateModel();

        _channel.ExchangeDeclare("employee-events-exchange", ExchangeType.Topic, durable: true);
        _channel.QueueDeclare("employee-created-queue", durable: true, exclusive: false, autoDelete: false);
        _channel.QueueBind("employee-created-queue", "employee-events-exchange", "employee.created");
        _channel.BasicQos(0, 1, false);

        var consumer = new AsyncEventingBasicConsumer(_channel);
        consumer.Received += async (model, ea) =>
        {
            using var scope = _serviceProvider.CreateScope(); // Scoped servislar (DbContext) uchun MUHIM!
            var emailService = scope.ServiceProvider.GetRequiredService<IEmailService>();

            try
            {
                var evt = JsonSerializer.Deserialize<EmployeeCreatedEvent>(
                    Encoding.UTF8.GetString(ea.Body.ToArray()));

                await emailService.SendWelcomeEmailAsync(evt!);
                _channel.BasicAck(ea.DeliveryTag, multiple: false);
            }
            catch
            {
                _channel.BasicNack(ea.DeliveryTag, multiple: false, requeue: false);
            }
        };

        _channel.BasicConsume("employee-created-queue", autoAck: false, consumer: consumer);
        return Task.CompletedTask;
    }

    public override void Dispose()
    {
        _channel?.Dispose();
        _connection?.Dispose();
        base.Dispose();
    }
}

// Program.cs (Consumer App)
builder.Services.AddHostedService<EmployeeCreatedConsumerService>();
```

```
⚠️ MUHIM: DbContext — Scoped lifetime. BackgroundService esa
   SINGLETON sifatida yashaydi. Shuning uchun har xabar qayta
   ishlashda YANGI Scope yaratish SHART (yuqoridagi
   `_serviceProvider.CreateScope()`) — aks holda DbContext
   thread-safety muammosi yoki "disposed context" xatosi chiqadi.
```

### 2 ta alohida application — Publisher va Consumer orasidagi to'liq muloqot

**OrderApi (Publisher)** — buyurtma yaratadi va xabar yuboradi:

```csharp
[ApiController]
[Route("api/orders")]
public class OrdersController : ControllerBase
{
    private readonly AppDbContext _context;
    private readonly IOrderEventPublisher _publisher;

    [HttpPost]
    public async Task<IActionResult> Create(CreateOrderDto dto)
    {
        var order = new Order { CustomerId = dto.CustomerId, Total = dto.Total };
        _context.Orders.Add(order);
        await _context.SaveChangesAsync(); // 1. Avval DB ga saqlanadi

        _publisher.PublishOrderCreated(new OrderCreatedEvent(
            order.Id, order.CustomerId, order.Total, DateTime.UtcNow)); // 2. Keyin xabar yuboriladi

        return Ok(order);
    }
}
```

**NotificationService (Consumer)** — xabarni oladi va email yuboradi:

```csharp
public class OrderCreatedConsumerService : BackgroundService
{
    // ... (yuqoridagi patternga o'xshash)
    // Received event ichida:
    //   var evt = Deserialize<OrderCreatedEvent>(...)
    //   await _emailService.SendOrderConfirmationAsync(evt);
    //   channel.BasicAck(...)
}
```

```
Oqim:
OrderApi (POST /api/orders)
    → DB'ga saqlanadi
    → RabbitMQ Exchange'ga xabar yuboriladi ("order.created")
    → Queue'da saqlanadi
    → NotificationService (alohida process/container) buni Consume qiladi
    → Email yuboriladi

OrderApi va NotificationService — BIR-BIRIDAN MUSTAQIL, alohida
DEPLOY qilinadi, alohida SCALE qilinadi (masalan NotificationService
3 ta instance bo'lib ishlashi mumkin, yuklamani BO'LISHIB oladi)
```

## 5. MassTransit bilan (zamonaviy yondashuv)

### MassTransit nima va nima uchun to'g'ridan RabbitMQ.Client'dan yaxshi

`RabbitMQ.Client` — **past darajadagi** (low-level) kutubxona — Exchange,
Queue, Binding'ni **qo'lda** e'lon qilish, serialization, retry,
reconnect mantig'ini **o'zingiz** yozishingiz kerak. **MassTransit** —
bu ustiga qurilgan **yuqori darajadagi abstraksiya**:

```
RabbitMQ.Client:                    MassTransit:
  ExchangeDeclare()                   Avtomatik (konventsiya asosida)
  QueueDeclare()                      Avtomatik
  QueueBind()                         Avtomatik
  JsonSerializer.Serialize()          Avtomatik (o'ziga xos envelope formatida)
  Manual retry logic                  Built-in Retry policy
  Manual reconnect logic              Built-in avtomatik qayta ulanish
  Manual DLX sozlash                  Built-in "error queue" konventsiyasi
```

### NuGet

```bash
dotnet add package MassTransit --version 8.1.3
dotnet add package MassTransit.RabbitMQ --version 8.1.3
```

### Program.cs sozlash

```csharp
builder.Services.AddMassTransit(x =>
{
    x.AddConsumer<EmployeeCreatedConsumer>(); // Consumer App'da

    x.UsingRabbitMq((context, cfg) =>
    {
        cfg.Host("localhost", "/", h =>
        {
            h.Username("guest");
            h.Password("guest");
        });

        cfg.ReceiveEndpoint("employee-created-queue", e =>
        {
            e.ConfigureConsumer<EmployeeCreatedConsumer>(context);

            // Built-in retry policy
            e.UseMessageRetry(r => r.Interval(3, TimeSpan.FromSeconds(5)));
        });
    });
});
```

### `IPublishEndpoint` orqali xabar yuborish

```csharp
public record EmployeeCreatedEvent(int Id, string FullName, DateTime CreatedAt);

public class EmployeeService
{
    private readonly IPublishEndpoint _publishEndpoint;

    public EmployeeService(IPublishEndpoint publishEndpoint)
        => _publishEndpoint = publishEndpoint;

    public async Task CreateAsync(CreateEmployeeDto dto)
    {
        var employee = /* ... DB ga saqlash ... */;

        // MassTransit — ICHKARIDA Exchange/Queue/Binding'ni O'ZI e'lon qiladi
        // (Fanout Exchange konventsiyasi bo'yicha — barcha Subscriber'lar oladi)
        await _publishEndpoint.Publish(new EmployeeCreatedEvent(
            employee.Id, employee.FullName, DateTime.UtcNow));
    }
}
```

### Consumer implement qilish

```csharp
public class EmployeeCreatedConsumer : IConsumer<EmployeeCreatedEvent>
{
    private readonly IEmailService _emailService;

    public EmployeeCreatedConsumer(IEmailService emailService) => _emailService = emailService;

    public async Task Consume(ConsumeContext<EmployeeCreatedEvent> context)
    {
        var evt = context.Message;
        await _emailService.SendWelcomeEmailAsync(evt.FullName);

        // ACK — MassTransit AVTOMATIK bajaradi (metod XATOSIZ tugasa)!
        // Agar Exception tashlansa — MassTransit AVTOMATIK retry/DLX (error queue) ga yo'naltiradi
    }
}
```

### Saga Pattern — ko'p qadamli jarayon

**Saga** — bir nechta servis orasidagi **uzoq muddatli, ko'p
bosqichli** biznes jarayonni (masalan: "Buyurtma yaratish → To'lov →
Ombordan chiqarish → Yetkazib berish") **holatini kuzatib boruvchi**
pattern. Har bir bosqich muvaffaqiyatsiz bo'lsa — **kompensatsion
amallar** (masalan, to'lovni qaytarish) bajariladi.

```csharp
public class OrderStateMachine : MassTransitStateMachine<OrderState>
{
    public State Submitted { get; private set; } = null!;
    public State PaymentProcessed { get; private set; } = null!;
    public State Shipped { get; private set; } = null!;

    public Event<OrderSubmitted> OrderSubmittedEvent { get; private set; } = null!;
    public Event<PaymentProcessed> PaymentProcessedEvent { get; private set; } = null!;

    public OrderStateMachine()
    {
        InstanceState(x => x.CurrentState);

        Initially(
            When(OrderSubmittedEvent)
                .TransitionTo(Submitted)
                .Publish(context => new ProcessPaymentCommand(context.Message.OrderId)));

        During(Submitted,
            When(PaymentProcessedEvent)
                .TransitionTo(PaymentProcessed)
                .Publish(context => new ShipOrderCommand(context.Message.OrderId)));
    }
}
```

Saga — ERP tizimida ko'p bosqichli jarayonlar (masalan: xodim
qabul qilish → shartnoma yaratish → oylik hisoblash tizimiga
qo'shish) uchun ishlatilishi mumkin.

## 6. Xavfsizlik va Production

### RabbitMQ Management UI

```
http://localhost:15672  (default management port)
Login: guest / guest (FAQAT localhost uchun — production'da O'ZGARTIRISH SHART!)
```

Bu UI orqali — Queue holatini, xabarlar sonini, Consumer'lar
ulanganini, Exchange/Binding sxemasini **vizual** ko'rish mumkin.

### Virtual Host — izolyatsiya

```
Bitta RabbitMQ server ICHIDA bir nechta "Virtual Host" (vhost)
yaratish mumkin — har biri MUSTAQIL Exchange/Queue nom fazosiga ega:

vhost: /production   → prod muhitning Queue/Exchange lari
vhost: /staging       → staging muhitning Queue/Exchange lari

Bu — bitta RabbitMQ CLUSTER'da BIR NECHTA muhit yoki jamoani
IZOLYATSIYA qilish imkonini beradi (bir-biriga XALAQIT bermasdan).
```

### Username/Password autentifikatsiya

```
❌ Production'da default "guest/guest" ishlatish — JIDDIY xavfsizlik
   zaifligi (bu login FAQAT localhost'dan ulanishga ruxsat beradi,
   lekin baribir OSON taxmin qilinadigan login)

✅ Har bir servis uchun ALOHIDA foydalanuvchi, MINIMAL huquq bilan
   (masalan, OrderService — faqat "orders" exchange'ga PUBLISH huquqi,
   boshqa Queue'larni O'QISHGA huquqi YO'Q)
```

### Message Serialization

```csharp
// System.Text.Json — .NET standart, tez, MassTransit default'i
var json = JsonSerializer.Serialize(evt);

// Producer va Consumer bir xil KONTRAKT (record/class strukturasi)ga
// ega bo'lishi SHART — aks holda deserialization XATO beradi!
```

**Versioning muammosi:** agar Producer yangi maydon qo'shsa (masalan
`Email`), eski Consumer'lar buni **e'tiborsiz qoldirishi** kerak
(backward compatible) — buzilmaslik uchun maydonlarni **faqat
qo'shish**, mavjudlarini **o'chirmaslik/o'zgartirmaslik** tavsiya
etiladi.

### Retry policy

```csharp
cfg.UseMessageRetry(r => r.Exponential(
    retryLimit: 5,
    minInterval: TimeSpan.FromSeconds(1),
    maxInterval: TimeSpan.FromSeconds(30),
    intervalDelta: TimeSpan.FromSeconds(5)));
```

```
Urinish 1: DARHOL
Urinish 2: 1 soniyadan keyin
Urinish 3: 6 soniyadan keyin (exponential o'sish)
Urinish 4: 11 soniyadan keyin
Urinish 5: 16 soniyadan keyin
Barcha urinishlar MUVAFFAQIYATSIZ bo'lsa → Error Queue (DLX) ga tushadi
```

### Circuit Breaker pattern

Agar Consumer doimiy ravishda tashqi servisga (masalan, email SMTP
serverga) ulanolmasa — **har bir xabar** uchun qayta-qayta urinish
o'rniga, **Circuit Breaker** vaqtincha "ochiladi" (barcha so'rovlarni
darhol rad etadi) — bu tashqi servisni **qo'shimcha yuklamadan**
himoya qiladi:

```csharp
// Polly kutubxonasi bilan (MassTransit yoki oddiy HttpClient bilan birga)
var circuitBreakerPolicy = Policy
    .Handle<Exception>()
    .CircuitBreakerAsync(exceptionsAllowedBeforeBreaking: 3,
                          durationOfBreak: TimeSpan.FromSeconds(30));
```

### Connection retry va reconnect

```csharp
var factory = new ConnectionFactory
{
    HostName = "localhost",
    AutomaticRecoveryEnabled = true,          // ✅ Ulanish uzilsa AVTOMATIK tiklanadi
    NetworkRecoveryInterval = TimeSpan.FromSeconds(5),
    TopologyRecoveryEnabled = true            // ✅ Exchange/Queue/Binding HAM avtomatik qayta e'lon qilinadi
};
```

MassTransit'da bu **default holatda yoqilgan** — qo'shimcha sozlash
talab qilinmaydi.

## 7. Imtihon savollari

1. Message Broker nima muammoni hal qiladi va u synchronous HTTP
   chaqiruvlardan qanday farq qiladi?
2. Producer to'g'ridan Queue'ga emas, nima uchun Exchange'ga xabar
   yuboradi?
3. Direct, Fanout va Topic Exchange orasidagi farqni har biriga
   misol bilan tushuntiring.
4. Manual va Automatic Acknowledgment orasidagi farq nima, va
   Automatic ACK qanday xatolik xavfini tug'diradi?
5. Durable Queue va Persistent Message orasidagi farq nima — nima
   uchun ikkalasi BIRGA ishlatilishi kerak?
6. `IConnection` nima uchun Singleton, `IModel` (Channel) esa har
   operatsiyada yangi yaratilishi tavsiya etiladi?
7. Dead Letter Exchange (DLX) nima muammoni hal qiladi?
8. `IHostedService`/`BackgroundService` ichida DbContext (Scoped)
   ishlatishda nima uchun har xabar uchun yangi Scope yaratish shart?
9. MassTransit oddiy `RabbitMQ.Client`dan qanday afzalliklarga ega?
10. Saga Pattern nima va u qanday ko'p bosqichli biznes jarayonlarni
    boshqarishga yordam beradi?
11. RabbitMQ va Kafka orasidagi asosiy arxitektura farqi nima, va
    qaysi holatlarda qaysi birini tanlaysiz?
12. `prefetchCount: 1` sozlamasi nima uchun kerak va u bir nechta
    Consumer orasida yuklamani qanday muvozanatlaydi?
