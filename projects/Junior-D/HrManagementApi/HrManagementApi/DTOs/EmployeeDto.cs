namespace HrManagementApi.DTOs;

public class EmployeeDto
{
    public int Id { get; set; }
    public required string FullName { get; set; }
    public DateOnly DateOfBirth { get; set; }
    public int PositionId { get; set; }
    public required string PositionName { get; set; }
    public int DepartmentId { get; set; }
    public required string DepartmentName { get; set; }
    public DateTime HiredAt { get; set; }
    public DateTime CreatedAt { get; set; }
    public DateTime? UpdatedAt { get; set; }
}