import datetime


def now_utc() -> datetime.datetime:
    return datetime.datetime.utcnow()


def get_monday_sunday_for_date(d: datetime.date) -> tuple[datetime.date, datetime.date]:
    monday = d - datetime.timedelta(days=d.weekday())
    sunday = monday + datetime.timedelta(days=6)
    return monday, sunday


def get_month_bounds_for_date(d: datetime.date) -> tuple[datetime.datetime, datetime.datetime]:
    start = datetime.datetime(d.year, d.month, 1)
    if d.month == 12:
        next_month = datetime.datetime(d.year + 1, 1, 1)
    else:
        next_month = datetime.datetime(d.year, d.month + 1, 1)
    end = next_month - datetime.timedelta(microseconds=1)
    return start, end

