# HTTP Verbs, Request/Response, HTTP va HTTPS — Junior C

## 1. HTTP Verbs — semantika

| Verb | Maqsad | Idempotent? | Body? |
|---|---|---|---|
| GET | Ma'lumot olish | ✅ | ❌ |
| POST | Yangi yaratish | ❌ | ✅ |
| PUT | To'liq yangilash | ✅ | ✅ |
| PATCH | Qisman yangilash | ❌ | ✅ |
| DELETE | O'chirish | ✅ | ❌ |
| HEAD | Faqat header | ✅ | ❌ |
| OPTIONS | Ruxsat tekshirish | ✅ | ❌ |

**Idempotent** = bir xil so'rov bir necha marta yuborilsa ham natija bir xil.

## 2. Content-Type

```
Request:
Content-Type: application/json    → JSON yuborilmoqda
Content-Type: multipart/form-data → Fayl yuborilmoqda
Content-Type: application/xml     → XML yuborilmoqda

Response:
Accept: application/json          → Client JSON xohlaydi
```

## 3. HTTP Status Kodlari

```
2xx — Muvaffaqiyatli:
  200 OK              → Oddiy muvaffaqiyat
  201 Created         → Yangi resurs yaratildi
  204 No Content      → Muvaffaqiyatli, javob yo'q (DELETE)

4xx — Client xatosi:
  400 Bad Request     → Noto'g'ri so'rov
  401 Unauthorized    → Autentifikatsiya kerak
  403 Forbidden       → Ruxsat yo'q
  404 Not Found       → Topilmadi
  409 Conflict        → Ziddiyat
  422 Unprocessable   → Validatsiya xatosi

5xx — Server xatosi:
  500 Internal Error  → Server xatosi
  502 Bad Gateway     → Gateway xatosi
  503 Unavailable     → Server vaqtincha ishlamaydi
```

## 4. HTTP vs HTTPS — ichida nima sodir bo'ladi?

```
HTTP:
  Client → [ochiq matn] → Server
  Hacker o'rtada o'qiy oladi! (Man-in-the-middle)

HTTPS:
  Client → [shifrlangan] → Server
  Hacker o'qiy olmaydi
```

### TLS Handshake

```
1. Client: "Men quyidagi cipher lar bilan ishlay olaman"
2. Server: "Mana mening sertifikatim (public key bilan)"
3. Client: Sertifikatni CA orqali tekshiradi
4. Client: Session key yaratadi, server public key bilan shifrlaydi
5. Server: Private key bilan ochadi → session key olinadi
6. Ikkalasi ham session key bilan xabar shifrlaydi
```

### HTTP/1.1 vs HTTP/2

```
HTTP/1.1:
  Har bir so'rov → yangi TCP ulanish
  Head-of-line blocking

HTTP/2:
  Bitta TCP → parallel so'rovlar (multiplexing)
  Header compression (HPACK)
  Server push
```

## 5. Qo'shimcha nuqtalar

- **CORS** — boshqa origin dan so'rov:
  ```csharp
  builder.Services.AddCors(o =>
      o.AddPolicy("Allow", p => p.AllowAnyOrigin()));
  ```
- **Idempotency key** — POST ni idempotent qilish:
  `Idempotency-Key: uuid` header.
- **ETag** — cache invalidation uchun resurs versiyasi.

## 6. Imtihon savollari

1. `PUT` va `PATCH` orasidagi farq nima?
2. Idempotent nima degani? Qaysi verblar idempotent?
3. TLS handshake qanday ishlaydi?
4. HTTP/2 ning HTTP/1.1 dan asosiy ustunligi nima?
5. 401 va 403 orasidagi farq nima?
