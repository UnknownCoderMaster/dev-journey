using TaskFlow.Application.Entities;

namespace TaskFlow.Application.Contracts;

public interface ITokenService
{
    string GenerateAccessToken(User user);
    string GenerateRefreshToken();
    int? ValidateRefreshToken(string refreshToken);
}