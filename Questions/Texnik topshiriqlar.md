# Middle D — texnik topshiriqlar

Middle D mavzulari asosida tuzilgan amaliy topshiriqlar. Har biri intervyuda
yoki sinov vazifasi sifatida berilishi mumkin bo'lgan shaklda yozilgan.

Har bir topshiriqda:

- **Vaziyat** — muammo qanday ko'rinishda keladi.
- **Topshiriq** — nima qilish kerak.
- **Qabul mezonlari** — ish tugaganini qanday tekshiraman.
- **Tuzoqlar** — yechimni aytmaydi, lekin qaysi tomonga qarash kerakligini
  eslatadi. Avval o'zim yechib ko'rib, keyin shu ro'yxat bo'yicha o'zimni
  tekshiraman.

Yechim kodi bu faylda yo'q — ataylab. Maqsad o'qib tushunish emas, yechib
ko'rish.

**Bo'limlar:** [EF Core va ma'lumotlar bazasi](#1-ef-core-va-malumotlar-bazasi) ·
[API va ASP.NET](#2-api-va-aspnet) · [Auth va xavfsizlik](#3-auth-va-xavfsizlik) ·
[Realtime va integratsiya](#4-realtime-va-integratsiya) ·
[Testing](#5-testing) · [Infratuzilma va deployment](#6-infratuzilma-va-deployment) ·
[Kattaroq topshiriqlar](#7-kattaroq-topshiriqlar)

---

## 1. EF Core va ma'lumotlar bazasi

### T-01. Sekin ro'yxat endpoint'ini tezlashtirish

**Vaziyat.** Kutubxona tizimida `GET /api/loans` endpoint'i kitob ijaralari
ro'yxatini qaytaradi. Har bir yozuvda kitob nomi, muallifi, o'quvchining ismi va
kechikish kunlari bor. Ro'yxatda 2 000 ta yozuv bo'lganda javob 14 sekundda
keladi. Log'da bir xil `SELECT ... FROM books WHERE id = $1` so'rovi minglab
marta takrorlanadi.

**Topshiriq.** Endpoint'ni 300 ms dan kam vaqtda javob beradigan qilish. Javob
formati o'zgarmasligi kerak.

**Qabul mezonlari.**

- Bitta HTTP so'rov uchun ketadigan SQL so'rovlari soni — doimiy (ro'yxat
  hajmiga bog'liq emas).
- Javobda ortiqcha maydon yo'q, ya'ni bazadan faqat kerakli ustunlar o'qiladi.
- `EXPLAIN ANALYZE` natijasida to'liq jadval skanlash yo'q.
- Pagination bor va uning standart hajmi chegaralangan.

**Tuzoqlar.** Lazy loading yoqilganmi? `Include` bilan tuzatish eng yaxshi yo'lmi
yoki projeksiya arzonroqmi? "Kechikish kunlari" hisoblanadigan maydon — u SQL'ga
tarjima bo'ladimi yoki har bir satr uchun .NET'da hisoblanadimi? Bir nechta
kolleksiya `Include` qilinganda qancha satr qaytadi? Filtr va saralash uchun
indeks bormi — va composite indeksda ustun tartibi to'g'rimi?

### T-02. To'lov ierarxiyasini loyihalash

**Vaziyat.** To'lovlarning uch turi bor: karta orqali (karta maskasi, bank
nomi, avtorizatsiya kodi), naqd (kassir ID, kassa raqami) va bank o'tkazmasi
(hisob raqami, MFO, to'lov topshiriqnomasi raqami). Har bir turda o'ziga xos
maydonlar **majburiy**.

**Topshiriq.** Shu ierarxiyani EF Core'da map qilish. TPH, TPT va TPC dan
birini tanlab, tanlovni yozma asoslash. Migratsiya yaratish va yaratilgan SQL
sxemasini ko'rsatish.

**Qabul mezonlari.**

- Uch tur uchun ham majburiy maydonlar baza darajasida majburlanadi (ilova
  koddan tashqari ham buzilmaydi).
- `GET /api/payments` hamma turni bitta ro'yxatda qaytaradi va bu so'rov
  samarali.
- `GET /api/payments/card` faqat karta to'lovlarini oladi.
- Boshqa jadval (masalan `refunds`) to'lovga FK bilan bog'lanadi.
- Yangi to'lov turi qo'shilganda sxema o'zgarishi hajmi hisoblangan.

**Tuzoqlar.** TPH tanlasam, NOT NULL ni qanday majburlaydigan? TPC tanlasam,
ID lar uch jadvalda takrorlanib ketmaydimi? Oxirgi mezon (`refunds` dan FK) uch
strategiyadan qaysi birini imkonsiz qiladi? Polimorf so'rov har bir strategiyada
qanday SQL beradi?

### T-03. Buyurtma holatini bir vaqtda ikki foydalanuvchi o'zgartirmoqda

**Vaziyat.** Operatorlar paneli bor. Ikki operator bir vaqtda bitta buyurtmani
ochadi. Birinchisi "tasdiqlandi" qiladi, ikkinchisi "bekor qilindi" qiladi.
Natijada buyurtma "bekor qilindi" holatida qoladi, lekin ombordan tovar
ajratilgan — chunki birinchi operatorning o'zgarishi jimgina yo'qoldi.

**Topshiriq.** Yo'qolgan o'zgarish (lost update) muammosini yechish. Ikkinchi
operator xatoni ko'rishi va joriy holatni qayta yuklashi kerak.

**Qabul mezonlari.**

- Konflikt holatida API `409 Conflict` qaytaradi va javobda joriy holat bor.
- Konflikt integration test bilan takrorlanadi (ikki parallel so'rov).
- Yechim butun jadvalni qulflamaydi, ya'ni boshqa buyurtmalar bilan ishlash
  to'xtamaydi.
- Holat o'tishlari ruxsat etilgan sxema bo'yicha tekshiriladi ("bekor
  qilingan" dan "tasdiqlangan" ga o'tib bo'lmaydi).

**Tuzoqlar.** Optimistik yoki pessimistik? Postgres'da concurrency token uchun
nima ishlatiladi? Izolyatsiya darajasini ko'tarish yechimi — bu nimani buzadi va
ilova qanday xatoga tayyor bo'lishi kerak? `DbUpdateConcurrencyException` ni
ushlab, mijozga nima qaytaraman?

### T-04. Sekin hisobotni optimallashtirish

**Vaziyat.** Dashboard'da "oxirgi 30 kun bo'yicha kunlik savdo" grafigi bor.
U har ochilganda 6–9 sekund yuklanadi. So'rov 4 jadvalni `JOIN` qiladi va
8 mln satr bo'yicha agregatsiya qiladi. Ma'lumotning 15 daqiqa eskirishi
biznes uchun qabul qilinadi.

**Topshiriq.** Grafikni 1 sekunddan kam vaqtda yuklanadigan qilish.

**Qabul mezonlari.**

- O'lchov bor: oldin va keyin, `EXPLAIN (ANALYZE, BUFFERS)` natijasi bilan.
- Yangilanish jarayoni o'qishni bloklamaydi.
- Yangilanish avtomatik va jadval bo'yicha ishlaydi.
- Yangilanish ishlamay qolsa, buni biladigan mexanizm bor (eskirganlik vaqti
  ko'rinadi).

**Tuzoqlar.** Materialized view'ni `REFRESH` qilish o'qishni bloklaydimi — va
buni oldini olish uchun nima shart? Indeks qo'shish o'zi yetarli emasmi?
Keshlash (`IMemoryCache`) bu yerda mos keladimi — bir nechta instance bo'lsa
nima bo'ladi? Yangilashni cron'ga qo'ysam, vaqt zonasi va bir-birining ustiga
tushish muammosi bormi?

### T-05. 1NF buzilgan jadvalni normallashtirish

**Vaziyat.** Legacy jadval:

```sql
CREATE TABLE suppliers (
    id        bigserial PRIMARY KEY,
    name      text NOT NULL,
    phones    text,          -- "+998901112233, +998933334455"
    address   text,          -- "Toshkent sh., Chilonzor t., Bunyodkor 12"
    tags      text           -- "oziq-ovqat;import;vip"
);
```

Yangi talab: viloyat bo'yicha filtr, telefon raqam bo'yicha qidiruv va teg
bo'yicha hisobot kerak.

**Topshiriq.** Sxemani qayta loyihalash, migratsiya yozish va mavjud ma'lumotni
ko'chirish skriptini tayyorlash.

**Qabul mezonlari.**

- Yangi talablarning uchtasi ham indeks orqali bajariladi,
  `LIKE '%...%'` emas.
- Migratsiya qaytariladigan (`Down`) yoki qaytarib bo'lmasligi aniq yozilgan.
- Ko'chirishda buzilgan ma'lumot (bo'sh telefon, noto'g'ri format) qayerga
  ketishi aniqlangan — jimgina tashlab yuborilmaydi.
- Qaysi maydon **ataylab** bo'linmagan holda qoldirilgani va nega — yozilgan.

**Tuzoqlar.** Hamma narsani bo'laklash to'g'ri qarormi? Manzil bo'yicha faqat
viloyat kerak bo'lsa, uni to'liq komponentlarga ajratish nimaga olib keladi?
Telefon uchun unikal cheklov qanday bo'lishi kerak — bitta raqam ikki
yetkazib beruvchida bo'lishi mumkinmi? Ko'chirishni bitta tranzaksiyada
qilsam, 2 mln satrda nima bo'ladi?

### T-06. Yaqin filiallarni topish

**Vaziyat.** Mobil ilova foydalanuvchining koordinatasini yuboradi va 5 km
radiusdagi filiallarni, masofa bo'yicha saralangan holda so'raydi. Filiallar
soni — 1 200 ta, so'rovlar soni — sekundda 50 ta.

**Topshiriq.** `GET /api/branches/nearby?lat=41.2995&lon=69.2401&radius=5000`
endpoint'ini amalga oshirish. Masofa **metrda** qaytarilsin.

**Qabul mezonlari.**

- Masofa haqiqiy metrda (gradusda emas) va xatolik 1% dan kam.
- So'rov spatial indeksdan foydalanadi — `EXPLAIN` bilan tasdiqlangan.
- Noto'g'ri koordinata (`lat=200`) `400` beradi.
- Radius chegaralangan (cheksiz radius so'rab butun bazani tortib
  bo'lmaydi).

**Tuzoqlar.** `new Point(x, y)` da birinchi argument nima? SRID 4326 da
`Distance()` nimani qaytaradi? Ustun tipi `geometry` yoki `geography` bo'lishi
kerakmi va bu masofa hisobiga qanday ta'sir qiladi? Masofa bo'yicha
saralash indeksdan foydalanadimi?

### T-07. Audit trail qo'shish

**Vaziyat.** Auditorlar talabi: `contracts` jadvalidagi har bir o'zgarish
yozilishi kerak — kim, qachon, qaysi maydonni, qanday qiymatdan qanday qiymatga
o'zgartirgan.

**Topshiriq.** Audit mexanizmini amalga oshirish. Ilovaning mavjud kodiga
minimal aralashish bilan.

**Qabul mezonlari.**

- Audit yozuvi asosiy o'zgarish bilan **bir xil tranzaksiyada** saqlanadi —
  biri bo'lib ikkinchisi bo'lmasligi mumkin emas.
- Faqat haqiqatan o'zgargan maydonlar yoziladi.
- Foydalanuvchi ID'si audit yozuviga tushadi, background job'da ham mantiqiy
  qiymat bo'ladi.
- Parol hash'i va shunga o'xshash maxfiy maydonlar auditga **tushmaydi**.
- Bulk operatsiyada (`ExecuteUpdate`) nima bo'lishi hujjatlashtirilgan.

**Tuzoqlar.** EF Core interceptor'i yoki `SaveChanges` override'i yoki baza
trigger'i — qaysi biri? Trigger tanlasam, foydalanuvchi ID'sini qanday
yetkazaman? `ChangeTracker` dan qaysi ma'lumotni olaman va `SaveChanges` dan
**oldin** yoki **keyin** olish kerak? `ExecuteUpdate`/`ExecuteDelete`
change tracker'dan o'tadimi?

---

## 2. API va ASP.NET

### T-08. Xatolarni markazlashtirish

**Vaziyat.** Loyihada 40 ta controller bor va har birida `try/catch` bloklari.
Xato javoblari har xil formatda: ba'zi joyda `{ "error": "..." }`, ba'zi joyda
oddiy matn, ba'zi joyda to'liq stack trace. Production log'ida esa foydalanuvchi
bildirgan xatoni topish imkonsiz.

**Topshiriq.** Xatolarni markazlashgan tarzda boshqarishga o'tkazish.
`try/catch` bloklarini controller'lardan olib tashlash.

**Qabul mezonlari.**

- Hamma xato javobi bir xil formatda (ProblemDetails) va `traceId` bor.
- Domen xatolari to'g'ri status kodga map qilinadi: topilmadi → 404,
  validatsiya → 400 yoki 422, ruxsat yo'q → 403, konflikt → 409.
- Kutilmagan xatoda mijozga ichki ma'lumot (SQL, ulanish satri, stack trace)
  **chiqmaydi**, lekin log'da to'liq bor.
- Development va Production'da xatti-harakat farqi aniq va sinalgan.
- Xato javoblari OpenAPI hujjatida ko'rinadi.

**Tuzoqlar.** `IExceptionHandler` bir nechta bo'lsa tartib qanday? Handler
`false` qaytarsa nima bo'ladi? Validatsiya xatosi uchun 400 yoki 422 — farqi
nimada? `app.UseExceptionHandler()` ni middleware zanjirida qayerga qo'yish
kerak? Javob allaqachon boshlangan bo'lsa (response started) nima bo'ladi?

### T-09. API ni versiyalash

**Vaziyat.** Mavjud `GET /api/orders` javobida `customerName` maydoni bor.
Yangi talab: o'rniga `customer` obyekti (`id`, `name`, `phone`) bo'lishi kerak.
Mobil ilovaning eski versiyasi do'konlarda yangilanmagan va kamida 6 oy
ishlashi kerak.

**Topshiriq.** Ikki versiyani bir vaqtda qo'llab-quvvatlash.

**Qabul mezonlari.**

- Eski mijoz hech narsa o'zgartirmasdan ishlashda davom etadi.
- Yangi mijoz yangi formatni oladi.
- OpenAPI hujjatida ikki versiya alohida ko'rinadi.
- v1 "deprecated" deb belgilangan va javob header'ida o'chirilish sanasi bor.
- Biznes mantiqi ikki nusxada emas.

**Tuzoqlar.** Versiyalash usulini tanlash — URL, header, query? Controller'ni
ikki nusxa qilish kodni ikki barobar qiladi; buning o'rniga nimani ajratish
kerak? Versiya faqat DTO'ga tegsa, uni qaysi qatlamda hal qilaman? `Sunset`
header'i nima va u qanday yoziladi?

### T-10. Konfiguratsiyani tartibga solish

**Vaziyat.** Kodda 60 ta joyda `configuration["Smtp:Host"]` ko'rinishidagi satr
kalitlar bor. Bir joyda `"Smpt:Host"` deb xato yozilgan va bu production'da
`null` bo'lib, xat yuborish ikki hafta ishlamagan — hech kim sezmagan.

**Topshiriq.** Options pattern'ga o'tkazish va shunga o'xshash xatoni
takrorlanmaydigan qilish.

**Qabul mezonlari.**

- Konfiguratsiya tipik klasslar orqali olinadi, satr kalitlar yo'q.
- Noto'g'ri yoki yetishmagan konfiguratsiyada ilova **ko'tarilmaydi**, birinchi
  so'rovda emas.
- Validatsiya qoidalari bor (majburiy maydon, diapazon, format).
- Bir xil tipdan bir nechta konfiguratsiya kerak bo'lgan holat (ikki SMTP
  server) qanday qilinishi ko'rsatilgan.
- Maxfiy qiymatlar `appsettings.json` da emas.

**Tuzoqlar.** `IOptions`, `IOptionsSnapshot`, `IOptionsMonitor` — qaysi biri
kerak va nega? Background servisda `IOptionsSnapshot` ni ishlatsam nima bo'ladi?
Validatsiyani ishga tushishda majburlash uchun nima yozish kerak? Development
va Production'da maxfiy qiymat qayerdan keladi?

### T-11. Pagination'ni to'g'ri qilish

**Vaziyat.** `GET /api/events` endpoint'i hodisalar jurnalini qaytaradi,
jadvalda 40 mln satr. Hozir `?page=N&size=20` ishlaydi. Mijozlar shikoyati:
200-sahifadan keyin sekinlashadi, va ro'yxatni aylantirganda ba'zi yozuvlar
ikki marta, ba'zilari esa umuman ko'rinmaydi.

**Topshiriq.** Pagination'ni qayta loyihalash.

**Qabul mezonlari.**

- Ro'yxatning oxiriga yetish vaqti boshidan ko'p farq qilmaydi.
- Yangi yozuv qo'shilganda mavjud sahifalar siljib ketmaydi.
- `size` chegaralangan, standart qiymat bor.
- Mijoz uchun migratsiya yo'li bor — eski usul darhol o'chirilmaydi.
- Javobda keyingi sahifani olish uchun kerakli ma'lumot bor.

**Tuzoqlar.** `OFFSET 4000` baza tomonida nima qiladi? Barqaror saralash uchun
nechta ustun kerak va nega bitta `created_at` yetarli emas? Cursor'ni ochiq
ko'rinishda (`?after_id=123`) berish keyinchalik nimani qiyinlashtiradi? Umumiy
sonni (`total`) qanday qaytaraman — yoki umuman qaytarmaymanmi?

### T-12. OpenAPI hujjatini to'liq qilish

**Vaziyat.** Frontend jamoasi shikoyat qiladi: Swagger sahifasida hamma
endpoint `200 OK` qaytaradi deb yozilgan, xato formatlari ko'rinmaydi, enum
qiymatlari raqam bo'lib chiqadi, va `POST` so'rovlarining namunasi yo'q.

**Topshiriq.** OpenAPI hujjatini frontend jamoasi uchun yetarli darajaga
keltirish.

**Qabul mezonlari.**

- Har bir endpoint uchun mumkin bo'lgan status kodlar va ularning javob
  sxemalari hujjatda bor.
- Enum qiymatlari o'qiladigan ko'rinishda.
- So'rov va javob namunalari bor.
- Autentifikatsiya sxemasi hujjatda tasvirlangan va UI'dan token bilan sinash
  mumkin.
- Hujjat Production'da ochiq emas yoki himoyalangan.

**Tuzoqlar.** .NET 9+ da hujjat generatsiyasi nima bilan qilinadi va UI alohida
kerakmi? Status kodlarni har bir action'ga qo'lda yozish o'rniga umumiy
mexanizm bormi? `ProducesResponseType` ni yozmasdan 404 ni hujjatga qanday
tushiraman? Minimal API'da bu Controller'dan farq qiladimi?

---

## 3. Auth va xavfsizlik

### T-13. Parol bilan autentifikatsiyani amalga oshirish

**Vaziyat.** Yangi ichki tizim. Tashqi identity provider ishlatish imkoni yo'q
(talab shunday), shuning uchun parol bilan autentifikatsiya o'zimizda bo'ladi.

**Topshiriq.** Ro'yxatdan o'tish, kirish, parolni o'zgartirish va parolni
tiklash oqimlarini amalga oshirish.

**Qabul mezonlari.**

- Parol maxsus, sozlanadigan narxli funksiya bilan hashlanadi; algoritm va
  parametrlar keyinchalik o'zgartirilishi mumkin (hash satrida saqlanadi).
- Taqqoslash doimiy vaqtda.
- Kirish xatosi foydalanuvchi mavjudligini oshkor qilmaydi.
- Parolni tiklash tokeni bir martalik, muddatli va bazada hashlangan holda
  saqlanadi.
- Brute force'ga qarshi cheklov bor (IP va hisob bo'yicha).
- Parol o'zgarganda mavjud sessiyalar bilan nima bo'lishi aniqlangan.

**Tuzoqlar.** SHA-256 nega yaramaydi? Salt'ni o'zim boshqarishim kerakmi? Parol
tiklash havolasini email'ga yuborishda token URL'da bo'ladi — u qayerlarda
log'ga tushadi? Hisobni bloklash o'zi hujum vektoriga aylanishi mumkinmi?
Parol o'zgarganda JWT'ni qanday bekor qilaman?

### T-14. TOTP bilan ikki faktorli autentifikatsiya

**Vaziyat.** Yuqoridagi tizimga MFA qo'shish kerak. Foydalanuvchi Google
Authenticator yoki shunga o'xshash ilovadan foydalanadi.

**Topshiriq.** MFA ni yoqish, kirishda kod so'rash va recovery kodlari
oqimini amalga oshirish.

**Qabul mezonlari.**

- Yoqish jarayonida foydalanuvchi birinchi kodni kiritib tasdiqlaydi — ya'ni
  ilova sozlanganini tekshirmasdan MFA yoqilmaydi.
- Ishlatilgan kod qayta ishlatilmaydi.
- Vaqt siljishi hisobga olinadi, lekin oyna keragidan keng emas.
- Recovery kodlari bir martalik va hashlangan holda saqlanadi.
- TOTP secret'i bazada ochiq holda turmaydi.
- MFA kodini tekshirishga ham rate limiting bor.

**Tuzoqlar.** Secret'ni parol kabi hashlab bo'ladimi — nega yo'q, va unda qanday
saqlanadi? Kodni qayta ishlatishni to'sish uchun nimani eslab qolish kerak va
qancha vaqt? Oynani ±3 qilsam nima buziladi? Foydalanuvchi telefonini
yo'qotsa, uni kim va qanday tiklaydi — va bu jarayon MFA'ning o'zini
aylanib o'tish yo'liga aylanmaydimi?

### T-15. JWT autentifikatsiyasini tekshirish

**Vaziyat.** Loyihada JWT ishlatiladi. Code review'da shu konfiguratsiya
ko'rindi:

```csharp
options.TokenValidationParameters = new TokenValidationParameters
{
    ValidateIssuer   = false,
    ValidateAudience = false,
    IssuerSigningKey = new SymmetricSecurityKey(
        Encoding.UTF8.GetBytes("secret123"))
};
```

Token muddati 30 kun, refresh token yo'q, foydalanuvchi bloklanganda uning
tokeni ishlashda davom etadi.

**Topshiriq.** Konfiguratsiyadagi hamma muammoni topish, tuzatish va har bir
tuzatishning sababini yozish. Refresh token mexanizmini qo'shish.

**Qabul mezonlari.**

- Har bir o'chirilgan tekshiruv qayta yoqilgan va nega kerakligi tushuntirilgan.
- Imzo kaliti yetarli uzunlikda va konfiguratsiyadan keladi, koddan emas.
- Ruxsat etilgan algoritm aniq belgilangan.
- Access token qisqa muddatli, refresh token bekor qilinadigan.
- Foydalanuvchi bloklanganda uning kirishi qancha vaqtda to'xtashi aniq
  va bu muddat qabul qilinadigan.
- Refresh token o'g'irlangan holatni aniqlash mexanizmi bor.

**Tuzoqlar.** `ValidateAudience = false` nimaga olib keladi — boshqa tizim
tokeni bu yerda ishlatilishi mumkinmi? `"secret123"` HS256 uchun nega yomon?
`ValidAlgorithms` belgilanmasa qanday hujum bo'ladi? `ClockSkew` ning standart
qiymati nima? Refresh token rotation nima va u qanday o'g'irlikni aniqlaydi?

### T-16. IDOR zaifligini topish va yopish

**Vaziyat.** Tibbiy klinika tizimi. Pentest hisoboti: autentifikatsiya qilingan
har qanday foydalanuvchi `GET /api/visits/{id}` orqali **boshqa bemorning**
tashrif tarixini ko'ra oladi. Shunga o'xshash muammo `GET /api/documents/{id}`
va `DELETE /api/appointments/{id}` da ham bor.

**Topshiriq.** Zaiflikni yopish va kelajakda shunday xato takrorlanmasligi
uchun mexanizm taklif qilish.

**Qabul mezonlari.**

- Uchta endpoint ham to'g'rilangan.
- Boshqa odamning resursiga murojaat `403` yoki `404` beradi — tanlov
  asoslangan.
- Shifokor o'z bemorini ko'ra oladi, admin hammasini — ya'ni qoida rolga ham
  bog'liq.
- Har bir holat uchun integration test bor: egasi, begona, shifokor, admin.
- Shunga o'xshash endpoint'larni topishning tizimli yo'li taklif qilingan.

**Tuzoqlar.** Tekshiruvni har bir controller'da qo'lda yozish ishlaydi, lekin
41-chi endpoint'da yana esdan chiqadi — buni qanday majburlash mumkin?
Atribut (`[Authorize]`) bu muammoni yecha oladimi? Resource-based avtorizatsiya
ASP.NET Core'da qanday qilinadi? `403` qaytarsam, bu resurs mavjudligini oshkor
qiladi — bu muhimmi?

### T-17. Sirlarni repozitoriydan chiqarish

**Vaziyat.** Loyiha repozitoriysida `appsettings.Production.json` fayli bor va
unda baza paroli, SMTP paroli va to'lov provayderining API kaliti ochiq yozilgan.
Fayl 8 oy oldin commit qilingan.

**Topshiriq.** Vaziyatni to'g'rilash rejasi va uni amalga oshirish.

**Qabul mezonlari.**

- Repozitoriyda sir qolmagan.
- Fosh bo'lgan sirlar bilan nima qilinishi aniq (va to'g'ri) hal qilingan.
- Development va Production uchun sirlarni berish yo'llari hujjatlashtirilgan.
- CI/CD pipeline sirlarni log'ga chiqarmaydi.
- Kelajakda sir commit qilinishini to'sadigan avtomatik tekshiruv qo'shilgan.

**Tuzoqlar.** Faylni o'chirib commit qilish yetarlimi? Git tarixi nima bo'ladi
va uni qayta yozish jamoaga qanday ta'sir qiladi? Tarixni tozalash sirni
xavfsiz qiladimi — yoki baribir bitta majburiy qadam qoladi? Konteynerda
`ENV` orqali berish qanchalik xavfsiz?

### T-18. Dinamik saralashni xavfsiz qilish

**Vaziyat.** Hisobot endpoint'ida mijoz saralash ustunini o'zi beradi:

```csharp
var sql = $"SELECT * FROM invoices ORDER BY {sortBy} {direction}";
return await db.Invoices.FromSqlRaw(sql).ToListAsync();
```

**Topshiriq.** SQL injection zaifligini yopish, dinamik saralash imkoniyatini
saqlab qolgan holda. Zaiflikni ko'rsatadigan test yozish (avval qizil bo'lsin).

**Qabul mezonlari.**

- Hujum vektorini ko'rsatuvchi test bor va tuzatishdan keyin u o'tadi.
- Mijoz faqat ruxsat etilgan ustunlar bo'yicha saralay oladi.
- Ruxsat etilmagan qiymat jimgina standartga tushmaydi — mijoz xatoni biladi.
- Bir nechta ustun bo'yicha saralash qo'llab-quvvatlanadi.
- Yechimda satr birlashtirish yo'q, yoki bor bo'lsa — faqat allowlist'dan
  kelgan qiymat bilan.

**Tuzoqlar.** `ORDER BY` ni parametr bilan berib bo'ladimi? `FromSql` va
`FromSqlRaw` farqi bu yerda yordam beradimi? Ustun nomini `Regex` bilan
tekshirish yetarlimi — nega allowlist ishonchliroq? Yechimni LINQ bilan
(`IQueryable` ustida) qurish mumkinmi?

---

## 4. Realtime va integratsiya

### T-19. Realtime bildirishnoma

**Vaziyat.** Yetkazib berish tizimi. Operator paneli kuryer holatini real
vaqtda ko'rishi kerak: kuryer buyurtmani oldi, yo'lda, yetkazdi. Hozir panel
har 5 sekundda `GET /api/deliveries` ni chaqiradi va bu bazaga sezilarli yuk
beradi.

**Topshiriq.** SignalR bilan push bildirishnomaga o'tkazish. Ilova 3 instance'da
ishlaydi, oldida Nginx bor.

**Qabul mezonlari.**

- Operator faqat o'z filialidagi kuryerlar haqida xabar oladi.
- Ulanish uzilib qayta tiklanganda operator o'tkazib yuborgan holatni ko'radi
  (ya'ni faqat push'ga tayanmaydi).
- Uchta instance'dan qaysi birida ulangan bo'lishidan qat'i nazar xabar yetib
  boradi.
- Faqat autentifikatsiya qilingan foydalanuvchi ulanadi.
- WebSocket haqiqatan ishlatilayotgani tekshirilgan (long polling'ga
  tushmagan).

**Tuzoqlar.** Nginx konfiguratsiyasida WebSocket uchun nima bo'lishi shart?
3 instance bilan `Clients.All` nima qiladi? Guruhga qo'shishni qayerda qilaman
va ulanish uzilganda guruh a'zoligi saqlanadimi? Hub'da `DbContext` ishlatish
mumkinmi — hub'ning lifetime'i qanday? Token'ni WebSocket ulanishida qanday
yuboraman (header qo'yish mumkin emas)?

### T-20. Hodisani ishonchli yuborish (Outbox)

**Vaziyat.** Buyurtma yaratilganda ombor servisiga RabbitMQ orqali xabar
yuboriladi. Kod shunday:

```csharp
db.Orders.Add(order);
await db.SaveChangesAsync(ct);
await bus.PublishAsync(new OrderCreated(order.Id), ct);
```

Ishlab chiqarishda holat kuzatilgan: baza'da buyurtma bor, lekin ombor hech
narsa olmagan. Teskarisi ham bo'lgan — ombor ikki marta zaxira qilgan.

**Topshiriq.** Ikkita muammoni ham yechish.

**Qabul mezonlari.**

- Buyurtma saqlangan bo'lsa, xabar albatta yuboriladi (kechikish bilan bo'lsa
  ham).
- Buyurtma saqlanmagan bo'lsa, xabar yuborilmaydi.
- Xabar ikki marta kelsa, qabul qiluvchida natija bir xil bo'ladi.
- Yuborilmayotgan xabarlar ko'rinadi (monitoring yoki so'rov bilan).
- Qayta ishlanmagan xabar jimgina yo'qolmaydi.

**Tuzoqlar.** Tranzaksiyani RabbitMQ'ga ham tarqatish mumkinmi va nega bu yo'l
tanlanmaydi? Xabarni bazaga yozsam, uni kim va qachon o'qiydi — bu jarayon ikki
instance'da ishlasa nima bo'ladi? Qabul qiluvchi tomonda takrorlanishni qanday
aniqlayman va bu ma'lumotni qancha saqlashim kerak? DLX nima uchun kerak?

### T-21. Tashqi API bilan ishonchli integratsiya

**Vaziyat.** To'lov provayderining API'si bilan integratsiya. Provayder
beqarorligi kuzatiladi: ba'zan 3 sekund, ba'zan 40 sekund javob beradi, ba'zan
`502` qaytaradi. Hozirgi kod har so'rovda `new HttpClient()` yaratadi va
yuklama oshganda `SocketException` chiqa boshlaydi.

**Topshiriq.** Integratsiyani ishonchli qilish.

**Qabul mezonlari.**

- Socket oqishi yo'q va DNS o'zgarishi hisobga olinadi.
- Timeout aniq belgilangan va provayder osilganda mening so'rovlarim
  to'planmaydi.
- Vaqtinchalik xatolarda retry bor, lekin to'lov ikki marta o'tib ketmaydi.
- Provayder uzoq ishlamaganda tizim unga urishni to'xtatadi va tezda xato
  qaytaradi.
- Integratsiya testda tashqi API chaqirilmaydi.
- Xato holatlari log'da tahlil qilish uchun yetarli ma'lumot bilan qoladi.

**Tuzoqlar.** `IHttpClientFactory` nima muammoni yechadi va nimani yechmaydi?
`POST` ni retry qilish nimaga olib keladi va buni xavfsiz qiladigan narsa
nima? Circuit breaker holatlari qanday va uni qanday sinab ko'raman?
`EnsureSuccessStatusCode()` nega xato tahlilini qiyinlashtiradi? Testda
`HttpClient` ni mock qilaman yoki boshqa narsani?

### T-22. Fayl yuklashni backend'dan chiqarish

**Vaziyat.** Foydalanuvchilar skan qilingan hujjat yuklaydi, o'rtacha 8 MB,
ba'zan 60 MB. Hozir fayl API orqali o'tadi va MinIO'ga saqlanadi. Natija:
yuklash paytida ilova xotirasi o'sadi, so'rovlar timeout bo'ladi, va
`MaxRequestBodySize` chegarasiga urildi.

**Topshiriq.** Yuklashni to'g'ridan-to'g'ri MinIO'ga o'tkazish.

**Qabul mezonlari.**

- Fayl ilova jarayonidan o'tmaydi.
- Mijoz faqat o'ziga ruxsat berilgan joyga yuklay oladi.
- Obyekt nomini server belgilaydi.
- Havola qisqa muddatli.
- Yuklangandan keyin fayl tekshiriladi (hajm, tur) va faqat shundan keyin
  tizimda "tasdiqlangan" bo'ladi.
- Tashlab ketilgan (yuklanib, tasdiqlanmagan) fayllar avtomatik tozalanadi.

**Tuzoqlar.** Mijoz bergan fayl nomini ishlatsam nima bo'ladi? Presigned URL
berganimdan keyin mijoz nima yuklaganini qanday bilaman — va u 60 MB o'rniga
2 GB yuborsa? "Tasdiqlangan" holatni qanday modellashtiraman? Vaqtinchalik
fayllarni tozalashni cron bilan qilaman yoki saqlagichning o'zi qila oladimi?

---

## 5. Testing

### T-23. Sinab bo'lmaydigan servisni sinaladigan qilish

**Vaziyat.** Shu klassga test yozish kerak:

```csharp
public sealed class SubscriptionService
{
    public bool ShouldRenew(Subscription s)
    {
        if (s.ExpiresAt > DateTime.UtcNow.AddDays(3)) return false;
        if (!s.AutoRenew) return false;

        var rate = new HttpClient()
            .GetFromJsonAsync<Rate>("https://cbu.uz/rate/USD")
            .GetAwaiter().GetResult();

        Logger.Write($"renew check {s.Id} at {DateTime.Now}");
        return s.Balance * rate.Value >= s.Price;
    }
}
```

**Topshiriq.** Klassni refactor qilib, unit test bilan qoplash. Xatti-harakat
o'zgarmasligi kerak.

**Qabul mezonlari.**

- Testlar tarmoqqa chiqmaydi va tizim vaqtiga bog'liq emas.
- "Muddat tugashiga 3 kun qoldi" chegarasi ikki tomondan sinalgan (2 kun,
  3 kun, 4 kun).
- Testlar istalgan tartibda va parallel ishlaydi.
- Mock soni minimal — nima mock qilinmagani ham asoslangan.
- `GetAwaiter().GetResult()` olib tashlangan.

**Tuzoqlar.** Vaqtni qanday almashtiraman — o'z interfeysimni yozamanmi yoki
.NET'da tayyorisi bormi? `HttpClient` ni mock qilish o'rniga nimani
almashtirish to'g'riroq? Statik `Logger` bilan nima qilaman? `DateTime.Now`
va `DateTime.UtcNow` ikkisi ham bor — bu o'zi xato emasmi?

### T-24. Integration test infratuzilmasi

**Vaziyat.** Loyihada 200 ta unit test bor, lekin integration test yo'q.
Oxirgi uch incident'ning hammasi unit testlar topa olmaydigan turda bo'lgan:
migratsiya qo'llanmagan, avtorizatsiya policy'si noto'g'ri sozlangan, va
Postgres'da `ILIKE` kutilganidek ishlamagan.

**Topshiriq.** Integration test infratuzilmasini qurish va shu uch holatni
qoplaydigan testlar yozish.

**Qabul mezonlari.**

- Testlar haqiqiy Postgres bilan ishlaydi.
- Testlar bir-biridan mustaqil — har qanday tartibda o'tadi.
- Tashqi servislar (to'lov, email) mock'langan, baza mock'lanmagan.
- Autentifikatsiya qilingan va qilinmagan so'rovlar ikkisi ham sinaladi.
- Testlar CI'da ishlaydi.
- Butun to'plam qabul qilinadigan vaqtda tugaydi (maqsad belgilangan).

**Tuzoqlar.** In-memory provider yoki SQLite nega bu uch holatni topa
olmaydi? Har bir test oldidan migratsiya qilish — bu qanchalik sekin va
alternativasi nima? Testlar orasida ma'lumotni tozalashning eng tez yo'li?
DI'dan servisni almashtirish uchun `WebApplicationFactory` da qaysi
metod? CI'da Docker bormi va bo'lmasa nima qilaman?

---

## 6. Infratuzilma va deployment

### T-25. Docker image'ni kichraytirish va xavfsizlashtirish

**Vaziyat.** ASP.NET Core ilovasining image'i 1.2 GB. Build 11 daqiqa davom
etadi va har safar NuGet paketlarini qaytadan yuklaydi. `docker history` da
`appsettings.Development.json` va `.git` papkasi ko'rinadi.

**Topshiriq.** Image hajmini va build vaqtini kamaytirish, sir oqishini yopish.

**Qabul mezonlari.**

- Image hajmi sezilarli kichik (maqsad belgilangan va o'lchangan).
- Kod o'zgarganda NuGet restore qayta ishlamaydi.
- Image ichida va uning tarixida sir yoki keraksiz fayl yo'q.
- Konteyner root foydalanuvchi sifatida ishlamaydi.
- Health check bor.
- `.dockerignore` kontekst ildizida va to'liq.

**Tuzoqlar.** `COPY . .` dan oldin nimani ko'chirish kerak va nega? Multi-stage
build ishlatsam ham sir image tarixida qoladimi — qaysi holatda? Runtime image
sifatida nimani tanlayman (`runtime`, `aspnet`, `alpine`, chiseled) va har
birining narxi nima? Root bo'lmagan foydalanuvchi port 80'ga bog'lana oladimi?

### T-26. CI pipeline qurish

**Vaziyat.** Loyihada CI yo'q. Build mahalliy mashinada qilinadi, ba'zan
"menda ishlaydi" holati chiqadi. Test'lar qo'lda ishga tushiriladi, shuning
uchun ko'pincha umuman ishga tushirilmaydi.

**Topshiriq.** CI pipeline yozish (GitHub Actions yoki GitLab CI).

**Qabul mezonlari.**

- Har bir PR'da build va testlar ishlaydi.
- Integration testlar uchun kerakli servis (Postgres) ko'tariladi.
- Paket keshi ishlaydi va build vaqti qabul qilinadigan.
- Test natijalari ko'rinadi.
- Testlar o'tmasa merge bloklanadi.
- Pipeline'dagi mantiq minimal — asosiy ish skriptda, YAML'da emas.
- Action/image versiyalari qattiq belgilangan.

**Tuzoqlar.** `main` ga push va PR trigger'lari bir xil kerakmi? Fork'dan
kelgan PR'da sirlar beriladimi? Job'lar orasida fayl qanday o'tadi? Keshni
noto'g'ri kalit bilan qursam nima bo'ladi? Integration testlar uchun baza
ko'tarishni GitHub va GitLab'da qanday qilinadi va farqi nimada?

### T-27. Linux serverga deploy qilish

**Vaziyat.** Yangi Ubuntu server berildi. Unga ASP.NET Core API ni joylashtirish
kerak: Nginx orqasida, `systemd` servis sifatida, HTTPS bilan.

**Topshiriq.** Deploy jarayonini amalga oshirish va hujjatlashtirish.

**Qabul mezonlari.**

- Ilova alohida, huquqi cheklangan foydalanuvchi ostida ishlaydi.
- Server qayta ishga tushganda ilova avtomatik ko'tariladi.
- Nginx HTTPS'ni terminate qiladi, HTTP → HTTPS yo'naltiradi.
- Ilova haqiqiy mijoz IP'sini va `https` sxemasini ko'radi.
- WebSocket ishlaydi.
- Log'lar bir joyda va rotatsiya bor.
- Fayl va papka huquqlari minimal.
- Deploy qadamlari takrorlanadigan ko'rinishda yozilgan.

**Tuzoqlar.** Ilova qaysi portda tinglashi kerak va u tashqaridan ochiq
bo'lishi kerakmi? `X-Forwarded-*` header'larini ishlatish uchun ilovada nima
sozlanadi va uni middleware zanjirida qayerga qo'yaman? `KnownProxies` ni
to'ldirmasam qanday zaiflik paydo bo'ladi? Log papkasiga qanday huquq kerak —
`777` nega javob emas? Sertifikatni qanday yangilayman?

### T-28. Jadvalli ishlarni qo'yish

**Vaziyat.** Uch xil fon ishi kerak:

1. Har kuni 03:00 (Toshkent vaqti) — kunlik hisobot yasash va email yuborish.
2. Har 15 daqiqada — tashqi tizimdan kurs olib kelish.
3. Har oyning oxirgi kuni — oylik yopilish, 20–40 daqiqa davom etadi.

Ilova 2 instance'da ishlaydi.

**Topshiriq.** Uchta ishni sozlash.

**Qabul mezonlari.**

- Har bir ish belgilangan vaqtda **bir marta** ishlaydi, ikki instance'da
  ikki marta emas.
- Vaqt zonasi to'g'ri — kunlik hisobot mahalliy 03:00 da.
- Uzoq ish keyingi ishga tushishni bloklamaydi va nusxalar to'planmaydi.
- Ish xato bersa, bu ko'rinadi (jimgina o'tmaydi) va qayta urinish qoidasi bor.
- Deploy paytida yarim bajarilgan ish holati buzilmaydi.
- Oylik yopilish qayta ishga tushirilsa, natija ikki barobar bo'lmaydi.

**Tuzoqlar.** Cron ifodasida "oyning oxirgi kuni" standart sintaksisda bormi?
Hangfire standart qaysi vaqt zonasida ishlaydi? Ikki instance'ni qanday
muvofiqlashtiraman? 30 daqiqalik ishni cron ishga tushirsa, u nimada bajariladi
— to'g'ridan-to'g'ri cron handler'ida bo'lishi to'g'rimi? Idempotentlikni
qanday ta'minlayman?

### T-29. Windows serverda muhit tayyorlash

**Vaziyat.** Mijoz infratuzilmasi Windows'da. Yangi Windows Server 2022 ga API
ni IIS orqali joylashtirish kerak. Baza boshqa serverda, 5432 portda.

**Topshiriq.** Serverni tayyorlash va deploy qilish. Qadamlarni PowerShell
skripti sifatida yozish.

**Qabul mezonlari.**

- IIS va kerakli komponentlar skript orqali o'rnatiladi.
- ASP.NET Core ilovasi IIS ostida ishlaydi.
- Firewall faqat kerakli portlarni, faqat kerakli manbalardan ochadi.
- Ilova papkalariga huquqlar minimal, log papkasiga yozish bor.
- Baza serveriga ulanish tekshirilgan.
- Skript qayta ishga tushirilsa xato bermaydi (idempotent).

**Tuzoqlar.** `Install-WindowsFeature` ASP.NET Core uchun hamma kerakli
narsani o'rnatadimi — 502.5 xatosining eng ko'p uchraydigan sababi nima?
Application pool qaysi hisob ostida ishlaydi va unga huquq berish uchun hisob
nomi qanday yoziladi? Firewall qoidasini qaysi profil uchun yaratish kerak?
Port ochiqligini tekshirishning PowerShell'dagi usuli qanday?

---

## 7. Kattaroq topshiriqlar

Bular bir necha mavzuni birlashtiradi va sinov loyihasi sifatida beriladigan
hajmda.

### T-30. Hujjat aylanishi servisi

**Vaziyat.** Ichki hujjat aylanishi tizimi kerak: xodim hujjat yuklaydi,
rahbar tasdiqlaydi yoki rad etadi, hujjatning har bir holati tarixda qoladi.
Hujjatlar 5–50 MB, oyiga ~3 000 ta. 40 foydalanuvchi.

**Topshiriq.** Servisni loyihalash va amalga oshirish.

Qamrashi kerak bo'lgan mavzular: EF Core mapping va migratsiya; fayllarni
obyekt saqlagichda saqlash; rol va resursga asoslangan avtorizatsiya; holat
mashinasi; hodisa (tasdiqlandi/rad etildi) bo'yicha bildirishnoma; audit;
integration test; Docker va CI.

**Qabul mezonlari.**

- Hujjat fayli bazada emas, obyekt saqlagichda; yuklash va yuklab olish
  ilovadan o'tmaydi.
- Holat o'tishlari ruxsat etilgan sxema bo'yicha, noto'g'ri o'tish `409`.
- Xodim faqat o'z hujjatini, rahbar o'z bo'limini, admin hammasini ko'radi.
- Har bir holat o'zgarishi kim va qachon qilgani bilan saqlanadi.
- Bildirishnoma yuborilmasa, hujjat holati baribir to'g'ri (ikkisi bir-biriga
  bog'liq emas).
- OpenAPI hujjati to'liq, xatolar ProblemDetails formatida.
- Integration testlar asosiy oqimlarni va avtorizatsiya chegaralarini qoplaydi.
- `README` da ishga tushirish va arxitektura qarorlari yozilgan.

**Nima baholanadi.** Arxitektura qarorlarining asoslanishi; avtorizatsiya
mantiqining markazlashganligi; fayl va metadata orasidagi muvofiqlikni qanday
ta'minlaganim; nimani **qilmaganim** va nega (ortiqcha qatlam qo'shmaslik ham
qaror).

### T-31. Omborxona qoldig'ini hisoblash servisi

**Vaziyat.** Omborda tovar qoldig'i hisoblanadi. Kirim, chiqim, inventarizatsiya
va qaytarish operatsiyalari bor. Bir vaqtda 15 ta operator ishlaydi.
Qoldiq manfiy bo'lishi mumkin emas. Kunning har daqiqasida "hozirgi qoldiq"
so'rovi keladi — sekundda ~80 ta.

**Topshiriq.** Servisni loyihalash va amalga oshirish.

Qamrashi kerak bo'lgan mavzular: tranzaksiya va izolyatsiya; concurrency;
indekslash; keshlash; EF Core so'rovlarini optimallashtirish; integration test
(shu jumladan parallel yozish); PL/pgSQL yoki materialized view (kerak bo'lsa).

**Qabul mezonlari.**

- 15 ta parallel chiqim operatsiyasida qoldiq hech qachon manfiy bo'lmaydi —
  bu testda tasdiqlangan.
- "Hozirgi qoldiq" so'rovi 50 ms dan kam.
- Qoldiqni hisoblash usuli asoslangan: har safar hisoblash, saqlangan qoldiq,
  yoki ikkisining kombinatsiyasi.
- Inventarizatsiya (qoldiqni tashqi qiymatga tenglashtirish) tarixni
  buzmaydi.
- Yuklama testi natijasi bor.
- Konflikt va qayta urinish mantiqi aniq.

**Nima baholanadi.** Qoldiqni qanday modellashtirganim (hodisalar yig'indisi
yoki joriy qiymat) va bu tanlovning narxini tushunganim; qulflash
strategiyasi; o'lchov bilan ishlash — taxmin emas, raqam.

### T-32. Mavjud API ni audit qilish

**Vaziyat.** Ishlab turgan, 60 endpoint'li API berildi. Hujjat yo'q,
test yo'q, so'nggi 3 oyda 7 ta production incident bo'lgan.

**Topshiriq.** API ni audit qilib, ustuvorlashtirilgan muammolar ro'yxatini
va tuzatish rejasini tayyorlash. Keyin birinchi uchta muammoni tuzatish.

**Tekshirish kerak bo'lgan yo'nalishlar.**

- Avtorizatsiya: har bir endpoint himoyalanganmi, IDOR bormi.
- Ma'lumotlar bazasi: N+1, indeks yo'qligi, sekin so'rovlar, tranzaksiya
  chegaralari.
- Xatolarni boshqarish: format, ichki ma'lumot oqishi, log yetarliligi.
- Sirlar: repozitoriy, konfiguratsiya, log.
- Konfiguratsiya: Production'da Development sozlamalari, CORS, Swagger.
- Ishonchlilik: tashqi integratsiyalarda timeout, retry, socket boshqaruvi.
- Konkurentlik: lost update, idempotentlik.

**Qabul mezonlari.**

- Har bir topilma: nima, qanday takrorlanadi, qanday ta'sir, qanday tuzatiladi.
- Ustuvorlik ta'sir va ehtimollik bo'yicha asoslangan.
- Birinchi uchta tuzatish amalga oshirilgan va test bilan qoplangan.
- Tuzatishlar orqaga mos (buzuvchi o'zgarish bo'lsa — migratsiya rejasi bilan).

**Nima baholanadi.** Muhimni ahamiyatsizdan ajrata olish; "hammasini qayta
yozish kerak" demasdan, bor tizim ichida ishlay olish; topilmani boshqa odam
takrorlashi mumkin bo'ladigan darajada aniq yozish.

---

## O'zimni tekshirish uchun umumiy ro'yxat

Yechimni tugatganimdan keyin shu savollarni o'zimga beraman. Ular topshiriqdan
qat'i nazar ishlaydi.

**To'g'rilik.**

- Chegara holatlari: bo'sh ro'yxat, `null`, nol, manfiy, juda katta qiymat.
- Parallel bajarilish: ikki so'rov bir vaqtda kelsa nima bo'ladi?
- Xato o'rtada sodir bo'lsa, tizim qanday holatda qoladi?
- Operatsiya ikki marta bajarilsa, natija bir xilmi?

**Ishlash tezligi.**

- So'rov soni ma'lumot hajmiga bog'liq o'sadimi?
- Indeks ishlatilayotganini **o'lchadimmi**, yoki taxmin qildimmi?
- Chegaralanmagan ro'yxat qaytaradigan joy bormi?
- Xotirada butun to'plamni ushlab turadigan joy bormi?

**Xavfsizlik.**

- Bu resursga murojaat qilgan odam unga **haqiqatan** haqlimi (nafaqat
  autentifikatsiya, avtorizatsiya ham)?
- Foydalanuvchi kiritgan ma'lumot qayerda kod bo'lib bajarilishi mumkin?
- Xato xabari ichki ma'lumotni oshkor qilmaydimi?
- Log'ga maxfiy ma'lumot tushmaydimi?

**Kuzatuvchanlik.**

- Bu kod production'da ishlamay qolsa, sababini log'dan topa olamanmi?
- Foydalanuvchi "xato chiqdi" desa, aniq so'rovni topish yo'li bormi?
- Muhim biznes hodisasi log'da qoladimi?

**Soddalik.**

- Qo'shgan har bir qatlam, interfeys va abstraksiya nimadan himoya qiladi?
- Shu talabni kamroq kod bilan bajarish mumkin edimi?
- Bu kodni oradan 6 oy o'tib o'zim tushunamanmi?
