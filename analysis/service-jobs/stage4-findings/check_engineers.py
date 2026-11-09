"""Stage 4: is the gap between engineers real, or luck?

Two checks:
1. A two-proportion z-test for each engineer against everyone else, with a
   Bonferroni correction because 12 tests at once will find "something" by chance.
2. Because I made the data, I know the truth: ENG-04 was set to fix 71% first
   time, ENG-09 93%, everyone else 86%. So I can re-make the year 500 times with
   different random seeds and see how often the test gets it right.
"""
import csv
import math
import random
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE.parent))
import make_data  # noqa: E402

ALPHA = 0.05
TRULY_WORSE = "ENG-04"   # set in make_data.FIX_RATE


def z_test(fixed, n, other_fixed, other_n):
    """Two-proportion z-test. Returns (z, two-sided p-value)."""
    pooled = (fixed + other_fixed) / (n + other_n)
    se = math.sqrt(pooled * (1 - pooled) * (1 / n + 1 / other_n))
    z = (fixed / n - other_fixed / other_n) / se
    return z, math.erfc(abs(z) / math.sqrt(2))


def counts(rows):
    n, f = Counter(), Counter()
    for r in rows:
        if r["job_type"] == "repair" and r["visit_type"] == "first":
            n[r["engineer_id"]] += 1
            f[r["engineer_id"]] += r["fixed_first_time"] == "yes"
    return n, f


def test_engineers(rows):
    """One row per engineer: (engineer, repairs, fixed, rate %, z, p, p after Bonferroni, flagged)."""
    n, f = counts(rows)
    total_n, total_f = sum(n.values()), sum(f.values())
    out = []
    for e in sorted(n):
        z, p = z_test(f[e], n[e], total_f - f[e], total_n - n[e])
        p_adj = min(1.0, p * len(n))
        # rate: + 1e-9 rounds halves up, the same way SQLite does in stage 2
        out.append((e, n[e], f[e], round(100 * f[e] / n[e] + 1e-9, 1), round(z, 2), p, p_adj,
                    z < 0 and p_adj < ALPHA))
    return out


def simulate(years=500):
    """Re-make the year with different seeds. How often is the right engineer flagged?"""
    right = wrong = 0
    for seed in range(years):
        flagged = {r[0] for r in test_engineers(make_data.build(random.Random(seed))) if r[7]}
        right += TRULY_WORSE in flagged
        wrong += bool(flagged - {TRULY_WORSE})
    return years, right, wrong


def main():
    with open(HERE.parent / "data" / "jobs_clean.csv", newline="") as fh:
        rows = list(csv.DictReader(fh))
    print("This year's clean data (from stage 1):")
    for e, n, f, rate, z, p, p_adj, flag in test_engineers(rows):
        print(f"  {e}  {f}/{n} = {rate}%  z={z:+.2f}  p={p:.4f}  adjusted p={p_adj:.3f}  {'FLAGGED' if flag else ''}")
    years, right, wrong = simulate()
    print(f"\nOver {years} made-up years: right engineer flagged in {right} ({100*right/years:.0f}%), "
          f"a wrong engineer flagged in {wrong} ({100*wrong/years:.0f}%).")


if __name__ == "__main__":
    main()
