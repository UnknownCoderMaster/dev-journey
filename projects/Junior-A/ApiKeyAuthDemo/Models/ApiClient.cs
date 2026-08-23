namespace ApiKeyAuthDemo.Models;

// DB'da SAQLANADIGAN yozuv — E'TIBOR BERING: RAW (asl) kalit HECH QACHON
// bu yerda YO'Q, faqat uning HASH'i (KeyHash) saqlanadi (parol kabi).
public class ApiClient
{
    public int Id { get; set; }
    public string Name { get; set; } = null!;
    public string KeyHash { get; set; } = null!;
    public string Scope { get; set; } = null!;
    public bool IsActive { get; set; } = true;
    public DateTime ExpiresAt { get; set; }
}
