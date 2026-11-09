"""Stage 1: clean the raw export and log every change.

Rule I follow: count the rows before and after every step, and write down
why each row changed. If the numbers don't add up, the clean is wrong.
"""
import csv
from collections import OrderedDict
from datetime import date, datetime
from pathlib import Path

HERE = Path(__file__).parent
RAW = HERE.parent / "data" / "jobs_raw.csv"
CLEAN = HERE.parent / "data" / "jobs_clean.csv"
LOG = HERE / "cleaning_log.md"


def parse_date(text):
    """Accept 2025-01-31 or 31/01/2025. Anything else is an error, not a guess."""
    text = text.strip()
    for fmt in ("%Y-%m-%d", "%d/%m/%Y"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            pass
    raise ValueError(f"unknown date format: {text!r}")


def parse_price(text):
    return float(str(text).replace("£", "").replace(",", "").strip())


def completeness(row):
    return sum(1 for v in row.values() if str(v).strip())


def clean(rows):
    """Return (clean_rows, steps). steps = list of (step, rows_before, rows_after, note)."""
    steps = []
    n = len(rows)

    # 1. Remove test jobs
    kept = [r for r in rows if not r["job_id"].startswith("TEST") and r["customer_id"] != "TEST"]
    steps.append(("Remove test jobs", n, len(kept), "job or customer id marked TEST"))

    # 2. Remove duplicates: same job_id twice. Keep the most complete copy.
    best = OrderedDict()
    for r in kept:
        j = r["job_id"]
        if j not in best or completeness(r) > completeness(best[j]):
            best[j] = r
    deduped = list(best.values())
    steps.append(("Remove duplicate jobs", len(kept), len(deduped), "same job_id exported twice"))

    # 3. Fix formats (no rows removed): dates, prices, blank areas
    out, mixed_dates, text_prices, blank_area, bad_order = [], 0, 0, 0, 0
    for r in deduped:
        c = dict(r)
        for col in ("requested_date", "visit_date"):
            if "/" in c[col]:
                mixed_dates += 1
            c[col] = parse_date(c[col])
        if "£" in str(c["price_gbp"]):
            text_prices += 1
        c["price_gbp"] = parse_price(c["price_gbp"])
        if not c["area"].strip():
            blank_area += 1
            c["area"] = "Unknown"
        # 4. A visit before the request is impossible. Keep the job, but don't
        #    trust its dates for waiting-time questions.
        c["date_issue"] = "yes" if c["visit_date"] < c["requested_date"] else "no"
        bad_order += c["date_issue"] == "yes"
        c["wait_days"] = "" if c["date_issue"] == "yes" else (c["visit_date"] - c["requested_date"]).days
        out.append(c)
    steps.append(("Fix formats", len(deduped), len(out),
                  f"{mixed_dates} dd/mm/yyyy dates, {text_prices} prices with £, "
                  f"{blank_area} blank areas set to Unknown, "
                  f"{bad_order} visits dated before the request flagged (kept, wait left blank)"))
    return out, steps


def main():
    with open(RAW, newline="") as f:
        raw = list(csv.DictReader(f))
    rows, steps = clean(raw)
    with open(CLEAN, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        for r in rows:
            w.writerow({k: (v.isoformat() if isinstance(v, date) else v) for k, v in r.items()})

    lines = ["# Stage 1 cleaning log", "",
             "Made by `clean.py`. Every step counts rows before and after.", "",
             "| Step | Rows before | Rows after | Removed | What changed |",
             "|---|---|---|---|---|"]
    for name, before, after, note in steps:
        lines.append(f"| {name} | {before} | {after} | {before - after} | {note} |")
    lines += ["", f"Check: {len(raw)} raw rows - "
              f"{sum(b - a for _, b, a, _ in steps)} removed = {len(rows)} clean rows."]
    LOG.write_text("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
