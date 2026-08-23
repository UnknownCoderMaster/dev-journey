namespace NLayerDemo.BusinessLogic.Dtos;

// BLL/Presentation qatlamlari uchun DTO — DAL'ning Entity'sidan MUSTAQIL
// (Entity o'zgarsa ham, bu — API "shartnomasi" sifatida barqaror qolishi mumkin).
public record EmployeeDto(
    int Id,
    string FullName,
    string Department,
    decimal BaseSalary,
    int YearsOfService,
    decimal AnnualBonus);
