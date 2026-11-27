# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "Rabbit MQ UI bilan ishlash"
CATEGORY = "Rabbit"
TITLE = "RabbitMQ Boshqaruv Paneli"
SUBTITLE = "Navbatlarni kuzatish, nosozlikni topish va sozlash"
FILENAME = "Rabbit MQ UI bilan ishlash.docx"


def build(d):
    h1(d, "1. Panelni yoqish")

    para(d, "Boshqaruv paneli RabbitMQ ning kengaytmasi bo'lib, uni "
            "alohida yoqish kerak. Rasmiy Docker tasvirining "
            "`management` versiyasida u allaqachon yoqilgan.")

    code(d, """services:
  rabbitmq:
    image: rabbitmq:4-management
    ports:
      - "5672:5672"      # AMQP — dasturlar ulanadi
      - "15672:15672"    # boshqaruv paneli
    environment:
      RABBITMQ_DEFAULT_USER: admin
      RABBITMQ_DEFAULT_PASS: ${RABBITMQ_PASSWORD}
    volumes:
      - rabbitmq_data:/var/lib/rabbitmq""")

    code(d, """# Alohida o'rnatilgan bo'lsa
rabbitmq-plugins enable rabbitmq_management""")

    para(d, "Panel `http://localhost:15672` manzilida ochiladi.")

    note(d, "Standart `guest` hisobi haqida:",
         "U faqat `localhost` dan ulanishga ruxsat beradi — tashqaridan "
         "kirib bo'lmaydi. Bu ataylab shunday qilingan va xavfsizlik "
         "chorasi hisoblanadi. Shuning uchun konteynerda ishlaganda o'z "
         "foydalanuvchimni yaratishim kerak bo'ladi.")

    # ───────────────────────────────────────────
    h1(d, "2. Panel bo'limlari")

    table(d, ["Bo'lim", "Nima ko'rsatadi"],
          [["Overview", "Umumiy holat, xabarlar tezligi, tugunlar"],
           ["Connections", "Faol ulanishlar va ularning holati"],
           ["Channels", "Ulanish ichidagi mantiqiy kanallar"],
           ["Exchanges", "Almashtirgichlar va ularning bog'lanishlari"],
           ["Queues", "Navbatlar, ulardagi xabarlar soni"],
           ["Admin", "Foydalanuvchilar, virtual hostlar, siyosatlar"]],
          widths=[3.6, 11.9])

    # ───────────────────────────────────────────
    h1(d, "3. Eng muhim ko'rsatkichlar")

    h2(d, "3.1 Navbatdagi xabarlar")

    table(d, ["Ko'rsatkich", "Ma'nosi"],
          [["Ready", "Iste'molchiga yuborishga tayyor"],
           ["Unacked", "Yuborilgan, lekin hali tasdiqlanmagan"],
           ["Total", "Ikkalasining yig'indisi"]],
          widths=[3.4, 12.1])

    note(d, "Bu uch raqam ko'p narsani aytadi:",
         "`Ready` o'sib borsa — iste'molchilar yetishmayapti yoki ular "
         "sekin ishlayapti. `Unacked` o'sib borsa va tushmasa — "
         "iste'molchi xabarni olgan, lekin qayta ishlay olmayapti yoki "
         "tasdiqlashni unutgan. Ikkinchisi ancha jiddiyroq muammo, chunki "
         "u odatda kod xatosini bildiradi.")

    h2(d, "3.2 Xabarlar tezligi")

    bullets(d, [
        "**Publish** — sekundiga nechta xabar kelyapti.",
        "**Deliver** — sekundiga nechta yetkazilyapti.",
        "**Ack** — sekundiga nechta tasdiqlanyapti.",
    ])

    para(d, "Agar `Publish` doimiy ravishda `Ack` dan yuqori bo'lsa, navbat "
            "o'sib boradi va oxir-oqibat xotira tugaydi.")

    h2(d, "3.3 Iste'molchilar soni")

    note(d, "Nol iste'molchi — eng tez-tez uchraydigan muammo:",
         "Xabarlar kelyapti, navbat o'syapti, lekin `Consumers` ustunida "
         "nol turibdi. Bu ilovam ishlamayotganini yoki ulanish "
         "uzilganini bildiradi. Men nosozlikni izlayotganda birinchi "
         "navbatda shu raqamga qarayman — ko'p holatda javob shu yerda "
         "topiladi.")

    # ───────────────────────────────────────────
    h1(d, "4. Panelda amaliy ishlar")

    h2(d, "4.1 Navbat yaratish")

    para(d, "`Queues` → `Add a new queue` bo'limida navbat parametrlari "
            "belgilanadi:")

    table(d, ["Parametr", "Ma'nosi"],
          [["Durable", "Server qayta ishga tushganda saqlanadi"],
           ["Auto delete", "Oxirgi iste'molchi ketganda o'chadi"],
           ["`x-message-ttl`", "Xabarning yashash muddati (ms)"],
           ["`x-max-length`", "Maksimal xabarlar soni"],
           ["`x-dead-letter-exchange`", "Rad etilgan xabarlar qayerga ketadi"],
           ["`x-queue-type`", "`classic` yoki `quorum`"]],
          widths=[5.2, 10.3])

    note(d, "Panelda navbat yaratish — faqat sinov uchun:",
         "Agar men navbatni qo'lda yaratsam va keyin ilova uni boshqa "
         "parametrlar bilan e'lon qilmoqchi bo'lsa, `PRECONDITION_FAILED` "
         "xatosi chiqadi. Navbat parametrlari o'zgarmas, shuning uchun "
         "ularni faqat kodda e'lon qilish va git da saqlash to'g'riroq.")

    code(d, """await channel.QueueDeclareAsync(
    queue: "orders.created",
    durable: true,
    exclusive: false,
    autoDelete: false,
    arguments: new Dictionary<string, object?>
    {
        ["x-dead-letter-exchange"] = "orders.dlx",
        ["x-message-ttl"] = 86_400_000
    });""")

    h2(d, "4.2 Xabarni ko'rish")

    para(d, "`Queues` → navbat → `Get messages` bo'limida navbatdagi "
            "xabarlarni ko'rish mumkin.")

    note(d, "`Ack Mode` ni to'g'ri tanlash juda muhim:",
         "`Nack message requeue true` — xabarni ko'rib, navbatga "
         "qaytaradi. `Automatic ack` esa uni **o'chiradi**. Men bir marta "
         "ikkinchisini tanlab, production navbatidagi xabarni yo'qotib "
         "qo'yganman. Shundan beri bu ro'yxatga alohida e'tibor beraman.")

    h2(d, "4.3 Xabar yuborish")

    para(d, "`Exchanges` → almashtirgich → `Publish message` orqali qo'lda "
            "xabar yuborish mumkin. Bu iste'molchini sinash uchun eng tez "
            "usul — ilovani ishga tushirmasdan turib uning ishlashini "
            "tekshirish mumkin.")

    code(d, """Routing key: orders.created
Payload:
{
  "orderId": 42,
  "customerId": 7,
  "total": 150000
}
Properties:
  content_type: application/json
  delivery_mode: 2""")

    note(d, "`delivery_mode: 2` ni yozishni unutmaslik kerak:",
         "U xabarni doimiy (persistent) qiladi, ya'ni server qayta ishga "
         "tushganda saqlanadi. `1` esa xabarni faqat xotirada saqlaydi. "
         "Navbat `durable` bo'lsa ham, xabar `persistent` bo'lmasa — u "
         "yo'qoladi. Bu ikki sozlama alohida ishlaydi va ikkalasi ham "
         "kerak.")

    h2(d, "4.4 Navbatni tozalash")

    para(d, "`Purge Messages` tugmasi navbatdagi barcha xabarlarni "
            "o'chiradi. Bu ortga qaytarilmaydi.")

    # ───────────────────────────────────────────
    h1(d, "5. Dead letter navbati")

    para(d, "Qayta ishlab bo'lmagan xabarlar yo'qolmasligi uchun ular "
            "alohida navbatga yo'naltiriladi.")

    code(d, """// Asosiy navbat
arguments: new Dictionary<string, object?>
{
    ["x-dead-letter-exchange"] = "orders.dlx",
    ["x-dead-letter-routing-key"] = "orders.failed"
}

// DLX va DLQ
await channel.ExchangeDeclareAsync("orders.dlx", ExchangeType.Direct, durable: true);
await channel.QueueDeclareAsync("orders.failed", durable: true,
    exclusive: false, autoDelete: false);
await channel.QueueBindAsync("orders.failed", "orders.dlx", "orders.failed");""")

    para(d, "Xabar quyidagi hollarda dead letter navbatiga tushadi:")

    bullets(d, [
        "Iste'molchi `BasicNack` yoki `BasicReject` ni `requeue: false` "
        "bilan chaqirganda.",
        "Xabarning `TTL` muddati tugaganda.",
        "Navbat maksimal uzunlikdan oshganda.",
    ])

    note(d, "DLQ ni kuzatish — eng foydali odatlardan biri:",
         "Men unga ogohlantirish qo'yaman: agar u yerda xabar paydo "
         "bo'lsa, xabar beriladi. Chunki DLQ ga tushgan har bir xabar — "
         "bu qayta ishlanmagan ish, ya'ni foydalanuvchi uchun bajarilmagan "
         "amal. Paneldan uning mazmunini o'qib, sababni aniqlash mumkin.")

    para(d, "Tuzatilgandan keyin xabarlarni qaytarish uchun `shovel` "
            "kengaytmasi ishlatiladi:")

    code(d, """rabbitmq-plugins enable rabbitmq_shovel rabbitmq_shovel_management""")

    # ───────────────────────────────────────────
    h1(d, "6. Nosozlikni topish tartibi")

    para(d, "Xabar yetib bormayotganda men quyidagi tartibda tekshiraman:")

    bullets(d, [
        "**Connections** — ilova umuman ulanganmi.",
        "**Queues → Consumers** — iste'molchi bormi.",
        "**Queues → Ready** — xabar navbatga tushyaptimi.",
        "**Exchanges → Bindings** — marshrutlash to'g'rimi.",
        "**DLQ** — xabar u yerga tushib ketmaganmi.",
    ], numbered=True)

    note(d, "To'rtinchi qadam ko'pincha javob beradi:",
         "Xabar yuborilgan, lekin hech qayerga bormagan — chunki "
         "almashtirgich va navbat o'rtasida bog'lanish yo'q yoki routing "
         "key mos kelmagan. RabbitMQ bunday xabarni jimgina tashlab "
         "yuboradi va hech qanday xatolik bermaydi. Panelda esa "
         "`Unroutable` hisoblagichi orqali buni ko'rish mumkin.")

    code(d, """// Yetib bormagan xabarlar haqida xabar olish
await channel.BasicPublishAsync(
    exchange: "orders",
    routingKey: "orders.created",
    mandatory: true,          // yetib bormasa qaytariladi
    basicProperties: props,
    body: body);

channel.BasicReturnAsync += (sender, ea) =>
{
    _logger.LogError("Xabar yetib bormadi: {Key}", ea.RoutingKey);
    return Task.CompletedTask;
};""")

    # ───────────────────────────────────────────
    h1(d, "7. Admin bo'limi")

    h2(d, "7.1 Foydalanuvchilar")

    code(d, """rabbitmqctl add_user app_user 'kuchli-parol'
rabbitmqctl set_user_tags app_user none
rabbitmqctl set_permissions -p / app_user "^orders\\." "^orders\\." "^orders\\." """)

    para(d, "Uchta naqsh mos ravishda sozlash, yozish va o'qish huquqini "
            "belgilaydi.")

    h2(d, "7.2 Siyosatlar")

    para(d, "Siyosat bir nechta navbatga bir yo'la sozlama qo'llaydi:")

    code(d, """rabbitmqctl set_policy ttl-policy "^temp\\." \\
    '{"message-ttl": 3600000, "max-length": 10000}' \\
    --apply-to queues""")

    note(d, "Siyosat navbat argumentlaridan farq qiladi:",
         "Argumentlar navbat yaratilganda belgilanadi va o'zgarmaydi. "
         "Siyosat esa keyinroq qo'llaniladi va o'zgartirilishi mumkin. "
         "Shuning uchun TTL va uzunlik chegarasi kabi sozlamalarni "
         "siyosat orqali berish moslashuvchanroq.")

    # ───────────────────────────────────────────
    h1(d, "8. Xavfsizlik")

    bullets(d, [
        "15672 portini internetga ochmaslik.",
        "Standart `guest` hisobini o'chirish yoki parolini o'zgartirish.",
        "Ilova uchun cheklangan huquqli alohida foydalanuvchi yaratish.",
        "HTTPS orqali ulanish (`15671` port).",
        "Virtual hostlar bilan muhitlarni ajratish.",
    ])

    # ───────────────────────────────────────────
    # ───────────────────────────────────────────
    h1(d, "9. Amaliyotdan: auditni navbatga chiqarish")

    para(d, "Ish joyimdagi MAD ERP tizimida RabbitMQ bitta aniq vazifa uchun ishlatiladi: "
            "hujjat tarixini yozish. Har bir hujjat holati o'zgarganda kim, qachon, "
            "qaysi IP dan va nimani o'zgartirgani jurnalga tushishi kerak. Bu talab "
            "majburiy, lekin foydalanuvchi uni kutib turishi shart emas.")

    para(d, "Shuning uchun servis xabarni navbatga qo'yadi va javobni qaytaradi. "
            "Jurnalni alohida job servisi o'z vaqtida, alohida bazaga yozadi.")

    h2(d, "9.1 Iste'molchi sozlamalari — panelda ko'rinadigan raqamlarning manbasi")

    para(d, "3-bo'limda prefetch va iste'molchilar soni haqida gap ketgan. Kodda ular "
            "shunday e'lon qilinadi:")

    code(d, """public class DocumentHistoryConsumerConfig : IWbConsumerConfig<DocumentHistoryMessage>
{
    public string Name => "MadErpDocumentHistory";
    public WbRabbitQueue Queue => AuditQueues.DocumentHistory;
    public ushort PrefetchCount { get; set; } = 1;
    public int WorkerCount { get; set; } = 1;
    public bool RequeueOnFailed { get; set; } = true;
}""", caption="DocumentHistoryConsumer.cs")

    para(d, "Ro'yxatga olish esa konfiguratsiyadan ustidan yozish imkonini qoldiradi, "
            "ya'ni bu qiymatlarni deploy qilmasdan o'zgartirish mumkin:")

    code(d, """services.AddRabbitMQConsumerClient(options =>
{
    config.GetSection("RabbitMQ").Bind(options);
})
.AddConsumer<DocumentHistoryMessage, DocumentHistoryConsumerConfig, DocumentHistoryConsumer>(
    options => config.GetSection("RabbitMQ:Consumers:DocumentHistory").Bind(options))
.AddConsumer<RowHistoryMessage, RowHistoryConsumerConfig, RowHistoryConsumer>(
    options => config.GetSection("RabbitMQ:Consumers:RowHistory").Bind(options));""")

    para(d, "`PrefetchCount = 1` va `WorkerCount = 1` — ataylab past qiymatlar. Jurnal "
            "yozishning tezligi muhim emas, lekin tartibi muhim: bir xil hujjat uchun "
            "ikki o'zgarish teskari tartibda yozilib qolmasligi kerak. Panelda bu "
            "o'zini shunday ko'rsatadi: `Unacked` ustuni deyarli har doim 1, "
            "`Ready` esa yuk ko'tarilganda o'sadi.")

    h2(d, "9.2 RequeueOnFailed — eng ko'p o'ylangan sozlama")

    para(d, "5-bo'limda dead letter navbati va cheksiz aylanish muammosi aytilgan. "
            "`RequeueOnFailed = true` aynan shu xatarni oladi: xato bergan xabar "
            "navbatga qaytariladi.")

    para(d, "Iste'molchining o'zida esa xato yutiladi va log ga yoziladi:")

    code(d, """try
{
    await _dbContext.DocumentHistories.AddAsync(documentHistory, cancellationToken);
    await _dbContext.SaveChangesAsync(cancellationToken);

    _logger.LogInformation("Document history saved: DocId={DocId}, TableId={TableId}",
        message.DocId, message.TableId);
}
catch (Exception ex)
{
    _logger.LogError(ex, "Error saving document history: DocId={DocId}, TableId={TableId}",
        message.DocId, message.TableId);
}""")

    para(d, "Bu yerda nozik ziddiyat bor. `catch` xatoni tashqariga chiqarmagani uchun "
            "broker xabarni muvaffaqiyatli deb hisoblaydi va `RequeueOnFailed` amalda "
            "ishga tushmaydi. Ya'ni jurnal yozuvi yo'qoladi, lekin navbat tiqilib "
            "qolmaydi.")

    note(d, "Menimcha bu ongli murosa, lekin uni bilib turish kerak:",
         "Agar xato tashqariga chiqarilsa, baza bir muddat ishlamaganda xabarlar "
         "navbatga qaytib-qaytib kelardi va 5-bo'limda aytilgan \"poison message\" "
         "holati paydo bo'lardi — bitta buzuq xabar butun navbatni to'xtatib qo'yardi. "
         "Hozirgi tanlov esa teskari tarafga og'ishgan: navbat hech qachon tiqilmaydi, "
         "lekin jurnalning to'liqligi kafolatlanmaydi. Audit uchun bu bahsli, chunki "
         "jurnalning maqsadi aynan to'liqlik. To'g'ri yechim — xatoni chiqarib, DLQ ga "
         "yuborish va DLQ ni panelda kuzatish. Bizda DLQ avtomatik sozlanadi, ya'ni "
         "infratuzilma buning uchun tayyor.")

    para(d, "Panelda buni tekshirish 6-bo'limdagi tartib bo'yicha oson: agar "
            "`DocumentHistory` navbatida `Ready` nol, `Unacked` nol, lekin bazada "
            "yozuvlar yetishmayotgan bo'lsa — demak xabarlar yutilgan, DLQ ga ham "
            "tushmagan. Bu holatda log dan `Error saving document history` qatorlarini "
            "qidirish kerak.")

    h1(d, "10. Xulosa")

    bullets(d, [
        "Panel `rabbitmq_management` kengaytmasi orqali ishlaydi va "
        "15672 portda ochiladi.",
        "`Ready` va `Unacked` raqamlari muammoning turini aytadi.",
        "`Consumers` nolga teng bo'lsa — ilova ulanmagan.",
        "Navbatni panelda yaratish parametrlar to'qnashuviga olib "
        "kelishi mumkin — uni kodda e'lon qilish to'g'riroq.",
        "`Get messages` da `Automatic ack` xabarni o'chiradi.",
        "Navbat `durable`, xabar `persistent` bo'lishi — ikki alohida "
        "sozlama.",
        "Dead letter navbatini kuzatish qayta ishlanmagan ishlarni "
        "ko'rsatadi.",
        "`mandatory` bayrog'i marshrutlanmagan xabar haqida xabar "
        "beradi.",
    ])

    sources(d, [
        ("Management Plugin — RabbitMQ hujjati",
         "https://www.rabbitmq.com/docs/management"),
        ("Queues — RabbitMQ hujjati",
         "https://www.rabbitmq.com/docs/queues"),
        ("Dead Letter Exchanges — RabbitMQ",
         "https://www.rabbitmq.com/docs/dlx"),
        ("Access Control — RabbitMQ",
         "https://www.rabbitmq.com/docs/access-control"),
    ])
