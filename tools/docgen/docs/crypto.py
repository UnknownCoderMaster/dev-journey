# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "Hashing, Symmetric Encryption, Public-Key Encryption and Signing"
CATEGORY = ".NET / C#"
TITLE = "Hashlash, Shifrlash va Imzolash"
SUBTITLE = "Kriptografiya asoslari va .NET dagi amalga oshirilishi"
FILENAME = "Hashing, Symmetric Encryption, Public-Key Encryption and Signing.docx"


def build(d):
    h1(d, "1. Uch xil vazifa")

    para(d, "Kriptografiyaning uch asosiy qo'llanishi bor va ularni "
            "chalkashtirmaslik muhim:")

    table(d, ["Vazifa", "Vosita", "Teskari aylantirish"],
          [["Barmoq izi olish", "Hash", "Mumkin emas"],
           ["Maxfiylikni saqlash", "Shifrlash", "Kalit bilan mumkin"],
           ["Haqiqiyligini tasdiqlash", "Imzo", "Tekshirish mumkin"]],
          widths=[4.4, 4.6, 6.5])

    note(d, "Eng ko'p uchraydigan chalkashlik:",
         "\"Parolni shifrlash\" degan ibora noto'g'ri. Parol "
         "shifrlanmaydi — u hashlanadi. Farq shundaki, shifrlangan "
         "narsani ochib bo'ladi, hashlangan narsani esa yo'q. Agar "
         "tizim parolni ochib bera olsa, demak u noto'g'ri "
         "saqlanayotgan.")

    # ───────────────────────────────────────────
    h1(d, "2. Hashlash")

    para(d, "Hash funksiyasi istalgan uzunlikdagi ma'lumotdan qat'iy "
            "uzunlikdagi qiymat hosil qiladi. Bir xil kirishdan doim bir "
            "xil natija chiqadi, lekin natijadan kirishni tiklab "
            "bo'lmaydi.")

    code(d, """using System.Security.Cryptography;

var data = File.ReadAllBytes("document.pdf");
var hash = SHA256.HashData(data);

Console.WriteLine(Convert.ToHexString(hash));""")

    code(d, """// Oqim uchun — katta fayllarda xotirani tejaydi
await using var stream = File.OpenRead("large-file.zip");
var hash = await SHA256.HashDataAsync(stream, ct);""")

    h2(d, "2.1 Qaysi algoritm")

    table(d, ["Algoritm", "Holati", "Qachon"],
          [["`MD5`", "Buzilgan", "Faqat nokriptografik tekshiruv"],
           ["`SHA-1`", "Buzilgan", "Ishlatilmaydi"],
           ["`SHA-256`", "Xavfsiz", "Umumiy maqsad"],
           ["`SHA-512`", "Xavfsiz", "Yuqori talab"],
           ["`SHA-3`", "Xavfsiz", "Muqobil variant"]],
          widths=[3.0, 3.6, 8.9])

    h2(d, "2.2 Parollar uchun alohida algoritmlar")

    note(d, "Oddiy hash parol uchun yaramaydi:",
         "`SHA-256` juda tez ishlaydi — zamonaviy videokarta sekundiga "
         "milliardlab hash hisoblay oladi. Ya'ni tajovuzkor lug'atdagi "
         "barcha parollarni tez sinab chiqadi. Parol uchun ataylab "
         "sekin funksiyalar kerak.")

    code(d, """// PBKDF2 — platformada mavjud
var salt = RandomNumberGenerator.GetBytes(16);

var hash = Rfc2898DeriveBytes.Pbkdf2(
    password: password,
    salt: salt,
    iterations: 600_000,
    hashAlgorithm: HashAlgorithmName.SHA256,
    outputLength: 32);""")

    code(d, """// Taqqoslash — doimiy vaqtda
var isValid = CryptographicOperations.FixedTimeEquals(computed, stored);""")

    # ───────────────────────────────────────────
    h1(d, "3. HMAC — kalit bilan hash")

    para(d, "HMAC ma'lumot o'zgarmaganini va uni maxfiy kalitni "
            "biladigan tomon yaratganini tasdiqlaydi.")

    code(d, """var key = Convert.FromBase64String(secretKey);
var payload = Encoding.UTF8.GetBytes(jsonBody);

var signature = HMACSHA256.HashData(key, payload);
var header = Convert.ToBase64String(signature);""")

    code(d, """// Webhook ni tekshirish
public bool VerifyWebhook(string body, string receivedSignature)
{
    var expected = HMACSHA256.HashData(
        _key, Encoding.UTF8.GetBytes(body));

    var received = Convert.FromBase64String(receivedSignature);

    return CryptographicOperations.FixedTimeEquals(expected, received);
}""")

    note(d, "Webhook larni tekshirish — HMAC ning eng keng tarqalgan "
            "qo'llanishi:",
         "To'lov tizimi menga xabar yuboradi va men uning haqiqatan "
         "o'sha tizimdan kelganiga ishonch hosil qilishim kerak. HMAC "
         "aynan shuni beradi — kalitni bilmagan odam to'g'ri imzo "
         "yarata olmaydi.")

    # ───────────────────────────────────────────
    h1(d, "4. Simmetrik shifrlash")

    para(d, "Simmetrik shifrlashda bir xil kalit ham shifrlash, ham "
            "ochish uchun ishlatiladi. U tez va katta hajmli ma'lumot "
            "uchun mos.")

    code(d, """// AES-GCM — tavsiya etiladigan rejim
public static byte[] Encrypt(byte[] plaintext, byte[] key)
{
    var nonce = RandomNumberGenerator.GetBytes(AesGcm.NonceByteSizes.MaxSize);
    var ciphertext = new byte[plaintext.Length];
    var tag = new byte[AesGcm.TagByteSizes.MaxSize];

    using var aes = new AesGcm(key, tag.Length);
    aes.Encrypt(nonce, plaintext, ciphertext, tag);

    // nonce + tag + ciphertext ni birlashtirib saqlaymiz
    var result = new byte[nonce.Length + tag.Length + ciphertext.Length];
    nonce.CopyTo(result, 0);
    tag.CopyTo(result, nonce.Length);
    ciphertext.CopyTo(result, nonce.Length + tag.Length);

    return result;
}""")

    code(d, """public static byte[] Decrypt(byte[] data, byte[] key)
{
    var nonceSize = AesGcm.NonceByteSizes.MaxSize;
    var tagSize = AesGcm.TagByteSizes.MaxSize;

    var nonce = data[..nonceSize];
    var tag = data[nonceSize..(nonceSize + tagSize)];
    var ciphertext = data[(nonceSize + tagSize)..];

    var plaintext = new byte[ciphertext.Length];

    using var aes = new AesGcm(key, tagSize);
    aes.Decrypt(nonce, ciphertext, tag, plaintext);

    return plaintext;
}""")

    note(d, "GCM rejimining afzalligi:",
         "U nafaqat shifrlaydi, balki butunlikni ham tekshiradi. Agar "
         "shifrlangan ma'lumot o'zgartirilgan bo'lsa, `Decrypt` "
         "xatolik beradi. Oddiy CBC rejimida esa buzilgan ma'lumot "
         "jimgina noto'g'ri natija beradi va men buni sezmasligim "
         "mumkin.")

    note(d, "Nonce haqidagi qoida juda qat'iy:",
         "Bir xil kalit bilan bir xil nonce ni **ikki marta ishlatish "
         "mumkin emas**. Bu GCM da butun himoyani buzadi — kalitni "
         "tiklash imkonini beradi. Shuning uchun nonce har safar "
         "tasodifiy generatsiya qilinishi kerak va u shifrlangan "
         "ma'lumot bilan birga saqlanadi (u maxfiy emas).")

    h2(d, "4.1 Kalitlarni boshqarish")

    code(d, """// Parol asosida kalit hosil qilish
var salt = RandomNumberGenerator.GetBytes(16);

var key = Rfc2898DeriveBytes.Pbkdf2(
    password, salt, 600_000, HashAlgorithmName.SHA256, 32);""")

    note(d, "Kalitlarni saqlash — shifrlashdan ko'ra qiyinroq masala:",
         "Algoritm to'g'ri bo'lsa ham, kalit kod ichida yoki "
         "konfiguratsiya faylida tursa, butun himoya ma'nosiz. Kalit "
         "sir omborida yoki apparat moduli ichida bo'lishi kerak.")

    # ───────────────────────────────────────────
    h1(d, "5. Asimmetrik shifrlash")

    para(d, "Asimmetrik kriptografiyada kalit juftligi ishlatiladi: "
            "ochiq kalit bilan shifrlangan narsani faqat maxfiy kalit "
            "ocha oladi.")

    code(d, """using var rsa = RSA.Create(3072);

// Kalitlarni eksport qilish
var publicKey = rsa.ExportSubjectPublicKeyInfoPem();
var privateKey = rsa.ExportPkcs8PrivateKeyPem();

// Shifrlash — ochiq kalit bilan
var encrypted = rsa.Encrypt(data, RSAEncryptionPadding.OaepSHA256);

// Ochish — maxfiy kalit bilan
var decrypted = rsa.Decrypt(encrypted, RSAEncryptionPadding.OaepSHA256);""")

    note(d, "RSA katta ma'lumotni shifrlay olmaydi:",
         "3072 bitli kalit bilan taxminan 300 baytgacha shifrlash "
         "mumkin. Shuning uchun amalda gibrid sxema ishlatiladi: "
         "tasodifiy AES kaliti yaratiladi, ma'lumot u bilan "
         "shifrlanadi, AES kaliti esa RSA bilan shifrlanadi. TLS ham "
         "aynan shunday ishlaydi.")

    code(d, """// Gibrid sxema
var aesKey = RandomNumberGenerator.GetBytes(32);
var encryptedData = EncryptWithAes(largeData, aesKey);
var encryptedKey = rsa.Encrypt(aesKey, RSAEncryptionPadding.OaepSHA256);

// Qabul qiluvchi: avval kalitni ochadi, keyin ma'lumotni""")

    # ───────────────────────────────────────────
    h1(d, "6. Raqamli imzo")

    para(d, "Imzo shifrlashning teskarisi: maxfiy kalit bilan imzolanadi, "
            "ochiq kalit bilan tekshiriladi. U ma'lumotni yashirmaydi, "
            "faqat uning manbasini va o'zgarmaganini tasdiqlaydi.")

    code(d, """// Imzolash
using var rsa = RSA.Create();
rsa.ImportFromPem(privateKeyPem);

var signature = rsa.SignData(
    data,
    HashAlgorithmName.SHA256,
    RSASignaturePadding.Pss);""")

    code(d, """// Tekshirish
using var verifier = RSA.Create();
verifier.ImportFromPem(publicKeyPem);

var isValid = verifier.VerifyData(
    data, signature,
    HashAlgorithmName.SHA256,
    RSASignaturePadding.Pss);""")

    h2(d, "6.1 ECDSA — zamonaviyroq muqobil")

    code(d, """using var ecdsa = ECDsa.Create(ECCurve.NamedCurves.nistP256);

var signature = ecdsa.SignData(data, HashAlgorithmName.SHA256);
var isValid = ecdsa.VerifyData(data, signature, HashAlgorithmName.SHA256);""")

    table(d, ["Jihat", "RSA", "ECDSA"],
          [["Kalit hajmi", "3072 bit", "256 bit"],
           ["Imzo hajmi", "384 bayt", "64 bayt"],
           ["Imzolash tezligi", "Sekinroq", "Tezroq"],
           ["Qo'llab-quvvatlanishi", "Hamma joyda", "Keng, lekin kamroq"]],
          widths=[4.0, 5.4, 6.1])

    note(d, "Teng xavfsizlik darajasida ECDSA ancha ixcham:",
         "256 bitli elliptik egri chiziq kaliti taxminan 3072 bitli RSA "
         "kalitiga teng kuchga ega. Bu ayniqsa cheklangan muhitlarda — "
         "mobil qurilma, IoT — sezilarli afzallik beradi.")

    # ───────────────────────────────────────────
    h1(d, "7. Amaliy qoidalar")

    bullets(d, [
        "O'z kriptografik algoritmingizni yozmaslik.",
        "Tasodifiy qiymatlar uchun `RandomNumberGenerator`, `Random` "
        "emas.",
        "Taqqoslash uchun `CryptographicOperations.FixedTimeEquals`.",
        "`MD5` va `SHA-1` ni xavfsizlik maqsadida ishlatmaslik.",
        "Shifrlash uchun AES-GCM, imzo uchun ECDSA yoki RSA-PSS.",
        "Kalitlarni sir omborida saqlash va muntazam almashtirish.",
        "Ishlatilgan kalit materialini `Clear()` bilan tozalash.",
    ])

    code(d, """// Xavfli
var token = new Random().Next().ToString();

// Xavfsiz
var token = Convert.ToBase64String(RandomNumberGenerator.GetBytes(32));""")

    note(d, "Eng muhim maslahat — o'zim yozmaslik:",
         "Kriptografiyada xatolik qilish juda oson va u ko'rinmaydi — "
         "kod ishlaydi, test o'tadi, lekin himoya yo'q. Platformadagi "
         "tayyor API lar mutaxassislar tomonidan yozilgan va "
         "tekshirilgan. Men faqat ularni to'g'ri chaqirishim kerak.")

    # ───────────────────────────────────────────
    h1(d, "8. Xulosa")

    bullets(d, [
        "Hash — qaytarilmaydi, shifrlash — kalit bilan ochiladi, imzo — "
        "manbani tasdiqlaydi.",
        "Parol shifrlanmaydi, hashlanadi — va oddiy hash bilan emas, "
        "ataylab sekin funksiya bilan.",
        "`MD5` va `SHA-1` xavfsizlik uchun yaroqsiz.",
        "HMAC kalit bilan hash hosil qiladi va webhook larni tekshirish "
        "uchun ishlatiladi.",
        "AES-GCM shifrlash bilan birga butunlikni ham tekshiradi.",
        "Bir xil kalit bilan nonce ni ikki marta ishlatish mumkin emas.",
        "RSA katta ma'lumotni shifrlay olmaydi — gibrid sxema "
        "ishlatiladi.",
        "ECDSA teng xavfsizlikda RSA dan ancha ixcham.",
        "Tasodifiy qiymatlar uchun faqat `RandomNumberGenerator`.",
    ])

    sources(d, [
        ("Cryptography model — .NET",
         "https://learn.microsoft.com/en-us/dotnet/standard/security/cryptography-model"),
        ("Cross-platform cryptography in .NET",
         "https://learn.microsoft.com/en-us/dotnet/standard/security/cross-platform-cryptography"),
        ("OWASP Cryptographic Storage Cheat Sheet",
         "https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html"),
        ("NIST SP 800-57 — Key Management",
         "https://csrc.nist.gov/pubs/sp/800/57/pt1/r5/final"),
    ])
