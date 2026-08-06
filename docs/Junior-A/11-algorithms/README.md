# Binary Search, Brute Force, Big O — Junior A

## 1. Nima? (Ta'rif)

**Brute Force** — barcha mumkin bo'lgan variantlarni **ketma-ket**
sinab, to'g'ri javobni topish strategiyasi. **Binary Search** —
**tartiblangan** massivda, qidiruv maydonini har qadamda **yarmiga**
kamaytirib qidirish algoritmi. **Big O Notation** — algoritmning
kirish hajmi o'sishi bilan **vaqt/xotira** qanday o'sishini
ifodalovchi matematik yozuv.

## 2. Nima uchun kerak?

To'g'ri algoritm tanlamaslik — kichik ma'lumotda **sezilmaydi**,
lekin katta hajmda (masalan, 1,000,000 xodim) — **soniyalar** o'rniga
**daqiqalar/soatlar** talab qilishi mumkin. Big O — bu farqni
**oldindan bashorat qilish** imkonini beradi.

## 3. Ichida nima sodir bo'ladi? (Mexanizm)

### 3.1 Brute Force — barcha variantlarni sinash

```csharp
// Misol: massivda ikkita element yig'indisi = target bo'lgan JUFTLIKNI topish
public static (int, int)? FindPairBruteForce(int[] arr, int target)
{
    for (int i = 0; i < arr.Length; i++)
        for (int j = i + 1; j < arr.Length; j++) // HAR JUFTLIKNI sinash
            if (arr[i] + arr[j] == target)
                return (arr[i], arr[j]);
    return null;
}
```

```
Vaqt murakkabligi: O(n²) — TASHQI loop n marta, ICHKI loop (o'rtacha)
                    n marta — n × n = n²

1,000 element uchun    — 1,000,000 taqqoslash (TEZ)
1,000,000 element uchun — 1,000,000,000,000 taqqoslash (SOATLAB!)
```

**Qachon Brute Force ishlatiladi:** kichik ma'lumot hajmi (n < 1000),
yoki masala **oddiy**, optimallashtirish **shart emas** bo'lganda
(early optimization — vaqt isrofi bo'lishi mumkin).

### 3.2 Binary Search — ikkilik qidirish

**Shart:** massiv **tartiblangan** bo'lishi SHART.

```csharp
// Iterativ implementatsiya
public static int BinarySearchIterative(int[] sortedArr, int target)
{
    int left = 0, right = sortedArr.Length - 1;

    while (left <= right)
    {
        int mid = left + (right - left) / 2; // (left + right) / 2 EMAS — OVERFLOW xavfi!

        if (sortedArr[mid] == target) return mid;
        if (sortedArr[mid] < target) left = mid + 1;  // O'NG yarimda qidirish
        else right = mid - 1;                          // CHAP yarimda qidirish
    }

    return -1; // Topilmadi
}

// Rekursiv implementatsiya
public static int BinarySearchRecursive(int[] arr, int target, int left, int right)
{
    if (left > right) return -1;

    int mid = left + (right - left) / 2;

    if (arr[mid] == target) return mid;
    if (arr[mid] < target) return BinarySearchRecursive(arr, target, mid + 1, right);
    return BinarySearchRecursive(arr, target, left, mid - 1);
}
```

```
Massiv: [1, 3, 5, 7, 9, 11, 13, 15], target = 11

1-qadam: left=0, right=7, mid=3 → arr[3]=7 < 11 → left=4
2-qadam: left=4, right=7, mid=5 → arr[5]=11 = 11 → TOPILDI! (index 5)

Har qadamda — QIDIRUV MAYDONI YARMIGA KAMAYADI: 8 → 4 → 2 → 1
```

### 3.3 `left`, `right`, `mid` — qanday hisoblanadi

```
left  — QIDIRUV oralig'ining BOSHI
right — QIDIRUV oralig'ining OXIRI
mid   — o'RTA nuqta: left + (right - left) / 2

⚠️ (left + right) / 2 — NAZARIY jihatdan bir xil, LEKIN agar
   left va right JUDA KATTA sonlar bo'lsa — YIG'INDI int.MaxValue'DAN
   OSHIB KETISHI (INTEGER OVERFLOW) mumkin!

✅ left + (right - left) / 2 — OVERFLOW XAVFISIZ (chunki
   (right - left) — HAR DOIM KICHIKROQ son)
```

### 3.4 Off-by-one xatolari — qanday oldini olish

```
❌ Umumiy xatolar:
   while (left < right)   — OXIRGI elementni O'TKAZIB YUBORISHI mumkin
   right = mid            — mid'ni QAYTA TEKSHIRISHGA olib kelishi mumkin (CHEKSIZ LOOP xavfi!)

✅ TO'G'RI pattern:
   while (left <= right)  — left VA right BIR XIL bo'lganda HAM tekshirish
   left = mid + 1         — mid'ni O'TKAZIB YUBORISH (allaqachon tekshirilgan)
   right = mid - 1        — mid'ni O'TKAZIB YUBORISH
```

### 3.5 `Array.BinarySearch()` — .NET built-in

```csharp
int[] sortedArr = { 1, 3, 5, 7, 9, 11 };
int index = Array.BinarySearch(sortedArr, 7); // → 3

// List<T> uchun
var list = new List<int> { 1, 3, 5, 7, 9 };
int idx = list.BinarySearch(5); // → 2

// Topilmasa — MANFIY qiymat qaytaradi (bitwise complement — qayerga
// QO'YISH kerakligini bildiradi)
int notFound = Array.BinarySearch(sortedArr, 6); // → manfiy son
```

### 3.6 O(log n) — nima uchun

```
n = 1,000,000 element:

Brute Force (chiziqli qidiruv): ENG YOMON holatda 1,000,000 QADAM
Binary Search: log2(1,000,000) ≈ 20 QADAM!

Har qadamda YARMIGA kamayadi:
1,000,000 → 500,000 → 250,000 → ... → 1 (taxminan 20 marta bo'linadi)

Bu — 2^20 ≈ 1,048,576 (deyarli 1 million) — shuning uchun
log2(1,000,000) ≈ 20
```

### 3.7 Real use case — ID bo'yicha qidirish, sorted list

```csharp
// ERP'da — TARTIBLANGAN xodim ID ro'yxatida TEZ qidiruv
var sortedEmployeeIds = employees.Select(e => e.Id).OrderBy(id => id).ToArray();
int position = Array.BinarySearch(sortedEmployeeIds, targetId);

// ⚠️ MUHIM: Agar ma'lumot DB'dan kelsa — Binary Search'ni QO'LDA
// implement qilish O'RNIGA, DB INDEKS (B-Tree, aslida Binary
// Search'ga O'XSHASH g'oya) ishlatilishi TAVSIYA ETILADI —
// docs/Middle-D/40-indexing'da batafsil.
```

### 3.8 Big O notation — barcha darajalar

```
O(1)       — Konstant — Dictionary["key"], arr[5]
O(log n)   — Logarifmik — Binary Search
O(n)       — Chiziqli — foreach, List.Contains()
O(n log n) — Merge Sort, Quick Sort (o'rtacha)
O(n²)      — Kvadratik — ICHMA-ICH loop (Bubble Sort, Brute Force juftlik)
O(2^n)     — Eksponensial — naive Fibonacci rekursiya
O(n!)      — Faktorial — barcha permutatsiyalarni sanash (Traveling Salesman brute force)
```

```
Grafik (o'sish tezligi, KATTADAN KICHIKKA):
n! > 2^n > n² > n log n > n > log n > 1
```

### 3.9 Space complexity — xotira murakkabligi

```csharp
// O(1) space — QO'SHIMCHA xotira KERAK EMAS (in-place)
public static void ReverseInPlace(int[] arr)
{
    int left = 0, right = arr.Length - 1;
    while (left < right)
    {
        (arr[left], arr[right]) = (arr[right], arr[left]);
        left++; right--;
    }
}

// O(n) space — YANGI massiv YARATILADI
public static int[] ReverseNewArray(int[] arr) => arr.Reverse().ToArray();
```

Binary Search (iterativ) — **O(1)** space (faqat 3 ta o'zgaruvchi:
left, right, mid). Binary Search (rekursiv) — **O(log n)** space
(rekursiya STACK — HAR chaqiruv uchun ALOHIDA STACK FRAME).

## 4. Kod — to'liq solishtirma misol

```csharp
public static class SearchBenchmark
{
    public static int LinearSearch(int[] arr, int target) // O(n)
    {
        for (int i = 0; i < arr.Length; i++)
            if (arr[i] == target) return i;
        return -1;
    }

    public static int BinarySearch(int[] sortedArr, int target) // O(log n)
    {
        int left = 0, right = sortedArr.Length - 1;
        while (left <= right)
        {
            int mid = left + (right - left) / 2;
            if (sortedArr[mid] == target) return mid;
            if (sortedArr[mid] < target) left = mid + 1;
            else right = mid - 1;
        }
        return -1;
    }
}
```

## 5. Qachon ishlatish kerak?

| Vaziyat | Yechim |
|---|---|
| Kichik hajm (n < 100), oddiy masala | Brute Force |
| Tartiblangan, katta hajmli ma'lumotda qidiruv | Binary Search |
| Tartiblanmagan ma'lumot, kamdan-kam qidiriladi | Chiziqli qidiruv (Linear) |
| Tez-tez qidiriladigan, DB'dagi ma'lumot | DB Index (B-Tree) |
| Tez-tez qidiriladigan, xotiradagi ma'lumot | `HashSet`/`Dictionary` (O(1)) |

## 6. Muhim nuqtalar

- Binary Search — **FAQAT tartiblangan** massivda ishlaydi —
  tartiblanmagan massivda ishlatilsa **noto'g'ri** natija berishi
  mumkin.
- `(left + right) / 2` — integer overflow xavfi bor katta massivlarda
  — `left + (right - left) / 2` xavfsizroq.
- Big O — **eng yomon holat** (worst case)ni ifodalaydi, odatda —
  amaliy o'rtacha holat biroz farq qilishi mumkin.

## 7. Imtihon savollari

1. Binary Search ishlashi uchun qanday shart bajarilishi kerak?
2. `(left + right) / 2` va `left + (right - left) / 2` orasidagi
   farq nima?
3. Off-by-one xatosi Binary Search'da qanday yuzaga kelishi mumkin?
4. Binary Search'ning vaqt murakkabligi nima uchun O(log n)?
5. Iterativ va rekursiv Binary Search — space complexity nuqtai
   nazaridan qanday farq qiladi?
6. Brute Force qachon oqilona tanlov hisoblanadi?
7. Big O notation nima va u nima uchun "eng yomon holat"ni
   ifodalaydi?
