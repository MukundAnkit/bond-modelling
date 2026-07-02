# Bond Modelling

Progressive fixed-income pricing and risk engine, built from the ground up across twelve modules:

1. **Single Instrument Pricing** — Price & Yield-to-Maturity calculator
2. **Risk Sensitivity** — Duration & Convexity
3. **Discrete Term Structure** — Bootstrapping
4. **Continuous Curve Optimization** — Nelson-Siegel
5. **Portfolio Level Analytics** — Risk Engine & Aggregation
6. **Market Data Integrations** — Yield Curve Data Fetchers
7. **Stochastic Rate Models** — PCA & Vasicek/CIR Simulations
8. **Interest Rate Derivatives** — Swaps, Caps/Floors, Swaptions
9. **Credit Risk & CDS** — Hazard Rates & Structural Models
10. **MBS & Prepayment** — Pass-throughs & OAS
11. **Advanced Term Structure** — Trinomial & Hull-White Trees
12. **Inflation-Linked Bonds** — Real Yields & TIPS

## Setup

```bash
# Install uv (if not installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Sync environment
uv sync --extra dev

# Activate
source .venv/bin/activate
```

## Usage

```python
from src.instruments.bond import Bond
from src.instruments.pricing import price
from src.instruments.ytm_solver import ytm_solver

bond = Bond(face_value=100, coupon_rate=0.05, maturity=3.0, freq=2)
p = price(bond, yield_rate=0.04)     # → ~102.80
y = ytm_solver(bond, target_price=p) # → ~0.04
```

## Tests

```bash
uv run pytest                   # all tests
uv run pytest -v                # verbose
uv run pytest --cov=src         # with coverage
```

## Project Structure

```
src/
├── instruments/       # Bond instrument definitions & pricing
├── risk/              # Duration & convexity
├── bootstrap/         # Discrete term structure bootstrapping
├── curve/             # Continuous yield curve (Nelson-Siegel)
├── models/            # Stochastic rate models (Vasicek, CIR, PCA, Monte Carlo)
├── portfolio/         # Portfolio aggregation and risk engine
├── data/              # Data source fetchers
├── credit/            # Credit risk & CDS pricing
├── mbs/               # Mortgage-backed securities & prepayment
├── trees/             # Interest rate trees (Trinomial, Hull-White)
├── inflation/         # Inflation-linked bonds (TIPS)
├── derivatives/       # Interest rate derivatives (Swaps, Caps, Swaptions)
└── utils/             # Shared helpers
```

## Verification

See `notebooks/01-single-instrument-pricing-verification.ipynb` for textbook cross-checks.

## License

MIT
