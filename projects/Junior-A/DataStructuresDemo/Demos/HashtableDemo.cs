using System.Collections;
using DataStructuresDemo.Models;

namespace DataStructuresDemo.Demos;

public static class HashtableDemo
{
    public static void Run()
    {
        Console.WriteLine("--- Hashtable — eski, non-generic kolleksiya ---\n");

        var table = new Hashtable();
        table.Add(1, new Employee { Id = 1, FullName = "Orzibek", Department = "IT" });
        table.Add("key2", "Bu — butunlay boshqa turdagi key va value!"); // Hashtable — key/value turini CHEKLAMAYDI!

        Console.WriteLine("Hashtable — har xil turdagi key/value'ni bitta jadvalda saqlay oladi:");
        // Hashtable — KeyValuePair<K,V> EMAS, DictionaryEntry ishlatadi (eski, non-generic API)!
        foreach (DictionaryEntry entry in table)
            Console.WriteLine($"   Key ({entry.Key.GetType().Name}): {entry.Key} -> Value: {entry.Value}");

        Console.WriteLine("\n[!] TYPE SAFETY yo'qligi muammosi:");
        object raw = table[1]!; // object qaytaradi — CAST SHART!
        var employee = (Employee)raw; // Explicit cast; agar TUR noto'g'ri bo'lsa — InvalidCastException!
        Console.WriteLine($"   Cast qilingandan keyin: {employee}");

        Console.WriteLine("\n[!] Noto'g'ri cast — runtime xatosi misoli:");
        try
        {
            var wrongCast = (int)table["key2"]!; // "key2" ostida string bor, int EMAS!
            Console.WriteLine(wrongCast);
        }
        catch (InvalidCastException ex)
        {
            Console.WriteLine($"   XATO: InvalidCastException -> {ex.Message}");
        }

        Console.WriteLine("\nXULOSA:");
        Console.WriteLine("  Dictionary<TKey,TValue> — GENERIC (compile-time type safety, boxing YO'Q).");
        Console.WriteLine("  Hashtable                — non-generic (runtime cast, VALUE type'lar uchun BOXING sodir bo'ladi).");
        Console.WriteLine("  Zamonaviy kodda Hashtable DEYARLI HECH QACHON ishlatilmasligi kerak — Dictionary<K,V> afzal.");
    }
}
