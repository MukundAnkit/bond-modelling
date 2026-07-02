# ruff: noqa
# mypy: ignore-errors
import numpy as np
from typing import Tuple


def simulate_exposures(
    mtm_paths: np.ndarray,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Calculate Expected Exposure (EE), Potential Future Exposure (PFE),
    and Expected Negative Exposure (ENE) from Mark-to-Market (MtM) paths.

    Args:
        mtm_paths: A 2D numpy array of shape (num_paths, num_time_steps) representing
                   the simulated MtM values of a portfolio.

    Returns:
        ee: Expected Exposure over time (1D array of length num_time_steps).
        pfe: Potential Future Exposure over time at 95% confidence level (1D array).
        ene: Expected Negative Exposure over time (1D array).
    """
    # Exposure is max(MtM, 0)
    positive_exposures = np.maximum(mtm_paths, 0)
    # Negative exposure is min(MtM, 0)
    negative_exposures = np.minimum(mtm_paths, 0)

    ee = np.mean(positive_exposures, axis=0)
    ene = np.mean(negative_exposures, axis=0)
    pfe = np.percentile(positive_exposures, 95, axis=0)

    return ee, pfe, ene
