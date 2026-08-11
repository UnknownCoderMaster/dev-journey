namespace DataStructuresDemo.Models;

public class Employee
{
    public int Id { get; set; }
    public string FullName { get; set; } = null!;
    public string Department { get; set; } = null!;

    public override string ToString() => $"[{Id}] {FullName} ({Department})";
}
