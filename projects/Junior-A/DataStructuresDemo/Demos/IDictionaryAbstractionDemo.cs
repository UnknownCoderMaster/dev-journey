using DataStructuresDemo.Models;

namespace DataStructuresDemo.Demos;

public static class IDictionaryAbstractionDemo
{
    public static void Run()
    {
        Console.WriteLine("--- IDictionary<TKey, TValue> — abstraksiya sifatida ishlatish ---\n");

        // Bitta metod (pastdagi PrintAll) — IDictionary interfeysini QABUL qiladi,
        // ICHIDA qaysi KONKRET implementatsiya (Dictionary, SortedDictionary)
        // ekanligi metod uchun MUHIM EMAS!
        IDictionary<int, Employee> plain = new Dictionary<int, Employee>();
        IDictionary<int, Employee> sorted = new SortedDictionary<int, Employee>();

        var employees = new[]
        {
            new Employee { Id = 3, FullName = "Aziz", Department = "IT" },
            new Employee { Id = 1, FullName = "Orzibek", Department = "IT" },
            new Employee { Id = 2, FullName = "Dilnoza", Department = "HR" }
        };

        foreach (var emp in employees)
        {
            plain[emp.Id] = emp;
            sorted[emp.Id] = emp;
        }

        Console.WriteLine("Dictionary (tartib KAFOLATLANMAYDI, odatda qo'shilish tartibida ko'rinadi):");
        PrintAll(plain);

        Console.WriteLine("\nSortedDictionary (HAR DOIM Key bo'yicha TARTIBLANGAN):");
        PrintAll(sorted);

        Console.WriteLine("\nXULOSA: 'PrintAll(IDictionary<int, Employee> dict)' metodi —");
        Console.WriteLine("qaysi konkret klass ekanligidan qat'i nazar ishlaydi. Bu — Dependency");
        Console.WriteLine("Inversion Principle (abstraksiyaga bog'liqlik) ning amaliy namunasi.");
    }

    // Metod — FAQAT interfeysga (abstraksiyaga) bog'liq, konkret klassga EMAS
    private static void PrintAll(IDictionary<int, Employee> dict)
    {
        foreach (var kvp in dict)
            Console.WriteLine($"   {kvp.Key} -> {kvp.Value}");
    }
}
