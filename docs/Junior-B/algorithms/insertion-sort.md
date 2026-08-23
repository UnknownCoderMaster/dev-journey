# Sorting Algorithm — Insertion Sort — Junior B

## 1. What (Nima?)

**Insertion Sort** — massivni tartiblash algoritmi: massivni
**TARTIBLANGAN** va **TARTIBLANMAGAN** ikki qismga "bo'lib",
tartiblanmagan qismdan HAR BIR elementni NAVBAT bilan olib,
tartiblangan qismning **TO'G'RI o'rniga "kiritadi"** (insert).

## 2. Real hayot analogiyasi

**QO'LDAGI KARTALARNI TARTIBLASH.** Karta o'yinida — QO'LINGIZDAGI
KARTALARNI TARTIBLAGANDA — SIZ ODATDA "Selection Sort" USLUBIDA
EMAS, "Insertion Sort" USLUBIDA HARAKAT QILASIZ: STOLDAN (yoki
DASTADAN) BIR KARTA OLASIZ VA UNI QO'LINGIZDAGI (ALLAQACHON
TARTIBLANGAN) KARTALAR ORASIGA, **TO'G'RI JOYIGA** "SUQIB
KIRITASIZ" — QOLGAN KARTALARNI SIQIB CHIQARIB.

## 3. Why (Nega kerak?)

Insertion Sort — Selection Sort'DAN KO'RA **AMALIYOTDA KO'PROQ**
FOYDALI, chunki:

1. **DEYARLI TARTIBLANGAN** MA'LUMOTLARDA — JUDA TEZ ISHLAYDI
   (BEST CASE — O(n)) — REAL DUNYODA KO'P MA'LUMOT (masalan,
   BOSHQA TIZIMDAN KELGAN, DEYARLI TARTIBLANGAN LOG YOZUVLARI)
   AYNAN SHUNDAY
2. **KICHIK MASSIVLAR**DA — Quick Sort/Merge Sort'DAN HAM TEZROQ
   (kam OVERHEAD) — SHUNING UCHUN .NET'ning `Array.Sort()` —
   KICHIK BO'LAKLAR (odatda <16 element) UCHUN Insertion Sort'GA
   "TUSHIB QOLADI" (Introsort STRATEGIYASI)
3. **ONLINE ALGORITM** — YANGI ELEMENT KELGANDA, BUTUN MASSIVNI
   QAYTA TARTIBLAMASDAN, TO'G'RI JOYGA "KIRITISH" MUMKIN

## 4. Internals (Ichki mexanizm)

### Algoritm QADAMLARI

```
Massiv: [12, 11, 13, 5, 6]

i=1: key=11, [12] bilan SOLISHTIRISH → 11 < 12, [11, 12] hosil bo'ladi
     Natija: [11, 12, 13, 5, 6]

i=2: key=13, [11,12] TARTIBLANGAN QISMGA SOLISHTIRIB → 13 > 12,
     JOYI O'ZGARMAYDI
     Natija: [11, 12, 13, 5, 6]

i=3: key=5, [11,12,13] bilan SOLISHTIRISH → 5 ENG KICHIK, HAMMASI
     BIR O'RINGA SILJIYDI, 5 BOSHIGA "KIRITILADI"
     Natija: [5, 11, 12, 13, 6]

i=4: key=6, [5,11,12,13] bilan SOLISHTIRISH → 6, 5DAN KEYIN,
     11DAN OLDIN "KIRITILADI"
     Natija: [5, 6, 11, 12, 13] — TARTIBLANGAN!
```

### Vaqt murakkabligi — BEST vs WORST CASE

```
BEST CASE — O(n) — massiv ALLAQACHON TARTIBLANGAN bo'lsa:
  HAR ELEMENT — FAQAT BITTA TAQQOSLASH bilan "O'Z JOYIDA" EKANI
  ANIQLANADI (ICHKI TSIKL DARHOL TO'XTAYDI)

WORST CASE — O(n²) — massiv TESKARI TARTIBLANGAN bo'lsa:
  HAR ELEMENT — TARTIBLANGAN QISMNING BOSHIGACHA SILJITILISHI
  KERAK (ICHKI TSIKL — TO'LIQ AYLANADI)

AVERAGE CASE — O(n²) — LEKIN KONSTANTA KOEFFITSIYENT Selection
Sort'DAN KICHIKROQ (ERTA TO'XTASH IMKONIYATI TUFAYLI)
```

```
Selection Sort — HAR DOIM O(n²) (BEST CASE HAM)
Insertion Sort — BEST CASE'da O(n) — bu ASOSIY FARQ!
```

### "SHIFT" mexanizmi — nima uchun SWAP EMAS

```
Insertion Sort — Selection Sort'DAN FARQLI, HAR JUFT elementni
SWAP QILMAYDI — BUNING O'RNIGA, ELEMENTLARNI "SILJITADI" (SHIFT)
VA key'NI TO'G'RI joyga BIR MARTA QO'YADI — bu, AYNIQSA KO'P
SILJISH KERAK bo'lganda, SWAP'DAN (HAR SAFAR 3 TA YOZISH: TEMP,
A, B) BIROZ SAMARALIROQ (HAR SILJISHDA FAQAT 1 TA YOZISH).
```

### STABLE algoritm — Selection Sort'DAN FARQI

```
Insertion Sort — STABLE! Chunki element FAQAT O'ZIDAN KATTA
(yoki TENG) elementlar TUFAYLI SILJIYDI — TENG QIYMATLI
elementlar BIR-BIRINI "O'TIB KETMAYDI" — ASL NISBIY TARTIB
SAQLANADI.

Misol: [(5,A), (3,B), (5,C)]
Insertion Sort natijasi: [(3,B), (5,A), (5,C)] — A HALI HAM
C'DAN OLDIN! (STABLE)
```

### Binary Insertion Sort — OPTIMALLASHTIRISH

```
Oddiy Insertion Sort — "TO'G'RI JOY"NI CHIZIQLI (linear) QIDIRADI
(O(n) HAR ELEMENT UCHUN).

Binary Insertion Sort — TARTIBLANGAN QISM ICHIDA, Binary Search
orqali "TO'G'RI JOY"NI O(log n) DA TOPADI — LEKIN SILJITISH
(shift) BARIBIR O(n) — shuning uchun UMUMIY VAQT murakkabligi
O(n²) BO'LIB QOLADI (TAQQOSLASH kamayadi, LEKIN SILJISH SONI
O'ZGARMAYDI).
```

## 5. Code (Amaliy kod)

```csharp
public static void InsertionSort(int[] arr)
{
    for (int i = 1; i < arr.Length; i++)
    {
        int key = arr[i];       // TARTIBLANMAGAN QISMDAN KEYINGI ELEMENT
        int j = i - 1;

        // TARTIBLANGAN QISMDA, key'DAN KATTA elementlarni BIR O'RINGA SILJITISH
        while (j >= 0 && arr[j] > key)
        {
            arr[j + 1] = arr[j];
            j--;
        }

        arr[j + 1] = key; // key'ni TO'G'RI JOYGA "KIRITISH"
    }
}
```

```csharp
// Generic versiya — Employee'larni SANA bo'yicha TARTIBLASH (STABLE — MUHIM!)
public static void InsertionSort<T>(List<T> list) where T : IComparable<T>
{
    for (int i = 1; i < list.Count; i++)
    {
        T key = list[i];
        int j = i - 1;

        while (j >= 0 && list[j].CompareTo(key) > 0)
        {
            list[j + 1] = list[j];
            j--;
        }
        list[j + 1] = key;
    }
}
```

```csharp
// "Online" xususiyat — YANGI kelgan elementni MAVJUD tartiblangan
// ro'yxatga QO'SHISH (butun ro'yxatni QAYTA tartiblamasdan)
public static void InsertSorted(List<int> sortedList, int newValue)
{
    int i = sortedList.Count - 1;
    sortedList.Add(0); // Joy OCHISH

    while (i >= 0 && sortedList[i] > newValue)
    {
        sortedList[i + 1] = sortedList[i];
        i--;
    }
    sortedList[i + 1] = newValue;
}
```

## 6. Keng tarqalgan xatolar / noto'g'ri tushunchalar

```
❌ "Insertion Sort — HAR DOIM O(n²)" — TO'LIQ TO'G'RI EMAS! BEST
   CASE (massiv ALLAQACHON TARTIBLANGAN) — O(n), bu — Selection
   Sort'dan MUHIM FARQI.

❌ "Insertion Sort — STABLE EMAS" — NOTO'G'RI! Insertion Sort —
   STABLE (Selection Sort esa STABLE EMAS — bu IKKALASINI
   CHALKASHTIRISH KENG TARQALGAN XATO).

❌ "Insertion Sort — KATTA massivlar uchun HAM YAXSHI ISHLAYDI" —
   YO'Q! O(n²) WORST/AVERAGE CASE — KATTA (masalan 100,000+)
   massivlarda JUDA SEKIN — FAQAT KICHIK massivlar YOKI
   "DEYARLI TARTIBLANGAN" ma'lumotlar uchun SAMARALI.

❌ "Binary Insertion Sort — O(n log n) VAQT murakkabligiga EGA" —
   NOTO'G'RI! Binary Search FAQAT TAQQOSLASH SONINI KAMAYTIRADI,
   SILJITISH (array shift) — BARIBIR O(n) — UMUMIY vaqt
   murakkabligi HALI HAM O(n²).
```

## 7. Exam (Interview savollari)

**1. Insertion Sort'ning BEST CASE vaqt murakkabligi NIMA VA U
QACHON YUZAGA KELADI?**
O(n) — massiv ALLAQACHON TO'LIQ TARTIBLANGAN bo'lsa. Bu holatda,
HAR YANGI ELEMENT — ICHKI TSIKLDA FAQAT BITTA TAQQOSLASH BILAN
"O'Z JOYIDA EKANI" ANIQLANADI, HECH QANDAY SILJISH KERAK EMAS.

**2. Insertion Sort STABLE, Selection Sort esa STABLE EMAS —
BU FARQ NIMADAN KELIB CHIQADI?**
Insertion Sort — elementni FAQAT O'ZIDAN KATTA elementlar
ORQALI SILJITADI, TENG QIYMATLILAR BIR-BIRINI "O'TIB KETMAYDI".
Selection Sort — UZOQDAGI ikki ELEMENTNI (masalan indeks 0 va 5)
TO'G'RIDAN SWAP QILADI — bu, ORADAGI TENG QIYMATLI elementlarning
NISBIY TARTIBINI BUZISHI mumkin.

**3. .NET'ning `Array.Sort()` nima uchun KICHIK massivlarda
Insertion Sort'GA "TUSHIB QOLADI"?**
Quick Sort/Merge Sort — REKURSIYA va BO'LISH (divide) OVERHEAD'iga
EGA — KICHIK massivlarda (odatda ~16 elementgacha) bu OVERHEAD —
O(n²) Insertion Sort'ning O'ZIDAN HAM KATTAROQ bo'lib qoladi.
Shuning uchun Introsort — KICHIK BO'LAKLARDA Insertion Sort'ga
"TUSHADI" (amaliy performance uchun).

**4. Insertion Sort qanday "ONLINE algoritm" hisoblanadi?**
Insertion Sort — YANGI element kelganda, BUTUN massivni QAYTA
TARTIBLAMASDAN, uni MAVJUD tartiblangan ro'yxatga TO'G'RI JOYGA
"KIRITISHI" mumkin — bu, MA'LUMOT OQIMI (stream) sifatida
KELAYOTGan holatlarda (masalan real-time SORTED LIST yuritish)
FOYDALI.

**5. Binary Insertion Sort — vaqt murakkabligini QANDAY (va
QANCHA) YAXSHILAYDI?**
Binary Search orqali, TO'G'RI KIRITISH POZITSIYASINI TOPISH —
O(n) O'RNIGA O(log n) TAQQOSLASH bilan AMALGA OSHIRILADI. LEKIN
ELEMENTLARNI SILJITISH (array shift) HALI HAM O(n) TALAB QILADI
— shuning uchun UMUMIY VAQT murakkabligi O(n²) BO'LIB QOLADI —
FAQAT TAQQOSLASHLAR SONI KAMAYADI, SILJISHLAR EMAS.
