# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "git log, git checkout,"
CATEGORY = "Git / Github / Gitlab"
TITLE = "git log va git checkout"
SUBTITLE = "Tarixni o'qish va holatlar orasida harakatlanish"
FILENAME = "git log, git checkout.docx"


def build(d):
    h1(d, "1. git log — tarixni o'qish")

    para(d, "Oddiy `git log` ko'p joy egallaydi va ko'rish noqulay. "
            "Men eng ko'p ishlatadigan shakllar:")

    code(d, """# Bir qatorda, grafik bilan — eng ko'p ishlatadiganim
git log --oneline --graph --decorate --all

# Oxirgi 10 commit
git log -10 --oneline

# Fayl bo'yicha
git log --oneline -- src/Services/PriceCalculator.cs

# Kod bo'yicha: shu matn qo'shilgan yoki o'chirilgan commit'lar
git log -S "CalculateDiscount" --oneline

# Muallif va sana bo'yicha
git log --author="Orzibek" --since="2 weeks ago" --oneline

# Commit xabari bo'yicha
git log --grep="payment" --oneline

# O'zgarishlar statistikasi bilan
git log --stat -3""")

    para(d, "`-S` (pickaxe) ni alohida ta'kidlayman — u \"bu funksiya "
            "qachon paydo bo'ldi yoki qachon o'chirildi\" degan savolga "
            "javob beradi. Bu juda tez-tez kerak bo'ladi va boshqa "
            "usul bilan topish qiyin.")

    h2(d, "O'z formatini yasash")

    code(d, """git log --pretty=format:"%h %ad %an: %s" --date=short -10""")

    code(d, """# Alias qilib qo'yish
git config --global alias.lg \\
  "log --graph --pretty=format:'%C(auto)%h%d %s %C(dim)(%an, %ar)' --all"

# Keyin shunchaki
git lg""")

    # ───────────────────────────────────────────
    h1(d, "2. Kim va qachon o'zgartirgan")

    code(d, """# Har bir qator kim tomonidan oxirgi o'zgartirilgan
git blame src/Services/PriceCalculator.cs

# Faqat ma'lum qatorlar
git blame -L 40,60 src/Services/PriceCalculator.cs

# Bo'shliq o'zgarishlarini e'tiborsiz qoldirish — formatlash commit'ini o'tkazadi
git blame -w src/Services/PriceCalculator.cs""")

    para(d, "`-w` juda foydali: avtomatik formatlash commit'i hamma "
            "qatorni \"o'zgartirgan\" bo'lib ko'rinadi va asl muallifni "
            "yashiradi. `-w` bo'shliq o'zgarishlarini hisobga olmaydi.")

    note(d, "Maqsad haqida",
         "`blame` ni \"kim aybdor\" uchun emas, **kontekst** uchun "
         "ishlataman: shu qator qaysi commit'da, qaysi vazifa uchun "
         "yozilgan. Commit xabari va ticket raqami odatda nima uchun "
         "shunday qilinganini tushuntiradi.")

    # ───────────────────────────────────────────
    h1(d, "3. Commit'lar orasidagi farq")

    code(d, """# Joriy o'zgarishlar (stage qilinmagan)
git diff

# Stage qilinganlar
git diff --staged

# Ikki branch orasidagi farq
git diff main..feature/order-export

# Faqat o'zgargan fayl nomlari
git diff --name-status main..feature/order-export

# Uch nuqta: umumiy ajdoddan beri feature'da nima o'zgargan
git diff main...feature/order-export""")

    para(d, "Ikki nuqta va uch nuqta farqi muhim. `main..feature` — "
            "ikki holatning to'g'ridan-to'g'ri farqi. "
            "`main...feature` — umumiy ajdoddan beri faqat `feature` "
            "da nima o'zgargani. PR'ni ko'rib chiqishda ikkinchisi "
            "to'g'ri, chunki `main` dagi boshqa o'zgarishlarni "
            "aralashtirmaydi.")

    # ───────────────────────────────────────────
    h1(d, "4. git checkout — uchta turli vazifa")

    para(d, "`checkout` tarixan juda ko'p ishni bajargan va bu "
            "chalkashlik manbai bo'lgan. Git 2.23 da u ikkiga "
            "bo'lingan:")

    table(d, ["Vazifa", "Eski buyruq", "Yangi buyruq"],
          [["Branch almashtirish", "`git checkout main`", "`git switch main`"],
           ["Branch yaratish", "`git checkout -b x`", "`git switch -c x`"],
           ["Fayl o'zgarishini bekor qilish", "`git checkout -- file`",
            "`git restore file`"],
           ["Commit'ga o'tish", "`git checkout a677ee1`",
            "`git switch --detach a677ee1`"]],
          widths=[4.6, 5.0, 4.9])

    para(d, "Yangi buyruqlarni ishlatishni afzal ko'raman, chunki "
            "niyat aniq ko'rinadi. Ayniqsa `restore` — `checkout -- file` "
            "ni tasodifan `checkout file` deb yozish branch'ga o'tishga "
            "urinishga aylanishi mumkin.")

    # ───────────────────────────────────────────
    h1(d, "5. Fayl va o'zgarishlarni tiklash")

    code(d, """# Stage qilinmagan o'zgarishni bekor qilish — O'ZGARISH YO'QOLADI
git restore src/Services/PriceCalculator.cs

# Hamma fayl
git restore .

# Stage'dan olib tashlash (o'zgarish saqlanadi)
git restore --staged src/Services/PriceCalculator.cs

# Boshqa commit'dagi versiyani olish
git restore --source=a677ee1 src/Services/PriceCalculator.cs

# O'chirilgan faylni tiklash
git restore --source=HEAD~1 src/Legacy/OldService.cs""")

    note(d, "Ehtiyot bo'ling",
         "`git restore <file>` commit qilinmagan o'zgarishni **qaytarib "
         "bo'lmaydigan** tarzda o'chiradi. Git'da bu o'zgarishning "
         "hech qanday nusxasi yo'q. Shubha bo'lsa, avval "
         "`git stash` qilaman — u o'zgarishni saqlab qo'yadi.")

    # ───────────────────────────────────────────
    h1(d, "6. Detached HEAD holati")

    code(d, """git switch --detach a677ee1
# yoki
git checkout a677ee1""")

    code(d, """You are in 'detached HEAD' state. You can look around, make
experimental changes and commit them...""")

    para(d, "Bu holatda `HEAD` branch'ga emas, to'g'ridan-to'g'ri "
            "commit'ga ishora qiladi. Ko'rish va sinash uchun "
            "normal holat — masalan eski versiyani ishga tushirib "
            "tekshirish.")

    para(d, "Xavfi: bu holatda commit qilsam, u **hech qanday "
            "branch'ga tegishli bo'lmaydi**. Boshqa branch'ga "
            "o'tishim bilan u \"yetib bo'lmaydigan\" bo'lib qoladi "
            "va oxir-oqibat garbage collection bilan o'chadi.")

    code(d, """# Detached holatda qilingan ishni saqlash
git switch -c experiment/new-approach

# Yoki keyinroq reflog'dan topish
git reflog
git switch -c recovered a677ee1""")

    # ───────────────────────────────────────────
    h1(d, "7. Reflog — xavfsizlik to'ri")

    code(d, """git reflog""")

    code(d, """a677ee1 HEAD@{0}: commit: Middle D hujjatlari
4e06e4e HEAD@{1}: checkout: moving from feature/x to main
9f3c2a1 HEAD@{2}: rebase finished: returning to refs/heads/feature/x""")

    para(d, "`reflog` — `HEAD` ning hamma harakati. Bu Git'ning eng "
            "muhim xavfsizlik mexanizmi: noto'g'ri `reset --hard`, "
            "o'chirilgan branch, buzilgan rebase — hammasi shu "
            "yerdan topiladi.")

    code(d, """# Noto'g'ri reset'ni qaytarish
git reset --hard HEAD@{1}

# Buzilgan rebase'dan oldingi holatga qaytish
git reset --hard ORIG_HEAD""")

    para(d, "Reflog yozuvlari standart holda 90 kun saqlanadi "
            "(yetib bo'lmaydigan commit'lar uchun 30 kun). Shuning "
            "uchun Git'da \"hammasini yo'qotdim\" degan holat "
            "amalda juda kam uchraydi — faqat commit qilinmagan "
            "o'zgarishlar haqiqatan qaytarib bo'lmaydi.")

    sources(d, [
        ("git-log Documentation",
         "https://git-scm.com/docs/git-log"),
        ("git-checkout Documentation",
         "https://git-scm.com/docs/git-checkout"),
        ("git-restore Documentation",
         "https://git-scm.com/docs/git-restore"),
        ("git-reflog Documentation",
         "https://git-scm.com/docs/git-reflog"),
    ])
