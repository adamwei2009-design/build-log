"""Checks for stage 3: the charts get made, and the numbers in their titles match the SQL."""
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE / "stage2-sql"))
sys.path.insert(0, str(HERE / "stage3-charts"))
import make_charts   # noqa: E402
import run_queries   # noqa: E402

CHARTS = ["chart1_busiest_months.png", "chart2_repair_wait.png", "chart3_first_time_fix.png"]


def test_three_charts_are_made():
    make_charts.main()
    for name in CHARTS:
        f = HERE / "stage3-charts" / name
        assert f.exists() and f.stat().st_size > 10_000


def test_title_claims_match_the_data():
    con = run_queries.load()
    q = run_queries.queries()
    months = run_queries.run(con, q["q1_busiest_months"][1])[1]
    repairs = [m[1] for m in months]
    assert max(repairs) / min(repairs) > 3                    # "more than triple"
    services = [m[2] for m in months]
    assert months[services.index(max(services))][0] in ("09", "10", "11")   # "peak in the autumn"
    (w, _, w_avg, w_pct), (r, _, r_avg, r_pct) = [row[:1] + row[1:] for row in run_queries.run(con, q["q2_repair_wait"][1])[1]]
    assert round(w_avg - r_avg, 1) == 1.5                     # "1.5 days longer"
    assert round(w_pct / r_pct, 1) == 2.5                     # "2.5 times the share"
