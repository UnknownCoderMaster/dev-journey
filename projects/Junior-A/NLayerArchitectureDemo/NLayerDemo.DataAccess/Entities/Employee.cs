namespace NLayerDemo.DataAccess.Entities;

// DAL darajasidagi entity — DB jadvaliga to'g'ridan mos keladi.
public class Employee
{
    public int Id { get; set; }
    public string FullName { get; set; } = null!;
    public string Department { get; set; } = null!;
    public decimal BaseSalary { get; set; }
    public int YearsOfService { get; set; }
}
