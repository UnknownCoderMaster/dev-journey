using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.Logging;
using TaskFlow.Application.Contracts;
using TaskFlow.Application.Entities;
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
                && c.Status != CardStatus.Done)
            .ToListAsync();

        foreach (var card in urgentCards)
        {
            _logger.LogInformation(
                "Deadline yaqinlashmoqda: Card {CardId} - {Title}", card.Id, card.Title);

            await _publisher.PublishAsync("card.deadline.reminder", new
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