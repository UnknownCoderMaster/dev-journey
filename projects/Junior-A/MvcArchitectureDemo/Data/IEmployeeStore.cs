using MvcArchitectureDemo.Models;

namespace MvcArchitectureDemo.Data;

// Bu — MVC'ning "Model" qatlamidagi ma'lumot manbai. Oddiy dars uchun
// XOTIRADA (Singleton) saqlanadi — haqiqiy loyihada bu EF Core DbContext
// bo'lardi (docs/12-mvc-nlayer-architecture'dagi N-Layer namunasiga qarang).
public interface IEmployeeStore
{
    List<Employee> GetAll();
    Employee? GetById(int id);
    Employee Add(Employee employee);
    bool Update(Employee employee);
    bool Delete(int id);
}
