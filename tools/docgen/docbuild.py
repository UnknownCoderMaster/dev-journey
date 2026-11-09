# -*- coding: utf-8 -*-
"""Middle D o'quv hujjatlari uchun .docx quruvchi yordamchilar.

Uslub qoidalari (foydalanuvchi talabi):
  - Matnda rang ishlatilmaydi. Sarlavhalar ham qora.
  - Rang faqat jadval sarlavhasida (juda yengil kulrang) va
    o'zim yasagan sxemalarda bo'lishi mumkin.
  - Jadvaldan kam foydalaniladi.
Format "Docker rabbit postgresni sozlash.docx" dan olingan:
Segoe UI 10.5pt, kod uchun Consolas, A4, chekkalar 1440/1800 twip.
"""
import re
from docx import Document
from docx.shared import Pt, Cm, RGBColor, Twips
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

BODY_FONT = "Segoe UI"
CODE_FONT = "Consolas"
BODY_SIZE = Pt(10.5)

INK = RGBColor(0x00, 0x00, 0x00)
SOFT = RGBColor(0x3A, 0x3A, 0x3A)

CODE_BG = "F4F4F4"
TBL_HDR_BG = "EDEDED"
NOTE_BG = "F7F7F7"
RULE = "BFBFBF"


def _shade(obj, hexcolor):
    el = obj._p if hasattr(obj, "_p") else obj._tc
    pr = el.get_or_add_pPr() if hasattr(el, "get_or_add_pPr") else el.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), hexcolor)
    pr.append(shd)


def _border(par, color=RULE, size=6, sides=("left",)):
    pPr = par._p.get_or_add_pPr()
    bdr = OxmlElement("w:pBdr")
    for s in sides:
        e = OxmlElement(f"w:{s}")
        e.set(qn("w:val"), "single")
        e.set(qn("w:sz"), str(size))
        e.set(qn("w:space"), "6")
        e.set(qn("w:color"), color)
        bdr.append(e)
    pPr.append(bdr)


def _rich(p, text, size=None, italic=False):
    """`kod` va **qalin** belgilarini tanib, mos run lar yasaydi. Rang yo'q."""
    size = size or BODY_SIZE
    for chunk in re.split(r"(`[^`]+`|\*\*[^*]+\*\*)", text):
        if not chunk:
            continue
        if chunk.startswith("`") and chunk.endswith("`"):
            r = p.add_run(chunk[1:-1])
            r.font.name = CODE_FONT
            r.font.size = Pt(size.pt - 1)
        elif chunk.startswith("**") and chunk.endswith("**"):
            r = p.add_run(chunk[2:-2])
            r.font.bold = True
            r.font.name, r.font.size = BODY_FONT, size
        else:
            r = p.add_run(chunk)
            r.font.name, r.font.size = BODY_FONT, size
        r.font.color.rgb = INK
        r.font.italic = italic
    return p


def new_doc():
    d = Document()
    s = d.sections[0]
    s.page_width, s.page_height = Twips(11906), Twips(16838)
    s.top_margin, s.bottom_margin = Twips(1440), Twips(2016)
    s.left_margin = s.right_margin = Twips(1800)

    st = d.styles["Normal"]
    st.font.name = BODY_FONT
    st.font.size = BODY_SIZE
    st.font.color.rgb = INK
    st.element.rPr.rFonts.set(qn("w:eastAsia"), BODY_FONT)
    st.paragraph_format.space_after = Pt(6)
    st.paragraph_format.line_spacing = 1.15

    for name, size in (("Heading 1", 15), ("Heading 2", 12), ("Heading 3", 11)):
        h = d.styles[name]
        h.font.name = BODY_FONT
        h.font.size = Pt(size)
        h.font.bold = True
        h.font.color.rgb = INK
        h.paragraph_format.space_before = Pt(14)
        h.paragraph_format.space_after = Pt(5)
    return d


def title(d, text, subtitle=None):
    p = d.add_paragraph()
    r = p.add_run(text)
    r.font.name, r.font.size, r.font.bold, r.font.color.rgb = BODY_FONT, Pt(19), True, INK
    p.paragraph_format.space_after = Pt(2)
    if subtitle:
        q = d.add_paragraph()
        s = q.add_run(subtitle)
        s.font.name, s.font.size, s.font.color.rgb = BODY_FONT, Pt(10.5), SOFT
        q.paragraph_format.space_after = Pt(12)
    return p


def meta_block(d, pairs):
    """Jadval emas — oddiy qatorlar (jadvaldan kam foydalanish talabi)."""
    for k, v in pairs:
        p = d.add_paragraph()
        p.paragraph_format.space_after = Pt(1)
        kr = p.add_run(f"{k}: ")
        kr.font.bold, kr.font.size, kr.font.name = True, Pt(10), BODY_FONT
        kr.font.color.rgb = INK
        vr = p.add_run(v)
        vr.font.size, vr.font.name, vr.font.color.rgb = Pt(10), BODY_FONT, INK
    rule = d.add_paragraph()
    _border(rule, size=4, sides=("bottom",))
    rule.paragraph_format.space_after = Pt(10)


def h1(d, t): return d.add_heading(t, level=1)
def h2(d, t): return d.add_heading(t, level=2)
def h3(d, t): return d.add_heading(t, level=3)


def para(d, text, italic=False):
    return _rich(d.add_paragraph(), text, italic=italic)


def bullets(d, items, numbered=False):
    style = "List Number" if numbered else "List Bullet"
    for it in items:
        p = d.add_paragraph(style=style)
        p.paragraph_format.space_after = Pt(3)
        _rich(p, it)


def code(d, text, caption=None):
    if caption:
        c = d.add_paragraph()
        cr = c.add_run(caption)
        cr.font.size, cr.font.italic, cr.font.name = Pt(9), True, BODY_FONT
        cr.font.color.rgb = SOFT
        c.paragraph_format.space_after = Pt(2)
    lines = text.rstrip("\n").split("\n")
    for i, line in enumerate(lines):
        p = d.add_paragraph()
        pf = p.paragraph_format
        pf.space_before = Pt(5 if i == 0 else 0)
        pf.space_after = Pt(5 if i == len(lines) - 1 else 0)
        pf.left_indent = Cm(0.3)
        pf.line_spacing = 1.0
        r = p.add_run(line if line else " ")
        r.font.name, r.font.size, r.font.color.rgb = CODE_FONT, Pt(9), INK
        _shade(p, CODE_BG)
    d.add_paragraph().paragraph_format.space_after = Pt(4)


def table(d, headers, rows, widths=None):
    t = d.add_table(rows=1, cols=len(headers))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.LEFT
    for i, htxt in enumerate(headers):
        c = t.rows[0].cells[i]
        _shade(c, TBL_HDR_BG)
        r = c.paragraphs[0].add_run(htxt)
        r.font.bold, r.font.size, r.font.name = True, Pt(9.5), BODY_FONT
        r.font.color.rgb = INK
    for row in rows:
        cells = t.add_row().cells
        for i, val in enumerate(row):
            _rich(cells[i].paragraphs[0], str(val), size=Pt(9.5))
    if widths:
        for row in t.rows:
            for i, w in enumerate(widths):
                row.cells[i].width = Cm(w)
    d.add_paragraph().paragraph_format.space_after = Pt(6)
    return t


def note(d, label, text):
    """Eslatma — rangsiz, chap chekkada chiziq va yengil kulrang fon."""
    p = d.add_paragraph()
    _shade(p, NOTE_BG)
    _border(p, color=RULE, size=8, sides=("left",))
    p.paragraph_format.left_indent = Cm(0.35)
    p.paragraph_format.space_before = Pt(6)
    p.paragraph_format.space_after = Pt(8)
    lr = p.add_run(f"{label}  ")
    lr.font.bold, lr.font.size, lr.font.name = True, Pt(9.5), BODY_FONT
    lr.font.color.rgb = INK
    _rich(p, text, size=Pt(9.5))
    return p


def image(d, path, caption=None, width_cm=15.5):
    d.add_picture(path, width=Cm(width_cm))
    d.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
    if caption:
        c = d.add_paragraph()
        c.alignment = WD_ALIGN_PARAGRAPH.CENTER
        cr = c.add_run(caption)
        cr.font.size, cr.font.italic, cr.font.name = Pt(9), True, BODY_FONT
        cr.font.color.rgb = SOFT
        c.paragraph_format.space_after = Pt(10)


def sources(d, items):
    h1(d, "Manbalar")
    for t, u in items:
        p = d.add_paragraph(style="List Bullet")
        p.paragraph_format.space_after = Pt(2)
        r = p.add_run(t + " — ")
        r.font.size, r.font.name, r.font.color.rgb = Pt(9.5), BODY_FONT, INK
        ur = p.add_run(u)
        ur.font.size, ur.font.name, ur.font.color.rgb = Pt(9), CODE_FONT, INK
