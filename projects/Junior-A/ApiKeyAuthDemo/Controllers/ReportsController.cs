using ApiKeyAuthDemo.Auth;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

namespace ApiKeyAuthDemo.Controllers;

// Bu controller — HECH BIR demo klientda mavjud bo'lmagan
// "admin:reports" scope'ini talab qiladi. Shu tarzda: API Key TO'G'RI
// bo'lsa ham (autentifikatsiya OK), scope MOS KELMASA -> 403 Forbidden
// (401 EMAS!) — bu, RBAC/scope mavzusidagi 401 vs 403 farqining
// API Key kontekstidagi ko'rinishi.
[ApiController]
[Route("api/reports")]
[Authorize(AuthenticationSchemes = ApiKeyAuthenticationHandler.SchemeName, Policy = "AdminReportsScope")]
public class ReportsController : ControllerBase
{
    [HttpGet("monthly")]
    public IActionResult MonthlyReport()
        => Ok(new { report = "Oylik hisobot (faqat 'admin:reports' scope uchun)" });
}
