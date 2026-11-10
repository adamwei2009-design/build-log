"""Load the Census 2021 central heating table (TS046) and answer questions in SQL.

Source: Office for National Statistics, Census 2021, table TS046, via Nomis.
Licence: Open Government Licence v3.0. See README.md.

Only the Python standard library is used, so anyone can run it.
"""
import csv
import sqlite3
from pathlib import Path

HERE = Path(__file__).parent
DATA = HERE / "data"
LA_FILE = DATA / "ts046_local_authorities_raw.csv"
REGION_FILE = DATA / "ts046_regions_raw.csv"

# The 12 heating categories, in the order the census publishes them.
TYPES = [
    "no_central_heating",
    "mains_gas_only",
    "tank_or_bottled_gas_only",
    "electric_only",
    "oil_only",
    "wood_only",
    "solid_fuel_only",
    "renewable_only",
    "district_or_communal_only",
    "other_only",
    "two_or_more_no_renewable",
    "two_or_more_with_renewable",
]


def read_wide(path):
    """Read one raw file. Returns a list of dicts with whole numbers."""
    rows = []
    with open(path, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            row = {"area_code": r["area_code"], "area_name": r["area_name"]}
            for col in ["total_households"] + TYPES:
                row[col] = int(r[col])
            rows.append(row)
    return rows


def check_rows(rows):
    """Return a list of problems. An empty list means the file is sound."""
    problems = []
    seen = set()
    for r in rows:
        if r["area_code"] in seen:
            problems.append(f"duplicate area {r['area_code']}")
        seen.add(r["area_code"])
        parts = sum(r[t] for t in TYPES)
        if parts != r["total_households"]:
            problems.append(f"{r['area_name']}: parts {parts} != total {r['total_households']}")
        if any(r[t] < 0 for t in TYPES):
            problems.append(f"{r['area_name']}: negative count")
    return problems


def country(area_code):
    return "Wales" if area_code.startswith("W") else "England"


def build_db(la_rows=None, region_rows=None):
    """Put the data into an in-memory SQLite database in long format."""
    la_rows = la_rows if la_rows is not None else read_wide(LA_FILE)
    region_rows = region_rows if region_rows is not None else read_wide(REGION_FILE)
    con = sqlite3.connect(":memory:")
    con.execute("CREATE TABLE area (area_code TEXT PRIMARY KEY, area_name TEXT, level TEXT, country TEXT, households INTEGER)")
    con.execute("CREATE TABLE heating (area_code TEXT, heating_type TEXT, households INTEGER)")
    for level, rows in (("local_authority", la_rows), ("region", region_rows)):
        for r in rows:
            con.execute("INSERT INTO area VALUES (?,?,?,?,?)",
                        (r["area_code"], r["area_name"], level, country(r["area_code"]), r["total_households"]))
            con.executemany("INSERT INTO heating VALUES (?,?,?)",
                            [(r["area_code"], t, r[t]) for t in TYPES])
    con.commit()
    return con


def queries():
    """Split queries.sql into {name: sql}. Each query starts with '-- name: x'."""
    out, name, buf = {}, None, []
    for line in (HERE / "queries.sql").read_text(encoding="utf-8").splitlines():
        if line.startswith("-- name:"):
            if name:
                out[name] = "\n".join(buf).strip()
            name, buf = line.split(":", 1)[1].strip(), []
        elif name is not None:
            buf.append(line)
    if name:
        out[name] = "\n".join(buf).strip()
    return out


def run(con, sql):
    cur = con.execute(sql)
    return [d[0] for d in cur.description], cur.fetchall()


def write_answers(con):
    lines = ["# SQL answers", "",
             "Made by `heating.py` from `queries.sql`. Do not edit by hand.", ""]
    for name, sql in queries().items():
        cols, rows = run(con, sql)
        lines += [f"## {name}", "", "```sql", sql, "```", "",
                  "| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
        lines += ["| " + " | ".join(str(v) for v in r) + " |" for r in rows]
        lines.append("")
    (HERE / "answers.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    la = read_wide(LA_FILE)
    reg = read_wide(REGION_FILE)
    problems = check_rows(la) + check_rows(reg)
    print(f"local authorities: {len(la)}, regions: {len(reg)}, problems: {len(problems)}")
    for p in problems:
        print("  ", p)
    print("households, local authorities:", sum(r["total_households"] for r in la))
    print("households, regions:          ", sum(r["total_households"] for r in reg))
    write_answers(build_db(la, reg))
    print("wrote answers.md")
