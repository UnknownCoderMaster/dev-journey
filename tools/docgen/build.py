# -*- coding: utf-8 -*-
"""Hujjatlarni yasash uchun runner.

Ishlatish:
    python build.py              # docs/ papkasidagi hamma modulni yasaydi
    python build.py change_tracking dbcontext_lifecycle
    python build.py --list       # tayyor modullar ro'yxati
    python build.py --todo       # hali yozilmagan mavzular

Daraja tanlash (standart — Middle D):
    python build.py --junior-a
"""
import importlib, os, sys, traceback

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

BASE = r"D:\ExtraWork\dev-journey\PersonalLearning"

TARGETS = {
    "middle-d": ("Middle D", "docs"),
    "junior-a": ("Junior A", "docs_ja"),
}

LEVEL, DOCS_PKG = TARGETS["middle-d"]
OUT_DIR = os.path.join(BASE, LEVEL)


def _select(argv):
    """--junior-a kabi bayroq bo'yicha daraja va papkani tanlaydi."""
    global LEVEL, DOCS_PKG, OUT_DIR
    for key, (level, pkg) in TARGETS.items():
        if f"--{key}" in argv:
            LEVEL, DOCS_PKG = level, pkg
            OUT_DIR = os.path.join(BASE, level)
    return [a for a in argv if a.lstrip("-") not in TARGETS]


def _modules():
    p = os.path.join(HERE, DOCS_PKG)
    if not os.path.isdir(p):
        return []
    return sorted(f[:-3] for f in os.listdir(p)
                  if f.endswith(".py") and not f.startswith("_"))


def build_one(name):
    from docbuild import new_doc, title, meta_block
    mod = importlib.import_module(f"{DOCS_PKG}.{name}")
    d = new_doc()
    title(d, mod.TITLE, mod.SUBTITLE)
    meta_block(d, [("Mavzu", mod.TOPIC), ("Kategoriya", mod.CATEGORY)])
    mod.build(d)
    out = os.path.join(OUT_DIR, mod.FILENAME)
    try:
        d.save(out)
    except PermissionError:
        return name, None, "FAYL BAND (ochiq turibdi)"
    return name, out, None


def main(argv):
    argv = _select(argv)
    if "--list" in argv:
        for m in _modules():
            print(" ", m)
        return
    if "--todo" in argv:
        import topics
        done = set()
        for m in _modules():
            done.add(importlib.import_module(f"{DOCS_PKG}.{m}").FILENAME)
        rows = topics.load(level=LEVEL)
        todo = [r for r in rows if r[2] not in done]
        print(f"{LEVEL} — tayyor: {len(rows) - len(todo)} / {len(rows)}"
              f"   qoldi: {len(todo)}\n")
        cur = None
        for cat, topic, fn, mark in todo:
            if cat != cur:
                cur = cat
                print(f"\n### {cat}")
            print("   ", fn)
        return

    names = [a for a in argv if not a.startswith("-")] or _modules()
    ok = fail = 0
    for n in names:
        try:
            name, out, err = build_one(n)
            if err:
                print(f"  [X] {n}: {err}"); fail += 1
            else:
                print(f"  [v] {os.path.basename(out)}"); ok += 1
        except Exception:
            print(f"  [X] {n}:"); traceback.print_exc(limit=2); fail += 1
    print(f"\nyasaldi: {ok}   xato: {fail}")


if __name__ == "__main__":
    main(sys.argv[1:])
