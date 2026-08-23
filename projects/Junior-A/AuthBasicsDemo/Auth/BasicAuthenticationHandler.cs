using System.Net.Http.Headers;
using System.Security.Claims;
using System.Text;
using System.Text.Encodings.Web;
using AuthBasicsDemo.Services;
using Microsoft.AspNetCore.Authentication;
using Microsoft.Extensions.Options;

namespace AuthBasicsDemo.Auth;

// ASP.NET Core'da "Basic" scheme BUILT-IN EMAS — bu, HAR BIR
// Custom Authentication Handler qanday yozilishini o'rgatish uchun
// AYNI shu mavzuning ("Authentication turlari") amaliy namunasi.
public class BasicAuthenticationHandler : AuthenticationHandler<AuthenticationSchemeOptions>
{
    public const string SchemeName = "Basic";

    private readonly IUserStore _userStore;

    public BasicAuthenticationHandler(
        IOptionsMonitor<AuthenticationSchemeOptions> options,
        ILoggerFactory logger,
        UrlEncoder encoder,
        IUserStore userStore) : base(options, logger, encoder)
        => _userStore = userStore;

    protected override Task<AuthenticateResult> HandleAuthenticateAsync()
    {
        if (!Request.Headers.ContainsKey("Authorization"))
            return Task.FromResult(AuthenticateResult.Fail("Authorization header topilmadi"));

        AuthenticationHeaderValue headerValue;
        try
        {
            headerValue = AuthenticationHeaderValue.Parse(Request.Headers.Authorization.ToString());
        }
        catch (FormatException)
        {
            return Task.FromResult(AuthenticateResult.Fail("Authorization header formati noto'g'ri"));
        }

        if (!SchemeName.Equals(headerValue.Scheme, StringComparison.OrdinalIgnoreCase))
            return Task.FromResult(AuthenticateResult.Fail($"'{SchemeName}' scheme kutilgan edi"));

        string decoded;
        try
        {
            var bytes = Convert.FromBase64String(headerValue.Parameter ?? string.Empty);
            decoded = Encoding.UTF8.GetString(bytes);
        }
        catch (FormatException)
        {
            return Task.FromResult(AuthenticateResult.Fail("Base64 dekodlashda xato"));
        }

        // decoded formati: "username:password"
        var separatorIndex = decoded.IndexOf(':');
        if (separatorIndex < 0)
            return Task.FromResult(AuthenticateResult.Fail("username:password formatiga mos emas"));

        var username = decoded[..separatorIndex];
        var password = decoded[(separatorIndex + 1)..];

        var user = _userStore.FindByUsername(username);
        if (user is null || !BCrypt.Net.BCrypt.Verify(password, user.PasswordHash))
            return Task.FromResult(AuthenticateResult.Fail("Login yoki parol noto'g'ri"));

        var claims = ClaimsBuilder.Build(user);
        var identity = new ClaimsIdentity(claims, Scheme.Name);
        var principal = new ClaimsPrincipal(identity);
        var ticket = new AuthenticationTicket(principal, Scheme.Name);

        return Task.FromResult(AuthenticateResult.Success(ticket));
    }

    // Autentifikatsiya MUVAFFAQIYATSIZ bo'lganda — brauzer/Postman'ga
    // "Basic realm=..." header yuboriladi (bu — brauzerni LOGIN oynasini
    // ko'rsatishga undaydigan standart HTTP mexanizm).
    protected override Task HandleChallengeAsync(AuthenticationProperties properties)
    {
        Response.Headers.Append("WWW-Authenticate", $"{SchemeName} realm=\"AuthBasicsDemo\"");
        return base.HandleChallengeAsync(properties);
    }
}
