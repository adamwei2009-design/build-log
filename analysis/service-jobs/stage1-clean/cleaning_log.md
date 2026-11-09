# Stage 1 cleaning log

Made by `clean.py`. Every step counts rows before and after.

| Step | Rows before | Rows after | Removed | What changed |
|---|---|---|---|---|
| Remove test jobs | 2533 | 2532 | 1 | job or customer id marked TEST |
| Remove duplicate jobs | 2532 | 2507 | 25 | same job_id exported twice |
| Fix formats | 2507 | 2507 | 0 | 395 dd/mm/yyyy dates, 30 prices with £, 18 blank areas set to Unknown, 12 visits dated before the request flagged (kept, wait left blank) |

Check: 2533 raw rows - 26 removed = 2507 clean rows.
