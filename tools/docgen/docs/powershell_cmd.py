# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "PowerShell va CMD bilan ishlash"
CATEGORY = "Windows server deployment"
TITLE = "PowerShell va CMD"
SUBTITLE = "Windows serverda buyruq qatori bilan ishlash"
FILENAME = "PowerShell va CMD bilan ishlash.docx"


def build(d):
    h1(d, "1. Ikki qobiq farqi")

    para(d, "CMD — eski buyruq interpretatori. U matn bilan ishlaydi: "
            "har bir buyruq matn chiqaradi, keyingisi uni tahlil "
            "qilishi kerak.")

    para(d, "PowerShell esa **obyektlar** bilan ishlaydi. Buyruq matn "
            "emas, to'liq obyekt qaytaradi va uning xossalariga "
            "to'g'ridan-to'g'ri murojaat qilish mumkin.")

    code(d, """# CMD — matnni tahlil qilish kerak
dir | findstr ".log"

# PowerShell — obyekt xossalari bilan ishlash
Get-ChildItem -Filter *.log |
    Where-Object { $_.Length -gt 1MB } |
    Sort-Object LastWriteTime -Descending |
    Select-Object Name, Length, LastWriteTime""")

    note(d, "Bu farqni tushunganimda PowerShell ancha mantiqiy bo'ldi:",
         "Matn bilan ishlaganda men chiqishning formatiga tayanaman — "
         "ustun qayerda boshlanadi, ajratuvchi nima. Format o'zgarsa, "
         "skriptim buziladi. Obyekt bilan ishlaganda esa men xossa "
         "nomiga murojaat qilaman va chiqish ko'rinishi umuman ahamiyat "
         "kasb etmaydi.")

    # ───────────────────────────────────────────
    h1(d, "2. PowerShell versiyalari")

    table(d, ["Versiya", "Buyruq", "Platforma"],
          [["Windows PowerShell 5.1", "`powershell.exe`", "Faqat Windows"],
           ["PowerShell 7+", "`pwsh.exe`", "Windows, Linux, macOS"]],
          widths=[5.0, 4.5, 6.0])

    code(d, """$PSVersionTable.PSVersion""")

    note(d, "Farqni bilish kerak:",
         "5.1 Windows bilan birga keladi va ko'p serverlarda faqat u "
         "bo'ladi. 7+ esa alohida o'rnatiladi va yangi imkoniyatlarga "
         "ega — `??`, `?.`, ternar operator, `&&` va `||`. Skript "
         "yozganda qaysi versiyada ishlashini hisobga olish kerak, aks "
         "holda u serverda sintaksis xatosi bilan to'xtaydi.")

    # ───────────────────────────────────────────
    h1(d, "3. Cmdlet nomlash tizimi")

    para(d, "PowerShell buyruqlari `Fe'l-Ot` shaklida nomlanadi va bu "
            "tizim izchil — nomini taxmin qilish mumkin.")

    table(d, ["Fe'l", "Ma'nosi", "Misol"],
          [["`Get`", "Olish", "`Get-Service`"],
           ["`Set`", "O'rnatish", "`Set-Location`"],
           ["`New`", "Yaratish", "`New-Item`"],
           ["`Remove`", "O'chirish", "`Remove-Item`"],
           ["`Start` / `Stop`", "Ishga tushirish / to'xtatish",
            "`Start-Service`"],
           ["`Test`", "Tekshirish", "`Test-Path`"]],
          widths=[3.2, 5.8, 6.5])

    code(d, """# Buyruq izlash
Get-Command *service*
Get-Command -Verb Get -Noun *Net*

# Yordam olish
Get-Help Get-Service -Full
Get-Help Get-Service -Examples

# Obyekt xossalarini ko'rish
Get-Service | Get-Member""")

    note(d, "`Get-Member` — PowerShell ni o'rganishdagi eng foydali buyruq:",
         "U obyektda qanday xossa va metodlar borligini ko'rsatadi. "
         "Nimani yozishni bilmaganimda men shu buyruqni ishlataman va "
         "javob odatda darhol topiladi.")

    # ───────────────────────────────────────────
    h1(d, "4. Quvur va filtrlash")

    code(d, """# Filtrlash
Get-Process | Where-Object { $_.CPU -gt 100 }
Get-Process | Where-Object CPU -gt 100          # qisqa shakl

# Saralash va tanlash
Get-Process |
    Sort-Object WorkingSet -Descending |
    Select-Object -First 10 Name, @{
        Name = 'Memory(MB)'
        Expression = { [math]::Round($_.WorkingSet / 1MB, 2) }
    }

# Har bir element uchun amal
Get-ChildItem *.log | ForEach-Object {
    Write-Host "$($_.Name): $($_.Length) bayt"
}

# Guruhlash va hisoblash
Get-Service | Group-Object Status | Select-Object Name, Count""")

    # ───────────────────────────────────────────
    h1(d, "5. Serverda tipik vazifalar")

    h2(d, "5.1 Xizmatlarni boshqarish")

    code(d, """Get-Service -Name "MyApp*"
Restart-Service -Name "MyAppService"
Stop-Service -Name "MyAppService" -Force

# Yangi xizmat yaratish
New-Service -Name "MyAppService" `
    -BinaryPathName "C:\\inetpub\\myapp\\MyApp.Api.exe" `
    -DisplayName "MyApp API" `
    -StartupType Automatic""")

    h2(d, "5.2 IIS boshqaruvi")

    code(d, """Import-Module WebAdministration

Get-Website
Get-WebAppPoolState -Name "MyAppPool"

Restart-WebAppPool -Name "MyAppPool"
Stop-Website -Name "MyApp"
Start-Website -Name "MyApp"

# Yangi sayt
New-Website -Name "MyApp" `
    -Port 80 `
    -PhysicalPath "C:\\inetpub\\myapp" `
    -ApplicationPool "MyAppPool\"""")

    h2(d, "5.3 Loglarni ko'rish")

    code(d, """# Fayl loglari
Get-Content "C:\\inetpub\\myapp\\logs\\app.log" -Tail 50
Get-Content "C:\\inetpub\\myapp\\logs\\app.log" -Tail 50 -Wait   # kuzatish

# Hodisalar jurnali
Get-WinEvent -FilterHashtable @{
    LogName   = 'Application'
    Level     = 2            # Error
    StartTime = (Get-Date).AddHours(-1)
} | Select-Object TimeCreated, ProviderName, Message -First 20""")

    note(d, "`-Wait` bayrog'i Linux dagi `tail -f` ga teng:",
         "Joylashtirishdan keyin ilovani kuzatish uchun aynan shu kerak "
         "bo'ladi. Men odatda ikkita oyna ochaman — birida loglar "
         "oqib turadi, ikkinchisida sinov so'rovlari yuboriladi.")

    h2(d, "5.4 Tarmoq tekshiruvi")

    code(d, """# Port tinglanayaptimi
Get-NetTCPConnection -LocalPort 443 -State Listen

# Kim band qilgan
Get-Process -Id (Get-NetTCPConnection -LocalPort 5000).OwningProcess

# Ulanishni sinash
Test-NetConnection -ComputerName "api.example.com" -Port 443

# HTTP so'rov
Invoke-WebRequest -Uri "http://localhost/health" -UseBasicParsing
Invoke-RestMethod -Uri "http://localhost/api/books" | ConvertTo-Json""")

    h2(d, "5.5 Disk holati")

    code(d, """Get-PSDrive -PSProvider FileSystem |
    Select-Object Name,
        @{N='Used(GB)'; E={[math]::Round($_.Used / 1GB, 2)}},
        @{N='Free(GB)'; E={[math]::Round($_.Free / 1GB, 2)}}

# Eng katta papkalar
Get-ChildItem "C:\\inetpub" -Directory |
    ForEach-Object {
        $size = (Get-ChildItem $_.FullName -Recurse -File -ErrorAction SilentlyContinue |
                 Measure-Object Length -Sum).Sum
        [PSCustomObject]@{
            Name = $_.Name
            SizeMB = [math]::Round($size / 1MB, 2)
        }
    } | Sort-Object SizeMB -Descending""")

    # ───────────────────────────────────────────
    h1(d, "6. Skript yozish")

    code(d, """param(
    [Parameter(Mandatory = $true)]
    [string]$Environment,

    [string]$Version = "latest"
)

$ErrorActionPreference = "Stop"

function Write-Step {
    param([string]$Message)
    Write-Host "==> $Message" -ForegroundColor Cyan
}

try {
    Write-Step "Ilova to'xtatilmoqda"
    Stop-WebAppPool -Name "MyAppPool"
    Start-Sleep -Seconds 3

    Write-Step "Zaxira nusxa olinmoqda"
    $backup = "C:\\backups\\myapp-$(Get-Date -Format 'yyyyMMdd-HHmmss')"
    Copy-Item "C:\\inetpub\\myapp" $backup -Recurse

    Write-Step "Yangi versiya ko'chirilmoqda"
    Copy-Item ".\\publish\\*" "C:\\inetpub\\myapp" -Recurse -Force

    Write-Step "Ilova ishga tushirilmoqda"
    Start-WebAppPool -Name "MyAppPool"

    Write-Step "Tekshirilmoqda"
    Start-Sleep -Seconds 5
    $response = Invoke-WebRequest "http://localhost/health" -UseBasicParsing

    if ($response.StatusCode -ne 200) {
        throw "Sog'liq tekshiruvi muvaffaqiyatsiz"
    }

    Write-Host "Joylashtirish yakunlandi" -ForegroundColor Green
}
catch {
    Write-Host "Xatolik: $_" -ForegroundColor Red
    exit 1
}""")

    note(d, "`$ErrorActionPreference = \"Stop\"` qatorini men har doim yozaman:",
         "Usiz PowerShell ko'p xatolarni shunchaki chop etib, keyingi "
         "qatorga o'tadi. Joylashtirish skriptida bu xavfli — fayl "
         "ko'chirilmagan bo'lsa ham skript \"muvaffaqiyatli\" tugaydi. "
         "Bu sozlama har qanday xatoni to'xtatuvchi qiladi.")

    h2(d, "6.1 Bajarish siyosati")

    code(d, """Get-ExecutionPolicy -List

# Serverda imzolangan skriptlarga ruxsat
Set-ExecutionPolicy RemoteSigned -Scope LocalMachine

# Bir martalik
powershell.exe -ExecutionPolicy Bypass -File .\\deploy.ps1""")

    # ───────────────────────────────────────────
    h1(d, "7. CMD hali kerak bo'ladigan joylar")

    code(d, """:: Muhit o'zgaruvchilari
setx ASPNETCORE_ENVIRONMENT "Production" /M

:: Xizmatlar
sc query MyAppService
sc config MyAppService start= auto

:: Tarmoq
ipconfig /all
ipconfig /flushdns
netstat -ano | findstr :443

:: IIS
iisreset
%windir%\\system32\\inetsrv\\appcmd list sites""")

    note(d, "`setx ... /M` ga alohida e'tibor:",
         "`/M` bayrog'isiz o'zgaruvchi faqat joriy foydalanuvchi uchun "
         "o'rnatiladi. Xizmat esa boshqa hisob nomidan ishlaydi va uni "
         "ko'rmaydi. Shuning uchun server sozlamalarida `/M` majburiy. "
         "Yana bir tafsilot — o'zgaruvchi faqat **yangi** jarayonlarga "
         "ta'sir qiladi, shuning uchun xizmatni qayta ishga tushirish "
         "kerak.")

    # ───────────────────────────────────────────
    h1(d, "8. Masofaviy boshqaruv")

    code(d, """# WinRM yoqish
Enable-PSRemoting -Force

# Masofaviy buyruq
Invoke-Command -ComputerName "web-01" -ScriptBlock {
    Get-Service -Name "MyAppService"
}

# Interaktiv sessiya
Enter-PSSession -ComputerName "web-01" -Credential (Get-Credential)

# Bir nechta serverda
Invoke-Command -ComputerName "web-01","web-02" -ScriptBlock {
    Restart-WebAppPool -Name "MyAppPool"
}""")

    # ───────────────────────────────────────────
    h1(d, "9. Xulosa")

    bullets(d, [
        "CMD matn bilan, PowerShell obyektlar bilan ishlaydi.",
        "PowerShell 5.1 Windows bilan keladi, 7+ alohida o'rnatiladi va "
        "yangi sintaksisga ega.",
        "Cmdlet lar `Fe'l-Ot` shaklida nomlanadi; `Get-Command` va "
        "`Get-Member` o'rganishda asosiy vosita.",
        "`Get-Content -Wait` Linux dagi `tail -f` ga teng.",
        "`$ErrorActionPreference = \"Stop\"` skriptni xatoda to'xtatadi.",
        "Bajarish siyosati skript ishga tushishini cheklaydi.",
        "`setx` da `/M` bayrog'isiz o'zgaruvchi xizmatlarga ko'rinmaydi.",
        "`Invoke-Command` bir nechta serverda bir yo'la buyruq "
        "bajarishga imkon beradi.",
    ])

    sources(d, [
        ("PowerShell Documentation — Microsoft Learn",
         "https://learn.microsoft.com/en-us/powershell/"),
        ("Windows Commands — Microsoft Learn",
         "https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/windows-commands"),
        ("about_Execution_Policies — PowerShell",
         "https://learn.microsoft.com/en-us/powershell/module/microsoft.powershell.core/about/about_execution_policies"),
        ("WebAdministration module — PowerShell",
         "https://learn.microsoft.com/en-us/powershell/module/webadministration/"),
    ])
