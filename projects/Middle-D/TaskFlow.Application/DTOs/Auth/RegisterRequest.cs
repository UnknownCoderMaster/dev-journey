using System.ComponentModel.DataAnnotations;

namespace TaskFlow.Application.DTOs.Auth;

public class RegisterRequest
{
    [Required, MaxLength(256)]
    public string FullName { get; set; } = null!;

    [Required, EmailAddress]
    public string Email { get; set; } = null!;

    [Required, MinLength(6)]
    public string Password { get; set; } = null!;
}