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
        await _publisher.PublishAsync("board.created", new
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