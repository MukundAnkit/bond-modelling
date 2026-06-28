# Implementation Plan: Module 3 — Discrete Term Structure (Bootstrapping)

## 1. Objective

Build a bootstrapping engine that extracts zero-coupon spot rates from a cross-section of par-valued sovereign bonds. This engine will serve as the discrete input to Module 4 (Nelson-Siegel continuous curve optimization).

## 2. Design Decisions

### 2.1. Coupon Frequency Handling

The MRD describes the algorithm using annual-pay logic (`z_1 = c_1`, then recursively solve for `z_2` ... `z_n`). Real Treasuries pay semi-annually, which requires interpolation at half-year coupon dates. The implementation will support both:

- **`freq=1` (annual)**: Clean textbook recursion — no interpolation needed.
- **`freq=2` (semi-annual)**: Coupon dates fall between annual maturity tenors; uses log-linear interpolation of discount factors to price intermediate cash flows.

### 2.2. Data Structures

- Input: two 1-D NumPy arrays — `maturities` (years) and `par_yields` (decimal), both sorted ascending.
- Output: `spot_rates` — same-length array of zero-coupon yields at each maturity.
- Internal: `discount_factors` array for fast interpolation.

### 2.3. Reuse of Existing Modules

- `src/instruments/bond.py` — **not used** directly (no single `Bond` instance for the curve); the bootstrap works on arrays.
- `src/instruments/pricing.py` — the `price()` function provides the mathematical foundation, but bootstrap solves its own PV equation for spot rates.

### 2.4. File Organization

| File | Purpose |
|---|---|
| `src/bootstrap/__init__.py` | Module docstring + public API exports |
| `src/bootstrap/bootstrap.py` | Core recursive bootstrapping algorithm |
| `src/bootstrap/interpolate.py` | Log-linear discount-factor interpolation (semi-annual support) |
| `tests/test_bootstrap/__init__.py` | Already exists |
| `tests/test_bootstrap/test_bootstrap.py` | Tests for spot-rate extraction |
| `tests/test_bootstrap/test_interpolate.py` | Tests for interpolation helpers |

## 3. Public API

```python
def bootstrap_spot_rates(
    maturities: np.ndarray,
    par_yields: np.ndarray,
    freq: int = 1,
) -> np.ndarray:
    """Extract zero-coupon spot rates from par yields.

    Parameters
    ----------
    maturities : np.ndarray
        1-D array of maturities in years, strictly increasing (e.g. [1, 2, 3, ..., 30]).
    par_yields : np.ndarray
        1-D array of par yields as decimals, same length as maturities.
    freq : int
        Coupon frequency (1 = annual, 2 = semi-annual).

    Returns
    -------
    np.ndarray
        Zero-coupon spot rates at each maturity, same length as inputs.
    """
```

## 4. Algorithm Detail

### 4.1. Annual (freq=1) — Textbook Recursion

Let `F = 100` (par), `P = 100` (trading at par), `c_i` = par yield at maturity `t_i`.

1. **Base case** (`i = 0`): `z_0 = c_0` (1Y spot = 1Y par yield).
2. **Recursion** (`i > 0`):
   ```
   known_pv = Σ_{j=0}^{i-1} [ (F * c_i) / (1 + z_j)^t_j ]
   remaining = F - known_pv
   z_i = [ (F * c_i + F) / remaining ]^(1/t_i) - 1
   ```

### 4.2. Semi-Annual (freq=2) — with Interpolation

Each bond at maturity `t_i` has `2*t_i` coupon dates at half-year increments. Coupon cash flows at half-year points need discount factors that are interpolated log-linearly from the known spot-rate grid.

- **Discount factor at known maturity**: `df(t) = 1 / (1 + z(t))^t`
- **Log-linear interpolation**: `ln(df(t))` is linearly interpolated between known grid points.
- **Solver**: For each maturity `t_i`, use the recursive formula with interpolated discount factors for intermediate coupons.

## 5. Interpolation Module

```python
def _interpolate_df(
    t_target: float,
    known_maturities: np.ndarray,
    known_spot_rates: np.ndarray,
) -> float:
    """Log-linear interpolation of discount factor at an arbitrary time."""
```

This remains a private helper inside `interpolate.py`, but exposed if needed.

## 6. Validation & Error Handling

- `maturities` must be strictly increasing, positive
- `par_yields` must be non-negative, same length as `maturities`
- `freq` must be 1 or 2
- Raise `ValueError` for invalid inputs
- Semi-annual case: reject maturities < 0.5 (first coupon needs 6mo spot)

## 7. Test Plan

### 7.1. Core Bootstrapping (annual)

| Test | Description |
|---|---|
| `test_flat_yield_curve` | All par yields = 5%; spot rates should equal 5% |
| `test_upward_sloping` | 1Y=4%, 2Y=5%, 3Y=6%; verify 2Y spot > 5% and 3Y spot > 6% |
| `test_downward_sloping` | 1Y=6%, 2Y=5%, 3Y=4%; verify 2Y spot < 5% and 3Y spot < 4% |
| `test_single_maturity` | Only 1Y bond; spot = par yield |
| `test_two_maturity` | 1Y=4%, 2Y=5%; spot_2 != 5% (coupon reinvestment effect) |
| `test_five_maturity` | Standard 5Y curve from textbook |
| `test_invalid_maturities` | Non-increasing → ValueError |
| `test_negative_yield` | Par yield = -0.01 → valid (negative rates) |
| `test_zero_coupon_curve` | All par yields = 0%; spot = 0% |

### 7.2. Semi-Annual Bootstrapping

| Test | Description |
|---|---|
| `test_semi_flat_yield_curve` | All par yields = 5%, freq=2; spot rates near 5% |
| `test_semi_consistency_with_annual` | Flat curve; freq=2 spot rates match analytical expectation |
| `test_semi_two_maturity` | 1Y=4%, 2Y=5%, freq=2; verify recursive logic holds |

### 7.3. Interpolation

| Test | Description |
|---|---|
| `test_interpolate_exact_match` | Interpolation at known grid points returns exact value |
| `test_interpolate_between` | Log-linear interpolation between two points |
| `test_interpolate_extrapolate_short` | t < shortest maturity (forward-fill nearest) |
| `test_interpolate_empty_input` | Single-point grid works |

## 8. Verification Notebook

Create `notebooks/03-bootstrapping-verification.ipynb` with:
- Textbook example: Bootstrapping from Fabozzi or Tuckman
- Plot of par yield curve vs. bootstrapped spot curve
- Comparison with manually computed spot rates

## 9. Execution Order (per AGENTS.md workflow)

Phase B — Test Generation:
1. Write `tests/test_bootstrap/test_interpolate.py`
2. Write `tests/test_bootstrap/test_bootstrap.py`
3. Run `uv run pytest` → confirm failures (TDD)

Phase C — Implementation:
4. Implement `src/bootstrap/interpolate.py`
5. Implement `src/bootstrap/bootstrap.py`
6. Update `src/bootstrap/__init__.py` with exports
7. Run `uv run pytest` → confirm all pass
8. Run `ruff check . && ruff format . --check && mypy src/` → all green
9. Create `notebooks/03-bootstrapping-verification.ipynb`
10. Git commit on feature branch `feat/module3-bootstrap` with passing build

Phase D — Handoff to Human:
11. Write `docs/walkthrough.md`
12. Human reviews, squash-merges to `dev`, updates `docs/project_status.md`
