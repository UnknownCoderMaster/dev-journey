using Microsoft.AspNetCore.Authorization;
using Microsoft.AspNetCore.Mvc;
using System.Security.Claims;
using Microsoft.EntityFrameworkCore;
using TaskFlow.Application.Contracts;
using TaskFlow.Infrastructure.Persistence;
using TaskFlow.Application.Entities;

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