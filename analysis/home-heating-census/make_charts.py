"""Turn the SQL answers into three charts.

Rules: the title says the answer, the numbers in the title come from the data
(and are tested), and bars start at zero.
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

import heating  # noqa: E402

HERE = Path(__file__).parent
BLUE, ORANGE, GREY, INK = "#2563eb", "#f59e0b", "#9ca3af", "#111827"
SOURCE = "Source: ONS, Census 2021, table TS046 (Nomis). Open Government Licence v3.0."


def style(ax, title, sub):
    ax.set_title(title, loc="left", fontsize=14.5, fontweight="bold", color=INK, pad=28)
    ax.text(0, 1.02, sub, transform=ax.transAxes, fontsize=10.5, color="#4b5563")
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    ax.spines["left"].set_color("#d1d5db")
    ax.spines["bottom"].set_color("#d1d5db")
    ax.tick_params(colors="#374151")


def save(fig, name):
    fig.text(0.01, 0.01, SOURCE, fontsize=8, color="#6b7280")
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    fig.savefig(HERE / name, dpi=150)
    plt.close(fig)


def heating_mix(con):
    """National shares, grouped into six plain-English bars. Returns [(label, pct)]."""
    rows = dict((r[0], r[1]) for r in heating.run(con, heating.queries()["q1_how_homes_are_heated"])[1])
    total = sum(rows.values())
    groups = [
        ("Mains gas only", ["mains_gas_only"]),
        ("Two or more types", ["two_or_more_no_renewable", "two_or_more_with_renewable"]),
        ("Electric only", ["electric_only"]),
        ("Oil only", ["oil_only"]),
        ("No central heating", ["no_central_heating"]),
        ("Everything else", ["tank_or_bottled_gas_only", "other_only", "district_or_communal_only",
                             "renewable_only", "solid_fuel_only", "wood_only"]),
    ]
    return [(label, round(100 * sum(rows[t] for t in types) / total, 1)) for label, types in groups]


def title1(con):
    pct = dict(heating_mix(con))["Mains gas only"]
    return f"Mains gas alone heats {pct}% of homes in England and Wales"


def region_gas(con):
    return [(r[0], r[2]) for r in heating.run(con, heating.queries()["q2_mains_gas_by_region"])[1]]


def title2(con):
    rows = region_gas(con)
    return f"{rows[0][0]} relies most on mains gas ({rows[0][1]}%), {rows[-1][0]} least ({rows[-1][1]}%)"


def oil_top(con):
    return [(r[0], r[3]) for r in heating.run(con, heating.queries()["q3_most_oil_heated_areas"])[1]]


def title3(con):
    name, pct = oil_top(con)[0]
    return f"In {name}, {pct}% of homes are heated by oil alone"


def barh(ax, rows, highlight):
    labels = [r[0] for r in rows][::-1]
    values = [r[1] for r in rows][::-1]
    colours = [ORANGE if l in highlight else BLUE for l in labels]
    ax.barh(labels, values, color=colours)
    for i, v in enumerate(values):
        ax.text(v + max(values) * 0.01, i, f"{v}%", va="center", fontsize=10, color=INK)
    ax.set_xlim(0, max(values) * 1.12)
    ax.set_xlabel("% of households")


def main():
    con = heating.build_db()
    fig, ax = plt.subplots(figsize=(9, 4.6))
    rows = heating_mix(con)
    barh(ax, rows, {"Mains gas only"})
    millions = round(con.execute("SELECT SUM(households) FROM area WHERE level = 'local_authority'").fetchone()[0] / 1e6, 1)
    style(ax, title1(con), f"Type of central heating, all {millions} million households, Census 2021")
    save(fig, "chart1_heating_mix.png")

    fig, ax = plt.subplots(figsize=(9, 5))
    rows = region_gas(con)
    barh(ax, rows, {rows[0][0], rows[-1][0]})
    style(ax, title2(con), "Homes heated by mains gas only, by region. Bars start at zero.")
    save(fig, "chart2_gas_by_region.png")

    fig, ax = plt.subplots(figsize=(9, 5))
    rows = oil_top(con)
    barh(ax, rows, {rows[0][0]})
    national = dict(heating_mix(con))["Oil only"]
    style(ax, title3(con), f"The 10 council areas with the highest share of oil-only heating (all areas together: {national}%)")
    save(fig, "chart3_oil_top10.png")


if __name__ == "__main__":
    main()
