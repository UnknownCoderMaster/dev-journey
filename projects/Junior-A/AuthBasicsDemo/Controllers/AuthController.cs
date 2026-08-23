using System.Security.Claims;
using AuthBasicsDemo.Models;
using AuthBasicsDemo.Services;
using Microsoft.AspNetCore.Authentication;
using Microsoft.AspNetCore.Authentication.Cookies;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

namespace AuthBasicsDemo.Controllers;

[ApiController]
[Route("api/auth")]
[AllowAnonymous] // Login/logout — HAR DOIM anonim (autentifikatsiyasiz) kirish mumkin bo'lishi SHART
public class AuthController : ControllerBase
{
    private readonly IUserStore _userStore;
    private readonly TokenService _tokenService;

    public AuthController(IUserStore userStore, TokenService tokenService)
    {
        _userStore = userStore;
        _tokenService = tokenService;
    }

    /// <summary>
    /// Password-based autentifikatsiya -> muvaffaqiyatli bo'lsa JWT (Bearer) token qaytaradi.
    /// Sinash uchun: admin/Admin123! yoki orzibek/User123!
    /// </summary>
    [HttpPost("login")]
    public IActionResult Login(LoginRequest request)
    {
        var user = _userStore.FindByUsername(request.Username);
        if (user is null || !BCrypt.Net.BCrypt.Verify(request.Password, user.PasswordHash))
            return Unauthorized(new { message = "Login yoki parol noto'g'ri" });

        var token = _tokenService.GenerateToken(user);
        return Ok(new
        {
            accessToken = token,
            expiresInMinutes = 30,
            message = "Bu tokenni Swagger'dagi 'Authorize' tugmasi orqali Bearer sifatida qo'ying"
        });
    }

    /// <summary>
    /// Password-based autentifikatsiya -> muvaffaqiyatli bo'lsa Cookie o'rnatadi (session-uslub).
    /// Swagger UI orqali emas, curl/Postman orqali (cookie jar bilan) sinash TAVSIYA ETILADI.
    /// </summary>
    [HttpPost("login-cookie")]
    public async Task<IActionResult> LoginCookie(LoginRequest request)
    {
        var user = _userStore.FindByUsername(request.Username);
        if (user is null || !BCrypt.Net.BCrypt.Verify(request.Password, user.PasswordHash))
            return Unauthorized(new { message = "Login yoki parol noto'g'ri" });

        var claims = ClaimsBuilder.Build(user);
        var identity = new ClaimsIdentity(claims, CookieAuthenticationDefaults.AuthenticationScheme);
        var principal = new ClaimsPrincipal(identity);

        await HttpContext.SignInAsync(CookieAuthenticationDefaults.AuthenticationScheme, principal, new AuthenticationProperties
        {
            IsPersistent = false,
            ExpiresUtc = DateTimeOffset.UtcNow.AddHours(1)
        });

        return Ok(new { message = $"'{user.Username}' cookie orqali tizimga kirdi. Endi /api/me/cookie'ni chaqirib ko'ring." });
    }

    [HttpPost("logout-cookie")]
    public async Task<IActionResult> LogoutCookie()
    {
        await HttpContext.SignOutAsync(CookieAuthenticationDefaults.AuthenticationScheme);
        return Ok(new { message = "Cookie sessiyasi tugatildi" });
    }
}
