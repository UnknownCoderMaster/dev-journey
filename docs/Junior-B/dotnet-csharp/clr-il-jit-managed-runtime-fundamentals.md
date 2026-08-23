# CLS, CLR, IL, JIT, Managed/Unmanaged Code, SDK, Runtime, .NET Standard, BCL, FCL — Junior B

## 1. What (Nima?)

Bu atamalar — .NET ekotizimining **poydevorini** tashkil qiladi:

- **CLR (Common Language Runtime)** — C# (yoki F#, VB.NET) kodini
  **ishga tushiruvchi virtual mashina** — xotira boshqaruvi (GC),
  type safety, exception handling, JIT compilation shu yerda amalga
  oshadi.
- **CLS (Common Language Specification)** — turli .NET tillari
  (C#, F#, VB.NET) **bir-biri bilan mos ishlashi** uchun rioya
  qilinishi kerak bo'lgan qoidalar to'plami.
- **IL (Intermediate Language)** — C# kompilyatordan chiqadigan,
  **CPU-ga bevosita tegishli bo'lmagan** oraliq bayt-kod (`MSIL`
  yoki `CIL` deb ham ataladi).
- **JIT (Just-In-Time Compiler)** — IL kodni, dastur **ishga
  tushish paytida**, mashinaning haqiqiy protsessor kodiga
  (native code) aylantiruvchi komponent.
- **Managed code** — CLR tomonidan boshqariladigan kod (GC, type
  safety bilan). **Unmanaged code** — CLR nazoratisiz ishlaydigan
  kod (C/C++, Win32 API) — xotirani dasturchi **qo'lda** boshqaradi.
- **SDK (Software Development Kit)** — kompilyator, CLI vositalar,
  NuGet, MSBuild — **dastur YARATISH** uchun kerak bo'lgan barcha
  narsa.
- **Runtime** — kompilyatsiya qilingan dasturni **ISHGA TUSHIRISH**
  uchun kerak bo'lgan minimal muhit (SDK'siz).
- **BCL (Base Class Library)** — `System.String`, `System.Collections`
  kabi **eng asosiy** klasslar to'plami.
- **FCL (Framework Class Library)** — BCL + `System.Net`,
  `System.Data` kabi **kengaytirilgan** kutubxonalar — BCL FCL'ning
  **kichik qismi**.
- **.NET Standard** — turli .NET implementatsiyalari (.NET Framework,
  .NET Core, Xamarin) **BIR XIL API'ga rioya qilishi** uchun
  yaratilgan spetsifikatsiya (hozir .NET 5+ bilan katta qismi
  **eskirgan**, lekin kutubxona muvofiqligi uchun hali uchraydi).

## 2. Real hayot analogiyasi

**CLR — aeroport nazorat minorasi.** Har bir samolyot (dastur) —
mustaqil parvoz qila olmaydi, minora (CLR) uni kuzatib, xavfsizlik
qoidalariga rioya qilishini ta'minlaydi, yoqilg'i (xotira) taqsimlaydi
va kerak bo'lganda "parvozni to'xtatadi" (exception, GC).

**IL — "xalqaro retsept kitobi".** Oshpaz (kompilyator) — retseptni
**hech bir mamlakatning maxsus oshxona jihozlariga bog'lamasdan**,
umumiy tushunarli tilda yozadi (IL). Keyin har bir mamlakatning
oshxonasi (protsessor arxitekturasi — x64, ARM) — bu retseptni **o'z
jihozlariga moslab** (JIT) tayyorlaydi.

**Managed vs Unmanaged — mehmonxona va shaxsiy uy.** Mehmonxonada
(managed) — xizmat ko'rsatuvchi xodimlar (GC) xonani sizning
o'rningizga TOZALAYDI. Shaxsiy uyda (unmanaged) — HAMMA narsani
(chiqindi tashlash, ta'mirlash) **O'ZINGIZ** qilishingiz kerak — bu
KO'PROQ nazorat beradi, lekin **XATO qilish OSON**.

## 3. Why (Nega kerak?)

CLR bo'lmasa — har bir dastur **to'g'ridan** operatsion tizim va
protsessorga moslashtirilgan bo'lishi kerak edi (C/C++ kabi) — bu
**xotira xavfsizligi muammolari** (buffer overflow, memory leak) va
**platformalar orasida ko'chirib bo'lmaslik** degani. .NET — bu
muammolarni **IL + CLR** orqali hal qildi: bir marta kompilyatsiya
qilingan IL — **istalgan platformada** (Windows, Linux, macOS) —
mos CLR (runtime) orqali ishlaydi.

**Java bilan solishtirish:** JVM (Java Virtual Machine) — CLR'ning
**to'g'ridan** o'xshashi — bytecode (IL'ning Java'dagi analogi) +
JIT. Farqi — .NET dastlab Windows-markazlashgan edi (.NET Framework),
.NET Core (endi shunchaki "**.NET**") bilan **to'liq kross-platform**
bo'ldi.

## 4. Internals (Ichki mexanizm)

### Kompilyatsiya bosqichlari

```
C# manba kodi (.cs)
    │  Roslyn kompilyator (csc.exe)
    ▼
IL kod + Metadata (.dll/.exe — "Assembly")
    │  CLR yuklaydi (Assembly Loader)
    ▼
JIT Compiler — METOD BIRINCHI MARTA chaqirilganda ISHGA TUSHADI
    │
    ▼
Native machine code (CPU'ga XOS) — XOTIRADA saqlanadi, KEYINGI
chaqiruvlar TO'G'RIDAN shu native kod orqali (QAYTA JIT QILINMAYDI)
```

### JIT — "Tier 0" va "Tier 1" (Tiered Compilation, .NET Core 3+)

```
Metod BIRINCHI marta chaqirilganda:
  Tier 0 — TEZ, lekin KAM OPTIMALLASHTIRILGAN kod generatsiya qilinadi
           (ilova TEZROQ ishga tushishi uchun)

Metod KO'P MARTA (hot path) chaqirilsa:
  Tier 1 — CLR fonda, QAYTA, TO'LIQ OPTIMALLASHTIRILGAN native kod
           generatsiya qiladi va ALMASHTIRADI (background rekompilyatsiya)
```

Bu — .NET'ning **ishga tushish tezligi** (startup time) va
**uzoq muddatli performance** orasidagi muvozanatni saqlash
strategiyasi.

### AOT (Ahead-of-Time) — JIT'dan farqi

```
JIT — RUNTIME'da, KERAK BO'LGANDA kompilyatsiya (default)
AOT (Native AOT, .NET 7+) — DEPLOY VAQTIDA, OLDINDAN native kodga
     aylantiriladi — JIT OVERHEAD YO'Q, ISHGA TUSHISH TEZROQ, lekin
     platform-SPETSIFIK binary (kross-platform ISHLAB CHIQARISH
     alohida QILINISHI kerak)
```

### Managed Heap va GC bilan bog'liqlik

CLR — **Managed Heap**ni boshqaradi (Gen 0/1/2, LOH — batafsil
`docs/Junior-A/03-gc-dispose-finalize`da). Unmanaged resurs (fayl
handle, socket) — CLR **bilmaydigan** xotira, shuning uchun
`IDisposable`/`using` orqali **qo'lda** boshqarilishi kerak.

### Type Safety — CLR qanday kafolatlaydi

```
JIT — IL'ni native kodga AYLANTIRISHDAN OLDIN, "Verification"
jarayonini o'tkazadi: TUR MOS KELMASLIGI (masalan int'ni string
sifatida O'QISHGA URINISH) — RUNTIME'da EMAS, VERIFICATION
bosqichida ANIQLANADI (agar kod "unsafe" deb belgilanmagan bo'lsa).
```

### SDK vs Runtime — nima FARQ QILADI

```
dotnet --list-sdks      — O'RNATILGAN SDK'lar (dastur YARATISH uchun)
dotnet --list-runtimes   — O'RNATILGAN Runtime'lar (dastur ISHGA
                            TUSHIRISH uchun, YENGILROQ, kompilyator
                            YO'Q)

Production SERVER — ODATDA faqat Runtime O'RNATILADI (SDK KERAK
EMAS, DISK joyi TEJALADI).
```

## 5. Code (Amaliy kod)

```csharp
// IL kodni ko'rish — ildasm yoki sharplab.io orqali
public int Add(int a, int b) => a + b;

// Yuqoridagi metod — QUYIDAGI IL'ga KOMPILYATSIYA QILINADI (soddalashtirilgan):
// .method public hidebysig instance int32 Add(int32 a, int32 b) cil managed
// {
//     ldarg.1      // a'ni STACK'ga YUKLASH
//     ldarg.2      // b'ni STACK'ga YUKLASH
//     add          // QO'SHISH
//     ret          // NATIJANI QAYTARISH
// }
```

```csharp
// Unmanaged resurs bilan ishlash — "unsafe" kod (CLR nazoratidan TASHQARI)
unsafe void ProcessBuffer(byte[] data)
{
    fixed (byte* ptr = data) // Pointer — CLR bevosita NAZORAT QILA OLMAYDI!
    {
        for (int i = 0; i < data.Length; i++)
            *(ptr + i) = 0;
    }
}
// csproj'da <AllowUnsafeBlocks>true</AllowUnsafeBlocks> kerak
```

```csharp
// Runtime versiyasini DASTUR ICHIDAN aniqlash
Console.WriteLine(Environment.Version);                       // CLR versiyasi
Console.WriteLine(System.Runtime.InteropServices.RuntimeInformation.FrameworkDescription); // ".NET 8.0.8"
```

## 6. Keng tarqalgan xatolar / noto'g'ri tushunchalar

```
❌ "C# — INTERPRETED til, Python kabi" — NOTO'G'RI! C# —
   KOMPILYATSIYA QILINADI (IL'ga, keyin JIT orqali native kodga).
   Runtime'da HAR QATOR "o'qib-bajarilmaydi" (interpreted tillarda
   bo'lgani kabi).

❌ ".NET Framework va .NET (Core) — BIR XIL narsa" — NOTO'G'RI!
   .NET Framework — FAQAT Windows, ESKIRGAN (yangi funksiya
   OLMAYDI). .NET (5+) — kross-platform, FAOL rivojlanmoqda.

❌ "JIT — HAR SAFAR metod chaqirilganda ISHLAYDI" — NOTO'G'RI!
   JIT — FAQAT BIRINCHI chaqiruvda ishlaydi, NATIJA (native kod)
   KESHLANADI, KEYINGI chaqiruvlar TO'G'RIDAN shu kod orqali.

❌ "Managed kod — HAR DOIM Unmanaged'dan SEKIN" — TO'LIQ TO'G'RI
   EMAS — JIT OPTIMALLASHTIRISHI (Tier 1, PGO) ko'p holatda C++ ga
   YAQIN performance beradi, ayniqsa uzoq ishlaydigan dasturlarda.
```

## 7. Exam (Interview savollari)

**1. IL va native machine code orasidagi farq nima?**
IL — CPU-ga bog'liq bo'lmagan, oraliq bayt-kod (CLR tushunadigan
instruktsiyalar). Native code — MUAYYAN protsessor (x64, ARM64)
UCHUN, JIT tomonidan generatsiya qilingan, TO'G'RIDAN bajariladigan
mashina kodi.

**2. JIT compilation qanday ishlaydi va u nima uchun "Just-In-Time"
deb ataladi?**
Metod BIRINCHI marta CHAQIRILGANDA (runtime'da, "aynan shu vaqtda"
kerak bo'lganda) — CLR uning IL kodini native kodga AYLANTIRADI va
XOTIRADA SAQLAYDI. Keyingi chaqiruvlar — QAYTA kompilyatsiyasiz,
to'g'ridan shu native kod orqali.

**3. Managed va Unmanaged kod orasidagi asosiy farq nima?**
Managed kod — CLR nazorati OSTIDA (GC xotirani AVTOMATIK boshqaradi,
type safety TA'MINLANADI). Unmanaged kod — CLR BILMAYDI, dasturchi
xotirani QO'LDA (malloc/free, yoki C#'da `unsafe`/pointer orqali)
boshqaradi.

**4. .NET Standard nima va u hozir nima uchun "eskirgan" hisoblanadi?**
.NET Standard — turli .NET implementatsiyalari (Framework, Core,
Xamarin) uchun UMUMIY API SPETSIFIKATSIYASI edi — kutubxona
YOZUVCHILARGA "BIR MARTA yozib, HAMMA JOYDA ishlatish" imkonini
berardi. .NET 5+ dan BOSHLAB — BARCHA implementatsiyalar BITTA
".NET"ga BIRLASHTIRILDI, shuning uchun YANGI loyihalarda .NET
Standard O'RNIGA to'g'ridan .NET 8 (yoki kerakli versiya) target
qilinadi.

**5. BCL va FCL orasidagi farq nima?**
BCL — ENG ASOSIY, "yadro" klasslar (`System.String`, `System.Collections`,
`System.IO`). FCL — BCL + KENGAYTIRILGAN funksionallik
(`System.Net`, `System.Data`, `System.Web`) — BCL, FCL'ning
KICHIK QISM to'plami.
