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
2. Murakkab, juda optimallashtirilgan SQL kerak bo'lganda — ADO.NET to'g'ridan ishlatiladi
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
  NpgsqlCommand yaratadi: "SELECT * FROM employees"
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

**EF Core = ADO.NET + LINQ tarjimoni + Change Tracker + Mapping (Reflection orqali)**

### Connection Pooling — muhim mexanizm

`connection.Open()` chaqirilganda bazaga yangi TCP ulanish ochilmaydi har safar — .NET Connection Pool ishlatadi:

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
  → Ma'lum vaqt (default: ~4-8 daqiqa) kutib turadi
  → Agar shu vaqt ichida hech kim ishlatmasa — keyin yopiladi
```

Connection string da pool sozlamalari:

```
"Host=localhost;Database=erp;Min Pool Size=5;Max Pool Size=100;"
```

### SqlDataReader — Forward-only, Connected, Streaming

```csharp
using var reader = await command.ExecuteReaderAsync();
while (await reader.ReadAsync())
{
    var name = reader["name"];
}
```

**Forward-only** — faqat oldinga o'qiy oladi, orqaga qaytib bo'lmaydi.
Bu cheklov — ataylab qilingan xotira optimallashtirish:

```
❌ Agar barcha natija avval xotiraga yuklansa (1 million qator):
   RAM: [qator1][qator2]...[qator1000000] ← hammasi bir vaqtda

✅ DataReader STREAMING qiladi:
   RAM: [joriy qator]  ← har doim FAQAT 1 ta qator
   while (reader.Read()) — har safar faqat 1 ta qator keladi,
   oldingi "unutiladi"
```

Agar orqaga qaytish imkoni bo'lsa edi — .NET barcha o'qilgan qatorlarni xotirada saqlashi kerak bo'lardi. Forward-only bo'lgani uchun — faqat joriy qator xotirada turadi.

**Connected** — connection ochiq turishi SHART, o'qish tugamaguncha.

EF Core ning `ToListAsync()` ichida ham xuddi shu DataReader ishlaydi, lekin hammasi List ga yig'ilib beriladi. Agar streaming saqlanishi kerak bo'lsa:

```csharp
// 1 million qatorni birdaniga RAM ga yuklamaydi
await foreach (var emp in _context.Employees.AsAsyncEnumerable())
{
    Process(emp);
}
```

### SQL Injection — nima va qanday himoya?

```csharp
// ❌ XAVFLI — string concatenation
var sql = $"SELECT * FROM employees WHERE name = '{userInput}'";

// Agar userInput = "x'; DROP TABLE employees; --"
// Yakuniy SQL:
// SELECT * FROM employees WHERE name = 'x'; DROP TABLE employees; --'
// 💥 Butun jadval o'chiriladi!

// ✅ XAVFSIZ — parametrlangan so'rov
command.Parameters.AddWithValue("@name", userInput);
// Qiymat SQL kod sifatida emas, DATA sifatida yuboriladi
```

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

EF Core da `SaveChangesAsync()` ichida — bu transaction logikasi avtomatik bajariladi (agar bir nechta o'zgarish bo'lsa).

## 4. Kod — to'liq misol (PostgreSQL, Npgsql)

```csharp
using Npgsql;

public class EmployeeRawRepository
{
    private readonly string _connectionString;

    public EmployeeRawRepository(string connectionString)
    {
        _connectionString = connectionString;
    }

    // SELECT — barcha xodimlar
    public async Task<List<Employee>> GetAllAsync()
    {
        var employees = new List<Employee>();

        using var connection = new NpgsqlConnection(_connectionString);
        await connection.OpenAsync();

        using var command = new NpgsqlCommand(
            "SELECT id, name, age FROM employees", connection);

        using var reader = await command.ExecuteReaderAsync();
        while (await reader.ReadAsync())
        {
            employees.Add(new Employee
            {
                Id   = reader.GetInt32(0),
                Name = reader.GetString(1),
                Age  = reader.GetInt32(2)
            });
        }

        return employees;
    }

    // INSERT — parametrlangan (SQL Injection himoyasi)
    public async Task InsertAsync(Employee emp)
    {
        using var connection = new NpgsqlConnection(_connectionString);
        await connection.OpenAsync();

        using var command = new NpgsqlCommand(
            "INSERT INTO employees (name, age) VALUES (@name, @age)",
            connection);

        command.Parameters.AddWithValue("@name", emp.Name);
        command.Parameters.AddWithValue("@age",  emp.Age);

        await command.ExecuteNonQueryAsync();
    }

    // UPDATE
    public async Task UpdateAsync(Employee emp)
    {
        using var connection = new NpgsqlConnection(_connectionString);
        await connection.OpenAsync();

        using var command = new NpgsqlCommand(
            "UPDATE employees SET name = @name, age = @age WHERE id = @id",
            connection);

        command.Parameters.AddWithValue("@name", emp.Name);
        command.Parameters.AddWithValue("@age",  emp.Age);
        command.Parameters.AddWithValue("@id",   emp.Id);

        await command.ExecuteNonQueryAsync();
    }

    // DELETE
    public async Task DeleteAsync(int id)
    {
        using var connection = new NpgsqlConnection(_connectionString);
        await connection.OpenAsync();

        using var command = new NpgsqlCommand(
            "DELETE FROM employees WHERE id = @id", connection);

        command.Parameters.AddWithValue("@id", id);
        await command.ExecuteNonQueryAsync();
    }
}
```

## 5. Qo'shimcha — e'tiborga olinishi kerak bo'lgan nuqtalar

- **`ExecuteNonQuery`** — INSERT, UPDATE, DELETE uchun (natija qaytmaydi, faqat ta'sirlangan qatorlar soni)
- **`ExecuteScalar`** — bitta qiymat qaytadigan so'rovlar uchun:
  ```csharp
  var count = (long)await command.ExecuteScalarAsync();
  // SELECT COUNT(*) FROM employees
  ```
- **`ExecuteReader`** — bir nechta qator qaytadigan SELECT uchun
- **Dapper** — ADO.NET ustiga yozilgan yengil ORM, EF Core dan tezroq, ADO.NET dan qulay: `connection.QueryAsync<Employee>("SELECT ...")` — mapping ni o'zi qiladi
- **`using` kalit so'zi** — `IDisposable` ni implement qilgan `SqlConnection`, `SqlCommand`, `SqlDataReader` lar `using` bilan yopilishi SHART, aks holda connection pool va xotira muammolari yuzaga keladi
- **Connection String ni appsettings.json da saqlash**: hech qachon kodda hardcode qilmang — `configuration["ConnectionStrings:Default"]` orqali oling
- **Async/Await**: ADO.NET ning barcha asosiy metodlari async versiyaga ega (`ExecuteReaderAsync`, `OpenAsync` va h.k.) — ularni ishlatish thread ni bloklamaslik uchun muhim

## 6. Imtihon savollari

1. `connection.Close()` chaqirilganda TCP ulanish darhol yopiladimi? Nima sodir bo'ladi?
2. Nima uchun `SqlDataReader` "forward-only"? Bu qanday xotira optimallashtirish bilan bog'liq?
3. Quyidagi kodda xavfsizlik muammosi nima va qanday tuzatiladi?
   ```csharp
   var sql = $"SELECT * FROM employees WHERE name = '{name}'";
   ```
4. EF Core `SaveChangesAsync()` chaqirilganda, agar 3 ta entity o'zgargan bo'lsa — bu nechta alohida SQL yuboradi va nima uchun Transaction kerak?
5. `ExecuteNonQuery`, `ExecuteScalar`, `ExecuteReader` — qaysi birini qachon ishlatish kerak?
