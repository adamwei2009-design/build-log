# Service jobs analysis: a data journey

A start-to-finish data analysis, done in stages and shared as I go.
The data is **completely made up** (see `make_data.py`). It copies the shape of a home service company's job export: repairs, services and installs over one year.

## The stages

| Stage | What I do | Status |
|---|---|---|
| 1 | [Get and clean the data](stage1-clean/) | Done |
| 2 | Ask the business questions in SQL | Next |
| 3 | Turn the answers into charts | Coming |
| 4 | Write up what I found | Coming |

## Stage 1: get and clean the data

A raw export is never ready to use. This one has the mess a real one has, put there on purpose:

- the same job exported twice
- a test job left in
- dates in two formats (`2025-01-31` and `31/01/2025`)
- prices typed as text with a £ sign
- blank areas
- visits dated *before* the customer asked for them

`clean.py` fixes these and counts the rows before and after every step. The [cleaning log](stage1-clean/cleaning_log.md) has the full numbers:

| Step | Rows before | Rows after | Removed |
|---|---|---|---|
| Remove test jobs | 2,533 | 2,532 | 1 |
| Remove duplicate jobs | 2,532 | 2,507 | 25 |
| Fix formats | 2,507 | 2,507 | 0 |

**2,533 raw rows, 26 removed, 2,507 clean rows.** The numbers add up, and a test checks they always do.

### Decisions I made, and why

- **Duplicates:** when a job appears twice, keep the most complete copy rather than the first one.
- **Blank areas:** set to `Unknown`, not deleted. The job still happened and still counts.
- **Visit before request:** these 12 jobs are kept, but their waiting time is left blank, so they can't drag the waiting-time answers in stage 2.
- **Unknown date formats:** stop with an error instead of guessing. A wrong date is worse than no date.

### The questions for stage 2

1. Which months are busiest, and for which kind of job?
2. How long do customers wait for a visit, and does winter change that?
3. What share of repairs are fixed on the first visit, and does it vary by engineer?
4. How often does a customer need a second visit for the same fault?
5. Which areas bring in the most per job?

## Run it

```
python3 make_data.py              # makes data/jobs_raw.csv
python3 stage1-clean/clean.py     # makes data/jobs_clean.csv and the log
pytest -q                         # 8 checks
```
