import sys
import numpy as np
from src.bootstrap.bootstrap import bootstrap_spot_rates
from src.instruments.bond import Bond

def test():
    maturities = np.array([1.0, 2.0, 3.0, 4.0, 5.0])
    par_yields = np.array([0.030, 0.035, 0.040, 0.045, 0.050])

    spot_annual = bootstrap_spot_rates(maturities, par_yields, freq=1)
    print("spot_annual", spot_annual)
    
    # check pricing
    spot_curve = np.column_stack([maturities, spot_annual])
    
    def price_with_spot_curve(bond, spot_curve):
        periods = bond.periods
        freq = bond.freq
        pv = 0.0
        for k in range(1, periods + 1):
            t = k / freq
            z = np.interp(t, spot_curve[:, 0], spot_curve[:, 1])
            df = 1.0 / (1.0 + z) ** t
            if k == periods:
                pv += (bond.coupon_payment + bond.face_value) * df
            else:
                pv += bond.coupon_payment * df
        return pv

    prices = []
    for t, c in zip(maturities, par_yields, strict=True):
        b = Bond(face_value=100, coupon_rate=c, maturity=t, freq=1)
        p = price_with_spot_curve(b, spot_curve)
        prices.append(p)
        print(f"Maturity {t} Price {p}")

    spot_semiannual = bootstrap_spot_rates(maturities, par_yields, freq=2)
    print("spot_semiannual", spot_semiannual)

    flat_par = np.full_like(maturities, 0.05)
    flat_spot = bootstrap_spot_rates(maturities, flat_par, freq=1)
    print("flat_spot", flat_spot)

if __name__ == "__main__":
    test()
