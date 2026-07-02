# ruff: noqa
# mypy: ignore-errors
import numpy as np


class TargetRedemptionNote:
    def __init__(self, notional, target_cap, coupon_rate_func, funding_rate_func):
        """
        Initialize TARN.
        :param notional: Notional amount
        :param target_cap: Total maximum coupon amount to be paid before note terminates
        :param coupon_rate_func: Function that takes (path_index, time_index) and returns coupon rate
        :param funding_rate_func: Function that takes (path_index, time_index) and returns discount rate
        """
        self.notional = notional
        self.target_cap = target_cap
        self.coupon_rate_func = coupon_rate_func
        self.funding_rate_func = funding_rate_func

    def price(self, n_paths, payment_times, dt=1.0):
        """
        Price the TARN using Monte Carlo.
        """
        total_payoffs = np.zeros(n_paths)

        for p in range(n_paths):
            accumulated_coupon = 0.0
            discount_factor = 1.0
            path_pv = 0.0

            for t_idx, t in enumerate(payment_times):
                coupon = self.coupon_rate_func(p, t_idx) * dt

                # Check if target is breached
                if accumulated_coupon + coupon >= self.target_cap:
                    # Cap the final coupon
                    final_coupon = self.target_cap - accumulated_coupon
                    accumulated_coupon = self.target_cap

                    # Discount final payment and principal
                    r = self.funding_rate_func(p, t_idx)
                    discount_factor *= np.exp(-r * dt)
                    path_pv += (final_coupon * self.notional) * discount_factor

                    # Principal repayment on termination
                    path_pv += self.notional * discount_factor
                    break
                else:
                    accumulated_coupon += coupon
                    r = self.funding_rate_func(p, t_idx)
                    discount_factor *= np.exp(-r * dt)
                    path_pv += (coupon * self.notional) * discount_factor

            # If target not reached, principal repaid at maturity
            if accumulated_coupon < self.target_cap:
                path_pv += self.notional * discount_factor

            total_payoffs[p] = path_pv

        return np.mean(total_payoffs), np.std(total_payoffs) / np.sqrt(n_paths)
