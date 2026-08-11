using AutoMapper;
using AutoMapper.QueryableExtensions;
using AutoMapperMapsterDemo.Data;
using AutoMapperMapsterDemo.Dtos;
using AutoMapperMapsterDemo.Mapping;
using Mapster;
using Microsoft.EntityFrameworkCore;

Console.OutputEncoding = System.Text.Encoding.UTF8;

// ============================================================
// SOZLASH
// ============================================================

var mapperConfig = new MapperConfiguration(cfg => cfg.AddProfile<EmployeeMappingProfile>());

try
{
    mapperConfig.AssertConfigurationIsValid(); // Barcha CreateMap to'g'ri sozlanganini tekshirish
    Console.WriteLine("[OK] AutoMapper konfiguratsiyasi to'g'ri.");
}
catch (AutoMapperConfigurationException ex)
{
    Console.WriteLine("[OGOHLANTIRISH] Konfiguratsiyada muammo bor: " + ex.Message);
}

var mapper = mapperConfig.CreateMapper();

using var context = new AppDbContext();
SeedData.Populate(context);

// ============================================================
// MENU
// ============================================================

while (true)
{
    Console.WriteLine();
    Console.WriteLine("================================================");
    Console.WriteLine("   AutoMapper / Mapster - O'QUV DEMO LOYIHASI");
    Console.WriteLine("================================================");
    Console.WriteLine("1 - ProjectTo<T>()        (EF Core bilan SQL darajasida mapping)");
    Console.WriteLine("2 - Conditional Mapping   (shart asosida property mapping)");
    Console.WriteLine("3 - Mapping Inheritance   (Include / IncludeBase)");
    Console.WriteLine("4 - Mapster bilan solishtirish");
    Console.WriteLine("0 - Chiqish");
    Console.Write("Tanlovingiz: ");

    var choice = Console.ReadLine();
    Console.WriteLine();

    switch (choice)
    {
        case "1": Demo1_ProjectTo(); break;
        case "2": Demo2_ConditionalMapping(); break;
        case "3": Demo3_MappingInheritance(); break;
        case "4": Demo4_MapsterComparison(); break;
        case "0": return;
        default: Console.WriteLine("Noto'g'ri tanlov, qayta urinib ko'ring."); break;
    }
}

// ============================================================
// DEMO 1 — ProjectTo<T>()
// ============================================================
void Demo1_ProjectTo()
{
    Console.WriteLine("--- DEMO 1: ProjectTo<T>() vs Map<T>() ---\n");

    Console.WriteLine("[A] Map<T>() -- Entity TO'LIQ (barcha ustun) DB'dan yuklanadi, KEYIN C#'da mapping qilinadi:");
    var fullEntities = context.Employees.Include(e => e.Department).ToList();
    var dtosViaMap = mapper.Map<List<EmployeeDto>>(fullEntities);
    Console.WriteLine($"    {fullEntities.Count} ta Entity yuklandi -> {dtosViaMap.Count} ta DTO'ga aylantirildi.\n");

    Console.WriteLine("[B] ProjectTo<T>() -- SQL SO'ROVNING O'ZI faqat KERAKLI ustunlarni tanlaydi:");
    var dtosViaProjectTo = context.Employees
        .ProjectTo<EmployeeDto>(mapper.ConfigurationProvider)
        .ToList();

    foreach (var dto in dtosViaProjectTo)
    {
        var bonusText = dto.Bonus.HasValue ? dto.Bonus.Value.ToString("N0") : "yo'q";
        Console.WriteLine($"    {dto.FullName,-20} | {dto.DepartmentName,-12} | Bonus: {bonusText}");
    }

    Console.WriteLine();
    Console.WriteLine("XULOSA: ProjectTo -- Expression Tree orqali EF Core'ga uzatiladi,");
    Console.WriteLine("shuning uchun DB darajasida FAQAT kerakli ustunlar SELECT qilinadi.");
    Console.WriteLine("Katta jadvallarda (masalan 50+ ustun) bu -- sezilarli performance farqi beradi.");
}

// ============================================================
// DEMO 2 — Conditional Mapping
// ============================================================
void Demo2_ConditionalMapping()
{
    Console.WriteLine("--- DEMO 2: Conditional Mapping ---\n");
    Console.WriteLine("Qoida: Bonus FAQAT BaseSalary > 5,000,000 bo'lgan xodimlarga beriladi.\n");

    var employees = context.Employees.Include(e => e.Department).ToList();

    foreach (var emp in employees)
    {
        var dto = mapper.Map<EmployeeDto>(emp);
        var bonusText = dto.Bonus.HasValue ? $"{dto.Bonus:N0} so'm" : "BONUS YO'Q (shart bajarilmadi)";
        Console.WriteLine($"    {emp.FullName,-20} | Maosh: {emp.BaseSalary,10:N0} | {bonusText}");
    }

    Console.WriteLine();
    Console.WriteLine("XULOSA: .Condition() -- HAR SAFAR mapping vaqtida tekshiriladi.");
    Console.WriteLine("Agar shart FALSE bo'lsa -- property'ning DEFAULT qiymati (bu yerda null) qoladi.");
}

// ============================================================
// DEMO 3 — Mapping Inheritance
// ============================================================
void Demo3_MappingInheritance()
{
    Console.WriteLine("--- DEMO 3: Mapping Inheritance (Include / IncludeBase) ---\n");

    // Bitta ro'yxatda — Manager va Contractor ARALASH (polimorfik kolleksiya)
    var employees = context.Employees.Include(e => e.Department).ToList();

    Console.WriteLine("Har xodim uchun mos DTO turi AVTOMATIK tanlanadi (runtime turi asosida):\n");

    foreach (var emp in employees)
    {
        // mapper.Map<EmployeeDto>(emp) chaqirilsa ham -- AutoMapper 'emp.GetType()'ni
        // RUNTIME'da tekshiradi va Include<Manager,ManagerDto>() sozlamasi tufayli
        // HAQIQATDA ManagerDto (yoki ContractorDto) obyektini qaytaradi!
        var dto = mapper.Map<EmployeeDto>(emp);

        Console.Write($"    {dto.FullName,-20} -> DTO turi: {dto.GetType().Name,-15}");

        switch (dto)
        {
            case ManagerDto managerDto:
                Console.WriteLine($" | TeamSize: {managerDto.TeamSize}");
                break;
            case ContractorDto contractorDto:
                Console.WriteLine($" | HourlyRate: {contractorDto.HourlyRate:N0}");
                break;
            default:
                Console.WriteLine();
                break;
        }
    }

    Console.WriteLine();
    Console.WriteLine("XULOSA:");
    Console.WriteLine("  Include<TDerived,TDerivedDto>()  -- bazaviy Profile'ga: \"Manager kelsa, ManagerDto ishlat\" deydi");
    Console.WriteLine("  IncludeBase<TBase,TBaseDto>()    -- sub-klass mappingiga: \"umumiy maydonlarni bazaviydan ol\" deydi");
}

// ============================================================
// DEMO 4 — Mapster bilan solishtirish
// ============================================================
void Demo4_MapsterComparison()
{
    Console.WriteLine("--- DEMO 4: Mapster bilan solishtirish ---\n");

    var employee = context.Employees.Include(e => e.Department).First();

    Console.WriteLine("[A] Mapster -- CONFIG YOZMASDAN (convention/flattening qoidalari asosida):");
    var dtoDefault = employee.Adapt<EmployeeDto>();
    Console.WriteLine($"    {dtoDefault.FullName} | DepartmentName: '{dtoDefault.DepartmentName}' | Bonus: {dtoDefault.Bonus}");
    Console.WriteLine("    (Eslatma: Mapster ham, AutoMapper kabi, 'Department.Name' -> 'DepartmentName'ni");
    Console.WriteLine("     AVTOMATIK flattening qilishga urinishi mumkin -- kutubxona konvensiyasiga bog'liq.)\n");

    Console.WriteLine("[B] Mapster -- TypeAdapterConfig orqali CUSTOM/CONDITIONAL mapping:");
    TypeAdapterConfig<AutoMapperMapsterDemo.Models.Employee, EmployeeDto>.NewConfig()
        .Map(dest => dest.DepartmentName, src => src.Department != null ? src.Department.Name : "Bo'limsiz")
        .Map(dest => dest.Bonus, src => src.BaseSalary > 5_000_000 ? src.BaseSalary * 0.1m : (decimal?)null);

    var dtoConfigured = employee.Adapt<EmployeeDto>();
    Console.WriteLine($"    {dtoConfigured.FullName} | DepartmentName: '{dtoConfigured.DepartmentName}' | Bonus: {dtoConfigured.Bonus}\n");

    Console.WriteLine("XULOSA (AutoMapper vs Mapster):");
    Console.WriteLine("  AutoMapper -- Profile klass, katta ERP loyihalarda konfiguratsiyani boshqarish oson,");
    Console.WriteLine("                ProjectTo<T>() -- EF Core bilan juda kuchli integratsiya.");
    Console.WriteLine("  Mapster    -- odatda tezroq (ayniqsa compile-time kod generatsiya rejimida),");
    Console.WriteLine("                sintaksis qisqaroq, lekin katta loyihada konfiguratsiyani topish biroz qiyinroq bo'lishi mumkin.");
}
