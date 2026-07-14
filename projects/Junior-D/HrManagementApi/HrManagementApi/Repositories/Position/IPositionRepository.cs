using HrManagementApi.Models;

namespace HrManagementApi.Repositories;

public interface IPositionRepository
{
    Task<List<Position>> GetAllAsync();
    Task<Position?> GetByIdAsync(int id);
    Task<int> CreateAsync(Position position);
    Task<bool> UpdateAsync(Position position);
    Task<bool> DeleteAsync(int id);
}
