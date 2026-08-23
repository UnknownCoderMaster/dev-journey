using AuthBasicsDemo.Models;

namespace AuthBasicsDemo.Services;

// ⚠️ FAQAT DEMO uchun — foydalanuvchilar XOTIRADA, parollar KOD ICHIDA
// (aniq matn sifatida emas — pastda BCrypt bilan HASH qilinadi).
// Haqiqiy loyihada bu — DB jadvali (Employees) va Registratsiya oqimi bo'lardi.
public class InMemoryUserStore : IUserStore
{
    private readonly List<AppUser> _users;

    public InMemoryUserStore()
    {
        _users = new List<AppUser>
        {
            new()
            {
                Id = 1,
                Username = "admin",
                PasswordHash = BCrypt.Net.BCrypt.HashPassword("Admin123!"),
                Role = "Admin"
            },
            new()
            {
                Id = 2,
                Username = "orzibek",
                PasswordHash = BCrypt.Net.BCrypt.HashPassword("User123!"),
                Role = "Employee"
            }
        };
    }

    public AppUser? FindByUsername(string username)
        => _users.FirstOrDefault(u => u.Username.Equals(username, StringComparison.OrdinalIgnoreCase));
}
