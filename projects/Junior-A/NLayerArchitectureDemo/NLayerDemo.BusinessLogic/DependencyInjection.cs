using Microsoft.Extensions.DependencyInjection;
using NLayerDemo.DataAccess;

namespace NLayerDemo.BusinessLogic;

public static class DependencyInjection
{
    public static IServiceCollection AddBusinessLogicLayer(this IServiceCollection services)
    {
        // BLL — o'zining pastki qatlamini (DataAccess) "zanjir" sifatida ulaydi.
        // Api loyihasi FAQAT shu bitta metodni chaqiradi — DataAccess
        // haqida umuman bilishi shart emas!
        services.AddDataAccessLayer();
        services.AddScoped<IEmployeeService, EmployeeService>();
        return services;
    }
}
