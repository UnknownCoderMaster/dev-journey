using HrManagementApi.DTOs;
using HrManagementApi.Models;

namespace HrManagementApi.Repositories;

public interface IEmployeeRepository
{
    Task<List<EmployeeDto>> GetAllAsync();
    Task<EmployeeDto?> GetByIdAsync(int id);
    Task<int> CreateAsync(Employee employee);
    Task<bool> UpdateAsync(Employee employee);
    Task<bool> DeleteAsync(int id);
}