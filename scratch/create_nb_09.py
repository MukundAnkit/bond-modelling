import nbformat
from nbformat.v4 import new_code_cell, new_markdown_cell, new_notebook

nb = new_notebook()

nb.cells.extend(
    [
        new_markdown_cell(
            "# Module 9: Credit Risk & CDS Modeling Verification\n\nThis notebook demonstrates the implementation of Structural and Reduced-Form credit risk models, as well as Credit Default Swap (CDS) pricing mechanics."
        ),
        new_code_cell("""import sys
import os
import numpy as np
import matplotlib.pyplot as plt

# Add src to path
sys.path.append(os.path.abspath('..'))

from src.credit.structural import MertonModel
from src.credit.reduced_form import constant_hazard_survival, piecewise_hazard_survival, jarrow_turnbull_price
from src.credit.cds import CDS, cds_premium_leg, cds_protection_leg, cds_par_spread
"""),
        new_markdown_cell(
            "## 1. Structural Models (Merton 1974)\n\nThe Merton model treats a firm's equity as a European Call option on its assets. The strike price is the face value of the firm's zero-coupon debt."
        ),
        new_code_cell("""# Example: Firm with Asset Value 100, Debt 80, 1-year maturity, 20% volatility
model = MertonModel(V=100.0, D=80.0, T=1.0, r=0.05, sigma_V=0.20)

print(f"Equity Value: ${model.equity_value():.2f}")
print(f"Debt Value: ${model.debt_value():.2f}")
print(f"Distance to Default (DD): {model.distance_to_default():.4f}")
print(f"Probability of Default (PD): {model.probability_of_default()*100:.2f}%")
print(f"Implied Credit Spread: {model.credit_spread()*10000:.1f} bps")
"""),
        new_code_cell(r"""# Plotting Distance to Default vs Asset Volatility
vols = np.linspace(0.05, 0.50, 50)
dds = [MertonModel(100, 80, 1.0, 0.05, vol).distance_to_default() for vol in vols]
pds = [MertonModel(100, 80, 1.0, 0.05, vol).probability_of_default() for vol in vols]

fig, ax1 = plt.subplots(figsize=(10, 5))

color = 'tab:blue'
ax1.set_xlabel('Asset Volatility ($\sigma_V$)')
ax1.set_ylabel('Distance to Default (DD)', color=color)
ax1.plot(vols, dds, color=color)
ax1.tick_params(axis='y', labelcolor=color)

ax2 = ax1.twinx()  
color = 'tab:red'
ax2.set_ylabel('Probability of Default (PD)', color=color)  
ax2.plot(vols, pds, color=color, linestyle='--')
ax2.tick_params(axis='y', labelcolor=color)

plt.title('Merton Model: Risk Metrics vs Asset Volatility')
fig.tight_layout()  
plt.show()
"""),
        new_markdown_cell(
            "## 2. Reduced-Form Models (Jarrow-Turnbull)\n\nReduced-form models model default as an exogenous Poisson process driven by a hazard rate $\\lambda$."
        ),
        new_code_cell(r"""# Survival curve with constant hazard rate (lambda = 5%)
times = np.linspace(0, 10, 100)
lam = 0.05
survivals = [constant_hazard_survival(lam, t) for t in times]

# Survival curve with piecewise hazard rates
hrates = [0.02, 0.05, 0.10]
ends = [2.0, 5.0, 10.0]
pw_survivals = [piecewise_hazard_survival(hrates, ends, t) for t in times]

plt.figure(figsize=(10, 5))
plt.plot(times, survivals, label=f'Constant $\lambda$ = {lam*100}%')
plt.plot(times, pw_survivals, label='Piecewise Hazard Rates', linestyle='--')
plt.title('Survival Probability Curves')
plt.xlabel('Time (Years)')
plt.ylabel('Survival Probability $S(t)$')
plt.legend()
plt.grid(True)
plt.show()
"""),
        new_markdown_cell(
            "## 3. Credit Default Swaps (CDS) Pricing\n\nComparing the Premium Leg (PV of regular premium payments) vs the Protection Leg (PV of default payoff)."
        ),
        new_code_cell("""def flat_yield_curve(t): return 0.04
def flat_survival_curve(t): return constant_hazard_survival(0.02, t)

# 5-Year CDS, Notional $10M, Spread 100 bps (0.01), Quarterly payments
cds = CDS(notional=10_000_000, spread=0.01, tenor=5.0, freq=4)
recovery_rate = 0.40

pv_premium = cds_premium_leg(cds, flat_yield_curve, flat_survival_curve)
pv_protection = cds_protection_leg(cds, flat_yield_curve, flat_survival_curve, recovery_rate)
par_spread = cds_par_spread(cds, flat_yield_curve, flat_survival_curve, recovery_rate)

print(f"Premium Leg PV (cost): ${pv_premium:,.2f}")
print(f"Protection Leg PV (payoff): ${pv_protection:,.2f}")
print(f"MTM Value to Buyer: ${pv_protection - pv_premium:,.2f}")
print(f"\\nFair Par Spread: {par_spread*10000:.1f} bps")
"""),
    ]
)

with open("notebooks/09-credit-risk-verification.ipynb", "w") as f:
    nbformat.write(nb, f)
