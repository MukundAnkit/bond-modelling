"""Cash flow generation utilities."""

from datetime import date

import numpy as np

from src.instruments.bond import Bond


def generate_cashflows(bond: Bond) -> tuple[np.ndarray, np.ndarray]:
    """Generate the times and amounts of all cash flows for a bond.

    Parameters
    ----------
    bond : Bond
        The bond instrument.

    Returns
    -------
    tuple[np.ndarray, np.ndarray]
        A tuple of (times_in_periods, cash_flow_amounts).
        - times_in_periods: 1D array of integers [1, 2, ..., n]
        - cash_flow_amounts: 1D array of dollar amounts for each period.

    """
    t = np.arange(1, bond.periods + 1)
    cf = np.full(bond.periods, bond.coupon_payment)
    cf[-1] += bond.face_value
    cf = np.round(cf, 10)
    return t, cf


def generate_cashflow_dates(
    issue_date: date,
    maturity_date: date,
    freq: int,
) -> list[date]:
    """Generate coupon payment dates for a bond.

    Parameters
    ----------
    issue_date : date
        Bond issue / start date.
    maturity_date : date
        Bond maturity date.
    freq : int
        Coupon payments per year (1, 2, 4, or 12).

    Returns
    -------
    list[date]
        Ordered list of coupon payment dates from issue to maturity.

    """
    months_per_period = 12 // freq
    dates_list: list[date] = []
    current = maturity_date
    while current >= issue_date:
        dates_list.append(current)
        month = current.month - months_per_period
        year = current.year
        if month <= 0:
            month += 12
            year -= 1
        day = min(current.day, _days_in_month(month, year))
        current = current.replace(year=year, month=month, day=day)
    dates_list.reverse()
    return dates_list


def _days_in_month(month: int, year: int) -> int:
    """Return the number of days in *month* of *year*."""
    if month == 2:
        return 29 if (year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)) else 28
    if month in (4, 6, 9, 11):
        return 30
    return 31
