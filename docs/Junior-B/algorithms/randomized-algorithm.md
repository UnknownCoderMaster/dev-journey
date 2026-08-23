# Randomized Algorithm — Junior B

## 1. What (Nima?)

**Randomized Algorithm** — bajarilishi davomida **TASODIFIY
(random) qiymatlardan** foydalanadigan algoritm — bu tasodifiylik,
algoritmning **natijasiga** (Las Vegas turi) yoki **vaqt
murakkabligiga** (Monte Carlo turi) ta'sir qilishi mumkin.

## 2. Real hayot analogiyasi

**Las Vegas algoritmi — "kalitni TOPGUNCHA QIDIRISH".** Siz
uydan CHIQAYOTGANDA, KALITNI QAYERGA QO'YGANINGIZNI ESLAY OLMAYSIZ.
XONALARNI **TASODIFIY TARTIBDA** TEKSHIRASIZ (har safar BOSHQA
TARTIBDA) — LEKIN OXIR-OQIBAT KALITNI **ANIQ TOPASIZ** (natija
DOIM TO'G'RI, FAQAT VAQT o'zgaruvchan).

**Monte Carlo algoritmi — "TAOMNING TATIB KO'RISH ORQALI SIFATINI
BAHOLASH".** Katta QOZONDAN OSH TAYYORLANGANDA, SIZ **BIR NECHTA
TASODIFIY QOSHIQ** OLIB TATIB KO'RASIZ (BUTUN QOZONNI EMAS) —
NATIJA **TEZ** CHIQADI, LEKIN 100% ANIQLIKKA KAFOLAT YO'Q
(EHTIMOLLIK bilan "OSH YAXSHI" DEYSIZ).

## 3. Why (Nega kerak?)

Ba'zi masalalarda — **DETERMINISTIK** (tasodifsiz) algoritm **ENG
YOMON holatda** (worst case) JUDA SEKIN ISHLAYDI (masalan Quick
Sort — tartiblangan massivda O(n²) bo'lishi mumkin), LEKIN
TASODIFIYLIK QO'SHILSA — **O'RTACHA HOLAT** KAFOLATLANADI, "yomon
holat" EHTIMOLI DEYARLI NOLGA TENG bo'lib qoladi.

**Load Balancing'da real misol:** Server so'rovlarni QAYSI
BACKEND'GA YUBORISHNI TANLASHDA — DOIM "BIRINCHI SERVER"GA
YUBORISH O'RNIGA, **TASODIFIY** TANLASH — YUKNI TENGROQ TAQSIMLAYDI
(ayniqsa Round Robin'ning "PATTERN" MUAMMOLARIDAN QOCHISH uchun).

## 4. Internals (Ichki mexanizm)

### Las Vegas vs Monte Carlo — RASMIY farq

```
Las Vegas Algorithm:
  - Bajarilish VAQTI — O'ZGARUVCHAN (RANDOM)
  - NATIJA — DOIM TO'G'RI (100% ANIQ)
  Misol: Randomized Quick Sort, Randomized Search

Monte Carlo Algorithm:
  - Bajarilish VAQTI — ODATDA BELGILANGAN (FIXED)
  - NATIJA — EHTIMOLLIK bilan TO'G'RI (100% EMAS)
  Misol: Miller-Rabin PRIMALITY TEST, Monte Carlo SIMULYATSIYA
```

### `System.Random` — PSEUDO-RANDOM GENERATOR (PRNG)

```
.NET'dagi Random — HAQIQIY "TASODIFIY" EMAS! Bu — "Pseudo-Random
Number Generator" (PRNG) — MATEMATIK FORMULA (masalan .NET 6+ da
xoshiro256** algoritmi) ASOSIDA, "SEED" (BOSHLANG'ICH QIYMAT)DAN
KETMA-KET SONLAR GENERATSIYA QILADI.

BIR XIL SEED — HAR DOIM BIR XIL KETMA-KETLIKNI BERADI (bu —
TEST QILISH uchun FOYDALI — DETERMINISTIK "tasodifiylik"):

var r1 = new Random(42);
var r2 = new Random(42);
r1.Next(); // → 1015745719
r2.Next(); // → 1015745719 (BIR XIL!)
```

```
⚠️ System.Random — THREAD-SAFE EMAS! Bir nechta thread BIR XIL
Random OBYEKTIDAN PARALLEL foydalansa — ICHKI HOLATI (state)
BUZILISHI mumkin. .NET 6+ da Random.Shared — THREAD-SAFE,
STATIK instance TAQDIM ETADI.
```

### Kriptografik xavfsiz RANDOM — `RandomNumberGenerator`

```
System.Random — BASHORAT QILINISHI MUMKIN (agar SEED yoki OLDINGI
NATIJALAR MA'LUM bo'lsa) — PAROL, TOKEN, API KEY GENERATSIYA
QILISHDA ISHLATILMASLIGI kerak!

System.Security.Cryptography.RandomNumberGenerator — OS DARAJASIDAGI
"ENTROPY" MANBALARIDAN (masalan sichqoncha harakati, DISK I/O
VAQTI) foydalanadi — BASHORAT QILIB BO'LMAYDI, KRIPTOGRAFIK
JIHATDAN XAVFSIZ.
```

### Randomized Quick Sort — nima uchun "YOMON HOLAT"NI OLDINI OLADI

```
Oddiy Quick Sort — PIVOT sifatida DOIM BIRINCHI (yoki OXIRGI)
ELEMENTNI TANLASA — TARTIBLANGAN (yoki DEYARLI TARTIBLANGAN)
massivda — HAR BO'LINISH "1 ta va n-1 ta" bo'lakka BO'LINADI —
O(n²) natija BERADI (ENG YOMON holat).

Randomized Quick Sort — PIVOT'NI TASODIFIY TANLAYDI — BU, HAR
QANDAY KIRISH MA'LUMOTI UCHUN, "YOMON HOLAT"GA TUSHISH EHTIMOLINI
DEYARLI NOLGA TUSHIRADI — O'RTACHA O(n log n) KAFOLATLANADI
(garchi NAZARIY jihatdan ENG YOMON HOLAT HALI HAM MAVJUD BO'LSA HAM).
```

## 5. Code (Amaliy kod)

```csharp
// Random.Shared — .NET 6+, THREAD-SAFE, HAR SAFAR YANGI Random YARATISH SHART EMAS
int diceRoll = Random.Shared.Next(1, 7); // 1 dan 6 gacha

// Fisher-Yates Shuffle — massivni TASODIFIY ARALASHTIRISH (O(n))
public static void Shuffle<T>(T[] array)
{
    for (int i = array.Length - 1; i > 0; i--)
    {
        int j = Random.Shared.Next(i + 1);
        (array[i], array[j]) = (array[j], array[i]);
    }
}
```

```csharp
// Randomized Quick Sort — PIVOT TASODIFIY TANLANADI
public static void RandomizedQuickSort(int[] arr, int low, int high)
{
    if (low < high)
    {
        int randomIndex = Random.Shared.Next(low, high + 1);
        (arr[randomIndex], arr[high]) = (arr[high], arr[randomIndex]); // PIVOT'ni OXIRGA KO'CHIRISH

        int pivotIndex = Partition(arr, low, high);
        RandomizedQuickSort(arr, low, pivotIndex - 1);
        RandomizedQuickSort(arr, pivotIndex + 1, high);
    }
}

private static int Partition(int[] arr, int low, int high)
{
    int pivot = arr[high];
    int i = low - 1;
    for (int j = low; j < high; j++)
    {
        if (arr[j] < pivot)
        {
            i++;
            (arr[i], arr[j]) = (arr[j], arr[i]);
        }
    }
    (arr[i + 1], arr[high]) = (arr[high], arr[i + 1]);
    return i + 1;
}
```

```csharp
// Kriptografik XAVFSIZ random — API Key generatsiyasi uchun
using System.Security.Cryptography;

public static string GenerateApiKey()
{
    var bytes = RandomNumberGenerator.GetBytes(32); // 256-bit ENTROPY
    return Convert.ToBase64String(bytes);
}
```

## 6. Keng tarqalgan xatolar / noto'g'ri tushunchalar

```
❌ "new Random() — HAR SAFAR CHAQIRILSA, HAR XIL NATIJA BERADI" —
   AGAR TSIKL ICHIDA `new Random()` KO'P MARTA CHAQIRILSA — TIZIM
   SOATI (SEED sifatida) BIR XIL bo'lishi MUMKIN (juda TEZ, BIR
   NECHTA millisekundda), NATIJADA BIR XIL SONLAR OLINADI!
   Random.Shared (yoki BITTA instance) ISHLATILISHI kerak.

❌ "System.Random — PAROL/TOKEN GENERATSIYASI uchun XAVFSIZ" —
   XAVFLI! Bu — PSEUDO-RANDOM, BASHORAT QILINISHI MUMKIN.
   RandomNumberGenerator ISHLATILISHI SHART.

❌ "Randomized algoritm — HAR DOIM TEZROQ" — NOTO'G'RI! Randomization
   — "O'RTACHA HOLAT"NI YAXSHILAYDI (yomon holatga tushish
   EHTIMOLINI kamaytiradi), lekin NAZARIY "ENG YOMON HOLAT" (worst
   case) HALI HAM MAVJUD (juda kam ehtimol bilan).

❌ "System.Random — THREAD-SAFE" — YO'Q (Random.Shared'DAN
   TASHQARI)! Bir nechta thread BIR XIL Random INSTANCE'IDAN
   PARALLEL foydalansa — ICHKI holat BUZILISHI, HATTO Exception
   TASHLASHI mumkin.
```

## 7. Exam (Interview savollari)

**1. Las Vegas va Monte Carlo algoritmlari orasidagi FARQ nima?**
Las Vegas — NATIJA DOIM TO'G'RI, BAJARILISH VAQTI O'ZGARUVCHAN.
Monte Carlo — BAJARILISH VAQTI ODATDA FIXED, NATIJA EHTIMOLLIK
BILAN TO'G'RI (100% EMAS).

**2. `System.Random` "haqiqiy tasodifiy" emasligini TUSHUNTIRING.**
`Random` — Pseudo-Random Number Generator (PRNG) — MATEMATIK
ALGORITM ORQALI, SEED'DAN BOSHLAB, DETERMINISTIK KETMA-KETLIKNI
GENERATSIYA QILADI. BIR XIL SEED — HAR DOIM BIR XIL NATIJALARNI
BERADI — bu "HAQIQIY" TASODIFIYLIK EMAS, LEKIN AMALIY MAQSADLAR
(o'yin, TEST) UCHUN YETARLI.

**3. Randomized Quick Sort nima uchun "YOMON HOLAT"NI (O(n²))
KAMROQ EHTIMOL QILADI?**
Oddiy Quick Sort'da PIVOT DOIM BIR XIL POZITSIYADAN (masalan
OXIRGI element) TANLANSA — TARTIBLANGAN massivda BALANSSIZ
BO'LINISHGA olib KELADI (O(n²)). PIVOT'NI TASODIFIY TANLASH — HAR
QANDAY KIRISH MA'LUMOTI UCHUN, BALANSSIZ BO'LINISH EHTIMOLINI
DEYARLI YO'QQA CHIQARADI (statistik jihatdan).

**4. Nima uchun `RandomNumberGenerator` — PAROL/TOKEN uchun
`System.Random`dan XAVFSIZROQ?**
`RandomNumberGenerator` — OS DARAJASIDAGI "ENTROPY" MANBALARIDAN
(HARDWARE HODISALARDAN) FOYDALANADI — NATIJANI BASHORAT QILIB
BO'LMAYDI. `System.Random` — DETERMINISTIK FORMULA, AGAR SEED
YOKI OLDINGI NATIJALAR MA'LUM BO'LSA — KEYINGI QIYMATLARNI
HISOBLAB TOPISH MUMKIN (kriptografik jihatdan ZAIF).

**5. `Random.Shared` (.NET 6+) qanday muammoni HAL QILADI?**
Ilgari, KO'P thread'da BIR XIL `Random` instance'ini ISHLATISH —
THREAD-SAFETY MUAMMOSIGA (buzilgan ICHKI holat) OLIB KELARDI, YOKI
HAR THREAD uchun ALOHIDA `Random` YARATISH KERAK EDI (bu esa
SEED KOLLIZIYASI XAVFINI TUG'DIRARDI). `Random.Shared` — THREAD-SAFE,
GLOBAL, OPTIMALLASHTIRILGAN instance TAQDIM ETADI.
