# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "df, ls, mkdir, cd, pwd, chmod, touch"
CATEGORY = "Linux server Deployment"
TITLE = "Linux: Fayl Tizimi Buyruqlari"
SUBTITLE = "Harakatlanish, papka yaratish va huquqlarni boshqarish"
FILENAME = "df, ls, mkdir, cd, pwd, chmod, touch.docx"


def build(d):
    h1(d, "1. Harakatlanish")

    h2(d, "1.1 pwd — qayerdaman")

    code(d, """pwd
# /var/www/myapp""")

    h2(d, "1.2 cd — papkaga o'tish")

    code(d, """cd /var/www/myapp      # mutlaq yo'l
cd logs                # nisbiy yo'l
cd ..                  # bir daraja yuqoriga
cd ~                   # uy papkasiga
cd -                   # oldingi papkaga qaytish
cd                     # uy papkasiga (argumentsiz)""")

    note(d, "`cd -` juda qulay:",
         "Ikki papka orasida tez-tez o'tish kerak bo'lganda u vaqt tejaydi. "
         "Masalan konfiguratsiya va loglar orasida — har safar to'liq yo'l "
         "yozmasdan, bitta belgi bilan almashish mumkin.")

    # ───────────────────────────────────────────
    h1(d, "2. ls — mazmunni ko'rish")

    code(d, """ls                 # oddiy ro'yxat
ls -l              # batafsil
ls -la             # yashirin fayllar bilan
ls -lh             # o'qiladigan hajm (KB, MB)
ls -lt             # vaqt bo'yicha saralangan
ls -ltr            # eng yangisi oxirida
ls -ld papka/      # papkaning o'zi haqida""")

    h2(d, "2.1 Batafsil chiqishni o'qish")

    code(d, """-rw-r--r--  1 www-data www-data  1.2K Oct 31 14:30 appsettings.json
drwxr-xr-x  3 www-data www-data  4.0K Oct 31 14:25 logs
-rwxr-xr-x  1 root     root      8.5M Oct 30 09:12 MyApp.Api
│└┬┘└┬┘└┬┘  │ └───┬──┘ └───┬──┘  └─┬─┘ └────┬────┘ └──────┬──────┘
│ │  │  │   │     │        │       │        │            │
│ │  │  │   │   egasi   guruhi   hajmi   o'zgartirilgan  nomi
│ │  │  └── boshqalar huquqi
│ │  └───── guruh huquqi
│ └──────── egasi huquqi
└────────── tur: - fayl, d papka, l havola""")

    # ───────────────────────────────────────────
    h1(d, "3. mkdir va touch — yaratish")

    code(d, """mkdir logs                          # bitta papka
mkdir -p /var/www/myapp/logs/2026    # oraliq papkalar bilan
mkdir -p app/{src,tests,docs}        # bir nechta birdan

touch app.log                        # bo'sh fayl yaratish
touch -a app.log                     # faqat o'qilgan vaqtni yangilash""")

    note(d, "`-p` bayrog'i ikkita foyda beradi:",
         "Birinchidan, u yo'ldagi barcha oraliq papkalarni yaratadi. "
         "Ikkinchidan, papka allaqachon mavjud bo'lsa, xatolik bermaydi. "
         "Shuning uchun skriptlarda `mkdir -p` yozish xavfsizroq — "
         "skript qayta ishga tushirilganda to'xtab qolmaydi.")

    note(d, "`touch` ning asosiy vazifasi aslida boshqa:",
         "U fayl vaqt belgilarini yangilash uchun yaratilgan. Bo'sh fayl "
         "yaratish — qo'shimcha ta'sir, chunki fayl bo'lmasa, u yaratiladi. "
         "Shuning uchun **mavjud faylga `touch` qilish uning mazmunini "
         "o'chirmaydi** — bu ko'pchilik o'ylagandan farqli.")

    # ───────────────────────────────────────────
    h1(d, "4. chmod — huquqlarni boshqarish")

    para(d, "Linux da har bir fayl uchun uch toifa huquq belgilanadi: "
            "egasi (user), guruh (group) va boshqalar (others).")

    table(d, ["Huquq", "Harf", "Raqam", "Fayl uchun", "Papka uchun"],
          [["O'qish", "`r`", "4", "Mazmunni o'qish", "Ro'yxatni ko'rish"],
           ["Yozish", "`w`", "2", "O'zgartirish", "Fayl qo'shish/o'chirish"],
           ["Bajarish", "`x`", "1", "Dastur sifatida ishga tushirish",
            "Ichiga kirish"]],
          widths=[2.6, 1.8, 1.8, 4.8, 4.5])

    h2(d, "4.1 Raqamli yozuv")

    code(d, """chmod 644 appsettings.json
#      │││
#      ││└── boshqalar: 4 = r--
#      │└─── guruh:     4 = r--
#      └──── egasi:     6 = rw-

chmod 755 deploy.sh      # rwxr-xr-x
chmod 600 private.key    # rw------- (faqat egasi)
chmod 700 secrets/       # rwx------ (faqat egasi kira oladi)""")

    table(d, ["Qiymat", "Ko'rinishi", "Qachon"],
          [["`644`", "`rw-r--r--`", "Oddiy fayllar"],
           ["`755`", "`rwxr-xr-x`", "Skriptlar va papkalar"],
           ["`600`", "`rw-------`", "Maxfiy fayllar, kalitlar"],
           ["`700`", "`rwx------`", "Maxfiy papkalar"],
           ["`777`", "`rwxrwxrwx`", "**Deyarli hech qachon**"]],
          widths=[2.6, 4.4, 8.5])

    note(d, "`chmod 777` haqida alohida gapirish kerak:",
         "Internetda muammoga yechim sifatida juda ko'p tavsiya qilinadi "
         "va u haqiqatan muammoni \"hal qiladi\" — chunki hamma narsaga "
         "ruxsat beradi. Lekin bu serverdagi har qanday jarayon o'sha "
         "faylni o'zgartira olishini anglatadi. To'g'ri yechim — egani "
         "to'g'rilash yoki aniq huquq berish, hamma narsani ochish emas.")

    h2(d, "4.2 Harfli yozuv")

    code(d, """chmod u+x deploy.sh        # egasiga bajarish huquqi
chmod g-w config.json      # guruhdan yozishni olib tashlash
chmod o-rwx secrets/       # boshqalardan hamma narsani olib tashlash
chmod a+r public.txt       # hammaga o'qish

chmod -R 755 /var/www/myapp    # rekursiv""")

    note(d, "Rekursiv `chmod` bilan ehtiyot bo'lish kerak:",
         "`chmod -R 755` papkalar uchun to'g'ri, lekin barcha fayllarga "
         "bajarish huquqini beradi — bu keraksiz. Fayl va papkalarni "
         "alohida ishlash to'g'riroq:")

    code(d, """find /var/www/myapp -type d -exec chmod 755 {} \\;
find /var/www/myapp -type f -exec chmod 644 {} \\;""")

    h2(d, "4.3 chown — egasini o'zgartirish")

    code(d, """sudo chown www-data:www-data /var/www/myapp
sudo chown -R www-data:www-data /var/www/myapp
sudo chown deploy /var/www/myapp/deploy.sh""")

    note(d, "Huquq muammolarining ko'pchiligi aslida ega muammosi:",
         "Fayl `root` ga tegishli, ilova esa `www-data` nomidan ishlaydi — "
         "shuning uchun u faylni o'qiy olmaydi. `chmod 777` buni "
         "\"tuzatadi\", lekin to'g'ri yechim `chown` bilan egani "
         "o'zgartirish bo'ladi.")

    # ───────────────────────────────────────────
    h1(d, "5. df — disk joyi")

    code(d, """df -h              # o'qiladigan shaklda
df -h /var         # ma'lum bo'lim uchun
df -i              # inode lar (fayllar soni chegarasi)""")

    code(d, """Filesystem      Size  Used Avail Use% Mounted on
/dev/sda1        50G   42G  5.5G  89% /
/dev/sdb1       100G   12G   83G  13% /var/lib/docker""")

    note(d, "`Use%` 90% dan oshsa, jiddiy muammo yaqinlashgan:",
         "Disk to'lganda baza yozishni to'xtatadi, loglar yozilmaydi va "
         "ilova kutilmagan tarzda ishdan chiqadi. Eng yomoni — bu "
         "xatoliklar tushunarsiz bo'ladi va sabab darhol ko'rinmaydi.")

    h2(d, "5.1 Nima joy egallayotganini topish")

    code(d, """du -sh /var/*                    # har bir papka hajmi
du -h --max-depth=1 /var/log     # bir daraja chuqurlikda
du -sh * | sort -rh | head -10   # eng kattalari

# Eng katta fayllarni topish
find /var -type f -size +100M -exec ls -lh {} \\;""")

    h2(d, "5.2 Tipik sabablar")

    bullets(d, [
        "**Loglar** — rotatsiya sozlanmagan bo'lsa, cheksiz o'sadi.",
        "**Docker** — ishlatilmayotgan tasvirlar va hajmlar.",
        "**Baza jurnallari** — WAL fayllari tozalanmasa.",
        "**Vaqtinchalik fayllar** — `/tmp` tozalanmagan bo'lsa.",
    ])

    code(d, """# Docker tozalash
docker system df                 # nima joy egallayotganini ko'rish
docker system prune -a --volumes # tozalash (ehtiyotkorlik bilan)

# Log rotatsiyasi
sudo nano /etc/logrotate.d/myapp""")

    code(d, """/var/log/myapp/*.log {
    daily
    rotate 14
    compress
    missingok
    notifempty
    create 0640 www-data www-data
}""")

    note(d, "`du` va `df` farq ko'rsatishi mumkin:",
         "Agar o'chirilgan fayl hali biror jarayon tomonidan ochiq "
         "turgan bo'lsa, `du` uni ko'rmaydi, lekin `df` joy band "
         "ekanini ko'rsatadi. Bunday holatda `lsof +L1` buyrug'i "
         "aybdorni topadi — odatda bu xizmatni qayta ishga tushirish "
         "bilan hal bo'ladi.")

    # ───────────────────────────────────────────
    h1(d, "6. Amaliy joylashtirish ketma-ketligi")

    code(d, """# Joy yetarliligini tekshirish
df -h /var/www

# Papka tuzilmasini yaratish
sudo mkdir -p /var/www/myapp/{logs,data,backups}

# Egalikni belgilash
sudo chown -R www-data:www-data /var/www/myapp

# Huquqlarni sozlash
sudo chmod 755 /var/www/myapp
sudo chmod 775 /var/www/myapp/logs      # xizmat yozishi kerak
sudo chmod 700 /var/www/myapp/data      # faqat egasi

# Natijani tekshirish
ls -la /var/www/myapp""")

    # ───────────────────────────────────────────
    h1(d, "7. Xulosa")

    bullets(d, [
        "`pwd` joriy papkani, `cd -` oldingisiga qaytishni beradi.",
        "`ls -lh` eng ko'p ishlatiladigan shakl; chiqishning birinchi "
        "ustuni huquqlarni ko'rsatadi.",
        "`mkdir -p` oraliq papkalarni yaratadi va mavjud bo'lsa xatolik "
        "bermaydi.",
        "`touch` mavjud faylning mazmunini o'chirmaydi.",
        "Huquqlar uch toifa uchun: egasi, guruh, boshqalar; `r`=4, "
        "`w`=2, `x`=1.",
        "`chmod 777` deyarli hech qachon to'g'ri yechim emas — ko'pincha "
        "muammo `chown` bilan hal bo'ladi.",
        "Fayl va papkalarga rekursiv huquqni alohida berish to'g'riroq.",
        "`df -h` disk to'lishini, `du -sh` esa sababni ko'rsatadi.",
    ])

    sources(d, [
        ("Coreutils — GNU manual",
         "https://www.gnu.org/software/coreutils/manual/coreutils.html"),
        ("chmod(1) — Linux manual page",
         "https://man7.org/linux/man-pages/man1/chmod.1.html"),
        ("df(1) — Linux manual page",
         "https://man7.org/linux/man-pages/man1/df.1.html"),
        ("Host ASP.NET Core on Linux with Nginx",
         "https://learn.microsoft.com/en-us/aspnet/core/host-and-deploy/linux-nginx"),
    ])
