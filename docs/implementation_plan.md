# Implementation Plan: Reusable Plotting Utilities

## Goal

Extract the repetitive matplotlib boilerplate from the notebook into a shared `src/utils/plotting.py` module. This standardises figure style, colour palette, and common chart patterns across the project (Module 1 notebook and future modules).

## Current State

`src/utils/` is an empty stub (only `__init__.py`). Every figure in `01-single-instrument-pricing-verification.ipynb` duplicates:

```python
plt.rcParams["figure.dpi"] = 120
plt.rcParams["font.size"] = 10
fig, ax = plt.subplots(figsize=(8, 4))
ax.set_xlabel("..."); ax.set_ylabel("..."); ax.set_title("...")
ax.legend(fontsize=9); ax.grid(alpha=0.3)
plt.tight_layout(); plt.show()
```

9 figure blocks across the notebook, all with near-identical setup.

## Proposed Module Structure

### `src/utils/plotting.py`

| Item | Description |
|---|---|
| `set_theme()` | Apply project-wide `rcParams` (dpi, font size, LaTeX, colour cycle) |
| `BOND_COLORS` dict | Named palette for instrument types |
| `figure(*args, **kwargs)` | Thin wrapper around `plt.subplots` with default `figsize=(8, 4)` |
| `subplots(*args, **kwargs)` | Thin wrapper for multi-axes layouts, default `figsize=(10, 4)` |
| `finish_plot(ax, ...)` | Apply grid, tight_layout, optional legend/title in one call |
| `price_yield_curve(ax, yields, prices, **kwargs)` | Standardised price-yield line plot |
| `reference_line(ax, y, **kwargs)` | Standardised par/reference `axhline` |

### `src/utils/__init__.py`

Re-export `set_theme`, `BOND_COLORS`, `figure`, `subplots`, `finish_plot`.

### Test file: `tests/test_utils/test_plotting.py`

Verify that:
- `set_theme()` sets expected rcParams
- `figure()` returns valid fig/ax with default figsize
- `subplots()` returns valid fig/axes with expected layout
- `finish_plot()` adds grid, tight_layout without error
- `BOND_COLORS` contains expected keys

## Colour Palette

```python
BOND_COLORS = {
    "price_curve": "#e74c3c",       # red — price-yield curve
    "coupon_bar": "#2ecc71",        # green — coupon payment bars
    "face_bar": "#3498db",          # blue — face value bar
    "solver": "#e67e22",            # orange — Newton trace
    "solver_error": "#c0392b",      # dark red — error trace
    "bisection": "#2980b9",         # blue — bisection trace
    "zero_coupon": "#9b59b6",       # purple — zero-coupon curve
    "reference": "gray",            # gray — par line / ref line
}
```

## Changes to the Notebook

After implementation, the notebook will import `set_theme` and call it in Cell 1 instead of manual `plt.rcParams`. Individual cells can optionally use `figure()` / `subplots()` and `finish_plot()`. **This notebook update will happen only if explicitly requested** — the plan delivery is the `plotting.py` module + test.

## Files Changed

| File | Change |
|---|---|
| `src/utils/__init__.py` | Add exports |
| `src/utils/plotting.py` | **New** — core module |
| `tests/test_utils/test_plotting.py` | **New** — unit tests |

## Verification

- `ruff check .` — no warnings
- `mypy src/` — no type errors
- `pytest -v --tb=short` — all tests pass (including new ones)
