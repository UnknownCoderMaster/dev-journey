# -*- coding: utf-8 -*-
from docbuild import *

TOPIC = "Python dasturlash tili"
CATEGORY = "AI / Machine Learning"
TITLE = "Python Dasturlash Tili"
SUBTITLE = "C# dasturchisi nuqtai nazaridan asoslar"
FILENAME = "Python dasturlash tili.docx"


def build(d):
    h1(d, "1. Nima uchun Python")

    para(d, "Backend dasturchisi uchun Python odatda asosiy til emas, "
            "lekin u bir nechta sohada amalda standart hisoblanadi: "
            "ma'lumotlarni tahlil qilish, mashinani o'qitish, "
            "avtomatlashtirish skriptlari va ma'lumot ko'chirish.")

    note(d, "Men uni shunday ishlataman:",
         "Bir martalik vazifalar uchun — ma'lumotni tozalash, hisobot "
         "tayyorlash, fayllarni ommaviy qayta nomlash. Bunday ish uchun "
         "`.NET` loyihasi yaratish, qurish va ishga tushirish ortiqcha "
         "bo'ladi; Python da esa bitta fayl yozib, darhol "
         "bajaraveraman.")

    # ───────────────────────────────────────────
    h1(d, "2. C# bilan asosiy farqlar")

    table(d, ["Jihat", "C#", "Python"],
          [["Tiplar", "Statik, kompilyatsiyada", "Dinamik, ish vaqtida"],
           ["Blok chegarasi", "Jingalak qavs", "Chekinish (indentation)"],
           ["Nomlash", "`PascalCase`", "`snake_case`"],
           ["Kirish nuqtasi", "`Main` metodi", "Fayl yuqoridan pastga"],
           ["Bajarish", "Kompilyatsiya qilinadi", "Interpretatsiya "
                                                  "qilinadi"]],
          widths=[3.4, 6.0, 6.1])

    code(d, """# Chekinish sintaksisning bir qismi
def calculate_discount(total, years):
    if years >= 5:
        rate = 0.15
    elif years >= 2:
        rate = 0.10
    else:
        rate = 0.05

    return round(total * rate, 2)""")

    note(d, "Chekinish eng katta moslashish nuqtasi bo'ldi:",
         "C# da bo'shliqlar faqat o'qish uchun. Python da esa ular "
         "mantiqni belgilaydi — bitta bo'shliq yetishmasa, kod "
         "boshqacha ishlaydi yoki umuman ishlamaydi. Shuning uchun men "
         "muharrirda avtomatik formatlashni darhol yoqib qo'yaman.")

    # ───────────────────────────────────────────
    h1(d, "3. Asosiy tiplar")

    code(d, """# Ro'yxat — o'zgaruvchan
books = ["Alpomish", "O'tkan kunlar", "Mehrobdan chayon"]
books.append("Sarob")
print(books[0], books[-1])      # birinchi va oxirgi

# Kesish (slicing)
print(books[1:3])               # 1 dan 3 gacha
print(books[::-1])              # teskari

# Lug'at — C# dagi Dictionary
prices = {"Alpomish": 45000, "Sarob": 38000}
prices["Yangi"] = 52000
print(prices.get("Yo'q", 0))    # sukutdagi qiymat bilan

# To'plam — noyob qiymatlar
tags = {"roman", "tarix", "roman"}      # ikkita element qoladi

# Kortej — o'zgarmas
point = (41.2995, 69.2401)
lat, lon = point                         # ajratib olish""")

    h2(d, "3.1 Ro'yxat generatorlari")

    code(d, """# C# dagi LINQ ga o'xshash, lekin tilga o'rnatilgan
expensive = [b for b in books if b.price > 50000]

names = [b.title.upper() for b in books]

by_id = {b.id: b for b in books}

# Shartli ifoda
labels = ["Qimmat" if b.price > 50000 else "Arzon" for b in books]""")

    note(d, "Bu sintaksis boshida g'alati ko'rindi, lekin tez o'rganiladi:",
         "`[x for x in items if condition]` aslida "
         "`items.Where(condition).Select(x => x)` bilan bir xil. Faqat "
         "tartib teskari — natija oldinda, manba keyin. Bir necha "
         "marta yozgandan keyin u tabiiy bo'lib qoladi.")

    # ───────────────────────────────────────────
    h1(d, "4. Tip ishoralari")

    para(d, "Python dinamik tilligicha qoladi, lekin tip ishoralari "
            "kodni o'qiladigan qiladi va muharrir yordamini "
            "yaxshilaydi.")

    code(d, """from dataclasses import dataclass
from datetime import date


@dataclass
class Book:
    id: int
    title: str
    price: float
    published: date | None = None


def find_expensive(books: list[Book], threshold: float) -> list[Book]:
    return [b for b in books if b.price > threshold]""")

    note(d, "`@dataclass` — C# dagi `record` ga eng yaqin narsa:",
         "U konstruktor, `__eq__` va `__repr__` ni avtomatik "
         "yaratadi. Usiz har bir klass uchun `__init__` ni qo'lda "
         "yozish kerak bo'ladi.")

    code(d, """# Tiplarni tekshirish
pip install mypy
mypy script.py""")

    note(d, "Tip ishoralari ish vaqtida tekshirilmaydi:",
         "Ular faqat hujjat va vositalar uchun. `def f(x: int)` deb "
         "yozsam ham, unga matn uzatish mumkin va Python shikoyat "
         "qilmaydi. Tekshirish uchun `mypy` kabi alohida vosita "
         "kerak. Bu C# dan kelgan odam uchun kutilmagan jihat.")

    # ───────────────────────────────────────────
    h1(d, "5. Virtual muhit va paketlar")

    code(d, """# Virtual muhit yaratish
python -m venv .venv

# Faollashtirish
.venv\\Scripts\\activate        # Windows
source .venv/bin/activate      # Linux/macOS

# Paket o'rnatish
pip install pandas openpyxl requests

# Bog'liqliklarni saqlash
pip freeze > requirements.txt
pip install -r requirements.txt""")

    note(d, "Virtual muhit majburiy amaliyot:",
         "Usiz paketlar tizim darajasida o'rnatiladi va turli "
         "loyihalar bir-birining versiyalarini buzadi. `.NET` da bu "
         "muammo yo'q — har bir loyiha o'z paketlarini oladi. Python "
         "da esa buni men o'zim ta'minlashim kerak.")

    note(d, "`.venv` papkasini git ga qo'ymaslik kerak:",
         "U yuzlab megabayt bo'lishi va platformaga bog'liq fayllarni "
         "o'z ichiga olishi mumkin. Git ga faqat `requirements.txt` "
         "tushadi.")

    # ───────────────────────────────────────────
    h1(d, "6. Amaliy misollar")

    h2(d, "6.1 Excel bilan ishlash")

    code(d, """import openpyxl

workbook = openpyxl.load_workbook("orders.xlsx")
sheet = workbook.active

total = 0
for row in sheet.iter_rows(min_row=2, values_only=True):
    order_id, customer, amount = row[:3]

    if amount is None:
        print(f"Bo'sh summa: {order_id}")
        continue

    total += amount

print(f"Jami: {total:,.2f}")""")

    h2(d, "6.2 Bazadan o'qish")

    code(d, """import psycopg

with psycopg.connect(
    "host=localhost dbname=app user=app password=secret"
) as conn:
    with conn.cursor() as cur:
        cur.execute(
            "SELECT id, title, price FROM books WHERE price > %s",
            (50_000,)                    # parametr — injectiondan himoya
        )

        for book_id, title, price in cur:
            print(f"{book_id:>5}  {title:<40}  {price:>10,.2f}")""")

    note(d, "`%s` bu yerda formatlash emas, parametr belgisi:",
         "Uni Python ning `%` operatori bilan chalkashtirmaslik kerak. "
         "Agar men `cur.execute(f\"... {value}\")` deb yozsam, bu SQL "
         "injection ga ochiq bo'ladi. Parametrlarni alltid ikkinchi "
         "argument sifatida uzatish kerak.")

    h2(d, "6.3 HTTP so'rovlar")

    code(d, """import requests

response = requests.get(
    "https://api.example.com/books",
    headers={"Authorization": f"Bearer {token}"},
    timeout=30
)

response.raise_for_status()
books = response.json()

for book in books:
    print(book["title"], book["price"])""")

    h2(d, "6.4 Fayllar bilan ishlash")

    code(d, """from pathlib import Path
import json

data_dir = Path("data")

for file in data_dir.glob("*.json"):
    content = json.loads(file.read_text(encoding="utf-8"))
    print(f"{file.name}: {len(content)} ta yozuv")

# Yozish
output = Path("result.json")
output.write_text(
    json.dumps(results, ensure_ascii=False, indent=2),
    encoding="utf-8"
)""")

    note(d, "`ensure_ascii=False` ni yozishni unutmaslik kerak:",
         "Usiz o'zbekcha harflar `\\u0279` ko'rinishidagi kodlarga "
         "aylanadi. Fayl texnik jihatdan to'g'ri bo'ladi, lekin uni "
         "odam o'qiy olmaydi.")

    # ───────────────────────────────────────────
    h1(d, "7. Ma'lumot tahlili uchun pandas")

    code(d, """import pandas as pd

df = pd.read_excel("orders.xlsx")

# Ko'rib chiqish
print(df.head())
print(df.info())
print(df.describe())

# Filtrlash va guruhlash
paid = df[df["status"] == "paid"]

summary = (paid
    .groupby("customer_id")
    .agg(total=("amount", "sum"), count=("id", "count"))
    .sort_values("total", ascending=False)
    .head(10))

print(summary)

# Saqlash
summary.to_excel("top-customers.xlsx")""")

    note(d, "pandas — Python ni o'rganishga arzitadigan sabablardan biri:",
         "Yuqoridagi besh qator `.NET` da o'nlab qator bo'lardi. "
         "Ma'lumotni tezda ko'rib chiqish, guruhlash va hisobot "
         "chiqarish uchun unga teng keladigan vosita kam.")

    # ───────────────────────────────────────────
    h1(d, "8. Skript tuzilmasi")

    code(d, """#!/usr/bin/env python3
\"\"\"Buyurtmalar hisobotini tayyorlaydi.\"\"\"

import argparse
import logging
import sys
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser(description="Hisobot tayyorlash")
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", default=Path("report.xlsx"), type=Path)
    parser.add_argument("--verbose", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    if not args.input.exists():
        logger.error("Fayl topilmadi: %s", args.input)
        return 1

    try:
        process(args.input, args.output)
        logger.info("Tayyor: %s", args.output)
        return 0
    except Exception:
        logger.exception("Xatolik yuz berdi")
        return 1


if __name__ == "__main__":
    sys.exit(main())""")

    note(d, "`if __name__ == \"__main__\":` nima qiladi:",
         "Fayl to'g'ridan-to'g'ri ishga tushirilsa, `__name__` "
         "qiymati `\"__main__\"` bo'ladi. Agar u boshqa fayldan "
         "import qilinsa — modul nomi bo'ladi. Shu shart tufayli bir "
         "fayl ham skript, ham kutubxona bo'la oladi.")

    # ───────────────────────────────────────────
    h1(d, "9. C# dan kelganda e'tibor beriladigan nuqtalar")

    bullets(d, [
        "**O'zgaruvchan sukutdagi argument** — `def f(items=[])` "
        "xavfli, chunki ro'yxat bir marta yaratiladi va chaqiruvlar "
        "orasida saqlanadi.",
        "**Hamma narsa havola bo'yicha uzatiladi** — ro'yxatni "
        "funksiyaga uzatsam va u o'zgartirsa, asl ro'yxat ham "
        "o'zgaradi.",
        "**`is` va `==` farqi** — birinchisi bir xil obyektmi, "
        "ikkinchisi teng qiymatmi.",
        "**Istisnolar `try/except` bilan ushlanadi**, `catch` emas.",
        "**`None` — `null` ning muqobili**, lekin `is None` bilan "
        "tekshiriladi.",
    ])

    code(d, """# Xavfli
def add_item(item, items=[]):
    items.append(item)
    return items

# To'g'ri
def add_item(item, items=None):
    if items is None:
        items = []
    items.append(item)
    return items""")

    # ───────────────────────────────────────────
    h1(d, "10. Xulosa")

    bullets(d, [
        "Python dinamik tipli; chekinish sintaksisning bir qismi.",
        "Tip ishoralari hujjat uchun — ular ish vaqtida "
        "tekshirilmaydi.",
        "`@dataclass` C# dagi `record` ga eng yaqin tushuncha.",
        "Virtual muhit majburiy — usiz loyihalar bir-birini buzadi.",
        "Ro'yxat generatorlari LINQ ning tilga o'rnatilgan muqobili.",
        "SQL parametrlarini `%s` orqali uzatish kerak, "
        "formatlashtirmaslik.",
        "`ensure_ascii=False` kirill va lotin bo'lmagan harflarni "
        "o'qiladigan qoldiradi.",
        "pandas ma'lumot tahlilini sezilarli soddalashtiradi.",
        "O'zgaruvchan sukutdagi argument — eng ko'p uchraydigan "
        "tuzoqlardan biri.",
    ])

    sources(d, [
        ("Python documentation",
         "https://docs.python.org/3/"),
        ("The Python Tutorial",
         "https://docs.python.org/3/tutorial/"),
        ("PEP 8 — Style Guide for Python Code",
         "https://peps.python.org/pep-0008/"),
        ("pandas documentation",
         "https://pandas.pydata.org/docs/"),
    ])
