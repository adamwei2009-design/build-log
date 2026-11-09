"""Stage 2: load the clean data into SQLite, run each question, write the answers."""
import csv
import re
import sqlite3
from pathlib import Path

HERE = Path(__file__).parent
CLEAN = HERE.parent / "data" / "jobs_clean.csv"
SQL = HERE / "queries.sql"
OUT = HERE / "answers.md"
NUMERIC = {"price_gbp": "REAL", "wait_days": "INTEGER"}


def load(path=CLEAN):
    con = sqlite3.connect(":memory:")
    with open(path, newline="") as f:
        rows = list(csv.DictReader(f))
    cols = list(rows[0])
    con.execute(f"CREATE TABLE jobs ({', '.join(f'{c} {NUMERIC.get(c, 'TEXT')}' for c in cols)})")
    for r in rows:
        if r["wait_days"] != "":
            r["wait_days"] = int(r["wait_days"])
        r["price_gbp"] = float(r["price_gbp"])
    con.executemany(f"INSERT INTO jobs VALUES ({', '.join('?' * len(cols))})",
                    [[r[c] for c in cols] for r in rows])
    n = con.execute("SELECT COUNT(*) FROM jobs").fetchone()[0]
    assert n == len(rows), "rows lost on load"
    return con


def queries(path=SQL):
    """Split the .sql file into {name: (comment, sql)}."""
    out = {}
    for block in re.split(r"^-- name: ", path.read_text(), flags=re.M)[1:]:
        name, body = block.split("\n", 1)
        notes = [l[3:] for l in body.splitlines() if l.startswith("-- ")]
        sql = "\n".join(l for l in body.splitlines() if not l.startswith("--")).strip()
        out[name.strip()] = (notes, sql)
    return out


def run(con, sql):
    cur = con.execute(sql)
    return [d[0] for d in cur.description], cur.fetchall()


def main():
    con = load()
    lines = ["# Stage 2 answers", "", "Made by `run_queries.py` from `queries.sql`. Every number below comes straight out of SQL.", ""]
    for name, (notes, sql) in queries().items():
        head, rows = run(con, sql)
        lines += [f"## {notes[0]}", ""] + [n for n in notes[1:]] + ["", "```sql", sql, "```", "",
                  "| " + " | ".join(head) + " |", "|" + "---|" * len(head)]
        lines += ["| " + " | ".join(str(v) for v in r) + " |" for r in rows]
        lines.append("")
    OUT.write_text("\n".join(lines))
    print(OUT.read_text())


if __name__ == "__main__":
    main()
