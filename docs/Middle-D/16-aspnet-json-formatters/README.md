# JSON Formatters — System.Text.Json vs Newtonsoft.Json — Middle D

## 1. Nima? (Ta'rif)

**Formatter** — HTTP request/response body'ni C# obyektiga (va
teskarisiga) aylantiruvchi komponent. ASP.NET Core'da default —
**System.Text.Json**; muqobil — **Newtonsoft.Json** (Json.NET).

## 2. Nima uchun kerak?

Client (masalan frontend) — ma'lum formatda (odatda JSON) ma'lumot
kutadi. Formatter — C# obyektlarini shu formatga **avtomatik**
aylantiradi, har controller'da qo'lda serialize qilish shart emas.

## 3. Ichida nima sodir bo'ladi? (Mexanizm)

### 3.1 Content Negotiation — Accept header

```
Client: Accept: application/json     → JSON formatter tanlanadi
Client: Accept: application/xml      → XML formatter (agar qo'shilgan bo'lsa)

ASP.NET Core — Accept header'ni tekshirib, mos formatter'ni
TOPADI. Hech biri mos kelmasa yoki Accept ko'rsatilmagan bo'lsa —
DEFAULT formatter (JSON) ishlatiladi.
```

### 3.2 System.Text.Json vs Newtonsoft.Json

| | System.Text.Json | Newtonsoft.Json |
|---|---|---|
| Tezlik | ✅ Tezroq | Sekinroq |
| Xotira | ✅ Kam allocation | Ko'proq |
| .NET default (6+) | ✅ Ha | ❌ Yo'q (qo'shimcha paket) |
| Imkoniyatlar | Cheklangan (ba'zi murakkab holatlar) | ✅ Juda boy (custom converter, circular ref) |
| Polymorphic serialization | .NET 7+ da qo'llab-quvvatlanadi | ✅ Kuchli, eski versiyalardan |

**Qachon Newtonsoft kerak:** murakkab polymorphism, `Dictionary`
bilan noan'anaviy key turi, yoki eski loyihadan **migratsiya**
qilinmagan holatlarda.

```csharp
// Newtonsoft qo'shish (agar kerak bo'lsa)
builder.Services.AddControllers().AddNewtonsoftJson();
```

### 3.3 JsonSerializerOptions — sozlash

```csharp
builder.Services.AddControllers().AddJsonOptions(options =>
{
    options.JsonSerializerOptions.PropertyNamingPolicy = JsonNamingPolicy.CamelCase; // "FullName" → "fullName"
    options.JsonSerializerOptions.DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull; // null maydonlar CHIQARILMAYDI
    options.JsonSerializerOptions.Converters.Add(new JsonStringEnumConverter()); // Enum — SON emas, STRING
    options.JsonSerializerOptions.WriteIndented = true; // Chiroyli formatlash (dev uchun)
});
```

### 3.4 Custom `JsonConverter`

```csharp
public class DateOnlyConverter : JsonConverter<DateOnly>
{
    public override DateOnly Read(ref Utf8JsonReader reader, Type typeToConvert, JsonSerializerOptions options)
        => DateOnly.Parse(reader.GetString()!);

    public override void Write(Utf8JsonWriter writer, DateOnly value, JsonSerializerOptions options)
        => writer.WriteStringValue(value.ToString("yyyy-MM-dd"));
}

options.JsonSerializerOptions.Converters.Add(new DateOnlyConverter());
```

### 3.5 XML formatter qo'shish

```csharp
builder.Services.AddControllers().AddXmlSerializerFormatters();
```

### 3.6 `[JsonIgnore]`, `[JsonPropertyName]`

```csharp
public class Employee
{
    [JsonPropertyName("full_name")] // JSON'da "full_name" (snake_case) bo'lsin
    public string FullName { get; set; } = null!;

    [JsonIgnore] // Bu maydon HECH QACHON JSON'ga chiqmaydi
    public string PasswordHash { get; set; } = null!;
}
```

### 3.7 Circular Reference — hal qilish

```
Employee → Department → Employees (List<Employee>) → Department → ... (CHEKSIZ!)

❌ System.Text.Json — DEFAULT holatda JsonException tashlaydi
   ("A possible object cycle was detected")

✅ Yechim 1: DTO ishlatish (Entity'ni TO'G'RIDAN qaytarmaslik)
✅ Yechim 2: ReferenceHandler.IgnoreCycles
   options.JsonSerializerOptions.ReferenceHandler = ReferenceHandler.IgnoreCycles;
```

```
⚠️ TAVSIYA: Circular reference muammosi — ko'pincha "Entity'ni
   to'g'ridan API javobida qaytarish" dizayn xatosining BELGISI.
   DTO/AutoMapper orqali FAQAT kerakli maydonlarni qaytarish —
   muammoni ILDIZIDAN hal qiladi.
```

### 3.8 DateTime serialization — UTC, format

```csharp
// System.Text.Json — DEFAULT holda ISO 8601 formatida serialize qiladi
// 2026-07-22T14:30:00Z (Z — UTC ekanini bildiradi)

var employee = new Employee { HiredAt = DateTime.UtcNow }; // ✅ HAR DOIM UtcNow
```

```
❌ DateTime.Now — SERVER local timezone'ga BOG'LIQ, turli serverlarda
   TURLICHA natija berishi mumkin!
✅ DateTime.UtcNow — HAR DOIM UTC, timezone muammosi YO'Q
   (frontend — o'z local vaqtiga O'ZI konvertatsiya qiladi)
```

## 4. Kod — to'liq misol

```csharp
builder.Services.AddControllers()
    .AddJsonOptions(options =>
    {
        options.JsonSerializerOptions.PropertyNamingPolicy = JsonNamingPolicy.CamelCase;
        options.JsonSerializerOptions.DefaultIgnoreCondition = JsonIgnoreCondition.WhenWritingNull;
        options.JsonSerializerOptions.Converters.Add(new JsonStringEnumConverter());
        options.JsonSerializerOptions.ReferenceHandler = ReferenceHandler.IgnoreCycles;
    });
```

## 5. Qachon ishlatish kerak?

| Vaziyat | Yechim |
|---|---|
| Yangi loyiha | System.Text.Json (default) |
| Murakkab polymorphic serialization, eski loyiha | Newtonsoft.Json |
| Legacy client faqat XML tushunadi | XML formatter qo'shish |
| Entity → API javob | DTO (circular reference oldini oladi) |

## 6. Muhim nuqtalar

- Entity'ni TO'G'RIDAN API javobida qaytarish — circular reference
  VA xavfsizlik (parol hash kabi maydonlar oshkor bo'lishi) xavfini
  tug'diradi — HAR DOIM DTO ishlatish tavsiya etiladi.
- `JsonStringEnumConverter` — enum'ni SON o'rniga STRING sifatida
  serialize qiladi (`0` o'rniga `"Admin"`) — API o'qilishini
  yaxshilaydi.

## 7. Imtihon savollari

1. System.Text.Json va Newtonsoft.Json orasidagi asosiy farqlarni
   ayting.
2. Content Negotiation qanday ishlaydi (Accept header orqali)?
3. Circular Reference muammosi nima va uni qanday hal qilish mumkin?
4. `[JsonIgnore]` va `[JsonPropertyName]` nima uchun ishlatiladi?
5. Nima uchun `DateTime.UtcNow` `DateTime.Now`dan afzalroq
   (serialization nuqtai nazaridan)?
6. Entity'ni to'g'ridan qaytarish o'rniga DTO ishlatish nima uchun
   tavsiya etiladi?
