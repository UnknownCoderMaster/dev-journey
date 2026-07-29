# EF Core — Spatial Data, NetTopologySuite — Middle D

## 1. Nima? (Ta'rif)

**Spatial Data** — geografik/geometrik ma'lumotlar (nuqta, chiziq,
poligon). **PostGIS** — PostgreSQL'ning spatial ma'lumot uchun
extension'i. **NetTopologySuite (NTS)** — .NET'da spatial
ma'lumotlar bilan ishlash uchun kutubxona, EF Core bilan integratsiya
qilingan.

## 2. Nima uchun kerak?

ERP tizimida — "eng yaqin filialni topish", "xodim ish joyidan
qanchalik uzoqda" kabi geografik hisob-kitoblar kerak bo'lishi
mumkin. Bunday hisoblarni **oddiy** SQL (latitude/longitude ustunlari
+ qo'lda formula) bilan qilish **noaniq va sekin** — PostGIS/NTS esa
**geometrik optimallashtirilgan** funksiyalar taqdim etadi.

## 3. Ichida nima sodir bo'ladi? (Mexanizm)

### 3.1 PostgreSQL'da PostGIS extension

```sql
CREATE EXTENSION IF NOT EXISTS postgis;
```

PostGIS — PostgreSQL'ga **spatial tur** (`geometry`, `geography`) va
**spatial funksiyalar** (`ST_Distance`, `ST_Contains`) qo'shadi.

### 3.2 NetTopologySuite NuGet

```bash
dotnet add package Npgsql.EntityFrameworkCore.PostgreSQL.NetTopologySuite --version 8.0.4
```

```csharp
options.UseNpgsql(connStr, o => o.UseNetTopologySuite());
```

### 3.3 Point, LineString, Polygon — asosiy turlar

```csharp
using NetTopologySuite.Geometries;

public class Office
{
    public int Id { get; set; }
    public string Name { get; set; } = null!;
    public Point Location { get; set; } = null!; // Nuqta (Longitude, Latitude)
}

var geometryFactory = NtsGeometryServices.Instance.CreateGeometryFactory(srid: 4326);
var office = new Office
{
    Name = "Toshkent filiali",
    Location = geometryFactory.CreatePoint(new Coordinate(69.2401, 41.2995)) // (X=Longitude, Y=Latitude)
};
```

```
Point       — bitta koordinata (ofis joylashuvi)
LineString  — nuqtalar zanjiri (masalan yetkazib berish yo'nalishi)
Polygon     — yopiq shakl (masalan filial xizmat ko'rsatish hududi)
```

### 3.4 Longitude va Latitude — X va Y

```
⚠️ ENG KO'P uchraydigan XATO:

GPS koordinatalar odatda "Latitude, Longitude" tartibida yoziladi
(masalan Google Maps'da: 41.2995, 69.2401)

LEKIN NetTopologySuite/PostGIS'da Point(X, Y) — X = LONGITUDE,
Y = LATITUDE (matematik x-y tizimiga mos, GEOGRAFIK tartibga EMAS)!

new Coordinate(69.2401, 41.2995) // X=69.24 (longitude), Y=41.29 (latitude)
                                  // TO'G'RI TARTIB!

new Coordinate(41.2995, 69.2401) // ❌ XATO — Latitude/Longitude ALMASHTIRILGAN
```

### 3.5 Masofani hisoblash — `Distance()`

```csharp
var offices = await _context.Offices
    .OrderBy(o => o.Location.Distance(employeeLocation))
    .Take(1)
    .ToListAsync(); // Eng YAQIN filial
```

```sql
-- Ichkarida generatsiya qilingan SQL (soddalashtirilgan)
SELECT * FROM offices ORDER BY ST_Distance(location, ST_Point(69.24, 41.29)) LIMIT 1;
```

`geometry` turi — **tekis** (planar) masofani hisoblaydi (kichik
hududlarda yetarli aniq). `geography` turi — Yer sharining
**egriligini** hisobga oladi (uzoq masofalar uchun aniqroq, lekin
sekinroq).

### 3.6 Geofencing — poligon ichida yoki yo'qligini tekshirish

```csharp
var isInsideZone = deliveryZone.Contains(employeeLocation);
```

```sql
SELECT ST_Contains(delivery_zone, ST_Point(69.24, 41.29));
```

**Geofencing** — "bu nuqta belgilangan hudud (poligon) ichidami"
tekshiruvi — yetkazib berish zonasi, xavfsizlik perimetri kabi
holatlarda ishlatiladi.

### 3.7 EF Core'da sozlash — `UseNetTopologySuite()`

```csharp
builder.Services.AddDbContext<AppDbContext>(options =>
    options.UseNpgsql(connStr, o => o.UseNetTopologySuite()));
```

Migratsiyada — `geometry`/`geography` ustun turi avtomatik
yaratiladi:

```csharp
modelBuilder.Entity<Office>()
    .Property(o => o.Location)
    .HasColumnType("geography (point)"); // Yer egriligini hisobga oladigan tur
```

### 3.8 Spatial Index

```sql
CREATE INDEX idx_offices_location ON offices USING GIST (location);
```

Spatial so'rovlar (masalan "eng yaqin 5 ta filial") — **GiST** indeks
bilan sezilarli tezlashadi (indekssiz — har qatorni tekshirish kerak
bo'lardi).

## 4. Kod — real use case: xodimga eng yaqin ofisni topish

```csharp
public async Task<Office?> FindNearestOfficeAsync(double lon, double lat)
{
    var employeeLocation = _geometryFactory.CreatePoint(new Coordinate(lon, lat));

    return await _context.Offices
        .OrderBy(o => o.Location.Distance(employeeLocation))
        .FirstOrDefaultAsync();
}

public async Task<List<Office>> FindOfficesWithinRadiusAsync(double lon, double lat, double radiusMeters)
{
    var point = _geometryFactory.CreatePoint(new Coordinate(lon, lat));
    return await _context.Offices
        .Where(o => o.Location.IsWithinDistance(point, radiusMeters))
        .ToListAsync();
}
```

## 5. Qachon ishlatish kerak?

| Vaziyat | Yechim |
|---|---|
| Eng yaqin filial/xizmat nuqtasini topish | `Distance()` + `OrderBy` |
| Hudud ichida/tashqarisida ekanligini tekshirish | `Contains()` (Geofencing) |
| Kichik hudud, tez hisob | `geometry` tur |
| Katta masofa, aniq (Yer egriligi hisobga olingan) hisob | `geography` tur |
| Tez spatial qidiruv | GiST indeks |

## 6. Muhim nuqtalar

- Longitude/Latitude tartibini ALMASHTIRIB YUBORISH — eng ko'p
  uchraydigan xato, natijalar **butunlay noto'g'ri** joyni ko'rsatadi.
- `geometry` vs `geography` — noto'g'ri tanlov, katta masofalarda
  **noaniq** natija berishi mumkin.
- Spatial so'rovlar — indekssiz **juda sekin** bo'lishi mumkin, GiST
  indeks amaliy jihatdan MAJBURIY.

## 7. Imtihon savollari

1. PostGIS nima va u PostgreSQL'ga qanday imkoniyat qo'shadi?
2. `Point(X, Y)`da qaysi qiymat Longitude, qaysi Latitude?
3. `geometry` va `geography` turlari orasidagi farq nima?
4. Geofencing nima va u qanday amalga oshiriladi?
5. Spatial so'rovlarda GiST indeks nima uchun muhim?
6. EF Core'da NetTopologySuite qanday sozlanadi?
