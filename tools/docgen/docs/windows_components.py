# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "Componentalarni qo'shish va o'chirish (IIS, Telnet, host file, HyperV)"
CATEGORY = "Windows server deployment"
TITLE = "Windows Komponentlarini Boshqarish"
SUBTITLE = "IIS, Telnet, Hyper-V va hosts fayli"
FILENAME = "Componentalarni qo'shish va ochirish (IIS,Telnet,host file, HyperV ...).docx"


def build(d):
    h1(d, "1. Komponentlar va rollar")

    para(d, "Windows Server da funksionallik ikki toifaga bo'linadi: "
            "rollar (server asosiy vazifasi — IIS, DNS, Hyper-V) va "
            "xususiyatlar (qo'shimcha imkoniyatlar — Telnet mijozi, "
            ".NET Framework).")

    para(d, "Ularni qo'shish va o'chirish grafik interfeys orqali ham, "
            "PowerShell orqali ham mumkin. Server uchun ikkinchisi "
            "afzal — u takrorlanadigan va skriptga yozilishi mumkin.")

    code(d, """# Mavjud rollarni ko'rish
Get-WindowsFeature | Where-Object { $_.InstallState -eq 'Installed' } |
    Select-Object Name, DisplayName

# Qidirish
Get-WindowsFeature -Name *Web*""")

    note(d, "Buyruqlar Windows Server va Windows 10/11 da farq qiladi:",
         "Serverda `Get-WindowsFeature` va `Install-WindowsFeature` "
         "ishlaydi. Oddiy Windows da esa ular yo'q — o'rniga "
         "`Get-WindowsOptionalFeature` va `Enable-WindowsOptionalFeature` "
         "ishlatiladi. Bu farqni bilmasdan skript yozsam, u boshqa "
         "mashinada ishlamaydi.")

    # ───────────────────────────────────────────
    h1(d, "2. IIS o'rnatish")

    code(d, """# Windows Server
Install-WindowsFeature -Name Web-Server -IncludeManagementTools

# Kerakli qo'shimchalar bilan
Install-WindowsFeature -Name `
    Web-Server, `
    Web-Mgmt-Console, `
    Web-Asp-Net45, `
    Web-Net-Ext45, `
    Web-ISAPI-Ext, `
    Web-ISAPI-Filter, `
    Web-Http-Logging, `
    Web-Static-Content, `
    Web-Default-Doc, `
    Web-Http-Errors, `
    Web-Http-Redirect, `
    Web-Dyn-Compression, `
    Web-Stat-Compression `
    -IncludeManagementTools""")

    code(d, """# Windows 10/11
Enable-WindowsOptionalFeature -Online `
    -FeatureName IIS-WebServerRole, IIS-WebServer `
    -All""")

    h2(d, "2.1 ASP.NET Core Hosting Bundle")

    para(d, "ASP.NET Core ilovalarini IIS da ishlatish uchun alohida "
            "paket kerak. U `.NET` runtime va IIS modulini o'rnatadi.")

    code(d, """# O'rnatilganini tekshirish
Get-ChildItem "C:\\Program Files\\dotnet\\shared\\Microsoft.AspNetCore.App"

# IIS moduli
Get-WebGlobalModule | Where-Object Name -like "*AspNetCore*" """)

    note(d, "Tartib muhim:",
         "Hosting Bundle IIS dan **keyin** o'rnatilishi kerak. Agar "
         "teskari tartibda qilsam, IIS moduli ro'yxatdan o'tmaydi va "
         "ilova 500.19 xatosi bilan ishga tushmaydi. Yechim — Hosting "
         "Bundle ni qayta o'rnatish yoki `iisreset` qilish.")

    code(d, """iisreset""")

    h2(d, "2.2 Tekshirish")

    code(d, """Get-Service W3SVC
Get-Website
Invoke-WebRequest http://localhost -UseBasicParsing | Select-Object StatusCode""")

    # ───────────────────────────────────────────
    h1(d, "3. Telnet mijozi")

    para(d, "Telnet protokol sifatida eskirgan va xavfsiz emas, lekin "
            "uning **mijozi** port ochiqligini tekshirish uchun hamon "
            "foydali.")

    code(d, """# Windows Server
Install-WindowsFeature -Name Telnet-Client

# Windows 10/11
Enable-WindowsOptionalFeature -Online -FeatureName TelnetClient""")

    code(d, """telnet smtp.example.com 25
telnet db-server 5432""")

    note(d, "Lekin PowerShell da yaxshiroq muqobil bor:",
         "`Test-NetConnection` xuddi shu ishni qiladi va ko'proq "
         "ma'lumot beradi — manzil yechilganmi, ping o'tadimi, port "
         "ochiqmi. Men Telnet ni faqat protokol bilan interaktiv "
         "gaplashish kerak bo'lganda o'rnataman.")

    code(d, """Test-NetConnection -ComputerName "db-server" -Port 5432

# Natija:
# ComputerName     : db-server
# RemoteAddress    : 10.0.1.20
# RemotePort       : 5432
# TcpTestSucceeded : True""")

    note(d, "Telnet **serverini** esa hech qachon o'rnatmaslik kerak:",
         "U parollarni ochiq matnda uzatadi. Masofaviy boshqaruv uchun "
         "SSH yoki PowerShell Remoting ishlatiladi.")

    # ───────────────────────────────────────────
    h1(d, "4. Hyper-V")

    code(d, """# Windows Server
Install-WindowsFeature -Name Hyper-V -IncludeManagementTools -Restart

# Windows 10/11 Pro
Enable-WindowsOptionalFeature -Online `
    -FeatureName Microsoft-Hyper-V -All""")

    para(d, "O'rnatishdan keyin mashinani qayta ishga tushirish shart. "
            "Protsessorda virtualizatsiya qo'llab-quvvatlanishi va BIOS "
            "da yoqilgan bo'lishi kerak.")

    code(d, """# Qo'llab-quvvatlanishini tekshirish
Get-ComputerInfo -Property "HyperV*"

systeminfo | findstr /i "Hyper-V" """)

    h2(d, "4.1 Docker bilan to'qnashuv")

    note(d, "Bu masala menda ham muammo tug'dirgan:",
         "Docker Desktop WSL2 yoki Hyper-V ni ishlatadi. VirtualBox "
         "kabi boshqa gipervizorlar esa Hyper-V yoqilgan bo'lsa "
         "ishlamaydi — chunki protsessorning virtualizatsiya "
         "imkoniyatini bir vaqtda faqat bittasi egallaydi. Ikkalasi "
         "kerak bo'lsa, yuklash profilini almashtirish kerak bo'ladi.")

    code(d, """# Hyper-V ni vaqtincha o'chirish
bcdedit /set hypervisorlaunchtype off
# qayta yuklash

# Qaytarish
bcdedit /set hypervisorlaunchtype auto""")

    h2(d, "4.2 Asosiy buyruqlar")

    code(d, """Get-VM
Start-VM -Name "test-server"
Stop-VM -Name "test-server"

# Nuqta saqlash
Checkpoint-VM -Name "test-server" -SnapshotName "before-update"
Restore-VMSnapshot -VMName "test-server" -Name "before-update" -Confirm:$false

# Virtual kommutator
New-VMSwitch -Name "Internal" -SwitchType Internal""")

    # ───────────────────────────────────────────
    h1(d, "5. hosts fayli")

    para(d, "`hosts` fayli domen nomlarini IP manzillarga qo'lda "
            "bog'laydi. U DNS dan **oldin** tekshiriladi, shuning uchun "
            "undagi yozuv DNS javobini bekor qiladi.")

    code(d, """C:\\Windows\\System32\\drivers\\etc\\hosts""")

    code(d, """127.0.0.1       localhost
::1             localhost

# Lokal ishlab chiqish
127.0.0.1       api.myapp.local
127.0.0.1       admin.myapp.local

# Sinov serveri
10.0.1.50       staging.myapp.local""")

    h2(d, "5.1 Tahrirlash")

    code(d, """# Administrator huquqi kerak
notepad C:\\Windows\\System32\\drivers\\etc\\hosts

# PowerShell orqali qo'shish
$hosts = "$env:SystemRoot\\System32\\drivers\\etc\\hosts"
Add-Content -Path $hosts -Value "`n10.0.1.50`tstaging.myapp.local"

# Keshni tozalash
ipconfig /flushdns""")

    note(d, "`ipconfig /flushdns` ni unutmaslik kerak:",
         "Windows DNS javoblarini keshlaydi. `hosts` faylini "
         "o'zgartirganimdan keyin eski qiymat hali keshda turgan "
         "bo'lishi mumkin va o'zgarish ishlamayotgandek ko'rinadi. Men "
         "bu bilan bir necha marta chalkashganman.")

    h2(d, "5.2 Amaliy qo'llanishlar")

    bullets(d, [
        "Lokal ishlab chiqishda real domen nomlarini sinash.",
        "Bir nechta sayt uchun IIS da host nomlari bilan ishlash.",
        "DNS o'zgarishini kutmasdan yangi serverni sinash.",
        "Keraksiz domenni bloklash — `0.0.0.0` ga yo'naltirish.",
    ])

    code(d, """# SSL sertifikat bilan lokal sinash uchun
127.0.0.1       api.myapp.local

# IIS da shu host nomi bilan bog'lanish
New-WebBinding -Name "MyApp" -Protocol https `
    -Port 443 -HostHeader "api.myapp.local\"""")

    note(d, "`hosts` faylini jamoada ishlatishda ehtiyot bo'lish kerak:",
         "U faqat mening mashinamda ishlaydi va git ga tushmaydi. Agar "
         "loyiha uni talab qilsa, buni `README` da aniq yozish kerak — "
         "aks holda yangi dasturchi loyihani ishga tushira olmaydi va "
         "sababni tushunmaydi.")

    # ───────────────────────────────────────────
    h1(d, "6. Komponentni o'chirish")

    code(d, """# Windows Server
Uninstall-WindowsFeature -Name Telnet-Client
Uninstall-WindowsFeature -Name Web-Server -Remove   # fayllarni ham o'chirish

# Windows 10/11
Disable-WindowsOptionalFeature -Online -FeatureName TelnetClient""")

    note(d, "`-Remove` bayrog'i haqida:",
         "Usiz komponent o'chiriladi, lekin uning fayllari diskda "
         "qoladi — bu keyinchalik qayta o'rnatishni tezlashtiradi. "
         "`-Remove` esa fayllarni ham o'chiradi va joy bo'shatadi, "
         "lekin qayta o'rnatishda o'rnatish manbasi kerak bo'ladi.")

    # ───────────────────────────────────────────
    h1(d, "7. Server tayyorlash skripti")

    code(d, """$ErrorActionPreference = "Stop"

$features = @(
    "Web-Server",
    "Web-Mgmt-Console",
    "Web-Http-Logging",
    "Web-Dyn-Compression",
    "Web-Stat-Compression"
)

foreach ($feature in $features) {
    $state = (Get-WindowsFeature -Name $feature).InstallState

    if ($state -eq 'Installed') {
        Write-Host "[o'rnatilgan] $feature" -ForegroundColor DarkGray
        continue
    }

    Write-Host "[o'rnatilmoqda] $feature" -ForegroundColor Cyan
    Install-WindowsFeature -Name $feature -IncludeManagementTools | Out-Null
}

Write-Host "Tayyor. IIS holati:" -ForegroundColor Green
Get-Service W3SVC | Select-Object Name, Status""")

    # ───────────────────────────────────────────
    h1(d, "8. Xulosa")

    bullets(d, [
        "Windows Server da `Install-WindowsFeature`, oddiy Windows da "
        "`Enable-WindowsOptionalFeature` ishlatiladi.",
        "ASP.NET Core Hosting Bundle IIS dan keyin o'rnatilishi kerak.",
        "Telnet mijozi port tekshirish uchun ishlatiladi, lekin "
        "`Test-NetConnection` yaxshiroq muqobil.",
        "Telnet serverini o'rnatmaslik kerak — u parollarni ochiq "
        "uzatadi.",
        "Hyper-V boshqa gipervizorlar bilan to'qnashadi; "
        "`hypervisorlaunchtype` bilan almashtiriladi.",
        "`hosts` fayli DNS dan oldin tekshiriladi va uni bekor qiladi.",
        "`hosts` o'zgartirilgandan keyin `ipconfig /flushdns` kerak.",
        "Komponentni o'chirishda `-Remove` fayllarni ham o'chiradi.",
    ])

    sources(d, [
        ("Install-WindowsFeature — PowerShell",
         "https://learn.microsoft.com/en-us/powershell/module/servermanager/install-windowsfeature"),
        ("Host ASP.NET Core on Windows with IIS",
         "https://learn.microsoft.com/en-us/aspnet/core/host-and-deploy/iis/"),
        ("Install Hyper-V on Windows Server",
         "https://learn.microsoft.com/en-us/windows-server/virtualization/hyper-v/get-started/install-hyper-v"),
        ("DISM — Enable or disable Windows features",
         "https://learn.microsoft.com/en-us/windows-hardware/manufacture/desktop/enable-or-disable-windows-features-using-dism"),
    ])
