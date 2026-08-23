using System.Text;
using AuthBasicsDemo.Auth;
using AuthBasicsDemo.Services;
using Microsoft.AspNetCore.Authentication.Cookies;
using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.AspNetCore.Authentication;
using Microsoft.IdentityModel.Tokens;
using Microsoft.OpenApi.Models;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();

// ============================================================
// SWAGGER — Bearer VA Basic uchun "Authorize" tugmasini yoqish
// ============================================================
builder.Services.AddSwaggerGen(options =>
{
    options.SwaggerDoc("v1", new OpenApiInfo
    {
        Title = "Auth Basics Demo",
        Version = "v1",
        Description = "docs/Junior-A/17-auth-basics uchun amaliy sinov loyihasi"
    });

    options.AddSecurityDefinition(JwtBearerDefaults.AuthenticationScheme, new OpenApiSecurityScheme
    {
        Name = "Authorization",
        Type = SecuritySchemeType.Http,
        Scheme = "Bearer",
        BearerFormat = "JWT",
        In = ParameterLocation.Header,
        Description = "POST /api/auth/login orqali token oling, keyin shu yerga qo'ying (faqat token, 'Bearer ' prefiksisiz)."
    });

    options.AddSecurityDefinition(BasicAuthenticationHandler.SchemeName, new OpenApiSecurityScheme
    {
        Name = "Authorization",
        Type = SecuritySchemeType.Http,
        Scheme = "Basic",
        Description = "Username/parol: admin/Admin123! yoki orzibek/User123!"
    });

    options.AddSecurityRequirement(new OpenApiSecurityRequirement
    {
        {
            new OpenApiSecurityScheme { Reference = new OpenApiReference { Type = ReferenceType.SecurityScheme, Id = JwtBearerDefaults.AuthenticationScheme } },
            Array.Empty<string>()
        },
        {
            new OpenApiSecurityScheme { Reference = new OpenApiReference { Type = ReferenceType.SecurityScheme, Id = BasicAuthenticationHandler.SchemeName } },
            Array.Empty<string>()
        }
    });
});

builder.Services.AddSingleton<IUserStore, InMemoryUserStore>();
builder.Services.AddSingleton<TokenService>();

// ============================================================
// AUTHENTICATION — bir vaqtda 3 ta scheme: Bearer (JWT), Basic, Cookie
// ============================================================
builder.Services.AddAuthentication(options =>
{
    options.DefaultAuthenticateScheme = JwtBearerDefaults.AuthenticationScheme;
    options.DefaultChallengeScheme = JwtBearerDefaults.AuthenticationScheme;
})
.AddJwtBearer(options =>
{
    var jwtSection = builder.Configuration.GetSection("Jwt");
    options.TokenValidationParameters = new TokenValidationParameters
    {
        ValidateIssuer = true,
        ValidIssuer = jwtSection["Issuer"],
        ValidateAudience = true,
        ValidAudience = jwtSection["Audience"],
        ValidateIssuerSigningKey = true,
        IssuerSigningKey = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(jwtSection["SecretKey"]!)),
        ValidateLifetime = true,
        ClockSkew = TimeSpan.Zero
    };
})
.AddCookie(CookieAuthenticationDefaults.AuthenticationScheme, options =>
{
    options.Cookie.Name = "AuthBasicsDemo.Auth";
    options.ExpireTimeSpan = TimeSpan.FromHours(1);

    // Bu — Web API, HTML LOGIN sahifasiga REDIRECT emas, 401/403 QAYTARISHI kerak!
    options.Events.OnRedirectToLogin = context =>
    {
        context.Response.StatusCode = StatusCodes.Status401Unauthorized;
        return Task.CompletedTask;
    };
    options.Events.OnRedirectToAccessDenied = context =>
    {
        context.Response.StatusCode = StatusCodes.Status403Forbidden;
        return Task.CompletedTask;
    };
})
.AddScheme<AuthenticationSchemeOptions, BasicAuthenticationHandler>(BasicAuthenticationHandler.SchemeName, null);

// ============================================================
// AUTHORIZATION — Role-based policy (401 vs 403 sinash uchun)
// ============================================================
builder.Services.AddAuthorization(options =>
{
    options.AddPolicy("AdminOnly", policy => policy.RequireRole("Admin"));
});

var app = builder.Build();

app.UseSwagger();
app.UseSwaggerUI();

// ⚠️ TARTIB MUHIM: Authentication OLDIN, Authorization KEYIN!
app.UseAuthentication();
app.UseAuthorization();

app.MapControllers();

app.Run();
