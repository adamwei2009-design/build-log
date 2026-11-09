from datetime import date, datetime, timedelta

from merge_repeats import Message, merge
from route_by_booking import route
from safe_delete_gate import check
from strip_png_metadata import PNG_SIGNATURE, make_chunk, strip

T = datetime(2026, 1, 5, 9, 0)


def test_repeats_within_window_become_one_alert():
    msgs = [Message("customer-a", T + timedelta(minutes=m), "noise") for m in (0, 5, 20)]
    alerts, events = merge(msgs)
    assert len(alerts) == 1 and len(alerts[0].messages) == 3
    assert events == [("NEW", "customer-a")]


def test_window_is_measured_from_last_message():
    msgs = [Message("customer-a", T + timedelta(minutes=m), "noise") for m in (0, 25, 50)]
    alerts, _ = merge(msgs)
    assert len(alerts) == 1


def test_gap_over_window_starts_new_alert():
    msgs = [Message("customer-a", T, "hi"), Message("customer-a", T + timedelta(minutes=31), "hi")]
    alerts, _ = merge(msgs)
    assert len(alerts) == 2


def test_new_urgent_words_raise_update_once():
    msgs = [
        Message("customer-a", T, "noise"),
        Message("customer-a", T + timedelta(minutes=2), "I can smell gas"),
        Message("customer-a", T + timedelta(minutes=3), "still smell gas"),
    ]
    _, events = merge(msgs)
    assert events == [("NEW", "customer-a"), ("UPDATE", "customer-a", ["gas", "smell"])]


def test_sender_case_and_spaces_ignored():
    msgs = [Message("Customer-A ", T, "x"), Message("customer-a", T + timedelta(minutes=1), "y")]
    alerts, _ = merge(msgs)
    assert len(alerts) == 1


def test_route_money_with_job_this_week():
    r = route("Where is my refund?", date(2026, 1, 5), date(2026, 1, 12))
    assert r == {"to": ["job_team"], "cc": ["accounts"]}


def test_route_money_job_far_away_or_past():
    assert route("invoice please", date(2026, 1, 5), date(2026, 1, 13))["to"] == ["accounts"]
    assert route("invoice please", date(2026, 1, 5), date(2026, 1, 1))["to"] == ["accounts"]


def test_route_not_money():
    assert route("change my appointment", date(2026, 1, 5), date(2026, 1, 6))["to"] == ["customer_service"]


def test_delete_gate():
    assert check({"a.jpg": 10}, {"a.jpg": 10}) == (True, [])
    ok, problems = check({"a.jpg": 10, "b.jpg": 5}, {"a.jpg": 9})
    assert not ok and len(problems) == 2
    assert check({}, {})[0] is False


def test_strip_png_removes_extra_chunks_keeps_image():
    ihdr = make_chunk(b"IHDR", bytes(13))
    idat = make_chunk(b"IDAT", b"pixels")
    junk = make_chunk(b"caBX", b"credentials")
    text = make_chunk(b"tEXt", b"Software\x00tool")
    iend = make_chunk(b"IEND", b"")
    clean, removed = strip(PNG_SIGNATURE + ihdr + junk + text + idat + iend)
    assert clean == PNG_SIGNATURE + ihdr + idat + iend
    assert removed == ["caBX", "tEXt"]
