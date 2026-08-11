# AutoMapper / Mapster — O'quv Demo Loyihasi

Bu ConsoleApp — quyidagi mavzularni **amaliy misollar** bilan
o'rgatish uchun yaratilgan (mos hujjat: `docs/Junior-A/19-automapper`):

1. **ProjectTo<T>()** — `Map<T>()` bilan solishtirib, EF Core so'rovi
   darajasida (SQL SELECT) mapping qanday ishlashini ko'rsatadi.
2. **Conditional Mapping** — `Condition()` orqali faqat shart
   bajarilganda property'ni mapping qilish.
3. **Mapping Inheritance** — `Include()`/`IncludeBase()` orqali
   `Manager`/`Contractor` kabi meros olgan klasslarni to'g'ri
   mapping qilish, va polimorfik DTO tanlash.
4. **Mapster bilan solishtirish** — bir xil vazifani AutoMapper va
   Mapster bilan yechib, sintaksis/yondashuv farqini ko'rish.

## Ishga tushirish

```bash
cd projects/Junior-A/AutoMapperMapsterDemo
dotnet run
```

Konsolda chiqqan menyudan (1-4) kerakli demoni tanlang. Ma'lumotlar
— EF Core'ning **InMemory** provayderida saqlanadi (haqiqiy DB
sozlash shart emas — dars uchun qulay).

## Loyiha tuzilmasi

```
Models/       — Employee (bazaviy), Manager, Contractor, Department
Dtos/         — EmployeeDto (bazaviy), ManagerDto, ContractorDto
Data/         — AppDbContext (InMemory), SeedData (namunaviy ma'lumot)
Mapping/      — EmployeeMappingProfile (barcha 3 texnika shu yerda)
Program.cs    — Konsol menyu + 4 ta demo metod
```
