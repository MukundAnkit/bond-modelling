import numpy as np  # noqa: D100


class VasicekModel:
    """Vasicek short-rate model.

    dr_t = a(b - r_t)dt + sigma * dW_t
    """

    def __init__(self, a: float, b: float, sigma: float):  # noqa: D107
        self.a = a
        self.b = b
        self.sigma = sigma

    def zcb_price(
        self, r_t: float | np.ndarray, tau: float | np.ndarray
    ) -> float | np.ndarray:
        """Calculate the price of a Zero-Coupon Bond.

        Args:
            r_t: Current short rate.
            tau: Time to maturity (T - t).

        Returns:
            Price of the bond.
        """  # noqa: D413
        a, b, sigma = self.a, self.b, self.sigma

        if np.isclose(a, 0):
            B = tau  # noqa: N806
            A = np.exp(0.5 * sigma**2 * tau**3 / 3.0)  # noqa: N806
        else:
            B = (1.0 - np.exp(-a * tau)) / a  # noqa: N806

            # Asymptotic long-term mean under risk-neutral measure
            # (Assuming no risk premium specified, so b is risk-neutral mean)
            term1 = (B - tau) * (b - (sigma**2) / (2 * a**2))
            term2 = (sigma**2 * B**2) / (4 * a)
            A = np.exp(term1 - term2)  # noqa: N806

        return A * np.exp(-B * r_t)


class CIRModel:
    """Cox-Ingersoll-Ross (CIR) short-rate model.

    dr_t = a(b - r_t)dt + sigma * sqrt(r_t) * dW_t
    """

    def __init__(self, a: float, b: float, sigma: float):  # noqa: D107
        self.a = a
        self.b = b
        self.sigma = sigma

        # Feller condition check (2ab > sigma^2) prevents rate from reaching zero
        if 2 * a * b <= sigma**2:
            import warnings

            warnings.warn(  # noqa: B028
                "Feller condition (2ab > sigma^2) is not satisfied. Rates may hit zero."
            )

    def zcb_price(
        self, r_t: float | np.ndarray, tau: float | np.ndarray
    ) -> float | np.ndarray:
        """Calculate the price of a Zero-Coupon Bond.

        Args:
            r_t: Current short rate.
            tau: Time to maturity (T - t).

        Returns:
            Price of the bond.
        """  # noqa: D413
        a, b, sigma = self.a, self.b, self.sigma

        h = np.sqrt(a**2 + 2 * sigma**2)

        exp_h_tau = np.exp(h * tau)

        B_num = 2 * (exp_h_tau - 1)  # noqa: N806
        B_den = 2 * h + (a + h) * (exp_h_tau - 1)  # noqa: N806
        B = B_num / B_den  # noqa: N806

        A_num = 2 * h * np.exp((a + h) * tau / 2)  # noqa: N806
        A_den = 2 * h + (a + h) * (exp_h_tau - 1)  # noqa: N806
        A = (A_num / A_den) ** (2 * a * b / sigma**2)  # noqa: N806

        return A * np.exp(-B * r_t)  # type: ignore
