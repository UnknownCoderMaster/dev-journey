using AuthBasicsDemo.Auth;
using Microsoft.AspNetCore.Authentication.Cookies;
using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

namespace AuthBasicsDemo.Controllers;

// Bitta vazifa — UCHTA endpoint: har biri FAQAT bitta autentifikatsiya
// usulini QABUL qiladi ([Authorize(AuthenticationSchemes = ...)]). Shu
// tarzda "aynan qaysi usul ishlayotgani" har doim ANIQ ko'rinadi.
[ApiController]
[Route("api/me")]
public class MeController : ControllerBase
{
    [HttpGet("bearer")]
    [Authorize(AuthenticationSchemes = JwtBearerDefaults.AuthenticationScheme)]
    public IActionResult MeViaBearer() => Ok(BuildResponse("Bearer (JWT)"));

    [HttpGet("basic")]
    [Authorize(AuthenticationSchemes = BasicAuthenticationHandler.SchemeName)]
    public IActionResult MeViaBasic() => Ok(BuildResponse("Basic"));

    [HttpGet("cookie")]
    [Authorize(AuthenticationSchemes = CookieAuthenticationDefaults.AuthenticationScheme)]
    public IActionResult MeViaCookie() => Ok(BuildResponse("Cookie"));

    private object BuildResponse(string scheme) => new
    {
        AuthenticationScheme = scheme,
        IsAuthenticated = User.Identity?.IsAuthenticated,
        Name = User.Identity?.Name,
        Claims = User.Claims.Select(c => new { c.Type, c.Value })
    };
}
