using System.Diagnostics;

namespace DataStructuresDemo.Demos;

public static class PerformanceComparisonDemo
{
    public static void Run()
    {
        Console.WriteLine("--- Performance solishtirish: List<T>.Contains() vs Dictionary.ContainsKey() ---\n");

        const int itemCount = 100_000;
        const int searchCount = 5_000;

        var list = new List<int>(itemCount);
        var dictionary = new Dictionary<int, bool>(itemCount);

        for (int i = 0; i < itemCount; i++)
        {
            list.Add(i);
            dictionary[i] = true;
        }

        var random = new Random(42); // Bir xil natija uchun FIXED seed
        var searchValues = Enumerable.Range(0, searchCount).Select(_ => random.Next(itemCount)).ToArray();

        var sw = Stopwatch.StartNew();
        foreach (var value in searchValues)
            list.Contains(value); // O(n) — har safar massiv boshidan qidiradi
        sw.Stop();
        var listTime = sw.ElapsedMilliseconds;

        sw.Restart();
        foreach (var value in searchValues)
            dictionary.ContainsKey(value); // O(1) — hash orqali to'g'ridan topadi
        sw.Stop();
        var dictTime = sw.ElapsedMilliseconds;

        Console.WriteLine($"Ma'lumot hajmi: {itemCount:N0} ta element, {searchCount:N0} marta qidiruv\n");
        Console.WriteLine($"List<int>.Contains()      -> {listTime,6} ms  (O(n) — chiziqli qidiruv)");
        Console.WriteLine($"Dictionary.ContainsKey()  -> {dictTime,6} ms  (O(1) — hash asosida)");

        if (dictTime > 0)
            Console.WriteLine($"\nDictionary — taxminan {(double)listTime / dictTime:N0} marta tezroq!");
        else
            Console.WriteLine("\nDictionary shu qadar tez ishladiki, o'lchash uchun vaqt deyarli 0 ms bo'ldi.");

        Console.WriteLine("\nXULOSA: Ma'lumot hajmi qancha katta bo'lsa, List va Dictionary orasidagi");
        Console.WriteLine("performance farqi shuncha sezilarli bo'ladi. Tez-tez qidiruv kerak bo'lsa —");
        Console.WriteLine("Dictionary/HashSet — List'dan deyarli har doim afzal.");
    }
}
