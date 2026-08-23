# Backup/Restore (UI orqali) — Junior B

## 1. What (Nima?)

**Backup (zaxira nusxa)** — DB'NING JORIY HOLATINI, **KELAJAKDA
QAYTA TIKLASH IMKONIYATI BILAN**, FAYLGA (yoki BOSHQA JOYGA)
SAQLASH JARAYONI. **Restore (qayta tiklash)** — SAQLANGAN
BACKUP FAYLIDAN, DB'NI **O'SHA VAQTDAGI HOLATIGA QAYTARISH**
JARAYONI. UI (masalan **pgAdmin**) ORQALI — BU JARAYONLARNI,
KOMANDA QATORI (`pg_dump`/`pg_restore`) BILISHNI TALAB
QILMASDAN, **GRAFIK INTERFEYS ORQALI** AMALGA OSHIRISH MUMKIN.

## 2. Real hayot analogiyasi

**Backup — MUHIM HUJJATLARNI FOTONUSXA OLIB, SEYFDA
SAQLASH.** Agar ASL HUJJAT (DB) YO'QOLSA, YONIB KETSA, YOKI
BUZILSA (data corruption, tasodifiy DELETE) — SIZDA FOTONUSXA
(backup) BOR, VA SIZ YO'QOTILGAN MA'LUMOTNI **QAYTA TIKLASHINGIZ
(restore)** MUMKIN. **Backup'ni QANCHALIK TEZ-TEZ OLISH** —
"QANCHA VAQT OLDINGI HOLATGA QAYTA OLASIZ" DEGAN SAVOLGA
JAVOB BERADI — AGAR HAR KUNI FOTONUSXA OLSANGIZ, ENG YOMON
HOLATDA — FAQAT 1 KUNLIK MA'LUMOTNI YO'QOTASIZ.

## 3. Why (Nega kerak?)

PRODUCTION DB'DA, **INSON XATOSI** (tasodifiy `DELETE FROM
users` WHERE'siz), **DASTUR XATOSI** (bug tufayli noto'g'ri
UPDATE), YOKI **APPARAT MUAMMOSI** (disk buzilishi) — HAR
QANDAY VAQTDA YUZ BERISHI MUMKIN. Backup — BUNDAY HOLATLARDA,
**BIZNESNI TO'XTATIB QO'YMASLIK** (DISASTER RECOVERY) UCHUN
YAGONA ISHONCHLI HIMOYA. pgAdmin KABI UI VOSITALARI — BACKUP/
RESTORE JARAYONINI, **KOMANDA QATORI SINTAKSISINI ESLAB
QOLISH SHART BO'LMAGAN HOLDA**, VIZUAL, XATOGA KAMROQ MOYIL
QILADI.

## 4. Internals (Ichki mexanizm)

### pgAdmin UI — ICHKARIDA `pg_dump`/`pg_restore` ISHLATADI

```
pgAdmin'ning "Backup..." VA "Restore..." MENYULARI —
ICHKARIDA, HAQIQATDA, POSTGRESQL'NING STANDART KOMANDA
QATORI VOSITALARINI (`pg_dump`, `pg_restore`, `psql`) —
FONDA (background) ISHGA TUSHIRADI. UI — FAQAT, BU
VOSITALARGA KERAKLI PARAMETRLARNI (format, jadval nomlari,
compression) VIZUAL SHAKLDA TANLASH VA JARAYON NATIJASINI
(progress bar, log) KO'RSATISH VOSITASI.
```

### Backup FORMATLARI — Plain, Custom, Directory, Tar

```
Plain (.sql)     — ODDIY, INSON O'QIY OLADIGAN SQL SKRIPT
                    (CREATE TABLE, INSERT SO'ROVLARI). Katta
                    DB'LARDA — SEKIN VA KATTA HAJMLI.

Custom (.backup) — PostgreSQL'ning O'ZIGA XOS, SIQILGAN
                    (compressed) BINARY FORMAT — SELEKTIV
                    RESTORE (masalan FAQAT MA'LUM JADVALLARNI
                    TIKLASH) IMKONINI BERADI, ODATDA TAVSIYA
                    ETILADIGAN FORMAT.

Directory        — HAR JADVAL, ALOHIDA FAYL SIFATIDA
                    SAQLANADI — PARALLEL BACKUP/RESTORE
                    (bir nechta jarayon bir vaqtda ishlashi)
                    IMKONINI BERADI — ENG TEZKOR KATTA DB'LAR
                    UCHUN.

Tar              — Directory formatiga O'XSHASH, LEKIN BITTA
                    TAR ARXIVIGA "O'RALGAN".
```

### Restore — Transaction ICHIDA BAJARILISHI (Consistency)

```
RESTORE JARAYONI — ODATDA, YAGONA KATTA TRANSACTION ICHIDA
BAJARILADI (yoki, Custom formatda, jadval-jadval BO'LIB, LEKIN
BUTUN JARAYON — "HAMMASI YOKI HECH NARSA" MANTIG'IGA EGA
BO'LISHI TAVSIYA ETILADI). Agar RESTORE JARAYONI YARIM YO'LDA
TO'XTAB QOLSA (masalan XATOLIK TUFAYLI) — DB, "YARIM TIKLANGAN,
NOTO'G'RI" HOLATDA QOLISHI MUMKIN — SHUNING UCHUN, RESTORE'DAN
OLDIN, ODATDA, ALOHIDA, BO'SH DB YARATIB, UNGA TIKLASH TAVSIYA
ETILADI (mavjud, ishlab turgan DB'ga to'g'ridan-to'g'ri emas).
```

## 5. Code (Amaliy kod)

```
pgAdmin orqali Backup olish — qadamlar:

1. Server daraxtida, kerakli DATABASE ustiga O'NG TUGMA bosing
2. "Backup..." ni tanlang
3. "Filename" — backup fayli saqlanadigan joyni tanlang (.backup)
4. "Format" — "Custom" ni tanlang (tavsiya etiladi — selektiv
   restore imkoniyati bilan)
5. "Dump Options" tabida — kerak bo'lsa, faqat ma'lum
   sxema/jadvallarni tanlash mumkin
6. "Backup" tugmasini bosing — progress bar ko'rinadi

pgAdmin orqali Restore qilish — qadamlar:

1. Server daraxtida, YANGI (bo'sh) DATABASE yarating
   (mavjud DB'ga to'g'ridan-to'g'ri restore qilish — xavfli!)
2. Yangi DATABASE ustiga o'ng tugma bosing → "Restore..."
3. "Filename" — oldin saqlangan .backup faylni tanlang
4. "Restore Options" tabida, kerak bo'lsa, faqat ma'lum
   jadvallarni tanlash mumkin
5. "Restore" tugmasini bosing
```

```bash
# pgAdmin UI'ning "orqasida" haqiqatda bajariladigan komandalar (solishtirish uchun)
pg_dump -h localhost -U postgres -d mydb -F c -f mydb_backup.backup
pg_restore -h localhost -U postgres -d mydb_new -F c mydb_backup.backup
```

```csharp
// C# tomonidan — production'da avtomatik backup, ODATDA cron job / hosting
// provider (Azure, AWS RDS) darajasida sozlanadi, ILOVA KODIDA emas.
// Lekin, dasturchi, "restore qilingan DB'ga ulanish" testini yozishi mumkin:
public class DatabaseHealthCheck
{
    public async Task<bool> CanConnectAsync(AppDbContext dbContext)
        => await dbContext.Database.CanConnectAsync();
}
```

## 6. Keng tarqalgan xatolar / noto'g'ri tushunchalar

```
❌ "Backup — FAQAT KATTA, ENTERPRISE LOYIHALAR UCHUN KERAK,
   KICHIK LOYIHADA SHART EMAS" — YO'Q! HATTO KICHIK LOYIHADA
   HAM, INSON XATOSI (masalan tasodifiy DELETE) — MA'LUMOT
   YO'QOTILISHIGA OLIB KELISHI MUMKIN — REGULAR BACKUP, LOYIHA
   HAJMIDAN QAT'I NAZAR, ZARUR.

❌ "Restore'ni, MAVJUD, ISHLAB TURGAN DB'GA TO'G'RIDAN-TO'G'RI
   QILISH — XAVFSIZ" — XAVFLI! Agar RESTORE JARAYONI YARIM
   YO'LDA TO'XTAB QOLSA, YOKI XATO BACKUP FAYL TANLANSA — 
   MAVJUD, ISHLAYOTGAN MA'LUMOTLAR BUZILISHI/YO'QOLISHI
   MUMKIN. ODATDA, YANGI, BO'SH DB'GA RESTORE QILIB, KEYIN
   TEKSHIRIB, SO'NG "ALMASHTIRISH" TAVSIYA ETILADI.

❌ "Plain (.sql) format — HAR DOIM ENG YAXSHI TANLOV (o'qish
   oson bo'lgani uchun)" — KATTA DB'LARDA, Plain format —
   SEKIN VA KATTA HAJMLI BO'LADI, SELEKTIV RESTORE IMKONIYATI
   YO'Q — Custom format, ODATDA, KO'PROQ TAVSIYA ETILADI.

❌ "Backup olingandan keyin, uni RESTORE QILIB KO'RISH SHART
   EMAS (backup — o'zi kifoya)" — XAVFLI! Backup fayl,
   BUZILGAN yoki NOTO'G'RI bo'lishi mumkin — MUNTAZAM
   RAVISHDA, BACKUP'NI TEST MUHITIDA RESTORE QILIB KO'RISH —
   UNING HAQIQATDA ISHLASHINI KAFOLATLASH UCHUN ZARUR.
```

## 7. Exam (Interview savollari)

**1. pgAdmin'dagi "Backup..." va "Restore..." UI FUNKSIYALARI,
ICHKARIDA QAYSI KOMANDA QATORI VOSITALARIGA ASOSLANGAN?**
`pg_dump` (backup uchun) va `pg_restore`/`psql` (restore
uchun) — pgAdmin, BU VOSITALARNI FONDA ISHGA TUSHIRIB,
NATIJANI VIZUAL INTERFEYS ORQALI KO'RSATADI.

**2. Custom (.backup) format, Plain (.sql) formatdan QANDAY
AFZALLIKKA EGA?**
Custom format — SIQILGAN (compressed), KICHIKROQ HAJMGA EGA,
VA SELEKTIV RESTORE (masalan FAQAT MA'LUM JADVALLARNI
TIKLASH) IMKONINI BERADI. Plain format — ODDIY SQL SKRIPT,
KATTA DB'LARDA SEKIN VA HAJMDOR, SELEKTIV RESTORE IMKONI
YO'Q.

**3. Nima uchun Restore JARAYONINI, MAVJUD, ISHLAB TURGAN
DB'GA TO'G'RIDAN-TO'G'RI EMAS, BALKI YANGI, BO'SH DB'GA
BAJARISH TAVSIYA ETILADI?**
Chunki, AGAR RESTORE JARAYONI XATOLIK TUFAYLI YARIM YO'LDA
TO'XTAB QOLSA, YOKI NOTO'G'RI BACKUP FAYL ISHLATILSA —
MAVJUD, ISHLAYOTGAN MA'LUMOTLAR BUZILISHI/YO'QOLISHI MUMKIN.
Yangi DB'ga restore qilib, TEKSHIRIB, SO'NG ALMASHTIRISH —
XAVFSIZROQ.

**4. Backup'ni MUNTAZAM RAVISHDA TEST MUHITIDA RESTORE QILIB
KO'RISH NIMA UCHUN MUHIM?**
Chunki BACKUP FAYL O'ZI, BUZILGAN, TO'LIQSIZ, YOKI NOTO'G'RI
SOZLANGAN BO'LISHI MUMKIN — FAQAT AMALIY RESTORE SINOVI,
BACKUP'NING HAQIQATDA ISHLASHINI (kelajakda kerak bo'lganda
ma'lumotni tiklay olishini) KAFOLATLAYDI.

**5. Backup FORMATLARI ORASIDA "Directory" FORMAT, QAYSI
STSENARIYDA (masalan JUDA KATTA DB'LARDA) TAVSIYA ETILADI,
VA NIMA UCHUN?**
Directory format — HAR JADVALNI ALOHIDA FAYL SIFATIDA
SAQLAYDI, VA PARALLEL (bir nechta jarayon bir vaqtda)
BACKUP/RESTORE IMKONINI BERADI — bu, JUDA KATTA DB'LARDA
(masalan yuzlab GB), BACKUP/RESTORE VAQTINI SEZILARLI
QISQARTIRADI.
