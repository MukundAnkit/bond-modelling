from typing import Any


class ScenarioGenerator:
    """Generator for macro-economic scenarios."""

    def __init__(self) -> None:
        pass

    def apply_non_parallel_shift(
        self, curve: Any, shift_type: str, alpha: float, pivot: float | None = None
    ) -> Any:
        """Apply a non-parallel shift to the yield curve."""
        import copy

        import numpy as np

        new_curve = copy.deepcopy(curve)
        if shift_type == "steepening":
            shift = alpha * np.log(1 + curve.tenors)
        elif shift_type == "flattening":
            shift = -alpha * np.log(1 + curve.tenors)
        elif shift_type == "twist":
            if pivot is None:
                raise ValueError("Pivot must be specified for twist shift")
            shift = alpha * (curve.tenors - pivot)
        else:
            raise ValueError(f"Unknown shift type: {shift_type}")

        new_curve.yields = curve.yields + shift
        return new_curve

    def apply_policy_shock(self, curve: Any, delta_r: float, decay: float) -> Any:
        """Apply a central bank policy shock to the yield curve."""
        import copy

        import numpy as np

        new_curve = copy.deepcopy(curve)
        shift = delta_r * np.exp(-decay * curve.tenors)
        new_curve.yields = curve.yields + shift
        return new_curve
