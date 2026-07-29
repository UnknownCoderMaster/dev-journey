# Memory-Mapped Files — Middle D

## 1. Nima? (Ta'rif)

**Memory-Mapped File** — diskdagi faylni to'g'ridan jarayon (process)
virtual xotira manzil fazosiga **"proyeksiya qilish"** mexanizmi —
fayl ma'lumotlariga oddiy massiv elementiga murojaat qilgandek kirish
imkonini beradi.

## 2. Nima uchun kerak?

Oddiy `File.ReadAllBytes()` — butun faylni **RAM'ga to'liq
nusxalaydi**. 10GB fayl uchun bu — 10GB RAM talab qiladi! Memory-Mapped
File — OS'ning **virtual memory** mexanizmidan foydalanib, faylning
**faqat kerakli qismini** (page) xotiraga yuklaydi — qolgani diskda
qoladi, lekin **xuddi RAM'dagidek** murojaat qilinadi.

## 3. Ichida nima sodir bo'ladi? (Mexanizm)

### 3.1 OS darajasida qanday ishlaydi

```
Oddiy fayl o'qish:
  Disk → [read() syscall] → Kernel buffer → [copy] → Process xotirasi
  (Ma'lumot IKKI MARTA nusxalanadi: disk→kernel, kernel→process)

Memory-Mapped File:
  Disk fayl ←→ Virtual Memory Page Table ←→ Process xotira manzili

  Process "xotiradan o'qiyapman" deb o'ylaydi, lekin ASLIDA:
  1. Process manzilga murojaat qiladi
  2. Agar shu "page" hali RAM'da bo'lmasa — PAGE FAULT yuz beradi
  3. OS avtomatik shu page'ni diskdan RAM'ga yuklaydi (LAZY LOADING)
  4. Keyingi murojaatlar — TO'G'RIDAN RAM'dan (tez)
```

```
┌─────────────────────┐
│  Process Virtual     │
│  Memory              │
│  ┌────────────────┐  │        ┌──────────────┐
│  │ Mapped Region  │──┼───────►│  Fayl (Disk)  │
│  └────────────────┘  │        └──────────────┘
└─────────────────────┘
   Bir nechta PROCESS BIR XIL faylni "map" qilsa —
   ULAR BIR XIL FIZIK XOTIRA sahifasini BO'LISHADI (Copy-on-Write)!
```

### 3.2 Oddiy o'qishdan farqi — xotira va tezlik

```
❌ File.ReadAllBytes("10gb-file.dat")
   → 10GB RAM darhol band qilinadi
   → Katta fayllar uchun OutOfMemoryException xavfi

✅ MemoryMappedFile bilan
   → Faqat HAQIQATDA ishlatilgan qismlar RAM'da
   → Fayl HAJMIDAN QAT'IY NAZAR — RAM sarfi MINIMAL
   → OS o'zi "kam ishlatilgan" sahifalarni RAM'dan CHIQARIB tashlaydi
     (kerak bo'lsa qayta yuklanadi)
```

### 3.3 `CreateFromFile` vs `CreateOrOpen`

```csharp
// CreateFromFile — MAVJUD fayl bilan ishlash
using var mmf = MemoryMappedFile.CreateFromFile(
    "data.bin", FileMode.Open, "MyMap", 0, MemoryMappedFileAccess.Read);

// CreateOrOpen — DISKDAGI FAYLGA BOG'LANMAGAN, faqat XOTIRADA
// (Processlar orasida ma'lumot almashish uchun — IPC!)
using var mmf2 = MemoryMappedFile.CreateOrOpen("SharedMemory", 1024);
```

### 3.4 ViewAccessor vs ViewStream

```csharp
// ViewAccessor — RANDOM ACCESS (istalgan joyga o'qish/yozish)
using var accessor = mmf.CreateViewAccessor(0, 1024);
int value = accessor.ReadInt32(100); // 100-offset'dan int o'qish
accessor.Write(200, 42);              // 200-offset'ga yozish

// ViewStream — FORWARD-ONLY oqim sifatida (Stream API bilan mos)
using var stream = mmf.CreateViewStream();
using var reader = new BinaryReader(stream);
int value2 = reader.ReadInt32();
```

`ViewAccessor` — istalgan pozitsiyaga **to'g'ridan** o'qish/yozish
uchun (masalan, katta binary fayl ichida ma'lum strukturaga ega
"record"larni indeks orqali topish). `ViewStream` — ketma-ket
(sequential) o'qish/yozish uchun, mavjud `Stream`-asoslangan API
bilan ishlash kerak bo'lganda.

### 3.5 Processlar orasi aloqa (IPC)

```csharp
// Process A — yozuvchi
using var mmf = MemoryMappedFile.CreateNew("SharedChannel", 256);
using var accessor = mmf.CreateViewAccessor();
accessor.Write(0, 12345); // Boshqa process buni O'QIY OLADI!

// Process B — o'quvchi (BOSHQA process, BIR XIL nom bilan)
using var mmf2 = MemoryMappedFile.OpenExisting("SharedChannel");
using var accessor2 = mmf2.CreateViewAccessor();
int value = accessor2.ReadInt32(0); // → 12345
```

Bu — ikkita **mustaqil process** (masalan, ikkita alohida .exe) o'rtasida
**disk yoki tarmoqsiz**, to'g'ridan xotira orqali tezkor ma'lumot
almashish imkonini beradi — Named Pipes'dan tezroq, lekin faqat BIR
mashinada ishlaydi.

### 3.6 Katta fayllar — streaming vs full load

```
100GB log faylida "ERROR" so'zini qidirish kerak:

❌ File.ReadAllText() — 100GB RAM kerak, DARHOL OutOfMemory

✅ Memory-Mapped File — fayl BO'LAKLARGA (masalan har 1MB) BO'LIB
   o'qiladi, HAR SAFAR faqat kerakli QISM RAM'ga yuklanadi
```

## 4. Kod — to'liq misol

```csharp
// Katta faylni bo'laklarga bo'lib qidirish
public bool ContainsPattern(string filePath, byte[] pattern)
{
    using var mmf = MemoryMappedFile.CreateFromFile(filePath, FileMode.Open);
    var fileInfo = new FileInfo(filePath);
    const long chunkSize = 1024 * 1024; // 1MB bo'laklar

    for (long offset = 0; offset < fileInfo.Length; offset += chunkSize)
    {
        long size = Math.Min(chunkSize, fileInfo.Length - offset);
        using var accessor = mmf.CreateViewAccessor(offset, size, MemoryMappedFileAccess.Read);

        var buffer = new byte[size];
        accessor.ReadArray(0, buffer, 0, (int)size);

        if (ContainsSubarray(buffer, pattern))
            return true;
    }
    return false;
}
```

## 5. Qachon ishlatish kerak?

| Vaziyat | Yechim |
|---|---|
| Juda katta fayl (GB darajasida), tasodifiy kirish kerak | Memory-Mapped File |
| Ikkita local process orasida tez ma'lumot almashish | `CreateOrOpen` (IPC) |
| Oddiy, kichik fayl (KB-MB) | Oddiy `File.ReadAllBytes`/`Stream` yetarli |
| Ketma-ket, katta faylni STREAM qilib o'qish | `FileStream` yoki `ViewStream` |

**Real use case:** Log fayllarini tahlil qiluvchi vosita, katta
video/rasm fayllarni qism-qism qayta ishlash, database engine'lar
(PostgreSQL o'zi ham ichkarida shunga o'xshash texnikalar ishlatadi).

## 6. Muhim nuqtalar

- Memory-Mapped File — **Windows va Linux**da farqli implementatsiya
  qilingan, lekin .NET API **bir xil** — kross-platform ishlaydi.
- Juda ko'p kichik fayl uchun — overhead (page table sozlash) foydadan
  ko'proq bo'lishi mumkin — faqat **katta** fayllar uchun foydali.
- `MemoryMappedFileAccess.ReadWrite` bilan ochilgan fayl — o'zgarishlar
  **avtomatik** diskka yoziladi (OS page cache orqali, `Flush()` bilan
  majburiy qilish mumkin).

## 7. Imtihon savollari

1. Memory-Mapped File OS darajasida qanday ishlaydi — "page fault"
   tushunchasi orqali tushuntiring.
2. Oddiy `File.ReadAllBytes()` bilan solishtirganda, xotira sarfi
   qanday farq qiladi?
3. `ViewAccessor` va `ViewStream` orasidagi farq nima?
4. `CreateFromFile` va `CreateOrOpen` qachon ishlatiladi?
5. Memory-Mapped File orqali IPC (Inter-Process Communication)
   qanday amalga oshiriladi?
6. Nima uchun bu texnika juda katta fayllar bilan ishlashda foydali,
   lekin kichik fayllar uchun ortiqcha bo'lishi mumkin?
