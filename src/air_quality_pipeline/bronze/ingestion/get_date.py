from calendar import monthrange
from datetime import date


def generate_months_period(
        start_date: str,
        end_date: str,
):
    """Increment the date from start to end of months."""

    start = date.fromisoformat(start_date)
    end = date.fromisoformat(end_date)

    if start > end:
        raise ValueError("start_date must be less than or equal to end_date")

    year = start.year
    month = start.month

    while (year, month) <= (end.year, end.month):
        first_day = date(year, month, 1)

        last_day_number = monthrange(year, month)[1]
        last_day = date(year, month, last_day_number)

        yield (
            first_day.strftime("%Y-%m-%d"),
            last_day.strftime("%Y-%m-%d"),
        )

        if month == 12:
            year += 1
            month = 1
        else:
            month += 1