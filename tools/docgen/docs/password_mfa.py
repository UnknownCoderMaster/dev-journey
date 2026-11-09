# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "Password-based authentication, Multi-factor authentication"
CATEGORY = "Auth"
TITLE = "Parol va Ko'p Faktorli Autentifikatsiya"
SUBTITLE = "Parollarni to'g'ri saqlash va ikkinchi himoya qatlamini qo'shish"
FILENAME = "Password-based authentication, Multi-factor authentication.docx"


def build(d):
    h1(d, "1. Autentifikatsiya va avtorizatsiya")

    para(d, "Ikki atama tez-tez chalkashtiriladi. Autentifikatsiya — foydalanuvchi "
            "kimligini aniqlash. Avtorizatsiya — aniqlangan foydalanuvchiga nima "
            "qilishga ruxsat borligini tekshirish.")

    para(d, "Ketma-ketlik har doim bir xil: avval kimligi aniqlanadi, keyin ruxsati "
            "tekshiriladi. HTTP status kodlari ham shuni aks ettiradi — `401` "
            "autentifikatsiya muammosi, `403` avtorizatsiya muammosi.")

    # ───────────────────────────────────────────
    h1(d, "2. Parolni saqlash")

    para(d, "Parolni bazada ochiq matnda saqlash qabul qilinmaydi. Oddiy hash "
            "funksiyasi — `MD5`, `SHA-1`, hatto `SHA-256` — ham yetarli emas, "
            "chunki ular tez ishlaydi va zamonaviy uskunada sekundiga milliardlab "
            "variant sinab ko'rish mumkin.")

    para(d, "Parol uchun maxsus, **ataylab sekin** funksiyalar mo'ljallangan:")

    table(d, ["Algoritm", "Holati"],
          [["`Argon2id`", "Hozirgi tavsiya; xotira talabi ham sozlanadi"],
           ["`bcrypt`", "Keng tarqalgan, ishonchli"],
           ["`PBKDF2`", "Standartlarga mos; `.NET` da o'rnatilgan"],
           ["`scrypt`", "Xotira talab qiladi, yaxshi"],
           ["`MD5`, `SHA-*`", "Parol uchun **yaramaydi**"]],
          widths=[4.0, 11.5])

    note(d, "\"Sekin\" so'zi bu yerda ijobiy ma'noda:",
         "Agar hash hisoblash 200 millisekund olsa, haqiqiy foydalanuvchi buni "
         "sezmaydi — u yiliga bir necha marta tizimga kiradi. Parollarni "
         "saralayotgan tajovuzkor esa sekundiga beshta variant sinay oladi, "
         "milliardlab emas. Bu farq butun himoyani belgilaydi.")

    h2(d, "2.1 Tuz (salt)")

    para(d, "Har bir parol uchun tasodifiy tuz yaratiladi va hash bilan birga "
            "saqlanadi. Tuz ikki vazifani bajaradi: bir xil parollar turli hash "
            "beradi, va oldindan hisoblangan jadvallar (rainbow table) ishlamaydi.")

    code(d, """// .NET da PBKDF2
public static string HashPassword(string password)
{
    var salt = RandomNumberGenerator.GetBytes(16);

    var hash = Rfc2898DeriveBytes.Pbkdf2(
        password: password,
        salt: salt,
        iterations: 600_000,
        hashAlgorithm: HashAlgorithmName.SHA256,
        outputLength: 32);

    return $"{Convert.ToBase64String(salt)}.{Convert.ToBase64String(hash)}";
}""")

    code(d, """public static bool Verify(string password, string stored)
{
    var parts = stored.Split('.');
    var salt = Convert.FromBase64String(parts[0]);
    var expected = Convert.FromBase64String(parts[1]);

    var actual = Rfc2898DeriveBytes.Pbkdf2(
        password, salt, 600_000, HashAlgorithmName.SHA256, 32);

    return CryptographicOperations.FixedTimeEquals(actual, expected);
}""")

    note(d, "`FixedTimeEquals` nega oddiy `==` emas:",
         "Oddiy taqqoslash birinchi farq topilgan joyda to'xtaydi. Demak to'g'ri "
         "boshlangan hash biroz uzoqroq tekshiriladi. Bu farq mikrosekundlarda "
         "bo'lsa ham, ko'p marta o'lchash orqali undan foydalanish mumkin — bu "
         "timing attack deb ataladi. `FixedTimeEquals` har doim bir xil vaqt "
         "sarflaydi.")

    h2(d, "2.2 ASP.NET Core Identity")

    para(d, "Amalda hash ni qo'lda yozish shart emas — Identity buni o'zi qiladi va "
            "algoritm versiyasini ham hash ichida saqlaydi:")

    code(d, """builder.Services
    .AddIdentityCore<AppUser>(options =>
    {
        options.Password.RequiredLength = 12;
        options.Password.RequireDigit = true;
        options.Password.RequireUppercase = true;
        options.Password.RequireNonAlphanumeric = false;

        options.Lockout.MaxFailedAccessAttempts = 5;
        options.Lockout.DefaultLockoutTimeSpan = TimeSpan.FromMinutes(15);

        options.User.RequireUniqueEmail = true;
    })
    .AddEntityFrameworkStores<AppDbContext>();""")

    note(d, "Parol talablari haqida fikrim o'zgargan:",
         "Avval \"murakkab parol\" degani katta harf, raqam va belgi bo'lishi deb "
         "o'ylardim. Keyin NIST tavsiyalarini o'qib, boshqacha tushundim: "
         "**uzunlik murakkablikdan muhimroq**. `P@ssw0rd!` talablarga javob "
         "beradi, lekin saralash lug'atida bor. `men kecha kitob o'qidim` esa "
         "ancha mustahkam. Shuning uchun men uzunlikni oshirib, majburiy belgi "
         "talabini yumshataman.")

    # ───────────────────────────────────────────
    h1(d, "3. Parol bilan bog'liq boshqa choralar")

    bullets(d, [
        "**Lockout** — ketma-ket noto'g'ri urinishlardan keyin hisobni vaqtincha "
        "bloklash.",
        "**Rate limiting** — bitta IP dan kelgan kirish urinishlarini cheklash.",
        "**Ma'lum bo'lib ketgan parollarni rad etish** — ommaviy sizib chiqqan "
        "parollar ro'yxati bilan solishtirish.",
        "**Parolni tiklash havolasini qisqa muddatli qilish** — 15-30 daqiqa.",
        "**Parol o'zgarganda barcha sessiyalarni bekor qilish.**",
    ])

    note(d, "Xatolik xabari haqida nozik nuqta:",
         "\"Bunday foydalanuvchi yo'q\" va \"Parol noto'g'ri\" degan ikki xil javob "
         "tajovuzkorga qaysi email lar ro'yxatdan o'tganini aytib beradi. Shuning "
         "uchun ikkala holatda ham bitta umumiy xabar qaytarish kerak: "
         "\"Email yoki parol noto'g'ri\".")

    # ───────────────────────────────────────────
    h1(d, "4. Ko'p faktorli autentifikatsiya")

    para(d, "MFA — kimlikni tasdiqlash uchun bir nechta mustaqil dalil talab qilish. "
            "Dalillar uch toifaga bo'linadi:")

    table(d, ["Toifa", "Misollar"],
          [["Bilgan narsasi", "Parol, PIN, maxfiy savol"],
           ["Egalik qilgan narsasi", "Telefon, apparat kalit, autentifikator ilovasi"],
           ["O'zi bo'lgan narsasi", "Barmoq izi, yuz, ovoz"]],
          widths=[4.4, 11.1])

    para(d, "Haqiqiy ko'p faktorli bo'lishi uchun dalillar **turli toifalardan** "
            "bo'lishi kerak. Parol va maxfiy savol — ikkalasi ham \"bilgan narsasi\", "
            "shuning uchun bu MFA emas.")

    h2(d, "4.1 Usullarni taqqoslash")

    table(d, ["Usul", "Xavfsizligi", "Qulayligi"],
          [["SMS kod", "Past — SIM almashtirish xavfi", "Yuqori"],
           ["Email kod", "Past — email o'zi buzilishi mumkin", "Yuqori"],
           ["TOTP ilovasi", "Yaxshi", "O'rtacha"],
           ["Push bildirishnoma", "Yaxshi", "Yuqori"],
           ["Apparat kalit (FIDO2)", "Eng yuqori", "Past"]],
          widths=[4.4, 6.0, 5.1])

    note(d, "SMS haqida ochiq gapirish kerak:",
         "SMS orqali kod yuborish MFA bo'lmagandan yaxshiroq, lekin eng zaif usul. "
         "SIM kartani qayta chiqartirish yoki operator orqali kodni ushlab qolish "
         "holatlari ma'lum. NIST ham SMS ni tavsiya etilmaydigan usullar qatoriga "
         "kiritgan. Shunga qaramay men uni ba'zan qoldiraman — chunki foydalanuvchilar "
         "uchun eng tushunarli usul va MFA umuman yo'qligidan ko'ra yaxshiroq.")

    h2(d, "4.2 TOTP qanday ishlaydi")

    para(d, "TOTP (Time-based One-Time Password) server va ilova o'rtasida bir marta "
            "umumiy sir almashishga asoslanadi. Keyin har ikki tomon ham joriy vaqt "
            "va shu sir asosida bir xil kodni mustaqil hisoblaydi.")

    bullets(d, [
        "Sir odatda QR kod orqali uzatiladi.",
        "Kod 30 soniyada bir yangilanadi.",
        "Internet aloqasi kerak emas — hisoblash lokal.",
        "Soat farqi uchun bir-ikki oynalik bag'rikenglik qoldiriladi.",
    ])

    code(d, """// Sir yaratish va QR uchun URI
var key = await _userManager.GetAuthenticatorKeyAsync(user);
if (string.IsNullOrEmpty(key))
{
    await _userManager.ResetAuthenticatorKeyAsync(user);
    key = await _userManager.GetAuthenticatorKeyAsync(user);
}

var uri = $"otpauth://totp/{issuer}:{user.Email}" +
          $"?secret={key}&issuer={issuer}&digits=6";""")

    code(d, """// Kodni tekshirish
var valid = await _userManager.VerifyTwoFactorTokenAsync(
    user,
    _userManager.Options.Tokens.AuthenticatorTokenProvider,
    code);

if (valid)
    await _signInManager.SignInAsync(user, isPersistent: false);""")

    h2(d, "4.3 Zaxira kodlar")

    para(d, "Telefon yo'qolsa, foydalanuvchi tizimga kira olmay qoladi. Shuning uchun "
            "bir martalik zaxira kodlar beriladi:")

    code(d, """var recoveryCodes = await _userManager
    .GenerateNewTwoFactorRecoveryCodesAsync(user, number: 10);""")

    note(d, "Bu qadam tashlab ketilmasligi kerak:",
         "MFA ni yoqib, zaxira kodlarni bermasam, telefonini yo'qotgan har bir "
         "foydalanuvchi qo'llab-quvvatlashga murojaat qiladi. Va o'sha yerda eng "
         "katta xavf paydo bo'ladi — chunki hisobni qo'lda tiklash jarayoni "
         "ko'pincha MFA ning o'zidan zaifroq bo'ladi.")

    # ───────────────────────────────────────────
    h1(d, "5. Qayerda MFA talab qilish")

    bullets(d, [
        "Administrator va yuqori huquqli hisoblar uchun — majburiy.",
        "Yangi qurilmadan birinchi kirishda.",
        "Muhim amallardan oldin — parol o'zgartirish, to'lov, ma'lumotni eksport "
        "qilish.",
        "Oddiy foydalanuvchilar uchun — ixtiyoriy, lekin tavsiya etiladigan.",
    ])

    code(d, """[Authorize]
[RequireMfa]      // o'z atributim
[HttpPost("account/change-email")]
public async Task<IActionResult> ChangeEmail(...) => ...;""")

    # ───────────────────────────────────────────
    h1(d, "6. Xulosa")

    bullets(d, [
        "Autentifikatsiya — kimligini aniqlash, avtorizatsiya — ruxsatini "
        "tekshirish.",
        "Parol uchun ataylab sekin algoritm kerak: Argon2id, bcrypt yoki PBKDF2.",
        "Har bir parolga alohida tuz; taqqoslash `FixedTimeEquals` bilan.",
        "Uzunlik murakkablikdan muhimroq — NIST shuni tavsiya qiladi.",
        "Kirish xatoliklarida bitta umumiy xabar qaytarish kerak.",
        "MFA dalillari turli toifalardan bo'lishi shart.",
        "SMS eng zaif usul; TOTP yoki apparat kalit afzalroq.",
        "Zaxira kodlarsiz MFA qo'llab-quvvatlash muammosiga aylanadi.",
    ])

    sources(d, [
        ("NIST SP 800-63B — Digital Identity Guidelines, Authentication",
         "https://pages.nist.gov/800-63-3/sp800-63b.html"),
        ("OWASP Password Storage Cheat Sheet",
         "https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html"),
        ("Two-factor authentication with TOTP in ASP.NET Core",
         "https://learn.microsoft.com/en-us/aspnet/core/security/authentication/identity-enable-qrcodes"),
        ("RFC 6238 — TOTP: Time-Based One-Time Password Algorithm",
         "https://www.rfc-editor.org/rfc/rfc6238"),
    ])
