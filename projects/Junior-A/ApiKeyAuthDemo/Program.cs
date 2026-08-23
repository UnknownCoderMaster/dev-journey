using ApiKeyAuthDemo.Auth;
using ApiKeyAuthDemo.Services;
using Microsoft.AspNetCore.Authentication;
using Microsoft.OpenApi.Models;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();

// ============================================================
// SWAGGER — X-Api-Key uchun "Authorize" tugmasini yoqish
// ============================================================
builder.Services.AddSwaggerGen(options =>
{
    options.SwaggerDoc("v1", new OpenApiInfo
    {
        Title = "API Key Auth Demo",
        Version = "v1",
        Description = "docs/Junior-A/18-api-key-auth uchun amaliy sinov loyihasi. " +
                      "Demo kalit: ApiKeyAuthDemo.Services.InMemoryApiKeyValidator.PartnerXRawKey"
    });

    options.AddSecurityDefinition(ApiKeyAuthenticationHandler.SchemeName, new OpenApiSecurityScheme
    {
        Name = ApiKeyAuthenticationHandler.HeaderName,
        Type = SecuritySchemeType.ApiKey,
        In = ParameterLocation.Header,
        Description = "X-Api-Key header orqali yuboriladigan statik kalit"
    });

    options.AddSecurityRequirement(new OpenApiSecurityRequirement
    {
        {
            new OpenApiSecurityScheme
            {
                Reference = new OpenApiReference { Type = ReferenceType.SecurityScheme, Id = ApiKeyAuthenticationHandler.SchemeName }
            },
            Array.Empty<string>()
        }
    });
});

builder.Services.AddSingleton<IApiKeyValidator, InMemoryApiKeyValidator>();

// ============================================================
// AUTHENTICATION — bitta custom "ApiKey" scheme
// ============================================================
builder.Services.AddAuthentication(ApiKeyAuthenticationHandler.SchemeName)
    .AddScheme<AuthenticationSchemeOptions, ApiKeyAuthenticationHandler>(ApiKeyAuthenticationHandler.SchemeName, null);

// ============================================================
// AUTHORIZATION — scope-based policy'lar (401 vs 403 sinash uchun)
// ============================================================
builder.Services.AddAuthorization(options =>
{
    options.AddPolicy("WebhookPaymentScope", policy =>
        policy.RequireAuthenticatedUser().RequireClaim("scope", "webhook:payment"));

    options.AddPolicy("AdminReportsScope", policy =>
        policy.RequireAuthenticatedUser().RequireClaim("scope", "admin:reports"));
});

var app = builder.Build();

app.UseSwagger();
app.UseSwaggerUI();

app.UseAuthentication();
app.UseAuthorization();

app.MapControllers();

app.Run();
