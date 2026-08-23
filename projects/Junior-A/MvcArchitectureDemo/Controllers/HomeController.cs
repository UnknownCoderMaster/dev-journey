using Microsoft.AspNetCore.Mvc;

namespace MvcArchitectureDemo.Controllers;

// "Controller : Controller" (ControllerBase EMAS!) — View() metodi
// AYNAN shu bazaviy klassdan keladi (docs 3.2-bo'lim).
public class HomeController : Controller
{
    public IActionResult Index()
    {
        // ViewData — Dictionary<string, object>, FAQAT SHU so'rov ichida yashaydi.
        ViewData["Title"] = "MVC Arxitektura — O'quv Demo";

        // ViewBag — ViewData'ning "dynamic" ko'rinishi — ICHKARIDA XUDDI O'SHA
        // Dictionary'ga yozadi! ViewBag.X va ViewData["X"] — BIR XIL manba.
        ViewBag.WelcomeMessage = "Model-View-Controller so'rov oqimini pastda AMALDA ko'ring";

        return View();
    }

    public IActionResult Error() => View();
}
