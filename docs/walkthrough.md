# Walkthrough: Module 3 — Discrete Term Structure (Bootstrapping)

## Summary

Implemented the bootstrapping engine that extracts zero-coupon spot rates
from a par yield curve. This is the discrete input needed by Module 4
(Nelson-Siegel continuous curve optimization).

## Files Changed

| File | Action | Purpose |
|---|---|---|
| `src/bootstrap/bootstrap.py` | **Created** | Core recursive algorithm |
| `src/bootstrap/interpolate.py` | **Created** | Log-linear discount-factor interpolation |
| `src/bootstrap/__init__.py` | Modified | Public API export |
| `tests/test_bootstrap/test_bootstrap.py` | **Created** | 18 tests for spot-rate extraction |
| `tests/test_bootstrap/test_interpolate.py` | **Created** | 8 tests for interpolation |
| `notebooks/03-bootstrapping-verification.ipynb` | **Created** | Textbook verification notebook |
| `docs/implementation_plan.md` | **Created** | Plan document |
| `docs/project_status.md` | Modified | Updated status |

## Test Results

```
122 passed in 0.43s
```

Breakdown:
- test_bootstrap: 18 tests (annual flat/sloping, error handling, semi-annual)
- test_interpolate: 8 tests (exact match, between points, forward-fill)
- + 96 existing tests from Modules 1-2

## Lint & Type Check

```
ruff check .       → All checks passed!
ruff format --check → 40 files already formatted
mypy src/          → Success: no issues found
```

## Verification Notebook

`notebooks/03-bootstrapping-verification.ipynb` includes:
- Textbook 5Y upward-sloping curve bootstrapping
- Re-pricing verification: all par bonds reprice to 100 using the spot curve
- Semi-annual curve comparison
- Flat curve validation
- Visual comparison: par yields vs. annual spot vs. semi-annual spot

## Commit

```
9da0f7c feat: add Module 3 bootstrap spot-rate extraction
```
