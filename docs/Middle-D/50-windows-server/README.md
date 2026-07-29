# Windows Server Deployment — Firewall, PowerShell, IIS — Middle D

## 1. Nima? (Ta'rif)

Windows Server'da ASP.NET Core ilovani deploy qilish uchun zarur
bo'lgan komponentlar: **Windows Firewall** (tarmoq xavfsizligi),
**IIS** (Internet Information Services — web server/reverse proxy),
**PowerShell** (skript va boshqaruv tili).

## 2. Nima uchun kerak?

Ko'p enterprise (korporativ) muhitlarda — Linux emas, **Windows
Server** infratuzilmasi ishlatiladi (ayniqsa .NET Framework'dan
migratsiya qilingan kompaniyalarda). Bu vositalarni bilish — Windows
muhitida deploy va diagnostika qilish uchun zarur.

## 3. Ichida nima sodir bo'ladi? (Mexanizm)

### 3.1 Windows Firewall — port ochish

```powershell
New-NetFirewallRule -DisplayName "ASP.NET Core API" `
    -Direction Inbound -Protocol TCP -LocalPort 8080 -Action Allow
```

Bu — tashqi trafik **8080 portiga** kirishiga ruxsat beradi (default
holda Windows Firewall — noma'lum portlarni **BLOKLAYDI**).

### 3.2 Papka permission — NTFS, Share permission

```
NTFS permission  — DISK darajasida, FAYL/PAPKAGA kim NIMA qila olishi
Share permission — TARMOQ orqali (\\server\share) kirishda QO'SHIMCHA cheklov

Amaldagi RUXSAT — IKKALASINING ENG QATTIQ (restrictive) kombinatsiyasi
```

```powershell
icacls "C:\inetpub\erp-api" /grant "IIS_IUSRS:(OI)(CI)RX"
```

### 3.3 IIS o'rnatish — Windows Features

```powershell
Install-WindowsFeature -Name Web-Server -IncludeManagementTools
```

IIS — **Web-Server** rolini yoqib o'rnatiladi (Server Manager GUI
orqali ham mumkin).

### 3.4 IIS da ASP.NET Core deployment

```
1. ASP.NET Core Hosting Bundle o'rnatiladi (IIS'ga .NET runtime +
   modul qo'shadi)
2. IIS'da yangi Site yaratiladi, Application Pool biriktiriladi
3. dotnet publish natijasi — Site papkasiga KO'CHIRILADI
```

### 3.5 Application Pool — No Managed Code

```
ASP.NET Core — o'zining ICHKI Kestrel serveriga ega — IIS'ning
"Managed Code" (klassik ASP.NET/.NET Framework) ISHLOV BERISH
JARAYONI KERAK EMAS!

Application Pool sozlamasi: .NET CLR Version = "No Managed Code"
(IIS faqat REVERSE PROXY sifatida ishlaydi, so'rovni Kestrel'ga
YO'NALTIRADI)
```

### 3.6 `web.config` — in-process vs out-of-process

```xml
<aspNetCore processPath="dotnet" arguments=".\ErpApi.dll"
            hostingModel="InProcess" />
```

```
InProcess  — ASP.NET Core ilova IIS worker process (w3wp.exe)
             ICHIDA ishlaydi — TEZROQ (IIS↔Kestrel oraliq HTTP
             qatlami YO'Q)
OutOfProcess — Kestrel ALOHIDA process sifatida ishlaydi, IIS —
               FAQAT reverse proxy (HTTP orqali Kestrel'ga uzatadi)
               — biroz SEKINROQ, lekin KO'PROQ IZOLYATSIYA
```

### 3.7 HTTPS sertifikat sozlash

```powershell
# Self-signed sertifikat (FAQAT test uchun)
New-SelfSignedCertificate -DnsName "erp.example.com" -CertStoreLocation "cert:\LocalMachine\My"
```

Production'da — **haqiqiy** CA (Let's Encrypt, DigiCert) tomonidan
berilgan sertifikat ishlatilishi kerak, self-signed — FAQAT ichki
test muhitida.

### 3.8 PowerShell asoslari

```powershell
Get-Service -Name "W3SVC"           # Servis holatini ko'rish
Start-Service -Name "erp-api"        # Ishga tushirish
Stop-Service -Name "erp-api"          # To'xtatish

Get-Process -Name "dotnet"            # Jarayonlarni ko'rish
Stop-Process -Id 1234 -Force          # Majburan to'xtatish

New-Item -ItemType Directory -Path "C:\logs" -Force
Remove-Item -Path "C:\temp\*" -Recurse -Force
Copy-Item -Path "C:\source\*" -Destination "C:\dest\" -Recurse

Get-Content "app.log" -Tail 50        # Fayl oxirgi 50 qatorini o'qish
Set-Content -Path "config.txt" -Value "yangi qiymat"
```

**Script fayl** — `.ps1` kengaytmasi bilan saqlanadi, `& .\deploy.ps1`
orqali ishga tushiriladi.

### 3.9 CMD asoslari

```cmd
ipconfig                 :: Tarmoq interfeyslari, IP manzillar
netstat -an | findstr :8080   :: 8080-port holatini ko'rish
tasklist | findstr dotnet     :: dotnet jarayonlarini ko'rish
```

### 3.10 Telnet, Hyper-V, hosts fayl

```powershell
# Telnet Client — DEFAULT o'rnatilmagan, yoqish kerak
Enable-WindowsOptionalFeature -Online -FeatureName TelnetClient

# Hyper-V — Windows'ning built-in virtualizatsiya platformasi
Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Hyper-V -All
```

```
hosts fayli — C:\Windows\System32\drivers\etc\hosts
  Domain nomlarni QO'LDA IP'ga BOG'LASH uchun (DNS'ni CHETLAB o'tib):
  127.0.0.1   local.erp.test
```

### 3.11 Windows Server monitoring — Event Viewer

```
Event Viewer — Windows Logs → Application — ASP.NET Core/IIS xatolari
              shu yerda ko'rinadi (Serilog/o'z log fayllaridan
              TASHQARI, IIS/Windows darajasidagi xatolar UCHUN).
```

## 4. Kod — deployment PowerShell skripti

```powershell
Stop-Service -Name "erp-api"
Copy-Item -Path ".\publish\*" -Destination "C:\inetpub\erp-api\" -Recurse -Force
icacls "C:\inetpub\erp-api" /grant "IIS_IUSRS:(OI)(CI)RX"
Start-Service -Name "erp-api"
Get-Service -Name "erp-api"
```

## 5. Qachon ishlatish kerak?

| Vaziyat | Yechim |
|---|---|
| Enterprise, Windows infratuzilma | IIS + Windows Server |
| Yuqori performance, minimal overhead | InProcess hosting |
| Skript orqali avtomatlashtirish | PowerShell (`.ps1`) |
| Tez tarmoq diagnostikasi | CMD (`ipconfig`, `netstat`) |

## 6. Muhim nuqtalar

- `No Managed Code` Application Pool — ASP.NET Core uchun TO'G'RI
  sozlama (klassik ASP.NET uchun EMAS).
- InProcess hosting — odatda TAVSIYA ETILADI (tezroq), lekin
  ko'proq izolyatsiya kerak bo'lsa OutOfProcess tanlanishi mumkin.
- Self-signed sertifikatlar — FAQAT test uchun, production'da
  ISHLATILMASIN.

## 7. Imtihon savollari

1. IIS'da "No Managed Code" Application Pool sozlamasi ASP.NET Core
   uchun nima uchun to'g'ri?
2. InProcess va OutOfProcess hosting orasidagi farq nima?
3. NTFS va Share permission orasidagi farq nima?
4. PowerShell'da servisni qayta ishga tushirish qanday amalga
   oshiriladi?
5. `hosts` fayli nima vazifani bajaradi?
