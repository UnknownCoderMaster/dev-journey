using Microsoft.EntityFrameworkCore;
using NLayerDemo.DataAccess.Entities;

namespace NLayerDemo.DataAccess;

// internal — FAQAT "SQL/EF Core orqali QANDAY saqlanishi" tafsilotini
// o'z ichiga oladi. Tashqi loyihalar (BusinessLogic, Api) FAQAT
// IEmployeeRepository interfeysini ko'radi, bu KONKRET klassni EMAS —
// docs/12-mvc-nlayer-architecture (3.6-bo'lim)dagi "Dependency direction"
// qoidasi shu tarzda COMPILER darajasida MAJBURLANADI.
internal class EmployeeRepository : IEmployeeRepository
{
    private readonly AppDbContext _context;

    public EmployeeRepository(AppDbContext context)
    {
        _context = context;
        _context.Seed();
    }

    public async Task<List<Employee>> GetAllAsync()
        => await _context.Employees.AsNoTracking().OrderBy(e => e.Id).ToListAsync();

    public async Task<Employee?> GetByIdAsync(int id)
        => await _context.Employees.FindAsync(id);

    public async Task<Employee> AddAsync(Employee employee)
    {
        employee.Id = await _context.Employees.AnyAsync()
            ? await _context.Employees.MaxAsync(e => e.Id) + 1
            : 1;

        _context.Employees.Add(employee);
        await _context.SaveChangesAsync();
        return employee;
    }

    public async Task UpdateAsync(Employee employee)
    {
        _context.Employees.Update(employee);
        await _context.SaveChangesAsync();
    }

    public async Task<bool> DeleteAsync(int id)
    {
        var employee = await _context.Employees.FindAsync(id);
        if (employee is null) return false;

        _context.Employees.Remove(employee);
        await _context.SaveChangesAsync();
        return true;
    }
}
