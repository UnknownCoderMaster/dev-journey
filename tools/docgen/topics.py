# -*- coding: utf-8 -*-
"""Mavzular reyestri — Excel dan o'qiladi va fayl nomlariga aylantiriladi.

Manba: "Даража белгилаш талаблари (1).xlsx", varaq "Функционаллар (Backend new)".
Faqat E ustunida "Xa" belgilangan mavzular olinadi.
"""
import re, warnings, unicodedata

XLSX = r"C:\Users\orzib\OneDrive\Desktop\Даража белгилаш талаблари (1).xlsx"
SHEET = "Функционаллар (Backend new)"
LEVEL = "Middle D"

# Windows fayl nomida ishlatib bo'lmaydigan belgilar
_BAD = r'\/:*?"<>|'

# Excel dagi matn fayl nomi uchun noqulay bo'lgan bir nechta holat
_OVERRIDES = {
    "Python dasturlashtili": "Python dasturlash tili",
    ".dockerignore": "dockerignore fayli",
    "vim , nano ,sudo , cat": "vim, nano, sudo, cat",
    "df , ls , mkdir, cd , pwd , chmod ,touch": "df, ls, mkdir, cd, pwd, chmod, touch",
    "Trigger,Sequence": "Trigger va Sequence",

    # Junior A
    "Delgates, Event, Anonymous functions, Lambda functions, Action, Func, Predicate":
        "Delegates, Event, Lambda, Action, Func, Predicate",
    "Controller action return types, ActionResult vs IActionResult, "
    "Synchronous and Asynchronous action, HttpResults type":
        "Controller action return types, ActionResult vs IActionResult",
    "Query combining (UNION , UNION ALL,EXCEPT , EXCEPT ALL ,INTERSECT, INTERSECTALL)":
        "Query combining (UNION, EXCEPT, INTERSECT)",
    "DI Container, Service Lifetimes(Scope,Transient,Singleton)":
        "DI Container, Service Lifetimes",
    "GC , using , Dispose, Finalize": "GC, using, Dispose, Finalize",
    "ActionResult,Status Codes,Routing": "ActionResult, Status Codes, Routing",
    "git log, git checkout,": "git log, git checkout",
    "Authentication va Authorization. Ularning farqlari.":
        "Authentication va Authorization farqlari",
    "How to stop EF creating indexes for foreign keys":
        "Foreign key uchun indeks yaratishni to'xtatish",
    "Value Comparers, Background, Shallow vs. deep comparison":
        "Value Comparers, Shallow vs deep comparison",
}


def _clean(s):
    s = re.sub(r"\s+", " ", s).strip()
    return s


def filename_for(topic):
    """Mavzu matnidan xavfsiz, lekin mavzuga mos fayl nomi yasaydi."""
    name = _OVERRIDES.get(_clean(topic), _clean(topic))
    name = name.replace("/", "-")          # SQL/NoSQL -> SQL-NoSQL
    for ch in _BAD:
        name = name.replace(ch, "")
    name = name.replace(" ,", ",")
    name = re.sub(r"\s+", " ", name).strip(" .,")
    # juda uzun nomlarni qisqartirish (Windows yo'l chegarasi)
    if len(name) > 90:
        cut = name[:90]
        if "," in cut:
            cut = cut[:cut.rfind(",")]
        name = cut.strip(" ,")
    return name + ".docx"


def load(required_only=True, level=LEVEL):
    """[(kategoriya, mavzu, fayl_nomi, belgi), ...] qaytaradi."""
    warnings.filterwarnings("ignore")
    import openpyxl
    ws = openpyxl.load_workbook(XLSX, data_only=True)[SHEET]
    out = []
    for row in ws.iter_rows(values_only=True):
        v = [("" if c is None else str(c).strip()) for c in row]
        if len(v) < 3 or not any(v):
            continue
        cat, topic, row_level = v[0], _clean(v[1]), v[2]
        if row_level != level or not topic:
            continue
        need = v[4] if len(v) > 4 else ""
        if required_only and need != "Xa":
            continue
        mark = v[5] if len(v) > 5 else ""
        out.append((cat, topic, filename_for(topic), mark))
    return out


if __name__ == "__main__":
    import sys
    lvl = " ".join(a for a in sys.argv[1:] if not a.startswith("-")) or LEVEL
    rows = load(level=lvl)
    print(f"{lvl}, 'Xa' belgilangan: {len(rows)} ta mavzu\n")
    cur = None
    for i, (cat, topic, fn, mark) in enumerate(rows, 1):
        if cat != cur:
            cur = cat
            print(f"\n### {cat}")
        extra = f"   [{mark}]" if mark else ""
        print(f"{i:3}. {fn}{extra}")
