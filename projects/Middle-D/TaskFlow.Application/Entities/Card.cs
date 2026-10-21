namespace TaskFlow.Application.Entities;

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