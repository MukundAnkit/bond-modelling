# Walkthrough — Module 2: Risk & Sensitivity

**Branch**: `feat/risk-duration-convexity`  
**Commit**: `b26c697`

## Summary

Implemented Macaulay Duration, Modified Duration, Convexity, interest-rate shock simulation, Effective Duration/Convexity, and Basel IRBB stress scenarios for fixed-rate bonds.

### Source Files

| File | Exports | Description |
|------|---------|-------------|
| `src/risk/duration.py` | `macaulay_duration`, `modified_duration` | Weighted-average time to cash flows; first-derivative sensitivity |
| `src/risk/convexity.py` | `convexity` | Second-derivative curvature measure |
| `src/risk/shock.py` | `price_shock`, `shocked_price` | Taylor expansion: ΔP ≈ -ModD·P·Δy + ½·Cx·P·(Δy)² |
| `src/risk/effective.py` | `effective_duration`, `effective_convexity` | Central-difference numerical duration/convexity for bonds with embedded options |
| `src/risk/stress.py` | `irbb_stress_scenarios`, `irbb_shock_vector` | Basel IRBB 6-scenario EVE stress framework (parallel ±100bp, steepener, flattener, short rate ±300bp) |

### Test Files

| File | Tests |
|------|-------|
| `tests/test_risk/test_duration.py` | 13 tests |
| `tests/test_risk/test_convexity.py` | 9 tests |
| `tests/test_risk/test_shock.py` | 10 tests |
| `tests/test_risk/test_effective.py` | 8 tests |
| `tests/test_risk/test_stress.py` | 9 tests |

**Total new tests**: 49 (15 added this session)

### Key Test Coverage

- **Mathematical cross-checks**: ZCB Macaulay Duration = maturity (annual + semi-annual); ZCB Modified Duration = T/(1+y); ZCB convexity closed-form verification
- **Numerical differentiation**: Modified Duration and Convexity verified against central difference approximations
- **Relationships**: Higher coupon → lower duration/convexity; longer maturity → higher duration/convexity; ModD = MacD / (1 + y/m)
- **Edge cases**: yield = 0, negative yields, single-period bonds, zero-coupon bonds
- **Shock simulation**: Δy = 0 → ΔP = 0; sign correctness; asymmetric gain/loss due to convexity; 1bp Taylor ≈ exact repricing; 100bp error < 0.5%
- **Effective measures**: effective duration converges to modified duration within 1e-5 for vanilla bonds; effective convexity matches analytical convexity; small-bump reduces numerical error; correct handling of zero and negative yields
- **Stress scenarios**: all 6 Basel scenarios returned; correct P&L sign (parallel up → loss, parallel down → gain); exact repricing match for parallel shocks via `shocked_price`; steepener penalises long bonds more than short; flattener has opposite effect; short-rate symmetric for par bonds

### Verification Results

```
pytest: 96 passed (49 new + 47 existing) — no regressions
ruff:   clean
mypy:   Success: no issues found in 18 source files
```

### API Surface

```python
def macaulay_duration(bond: Bond, yield_rate: float) -> float
def modified_duration(bond: Bond, yield_rate: float) -> float
def convexity(bond: Bond, yield_rate: float) -> float
def price_shock(bond: Bond, yield_rate: float, delta_y: float) -> float
def shocked_price(bond: Bond, yield_rate: float, delta_y: float) -> float
def effective_duration(bond: Bond, yield_rate: float, bump: float = 0.0001) -> float
def effective_convexity(bond: Bond, yield_rate: float, bump: float = 0.0001) -> float
def irbb_shock_vector(scenario: str, tenors: NDArray[np.float64]) -> NDArray[np.float64]
def irbb_stress_scenarios(bond: Bond, yield_rate: float) -> dict[str, dict[str, float]]
```

All functions use NumPy-vectorized cash-flow summation for numerical stability and accept any valid `Bond` instance.
