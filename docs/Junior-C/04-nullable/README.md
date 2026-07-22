# Nullable — `?`, `??`, `!`, `= null!`, `default!` — Junior C

## 1. Nima?

**Nullable** — o'zgaruvchi `null` qiymat qabul qila olishini
belgilash mexanizmi.

## 2. Nullable Value Types — `?`

```csharp
int x = null;   // ❌ int null bo'la olmaydi
int? x = null;  // ✅ Nullable<int> — null bo'lishi mumkin

int? age = null;
if (age.HasValue)
    Console.WriteLine(age.Value);
else
    Console.WriteLine("Yosh kiritilmagan");
```

`int?` = `Nullable<int>` — ichida `Value` va `HasValue` mavjud.

## 3. Nullable Reference Types (C# 8+)

```csharp
// Loyihada yoqish (csproj):
// <Nullable>enable</Nullable>

string name = null;  // ⚠️ Ogohlantirish
string? name = null; // ✅ Aniq null bo'lishi mumkin
```

## 4. Operatorlar

### `??` — Null coalescing

```csharp
string? name = null;
string result = name ?? "Noma'lum"; // → "Noma'lum"

// Zanjir
string? a = null, b = null, c = "topildi";
string r = a ?? b ?? c; // → "topildi"
```

### `??=` — Null coalescing assignment

```csharp
string? name = null;
name ??= "Default"; // Agar null bo'lsa — o'rnat
Console.WriteLine(name); // → "Default"
```

### `?.` — Null conditional

```csharp
Employee? emp = null;
int? len = emp?.Name?.Length; // null (exception yo'q!)

string? city = emp?.Address?.City?.ToUpper();
```

### `!` — Null forgiving operator

```csharp
string? name = GetName();
int len = name!.Length; // "Men kafolat beraman, null emas"
// Agar aslida null bo'lsa — runtime NullReferenceException!
```

## 5. `default!` va `= null!`

```csharp
public class Employee
{
    // Ogohlantirish yo'qoladi, lekin xavf saqlanadi
    public string Name { get; set; } = null!;
    public string Position { get; set; } = default!;

    // Eng to'g'ri yondashuv (C# 11+)
    public required string Name { get; set; }
}
```

## 6. Amalda — ERP misoli

```csharp
public class EmployeeService
{
    public async Task<string> GetDepartmentName(int employeeId)
    {
        var emp = await _repo.GetByIdAsync(employeeId);
        return emp?.Department?.Name ?? "Bo'lim tayinlanmagan";
    }

    public void UpdateAge(Employee emp, int? age)
    {
        if (age.HasValue && age.Value > 0)
            emp.Age = age.Value;

        emp.Age = age ?? emp.Age; // null bo'lsa o'zgartirma
    }
}
```

## 7. Qo'shimcha nuqtalar

- **`Nullable<T>` struct** — `int?` aslida `Nullable<int>` struct.
- **Null Object Pattern** — null o'rniga "bo'sh" obyekt qaytarish:
  ```csharp
  public Employee GetById(int id)
      => _repo.GetById(id) ?? Employee.Empty;
  ```
- **`ArgumentNullException.ThrowIfNull`** (C# 10+):
  ```csharp
  ArgumentNullException.ThrowIfNull(employee);
  ```

## 8. Imtihon savollari

1. `int?` va `int` orasidagi farq nima? Xotirada qanday saqlanadi?
2. `?.` operatori nima uchun kerak?
3. `??` va `??=` orasidagi farq nima?
4. `null!` ishlatish xavfli emasmi? Qachon to'g'ri, qachon xato?
5. `required` kalit so'zi (C# 11+) nima uchun `= null!` dan yaxshiroq?
