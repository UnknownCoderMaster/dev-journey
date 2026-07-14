# ADO.NET — Junior D

## 1. Nima?

**ADO.NET (ActiveX Data Objects .NET)** — .NET dan ma'lumotlar bazasi
bilan **eng past darajada, to'g'ridan-to'g'ri** ishlash texnologiyasi.

```csharp
using Npgsql; // PostgreSQL uchun

using var connection = new NpgsqlConnection(connectionString);
await connection.OpenAsync();

using var command = new NpgsqlCommand(
    "SELECT * FROM employees", connection);

using var reader = await command.ExecuteReaderAsync();
while (await reader.ReadAsync())
{
    Console.WriteLine(reader["name"]);
}
```

## 2. Nima uchun kerak?

```
EF Core    → yuqori darajadagi qatlam (qulay, lekin "sehr" tuyuladi)
ADO.NET    → past darajadagi qatlam (EF Core'ning O'ZI ichida shuni ishlatadi)
```

ADO.NET ni bilish kerak, chunki:
1. EF Core ICHIDA aynan ADO.NET ishlaydi — EF Core faqat "qulaylik qatlami"
2. Murakkab, optimallashtirilgan SQL kerak bo'lganda — ADO.NET to'g'ridan ishlatiladi
3. Intervyuda "EF Core qanday ishlaydi?" deyilganda — javob ADO.NET orqali beriladi

## 3. Ichida nima sodir bo'ladi?

### EF Core va ADO.NET munosabati

```
Siz yozasiz:
  _context.Employees.ToListAsync()
         │
         ▼
EF Core ichida (LINQ Provider):
  LINQ → SQL ga "tarjima" qilinadi
         │
         ▼
EF Core ADO.NET ni chaqiradi:
  NpgsqlCommand yaratadi
  NpgsqlConnection orqali bazaga yuboradi
         │
         ▼
NpgsqlDataReader orqali natijalarni o'qiydi
         │
         ▼
EF Core natijalarni Employee obyektlariga mapping qiladi (Reflection orqali!)
         │
         ▼
List<Employee> qaytadi
```

EF Core = ADO.NET + LINQ tarjimoni + Change Tracker + Mapping (Reflection orqali)

---

### Connection Pooling — muhim mexanizm

`connection.Open()` chaqirilganda bazaga **yangi TCP ulanish** ochilmaydi
har safar — .NET **Connection Pool** ishlatadi:

```
connection.Open() chaqirilganda:

  Pool da BO'SH connection bormi?
       │
       ├─ HA  → mavjud TCP socket ni qayta beradi
       │        (tezroq — TCP handshake qayta bo'lmaydi)
       │
       └─ YO'Q → yangi TCP socket ochadi:
                  1. TCP handshake (SYN, SYN-ACK, ACK)
                  2. Database bilan autentifikatsiya
                  3. Bu ~50-200ms vaqt oladi!

connection.Close() chaqirilganda:
  TCP socket DARHOL yopilmaydi!
  → Pool ga "bo'sh" deb belgilanib qaytariladi
  → Ma'lum vaqt (~4-8 daqiqa) kutib turadi
  → Hech kim ishlatmasa — keyin yopiladi
```

Connection = TCP socket + autentifikatsiya holati (thread emas!)

Connection string da pool sozlamalari:
```
"Host=localhost;Database=erp;Min Pool Size=5;Max Pool Size=100;"
```

---

### SqlDataReader — Forward-only, Connected, Streaming

```csharp
using var reader = await command.ExecuteReaderAsync();
while (await reader.ReadAsync())
{
    var name = reader["name"];
}
```

**Forward-only** — faqat oldinga o'qiy oladi, orqaga qaytib bo'lmaydi.

Bu cheklov — ataylab qilingan **xotira optimallashtirish**:

```
❌ Agar barcha natija avval xotiraga yuklansa (1 million qator):
   RAM: [qator1][qator2]...[qator1000000] ← hammasi bir vaqtda

✅ DataReader STREAMING qiladi:
   RAM: [joriy qator] ← har doim FAQAT 1 ta qator
```

Agar orqaga qaytish imkoni bo'lsa edi — .NET barcha o'qilgan qatorlarni
xotirada saqlashi kerak bo'lardi. Forward-only bo'lgani uchun — faqat
joriy qator xotirada turadi.

**Connected** — connection ochiq turishi SHART, o'qish tugamaguncha.

EF Core streaming uchun:
```csharp
await foreach (var emp in _context.Employees.AsAsyncEnumerable())
{
    Process(emp); // bitta-bitta keladi, RAM ga hammasi yuklanmaydi
}
```

---

### SQL Injection — nima va qanday himoya?

```csharp
// ❌ XAVFLI — string concatenation
var sql = $"SELECT * FROM employees WHERE name = '{userInput}'";
// Agar userInput = "x'; DROP TABLE employees; --"
// 💥 Butun jadval o'chiriladi!

// ✅ XAVFSIZ — parametrlangan so'rov
command.Parameters.AddWithValue("@name", userInput);
// Qiymat SQL kod sifatida emas, DATA sifatida yuboriladi
```

---

### Transaction — bir nechta amalni "bitta" qilish

```csharp
using var connection = new NpgsqlConnection(_connectionString);
await connection.OpenAsync();
using var transaction = await connection.BeginTransactionAsync();

try
{
    using var cmd1 = new NpgsqlCommand(
        "UPDATE accounts SET balance = balance - 100 WHERE id = 1",
        connection, transaction);
    await cmd1.ExecuteNonQueryAsync();

    using var cmd2 = new NpgsqlCommand(
        "UPDATE accounts SET balance = balance + 100 WHERE id = 2",
        connection, transaction);
    await cmd2.ExecuteNonQueryAsync();

    await transaction.CommitAsync();   // Ikkalasi ham muvaffaqiyatli
}
catch
{
    await transaction.RollbackAsync(); // Xato bo'lsa — ikkalasi ham bekor
    throw;
}
```

EF Core da `SaveChangesAsync()` — bu transaction logikasini avtomatik bajaradi.

---

### Repository Pattern — ADO.NET bilan

ADO.NET da Repository kerak, chunki:
```
1. SQL kodi — Repository da yashirilgan
2. Controller faqat HTTP bilan shug'ullanadi
3. Bir xil SQL takrorlanmaydi
4. Keyinchalik EF Core ga o'tish oson

Controller → Repository (SQL yashiringan) → ADO.NET → DB
```

EF Core + CQRS da esa Repository shart emas:
```
DbContext o'zi Repository + Unit of Work ni implement qiladi
Controller → Handler → DbContext → DB
```

## 4. Execute metodlari — qaysi birini qachon?

| Metod | Qachon | Qaytaradi |
|---|---|---|
| `ExecuteReader` | SELECT (ko'p qator) | DataReader |
| `ExecuteScalar` | SELECT COUNT(*), RETURNING id | Bitta qiymat |
| `ExecuteNonQuery` | INSERT, UPDATE, DELETE | Ta'sirlangan qatorlar soni |

```csharp
// ExecuteReader — ko'p qator
using var reader = await command.ExecuteReaderAsync();

// ExecuteScalar — bitta qiymat (masalan yangi id)
var id = await command.ExecuteScalarAsync();
return Convert.ToInt32(id);

// ExecuteNonQuery — ta'sirlangan qatorlar
var rowsAffected = await command.ExecuteNonQueryAsync();
return rowsAffected > 0;
```

## 5. Amaliy loyiha — HR Management API

Bu mavzu doirasida **HR Management API** loyihasi qurildi:

**Texnologiyalar:** ASP.NET Core Web API + ADO.NET + Npgsql + PostgreSQL + Swagger

**Jadvallar:**
```sql
departments  → id, name, created_at, updated_at
positions    → id, name, department_id, created_at, updated_at
employees    → id, full_name, date_of_birth, position_id, hired_at,
               created_at, updated_at
```

**Papka tuzilmasi:**
```
HrManagementApi/
├── Controllers/
│   ├── DepartmentsController.cs
│   ├── PositionsController.cs
│   └── EmployeesController.cs
├── Repositories/
│   ├── IDepartmentRepository.cs
│   ├── DepartmentRepository.cs
│   ├── IPositionRepository.cs
│   ├── PositionRepository.cs
│   ├── IEmployeeRepository.cs
│   └── EmployeeRepository.cs
├── Models/
│   ├── Department.cs
│   ├── Position.cs
│   └── Employee.cs
├── DTOs/
│   └── EmployeeDto.cs
├── appsettings.json
└── Program.cs
```

**O'rganilgan asosiy nuqtalar:**
- ADO.NET — to'g'ridan SQL yozish
- Connection Pooling — TCP socket qayta ishlatilishi
- Forward-only DataReader — xotira optimallashtirish
- SQL Injection himoyasi — parametrlangan so'rovlar
- Repository Pattern — SQL ni yashirish
- JOIN — EmployeeDto bilan bog'liq jadvallardan ma'lumot olish
- REST konvensiyasi — to'g'ri HTTP metodlar va route lar
- `ExecuteReader`, `ExecuteScalar`, `ExecuteNonQuery` — to'g'ri joyda

**Loyiha joylashuvi:** `projects/Junior-D/HrManagementApi/`

## 6. Qo'shimcha — e'tiborga olinishi kerak bo'lgan nuqtalar

- **`using` kalit so'zi** — `NpgsqlConnection`, `NpgsqlCommand`,
  `NpgsqlDataReader` lar `IDisposable` — `using` bilan yopilishi SHART
- **`DateTime.UtcNow`** — `DateTime.Now` o'rniga ishlatish tavsiya etiladi,
  timezone muammolarini oldini oladi
- **`created_at`** — kodda yubormasdan DB ga `DEFAULT NOW()` ishonib
  qoldirish yaxshi amaliyot
- **`DateOnly`** — Npgsql da `NpgsqlDbType.Date` bilan yuborish ishonchli
- **Dapper** — ADO.NET ustiga yozilgan yengil ORM, mapping ni o'zi qiladi:
  `connection.QueryAsync<Employee>("SELECT ...")`
- **Connection string** — hech qachon kodda hardcode qilmang,
  `appsettings.json` dan oling (va real parollarni git'ga commit qilmang —
  `.gitignore` orqali chiqarib tashlang, `.example` fayl bilan formatni
  ko'rsating)

## 7. Imtihon savollari

1. `connection.Close()` chaqirilganda TCP ulanish darhol yopiladimi?
2. Nima uchun `SqlDataReader` "forward-only"? Xotira bilan bog'liqligini tushuntiring.
3. SQL Injection nima va qanday himoya qilinadi?
4. EF Core `SaveChangesAsync()` da 3 ta entity o'zgargan bo'lsa —
   nechta SQL yuboriladi va nima uchun Transaction kerak?
5. `ExecuteNonQuery`, `ExecuteScalar`, `ExecuteReader` — qaysi birini qachon?
6. Repository Pattern nima uchun kerak va EF Core + CQRS da nima uchun
   shart emas?
