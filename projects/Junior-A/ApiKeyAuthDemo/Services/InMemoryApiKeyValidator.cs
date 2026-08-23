using System.Security.Cryptography;
using System.Text;
using ApiKeyAuthDemo.Models;

namespace ApiKeyAuthDemo.Services;

// ⚠️ FAQAT DEMO uchun — RAW (asl) kalitlar bu yerda "const" sifatida
// KO'RINADI, chunki sizga SINASH uchun ular KERAK. HAQIQIY loyihada RAW
// kalit — FAQAT klient uchun kalit YARATILGAN paytda, BIR MARTA
// ko'rsatiladi (masalan ekranda), va HECH QACHON qayta ko'rsatilmaydi —
// DB'da FAQAT HASH saqlanadi (docs/Junior-A/18-api-key-auth, 3.4-bo'lim).
public class InMemoryApiKeyValidator : IApiKeyValidator
{
    public const string PartnerXRawKey = "px_live_9F3kQlZ7mN2vRt8bXcW1sYdA4uEjHpLo";
    public const string ExpiredPartnerRawKey = "px_expired_1a2b3c4d5e6f7g8h9i0jklmno";

    private readonly List<ApiClient> _clients;

    public InMemoryApiKeyValidator()
    {
        _clients = new List<ApiClient>
        {
            new()
            {
                Id = 1,
                Name = "PartnerX (to'lov tizimi)",
                KeyHash = Hash(PartnerXRawKey),
                Scope = "webhook:payment",
                IsActive = true,
                ExpiresAt = DateTime.UtcNow.AddYears(1)
            },
            new()
            {
                Id = 2,
                Name = "Eski hamkor (muddati o'tgan)",
                KeyHash = Hash(ExpiredPartnerRawKey),
                Scope = "webhook:payment",
                IsActive = true,
                ExpiresAt = DateTime.UtcNow.AddDays(-1) // ⚠️ ATAYLAB o'tgan — Expiry sinovi uchun
            }
        };
    }

    public Task<ApiClient?> ValidateAsync(string apiKey)
    {
        var hash = Hash(apiKey);

        // Har bir shart — HAQIQIY loyihada MUHIM: hash MOS kelishi,
        // klient FAOL (IsActive) bo'lishi VA muddati O'TMAGAN bo'lishi kerak.
        var client = _clients.FirstOrDefault(c =>
            c.KeyHash == hash && c.IsActive && c.ExpiresAt > DateTime.UtcNow);

        return Task.FromResult(client);
    }

    private static string Hash(string value)
    {
        var bytes = SHA256.HashData(Encoding.UTF8.GetBytes(value));
        return Convert.ToHexString(bytes);
    }
}
