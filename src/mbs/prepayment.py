"""Prepayment models for Mortgage-Backed Securities."""


def cpr_to_smm(cpr: float) -> float:
    """Convert CPR to Single Monthly Mortality (SMM)."""
    return float(1.0 - (1.0 - cpr) ** (1.0 / 12.0))


def smm_to_cpr(smm: float) -> float:
    """Convert SMM to Conditional Prepayment Rate (CPR)."""
    return float(1.0 - (1.0 - smm) ** 12.0)


def psa_to_cpr(psa: float, month: int) -> float:
    """Calculate CPR based on the PSA curve for a given month."""
    if month < 1:
        raise ValueError("Month must be >= 1")

    cpr_100 = min(month * 0.002, 0.06)
    return cpr_100 * (psa / 100.0)


def psa_to_smm(psa: float, month: int) -> float:
    """Calculate SMM based on the PSA curve for a given month."""
    cpr = psa_to_cpr(psa, month)
    return cpr_to_smm(cpr)
