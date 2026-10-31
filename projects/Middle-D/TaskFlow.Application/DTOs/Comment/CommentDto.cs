namespace TaskFlow.Application.DTOs.Comment;

public record CommentDto(
    int Id,
    string Content,
    int AuthorId,
    string AuthorName,
    DateTime CreatedAt);