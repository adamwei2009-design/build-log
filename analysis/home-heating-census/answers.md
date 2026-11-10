# SQL answers

Made by `heating.py` from `queries.sql`. Do not edit by hand.

## q1_how_homes_are_heated

```sql
SELECT h.heating_type,
       SUM(h.households) AS households,
       ROUND(100.0 * SUM(h.households) / (SELECT SUM(households) FROM area WHERE level = 'local_authority'), 1) AS pct
FROM heating h JOIN area a USING (area_code)
WHERE a.level = 'local_authority'
GROUP BY h.heating_type
ORDER BY households DESC;
```

| heating_type | households | pct |
|---|---|---|
| mains_gas_only | 18298730 | 73.8 |
| two_or_more_no_renewable | 2113324 | 8.5 |
| electric_only | 2113123 | 8.5 |
| oil_only | 865944 | 3.5 |
| no_central_heating | 367119 | 1.5 |
| tank_or_bottled_gas_only | 260108 | 1.0 |
| other_only | 225399 | 0.9 |
| district_or_communal_only | 220893 | 0.9 |
| two_or_more_with_renewable | 134659 | 0.5 |
| renewable_only | 98729 | 0.4 |
| solid_fuel_only | 49469 | 0.2 |
| wood_only | 35720 | 0.1 |

## q2_mains_gas_by_region

```sql
SELECT a.area_name AS region,
       a.households,
       ROUND(100.0 * h.households / a.households, 1) AS mains_gas_only_pct
FROM area a JOIN heating h USING (area_code)
WHERE a.level = 'region' AND h.heating_type = 'mains_gas_only'
ORDER BY mains_gas_only_pct DESC;
```

| region | households | mains_gas_only_pct |
|---|---|---|
| North East | 1175677 | 79.2 |
| North West | 3153401 | 78.7 |
| Yorkshire and The Humber | 2330658 | 77.5 |
| East Midlands | 2037333 | 76.3 |
| West Midlands | 2429490 | 75.2 |
| South East | 3807965 | 74.6 |
| Wales | 1347114 | 71.6 |
| London | 3423890 | 70.5 |
| East | 2628782 | 70.1 |
| South West | 2448877 | 66.9 |

## q3_most_oil_heated_areas

```sql
SELECT a.area_name, a.country, a.households,
       ROUND(100.0 * h.households / a.households, 1) AS oil_only_pct
FROM area a JOIN heating h USING (area_code)
WHERE a.level = 'local_authority' AND h.heating_type = 'oil_only'
ORDER BY oil_only_pct DESC
LIMIT 10;
```

| area_name | country | households | oil_only_pct |
|---|---|---|---|
| Ceredigion | Wales | 30894 | 35.3 |
| Mid Suffolk | England | 44339 | 30.3 |
| Powys | Wales | 60180 | 27.7 |
| King's Lynn and West Norfolk | England | 67467 | 25.1 |
| Eden | England | 24613 | 24.7 |
| North Norfolk | England | 48378 | 24.6 |
| South Norfolk | England | 61381 | 24.2 |
| Breckland | England | 60359 | 23.7 |
| Carmarthenshire | Wales | 81761 | 23.7 |
| Pembrokeshire | Wales | 55489 | 22.7 |

## q4_most_homes_without_central_heating

```sql
SELECT a.area_name, a.households,
       h.households AS no_central_heating,
       ROUND(100.0 * h.households / a.households, 1) AS pct
FROM area a JOIN heating h USING (area_code)
WHERE a.level = 'local_authority' AND h.heating_type = 'no_central_heating'
ORDER BY pct DESC
LIMIT 10;
```

| area_name | households | no_central_heating | pct |
|---|---|---|---|
| Isles of Scilly | 942 | 165 | 17.5 |
| Westminster | 94815 | 3680 | 3.9 |
| City of London | 4915 | 184 | 3.7 |
| Cornwall | 250535 | 8776 | 3.5 |
| Kensington and Chelsea | 66884 | 2300 | 3.4 |
| Gwynedd | 51105 | 1648 | 3.2 |
| Southwark | 130818 | 4021 | 3.1 |
| Tower Hamlets | 120539 | 3690 | 3.1 |
| Torridge | 30457 | 925 | 3.0 |
| Barrow-in-Furness | 31260 | 892 | 2.9 |

## q5_england_vs_wales

```sql
SELECT a.country,
       SUM(a.households) AS households,
       ROUND(100.0 * SUM(h.households) / SUM(a.households), 1) AS mains_gas_only_pct
FROM area a JOIN heating h USING (area_code)
WHERE a.level = 'local_authority' AND h.heating_type = 'mains_gas_only'
GROUP BY a.country;
```

| country | households | mains_gas_only_pct |
|---|---|---|
| England | 23436104 | 74.0 |
| Wales | 1347113 | 71.6 |

## q6_spread_across_local_authorities

```sql
SELECT COUNT(*) AS local_authorities,
       MIN(pct) AS lowest_mains_gas_pct,
       MAX(pct) AS highest_mains_gas_pct,
       SUM(CASE WHEN pct < 50 THEN 1 ELSE 0 END) AS areas_under_half
FROM (
  SELECT ROUND(100.0 * h.households / a.households, 1) AS pct
  FROM area a JOIN heating h USING (area_code)
  WHERE a.level = 'local_authority' AND h.heating_type = 'mains_gas_only'
);
```

| local_authorities | lowest_mains_gas_pct | highest_mains_gas_pct | areas_under_half |
|---|---|---|---|
| 331 | 6.4 | 85.8 | 17 |
