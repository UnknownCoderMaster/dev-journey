namespace AuthBasicsDemo.Models;

// DEMO uchun soddalashtirilgan foydalanuvchi modeli.
// Haqiqiy loyihada — Employee/User jadvali, registratsiya oqimi va h.k. bo'ladi.
public class AppUser
{
    public int Id { get; set; }
    public string Username { get; set; } = null!;
    public string PasswordHash { get; set; } = null!;
    public string Role { get; set; } = null!;
}
