using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

namespace AuthBasicsDemo.Controllers;

// 401 vs 403'ni JONLI sinash uchun:
//   1) Hech qanday token bermasdan chaqiring        -> 401 Unauthorized ("kim ekaning bilmayman")
//   2) 'orzibek' (Employee) tokeni bilan chaqiring    -> 403 Forbidden ("kim ekaning bilaman, ruxsating yo'q")
//   3) 'admin' (Admin) tokeni bilan chaqiring         -> 200 OK
[ApiController]
[Route("api/admin")]
public class AdminController : ControllerBase
{
    [HttpGet("salary-report")]
    [Authorize(Policy = "AdminOnly")] // Program.cs'da: RequireRole("Admin")
    public IActionResult GetSalaryReport()
    {
        return Ok(new
        {
            report = "Maxfiy moliyaviy hisobot",
            generatedFor = User.Identity?.Name,
            note = "Bu javobni faqat 'Admin' rolidagi foydalanuvchi ko'ra oladi."
        });
    }
}
