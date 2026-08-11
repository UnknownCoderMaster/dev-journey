# Key-Value Pair Structures — O'quv Demo Loyihasi

Bu ConsoleApp — quyidagi mavzuni **amaliy misollar** bilan o'rgatish
uchun yaratilgan (mos hujjat: `docs/Junior-A/21-data-structures`):

**Key Value Pair structures (IDictionary, Dictionary, Hashtable)**

1. **Dictionary<TKey,TValue> asoslari** — Add, indexer, `TryGetValue`
   (xavfsiz) vs indexer (`KeyNotFoundException` xavfi), `ContainsKey`,
   `Remove`, capacity.
2. **Hashtable** — eski, non-generic kolleksiya; boxing/type-safety
   muammolarini jonli misolda ko'rsatish (`InvalidCastException`).
3. **IDictionary abstraksiyasi** — bitta metodning `Dictionary` va
   `SortedDictionary`ni bir xilda qabul qilishi (Dependency Inversion
   amaliyoti).
4. **Performance solishtirish** — `List<T>.Contains()` (O(n)) va
   `Dictionary.ContainsKey()` (O(1)) ni `Stopwatch` bilan real vaqtda
   o'lchash.

## Ishga tushirish

```bash
cd projects/Junior-A/DataStructuresDemo
dotnet run
```

Konsolda chiqqan menyudan (1-4) kerakli demoni tanlang.

## Loyiha tuzilmasi

```
Models/   — Employee (demo uchun oddiy model)
Demos/    — har bir mavzu uchun alohida statik klass
Program.cs — konsol menyu
```
