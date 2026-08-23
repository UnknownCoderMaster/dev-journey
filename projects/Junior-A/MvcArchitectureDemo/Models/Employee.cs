using System.ComponentModel.DataAnnotations;

namespace MvcArchitectureDemo.Models;

// MVC'dagi "Model" — ma'lumot + (oddiy) biznes/validatsiya qoidalarini
// o'z ichiga oladi. Bu klass — HAM Controller, HAM View tomonidan
// (@model Employee orqali) ISHLATILADI.
public class Employee
{
    public int Id { get; set; }

    [Required(ErrorMessage = "Ism majburiy")]
    [Display(Name = "To'liq ism")]
    public string FullName { get; set; } = null!;

    [Required(ErrorMessage = "Bo'lim majburiy")]
    [Display(Name = "Bo'lim")]
    public string Department { get; set; } = null!;

    [Range(0, double.MaxValue, ErrorMessage = "Maosh manfiy bo'lishi mumkin emas")]
    [Display(Name = "Maosh")]
    public decimal Salary { get; set; }

    [Range(0, 50, ErrorMessage = "Staj 0-50 oralig'ida bo'lishi kerak")]
    [Display(Name = "Ish staji (yil)")]
    public int YearsOfService { get; set; }
}
