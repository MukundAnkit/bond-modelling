"""Basel IRBB regulatory stress scenarios.

Implements the six non-parallel interest-rate shock regimes prescribed by
the Basel Committee's Interest Rate Risk in the Banking Book (IRBB)
standardised framework.  Each scenario returns the shocked bond price and
the resulting P&L (price change).
"""

from collections.abc import Callable

import numpy as np
from numpy.typing import NDArray

from src.instruments.bond import Bond
from src.instruments.pricing import price

# ---------------------------------------------------------------------------
# Scenario definitions — each returns a shock vector over a given tenor grid
# ---------------------------------------------------------------------------

ScenarioFn = Callable[[list[float]], NDArray[np.float64]]


def _parallel_up(key_rates: list[float]) -> NDArray[np.float64]:
    return np.full(len(key_rates), 0.01)


def _parallel_down(key_rates: list[float]) -> NDArray[np.float64]:
    return np.full(len(key_rates), -0.01)


def _steepener(key_rates: list[float]) -> NDArray[np.float64]:
    r"""Short rates  down −100 bp → long rates up +100 bp (linear ramp)."""
    return np.array([-0.01 + 0.02 * min(kr / 20.0, 1.0) for kr in key_rates])


def _flattener(key_rates: list[float]) -> NDArray[np.float64]:
    r"""Short rates  up +100 bp → long rates down −100 bp (linear ramp)."""
    return np.array([0.01 - 0.02 * min(kr / 20.0, 1.0) for kr in key_rates])


def _short_rate_up(key_rates: list[float]) -> NDArray[np.float64]:
    r"""Short end +300 bp decaying linearly to 0 at 20 years."""
    return np.array([0.03 * max(0.0, 1.0 - kr / 20.0) for kr in key_rates])


def _short_rate_down(key_rates: list[float]) -> NDArray[np.float64]:
    r"""Short end −300 bp decaying linearly to 0 at 20 years."""
    return np.array([-0.03 * max(0.0, 1.0 - kr / 20.0) for kr in key_rates])


# ---------------------------------------------------------------------------
# Registry of named scenarios
# ---------------------------------------------------------------------------

SCENARIOS: dict[str, ScenarioFn] = {
    "parallel_up": _parallel_up,
    "parallel_down": _parallel_down,
    "steepener": _steepener,
    "flattener": _flattener,
    "short_rate_up": _short_rate_up,
    "short_rate_down": _short_rate_down,
}


# ---------------------------------------------------------------------------
# Repricing helpers
# ---------------------------------------------------------------------------


def irbb_shock_vector(
    scenario: str,
    key_rates: list[float],
) -> NDArray[np.float64]:
    r"""Return the yield-shock vector for a named IRBB scenario.

    Parameters
    ----------
    scenario : str
        One of ``\"parallel_up\"``, ``\"parallel_down\"``, ``\"steepener\"``,
        ``\"flattener\"``, ``\"short_rate_up\"``, ``\"short_rate_down\"``.
    key_rates : list[float]
        Tenor points in years at which the shock is defined.

    Returns
    -------
    NDArray[np.float64]
        Shock magnitude (in decimal) at each key-rate tenor.

    """
    return SCENARIOS[scenario](key_rates)


def shocked_price_non_parallel(
    bond: Bond,
    yield_rate: float,
    key_rates: list[float],
    shocks: NDArray[np.float64],
) -> float:
    """Reprice a bond under a non-parallel yield-curve shock.

    Each cash flow is discounted at ``yield_rate + interpolated_shock``,
    where the shock at the cash flow's time-to-maturity is linearly
    interpolated from the key-rate grid.

    Parameters
    ----------
    bond : Bond
        The bond instrument.
    yield_rate : float
        Base market yield (YTM) as a decimal.
    key_rates : list[float]
        Tenor points (years) defining the shock vector.
    shocks : NDArray[np.float64]
        Shock magnitude at each key-rate tenor (same length as ``key_rates``).

    Returns
    -------
    float
        Bond price under the shocked yield curve.

    """
    m = bond.freq
    n = bond.periods
    t_years = np.arange(1, n + 1) / m

    cf = np.full(n, bond.coupon_payment)
    cf[-1] += bond.face_value

    cash_flow_shocks = np.interp(t_years, key_rates, shocks)
    rate_per_period = (yield_rate + cash_flow_shocks) / m
    periods = np.arange(1, n + 1)
    discount_factors = (1.0 + rate_per_period) ** (-periods)

    return float(np.sum(cf * discount_factors))


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def irbb_stress_scenarios(
    bond: Bond,
    yield_rate: float,
    key_rates: list[float] | None = None,
) -> dict[str, dict[str, float]]:
    r"""Apply all six Basel IRBB stress scenarios to a bond.

    Parameters
    ----------
    bond : Bond
        The bond instrument.
    yield_rate : float
        Current market yield (YTM) as a decimal.
    key_rates : list[float], optional
        Tenor points (years) defining the shock vector.  Defaults to
        ``[0.5, 1, 2, 3, 5, 7, 10, 20, 30]`` truncated at bond maturity.

    Returns
    -------
    dict[str, dict[str, float]]
        Mapping of scenario name to ``{"price": ..., "pnl": ...}``.

    """
    if key_rates is None:
        key_rates = [
            kr
            for kr in [0.5, 1.0, 2.0, 3.0, 5.0, 7.0, 10.0, 20.0, 30.0]
            if kr <= bond.maturity
        ]

    p0 = price(bond, yield_rate)
    results: dict[str, dict[str, float]] = {}

    for name, fn in SCENARIOS.items():
        shocks = fn(key_rates)
        p_shocked = shocked_price_non_parallel(bond, yield_rate, key_rates, shocks)
        results[name] = {"price": p_shocked, "pnl": p_shocked - p0}

    return results
