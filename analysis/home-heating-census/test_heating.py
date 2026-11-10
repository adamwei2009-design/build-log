"""Checks for the home heating analysis. Run:  pytest -q"""
import heating
import make_charts
from get_data import reshape

LA = heating.read_wide(heating.LA_FILE)
REG = heating.read_wide(heating.REGION_FILE)
CON = heating.build_db(LA, REG)
Q = heating.queries()


def pct(part, whole):
    return round(100 * part / whole, 1)


# ---- the data itself ----

def test_row_counts():
    assert len(LA) == 331   # local authority districts, England and Wales
    assert len(REG) == 10   # 9 English regions plus Wales


def test_no_problems_in_either_file():
    assert heating.check_rows(LA) == []
    assert heating.check_rows(REG) == []


def test_every_area_adds_up():
    for r in LA + REG:
        assert sum(r[t] for t in heating.TYPES) == r["total_households"], r["area_name"]


def test_two_levels_agree_closely():
    # The census changes small counts slightly to protect privacy, so the
    # 331 areas and the 10 regions do not sum to exactly the same number.
    la_total = sum(r["total_households"] for r in LA)
    reg_total = sum(r["total_households"] for r in REG)
    assert la_total == 24_783_217
    assert reg_total == 24_783_187
    assert abs(la_total - reg_total) / reg_total < 0.00001   # under 0.001%


def test_nothing_lost_loading_into_sqlite():
    n_areas = CON.execute("SELECT COUNT(*) FROM area").fetchone()[0]
    n_rows = CON.execute("SELECT COUNT(*) FROM heating").fetchone()[0]
    assert n_areas == 341
    assert n_rows == 341 * 12
    db_total = CON.execute("SELECT SUM(households) FROM heating").fetchone()[0]
    assert db_total == sum(r["total_households"] for r in LA + REG)


# ---- every SQL answer, worked out a second way in plain Python ----

def test_q1_matches_python():
    total = sum(r["total_households"] for r in LA)
    expected = {t: (sum(r[t] for r in LA), pct(sum(r[t] for r in LA), total)) for t in heating.TYPES}
    rows = heating.run(CON, Q["q1_how_homes_are_heated"])[1]
    assert {r[0]: (r[1], r[2]) for r in rows} == expected
    assert [r[1] for r in rows] == sorted((r[1] for r in rows), reverse=True)


def test_q2_matches_python():
    expected = sorted(((r["area_name"], pct(r["mains_gas_only"], r["total_households"])) for r in REG),
                      key=lambda x: -x[1])
    rows = heating.run(CON, Q["q2_mains_gas_by_region"])[1]
    assert [(r[0], r[2]) for r in rows] == expected


def test_q3_matches_python():
    expected = sorted(((pct(r["oil_only"], r["total_households"]), r["area_name"]) for r in LA), reverse=True)[:10]
    rows = heating.run(CON, Q["q3_most_oil_heated_areas"])[1]
    assert sorted(((r[3], r[0]) for r in rows), reverse=True) == expected


def test_q4_matches_python():
    expected = sorted(((pct(r["no_central_heating"], r["total_households"]), r["area_name"]) for r in LA), reverse=True)[:10]
    rows = heating.run(CON, Q["q4_most_homes_without_central_heating"])[1]
    assert sorted(((r[3], r[0]) for r in rows), reverse=True) == expected


def test_q5_matches_python():
    rows = dict((r[0], (r[1], r[2])) for r in heating.run(CON, Q["q5_england_vs_wales"])[1])
    for name, letter in (("England", "E"), ("Wales", "W")):
        mine = [r for r in LA if r["area_code"].startswith(letter)]
        total = sum(r["total_households"] for r in mine)
        assert rows[name] == (total, pct(sum(r["mains_gas_only"] for r in mine), total))


def test_q6_matches_python():
    pcts = [pct(r["mains_gas_only"], r["total_households"]) for r in LA]
    row = heating.run(CON, Q["q6_spread_across_local_authorities"])[1][0]
    assert row == (331, min(pcts), max(pcts), sum(1 for p in pcts if p < 50))


# ---- chart titles: if the data changed, these would fail ----

def test_chart_titles_are_true():
    assert make_charts.title1(CON) == "Mains gas alone heats 73.8% of homes in England and Wales"
    assert make_charts.title2(CON) == "North East relies most on mains gas (79.2%), South West least (66.9%)"
    assert make_charts.title3(CON) == "In Ceredigion, 35.3% of homes are heated by oil alone"


def test_chart1_groups_cover_every_home():
    assert abs(sum(p for _, p in make_charts.heating_mix(CON)) - 100) <= 0.3   # rounding only


# ---- the download reshaping ----

def test_reshape_long_to_wide():
    lines = ['"GEOGRAPHY_CODE","GEOGRAPHY_NAME","C2021_HEATING_13","OBS_VALUE"']
    lines += [f'"X1","Test, Area","{i}",{i * 10}' for i in range(13)]
    rows = reshape("\n".join(lines))
    assert rows == [["X1", "Test, Area"] + [i * 10 for i in range(13)]]
