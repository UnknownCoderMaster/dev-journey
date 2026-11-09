# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "Minio buckets (create, delete, temp bucket, edit)"
CATEGORY = "Minio"
TITLE = "MinIO Bucket larni Boshqarish"
SUBTITLE = "Yaratish, o'chirish, siyosat va avtomatik tozalash"
FILENAME = "Minio buckets (create, delete, temp bucket, edit).docx"


def build(d):
    h1(d, "1. Bucket nima")

    para(d, "Bucket — obyektlar saqlanadigan yuqori darajadagi idish. "
            "Har bir obyekt albatta biror bucket ga tegishli bo'ladi.")

    para(d, "Bucket papka emas — u ichma-ich joylashmaydi. Ierarxiya "
            "tuyg'usi obyekt kalitidagi `/` belgilari orqali hosil "
            "qilinadi, lekin bu shunchaki nom qismi.")

    h2(d, "1.1 Nomlash qoidalari")

    bullets(d, [
        "3 dan 63 belgigacha.",
        "Faqat kichik harflar, raqamlar, defis va nuqta.",
        "Harf yoki raqam bilan boshlanishi va tugashi kerak.",
        "IP manzil ko'rinishida bo'lmasligi lozim.",
        "Butun tizim bo'ylab noyob bo'lishi kerak.",
    ])

    code(d, """# To'g'ri
user-avatars
invoices-2026
app.documents

# Noto'g'ri
UserAvatars        # katta harf
my_bucket          # pastki chiziq
192.168.1.1        # IP ko'rinishi""")

    # ───────────────────────────────────────────
    h1(d, "2. Bucket yaratish")

    code(d, """public async Task EnsureBucketAsync(string bucket, CancellationToken ct)
{
    var exists = await _minio.BucketExistsAsync(
        new BucketExistsArgs().WithBucket(bucket), ct);

    if (exists)
        return;

    await _minio.MakeBucketAsync(
        new MakeBucketArgs().WithBucket(bucket), ct);

    _logger.LogInformation("Bucket yaratildi: {Bucket}", bucket);
}""")

    h2(d, "2.1 Ishga tushishda tayyorlash")

    code(d, """public class MinioInitializer : IHostedService
{
    private static readonly string[] RequiredBuckets =
        ["uploads", "avatars", "invoices", "temp"];

    public async Task StartAsync(CancellationToken ct)
    {
        foreach (var bucket in RequiredBuckets)
            await _storage.EnsureBucketAsync(bucket, ct);
    }

    public Task StopAsync(CancellationToken ct) => Task.CompletedTask;
}

builder.Services.AddHostedService<MinioInitializer>();""")

    note(d, "Bu yondashuv menga qulay tuyuldi:",
         "Ilova ishga tushganda kerakli bucket lar mavjudligi "
         "ta'minlanadi. Yangi muhitga joylashtirishda qo'lda hech narsa "
         "yaratish kerak emas. Lekin production da bu huquqni ilova "
         "foydalanuvchisiga berish kerakmi degan savol tug'iladi — "
         "ba'zan bucket yaratishni infratuzilma skriptiga qoldirish "
         "to'g'riroq.")

    # ───────────────────────────────────────────
    h1(d, "3. Bucket siyosati")

    para(d, "Sukut bo'yicha bucket yopiq — unga faqat autentifikatsiyadan "
            "o'tgan so'rovlar kira oladi. Siyosat orqali buni "
            "o'zgartirish mumkin.")

    code(d, """var policy = @"
{
  ""Version"": ""2012-10-17"",
  ""Statement"": [
    {
      ""Effect"": ""Allow"",
      ""Principal"": { ""AWS"": [""*""] },
      ""Action"": [""s3:GetObject""],
      ""Resource"": [""arn:aws:s3:::" + bucket + @"/public/*""]
    }
  ]
}";

await _minio.SetPolicyAsync(
    new SetPolicyArgs().WithBucket(bucket).WithPolicy(policy), ct);""")

    note(d, "Bu siyosatda `public/` prefiksi muhim:",
         "U butun bucket ni emas, faqat `public/` bilan boshlanadigan "
         "obyektlarni ochadi. Shunday qilib bitta bucket ichida ham ochiq, "
         "ham yopiq fayllarni saqlash mumkin. Butun bucket ni ochiq "
         "qilish — keng tarqalgan, lekin xavfli yechim.")

    code(d, """// Joriy siyosatni o'qish
var current = await _minio.GetPolicyAsync(
    new GetPolicyArgs().WithBucket(bucket), ct);""")

    # ───────────────────────────────────────────
    h1(d, "4. Vaqtinchalik bucket va avtomatik tozalash")

    para(d, "Vaqtinchalik fayllar — yuklanayotgan, lekin hali "
            "tasdiqlanmagan hujjatlar, eksport natijalari, qoralama "
            "rasmlar. Ularni qo'lda tozalash unutiladi, shuning uchun "
            "hayot sikli qoidasi qo'yiladi.")

    code(d, """var lifecycle = new LifecycleConfiguration
{
    Rules =
    [
        new LifecycleRule
        {
            ID = "expire-temp-files",
            Status = "Enabled",
            Filter = new RuleFilter { Prefix = "temp/" },
            Expiration = new Expiration { Days = 1 }
        },
        new LifecycleRule
        {
            ID = "expire-exports",
            Status = "Enabled",
            Filter = new RuleFilter { Prefix = "exports/" },
            Expiration = new Expiration { Days = 7 }
        }
    ]
};

await _minio.SetBucketLifecycleAsync(
    new SetBucketLifecycleArgs()
        .WithBucket(bucket)
        .WithLifecycleConfiguration(lifecycle),
    ct);""")

    code(d, """# mc buyrug'i orqali ham qilish mumkin
mc ilm rule add --expire-days 1 myminio/temp --prefix "temp/"
mc ilm rule ls myminio/temp""")

    note(d, "Bu mexanizm menga juda yoqdi:",
         "Avval men eski fayllarni tozalash uchun fon vazifasi yozgan "
         "edim — u har kecha ishga tushib, sanani tekshirib, o'chirardi. "
         "Hayot sikli qoidasi bilan esa bu kod butunlay keraksiz bo'ladi. "
         "MinIO buni o'zi, mening ilovamdan mustaqil bajaradi.")

    note(d, "Bitta eslatma bor:",
         "Hayot sikli qoidasi darhol ishlamaydi — u davriy ravishda "
         "tekshiriladi. Shuning uchun \"bir kundan keyin o'chadi\" degani "
         "aniq 24 soat emas, taxminan bir kun. Agar aniq vaqt muhim bo'lsa, "
         "bu mexanizm mos kelmaydi.")

    # ───────────────────────────────────────────
    h1(d, "5. Versiyalash")

    code(d, """await _minio.SetVersioningAsync(
    new SetVersioningArgs()
        .WithBucket(bucket)
        .WithVersioningEnabled(),
    ct);""")

    para(d, "Versiyalash yoqilganda obyekt ustiga yozish eskisini "
            "o'chirmaydi — yangi versiya yaratiladi. O'chirish ham "
            "haqiqiy o'chirish emas, o'chirish belgisi qo'yish bo'ladi.")

    note(d, "Bu tasodifiy o'chirishdan himoya qiladi, lekin narxi bor:",
         "Har bir versiya joy egallaydi va bucket hajmi tez o'sadi. "
         "Shuning uchun versiyalashni yoqsam, eski versiyalarni "
         "o'chiradigan hayot sikli qoidasini ham qo'shaman — aks holda "
         "disk bir necha oyda to'lib ketadi.")

    code(d, """new LifecycleRule
{
    ID = "expire-old-versions",
    Status = "Enabled",
    Filter = new RuleFilter { Prefix = "" },
    NoncurrentVersionExpiration = new NoncurrentVersionExpiration
    {
        NoncurrentDays = 30
    }
}""")

    # ───────────────────────────────────────────
    h1(d, "6. Obyektlarni ro'yxatlash")

    code(d, """public async Task<List<string>> ListAsync(
    string bucket, string prefix, CancellationToken ct)
{
    var result = new List<string>();

    var args = new ListObjectsArgs()
        .WithBucket(bucket)
        .WithPrefix(prefix)
        .WithRecursive(true);

    await foreach (var item in _minio.ListObjectsEnumAsync(args, ct))
        result.Add(item.Key);

    return result;
}""")

    note(d, "Ro'yxatlash qimmat operatsiya:",
         "Millionlab obyekt bo'lgan bucket da `ListObjects` juda sekin "
         "ishlaydi. Shuning uchun men obyekt kalitlarini bazada ham "
         "saqlayman — qidiruv va ro'yxat bazadan olinadi, MinIO esa faqat "
         "faylning o'zini beradi. Bu takrorlanishdek ko'rinadi, lekin "
         "amalda zarur.")

    # ───────────────────────────────────────────
    h1(d, "7. Bucket o'chirish")

    code(d, """// Bucket faqat bo'sh bo'lsa o'chadi
public async Task DeleteBucketAsync(string bucket, CancellationToken ct)
{
    var objects = new List<string>();

    await foreach (var item in _minio.ListObjectsEnumAsync(
        new ListObjectsArgs().WithBucket(bucket).WithRecursive(true), ct))
    {
        objects.Add(item.Key);
    }

    if (objects.Count > 0)
    {
        await _minio.RemoveObjectsAsync(
            new RemoveObjectsArgs().WithBucket(bucket).WithObjects(objects),
            ct);
    }

    await _minio.RemoveBucketAsync(
        new RemoveBucketArgs().WithBucket(bucket), ct);
}""")

    note(d, "Bu kodni ehtiyotkorlik bilan ishlatish kerak:",
         "U butun bucket ni bo'shatadi va o'chiradi — ortga qaytarib "
         "bo'lmaydi. Men bunday kodni ilovaning oddiy oqimiga umuman "
         "qo'ymayman; u faqat test muhitini tozalash skriptida bo'ladi.")

    # ───────────────────────────────────────────
    h1(d, "8. mc buyruqlari")

    code(d, """# Ulanish sozlash
mc alias set myminio http://localhost:9000 minioadmin parol

# Bucket amallari
mc mb myminio/invoices
mc ls myminio
mc ls myminio/invoices --recursive
mc rb myminio/old-bucket --force

# Fayl amallari
mc cp report.pdf myminio/invoices/
mc mirror ./local-folder myminio/backups/

# Siyosat
mc anonymous set download myminio/public
mc anonymous get myminio/public

# Hajm ma'lumoti
mc du myminio/invoices""")

    # ───────────────────────────────────────────
    h1(d, "9. Bucket tuzilmasini loyihalash")

    table(d, ["Yondashuv", "Afzalligi", "Kamchiligi"],
          [["Har maqsadga alohida bucket",
            "Siyosat va hayot sikli aniq", "Bucket lar ko'payadi"],
           ["Bitta bucket, prefikslar bilan",
            "Boshqarish oson", "Siyosat nozik sozlanmaydi"],
           ["Har ijarachiga alohida bucket",
            "To'liq izolyatsiya", "Miqyoslash cheklovi bor"]],
          widths=[5.0, 5.3, 5.2])

    note(d, "Mening tanlovim:",
         "Maqsad bo'yicha ajrataman — `avatars`, `invoices`, `temp`. "
         "Sababi shundaki, ularning hayot sikli va siyosati butunlay "
         "boshqacha: avatarlar ochiq va doimiy, hisob-fakturalar yopiq va "
         "uzoq saqlanadi, vaqtinchalik fayllar esa bir kunda o'chadi. "
         "Bitta bucket da bu qoidalarni ajratish ancha qiyin bo'lardi.")

    # ───────────────────────────────────────────
    h1(d, "10. Xulosa")

    bullets(d, [
        "Bucket — obyektlar uchun yuqori darajadagi idish; u ichma-ich "
        "joylashmaydi.",
        "Nom kichik harflar, raqam, defis va nuqtadan iborat bo'lishi "
        "kerak.",
        "`BucketExistsAsync` + `MakeBucketAsync` — ishga tushishda "
        "tayyorlashning odatiy usuli.",
        "Siyosatni butun bucket ga emas, prefiksga qo'llash xavfsizroq.",
        "Hayot sikli qoidalari vaqtinchalik fayllarni avtomatik tozalaydi "
        "— fon vazifasi kerak bo'lmaydi.",
        "Qoida darhol emas, davriy tekshiruvda ishlaydi.",
        "Versiyalash tasodifiy o'chirishdan himoya qiladi, lekin eski "
        "versiyalar uchun tozalash qoidasi kerak.",
        "Obyektlarni ro'yxatlash qimmat — kalitlarni bazada ham saqlash "
        "foydali.",
    ])

    sources(d, [
        ("MinIO Object Storage — Buckets",
         "https://min.io/docs/minio/linux/administration/console/managing-objects.html"),
        ("Object Lifecycle Management — MinIO",
         "https://min.io/docs/minio/linux/administration/object-management/object-lifecycle-management.html"),
        ("MinIO Client (mc) — Reference",
         "https://min.io/docs/minio/linux/reference/minio-mc.html"),
        ("MinIO .NET SDK — GitHub",
         "https://github.com/minio/minio-dotnet"),
    ])
