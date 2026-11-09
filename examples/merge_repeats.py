"""Merge repeat messages from the same sender into one alert.

Idea: a worried customer often sends 3 to 5 emails in a few minutes.
Five alerts for one problem means people start ignoring alerts.
So messages from the same sender within a time window become ONE alert,
and a follow-up only raises an UPDATE if it adds new urgent words.

All data in this repo is made up.
"""
from dataclasses import dataclass, field
from datetime import datetime, timedelta

URGENT_WORDS = {"gas", "smell", "leak", "carbon monoxide", "no heating", "no hot water"}


@dataclass
class Message:
    sender: str
    sent_at: datetime
    text: str


@dataclass
class Alert:
    sender: str
    first_at: datetime
    last_at: datetime
    messages: list = field(default_factory=list)
    urgent_words: set = field(default_factory=set)
    updates: int = 0


def find_urgent(text: str) -> set:
    lowered = text.lower()
    return {w for w in URGENT_WORDS if w in lowered}


def merge(messages, window_minutes: int = 30):
    """Return (alerts, events). events lists what a person would be told:
    ("NEW", sender) or ("UPDATE", sender, new_words)."""
    window = timedelta(minutes=window_minutes)
    open_alerts = {}
    alerts, events = [], []
    for msg in sorted(messages, key=lambda m: m.sent_at):
        key = msg.sender.strip().lower()
        words = find_urgent(msg.text)
        alert = open_alerts.get(key)
        if alert and msg.sent_at - alert.last_at <= window:
            alert.messages.append(msg)
            alert.last_at = msg.sent_at
            new_words = words - alert.urgent_words
            if new_words:
                alert.urgent_words |= new_words
                alert.updates += 1
                events.append(("UPDATE", key, sorted(new_words)))
            continue
        alert = Alert(key, msg.sent_at, msg.sent_at, [msg], set(words))
        open_alerts[key] = alert
        alerts.append(alert)
        events.append(("NEW", key))
    return alerts, events


if __name__ == "__main__":
    t = datetime(2026, 1, 5, 9, 0)
    demo = [
        Message("customer-sam", t, "My boiler is making a noise"),
        Message("Customer-Sam ", t + timedelta(minutes=4), "Still making a noise"),
        Message("customer-sam", t + timedelta(minutes=9), "Now there is no hot water"),
        Message("customer-jo", t + timedelta(minutes=10), "Can I book a service?"),
        Message("customer-sam", t + timedelta(hours=3), "Thanks, all sorted"),
    ]
    alerts, events = merge(demo)
    print(f"{len(demo)} messages -> {len(alerts)} alerts")
    for e in events:
        print(e)
