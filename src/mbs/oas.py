"""Option-Adjusted Spread calculation module."""

from collections.abc import Callable

import numpy as np
import scipy.optimize as opt

from .pass_through import project_cash_flows


def generate_hw1f_paths(
    r0: float,
    a: float,
    sigma: float,
    n_paths: int,
    term_months: int,
    dt: float = 1.0 / 12.0,
    theta: float | np.ndarray = 0.05
) -> np.ndarray:
    """Generate interest rate paths using the Hull-White 1-factor model.
    
    dr(t) = (theta(t) - a * r(t)) dt + sigma * dW(t)
    """
    paths = np.zeros((n_paths, term_months))
    paths[:, 0] = r0
    
    if isinstance(theta, (int, float)):
        theta_arr = np.full(term_months, theta)
    else:
        theta_arr = theta

    Z = np.random.standard_normal((n_paths, term_months - 1))
    
    for t in range(1, term_months):
        dr = (theta_arr[t-1] - a * paths[:, t-1]) * dt + sigma * np.sqrt(dt) * Z[:, t-1]
        paths[:, t] = paths[:, t-1] + dr
        
    return paths


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
    prepayment_model: Callable[[np.ndarray, float], np.ndarray | Callable[[int, float], float]],
) -> float:
    """Calculate the Option-Adjusted Spread (OAS) for an MBS."""
    n_paths = rate_paths.shape[0]
    all_cash_flows = []

    for i in range(n_paths):
        # prepayment_model can return either a static vector or a callable for dynamic burnout
        smm_vector_or_func = prepayment_model(rate_paths[i], wac)
        cf_dict = project_cash_flows(balance, wac, term, smm_vector_or_func)
        all_cash_flows.append(cf_dict["total_cash_flow"])

    def price_diff(oas_val: float) -> float:
        pv_sum = 0.0
        for i in range(n_paths):
            pv_sum += price_mbs(all_cash_flows[i], rate_paths[i], oas_val)
        expected_pv = pv_sum / n_paths
        return float(expected_pv - price)

    try:
        oas_solution = opt.brentq(price_diff, -0.20, 0.50)
        return float(oas_solution)
    except ValueError:
        solution = opt.fsolve(price_diff, x0=[0.0])
        return float(solution[0])
