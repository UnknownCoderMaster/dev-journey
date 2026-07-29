# RBAC, ABAC, PBAC, DAC, MAC — Avtorizatsiya Modellari — Middle D

> RBAC va Policy-based Authorization'ning ASP.NET Core implementatsiyasi
> chuqur tarzda [02-role-based-authorization](../02-role-based-authorization/README.md)da
> yoritilgan. Bu fayl — **5 ta avtorizatsiya modelini (RBAC, ABAC,
> PBAC, DAC, MAC) bir-biri bilan solishtirgan holda** to'liq
> tushuntiradi.

## 1. Nima? (Ta'rif)

Avtorizatsiya modellari — "kimga nima ruxsat berilishi" qarorini
**qanday mezon** asosida qabul qilishni belgilaydigan yondashuvlar:

- **RBAC** — Role asosida (statik rol)
- **ABAC** — Attribute (foydalanuvchi/resurs/kontekst) asosida (dinamik)
- **PBAC** — Policy (qoida to'plami) asosida
- **DAC** — Discretionary — resurs **egasi** ruxsat beradi
- **MAC** — Mandatory — markazlashgan **xavfsizlik darajasi** asosida

## 2. Nima uchun kerak?

Har bir model — turli murakkablikdagi tizimlarga mos. Oddiy ERP'da
RBAC yetarli, lekin "faqat ish vaqtida, faqat o'z filialidagi
hujjatlarga kirish" kabi murakkab qoida — ABAC/PBAC talab qiladi.

## 3. Ichida nima sodir bo'ladi? (Mexanizm)

### 3.1 RBAC — Role-Based

```
Foydalanuvchi → Rol → Ruxsatlar
   Orzibek   →  Admin →  [Create, Read, Update, Delete]

[Authorize(Roles = "Admin")] — STATIK, kontekstga bog'liq EMAS
```

### 3.2 ABAC — Attribute-Based

```
Qaror = f(User attributes, Resource attributes, Environment attributes)

Misol: "Manager BO'LSA VA hujjat O'Z BO'LIMIGA tegishli BO'LSA
        VA hozir ISH VAQTI (9:00-18:00) BO'LSA → ruxsat"

policy.RequireAssertion(ctx =>
{
    var isManager = ctx.User.IsInRole("Manager");
    var sameDept = ...; // resurs bilan solishtirish
    var isWorkHours = DateTime.Now.Hour is >= 9 and < 18;
    return isManager && sameDept && isWorkHours;
});
```

ABAC — RBAC'dan farqli, **DINAMIK** — har so'rovda turli
kombinatsiyalar natijasida turlicha qaror chiqishi mumkin.

### 3.3 PBAC — Policy-Based

```
ASP.NET Core'ning O'ZI — aslida PBAC modelini implement qiladi:
RBAC HAM, ABAC HAM — Policy ICHIDA ifodalanishi mumkin.

options.AddPolicy("ComplexPolicy", policy =>
    policy.RequireRole("Manager")           // RBAC qismi
          .RequireClaim("department", "IT") // Claims qismi
          .RequireAssertion(ctx => ...));    // ABAC qismi
```

PBAC — RBAC/ABAC'ni **BIRLASHTIRUVCHI** freymvork sifatida qaraladi.

### 3.4 DAC — Discretionary Access Control

```
Resurs EGASI — kim kirishini O'ZI hal qiladi (masalan, Google Docs'da
"faylni X bilan ulashish" tugmasi).

Fayl tizimida: chmod, ACL (Access Control List) — egasi boshqa
foydalanuvchiga o'qish/yozish huquqi BERADI yoki OLIB TASHLAYDI.

ERP misolida: xodim o'z hujjatini boshqa xodim bilan "ulashishi"
mumkin — markaziy admin buni OLDINDAN belgilamagan.
```

### 3.5 MAC — Mandatory Access Control

```
MARKAZLASHGAN xavfsizlik siyosati — FOYDALANUVCHI (yoki resurs
EGASI) O'ZGARTIRA OLMAYDI, faqat TIZIM ADMINISTRATORI belgilaydi.

Harbiy/davlat tizimlarida: "Maxfiy", "Juda Maxfiy", "Ochiq" kabi
DARAJALAR — foydalanuvchi FAQAT O'Z DARAJASI yoki PASTROQ darajadagi
ma'lumotga kira oladi, HECH QANDAY istisno YO'Q (hatto resurs egasi
ham buni o'zgartira olmaydi).

ERP'da kamdan-kam ishlatiladi (juda qattiq), lekin: "Maosh
ma'lumoti — FAQAT HR va Moliya bo'limi, HECH KIM BOSHQA — hatto
Admin ham ko'ra olmasin" kabi qoida — MAC mantig'iga yaqin.
```

### 3.6 Solishtirish jadvali

| Model | Qaror kim tomonidan | Moslashuvchanlik | Murakkablik |
|---|---|---|---|
| RBAC | Tizim (rol asosida) | Past | Past |
| ABAC | Tizim (atribut kombinatsiyasi) | Yuqori | Yuqori |
| PBAC | Tizim (qoida to'plami) | Yuqori | O'rta |
| DAC | Resurs EGASI | O'rta | O'rta |
| MAC | Markaziy ADMIN, o'zgartirilmas | Past (ataylab) | Yuqori (tashkil qilish) |

## 4. Kod — Custom Handler (ABAC/DAC uslubida)

```csharp
public class ResourceOwnerRequirement : IAuthorizationRequirement { }

public class ResourceOwnerHandler : AuthorizationHandler<ResourceOwnerRequirement, Document>
{
    protected override Task HandleRequirementAsync(
        AuthorizationHandlerContext context, ResourceOwnerRequirement requirement, Document resource)
    {
        var userId = context.User.FindFirst(JwtRegisteredClaimNames.Sub)?.Value;

        // DAC — resurs EGASI (yoki u ruxsat bergan ulanish) tekshiriladi
        if (resource.OwnerId.ToString() == userId || resource.SharedWithUserIds.Contains(userId))
            context.Succeed(requirement);

        return Task.CompletedTask;
    }
}
```

## 5. Qachon ishlatish kerak?

| Vaziyat | Model |
|---|---|
| Oddiy, statik rollar (Admin/User) | RBAC |
| Kontekstga bog'liq murakkab qoida | ABAC |
| Bir nechta qoidani birlashtirish | PBAC (ASP.NET Core standart usuli) |
| Foydalanuvchi o'z resursini ulashadi | DAC |
| Qattiq, o'zgartirilmas xavfsizlik darajasi | MAC |

## 6. Muhim nuqtalar

- Amalda ko'p tizim — **RBAC + ABAC gibrid** ishlatadi (asosiy rol +
  qo'shimcha dinamik shartlar).
- DAC — moslashuvchan, lekin **noto'g'ri ulashish** xavfi bor (masalan,
  tasodifan barcha kirish huquqini berish).
- MAC — eng xavfsiz, lekin eng **qattiq** — amaliy biznes tizimlarida
  kamdan-kam to'liq qo'llaniladi.

## 7. Imtihon savollari

1. RBAC va ABAC orasidagi asosiy farq nima — statik va dinamik
   nuqtai nazaridan?
2. PBAC nima uchun RBAC va ABAC'ni "birlashtiruvchi" deb hisoblanadi?
3. DAC va MAC orasidagi farqni "kim qaror qabul qiladi" nuqtai
   nazaridan tushuntiring.
4. ERP tizimida qaysi ma'lumot uchun MAC mantig'i mos bo'lishi mumkin?
5. ASP.NET Core `RequireAssertion` qaysi modelni (ABAC/RBAC/PBAC)
   ifodalashga eng mos keladi?
6. Real loyihada RBAC va ABAC gibrid qanday ko'rinishda bo'lishi
   mumkin — misol keltiring.
