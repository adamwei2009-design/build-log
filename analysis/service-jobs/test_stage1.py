"""Checks for stage 1. Each test re-counts something a different way from clean.py."""
import csv
import sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE / "stage1-clean"))
sys.path.insert(0, str(HERE))
import clean          # noqa: E402
import make_data      # noqa: E402


def load_raw(tmp_path):
    out = tmp_path / "raw.csv"
    make_data.main(out)
    with open(out, newline="") as f:
        return list(csv.DictReader(f))


def test_data_is_the_same_every_run(tmp_path):
    a = load_raw(tmp_path)
    b = load_raw(tmp_path)
    assert a == b


def test_row_count_matches_unique_real_jobs(tmp_path):
    raw = load_raw(tmp_path)
    expected = len({r["job_id"] for r in raw if not r["job_id"].startswith("TEST")})
    rows, steps = clean.clean(raw)
    assert len(rows) == expected
    # the log must add up: raw minus everything removed equals what is left
    assert len(raw) - sum(b - a for _, b, a, _ in steps) == len(rows)


def test_no_duplicates_or_test_jobs_left(tmp_path):
    rows, _ = clean.clean(load_raw(tmp_path))
    ids = [r["job_id"] for r in rows]
    assert len(ids) == len(set(ids))
    assert not any(i.startswith("TEST") for i in ids)


def test_formats_are_fixed(tmp_path):
    rows, _ = clean.clean(load_raw(tmp_path))
    for r in rows:
        assert isinstance(r["requested_date"], date) and isinstance(r["visit_date"], date)
        assert isinstance(r["price_gbp"], float) and r["price_gbp"] >= 0
        assert r["area"] in {"North", "South", "East", "West", "Central", "Unknown"}


def test_wait_is_blank_only_when_dates_are_impossible(tmp_path):
    rows, _ = clean.clean(load_raw(tmp_path))
    for r in rows:
        if r["date_issue"] == "yes":
            assert r["wait_days"] == "" and r["visit_date"] < r["requested_date"]
        else:
            assert r["wait_days"] >= 0


def test_both_date_formats_parse_to_the_same_day():
    assert clean.parse_date("31/01/2025") == clean.parse_date("2025-01-31") == date(2025, 1, 31)


def test_unknown_date_format_is_an_error_not_a_guess():
    import pytest
    with pytest.raises(ValueError):
        clean.parse_date("Jan 31 2025")


def test_price_with_pound_sign():
    assert clean.parse_price("£1,234.50") == 1234.5
