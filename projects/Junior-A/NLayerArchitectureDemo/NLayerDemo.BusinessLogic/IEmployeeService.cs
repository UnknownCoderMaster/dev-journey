using NLayerDemo.BusinessLogic.Dtos;

namespace NLayerDemo.BusinessLogic;

public interface IEmployeeService
{
    Task<List<EmployeeDto>> GetAllAsync();
    Task<EmployeeDto> GetByIdAsync(int id);
    Task<EmployeeDto> CreateAsync(CreateEmployeeDto dto);
    Task<EmployeeDto> UpdateAsync(int id, UpdateEmployeeDto dto);
    Task DeleteAsync(int id);
    Task<decimal> CalculateBonusAsync(int id);
}
