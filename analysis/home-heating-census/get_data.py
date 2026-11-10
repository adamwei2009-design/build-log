"""Download table TS046 (central heating) from Nomis and save it one row per area.

Nomis is the Office for National Statistics' official service for census data.
The download has one row per area per heating type (331 areas x 13 values).
This script reshapes that into one row per area, which is what data/ holds.

Run:  python get_data.py
Needs internet access. The files in data/ come from this same download address
and the same reshaping, done on 10 November 2026.
"""
import csv
import io
import urllib.request
from pathlib import Path

from heating import TYPES

API = ("https://www.nomisweb.co.uk/api/v01/dataset/NM_2064_1.data.csv"
       "?date=latest&geography={geo}&measures=20100"
       "&select=geography_code,geography_name,c2021_heating_13,obs_value")
# Nomis geography types: 2022 local authority districts, and regions (plus Wales).
GEOGRAPHIES = {"TYPE154": "ts046_local_authorities_raw.csv", "TYPE480": "ts046_regions_raw.csv"}
COLUMNS = ["total_households"] + TYPES  # census codes 0 to 12, in order


def reshape(csv_text):
    """Turn the long download into one row per area. Returns a list of lists."""
    areas = {}
    for r in csv.DictReader(io.StringIO(csv_text)):
        code = r["GEOGRAPHY_CODE"]
        area = areas.setdefault(code, {"name": r["GEOGRAPHY_NAME"], "values": {}})
        area["values"][int(r["C2021_HEATING_13"])] = int(r["OBS_VALUE"])
    rows = []
    for code, area in areas.items():
        if sorted(area["values"]) != list(range(13)):
            raise ValueError(f"{code} does not have all 13 values")
        rows.append([code, area["name"]] + [area["values"][i] for i in range(13)])
    return rows


def save(rows, path):
    with open(path, "w", newline="", encoding="utf-8") as f:
        f.write("area_code,area_name," + ",".join(COLUMNS) + "\n")
        for r in rows:
            f.write(f'{r[0]},"{r[1]}",' + ",".join(str(v) for v in r[2:]) + "\n")


if __name__ == "__main__":
    out = Path(__file__).parent / "data"
    for geo, name in GEOGRAPHIES.items():
        with urllib.request.urlopen(API.format(geo=geo), timeout=60) as resp:
            text = resp.read().decode("utf-8")
        rows = reshape(text)
        save(rows, out / name)
        print(f"{name}: {len(rows)} areas")
