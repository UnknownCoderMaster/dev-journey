using HrManagementApi.Models;
using Npgsql;

namespace HrManagementApi.Repositories;

public class DepartmentRepository : IDepartmentRepository
{
    private readonly string _connectionString;

    public DepartmentRepository(string connectionString)
    {
        _connectionString = connectionString;
    }

    public async Task<int> CreateAsync(Department department)
    {
        string query = "INSERT INTO public.departments (name, created_at) VALUES (@name, @created_at) RETURNING id";

        using var connection = new NpgsqlConnection(_connectionString);
        await connection.OpenAsync();

        using var command = new NpgsqlCommand(query, connection);
        command.Parameters.AddWithValue("@name", department.Name);
        command.Parameters.AddWithValue("@created_at", DateTime.Now);

        var id = await command.ExecuteScalarAsync();
        return Convert.ToInt32(id);
    }

    public async Task<bool> DeleteAsync(int id)
    {
        string query = "DELETE FROM public.departments WHERE id = @id";

        using var connection = new NpgsqlConnection(_connectionString);
        await connection.OpenAsync();

        using var command = new NpgsqlCommand(query, connection);
        command.Parameters.AddWithValue("@id", id);

        var rowsAffected = await command.ExecuteNonQueryAsync();
        return rowsAffected > 0;
    }

    public async Task<List<Department>> GetAllAsync()
    {
        var departments = new List<Department>();

        string query = "SELECT id, name, created_at FROM public.departments " +
                       "ORDER BY id DESC";

        using var connection = new NpgsqlConnection(_connectionString);
        await connection.OpenAsync();

        using var command = new NpgsqlCommand(query, connection);
        using var reader = await command.ExecuteReaderAsync();

        while (await reader.ReadAsync())
        {
            departments.Add(new Department
            {
                Id = reader.GetInt32(0),
                Name = reader.GetString(1),
                CreatedAt = reader.GetDateTime(2)
            });
        }

        return departments;
    }

    public async Task<Department?> GetByIdAsync(int id)
    {
        Department? department = null;

        string query = "SELECT id, name, created_at FROM public.departments WHERE id = @id LIMIT 1";

        using var connection = new NpgsqlConnection(_connectionString);
        await connection.OpenAsync();

        using var command = new NpgsqlCommand(query, connection);
        command.Parameters.AddWithValue("@id", id);

        using var reader = await command.ExecuteReaderAsync();

        if (await reader.ReadAsync())
        {
            department = new Department
            {
                Id = reader.GetInt32(0),
                Name = reader.GetString(1),
                CreatedAt = reader.GetDateTime(2)
            };
        }

        return department;
    }

    public async Task<bool> UpdateAsync(Department department)
    {
        string query = "UPDATE public.departments SET name = @name, updated_at = @updated_at WHERE id = @id";

        using var connection = new NpgsqlConnection(_connectionString);
        await connection.OpenAsync();

        using var command = new NpgsqlCommand(query, connection);
        command.Parameters.AddWithValue("@name", department.Name);
        command.Parameters.AddWithValue("@updated_at", DateTime.Now);
        command.Parameters.AddWithValue("@id", department.Id);

        var rowsAffected = await command.ExecuteNonQueryAsync();
        return rowsAffected > 0;
    }
}
