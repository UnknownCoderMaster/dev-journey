# Role-based va Policy-based Avtorizatsiya — ASP.NET Core — Middle D

## 1. Nima? (Ta'rif)

**Authorization (Avtorizatsiya)** — allaqachon autentifikatsiyadan
o'tgan (kim ekanligi aniqlangan) foydalanuvchining **muayyan amalni
bajarishga huquqi bor-yo'qligini** aniqlash jarayoni.

**RBAC (Role-Based Access Control)** — huquqlar **rollar** orqali
boshqariladigan model: foydalanuvchiga rol beriladi (`Admin`,
`Manager`, `Employee`), va har bir rolga muayyan amallar ruxsat
etiladi.

**Policy-based Authorization** — ASP.NET Core'ning RBAC'dan
kengroq, **moslashuvchan qoidalar** (policy) asosida qaror qabul
qiluvchi avtorizatsiya tizimi.

**Claims-based Authorization** — foydalanuvchi haqidagi **key-value**
juftliklar (claims) asosida qaror qabul qilish.

**ABAC (Attribute-Based Access Control)** — huquqlar foydalanuvchi,
resurs va **kontekst atributlari** kombinatsiyasi asosida **dinamik**
hisoblanadigan eng moslashuvchan model.

## 2. Nima uchun kerak? (Muammo va yechim)

### Authentication vs Authorization farqi

```
Authentication: "SEN KIMSAN?"
  → Login/parol, JWT token tekshiruvi orqali javob topiladi
  → Natija: HttpContext.User (ClaimsPrincipal) to'ldiriladi

Authorization: "SEN NIMA QILA OLASAN?"
  → User allaqachon ma'lum, endi uning HUQUQI tekshiriladi
  → Natija: 200 OK (ruxsat) yoki 403 Forbidden (ruxsat yo'q)
```

**Middleware pipeline tartibi:**

```
So'rov keladi
    │
    ▼
UseAuthentication()  ← Token o'qiladi, User ANIQLANADI (kim ekanligi)
    │
    ▼
UseAuthorization()   ← [Authorize] tekshiriladi (nima qila olishi)
    │
    ▼
Controller Action bajariladi (agar RUXSAT bo'lsa)
```

Agar avtorizatsiya bo'lmaganida — har bir Controller action ichida
qo'lda `if (user.Role != "Admin") return Forbid();` yozish kerak
bo'lardi — bu takrorlanuvchi va xato qilish oson kod. Faqat RBAC
(oddiy rol tekshiruvi) yetarli bo'lmagan holatlar ham bor: masalan,
"foydalanuvchi FAQAT o'ZINING ma'lumotlarini ko'ra oladi" — bu
**resource-based** avtorizatsiya talab qiladi, oddiy rol tekshiruvi
YETARLI EMAS.

**Real hayot analogiyasi:** Authentication — bino kirish eshigidagi
**pasport tekshiruvi** (kim ekaningizni aniqlaydi). Authorization —
ichkarida har bir xonaning eshigidagi **kalit karta o'qigich**
(qaysi xonalarga kirish huquqingiz borligini tekshiradi) — pasportda
yozilgan lavozim (rol) asosida.

## 3. Ichida nima sodir bo'ladi? (Mexanizm)

### 3.1 RBAC — Role qanday beriladi va JWT'da qanday saqlanadi

```csharp
// Token yaratishda role claim qo'shiladi
var claims = new List<Claim>
{
    new(ClaimTypes.Name, user.FullName),
    new(ClaimTypes.Role, "Admin"),      // ✅ Bitta rol
    new(ClaimTypes.Role, "Manager")     // ✅ Bir nechta rol — bir nechta Claim qo'shiladi
};
```

JWT payload'da:
```json
{
  "sub": "123",
  "role": ["Admin", "Manager"]  // Bir nechta rol — array sifatida
}
```

`JwtBearer` middleware — tokenni tekshirganda, har bir `role` claim'ini
**`ClaimTypes.Role`** turiga mapping qiladi, va bu — `User.IsInRole()`
metodi orqali tekshiriladigan bo'ladi.

### 3.2 `[Authorize(Roles = "Admin")]` — ichida qanday ishlaydi

```csharp
[Authorize(Roles = "Admin")]
public IActionResult DeleteEmployee(int id) { /* ... */ }
```

Ichkarida bu — `RolesAuthorizationRequirement` degan
`IAuthorizationRequirement` yaratadi, va uning `HandleRequirementAsync`
metodi quyidagicha ishlaydi:

```
1. HttpContext.User.Identity.IsAuthenticated tekshiriladi
   → Agar FALSE bo'lsa — 401 Unauthorized

2. User.IsInRole("Admin") chaqiriladi
   → Bu ICHKARIDA: User.Claims.Any(c => c.Type == ClaimTypes.Role
                                      && c.Value == "Admin")

3. TRUE bo'lsa — Action BAJARILADI (200 OK va h.k.)
   FALSE bo'lsa — 403 Forbidden
```

```csharp
[Authorize(Roles = "Admin,Manager")] // VERGUL = "OR" mantiq
// Foydalanuvchi Admin YOKI Manager bo'lsa — YETARLI

[Authorize(Roles = "Admin")]
[Authorize(Roles = "Manager")] // Ikkita ALOHIDA atribut = "AND" mantiq
// Foydalanuvchi Admin VA Manager — IKKALASI HAM bo'lishi SHART (kamdan-kam kerak bo'ladi)
```

### 3.3 `[AllowAnonymous]` — qachon ishlatiladi

```csharp
[Authorize] // Butun controller himoyalangan
public class EmployeesController : ControllerBase
{
    [AllowAnonymous] // Bu action — ISTISNO, token SHART emas
    [HttpGet("public-info")]
    public IActionResult GetPublicInfo() => Ok(...);
}
```

`[AllowAnonymous]` — controller darajasidagi `[Authorize]`ni **faqat
shu action uchun** bekor qiladi. E'tibor bering: agar
`[AllowAnonymous]` global filter sifatida qo'shilgan bo'lsa — u
BARCHA `[Authorize]` larni bekor qilishi mumkin (kamdan-kam kerak
bo'ladigan holat).

### 3.4 Policy-based Authorization — RBAC'dan farqi

RBAC — faqat "qaysi rol" degan **bitta** o'lchovga qaraydi. Policy —
**har qanday murakkab mantiq**ni o'z ichiga olishi mumkin: yosh,
sertifikat, IP manzil, vaqt, resurs egaligi va h.k.

```csharp
builder.Services.AddAuthorization(options =>
{
    // RequireRole — RBAC'ning policy ko'rinishi
    options.AddPolicy("AdminOnly", policy =>
        policy.RequireRole("Admin"));

    // RequireClaim — muayyan claim mavjudligini/qiymatini tekshirish
    options.AddPolicy("HasDepartmentAccess", policy =>
        policy.RequireClaim("department_id", "1", "2", "3"));

    // RequireAssertion — ISTALGAN mantiqiy shart (eng moslashuvchan)
    options.AddPolicy("MinimumAge18", policy =>
        policy.RequireAssertion(context =>
        {
            var dobClaim = context.User.FindFirst("date_of_birth")?.Value;
            if (dobClaim is null) return false;
            var age = DateTime.UtcNow.Year - DateTime.Parse(dobClaim).Year;
            return age >= 18;
        }));

    // Bir nechta shartni birlashtirish
    options.AddPolicy("SeniorManager", policy =>
        policy.RequireRole("Manager")
              .RequireClaim("seniority", "senior"));
});
```

```csharp
[Authorize(Policy = "AdminOnly")]
public IActionResult Delete(int id) { /* ... */ }
```

### 3.5 `IAuthorizationRequirement` va `IAuthorizationHandler` — Custom Policy

Murakkab mantiq uchun (masalan, "faqat o'z bo'limi ma'lumotlarini
ko'rish") — **custom requirement + handler** yaratiladi:

```csharp
// 1. Requirement — "nima talab qilinishi" (faqat "marker", mantiq yo'q)
public class SameDepartmentRequirement : IAuthorizationRequirement { }

// 2. Handler — "qanday tekshirilishi" (haqiqiy mantiq shu yerda)
public class SameDepartmentHandler : AuthorizationHandler<SameDepartmentRequirement, Employee>
{
    protected override Task HandleRequirementAsync(
        AuthorizationHandlerContext context,
        SameDepartmentRequirement requirement,
        Employee resource) // Resource-based — TEKSHIRILAYOTGAN OBYEKT
    {
        var userDeptId = context.User.FindFirst("department_id")?.Value;

        if (userDeptId == resource.DepartmentId.ToString())
        {
            context.Succeed(requirement); // ✅ Talab BAJARILDI
        }
        // context.Fail() chaqirilmasa — DEFAULT holda "muvaffaqiyatsiz" hisoblanadi
        // (boshqa handler'lar hali ham "Succeed" qilishi mumkin bo'lgani uchun)

        return Task.CompletedTask;
    }
}

// 3. DI ga ro'yxatdan o'tkazish
builder.Services.AddScoped<IAuthorizationHandler, SameDepartmentHandler>();

// 4. Controller'da ishlatish (Resource-based — qo'lda chaqiriladi)
public class EmployeesController : ControllerBase
{
    private readonly IAuthorizationService _authService;

    [HttpGet("{id}")]
    public async Task<IActionResult> GetById(int id)
    {
        var emp = await _repo.GetByIdAsync(id);

        var result = await _authService.AuthorizeAsync(
            User, emp, new SameDepartmentRequirement());

        if (!result.Succeeded)
            return Forbid();

        return Ok(emp);
    }
}
```

### 3.6 Resource-based Authorization — nima uchun kerak

Oddiy `[Authorize(Roles = "Employee")]` — **barcha** xodimlarga bir
xil huquq beradi, lekin real hayotda "Har bir xodim FAQAT o'z
profilini tahrirlay oladi" kabi qoidalar bor — bu qoida **muayyan
resursga** bog'liq (qaysi xodim ID si), shuning uchun **atribut
darajasida emas, kod ichida, resurs bilan birga** tekshirilishi kerak
— yuqoridagi `AuthorizeAsync(User, resource, requirement)` patterni.

### 3.7 Claims-based Authorization — asoslari

```csharp
// ClaimsPrincipal — foydalanuvchining BARCHA claims to'plami
// ClaimsIdentity — bitta autentifikatsiya manbasidan kelgan claims guruhi
// (bitta User bir nechta Identity'ga ega bo'lishi mumkin — masalan, JWT + Windows Auth)

public IActionResult Get()
{
    ClaimsPrincipal principal = User;             // Joriy foydalanuvchi
    ClaimsIdentity? identity = User.Identity as ClaimsIdentity;

    string? userId = User.FindFirst(ClaimTypes.NameIdentifier)?.Value;
    string? email = User.FindFirst(ClaimTypes.Email)?.Value;
    var allClaims = User.Claims.Select(c => new { c.Type, c.Value });

    return Ok(allClaims);
}
```

```
ClaimsPrincipal
    │
    └── ClaimsIdentity (masalan, "Jwt" scheme'idan)
            │
            ├── Claim { Type: "sub", Value: "123" }
            ├── Claim { Type: "role", Value: "Admin" }
            └── Claim { Type: "department_id", Value: "5" }
```

### 3.8 ABAC — RBAC'dan farqi va dinamik policy

```
RBAC: "Sen ADMIN bo'lsang — hamma narsani qila olasan"
      (STATIK — faqat rol asosida, kontekstsiz)

ABAC: "Sen MANAGER bo'lsang VA bu hujjat SENING BO'LIMINGGA tegishli
       bo'lsa VA hozir ISH VAQTI bo'lsa — tahrirlashga ruxsat"
      (DINAMIK — foydalanuvchi + resurs + kontekst atributlari)
```

ABAC — `RequireAssertion` yoki custom `IAuthorizationHandler` orqali
ASP.NET Core'da amalga oshiriladi — policy nomi bilan emas, balki
**runtime'da hisoblanadigan shart** bilan qaror qabul qilinadi.

## 4. Kod — to'liq implementatsiya

### Program.cs — to'liq sozlash

```csharp
builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddJwtBearer(/* ... 01-jwt-authentication faylida ko'rsatilgan ... */);

builder.Services.AddAuthorization(options =>
{
    options.AddPolicy("AdminOnly", p => p.RequireRole("Admin"));

    options.AddPolicy("CanManageEmployees", p =>
        p.RequireRole("Admin", "HR")); // OR mantiq (RequireRole bir nechta arg qabul qiladi)

    options.AddPolicy("SameDepartmentOnly", p =>
        p.Requirements.Add(new SameDepartmentRequirement()));

    // Default policy — [Authorize] (parametrsiz) qaysi shartni talab qilishi
    options.DefaultPolicy = new AuthorizationPolicyBuilder()
        .RequireAuthenticatedUser()
        .Build();

    // Fallback policy — HECH QANDAY [Authorize]/[AllowAnonymous] bo'lmagan
    // endpointlar uchun ham autentifikatsiya talab qilish (xavfsiz default)
    options.FallbackPolicy = options.DefaultPolicy;
});

builder.Services.AddScoped<IAuthorizationHandler, SameDepartmentHandler>();
builder.Services.AddScoped<ICurrentUserService, CurrentUserService>();

var app = builder.Build();
app.UseAuthentication();
app.UseAuthorization();
app.MapControllers();
app.Run();
```

### Controller'da Policy va Role birgalikda

```csharp
[ApiController]
[Route("api/employees")]
[Authorize] // Barcha action — autentifikatsiya SHART
public class EmployeesController : ControllerBase
{
    [HttpGet]
    public IActionResult GetAll() => Ok(_repo.GetAll());  // Har qanday autentifikatsiyadan o'tgan user

    [HttpDelete("{id}")]
    [Authorize(Roles = "Admin")]              // Faqat Admin
    public IActionResult Delete(int id) { /* ... */ }

    [HttpPost]
    [Authorize(Policy = "CanManageEmployees")] // Policy orqali (Admin YOKI HR)
    public IActionResult Create(CreateEmployeeDto dto) { /* ... */ }

    [HttpPut("{id}")]
    public async Task<IActionResult> Update(int id, UpdateEmployeeDto dto)
    {
        var emp = await _repo.GetByIdAsync(id);
        var authResult = await _authService.AuthorizeAsync(
            User, emp, "SameDepartmentOnly");

        if (!authResult.Succeeded) return Forbid();

        // ... yangilash
        return NoContent();
    }
}
```

### `ICurrentUserService` — joriy foydalanuvchi ma'lumotlarini olish

Controller/Handler ichida `HttpContext.User`ga to'g'ridan murojaat
qilish — **testability**ni yomonlashtiradi (mock qilish qiyin) va
`HttpContext`ni Controller'dan tashqariga (masalan, MediatR
Handler'ga) uzatish yaxshi amaliyot emas. Yechim — abstraksiya:

```csharp
public interface ICurrentUserService
{
    int? UserId { get; }
    string? Role { get; }
    int? DepartmentId { get; }
    bool IsInRole(string role);
}

public class CurrentUserService : ICurrentUserService
{
    private readonly IHttpContextAccessor _httpContextAccessor;

    public CurrentUserService(IHttpContextAccessor httpContextAccessor)
        => _httpContextAccessor = httpContextAccessor;

    public int? UserId
    {
        get
        {
            var claim = _httpContextAccessor.HttpContext?.User
                .FindFirst(JwtRegisteredClaimNames.Sub)?.Value;
            return claim is null ? null : int.Parse(claim);
        }
    }

    public string? Role => _httpContextAccessor.HttpContext?.User
        .FindFirst(ClaimTypes.Role)?.Value;

    public int? DepartmentId
    {
        get
        {
            var claim = _httpContextAccessor.HttpContext?.User
                .FindFirst("department_id")?.Value;
            return claim is null ? null : int.Parse(claim);
        }
    }

    public bool IsInRole(string role) =>
        _httpContextAccessor.HttpContext?.User.IsInRole(role) ?? false;
}

// Program.cs da ro'yxatdan o'tkazish
builder.Services.AddHttpContextAccessor();
builder.Services.AddScoped<ICurrentUserService, CurrentUserService>();
```

### MediatR Handler'da avtorizatsiya (CQRS kontekstida)

MediatR Handler'lar HTTP qatlamidan **ajratilgan** bo'lishi kerak
(`HttpContext`ga bevosita bog'liq bo'lmasligi), shuning uchun
`ICurrentUserService` orqali avtorizatsiya mantig'i Handler ichiga
o'tkaziladi:

```csharp
public record DeleteEmployeeCommand(int Id) : IRequest;

public class DeleteEmployeeHandler : IRequestHandler<DeleteEmployeeCommand>
{
    private readonly ICurrentUserService _currentUser;
    private readonly AppDbContext _context;

    public async Task Handle(DeleteEmployeeCommand request, CancellationToken ct)
    {
        var emp = await _context.Employees.FindAsync([request.Id], ct)
            ?? throw new NotFoundException("Xodim topilmadi");

        // Resource-based tekshiruv — Handler ichida, HttpContext'siz
        if (_currentUser.Role != "Admin" && _currentUser.DepartmentId != emp.DepartmentId)
            throw new ForbiddenException("Bu xodimni o'chirishga huquqingiz yo'q");

        _context.Employees.Remove(emp);
        await _context.SaveChangesAsync(ct);
    }
}
```

Bu yondashuv — **MediatR Pipeline Behavior** orqali ham
umumlashtirilishi mumkin (har bir Command uchun avtomatik
avtorizatsiya tekshiruvi, cross-cutting concern sifatida):

```csharp
public class AuthorizationBehavior<TRequest, TResponse> : IPipelineBehavior<TRequest, TResponse>
    where TRequest : IRequest<TResponse>
{
    private readonly ICurrentUserService _currentUser;

    public async Task<TResponse> Handle(
        TRequest request, RequestHandlerDelegate<TResponse> next, CancellationToken ct)
    {
        if (request is IRequireAdminRole && _currentUser.Role != "Admin")
            throw new ForbiddenException("Admin huquqi kerak");

        return await next();
    }
}
```

## 5. Qachon va qanday ishlatish kerak?

| Vaziyat | Yechim |
|---|---|
| Oddiy, statik rol tekshiruvi | `[Authorize(Roles = "Admin")]` |
| Bir nechta shart kombinatsiyasi | Policy + `RequireAssertion` |
| Resursga (obyektga) bog'liq huquq | Resource-based (`IAuthorizationHandler<T>`) |
| Murakkab, ko'p bosqichli biznes qoida | Custom `IAuthorizationHandler` |
| CQRS/MediatR arxitekturada | `ICurrentUserService` + Handler ichida tekshiruv yoki Pipeline Behavior |
| Runtime'da o'zgaruvchan, kontekstga bog'liq huquq | ABAC (`RequireAssertion`) |

**Best practices:**
- **Principle of Least Privilege** — foydalanuvchiga faqat **zarur
  minimal** huquq berilishi kerak, "keyin kerak bo'lishi mumkin" deb
  ortiqcha huquq berilmasin
- Controller'da faqat **oddiy** tekshiruvlar (`[Authorize(Roles=...)]`),
  murakkab mantiq — Handler yoki Policy Handler'da
- Har doim **`[Authorize]` default** bo'lishi kerak (FallbackPolicy),
  `[AllowAnonymous]` — **aniq va ataylab** belgilangan istisno

**Anti-patternlar:**

```csharp
// ❌ Rol nomini controller ichida "sehrli string" sifatida qayta-qayta yozish
[Authorize(Roles = "Admin")]
// ✅ Konstantalar orqali (typo xatosidan himoya)
public static class Roles { public const string Admin = "Admin"; }
[Authorize(Roles = Roles.Admin)]

// ❌ Frontend'da faqat UI elementini yashirish, backend'da tekshirmaslik
// (hujumchi to'g'ridan API'ga so'rov yuborishi mumkin!)

// ❌ Client'dan kelgan "role" parametriga ISHONISH
public IActionResult Delete(int id, [FromQuery] string role)
{
    if (role == "Admin") { /* ... */ } // ❌ Client XOHLAGAN qiymatni yuborishi mumkin!
}
// ✅ FAQAT token ichidagi (server tomonidan imzolangan) claims'ga ishonish
```

## 6. Xavfsizlik va muhim nuqtalar

### Role escalation — rol oshirishdan himoya

**Role escalation** — foydalanuvchi o'z huquqini **noqonuniy** yo'l
bilan oshirishga urinishi (masalan, o'z profilini tahrirlash
so'rovida `role: "Admin"` maydonini qo'shib yuborish).

```csharp
// ❌ XAVFLI — client yuborgan DTO to'g'ridan Entity'ga mapping qilinadi
public IActionResult UpdateProfile(int id, Employee updatedEmployee)
{
    _context.Update(updatedEmployee); // Agar Employee'da Role property bo'lsa —
                                        // client uni O'ZGARTIRISHI mumkin!
}

// ✅ XAVFSIZ — faqat RUXSAT ETILGAN maydonlar UpdateDto'da bo'ladi
public class UpdateProfileDto
{
    public string FullName { get; set; } = null!;
    public string Phone { get; set; } = null!;
    // Role MAYDONI YO'Q — client uni umuman yubora olmaydi!
}
```

### IDOR (Insecure Direct Object Reference)

Foydalanuvchi URL'dagi ID'ni o'zgartirib, **boshqa birovning**
ma'lumotiga kirishga urinishi:

```
GET /api/employees/42/salary   ← Foydalanuvchi O'ZINING id=42 ekanligini bilishi mumkin
GET /api/employees/43/salary   ← Boshqa xodimning (43) maoshini so'rasa nima bo'ladi?
```

```csharp
// ❌ XAVFLI — faqat token borligi tekshirilgan, EGALIK tekshirilmagan
[Authorize]
public IActionResult GetSalary(int id) => Ok(_repo.GetSalary(id)); // ISTALGAN id qabul qilinadi!

// ✅ XAVFSIZ — resurs EGALIGI yoki huquqi tekshiriladi
[Authorize]
public IActionResult GetSalary(int id)
{
    if (id != _currentUser.UserId && _currentUser.Role != "HR")
        return Forbid();

    return Ok(_repo.GetSalary(id));
}
```

### Principle of Least Privilege — amalda

```
❌ Yangi xodimga "hammasi ishlashi uchun" Admin rol berish
✅ Aniq vazifasi uchun zarur MINIMAL rol/policy berish

❌ Bitta "SuperUser" rol bilan hammasini boshqarish
✅ Granular rollar: Employee, Manager, HR, Admin — har biri ANIQ chegarada
```

## 7. Imtihon savollari

1. Authentication va Authorization orasidagi farqni middleware
   pipeline kontekstida tushuntiring.
2. `[Authorize(Roles = "Admin,Manager")]` va ikkita alohida
   `[Authorize(Roles = "Admin")]` + `[Authorize(Roles = "Manager")]`
   atributi orasidagi mantiqiy farq nima?
3. Policy-based Authorization RBAC'dan nima bilan farq qiladi va
   qachon Policy ishlatish kerak?
4. `IAuthorizationRequirement` va `IAuthorizationHandler` orasidagi
   vazifa taqsimotini tushuntiring.
5. Resource-based Authorization nima va u nima uchun oddiy
   `[Authorize(Roles=...)]` bilan yechib bo'lmaydigan muammoni hal
   qiladi?
6. ABAC RBAC'dan qanday farq qiladi? Real misol keltiring.
7. MediatR CQRS arxitekturasida avtorizatsiya tekshiruvini qayerda
   (Controller'da yoki Handler'da) joylashtirish kerak va nima
   uchun?
8. IDOR (Insecure Direct Object Reference) zaifligi nima va uni
   qanday oldini olish mumkin?
9. Role escalation hujumi nima va DTO dizayni bu hujumni qanday
   oldini oladi?
10. `FallbackPolicy` nima uchun kerak va u sozlanmagan holatda qanday
    xavfsizlik muammosi yuzaga kelishi mumkin?
