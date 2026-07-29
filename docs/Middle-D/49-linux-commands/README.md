# Linux Server Buyruqlari — Middle D

## 1. Nima? (Ta'rif)

Linux serverda ilova deploy qilish, fayllarni boshqarish, jarayonlarni
kuzatish uchun zarur bo'lgan asosiy komandanoq (terminal) buyruqlari
majmuasi.

## 2. Nima uchun kerak?

ASP.NET Core ilova — ko'pincha Linux serverda (Ubuntu, Debian) yoki
Docker konteynerida ishlaydi. Serverga SSH orqali ulanib, muammoni
diagnostika qilish, konfiguratsiya o'zgartirish uchun bu buyruqlar
zarur.

## 3. Ichida nima sodir bo'ladi? (Mexanizm)

### 3.1 Matn muharrirlari — vim, nano

```bash
vim appsettings.json
# i        — INSERT rejimga o'tish (matn kiritish mumkin)
# Esc      — INSERT rejimdan CHIQISH (buyruq rejimga qaytish)
# :wq      — SAQLASH va CHIQISH
# :q!      — SAQLAMASDAN CHIQISH (o'zgarishlarni bekor qilish)

nano appsettings.json
# Ctrl+O    — SAQLASH (Write Out)
# Ctrl+X    — CHIQISH
```

`vim` — **modal** muharrir (Insert/Normal/Visual rejimlari bor) —
o'rganish qiyinroq, lekin tezkor. `nano` — **oddiy**, boshlang'ich
uchun qulayroq.

### 3.2 `sudo` — admin huquqi

```bash
sudo systemctl restart nginx
```

`sudo` (superuser do) — vaqtincha **root** (administrator) huquqi
bilan buyruq bajarish — fayl tizimi, tizim xizmatlari kabi
himoyalangan resurslarga kirish uchun kerak.

### 3.3 Fayl ko'rish — `cat`

```bash
cat /var/log/app.log
cat -n file.txt  # Qator raqamlari bilan
```

### 3.4 Disk joyi — `df -h`

```bash
df -h
# Filesystem      Size  Used Avail Use% Mounted on
# /dev/sda1        50G   30G   18G  63% /
```

`-h` — human-readable (GB/MB ko'rinishida, baytlarda EMAS).

### 3.5 Fayl ro'yxati — `ls -la`

```bash
ls -la
# drwxr-xr-x  2 user user 4096 Jul 22 10:00 myapp
# -rw-r--r--  1 user user  512 Jul 22 10:00 appsettings.json
```

`-l` — batafsil (permission, egasi, hajm), `-a` — YASHIRIN fayllar
(nomi `.` bilan boshlanadigan) HAM ko'rsatiladi.

### 3.6 Papka yaratish — `mkdir -p`

```bash
mkdir -p /var/www/erp-api/logs
```

`-p` — ICHMA-ICH papkalarni **BIR NECHTASINI BIRDANIGA** yaratadi
(agar ota papka mavjud bo'lmasa ham, xato bermaydi).

### 3.7 Navigatsiya — `cd`, `pwd`

```bash
cd /var/www/erp-api   # Papkaga o'tish
pwd                    # Joriy papka yo'lini ko'rsatish (Print Working Directory)
cd ..                  # Bir daraja YUQORIGA
cd ~                   # Uy papkasiga
```

### 3.8 `chmod` — ruxsatlar

```bash
chmod 755 script.sh
chmod 644 appsettings.json
```

```
Ruxsat raqamlari (3 raqam: Owner, Group, Others):
  4 = Read (r)
  2 = Write (w)
  1 = Execute (x)

755 = Owner: 7 (rwx=4+2+1), Group: 5 (r-x=4+1), Others: 5 (r-x=4+1)
  → Egasi TO'LIQ huquq, boshqalar FAQAT o'qish+bajarish

644 = Owner: 6 (rw-=4+2), Group: 4 (r--), Others: 4 (r--)
  → Egasi o'qish/yozish, boshqalar FAQAT o'qish (BAJARISH huquqisiz)
```

### 3.9 `chown` — egasini o'zgartirish

```bash
sudo chown www-data:www-data /var/www/erp-api -R
```

`www-data` — odatda web server (Nginx) ishlaydigan foydalanuvchi —
ilova fayllariga shu foydalanuvchi **egalik** qilishi kerak (aks
holda web server fayllarni O'QIY OLMASLIGI mumkin).

### 3.10 `systemctl` — servis boshqarish

```bash
sudo systemctl start erp-api      # ISHGA TUSHIRISH
sudo systemctl stop erp-api        # TO'XTATISH
sudo systemctl restart erp-api     # QAYTA ISHGA TUSHIRISH
sudo systemctl status erp-api      # HOLATNI ko'rish
sudo systemctl enable erp-api      # Server QAYTA YUKLANGANDA AVTOMATIK ishga tushishi
```

### 3.11 `journalctl` — log ko'rish

```bash
journalctl -u erp-api -f          # Servis logini JONLI (live, follow) kuzatish
journalctl -u erp-api --since today
```

### 3.12 `ps aux`, `kill` — jarayonlar

```bash
ps aux | grep dotnet   # dotnet jarayonlarini topish
kill -9 12345           # PID 12345 ni MAJBURAN o'chirish (-9 = SIGKILL)
kill -15 12345          # "muloyim" so'rov (SIGTERM) — jarayon O'ZI tozalab chiqishi mumkin
```

### 3.13 `grep`, `find` — qidirish

```bash
grep -r "ERROR" /var/log/app/           # BARCHA fayllarda "ERROR" so'zini qidirish
grep -i "error" app.log                  # Katta-kichik harfga E'TIBORSIZ
find / -name "appsettings.json"          # Fayl NOMI bo'yicha qidirish
```

### 3.14 `tar`, `zip` — arxivlash

```bash
tar -czvf backup.tar.gz /var/www/erp-api   # Arxivlash (c=create, z=gzip, v=verbose, f=file)
tar -xzvf backup.tar.gz                     # Arxivdan CHIQARISH (x=extract)
zip -r backup.zip /var/www/erp-api
```

### 3.15 `scp`, `ssh`

```bash
scp local-file.txt user@server:/remote/path/
ssh user@server
ssh-keygen -t ed25519 -C "email@example.com"
```

## 4. Kod — real deployment skripti

```bash
#!/bin/bash
cd /var/www/erp-api
sudo systemctl stop erp-api
git pull origin main
dotnet publish -c Release -o ./publish
sudo chown -R www-data:www-data ./publish
sudo systemctl start erp-api
sudo systemctl status erp-api
```

## 5. Qachon ishlatish kerak?

| Vaziyat | Buyruq |
|---|---|
| Konfiguratsiya faylini tahrirlash | `vim`/`nano` |
| Ilovani qayta ishga tushirish | `systemctl restart` |
| Xatoni diagnostika qilish | `journalctl -u <service> -f` |
| Disk joyi tekshirish | `df -h` |
| Fayl ruxsatlarini sozlash | `chmod`, `chown` |

## 6. Muhim nuqtalar

- `chmod 777` — HECH QACHON ishlatilmasin (barcha ruxsat, HAMMAGA) —
  jiddiy xavfsizlik zaifligi.
- `kill -9` — jarayonni **majburan** o'chiradi, resurslarni to'g'ri
  tozalashga IMKON BERMAYDI — avval `kill -15` (SIGTERM) sinab
  ko'rish tavsiya etiladi.
- `sudo` — **faqat kerak bo'lganda** ishlatilishi kerak, har buyruq
  oldiga qo'yish yaxshi amaliyot emas.

## 7. Imtihon savollari

1. `chmod 755` va `chmod 644` orasidagi farqni tushuntiring.
2. `kill -9` va `kill -15` orasidagi farq nima?
3. `systemctl restart` va `systemctl enable` orasidagi farq nima?
4. `mkdir -p` nima uchun oddiy `mkdir`dan farq qiladi?
5. `journalctl -u <service> -f` qanday vaziyatda foydali?
