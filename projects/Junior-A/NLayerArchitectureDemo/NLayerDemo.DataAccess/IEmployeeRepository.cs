using NLayerDemo.DataAccess.Entities;

namespace NLayerDemo.DataAccess;

// PUBLIC — bu interfeys orqaligina BusinessLogic, DataAccess bilan "gaplashadi".
// Konkret EmployeeRepository klassi esa internal (pastga qarang).
public interface IEmployeeRepository
{
    Task<List<Employee>> GetAllAsync();
    Task<Employee?> GetByIdAsync(int id);
    Task<Employee> AddAsync(Employee employee);
    Task UpdateAsync(Employee employee);
    Task<bool> DeleteAsync(int id);
}
