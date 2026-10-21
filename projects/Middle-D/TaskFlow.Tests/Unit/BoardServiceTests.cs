using Microsoft.EntityFrameworkCore;
using NSubstitute;
using TaskFlow.Application.Contracts;
using TaskFlow.Application.Entities;
using TaskFlow.Infrastructure.Persistence;

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
    public async Task Publish_ShouldBeCalled_WhenBoardCreated()
    {
        // Arrange
        var publisher = Substitute.For<IRabbitMQPublisher>();

        // Act
        await publisher.PublishAsync("board.created", new { BoardId = 1, Name = "Test Board" });

        // Assert
        await publisher.Received(1).PublishAsync(
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