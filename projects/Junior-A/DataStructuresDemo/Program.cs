using DataStructuresDemo.Demos;

Console.OutputEncoding = System.Text.Encoding.UTF8;

while (true)
{
    Console.WriteLine();
    Console.WriteLine("================================================");
    Console.WriteLine("   Key-Value Pair Structures - O'QUV DEMO LOYIHASI");
    Console.WriteLine("================================================");
    Console.WriteLine("1 - Dictionary<TKey,TValue>   (asosiy amaliyot)");
    Console.WriteLine("2 - Hashtable                 (eski, non-generic)");
    Console.WriteLine("3 - IDictionary abstraksiyasi  (interfeys sifatida)");
    Console.WriteLine("4 - Performance solishtirish   (List vs Dictionary)");
    Console.WriteLine("0 - Chiqish");
    Console.Write("Tanlovingiz: ");

    var choice = Console.ReadLine();
    Console.WriteLine();

    switch (choice)
    {
        case "1": DictionaryBasicsDemo.Run(); break;
        case "2": HashtableDemo.Run(); break;
        case "3": IDictionaryAbstractionDemo.Run(); break;
        case "4": PerformanceComparisonDemo.Run(); break;
        case "0": return;
        default: Console.WriteLine("Noto'g'ri tanlov, qayta urinib ko'ring."); break;
    }
}
