namespace TaskFlow.Application.Contracts;

public interface IRabbitMQPublisher
{
    Task PublishAsync<T>(string routingKey, T message, CancellationToken cancellationToken = default);
}