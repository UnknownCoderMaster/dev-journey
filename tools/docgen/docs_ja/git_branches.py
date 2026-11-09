# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "Git branches (create, delete, merge, based branch, switch branch)"
CATEGORY = "Git / Github / Gitlab"
TITLE = "Git Branchlar"
SUBTITLE = "Yaratish, almashtirish, birlashtirish va o'chirish"
FILENAME = "Git branches (create, delete, merge, based branch, switch branch).docx"


def build(d):
    h1(d, "1. Branch nima")

    para(d, "Git'da branch — commit'ga ishora qiluvchi **ko'chma "
            "ko'rsatkich**. U papka yoki nusxa emas, shunchaki 40 "
            "belgili commit hash'i yozilgan kichik fayl.")

    code(d, """$ cat .git/refs/heads/main
a677ee19f1c4b2d8e3f05a7b9c6d1e4f8a2b3c5d""")

    para(d, "Shuning uchun branch yaratish bir zumda bajariladi va "
            "hech qanday disk joyi talab qilmaydi. Bu Git'ning eng "
            "muhim amaliy xususiyatlaridan biri — branch yaratish "
            "arzon, shuning uchun undan erkin foydalanish mumkin.")

    para(d, "`HEAD` esa joriy branch'ga ishora qiladi:")

    code(d, """$ cat .git/HEAD
ref: refs/heads/feature/order-export""")

    # ───────────────────────────────────────────
    h1(d, "2. Yaratish va almashtirish")

    code(d, """# Yaratish va darhol o'tish (zamonaviy buyruq)
git switch -c feature/order-export

# Eski, lekin hali keng ishlatiladigan shakl
git checkout -b feature/order-export

# Faqat yaratish, o'tmasdan
git branch feature/order-export

# Mavjud branch'ga o'tish
git switch main
git switch -          # oldingi branch'ga qaytish""")

    para(d, "`switch` va `restore` buyruqlari Git 2.23 da `checkout` ni "
            "ikkiga bo'lish uchun qo'shilgan. `checkout` juda ko'p "
            "vazifani bajarardi — branch almashtirish, fayl tiklash, "
            "commit'ga o'tish — va bu chalkashlik keltirardi.")

    bullets(d, [
        "`git switch` — branch bilan ishlash.",
        "`git restore` — fayl mazmunini tiklash.",
        "`git checkout` — ikkisini ham qiladi, orqaga moslik uchun "
        "qolgan.",
    ])

    h2(d, "Boshqa branch asosida yaratish")

    code(d, """# develop asosida
git switch -c feature/new-report develop

# Masofaviy branch asosida
git switch -c hotfix/payment origin/release/2.4

# Aniq commit asosida
git switch -c fix/regression a677ee1

# Teg asosida
git switch -c hotfix/critical v2.3.1""")

    para(d, "Bu juda muhim detal: branch **qaysi nuqtadan** "
            "boshlanganini tanlash kerak. Agar `main` da turib "
            "`feature/x` yaratsam, u `main` dan boshlanadi; `develop` "
            "dan boshlashi kerak bo'lsa, buni aniq ko'rsatishim kerak. "
            "Noto'g'ri bazadan boshlash keyinchalik merge paytida "
            "keraksiz commit'lar olib kelishiga sabab bo'ladi.")

    # ───────────────────────────────────────────
    h1(d, "3. Ro'yxat va holat")

    code(d, """git branch                 # lokal branchlar
git branch -r              # masofaviy
git branch -a              # hammasi
git branch -vv             # oxirgi commit va upstream bilan

# Birlashtirilganlarni topish
git branch --merged main
git branch --no-merged main

# Oxirgi o'zgarish bo'yicha saralash — eski branchlarni topish uchun
git branch --sort=-committerdate -v""")

    para(d, "`git branch -vv` natijasida har bir branch yonida uning "
            "upstream'i va qancha commit oldinda yoki orqada ekani "
            "ko'rinadi. Men bu buyruqni eng ko'p ishlataman, chunki u "
            "bir qarashda holatni ko'rsatadi.")

    # ───────────────────────────────────────────
    h1(d, "4. Birlashtirish: merge va rebase")

    h2(d, "Merge")

    code(d, """git switch main
git pull
git merge feature/order-export""")

    para(d, "Merge ikki tarix chizig'ini birlashtiradi. Agar maqsad "
            "branch'da yangi commit bo'lmasa, Git **fast-forward** "
            "qiladi — shunchaki ko'rsatkichni surib qo'yadi, yangi "
            "commit yaratmaydi.")

    code(d, """# Har doim merge commit yaratish — tarix aniq ko'rinadi
git merge --no-ff feature/order-export

# Faqat fast-forward bo'lsa birlashtirish, aks holda to'xtash
git merge --ff-only feature/order-export""")

    para(d, "`--no-ff` ni afzal ko'raman: merge commit tarixda "
            "\"shu yerda bitta funksiya qo'shildi\" degan belgi "
            "qoldiradi va kerak bo'lsa butun funksiyani bitta "
            "`git revert -m 1` bilan qaytarish mumkin.")

    h2(d, "Rebase")

    code(d, """git switch feature/order-export
git rebase main""")

    para(d, "Rebase commit'larni yangi bazaga **qayta qo'yadi**. "
            "Natijada tarix chiziqli bo'ladi, merge commit yo'q.")

    para(d, "Lekin rebase commit'larni **qayta yozadi** — ularning "
            "hash'i o'zgaradi. Shuning uchun asosiy qoida:")

    note(d, "Rebase qoidasi",
         "Boshqalar bilan ulashilgan branch'ni **hech qachon** rebase "
         "qilmaslik. Agar branch push qilingan va kimdir uni olgan "
         "bo'lsa, rebase ularning tarixini buzadi. O'z lokal "
         "branch'ingizni esa erkin rebase qilish mumkin.")

    code(d, """# Majburan push qilish kerak bo'lsa — xavfsizroq variant
git push --force-with-lease""")

    para(d, "`--force-with-lease` masofaviy branch men oxirgi "
            "ko'rganimdan beri o'zgarmaganini tekshiradi. Oddiy "
            "`--force` esa boshqa odamning ishini jimgina o'chirib "
            "yuboradi.")

    h2(d, "Qaysi birini tanlayman")

    table(d, ["Holat", "Tanlov"],
          [["Feature branch'ni `main` ga qo'shish", "Merge (`--no-ff`) yoki squash"],
           ["`main` dagi yangi commit'larni feature'ga olish",
            "Rebase — tarix toza qoladi"],
           ["Branch ulashilgan", "Merge — rebase xavfli"],
           ["Ko'p mayda commit bor", "Squash merge"]],
          widths=[7.2, 7.3])

    # ───────────────────────────────────────────
    h1(d, "5. O'chirish")

    code(d, """# Lokal — faqat birlashtirilgan bo'lsa
git branch -d feature/order-export

# Lokal — majburan (birlashtirilmagan bo'lsa ham)
git branch -D feature/order-export

# Masofaviy
git push origin --delete feature/order-export

# Mahalliyda qolgan "o'lik" masofaviy havolalarni tozalash
git fetch --prune""")

    para(d, "Kichik harf `-d` himoya mexanizmi: branch "
            "birlashtirilmagan bo'lsa Git ogohlantiradi va "
            "o'chirmaydi. `-D` esa bu himoyani chetlab o'tadi. "
            "Shuning uchun odatda `-d` ni ishlataman va "
            "ogohlantirish chiqsa sababini tekshiraman.")

    h2(d, "Noto'g'ri o'chirilgan branch'ni tiklash")

    code(d, """# O'chirilgan branch commit'ini topish
git reflog

# Topilgan hash'dan qayta yaratish
git switch -c feature/order-export a677ee1""")

    para(d, "`reflog` — `HEAD` ning harakatlar tarixi. U commit'lar "
            "hali garbage collection bilan o'chirilmaganini ko'rsatadi "
            "(standart holda 90 kun). Shuning uchun Git'da "
            "\"yo'qotilgan\" ish deyarli har doim tiklanadi.")

    # ───────────────────────────────────────────
    h1(d, "6. Nomlash va amaliy odatlar")

    code(d, """feature/order-export
fix/null-reference-on-login
hotfix/payment-timeout
chore/update-dependencies
refactor/extract-price-calculator""")

    bullets(d, [
        "**Prefiks bilan turini ko'rsataman** — ro'yxat uzun bo'lganda "
        "bu juda yordam beradi.",
        "**Kichik harf va chiziqcha** — katta-kichik harfga sezgir "
        "bo'lmagan fayl tizimlarida muammo chiqmaydi.",
        "**Ticket raqamini qo'shish** foydali: `feature/PROJ-142-order-export`.",
        "**Branch'ni qisqa yashashini ta'minlash.** Uzoq yashagan "
        "branch'da merge konflikti muqarrar o'sadi. Bir-ikki kunda "
        "birlashtirishga harakat qilaman.",
        "**Har kuni `main` dan yangilanish olish** — konfliktni kichik "
        "bo'laklarda hal qilish osonroq.",
    ])

    sources(d, [
        ("git-branch Documentation",
         "https://git-scm.com/docs/git-branch"),
        ("git-switch Documentation",
         "https://git-scm.com/docs/git-switch"),
        ("git-merge Documentation",
         "https://git-scm.com/docs/git-merge"),
        ("Git Branching — Pro Git book",
         "https://git-scm.com/book/en/v2/Git-Branching-Branches-in-a-Nutshell"),
    ])
