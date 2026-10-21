using Hangfire;
using Hangfire.PostgreSql;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using TaskFlow.Application.Contracts;
using TaskFlow.Infrastructure.Auth;
using TaskFlow.Infrastructure.Caching;
using TaskFlow.Infrastructure.Jobs;
using TaskFlow.Infrastructure.Messaging;
using TaskFlow.Infrastructure.Persistence;
using TaskFlow.Infrastructure.Storage;

namespace TaskFlow.Infrastructure;

public static class DependencyInjection
{
    public static IServiceCollection AddInfrastructure(
        this IServiceCollection services,
        IConfiguration config)
    {
        var connectionString = config.GetConnectionString("DefaultConnection")!;
        var hangfireConnectionString = config.GetConnectionString("HangfireConnection")!;

        // EF Core
        services.AddDbContext<AppDbContext>(options =>
            options.UseNpgsql(connectionString));

        // IMemoryCache
        services.AddMemoryCache();
        services.AddSingleton<ICacheService, MemoryCacheService>();

        // Minio
        services.AddSingleton<IMinioService, MinioService>();

        // RabbitMQ
        services.AddSingleton<IRabbitMQPublisher, RabbitMQPublisher>();

        // JWT TokenService
        services.AddScoped<ITokenService, TokenService>();

        // Hangfire
        services.AddHangfire(hf => hf
            .SetDataCompatibilityLevel(CompatibilityLevel.Version_180)
            .UseSimpleAssemblyNameTypeSerializer()
            .UseRecommendedSerializerSettings()
            .UsePostgreSqlStorage(
                opt => opt.UseNpgsqlConnection(hangfireConnectionString),
                new PostgreSqlStorageOptions
                {
                    // Hangfire jadvallari alohida schema da turadi —
                    // biznes jadvallar bilan aralashmaydi
                    SchemaName = "hangfire",

                    // Jadvallarni birinchi ishga tushishda avtomatik yaratish
                    PrepareSchemaIfNecessary = true,

                    // Yangi job ni qanchalik tez-tez tekshirish
                    QueuePollInterval = TimeSpan.FromSeconds(15),

                    // Job bajarilmay qolsa, qancha vaqtdan keyin boshqasiga beriladi
                    InvisibilityTimeout = TimeSpan.FromMinutes(30),

                    DistributedLockTimeout = TimeSpan.FromMinutes(1)
                }));

        // Worker sonini cheklash — default ProcessorCount * 5 juda ko'p
        services.AddHangfireServer(options =>
        {
            options.WorkerCount = config.GetValue<int>("Hangfire:WorkerCount", 5);
        });

        services.AddScoped<DeadlineReminderJob>();

        return services;
    }
}