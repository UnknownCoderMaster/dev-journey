# -*- coding: utf-8 -*-
"""SignalR transport tanlash tartibi va har birining imkoniyatlari."""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
os.makedirs(OUT, exist_ok=True)

INK, MUTED = "#1a1a1a", "#6b7280"
C_WS, C_SSE, C_LP, C_NEG = "#1e7e4f", "#b8860b", "#c0392b", "#1f4e79"

fig, ax = plt.subplots(figsize=(12.2, 5.2))
fig.patch.set_facecolor("white")
ax.set_xlim(0, 100)
ax.set_ylim(0, 50)
ax.axis("off")


def box(x, y, w, h, title, lines, color):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0",
                                fc="white", ec=color, lw=2.0, zorder=3))
    ax.text(x + w / 2, y + h - 4.2, title, ha="center", va="center", zorder=4,
            fontsize=10.5, fontweight="bold", color=color)
    for i, ln in enumerate(lines):
        ax.text(x + w / 2, y + h - 9.0 - i * 4.0, ln, ha="center", va="center",
                zorder=4, fontsize=8.2, color=MUTED)


# negotiate
ax.add_patch(FancyBboxPatch((28, 40), 44, 8, boxstyle="round,pad=0",
                            fc="white", ec=C_NEG, lw=2.0, zorder=3))
ax.text(50, 45.6, "POST /hub/negotiate", ha="center", va="center", zorder=4,
        fontsize=10.2, fontweight="bold", color=C_NEG)
ax.text(50, 41.8, "server qo'llab-quvvatlaydigan transportlarni e'lon qiladi",
        ha="center", va="center", zorder=4, fontsize=8.2, color=MUTED)

box(3, 8, 28, 24, "1.  WebSockets",
    ["bitta doimiy ulanish", "ikki tomonlama", "eng kam kechikish",
     "proxy bloklashi mumkin"], C_WS)
box(36, 8, 28, 24, "2.  Server-Sent Events",
    ["faqat server → mijoz", "mijozdan yuborish uchun",
     "alohida HTTP so'rov", "brauzerda keng qo'llanadi"], C_SSE)
box(69, 8, 28, 24, "3.  Long Polling",
    ["har xabar — yangi so'rov", "eng ko'p tarmoq yuki",
     "deyarli hamma joyda ishlaydi", "oxirgi zaxira"], C_LP)

for x, color in ((17, C_WS), (50, C_SSE), (83, C_LP)):
    ax.add_patch(FancyArrowPatch((50, 39.6), (x, 32.4), arrowstyle="-|>",
                                 mutation_scale=13, color=color, lw=1.5,
                                 zorder=2, connectionstyle="arc3,rad=0.0"))

for x0, x1 in ((31.4, 35.6), (64.4, 68.6)):
    ax.add_patch(FancyArrowPatch((x0, 20), (x1, 20), arrowstyle="-|>",
                                 mutation_scale=12, color=MUTED, lw=1.4, zorder=2))
    ax.text((x0 + x1) / 2, 22.4, "ishlamasa", ha="center", va="center",
            fontsize=7.6, color=MUTED, style="italic",
            bbox=dict(fc="white", ec="none", pad=1.5))

ax.text(50, 3.2,
        "Mijoz ro'yxatdagi birinchi mos transportni tanlaydi; u ishlamasa keyingisiga o'tadi. "
        "Ilova kodi qaysi transport tanlanganini bilmaydi.",
        ha="center", va="center", fontsize=9.0, color=INK, linespacing=1.4)

ax.set_title("SignalR da transport tanlash tartibi",
             fontsize=13.0, fontweight="bold", color=INK, pad=12)

out = os.path.join(OUT, "signalr_transports.png")
fig.savefig(out, dpi=190, facecolor="white", bbox_inches="tight")
print("saqlandi:", out)
