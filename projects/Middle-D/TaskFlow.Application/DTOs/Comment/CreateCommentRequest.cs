using System.ComponentModel.DataAnnotations;

namespace TaskFlow.Application.DTOs.Comment;

public class CreateCommentRequest
{
    [Required(ErrorMessage = "Izoh matni bo'sh bo'lmasligi kerak")]
    [MinLength(1)]
    [MaxLength(2000, ErrorMessage = "Izoh 2000 belgidan oshmasligi kerak")]
    public string Content { get; set; } = null!;
}