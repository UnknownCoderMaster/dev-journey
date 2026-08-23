using MvcArchitectureDemo.Models;

namespace MvcArchitectureDemo.Data;

public class InMemoryEmployeeStore : IEmployeeStore
{
    private readonly List<Employee> _employees = new()
    {
        new Employee { Id = 1, FullName = "Orzibek Toshmatov", Department = "IT", Salary = 8_000_000, YearsOfService = 3 },
        new Employee { Id = 2, FullName = "Dilnoza Karimova", Department = "HR", Salary = 6_000_000, YearsOfService = 1 }
    };

    private int _nextId = 3;

    public List<Employee> GetAll() => _employees;

    public Employee? GetById(int id) => _employees.FirstOrDefault(e => e.Id == id);

    public Employee Add(Employee employee)
    {
        employee.Id = _nextId++;
        _employees.Add(employee);
        return employee;
    }

    public bool Update(Employee employee)
    {
        var existing = GetById(employee.Id);
        if (existing is null) return false;

        existing.FullName = employee.FullName;
        existing.Department = employee.Department;
        existing.Salary = employee.Salary;
        existing.YearsOfService = employee.YearsOfService;
        return true;
    }

    public bool Delete(int id)
    {
        var existing = GetById(id);
        return existing is not null && _employees.Remove(existing);
    }
}
