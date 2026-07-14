using HrManagementApi.DTOs;
using HrManagementApi.Models;
using Npgsql;
using System.Data;

namespace HrManagementApi.Repositories;

public class EmployeeRepository : IEmployeeRepository
{
    private readonly string _connectionString;

    public EmployeeRepository(string connectionString)
    {
        _connectionString = connectionString;
    }

    public async Task<int> CreateAsync(Employee employee)
    {
        string query = "INSERT INTO public.employees (full_name, date_of_birth, position_id, hired_at, created_at) VALUES (@full_name, @date_of_birth, @position_id, @hired_at, @created_at) RETURNING id";

        using var connection = new NpgsqlConnection(_connectionString);
        await connection.OpenAsync();

        using var command = new NpgsqlCommand(query, connection);
        command.Parameters.AddWithValue("@full_name", employee.FullName);
        command.Parameters.Add(new NpgsqlParameter("@date_of_birth", NpgsqlTypes.NpgsqlDbType.Date)
        {
            Value = employee.DateOfBirth
        });
        command.Parameters.AddWithValue("@position_id", employee.PositionId);
        command.Parameters.AddWithValue("@hired_at", employee.HiredAt);
        command.Parameters.AddWithValue("@created_at", DateTime.Now);

        var id = await command.ExecuteScalarAsync();
        return Convert.ToInt32(id);
    }

    public async Task<bool> DeleteAsync(int id)
    {
        string query = "DELETE FROM public.employees WHERE id = @id";

        using var connection = new NpgsqlConnection(_connectionString);
        await connection.OpenAsync();

        using var command = new NpgsqlCommand(query, connection);
        command.Parameters.AddWithValue("@id", id);

        var rowsAffected = await command.ExecuteNonQueryAsync();
        return rowsAffected > 0;
    }

    public async Task<List<EmployeeDto>> GetAllAsync()
    {
        string query = "SELECT e.id, e.full_name, e.date_of_birth, p.id as position_id, p.name as position_name, p.department_id, d.name as department_name, e.hired_at, e.created_at, e.updated_at " +
            "FROM public.employees as e " +
            "LEFT JOIN public.positions as p " +
            "ON e.position_id = p.id " +
            "LEFT JOIN public.departments as d " +
            "ON p.department_id = d.id " +
            "ORDER BY e.id DESC";

        using var connection = new NpgsqlConnection(_connectionString);
        await connection.OpenAsync();

        using var command = new NpgsqlCommand(query, connection);
        using var reader = await command.ExecuteReaderAsync();

        var employees = new List<EmployeeDto>();
        while (await reader.ReadAsync())
        {
            employees.Add(new EmployeeDto
            {
                Id = reader.GetInt32(0),
                FullName = reader.GetString(1),
                DateOfBirth = DateOnly.FromDateTime(reader.GetDateTime(2)),
                PositionId = reader.GetInt32(3),
                PositionName = reader.GetString(4),
                DepartmentId = reader.GetInt32(5),
                DepartmentName = reader.GetString(6),
                HiredAt = reader.GetDateTime(7),
                CreatedAt = reader.GetDateTime(8),
                UpdatedAt = reader.IsDBNull(9) ? null : reader.GetDateTime(9)
            });
        }

        return employees;
    }

    public async Task<EmployeeDto?> GetByIdAsync(int id)
    {
        string query = "SELECT e.id, e.full_name, e.date_of_birth, p.id as position_id, p.name as position_name, p.department_id, d.name as department_name, e.hired_at, e.created_at, e.updated_at " +
            "FROM public.employees as e " +
            "LEFT JOIN public.positions as p " +
            "ON e.position_id = p.id " +
            "LEFT JOIN public.departments as d " +
            "ON p.department_id = d.id " +
            "WHERE e.id = @id " +
            "LIMIT 1";

        using var connection = new NpgsqlConnection(_connectionString);
        await connection.OpenAsync();

        using var command = new NpgsqlCommand(query, connection);
        command.Parameters.AddWithValue("@id", id);

        using var reader = await command.ExecuteReaderAsync();
        if (await reader.ReadAsync())
        {
            return new EmployeeDto
            {
                Id = reader.GetInt32(0),
                FullName = reader.GetString(1),
                DateOfBirth = DateOnly.FromDateTime(reader.GetDateTime(2)),
                PositionId = reader.GetInt32(3),
                PositionName = reader.GetString(4),
                DepartmentId = reader.GetInt32(5),
                DepartmentName = reader.GetString(6),
                HiredAt = reader.GetDateTime(7),
                CreatedAt = reader.GetDateTime(8),
                UpdatedAt = reader.IsDBNull(9) ? null : reader.GetDateTime(9)
            };
        }

        return null;
    }

    public async Task<bool> UpdateAsync(Employee employee)
    {
        string query = "UPDATE public.employees SET full_name = @full_name, date_of_birth = @date_of_birth, position_id = @position_id, hired_at = @hired_at, updated_at = @updated_at WHERE id = @id";

        using var connection = new NpgsqlConnection(_connectionString);
        await connection.OpenAsync();

        using var command = new NpgsqlCommand(query, connection);
        command.Parameters.AddWithValue("@full_name", employee.FullName);
        command.Parameters.Add(new NpgsqlParameter("@date_of_birth", NpgsqlTypes.NpgsqlDbType.Date)
        {
            Value = employee.DateOfBirth
        });
        command.Parameters.AddWithValue("@position_id", employee.PositionId);
        command.Parameters.AddWithValue("@hired_at", employee.HiredAt);
        command.Parameters.AddWithValue("@updated_at", DateTime.Now);
        command.Parameters.AddWithValue("@id", employee.Id);

        var rowsAffected = await command.ExecuteNonQueryAsync();
        return rowsAffected > 0;
    }
}
