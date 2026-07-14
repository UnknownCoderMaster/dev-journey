using HrManagementApi.Models;
using HrManagementApi.Repositories;
using Microsoft.AspNetCore.Mvc;

namespace HrManagementApi.Controllers;

[ApiController]
[Route("api/[controller]")]
public class EmployeesController : ControllerBase
{
    private readonly IEmployeeRepository _employeeRepository;

    public EmployeesController(IEmployeeRepository employeeRepository)
    {
        _employeeRepository = employeeRepository;
    }

    [HttpGet]
    public async Task<IActionResult> GetAllEmployees()
    {
        var employees = await _employeeRepository.GetAllAsync();
        return Ok(employees);
    }

    [HttpGet("{id}")]
    public async Task<IActionResult> GetEmployeeById(int id)
    {
        var employee = await _employeeRepository.GetByIdAsync(id);
        if (employee == null)
            return NotFound();
        return Ok(employee);
    }

    [HttpPost]
    public async Task<IActionResult> CreateEmployee([FromBody] Employee employee)
    {
        if (employee == null || string.IsNullOrWhiteSpace(employee.FullName))
            return BadRequest("Noto'g'ri ma'lumot.");

        var newId = await _employeeRepository.CreateAsync(employee);
        employee.Id = newId;

        return CreatedAtAction(nameof(GetEmployeeById), new { id = newId }, employee);
    }

    [HttpPut("{id}")]
    public async Task<IActionResult> UpdateEmployee(
        int id, [FromBody] Employee employee)
    {
        if (id != employee.Id)
            return BadRequest("ID mos kelmayapti.");

        var updated = await _employeeRepository.UpdateAsync(employee);
        if (!updated)
            return NotFound();

        return Ok(employee);
    }

    [HttpDelete("{id}")]
    public async Task<IActionResult> DeleteEmployee(int id)
    {
        var deleted = await _employeeRepository.DeleteAsync(id);
        if (!deleted)
            return NotFound();

        return NoContent();
    }
}
