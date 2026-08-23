using NLayerDemo.BusinessLogic.Dtos;
using NLayerDemo.BusinessLogic.Exceptions;
using NLayerDemo.DataAccess;
using NLayerDemo.DataAccess.Entities;

namespace NLayerDemo.BusinessLogic;

// ⚠️ "God Service" — docs/Junior-A/12-mvc-nlayer-architecture (4-bo'lim)
// dagi aynan shu anti-patternning jonli namunasi: BITTA klass — CRUD +
// biznes qoida (bonus hisoblash) + validatsiya — hammasini o'z ichiga
// oladi. Bu ISHLAYDI, lekin loyiha kattalashsa — bu klass "shishib"
// ketadi (o'nlab metod). Solishtiring: Middle-D/Junior-D loyihalaridagi
// CQRS/MediatR yechimi bilan — har operatsiya alohida, kichik Handler
// bo'lardi (docs 3.13-bo'lim).
public class EmployeeService : IEmployeeService
{
    private const decimal BonusRatePerYear = 0.1m;

    // FAQAT interfeysga bog'liq — konkret EmployeeRepository klassini
    // BusinessLogic loyihasi UMUMAN KO'RA OLMAYDI (u internal, DataAccess'da)!
    private readonly IEmployeeRepository _repository;

    public EmployeeService(IEmployeeRepository repository) => _repository = repository;

    public async Task<List<EmployeeDto>> GetAllAsync()
    {
        var employees = await _repository.GetAllAsync();
        return employees.Select(ToDto).ToList();
    }

    public async Task<EmployeeDto> GetByIdAsync(int id)
    {
        var employee = await _repository.GetByIdAsync(id)
            ?? throw new NotFoundException($"ID={id} bo'lgan xodim topilmadi");

        return ToDto(employee);
    }

    public async Task<EmployeeDto> CreateAsync(CreateEmployeeDto dto)
    {
        // === BIZNES QOIDA (validatsiya) — bu yer, BLL, shu yerga tegishli ===
        if (string.IsNullOrWhiteSpace(dto.FullName))
            throw new ArgumentException("Ism bo'sh bo'lishi mumkin emas");
        if (dto.BaseSalary <= 0)
            throw new ArgumentException("Maosh musbat bo'lishi kerak");

        var entity = new Employee
        {
            FullName = dto.FullName,
            Department = dto.Department,
            BaseSalary = dto.BaseSalary,
            YearsOfService = dto.YearsOfService
        };

        var created = await _repository.AddAsync(entity);
        return ToDto(created);
    }

    public async Task<EmployeeDto> UpdateAsync(int id, UpdateEmployeeDto dto)
    {
        var employee = await _repository.GetByIdAsync(id)
            ?? throw new NotFoundException($"ID={id} bo'lgan xodim topilmadi");

        employee.FullName = dto.FullName;
        employee.Department = dto.Department;
        employee.BaseSalary = dto.BaseSalary;
        employee.YearsOfService = dto.YearsOfService;

        await _repository.UpdateAsync(employee);
        return ToDto(employee);
    }

    public async Task DeleteAsync(int id)
    {
        var deleted = await _repository.DeleteAsync(id);
        if (!deleted) throw new NotFoundException($"ID={id} bo'lgan xodim topilmadi");
    }

    public async Task<decimal> CalculateBonusAsync(int id)
    {
        var employee = await _repository.GetByIdAsync(id)
            ?? throw new NotFoundException($"ID={id} bo'lgan xodim topilmadi");

        // === BIZNES QOIDA — docs 3.8-bo'limdagi aynan shu misol ===
        return employee.BaseSalary * BonusRatePerYear * employee.YearsOfService;
    }

    private static EmployeeDto ToDto(Employee e) =>
        new(e.Id, e.FullName, e.Department, e.BaseSalary, e.YearsOfService,
            e.BaseSalary * BonusRatePerYear * e.YearsOfService);
}
