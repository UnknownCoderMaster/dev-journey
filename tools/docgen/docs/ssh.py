# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "SSH"
CATEGORY = "Web"
TITLE = "SSH"
SUBTITLE = "Masofaviy serverga xavfsiz ulanish va kalitlar bilan ishlash"
FILENAME = "SSH.docx"


def build(d):
    h1(d, "1. SSH nima")

    para(d, "SSH (Secure Shell) — masofadagi kompyuterga shifrlangan kanal orqali "
            "ulanish protokoli. U 22-portda ishlaydi va serverni boshqarishning "
            "asosiy vositasi hisoblanadi.")

    para(d, "SSH dan oldin Telnet ishlatilgan, lekin u ma'lumotni ochiq matnda "
            "uzatardi — parol ham shu holda ketardi. SSH butun aloqani shifrlaydi va "
            "serverning haqiqiyligini ham tekshiradi.")

    code(d, """ssh user@192.168.1.50
ssh -p 2222 deploy@server.example.com""")

    # ───────────────────────────────────────────
    h1(d, "2. Ulanish qanday kechadi")

    bullets(d, [
        "Mijoz serverga ulanadi va ikkalasi shifrlash usulini kelishib oladi.",
        "Server o'zining ochiq kalitini yuboradi; mijoz uni tekshiradi.",
        "Umumiy sessiya kaliti hosil qilinadi va aloqa shifrlanadi.",
        "Shundan keyingina foydalanuvchi autentifikatsiyadan o'tadi.",
    ], numbered=True)

    para(d, "Ketma-ketlikdagi muhim tafsilot: parol shifrlangan kanal o'rnatilgandan "
            "**keyin** yuboriladi, ya'ni u hech qachon ochiq holda ketmaydi.")

    h2(d, "2.1 Server kalitini tekshirish")

    para(d, "Birinchi ulanishda quyidagi savol chiqadi:")

    code(d, """The authenticity of host 'server.example.com' can't be established.
ED25519 key fingerprint is SHA256:abc123...
Are you sure you want to continue connecting (yes/no)?""")

    para(d, "Tasdiqlangandan keyin kalit `~/.ssh/known_hosts` fayliga yoziladi. "
            "Keyingi ulanishlarda u taqqoslanadi.")

    note(d, "Bu ogohlantirishni e'tiborsiz qoldirmaslik kerak:",
         "Agar keyinroq \"REMOTE HOST IDENTIFICATION HAS CHANGED\" degan "
         "ogohlantirish chiqsa, bu ikki narsani anglatishi mumkin: yo server qayta "
         "o'rnatilgan, yo kimdir o'rtada turib o'zini server qilib ko'rsatyapti. "
         "Ko'pchilik birinchisini taxmin qilib, `known_hosts` dan satrni o'chirib "
         "tashlaydi — lekin avval sababini aniqlash to'g'riroq bo'ladi.")

    # ───────────────────────────────────────────
    h1(d, "3. Kalitlar bilan autentifikatsiya")

    para(d, "Parol o'rniga kalit juftligi ishlatilishi mumkin va bu ancha xavfsizroq. "
            "Juftlik ikki fayldan iborat: maxfiy kalit mening mashinamda qoladi, "
            "ochiq kalit serverga joylashtiriladi.")

    h2(d, "3.1 Kalit yaratish")

    code(d, """ssh-keygen -t ed25519 -C "orzibek@ish-kompyuteri"

# Natija:
#   ~/.ssh/id_ed25519       — maxfiy kalit (hech kimga berilmaydi)
#   ~/.ssh/id_ed25519.pub   — ochiq kalit (serverga qo'yiladi)""")

    table(d, ["Algoritm", "Holati"],
          [["`ed25519`", "Tavsiya etiladi — qisqa, tez, mustahkam"],
           ["`rsa` (4096 bit)", "Ishlaydi, eski tizimlar uchun"],
           ["`rsa` (1024 bit)", "Ishlatilmaydi — zaif"],
           ["`dsa`", "Eskirgan, o'chirilgan"]],
          widths=[4.0, 11.5])

    h2(d, "3.2 Kalitni serverga joylashtirish")

    code(d, """ssh-copy-id user@server.example.com

# Yoki qo'lda:
cat ~/.ssh/id_ed25519.pub | ssh user@server \\
    "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"

# Huquqlar to'g'ri bo'lishi shart:
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys""")

    note(d, "Huquqlar masalasi ko'p vaqt oladi:",
         "SSH `authorized_keys` fayliga boshqalar yoza olsa, uni umuman "
         "ishlatmaydi va buni jimgina qiladi — xatolik xabari aniq bo'lmaydi. "
         "Kalit ishlamayotganda men birinchi navbatda huquqlarni tekshiraman. "
         "Serverda `/var/log/auth.log` faylida sabab yozilgan bo'ladi.")

    h2(d, "3.3 Maxfiy kalit parolini saqlash")

    code(d, """# Agentni ishga tushirish va kalitni qo'shish
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519""")

    para(d, "Agent kalitni xotirada ochiq holda saqlaydi, shunda har ulanishda "
            "parol so'ralmaydi.")

    # ───────────────────────────────────────────
    h1(d, "4. SSH konfiguratsiya fayli")

    para(d, "Har safar uzun buyruq yozmaslik uchun `~/.ssh/config` faylida qisqa "
            "nomlar belgilanadi:")

    code(d, """Host prod
    HostName 203.0.113.42
    User deploy
    Port 2222
    IdentityFile ~/.ssh/id_ed25519_prod
    ServerAliveInterval 60

Host staging
    HostName 203.0.113.43
    User deploy
    IdentityFile ~/.ssh/id_ed25519_staging""")

    code(d, """ssh prod            # endi shu yetarli
scp build.zip prod:/var/www/""")

    # ───────────────────────────────────────────
    h1(d, "5. Fayl uzatish")

    code(d, """# Bitta fayl
scp report.pdf user@server:/home/user/

# Papka
scp -r ./dist user@server:/var/www/app/

# Serverdan olish
scp user@server:/var/log/app.log ./

# Sinxronlash — faqat o'zgarganini yuboradi
rsync -avz --delete ./dist/ user@server:/var/www/app/""")

    para(d, "Katta yoki tez-tez yangilanadigan papkalar uchun `rsync` ancha "
            "samarali — u faqat farqni uzatadi.")

    # ───────────────────────────────────────────
    h1(d, "6. Tunnel yaratish")

    para(d, "SSH orqali faqat buyruq bajarish emas, port yo'naltirish ham mumkin. "
            "Bu ichki tarmoqdagi xizmatga xavfsiz ulanishning oddiy usuli.")

    h2(d, "6.1 Lokal yo'naltirish")

    code(d, """ssh -L 5433:localhost:5432 user@server""")

    para(d, "Endi o'z kompyuterimdagi 5433-port serverdagi 5432-portga ulanadi. "
            "Bazani internetga ochmasdan turib unga ulanish mumkin bo'ladi:")

    code(d, """Host=localhost;Port=5433;Database=app;Username=app_user""")

    note(d, "Bu usul menga juda qo'l keladi:",
         "Production bazasini tashqariga ochish xavfli, lekin ba'zan unga ulanib "
         "tekshirish kerak bo'ladi. SSH tunnel bu masalani hal qiladi — baza porti "
         "yopiq qoladi, men esa SSH orqali unga yetib boraman. Qo'shimcha hech "
         "qanday sozlama kerak emas.")

    h2(d, "6.2 Masofaviy yo'naltirish")

    code(d, """ssh -R 8080:localhost:3000 user@server""")

    para(d, "Teskari yo'nalish — serverdagi 8080-port mening mashinamdagi 3000-portga "
            "ulanadi. Lokal ishlab chiqilayotgan xizmatni tashqariga ko'rsatish uchun "
            "ishlatiladi.")

    # ───────────────────────────────────────────
    h1(d, "7. Serverni xavfsizlash")

    code(d, """# /etc/ssh/sshd_config

PermitRootLogin no              # root bilan to'g'ridan-to'g'ri kirmaslik
PasswordAuthentication no       # faqat kalit bilan
PubkeyAuthentication yes
Port 2222                       # standart bo'lmagan port
MaxAuthTries 3
AllowUsers deploy admin""")

    code(d, """sudo sshd -t                    # konfiguratsiyani tekshirish
sudo systemctl restart sshd""")

    note(d, "Buni qilishdan oldin ehtiyot chorasi:",
         "`PasswordAuthentication no` qo'yishdan oldin kalit bilan kirish "
         "ishlayotganiga **ishonch hosil qilish** kerak. Men bir marta kalitni "
         "to'g'ri joylashtirmasdan parolni o'chirib qo'ygandim va serverga kira "
         "olmay qoldim. Qoidam shu: yangi sozlamani sinab ko'rish uchun eski "
         "sessiyani ochiq qoldirib, ikkinchi oynada yangi ulanish urinib ko'raman.")

    para(d, "Qo'shimcha himoya sifatida takroriy noto'g'ri urinishlarni bloklovchi "
            "vosita o'rnatiladi:")

    code(d, """sudo apt install fail2ban
sudo systemctl enable --now fail2ban""")

    # ───────────────────────────────────────────
    h1(d, "8. Nosozlikni topish")

    code(d, """ssh -v user@server      # batafsil
ssh -vvv user@server    # eng batafsil

# Serverda
sudo tail -f /var/log/auth.log
sudo systemctl status sshd""")

    table(d, ["Xatolik", "Odatdagi sabab"],
          [["Permission denied (publickey)", "Kalit joylashtirilmagan yoki huquqlar noto'g'ri"],
           ["Connection refused", "SSH xizmati ishlamayapti yoki port boshqa"],
           ["Connection timed out", "Firewall bloklayapti yoki manzil noto'g'ri"],
           ["Host key verification failed", "Server kaliti o'zgargan"]],
          widths=[5.6, 9.9])

    # ───────────────────────────────────────────
    h1(d, "9. Xulosa")

    bullets(d, [
        "SSH 22-portda ishlaydi va butun aloqani shifrlaydi; parol shifrlangan "
        "kanal o'rnatilgandan keyin yuboriladi.",
        "`known_hosts` serverning haqiqiyligini tekshiradi; kalit o'zgarganidagi "
        "ogohlantirishni jiddiy qabul qilish kerak.",
        "Kalit bilan autentifikatsiya paroldan xavfsizroq; `ed25519` tavsiya "
        "etiladi.",
        "`authorized_keys` fayli huquqlari noto'g'ri bo'lsa, kalit jimgina "
        "ishlamaydi.",
        "`~/.ssh/config` ulanishlarni qisqa nomlar bilan saqlaydi.",
        "`-L` lokal, `-R` masofaviy port yo'naltirishni beradi; tunnel bazani "
        "ochmasdan unga ulanish imkonini beradi.",
        "Serverda `PermitRootLogin no` va `PasswordAuthentication no` qo'yish "
        "tavsiya etiladi — lekin avval kalitni sinab ko'rish shart.",
    ])

    sources(d, [
        ("OpenSSH — rasmiy sayt",
         "https://www.openssh.com/manual.html"),
        ("ssh_config(5) — OpenSSH manual",
         "https://man.openbsd.org/ssh_config"),
        ("sshd_config(5) — OpenSSH manual",
         "https://man.openbsd.org/sshd_config"),
    ])
