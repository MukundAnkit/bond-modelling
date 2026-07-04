"""Day count conventions for fixed-income markets.

Provides functions to compute the year fraction between two dates
according to standard market conventions: 30/360, Act/Act, Act/360,
and Act/365.
"""

from collections.abc import Callable
from datetime import date


def thirty_360(start: date, end: date) -> float:
    """Calculate year fraction using the 30/360 (US) day count convention.

    Each month is treated as 30 days, each year as 360 days.
    Uses the US (NASD) rule: if the start date is the 31st, it becomes
    the 30th; if the end date is the 31st and the start is the 30th,
    the end becomes the 1st of the following month.

    Parameters
    ----------
    start : date
        Start date of the accrual period.
    end : date
        End date of the accrual period.

    Returns
    -------
    float
        Year fraction between start and end.

    """
    d1 = min(start.day, 30)
    d2 = 30 if end.day == 31 and (start.day == 30 or start.day == 31) else end.day
    return float(
        ((end.year - start.year) * 360 + (end.month - start.month) * 30 + (d2 - d1))
        / 360.0
    )


def act_act(start: date, end: date) -> float:
    """Calculate year fraction using the Act/Act (ISMA) day count convention.

    Uses actual calendar days in the numerator and the actual number of
    days in the relevant year(s) in the denominator.

    Parameters
    ----------
    start : date
        Start date of the accrual period.
    end : date
        End date of the accrual period.

    Returns
    -------
    float
        Year fraction between start and end.

    """
    if start.year == end.year:
        days_in_year = 366 if _is_leap(start.year) else 365
        return (end - start).days / days_in_year

    # Split across years
    days_first = (date(start.year, 12, 31) - start).days + 1
    days_in_first = 366 if _is_leap(start.year) else 365
    frac_first = days_first / days_in_first

    days_last = (end - date(end.year, 1, 1)).days
    days_in_last = 366 if _is_leap(end.year) else 365
    frac_last = days_last / days_in_last

    middle_years = end.year - start.year - 1
    return frac_first + middle_years + frac_last


def act_360(start: date, end: date) -> float:
    """Calculate year fraction using the Act/360 day count convention.

    Actual calendar days divided by 360 (Money Market convention).

    Parameters
    ----------
    start : date
        Start date of the accrual period.
    end : date
        End date of the accrual period.

    Returns
    -------
    float
        Year fraction between start and end.

    """
    return (end - start).days / 360.0


def act_365(start: date, end: date) -> float:
    """Calculate year fraction using the Act/365 (Fixed) day count convention.

    Actual calendar days divided by 365 (UK/English convention).

    Parameters
    ----------
    start : date
        Start date of the accrual period.
    end : date
        End date of the accrual period.

    Returns
    -------
    float
        Year fraction between start and end.

    """
    return (end - start).days / 365.0


def year_fraction(start: date, end: date, convention: str = "act_act") -> float:
    """Calculate the year fraction between two dates under a given convention.

    Parameters
    ----------
    start : date
        Start date of the accrual period.
    end : date
        End date of the accrual period.
    convention : str, optional
        Day count convention name: ``"30/360"``, ``"act_act"``, ``"act_360"``,
        or ``"act_365"``. Default is ``"act_act"``.

    Returns
    -------
    float
        Year fraction between start and end.

    Raises
    ------
    ValueError
        If the convention is not recognised.

    """
    _conventions: dict[str, Callable[[date, date], float]] = {
        "30/360": thirty_360,
        "act_act": act_act,
        "act_360": act_360,
        "act_365": act_365,
    }
    func = _conventions.get(convention)
    if func is None:
        raise ValueError(
            f"Unknown day count convention '{convention}'. "
            f"Choose from {list(_conventions)}."
        )
    return func(start, end)


def _is_leap(year: int) -> bool:
    """Return True if *year* is a leap year."""
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)
