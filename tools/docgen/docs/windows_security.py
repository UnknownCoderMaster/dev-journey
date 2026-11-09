# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "Windows security (firewall, folder larni permissionlarini boshqarish)"
CATEGORY = "Windows server deployment"
TITLE = "Windows Server Xavfsizligi"
SUBTITLE = "Firewall qoidalari va papka huquqlarini boshqarish"
FILENAME = "Windows security (firewall, folder larni permissionlarini boshqarish).docx"


def build(d):
    h1(d, "1. Windows Firewall")

    para(d, "Windows Defender Firewall uchta profil bilan ishlaydi va "
            "har biri alohida sozlanadi:")

    table(d, ["Profil", "Qachon faol"],
          [["Domain", "Mashina domen tarmog'ida"],
           ["Private", "Ishonchli uy yoki ish tarmog'i"],
           ["Public", "Ochiq tarmoq; eng qattiq qoidalar"]],
          widths=[3.4, 12.1])

    note(d, "Server odatda Public profilda bo'ladi:",
         "Agar qoida faqat Private uchun yaratilsa, u serverda umuman "
         "ishlamaydi va bu chalkashlik tug'diradi — qoida ro'yxatda "
         "ko'rinadi, lekin ta'sir qilmaydi. Shuning uchun men qoida "
         "yaratganda profilni aniq ko'rsataman.")

    h2(d, "1.1 Holatni ko'rish")

    code(d, """Get-NetFirewallProfile | Select-Object Name, Enabled,
    DefaultInboundAction, DefaultOutboundAction

Get-NetFirewallRule -Enabled True -Direction Inbound |
    Select-Object DisplayName, Profile, Action |
    Sort-Object DisplayName""")

    h2(d, "1.2 Qoida yaratish")

    code(d, """# HTTPS uchun port ochish
New-NetFirewallRule `
    -DisplayName "HTTPS kiruvchi" `
    -Direction Inbound `
    -Protocol TCP `
    -LocalPort 443 `
    -Action Allow `
    -Profile Any

# Faqat ma'lum manzildan — ancha xavfsizroq
New-NetFirewallRule `
    -DisplayName "SQL Server ichki tarmoqdan" `
    -Direction Inbound `
    -Protocol TCP `
    -LocalPort 1433 `
    -RemoteAddress 10.0.0.0/8 `
    -Action Allow `
    -Profile Domain,Private""")

    note(d, "`RemoteAddress` ni ishlatish odatini shakllantirish kerak:",
         "Portni butun dunyoga ochish o'rniga faqat kerakli tarmoqqa "
         "ochish — bu bir qator qo'shimcha kod, lekin hujum maydonini "
         "keskin kichraytiradi. Baza portini internetga ochish esa "
         "deyarli har doim xato.")

    h2(d, "1.3 Qoidalarni boshqarish")

    code(d, """# O'chirish (saqlab)
Disable-NetFirewallRule -DisplayName "HTTPS kiruvchi"

# Yoqish
Enable-NetFirewallRule -DisplayName "HTTPS kiruvchi"

# Butunlay o'chirish
Remove-NetFirewallRule -DisplayName "HTTPS kiruvchi"

# Qoidani o'zgartirish
Set-NetFirewallRule -DisplayName "HTTPS kiruvchi" `
    -RemoteAddress 203.0.113.0/24""")

    h2(d, "1.4 Chiquvchi trafikni cheklash")

    code(d, """# Sukut bo'yicha chiquvchi trafikni bloklash
Set-NetFirewallProfile -Profile Public -DefaultOutboundAction Block

# Keyin kerakliga ruxsat
New-NetFirewallRule -DisplayName "HTTPS chiquvchi" `
    -Direction Outbound -Protocol TCP -RemotePort 443 -Action Allow""")

    note(d, "Bu qadamni ehtiyotkorlik bilan qilish kerak:",
         "Chiquvchi trafikni bloklash zararli dasturning ma'lumot "
         "yuborishini to'sadi, lekin ilovangizning ham tashqi API ga "
         "murojaatini to'xtatishi mumkin. Men buni avval sinov muhitida "
         "qo'llab, nimalar ishlamay qolganini ro'yxatga olaman.")

    # ───────────────────────────────────────────
    h1(d, "2. NTFS huquqlari")

    para(d, "Windows da huquqlar kirish nazorati ro'yxati (ACL) orqali "
            "beriladi. Har bir ro'yxat elementi (ACE) kimga qanday "
            "huquq berilganini yoki taqiqlanganini belgilaydi.")

    h2(d, "2.1 Asosiy huquqlar")

    table(d, ["Huquq", "Ma'nosi"],
          [["`Read`", "O'qish va ro'yxatni ko'rish"],
           ["`Write`", "Yozish va yangi fayl yaratish"],
           ["`ReadAndExecute`", "O'qish va dastur ishga tushirish"],
           ["`Modify`", "O'qish, yozish, o'chirish"],
           ["`FullControl`", "Hamma narsa, huquqlarni o'zgartirish ham"]],
          widths=[4.4, 11.1])

    h2(d, "2.2 Joriy huquqlarni ko'rish")

    code(d, """# PowerShell
Get-Acl "C:\\inetpub\\myapp" | Format-List

(Get-Acl "C:\\inetpub\\myapp").Access |
    Select-Object IdentityReference, FileSystemRights,
                  AccessControlType, IsInherited |
    Format-Table -AutoSize

# icacls — qisqaroq chiqish
icacls "C:\\inetpub\\myapp" """)

    h2(d, "2.3 Huquq berish")

    code(d, """$path = "C:\\inetpub\\myapp"
$acl = Get-Acl $path

$rule = New-Object System.Security.AccessControl.FileSystemAccessRule(
    "IIS AppPool\\MyAppPool",
    "ReadAndExecute",
    "ContainerInherit,ObjectInherit",
    "None",
    "Allow")

$acl.AddAccessRule($rule)
Set-Acl -Path $path -AclObject $acl""")

    code(d, """# icacls bilan qisqaroq
icacls "C:\\inetpub\\myapp" /grant "IIS AppPool\\MyAppPool:(OI)(CI)RX"
icacls "C:\\inetpub\\myapp\\logs" /grant "IIS AppPool\\MyAppPool:(OI)(CI)M" """)

    table(d, ["Bayroq", "Ma'nosi"],
          [["`(OI)`", "Object Inherit — fayllarga meros"],
           ["`(CI)`", "Container Inherit — papkalarga meros"],
           ["`R`", "O'qish"],
           ["`RX`", "O'qish va bajarish"],
           ["`M`", "O'zgartirish"],
           ["`F`", "To'liq nazorat"]],
          widths=[3.0, 12.5])

    note(d, "`IIS AppPool\\` prefiksi muhim:",
         "IIS har bir ilova havzasi uchun virtual hisob yaratadi va u "
         "foydalanuvchilar ro'yxatida ko'rinmaydi. Shuning uchun uni "
         "qo'lda, aynan shu shaklda yozish kerak. Men birinchi marta "
         "foydalanuvchini ro'yxatdan izlab topa olmaganman va buni "
         "tushunishga ancha vaqt ketgan.")

    # ───────────────────────────────────────────
    h1(d, "3. Eng kam huquq tamoyili")

    para(d, "ASP.NET Core ilovasi uchun odatdagi huquqlar taqsimoti:")

    table(d, ["Papka", "Huquq", "Sabab"],
          [["Ilova papkasi", "`ReadAndExecute`", "Faqat o'qish va ishga "
                                                 "tushirish"],
           ["`logs`", "`Modify`", "Log fayllarini yozish"],
           ["`uploads`", "`Modify`", "Yuklangan fayllar"],
           ["`App_Data`", "`Modify`", "Ma'lumot fayllari"],
           ["Konfiguratsiya", "`Read`", "O'zgartirish kerak emas"]],
          widths=[3.6, 4.0, 7.9])

    note(d, "Ilova papkasiga yozish huquqini bermaslik — muhim qoida:",
         "Agar ilova o'z fayllarini o'zgartira olsa, zaiflik topilgan "
         "taqdirda tajovuzkor kodni almashtirishi mumkin. O'qish huquqi "
         "esa bunday imkonni bermaydi. Yozish kerak bo'lgan papkalarni "
         "alohida ajratish bir necha daqiqa vaqt oladi, lekin himoya "
         "darajasini sezilarli oshiradi.")

    code(d, """# Tayyorlash skripti
$app = "C:\\inetpub\\myapp"
$pool = "IIS AppPool\\MyAppPool"

New-Item -ItemType Directory -Force -Path "$app\\logs", "$app\\uploads" | Out-Null

icacls $app /grant "${pool}:(OI)(CI)RX"
icacls "$app\\logs" /grant "${pool}:(OI)(CI)M"
icacls "$app\\uploads" /grant "${pool}:(OI)(CI)M" """)

    # ───────────────────────────────────────────
    h1(d, "4. Merosni boshqarish")

    para(d, "Sukut bo'yicha papka huquqlarni ota papkadan meros oladi. "
            "Maxfiy papkalar uchun merosni uzish kerak bo'ladi:")

    code(d, """# Merosni uzish, lekin mavjud huquqlarni saqlash
icacls "C:\\inetpub\\myapp\\secrets" /inheritance:d

# Keraksizlarni olib tashlash
icacls "C:\\inetpub\\myapp\\secrets" /remove "Users"
icacls "C:\\inetpub\\myapp\\secrets" /remove "Everyone"

# Faqat kerakliga ruxsat
icacls "C:\\inetpub\\myapp\\secrets" /grant "IIS AppPool\\MyAppPool:(OI)(CI)R" """)

    note(d, "`Users` guruhi sukut bo'yicha ko'p joyga o'qish huquqiga ega:",
         "Bu mashinaga kirgan har qanday foydalanuvchi sertifikat yoki "
         "konfiguratsiya faylini o'qiy olishini anglatadi. Maxfiy "
         "papkalarda merosni uzib, bu guruhni olib tashlash kerak.")

    # ───────────────────────────────────────────
    h1(d, "5. Boshqa xavfsizlik choralari")

    h2(d, "5.1 Keraksiz xizmatlarni o'chirish")

    code(d, """Get-Service | Where-Object { $_.Status -eq 'Running' } |
    Select-Object Name, DisplayName | Sort-Object Name

Stop-Service -Name "RemoteRegistry"
Set-Service -Name "RemoteRegistry" -StartupType Disabled""")

    h2(d, "5.2 Hisoblarni nazorat qilish")

    code(d, """# Lokal hisoblar
Get-LocalUser | Select-Object Name, Enabled, LastLogon

# Administratorlar guruhi
Get-LocalGroupMember -Group "Administrators"

# Mehmon hisobini o'chirish
Disable-LocalUser -Name "Guest\"""")

    h2(d, "5.3 Yangilanishlar")

    code(d, """Get-HotFix | Sort-Object InstalledOn -Descending |
    Select-Object -First 10""")

    h2(d, "5.4 Audit")

    code(d, """# Muvaffaqiyatsiz kirish urinishlari
Get-WinEvent -FilterHashtable @{
    LogName   = 'Security'
    ID        = 4625
    StartTime = (Get-Date).AddDays(-1)
} | Select-Object TimeCreated, Message -First 20""")

    note(d, "4625 hodisasi — eng foydali audit kodlaridan biri:",
         "Agar bir necha daqiqada o'nlab muvaffaqiyatsiz urinish bo'lsa, "
         "bu parolni saralash hujumini bildiradi. Men bunday holatlarga "
         "ogohlantirish qo'yaman — chunki hujum odatda muvaffaqiyatga "
         "erishishidan ancha oldin ko'rinadi.")

    # ───────────────────────────────────────────
    h1(d, "6. Tekshirish ro'yxati")

    bullets(d, [
        "Firewall barcha profillarda yoqilganmi.",
        "Faqat kerakli portlar ochiqmi va ular manzil bo'yicha "
        "cheklanganmi.",
        "Ilova havzasi hisobiga faqat kerakli huquqlar berilganmi.",
        "Ilova papkasiga yozish huquqi berilmaganmi.",
        "Maxfiy papkalarda meros uzilganmi.",
        "Keraksiz xizmatlar o'chirilganmi.",
        "Administratorlar guruhida ortiqcha hisob yo'qmi.",
        "Yangilanishlar o'rnatilganmi.",
    ])

    # ───────────────────────────────────────────
    h1(d, "7. Xulosa")

    bullets(d, [
        "Firewall uchta profil bilan ishlaydi; server odatda Public "
        "profilda bo'ladi.",
        "`New-NetFirewallRule` bilan qoida yaratilganda profil aniq "
        "ko'rsatilishi kerak.",
        "`RemoteAddress` bilan cheklash hujum maydonini kichraytiradi.",
        "NTFS huquqlari ACL orqali beriladi; `icacls` tez boshqarish "
        "imkonini beradi.",
        "IIS ilova havzasi hisobi `IIS AppPool\\` prefiksi bilan "
        "yoziladi.",
        "Ilova papkasiga faqat o'qish, yozish kerak bo'lgan papkalarga "
        "alohida huquq beriladi.",
        "Maxfiy papkalarda meros uzilib, `Users` guruhi olib "
        "tashlanadi.",
        "4625 hodisa kodi muvaffaqiyatsiz kirish urinishlarini "
        "ko'rsatadi.",
    ])

    sources(d, [
        ("Windows Defender Firewall with Advanced Security — Microsoft Learn",
         "https://learn.microsoft.com/en-us/windows/security/operating-system-security/network-security/windows-firewall/"),
        ("NetSecurity PowerShell module",
         "https://learn.microsoft.com/en-us/powershell/module/netsecurity/"),
        ("icacls — Windows Commands",
         "https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/icacls"),
        ("Host ASP.NET Core on Windows with IIS",
         "https://learn.microsoft.com/en-us/aspnet/core/host-and-deploy/iis/"),
    ])
