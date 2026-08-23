# API Key Auth Demo — O'quv Loyihasi

Bu Web API — `docs/Junior-A/18-api-key-auth` mavzusini **amalda**
sinab ko'rish uchun yaratilgan: custom `AuthenticationHandler`,
`X-Api-Key` header, DB'da faqat **hash** saqlash, va **scope**
asosida cheklash (401 vs 403 farqi bilan birga).

## Ishga tushirish

```bash
cd projects/Junior-A/ApiKeyAuthDemo
dotnet run
```

Brauzer avtomatik `https://localhost:7179/swagger` (yoki
`http://localhost:5279/swagger`) sahifasini ochadi.

## Demo API kalitlar

Bular — `Services/InMemoryApiKeyValidator.cs` faylida (faqat demo
uchun, kodda ochiq — haqiqiy loyihada bunday QILINMAYDI, README'dagi
"Eslatma" bo'limiga qarang):

| Kalit | Nomi | Scope | Holati |
|---|---|---|---|
| `px_live_9F3kQlZ7mN2vRt8bXcW1sYdA4uEjHpLo` | PartnerX | `webhook:payment` | ✅ Faol |
| `px_expired_1a2b3c4d5e6f7g8h9i0jklmno` | Eski hamkor | `webhook:payment` | ❌ Muddati o'tgan |

## 1. To'g'ri kalit bilan — muvaffaqiyatli chaqiruv

Swagger'da **Authorize** tugmasini bosib, `X-Api-Key` maydoniga
`px_live_9F3kQlZ7mN2vRt8bXcW1sYdA4uEjHpLo` ni qo'ying, so'ng:

```bash
curl -H "X-Api-Key: px_live_9F3kQlZ7mN2vRt8bXcW1sYdA4uEjHpLo" \
  http://localhost:5279/api/webhooks/whoami

curl -X POST http://localhost:5279/api/webhooks/payment-notification \
  -H "X-Api-Key: px_live_9F3kQlZ7mN2vRt8bXcW1sYdA4uEjHpLo" \
  -H "Content-Type: application/json" \
  -d '{"orderId":"ORD-1001","amount":250000,"currency":"UZS"}'
```

## 2. Kalit yo'q / noto'g'ri / muddati o'tgan — 401

```bash
curl -i http://localhost:5279/api/webhooks/whoami
# -> 401, WWW-Authenticate: ApiKey realm="ApiKeyAuthDemo"

curl -i -H "X-Api-Key: notogri-kalit" http://localhost:5279/api/webhooks/whoami
# -> 401

curl -i -H "X-Api-Key: px_expired_1a2b3c4d5e6f7g8h9i0jklmno" http://localhost:5279/api/webhooks/whoami
# -> 401 (ExpiresAt o'tgan — Validator uni "topilmadi" deb hisoblaydi)
```

## 3. To'g'ri kalit, LEKIN noto'g'ri scope — 403

`PartnerX` kaliti faqat `webhook:payment` scope'iga ega, lekin
`/api/reports/monthly` — `admin:reports` scope'ini talab qiladi:

```bash
curl -i -H "X-Api-Key: px_live_9F3kQlZ7mN2vRt8bXcW1sYdA4uEjHpLo" \
  http://localhost:5279/api/reports/monthly
# -> 403 Forbidden ("kim ekaning bilaman — PartnerX — lekin ruxsating yo'q")
```

Bu — **401 vs 403** farqining API Key kontekstidagi aniq
namunasi: kalit yo'q/noto'g'ri bo'lsa 401, kalit to'g'ri lekin
scope yetarli bo'lmasa 403.

## Loyiha tuzilmasi

```
Auth/ApiKeyAuthenticationHandler.cs   — Custom AuthenticationHandler (X-Api-Key)
Controllers/WebhookController.cs      — payment-notification, whoami
Controllers/ReportsController.cs      — scope-based 403 demosi
Services/InMemoryApiKeyValidator.cs   — kalitlarni HASH qilib saqlash/tekshirish
Program.cs                            — scheme + scope-based policy sozlash
```

## Eslatma

- API Key DB'da **hash** (SHA256) qilib saqlanadi — parol kabi,
  RAW qiymat qayta tiklanmaydi.
- Bu loyihada RAW demo kalitlar kod ichida **const** sifatida
  ko'rinadi — bu FAQAT sizga sinash imkonini berish uchun. Haqiqiy
  loyihada RAW kalit foydalanuvchiga **faqat yaratilgan paytda bir
  marta** ko'rsatiladi, kod ichida hech qachon saqlanmaydi.
