"""Bermudan swaption pricing."""

import numpy as np

from .hull_white import HullWhite1F
from .trinomial_tree import HWTree


class BermudanSwaption:
    """Prices a Bermudan Swaption using a Hull-White Trinomial Tree."""

    def __init__(
        self,
        hw_model: HullWhite1F,
        tree: HWTree,
        strike: float,
        exercise_times: list[float],
        swap_payment_times: list[float],
        is_payer: bool = True,
    ):
        """Initialize."""
        self.hw_model = hw_model
        self.tree = tree
        self.strike = strike
        self.exercise_times = sorted(exercise_times)
        self.swap_payment_times = sorted(swap_payment_times)
        self.is_payer = is_payer

    def _swap_value(self, t: float, r_t: float) -> float:
        remaining_payments = [t_p for t_p in self.swap_payment_times if t_p > t]
        if not remaining_payments:
            return 0.0

        p_0_t = self.tree.zero_curve(t)
        pv_fixed = 0.0

        prev_t = t
        zcb_last = 1.0
        for t_p in remaining_payments:
            p_0_end = self.tree.zero_curve(t_p)
            zcb = self.hw_model.zero_coupon_bond(t, t_p, r_t, p_0_t, p_0_end)
            dt = t_p - prev_t
            pv_fixed += self.strike * dt * zcb
            prev_t = t_p
            zcb_last = zcb

        pv_floating = 1.0 - zcb_last

        if self.is_payer:
            return float(max(0.0, pv_floating - pv_fixed))
        return float(max(0.0, pv_fixed - pv_floating))

    def price(self) -> float:
        """Price the swaption."""
        dt = self.tree.dt
        exercise_steps = [int(round(t / dt)) for t in self.exercise_times]
        last_step = exercise_steps[-1]

        v = {}
        for j in self.tree.Q[last_step]:
            r_t = self.tree.get_rate(last_step, j)
            v[j] = self._swap_value(last_step * dt, r_t)

        for i in range(last_step - 1, -1, -1):
            v_prev = {}
            is_exercise_date = i in exercise_steps

            for j in self.tree.Q[i]:
                r_t = self.tree.get_rate(i, j)
                discount = np.exp(-r_t * dt)

                j_up, j_mid, j_down = self.tree.connections[i][j]
                pu, pm, pd = self.tree.probs[i][j]

                cont_value = discount * (
                    pu * v.get(j_up, 0.0)
                    + pm * v.get(j_mid, 0.0)
                    + pd * v.get(j_down, 0.0)
                )

                if is_exercise_date:
                    ex_value = self._swap_value(i * dt, r_t)
                    v_prev[j] = max(ex_value, cont_value)
                else:
                    v_prev[j] = cont_value

            v = v_prev

        return float(v[0])
