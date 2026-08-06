# Git — Branches, Conflict, Log, Checkout — Junior A

## 1. Nima? (Ta'rif)

**Git** — kod tarixini boshqaruvchi **distributed version control**
tizimi. **Branch** — asosiy kod chizig'idan **mustaqil rivojlanadigan**
ish yo'nalishi.

## 2. Nima uchun kerak?

Bir nechta dasturchi **BIR VAQTDA**, **bir-biriga xalaqit
bermasdan** ishlashi kerak. Branch — har kim **o'z alohida
nusxasi**da ishlaydi, keyin **birlashtiradi** (merge). Git tarix
— **har o'zgarishni** kuzatib borish, kerak bo'lsa **qaytarish**
imkonini beradi.

## 3. Ichida nima sodir bo'ladi? (Mexanizm)

### 3.1 Branch — asosiy buyruqlar

```bash
git branch                    # Mavjud branch'lar RO'YXATI
git branch feature/employee-crud     # YANGI branch YARATISH (o'tmasdan)
git checkout -b feature/employee-crud # YARATISH + O'TISH (bitta buyruqda)
git switch feature/employee-crud      # O'TISH (zamonaviy, checkout'dan SODDAROQ)
git switch -c feature/new-feature     # YARATISH + O'TISH (zamonaviy usul)
git branch -d feature/employee-crud   # O'CHIRISH (agar MERGE qilingan bo'lsa)
git branch -D feature/employee-crud   # MAJBURIY o'chirish (merge qilinmagan bo'lsa ham)
```

### 3.2 `git merge` vs `git rebase`

```
git merge feature/xyz — feature branch'ni CURRENT branch'ga
                          BIRLASHTIRADI, YANGI "merge commit" YARATADI
                          Tarix — HAQIQIY (branching) ko'rinishini SAQLAYDI

git rebase main        — CURRENT branch'ning commit'larini, XUDDI
                          ULAR main'ning ENG SO'NGGI holatidan
                          KEYIN yaratilgandek, QAYTA "O'YNAYDI"
                          Tarix — CHIZIQLI (linear), "TOZA" ko'rinadi
```

```
merge:                          rebase:
main:    A---B---C---M          main:    A---B---C
              \     /                              \
feature:       D---E                    feature:    D'--E' (QAYTA yaratilgan!)

⚠️ Rebase — commit HASH'larini O'ZGARTIRADI! Agar branch ALLAQACHON
   BOSHQALAR bilan BO'LISHILGAN (masalan push qilingan) bo'lsa —
   rebase XAVFLI (boshqalarning tarixi bilan ZIDDIYAT keltirib
   chiqarishi mumkin) — FAQAT LOCAL, HALI PUSH QILINMAGAN
   commit'larda ishlatilishi TAVSIYA ETILADI.
```

### 3.3 Based branch

```bash
git checkout -b feature/payroll main # 'main'DAN YANGI branch YARATISH
```

### 3.4 Conflict — qanday yuzaga keladi

```
IKKI branch — BIR XIL FAYL, BIR XIL QATORNI, TURLICHA o'zgartirsa —
git AVTOMATIK "BIRLASHTIRA OLMAYDI" — CONFLICT yuz beradi.
```

```
Conflict markers:
<<<<<<< HEAD
    public decimal Salary { get; set; } = 5000000;
=======
    public decimal Salary { get; set; } = 6000000;
>>>>>>> feature/salary-update
```

**Hal qilish:**
```
1. Faylni EDITOR'da OCHISH, KERAKLI qismni SAQLAB QOLISH
2. Conflict marker'larni (<<<, ===, >>>) O'CHIRISH
3. git add <file>
4. git commit (yoki git merge --continue)
```

```bash
git mergetool # Visual diff tool (VS Code, Beyond Compare va h.k.) orqali
```

**Conflict oldini olish:** kichik, tez-tez PR'lar (uzoq muddat
alohida branch'da ishlash — conflict ehtimolini oshiradi).

### 3.5 `git log` — tarix ko'rish

```bash
git log                              # To'liq tarix
git log --oneline                     # Qisqa (bitta qator/commit)
git log --oneline --graph --all       # VIZUAL branch daraxti
git log --author="Orzibek"            # MUALLIF bo'yicha FILTR
git log --since="2 weeks ago"          # VAQT bo'yicha
git log --grep="fix"                   # COMMIT XABARIDA qidirish
```

### 3.6 `git checkout` — branch, commit, file

```bash
git checkout feature/xyz          # Branch'ga O'TISH
git checkout a1b2c3d               # ANIQ commit'ga O'TISH ("detached HEAD" holati!)
git checkout -- file.txt           # Fayldagi SAQLANMAGAN o'zgarishlarni BEKOR QILISH
```

```
Detached HEAD — commit'ga TO'G'RIDAN o'tilganda (branch'ga EMAS),
Git "HOZIRGI holatingiz HECH QANDAY BRANCH'GA tegishli EMAS" deb
OGOHLANTIRADI. Agar bu YERDA YANGI commit qilinsa — u HECH QANDAY
branch orqali "ESLAB QOLINMAYDI" (branch YARATILMASA — YO'QOLISHI
mumkin).
```

### 3.7 `git stash` — vaqtincha saqlash

```bash
git stash                    # HOZIRGI o'zgarishlarni VAQTINCHA "OLIB QO'YISH"
git stash list                # Saqlangan stash'lar RO'YXATI
git stash pop                 # Oxirgi stash'ni QAYTARISH (va RO'YXATDAN o'chirish)
git stash apply                # QAYTARISH (lekin RO'YXATDA QOLDIRISH)
```

Foydali holat: boshqa branch'ga **tezkor** o'tish kerak (masalan,
production bug), lekin hozirgi ish **hali tugallanmagan**.

### 3.8 `git cherry-pick` — bitta commit olish

```bash
git cherry-pick a1b2c3d # BOSHQA branch'dan, FAQAT BITTA commit'ni JORIY branch'ga QO'SHISH
```

### 3.9 `git reset` vs `git revert`

```
git reset --hard a1b2c3d  — HISTORY'ni O'ZGARTIRADI (commit'lar
                              YO'QOLADI), FAQAT LOCAL, PUSH
                              qilinmagan holatda XAVFSIZ

git revert a1b2c3d         — YANGI commit YARATADI, ESKI commit'ni
                              "TESKARI QILADI" — TARIX SAQLANADI,
                              PUSH qilingan (shared) branch'larda
                              XAVFSIZ
```

```
⚠️ git reset --hard — PUSH qilingan (boshqalar bilan BO'LISHILGAN)
   branch'da ISHLATILMASIN! Bu — boshqalarning tarixi bilan
   ZIDDIYAT keltirib chiqaradi.

✅ git revert — SHARED branch'larda XAVFSIZ (chunki YANGI commit
   qo'shadi, ESKINI O'CHIRMAYDI).
```

### 3.10 Pull Request / Merge Request — code review jarayoni

```
1. Feature branch YARATILADI
2. O'zgarish qilinadi, COMMIT/PUSH qilinadi
3. PR/MR OCHILADI — main branch'ga BIRLASHTIRISH SO'RALADI
4. Jamoadosh CODE REVIEW qiladi (comment, o'zgartirish so'raydi)
5. CI/CD — AVTOMATIK test/build ISHGA TUSHADI
6. TASDIQLANGANDAN so'ng — MERGE qilinadi
```

### 3.11 Gitflow vs Trunk-based

```
Gitflow — main, develop, feature/*, release/*, hotfix/* — KO'P
           branch turi, MURAKKAB, KATTA, sekin-release loyihalarda

Trunk-based — HAMMA to'g'ridan main'ga (yoki QISQA feature branch)
               commit qiladi, TEZ-TEZ deploy, CI/CD'ga MOS
```

## 4. Kod — real workflow misoli

```bash
git switch -c feature/employee-bonus main
# ... o'zgartirishlar
git add .
git commit -m "Add employee bonus calculation"
git push origin feature/employee-bonus
# GitHub'da PR OCHILADI, review'dan O'TADI, MERGE qilinadi
git switch main
git pull origin main
git branch -d feature/employee-bonus
```

## 5. Qachon ishlatish kerak?

| Vaziyat | Yechim |
|---|---|
| Yangi funksionallik ustida ishlash | Feature branch |
| Lokal, hali push qilinmagan commit'larni tozalash | `rebase` |
| Shared branch tarixini o'zgartirmasdan bekor qilish | `revert` |
| Vaqtincha ishni "yon qo'yish" | `stash` |
| Bitta commit'ni boshqa branch'ga olish | `cherry-pick` |

## 6. Muhim nuqtalar

- `git reset --hard` — **push qilinmagan** commit'larda xavfsiz,
  **push qilingan** (shared) tarixda **XAVFLI**.
- Rebase — tarixni "tozalaydi", lekin **shared branch**larda
  ishlatilmasligi kerak.
- Kichik, tez-tez PR — conflict ehtimolini **sezilarli**
  kamaytiradi.

## 7. Imtihon savollari

1. `git merge` va `git rebase` orasidagi farq nima?
2. Conflict qanday yuzaga keladi va uni qanday hal qilish kerak?
3. `git reset --hard` va `git revert` orasidagi farq nima, va
   qaysi biri shared branch'da xavfsiz?
4. Detached HEAD holati nima?
5. `git stash` qanday amaliy vaziyatda foydali?
6. Gitflow va Trunk-based workflow orasidagi farq nima?
7. `git cherry-pick` qachon ishlatiladi?
