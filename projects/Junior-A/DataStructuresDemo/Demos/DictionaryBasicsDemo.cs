using DataStructuresDemo.Models;

namespace DataStructuresDemo.Demos;

public static class DictionaryBasicsDemo
{
    public static void Run()
    {
        Console.WriteLine("--- Dictionary<TKey, TValue> — asosiy amaliyot ---\n");

        // Dictionary<int, Employee> — KEY (int, xodim ID) orqali TEZ (O(1)) qidiruv uchun
        var employees = new Dictionary<int, Employee>();

        // === Add / Indexer ===
        employees.Add(1, new Employee { Id = 1, FullName = "Orzibek Toshmatov", Department = "IT" });
        employees[2] = new Employee { Id = 2, FullName = "Dilnoza Karimova", Department = "HR" }; // Indexer — Add YOKI Update
        employees[3] = new Employee { Id = 3, FullName = "Aziz Yusupov", Department = "IT" };

        Console.WriteLine("Barcha xodimlar (Dictionary bo'ylab iteratsiya):");
        foreach (KeyValuePair<int, Employee> kvp in employees)
            Console.WriteLine($"   Key={kvp.Key} -> {kvp.Value}");

        // === TryGetValue — XAVFSIZ o'qish (Exception TASHLAMAYDI) ===
        Console.WriteLine("\nTryGetValue bilan qidirish (ID=2):");
        if (employees.TryGetValue(2, out var found))
            Console.WriteLine($"   Topildi: {found}");
        else
            Console.WriteLine("   Topilmadi");

        Console.WriteLine("\nTryGetValue bilan MAVJUD BO'LMAGAN ID (999) qidirish:");
        if (!employees.TryGetValue(999, out _))
            Console.WriteLine("   Topilmadi (Exception TASHLANMADI — bu TryGetValue'ning AFZALLIGI!)");

        // === ContainsKey ===
        Console.WriteLine($"\nContainsKey(1): {employees.ContainsKey(1)}");
        Console.WriteLine($"ContainsKey(999): {employees.ContainsKey(999)}");

        // === Indexer bilan MAVJUD BO'LMAGAN KEY — XATOLIK! ===
        Console.WriteLine("\n[!] employees[999] — mavjud bo'lmagan KEY bilan indexer chaqirish:");
        try
        {
            var bad = employees[999];
            Console.WriteLine(bad); // Bu qatorga hech qachon YETIB kelmaydi
        }
        catch (KeyNotFoundException ex)
        {
            Console.WriteLine($"   XATO: KeyNotFoundException -> {ex.Message}");
            Console.WriteLine("   XULOSA: Key mavjudligiga ISHONCH bo'lmasa — HAR DOIM TryGetValue ishlating!");
        }

        // === Remove ===
        employees.Remove(3);
        Console.WriteLine($"\nID=3 o'chirildi. Qolgan xodimlar soni: {employees.Count}");

        // === Capacity oldindan belgilash (performance) ===
        var bigDictionary = new Dictionary<int, Employee>(capacity: 10_000);
        Console.WriteLine($"\nCapacity bilan yaratilgan bo'sh Dictionary (elementlar hali yo'q, Count={bigDictionary.Count}):");
        Console.WriteLine("Agar hajm OLDINDAN ma'lum bo'lsa — capacity berish, ICHKI massivni QAYTA-QAYTA");
        Console.WriteLine("kattalashtirishni (resize) OLDINI OLADI (performance foyda).");
    }
}
