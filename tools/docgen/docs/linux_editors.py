# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "vim, nano, sudo, cat"
CATEGORY = "Linux server Deployment"
TITLE = "Linux: Matn Tahrirlash va Huquqlar"
SUBTITLE = "vim, nano, sudo va cat buyruqlari"
FILENAME = "vim, nano, sudo, cat.docx"


def build(d):
    h1(d, "1. Nima uchun bu buyruqlar")

    para(d, "Serverga SSH orqali ulanilganda grafik interfeys bo'lmaydi. "
            "Konfiguratsiya faylini ko'rish, tahrirlash va tizim darajasidagi "
            "amallarni bajarish uchun shu to'rtta buyruq deyarli har kuni "
            "kerak bo'ladi.")

    # ───────────────────────────────────────────
    h1(d, "2. cat — fayl mazmunini ko'rish")

    code(d, """cat appsettings.json              # butun faylni chiqaradi
cat -n Program.cs                # qator raqamlari bilan
cat file1.txt file2.txt          # birlashtirib chiqaradi""")

    h2(d, "2.1 Fayl yaratish")

    code(d, """# Qayta yozish
cat > notes.txt
Matn kiritiladi
Ctrl+D bilan tugatiladi

# Oxiriga qo'shish
cat >> notes.txt""")

    h2(d, "2.2 Heredoc bilan")

    code(d, """cat > /etc/systemd/system/myapp.service <<'EOF'
[Unit]
Description=MyApp API
After=network.target

[Service]
WorkingDirectory=/var/www/myapp
ExecStart=/usr/bin/dotnet /var/www/myapp/MyApp.Api.dll
Restart=always
User=www-data
Environment=ASPNETCORE_ENVIRONMENT=Production

[Install]
WantedBy=multi-user.target
EOF""")

    note(d, "`<<'EOF'` dagi qo'shtirnoq muhim:",
         "Qo'shtirnoqsiz yozsam, qobiq matn ichidagi `$` belgilarini "
         "o'zgaruvchi deb qabul qiladi va ularni almashtiradi. "
         "Konfiguratsiya faylida esa `$` ko'pincha matn sifatida kerak "
         "bo'ladi. Qo'shtirnoq bu almashtirishni o'chiradi.")

    h2(d, "2.3 Katta fayllar uchun muqobil")

    table(d, ["Buyruq", "Vazifasi"],
          [["`cat`", "Butun faylni bir yo'la chiqaradi"],
           ["`less`", "Sahifalab ko'rish; qidirish mumkin"],
           ["`head -n 20`", "Birinchi 20 qator"],
           ["`tail -n 50`", "Oxirgi 50 qator"],
           ["`tail -f`", "Yangi qatorlarni kuzatib turadi"]],
          widths=[3.6, 11.9])

    code(d, """tail -f /var/log/myapp/app.log           # loglarni jonli kuzatish
tail -n 100 -f app.log | grep ERROR      # faqat xatoliklarni""")

    note(d, "Log faylini `cat` bilan ochmaslik kerak:",
         "Gigabaytli log faylni `cat` qilsam, terminal uni to'liq "
         "chiqarmoqchi bo'ladi va bir necha daqiqa qotib qoladi. "
         "`tail -f` esa faqat oxirini ko'rsatadi va yangi qatorlarni "
         "kuzatadi — nosozlikni topishda aynan shu kerak bo'ladi.")

    # ───────────────────────────────────────────
    h1(d, "3. nano — oddiy tahrirlovchi")

    para(d, "nano o'rganish uchun eng oson tahrirlovchi. Buyruqlar ekran "
            "pastida ko'rsatib turiladi, shuning uchun hech narsa yodlash "
            "shart emas.")

    code(d, """nano appsettings.json
nano -l Program.cs        # qator raqamlari bilan""")

    table(d, ["Tugma", "Vazifasi"],
          [["`Ctrl+O`", "Saqlash (keyin `Enter`)"],
           ["`Ctrl+X`", "Chiqish"],
           ["`Ctrl+W`", "Qidirish"],
           ["`Ctrl+K`", "Qatorni kesish"],
           ["`Ctrl+U`", "Qo'yish"],
           ["`Ctrl+_`", "Qatorga o'tish"],
           ["`Alt+U`", "Bekor qilish"]],
          widths=[3.2, 12.3])

    note(d, "Ekrandagi `^O` belgisi `Ctrl+O` degani:",
         "Bu eski terminal an'anasi va birinchi marta chalkashtiradi. "
         "`^` — `Ctrl`, `M-` — `Alt`. Buni bilsam, ekran pastidagi "
         "ro'yxat butunlay tushunarli bo'ladi.")

    # ───────────────────────────────────────────
    h1(d, "4. vim — kuchli tahrirlovchi")

    para(d, "vim deyarli har qanday Linux tizimida mavjud va serverda "
            "nano bo'lmasligi mumkin. Shuning uchun uning asoslarini "
            "bilish foydali.")

    h2(d, "4.1 Rejimlar")

    table(d, ["Rejim", "Nima qilinadi", "Qanday kiriladi"],
          [["Normal", "Harakat va buyruqlar", "`Esc`"],
           ["Insert", "Matn yozish", "`i`, `a`, `o`"],
           ["Visual", "Belgilash", "`v`, `V`, `Ctrl+v`"],
           ["Command", "`:` buyruqlari", "`:`"]],
          widths=[3.2, 7.3, 5.0])

    note(d, "Rejimlar tushunchasi — vim dagi asosiy to'siq:",
         "Odatdagi tahrirlovchida men faylni ochib, darhol yoza "
         "boshlayman. vim esa Normal rejimda ochiladi va u yerda har bir "
         "harf buyruq hisoblanadi. `d` bosilsa — o'chirish, `x` bosilsa — "
         "belgi o'chadi. Bu bilmaganga juda chalkash tuyuladi.")

    h2(d, "4.2 Eng zarur buyruqlar")

    code(d, """# Chiqish
:q        # chiqish (o'zgarish bo'lmasa)
:q!       # saqlamasdan chiqish
:wq       # saqlab chiqish
:w        # faqat saqlash

# Tahrirlash boshlash
i         # kursordan oldin yozish
a         # kursordan keyin yozish
o         # pastga yangi qator ochish

# Harakat
gg        # fayl boshiga
G         # fayl oxiriga
:42       # 42-qatorga

# O'chirish
dd        # qatorni o'chirish
3dd       # uchta qatorni
u         # bekor qilish

# Qidirish
/xato     # oldinga qidirish
n         # keyingi natija
:%s/eski/yangi/g    # hammasini almashtirish""")

    note(d, "Eng muhim buyruq — `:q!`:",
         "vim ichiga tasodifan kirib qolgan va chiqa olmagan holat juda "
         "keng tarqalgan. `Esc` bosib, keyin `:q!` yozib `Enter` bosish "
         "har doim ishlaydi — o'zgarishlar saqlanmaydi, lekin kamida "
         "chiqib ketish mumkin.")

    h2(d, "4.3 Sukutdagi tahrirlovchini o'zgartirish")

    code(d, """# Joriy sessiya uchun
export EDITOR=nano

# Doimiy
echo 'export EDITOR=nano' >> ~/.bashrc

# git uchun alohida
git config --global core.editor nano""")

    # ───────────────────────────────────────────
    h1(d, "5. sudo — huquqlarni ko'tarish")

    para(d, "Linux da tizim fayllarini o'zgartirish uchun administrator "
            "huquqi kerak. `sudo` bitta buyruqni shunday huquq bilan "
            "bajaradi.")

    code(d, """sudo systemctl restart myapp
sudo nano /etc/nginx/nginx.conf
sudo -u postgres psql          # boshqa foydalanuvchi nomidan
sudo -i                        # root qobig'iga o'tish""")

    h2(d, "5.1 Nega root bilan ishlamaslik kerak")

    bullets(d, [
        "Xato buyruq butun tizimni buzishi mumkin.",
        "Har bir `sudo` chaqiruvi logga yoziladi — kim nima qilgani "
        "ma'lum bo'ladi.",
        "Zararli dastur oddiy foydalanuvchi huquqi bilan cheklangan "
        "bo'ladi.",
    ])

    code(d, """# Kim nima qilganini ko'rish
sudo cat /var/log/auth.log | grep sudo""")

    h2(d, "5.2 Keng tarqalgan tuzoq")

    code(d, """# Ishlamaydi — qayta yo'naltirish oddiy huquq bilan bajariladi
sudo echo "text" > /etc/protected.conf

# To'g'ri yechimlar
echo "text" | sudo tee /etc/protected.conf
echo "text" | sudo tee -a /etc/protected.conf    # qo'shish
sudo sh -c 'echo "text" > /etc/protected.conf'""")

    note(d, "Bu meni bir marta chalg'itgan:",
         "`sudo` faqat `echo` ga tegishli, `>` esa joriy qobiq tomonidan "
         "bajariladi — u esa oddiy huquqda ishlaydi. Shuning uchun "
         "\"Permission denied\" chiqadi, garchi men `sudo` yozgan "
         "bo'lsam ham. `tee` esa to'liq `sudo` ostida ishlaydi va "
         "muammoni hal qiladi.")

    h2(d, "5.3 Sudoers sozlamalari")

    code(d, """sudo visudo        # faylni tekshirish bilan ochadi""")

    code(d, """# Parolsiz ma'lum buyruqlar
deploy ALL=(ALL) NOPASSWD: /bin/systemctl restart myapp
deploy ALL=(ALL) NOPASSWD: /bin/systemctl status myapp""")

    note(d, "`visudo` dan foydalanish shart:",
         "U faylni saqlashdan oldin sintaksisni tekshiradi. Agar "
         "`/etc/sudoers` faylida xato bo'lsa, `sudo` umuman ishlamay "
         "qoladi va uni tuzatish uchun huquq kerak — ya'ni yopiq doira "
         "hosil bo'ladi. `visudo` aynan shundan himoya qiladi.")

    # ───────────────────────────────────────────
    h1(d, "6. Amaliy ketma-ketlik")

    code(d, """# 1. Joriy holatni ko'rish
cat /etc/nginx/sites-available/myapp

# 2. Zaxira nusxa olish
sudo cp /etc/nginx/sites-available/myapp \\
        /etc/nginx/sites-available/myapp.bak

# 3. Tahrirlash
sudo nano /etc/nginx/sites-available/myapp

# 4. Sintaksisni tekshirish
sudo nginx -t

# 5. Qo'llash
sudo systemctl reload nginx

# 6. Natijani tekshirish
sudo systemctl status nginx
curl -I http://localhost/""")

    note(d, "Ikkinchi qadamni men hech qachon tashlab ketmayman:",
         "Konfiguratsiya faylini tahrirlashdan oldin nusxa olish bir soniya "
         "vaqt oladi, lekin xato qilganimda hammasini tiklashga imkon "
         "beradi. Serverda esa xato qilish — xizmat ishlamasligi degani.")

    # ───────────────────────────────────────────
    h1(d, "7. Xulosa")

    bullets(d, [
        "`cat` faylni to'liq chiqaradi; katta fayllar uchun `less`, "
        "`head`, `tail` ishlatiladi.",
        "`tail -f` loglarni jonli kuzatish uchun asosiy vosita.",
        "Heredoc (`<<'EOF'`) bilan fayl yaratish qulay; qo'shtirnoq "
        "o'zgaruvchi almashtirishni o'chiradi.",
        "nano oddiy va buyruqlari ekranda ko'rinadi; `^O` — `Ctrl+O`.",
        "vim rejimlarga asoslangan; `Esc` keyin `:q!` har doim chiqish "
        "imkonini beradi.",
        "`sudo` bitta buyruqni administrator huquqi bilan bajaradi va "
        "logga yozadi.",
        "`sudo echo > fayl` ishlamaydi — `sudo tee` ishlatish kerak.",
        "`/etc/sudoers` ni faqat `visudo` orqali tahrirlash lozim.",
    ])

    sources(d, [
        ("GNU nano — rasmiy hujjat",
         "https://www.nano-editor.org/docs.php"),
        ("Vim documentation",
         "https://vimhelp.org/"),
        ("sudo(8) — Linux manual page",
         "https://man7.org/linux/man-pages/man8/sudo.8.html"),
        ("cat(1) — Linux manual page",
         "https://man7.org/linux/man-pages/man1/cat.1.html"),
    ])
