using AutoMapperMapsterDemo.Models;
using Microsoft.EntityFrameworkCore;

namespace AutoMapperMapsterDemo.Data;

public class AppDbContext : DbContext
{
    public DbSet<Employee> Employees => Set<Employee>();
    public DbSet<Department> Departments => Set<Department>();

    protected override void OnConfiguring(DbContextOptionsBuilder optionsBuilder)
        // InMemory provayder — haqiqiy PostgreSQL o'rniga, DARS uchun qulay
        // (qo'shimcha DB sozlash shart emas, lekin IQueryable/ProjectTo() xuddi
        // haqiqiy EF Core provayderdagidek ishlaydi).
        => optionsBuilder.UseInMemoryDatabase("AutoMapperDemoDb");

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        // TPH (Table-per-Hierarchy) — Manager va Contractor bitta "Employees"
        // jadvalida, "EmployeeType" ustuni orqali tur aniqlanadi.
        // Batafsil: docs/Middle-D/23-ef-core-hierarchy
        modelBuilder.Entity<Employee>()
            .HasDiscriminator<string>("EmployeeType")
            .HasValue<Manager>("Manager")
            .HasValue<Contractor>("Contractor");
    }
}
