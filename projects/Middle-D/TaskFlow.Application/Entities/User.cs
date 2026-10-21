namespace TaskFlow.Application.Entities;

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