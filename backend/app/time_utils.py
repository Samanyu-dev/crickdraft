from datetime import datetime, timedelta, timezone

IST = timezone(timedelta(hours=5, minutes=30))


def ist_today() -> str:
    return datetime.now(IST).date().isoformat()
