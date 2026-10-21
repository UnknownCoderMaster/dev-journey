using Microsoft.EntityFrameworkCore;
using TaskFlow.Application.Entities;

namespace TaskFlow.Infrastructure.Persistence;

public class AppDbContext : DbContext
{
    public AppDbContext(DbContextOptions<AppDbContext> options) : base(options) { }

    public DbSet<User> Users => Set<User>();
    public DbSet<Board> Boards => Set<Board>();
    public DbSet<Card> Cards => Set<Card>();
    public DbSet<Comment> Comments => Set<Comment>();
    public DbSet<Attachment> Attachments => Set<Attachment>();

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        // User
        modelBuilder.Entity<User>(e =>
        {
            e.HasKey(x => x.Id);
            e.HasIndex(x => x.Email).IsUnique();
            e.Property(x => x.Email).HasMaxLength(256);
            e.Property(x => x.FullName).HasMaxLength(256);
            e.Property(x => x.Role).HasDefaultValue("Member");
        });

        // Board
        modelBuilder.Entity<Board>(e =>
        {
            e.HasKey(x => x.Id);
            e.Property(x => x.Name).HasMaxLength(256);
            e.HasOne(x => x.Owner)
             .WithMany(x => x.OwnedBoards)
             .HasForeignKey(x => x.OwnerId)
             .OnDelete(DeleteBehavior.Restrict);
        });

        // Card
        modelBuilder.Entity<Card>(e =>
        {
            e.HasKey(x => x.Id);
            e.Property(x => x.Title).HasMaxLength(512);
            e.Property(x => x.Status)
             .HasConversion<string>()
             .HasDefaultValue(CardStatus.Todo);
            e.HasOne(x => x.Board)
             .WithMany(x => x.Cards)
             .HasForeignKey(x => x.BoardId)
             .OnDelete(DeleteBehavior.Cascade);
            e.HasOne(x => x.Assignee)
             .WithMany(x => x.AssignedCards)
             .HasForeignKey(x => x.AssigneeId)
             .OnDelete(DeleteBehavior.SetNull);
        });

        // Comment
        modelBuilder.Entity<Comment>(e =>
        {
            e.HasKey(x => x.Id);
            e.HasOne(x => x.Card)
             .WithMany(x => x.Comments)
             .HasForeignKey(x => x.CardId)
             .OnDelete(DeleteBehavior.Cascade);
        });

        // Attachment
        modelBuilder.Entity<Attachment>(e =>
        {
            e.HasKey(x => x.Id);
            e.HasOne(x => x.Card)
             .WithMany(x => x.Attachments)
             .HasForeignKey(x => x.CardId)
             .OnDelete(DeleteBehavior.Cascade);
        });
    }
}