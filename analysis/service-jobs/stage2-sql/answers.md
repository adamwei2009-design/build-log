# Stage 2 answers

Made by `run_queries.py` from `queries.sql`. Every number below comes straight out of SQL.

## Q1. Which months are busiest, and for which kind of job?

Counts first visits only, so a return visit for the same fault isn't counted twice.

```sql
SELECT strftime('%m', requested_date)                      AS month,
       SUM(job_type = 'repair')                            AS repairs,
       SUM(job_type = 'service')                           AS services,
       SUM(job_type = 'install')                           AS installs,
       COUNT(*)                                            AS total
FROM jobs
WHERE visit_type = 'first'
GROUP BY month
ORDER BY month;
```

| month | repairs | services | installs | total |
|---|---|---|---|---|
| 01 | 152 | 56 | 26 | 234 |
| 02 | 133 | 56 | 22 | 211 |
| 03 | 105 | 64 | 22 | 191 |
| 04 | 76 | 72 | 20 | 168 |
| 05 | 57 | 80 | 18 | 155 |
| 06 | 48 | 80 | 18 | 146 |
| 07 | 48 | 80 | 18 | 146 |
| 08 | 48 | 88 | 18 | 154 |
| 09 | 66 | 104 | 20 | 190 |
| 10 | 95 | 112 | 24 | 231 |
| 11 | 133 | 96 | 26 | 255 |
| 12 | 171 | 64 | 24 | 259 |

## Q2. How long do customers wait for a repair, and does winter change that?

Leaves out the 12 jobs whose dates are impossible (wait_days is blank for them).

```sql
SELECT CASE WHEN strftime('%m', requested_date) IN ('12','01','02')
            THEN 'Winter (Dec to Feb)' ELSE 'Rest of year' END AS season,
       COUNT(*)                                            AS repairs,
       ROUND(AVG(wait_days), 1)                            AS avg_wait_days,
       ROUND(100.0 * SUM(wait_days > 5) / COUNT(*), 1)     AS pct_waiting_over_5_days
FROM jobs
WHERE job_type = 'repair' AND visit_type = 'first' AND wait_days <> ''
GROUP BY season
ORDER BY season DESC;
```

| season | repairs | avg_wait_days | pct_waiting_over_5_days |
|---|---|---|---|
| Winter (Dec to Feb) | 452 | 4.6 | 37.6 |
| Rest of year | 675 | 3.1 | 15.3 |

## Q3. What share of repairs are fixed on the first visit, by engineer?


```sql
SELECT engineer_id,
       COUNT(*)                                                        AS repairs,
       SUM(fixed_first_time = 'yes')                                   AS fixed_first_time,
       ROUND(100.0 * SUM(fixed_first_time = 'yes') / COUNT(*), 1)      AS fix_rate_pct
FROM jobs
WHERE job_type = 'repair' AND visit_type = 'first'
GROUP BY engineer_id
ORDER BY fix_rate_pct ASC;
```

| engineer_id | repairs | fixed_first_time | fix_rate_pct |
|---|---|---|---|
| ENG-08 | 111 | 82 | 73.9 |
| ENG-04 | 96 | 78 | 81.3 |
| ENG-02 | 101 | 83 | 82.2 |
| ENG-12 | 113 | 93 | 82.3 |
| ENG-03 | 99 | 83 | 83.8 |
| ENG-06 | 79 | 68 | 86.1 |
| ENG-07 | 85 | 74 | 87.1 |
| ENG-01 | 89 | 78 | 87.6 |
| ENG-11 | 79 | 71 | 89.9 |
| ENG-05 | 84 | 76 | 90.5 |
| ENG-09 | 97 | 88 | 90.7 |
| ENG-10 | 99 | 91 | 91.9 |

## Q4. How often does a repair need a second visit?

A return visit is a second trip for the same fault. First visits are grouped by when the customer asked;
return visits by the date of the first visit, which is close enough for a season split.

```sql
SELECT CASE WHEN strftime('%m', requested_date) IN ('12','01','02')
            THEN 'Winter (Dec to Feb)' ELSE 'Rest of year' END AS season,
       SUM(visit_type = 'first')                                       AS repairs,
       SUM(visit_type = 'return')                                      AS return_visits,
       ROUND(100.0 * SUM(visit_type = 'return') / SUM(visit_type = 'first'), 1) AS extra_visits_pct
FROM jobs
WHERE job_type = 'repair'
GROUP BY season
UNION ALL
SELECT 'Whole year', SUM(visit_type = 'first'), SUM(visit_type = 'return'),
       ROUND(100.0 * SUM(visit_type = 'return') / SUM(visit_type = 'first'), 1)
FROM jobs
WHERE job_type = 'repair';
```

| season | repairs | return_visits | extra_visits_pct |
|---|---|---|---|
| Rest of year | 676 | 105 | 15.5 |
| Winter (Dec to Feb) | 456 | 62 | 13.6 |
| Whole year | 1132 | 167 | 14.8 |

## Q5. Which areas bring in the most, and is it just because they have more jobs?

Paid first visits only. Installs are shown on their own because one install
is worth about 20 repairs and would hide everything else.

```sql
SELECT area,
       COUNT(*)                                                         AS jobs,
       CAST(ROUND(SUM(price_gbp)) AS INTEGER)                           AS revenue_gbp,
       CAST(ROUND(SUM(price_gbp) / COUNT(*)) AS INTEGER)                AS revenue_per_job_gbp,
       CAST(ROUND(AVG(CASE WHEN job_type <> 'install' THEN price_gbp END)) AS INTEGER) AS avg_repair_or_service_gbp,
       SUM(job_type = 'install')                                        AS installs
FROM jobs
WHERE visit_type = 'first'
GROUP BY area
ORDER BY revenue_gbp DESC;
```

| area | jobs | revenue_gbp | revenue_per_job_gbp | avg_repair_or_service_gbp | installs |
|---|---|---|---|---|---|
| West | 497 | 216747 | 436 | 156 | 55 |
| East | 489 | 201513 | 412 | 152 | 51 |
| Central | 462 | 200949 | 435 | 152 | 52 |
| North | 439 | 188042 | 428 | 153 | 50 |
| South | 437 | 177583 | 406 | 149 | 46 |
| Unknown | 16 | 7798 | 487 | 141 | 2 |
