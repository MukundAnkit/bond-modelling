"""CPI indexing and inflation adjustments for TIPS."""


def daily_ref_cpi(
    cpi_first_of_month: float,
    cpi_next_month: float,
    day_of_month: int,
    days_in_month: int,
) -> float:
    """Calculate the daily Reference CPI using linear interpolation.

    For a given day of the month, the Reference CPI is interpolated between
    the applicable CPI for the first day of the current month and the first
    day of the next month (usually a 2-3 month lag).

    Parameters
    ----------
    cpi_first_of_month : float
        The reference CPI applicable to the 1st of the settlement month.
    cpi_next_month : float
        The reference CPI applicable to the 1st of the next month.
    day_of_month : int
        The day of the month for settlement (1-based).
    days_in_month : int
        Total number of days in the settlement month.

    Returns
    -------
    float
        The interpolated daily Reference CPI.

    """
    if days_in_month <= 0:
        raise ValueError("days_in_month must be strictly positive")
    if day_of_month < 1 or day_of_month > days_in_month:
        raise ValueError("day_of_month must be between 1 and days_in_month")

    ratio = (day_of_month - 1) / days_in_month
    return cpi_first_of_month + ratio * (cpi_next_month - cpi_first_of_month)


def index_ratio(ref_cpi: float, base_cpi: float) -> float:
    """Calculate the index ratio for a specific date.

    Parameters
    ----------
    ref_cpi : float
        The interpolated Reference CPI for the current date.
    base_cpi : float
        The Base CPI at bond issuance.

    Returns
    -------
    float
        The index ratio used to scale cash flows.

    """
    if base_cpi <= 0:
        raise ValueError("base_cpi must be positive")
    return ref_cpi / base_cpi
