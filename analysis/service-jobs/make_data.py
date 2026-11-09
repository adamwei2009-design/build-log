"""Make a realistic but completely made-up export of home service jobs.

Nothing here is real. Names are ids, areas are compass points, and the
numbers come from a seeded random generator, so the file is the same every
time you run it.

On purpose, the export has the kind of mess a real one has:
duplicate rows, blank areas, mixed date formats, prices typed with a pound
sign, a test job, and a few visits dated before the customer asked.
Stage 1 finds and fixes those.
"""
import csv
import random
from datetime import date, timedelta
from pathlib import Path

SEED = 42
YEAR = 2025
AREAS = ["North", "South", "East", "West", "Central"]
ENGINEERS = [f"ENG-{n:02d}" for n in range(1, 13)]
# How busy each month is for each job type (made-up seasonality)
MONTH_WEIGHT = {
    "repair":  [1.6, 1.4, 1.1, 0.8, 0.6, 0.5, 0.5, 0.5, 0.7, 1.0, 1.4, 1.8],
    "service": [0.7, 0.7, 0.8, 0.9, 1.0, 1.0, 1.0, 1.1, 1.3, 1.4, 1.2, 0.8],
    "install": [1.2, 1.0, 1.0, 0.9, 0.8, 0.8, 0.8, 0.8, 0.9, 1.1, 1.2, 1.1],
}
BASE_JOBS = {"repair": 95, "service": 80, "install": 22}   # per month, before weights
PRICE = {"repair": (90, 320), "service": (75, 110), "install": (1800, 3600)}
WAIT_DAYS = {"repair": (0, 6), "service": (3, 21), "install": (7, 35)}
FIX_RATE = {e: 0.86 for e in ENGINEERS} | {"ENG-04": 0.71, "ENG-09": 0.93}


def fmt_date(d, rng):
    # Most rows use ISO dates; some come out of the old system as dd/mm/yyyy
    return d.strftime("%d/%m/%Y") if rng.random() < 0.08 else d.isoformat()


def build(rng):
    rows, job_no = [], 1000
    customers = [f"C{n:05d}" for n in range(1, 1601)]
    for month in range(1, 13):
        for job_type, base in BASE_JOBS.items():
            for _ in range(round(base * MONTH_WEIGHT[job_type][month - 1])):
                job_no += 1
                day = rng.randint(1, 28)
                requested = date(YEAR, month, day)
                lo, hi = WAIT_DAYS[job_type]
                extra = 3 if (job_type == "repair" and month in (1, 2, 12)) else 0
                visit = requested + timedelta(days=rng.randint(lo, hi + extra))
                engineer = rng.choice(ENGINEERS)
                fixed = job_type != "repair" or rng.random() < FIX_RATE[engineer]
                lo_p, hi_p = PRICE[job_type]
                rows.append({
                    "job_id": f"J{job_no}",
                    "customer_id": rng.choice(customers),
                    "area": rng.choice(AREAS),
                    "job_type": job_type,
                    "requested_date": requested,
                    "visit_date": visit,
                    "engineer_id": engineer,
                    "fixed_first_time": "yes" if fixed else "no",
                    "price_gbp": round(rng.uniform(lo_p, hi_p), 2),
                })
    # Repairs not fixed first time get a follow-up visit within 3 to 14 days
    for r in [r for r in rows if r["fixed_first_time"] == "no"]:
        job_no += 1
        follow = r["visit_date"] + timedelta(days=rng.randint(3, 14))
        rows.append(r | {"job_id": f"J{job_no}", "requested_date": r["visit_date"],
                         "visit_date": follow, "fixed_first_time": "yes",
                         "price_gbp": 0.0})
    return rows


def add_mess(rows, rng):
    messy = [dict(r) for r in rows]
    for r in rng.sample(messy, 25):          # duplicate rows from a double export
        messy.append(dict(r))
    for r in rng.sample(messy, 18):          # blank area
        r["area"] = ""
    for r in rng.sample(messy, 12):          # visit typed before the request
        r["visit_date"] = r["requested_date"] - timedelta(days=rng.randint(1, 5))
    for r in rng.sample(messy, 30):          # price typed as text
        r["price_gbp"] = f"£{r['price_gbp']}"
    messy.append(dict(messy[0]) | {"job_id": "TEST-1", "customer_id": "TEST"})
    for r in messy:
        r["requested_date"] = fmt_date(r["requested_date"], rng)
        r["visit_date"] = fmt_date(r["visit_date"], rng)
    rng.shuffle(messy)
    return messy


def main(out=Path(__file__).parent / "data" / "jobs_raw.csv"):
    rng = random.Random(SEED)
    rows = add_mess(build(rng), rng)
    out.parent.mkdir(exist_ok=True)
    with open(out, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {len(rows)} rows to {out}")


if __name__ == "__main__":
    main()
