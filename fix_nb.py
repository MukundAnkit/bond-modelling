path = "notebooks/08-derivatives-pricing-verification.ipynb"
with open(path) as f:
    content = f.read()

content = content.replace("cap_floor_black", "cap_floor_bachelier")
content = content.replace("price_swaption_black", "price_swaption_bachelier")
content = content.replace("Black", "Bachelier")
content = content.replace("black", "bachelier")

with open(path, "w") as f:
    f.write(content)
