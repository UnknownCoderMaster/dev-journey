# RabbitMQ — Message Broker, Publisher, Consumer — Middle D

> RabbitMQ'ning to'liq, chuqur hujjati (AMQP mexanizmi, Exchange
> turlari, Publisher/Consumer implementatsiyasi, MassTransit, Saga
> Pattern, Production sozlamalari) [03-rabbitmq](../03-rabbitmq/README.md)da
> mavjud. Bu fayl — o'sha materialning **curriculum'dagi rasmiy
> o'rni** sifatida, asosiy nuqtalarni qisqa shaklda takrorlaydi.

## 1. Nima? (Ta'rif)

**Message Broker** — servislar orasida **asinxron** xabar
almashinuvini ta'minlovchi vositachi. **RabbitMQ** — **AMQP**
standarti asosida ishlaydigan eng keng tarqalgan open-source
message broker.

## 2. Nima uchun kerak?

To'g'ridan HTTP orqali servislarni bog'lash — **tight coupling**
yaratadi (bitta servis ishlamasa, ikkinchisi ham to'xtaydi).
RabbitMQ — bu bog'liqlikni **asinxron navbat** orqali "bo'shashtiradi".

## 3. Ichida nima sodir bo'ladi? (Mexanizm)

```
Producer → Exchange → (Binding, Routing Key) → Queue → Consumer
```

**Exchange turlari:** `Direct` (aniq routing key mos kelsa),
`Fanout` (barcha bog'langan Queue'ga, broadcast), `Topic` (wildcard
pattern, `*`/`#`), `Headers` (header asosida).

**Acknowledgment:** Manual ACK — Consumer xabarni **muvaffaqiyatli**
qayta ishlagach `BasicAck()` chaqiradi; Automatic ACK — xabar
yuborilishi bilanoq "yetkazildi" deb hisoblanadi (yiqilish holatida
xabar **yo'qolishi** mumkin).

**Durable Queue + Persistent Message** — ikkalasi BIRGA bo'lsa,
server qayta ishga tushganda ham xabarlar **saqlanib qoladi**.

**Dead Letter Exchange (DLX)** — qayta ishlab bo'lmagan xabarlar
uchun "zaxira" yo'nalish.

## 4. Kod — qisqacha (to'liq versiya boshqa faylda)

```bash
dotnet add package RabbitMQ.Client
```

```csharp
// Publisher
channel.BasicPublish(exchange: "employee-events", routingKey: "employee.created",
    basicProperties: props, body: jsonBytes);

// Consumer
var consumer = new AsyncEventingBasicConsumer(channel);
consumer.Received += async (model, ea) =>
{
    // ... qayta ishlash
    channel.BasicAck(ea.DeliveryTag, multiple: false);
};
channel.BasicConsume(queue: "employee-created-queue", autoAck: false, consumer: consumer);
```

**MassTransit** (tavsiya etiladigan zamonaviy yondashuv) —
Exchange/Queue/Binding'ni avtomatik boshqaradi, built-in retry va
error queue beradi:

```csharp
builder.Services.AddMassTransit(x =>
{
    x.AddConsumer<EmployeeCreatedConsumer>();
    x.UsingRabbitMq((context, cfg) => cfg.Host("localhost"));
});
```

## 5. Qachon ishlatish kerak?

Task queue, murakkab routing, mikroservislar orasida event-driven
aloqa kerak bo'lganda. Juda katta hajmli event stream (log
aggregatsiya) uchun — Kafka ko'proq mos.

## 6. Muhim nuqtalar

- Production'da default `guest/guest` login ISHLATILMASIN.
- `IConnection` — Singleton, `IModel` (Channel) — har operatsiya
  uchun.
- Retry policy va Circuit Breaker — tashqi bog'liqliklarni himoya
  qiladi.

## 7. Imtihon savollari

1. Producer nima uchun to'g'ridan Queue'ga emas, Exchange'ga xabar
   yuboradi?
2. Direct, Fanout, Topic Exchange orasidagi farqni tushuntiring.
3. Manual va Automatic ACK orasidagi farq nima?
4. Dead Letter Exchange qanday muammoni hal qiladi?
5. MassTransit RabbitMQ.Client'dan qanday afzalliklarga ega?
6. RabbitMQ va Kafka qanday holatlarda farqli tanlanadi?

To'liq tafsilotlar uchun: [03-rabbitmq/README.md](../03-rabbitmq/README.md)
