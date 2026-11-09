# -*- coding: utf-8 -*-
"""TPH / TPT / TPC — bitta ierarxiya uchun uch xil jadval sxemasi."""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")
os.makedirs(OUT, exist_ok=True)

INK, MUTED, LINE = "#1a1a1a", "#6b7280", "#9ca3af"
C_TPH, C_TPT, C_TPC = "#1f4e79", "#1e7e4f", "#b8860b"

fig, axes = plt.subplots(1, 3, figsize=(13.4, 4.5))
fig.patch.set_facecolor("white")


def tbl(ax, x, y, w, name, cols, color, note=None):
    """Ustunlar ro'yxati bilan jadval qutisi chizadi. Balandligini qaytaradi."""
    rh = 2.5
    h = rh * (len(cols) + 1)
    ax.add_patch(FancyBboxPatch((x, y - h), w, h, boxstyle="round,pad=0",
                                fc="white", ec=color, lw=1.8, zorder=3))
    # sarlavha yo'lagi
    ax.add_patch(FancyBboxPatch((x, y - rh), w, rh, boxstyle="round,pad=0",
                                fc=color, ec=color, lw=1.8, zorder=4))
    ax.text(x + w / 2, y - rh * 0.55, name, ha="center", va="center", zorder=5,
            fontsize=8.6, fontweight="bold", color="white")
    for i, (c, dim) in enumerate(cols):
        ax.text(x + 1.2, y - rh * (i + 1) - rh * 0.55, c, ha="left", va="center",
                zorder=5, fontsize=7.4, color=(MUTED if dim else INK),
                style=("italic" if dim else "normal"))
        if i < len(cols) - 1:
            ax.plot([x, x + w], [y - rh * (i + 2)] * 2, color="#e5e7eb",
                    lw=0.7, zorder=4)
    if note:
        ax.text(x + w / 2, y - h - 1.4, note, ha="center", va="top",
                fontsize=7.0, color=MUTED, style="italic", linespacing=1.3)
    return h


for ax in axes:
    ax.set_xlim(0, 44)
    ax.set_ylim(21, 60)
    ax.axis("off")

# ── TPH ────────────────────────────────────────
ax = axes[0]
ax.set_title("TPH — bitta jadval", fontsize=11, fontweight="bold",
             color=C_TPH, pad=14)
tbl(ax, 4, 52, 36, "payments",
    [("Id, Amount, CreatedAt", False),
     ("PaymentType  (diskriminator)", False),
     ("MaskedCardNumber   NULL", True),
     ("BankName           NULL", True),
     ("CashierName        NULL", True)],
    C_TPH,
    note="Bo'sh kataklar bor, lekin JOIN yo'q.\nNOT NULL qo'yib bo'lmaydi.")

# ── TPT ────────────────────────────────────────
ax = axes[1]
ax.set_title("TPT — tipga bitta jadval", fontsize=11, fontweight="bold",
             color=C_TPT, pad=14)
tbl(ax, 11, 56, 22, "payments", [("Id, Amount, CreatedAt", False)], C_TPT)
tbl(ax, 0.5, 40, 21, "card_payments",
    [("Id  (FK → payments)", True),
     ("MaskedCardNumber", False),
     ("BankName", False)], C_TPT)
tbl(ax, 23.5, 40, 20, "cash_payments",
    [("Id  (FK → payments)", True),
     ("CashierName", False)], C_TPT)
for xs in ((16.4, 11.2), (27.6, 32.8)):
    ax.add_patch(FancyArrowPatch((xs[1], 40.3), (xs[0], 50.7),
                                 arrowstyle="-|>", mutation_scale=11,
                                 color=LINE, lw=1.3, zorder=2))
ax.text(22, 27.5,
        "Umumiy ustunlar bir joyda saqlanadi.\n"
        "Har bir so'rov JOIN talab qiladi.",
        ha="center", va="top", fontsize=7.0, color=MUTED,
        style="italic", linespacing=1.3)

# ── TPC ────────────────────────────────────────
ax = axes[2]
ax.set_title("TPC — konkret tipga jadval", fontsize=11, fontweight="bold",
             color=C_TPC, pad=14)
tbl(ax, 1, 52, 42, "card_payments",
    [("Id, Amount, CreatedAt", True),
     ("MaskedCardNumber, BankName", False)], C_TPC)
tbl(ax, 1, 36, 42, "cash_payments",
    [("Id, Amount, CreatedAt", True),
     ("CashierName", False)], C_TPC)
ax.text(22, 26.5,
        "Bazaviy tip uchun jadval yo'q.\n"
        "Umumiy ustunlar takrorlanadi; Id lar\n"
        "jadvallar aro ham noyob bo'lishi shart.",
        ha="center", va="top", fontsize=7.0, color=MUTED,
        style="italic", linespacing=1.3)

fig.suptitle("Payment → CardPayment, CashPayment ierarxiyasi uchun uch xil mapping",
             fontsize=12.5, fontweight="bold", color=INK, y=1.03)

out = os.path.join(OUT, "inheritance_strategies.png")
fig.savefig(out, dpi=190, facecolor="white", bbox_inches="tight")
print("saqlandi:", out)
