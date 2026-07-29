# Recursive Algorithms — Divide & Conquer, DP, Greedy, Backtracking, Hashing — Middle D

## 1. Nima? (Ta'rif)

Bu hujjat — asosiy algoritmik paradigmalarni qamrab oladi: **Divide
and Conquer** (bo'l va yengib chiq), **Dynamic Programming**
(dinamik dasturlash), **Greedy** (ochko'z algoritm), **Backtracking**
(orqaga qaytish), va **Hashing** algoritmlari.

## 2. Nima uchun kerak?

Bu paradigmalar — murakkab masalalarni **samarali** yechishning
"andozalari" (patterns). To'g'ri paradigma tanlanmasa — yechim
**eksponensial** vaqt olishi mumkin (masalan, naive Fibonacci —
2^n, DP bilan — n).

## 3. Ichida nima sodir bo'ladi? (Mexanizm)

### 3.1 Divide and Conquer — Merge Sort

```
1. Massivni IKKIGA BO'LISH (Divide)
2. Har yarmini REKURSIV tartiblash (Conquer)
3. Ikki tartiblangan yarmini BIRLASHTIRISH (Combine)
```

```csharp
public static int[] MergeSort(int[] arr)
{
    if (arr.Length <= 1) return arr;

    int mid = arr.Length / 2;
    var left = MergeSort(arr[..mid]);
    var right = MergeSort(arr[mid..]);

    return Merge(left, right);
}

private static int[] Merge(int[] left, int[] right)
{
    var result = new int[left.Length + right.Length];
    int i = 0, j = 0, k = 0;
    while (i < left.Length && j < right.Length)
        result[k++] = left[i] <= right[j] ? left[i++] : right[j++];
    while (i < left.Length) result[k++] = left[i++];
    while (j < right.Length) result[k++] = right[j++];
    return result;
}
```

**Murakkablik:** O(n log n) — har bo'linish darajasi `log n`, har
darajada `n` ta element birlashtiriladi.

### 3.2 Binary Search — O(log n)

```csharp
public static int BinarySearch(int[] sortedArr, int target)
{
    int low = 0, high = sortedArr.Length - 1;
    while (low <= high)
    {
        int mid = low + (high - low) / 2;
        if (sortedArr[mid] == target) return mid;
        if (sortedArr[mid] < target) low = mid + 1;
        else high = mid - 1;
    }
    return -1;
}
```

Har qadamda qidiruv maydoni **YARMIGA** kamayadi — 1,000,000 element
uchun FAQAT ~20 taqqoslash yetarli (2^20 ≈ 1M).

### 3.3 Dynamic Programming — Memoization vs Tabulation

```csharp
// ❌ Naive rekursiya — O(2^n), JUDA SEKIN (bir xil qiymat QAYTA-QAYTA hisoblanadi)
public static long FibNaive(int n) => n <= 1 ? n : FibNaive(n - 1) + FibNaive(n - 2);

// ✅ Memoization (Top-Down) — natijalarni KESHLAB, QAYTA HISOBLASHNI oldini oladi
public static long FibMemo(int n, Dictionary<int, long>? cache = null)
{
    cache ??= new();
    if (n <= 1) return n;
    if (cache.TryGetValue(n, out var cached)) return cached;
    var result = FibMemo(n - 1, cache) + FibMemo(n - 2, cache);
    cache[n] = result;
    return result;
}

// ✅ Tabulation (Bottom-Up) — REKURSIYASIZ, iterativ, XOTIRA SAMARALIROQ
public static long FibTabulation(int n)
{
    if (n <= 1) return n;
    long prev = 0, curr = 1;
    for (int i = 2; i <= n; i++)
        (prev, curr) = (curr, prev + curr);
    return curr;
}
```

```
Naive:        O(2^n) vaqt — n=40 uchun MILLIARDLAB chaqiriq!
Memoization:  O(n) vaqt, O(n) xotira (rekursiya STACK + cache)
Tabulation:   O(n) vaqt, O(1) xotira (FAQAT oxirgi ikki qiymat kerak)
```

### 3.4 Knapsack Problem — DP misoli

```csharp
public static int Knapsack(int[] weights, int[] values, int capacity)
{
    int n = weights.Length;
    var dp = new int[n + 1, capacity + 1];

    for (int i = 1; i <= n; i++)
        for (int w = 0; w <= capacity; w++)
        {
            if (weights[i - 1] <= w)
                dp[i, w] = Math.Max(dp[i - 1, w], values[i - 1] + dp[i - 1, w - weights[i - 1]]);
            else
                dp[i, w] = dp[i - 1, w];
        }

    return dp[n, capacity];
}
```

### 3.5 Greedy Algorithm — har qadamda optimal tanlov

```csharp
// Coin Change (greedy — FAQAT ma'lum tanga qiymatlarida ISHLAYDI!)
public static int CoinChangeGreedy(int[] coins, int amount)
{
    Array.Sort(coins, (a, b) => b - a); // Kattadan kichikka
    int count = 0;
    foreach (var coin in coins)
    {
        count += amount / coin;
        amount %= coin;
    }
    return amount == 0 ? count : -1;
}
```

```
Qachon Greedy ISHLAYDI: coins = [1, 5, 10, 25] (AQSH tangalari) —
HAR DOIM optimal natija beradi (chunki bu tizim "kanonik").

Qachon Greedy ISHLAMAYDI: coins = [1, 3, 4], amount = 6
  Greedy: 4 + 1 + 1 = 3 ta tanga
  OPTIMAL: 3 + 3 = 2 ta tanga (Greedy BU YERDA XATO javob beradi!)

Bunday holatlarda — DP (Dynamic Programming) ISHLATILISHI kerak.
```

### 3.6 Backtracking — N-Queens

```csharp
public static bool SolveNQueens(int[] board, int row, int n)
{
    if (row == n) return true; // BARCHA qirolichalar joylashtirildi

    for (int col = 0; col < n; col++)
    {
        if (IsSafe(board, row, col))
        {
            board[row] = col;               // SINAB KO'RISH
            if (SolveNQueens(board, row + 1, n))
                return true;
            // board[row] YANGI qiymat bilan KEYINGI ITERATSIYADA qayta yoziladi (implicit backtrack)
        }
    }
    return false; // HECH BIRI ISHLAMADI — OLDINGI QADAMGA QAYTISH (rekursiya orqali)
}

private static bool IsSafe(int[] board, int row, int col)
{
    for (int i = 0; i < row; i++)
    {
        if (board[i] == col || Math.Abs(board[i] - col) == row - i)
            return false; // BIR XIL ustun yoki DIAGONAL
    }
    return true;
}
```

Backtracking — har qadamda **"sinab ko'rish"**, agar KEYINGI
qadamlarning HECH BIRI ishlamasa — **orqaga qaytib**, BOSHQA
variantni sinash — Sudoku Solver ham xuddi shu paradigma bilan
yechiladi.

### 3.7 Hashing Algorithms

```
Hash function — DETERMINISTIK (bir xil kirish — HAR DOIM bir xil
                 natija), TEZ hisoblanadigan funksiya

Collision — IKKI xil kirish BIR XIL hash beradi:
  Yechim: Chaining (bir xil bucket'da LIST) yoki Open Addressing
          (keyingi bo'sh joyni QIDIRISH)

SHA256/SHA512 — CRYPTOGRAPHIC hash — collision topish DEYARLI
                 IMKONSIZ (hisoblash jihatidan)
BCrypt         — parol uchun MAXSUS, ATAYLAB SEKIN hash (salt bilan)
```

## 4. Kod — Big O solishtirish jadvali

| Algoritm | Vaqt murakkabligi | Xotira |
|---|---|---|
| Merge Sort | O(n log n) | O(n) |
| Binary Search | O(log n) | O(1) |
| Fibonacci (naive) | O(2^n) | O(n) (stack) |
| Fibonacci (DP tabulation) | O(n) | O(1) |
| Knapsack (DP) | O(n × capacity) | O(n × capacity) |
| N-Queens (backtracking) | O(n!) (eng yomon holat) | O(n) |
| Hash table lookup | O(1) o'rtacha | O(n) |

## 5. Qachon ishlatish kerak?

| Vaziyat | Yechim |
|---|---|
| Katta massivni tartiblash | Merge Sort / Quick Sort |
| Tartiblangan massivda qidirish | Binary Search |
| Takrorlanuvchi sub-muammolar (Fibonacci, Knapsack) | Dynamic Programming |
| Har qadamda "lokal optimal" YETARLI (masalan standart tanga tizimi) | Greedy |
| Barcha variantni sinash kerak (Sudoku, N-Queens) | Backtracking |
| Tez qidiruv/unique tekshiruv | Hashing (`HashSet`/`Dictionary`) |

## 6. Muhim nuqtalar

- Greedy — **HAR DOIM** optimal natija bermaydi — faqat "greedy-choice
  property" bajarilgan masalalarda ishlaydi.
- Memoization (rekursiv) va Tabulation (iterativ) — bir xil
  natija beradi, lekin Tabulation odatda **kamroq xotira** ishlatadi
  (stack overflow xavfi yo'q).
- Backtracking — eng yomon holatda **eksponensial** vaqt olishi
  mumkin, lekin **pruning** (noto'g'ri yo'lni erta tashlab yuborish)
  bilan amaliy jihatdan tez ishlaydi.

## 7. Imtihon savollari

1. Divide and Conquer paradigmasining 3 bosqichini ayting va Merge
   Sort orqali tushuntiring.
2. Memoization va Tabulation orasidagi farq nima?
3. Greedy algoritm qachon ishlamaydi — misol bilan tushuntiring
   (Coin Change).
4. Backtracking N-Queens masalasida qanday ishlaydi?
5. Hash collision nima va u qanday hal qilinadi?
6. Nima uchun BCrypt ataylab "sekin" qilib yaratilgan?
