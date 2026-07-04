import typing
from typing import Callable, Union
import numpy as np  # noqa: D100
from src.utils.stochastic import integrate_function


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


class HullWhite1FModel:
    """Time-varying Hull-White One-Factor Model.

    dr_t = (theta(t) - a * r_t)dt + sigma * dW_t
    """

    def __init__(self, a: float, sigma: float, theta: Callable[[float], float]):
        self.a = a
        self.sigma = sigma
        self.theta = theta

    def zcb_price(self, r_t: float, t: float, T: float) -> float:
        """Calculate the price of a Zero-Coupon Bond."""
        if T == t:
            return 1.0

        a = self.a
        sigma = self.sigma

        def B(s: float, T_param: float) -> float:
            return (1.0 - np.exp(-a * (T_param - s))) / a

        def integrand(s: float) -> float:
            BsT = B(s, T)
            return 0.5 * sigma**2 * BsT**2 - self.theta(s) * BsT

        ln_A = integrate_function(integrand, t, T)
        A = np.exp(ln_A)

        return A * np.exp(-B(t, T) * r_t)


class HullWhite2FModel:
    """Time-varying Hull-White Two-Factor Model.

    r_t = x_t + y_t + phi(t)
    dx_t = -a * x_t * dt + sigma1 * dW1_t
    dy_t = -b * y_t * dt + sigma2 * dW2_t
    dW1_t * dW2_t = rho * dt
    """

    def __init__(
        self,
        a: float,
        b: float,
        sigma1: float,
        sigma2: float,
        rho: float,
        phi: Callable[[float], float],
    ):
        self.a = a
        self.b = b
        self.sigma1 = sigma1
        self.sigma2 = sigma2
        self.rho = rho
        self.phi = phi

    def zcb_price(self, x_t: float, y_t: float, t: float, T: float) -> float:
        """Calculate the price of a Zero-Coupon Bond."""
        if T == t:
            return 1.0

        a, b = self.a, self.b
        sigma1, sigma2 = self.sigma1, self.sigma2
        rho = self.rho

        def B_z(z: float, tau: float) -> float:
            return (1.0 - np.exp(-z * tau)) / z if z != 0 else tau

        tau = T - t
        Bx = B_z(a, tau)
        By = B_z(b, tau)

        # Variance term V(t,T)
        term1 = (sigma1**2 / a**2) * (tau - Bx - 0.5 * a * Bx**2)
        term2 = (sigma2**2 / b**2) * (tau - By - 0.5 * b * By**2)
        term3 = (2 * rho * sigma1 * sigma2 / (a * b)) * (
            tau - Bx - By + B_z(a + b, tau)
        )
        V = term1 + term2 + term3

        int_phi = integrate_function(self.phi, t, T)

        return np.exp(-int_phi - Bx * x_t - By * y_t + 0.5 * V)


class ShiftedCIRModel:
    """Shifted Cox-Ingersoll-Ross (CIR) model.

    r_t = x_t + shift
    dx_t = a(b - x_t)dt + sigma * sqrt(x_t) * dW_t
    """

    def __init__(self, a: float, b: float, sigma: float, shift: float):
        self.a = a
        self.b = b
        self.sigma = sigma
        self.shift = shift

        if 2 * a * b <= sigma**2:
            import warnings
            warnings.warn(
                "Feller condition (2ab > sigma^2) is not satisfied for the underlying CIR process."
            )

    def zcb_price(
        self, r_t: Union[float, np.ndarray], tau: Union[float, np.ndarray]
    ) -> Union[float, np.ndarray]:
        """Calculate the price of a Zero-Coupon Bond."""
        a, b, sigma = self.a, self.b, self.sigma
        h = np.sqrt(a**2 + 2 * sigma**2)
        exp_h_tau = np.exp(h * tau)

        B_num = 2 * (exp_h_tau - 1)
        B_den = 2 * h + (a + h) * (exp_h_tau - 1)
        B = B_num / B_den

        A_num = 2 * h * np.exp((a + h) * tau / 2)
        A_den = 2 * h + (a + h) * (exp_h_tau - 1)
        A = (A_num / A_den) ** (2 * a * b / sigma**2)

        x_t = r_t - self.shift

        return A * np.exp(-B * x_t) * np.exp(-self.shift * tau)


class ShiftedLognormalModel:
    """Shifted Lognormal Model (Black-Karasinski style with constant parameters).

    x_t = r_t - shift
    d(ln(x_t)) = (theta - a * ln(x_t))dt + sigma * dW_t
    """

    def __init__(self, a: float, theta: float, sigma: float, shift: float):
        self.a = a
        self.theta = theta
        self.sigma = sigma
        self.shift = shift
