import numpy as np
from scipy.stats import norm
import math

def merton_jump_diffusion_call(V, D, T, r, sigma, lambda_j, mu_j, sigma_j, N=50):
    k = np.exp(mu_j + 0.5 * sigma_j**2) - 1
    lambda_prime = lambda_j * (1 + k)
    
    call_price = 0.0
    for n in range(N):
        # Poisson probability
        prob = np.exp(-lambda_prime * T) * (lambda_prime * T)**n / math.factorial(n)
        
        sigma_n = np.sqrt(sigma**2 + n * sigma_j**2 / T)
        r_n = r - lambda_j * k + n * (mu_j + 0.5 * sigma_j**2) / T
        
        # Black Scholes
        d1 = (np.log(V/D) + (r_n + 0.5 * sigma_n**2)*T) / (sigma_n * np.sqrt(T))
        d2 = d1 - sigma_n * np.sqrt(T)
        
        bs_call = V * norm.cdf(d1) - D * np.exp(-r_n * T) * norm.cdf(d2)
        call_price += prob * bs_call
        
    return call_price

print(merton_jump_diffusion_call(100, 80, 1.0, 0.05, 0.20, 0.5, -0.1, 0.3))
