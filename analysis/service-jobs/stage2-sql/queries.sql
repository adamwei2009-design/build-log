-- Stage 2: five business questions, answered in SQL (SQLite).
-- Table: jobs (one row per visit, made by stage 1). Each query starts with "-- name:".

-- name: q1_busiest_months
-- Q1. Which months are busiest, and for which kind of job?
-- Counts first visits only, so a return visit for the same fault isn't counted twice.
SELECT strftime('%m', requested_date)                      AS month,
       SUM(job_type = 'repair')                            AS repairs,
       SUM(job_type = 'service')                           AS services,
       SUM(job_type = 'install')                           AS installs,
       COUNT(*)                                            AS total
FROM jobs
WHERE visit_type = 'first'
GROUP BY month
ORDER BY month;

-- name: q2_repair_wait
-- Q2. How long do customers wait for a repair, and does winter change that?
-- Leaves out the 12 jobs whose dates are impossible (wait_days is blank for them).
SELECT CASE WHEN strftime('%m', requested_date) IN ('12','01','02')
            THEN 'Winter (Dec to Feb)' ELSE 'Rest of year' END AS season,
       COUNT(*)                                            AS repairs,
       ROUND(AVG(wait_days), 1)                            AS avg_wait_days,
       ROUND(100.0 * SUM(wait_days > 5) / COUNT(*), 1)     AS pct_waiting_over_5_days
FROM jobs
WHERE job_type = 'repair' AND visit_type = 'first' AND wait_days <> ''
GROUP BY season
ORDER BY season DESC;

-- name: q3_first_time_fix
-- Q3. What share of repairs are fixed on the first visit, by engineer?
SELECT engineer_id,
       COUNT(*)                                                        AS repairs,
       SUM(fixed_first_time = 'yes')                                   AS fixed_first_time,
       ROUND(100.0 * SUM(fixed_first_time = 'yes') / COUNT(*), 1)      AS fix_rate_pct
FROM jobs
WHERE job_type = 'repair' AND visit_type = 'first'
GROUP BY engineer_id
ORDER BY fix_rate_pct ASC;

-- name: q4_return_visits
-- Q4. How often does a repair need a second visit?
-- A return visit is a second trip for the same fault. First visits are grouped by when the customer asked;
-- return visits by the date of the first visit, which is close enough for a season split.
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

-- name: q5_value_by_area
-- Q5. Which areas bring in the most, and is it just because they have more jobs?
-- Paid first visits only. Installs are shown on their own because one install
-- is worth about 20 repairs and would hide everything else.
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
