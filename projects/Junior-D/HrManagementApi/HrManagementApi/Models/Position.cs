namespace HrManagementApi.Models;

public class Position
{
    public int Id { get; set; }
    public required string Name { get; set; }
    public int DepartmentId { get; set; }
    public DateTime CreatedAt { get; set; }
    public DateTime? UpdatedAt { get; set; }
}