using System.Security.Claims;
using System.Text.Encodings.Web;
using ApiKeyAuthDemo.Services;
using Microsoft.AspNetCore.Authentication;
using Microsoft.Extensions.Options;

namespace ApiKeyAuthDemo.Auth;

// docs/Junior-A/18-api-key-auth (3.3-bo'lim) dagi patternning
// TO'LIQ ISHLAYDIGAN implementatsiyasi.
public class ApiKeyAuthenticationHandler : AuthenticationHandler<AuthenticationSchemeOptions>
{
    public const string SchemeName = "ApiKey";
    public const string HeaderName = "X-Api-Key";

    private readonly IApiKeyValidator _validator;

    public ApiKeyAuthenticationHandler(
        IOptionsMonitor<AuthenticationSchemeOptions> options,
        ILoggerFactory logger,
        UrlEncoder encoder,
        IApiKeyValidator validator) : base(options, logger, encoder)
        => _validator = validator;

    protected override async Task<AuthenticateResult> HandleAuthenticateAsync()
    {
        if (!Request.Headers.TryGetValue(HeaderName, out var apiKeyHeader))
            return AuthenticateResult.Fail($"'{HeaderName}' header topilmadi");

        var apiKey = apiKeyHeader.ToString();
        if (string.IsNullOrWhiteSpace(apiKey))
            return AuthenticateResult.Fail("API Key bo'sh bo'lishi mumkin emas");

        var client = await _validator.ValidateAsync(apiKey);
        if (client is null)
            return AuthenticateResult.Fail("API Key yaroqsiz, faol emas yoki muddati o'tgan");

        var claims = new[]
        {
            new Claim(ClaimTypes.Name, client.Name),
            new Claim("scope", client.Scope),
            new Claim("client_id", client.Id.ToString())
        };

        var identity = new ClaimsIdentity(claims, Scheme.Name);
        var principal = new ClaimsPrincipal(identity);
        var ticket = new AuthenticationTicket(principal, Scheme.Name);

        return AuthenticateResult.Success(ticket);
    }

    protected override Task HandleChallengeAsync(AuthenticationProperties properties)
    {
        Response.StatusCode = StatusCodes.Status401Unauthorized;
        Response.Headers.Append("WWW-Authenticate", $"{SchemeName} realm=\"ApiKeyAuthDemo\"");
        return Task.CompletedTask;
    }

    // Autentifikatsiya MUVAFFAQIYATLI, lekin Policy (masalan scope) mos
    // kelmaganda chaqiriladi -> 403 Forbidden (401 EMAS!).
    protected override Task HandleForbiddenAsync(AuthenticationProperties properties)
    {
        Response.StatusCode = StatusCodes.Status403Forbidden;
        return Task.CompletedTask;
    }
}
