"""Checks for stage 2: every SQL answer is re-counted in plain Python and must match."""
import csv
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE / "stage1-clean"))
sys.path.insert(0, str(HERE / "stage2-sql"))
sys.path.insert(0, str(HERE))
import clean          # noqa: E402
import make_data      # noqa: E402
import run_queries    # noqa: E402

WINTER = {"12", "01", "02"}


def setup_data(tmp_path):
    raw = tmp_path / "raw.csv"
    make_data.main(raw)
    with open(raw, newline="") as f:
        rows, _ = clean.clean(list(csv.DictReader(f)))
    out = tmp_path / "clean.csv"
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        for r in rows:
            w.writerow({k: (v.isoformat() if hasattr(v, "isoformat") else v) for k, v in r.items()})
    with open(out, newline="") as f:
        py_rows = list(csv.DictReader(f))
    return run_queries.load(out), py_rows


def answer(con, name):
    return run_queries.run(con, run_queries.queries()[name][1])[1]


def test_all_five_questions_are_in_the_file():
    assert list(run_queries.queries()) == ["q1_busiest_months", "q2_repair_wait", "q3_first_time_fix",
                                           "q4_return_visits", "q5_value_by_area"]


def test_q1_month_counts(tmp_path):
    con, rows = setup_data(tmp_path)
    c = Counter((r["requested_date"][5:7], r["job_type"]) for r in rows if r["visit_type"] == "first")
    for month, rep, serv, inst, total in answer(con, "q1_busiest_months"):
        assert (rep, serv, inst) == (c[(month, "repair")], c[(month, "service")], c[(month, "install")])
        assert total == rep + serv + inst
    assert sum(r[4] for r in answer(con, "q1_busiest_months")) == sum(r["visit_type"] == "first" for r in rows)


def test_q2_waits_skip_impossible_dates(tmp_path):
    con, rows = setup_data(tmp_path)
    groups = defaultdict(list)
    for r in rows:
        if r["job_type"] == "repair" and r["visit_type"] == "first" and r["wait_days"] != "":
            groups["Winter (Dec to Feb)" if r["requested_date"][5:7] in WINTER else "Rest of year"].append(int(r["wait_days"]))
    for season, n, avg, pct in answer(con, "q2_repair_wait"):
        w = groups[season]
        assert n == len(w)
        assert avg == round(sum(w) / len(w), 1)
        assert pct == round(100 * sum(x > 5 for x in w) / len(w), 1)


def test_q3_fix_rate_by_engineer(tmp_path):
    con, rows = setup_data(tmp_path)
    reps = [r for r in rows if r["job_type"] == "repair" and r["visit_type"] == "first"]
    got = answer(con, "q3_first_time_fix")
    assert sum(g[1] for g in got) == len(reps)
    for eng, n, fixed, pct in got:
        mine = [r for r in reps if r["engineer_id"] == eng]
        assert n == len(mine) and fixed == sum(r["fixed_first_time"] == "yes" for r in mine)
    assert [g[3] for g in got] == sorted(g[3] for g in got)   # worst first


def test_q4_return_visits_match_unfixed_repairs(tmp_path):
    con, rows = setup_data(tmp_path)
    whole = [r for r in answer(con, "q4_return_visits") if r[0] == "Whole year"][0]
    first = [r for r in rows if r["job_type"] == "repair" and r["visit_type"] == "first"]
    # every repair not fixed first time should have exactly one return visit
    assert whole[1] == len(first)
    assert whole[2] == sum(r["fixed_first_time"] == "no" for r in first)
    parts = [r for r in answer(con, "q4_return_visits") if r[0] != "Whole year"]
    assert sum(p[1] for p in parts) == whole[1] and sum(p[2] for p in parts) == whole[2]


def test_q5_revenue_adds_up(tmp_path):
    con, rows = setup_data(tmp_path)
    first = [r for r in rows if r["visit_type"] == "first"]
    got = answer(con, "q5_value_by_area")
    assert sum(g[1] for g in got) == len(first)
    assert abs(sum(g[2] for g in got) - sum(float(r["price_gbp"]) for r in first)) <= len(got)  # rounding only
    assert [g[2] for g in got] == sorted((g[2] for g in got), reverse=True)


def test_no_rows_lost_loading_into_sqlite(tmp_path):
    con, rows = setup_data(tmp_path)
    assert con.execute("SELECT COUNT(*) FROM jobs").fetchone()[0] == len(rows)
