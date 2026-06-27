# Project Status

> Last updated: 2026-06-27

---

## Environment

| Item | Detail |
|---|---|
| Python | 3.12.13 |
| Package manager | uv 0.11.25 |
| Virtual env | `.venv/` |
| Core deps | numpy, scipy, pandas |
| Dev deps | pytest, pytest-cov, jupyter, pandas-datareader, yfinance, requests |

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
│   ├── project_plan.md         # MRD — full specification
│   └── project_status.md       # This file — current state
├── src/
│   ├── module1_pricing/        # Module 1 — COMPLETE
│   │   ├── __init__.py
│   │   ├── bond.py             #   Bond dataclass
│   │   ├── pricing.py          #   Price calculator (PV of cash flows)
│   │   └── ytm_solver.py       #   YTM solver (Newton + bisection)
│   ├── module2_risk/           # Module 2 — not started
│   ├── module3_bootstrap/      # Module 3 — not started
│   ├── module4_nelsonsiegel/   # Module 4 — not started
│   ├── data/                   # Data source fetchers — not started
│   └── utils/                  # Shared helpers — empty
├── tests/
│   ├── __init__.py
│   ├── test_module1_pricing/   # Module 1 tests — 16 passing
│   │   ├── __init__.py
│   │   ├── test_pricing.py     #   9 tests
│   │   └── test_ytm_solver.py  #   7 tests
│   ├── test_module2_risk/      # empty (scaffold)
│   ├── test_module3_bootstrap/ # empty (scaffold)
│   └── test_module4_nelsonsiegel/ # empty (scaffold)
└── notebooks/
    └── verification_module1.ipynb  # Textbook verification notebook
```

---

## Version Control

| Item | Detail |
|---|---|
| Remote | `https://github.com/MukundAnkit/bond-modelling.git` |
| Branches | `main` (empty), `dev` (active) |
| Workflow | Feature branches (`feat/*`) → PR → `dev` → PR → `main` |
| CI | GitHub Actions — runs `uv run pytest` on push/PR to `dev` or `main` |
| PR template | Checklist with type tags + verification steps |

---

## Module Progress

| Module | Status | Details |
|---|---|---|
| 1 — Single Instrument Pricing | **Complete** | Bond dataclass, price(), YTM solver with Newton-Raphson + bisection fallback. Tolerance $10^{-6}$. Verified via 16 passing tests. |
| 2 — Risk Sensitivity | Not started | Duration & Convexity |
| 3 — Discrete Term Structure | Not started | Bootstrapping |
| 4 — Continuous Curve Optimization | Not started | Nelson-Siegel |

---

## Module 1 — Implementation Details

### `Bond` dataclass (`src/module1_pricing/bond.py`)
- Fields: `face_value`, `coupon_rate`, `maturity`, `freq` (default 2)
- Properties: `periods` (= maturity × freq), `coupon_payment` (= face × coupon / freq)
- Validation: rejects negative/zero face value, negative coupon, non-positive maturity, invalid freq (must be 1, 2, 4, or 12)

### `price()` (`src/module1_pricing/pricing.py`)
- Vectorized PV computation using numpy
- Formula: $P = \sum_{t=1}^{T \times m} \frac{C/m}{(1 + y/m)^t} + \frac{F}{(1 + y/m)^{T \times m}}$

### YTM Solvers (`src/module1_pricing/ytm_solver.py`)
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

1. ~~Module 1 (complete)~~
2. **Module 2**: Duration & Convexity — implement Macaulay Duration, Modified Duration, Convexity, shock simulation
3. Module 3: Bootstrapping
4. Module 4: Nelson-Siegel

Each module must be back-tested against established financial calculators before the next begins.
