"""Checks for stage 4: the statistics behave, and the headline claims stay true."""
import csv
import math
import sys
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE / "stage4-findings"))
sys.path.insert(0, str(HERE))
import check_engineers as ce  # noqa: E402


def clean_rows():
    with open(HERE / "data" / "jobs_clean.csv", newline="") as f:
        return list(csv.DictReader(f))


def test_z_test_is_zero_when_rates_match():
    z, p = ce.z_test(80, 100, 800, 1000)
    assert abs(z) < 1e-9 and abs(p - 1) < 1e-9


def test_z_test_known_value():
    # 70/100 against 850/1000: worked out by hand, z is about -4.0
    z, p = ce.z_test(70, 100, 850, 1000)
    assert -4.2 < z < -3.8 and p < 0.001


def test_bonferroni_never_goes_above_one():
    assert all(r[6] <= 1.0 for r in ce.test_engineers(clean_rows()))


def test_this_years_flag_is_eng08_not_eng04():
    flagged = [r[0] for r in ce.test_engineers(clean_rows()) if r[7]]
    assert flagged == ["ENG-08"]


def test_rates_match_the_sql_answers():
    sys.path.insert(0, str(HERE / "stage2-sql"))
    import run_queries
    con = run_queries.load()
    sql = {r[0]: r[3] for r in run_queries.run(con, run_queries.queries()["q3_first_time_fix"][1])[1]}
    assert {r[0]: r[3] for r in ce.test_engineers(clean_rows())} == sql


def test_simulation_headline():
    years, right, wrong = ce.simulate(500)
    assert (years, right, wrong) == (500, 411, 15)
