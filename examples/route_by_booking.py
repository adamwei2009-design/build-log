"""Route a money request by context, not just by category.

Idea: a refund or invoice question usually goes to the accounts team.
But if the customer has a job booked in the next few days, the team doing
that job needs to know first, with accounts copied in.

All names and data here are made up.
"""
from datetime import date

MONEY_WORDS = ("refund", "invoice", "deposit", "payment")


def is_money_request(text: str) -> bool:
    t = text.lower()
    return any(w in t for w in MONEY_WORDS)


def route(text: str, today: date, booked_job_date=None, window_days: int = 7):
    """Return {"to": [...], "cc": [...]}."""
    if not is_money_request(text):
        return {"to": ["customer_service"], "cc": []}
    if booked_job_date is not None:
        days_away = (booked_job_date - today).days
        if 0 <= days_away <= window_days:
            return {"to": ["job_team"], "cc": ["accounts"]}
    return {"to": ["accounts"], "cc": []}


if __name__ == "__main__":
    today = date(2026, 1, 5)
    print(route("Where is my refund?", today))
    print(route("Can I get an invoice?", today, booked_job_date=date(2026, 1, 9)))
    print(route("Can I get an invoice?", today, booked_job_date=date(2026, 2, 20)))
    print(route("Can I change my appointment?", today))
