namespace AutoMapperMapsterDemo.Models;

// Bazaviy klass — TPH (Table-per-Hierarchy) inheritance uchun ASOS.
// Manager va Contractor — shu klassdan MEROS OLADI (Mapping Inheritance
// demosida AutoMapper'ning Include/IncludeBase mexanizmini ko'rsatish uchun).
public abstract class Employee
{
    public int Id { get; set; }
    public string FullName { get; set; } = null!;
    public decimal BaseSalary { get; set; }

    public int DepartmentId { get; set; }
    public Department? Department { get; set; }
}
