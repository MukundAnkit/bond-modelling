"""Key Rate Duration for non-parallel yield curve sensitivity."""

import numpy as np

from src.instruments.bond import Bond
from src.instruments.pricing import price


def key_rate_durations(
    bond: Bond,
    yield_rate: float,
    key_rates: list[float] | None = None,
    bump: float = 0.0001,
) -> dict[float, float]:
    r"""Calculate Key Rate Durations via numerical bumping.

    Each key rate tenor is bumped independently by ``bump`` and the
    resulting percentage price change gives the partial duration at that
    tenor.  Cash flows that fall between key rate tenors are linearly
    interpolated between the two bracketing tenors.

    For a flat yield curve the sum of all Key Rate Durations equals
    Modified Duration (within numerical precision).

    Parameters
    ----------
    bond : Bond
        The bond instrument.
    yield_rate : float
        Flat yield curve level as a decimal.
    key_rates : list[float], optional
        Tenor points in years.  Defaults to
        ``[0.5, 1, 2, 3, 5, 7, 10, 20, 30]`` truncated at bond maturity.
    bump : float, optional
        Size of yield bump in decimal (default 1 bp = 0.0001).

    Returns
    -------
    dict[float, float]
        Mapping of tenor (years) → Key Rate Duration.

    """
    if key_rates is None:
        standard = [0.5, 1.0, 2.0, 3.0, 5.0, 7.0, 10.0, 20.0, 30.0]
        key_rates = [k for k in standard if k <= bond.maturity]
        if not key_rates or key_rates[-1] < bond.maturity:
            key_rates.append(bond.maturity)

    p0 = price(bond, yield_rate)
    m = bond.freq
    n = bond.periods
    t_years = np.arange(1, n + 1) / m  # cash flow times in years

    # Build cash flow vector
    cf = np.full(n, bond.coupon_payment)
    cf[-1] += bond.face_value

    results: dict[float, float] = {}

    for kr in key_rates:
        # For each key rate, compute weights: how much of each CF's
        # discount rate is affected by a bump at this key rate.
        weights = np.zeros(n)
        for i, t in enumerate(t_years):
            # Find bracketing key rates
            if t <= key_rates[0]:
                # Before or at the first key rate
                if kr == key_rates[0]:
                    weights[i] = 1.0
            elif t >= key_rates[-1]:
                # At or after the last key rate
                if kr == key_rates[-1]:
                    weights[i] = 1.0
            else:
                # Between two key rates — linear interpolation
                for j in range(len(key_rates) - 1):
                    if key_rates[j] <= t <= key_rates[j + 1]:
                        if kr == key_rates[j]:
                            weights[i] = (
                                (key_rates[j + 1] - t)
                                / (key_rates[j + 1] - key_rates[j])
                            )
                        elif kr == key_rates[j + 1]:
                            weights[i] = (
                                (t - key_rates[j])
                                / (key_rates[j + 1] - key_rates[j])
                            )
                        break

        # Bump the yield for each CF proportionally.
        # Each cash flow is discounted independently at its own bumped rate.
        rate_per_period = yield_rate / m
        bumped_rate_per_period = rate_per_period + weights * (bump / m)
        periods = np.arange(1, n + 1)
        discount_factors = (1.0 + bumped_rate_per_period) ** (-periods)
        p_bumped = float(np.sum(cf * discount_factors))

        krd = -(p_bumped - p0) / (bump * p0)
        results[kr] = krd

    return results
