"""Pass-through MBS math module."""

from collections.abc import Callable

import numpy as np


def calculate_scheduled_pmt(balance: float, rate: float, term: int) -> float:
    """Calculate the scheduled monthly payment for a fixed-rate mortgage.

    Args:
        balance: Beginning balance.
        rate: Monthly interest rate (annual rate / 12).
        term: Remaining term in months.

    Returns:
        Scheduled monthly payment.

    """
    if rate <= 0:
        return balance / term if term > 0 else 0.0
    return balance * rate / (1 - (1 + rate) ** -term)


def project_cash_flows(
    balance: float,
    wac: float,
    term: int,
    smm_vector_or_func: list[float] | np.ndarray | Callable[[int, float], float],
) -> dict[str, np.ndarray]:
    """Project cash flows for a pass-through MBS."""
    monthly_rate = wac / 12.0

    balances = np.zeros(term + 1)
    balances[0] = balance

    sched_prin = np.zeros(term)
    prepayments = np.zeros(term)
    interest = np.zeros(term)

    for t in range(term):
        if balances[t] <= 0:
            break

        rem_term = term - t
        pmt = calculate_scheduled_pmt(balances[t], monthly_rate, rem_term)

        interest[t] = balances[t] * monthly_rate
        sched_prin[t] = min(pmt - interest[t], balances[t])

        rem_balance = balances[t] - sched_prin[t]

        if callable(smm_vector_or_func):
            pool_factor = balances[t] / balance if balance > 0 else 0.0
            smm = smm_vector_or_func(t, pool_factor)
        else:
            smm = (
                smm_vector_or_func[t]
                if t < len(smm_vector_or_func)
                else smm_vector_or_func[-1]
            )

        prepayments[t] = min(rem_balance * smm, rem_balance)

        balances[t + 1] = balances[t] - sched_prin[t] - prepayments[t]

    total_prin = sched_prin + prepayments
    total_cf = total_prin + interest

    return {
        "balance": balances,
        "scheduled_principal": sched_prin,
        "prepayment": prepayments,
        "interest": interest,
        "total_principal": total_prin,
        "total_cash_flow": total_cf,
    }


def average_life(total_principal: np.ndarray, initial_balance: float) -> float:
    """Calculate the Weighted Average Life (WAL) in years."""
    if initial_balance <= 0 or np.sum(total_principal) <= 0:
        return 0.0

    months = np.arange(1, len(total_principal) + 1)
    return float(np.sum(months * total_principal) / (12.0 * initial_balance))
