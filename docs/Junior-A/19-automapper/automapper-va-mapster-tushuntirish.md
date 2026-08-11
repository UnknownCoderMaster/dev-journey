# AutoMapper va Mapster: "Magic" emas, balki Reflection + Expression Trees

Ikkalasi ham asosda bir xil g'oyaga tayanadi: **runtime'da property'larni ko'rib chiqib, ular orasida moslikni topib, keyin shu moslik asosida kod generatsiya qilish**. Farqi — *qachon* va *qanday* bu kodni generatsiya qilishida.

---

## 1-qadam: Eng sodda (va sekin) usul — Pure Reflection

Agar sen o'zing mapper yozsang, birinchi urinishing shunday bo'ladi:

```csharp
public static TDestination MapNaive<TSource, TDestination>(TSource source)
    where TDestination : new()
{
    var dest = new TDestination();
    var sourceProps = typeof(TSource).GetProperties();
    var destProps = typeof(TDestination).GetProperties();

    foreach (var sp in sourceProps)
    {
        var dp = destProps.FirstOrDefault(p => p.Name == sp.Name && p.PropertyType == sp.PropertyType);
        if (dp != null)
        {
            var value = sp.GetValue(source);   // Reflection GetValue
            dp.SetValue(dest, value);           // Reflection SetValue
        }
    }
    return dest;
}
```

Bu **ishlaydi**, lekin juda sekin — chunki har bir `GetValue`/`SetValue` chaqiruvi:
- Type metadata'ni tekshiradi
- Boxing/unboxing qiladi (value type'lar uchun)
- JIT optimizatsiyasidan foydalana olmaydi

Har bir map chaqiruvida shu reflection ishi **qaytadan** bajariladi. AutoMapper va Mapster buni qilmaydi — ular buni **faqat bir marta** qiladi.

---

## 2-qadam: AutoMapper qanday ishlaydi — Expression Trees

AutoMapper'ning yuragi — **`System.Linq.Expressions`**. Mana asosiy g'oya:

### a) Konfiguratsiya vaqtida (`CreateMap<Source, Dest>()`)

AutoMapper reflection orqali ikkala type'ning property'larini bir marta tekshiradi va **Expression Tree** quradi — bu aslida kelajakda kompilyatsiya qilinadigan kodning "chizmasi":

```csharp
// Ichki jarayon (soddalashtirilgan):
ParameterExpression sourceParam = Expression.Parameter(typeof(Source), "src");

var bindings = new List<MemberBinding>();
foreach (var destProp in destProps)
{
    var sourceProp = FindMatchingProperty(destProp);
    if (sourceProp != null)
    {
        var propertyAccess = Expression.Property(sourceParam, sourceProp);
        bindings.Add(Expression.Bind(destProp, propertyAccess));
    }
}

var newExpr = Expression.New(typeof(Dest));
var initExpr = Expression.MemberInit(newExpr, bindings);

// Bu aslida quyidagi kodni "yozib" beradi:
// src => new Dest { Name = src.Name, Age = src.Age, ... }
var lambda = Expression.Lambda<Func<Source, Dest>>(initExpr, sourceParam);
```

### b) Compile() — bu yerda haqiqiy sehr ochiladi

```csharp
Func<Source, Dest> compiledMapFunc = lambda.Compile();
```

`.Compile()` chaqirilganda, .NET bu Expression Tree'ni **haqiqiy IL (Intermediate Language) kodga** aylantiradi va uni dynamic method sifatida yaratadi. Natijada sen qo'lda yozgan:

```csharp
Dest Map(Source src) => new Dest { Name = src.Name, Age = src.Age };
```

koddan **deyarli farqsiz tezlikda ishlaydigan delegate** olasan.

### c) Keyingi chaqiruvlar — reflection yo'q!

```csharp
var dest = mapper.Map<Dest>(source);
```

Bu chaqirilganda AutoMapper allaqachon compile qilingan `Func<Source, Dest>` delegatni ichki dictionary'dan (`TypeMap` cache) topib, to'g'ridan-to'g'ri chaqiradi. **Hech qanday runtime reflection yo'q** — faqat bitta compiled delegate chaqiruvi.

**Xulosa:** AutoMapper'da "magic" — bu reflection + expression tree + JIT compile qilishning **bir martalik narxi**, keyin esa u deyarli qo'lda yozilgan kod tezligida ishlaydi.

---

## 3-qadam: Mapster qanday farq qiladi — Source Generators (Compile-Time)

Mapster ikkita rejimda ishlashi mumkin:

### a) Runtime rejimi (AutoMapper'ga o'xshash)
`TypeAdapterConfig` orqali Expression Tree quradi va Compile qiladi — xuddi yuqoridagi kabi, lekin ko'proq optimallashtirilgan (masalan, null-check'larni ham expression darajasida quradi).

### b) Compile-Time (Source Generator) rejimi — bu haqiqiy farq

`Mapster.Tool` yoki `MapsterMapper` bilan **Roslyn Source Generator** ishlatilganda, mapping kodi **build vaqtida** haqiqiy `.cs` fayl sifatida generatsiya qilinadi:

```csharp
// Sen yozasan:
[GenerateMapper]
public partial class UserDto { }

// Compiler avtomatik generatsiya qiladi (haqiqiy fayl!):
public static class UserMapper
{
    public static UserDto AdaptToDto(this User source)
    {
        return new UserDto
        {
            Id = source.Id,
            Name = source.Name,
            Email = source.Email
        };
    }
}
```

Bu holatda runtime'da **hech qanday reflection, hech qanday expression compile qilish yo'q** — chunki kod allaqachon oddiy C# kod sifatida yozilgan va build vaqtida IL'ga aylangan. Shuning uchun Mapster benchmark'larda AutoMapper'dan tezroq chiqadi — ayniqsa source generator rejimida.

---

## Umumiy taqqoslash jadvali

| Bosqich | Pure Reflection | AutoMapper | Mapster (runtime) | Mapster (source gen) |
|---|---|---|---|---|
| Property moslikni topish | Har safar | Bir marta (config) | Bir marta (config) | Build vaqtida |
| Kod generatsiya | Yo'q | Expression Tree → Compile | Expression Tree → Compile | Haqiqiy `.cs` kod |
| Har bir `Map()` chaqiruvi | Sekin (reflection) | Tez (compiled delegate) | Tez (compiled delegate) | Eng tez (statik chaqiruv) |
| Debug qilish imkoni | Oson | Qiyin (IL ichida) | Qiyin | Oson (kodni ko'rasan) |

---

## Amaliy jihat (ERP/production loyihalar uchun)

```csharp
var config = new MapperConfiguration(cfg => cfg.CreateMap<Entity, Dto>());
config.AssertConfigurationIsValid(); // Bu metod Expression Tree'larni tekshiradi
```

`Mapper` obyektini **har bir request'da yangidan yaratish katta xato** — chunki bu Expression Tree qurish va Compile qilish jarayonini har safar qaytaradi. Shu sabab DI'da `IMapper` **singleton** sifatida ro'yxatdan o'tkaziladi (`services.AddAutoMapper(...)` buni avtomatik to'g'ri qiladi) — chunki `MapperConfiguration` bir marta yaratilib, compiled delegate'lar butun ilova hayoti davomida qayta ishlatiladi.
