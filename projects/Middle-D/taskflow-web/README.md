# TaskFlow Web

`TaskFlow.API` uchun frontend. Vue 3 (Composition API, `<script setup>`),
TypeScript, Vite, Pinia, Vue Router va `@microsoft/signalr`.

Maqsadi — backend'ni haqiqiy mijoz orqali tekshirish: har bir endpoint
ishlab turganini ko'rish va API shartnomasidagi nomuvofiqliklarni topish.

## Ishga tushirish

Node.js 20.19+ yoki 22.12+ kerak (Vite 6 talabi).

```bash
cd projects/Middle-D/taskflow-web

cp .env.example .env     # kerak bo'lsa manzilni o'zgartiring
npm install
npm run dev              # http://localhost:5173
```

Backend bir vaqtda ishlab turishi kerak:

```bash
cd projects/Middle-D/TaskFlow.API
dotnet run --launch-profile https      # https://localhost:7108
```

Birinchi ishga tushirishda dev sertifikatini ishonchli qilib qo'yish kerak:

```bash
dotnet dev-certs https --trust
```

### Nega proxy orqali

`TaskFlow.API` da **CORS sozlanmagan**. Shuning uchun brauzer
`localhost:5173` dan `localhost:7108` ga to'g'ridan-to'g'ri so'rov
yubora olmaydi — javob CORS siyosati bo'yicha bloklanadi.

Yechim sifatida Vite dev serverining proxy'si ishlatiladi
(`vite.config.ts`): `/api` va `/hubs` so'rovlari backend'ga uzatiladi va
brauzer uchun hammasi bitta origin'dan ketadi. Backend kodiga tegish
kerak bo'lmaydi.

Production uchun ikki variant bor: ikkisini bitta origin ostida host
qilish (`dist/` ni `wwwroot` ga qo'yish) yoki backend'da CORS yoqish.

## Tuzilishi

```
src/
  api/
    client.ts         fetch ustidagi qatlam: token, 401, xato formatlari
    resources.ts      endpoint'lar ro'yxati — API shartnomasining aksi
  components/
    board/            BoardColumn, CardItem, CardDrawer
    layout/           AppHeader
    ui/               AppButton, AppField, AppModal, AppBadge, AppState,
                      AppToaster, AppAvatar
  composables/
    useBoardHub.ts    SignalR ulanishi, guruhga qo'shilish, hodisalar
    useCardStatus.ts  enum normallashtirish (raqam va satr)
    useFormat.ts      sana, hajm, muddat holati
  stores/             auth, boards, cards, toasts (Pinia setup stores)
  types/index.ts      backend DTO'lari
  views/              Login, Register, Boards, Board, NotFound
```

## Qamralgan endpoint'lar

| Endpoint | Frontend'da |
|---|---|
| `POST /api/auth/register` | Ro'yxatdan o'tish sahifasi |
| `POST /api/auth/login` | Kirish sahifasi |
| `GET /api/boards` | Doskalar ro'yxati |
| `POST /api/boards` | "Yangi doska" modali |
| `GET /api/boards/{id}/cards` | Kanban ustunlari |
| `POST /api/boards/{id}/cards` | "Yangi karta" modali |
| `PATCH /api/boards/{id}/cards/{cardId}/status` | Sudrab tashlash va tugmalar |
| `DELETE /api/boards/{id}/cards/{cardId}` | Karta panelidan o'chirish |
| `GET /api/cards/{id}/comments` | Karta paneli |
| `POST /api/cards/{id}/comments` | Izoh yuborish |
| `DELETE /api/cards/{id}/comments/{commentId}` | O'z izohini o'chirish |
| `POST /api/cards/{id}/attachments` | Fayl yuklash |
| `GET /api/cards/{id}/attachments/{aid}/url` | MinIO presigned havolasi |
| `DELETE /api/cards/{id}/attachments/{aid}` | Faylni o'chirish |
| `/hubs/tasks` | Real vaqt: karta va izoh hodisalari |

`GET /api/boards/{id}` ishlatilmadi — sababi pastda.

## Backend'da topilgan muammolar

Frontend yozish jarayonida chiqqan nomuvofiqliklar. Ro'yxat
muhimlik tartibida.

### 1. `GET /api/boards/{id}` parol hashini oshkor qiladi

`BoardsController.GetById` EF entity'sini to'g'ridan-to'g'ri qaytaradi:

```csharp
var board = await _context.Boards
    .Include(b => b.Owner)              // User entity
    .Include(b => b.Cards)
        .ThenInclude(c => c.Assignee)   // User entity
    .FirstOrDefaultAsync(b => b.Id == id);

return Ok(board);
```

`User` entity'sida `PasswordHash` bor, shuning uchun u JSON javobga
tushadi. Bu ochiq zaiflik: har qanday tizimga kirgan foydalanuvchi
doska egasi va mas'ullarning bcrypt hashlarini o'qiy oladi.

Ustiga `Board → Cards → Board` aylanma havolasi bor, shuning uchun
serializatsiya ham muammo berishi mumkin.

Shu sababli frontend bu endpoint'ni **ishlatmaydi** — doska sarlavhasini
`GET /api/boards` projeksiyasidan oladi.

Yechim: DTO qaytarish yoki `Select` bilan projeksiya qilish.

### 2. Status enum ikki xil formatda qaytadi

`JsonStringEnumConverter` sozlanmagan, shuning uchun REST javoblarida
status **raqam** bo'lib keladi:

```json
{ "id": 12, "title": "Hisobot", "status": 1 }
```

SignalR hodisasida esa `.ToString()` chaqirilgan — **satr** keladi:

```csharp
.SendAsync("CardStatusUpdated", new { CardId = cardId, NewStatus = request.Status.ToString() });
```

Bitta maydon ikki joyda ikki xil tipda bo'lishi mijozni ikkisini ham
qayta ishlashga majbur qiladi (`src/composables/useCardStatus.ts`).

Yechim: `JsonStringEnumConverter` qo'shib, hamma joyda satr ishlatish.

### 3. `POST` javoblari `GET` projeksiyasiga mos kelmaydi

`POST /api/boards` va `POST /api/boards/{id}/cards` EF entity'sini
qaytaradi, `GET` esa anonim projeksiyani. Shakllar har xil, shuning
uchun frontend yaratilgandan keyin ro'yxatni **qayta o'qishga** majbur —
ortiqcha so'rov.

Yechim: `POST` ham `GET` bilan bir xil DTO qaytarsin.

### 4. Biriktirilgan fayllar ro'yxati endpoint'i yo'q

`AttachmentsController` da `POST`, `GET {id}/url` va `DELETE` bor, lekin
kartaning fayllarini **ro'yxat** qilib beradigan endpoint yo'q. Shuning
uchun karta panelida faqat shu sessiyada yuklangan fayllar ko'rinadi —
sahifa yangilansa ro'yxat bo'shaydi, lekin `attachmentsCount` noldan
katta bo'lib turadi.

Yechim: `GET /api/cards/{cardId}/attachments` qo'shish.

### 5. Foydalanuvchilar ro'yxati endpoint'i yo'q

`CreateCardRequest` da `AssigneeId` bor, lekin foydalanuvchilarni
olish yo'li yo'q. Shuning uchun UI dan mas'ul tanlab bo'lmaydi va
kartalar mas'ulsiz yaratiladi.

Yechim: `GET /api/users` (kamida `id` va `fullName`).

### 6. `GET /api/boards` hamma foydalanuvchiga bir xil ro'yxat beradi

So'rov `OwnerId` bo'yicha filtrlanmaydi va natija global kalit bilan
keshlanadi (`boards_list`). Ya'ni har qanday foydalanuvchi hamma
doskani ko'radi. Agar bu ataylab bo'lsa muammo yo'q; aks holda bu
IDOR turidagi kamchilik.

Shunga o'xshash: `CardsController` va `CommentsController` da ham
foydalanuvchi shu doskaga haqli ekani tekshirilmaydi.

### 7. Kesh faqat bitta joyda tozalanadi

`boards_list` keshi `POST /api/boards` da tozalanadi, lekin karta
qo'shilganda yoki o'chirilganda tozalanmaydi. Natijada
`cardsCount` 5 daqiqagacha eski qiymatda qoladi.

Frontend buni mahalliy hisoblagich bilan yamoqlaydi
(`boards.bumpCardsCount`), lekin bu backend muammosini yashiradi.

### 8. `CreateBoardRequest` ikki joyda

`TaskFlow.Application/DTOs/Board/CreateBoardRequest.cs` — bo'sh
`internal class`, hech qayerda ishlatilmaydi. Haqiqiy DTO
`BoardsController.cs` ning oxirida `record` sifatida e'lon qilingan.
Birinchi fayl o'lik kod.

### 9. Refresh token ishlamaydi

`POST /api/auth/login` refresh token qaytaradi, lekin uni almashtirish
uchun endpoint yo'q va `TokenService.ValidateRefreshToken` har doim
`null` qaytaradi. Token bazada ham saqlanmaydi.

Natijada access token muddati tugaganda (`Jwt:AccessTokenExpireMinutes`)
foydalanuvchi qaytadan login qilishga majbur. Frontend refresh'ni
ataylab amalga oshirmadi — backend tomoni yo'q.

### 10. `UseHttpsRedirection` va HTTP profili

`http` profili bilan ishga tushirilsa, `UseHttpsRedirection` HTTPS
portini topa olmaydi va ogohlantirish beradi. Shuning uchun proxy
standart holda `https://localhost:7108` ga ko'rsatadi.

## Qanday tekshiraman

1. `dotnet run --launch-profile https` — backend ko'tariladi.
2. `npm run dev` — frontend ko'tariladi.
3. Ro'yxatdan o'tish → doska yaratish → karta qo'shish.
4. Ikkinchi brauzer oynasida shu doskani ochish: bir oynada kartani
   sudrab ko'chirsa, ikkinchisida darhol o'zgarishi kerak. Agar
   o'zgarmasa — SignalR ulanmagan, header'dagi belgi buni ko'rsatadi.
5. Izoh qo'shish — ikkinchi oynada ham paydo bo'lishi kerak.
6. Fayl yuklash — MinIO ishlab turgan bo'lishi kerak
   (`docker-compose.yml`).

## Keyingi qadamlar

- Backend'da yuqoridagi 1 va 2-muammolarni tuzatish (eng muhimlari).
- `GET /api/users` va `GET /api/cards/{id}/attachments` qo'shilgandan
  keyin UI da mas'ul tanlash va fayllar ro'yxatini yoqish.
- Vitest bilan store'lar va `useCardStatus` uchun testlar.
- Doskani o'chirish va tahrirlash (backend'da endpoint yo'q).
