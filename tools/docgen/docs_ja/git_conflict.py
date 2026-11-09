# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "Git conflict solve"
CATEGORY = "Git / Github / Gitlab"
TITLE = "Git Konfliktlarini Hal Qilish"
SUBTITLE = "Konflikt nima uchun chiqadi va qanday to'g'ri yechiladi"
FILENAME = "Git conflict solve.docx"


def build(d):
    h1(d, "1. Konflikt qachon chiqadi")

    para(d, "Git o'zgarishlarni avtomatik birlashtiradi, lekin bitta "
            "holatda buni qila olmaydi: ikki branch **bir xil faylning "
            "bir xil qatorlarini** turlicha o'zgartirgan bo'lsa.")

    para(d, "Shuni ta'kidlash kerak: turli joylardagi o'zgarish "
            "konflikt bermaydi. Bitta faylni ikki odam tahrirlagani "
            "o'zi muammo emas — muammo faqat kesishgan qatorlarda.")

    para(d, "Konflikt chiqadigan amallar: `merge`, `rebase`, "
            "`cherry-pick`, `stash pop`, `revert`.")

    # ───────────────────────────────────────────
    h1(d, "2. Konflikt belgilari")

    code(d, """$ git merge feature/discount
Auto-merging src/Services/PriceCalculator.cs
CONFLICT (content): Merge conflict in src/Services/PriceCalculator.cs
Automatic merge failed; fix conflicts and then commit the result.""")

    para(d, "Git konflikt joyini faylga belgilar bilan yozadi:")

    code(d, """public decimal Calculate(Order order)
{
<<<<<<< HEAD
    var total = order.Items.Sum(i => i.Quantity * i.UnitPrice);
    return total > 1_000_000m ? total * 0.95m : total;
=======
    var total = order.Items.Sum(i => i.Total);
    return _discountService.Apply(total, order.CustomerId);
>>>>>>> feature/discount
}""")

    bullets(d, [
        "`<<<<<<< HEAD` — joriy branch'dagi versiya (men turgan joy).",
        "`=======` — ajratuvchi.",
        "`>>>>>>> feature/discount` — kelgan versiya.",
    ])

    para(d, "Rebase paytida tomonlar **teskari** ko'rinadi, chunki "
            "rebase mening commit'larimni yangi baza ustiga qo'yadi. "
            "`HEAD` — baza branch, pastdagi esa mening o'zgarishim. "
            "Bu chalkashtiradigan detal, shuning uchun har safar "
            "e'tibor beraman.")

    # ───────────────────────────────────────────
    h1(d, "3. Holatni ko'rish")

    code(d, """git status

# Faqat konfliktli fayllar
git diff --name-only --diff-filter=U

# Uch tomonni birga ko'rish — eng foydali ko'rinish
git diff --merge

# Har bir tomonni alohida ko'rish
git show :1:src/Services/PriceCalculator.cs    # umumiy ajdod
git show :2:src/Services/PriceCalculator.cs    # HEAD (bizning)
git show :3:src/Services/PriceCalculator.cs    # kelgan (ularning)""")

    para(d, "Umumiy ajdodni (`:1`) ko'rish ko'pincha hal qiluvchi "
            "ma'lumot beradi: u ikki tomon **nimadan** boshlangani "
            "ko'rsatadi, shuning uchun har bir tomon nimani o'zgartirgani "
            "aniq bo'ladi.")

    code(d, """# Uch tomonli belgilar bilan ko'rsatish — ajdodni ham qo'shadi
git config merge.conflictStyle zdiff3""")

    para(d, "`zdiff3` uslubini yoqishni tavsiya qilaman: u konflikt "
            "blokiga umumiy ajdod versiyasini ham qo'shadi va bu "
            "qarorni ancha osonlashtiradi.")

    # ───────────────────────────────────────────
    h1(d, "4. Hal qilish")

    para(d, "Konfliktni hal qilish — belgilarni olib tashlab, "
            "**to'g'ri yakuniy kodni** yozish. Bu ko'pincha ikki "
            "versiyadan birini tanlash emas, balki ikkisini "
            "birlashtirish bo'ladi:")

    code(d, """public decimal Calculate(Order order)
{
    var total = order.Items.Sum(i => i.Total);                  // ularning refactor'i
    return _discountService.Apply(total, order.CustomerId);     // ularning yangi mantiqi
}""")

    code(d, """# Hal qilingandan keyin
git add src/Services/PriceCalculator.cs
git status                      # qolgan konfliktlar bormi?

# Merge'ni tugatish
git commit

# Rebase'ni davom ettirish
git rebase --continue""")

    h2(d, "Bir tomonni butunlay tanlash")

    code(d, """git checkout --ours  src/Config/appsettings.json     # HEAD versiyasi
git checkout --theirs src/Config/appsettings.json     # kelgan versiya
git add src/Config/appsettings.json""")

    para(d, "Bu generatsiya qilingan fayllar yoki lock fayllar uchun "
            "qulay. Lekin kod faylida ehtiyot bo'lish kerak: bir "
            "tomonni tanlash ikkinchi tomonning **butun faylidagi** "
            "o'zgarishni emas, faqat shu konflikt blokidagi "
            "o'zgarishni oladi — qolgan qismlar baribir birlashgan "
            "bo'ladi.")

    h2(d, "Bekor qilish")

    code(d, """git merge --abort
git rebase --abort
git cherry-pick --abort""")

    para(d, "Konflikt juda chalkash bo'lsa, bekor qilib boshqacha "
            "yondashish yaxshiroq. Masalan avval `main` ni feature'ga "
            "olib, konfliktni o'z branch'imda hal qilib, keyin merge "
            "qilaman — shunda `main` hech qachon buzilgan holatda "
            "bo'lmaydi.")

    # ───────────────────────────────────────────
    h1(d, "5. Hal qilgandan keyin majburiy qadam")

    para(d, "Bu eng ko'p e'tibordan chetda qoladigan qism. "
            "Konfliktni \"belgilar yo'q\" holatiga keltirish yetarli "
            "emas — natija **kompilyatsiya bo'lishi va testlardan "
            "o'tishi** kerak.")

    code(d, """dotnet build
dotnet test""")

    para(d, "Konflikt hal qilishda tipik xato: ikki tomon bir xil "
            "metodni turlicha o'zgartirgan, men ikkisini "
            "mexanik birlashtirdim va natijada mantiq buzildi — "
            "lekin sintaksis to'g'ri, shuning uchun hech narsa "
            "ogohlantirmaydi.")

    note(d, "Mening qoidam",
         "Konflikt hal qilganda faqat qatorlarni emas, **niyatni** "
         "tushunishga harakat qilaman: ikki tomon nima qilmoqchi "
         "edi? Tushunarsiz bo'lsa, o'zgarishni yozgan odamdan "
         "so'rayman — taxmin qilib birlashtirish xatoga olib keladi.")

    # ───────────────────────────────────────────
    h1(d, "6. Konfliktni kamaytirish")

    bullets(d, [
        "**Branch'ni qisqa yashashini ta'minlash.** Konflikt ehtimoli "
        "branch yoshi bilan o'sadi. Bir-ikki kunlik branch'da konflikt "
        "kam, ikki haftalikda muqarrar.",
        "**Har kuni `main` dan yangilanish olish** — kichik "
        "konfliktlarni bir nechta kichik bo'lakda hal qilish bitta "
        "katta konfliktdan ancha oson.",
        "**Formatlash qoidalarini kelishish.** `.editorconfig` va "
        "avtomatik formatlash bo'lmasa, konfliktlarning yarmi faqat "
        "bo'shliq va qator oxiri tufayli chiqadi.",
        "**Katta faylni bo'lish.** 2000 qatorli fayl konflikt "
        "magnitiga aylanadi.",
        "**Jamoada ishni bo'lish.** Ikki odam bir vaqtda bir xil "
        "faylni refactor qilmasligi kerak — buni oldindan "
        "muhokama qilish arzonroq.",
    ])

    h2(d, "rerere — bir xil konfliktni qayta yechmaslik")

    code(d, """git config --global rerere.enabled true""")

    para(d, "\"Reuse recorded resolution\" — Git hal qilgan "
            "konfliktlarimni eslab qoladi va bir xil konflikt yana "
            "chiqsa, uni avtomatik qo'llaydi. Uzoq yashaydigan "
            "branch'ni bir necha marta rebase qilganda juda ko'p "
            "vaqt tejaydi.")

    # ───────────────────────────────────────────
    h1(d, "7. Maxsus holatlar")

    h2(d, "Binary fayl konflikti")

    para(d, "Rasm yoki `.docx` kabi faylda Git birlashtira olmaydi — "
            "faqat bir tomonni tanlash mumkin:")

    code(d, """git checkout --theirs docs/architecture.png
git add docs/architecture.png""")

    h2(d, "O'chirish va o'zgartirish konflikti")

    code(d, """CONFLICT (modify/delete): src/Legacy/OldService.cs deleted in
feature/cleanup and modified in HEAD""")

    code(d, """# O'chirishni qabul qilish
git rm src/Legacy/OldService.cs

# Saqlab qolish
git add src/Legacy/OldService.cs""")

    para(d, "Bu holatda qaror texnik emas, mantiqiy: fayl haqiqatan "
            "kerak emasmi? Shuning uchun o'chirgan odamning niyatini "
            "bilish kerak bo'ladi.")

    sources(d, [
        ("Basic Merge Conflicts — Pro Git",
         "https://git-scm.com/book/en/v2/Git-Branching-Basic-Branching-and-Merging"),
        ("Advanced Merging — Pro Git",
         "https://git-scm.com/book/en/v2/Git-Tools-Advanced-Merging"),
        ("git-rerere Documentation",
         "https://git-scm.com/docs/git-rerere"),
        ("merge.conflictStyle configuration",
         "https://git-scm.com/docs/git-config#Documentation/git-config.txt-mergeconflictStyle"),
    ])
