using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using Microsoft.AspNetCore.SignalR;
using Microsoft.EntityFrameworkCore;
using System.Security.Claims;
using TaskFlow.API.Hubs;
using TaskFlow.Application.Contracts;
using TaskFlow.Application.DTOs.Comment;
using TaskFlow.Application.Entities;
using TaskFlow.Infrastructure.Persistence;

namespace TaskFlow.API.Controllers;

[Authorize]
[ApiController]
[Route("api/cards/{cardId:int}/comments")]
public class CommentsController : ControllerBase
{
    private readonly AppDbContext _context;
    private readonly IRabbitMQPublisher _publisher;
    private readonly IHubContext<TaskHub> _hubContext;

    public CommentsController(
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

    private string CurrentUserName =>
        User.FindFirstValue(ClaimTypes.Name) ?? "Noma'lum";

    [HttpGet]
    public async Task<ActionResult<List<CommentDto>>> GetAll(
        int cardId, CancellationToken ct)
    {
        var cardExists = await _context.Cards.AnyAsync(c => c.Id == cardId, ct);
        if (!cardExists)
            return NotFound(new { message = "Karta topilmadi" });

        var comments = await _context.Comments
            .Where(c => c.CardId == cardId)
            .OrderBy(c => c.CreatedAt)
            .Select(c => new CommentDto(
                c.Id,
                c.Content,
                c.UserId,
                c.User.FullName,
                c.CreatedAt))
            .ToListAsync(ct);

        return Ok(comments);
    }

    [HttpPost]
    public async Task<ActionResult<CommentDto>> Create(
        int cardId,
        [FromBody] CreateCommentRequest request,
        CancellationToken ct)
    {
        // Kartani to'liq yuklamaymiz — faqat kerakli maydonlarni olamiz.
        // BoardId SignalR guruhini aniqlash uchun kerak.
        var card = await _context.Cards
            .Where(c => c.Id == cardId)
            .Select(c => new { c.Id, c.BoardId, c.Title })
            .FirstOrDefaultAsync(ct);

        if (card is null)
            return NotFound(new { message = "Karta topilmadi" });

        var comment = new Comment
        {
            Content = request.Content,
            CardId = cardId,
            UserId = CurrentUserId
        };

        _context.Comments.Add(comment);
        await _context.SaveChangesAsync(ct);

        var dto = new CommentDto(
            comment.Id,
            comment.Content,
            CurrentUserId,
            CurrentUserName,
            comment.CreatedAt);

        // Real-time: board ni ochib turganlarga darhol yetkazamiz
        await _hubContext.Clients
            .Group($"board-{card.BoardId}")
            .SendAsync("CommentCreated", new
            {
                CardId = cardId,
                Comment = dto
            }, ct);

        // Fon ishlovi uchun hodisa: email yuborish, audit va h.k.
        await _publisher.PublishAsync("comment.created", new
        {
            CommentId = comment.Id,
            CardId = cardId,
            CardTitle = card.Title,
            BoardId = card.BoardId,
            AuthorId = CurrentUserId,
            AuthorName = CurrentUserName,
            Content = comment.Content
        }, ct);

        return CreatedAtAction(nameof(GetAll), new { cardId }, dto);
    }

    [HttpDelete("{commentId:int}")]
    public async Task<IActionResult> Delete(
        int cardId, int commentId, CancellationToken ct)
    {
        var comment = await _context.Comments
            .FirstOrDefaultAsync(c => c.Id == commentId && c.CardId == cardId, ct);

        if (comment is null)
            return NotFound();

        // Izohni faqat muallifi o'chira oladi
        if (comment.UserId != CurrentUserId)
            return Forbid();

        var boardId = await _context.Cards
            .Where(c => c.Id == cardId)
            .Select(c => c.BoardId)
            .FirstAsync(ct);

        _context.Comments.Remove(comment);
        await _context.SaveChangesAsync(ct);

        await _hubContext.Clients
            .Group($"board-{boardId}")
            .SendAsync("CommentDeleted", new { CardId = cardId, CommentId = commentId }, ct);

        return NoContent();
    }
}