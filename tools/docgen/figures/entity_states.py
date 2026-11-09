# -*- coding: utf-8 -*-
"""EF Core entity holatlari va ular orasidagi o'tishlar sxemasi."""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
os.makedirs(OUT, exist_ok=True)

INK, MUTED = "#1a1a1a", "#6b7280"
C_DET, C_ADD, C_UNC, C_MOD, C_DEL = "#6b7280", "#1e7e4f", "#1f4e79", "#b8860b", "#c0392b"

fig, ax = plt.subplots(figsize=(12.6, 6.0))
fig.patch.set_facecolor("white")
ax.set_xlim(0, 100); ax.set_ylim(0, 64); ax.axis("off")

W, H = 24, 11
BOX = {
    "Detached":  (2,  24, C_DET, "Kontekst bu obyektni\nbilmaydi"),
    "Added":     (34, 40, C_ADD, "SaveChanges →  INSERT"),
    "Unchanged": (34, 22, C_UNC, "O'zgarmagan —\nhech narsa qilinmaydi"),
    "Modified":  (68, 40, C_MOD, "SaveChanges →  UPDATE"),
    "Deleted":   (68,  4, C_DEL, "SaveChanges →  DELETE"),
}

for name, (x, y, color, sub) in BOX.items():
    ax.add_patch(FancyBboxPatch((x, y), W, H, boxstyle="round,pad=0",
                                fc="white", ec=color, lw=2.0, zorder=3))
    ax.text(x + W / 2, y + H * 0.64, name, ha="center", va="center", zorder=4,
            fontsize=12.5, fontweight="bold", color=color)
    ax.text(x + W / 2, y + H * 0.26, sub, ha="center", va="center", zorder=4,
            fontsize=8.5, color=MUTED, linespacing=1.4)


def arrow(p1, p2, color, rad=0.0):
    ax.add_patch(FancyArrowPatch(p1, p2, arrowstyle="-|>", mutation_scale=15,
                                 color=color, lw=1.6, zorder=2,
                                 connectionstyle=f"arc3,rad={rad}"))


def label(x, y, text, color):
    ax.text(x, y, text, ha="center", va="center", fontsize=8.8, zorder=5,
            color=color, fontweight="bold", linespacing=1.35,
            bbox=dict(fc="white", ec="none", pad=2.0))


# Detached → Added
arrow((26, 32), (34, 44), C_ADD, rad=0.15)
label(27.5, 40.5, "Add()", C_ADD)

# Detached → Unchanged
arrow((26, 29), (34, 28), C_UNC, rad=-0.1)
label(30, 23.5, "so'rov natijasi\nyoki Attach()", C_UNC)

# Added → Unchanged
arrow((46, 40), (46, 33), C_UNC)
label(39.5, 36.5, "SaveChanges()", C_UNC)

# Unchanged → Modified
arrow((58, 30), (68, 44), C_MOD, rad=0.15)
label(64.5, 35.5, "xossa\no'zgartirildi", C_MOD)

# Modified → Unchanged
arrow((68, 41), (56, 33), C_UNC, rad=0.25)
label(74, 32.0, "SaveChanges()", C_UNC)

# Unchanged → Deleted
arrow((50, 22), (68, 11), C_DEL, rad=-0.18)
label(56, 14.5, "Remove()", C_DEL)

ax.text(50, 58.5,
        "Har bir entity kontekst ichida shu besh holatdan birida bo'ladi. "
        "SaveChanges() faqat Added, Modified va Deleted holatidagilarga ta'sir qiladi.",
        ha="center", va="center", fontsize=9.6, color=INK)

ax.text(50, 1.0,
        "Deleted entity SaveChanges() dan keyin Detached holatiga o'tadi.   •   "
        "AsNoTracking() bilan olingan entity umuman kuzatilmaydi — u Detached bo'lib qoladi.",
        ha="center", va="center", fontsize=9.2, color=MUTED, style="italic")

ax.set_title("EF Core da entity holatlari va ular orasidagi o'tishlar",
             fontsize=13.5, fontweight="bold", color=INK, pad=10)

out = os.path.join(OUT, "entity_states.png")
fig.savefig(out, dpi=190, facecolor="white", bbox_inches="tight")
print("saqlandi:", out)
