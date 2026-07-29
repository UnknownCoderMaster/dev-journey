# Minio — Object Storage — Middle D

## 1. Nima? (Ta'rif)

**Minio** — **S3-compatible** (Amazon S3 API'siga mos) ochiq kodli
**Object Storage** tizimi — fayllarni (rasm, hujjat, video) **bucket**
larda saqlash uchun mo'ljallangan, o'z serveringizda (self-hosted)
ishlaydigan yechim.

## 2. Nima uchun kerak?

Fayllarni **to'g'ridan** DB'da (BLOB) yoki server diskida saqlash —
katta hajmda **samarasiz** va **masshtablanmaydigan**. Object
Storage — fayllarni **alohida, ixtisoslashgan** xizmatda saqlaydi,
DB esa faqat **URL/metadata**ni saqlaydi.

## 3. Ichida nima sodir bo'ladi? (Mexanizm)

### 3.1 AWS S3 bilan farqi

```
Minio — SELF-HOSTED (o'z serveringizda/Docker'da ishga tushirasiz),
        BEPUL, S3 API bilan TO'LIQ mos

AWS S3 — Amazon'ning CLOUD xizmati, TO'LOVLI, infratuzilmani
          AMAZON boshqaradi

Ikkalasi HAM BIR XIL API (`PutObject`, `GetObject` va h.k.) —
kodni O'ZGARTIRMASDAN Minio'dan S3'ga (yoki teskarisiga) O'TISH
MUMKIN.
```

### 3.2 Bucket va Object

```
Bucket — "papka" (aslida — NOYOB nomga ega, tekis konteyner)
Object — bucket ICHIDAGI HAR BIR fayl (nomi, ma'lumoti, metadata bilan)

bucket: "employee-documents"
  object: "contracts/2026/employee-42-contract.pdf"
  object: "photos/employee-42-photo.jpg"
```

### 3.3 NuGet va DI

```bash
dotnet add package Minio --version 6.0.2
```

```csharp
builder.Services.AddSingleton<IMinioClient>(sp =>
    new MinioClient()
        .WithEndpoint(builder.Configuration["Minio:Endpoint"])
        .WithCredentials(builder.Configuration["Minio:AccessKey"], builder.Configuration["Minio:SecretKey"])
        .WithSSL(builder.Environment.IsProduction())
        .Build());
```

### 3.4 Bucket yaratish, borligini tekshirish

```csharp
public async Task EnsureBucketExistsAsync(string bucketName)
{
    bool exists = await _minioClient.BucketExistsAsync(
        new BucketExistsArgs().WithBucket(bucketName));

    if (!exists)
        await _minioClient.MakeBucketAsync(new MakeBucketArgs().WithBucket(bucketName));
}
```

### 3.5 Fayl yuklash (PutObject)

```csharp
public async Task UploadFileAsync(string bucketName, string objectName, Stream fileStream, string contentType)
{
    await _minioClient.PutObjectAsync(new PutObjectArgs()
        .WithBucket(bucketName)
        .WithObject(objectName)
        .WithStreamData(fileStream)
        .WithObjectSize(fileStream.Length)
        .WithContentType(contentType));
}
```

### 3.6 Fayl yuklab olish (GetObject)

```csharp
public async Task<MemoryStream> DownloadFileAsync(string bucketName, string objectName)
{
    var memoryStream = new MemoryStream();
    await _minioClient.GetObjectAsync(new GetObjectArgs()
        .WithBucket(bucketName)
        .WithObject(objectName)
        .WithCallbackStream(stream => stream.CopyTo(memoryStream)));

    memoryStream.Position = 0;
    return memoryStream;
}
```

### 3.7 Ro'yxat olish (ListObjects)

```csharp
var objects = new List<string>();
var observable = _minioClient.ListObjectsAsync(new ListObjectsArgs()
    .WithBucket(bucketName)
    .WithPrefix("contracts/2026/")
    .WithRecursive(true));

observable.Subscribe(item => objects.Add(item.Key));
```

### 3.8 O'chirish (RemoveObject)

```csharp
await _minioClient.RemoveObjectAsync(new RemoveObjectArgs()
    .WithBucket(bucketName)
    .WithObject(objectName));
```

### 3.9 Presigned URL — vaqtinchalik URL yaratish

```csharp
var presignedUrl = await _minioClient.PresignedGetObjectAsync(new PresignedGetObjectArgs()
    .WithBucket(bucketName)
    .WithObject(objectName)
    .WithExpiry(60 * 60)); // 1 soat amal qiladi
```

```
Presigned URL — PRIVATE bucket'dagi faylga, VAQTINCHA (belgilangan
muddat ichida) TO'G'RIDAN kirish imkonini beruvchi URL. Bu — API
serverini "oraliq qatlam" sifatida ISHLATMASDAN, client
brauzerining TO'G'RIDAN Minio'dan fayl yuklab olishiga (yoki
yuklashiga) IMKON BERADI — API serverga YUKLAMA TUSHMAYDI.
```

### 3.10 Access Policy — public, private

```csharp
// Bucket'ni PUBLIC qilish (hamma o'qiy oladi)
string policy = @"{
  ""Version"": ""2012-10-17"",
  ""Statement"": [{
    ""Effect"": ""Allow"", ""Principal"": ""*"",
    ""Action"": [""s3:GetObject""], ""Resource"": [""arn:aws:s3:::public-bucket/*""]
  }]
}";
await _minioClient.SetPolicyAsync(new SetPolicyArgs().WithBucket("public-bucket").WithPolicy(policy));
```

```
⚠️ ERP kabi maxfiy hujjatlar uchun — bucket HAR DOIM PRIVATE
   bo'lishi kerak, kirish FAQAT Presigned URL orqali (vaqtinchalik,
   nazoratli).
```

## 4. Kod — Docker'da local development

```yaml
# docker-compose.yml
services:
  minio:
    image: minio/minio
    ports:
      - "9000:9000"  # API
      - "9001:9001"  # Console
    environment:
      MINIO_ROOT_USER: admin
      MINIO_ROOT_PASSWORD: password123
    command: server /data --console-address ":9001"
    volumes:
      - minio_data:/data
volumes:
  minio_data:
```

```json
// appsettings.json
{
  "Minio": { "Endpoint": "localhost:9000", "AccessKey": "admin", "SecretKey": "password123" }
}
```

## 5. Qachon ishlatish kerak?

| Vaziyat | Yechim |
|---|---|
| Xodim rasmi, hujjat, fayl saqlash | Minio bucket |
| Fayl maxfiy, faqat egasi kirishi kerak | Private bucket + Presigned URL |
| Fayl hammaga ochiq (masalan logo) | Public bucket |
| Cloud'ga bog'lanmaslik, o'z serverda saqlash | Minio (S3 o'rniga) |

## 6. Muhim nuqtalar

- Fayllarni DB'da BLOB sifatida saqlash — katta hajmda DB
  performance'ini YOMONLASHTIRADI, Object Storage doim afzal.
- Presigned URL — API serverni "oraliq" qilmasdan, YUKLAMANI
  KAMAYTIRADI.
- Access Key/Secret Key — HECH QACHON kodga hardcode qilinmasin —
  Environment variable/Secret Manager orqali.

## 7. Imtihon savollari

1. Object Storage nima va u nima uchun DB'da BLOB saqlashdan
   afzalroq?
2. Bucket va Object orasidagi farq nima?
3. Presigned URL nima va u qanday amaliy foyda beradi (API
   serverga yuklama nuqtai nazaridan)?
4. Minio va AWS S3 orasidagi farq nima, va nima uchun kod BIR
   XIL API bilan ishlaydi?
5. ERP tizimida maxfiy hujjatlar uchun qaysi Access Policy
   ishlatilishi kerak?
