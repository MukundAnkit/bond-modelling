"""Reusable plotting utilities for the bond modelling project.

Provides project-wide matplotlib configuration, a standardised colour
palette, figure factories with sensible defaults, and convenience helpers
for common bond visualisation patterns.
"""

from dataclasses import dataclass
from typing import Any

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.axes import Axes
from matplotlib.figure import Figure

# ---------------------------------------------------------------------------
# Theme
# ---------------------------------------------------------------------------


def set_theme() -> None:
    """Apply project-wide matplotlib style defaults.

    Should be called once at the start of any notebook or script that
    produces figures for this project.
    """
    plt.rcParams["figure.dpi"] = 120
    plt.rcParams["font.size"] = 10
    plt.rcParams["lines.linewidth"] = 1.8
    plt.rcParams["grid.alpha"] = 0.3


# ---------------------------------------------------------------------------
# Colour palette
# ---------------------------------------------------------------------------

BOND_COLORS: dict[str, str] = {
    "price_curve": "#e74c3c",
    "coupon_bar": "#2ecc71",
    "face_bar": "#3498db",
    "solver": "#e67e22",
    "solver_error": "#c0392b",
    "bisection": "#2980b9",
    "zero_coupon": "#9b59b6",
    "reference": "gray",
}


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------


@dataclass
class FigureConfig:
    """Default layout parameters for project figures.

    Attributes
    ----------
    single_figsize : tuple[float, float]
        (width, height) for single-axis figures.
    subplot_figsize : tuple[float, float]
        (width, height) for multi-axis layouts.
    legend_fontsize : int
        Font size for single-axis figure legends.
    subplot_legend_fontsize : int
        Font size for subplot figure legends.

    """

    single_figsize: tuple[float, float] = (8, 4)
    subplot_figsize: tuple[float, float] = (10, 4)
    legend_fontsize: int = 9
    subplot_legend_fontsize: int = 8


DEFAULT_CONFIG: FigureConfig = FigureConfig()


# ---------------------------------------------------------------------------
# Figure factories
# ---------------------------------------------------------------------------


def figure(
    figsize: tuple[float, float] | None = None,
    **kwargs: Any,
) -> tuple[Figure, Axes]:
    """Create a single-axis figure with project-wide defaults.

    Parameters
    ----------
    figsize : tuple[float, float], optional
        (width, height) in inches. Defaults to ``FigureConfig.single_figsize``.
    **kwargs
        Additional keyword arguments forwarded to ``plt.subplots``.

    Returns
    -------
    tuple[Figure, Axes]
        The figure and its single axes.

    """
    if figsize is None:
        figsize = DEFAULT_CONFIG.single_figsize
    fig, ax = plt.subplots(figsize=figsize, **kwargs)
    return fig, ax


def subplots(
    nrows: int = 1,
    ncols: int = 2,
    figsize: tuple[float, float] | None = None,
    **kwargs: Any,
) -> tuple[Figure, np.ndarray]:
    """Create a multi-axis figure with project-wide defaults.

    Parameters
    ----------
    nrows : int
        Number of rows of subplots.
    ncols : int
        Number of columns of subplots.
    figsize : tuple[float, float], optional
        (width, height) in inches. Defaults to ``FigureConfig.subplot_figsize``.
    **kwargs
        Additional keyword arguments forwarded to ``plt.subplots``.

    Returns
    -------
    tuple[Figure, np.ndarray]
        The figure and a 1-D array of its axes.

    """
    if figsize is None:
        figsize = DEFAULT_CONFIG.subplot_figsize
    fig, axes = plt.subplots(nrows, ncols, figsize=figsize, **kwargs)
    return fig, axes


# ---------------------------------------------------------------------------
# Formatting helpers
# ---------------------------------------------------------------------------


def finish_plot(
    ax: Axes,
    title: str | None = None,
    xlabel: str | None = None,
    ylabel: str | None = None,
    legend: bool = True,
    grid: bool = True,
    tight: bool = True,
) -> None:
    """Apply standardised finishing touches to a completed plot.

    Parameters
    ----------
    ax : Axes
        The axes to format.
    title : str, optional
        Axis title.
    xlabel : str, optional
        X-axis label.
    ylabel : str, optional
        Y-axis label.
    legend : bool
        Whether to draw the legend.
    grid : bool
        Whether to show the grid.
    tight : bool
        Whether to call ``plt.tight_layout()``.

    """
    if xlabel is not None:
        ax.set_xlabel(xlabel)
    if ylabel is not None:
        ax.set_ylabel(ylabel)
    if title is not None:
        ax.set_title(title)
    if grid:
        ax.grid(alpha=plt.rcParams.get("grid.alpha", 0.3))
    if legend:
        ax.legend(fontsize=DEFAULT_CONFIG.legend_fontsize)
    if tight:
        plt.tight_layout()


def reference_line(
    ax: Axes,
    y: float = 100,
    label: str | None = None,
    ls: str = ":",
    alpha: float = 0.4,
) -> None:
    """Add a horizontal reference line (e.g. par line at ``y=100``).

    Parameters
    ----------
    ax : Axes
        The axes to draw on.
    y : float
        Y-value for the horizontal line.
    label : str, optional
        Legend label.
    ls : str
        Line style (default ``":"`` dotted).
    alpha : float
        Line transparency.

    """
    ax.axhline(
        y,
        color=BOND_COLORS["reference"],
        ls=ls,
        alpha=alpha,
        label=label,
    )


# ---------------------------------------------------------------------------
# Standard plot helpers
# ---------------------------------------------------------------------------


def price_yield_curve(
    ax: Axes,
    yields: np.ndarray,
    prices: np.ndarray,
    label: str | None = None,
    color: str = BOND_COLORS["price_curve"],
    **kwargs: Any,
) -> None:
    """Plot a standardised price-yield curve.

    The yield values are automatically converted from decimal to percentage
    for display on the x-axis.

    Parameters
    ----------
    ax : Axes
        The axes to draw on.
    yields : np.ndarray
        Yield values as decimals (e.g. ``0.05`` for 5 %).
    prices : np.ndarray
        Corresponding bond prices.
    label : str, optional
        Legend label.
    color : str
        Line colour (default ``BOND_COLORS["price_curve"]``).
    **kwargs
        Additional keyword arguments forwarded to ``ax.plot``.

    """
    ax.plot(yields * 100, prices, color=color, label=label, **kwargs)
