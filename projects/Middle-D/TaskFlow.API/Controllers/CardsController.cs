using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.SignalR;
using Microsoft.EntityFrameworkCore;
using System.Security.Claims;
using TaskFlow.API.Hubs;
using TaskFlow.Application.Contracts;
using TaskFlow.Application.Entities;
using TaskFlow.Infrastructure.Persistence;

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
        await _publisher.PublishAsync("card.created", new
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
        await _publisher.PublishAsync("card.status.updated", new
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