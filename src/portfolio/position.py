"""Bond position class to represent holdings of a single bond instrument."""

from dataclasses import dataclass

from src.curve.nelson_siegel import NelsonSiegelCurve
from src.instruments.bond import Bond
from src.instruments.pricing import price
from src.risk.convexity import convexity
from src.risk.duration import modified_duration


@dataclass
class Position:
    """A position holding a quantity of a specific fixed-rate bond.

    Parameters
    ----------
    bond : Bond
        The bond instrument.
    quantity : int
        The number of bonds held in this position. Must be positive.
    purchase_price : float, optional
        The purchase price per bond (for P&L tracking). Default is ``None``.

    """

    bond: Bond
    quantity: int
    purchase_price: float | None = None

    def __post_init__(self) -> None:
        """Validate inputs on construction."""
        if self.quantity <= 0:
            raise ValueError("quantity must be strictly positive")

    @property
    def face_value(self) -> float:
        """Total face value of the position."""
        return float(self.quantity * self.bond.face_value)

    def market_value(self, yield_curve: NelsonSiegelCurve) -> float:
        """Calculate the total market value of this position.

        Parameters
        ----------
        yield_curve : NelsonSiegelCurve
            The yield curve to use for pricing.

        Returns
        -------
        float
            The position's market value.

        """
        y = float(yield_curve.yield_rate(self.bond.maturity))
        single_price = price(self.bond, y)
        return float(self.quantity * single_price)

    def duration(self, yield_curve: NelsonSiegelCurve) -> float:
        """Calculate the Modified Duration of the bond under the yield curve.

        Parameters
        ----------
        yield_curve : NelsonSiegelCurve
            The yield curve to use for pricing.

        Returns
        -------
        float
            The bond's Modified Duration.

        """
        y = float(yield_curve.yield_rate(self.bond.maturity))
        return float(modified_duration(self.bond, y))

    def convexity(self, yield_curve: NelsonSiegelCurve) -> float:
        """Calculate the Convexity of the bond under the yield curve.

        Parameters
        ----------
        yield_curve : NelsonSiegelCurve
            The yield curve to use for pricing.

        Returns
        -------
        float
            The bond's Convexity.

        """
        y = float(yield_curve.yield_rate(self.bond.maturity))
        return float(convexity(self.bond, y))

    def dv01(self, yield_curve: NelsonSiegelCurve) -> float:
        """Calculate the DV01 (dollar value of a basis point) for the position.

        Parameters
        ----------
        yield_curve : NelsonSiegelCurve
            The yield curve to use for pricing.

        Returns
        -------
        float
            The dollar sensitivity to a 1 basis point increase in yield.

        """
        y = float(yield_curve.yield_rate(self.bond.maturity))
        mod_d = modified_duration(self.bond, y)
        mv = self.market_value(yield_curve)
        return float(mod_d * mv * 0.0001)
