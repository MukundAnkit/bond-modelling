"""Algorithmic Adjoint Differentiation (AAD) framework."""

from __future__ import annotations

from typing import Any

import numpy as np
from scipy.stats import norm


class Dual:
    """A node in the computation graph for AAD."""

    def __init__(
        self,
        value: float,
        children: list[Any] | None = None,
        local_gradients: list[float] | None = None,
    ) -> None:
        self.value = float(value)
        self.children = children if children is not None else []
        self.local_gradients = local_gradients if local_gradients is not None else []
        self.adjoint = 0.0

    def __add__(self, other: float | Dual) -> Dual:
        if not isinstance(other, Dual):
            other = Dual(other)
        return Dual(self.value + other.value, [self, other], [1.0, 1.0])

    def __radd__(self, other: float | Dual) -> Dual:
        return self.__add__(other)

    def __sub__(self, other: float | Dual) -> Dual:
        if not isinstance(other, Dual):
            other = Dual(other)
        return Dual(self.value - other.value, [self, other], [1.0, -1.0])

    def __rsub__(self, other: float | Dual) -> Dual:
        if not isinstance(other, Dual):
            other = Dual(other)
        return Dual(other.value - self.value, [other, self], [1.0, -1.0])

    def __mul__(self, other: float | Dual) -> Dual:
        if not isinstance(other, Dual):
            other = Dual(other)
        return Dual(self.value * other.value, [self, other], [other.value, self.value])

    def __rmul__(self, other: float | Dual) -> Dual:
        return self.__mul__(other)

    def __truediv__(self, other: float | Dual) -> Dual:
        if not isinstance(other, Dual):
            other = Dual(other)
        return Dual(
            self.value / other.value,
            [self, other],
            [1.0 / other.value, -self.value / (other.value**2)],
        )

    def __rtruediv__(self, other: float | Dual) -> Dual:
        if not isinstance(other, Dual):
            other = Dual(other)
        return Dual(
            other.value / self.value,
            [other, self],
            [1.0 / self.value, -other.value / (self.value**2)],
        )

    def __pow__(self, other: float | Dual) -> Dual:
        if not isinstance(other, Dual):
            return Dual(
                self.value**other, [self], [other * (self.value ** (other - 1))]
            )
        return Dual(
            self.value**other.value,
            [self, other],
            [
                other.value * (self.value ** (other.value - 1)),
                (self.value**other.value) * np.log(self.value),
            ],
        )

    def __neg__(self) -> Dual:
        return Dual(-self.value, [self], [-1.0])

    def __float__(self) -> float:
        return float(self.value)

    def backward(self) -> None:
        """Compute adjoints using backward accumulation."""
        self.adjoint = 1.0
        topo: list[Any] = []
        visited: set[int] = set()

        def build_topo(node: Any) -> None:
            if id(node) not in visited:
                visited.add(id(node))
                for child in node.children:
                    build_topo(child)
                topo.append(node)

        build_topo(self)

        for node in reversed(topo):
            for child, local_grad in zip(
                node.children, node.local_gradients, strict=False
            ):
                child.adjoint += node.adjoint * local_grad


def exp(x: float | Dual) -> float | Dual:
    if isinstance(x, Dual):
        val = np.exp(x.value)
        return Dual(val, [x], [val])
    return float(np.exp(x))


def log(x: float | Dual) -> float | Dual:
    if isinstance(x, Dual):
        val = np.log(x.value)
        return Dual(val, [x], [1.0 / x.value])
    return float(np.log(x))


def sqrt(x: float | Dual) -> float | Dual:
    if isinstance(x, Dual):
        val = np.sqrt(x.value)
        return Dual(val, [x], [0.5 / val])
    return float(np.sqrt(x))


def maximum(x: float | Dual, y: float | Dual) -> float | Dual:
    if not isinstance(x, Dual) and not isinstance(y, Dual):
        return max(x, y)

    if isinstance(x, Dual):
        x_val: float = x.value
    else:
        x_val = x
    if isinstance(y, Dual):
        y_val: float = y.value
    else:
        y_val = y

    val: float = max(x_val, y_val)

    if isinstance(x, Dual) and isinstance(y, Dual):
        return Dual(
            val, [x, y], [1.0 if x_val > y_val else 0.0, 1.0 if y_val > x_val else 0.0]
        )
    elif isinstance(x, Dual):
        return Dual(val, [x], [1.0 if x_val > y_val else 0.0])
    else:
        return Dual(val, [y], [1.0 if y_val > x_val else 0.0])


def norm_cdf(x: float | Dual) -> float | Dual:
    if isinstance(x, Dual):
        val = norm.cdf(x.value)
        grad = norm.pdf(x.value)
        return Dual(val, [x], [grad])
    return float(norm.cdf(x))


def norm_pdf(x: float | Dual) -> float | Dual:
    if isinstance(x, Dual):
        val = norm.pdf(x.value)
        grad = -x.value * val
        return Dual(val, [x], [grad])
    return float(norm.pdf(x))
