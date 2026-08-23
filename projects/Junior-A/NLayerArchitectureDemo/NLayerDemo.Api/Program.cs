using Microsoft.OpenApi.Models;
using NLayerDemo.BusinessLogic;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddControllers();
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen(options =>
{
    options.SwaggerDoc("v1", new OpenApiInfo
    {
        Title = "N-Layer Architecture Demo",
        Version = "v1",
        Description = "docs/Junior-A/12-mvc-nlayer-architecture uchun amaliy sinov loyihasi. " +
                      "3 ta ALOHIDA loyiha: DataAccess -> BusinessLogic -> Api (bir yo'nalishda)."
    });
});

// ⚠️ Bitta qator — lekin uch qatlamning HAMMASINI (BLL + ICHIDAGI DAL)
// zanjir bo'ylab register qiladi. Api — buning orqasida nima borligini
// bilishi shart emas (Dependency Inversion amaliyoti).
builder.Services.AddBusinessLogicLayer();

var app = builder.Build();

app.UseSwagger();
app.UseSwaggerUI();

app.UseAuthorization();
app.MapControllers();

app.Run();
