# Project Status

> Last updated: 2026-09-20

---

## Environment

| Item | Detail |
|---|---|
| Python | 3.12.x |
| Package manager | uv |
| Virtual env | `.venv/` |
| Core deps | numpy, scipy, pandas |
| Dev deps | pytest, pytest-cov, ruff, mypy, jupyter, pandas-datareader, yfinance, requests |

---

## Project Structure

```
bond_modelling/
├── pyproject.toml              # Project config & dependencies (version 1.0.0)
├── .editorconfig               # Editor consistency rules
├── .gitignore
├── .python-version
├── LICENSE                     # MIT license
├── README.md                   # Project description & usage
├── uv.lock                     # Locked dependency tree
├── .github/
│   ├── workflows/
│   │   ├── ci.yml               # GitHub Actions — lint/typecheck/tests on push/PR
│   │   └── release.yml          # GitHub Actions — tag-triggered release build + publish
│   └── pull_request_template.md
├── docs/
│   └── project_status.md        # This file — current state
├── src/
│   ├── instruments/             # Bond definitions, pricing, YTM solvers
│   ├── risk/                    # Duration, convexity, dollar measures, stress
│   ├── bootstrap/               # Discrete term-structure bootstrapping
│   ├── curve/                   # Nelson-Siegel curve, PCA
│   ├── derivatives/             # Swaps, caps/floors, swaptions (Vasicek & Black)
│   ├── data/                    # FRED, Treasury, yfinance, FINRA fetchers + validation
│   ├── models/                  # Vasicek/CIR, Monte Carlo simulation, calibration
│   ├── portfolio/               # Positions, aggregation, portfolio stress
│   ├── credit/                  # Hazard rates, Merton, single-name CDS
│   ├── mbs/                     # Prepayment CPR/SMM, pass-throughs, OAS
│   ├── trees/                   # Trinomial & Hull-White lattices
│   ├── inflation/               # TIPS, real vs nominal curves
│   ├── structured/              # Copulas, tranches, synthetic CDOs
│   ├── exotics/                 # LMM, CMS, TARNs
│   ├── xva/                     # Exposure simulation, CVA/DVA/FVA/KVA
│   └── utils/                   # Plotting & caching helpers
├── tests/
│   ├── test_pricing/            # 51 tests
│   ├── test_risk/               # 66 tests
│   ├── test_bootstrap/          # 28 tests
│   ├── test_curve/              # 11 tests
│   ├── test_nelsonsiegel/       # 8 tests
│   ├── test_portfolio/          # 11 tests
│   ├── test_data/               # 15 tests
│   ├── test_utils/              # 21 tests
│   ├── test_models/             # 13 tests
│   ├── test_derivatives/        # 11 tests
│   ├── test_credit/             # 12 tests
│   ├── test_mbs/                # 11 tests
│   ├── test_trees/              # 6 tests
│   ├── test_inflation/          # 9 tests
│   ├── test_structured/         # 9 tests
│   ├── test_exotics/            # 6 tests
│   └── test_xva/                # 7 tests
├── notebooks/                   # Module verification notebooks (01–16)
└── output/                      # Consolidated executed outputs (html/ipynb)
```

---

## Version Control

| Item | Detail |
|---|---|
| Remote | `https://github.com/MukundAnkit/bond-modelling.git` |
| Branches | `main` (releases, currently `v1.0.0`), `dev` (active integration) |
| Workflow | Feature branches (`feat/*`) → PR → `dev` → PR → `main` (tagged) |
| CI | GitHub Actions — runs `ruff check`, `ruff format --check`, `mypy src/`, `pytest` on push/PR to `dev` or `main` |
| Release | Pushing a `v*` tag to `main` triggers `release.yml` (verify → `uv build` → GitHub Release with wheel/sdist + generated notes) |
| PR template | Checklist with type tags + verification steps |
| Latest release | [`v1.0.0`](https://github.com/MukundAnkit/bond-modelling/releases/tag/v1.0.0) — full 16-module engine |

---

## Module Progress

| Module | Status | Details |
|---|---|---|
| Instruments (Pricing & YTM) | **Complete** | Bond dataclass, price(), YTM solver with Newton-Raphson + bisection fallback. Tolerance $10^{-6}$. |
| Utils (Plotting) | **Complete** | `set_theme()`, `BOND_COLORS`, `FigureConfig`, `figure()`, `subplots()`, `finish_plot()`, `reference_line()`, `price_yield_curve()`. |
| Risk (Sensitivity) | **Complete** | Macaulay/Modified Duration, Convexity, Taylor-series shock, Dollar Duration/DV01, Effective D/C, Key Rate Duration, Basel IRBB stress scenarios. |
| Bootstrap (Term Structure) | **Complete** | Recursive bootstrapping (annual + semi-annual), log-linear discount-factor interpolation. 28 tests. |
| Curve (Optimization) | **Complete** | Nelson-Siegel continuous parametric curve optimization via multi-start Nelder-Mead. 8 tests. |
| Portfolio (Aggregation) | **Complete** | Position and Portfolio classes, MV-weighted duration/convexity, DV01, KRD vectors, and Basel stress testing. 11 tests. |
| Caching & Validation | **Complete** | JSONCache with TTL validation, cross_validate_yields comparing FRED vs yfinance. |
| Data Integrations | **Complete** | FredFetcher, TreasuryFetcher, YFinanceFetcher, and FINRA mocks. 15 tests. |
| Stochastic Models | **Complete** | PCA curve extraction, Vasicek/CIR models, calibration, Monte Carlo paths. 13 tests. |
| Derivatives | **Complete** | Vanilla Swaps, Caps, Floors, Swaptions using Vasicek analytical and Black (1976) models. 11 tests. |
| Credit Risk & CDS | **Complete** | Hazard rate calibration, structural (Merton) models, and single-name CDS pricing. 12 tests. |
| MBS & Prepayment | **Complete** | CPR/SMM prepayment modeling, pass-through cash flows, Option-Adjusted Spread (OAS). 11 tests. |
| Advanced Trees | **Complete** | Trinomial trees, Hull-White lattice, Bermudan swaption pricing. 6 tests. |
| Inflation Bonds | **Complete** | TIPS, real vs. nominal curves, and break-even inflation calculations. 9 tests. |
| Value at Risk (VaR) | **Complete** | Historical, Parametric, and Monte Carlo VaR & Expected Shortfall computation. |
| Structured Products | **Complete** | Gaussian/Student-t Copulas, Tranche loss (Equity/Mezz/Senior), Synthetic CDO/CLO pricing. 9 tests. |
| Interest Rate Exotics | **Complete** | LIBOR Market Model (LMM/BGM), Constant Maturity Swaps (CMS), Target Redemption Notes (TARNs). 6 tests. |
| XVA & Counterparty Risk | **Complete** | EE/PFE exposure simulation, Credit Valuation Adjustment (CVA), Debt (DVA), Funding (FVA), KVA. 7 tests. |

---

## Instruments — Implementation Details

### `Bond` dataclass (`src/instruments/bond.py`)
- Fields: `face_value`, `coupon_rate`, `maturity`, `freq` (default 2)
- Properties: `periods` (= maturity × freq), `coupon_payment` (= face × coupon / freq)
- Validation: rejects negative/zero face value, negative coupon, non-positive maturity, invalid freq (must be 1, 2, 4, or 12)

### `price()` (`src/instruments/pricing.py`)
- Vectorized PV computation using numpy
- Formula: $P = \sum_{t=1}^{T \times m} \frac{C/m}{(1 + y/m)^t} + \frac{F}{(1 + y/m)^{T \times m}}$
- Also exposes `zero_coupon_price`, `accrued_interest`, `dirty_price`, `clean_price_from_dirty`

### YTM Solvers (`src/instruments/ytm_solver.py`)
- **Newton-Raphson** (`ytm_newton`): Uses numerical derivative (central difference), default guess 5%, max 500 iterations
- **Brent** (`ytm_brentq`) and **Bisection** (`ytm_bisection`): robust fallbacks bracketing between -5% and +50%
- **Combined** (`ytm_solver`): Tries Brent first, then Newton, then bisection
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

### PCA (`src/curve/pca.py`)
- Standardizes empirical yield curve panels and extracts Level, Slope, Curvature components

---

## Portfolio — Implementation Details

### `Position` (`src/portfolio/position.py`)
- Holds a single bond instrument and transaction quantity.
- Computes position-level market value, Modified Duration, Convexity, and DV01.

### `Portfolio` (`src/portfolio/portfolio.py`)
- Groups bond positions.
- Computes MV-weighted Modified Duration, Convexity, and KRD vectors.
- Computes aggregate DV01.
- Runs portfolio-level stress P&L under Basel IRBB standardized scenarios.

---

## Caching & Validation — Implementation Details

### `JSONCache` (`src/utils/cache.py`)
- File-based cache using MD5 hashes for key-to-file path mapping.
- Enforces TTL checks and automatic deletion of expired cache records.

### `cross_validate_yields` (`src/data/validation.py`)
- Automatic decimal scaling alignment of percentage (FRED) and CBOE 10x scaled (Yahoo Finance) yield arrays.
- Checks and reports basis point discrepancies above a custom threshold.

---

## Data Fetchers — Implementation Details

### Data fetching interfaces (`src/data/`)
- `FredFetcher`: Retrieves treasury yields via `pandas_datareader`.
- `YFinanceFetcher`: Retrieves sovereign benchmark rates via `yfinance`.
- `TreasuryFetcher`: Uses US Treasury Fiscal API.

---

## Stochastic Models — Implementation Details

### Vasicek & CIR (`src/models/stochastic.py`, `calibration.py`)
- Implements closed-form zero-coupon bond pricing under affine term structure.
- Calibrates mean-reversion $\kappa$, long-term mean $\theta$, and volatility $\sigma$ using empirical regressions.
- `MonteCarloEngine` runs Euler-Maruyama discretization for path generation.

---

## Derivatives — Implementation Details

### `InterestRateSwap` (`src/derivatives/swap.py`)
- Defines standard fixed-for-floating Interest Rate Swaps.
- Computes fair Par Swap Rate via `swap_rate()`.
- Values off-market swaps (payer or receiver) via `swap_pv()`.

### `Cap` & `Floor` (`src/derivatives/cap_floor.py`)
- Prices interest rate caps and floors across all individual caplets/floorlets.
- Solved analytically under the Vasicek model and under Black's 1976 model.
- Put-Call Parity verified.

### `Swaption` (`src/derivatives/swaption.py`)
- European options to enter a swap at expiry.
- Priced under the Vasicek model via Jamshidian's Trick and under Black's 1976 model.

---

## Credit, MBS, Trees, Inflation, Structured, Exotics, XVA — Implementation Details

### Credit (`src/credit/`)
- Hazard-rate CDS pricing, structural (Merton) default models.

### MBS (`src/mbs/`)
- Prepayment modeling via CPR/SMM, pass-through cash flows, Option-Adjusted Spread (OAS).

### Trees (`src/trees/`)
- Trinomial and Hull-White lattices with binomial sanity checks; Bermudan swaption pricing.

### Inflation (`src/inflation/`)
- TIPS pricing, real vs nominal curve conversion, break-even inflation.

### Structured (`src/structured/`)
- Gaussian/Student-t copulas, tranche loss (Equity/Mezz/Senior), synthetic CDO/CLO pricing, floating-rate note (FRN) support.

### Exotics (`src/exotics/`)
- LIBOR Market Model (LMM/BGM), Constant Maturity Swap (CMS), Target Redemption Notes (TARNs).

### XVA (`src/xva/`)
- Exposure simulation (EE/PFE, optional margin), CVA/DVA/FVA/KVA with wrong-way risk support.

---

## Test Results

```
295 passed in 3.13s
```

| Test suite | Tests | Key coverage |
|---|---|---|
| `test_pricing` | 51 | Bond validation, pricing (par/premium/discount/zero), YTM solvers |
| `test_risk` | 66 | Duration, convexity, shock, dollar measures, effective D/C, key rate duration, stress |
| `test_bootstrap` | 28 | Annual/semi-annual bootstrapping, interpolation, error handling |
| `test_utils` | 21 | Plotting configurations, price-yield curves, JSONCache get/set/TTL/clear |
| `test_data` | 15 | Crossover yield-curve validation, fetcher mocks |
| `test_models` | 13 | Vasicek/CIR pricing, calibration, Monte Carlo simulation |
| `test_credit` | 12 | Hazard rates, CDS, structural models |
| `test_curve` | 11 | Curve evaluation & helpers |
| `test_portfolio` | 11 | Position/portfolio MV, weighted duration, DV01, KRD, stress PnL |
| `test_derivatives` | 11 | Swaps, caps/floors, swaptions (parity checks) |
| `test_mbs` | 11 | Prepayment, pass-through cash flows, OAS |
| `test_inflation` | 9 | TIPS pricing, real/nominal conversion |
| `test_structured` | 9 | Copulas, tranches, CDO, FRN |
| `test_nelsonsiegel` | 8 | Nelson-Siegel evaluation, fit, bound enforcement |
| `test_xva` | 7 | Exposure simulation, CVA/DVA/FVA/KVA |
| `test_trees` | 6 | Trinomial/Hull-White trees, Bermudan swaption |
| `test_exotics` | 6 | LMM, CMS, TARNs |

---

## Status

All 16 core mathematical modules are implemented, verified against textbook examples in `notebooks/`, and shipped in **v1.0.0** (2026-09-19).

Current build gates: `uv run ruff check .` → `uv run ruff format . --check` → `uv run mypy src/` → `uv run pytest` (295 passing).