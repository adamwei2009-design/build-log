"""Stage 3: turn the SQL answers into three charts.

Each chart answers one question and its title says the answer, so you
don't need to study it to get the point.
"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent / "stage2-sql"))
import run_queries  # noqa: E402

BLUE, ORANGE, GREY, RED, INK = "#2563eb", "#f59e0b", "#9ca3af", "#dc2626", "#111827"
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def style(ax, title, sub):
    ax.set_title(title, loc="left", fontsize=15, fontweight="bold", color=INK, pad=28)
    ax.text(0, 1.02, sub, transform=ax.transAxes, fontsize=10.5, color="#4b5563")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.spines["left"].set_color("#d1d5db")
    ax.spines["bottom"].set_color("#d1d5db")
    ax.tick_params(colors="#374151")


def save(fig, name):
    fig.tight_layout()
    fig.savefig(HERE / name, dpi=150)
    plt.close(fig)


def chart1_months(con):
    rows = run_queries.run(con, run_queries.queries()["q1_busiest_months"][1])[1]
    rep = [r[1] for r in rows]; serv = [r[2] for r in rows]; inst = [r[3] for r in rows]
    fig, ax = plt.subplots(figsize=(9, 4.8))
    ax.plot(MONTHS, rep, color=BLUE, lw=2.6, marker="o", label="Repairs")
    ax.plot(MONTHS, serv, color=ORANGE, lw=2.6, marker="o", label="Services")
    ax.plot(MONTHS, inst, color=GREY, lw=2, marker="o", label="Installs")
    ax.annotate(f"{rep[11]} repairs in Dec", (11, rep[11]), xytext=(7.6, rep[11] - 8), color=BLUE, fontsize=10)
    ax.annotate(f"{min(rep)} a month in summer", (6, min(rep)), xytext=(5.2, min(rep) - 12), color=BLUE, fontsize=10)
    ax.set_ylim(0, max(rep) * 1.15)
    ax.set_ylabel("Jobs requested")
    ax.legend(frameon=False, loc="upper center", ncol=3)
    style(ax, "Repairs more than triple in winter. Services peak in the autumn.",
          "Q1. Jobs requested each month, first visits only, 2025 (made-up data)")
    save(fig, "chart1_busiest_months.png")


def chart2_wait(con):
    rows = run_queries.run(con, run_queries.queries()["q2_repair_wait"][1])[1]
    labels = [r[0] for r in rows]; avg = [r[2] for r in rows]; over5 = [r[3] for r in rows]
    fig, axes = plt.subplots(1, 2, figsize=(9, 4.4))
    for ax, vals, unit, sub in ((axes[0], avg, " days", "Average wait for a repair"),
                                (axes[1], over5, "%", "Share waiting more than 5 days")):
        bars = ax.bar(labels, vals, color=[BLUE, GREY], width=0.55)
        for b, v in zip(bars, vals):
            ax.text(b.get_x() + b.get_width() / 2, v, f"{v}{unit}", ha="center", va="bottom",
                    fontsize=12, fontweight="bold", color=INK)
        ax.set_ylim(0, max(vals) * 1.25)
        ax.set_yticks([])
        ax.set_xlabel(sub, color="#374151", fontsize=10.5, labelpad=8)
        for s in ("top", "right", "left"):
            ax.spines[s].set_visible(False)
    fig.suptitle("Winter repairs wait 1.5 days longer, and 2.5 times the share wait over 5 days",
                 x=0.02, ha="left", fontsize=13.5, fontweight="bold", color=INK)
    fig.text(0.02, 0.88, "Q2. Repairs only. The 12 jobs with impossible dates are left out (made-up data)",
             fontsize=10.5, color="#4b5563")
    fig.tight_layout(rect=(0, 0, 1, 0.86))
    fig.savefig(HERE / "chart2_repair_wait.png", dpi=150)
    plt.close(fig)


def chart3_fix_rate(con):
    rows = run_queries.run(con, run_queries.queries()["q3_first_time_fix"][1])[1]
    rows = sorted(rows, key=lambda r: r[3])
    names = [r[0] for r in rows]; pct = [r[3] for r in rows]; n = [r[1] for r in rows]
    overall = round(100 * sum(r[2] for r in rows) / sum(n), 1)
    fig, ax = plt.subplots(figsize=(9, 5.2))
    # A dot plot, not bars: bars must start at 0, and at 0 the differences vanish.
    # Dots let the axis start at 60% honestly.
    colors = [RED if p == min(pct) else BLUE for p in pct]
    ax.hlines(names, 60, pct, color="#e5e7eb", lw=1.5)
    ax.scatter(pct, names, color=colors, s=70, zorder=3)
    ax.axvline(overall, color=INK, lw=1.2, ls="--")
    ax.text(overall + 0.3, -0.9, f"All engineers {overall}%", fontsize=10, color=INK)
    for i, (p, k) in enumerate(zip(pct, n)):
        ax.text(max(pct) + 2.5, i, f"{p}%  ({k} repairs)", va="center", fontsize=9.5, color="#374151")
    ax.set_ylim(-1.3, len(names) - 0.5)
    ax.set_xlim(60, 106)
    ax.set_xticks(range(60, 101, 10))
    ax.set_xlabel("Repairs fixed on the first visit (%)")
    style(ax, f"First-time fix runs from {min(pct)}% to {max(pct)}%. Is that a real gap?",
          "Q3. Each engineer's first visits for repairs. Around 100 each, so stage 4 tests if the gap is real")
    save(fig, "chart3_first_time_fix.png")


def main():
    con = run_queries.load()
    chart1_months(con)
    chart2_wait(con)
    chart3_fix_rate(con)
    print("3 charts written to", HERE)


if __name__ == "__main__":
    main()
