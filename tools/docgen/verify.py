# -*- coding: utf-8 -*-
"""Yaratilgan hujjatlarni uslub bo'yicha tekshiradi.

Tekshiriladi:
  - begona rang (faqat 000000 va 3A3A3A ruxsat)
  - kirill harflari (hujjat lotin o'zbek tilida)
  - TaskFlow loyihasining ortiqcha eslatilishi
  - screenshot joylari
  - zip butunligi
"""
import glob, os, re, sys, zipfile
from docx import Document

BASE = r"D:\ExtraWork\dev-journey\PersonalLearning"
DIRS = {"middle-d": "Middle D", "junior-a": "Junior A"}
OUT_DIR = os.path.join(BASE, DIRS["middle-d"])
ALLOWED = {"000000", "3A3A3A"}
# Men qo'lda yozgan hujjatlar — generator ularga tegmaydi, tekshirilmaydi ham
SKIP = {"Docker rabbit postgresni sozlash.docx"}
TASKFLOW_LIMIT = 3          # shu sondan ortiq eslatilsa belgilanadi


def colors_of(doc):
    found = set()
    runs = [r for p in doc.paragraphs for r in p.runs]
    for t in doc.tables:
        for row in t.rows:
            for cell in row.cells:
                runs += [r for p in cell.paragraphs for r in p.runs]
    for r in runs:
        c = r.font.color
        if c is not None and c.rgb is not None:
            found.add(str(c.rgb))
    return found


def check(path):
    name = os.path.basename(path)
    try:
        doc = Document(path)
    except Exception as e:
        return name, None, [f"ochib bo'lmadi ({type(e).__name__})"]

    text = "\n".join(p.text for p in doc.paragraphs)
    problems = []

    stray = sorted(colors_of(doc) - ALLOWED)
    if stray:
        problems.append(f"begona rang: {', '.join(stray)}")

    cyr = sorted(set(re.findall(r"[\u0400-\u04FF]+", text)))
    if cyr:
        problems.append(f"kirill: {', '.join(cyr[:5])}")

    tf = len(re.findall(r"TaskFlow", text, re.I))
    if tf > TASKFLOW_LIMIT:
        problems.append(f"TaskFlow {tf} marta")

    ss = len(re.findall(r"screenshot|skrinshot", text, re.I))
    if ss:
        problems.append(f"screenshot {ss} marta")

    try:
        if zipfile.ZipFile(path).testzip() is not None:
            problems.append("zip buzuq")
    except Exception:
        problems.append("zip o'qilmadi")

    stats = {
        "par": len(doc.paragraphs),
        "tbl": len(doc.tables),
        "img": sum(1 for r in doc.part.rels.values() if "image" in r.reltype),
    }
    return name, stats, problems


def main(argv):
    global OUT_DIR
    for key, folder in DIRS.items():
        if f"--{key}" in argv:
            OUT_DIR = os.path.join(BASE, folder)
    argv = [a for a in argv if a.lstrip("-") not in DIRS]
    only = [a.lower() for a in argv if not a.startswith("-")]
    verbose = "-v" in argv

    bad = ok = 0
    for path in sorted(glob.glob(os.path.join(OUT_DIR, "*.docx"))):
        if os.path.basename(path) in SKIP:
            continue
        name, stats, problems = check(path)
        if only and not any(o in name.lower() for o in only):
            continue
        if problems:
            bad += 1
            print(f"  [X] {name}")
            for p in problems:
                print(f"        - {p}")
        else:
            ok += 1
            if verbose:
                print(f"  [v] {name[:50]:52} "
                      f"par={stats['par']:4} tbl={stats['tbl']} img={stats['img']}")

    print(f"\ntoza: {ok}   muammoli: {bad}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
