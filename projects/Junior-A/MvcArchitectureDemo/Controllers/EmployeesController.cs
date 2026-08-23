using Microsoft.AspNetCore.Mvc;
using MvcArchitectureDemo.Data;
using MvcArchitectureDemo.Models;

namespace MvcArchitectureDemo.Controllers;

// Bu Controller — docs/12-mvc-nlayer-architecture (3.1-bo'lim)dagi
// TO'LIQ so'rov oqimini (Request Flow) amalda ko'rsatadi:
// Brauzer -> Controller -> Model (IEmployeeStore) -> Controller -> View -> Brauzer.
public class EmployeesController : Controller
{
    private readonly IEmployeeStore _store;

    public EmployeesController(IEmployeeStore store) => _store = store;

    // GET /Employees
    public IActionResult Index()
    {
        ViewBag.Title = "Xodimlar ro'yxati"; // ViewBag orqali sarlavha uzatiladi

        var employees = _store.GetAll();
        return View(employees); // 'employees' — STRONGLY TYPED Model sifatida View'ga uzatiladi
    }

    // GET /Employees/Details/5
    public IActionResult Details(int id)
    {
        var employee = _store.GetById(id);
        if (employee is null) return NotFound();
        return View(employee);
    }

    // GET /Employees/Create
    public IActionResult Create() => View();

    // POST /Employees/Create
    [HttpPost]
    [ValidateAntiForgeryToken]
    public IActionResult Create(Employee employee)
    {
        // Model'dagi [Required], [Range] kabi atributlar — ModelState orqali
        // AVTOMATIK tekshiriladi (docs/Junior-A/20-input-validation'ga o'xshash).
        if (!ModelState.IsValid) return View(employee); // Xato bo'lsa — SHU FORM, kiritilgan qiymatlar bilan qaytariladi

        _store.Add(employee);

        // TempData — REDIRECT'DAN KEYIN HAM saqlanadi! (ViewData/ViewBag —
        // Redirect paytida YO'QOLARDI, chunki ular YANGI HTTP so'rov, YANGI umr).
        TempData["Message"] = $"'{employee.FullName}' muvaffaqiyatli qo'shildi!";

        return RedirectToAction(nameof(Index));
    }

    // GET /Employees/Edit/5
    public IActionResult Edit(int id)
    {
        var employee = _store.GetById(id);
        if (employee is null) return NotFound();
        return View(employee);
    }

    // POST /Employees/Edit/5
    [HttpPost]
    [ValidateAntiForgeryToken]
    public IActionResult Edit(int id, Employee employee)
    {
        if (id != employee.Id) return BadRequest();
        if (!ModelState.IsValid) return View(employee);

        _store.Update(employee);
        TempData["Message"] = $"'{employee.FullName}' ma'lumotlari yangilandi!";
        return RedirectToAction(nameof(Index));
    }

    // GET /Employees/Delete/5
    public IActionResult Delete(int id)
    {
        var employee = _store.GetById(id);
        if (employee is null) return NotFound();
        return View(employee);
    }

    // POST /Employees/Delete/5 — nom to'qnashmasligi uchun DeleteConfirmed,
    // lekin [ActionName("Delete")] orqali URL /Employees/Delete/5 bo'lib qoladi.
    [HttpPost, ActionName("Delete")]
    [ValidateAntiForgeryToken]
    public IActionResult DeleteConfirmed(int id)
    {
        var employee = _store.GetById(id);
        _store.Delete(id);
        TempData["Message"] = $"'{employee?.FullName}' o'chirildi!";
        return RedirectToAction(nameof(Index));
    }
}
