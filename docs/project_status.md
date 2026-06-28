# Project Status

> Last updated: 2026-06-28 (v0.1.1 — Plotting utils added, Module 1 refined)

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
│   ├── risk/           # Duration & Convexity — scaffold (empty __init__.py)
│   ├── bootstrap/      # Bootstrapping — not started
│   ├── curve/   # Nelson-Siegel curve — not started
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
│   ├── test_risk/      # scaffold (empty)
│   ├── test_bootstrap/ # scaffold (empty)
│   └── test_nelsonsiegel/ # scaffold (empty)
└── notebooks/
    └── 01-single-instrument-pricing-verification.ipynb  # Textbook verification notebook
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

---

## Module Progress

| Module | Status | Details |
|---|---|---|---|
| Instruments (Pricing & YTM) | **Complete** | Bond dataclass, price(), YTM solver with Newton-Raphson + bisection fallback. Tolerance $10^{-6}$. Verified via 16 passing tests. |
| Utils (Plotting) | **Complete** | `set_theme()`, `BOND_COLORS`, `FigureConfig`, `figure()`, `subplots()`, `finish_plot()`, `reference_line()`, `price_yield_curve()`. 18 tests. |
| Risk (Sensitivity) | **Next →** | Duration & Convexity — scaffold ready |
| Bootstrap (Term Structure) | Not started | Bootstrapping |
| Curve (Optimization) | Not started | Nelson-Siegel |

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

### Test Results

```
16 passed in 0.06s
```

- Bond validation: creation, rejected invalid inputs (4 tests)
- Pricing: par, premium, discount, zero-coupon (4 tests)
- YTM solvers: Newton (par/premium/discount), bisection, combined solver, zero-coupon, not-bracketed error (7 tests)

---

## Next Steps

Per the Execution Protocol in the MRD, development must proceed in order:

1. ~~Instruments (Pricing & YTM — complete)~~
2. **Risk**: Duration & Convexity — implement Macaulay Duration, Modified Duration, Convexity, shock simulation
3. Bootstrap: Bootstrapping
4. Curve: Nelson-Siegel

Each module must be back-tested against established financial calculators before the next begins.
