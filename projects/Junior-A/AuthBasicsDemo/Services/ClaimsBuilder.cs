using System.Security.Claims;
using AuthBasicsDemo.Models;

namespace AuthBasicsDemo.Services;

// Uchala autentifikatsiya usuli (Bearer, Basic, Cookie) UCHUN
// BIR XIL claims to'plamini generatsiya qiladi — shu tarzda /api/me/*
// endpointlari QAYSI usul ishlatilganidan qat'i nazar BIR XIL formatda javob beradi.
public static class ClaimsBuilder
{
    public static List<Claim> Build(AppUser user) => new()
    {
        new Claim(ClaimTypes.NameIdentifier, user.Id.ToString()),
        new Claim(ClaimTypes.Name, user.Username),
        new Claim(ClaimTypes.Role, user.Role)
    };
}
