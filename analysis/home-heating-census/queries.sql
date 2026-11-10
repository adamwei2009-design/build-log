-- Census 2021, table TS046 (central heating), England and Wales.
-- Each query answers one question. heating.py runs them and writes answers.md.

-- name: q1_how_homes_are_heated
SELECT h.heating_type,
       SUM(h.households) AS households,
       ROUND(100.0 * SUM(h.households) / (SELECT SUM(households) FROM area WHERE level = 'local_authority'), 1) AS pct
FROM heating h JOIN area a USING (area_code)
WHERE a.level = 'local_authority'
GROUP BY h.heating_type
ORDER BY households DESC;

-- name: q2_mains_gas_by_region
SELECT a.area_name AS region,
       a.households,
       ROUND(100.0 * h.households / a.households, 1) AS mains_gas_only_pct
FROM area a JOIN heating h USING (area_code)
WHERE a.level = 'region' AND h.heating_type = 'mains_gas_only'
ORDER BY mains_gas_only_pct DESC;

-- name: q3_most_oil_heated_areas
SELECT a.area_name, a.country, a.households,
       ROUND(100.0 * h.households / a.households, 1) AS oil_only_pct
FROM area a JOIN heating h USING (area_code)
WHERE a.level = 'local_authority' AND h.heating_type = 'oil_only'
ORDER BY oil_only_pct DESC
LIMIT 10;

-- name: q4_most_homes_without_central_heating
SELECT a.area_name, a.households,
       h.households AS no_central_heating,
       ROUND(100.0 * h.households / a.households, 1) AS pct
FROM area a JOIN heating h USING (area_code)
WHERE a.level = 'local_authority' AND h.heating_type = 'no_central_heating'
ORDER BY pct DESC
LIMIT 10;

-- name: q5_england_vs_wales
SELECT a.country,
       SUM(a.households) AS households,
       ROUND(100.0 * SUM(h.households) / SUM(a.households), 1) AS mains_gas_only_pct
FROM area a JOIN heating h USING (area_code)
WHERE a.level = 'local_authority' AND h.heating_type = 'mains_gas_only'
GROUP BY a.country;

-- name: q6_spread_across_local_authorities
SELECT COUNT(*) AS local_authorities,
       MIN(pct) AS lowest_mains_gas_pct,
       MAX(pct) AS highest_mains_gas_pct,
       SUM(CASE WHEN pct < 50 THEN 1 ELSE 0 END) AS areas_under_half
FROM (
  SELECT ROUND(100.0 * h.households / a.households, 1) AS pct
  FROM area a JOIN heating h USING (area_code)
  WHERE a.level = 'local_authority' AND h.heating_type = 'mains_gas_only'
);
