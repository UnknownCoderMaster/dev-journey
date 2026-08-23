using AuthBasicsDemo.Models;

namespace AuthBasicsDemo.Services;

public interface IUserStore
{
    AppUser? FindByUsername(string username);
}
