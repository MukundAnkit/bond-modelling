# Implementation Plan: Module 45 Analytics

## 1. Advanced Instrument Structuring

### 1.1 Floating Rate Notes (FRNs)
**Mathematical Framework:**
An FRN pays coupons based on a reference rate (e.g., SOFR, LIBOR) plus a quoted spread (QM). 
The cash flow at time $t_i$ is given by:
$$ CF_i = N \times \Delta_i \times (R(t_{i-1}, t_i) + QM) $$
where:
- $N$ is the notional amount.
- $\Delta_i$ is the day-count fraction for the period.
- $R(t_{i-1}, t_i)$ is the reference rate set at $t_{i-1}$ for the period to $t_i$.

The price of the FRN is the present value of expected cash flows discounted by the discount margin (DM) curve:
$$ P = \sum_{i=1}^n \frac{CF_i}{(1 + r_i + DM)^{t_i}} $$

**Data Structures:**
- `FloatingRateNote` (class): Inherits from base `Instrument`. Contains `notional`, `reference_curve`, `quoted_margin`, `day_count_convention`, and `payment_frequency`.

**Edge Cases:**
- Negative interest rates (floor at zero if specified).
- Irregular first/last coupon periods.
- Reset dates not exactly matching payment dates.

### 1.2 Interest Rate Lattices (Binomial Tree)
**Mathematical Framework:**
We implement a simple binomial tree for the short rate $r$.
At each node $(i, j)$ (time step $i$, state $j$):
- The rate can move up to $r_{i+1, j+1} = r_{i, j} \times u$
- The rate can move down to $r_{i+1, j} = r_{i, j} \times d$
Where $u = e^{\sigma \sqrt{\Delta t}}$ and $d = 1/u$.
The risk-neutral probability is $p = 0.5$ in standard models like Ho-Lee (additive) or Black-Derman-Toy (log-normal). We will use a log-normal specification: $r_{i, j} = r_{i, 0} u^{2j}$.

**Data Structures:**
- `BinomialTree` (class): Contains `rates` (2D list or NumPy array), `time_steps`, `volatility`.

**Edge Cases:**
- Negative rates in additive models.
- Recombining tree precision (floating point errors).

## 2. Macro-Scenario & Stress Testing

### 2.1 Non-Parallel Curve Shifts
**Mathematical Framework:**
A yield curve $Y(T)$ can be shocked by a non-parallel shift function $S(T)$:
$$ Y_{shocked}(T) = Y(T) + S(T) $$
Common shifts:
- **Steepening**: $S(T) = \alpha \times \ln(1 + T)$
- **Flattening**: $S(T) = -\alpha \times \ln(1 + T)$
- **Twist**: Pivot at maturity $T_{pivot}$, where $S(T) = \alpha \times (T - T_{pivot})$.

### 2.2 Central Bank Policy Shocks
**Mathematical Framework:**
Policy shocks primarily affect the short end of the curve, fading out over time:
$$ S(T) = \Delta R_{policy} \times e^{-\lambda T} $$
where $\lambda$ controls the decay rate of the shock along the curve.

**Data Structures:**
- `ScenarioGenerator` (class): Contains methods `apply_non_parallel_shift(curve, shift_type, alpha, pivot)` and `apply_policy_shock(curve, delta_r, decay)`.

**Edge Cases:**
- Yields dropping below zero after a flattening or downward shift.
- Interpolation bounds when shock is applied sparsely.
