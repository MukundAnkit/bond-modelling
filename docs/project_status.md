# Project Status

> Last updated: 2026-06-28 (v0.3.0 — Module 4: Curve optimization complete)

---

## Environment

| Item | Detail |
|---|---|
| Python | 3.12.13 |
| Package manager | uv 0.11.25 |
| Virtual env | `.venv/` |
| Core deps | numpy, scipy, pandas |
| Dev deps | pytest, pytest-cov, ruff, mypy, jupyter, pandas-datareader, yfinance, requests |

---

## Project Structure

```
bond_modelling/
├── pyproject.toml              # Project config & dependencies
├── .editorconfig               # Editor consistency rules
├── .gitignore
├── .python-version
├── LICENSE                     # MIT license
├── README.md                   # Project description & usage
├── uv.lock                     # Locked dependency tree
├── .github/
│   ├── workflows/
│   │   └── ci.yml              # GitHub Actions — auto-run tests on push/PR
│   └── pull_request_template.md
├── docs/
│   ├── project_plan.md            # MRD — full specification
│   ├── project_status.md          # This file — current state
│   └── development_workflow.md    # Branching, commits, PR practices
├── src/
│   ├── instruments/        # Pricing & YTM — COMPLETE
│   │   ├── __init__.py
│   │   ├── bond.py             #   Bond dataclass
│   │   ├── pricing.py          #   Price calculator (PV of cash flows)
│   │   └── ytm_solver.py       #   YTM solver (Newton + bisection)
│   ├── risk/               # Risk & Sensitivity — COMPLETE
│   │   ├── __init__.py
│   │   ├── duration.py         #   Macaulay & Modified Duration
│   │   ├── convexity.py        #   Convexity (second derivative)
│   │   ├── shock.py            #   Taylor-series shock simulation
│   │   ├── dollar_measures.py  #   Dollar Duration, DV01, Dollar Convexity
│   │   ├── effective.py        #   Effective Duration & Convexity (yield-curve bumping)
│   │   ├── key_rate_duration.py#   Key Rate Duration (non-parallel shifts)
│   │   └── stress.py           #   Basel IRBB non-parallel stress scenarios
│   ├── bootstrap/      # Bootstrapping — COMPLETE
│   │   ├── __init__.py
│   │   ├── bootstrap.py        #   Recursive spot-rate bootstrapping
│   │   └── interpolate.py      #   Log-linear discount-factor interpolation
│   ├── curve/          # Nelson-Siegel curve — COMPLETE
│   │   ├── __init__.py
│   │   └── nelson_siegel.py    #   Nelson-Siegel curve model & optimizer
│   ├── data/                   # Data source fetchers — not started
│   └── utils/                  # Shared helpers — plotting.py added
├── tests/
│   ├── __init__.py
│   ├── test_pricing/   # Pricing tests — 16 passing
│   │   ├── __init__.py
│   │   ├── test_pricing.py     #   9 tests
│   │   └── test_ytm_solver.py  #   7 tests
│   ├── test_utils/     # Utils tests — 18 passing
│   │   ├── __init__.py
│   │   └── test_plotting.py    #  18 tests
│   ├── test_risk/      # Risk tests — 62 passing
│   │   ├── __init__.py
│   │   ├── test_duration.py         #  14 tests
│   │   ├── test_convexity.py        #   9 tests
│   │   ├── test_shock.py            #   9 tests
│   │   ├── test_dollar_measures.py  #   8 tests
│   │   ├── test_effective.py        #   8 tests
│   │   ├── test_key_rate_duration.py#   5 tests
│   │   └── test_stress.py           #   9 tests
│   ├── test_bootstrap/ # Bootstrap tests — 26 passing
│   │   ├── __init__.py
│   │   ├── test_bootstrap.py      #  18 tests
│   │   └── test_interpolate.py    #   8 tests
│   └── test_nelsonsiegel/ # Nelson-Siegel tests — 8 passing
│       ├── __init__.py
│       └── test_nelson_siegel.py  #   8 tests
└── notebooks/
    ├── 01-single-instrument-pricing-verification.ipynb  # Textbook verification notebook
    ├── 02-risk-sensitivity-verification.ipynb           # Duration & convexity notebook
    ├── 03-bootstrapping-verification.ipynb               # Bootstrapping verification notebook
    └── 04-nelson-siegel-verification.ipynb              # Nelson-Siegel verification notebook
```

---

## Version Control

| Item | Detail |
|---|---|
| Remote | `https://github.com/MukundAnkit/bond-modelling.git` |
| Branches | `main` (`v0.1.0`), `dev` (active) |
| Workflow | Feature branches (`feat/*`) → PR → `dev` → release PR → `main` (tagged) |
| CI | GitHub Actions — runs `ruff check`, `ruff format --check`, `mypy src/`, `pytest` on push/PR to `dev` or `main` |
| PR template | Checklist with type tags + verification steps |
| Workflow guide | See [`docs/development_workflow.md`](development_workflow.md) |
| Latest release | [`v0.1.0`](https://github.com/MukundAnkit/bond-modelling/releases/tag/v0.1.0) — Module 1: Single Instrument Pricing |
| Latest tag (unreleased) | `v0.2.0` — Module 2: Risk & Sensitivity (on `dev`) |

---

## Module Progress

| Module | Status | Details |
|---|---|---|
| Instruments (Pricing & YTM) | **Complete** | Bond dataclass, price(), YTM solver with Newton-Raphson + bisection fallback. Tolerance $10^{-6}$. |
| Utils (Plotting) | **Complete** | `set_theme()`, `BOND_COLORS`, `FigureConfig`, `figure()`, `subplots()`, `finish_plot()`, `reference_line()`, `price_yield_curve()`. |
| Risk (Sensitivity) | **Complete** | Macaulay/Modified Duration, Convexity, Taylor-series shock, Dollar Duration/DV01, Effective D/C, Key Rate Duration, Basel IRBB stress scenarios. |
| Bootstrap (Term Structure) | **Complete** | Recursive bootstrapping (annual + semi-annual), log-linear discount-factor interpolation. 26 tests. |
| Curve (Optimization) | **Complete** | Nelson-Siegel continuous parametric curve optimization via multi-start Nelder-Mead. 8 tests. |

---

## Instruments — Implementation Details

### `Bond` dataclass (`src/instruments/bond.py`)
- Fields: `face_value`, `coupon_rate`, `maturity`, `freq` (default 2)
- Properties: `periods` (= maturity × freq), `coupon_payment` (= face × coupon / freq)
- Validation: rejects negative/zero face value, negative coupon, non-positive maturity, invalid freq (must be 1, 2, 4, or 12)

### `price()` (`src/instruments/pricing.py`)
- Vectorized PV computation using numpy
- Formula: $P = \sum_{t=1}^{T \times m} \frac{C/m}{(1 + y/m)^t} + \frac{F}{(1 + y/m)^{T \times m}}$

### YTM Solvers (`src/instruments/ytm_solver.py`)
- **Newton-Raphson** (`ytm_newton`): Uses numerical derivative (central difference), default guess 5%, max 500 iterations
- **Bisection** (`ytm_bisection`): Brackets between -5% and +50%, 500 max iterations
- **Combined** (`ytm_solver`): Tries Newton first, falls back to bisection on failure
- Tolerance: $10^{-6}$

---

## Risk — Implementation Details

### Duration (`src/risk/duration.py`)
- `macaulay_duration()`: Time-weighted PV of cash flows divided by full price
- `modified_duration()`: Macaulay Duration / (1 + y/m)

### Convexity (`src/risk/convexity.py`)
- `convexity()`: Second derivative of price w.r.t. yield

### Shock Simulation (`src/risk/shock.py`)
- `price_shock()`: $\Delta P \approx -ModD \cdot P \cdot \Delta y + \frac{1}{2} \cdot Cx \cdot P \cdot (\Delta y)^2$
- Supports single shock or vector of shocks

### Dollar Measures (`src/risk/dollar_measures.py`)
- `dollar_duration()`: $DD = ModD \cdot P$
- `dv01()`: $DV01 = DD \cdot 0.0001$
- `dollar_convexity()`: $DC = Cx \cdot P$

### Effective Duration & Convexity (`src/risk/effective.py`)
- `effective_duration()`: $\frac{P_{-\Delta y} - P_{+\Delta y}}{2 \cdot P_0 \cdot \Delta y}$
- `effective_convexity()`: $\frac{P_{-\Delta y} + P_{+\Delta y} - 2P_0}{P_0 \cdot (\Delta y)^2}$
- Uses yield-curve bumping (parallel shift)

### Key Rate Duration (`src/risk/key_rate_duration.py`)
- `key_rate_duration()`: Sensitivity to non-parallel shifts at specific tenors
- Interpolates key rate shocks across the cash-flow timeline

### Basel IRBB Stress (`src/risk/stress.py`)
- Six non-parallel stress scenarios: Parallel Short, Parallel Long, Steepener, Flattener, Short Rate, Long Rate
- `stress_scenarios()`: Returns shocked yield curves for all six regimes
- `stress_pnl()`: Revalues bond under each scenario and computes P&L

---

## Bootstrap — Implementation Details

### `bootstrap_spot_rates()` (`src/bootstrap/bootstrap.py`)
- Recursive algorithm: first spot rate = first par yield, then strips coupons sequentially
- Supports annual (`freq=1`) and semi-annual (`freq=2`) coupon payments
- Semi-annual case uses log-linear discount-factor interpolation for intermediate cash flows

### `interpolate_df()` (`src/bootstrap/interpolate.py`)
- Log-linear interpolation of discount factors between known spot-rate grid points
- Forward-fill for target times outside the grid (uses nearest spot rate)

---

## Curve — Implementation Details

### `NelsonSiegelCurve` (`src/curve/nelson_siegel.py`)
- Properties & aliases: `beta0`, `beta1`, `beta2`, `tau` (and aliases `level`, `slope`, `curvature`, `decay`)
- Evaluation: `yield_rate(t)` and `__call__(t)` with support for scalar/vector inputs and limit calculation at $t \to 0$
- SSE calculation: `sse(maturities, spot_rates)`
- Optimization: `fit(maturities, spot_rates)` runs multi-start Nelder-Mead on candidate $\tau$ initial values `[0.5, 1.0, 2.0, 5.0, 10.0]` to guarantee convergence, with bound enforcement ($\beta_0 \ge 10^{-6}$, $\tau \ge 10^{-6}$)

---

## Test Results

```
130 passed in 0.77s
```

| Test suite | Tests | Key coverage |
|---|---|---|
| `test_pricing` | 16 | Bond validation, pricing (par/premium/discount/zero), YTM solvers |
| `test_utils` | 18 | Plotting config, figure creation, price-yield curves |
| `test_risk` | 62 | Duration, convexity, shock, dollar measures, effective D/C, key rate duration, stress |
| `test_bootstrap` | 26 | Annual/semi-annual bootstrapping, interpolation, error handling |
| `test_nelsonsiegel` | 8 | Evaluation (scalar/vector), limits at t=0, SSE, heuristic/parameter-recovery fit, bound enforcement |

---

## Next Steps

Per the Execution Protocol in the MRD, development must proceed in order:

1. ~~Instruments (Pricing & YTM — complete)~~
2. ~~Risk (Sensitivity — complete)~~
3. ~~Bootstrap (Term Structure — complete)~~
4. ~~Curve (Continuous Optimization — complete)~~

Next Steps: Data Source Fetchers (FRED, Yahoo Finance, FINRA) integration and pipeline setup.
