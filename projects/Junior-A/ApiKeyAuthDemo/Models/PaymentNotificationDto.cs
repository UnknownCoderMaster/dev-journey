namespace ApiKeyAuthDemo.Models;

public record PaymentNotificationDto(string OrderId, decimal Amount, string Currency);
