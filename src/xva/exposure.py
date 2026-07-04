# ruff: noqa
# mypy: ignore-errors
import numpy as np
from typing import Tuple


def simulate_exposures(
    mtm_paths: np.ndarray,
    mpor_steps: int = 0,
    im_paths: np.ndarray = None,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Calculate Expected Exposure (EE), Potential Future Exposure (PFE),
    and Expected Negative Exposure (ENE) from Mark-to-Market (MtM) paths.
    Incorporates Variation Margin (VM) and Initial Margin (IM) with a Margin Period of Risk (MPoR).

    Args:
        mtm_paths: A 2D numpy array of shape (num_paths, num_time_steps) representing
                   the simulated MtM values of a portfolio.
        mpor_steps: Number of time steps for the Margin Period of Risk (MPoR).
                    If > 0, VM at step t is MtM at step t - mpor_steps.
        im_paths: A 2D numpy array of Initial Margin (IM) posted by the counterparty.

    Returns:
        ee: Expected Exposure over time (1D array of length num_time_steps).
        pfe: Potential Future Exposure over time at 95% confidence level (1D array).
        ene: Expected Negative Exposure over time (1D array).
    """
    vm_paths = np.zeros_like(mtm_paths)
    if mpor_steps > 0:
        vm_paths[:, mpor_steps:] = mtm_paths[:, :-mpor_steps]
        
    if im_paths is None:
        im_paths = np.zeros_like(mtm_paths)
        
    net_mtm = mtm_paths - vm_paths
    
    # Exposure is max(MtM - VM - IM, 0)
    positive_exposures = np.maximum(net_mtm - im_paths, 0)
    # Negative exposure is min(MtM - VM, 0)
    negative_exposures = np.minimum(net_mtm, 0)

    ee = np.mean(positive_exposures, axis=0)
    ene = np.mean(negative_exposures, axis=0)
    pfe = np.percentile(positive_exposures, 95, axis=0)

    return ee, pfe, ene
