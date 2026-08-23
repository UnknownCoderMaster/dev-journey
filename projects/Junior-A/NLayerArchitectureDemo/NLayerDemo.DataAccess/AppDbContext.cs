using Microsoft.EntityFrameworkCore;
using NLayerDemo.DataAccess.Entities;

namespace NLayerDemo.DataAccess;

// internal — bu klass FAQAT DataAccess loyihasi ICHIDA ko'rinadi.
// BusinessLogic yoki Api loyihasi bu klassni hech qachon to'g'ridan
// ko'ra olmaydi (compile-time xato beradi) — Data Access qatlamining
// ichki implementatsiya tafsiloti shu tarzda "yashiriladi".
internal class AppDbContext : DbContext
{
    public DbSet<Employee> Employees => Set<Employee>();

    protected override void OnConfiguring(DbContextOptionsBuilder optionsBuilder)
        => optionsBuilder.UseInMemoryDatabase("NLayerDemoDb");

    public void Seed()
    {
        if (Employees.Any()) return;

        Employees.AddRange(
            new Employee { Id = 1, FullName = "Orzibek Toshmatov", Department = "IT", BaseSalary = 8_000_000, YearsOfService = 3 },
            new Employee { Id = 2, FullName = "Dilnoza Karimova", Department = "HR", BaseSalary = 6_000_000, YearsOfService = 1 },
            new Employee { Id = 3, FullName = "Aziz Yusupov", Department = "IT", BaseSalary = 7_500_000, YearsOfService = 5 }
        );
        SaveChanges();
    }
}
