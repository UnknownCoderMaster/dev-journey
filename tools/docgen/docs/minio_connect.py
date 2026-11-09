# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "Minio ulash"
CATEGORY = "Minio"
TITLE = "MinIO ni Loyihaga Ulash"
SUBTITLE = "Obyekt ombori, sozlash va fayllar bilan ishlash"
FILENAME = "Minio ulash.docx"


def build(d):
    h1(d, "1. Obyekt ombori nima")

    para(d, "Obyekt ombori — fayllarni papka ierarxiyasi emas, kalit-qiymat "
            "juftligi sifatida saqlaydigan tizim. Har bir fayl noyob kalit "
            "bilan saqlanadi va HTTP orqali olinadi.")

    para(d, "MinIO — S3 bilan mos obyekt ombori. \"S3 bilan mos\" degani — "
            "Amazon S3 uchun yozilgan har qanday mijoz kutubxonasi MinIO "
            "bilan ham ishlaydi.")

    note(d, "Nima uchun fayllarni bazaga yoki diskka saqlamaslik kerak:",
         "Bazaga saqlasam, u shishib ketadi, zaxira nusxalar og'irlashadi "
         "va so'rovlar sekinlashadi. Serverning diskiga saqlasam, ilovani "
         "ikkinchi nusxada ishga tushira olmayman — chunki fayl faqat "
         "bitta mashinada bo'ladi. Obyekt ombori ikkala muammoni ham hal "
         "qiladi.")

    # ───────────────────────────────────────────
    h1(d, "2. Ishga tushirish")

    code(d, """services:
  minio:
    image: minio/minio:latest
    command: server /data --console-address ":9001"
    ports:
      - "9000:9000"      # API
      - "9001:9001"      # boshqaruv paneli
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: ${MINIO_PASSWORD}
    volumes:
      - minio_data:/data
    healthcheck:
      test: ["CMD", "mc", "ready", "local"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  minio_data:""")

    note(d, "Ikki port ajratilgani muhim:",
         "9000 — dasturlar ulanadigan API, 9001 — brauzerda ochiladigan "
         "boshqaruv paneli. Production da 9001 ni tashqariga ochmaslik "
         "kerak, chunki u orqali barcha fayllarga kirish mumkin.")

    # ───────────────────────────────────────────
    h1(d, "3. .NET dan ulanish")

    code(d, """dotnet add package Minio""")

    code(d, """public class MinioOptions
{
    public const string SectionName = "Minio";

    public string Endpoint { get; set; } = string.Empty;
    public string AccessKey { get; set; } = string.Empty;
    public string SecretKey { get; set; } = string.Empty;
    public bool UseSsl { get; set; }
    public string DefaultBucket { get; set; } = "uploads";
}""")

    code(d, """builder.Services
    .AddOptions<MinioOptions>()
    .Bind(builder.Configuration.GetSection(MinioOptions.SectionName))
    .ValidateDataAnnotations()
    .ValidateOnStart();

builder.Services.AddSingleton<IMinioClient>(sp =>
{
    var options = sp.GetRequiredService<IOptions<MinioOptions>>().Value;

    return new MinioClient()
        .WithEndpoint(options.Endpoint)
        .WithCredentials(options.AccessKey, options.SecretKey)
        .WithSSL(options.UseSsl)
        .Build();
});""")

    note(d, "Mijozni `Singleton` qilish to'g'ri:",
         "U ichkarida `HttpClient` ishlatadi va har so'rovda yangi nusxa "
         "yaratish soket tugashiga olib keladi. Mijozning o'zi oqim uchun "
         "xavfsiz, shuning uchun bitta nusxa barcha so'rovlarga yetadi.")

    # ───────────────────────────────────────────
    h1(d, "4. Asosiy amallar")

    h2(d, "4.1 Fayl yuklash")

    code(d, """public async Task<string> UploadAsync(
    IFormFile file, CancellationToken ct)
{
    var objectName = $"{DateTime.UtcNow:yyyy/MM/dd}/" +
                     $"{Guid.NewGuid()}{Path.GetExtension(file.FileName)}";

    await using var stream = file.OpenReadStream();

    await _minio.PutObjectAsync(
        new PutObjectArgs()
            .WithBucket(_options.DefaultBucket)
            .WithObject(objectName)
            .WithStreamData(stream)
            .WithObjectSize(file.Length)
            .WithContentType(file.ContentType)
            .WithHeaders(new Dictionary<string, string>
            {
                ["x-amz-meta-original-name"] = file.FileName
            }),
        ct);

    return objectName;
}""")

    note(d, "Kalit tuzilmasi haqida o'ylab topgan yechimim:",
         "Men sanaga qarab prefiks qo'yaman — `2026/10/31/...`. Obyekt "
         "omborida papka tushunchasi yo'q, lekin kalitdagi `/` belgisi "
         "boshqaruv panelida papka kabi ko'rsatiladi. Bu minglab faylni "
         "ko'rish va eskilarini tozalashni ancha osonlashtiradi.")

    note(d, "Asl fayl nomini kalit sifatida ishlatmaslik kerak:",
         "U takrorlanishi, maxsus belgilar tutishi va yo'ldan chiqish "
         "hujumiga imkon berishi mumkin. Men `Guid` ishlatib, asl nomni "
         "metama'lumotda saqlayman — shunda yuklab olishda uni tiklash "
         "mumkin.")

    h2(d, "4.2 Yuklab olish")

    code(d, """public async Task<Stream> DownloadAsync(
    string objectName, CancellationToken ct)
{
    var ms = new MemoryStream();

    await _minio.GetObjectAsync(
        new GetObjectArgs()
            .WithBucket(_options.DefaultBucket)
            .WithObject(objectName)
            .WithCallbackStream(stream => stream.CopyTo(ms)),
        ct);

    ms.Position = 0;
    return ms;
}""")

    h2(d, "4.3 Mavjudligini tekshirish va o'chirish")

    code(d, """// Metama'lumotni olish — mavjudligini ham tekshiradi
try
{
    var stat = await _minio.StatObjectAsync(
        new StatObjectArgs()
            .WithBucket(bucket)
            .WithObject(objectName),
        ct);

    Console.WriteLine($"Hajmi: {stat.Size}, Tipi: {stat.ContentType}");
}
catch (ObjectNotFoundException)
{
    return null;
}

// O'chirish
await _minio.RemoveObjectAsync(
    new RemoveObjectArgs().WithBucket(bucket).WithObject(objectName), ct);""")

    # ───────────────────────────────────────────
    h1(d, "5. Oldindan imzolangan havolalar")

    para(d, "Faylni ilova orqali uzatish uning trafigini mening serverim "
            "orqali o'tkazadi. Oldindan imzolangan havola esa mijozga "
            "to'g'ridan-to'g'ri MinIO dan olish imkonini beradi.")

    code(d, """// Yuklab olish uchun
var url = await _minio.PresignedGetObjectAsync(
    new PresignedGetObjectArgs()
        .WithBucket(bucket)
        .WithObject(objectName)
        .WithExpiry(60 * 15));      // 15 daqiqa

// Yuklash uchun — mijoz to'g'ridan-to'g'ri yuklaydi
var uploadUrl = await _minio.PresignedPutObjectAsync(
    new PresignedPutObjectArgs()
        .WithBucket(bucket)
        .WithObject(objectName)
        .WithExpiry(60 * 10));""")

    note(d, "Bu naqsh menga juda mantiqiy tuyuldi:",
         "Katta faylni yuklashda ilovam shunchaki vositachi bo'lib qoladi — "
         "u baytlarni qabul qilib, boshqa joyga uzatadi va shu davomida "
         "xotira hamda ulanish band qiladi. Imzolangan havola bilan esa "
         "ilova faqat ruxsat beradi, trafik esa undan chetlab o'tadi.")

    note(d, "Xavfsizlik jihati:",
         "Havola imzolangan va muddatli, lekin uni olgan har kim ishlata "
         "oladi. Shuning uchun muddatni iloji boricha qisqa qilaman va "
         "havolani faqat haqiqatan huquqi bor foydalanuvchiga beraman — "
         "ya'ni ruxsat tekshiruvi havola yaratishdan oldin bo'ladi.")

    # ───────────────────────────────────────────
    h1(d, "6. Xatoliklarni qayta ishlash")

    code(d, """try
{
    await _minio.PutObjectAsync(args, ct);
}
catch (BucketNotFoundException)
{
    _logger.LogError("Bucket topilmadi: {Bucket}", bucket);
    throw;
}
catch (AccessDeniedException)
{
    _logger.LogError("Kirish rad etildi — kalitlarni tekshiring");
    throw;
}
catch (ConnectionException ex)
{
    _logger.LogError(ex, "MinIO ga ulanib bo'lmadi");
    throw;
}""")

    h2(d, "6.1 Chidamlilik")

    code(d, """builder.Services.AddHttpClient("minio")
    .AddStandardResilienceHandler(options =>
    {
        options.Retry.MaxRetryAttempts = 3;
        options.AttemptTimeout.Timeout = TimeSpan.FromSeconds(30);
    });""")

    # ───────────────────────────────────────────
    h1(d, "7. Sog'liq tekshiruvi")

    code(d, """builder.Services.AddHealthChecks()
    .AddCheck<MinioHealthCheck>("minio");

public class MinioHealthCheck : IHealthCheck
{
    private readonly IMinioClient _minio;

    public async Task<HealthCheckResult> CheckHealthAsync(
        HealthCheckContext context, CancellationToken ct = default)
    {
        try
        {
            await _minio.ListBucketsAsync(ct);
            return HealthCheckResult.Healthy();
        }
        catch (Exception ex)
        {
            return HealthCheckResult.Unhealthy("MinIO javob bermayapti", ex);
        }
    }
}""")

    # ───────────────────────────────────────────
    h1(d, "8. Production uchun eslatmalar")

    bullets(d, [
        "Root hisob o'rniga alohida foydalanuvchi va cheklangan siyosat "
        "yaratish.",
        "HTTPS ishlatish — `UseSsl = true`.",
        "Boshqaruv panelini tashqariga ochmaslik.",
        "Bucket siyosatini aniq belgilash — sukut bo'yicha yopiq.",
        "Zaxira nusxa strategiyasini o'ylash — `mc mirror` yordam beradi.",
    ])

    code(d, """# Alohida foydalanuvchi yaratish
mc admin user add myminio app-user 'kuchli-parol'
mc admin policy attach myminio readwrite --user app-user""")

    # ───────────────────────────────────────────
    h1(d, "9. Xulosa")

    bullets(d, [
        "MinIO — S3 bilan mos obyekt ombori; S3 mijozlari u bilan "
        "ishlaydi.",
        "Fayllarni bazaga yoki lokal diskka saqlash miqyoslashni "
        "to'sadi.",
        "`IMinioClient` `Singleton` sifatida ro'yxatdan o'tkaziladi.",
        "Obyekt kalitida sanaga asoslangan prefiks tashkil qilishni "
        "osonlashtiradi.",
        "Asl fayl nomini kalit sifatida ishlatmaslik — `Guid` va "
        "metama'lumot afzal.",
        "Oldindan imzolangan havolalar trafikni ilovadan chetlab "
        "o'tkazadi.",
        "Havola muddati qisqa bo'lishi va ruxsat oldindan tekshirilishi "
        "kerak.",
        "Production da root hisob emas, cheklangan foydalanuvchi "
        "ishlatiladi.",
    ])

    sources(d, [
        ("MinIO Object Storage — rasmiy hujjat",
         "https://min.io/docs/minio/linux/index.html"),
        ("MinIO .NET SDK — GitHub",
         "https://github.com/minio/minio-dotnet"),
        ("Presigned URLs — MinIO hujjati",
         "https://min.io/docs/minio/linux/developers/dotnet/API.html"),
    ])
