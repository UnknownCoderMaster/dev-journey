# TLS Handshake — Real Hayotiy Misol Asosida Tushuntirish

TLS handshake'ni tushunishning eng yaxshi yo'li — buni **"begona odam bilan xavfsiz maxfiy suhbat boshlash"** jarayoniga o'xshatish.

## Voqea: Sen (Client) va Bank (Server)

Tasavvur qil — senga noma'lum shahardagi bank bilan **maxfiy xat yozishmoq** kerak, lekin pochta yo'lida hamma xatni o'qiy oladi (internet — ochiq kanal). Shu bilan birga, sen bu "bank" haqiqatan ham bank ekanligiga, firibgar emasligiga ishonch hosil qilishing kerak.

---

### 1-qadam: Salomlashish va "til kelishuvi" — `ClientHello`

Sen bankka xat yozasan:

> *"Salom, men siz bilan gaplashmoqchiman. Mana men biladigan maxfiy yozishma usullarim ro'yxati (AES, ChaCha20...). Va mana men o'ylab topgan tasodifiy raqam (random number) — buni keyin ishlatamiz."*

Bu — **`ClientHello`**: qaysi shifrlash algoritmlarini (cipher suites) qo'llab-quvvatlashing, TLS versiyasi va tasodifiy son (client random) yuboriladi.

### 2-qadam: Bank javob beradi va "shaxsini tasdiqlaydi" — `ServerHello` + `Certificate`

Bank javob yozadi:

> *"Yaxshi, biz AES-256 usulida gaplashamiz. Mana mening tasodifiy raqamim ham. Va — mana mening **pasportim** (SSL sertifikat) — bu meni "XYZ Bank" ekanligimni tasdiqlaydi, buni **elchixona** (Certificate Authority — masalan DigiCert) imzolagan."*

Sen bu "pasport"ni tekshirasan — imzo haqiqatan ham ishonchli elchixonaniki ekanligini, muddati o'tmaganini, va bank nomi to'g'ri ekanligini (domain match) tekshirasan. Bu — brauzeringda oldindan o'rnatilgan ishonchli CA ro'yxati orqali amalga oshadi.

Agar pasport soxta bo'lsa yoki muddati o'tgan bo'lsa — brauzer senga **"Bu sayt xavfli!"** deb qizil ekran ko'rsatadi.

### 3-qadam: Maxfiy "seyf kaliti"ni birgalikda yaratish — Key Exchange (ECDHE)

Endi eng qiziq qismi. Sen va bank — ikkovlaringiz ham hech kimga aytmasdan, faqat ochiq pochta orqali yozishib turib, **umumiy bir maxfiy kalitni** yaratishingiz kerak, garchi pochtachi (tajovuzkor) hamma xatni ko'rib tursa ham.

Bu xuddi shunga o'xshaydi:

- Sen o'zingda faqat senga ma'lum "maxfiy rang aralashmasi" bor (private key)
- Bank ham o'ziga xos "maxfiy rang aralashmasi" bor (private key)
- Ikkovlaring ham "ochiq ranglaringizni" (public key) bir-biringizga pochta orqali yuborasiz
- Har biringiz o'z maxfiy rangingizni qarshi tomonning ochiq rangi bilan aralashtirasiz
- Natijada — matematik jihatdan ikkovlaringizda ham bir xil yakuniy rang (shared secret) hosil bo'ladi, lekin pochtachi (kim eshitib tursa ham) faqat "ochiq ranglarni" ko'rgani uchun, yakuniy rangni hisoblab chiqara olmaydi

Bu — **Diffie-Hellman (ECDHE)** algoritmi, matematik jihatdan bir tomonlama funksiyalarga asoslangan (ochiq qismdan maxfiy qismni "orqaga qaytarib" hisoblash amaliy jihatdan imkonsiz).

### 4-qadam: "Endi tayyormiz" tasdiqlash — `Finished`

Ikkovlaring ham endi bir xil maxfiy kalitga egasiz. Buni tasdiqlash uchun bir-biringizga qisqa "test xat" yuborasiz — shifrlangan holda:

> *"Agar sen ham mening maxfiy kalitimni to'g'ri hisoblagan bo'lsang, bu xatni ocha olasan."*

Ikkalangiz ham muvaffaqiyatli ochsa — demak hamma narsa to'g'ri ishladi.

### 5-qadam: Endi haqiqiy maxfiy suhbat boshlanadi — Symmetric Encryption

Shu paytdan boshlab, siz endi sekin-og'ir "pasport tekshirish" yoki "rang aralashtirish" bilan shug'ullanmaysiz — **umumiy maxfiy kalit (session key)** orqali oddiy, tez shifrlash (AES) bilan gaplashaverasiz. Bu — brauzeringda ko'rgan HTTPS orqali yuklangan sahifa ma'lumotlari.

---

## Real TLS terminlariga moslashtirish

| Voqeadagi qadam | Haqiqiy TLS termini |
|---|---|
| "Salom, mana usullarim ro'yxati" | `ClientHello` (cipher suites, TLS version, client random) |
| "Mening pasportim, mana usul tanladim" | `ServerHello` + `Certificate` |
| Pasportni elchixona orqali tekshirish | Certificate Authority (CA) orqali tasdiqlash |
| "Rang aralashmasi" almashish | ECDHE (Elliptic Curve Diffie-Hellman) — key exchange |
| Yakuniy umumiy maxfiy rang | Session key (shared secret) |
| "Test xat" almashish | `Finished` message |
| Tezkor shifrlangan suhbat | Symmetric encryption (AES-GCM) orqali haqiqiy data almashish |

## Nega bu jarayon shu qadar murakkab?

Chunki ikkita muammoni bir vaqtning o'zida hal qilish kerak:

1. **Kim ekaningni tasdiqlash** (authentication) — pasport/sertifikat orqali
2. **Ochiq kanalda maxfiy kalit yaratish** (key exchange) — hech kim tinglab tursa ham, faqat ikkovlaring bilishi kerak bo'lgan kalit hosil qilish

Asymmetric shifrlash (RSA/ECDHE) — bu ikkalasini ham hal qiladi, lekin sekin ishlaydi, shuning uchun faqat "tanishuv" bosqichida ishlatiladi. Keyin tezroq symmetric shifrlashga (AES) o'tiladi, chunki endi ikkalangizda ham bir xil maxfiy kalit bor.
