namespace AutoMapperMapsterDemo.Dtos;

// Bazaviy DTO — barcha xodim turlari uchun UMUMIY maydonlar.
public class EmployeeDto
{
    public int Id { get; set; }
    public string FullName { get; set; } = null!;
    public string DepartmentName { get; set; } = null!;

    // Conditional Mapping demosi uchun — FAQAT shart bajarilsa qiymat oladi (aks holda null).
    public decimal? Bonus { get; set; }
}
