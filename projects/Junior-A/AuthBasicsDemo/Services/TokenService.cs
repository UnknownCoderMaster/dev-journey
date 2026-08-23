using System.IdentityModel.Tokens.Jwt;
using System.Text;
using AuthBasicsDemo.Models;
using Microsoft.IdentityModel.Tokens;

namespace AuthBasicsDemo.Services;

public class TokenService
{
    private readonly IConfiguration _config;

    public TokenService(IConfiguration config) => _config = config;

    public string GenerateToken(AppUser user)
    {
        var claims = ClaimsBuilder.Build(user);

        var key = new SymmetricSecurityKey(Encoding.UTF8.GetBytes(_config["Jwt:SecretKey"]!));
        var credentials = new SigningCredentials(key, SecurityAlgorithms.HmacSha256);

        var token = new JwtSecurityToken(
            issuer: _config["Jwt:Issuer"],
            audience: _config["Jwt:Audience"],
            claims: claims,
            expires: DateTime.UtcNow.AddMinutes(30), // Qasddan QISQA — Access Token amaliyotini his qilish uchun
            signingCredentials: credentials);

        return new JwtSecurityTokenHandler().WriteToken(token);
    }
}
