using ApiKeyAuthDemo.Auth;
using ApiKeyAuthDemo.Models;
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;

namespace ApiKeyAuthDemo.Controllers;

// docs/Junior-A/18-api-key-auth (4-bo'lim) dagi "webhook, third-party
// integration" real misolining ishlaydigan versiyasi.
[ApiController]
[Route("api/webhooks")]
[Authorize(AuthenticationSchemes = ApiKeyAuthenticationHandler.SchemeName)]
public class WebhookController : ControllerBase
{
    /// <summary>
    /// FAQAT "webhook:payment" scope'iga ega API Key bilan chaqirish mumkin.
    /// </summary>
    [HttpPost("payment-notification")]
    [Authorize(Policy = "WebhookPaymentScope")]
    public IActionResult HandlePaymentNotification(PaymentNotificationDto dto)
    {
        // Bu yerga FAQAT to'g'ri API Key VA to'g'ri scope bilan kelgan so'rov yetib keladi.
        return Ok(new
        {
            message = "To'lov bildirishnomasi qabul qilindi",
            processedBy = User.Identity?.Name,
            scope = User.FindFirst("scope")?.Value,
            payload = dto
        });
    }

    /// <summary>
    /// Faqat API Key TO'G'RI ekanligini (scope'siz) tekshirish uchun — "whoami".
    /// </summary>
    [HttpGet("whoami")]
    public IActionResult WhoAmI()
    {
        return Ok(new
        {
            IsAuthenticated = User.Identity?.IsAuthenticated,
            ClientName = User.Identity?.Name,
            Claims = User.Claims.Select(c => new { c.Type, c.Value })
        });
    }
}
