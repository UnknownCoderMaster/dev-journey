using ApiKeyAuthDemo.Models;

namespace ApiKeyAuthDemo.Services;

public interface IApiKeyValidator
{
    Task<ApiClient?> ValidateAsync(string apiKey);
}
