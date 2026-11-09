# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "REST vs SOAP (JSON vs XML)"
CATEGORY = "Tashqi tizimlar bilan ishlash"
TITLE = "REST va SOAP"
SUBTITLE = "Ikki yondashuv, JSON va XML formatlari"
FILENAME = "REST vs SOAP (JSON vs XML).docx"


def build(d):
    h1(d, "1. Tushunchalarni ajratish")

    para(d, "Taqqoslashni boshlashdan oldin bir noaniqlikni "
            "aniqlashtirish kerak: **SOAP — protokol, REST — "
            "arxitektura uslubi**. Ular bir darajadagi narsalar "
            "emas.")

    bullets(d, [
        "**SOAP** — qat'iy belgilangan protokol: xabar formati "
        "(XML envelope), xato formati, kengaytmalar (WS-Security, "
        "WS-Transaction).",
        "**REST** — tamoyillar to'plami: resurslar, HTTP "
        "metodlari semantikasi, stateless aloqa, yagona "
        "interfeys. Hech qanday majburiy format yo'q.",
    ])

    para(d, "Shuning uchun \"REST protokoli\" degan ibora "
            "noto'g'ri, va REST API JSON emas, XML qaytarishi "
            "ham mumkin.")

    # ───────────────────────────────────────────
    h1(d, "2. SOAP xabari qanday ko'rinadi")

    code(d, """POST /OrderService.asmx HTTP/1.1
Content-Type: text/xml; charset=utf-8
SOAPAction: "http://example.com/CreateOrder"

<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
  <soap:Header>
    <AuthToken xmlns="http://example.com/">eyJhbGciOi...</AuthToken>
  </soap:Header>
  <soap:Body>
    <CreateOrder xmlns="http://example.com/">
      <customerId>3f2b8c1a</customerId>
      <items>
        <OrderItem>
          <productId>a1c9</productId>
          <quantity>2</quantity>
        </OrderItem>
      </items>
    </CreateOrder>
  </soap:Body>
</soap:Envelope>""")

    para(d, "Diqqat qilinadigan narsa: hamma operatsiya bitta "
            "endpoint'ga `POST` bilan yuboriladi. HTTP metodi va "
            "status kodlari semantik ma'noga ega emas — amal "
            "`SOAPAction` va tana ichida ko'rsatiladi.")

    code(d, """<!-- SOAP xato javobi: HTTP 500 bo'lsa ham -->
<soap:Fault>
  <faultcode>soap:Client</faultcode>
  <faultstring>Mijoz topilmadi</faultstring>
  <detail><errorCode>CUSTOMER_NOT_FOUND</errorCode></detail>
</soap:Fault>""")

    # ───────────────────────────────────────────
    h1(d, "3. REST ekvivalenti")

    code(d, """POST /api/orders HTTP/1.1
Content-Type: application/json
Authorization: Bearer eyJhbGciOi...

{"customerId":"3f2b8c1a","items":[{"productId":"a1c9","quantity":2}]}

---

HTTP/1.1 201 Created
Location: /api/orders/7f3c9a1e
Content-Type: application/json

{"id":"7f3c9a1e","number":"ORD-1042","total":250000}""")

    para(d, "Bu yerda HTTP o'zi ishlatiladi: metod amalni, status "
            "kod natijani, `Location` yangi resurs manzilini "
            "bildiradi. Natijada xabar kichik va infratuzilma "
            "(kesh, proxy, log) uni tushunadi.")

    # ───────────────────────────────────────────
    h1(d, "4. Taqqoslash")

    table(d, ["", "SOAP", "REST"],
          [["Format", "Faqat XML", "JSON, XML, protobuf — ixtiyoriy"],
           ["Transport", "HTTP, SMTP, TCP", "Asosan HTTP"],
           ["Shartnoma", "WSDL — rasmiy va majburiy", "OpenAPI — ixtiyoriy"],
           ["Xabar hajmi", "Katta (envelope, namespace)", "Kichik"],
           ["Keshlash", "Qiyin (hammasi POST)", "HTTP keshi tabiiy ishlaydi"],
           ["Xavfsizlik", "WS-Security — xabar darajasida", "TLS, OAuth, JWT"],
           ["Tranzaksiya", "WS-Transaction — standart bor", "Yo'q, Saga kerak"],
           ["Kod generatsiyasi", "WSDL dan avtomatik", "OpenAPI dan mumkin"]],
          widths=[3.4, 5.4, 5.7])

    # ───────────────────────────────────────────
    h1(d, "5. SOAP qachon hali ham uchraydi")

    para(d, "Yangi loyihada SOAP tanlanmaydi, lekin unga "
            "ulanish kerak bo'lishi juda ko'p uchraydi:")

    bullets(d, [
        "Davlat tizimlari va soliq organlari API'lari.",
        "Bank va to'lov tizimlarining eski integratsiyalari.",
        "Korporativ ERP va buxgalteriya tizimlari.",
        "Telekom operatorlarining billing tizimlari.",
    ])

    para(d, "Bu holatda SOAP'ning kuchli tomonlari sabab "
            "bo'ladi: WSDL rasmiy shartnoma beradi, "
            "WS-Security xabarni **transport darajasidan "
            "mustaqil** imzolaydi va shifrlaydi, va bu ko'p "
            "vositachi orqali o'tadigan hujjat aylanishida "
            "muhim.")

    # ───────────────────────────────────────────
    h1(d, "6. .NET da SOAP servisga ulanish")

    code(d, """# WSDL dan mijoz kodi generatsiya qilish
dotnet tool install --global dotnet-svcutil

dotnet-svcutil https://partner.example.com/OrderService?wsdl \\
    --namespace "*,Shop.Integration.Partner" \\
    --outputFile PartnerClient.cs""")

    code(d, """var binding = new BasicHttpsBinding
{
    MaxReceivedMessageSize = 10 * 1024 * 1024,
    SendTimeout = TimeSpan.FromSeconds(30)
};

var endpoint = new EndpointAddress("https://partner.example.com/OrderService");

using var client = new OrderServiceClient(binding, endpoint);

client.ClientCredentials.UserName.UserName = options.UserName;
client.ClientCredentials.UserName.Password = options.Password;

var response = await client.CreateOrderAsync(request);""")

    note(d, "Muhim cheklov",
         "WCF **server** tomoni .NET Core va undan keyingi "
         "versiyalarda qo'llanmaydi. Mijoz tomoni esa "
         "`System.ServiceModel.*` paketlari orqali ishlaydi. "
         "SOAP servis **yozish** kerak bo'lsa, `CoreWCF` loyihasi "
         "ishlatiladi.")

    # ───────────────────────────────────────────
    h1(d, "7. JSON va XML")

    code(d, """// JSON — ixcham
{"id":42,"name":"Mahsulot","price":250000,"tags":["yangi","chegirma"]}""")

    code(d, """<!-- XML — batafsil, lekin og'irroq -->
<product id="42">
  <name>Mahsulot</name>
  <price currency="UZS">250000</price>
  <tags>
    <tag>yangi</tag>
    <tag>chegirma</tag>
  </tags>
</product>""")

    table(d, ["", "JSON", "XML"],
          [["Hajm", "Kichik", "2-4 barobar kattaroq"],
           ["Parse tezligi", "Tez", "Sekinroq"],
           ["Atributlar", "Yo'q", "Bor"],
           ["Izohlar", "Yo'q (standartda)", "Bor"],
           ["Sxema", "JSON Schema", "XSD — kuchliroq"],
           ["So'rov tili", "JSONPath", "XPath — ancha kuchli"],
           ["Namespace", "Yo'q", "Bor"],
           ["Hujjat tuzilishi", "Mos emas", "Mos (matn + markup)"]],
          widths=[3.4, 5.4, 5.7])

    para(d, "JSON ni standart tanlov deb bilaman: kichik, tez, "
            "va mijozlarning aksariyati uni tabiiy qayta "
            "ishlaydi.")

    para(d, "XML esa ikki holatda haqiqatan ustun: hujjat "
            "tuzilishi kerak bo'lganda (Office formatlari aynan "
            "XML asosida) va **qattiq validatsiya** kerak "
            "bo'lganda — XSD JSON Schema'dan kuchliroq va u "
            "sxemani shartnoma sifatida ishlatishga imkon "
            "beradi.")

    h2(d, "Ikkisini ham qo'llab-quvvatlash")

    code(d, """builder.Services.AddControllers(options =>
{
    options.RespectBrowserAcceptHeader = true;
})
.AddXmlSerializerFormatters();""")

    para(d, "Shundan keyin mijoz `Accept: application/xml` "
            "yuborsa XML, `application/json` yuborsa JSON oladi — "
            "controller kodi o'zgarmaydi.")

    # ───────────────────────────────────────────
    h1(d, "8. Hozirgi alternativalar")

    bullets(d, [
        "**gRPC** — protobuf va HTTP/2 ustida. Ichki "
        "mikroservislar orasida tez va qat'iy shartnomali. "
        "Brauzerdan to'g'ridan-to'g'ri ishlatish qiyin.",
        "**GraphQL** — mijoz qaysi maydonlar kerakligini o'zi "
        "so'raydi. Mobil ilovalar va murakkab UI uchun qulay, "
        "lekin keshlash va so'rov murakkabligini cheklash "
        "qo'shimcha ish talab qiladi.",
        "**Webhook** — teskari yo'nalish: server mijozga xabar "
        "beradi. Uzoq davom etadigan operatsiyalar uchun "
        "polling'dan yaxshiroq.",
    ])

    para(d, "Tanlov qoidam: ommaviy API va brauzer mijozlari "
            "uchun — REST + JSON. Ichki servislar orasida va "
            "yuqori yuklamada — gRPC. SOAP — faqat hamkor "
            "tizim talab qilganda.")

    sources(d, [
        ("SOAP Version 1.2 — W3C",
         "https://www.w3.org/TR/soap12/"),
        ("RFC 9110 — HTTP Semantics",
         "https://datatracker.ietf.org/doc/html/rfc9110"),
        ("dotnet-svcutil tool",
         "https://learn.microsoft.com/en-us/dotnet/core/additional-tools/dotnet-svcutil-guide"),
        ("Format response data in ASP.NET Core Web API",
         "https://learn.microsoft.com/en-us/aspnet/core/web-api/advanced/formatting"),
    ])
