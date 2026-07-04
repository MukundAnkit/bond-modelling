import nbformat as nbf
import os

def create_swaps_notebook():
    nb = nbf.v4.new_notebook()
    nb.cells = [
        nbf.v4.new_markdown_cell("# 08 - Swaps Verification\n\nThis notebook demonstrates the Multi-Curve Integration and AAD framework for Interest Rate Swaps."),
        nbf.v4.new_code_cell("""import sys
import os
sys.path.append(os.path.abspath('..'))

import numpy as np
from src.derivatives.swap import InterestRateSwap, swap_pv, swap_rate
from src.curve.nelson_siegel import NelsonSiegelCurve
from src.derivatives.aad import Dual"""),
        nbf.v4.new_markdown_cell("## 1. Multi-Curve Pricing"),
        nbf.v4.new_code_cell("""# Discount and Forward curves
discount_curve = NelsonSiegelCurve(0.03, 0.0, 0.0, 1.0)
forward_curve = NelsonSiegelCurve(0.04, 0.0, 0.0, 1.0)

swap = InterestRateSwap(notional=1e6, fixed_rate=0.035, tenor=5.0, freq=2)

pv = swap_pv(swap, discount_curve, forward_curve, position="receiver")
print(f"Swap PV (Multi-Curve): {float(pv):.2f}")
"""),
        nbf.v4.new_markdown_cell("## 2. AAD Exact Greeks"),
        nbf.v4.new_code_cell("""# Using Dual numbers to get exact sensitivities (Rho) to parallel curve shifts
bump_d = Dual(0.0)
bump_f = Dual(0.0)

def bumped_discount(t):
    # AAD-enabled discount curve wrapper
    return 0.03 + bump_d

def bumped_forward(t):
    return 0.04 + bump_f

pv_dual = swap_pv(swap, bumped_discount, bumped_forward, position="receiver")
pv_dual.backward()

print(f"PV: {float(pv_dual):.2f}")
print(f"DV01 w.r.t Discount Curve: {bump_d.adjoint:.2f}")
print(f"DV01 w.r.t Forward Curve: {bump_f.adjoint:.2f}")
""")
    ]
    with open("notebooks/08-swaps-verification.ipynb", "w") as f:
        nbf.write(nb, f)

def create_options_notebook():
    nb = nbf.v4.new_notebook()
    nb.cells = [
        nbf.v4.new_markdown_cell("# 09 - Options Verification\n\nThis notebook demonstrates the Bachelier/SABR models and AAD Greeks for Swaptions & Caps/Floors."),
        nbf.v4.new_code_cell("""import sys
import os
sys.path.append(os.path.abspath('..'))

import numpy as np
from src.derivatives.swaption import Swaption, price_swaption_bachelier
from src.derivatives.swap import InterestRateSwap
from src.curve.nelson_siegel import NelsonSiegelCurve
from src.derivatives.aad import Dual"""),
        nbf.v4.new_markdown_cell("## 1. Bachelier Swaption Pricing"),
        nbf.v4.new_code_cell("""discount_curve = NelsonSiegelCurve(0.04, 0.0, 0.0, 1.0)
swap = InterestRateSwap(notional=1e6, fixed_rate=0.04, tenor=5.0, freq=2)
swaption = Swaption(swap, expiry=2.0, option_type="payer")

pv = price_swaption_bachelier(swaption, discount_curve, vol=0.0050)
print(f"Swaption PV (Bachelier): {float(pv):.2f}")
"""),
        nbf.v4.new_markdown_cell("## 2. SABR Swaption Pricing"),
        nbf.v4.new_code_cell("""sabr_params = {"alpha": 0.0050, "rho": -0.2, "nu": 0.3}
pv_sabr = price_swaption_bachelier(swaption, discount_curve, sabr_params=sabr_params)
print(f"Swaption PV (SABR): {float(pv_sabr):.2f}")
"""),
        nbf.v4.new_markdown_cell("## 3. AAD Exact Vega and Delta"),
        nbf.v4.new_code_cell("""# Using Dual numbers to get exact Greeks
from src.derivatives.bachelier import bachelier_formula

fwd = Dual(0.04)
strike = Dual(0.04)
t_exp = Dual(2.0)
vol = Dual(0.0050)
df = Dual(np.exp(-0.04 * 2.0))

px = bachelier_formula(fwd, strike, t_exp, vol, df, is_call=True)
px.backward()

print(f"Option Price: {float(px):.6f}")
print(f"Delta: {fwd.adjoint:.6f}")
print(f"Vega: {vol.adjoint:.6f}")
""")
    ]
    with open("notebooks/09-options-verification.ipynb", "w") as f:
        nbf.write(nb, f)

if __name__ == "__main__":
    create_swaps_notebook()
    create_options_notebook()
