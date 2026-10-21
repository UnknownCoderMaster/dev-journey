namespace TaskFlow.Application.Entities;

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
