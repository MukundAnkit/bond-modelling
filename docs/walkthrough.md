# Walkthrough — Module 2: Risk & Sensitivity

**Branch**: `feat/risk-duration-convexity`  
**Commit**: `68492fe`

## Summary

Implemented Macaulay Duration, Modified Duration, Convexity, and interest-rate shock simulation for fixed-rate bonds.

### Source Files

| File | Exports | Description |
|------|---------|-------------|
| `src/risk/duration.py` | `macaulay_duration`, `modified_duration` | Weighted-average time to cash flows; first-derivative sensitivity |
| `src/risk/convexity.py` | `convexity` | Second-derivative curvature measure |
| `src/risk/shock.py` | `price_shock`, `shocked_price` | Taylor expansion: ΔP ≈ -ModD·P·Δy + ½·Cx·P·(Δy)² |

### Test Files

| File | Tests |
|------|-------|
| `tests/test_risk/test_duration.py` | 13 tests |
| `tests/test_risk/test_convexity.py` | 9 tests |
| `tests/test_risk/test_shock.py` | 10 tests |

**Total new tests**: 32

### Key Test Coverage

- **Mathematical cross-checks**: ZCB Macaulay Duration = maturity (annual + semi-annual); ZCB Modified Duration = T/(1+y); ZCB convexity closed-form verification
- **Numerical differentiation**: Modified Duration and Convexity verified against central difference approximations
- **Relationships**: Higher coupon → lower duration/convexity; longer maturity → higher duration/convexity; ModD = MacD / (1 + y/m)
- **Edge cases**: yield = 0, negative yields, single-period bonds, zero-coupon bonds
- **Shock simulation**: Δy = 0 → ΔP = 0; sign correctness; asymmetric gain/loss due to convexity; 1bp Taylor ≈ exact repricing; 100bp error < 0.5%

### Verification Results

```
pytest: 66 passed (32 new + 34 existing) — no regressions
ruff:   clean
mypy:   Success: no issues found in 14 source files
```

### API Surface

```python
def macaulay_duration(bond: Bond, yield_rate: float) -> float
def modified_duration(bond: Bond, yield_rate: float) -> float
def convexity(bond: Bond, yield_rate: float) -> float
def price_shock(bond: Bond, yield_rate: float, delta_y: float) -> float
def shocked_price(bond: Bond, yield_rate: float, delta_y: float) -> float
```

All functions use NumPy-vectorized cash-flow summation for numerical stability and accept any valid `Bond` instance.
