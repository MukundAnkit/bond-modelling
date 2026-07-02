"""Option-Adjusted Spread calculation module."""

from collections.abc import Callable

import numpy as np
import scipy.optimize as opt

from .pass_through import project_cash_flows


def price_mbs(cash_flows: np.ndarray, rate_path: np.ndarray, oas: float = 0.0) -> float:
    """Calculate PV of MBS cash flows for a given rate path & OAS."""
    discount_rates = (rate_path[: len(cash_flows)] + oas) / 12.0
    discount_factors = 1.0 / np.cumprod(1.0 + discount_rates)

    return float(np.sum(cash_flows * discount_factors))


def calculate_oas(
    price: float,
    balance: float,
    wac: float,
    term: int,
    rate_paths: np.ndarray,
    prepayment_model: Callable[[np.ndarray, float], np.ndarray],
) -> float:
    """Calculate the Option-Adjusted Spread (OAS) for an MBS."""
    n_paths = rate_paths.shape[0]
    all_cash_flows = []

    for i in range(n_paths):
        smm_vector = prepayment_model(rate_paths[i], wac)
        cf_dict = project_cash_flows(balance, wac, term, smm_vector)
        all_cash_flows.append(cf_dict["total_cash_flow"])

    def price_diff(oas_val: float) -> float:
        pv_sum = 0.0
        for i in range(n_paths):
            pv_sum += price_mbs(all_cash_flows[i], rate_paths[i], oas_val)
        expected_pv = pv_sum / n_paths
        return float(expected_pv - price)

    try:
        oas_solution = opt.brentq(price_diff, -0.10, 0.50)
        return float(oas_solution)
    except ValueError:
        solution = opt.fsolve(price_diff, x0=[0.0])
        return float(solution[0])
