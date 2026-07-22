# SSH, SCP, curl, telnet, traceroute — Junior C

## 1. Nima?

**SSH (Secure Shell)** — masofadagi kompyuterga **shifrlangan**
tarmoq orqali xavfsiz ulanish va buyruq bajarish protokoli (port 22).
**curl** — HTTP(S) va boshqa protokollar bo'yicha so'rov yuboruvchi
komandanoq vositasi. **telnet** — oddiy (shifrlanmagan) TCP ulanish
o'rnatuvchi eski protokol, hozir asosan **port tekshirish** uchun
ishlatiladi.

## 2. Nima uchun kerak?

Serverga masofadan turib kirish, deploy qilish, log ko'rish, fayl
ko'chirish — bularning barchasi SSH orqali amalga oshiriladi. Agar
SSH bo'lmaganida — parolni ochiq matn bilan yuborish (Telnet kabi)
kerak bo'lardi — bu tarmoqda **kimdir tinglayotgan bo'lsa** darhol
kompromatatsiyaga olib keladi.

`curl` — API'ni Postman/brauzersiz, terminal orqali, CI/CD
skriptlarida, yoki serverga SSH orqali kirib turib tezkor test qilish
uchun zarur.

`telnet`/`traceroute` — tarmoq muammolarini diagnostika qilish uchun
(masalan, "nega DB'ga ulanolmayapman — port yopiqmi, yo'l uzilganmi?").

## 3. Ichida nima sodir bo'ladi? (Mexanizm)

### 3.1 SSH — qanday ishlaydi

```
1. TCP ulanish (port 22) o'rnatiladi
2. Server o'z "host key" (public key) ini yuboradi
   → Client birinchi marta ulanganda "bu key ishonchlimi?" deb so'raydi
   → known_hosts faylida saqlanadi (keyingi safar solishtirish uchun)
3. Key Exchange — simmetrik session key (Diffie-Hellman orqali) o'rnatiladi
4. Autentifikatsiya:
   a) Parol orqali (kamroq xavfsiz, brute-force xavfi)
   b) SSH kalit juftligi orqali (tavsiya etiladi)
5. Shifrlangan "kanal" ochiladi — barcha buyruq/javob shu orqali o'tadi
```

### 3.2 SSH kalit juftligi — RSA/Ed25519

```bash
# RSA (keng qo'llab-quvvatlanadigan, eski)
ssh-keygen -t rsa -b 4096 -C "email@example.com"

# Ed25519 (zamonaviy, tezroq, kichikroq kalit, tavsiya etiladi)
ssh-keygen -t ed25519 -C "email@example.com"
```

```
~/.ssh/id_ed25519      → PRIVATE KEY — hech kimga, hech qachon bermang!
~/.ssh/id_ed25519.pub  → PUBLIC KEY — serverga qo'shiladi
```

**Ishlash mexanizmi (asimmetrik kriptografiya):**
```
Public key — serverning ~/.ssh/authorized_keys fayliga qo'shiladi

Ulanish paytida:
1. Server client'ga "challenge" (tasodifiy son) yuboradi
2. Client uni O'Z PRIVATE key'i bilan imzolaydi
3. Server buni PUBLIC key (allaqachon authorized_keys da bor) bilan tekshiradi
4. Mos kelsa — autentifikatsiya MUVAFFAQIYATLI (parol yubormasdan!)
```

```bash
ssh-copy-id username@192.168.1.100   # Public key'ni avtomatik serverga yuklaydi
```

### 3.3 SSH ulanish

```bash
ssh username@192.168.1.100                  # Standart, port 22
ssh -p 2222 username@192.168.1.100            # Boshqa port
ssh -i ~/.ssh/id_ed25519 username@192.168.1.100  # Aniq private key ko'rsatish
ssh -v username@192.168.1.100                 # Verbose — debugging uchun
```

### 3.4 SSH config fayli — `~/.ssh/config`

```
Host prod
    HostName 192.168.1.100
    User ubuntu
    Port 2222
    IdentityFile ~/.ssh/id_ed25519

Host staging
    HostName 192.168.1.200
    User deploy
    IdentityFile ~/.ssh/id_ed25519_staging
```

```bash
ssh prod       # Barcha sozlamalar bilan bitta so'z bilan ulanadi!
scp file.txt prod:/var/www/
```

### 3.5 Port Forwarding

```bash
# LOCAL forwarding — masofadagi serverdagi portni O'ZINGIZNING kompyuteringizga "ochish"
ssh -L 5432:localhost:5432 ubuntu@192.168.1.100
# → Endi localhost:5432 orqali serverning PostgreSQL'iga ulansa bo'ladi

# REMOTE forwarding — teskarisi, O'ZINGIZNING portni serverga "ochish"
ssh -R 8080:localhost:3000 ubuntu@192.168.1.100

# DYNAMIC forwarding — SOCKS proxy sifatida
ssh -D 1080 ubuntu@192.168.1.100
```

### 3.6 SCP — fayl nusxalash

```bash
# Local → Server
scp file.txt username@192.168.1.100:/var/www/

# Server → Local
scp username@192.168.1.100:/var/log/app.log ./

# Papka nusxalash (rekursiv)
scp -r ./dist username@192.168.1.100:/var/www/

# SSH config'dagi alias bilan
scp file.txt prod:/var/www/
```

`scp` — SSH protokoli **ustida** ishlaydi, shuning uchun trafik
shifrlangan.

### 3.7 rsync — SCP dan farqi

```bash
rsync -avz ./dist/ ubuntu@192.168.1.100:/var/www/
```

```
scp:   HAR DOIM barcha fayllarni TO'LIQ ko'chiradi (qayta ko'chirsa ham)
rsync: DELTA SYNC — faqat O'ZGARGAN qismlarni yuboradi (checksum solishtiradi)
       → Katta loyihalarda, qayta-qayta deploy qilishda ANCHA tezroq
```

`-a` (archive — permission/timestamp saqlaydi), `-v` (verbose),
`-z` (compress) — deploy skriptlarida eng ko'p ishlatiladigan flag'lar.

## 4. Kod — amalda

### curl — barcha metodlar va misollar

```bash
# GET
curl https://api.example.com/employees

# Header bilan
curl -X GET https://api.example.com/employees \
  -H "Authorization: Bearer eyJhbGc..." \
  -H "Content-Type: application/json"

# POST — JSON body bilan
curl -X POST https://api.example.com/employees \
  -H "Content-Type: application/json" \
  -d '{"name": "Orzibek", "age": 25}'

# PUT
curl -X PUT https://api.example.com/employees/1 \
  -H "Content-Type: application/json" \
  -d '{"name": "Orzibek Updated"}'

# DELETE
curl -X DELETE https://api.example.com/employees/1

# Faqat response header (body yo'q)
curl -I https://api.example.com/employees

# Verbose — TCP/TLS handshake, header larni to'liq ko'rish (debugging uchun)
curl -v https://api.example.com/employees

# SSL sertifikat tekshiruvini o'chirish (FAQAT local test uchun!)
curl -k https://localhost:5001/api/employees

# Fayl yuklab olish
curl -o output.json https://api.example.com/export

# Response'ni fayldan o'qib yuborish
curl -X POST https://api.example.com/employees -d @payload.json

# Keycloak/JWT token olish (loyihadagi auth stack uchun real misol)
curl -X POST https://keycloak.local/realms/erp/protocol/openid-connect/token \
  -d "grant_type=password" \
  -d "client_id=erp-api" \
  -d "username=admin" \
  -d "password=secret"
```

### telnet — port tekshirish

```bash
telnet 192.168.1.100 5432   # PostgreSQL porti ochiqmi?
telnet 192.168.1.100 80     # HTTP porti ochiqmi?

# Natijalar:
# "Connected to ..." → port OCHIQ, xizmat javob beryapti ✅
# "Connection refused" → port YOPIQ yoki xizmat ishlamayapti ❌
# Javob HECH NARSA bermasa (timeout) → firewall bloklagan bo'lishi mumkin
```

### traceroute/tracert — yo'l kuzatish

```bash
# Windows
tracert google.com

# Linux/Mac
traceroute google.com
```

```
Har bir "hop" — paket qaysi router orqali o'tganini ko'rsatadi:

1  192.168.1.1     1 ms   (uy routeri)
2  10.20.0.1        5 ms   (ISP)
3  172.16.5.1      15 ms   (magistral)
...
10 142.250.х.х      45 ms  (google server)

Agar biror hop'da "* * *" (timeout) ko'p bo'lsa —
o'sha nuqtada tarmoq sekinlashuvi yoki uzilish bor
```

Ichkarida `traceroute` — **TTL (Time To Live)** ni 1 dan boshlab
oshirib boradi: TTL=1 paket birinchi routerda "vaqti tugadi" xatosi
bilan qaytadi (kim ekanini bildiradi), TTL=2 — ikkinchi router va
hokazo — shu tarzda butun yo'l xaritaga tushiriladi.

### ping — ICMP

```bash
ping google.com
# 64 bytes from ...: icmp_seq=1 ttl=115 time=12.3 ms
```

`ping` — ICMP Echo Request/Reply protokoli orqali ishlaydi — server
"tirikligini" va **latency** (javob vaqti)ni tekshiradi. Diqqat: ba'zi
serverlar xavfsizlik siyosati sababli ICMP ga javob bermaydi (bu port
yopiq degani emas!).

### netstat — portlar va ulanishlar

```bash
netstat -an | grep LISTEN     # Qaysi portlar "tinglayapti"
netstat -an | grep 5432       # PostgreSQL porti band/bo'shligini tekshirish

# Windows'da
netstat -ano | findstr :5432
```

## 5. Amalda — deployment skriptida birgalikda ishlatilishi

```bash
# 1. Serverga ulanish (SSH config orqali)
ssh prod

# 2. Yangi build'ni serverga yuklash
scp -r ./publish/* prod:/var/www/hr-api/

# 3. Xizmatni qayta ishga tushirish
ssh prod "sudo systemctl restart hr-api"

# 4. Xizmat ishga tushganini tekshirish
curl -I http://prod-server/api/health

# 5. Agar javob bo'lmasa — port ochiqligini tekshirish
telnet prod-server 5000
```

## 6. Qachon ishlatish kerak?

| Vaziyat | Vosita |
|---|---|
| Serverga masofadan kirish, buyruq bajarish | `ssh` |
| Bitta/oz sonli fayl ko'chirish | `scp` |
| Katta loyiha, tez-tez deploy (faqat farqni yuborish) | `rsync` |
| API'ni terminal/skript orqali test qilish | `curl` |
| Port ochiq-yopiqligini tekshirish | `telnet` yoki `nc` |
| Tarmoq yo'lidagi sekinlik/uzilishni aniqlash | `traceroute`/`tracert` |
| Server "tirikligini" tekshirish (latency) | `ping` |
| Mahalliy portlar holatini ko'rish | `netstat` |

## 7. Qo'shimcha — chuqur nuqtalar

- **`known_hosts` fayli** — birinchi ulanishda server "host key"i
  saqlanadi. Agar server key'i **keyinchalik o'zgarsa** (masalan,
  server qayta o'rnatilgan) — SSH **ogohlantirish** beradi ("WARNING:
  REMOTE HOST IDENTIFICATION HAS CHANGED!") — bu Man-in-the-Middle
  hujumidan himoya.

- **`ssh-agent`** — private key parolini har safar kiritmaslik uchun
  xotirada (session davomida) saqlaydigan xizmat.

- **Firewall va telnet farqi:** agar port **yopiq** bo'lsa —
  "Connection refused" (darhol javob). Agar **firewall bloklagan**
  bo'lsa — hech qanday javob (timeout) — bu ikkisini farqlash muhim
  diagnostika ko'nikmasi.

- **`curl` bilan `Refit`ning aloqasi:** loyihada ishlatiladigan
  `Refit` kutubxonasi — HTTP so'rovlarni deklarativ C# interfeys
  orqali yasaydi, lekin "qopqoq ostida" xuddi `curl` kabi HTTP
  so'rov yuboradi. `curl -v` bilan qo'lda test qilib ko'rish —
  Refit orqali ishlamayotgan integratsiyani debug qilishning eng
  tez yo'li.

- **Real loyihada uchraydigan xato:** production serverga **parol
  bilan** SSH ulanishni yoqib qo'yish — brute-force hujumga ochiq
  qoldiradi. Xavfsizlik best-practice: `PasswordAuthentication no`
  serverning `sshd_config`ida, faqat kalit orqali autentifikatsiya.

## 8. Imtihon savollari

1. SSH kalit juftligi (public/private) qanday ishlaydi — autentifikatsiya
   jarayonini qadamma-qadam tushuntiring.
2. `scp` va `rsync` orasidagi asosiy farq nima?
3. `curl -v` qanday ma'lumot ko'rsatadi va u qachon foydali?
4. `telnet` bilan port tekshirilganda "Connection refused" va
   "timeout" orasidagi farq nima anglatadi?
5. SSH config fayli (`~/.ssh/config`) nima uchun kerak va u qanday
   ish jarayonini soddalashtiradi?
6. `traceroute` ichki mexanizmi (TTL asosida) qanday ishlaydi?
7. Nima uchun production serverlarda parol orqali SSH autentifikatsiya
   o'rniga faqat kalit ishlatish tavsiya etiladi?
