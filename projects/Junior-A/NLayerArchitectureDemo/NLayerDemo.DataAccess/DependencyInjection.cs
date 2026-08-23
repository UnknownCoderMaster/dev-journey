using Microsoft.Extensions.DependencyInjection;

namespace NLayerDemo.DataAccess;

// PUBLIC "eshik" — DataAccess qatlamining yagona tashqariga ochiq
// ro'yxatdan o'tkazish nuqtasi. Ichkarida internal AppDbContext va
// EmployeeRepository'ni register qiladi — bu klasslarga tashqaridan
// to'g'ridan kirib bo'lmasa ham, DI Container ularni topa oladi,
// chunki bu kod ham DataAccess assembly'sining o'zida joylashgan.
public static class DependencyInjection
{
    public static IServiceCollection AddDataAccessLayer(this IServiceCollection services)
    {
        services.AddDbContext<AppDbContext>();
        services.AddScoped<IEmployeeRepository, EmployeeRepository>();
        return services;
    }
}
