# Walkthrough: Plotting Utilities Module

## Summary

Created a reusable `src/utils/plotting.py` module that extracts the repetitive
matplotlib boilerplate from the notebook into shared, standardised utilities.

## Changes

| File | Status | Description |
|---|---|---|
| `src/utils/plotting.py` | **New** | Core module — theme, colour palette, figure factories, formatting helpers, standard plot helpers |
| `src/utils/__init__.py` | Modified | Re-exports all public symbols from `plotting` |
| `tests/test_utils/test_plotting.py` | **New** | 18 unit tests covering all public API |
| `tests/test_utils/__init__.py` | **New** | Package marker |
| `pyproject.toml` | Modified | Added D101, D102 to test per-file ruff ignores |
| `notebooks/01-single-instrument-pricing-verification.ipynb` | Modified | Replaced `plt.rcParams[...]` with `set_theme()` call |

## Module API

- `set_theme()` — applies project-wide rcParams (dpi=120, font.size=10, etc.)
- `BOND_COLORS` — 8 named colours for consistent chart styling
- `FigureConfig` / `DEFAULT_CONFIG` — dataclass for layout parameters
- `figure()` / `subplots()` — figure factories with project defaults
- `finish_plot()` — grid, labels, title, legend, tight_layout in one call
- `reference_line()` — standardised `axhline` (par line at y=100)
- `price_yield_curve()` — standardised price-yield curve plot

## Verification

```
ruff check .      → All checks passed!
ruff format .     → already formatted
mypy src/         → Success: no issues found
pytest -v         → 34/34 passed (16 existing + 18 new)
```

## Notebook Impact

The notebook refactor is minimal (one line added, two removed) and
produces *identical* output — `set_theme()` sets exactly the same
`rcParams` as the original inline code.
