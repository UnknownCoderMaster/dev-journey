# TaskFlow API — To'liq Qurilish Ko'rsatmasi

## Loyiha haqida
- **Stack:** ASP.NET Core 8, EF Core, PostgreSQL, RabbitMQ, Minio, Hangfire, SignalR, JWT
- **Maqsad:** Middle D texnologiyalarini amalda o'rganish
- **Repo joyi:** `C:\ExtraWork\dev-journey\projects\Middle-D\TaskFlowApi\`

---

## BOSQICH 1 — Loyiha skeleton va Docker

### 1.1 Solution yaratish

```bash
cd C:\ExtraWork\dev-journey\projects\Middle-D
dotnet new sln -n TaskFlowApi
dotnet new webapi -n TaskFlow.API
dotnet new classlib -n TaskFlow.Application
dotnet new classlib -n TaskFlow.Infrastructure
dotnet new xunit -n TaskFlow.Tests

dotnet sln add TaskFlow.API
dotnet sln add TaskFlow.Application
dotnet sln add TaskFlow.Infrastructure
dotnet sln add TaskFlow.Tests

# Reference lar
cd TaskFlow.API
dotnet add reference ../TaskFlow.Application
dotnet add reference ../TaskFlow.Infrastructure

cd ../TaskFlow.Infrastructure
dotnet add reference ../TaskFlow.Application

cd ../TaskFlow.Tests
dotnet add reference ../TaskFlow.Application
dotnet add reference ../TaskFlow.Infrastructure
```

### 1.2 NuGet paketlar

**TaskFlow.API:**
```bash
cd TaskFlow.API
dotnet add package Microsoft.AspNetCore.Authentication.JwtBearer
dotnet add package Swashbuckle.AspNetCore
dotnet add package MediatR
dotnet add package MediatR.Extensions.Microsoft.DependencyInjection
dotnet add package Hangfire.AspNetCore
dotnet add package Hangfire.PostgreSql
dotnet add package Microsoft.AspNetCore.SignalR
```

**TaskFlow.Infrastructure:**
```bash
cd TaskFlow.Infrastructure
dotnet add package Microsoft.EntityFrameworkCore
dotnet add package Npgsql.EntityFrameworkCore.PostgreSQL
dotnet add package RabbitMQ.Client
dotnet add package Minio
dotnet add package Microsoft.Extensions.Caching.Memory
dotnet add package Microsoft.AspNetCore.SignalR.Core
dotnet add package System.IdentityModel.Tokens.Jwt
dotnet add package BCrypt.Net-Next
```

**TaskFlow.Tests:**
```bash
cd TaskFlow.Tests
dotnet add package NSubstitute
dotnet add package FluentAssertions
dotnet add package Microsoft.EntityFrameworkCore.InMemory
```

### 1.3 docker-compose.yml

`C:\ExtraWork\dev-journey\projects\Middle-D\TaskFlowApi\` papkasida yarating:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15
    container_name: taskflow_postgres
    environment:
      POSTGRES_DB: taskflow_db
      POSTGRES_USER: taskflow_user
      POSTGRES_PASSWORD: taskflow_pass
    ports:
      - "5433:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - taskflow_network

  rabbitmq:
    image: rabbitmq:3-management
    container_name: taskflow_rabbitmq
    environment:
      RABBITMQ_DEFAULT_USER: taskflow_user
      RABBITMQ_DEFAULT_PASS: taskflow_pass
    ports:
      - "5672:5672"
      - "15672:15672"   # Management UI: http://localhost:15672
    volumes:
      - rabbitmq_data:/var/lib/rabbitmq
    networks:
      - taskflow_network

  minio:
    image: quay.io/minio/minio
    container_name: taskflow_minio
    command: server /data --console-address ":9001"
    environment:
      MINIO_ROOT_USER: taskflow_user
      MINIO_ROOT_PASSWORD: taskflow_pass123
    ports:
      - "9000:9000"
      - "9001:9001"   # Console UI: http://localhost:9001
    volumes:
      - minio_data:/data
    networks:
      - taskflow_network

volumes:
  postgres_data:
  rabbitmq_data:
  minio_data:

networks:
  taskflow_network:
    driver: bridge
```

### 1.4 Konteynerlarni ishga tushirish

```bash
cd C:\ExtraWork\dev-journey\projects\Middle-D\TaskFlowApi
docker-compose up -d

# Tekshirish
docker ps
# postgres, rabbitmq, minio — hammasi running bo'lishi kerak
```

---

## BOSQICH 2 — Domain va ma'lumotlar bazasi

### 2.1 Papka tuzilmasi

```
TaskFlow.Application/
├── Contracts/
│   ├── IMinioService.cs
│   ├── IRabbitMQPublisher.cs
│   ├── ICacheService.cs
│   └── ITokenService.cs
├── DTOs/
│   ├── Auth/
│   │   ├── LoginRequest.cs
│   │   ├── RegisterRequest.cs
│   │   └── TokenResponse.cs
│   ├── Board/
│   │   ├── CreateBoardRequest.cs
│   │   └── BoardDto.cs
│   ├── Card/
│   │   ├── CreateCardRequest.cs
│   │   ├── UpdateCardRequest.cs
│   │   └── CardDto.cs
│   └── Comment/
│       ├── CreateCommentRequest.cs
│       └── CommentDto.cs
└── Common/
    └── Result.cs

TaskFlow.Infrastructure/
├── Persistence/
│   ├── Entities/
│   │   ├── User.cs
│   │   ├── Board.cs
│   │   ├── Card.cs
│   │   ├── Comment.cs
│   │   └── Attachment.cs
│   ├── AppDbContext.cs
│   └── Migrations/
├── Messaging/
│   ├── RabbitMQPublisher.cs
│   └── RabbitMQConsumer.cs
├── Storage/
│   └── MinioService.cs
├── Caching/
│   └── MemoryCacheService.cs
├── Jobs/
│   ├── DeadlineReminderJob.cs
│   └── CleanupJob.cs
├── Auth/
│   └── TokenService.cs
└── DependencyInjection.cs

TaskFlow.API/
├── Controllers/
│   ├── AuthController.cs
│   ├── BoardsController.cs
│   ├── CardsController.cs
│   ├── CommentsController.cs
│   └── AttachmentsController.cs
├── Hubs/
│   └── TaskHub.cs
├── Middlewares/
│   └── ExceptionMiddleware.cs
├── appsettings.json
└── Program.cs
```

### 2.2 Entity lar

**TaskFlow.Infrastructure/Persistence/Entities/User.cs:**
```csharp
namespace TaskFlow.Infrastructure.Persistence.Entities;

public class User
{
    public int Id { get; set; }
    public string FullName { get; set; } = null!;
    public string Email { get; set; } = null!;
    public string PasswordHash { get; set; } = null!;
    public string Role { get; set; } = "Member"; // Admin, Member
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;

    public ICollection<Board> OwnedBoards { get; set; } = new List<Board>();
    public ICollection<Card> AssignedCards { get; set; } = new List<Card>();
}
```

**TaskFlow.Infrastructure/Persistence/Entities/Board.cs:**
```csharp
namespace TaskFlow.Infrastructure.Persistence.Entities;

public class Board
{
    public int Id { get; set; }
    public string Name { get; set; } = null!;
    public string? Description { get; set; }
    public int OwnerId { get; set; }
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;

    public User Owner { get; set; } = null!;
    public ICollection<Card> Cards { get; set; } = new List<Card>();
}
```

**TaskFlow.Infrastructure/Persistence/Entities/Card.cs:**
```csharp
namespace TaskFlow.Infrastructure.Persistence.Entities;

public enum CardStatus { Todo, InProgress, Done }

public class Card
{
    public int Id { get; set; }
    public string Title { get; set; } = null!;
    public string? Description { get; set; }
    public CardStatus Status { get; set; } = CardStatus.Todo;
    public DateTime? Deadline { get; set; }
    public int BoardId { get; set; }
    public int? AssigneeId { get; set; }
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    public DateTime UpdatedAt { get; set; } = DateTime.UtcNow;

    public Board Board { get; set; } = null!;
    public User? Assignee { get; set; }
    public ICollection<Comment> Comments { get; set; } = new List<Comment>();
    public ICollection<Attachment> Attachments { get; set; } = new List<Attachment>();
}
```

**TaskFlow.Infrastructure/Persistence/Entities/Comment.cs:**
```csharp
namespace TaskFlow.Infrastructure.Persistence.Entities;

public class Comment
{
    public int Id { get; set; }
    public string Content { get; set; } = null!;
    public int CardId { get; set; }
    public int UserId { get; set; }
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;

    public Card Card { get; set; } = null!;
    public User User { get; set; } = null!;
}
```

**TaskFlow.Infrastructure/Persistence/Entities/Attachment.cs:**
```csharp
namespace TaskFlow.Infrastructure.Persistence.Entities;

public class Attachment
{
    public int Id { get; set; }
    public string FileName { get; set; } = null!;
    public string MinioPath { get; set; } = null!;
    public long FileSize { get; set; }
    public int CardId { get; set; }
    public int UploadedBy { get; set; }
    public DateTime UploadedAt { get; set; } = DateTime.UtcNow;

    public Card Card { get; set; } = null!;
}
```

### 2.3 AppDbContext

**TaskFlow.Infrastructure/Persistence/AppDbContext.cs:**
```csharp
using Microsoft.EntityFrameworkCore;
using TaskFlow.Infrastructure.Persistence.Entities;

namespace TaskFlow.Infrastructure.Persistence;

public class AppDbContext : DbContext
{
    public AppDbContext(DbContextOptions<AppDbContext> options) : base(options) { }

    public DbSet<User> Users => Set<User>();
    public DbSet<Board> Boards => Set<Board>();
    public DbSet<Card> Cards => Set<Card>();
    public DbSet<Comment> Comments => Set<Comment>();
    public DbSet<Attachment> Attachments => Set<Attachment>();

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        // User
        modelBuilder.Entity<User>(e =>
        {
            e.HasKey(x => x.Id);
            e.HasIndex(x => x.Email).IsUnique();
            e.Property(x => x.Email).HasMaxLength(256);
            e.Property(x => x.FullName).HasMaxLength(256);
            e.Property(x => x.Role).HasDefaultValue("Member");
        });

        // Board
        modelBuilder.Entity<Board>(e =>
        {
            e.HasKey(x => x.Id);
            e.Property(x => x.Name).HasMaxLength(256);
            e.HasOne(x => x.Owner)
             .WithMany(x => x.OwnedBoards)
             .HasForeignKey(x => x.OwnerId)
             .OnDelete(DeleteBehavior.Restrict);
        });

        // Card
        modelBuilder.Entity<Card>(e =>
        {
            e.HasKey(x => x.Id);
            e.Property(x => x.Title).HasMaxLength(512);
            e.Property(x => x.Status)
             .HasConversion<string>()
             .HasDefaultValue(CardStatus.Todo);
            e.HasOne(x => x.Board)
             .WithMany(x => x.Cards)
             .HasForeignKey(x => x.BoardId)
             .OnDelete(DeleteBehavior.Cascade);
            e.HasOne(x => x.Assignee)
             .WithMany(x => x.AssignedCards)
             .HasForeignKey(x => x.AssigneeId)
             .OnDelete(DeleteBehavior.SetNull);
        });

        // Comment
        modelBuilder.Entity<Comment>(e =>
        {
            e.HasKey(x => x.Id);
            e.HasOne(x => x.Card)
             .WithMany(x => x.Comments)
             .HasForeignKey(x => x.CardId)
             .OnDelete(DeleteBehavior.Cascade);
        });

        // Attachment
        modelBuilder.Entity<Attachment>(e =>
        {
            e.HasKey(x => x.Id);
            e.HasOne(x => x.Card)
             .WithMany(x => x.Attachments)
             .HasForeignKey(x => x.CardId)
             .OnDelete(DeleteBehavior.Cascade);
        });
    }
}
```

### 2.4 Migration va baza yaratish

```bash
cd TaskFlow.API
dotnet add package Microsoft.EntityFrameworkCore.Design

dotnet ef migrations add InitialCreate --project ../TaskFlow.Infrastructure --startup-project .
dotnet ef database update --project ../TaskFlow.Infrastructure --startup-project .
```

---

## BOSQICH 3 — JWT Auth

### 3.1 appsettings.json

```json
{
  "ConnectionStrings": {
    "DefaultConnection": "Host=localhost;Port=5433;Database=taskflow_db;Username=taskflow_user;Password=taskflow_pass"
  },
  "Jwt": {
    "SecretKey": "taskflow-super-secret-key-minimum-32-characters!!",
    "Issuer": "TaskFlowApi",
    "Audience": "TaskFlowClient",
    "AccessTokenExpireMinutes": 60,
    "RefreshTokenExpireDays": 7
  },
  "RabbitMQ": {
    "Host": "localhost",
    "Port": 5672,
    "Username": "taskflow_user",
    "Password": "taskflow_pass",
    "ExchangeName": "taskflow_exchange"
  },
  "Minio": {
    "Endpoint": "localhost:9000",
    "AccessKey": "taskflow_user",
    "SecretKey": "taskflow_pass123",
    "BucketName": "taskflow-files",
    "UseSSL": false
  },
  "Hangfire": {
    "DashboardPath": "/hangfire"
  }
}
```

### 3.2 Kontraktlar

**TaskFlow.Application/Contracts/ITokenService.cs:**
```csharp
using TaskFlow.Infrastructure.Persistence.Entities;

namespace TaskFlow.Application.Contracts;

public interface ITokenService
{
    string GenerateAccessToken(User user);
    string GenerateRefreshToken();
    int? ValidateRefreshToken(string refreshToken);
}
```

**TaskFlow.Application/Contracts/ICacheService.cs:**
```csharp
namespace TaskFlow.Application.Contracts;

public interface ICacheService
{
    T? Get<T>(string key);
    void Set<T>(string key, T value, TimeSpan expiration);
    void Remove(string key);
}
```

**TaskFlow.Application/Contracts/IRabbitMQPublisher.cs:**
```csharp
namespace TaskFlow.Application.Contracts;

public interface IRabbitMQPublisher
{
    void Publish<T>(string routingKey, T message);
}
```

**TaskFlow.Application/Contracts/IMinioService.cs:**
```csharp
namespace TaskFlow.Application.Contracts;

public interface IMinioService
{
    Task<string> UploadFileAsync(Stream fileStream, string fileName, string contentType);
    Task<string> GetFileUrlAsync(string objectName);
    Task DeleteFileAsync(string objectName);
}
```

### 3.3 TokenService

**TaskFlow.Infrastructure/Auth/TokenService.cs:**
```csharp
using System.IdentityModel.Tokens.Jwt;
using System.Security.Claims;
using System.Security.Cryptography;
using System.Text;
using Microsoft.Extensions.Configuration;
using Microsoft.IdentityModel.Tokens;
using TaskFlow.Application.Contracts;
using TaskFlow.Infrastructure.Persistence.Entities;

namespace TaskFlow.Infrastructure.Auth;

public class TokenService : ITokenService
{
    private readonly IConfiguration _config;

    public TokenService(IConfiguration config)
    {
        _config = config;
    }

    public string GenerateAccessToken(User user)
    {
        var key = new SymmetricSecurityKey(
            Encoding.UTF8.GetBytes(_config["Jwt:SecretKey"]!));

        var credentials = new SigningCredentials(key, SecurityAlgorithms.HmacSha256);

        var claims = new[]
        {
            new Claim(ClaimTypes.NameIdentifier, user.Id.ToString()),
            new Claim(ClaimTypes.Email, user.Email),
            new Claim(ClaimTypes.Name, user.FullName),
            new Claim(ClaimTypes.Role, user.Role)
        };

        var token = new JwtSecurityToken(
            issuer: _config["Jwt:Issuer"],
            audience: _config["Jwt:Audience"],
            claims: claims,
            expires: DateTime.UtcNow.AddMinutes(
                int.Parse(_config["Jwt:AccessTokenExpireMinutes"]!)),
            signingCredentials: credentials
        );

        return new JwtSecurityTokenHandler().WriteToken(token);
    }

    public string GenerateRefreshToken()
    {
        return Convert.ToBase64String(RandomNumberGenerator.GetBytes(64));
    }

    public int? ValidateRefreshToken(string refreshToken)
    {
        // Oddiy implementatsiya — keyinchalik DB ga saqlash mumkin
        // Hozir faqat JWT dan user ID ni chiqaramiz
        return null;
    }
}
```

### 3.4 DTOs

**TaskFlow.Application/DTOs/Auth/LoginRequest.cs:**
```csharp
using System.ComponentModel.DataAnnotations;

namespace TaskFlow.Application.DTOs.Auth;

public class LoginRequest
{
    [Required, EmailAddress]
    public string Email { get; set; } = null!;

    [Required, MinLength(6)]
    public string Password { get; set; } = null!;
}
```

**TaskFlow.Application/DTOs/Auth/RegisterRequest.cs:**
```csharp
using System.ComponentModel.DataAnnotations;

namespace TaskFlow.Application.DTOs.Auth;

public class RegisterRequest
{
    [Required, MaxLength(256)]
    public string FullName { get; set; } = null!;

    [Required, EmailAddress]
    public string Email { get; set; } = null!;

    [Required, MinLength(6)]
    public string Password { get; set; } = null!;
}
```

**TaskFlow.Application/DTOs/Auth/TokenResponse.cs:**
```csharp
namespace TaskFlow.Application.DTOs.Auth;

public class TokenResponse
{
    public string AccessToken { get; set; } = null!;
    public string RefreshToken { get; set; } = null!;
    public DateTime ExpiresAt { get; set; }
}
```

### 3.5 AuthController

**TaskFlow.API/Controllers/AuthController.cs:**
```csharp
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using TaskFlow.Application.Contracts;
using TaskFlow.Application.DTOs.Auth;
using TaskFlow.Infrastructure.Persistence;
using TaskFlow.Infrastructure.Persistence.Entities;
using BCrypt.Net;

namespace TaskFlow.API.Controllers;

[ApiController]
[Route("api/[controller]")]
public class AuthController : ControllerBase
{
    private readonly AppDbContext _context;
    private readonly ITokenService _tokenService;

    public AuthController(AppDbContext context, ITokenService tokenService)
    {
        _context = context;
        _tokenService = tokenService;
    }

    [HttpPost("register")]
    public async Task<IActionResult> Register([FromBody] RegisterRequest request)
    {
        if (await _context.Users.AnyAsync(u => u.Email == request.Email))
            return Conflict(new { message = "Bu email allaqachon ro'yxatdan o'tgan" });

        var user = new User
        {
            FullName = request.FullName,
            Email = request.Email,
            PasswordHash = BCrypt.Net.BCrypt.HashPassword(request.Password)
        };

        _context.Users.Add(user);
        await _context.SaveChangesAsync();

        return Ok(new { message = "Muvaffaqiyatli ro'yxatdan o'tildi", userId = user.Id });
    }

    [HttpPost("login")]
    public async Task<ActionResult<TokenResponse>> Login([FromBody] LoginRequest request)
    {
        var user = await _context.Users
            .FirstOrDefaultAsync(u => u.Email == request.Email);

        if (user is null || !BCrypt.Net.BCrypt.Verify(request.Password, user.PasswordHash))
            return Unauthorized(new { message = "Email yoki parol noto'g'ri" });

        var accessToken = _tokenService.GenerateAccessToken(user);
        var refreshToken = _tokenService.GenerateRefreshToken();

        return Ok(new TokenResponse
        {
            AccessToken = accessToken,
            RefreshToken = refreshToken,
            ExpiresAt = DateTime.UtcNow.AddHours(1)
        });
    }
}
```

---

## BOSQICH 4 — Infrastructure servislar

### 4.1 MemoryCacheService

**TaskFlow.Infrastructure/Caching/MemoryCacheService.cs:**
```csharp
using Microsoft.Extensions.Caching.Memory;
using TaskFlow.Application.Contracts;

namespace TaskFlow.Infrastructure.Caching;

public class MemoryCacheService : ICacheService
{
    private readonly IMemoryCache _cache;

    public MemoryCacheService(IMemoryCache cache)
    {
        _cache = cache;
    }

    public T? Get<T>(string key)
    {
        _cache.TryGetValue(key, out T? value);
        return value;
    }

    public void Set<T>(string key, T value, TimeSpan expiration)
    {
        var options = new MemoryCacheEntryOptions
        {
            AbsoluteExpirationRelativeToNow = expiration
        };
        _cache.Set(key, value, options);
    }

    public void Remove(string key)
    {
        _cache.Remove(key);
    }
}
```

### 4.2 MinioService

**TaskFlow.Infrastructure/Storage/MinioService.cs:**
```csharp
using Microsoft.Extensions.Configuration;
using Minio;
using Minio.DataModel.Args;
using TaskFlow.Application.Contracts;

namespace TaskFlow.Infrastructure.Storage;

public class MinioService : IMinioService
{
    private readonly IMinioClient _minioClient;
    private readonly string _bucketName;

    public MinioService(IConfiguration config)
    {
        _bucketName = config["Minio:BucketName"]!;
        _minioClient = new MinioClient()
            .WithEndpoint(config["Minio:Endpoint"])
            .WithCredentials(config["Minio:AccessKey"], config["Minio:SecretKey"])
            .WithSSL(bool.Parse(config["Minio:UseSSL"] ?? "false"))
            .Build();

        EnsureBucketExistsAsync().GetAwaiter().GetResult();
    }

    private async Task EnsureBucketExistsAsync()
    {
        var exists = await _minioClient.BucketExistsAsync(
            new BucketExistsArgs().WithBucket(_bucketName));

        if (!exists)
        {
            await _minioClient.MakeBucketAsync(
                new MakeBucketArgs().WithBucket(_bucketName));
        }
    }

    public async Task<string> UploadFileAsync(Stream fileStream, string fileName, string contentType)
    {
        var objectName = $"{Guid.NewGuid()}-{fileName}";

        await _minioClient.PutObjectAsync(new PutObjectArgs()
            .WithBucket(_bucketName)
            .WithObject(objectName)
            .WithStreamData(fileStream)
            .WithObjectSize(fileStream.Length)
            .WithContentType(contentType));

        return objectName;
    }

    public async Task<string> GetFileUrlAsync(string objectName)
    {
        return await _minioClient.PresignedGetObjectAsync(
            new PresignedGetObjectArgs()
                .WithBucket(_bucketName)
                .WithObject(objectName)
                .WithExpiry(60 * 60)); // 1 soat
    }

    public async Task DeleteFileAsync(string objectName)
    {
        await _minioClient.RemoveObjectAsync(
            new RemoveObjectArgs()
                .WithBucket(_bucketName)
                .WithObject(objectName));
    }
}
```

### 4.3 RabbitMQPublisher

**TaskFlow.Infrastructure/Messaging/RabbitMQPublisher.cs:**
```csharp
using System.Text;
using System.Text.Json;
using Microsoft.Extensions.Configuration;
using RabbitMQ.Client;
using TaskFlow.Application.Contracts;

namespace TaskFlow.Infrastructure.Messaging;

public class RabbitMQPublisher : IRabbitMQPublisher, IDisposable
{
    private readonly IConnection _connection;
    private readonly IModel _channel;
    private readonly string _exchangeName;

    public RabbitMQPublisher(IConfiguration config)
    {
        _exchangeName = config["RabbitMQ:ExchangeName"]!;

        var factory = new ConnectionFactory
        {
            HostName = config["RabbitMQ:Host"],
            Port = int.Parse(config["RabbitMQ:Port"]!),
            UserName = config["RabbitMQ:Username"],
            Password = config["RabbitMQ:Password"]
        };

        _connection = factory.CreateConnection();
        _channel = _connection.CreateModel();

        _channel.ExchangeDeclare(
            exchange: _exchangeName,
            type: ExchangeType.Topic,
            durable: true);
    }

    public void Publish<T>(string routingKey, T message)
    {
        var json = JsonSerializer.Serialize(message);
        var body = Encoding.UTF8.GetBytes(json);

        var properties = _channel.CreateBasicProperties();
        properties.Persistent = true;
        properties.ContentType = "application/json";

        _channel.BasicPublish(
            exchange: _exchangeName,
            routingKey: routingKey,
            basicProperties: properties,
            body: body);
    }

    public void Dispose()
    {
        _channel?.Dispose();
        _connection?.Dispose();
    }
}
```

### 4.4 SignalR Hub

**TaskFlow.API/Hubs/TaskHub.cs:**
```csharp
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.SignalR;

namespace TaskFlow.API.Hubs;

[Authorize]
public class TaskHub : Hub
{
    // Foydalanuvchi board ga qo'shiladi
    public async Task JoinBoard(string boardId)
    {
        await Groups.AddToGroupAsync(Context.ConnectionId, $"board-{boardId}");
    }

    // Foydalanuvchi board dan chiqadi
    public async Task LeaveBoard(string boardId)
    {
        await Groups.RemoveFromGroupAsync(Context.ConnectionId, $"board-{boardId}");
    }
}
```

### 4.5 Hangfire Jobs

**TaskFlow.Infrastructure/Jobs/DeadlineReminderJob.cs:**
```csharp
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Logging;
using TaskFlow.Application.Contracts;
using TaskFlow.Infrastructure.Persistence;

namespace TaskFlow.Infrastructure.Jobs;

public class DeadlineReminderJob
{
    private readonly AppDbContext _context;
    private readonly IRabbitMQPublisher _publisher;
    private readonly ILogger<DeadlineReminderJob> _logger;

    public DeadlineReminderJob(
        AppDbContext context,
        IRabbitMQPublisher publisher,
        ILogger<DeadlineReminderJob> logger)
    {
        _context = context;
        _publisher = publisher;
        _logger = logger;
    }

    public async Task ExecuteAsync()
    {
        var tomorrow = DateTime.UtcNow.AddDays(1);

        var urgentCards = await _context.Cards
            .Include(c => c.Assignee)
            .Where(c => c.Deadline.HasValue
                && c.Deadline.Value.Date == tomorrow.Date
                && c.Status != Persistence.Entities.CardStatus.Done)
            .ToListAsync();

        foreach (var card in urgentCards)
        {
            _logger.LogInformation(
                "Deadline yaqinlashmoqda: Card {CardId} - {Title}", card.Id, card.Title);

            _publisher.Publish("card.deadline.reminder", new
            {
                CardId = card.Id,
                Title = card.Title,
                Deadline = card.Deadline,
                AssigneeEmail = card.Assignee?.Email
            });
        }

        _logger.LogInformation("{Count} ta karta uchun eslatma yuborildi", urgentCards.Count);
    }
}
```

---

## BOSQICH 5 — DI va Program.cs

### 5.1 DependencyInjection.cs

**TaskFlow.Infrastructure/DependencyInjection.cs:**
```csharp
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
        // EF Core
        services.AddDbContext<AppDbContext>(options =>
            options.UseNpgsql(config.GetConnectionString("DefaultConnection")));

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
            .UsePostgreSqlStorage(config.GetConnectionString("DefaultConnection")));

        services.AddHangfireServer();
        services.AddScoped<DeadlineReminderJob>();

        return services;
    }
}
```

### 5.2 Program.cs

**TaskFlow.API/Program.cs:**
```csharp
using System.Text;
using Hangfire;
using Microsoft.AspNetCore.Authentication.JwtBearer;
using Microsoft.IdentityModel.Tokens;
using Microsoft.OpenApi.Models;
using TaskFlow.Infrastructure;
using TaskFlow.Infrastructure.Jobs;
using TaskFlow.API.Hubs;

var builder = WebApplication.CreateBuilder(args);

// Controllers
builder.Services.AddControllers();

// Swagger
builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen(c =>
{
    c.SwaggerDoc("v1", new OpenApiInfo { Title = "TaskFlow API", Version = "v1" });

    // Swagger da JWT token kiritish imkoniyati
    c.AddSecurityDefinition("Bearer", new OpenApiSecurityScheme
    {
        Description = "JWT token kiriting: Bearer {token}",
        Name = "Authorization",
        In = ParameterLocation.Header,
        Type = SecuritySchemeType.ApiKey,
        Scheme = "Bearer"
    });

    c.AddSecurityRequirement(new OpenApiSecurityRequirement
    {
        {
            new OpenApiSecurityScheme
            {
                Reference = new OpenApiReference
                {
                    Type = ReferenceType.SecurityScheme,
                    Id = "Bearer"
                }
            },
            Array.Empty<string>()
        }
    });
});

// JWT Authentication
builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddJwtBearer(options =>
    {
        options.TokenValidationParameters = new TokenValidationParameters
        {
            ValidateIssuer = true,
            ValidateAudience = true,
            ValidateLifetime = true,
            ValidateIssuerSigningKey = true,
            ValidIssuer = builder.Configuration["Jwt:Issuer"],
            ValidAudience = builder.Configuration["Jwt:Audience"],
            IssuerSigningKey = new SymmetricSecurityKey(
                Encoding.UTF8.GetBytes(builder.Configuration["Jwt:SecretKey"]!))
        };

        // SignalR uchun token query string dan olish
        options.Events = new JwtBearerEvents
        {
            OnMessageReceived = context =>
            {
                var accessToken = context.Request.Query["access_token"];
                var path = context.HttpContext.Request.Path;
                if (!string.IsNullOrEmpty(accessToken) && path.StartsWithSegments("/hubs"))
                {
                    context.Token = accessToken;
                }
                return Task.CompletedTask;
            }
        };
    });

builder.Services.AddAuthorization();

// SignalR
builder.Services.AddSignalR();

// Infrastructure
builder.Services.AddInfrastructure(builder.Configuration);

var app = builder.Build();

// Middleware
if (app.Environment.IsDevelopment())
{
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.UseHttpsRedirection();
app.UseAuthentication();
app.UseAuthorization();

app.MapControllers();

// SignalR Hub
app.MapHub<TaskHub>("/hubs/tasks");

// Hangfire Dashboard
app.UseHangfireDashboard("/hangfire");

// Hangfire Cron Jobs
RecurringJob.AddOrUpdate<DeadlineReminderJob>(
    "deadline-reminder",
    job => job.ExecuteAsync(),
    "0 8 * * *"); // Har kuni soat 08:00 da

app.Run();
```

---

## BOSQICH 6 — CRUD Controllerlar

### 6.1 BoardsController

**TaskFlow.API/Controllers/BoardsController.cs:**
```csharp
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.SignalR;
using Microsoft.EntityFrameworkCore;
using System.Security.Claims;
using TaskFlow.Application.Contracts;
using TaskFlow.Infrastructure.Persistence;
using TaskFlow.Infrastructure.Persistence.Entities;
using TaskFlow.API.Hubs;

namespace TaskFlow.API.Controllers;

[Authorize]
[ApiController]
[Route("api/[controller]")]
public class BoardsController : ControllerBase
{
    private readonly AppDbContext _context;
    private readonly ICacheService _cache;
    private readonly IRabbitMQPublisher _publisher;
    private readonly IHubContext<TaskHub> _hubContext;

    public BoardsController(
        AppDbContext context,
        ICacheService cache,
        IRabbitMQPublisher publisher,
        IHubContext<TaskHub> hubContext)
    {
        _context = context;
        _cache = cache;
        _publisher = publisher;
        _hubContext = hubContext;
    }

    private int CurrentUserId =>
        int.Parse(User.FindFirstValue(ClaimTypes.NameIdentifier)!);

    [HttpGet]
    public async Task<IActionResult> GetAll()
    {
        const string cacheKey = "boards_list";

        var cached = _cache.Get<List<object>>(cacheKey);
        if (cached is not null)
            return Ok(cached);

        var boards = await _context.Boards
            .Include(b => b.Owner)
            .Select(b => new
            {
                b.Id,
                b.Name,
                b.Description,
                Owner = b.Owner.FullName,
                CardsCount = b.Cards.Count,
                b.CreatedAt
            })
            .ToListAsync();

        _cache.Set(cacheKey, boards, TimeSpan.FromMinutes(5));

        return Ok(boards);
    }

    [HttpGet("{id}")]
    public async Task<IActionResult> GetById(int id)
    {
        var board = await _context.Boards
            .Include(b => b.Owner)
            .Include(b => b.Cards)
                .ThenInclude(c => c.Assignee)
            .FirstOrDefaultAsync(b => b.Id == id);

        if (board is null)
            return NotFound();

        return Ok(board);
    }

    [HttpPost]
    public async Task<IActionResult> Create([FromBody] CreateBoardRequest request)
    {
        var board = new Board
        {
            Name = request.Name,
            Description = request.Description,
            OwnerId = CurrentUserId
        };

        _context.Boards.Add(board);
        await _context.SaveChangesAsync();

        // Cache ni tozalash
        _cache.Remove("boards_list");

        // RabbitMQ ga hodisa yuborish
        _publisher.Publish("board.created", new
        {
            BoardId = board.Id,
            Name = board.Name,
            CreatedBy = CurrentUserId
        });

        return CreatedAtAction(nameof(GetById), new { id = board.Id }, board);
    }

    [HttpDelete("{id}")]
    public async Task<IActionResult> Delete(int id)
    {
        var board = await _context.Boards.FindAsync(id);
        if (board is null) return NotFound();
        if (board.OwnerId != CurrentUserId) return Forbid();

        _context.Boards.Remove(board);
        await _context.SaveChangesAsync();

        _cache.Remove("boards_list");

        return NoContent();
    }
}

public record CreateBoardRequest(string Name, string? Description);
```

### 6.2 CardsController

**TaskFlow.API/Controllers/CardsController.cs:**
```csharp
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.SignalR;
using Microsoft.EntityFrameworkCore;
using System.Security.Claims;
using TaskFlow.Application.Contracts;
using TaskFlow.Infrastructure.Persistence;
using TaskFlow.Infrastructure.Persistence.Entities;
using TaskFlow.API.Hubs;

namespace TaskFlow.API.Controllers;

[Authorize]
[ApiController]
[Route("api/boards/{boardId}/cards")]
public class CardsController : ControllerBase
{
    private readonly AppDbContext _context;
    private readonly IRabbitMQPublisher _publisher;
    private readonly IHubContext<TaskHub> _hubContext;

    public CardsController(
        AppDbContext context,
        IRabbitMQPublisher publisher,
        IHubContext<TaskHub> hubContext)
    {
        _context = context;
        _publisher = publisher;
        _hubContext = hubContext;
    }

    private int CurrentUserId =>
        int.Parse(User.FindFirstValue(ClaimTypes.NameIdentifier)!);

    [HttpGet]
    public async Task<IActionResult> GetAll(int boardId)
    {
        var cards = await _context.Cards
            .Where(c => c.BoardId == boardId)
            .Include(c => c.Assignee)
            .Select(c => new
            {
                c.Id,
                c.Title,
                c.Description,
                c.Status,
                c.Deadline,
                Assignee = c.Assignee == null ? null : c.Assignee.FullName,
                CommentsCount = c.Comments.Count,
                AttachmentsCount = c.Attachments.Count,
                c.CreatedAt
            })
            .OrderByDescending(c => c.CreatedAt)
            .ToListAsync();

        return Ok(cards);
    }

    [HttpPost]
    public async Task<IActionResult> Create(int boardId, [FromBody] CreateCardRequest request)
    {
        var boardExists = await _context.Boards.AnyAsync(b => b.Id == boardId);
        if (!boardExists) return NotFound("Board topilmadi");

        var card = new Card
        {
            Title = request.Title,
            Description = request.Description,
            Deadline = request.Deadline,
            AssigneeId = request.AssigneeId,
            BoardId = boardId
        };

        _context.Cards.Add(card);
        await _context.SaveChangesAsync();

        // RabbitMQ — yangi karta hodisasi
        _publisher.Publish("card.created", new
        {
            CardId = card.Id,
            Title = card.Title,
            BoardId = boardId,
            CreatedBy = CurrentUserId
        });

        // SignalR — board dagi barchaga real-time xabar
        await _hubContext.Clients
            .Group($"board-{boardId}")
            .SendAsync("CardCreated", new { card.Id, card.Title, card.Status });

        return CreatedAtAction(nameof(GetAll), new { boardId }, card);
    }

    [HttpPatch("{cardId}/status")]
    public async Task<IActionResult> UpdateStatus(
        int boardId, int cardId, [FromBody] UpdateCardStatusRequest request)
    {
        var card = await _context.Cards
            .FirstOrDefaultAsync(c => c.Id == cardId && c.BoardId == boardId);

        if (card is null) return NotFound();

        card.Status = request.Status;
        card.UpdatedAt = DateTime.UtcNow;
        await _context.SaveChangesAsync();

        // SignalR — status o'zgardi
        await _hubContext.Clients
            .Group($"board-{boardId}")
            .SendAsync("CardStatusUpdated", new
            {
                CardId = cardId,
                NewStatus = request.Status.ToString()
            });

        // RabbitMQ — hodisa
        _publisher.Publish("card.status.updated", new
        {
            CardId = cardId,
            Status = request.Status.ToString(),
            UpdatedBy = CurrentUserId
        });

        return Ok(new { message = "Status yangilandi", status = request.Status });
    }

    [HttpDelete("{cardId}")]
    public async Task<IActionResult> Delete(int boardId, int cardId)
    {
        var card = await _context.Cards
            .FirstOrDefaultAsync(c => c.Id == cardId && c.BoardId == boardId);

        if (card is null) return NotFound();

        _context.Cards.Remove(card);
        await _context.SaveChangesAsync();

        await _hubContext.Clients
            .Group($"board-{boardId}")
            .SendAsync("CardDeleted", new { CardId = cardId });

        return NoContent();
    }
}

public record CreateCardRequest(
    string Title,
    string? Description,
    DateTime? Deadline,
    int? AssigneeId);

public record UpdateCardStatusRequest(CardStatus Status);
```

### 6.3 AttachmentsController

**TaskFlow.API/Controllers/AttachmentsController.cs:**
```csharp
using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using System.Security.Claims;
using TaskFlow.Application.Contracts;
using TaskFlow.Infrastructure.Persistence;
using TaskFlow.Infrastructure.Persistence.Entities;

namespace TaskFlow.API.Controllers;

[Authorize]
[ApiController]
[Route("api/cards/{cardId}/attachments")]
public class AttachmentsController : ControllerBase
{
    private readonly AppDbContext _context;
    private readonly IMinioService _minioService;

    public AttachmentsController(AppDbContext context, IMinioService minioService)
    {
        _context = context;
        _minioService = minioService;
    }

    private int CurrentUserId =>
        int.Parse(User.FindFirstValue(ClaimTypes.NameIdentifier)!);

    [HttpPost]
    public async Task<IActionResult> Upload(int cardId, IFormFile file)
    {
        if (file.Length == 0)
            return BadRequest("Fayl bo'sh");

        if (file.Length > 10 * 1024 * 1024) // 10MB limit
            return BadRequest("Fayl hajmi 10MB dan oshmasligi kerak");

        var cardExists = await _context.Cards.AnyAsync(c => c.Id == cardId);
        if (!cardExists) return NotFound("Karta topilmadi");

        using var stream = file.OpenReadStream();
        var objectName = await _minioService.UploadFileAsync(
            stream, file.FileName, file.ContentType);

        var attachment = new Attachment
        {
            FileName = file.FileName,
            MinioPath = objectName,
            FileSize = file.Length,
            CardId = cardId,
            UploadedBy = CurrentUserId
        };

        _context.Attachments.Add(attachment);
        await _context.SaveChangesAsync();

        return Ok(new
        {
            attachment.Id,
            attachment.FileName,
            attachment.FileSize,
            attachment.UploadedAt
        });
    }

    [HttpGet("{attachmentId}/url")]
    public async Task<IActionResult> GetDownloadUrl(int cardId, int attachmentId)
    {
        var attachment = await _context.Attachments
            .FirstOrDefaultAsync(a => a.Id == attachmentId && a.CardId == cardId);

        if (attachment is null) return NotFound();

        var url = await _minioService.GetFileUrlAsync(attachment.MinioPath);
        return Ok(new { url, expiresIn = "1 soat" });
    }

    [HttpDelete("{attachmentId}")]
    public async Task<IActionResult> Delete(int cardId, int attachmentId)
    {
        var attachment = await _context.Attachments
            .FirstOrDefaultAsync(a => a.Id == attachmentId && a.CardId == cardId);

        if (attachment is null) return NotFound();

        await _minioService.DeleteFileAsync(attachment.MinioPath);

        _context.Attachments.Remove(attachment);
        await _context.SaveChangesAsync();

        return NoContent();
    }
}
```

---

## BOSQICH 7 — Testing (NSubstitute)

**TaskFlow.Tests/Unit/BoardServiceTests.cs:**
```csharp
using Microsoft.EntityFrameworkCore;
using NSubstitute;
using TaskFlow.Application.Contracts;
using TaskFlow.Infrastructure.Persistence;
using TaskFlow.Infrastructure.Persistence.Entities;
using Xunit;

namespace TaskFlow.Tests.Unit;

public class BoardServiceTests
{
    private AppDbContext CreateInMemoryContext()
    {
        var options = new DbContextOptionsBuilder<AppDbContext>()
            .UseInMemoryDatabase(databaseName: Guid.NewGuid().ToString())
            .Options;
        return new AppDbContext(options);
    }

    [Fact]
    public void Publish_ShouldBeCalled_WhenBoardCreated()
    {
        // Arrange
        var publisher = Substitute.For<IRabbitMQPublisher>();

        // Act
        publisher.Publish("board.created", new { BoardId = 1, Name = "Test Board" });

        // Assert
        publisher.Received(1).Publish(
            Arg.Is<string>(r => r == "board.created"),
            Arg.Any<object>());
    }

    [Fact]
    public async Task GetBoards_ShouldReturnCachedData_WhenCacheExists()
    {
        // Arrange
        var cache = Substitute.For<ICacheService>();
        var expectedBoards = new List<object> { new { Id = 1, Name = "Board 1" } };
        cache.Get<List<object>>("boards_list").Returns(expectedBoards);

        // Act
        var result = cache.Get<List<object>>("boards_list");

        // Assert
        Assert.NotNull(result);
        Assert.Single(result);
    }

    [Fact]
    public async Task CreateCard_ShouldSaveToDatabase()
    {
        // Arrange
        using var context = CreateInMemoryContext();

        // User yaratamiz (FK uchun)
        var user = new User
        {
            FullName = "Test User",
            Email = "test@test.com",
            PasswordHash = "hash"
        };
        context.Users.Add(user);

        var board = new Board { Name = "Test Board", OwnerId = 1 };
        context.Boards.Add(board);
        await context.SaveChangesAsync();

        var card = new Card
        {
            Title = "Test Card",
            BoardId = board.Id
        };

        // Act
        context.Cards.Add(card);
        await context.SaveChangesAsync();

        // Assert
        var savedCard = await context.Cards.FirstOrDefaultAsync(c => c.Title == "Test Card");
        Assert.NotNull(savedCard);
        Assert.Equal("Test Card", savedCard.Title);
    }

    [Fact]
    public async Task MinioService_Upload_ShouldBeCalled()
    {
        // Arrange
        var minioService = Substitute.For<IMinioService>();
        minioService
            .UploadFileAsync(Arg.Any<Stream>(), Arg.Any<string>(), Arg.Any<string>())
            .Returns("test-object-name");

        using var stream = new MemoryStream(new byte[] { 1, 2, 3 });

        // Act
        var result = await minioService.UploadFileAsync(stream, "test.pdf", "application/pdf");

        // Assert
        Assert.Equal("test-object-name", result);
        await minioService.Received(1)
            .UploadFileAsync(Arg.Any<Stream>(), "test.pdf", "application/pdf");
    }
}
```

---

## BOSQICH 8 — Git va ishga tushirish

### 8.1 .gitignore

```
bin/
obj/
*.user
.vs/
appsettings.Development.json
```

### 8.2 Loyihani ishga tushirish tartibi

```bash
# 1. Docker konteynerlarni ishga tushiring
docker-compose up -d

# 2. Ma'lumotlar bazasini yarating
cd TaskFlow.API
dotnet ef database update --project ../TaskFlow.Infrastructure --startup-project .

# 3. API ni ishga tushiring
dotnet run

# 4. Swagger: https://localhost:5001/swagger
# 5. RabbitMQ UI: http://localhost:15672 (taskflow_user/taskflow_pass)
# 6. Minio UI: http://localhost:9001 (taskflow_user/taskflow_pass123)
# 7. Hangfire: https://localhost:5001/hangfire
```

### 8.3 Git commit

```bash
cd C:\ExtraWork\dev-journey
git add .
git commit -m "Middle D: TaskFlow API loyihasi boshlandi (JWT + Docker + SignalR + RabbitMQ + Minio + Hangfire)"
git push origin main
```

---

## Sinov tartibi (Swagger orqali)

```
1. POST /api/auth/register    → Foydalanuvchi yaratish
2. POST /api/auth/login       → Token olish
3. Swagger da "Authorize" → Bearer {token}
4. POST /api/boards           → Board yaratish
5. POST /api/boards/1/cards   → Karta yaratish
6. PATCH /api/boards/1/cards/1/status → Status o'zgartirish
7. POST /api/cards/1/attachments → Fayl yuklash
8. GET  /api/cards/1/attachments/1/url → Fayl URL olish
```

---

## Qo'shimcha imkoniyatlar (keyinroq)

- [ ] CommentsController — karta izohlari
- [ ] RabbitMQ Consumer — hodisalarni qabul qilish
- [ ] SignalR client (HTML/JS) — real-time test
- [ ] Refresh token saqlash (DB da)
- [ ] Integration testlar (WebApplicationFactory)
- [ ] Docker ga API ni ham qo'shish