using HrManagementApi.Models;
using HrManagementApi.Repositories;
using Microsoft.AspNetCore.Mvc;

namespace HrManagementApi.Controllers;

[ApiController]
[Route("api/[controller]")]
public class DepartmentsController : ControllerBase
{
    private readonly IDepartmentRepository _departmentRepository;

    public DepartmentsController(IDepartmentRepository departmentRepository)
    {
        _departmentRepository = departmentRepository;
    }

    [HttpGet]
    public async Task<IActionResult> GetAllDepartments()
    {
        var departments = await _departmentRepository.GetAllAsync();
        return Ok(departments);
    }

    [HttpGet("{id}")]
    public async Task<IActionResult> GetDepartmentById(int id)
    {
        var department = await _departmentRepository.GetByIdAsync(id);
        if (department == null)
            return NotFound();
        return Ok(department);
    }

    [HttpPost]
    public async Task<IActionResult> CreateDepartment([FromBody] Department department)
    {
        if (department == null || string.IsNullOrWhiteSpace(department.Name))
            return BadRequest("Noto'g'ri ma'lumot.");

        var newId = await _departmentRepository.CreateAsync(department);
        department.Id = newId;

        return CreatedAtAction(nameof(GetDepartmentById), new { id = newId }, department);
    }

    [HttpPut("{id}")]
    public async Task<IActionResult> UpdateDepartment(
        int id, [FromBody] Department department)
    {
        if (id != department.Id)
            return BadRequest("ID mos kelmayapti.");

        var updated = await _departmentRepository.UpdateAsync(department);
        if (!updated)
            return NotFound();

        return Ok(department);
    }

    [HttpDelete("{id}")]
    public async Task<IActionResult> DeleteDepartment(int id)
    {
        var deleted = await _departmentRepository.DeleteAsync(id);
        if (!deleted)
            return NotFound();

        return NoContent();
    }
}