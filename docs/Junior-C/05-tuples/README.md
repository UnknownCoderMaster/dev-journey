# Tuples — Junior C

## 1. Nima?

**Tuple** — bir nechta qiymatni bitta "to'plam" sifatida qaytarish
yoki saqlash uchun mo'ljallangan yengil tuzilma.

## 2. Nima uchun kerak?

```csharp
// ❌ Faqat bitta qiymat qaytarish mumkin edi
public int Divide(int a, int b) { return a / b; }

// ✅ Tuple bilan — bo'linma va qoldiqni birgalikda
public (int quotient, int remainder) Divide(int a, int b)
    => (a / b, a % b);
```

## 3. Tuple turlari

### ValueTuple — zamonaviy (C# 7+)

```csharp
// Nomsiz
var t = (1, "salom", true);
Console.WriteLine(t.Item1); // → 1
Console.WriteLine(t.Item2); // → "salom"

// Nomli
var person = (Name: "Orzibek", Age: 25);
Console.WriteLine(person.Name); // → "Orzibek"
Console.WriteLine(person.Age);  // → 25
```

### Deconstruction — qiymatlarni ajratish

```csharp
var (name, age) = GetPerson();
Console.WriteLine(name); // → "Orzibek"

// Keraksiz qiymatni o'tkazib yuborish
var (_, age) = GetPerson(); // Faqat age kerak
```

## 4. Ichida nima sodir bo'ladi?

`ValueTuple` — **struct** (Value Type):
- Stack da saqlanadi
- Boxing yo'q
- Nusxa olinadi (reference emas)

Eski `Tuple<T1, T2>` — **class** (Reference Type), Heap da saqlanadi.
Zamonaviy kodda ishlatilmaydi.

## 5. Kod — amalda

```csharp
public (bool success, string message, int id) CreateEmployee(CreateEmployeeDto dto)
{
    if (string.IsNullOrWhiteSpace(dto.Name))
        return (false, "Ism bo'sh bo'lishi mumkin emas", 0);

    var id = _repo.Create(dto);
    return (true, "Muvaffaqiyatli yaratildi", id);
}

// Chaqirish
var (success, message, id) = CreateEmployee(dto);
if (!success)
    return BadRequest(message);
```

## 6. Tuple vs DTO — qachon qaysi?

```
Tuple:
  ✅ Ichki metod — tashqarida ko'rinmaydi
  ✅ 2-3 ta qiymat, oddiy
  ❌ Public API da — tushunarsiz

DTO/Record:
  ✅ Public API, Controller
  ✅ Validatsiya, dokumentatsiya kerak bo'lsa
  ✅ 3+ ta maydon
```

## 7. Qo'shimcha nuqtalar

- **`record` (C# 9+)** — Tuple ning kuchliroq alternativasi:
  ```csharp
  record PersonInfo(string Name, int Age);
  ```
- **Switch expression bilan** — Pattern matching:
  ```csharp
  string result = person switch
  {
      ("Orzibek", > 18) => "Katta yoshli Orzibek",
      (_, < 18)         => "Voyaga yetmagan",
      _                 => "Boshqa"
  };
  ```

## 8. Imtihon savollari

1. `ValueTuple` va eski `Tuple<T>` orasidagi asosiy farq nima?
2. Deconstruction nima va qanday ishlaydi?
3. Qachon Tuple, qachon DTO ishlatish kerak?
4. `_` (discard) nima uchun ishlatiladi?
