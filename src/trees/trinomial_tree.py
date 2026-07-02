"""Trinomial tree models for interest rates."""

from collections.abc import Callable

import numpy as np


class TrinomialTree:
    """Base class for generic Trinomial Tree."""

    pass


class HWTree(TrinomialTree):
    """Hull-White Trinomial Tree."""

    def __init__(
        self,
        a: float,
        sigma: float,
        time_step: float,
        num_steps: int,
        zero_curve: Callable[[float], float],
    ):
        """Initialize the tree."""
        self.a = a
        self.sigma = sigma
        self.dt = time_step
        self.N = num_steps
        self.zero_curve = zero_curve

        self.dr = sigma * np.sqrt(3 * self.dt)
        if a > 0:
            self.j_max = int(np.ceil(0.184 / (a * self.dt)))
        else:
            self.j_max = num_steps

        self.Q: dict[int, dict[int, float]] = {i: {} for i in range(self.N + 1)}
        self.alpha = np.zeros(self.N + 1)

        self.probs: dict[int, dict[int, tuple[float, float, float]]] = {
            i: {} for i in range(self.N)
        }
        self.connections: dict[int, dict[int, tuple[int, int, int]]] = {
            i: {} for i in range(self.N)
        }

        self._build_tree()

    def _get_j_nodes(self, i: int) -> list[int]:
        """Get nodes."""
        max_j = min(i, self.j_max)
        return list(range(-max_j, max_j + 1))

    def _build_tree(self) -> None:
        """Construct the tree."""
        self.Q[0][0] = 1.0

        for i in range(self.N):
            p_next = self.zero_curve((i + 1) * self.dt)
            sum_q_exp = 0.0

            for j in self.Q[i]:
                r_star = j * self.dr
                sum_q_exp += self.Q[i][j] * np.exp(-r_star * self.dt)

            self.alpha[i] = (np.log(sum_q_exp) - np.log(p_next)) / self.dt

            for j in self.Q[i]:
                if j == self.j_max:
                    j_up, j_mid, j_down = j, j - 1, j - 2
                    pu = 7.0 / 6.0 + 0.5 * (
                        self.a**2 * j**2 * self.dt**2 - 3 * self.a * j * self.dt
                    )
                    pm = (
                        -1.0 / 3.0
                        - self.a**2 * j**2 * self.dt**2
                        + 2 * self.a * j * self.dt
                    )
                    pd = 1.0 / 6.0 + 0.5 * (
                        self.a**2 * j**2 * self.dt**2 - self.a * j * self.dt
                    )
                elif j == -self.j_max:
                    j_up, j_mid, j_down = j + 2, j + 1, j
                    pu = 1.0 / 6.0 + 0.5 * (
                        self.a**2 * j**2 * self.dt**2 + self.a * j * self.dt
                    )
                    pm = (
                        -1.0 / 3.0
                        - self.a**2 * j**2 * self.dt**2
                        - 2 * self.a * j * self.dt
                    )
                    pd = 7.0 / 6.0 + 0.5 * (
                        self.a**2 * j**2 * self.dt**2 + 3 * self.a * j * self.dt
                    )
                else:
                    j_up, j_mid, j_down = j + 1, j, j - 1
                    pu = 1.0 / 6.0 + 0.5 * (
                        self.a**2 * j**2 * self.dt**2 - self.a * j * self.dt
                    )
                    pm = 2.0 / 3.0 - self.a**2 * j**2 * self.dt**2
                    pd = 1.0 / 6.0 + 0.5 * (
                        self.a**2 * j**2 * self.dt**2 + self.a * j * self.dt
                    )

                self.probs[i][j] = (pu, pm, pd)
                self.connections[i][j] = (j_up, j_mid, j_down)

                r = self.alpha[i] + j * self.dr
                discount = np.exp(-r * self.dt)

                for k, p in zip([j_up, j_mid, j_down], [pu, pm, pd], strict=False):
                    if k not in self.Q[i + 1]:
                        self.Q[i + 1][k] = 0.0
                    self.Q[i + 1][k] += self.Q[i][j] * p * discount

    def get_rate(self, i: int, j: int) -> float:
        """Get short rate."""
        return float(self.alpha[i] + j * self.dr)
