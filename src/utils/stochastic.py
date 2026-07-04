import numpy as np
import scipy.integrate as integrate
from typing import Callable

def integrate_function(func: Callable[[float], float], a: float, b: float) -> float:
    """Rigorous numerical integration using quadrature.
    
    Args:
        func: The function to integrate.
        a: Lower bound.
        b: Upper bound.
        
    Returns:
        The definite integral of the function from a to b.
    """
    if a == b:
        return 0.0
    result, _ = integrate.quad(func, a, b)
    return result
