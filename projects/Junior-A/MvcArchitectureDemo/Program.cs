using MvcArchitectureDemo.Data;

var builder = WebApplication.CreateBuilder(args);

// AddControllersWithViews() — AddControllers()dan farqli, Razor View
// Engine'ni HAM yoqadi (docs 3.2-bo'lim: MVC vs Web API farqi).
builder.Services.AddControllersWithViews();
builder.Services.AddSingleton<IEmployeeStore, InMemoryEmployeeStore>();

var app = builder.Build();

if (!app.Environment.IsDevelopment())
{
    app.UseExceptionHandler("/Home/Error");
    app.UseHsts();
}

app.UseStaticFiles();
app.UseRouting();
app.UseAuthorization();

// Convention-based routing — {controller}/{action}/{id?} (docs 3.1-bo'lim).
// Attribute routing'dan farqli, HAR bir action uchun [Route] yozish shart emas.
app.MapControllerRoute(
    name: "default",
    pattern: "{controller=Home}/{action=Index}/{id?}");

app.Run();
