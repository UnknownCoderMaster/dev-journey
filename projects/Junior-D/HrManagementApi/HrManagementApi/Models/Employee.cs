namespace HrManagementApi.Models;

public class Employee
{
    public int Id { get; set; }
    public required string FullName { get; set; }
    public DateOnly DateOfBirth { get; set; }
    public int PositionId { get; set; }
    public DateTime HiredAt { get; set; }
    public DateTime CreatedAt { get; set; }
    public DateTime? UpdatedAt { get; set; }
}