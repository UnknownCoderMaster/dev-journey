using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.Logging;
using RabbitMQ.Client;
using System.Text.Json;
using TaskFlow.Application.Contracts;

namespace TaskFlow.Infrastructure.Messaging;

public sealed class RabbitMQPublisher : IRabbitMQPublisher, IAsyncDisposable
{
    private readonly ConnectionFactory _factory;
    private readonly string _exchangeName;
    private readonly ILogger<RabbitMQPublisher> _logger;

    // Bog'lanishni faqat bitta thread yaratishi uchun
    private readonly SemaphoreSlim _initLock = new(1, 1);

    // Channel thread-safe emas — publish larni navbatga solamiz
    private readonly SemaphoreSlim _publishLock = new(1, 1);

    private IConnection? _connection;
    private IChannel? _channel;
    private bool _disposed;

    public RabbitMQPublisher(IConfiguration config, ILogger<RabbitMQPublisher> logger)
    {
        _logger = logger;
        _exchangeName = config["RabbitMQ:ExchangeName"]!;

        _factory = new ConnectionFactory
        {
            HostName = config["RabbitMQ:Host"]!,
            Port = int.Parse(config["RabbitMQ:Port"]!),
            UserName = config["RabbitMQ:Username"]!,
            Password = config["RabbitMQ:Password"]!,

            // Bog'lanish uzilsa avtomatik tiklanadi
            AutomaticRecoveryEnabled = true,
            TopologyRecoveryEnabled = true,
            NetworkRecoveryInterval = TimeSpan.FromSeconds(10),

            // RabbitMQ Management UI da ko'rinadi — debug uchun qulay
            ClientProvidedName = "taskflow-api:publisher"
        };
    }

    /// <summary>
    /// Channel ni qaytaradi. Birinchi chaqiriqda bog'lanish o'rnatiladi,
    /// keyingilarida mavjudi qayta ishlatiladi.
    /// </summary>
    private async Task<IChannel> GetChannelAsync(CancellationToken ct)
    {
        // Tez yo'l: channel ochiq bo'lsa, lock ga kirmaymiz
        if (_channel is { IsOpen: true })
            return _channel;

        await _initLock.WaitAsync(ct);
        try
        {
            // Lock ichida qayta tekshirish — boshqa thread allaqachon yaratgan bo'lishi mumkin
            if (_channel is { IsOpen: true })
                return _channel;

            if (_connection is null || !_connection.IsOpen)
            {
                _logger.LogInformation("RabbitMQ ga ulanmoqda: {Host}:{Port}",
                    _factory.HostName, _factory.Port);

                _connection = await _factory.CreateConnectionAsync(ct);

                _logger.LogInformation("RabbitMQ bog'lanishi o'rnatildi");
            }

            _channel = await _connection.CreateChannelAsync(cancellationToken: ct);

            await _channel.ExchangeDeclareAsync(
                exchange: _exchangeName,
                type: ExchangeType.Topic,
                durable: true,
                autoDelete: false,
                arguments: null,
                cancellationToken: ct);

            _logger.LogInformation("Exchange tayyor: {Exchange}", _exchangeName);

            return _channel;
        }
        finally
        {
            _initLock.Release();
        }
    }

    public async Task PublishAsync<T>(
        string routingKey,
        T message,
        CancellationToken cancellationToken = default)
    {
        ObjectDisposedException.ThrowIf(_disposed, this);

        var body = JsonSerializer.SerializeToUtf8Bytes(message);

        var properties = new BasicProperties
        {
            Persistent = true,                    // Disk ga yoziladi, restart da yo'qolmaydi
            ContentType = "application/json",
            MessageId = Guid.NewGuid().ToString(),
            Timestamp = new AmqpTimestamp(DateTimeOffset.UtcNow.ToUnixTimeSeconds())
        };

        var channel = await GetChannelAsync(cancellationToken);

        await _publishLock.WaitAsync(cancellationToken);
        try
        {
            await channel.BasicPublishAsync(
                exchange: _exchangeName,
                routingKey: routingKey,
                mandatory: false,
                basicProperties: properties,
                body: body,
                cancellationToken: cancellationToken);

            _logger.LogDebug("Xabar yuborildi: {RoutingKey}", routingKey);
        }
        finally
        {
            _publishLock.Release();
        }
    }

    public async ValueTask DisposeAsync()
    {
        if (_disposed) return;
        _disposed = true;

        try
        {
            if (_channel is not null)
            {
                await _channel.CloseAsync();
                await _channel.DisposeAsync();
            }

            if (_connection is not null)
            {
                await _connection.CloseAsync();
                await _connection.DisposeAsync();
            }
        }
        catch (Exception ex)
        {
            _logger.LogWarning(ex, "RabbitMQ bog'lanishini yopishda xatolik");
        }
        finally
        {
            _initLock.Dispose();
            _publishLock.Dispose();
        }
    }
}
