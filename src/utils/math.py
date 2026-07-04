"""Generic mathematical and numerical utilities."""

from collections.abc import Callable

TOLERANCE = 1e-6
MAX_ITER = 500


def central_difference(
    func: Callable[[float], float], x: float, eps: float = 1e-6
) -> float:
    """Approximate the first derivative of a function using central difference.

    Parameters
    ----------
    func : Callable[[float], float]
        The mathematical function f(x) to differentiate.
    x : float
        The point at which to evaluate the derivative.
    eps : float, optional
        The step size for the finite difference. Default is 1e-6.

    Returns
    -------
    float
        The approximate first derivative f'(x).

    """
    return (func(x + eps) - func(x - eps)) / (2 * eps)


def newton_raphson(
    func: Callable[[float], float],
    deriv: Callable[[float], float] | None = None,
    guess: float = 0.05,
    tol: float = TOLERANCE,
    max_iter: int = MAX_ITER,
) -> float:
    """Find a root of a function using the Newton-Raphson method.

    Parameters
    ----------
    func : Callable[[float], float]
        The objective function f(x) for which to find f(x) = 0.
    deriv : Callable[[float], float], optional
        The first derivative f'(x). If None, central difference is used.
    guess : float, optional
        Initial estimate for the root. Default is 0.05.
    tol : float, optional
        Convergence tolerance. Default is 1e-6.
    max_iter : int, optional
        Maximum number of iterations. Default is 500.

    Returns
    -------
    float
        The estimated root x.

    Raises
    ------
    RuntimeError
        If the method does not converge within max_iter.

    """
    x = guess
    for _ in range(max_iter):
        f = func(x)
        if abs(f) < tol:
            return x

        df = deriv(x) if deriv is not None else central_difference(func, x)

        if abs(df) < 1e-12:
            break
        x -= f / df

    raise RuntimeError("Newton-Raphson did not converge")


def bisection(
    func: Callable[[float], float],
    lower: float,
    upper: float,
    tol: float = TOLERANCE,
    max_iter: int = MAX_ITER,
) -> float:
    """Find a root of a function using the bisection method.

    Parameters
    ----------
    func : Callable[[float], float]
        The objective function f(x) for which to find f(x) = 0.
    lower : float
        Lower bound of the search interval.
    upper : float
        Upper bound of the search interval.
    tol : float, optional
        Convergence tolerance. Default is 1e-6.
    max_iter : int, optional
        Maximum number of iterations. Default is 500.

    Returns
    -------
    float
        The estimated root x.

    Raises
    ------
    ValueError
        If the root is not bracketed by lower and upper.
    RuntimeError
        If the method does not converge within max_iter.

    """
    f_low = func(lower)
    f_high = func(upper)

    if f_low * f_high > 0:
        raise ValueError(
            f"Root not bracketed: f({lower})={f_low:.4f}, f({upper})={f_high:.4f}"
        )

    for _ in range(max_iter):
        mid = (lower + upper) / 2
        f_mid = func(mid)

        if abs(f_mid) < tol:
            return mid

        if f_low * f_mid <= 0:
            upper = mid
            f_high = f_mid
        else:
            lower = mid
            f_low = f_mid

    raise RuntimeError("Bisection did not converge")

import numpy as np

def jacobian_central_difference(
    func: Callable[[np.ndarray], np.ndarray], x: np.ndarray, eps: float = 1e-6
) -> np.ndarray:
    """Approximate the Jacobian matrix using central difference."""
    n = len(x)
    m = len(func(x))
    J = np.zeros((m, n))
    for i in range(n):
        x_plus = x.copy()
        x_minus = x.copy()
        x_plus[i] += eps
        x_minus[i] -= eps
        J[:, i] = (func(x_plus) - func(x_minus)) / (2 * eps)
    return J

def newton_raphson_multi(
    func: Callable[[np.ndarray], np.ndarray],
    guess: np.ndarray,
    jac: Callable[[np.ndarray], np.ndarray] | None = None,
    tol: float = TOLERANCE,
    max_iter: int = MAX_ITER,
) -> np.ndarray:
    """Find a root of a multivariate function using the Newton-Raphson method."""
    x = np.asarray(guess, dtype=float)
    for _ in range(max_iter):
        f = func(x)
        if np.linalg.norm(f, ord=np.inf) < tol:
            return x
        
        J = jac(x) if jac is not None else jacobian_central_difference(func, x)
        
        try:
            dx = np.linalg.solve(J, -f)
        except np.linalg.LinAlgError:
            # Fallback to least squares if singular
            dx, _, _, _ = np.linalg.lstsq(J, -f, rcond=None)
            
        x += dx
        if np.linalg.norm(dx, ord=np.inf) < 1e-12:
            break
            
    if np.linalg.norm(func(x), ord=np.inf) >= tol:
        raise RuntimeError("Multivariate Newton-Raphson did not converge")
    return x
