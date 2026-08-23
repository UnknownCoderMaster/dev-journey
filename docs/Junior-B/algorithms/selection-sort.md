# Sorting Algorithm — Selection Sort — Junior B

## 1. What (Nima?)

**Selection Sort** — massivni tartiblash algoritmi: HAR ITERATSIYADA
**TARTIBLANMAGAN QISMDAN ENG KICHIK (yoki ENG KATTA) ELEMENTNI
TOPIB**, uni TARTIBLANGAN QISM OXIRIGA "TANLAB" (select) QO'YADI.

## 2. Real hayot analogiyasi

**Sinf jurnalidagi o'quvchilarni bo'y bo'yicha SAFGA TIZISH.**
O'qituvchi (algoritm) — BUTUN SINFNI (tartiblanmagan massiv)
AYLANIB CHIQIB, **ENG PASTBO'YLI** o'quvchini TOPADI VA UNI
SAFNING BOSHIGA CHIQARADI. KEYIN QOLGAN o'quvchilar ORASIDAN YANA
ENG PASTBO'YLINI TOPIB, IKKINCHI O'RINGA QO'YADI — VA HOKAZO.
HAR "AYLANISH"DA — FAQAT **BITTA** O'QUVCHI JOYINI TOPADI.

## 3. Why (Nega kerak?)

Selection Sort — **AMALIYOTDA KAMDAN-KAM ISHLATILADI** (Insertion
Sort/Quick Sort ko'pincha AFZAL), LEKIN u — **ALGORITMIK FIKRLASH
ASOSI** sifatida O'QITILADI, chunki:

1. **TUSHUNISH ENG OSON** algoritmlardan biri — SODDA MANTIQ
2. **XOTIRA almashinuvlari MINIMAL** — HAR ITERATSIYADA FAQAT
   **BITTA SWAP** (bu — YOZISH QIMMAT BO'LGAN xotira — masalan
   FLASH MEMORY — bilan ishlashda AFZALLIK bo'lishi mumkin)
3. **IN-PLACE** — QO'SHIMCHA massiv KERAK EMAS (O(1) space)

**Merge Sort/Quick Sort bilan solishtirish:** ULAR O(n log n),
Selection Sort — O(n²) — KATTA MA'LUMOTLAR uchun **SEZILARLI
SEKINROQ**, shuning uchun PRODUCTION kodda .NET'ning O'ZINING
`Array.Sort()` (Introspective Sort — Quick+Heap+Insertion
KOMBINATSIYASI) ISHLATILADI.

## 4. Internals (Ichki mexanizm)

### Algoritm QADAMLARI

```
Massiv: [64, 25, 12, 22, 11]

1-ITERATSIYA (i=0): [0..4] orasidan ENG KICHIK — 11 (indeks 4)
  11 ni 0-POZITSIYAGA SWAP: [11, 25, 12, 22, 64]

2-ITERATSIYA (i=1): [1..4] orasidan ENG KICHIK — 12 (indeks 2)
  12 ni 1-POZITSIYAGA SWAP: [11, 12, 25, 22, 64]

3-ITERATSIYA (i=2): [2..4] orasidan ENG KICHIK — 22 (indeks 3)
  22 ni 2-POZITSIYAGA SWAP: [11, 12, 22, 25, 64]

4-ITERATSIYA (i=3): [3..4] orasidan ENG KICHIK — 25 (allaqachon TO'G'RI joyda)
  [11, 12, 22, 25, 64] — TARTIBLANGAN!
```

### Vaqt murakkabligi — NIMA UCHUN O(n²)

```
TASHQI TSIKL — n MARTA (HAR ELEMENT uchun "TO'G'RI JOY" QIDIRISH)
ICHKI TSIKL — O'RTACHA n/2 MARTA (QOLGAN ELEMENTLAR ORASIDAN
              ENG KICHIGINI QIDIRISH)

Jami TAQQOSLASHLAR: n + (n-1) + (n-2) + ... + 1 = n(n-1)/2 ≈ n²/2

Big O NOTATSIYASIDA — KONSTANTALAR (1/2) TASHLAB YUBORILADI:
O(n²) — BEST, AVERAGE, WORST CASE — BARCHASI BIR XIL O(n²)!
(Massiv ALLAQACHON TARTIBLANGAN bo'lsa HAM — ALGORITM BARIBIR
HAR ELEMENTNI TEKSHIRADI — bu Insertion Sort'dan FARQI, U
TARTIBLANGAN massivda TEZROQ ISHLAYDI)
```

### Xotira murakkabligi — O(1), IN-PLACE

```
Selection Sort — QO'SHIMCHA massiv YARATMAYDI, FAQAT ASL massiv
ICHIDA ELEMENTLARNI "SWAP" QILADI — SHUNING UCHUN Space
Complexity — O(1) (FAQAT bir NECHTA VAQTINCHALIK o'zgaruvchi:
i, j, minIndex).
```

### STABLE emasligi

```
Stable Sort — BIR XIL QIYMATGA EGA elementlarning NISBIY TARTIBI
              SAQLANADI

Selection Sort — STABLE EMAS! SWAP operatsiyasi — ba'zan BIR XIL
QIYMATGA EGA elementlarning ASL TARTIBINI BUZISHI mumkin:

Misol: [(5,A), (3,B), (5,C)] — 5 ikkita bor
Tartiblashdan KEYIN: [(3,B), (5,C), (5,A)] — (5,A) va (5,C)
NING TARTIBI ALMASHDI! (ASLIDA A OLDIN edi, ENDI C OLDIN)
```

## 5. Code (Amaliy kod)

```csharp
public static void SelectionSort(int[] arr)
{
    int n = arr.Length;

    for (int i = 0; i < n - 1; i++)
    {
        int minIndex = i;

        // TARTIBLANMAGAN QISMDAN ENG KICHIK ELEMENTNI QIDIRISH
        for (int j = i + 1; j < n; j++)
        {
            if (arr[j] < arr[minIndex])
                minIndex = j;
        }

        // ENG KICHIK ELEMENTNI JORIY POZITSIYAGA SWAP QILISH
        if (minIndex != i)
            (arr[i], arr[minIndex]) = (arr[minIndex], arr[i]);
    }
}
```

```csharp
// Generic versiya — ISTALGAN IComparable TUR uchun (masalan Employee)
public static void SelectionSort<T>(T[] arr) where T : IComparable<T>
{
    for (int i = 0; i < arr.Length - 1; i++)
    {
        int minIndex = i;
        for (int j = i + 1; j < arr.Length; j++)
        {
            if (arr[j].CompareTo(arr[minIndex]) < 0)
                minIndex = j;
        }
        if (minIndex != i)
            (arr[i], arr[minIndex]) = (arr[minIndex], arr[i]);
    }
}

// Ishlatish — Employee'larni MAOSH bo'yicha TARTIBLASH
public class Employee : IComparable<Employee>
{
    public string FullName { get; set; } = null!;
    public decimal Salary { get; set; }
    public int CompareTo(Employee? other) => Salary.CompareTo(other?.Salary);
}
```

## 6. Keng tarqalgan xatolar / noto'g'ri tushunchalar

```
❌ "Selection Sort — STABLE" — NOTO'G'RI! Yuqoridagi 4-bo'limdagi
   misolga qarang — SWAP operatsiyasi BIR XIL QIYMATLARNING
   NISBIY TARTIBINI BUZISHI mumkin.

❌ "Selection Sort — TARTIBLANGAN massivda TEZROQ ISHLAYDI" —
   NOTO'G'RI! Insertion Sort'dan FARQLI, Selection Sort — HAR
   DOIM O(n²) TAQQOSLASH BAJARADI, MASSIV HOLATIDAN QAT'I NAZAR
   (BEST CASE HAM O(n²)).

❌ "Selection Sort — KO'P XOTIRA ISHLATADI" — YO'Q! Bu — IN-PLACE
   algoritm, O(1) QO'SHIMCHA XOTIRA (faqat BIR NECHTA
   o'zgaruvchi).

❌ "n TA element uchun n² MARTA SWAP QILINADI" — NOTO'G'RI!
   TAQQOSLASH — O(n²) MARTA, LEKIN SWAP — FAQAT n MARTA (HAR
   TASHQI ITERATSIYADA BIR MARTA) — BU, Selection Sort'ning
   YOZISH-ISKALADIGAN xotira (masalan Flash) uchun AFZALLIGI.
```

## 7. Exam (Interview savollari)

**1. Selection Sort'ning VAQT murakkabligi NIMA UCHUN HAR DOIM
O(n²), TARTIBLANGAN massivda HAM?**
Algoritm HAR ITERATSIYADA — QOLGAN BARCHA elementlarni TEKSHIRIB,
ENG KICHIGINI QIDIRADI — MASSIV ALLAQACHON TARTIBLANGAN bo'lsa
HAM, BU QIDIRUV JARAYONI O'ZGARMAYDI (HECH QANDAY "ERTA TO'XTASH"
mexanizmi YO'Q).

**2. Selection Sort STABLE emasligini MISOL bilan TUSHUNTIRING.**
Ikkita BIR XIL QIYMATGA EGA element (masalan bir xil maoshli
IKKI xodim) — SWAP operatsiyasi TUFAYLI, ULARNING ASL NISBIY
TARTIBI BUZILISHI MUMKIN (masalan, dastlab BIRINCHI BO'LGAN
element — TARTIBLASHDAN KEYIN IKKINCHI bo'lib QOLISHI mumkin).

**3. Selection Sort va Insertion Sort orasidagi ASOSIY FARQ nima?**
Selection Sort — HAR ITERATSIYADA "ENG KICHIK"NI QIDIRIB TOPADI
(HAR DOIM O(n²), massiv holatidan qat'i nazar). Insertion Sort —
HAR ELEMENTNI TARTIBLANGAN QISMGA "JOYLASHTIRADI" (BEST CASE —
O(n), agar massiv ALLAQACHON DEYARLI TARTIBLANGAN bo'lsa).

**4. Nima uchun Selection Sort — YOZISH QIMMAT bo'lgan XOTIRA
(masalan Flash Memory) uchun AFZAL bo'lishi mumkin?**
Selection Sort — FAQAT n MARTA (HAR TASHQI ITERATSIYADA BIR
MARTA) SWAP BAJARADI — bu, KO'P algoritmlarga (masalan Bubble
Sort, O(n²) SWAP) NISBATAN, YOZISH OPERATSIYALARI SONINI SEZILARLI
KAMAYTIRADI.

**5. `.NET`ning `Array.Sort()` metodi Selection Sort'ni ISHLATADIMI?**
Yo'q. `.NET`ning `Array.Sort()` — **Introspective Sort** (Introsort)
ISHLATADI — bu, Quick Sort (ASOSIY), Heap Sort (Quick Sort
CHUQURLIGI ORTIB KETSA, YOMON HOLATNI OLDINI OLISH uchun) va
Insertion Sort (KICHIK MASSIVLAR — ~16 element — uchun TEZROQ)
KOMBINATSIYASI — O(n log n) KAFOLATLANADI.
