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
