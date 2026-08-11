using AutoMapperMapsterDemo.Models;

namespace AutoMapperMapsterDemo.Data;

public static class SeedData
{
    public static void Populate(AppDbContext context)
    {
        var it = new Department { Id = 1, Name = "IT bo'limi" };
        var hr = new Department { Id = 2, Name = "HR bo'limi" };
        context.Departments.AddRange(it, hr);

        context.Employees.AddRange(
            new Manager
            {
                Id = 1,
                FullName = "Diyorbek Toshmatov",
                BaseSalary = 8_000_000, // > 5,000,000 -> Conditional Mapping'da Bonus OLADI
                DepartmentId = it.Id,
                Department = it,
                TeamSize = 5
            },
            new Contractor
            {
                Id = 2,
                FullName = "Dilnoza Karimova",
                BaseSalary = 3_000_000, // <= 5,000,000 -> Bonus OLMAYDI
                DepartmentId = hr.Id,
                Department = hr,
                HourlyRate = 50_000,
                HoursWorked = 160
            },
            new Manager
            {
                Id = 3,
                FullName = "Aziz Yusupov",
                BaseSalary = 6_500_000, // > 5,000,000 -> Bonus OLADI
                DepartmentId = it.Id,
                Department = it,
                TeamSize = 3
            }
        );

        context.SaveChanges();
    }
}
