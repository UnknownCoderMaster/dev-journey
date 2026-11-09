# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "Record types (C# 9+)"
CATEGORY = ".NET / C#"
TITLE = "Record Turlari"
SUBTITLE = "Ma'lumot saqlash uchun mo'ljallangan turlar"
FILENAME = "Record types (C# 9+).docx"


def build(d):
    h1(d, "1. Record nima muammoni hal qiladi")

    para(d, "Faqat ma'lumot saqlaydigan klass yozish C# da ko'p takrorlanuvchi "
            "kod talab qilardi. DTO uchun qiymat bo'yicha taqqoslash, "
            "`GetHashCode`, `ToString` va o'zgarmaslik kerak bo'lsa, natija "
            "shunday ko'rinardi:")

    code(d, """public class Money : IEquatable<Money>
{
    public decimal Amount { get; }
    public string Currency { get; }

    public Money(decimal amount, string currency)
        => (Amount, Currency) = (amount, currency);

    public bool Equals(Money? other)
        => other is not null && Amount == other.Amount && Currency == other.Currency;

    public override bool Equals(object? obj) => Equals(obj as Money);
    public override int GetHashCode() => HashCode.Combine(Amount, Currency);
    public override string ToString() => $"Money {{ Amount = {Amount}, Currency = {Currency} }}";
}""")

    para(d, "C# 9 dan boshlab shu kodning hammasi bitta qatorga sig'adi:")

    code(d, """public record Money(decimal Amount, string Currency);""")

    # ───────────────────────────────────────────
    h1(d, "2. Kompilyator nimani o'zi yozadi")

    bullets(d, [
        "**Konstruktor** — pozitsion parametrlardan (primary constructor).",
        "**`init` xossalari** — yaratilgandan keyin o'zgartirilmaydi.",
        "**Qiymat bo'yicha tenglik** — `Equals`, `GetHashCode`, `==` va `!=`.",
        "**`ToString()`** — hamma xossa qiymati bilan, debug uchun qulay.",
        "**`Deconstruct`** — pattern matching va dekonstruksiya uchun.",
        "**`with` ifodasi** — nusxa olib, bir nechta xossani o'zgartirish.",
    ])

    code(d, """var a = new Money(100m, "UZS");
var b = new Money(100m, "UZS");

Console.WriteLine(a == b);           // True — qiymat bo'yicha
Console.WriteLine(a);                // Money { Amount = 100, Currency = UZS }

var (amount, currency) = a;          // dekonstruksiya""")

    para(d, "Oddiy klassda `a == b` natijasi `False` bo'lardi, chunki ular "
            "havola bo'yicha taqqoslanadi. Record'da esa tenglik tarkibiga "
            "qarab aniqlanadi — bu ularning eng muhim farqi.")

    # ───────────────────────────────────────────
    h1(d, "3. with ifodasi")

    para(d, "Record o'zgarmas bo'lgani uchun xossani o'zgartirish uchun yangi "
            "nusxa yasaladi. `with` buni qisqa qiladi:")

    code(d, """var original = new Money(100m, "UZS");
var doubled = original with { Amount = 200m };

// original o'zgarmagan
Console.WriteLine(original.Amount);    // 100
Console.WriteLine(doubled.Currency);   // UZS — ko'chib o'tdi""")

    para(d, "`with` xossalarni ko'chirish uchun yashirin copy-konstruktordan "
            "foydalanadi. Uni o'zim ham e'lon qilishim mumkin, agar nusxa "
            "olishda qo'shimcha mantiq kerak bo'lsa.")

    note(d, "Muhim",
         "Nusxa olish **sayoz** (shallow). Record ichida `List<T>` bo'lsa, "
         "nusxa va asl obyekt bitta ro'yxatni ulashadi — ya'ni biri orqali "
         "ro'yxatga element qo'shilsa, ikkinchisida ham ko'rinadi. "
         "Shuning uchun record ichida o'zgaruvchan kolleksiya saqlashdan "
         "qochaman.")

    # ───────────────────────────────────────────
    h1(d, "4. Record turlari")

    code(d, """// reference tur (standart)
public record Customer(Guid Id, string Name);
public record class Order(Guid Id, decimal Total);     // aynan shu narsa

// qiymat turi
public record struct Point(int X, int Y);

// o'zgarmas qiymat turi
public readonly record struct Coordinate(double Lat, double Lon);""")

    para(d, "`record struct` da xossalar standart holda **o'zgaruvchan** "
            "bo'ladi — bu `record class` dan farq qiladi. O'zgarmaslik kerak "
            "bo'lsa `readonly record struct` yoziladi.")

    para(d, "Kichik, o'zgarmas, qiymat semantikasiga ega turlar uchun "
            "`readonly record struct` yaxshi tanlov: heap da obyekt "
            "yaratilmaydi, shuning uchun GC ga yuk tushmaydi.")

    # ───────────────────────────────────────────
    h1(d, "5. Record ichida qo'shimcha a'zolar")

    para(d, "Record oddiy klass kabi metod, xossa va validatsiyaga ega "
            "bo'lishi mumkin:")

    code(d, """public record Money(decimal Amount, string Currency)
{
    public bool IsZero => Amount == 0;

    public Money Add(Money other)
    {
        if (other.Currency != Currency)
            throw new InvalidOperationException("Valyutalar mos emas");
        return this with { Amount = Amount + other.Amount };
    }
}""")

    h2(d, "Validatsiya")

    code(d, """public record Money
{
    public decimal Amount { get; }
    public string Currency { get; }

    public Money(decimal amount, string currency)
    {
        if (amount < 0) throw new ArgumentOutOfRangeException(nameof(amount));
        if (currency.Length != 3) throw new ArgumentException("ISO kod kerak");

        Amount = amount;
        Currency = currency;
    }
}""")

    para(d, "Pozitsion sintaksis bilan validatsiya qo'shish uchun esa "
            "`init` aksessorini qo'lda yozish kerak bo'ladi — shuning uchun "
            "qattiq validatsiya kerak bo'lsa to'liq shaklga o'taman.")

    # ───────────────────────────────────────────
    h1(d, "6. Meros va tenglik")

    code(d, """public abstract record Shape;
public record Circle(double Radius) : Shape;
public record Square(double Side) : Shape;""")

    para(d, "Record'lar meros olishi mumkin, lekin tenglikda bir nozik "
            "qoida bor: tenglik **aniq turni** ham tekshiradi. Shuning uchun "
            "bir xil maydonli ikki turli record teng bo'lmaydi:")

    code(d, """public record A(int X);
public record B(int X) : A(X);

A first = new A(1);
A second = new B(1);
Console.WriteLine(first == second);    // False — turlar har xil""")

    para(d, "Buni kompilyator yashirin `EqualityContract` xossasi orqali "
            "amalga oshiradi. Oddiy klassda `Equals` ni qo'lda yozganda "
            "aynan shu xato ko'p qilinadi, record esa to'g'ri xatti-harakatni "
            "o'zi beradi.")

    # ───────────────────────────────────────────
    h1(d, "7. Qachon record, qachon class")

    table(d, ["Holat", "Tanlov"],
          [["DTO, API so'rov/javob modeli", "`record`"],
           ["Domen hodisasi (event)", "`record`"],
           ["Value object (`Money`, `Address`)", "`record` yoki `record struct`"],
           ["Konfiguratsiya obyekti", "`class` (binding `set` talab qiladi)"],
           ["EF Core entity", "`class`"],
           ["Holati o'zgaradigan domen obyekti", "`class`"]],
          widths=[7.2, 7.3])

    para(d, "EF Core entity'si uchun record ishlatmaslik sababim — entity "
            "o'zgaradigan, kalit bo'yicha aniqlanadigan obyekt. Record esa "
            "qiymat bo'yicha tenglikni beradi, bu entity semantikasiga "
            "qarshi: ikki alohida mijoz bir xil ismga ega bo'lsa, ular teng "
            "emas. Ustiga change tracking o'zgarmas xossalar bilan "
            "noqulay ishlaydi.")

    note(d, "Qisqa qoida",
         "Obyekt **nima ekanligi** uning maydonlari bilan to'liq "
         "aniqlanadimi? Agar ha — record. Agar obyektning o'ziga xosligi "
         "(identity) muhim bo'lsa — class.")

    sources(d, [
        ("Records — C# reference",
         "https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/builtin-types/record"),
        ("Choosing between class, record and struct",
         "https://learn.microsoft.com/en-us/dotnet/standard/design-guidelines/choosing-between-class-and-struct"),
        ("with expression",
         "https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/operators/with-expression"),
    ])
