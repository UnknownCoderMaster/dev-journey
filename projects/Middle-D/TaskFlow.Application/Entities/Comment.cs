namespace TaskFlow.Application.Entities;

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