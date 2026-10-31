using Microsoft.Extensions.Configuration;
using Microsoft.Extensions.DependencyInjection;
using Microsoft.Extensions.Hosting;
using Microsoft.Extensions.Logging;
using RabbitMQ.Client;
using RabbitMQ.Client.Events;
using System.Text;
using System.Text.Json;

namespace TaskFlow.Infrastructure.Messaging;

public sealed class RabbitMQConsumer : BackgroundService
{
    private const string QueueName = "taskflow_events";
    private const string DeadLetterExchange = "taskflow_dlx";
    private const string DeadLetterQueue = "taskflow_events_dead";

    private readonly ConnectionFactory _factory;
    private readonly string _exchangeName;
    private readonly ILogger<RabbitMQConsumer> _logger;
    private readonly IServiceScopeFactory _scopeFactory;

    private IConnection? _connection;
    private IChannel? _channel;

    public RabbitMQConsumer(
        IConfiguration config,
        ILogger<RabbitMQConsumer> logger,
        IServiceScopeFactory scopeFactory)
    {
        _logger = logger;
        _scopeFactory = scopeFactory;
        _exchangeName = config["RabbitMQ:ExchangeName"]!;

        _factory = new ConnectionFactory
        {
            HostName = config["RabbitMQ:Host"]!,
            Port = int.Parse(config["RabbitMQ:Port"]!),
            UserName = config["RabbitMQ:Username"]!,
            Password = config["RabbitMQ:Password"]!,
            AutomaticRecoveryEnabled = true,
            TopologyRecoveryEnabled = true,
            NetworkRecoveryInterval = TimeSpan.FromSeconds(10),
            ClientProvidedName = "taskflow-api:consumer"
        };
    }

    protected override async Task ExecuteAsync(CancellationToken stoppingToken)
    {
        // RabbitMQ ilovadan kechroq ko'tarilishi mumkin — qayta urinamiz
        while (!stoppingToken.IsCancellationRequested)
        {
            try
            {
                await StartConsumingAsync(stoppingToken);
                break;
            }
            catch (OperationCanceledException)
            {
                return;
            }
            catch (Exception ex)
            {
                _logger.LogWarning(ex,
                    "Consumer ulanmadi. 10 soniyadan keyin qayta urinaman");

                await Task.Delay(TimeSpan.FromSeconds(10), stoppingToken);
            }
        }

        // Consumer ro'yxatdan o'tdi. Ilova to'xtaguncha kutamiz.
        try
        {
            await Task.Delay(Timeout.Infinite, stoppingToken);
        }
        catch (OperationCanceledException)
        {
            // Normal to'xtash
        }
    }

    private async Task StartConsumingAsync(CancellationToken ct)
    {
        _connection = await _factory.CreateConnectionAsync(ct);
        _channel = await _connection.CreateChannelAsync(cancellationToken: ct);

        // --- Dead letter infratuzilmasi ---
        await _channel.ExchangeDeclareAsync(
            exchange: DeadLetterExchange,
            type: ExchangeType.Fanout,
            durable: true,
            autoDelete: false,
            cancellationToken: ct);

        await _channel.QueueDeclareAsync(
            queue: DeadLetterQueue,
            durable: true,
            exclusive: false,
            autoDelete: false,
            cancellationToken: ct);

        await _channel.QueueBindAsync(
            queue: DeadLetterQueue,
            exchange: DeadLetterExchange,
            routingKey: string.Empty,
            cancellationToken: ct);

        // --- Asosiy exchange (publisher bilan bir xil) ---
        await _channel.ExchangeDeclareAsync(
            exchange: _exchangeName,
            type: ExchangeType.Topic,
            durable: true,
            autoDelete: false,
            cancellationToken: ct);

        // --- Asosiy navbat, DLX ga ulangan ---
        var queueArgs = new Dictionary<string, object?>
        {
            ["x-dead-letter-exchange"] = DeadLetterExchange
        };

        await _channel.QueueDeclareAsync(
            queue: QueueName,
            durable: true,
            exclusive: false,
            autoDelete: false,
            arguments: queueArgs,
            cancellationToken: ct);

        // Qaysi hodisalarni eshitamiz.
        // "#" — bir yoki bir nechta so'z (card.created, card.status.updated ...)
        foreach (var pattern in new[] { "board.#", "card.#", "comment.#" })
        {
            await _channel.QueueBindAsync(
                queue: QueueName,
                exchange: _exchangeName,
                routingKey: pattern,
                cancellationToken: ct);
        }

        // Bir vaqtda 10 tadan ortiq tasdiqlanmagan xabar bermasin
        await _channel.BasicQosAsync(
            prefetchSize: 0,
            prefetchCount: 10,
            global: false,
            cancellationToken: ct);

        var consumer = new AsyncEventingBasicConsumer(_channel);
        consumer.ReceivedAsync += OnMessageReceivedAsync;

        await _channel.BasicConsumeAsync(
            queue: QueueName,
            autoAck: false,
            consumer: consumer,
            cancellationToken: ct);

        _logger.LogInformation(
            "RabbitMQ consumer ishga tushdi. Navbat: {Queue}", QueueName);
    }

    private async Task OnMessageReceivedAsync(object sender, BasicDeliverEventArgs ea)
    {
        // MUHIM: v7 da Body kutubxonaga tegishli va faqat shu handler ichida
        // amal qiladi. Tashqarida ishlatish uchun nusxa olish shart.
        var json = Encoding.UTF8.GetString(ea.Body.ToArray());
        var routingKey = ea.RoutingKey;

        try
        {
            // BackgroundService singleton, DbContext esa scoped.
            // Har bir xabar uchun alohida scope ochamiz.
            using var scope = _scopeFactory.CreateScope();

            await HandleEventAsync(routingKey, json, scope.ServiceProvider);

            await _channel!.BasicAckAsync(ea.DeliveryTag, multiple: false);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex,
                "Hodisani qayta ishlashda xatolik. RoutingKey: {RoutingKey}", routingKey);

            // requeue: false → xabar dead letter navbatiga tushadi.
            // true qilsak, buzuq xabar cheksiz aylanaveradi.
            await _channel!.BasicNackAsync(ea.DeliveryTag, multiple: false, requeue: false);
        }
    }

    private Task HandleEventAsync(
        string routingKey, string json, IServiceProvider services)
    {
        using var doc = JsonDocument.Parse(json);
        var root = doc.RootElement;

        switch (routingKey)
        {
            case "card.deadline.reminder":
                // Haqiqiy loyihada bu yerda email/push yuboriladi
                _logger.LogInformation(
                    "[ESLATMA] Karta muddati yaqinlashdi: {Title} → {Email}",
                    root.GetProperty("Title").GetString(),
                    root.TryGetProperty("AssigneeEmail", out var email)
                        ? email.GetString() : "(tayinlanmagan)");
                break;

            case "comment.created":
                _logger.LogInformation(
                    "[IZOH] {Author} '{Card}' kartasiga izoh qoldirdi",
                    root.GetProperty("AuthorName").GetString(),
                    root.GetProperty("CardTitle").GetString());
                break;

            case "card.created":
                _logger.LogInformation(
                    "[AUDIT] Yangi karta: {Title} (board {BoardId})",
                    root.GetProperty("Title").GetString(),
                    root.GetProperty("BoardId").GetInt32());
                break;

            case "card.status.updated":
                _logger.LogInformation(
                    "[AUDIT] Karta {CardId} holati → {Status}",
                    root.GetProperty("CardId").GetInt32(),
                    root.GetProperty("Status").GetString());
                break;

            case "board.created":
                _logger.LogInformation(
                    "[AUDIT] Yangi board: {Name}",
                    root.GetProperty("Name").GetString());
                break;

            default:
                _logger.LogWarning(
                    "Noma'lum hodisa turi: {RoutingKey}", routingKey);
                break;
        }

        return Task.CompletedTask;
    }

    public override async Task StopAsync(CancellationToken cancellationToken)
    {
        try
        {
            if (_channel is not null)
            {
                await _channel.CloseAsync(cancellationToken);
                await _channel.DisposeAsync();
            }

            if (_connection is not null)
            {
                await _connection.CloseAsync(cancellationToken);
                await _connection.DisposeAsync();
            }
        }
        catch (Exception ex)
        {
            _logger.LogWarning(ex, "Consumer ni yopishda xatolik");
        }

        await base.StopAsync(cancellationToken);
    }
}
