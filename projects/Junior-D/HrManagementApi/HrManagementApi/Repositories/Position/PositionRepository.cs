using HrManagementApi.Models;
using Npgsql;

namespace HrManagementApi.Repositories;

public class PositionRepository : IPositionRepository
{
    private readonly string _connectionString;

    public PositionRepository(string connectionString)
    {
        _connectionString = connectionString;
    }

    public async Task<int> CreateAsync(Position position)
    {
        string query = "INSERT INTO public.positions (name, department_id, created_at) VALUES (@name, @department_id, @created_at) RETURNING id";

        using var connection = new NpgsqlConnection(_connectionString);
        await connection.OpenAsync();

        using var command = new NpgsqlCommand(query, connection);
        command.Parameters.AddWithValue("@name", position.Name);
        command.Parameters.AddWithValue("@department_id", position.DepartmentId);
        command.Parameters.AddWithValue("@created_at", DateTime.Now);

        var id = await command.ExecuteScalarAsync();
        return Convert.ToInt32(id);
    }

    public async Task<bool> DeleteAsync(int id)
    {
        string query = "DELETE FROM public.positions WHERE id = @id";

        using var connection = new NpgsqlConnection(_connectionString);
        await connection.OpenAsync();

        using var command = new NpgsqlCommand(query, connection);
        command.Parameters.AddWithValue("@id", id);

        var rowsAffected = await command.ExecuteNonQueryAsync();
        return rowsAffected > 0;
    }

    public async Task<List<Position>> GetAllAsync()
    {
        string query = "SELECT id, name, department_id, created_at FROM public.positions ORDER BY id DESC";

        using var connection = new NpgsqlConnection(_connectionString);
        await connection.OpenAsync();

        using var command = new NpgsqlCommand(query, connection);
        using var reader = await command.ExecuteReaderAsync();

        var positions = new List<Position>();
        while (await reader.ReadAsync())
        {
            positions.Add(new Position
            {
                Id = reader.GetInt32(0),
                Name = reader.GetString(1),
                DepartmentId = reader.GetInt32(2),
                CreatedAt = reader.GetDateTime(3)
            });
        }

        return positions;
    }

    public async Task<Position?> GetByIdAsync(int id)
    {
        string query = "SELECT id, name, department_id, created_at FROM public.positions WHERE id = @id";

        using var connection = new NpgsqlConnection(_connectionString);
        await connection.OpenAsync();

        using var command = new NpgsqlCommand(query, connection);
        command.Parameters.AddWithValue("@id", id);

        using var reader = await command.ExecuteReaderAsync();
        if (await reader.ReadAsync())
        {
            return new Position
            {
                Id = reader.GetInt32(0),
                Name = reader.GetString(1),
                DepartmentId = reader.GetInt32(2),
                CreatedAt = reader.GetDateTime(3)
            };
        }

        return null;
    }

    public async Task<bool> UpdateAsync(Position position)
    {
        string query = "UPDATE public.positions SET name = @name, department_id = @department_id, updated_at = @updated_at WHERE id = @id";

        using var connection = new NpgsqlConnection(_connectionString);
        await connection.OpenAsync();

        using var command = new NpgsqlCommand(query, connection);
        command.Parameters.AddWithValue("@name", position.Name);
        command.Parameters.AddWithValue("@department_id", position.DepartmentId);
        command.Parameters.AddWithValue("@updated_at", DateTime.Now);
        command.Parameters.AddWithValue("@id", position.Id);

        var rowsAffected = await command.ExecuteNonQueryAsync();
        return rowsAffected > 0;
    }
}
