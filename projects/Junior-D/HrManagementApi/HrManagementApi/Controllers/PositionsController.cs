using HrManagementApi.Models;
using HrManagementApi.Repositories;
using Microsoft.AspNetCore.Mvc;

namespace HrManagementApi.Controllers;

[ApiController]
[Route("api/[controller]")]
public class PositionsController : ControllerBase
{
    private readonly IPositionRepository _positionRepository;

    public PositionsController(IPositionRepository positionRepository)
    {
        _positionRepository = positionRepository;
    }

    [HttpGet]
    public async Task<IActionResult> GetAllPositions()
    {
        var positions = await _positionRepository.GetAllAsync();
        return Ok(positions);
    }

    [HttpGet("{id}")]
    public async Task<IActionResult> GetPositionById(int id)
    {
        var position = await _positionRepository.GetByIdAsync(id);
        if (position == null)
            return NotFound();
        return Ok(position);
    }

    [HttpPost]
    public async Task<IActionResult> CreatePosition([FromBody] Position position)
    {
        if (position == null || string.IsNullOrWhiteSpace(position.Name))
            return BadRequest("Noto'g'ri ma'lumot.");

        var newId = await _positionRepository.CreateAsync(position);
        position.Id = newId;

        return CreatedAtAction(nameof(GetPositionById), new { id = newId }, position);
    }

    [HttpPut("{id}")]
    public async Task<IActionResult> UpdatePosition(
        int id, [FromBody] Position position)
    {
        if (id != position.Id)
            return BadRequest("ID mos kelmayapti.");

        var updated = await _positionRepository.UpdateAsync(position);
        if (!updated)
            return NotFound();

        return Ok(position);
    }

    [HttpDelete("{id}")]
    public async Task<IActionResult> DeletePosition(int id)
    {
        var deleted = await _positionRepository.DeleteAsync(id);
        if (!deleted)
            return NotFound();

        return NoContent();
    }
}
