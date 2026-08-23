using Microsoft.AspNetCore.Mvc;
using NLayerDemo.BusinessLogic;
using NLayerDemo.BusinessLogic.Dtos;
using NLayerDemo.BusinessLogic.Exceptions;

// ⚠️ SINAB KO'RING (nozik farq bor!): NLayerDemo.Api.csproj DataAccess'ga
// ProjectReference'ga EGA EMAS, lekin BusinessLogic'ning ProjectReference'i
// TRANZITIV ravishda DataAccess'ning PUBLIC turlarini (masalan
// IEmployeeRepository, Entities.Employee) ko'rinadigan qiladi — bu .NET'ning
// ODDIY, KUTILGAN xatti-harakati (shuning uchun "using NLayerDemo.DataAccess;"
// yozib qo'yish O'ZI xato bermaydi).
//
// LEKIN: konkret "EmployeeRepository" klassi DataAccess'da `internal` deb
// belgilangan — shuning uchun "new NLayerDemo.DataAccess.EmployeeRepository(...)"
// yozib ko'rsangiz — CS0122 "is inaccessible due to its protection level"
// xatosini olasiz (buni loyihada AMALDA sinab, tasdiqlab ko'rilgan).
// XULOSA: Dependency direction — ProjectReference emas, balki `internal`
// access modifier orqali COMPILER darajasida MAJBURLANADI (docs 3.6-bo'lim).

namespace NLayerDemo.Api.Controllers;

[ApiController]
[Route("api/[controller]")]
public class EmployeesController : ControllerBase
{
    // Presentation — FAQAT BLL interfeysiga bog'liq, EmployeeService
    // konkret klassiga ham EMAS (DIP amaliyoti).
    private readonly IEmployeeService _service;

    public EmployeesController(IEmployeeService service) => _service = service;

    [HttpGet]
    public async Task<ActionResult<List<EmployeeDto>>> GetAll() => Ok(await _service.GetAllAsync());

    [HttpGet("{id:int}")]
    public async Task<ActionResult<EmployeeDto>> GetById(int id)
    {
        try { return Ok(await _service.GetByIdAsync(id)); }
        catch (NotFoundException ex) { return NotFound(new { message = ex.Message }); }
    }

    [HttpPost]
    public async Task<ActionResult<EmployeeDto>> Create(CreateEmployeeDto dto)
    {
        try
        {
            var created = await _service.CreateAsync(dto);
            return CreatedAtAction(nameof(GetById), new { id = created.Id }, created);
        }
        catch (ArgumentException ex) { return BadRequest(new { message = ex.Message }); }
    }

    [HttpPut("{id:int}")]
    public async Task<ActionResult<EmployeeDto>> Update(int id, UpdateEmployeeDto dto)
    {
        try { return Ok(await _service.UpdateAsync(id, dto)); }
        catch (NotFoundException ex) { return NotFound(new { message = ex.Message }); }
    }

    [HttpDelete("{id:int}")]
    public async Task<IActionResult> Delete(int id)
    {
        try
        {
            await _service.DeleteAsync(id);
            return NoContent();
        }
        catch (NotFoundException ex) { return NotFound(new { message = ex.Message }); }
    }

    // docs 3.9-bo'limidagi "Presentation — Controller, API" misolining aynan o'zi.
    [HttpGet("{id:int}/bonus")]
    public async Task<IActionResult> GetBonus(int id)
    {
        try
        {
            var bonus = await _service.CalculateBonusAsync(id);
            return Ok(new { employeeId = id, annualBonus = bonus });
        }
        catch (NotFoundException ex) { return NotFound(new { message = ex.Message }); }
    }
}
