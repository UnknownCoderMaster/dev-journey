# Auth Basics Demo — O'quv Loyihasi

Bu Web API — `docs/Junior-A/17-auth-basics` mavzusini **amalda**
sinab ko'rish uchun yaratilgan. Bitta loyihada **3 ta autentifikatsiya
usuli** (Bearer/JWT, Basic, Cookie) bir vaqtda ishlaydi, shu bilan
birga **401 vs 403** farqini ham jonli ko'rsatadi.

## Ishga tushirish

```bash
cd projects/Junior-A/AuthBasicsDemo
dotnet run
```

Brauzer avtomatik `https://localhost:7178/swagger` (yoki
`http://localhost:5278/swagger`) sahifasini ochadi.

## Demo foydalanuvchilar

| Username | Parol | Rol |
|---|---|---|
| `admin` | `Admin123!` | Admin |
| `orzibek` | `User123!` | Employee |

## 1. Bearer (JWT) — sinash

1. Swagger'da `POST /api/auth/login` — body: `{"username":"admin","password":"Admin123!"}`
2. Javobdagi `accessToken`ni nusxalang
3. Swagger'dagi **Authorize** tugmasini bosing, `Bearer` bo'limiga tokenni qo'ying
4. `GET /api/me/bearer` — claims'laringizni ko'rasiz
5. `GET /api/admin/salary-report` — `admin` bilan `200 OK`, `orzibek` bilan `403 Forbidden`

curl orqali:
```bash
TOKEN=$(curl -s -X POST http://localhost:5278/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"Admin123!"}' | jq -r .accessToken)

curl -H "Authorization: Bearer $TOKEN" http://localhost:5278/api/me/bearer
```

## 2. Basic — sinash

Swagger'da **Authorize** tugmasidagi `Basic` bo'limiga
username/parolni kiriting (masalan `admin`/`Admin123!`), so'ng
`GET /api/me/basic`ni chaqiring.

curl orqali:
```bash
curl -u admin:Admin123! http://localhost:5278/api/me/basic
```

> Diqqat: `Authorization: Basic base64(user:pass)` — bu **shifrlash
> emas**, oddiy encoding. Shu sababli Basic Auth HAR DOIM HTTPS bilan
> birga ishlatilishi kerak (production'da).

## 3. Cookie — sinash

Swagger UI cookie oqimini ko'rsatish uchun eng qulay vosita emas —
**curl** (cookie jar bilan) yoki **Postman** tavsiya etiladi:

```bash
curl -c cookies.txt -X POST http://localhost:5278/api/auth/login-cookie \
  -H "Content-Type: application/json" \
  -d '{"username":"orzibek","password":"User123!"}'

curl -b cookies.txt http://localhost:5278/api/me/cookie
curl -b cookies.txt -X POST http://localhost:5278/api/auth/logout-cookie
```

## 4. 401 vs 403 — bevosita solishtirish

```bash
# 1) Token BUTUNLAY yo'q -> 401 Unauthorized ("kim ekaning bilmayman")
curl -i http://localhost:5278/api/admin/salary-report

# 2) 'orzibek' (Employee) tokeni bilan -> 403 Forbidden ("bilaman, lekin ruxsat yo'q")
curl -i -H "Authorization: Bearer <orzibek_token>" http://localhost:5278/api/admin/salary-report

# 3) 'admin' tokeni bilan -> 200 OK
curl -i -H "Authorization: Bearer <admin_token>" http://localhost:5278/api/admin/salary-report
```

## Loyiha tuzilmasi

```
Auth/BasicAuthenticationHandler.cs  — Custom AuthenticationHandler (Basic scheme)
Controllers/AuthController.cs       — login (JWT), login-cookie, logout-cookie
Controllers/MeController.cs         — /api/me/bearer|basic|cookie — ClaimsPrincipal ko'rsatish
Controllers/AdminController.cs      — Role-based policy, 401 vs 403 demosi
Services/                           — InMemoryUserStore, TokenService, ClaimsBuilder
Program.cs                          — 3 ta scheme + policy sozlash
```

## Eslatma

`appsettings.json`dagi `Jwt:SecretKey` — **faqat shu demo uchun**,
kodda ochiq turibdi. Haqiqiy loyihada bu — Environment Variable/Key
Vault orqali olinishi SHART (batafsil: `docs/Middle-D/52-safe-credentials`).
