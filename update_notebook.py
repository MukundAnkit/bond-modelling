import nbformat

with open("notebooks/10-mbs-verification.ipynb") as f:
    nb = nbformat.read(f, as_version=4)

# 1. Richard-Roll Markdown
md1 = nbformat.v4.new_markdown_cell(
    source="## Richard-Roll Prepayment Model\nDemonstrating the new stochastic/behavioral prepayment modeling."
)
# 1. Richard-Roll Code
code1_src = """import numpy as np
import matplotlib.pyplot as plt
from src.mbs.prepayment import richard_roll_cpr

months = np.arange(1, 121)
wac = 0.06
rates = [0.03, 0.05, 0.07]  # Different current rates to show refinancing incentive

plt.figure(figsize=(10, 5))
for r in rates:
    cpr_curve = [richard_roll_cpr(wac, r, m, m%12 + 1, pool_factor=1.0) for m in months]
    plt.plot(months, cpr_curve, label=f"Current Rate: {r*100}%")

plt.title("Richard-Roll Prepayment Curves (WAC=6%)")
plt.xlabel("Month")
plt.ylabel("CPR")
plt.legend()
plt.grid(True)
plt.show()
"""
code1 = nbformat.v4.new_code_cell(source=code1_src)

# 2. Hull-White OAS Markdown
md2 = nbformat.v4.new_markdown_cell(
    source="## Monte Carlo OAS using Hull-White\nPricing the prepayment option using stochastic generated paths."
)
# 2. Hull-White OAS Code
code2_src = """from src.mbs.oas import generate_hw1f_paths, calculate_oas, price_mbs
from src.mbs.pass_through import project_cash_flows

# Generate HW1F paths
n_paths = 100
term = 360
r0 = 0.05
a = 0.1
sigma = 0.01

rate_paths = generate_hw1f_paths(r0, a, sigma, n_paths, term, 1.0/12.0, r0)

plt.figure(figsize=(10, 5))
for i in range(10):
    plt.plot(rate_paths[i, :])
plt.title("Hull-White 1F Interest Rate Paths")
plt.xlabel("Month")
plt.ylabel("Short Rate")
plt.grid(True)
plt.show()

# Calculate OAS
balance = 100000
wac = 0.06

# We'll use a dynamic prepayment model (richard-roll)
def dynamic_smm_hw(rate_path, wac_val):
    # rate_path is an array of length term
    def smm_func(t, pool_factor):
        # We need the rate at time t
        current_rate = rate_path[t] if t < len(rate_path) else rate_path[-1]
        cpr = richard_roll_cpr(wac_val, current_rate, t+1, (t%12)+1, pool_factor)
        return 1.0 - (1.0 - cpr)**(1.0/12.0)
    return smm_func

# To find OAS, we need a price first. Let's assume price = 101000
price = 101000
oas = calculate_oas(price, balance, wac, term, rate_paths, dynamic_smm_hw)
print(f"Calculated Monte Carlo OAS: {oas*10000:.2f} bps")
"""
code2 = nbformat.v4.new_code_cell(source=code2_src)

nb.cells.extend([md1, code1, md2, code2])

with open("notebooks/10-mbs-verification.ipynb", "w") as f:
    nbformat.write(nb, f)
