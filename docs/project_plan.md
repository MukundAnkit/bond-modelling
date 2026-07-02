# Modeling Requirements Document (MRD): Progressive Fixed-Income Engine

## 1. Primary Modeling Objectives

The objective of this project is to build a full-stack fixed-income pricing and risk engine in progressive stages. Rather than starting with advanced parametric models, the system will be built from the ground up, ensuring absolute mathematical accuracy at the individual bond level before scaling to macro-level yield curve dynamics.

### 1.1. Primary Data Sources

To feed the models across all stages, the system will primarily rely on the following accessible data providers:

- **FRED (Federal Reserve Economic Data)**: The primary source for historical U.S. Treasury yields and macroeconomic time-series data, accessible programmatically via the pandas_datareader API.
- **U.S. Department of the Treasury**: Used to source the official Daily Treasury Par Yield Curve Rates.
- **FINRA Market Data Center**: Utilized for extracting specifications on individual corporate and municipal bonds (Face Value, Coupon, Maturity, and current trading price).
- **Yahoo Finance (yfinance)**: Leveraged for pulling live, end-of-day pricing and yields on benchmark sovereign debt tickers (e.g., ^IRX, ^TNX).

The project will be executed in four distinct modules:

- **Module 1**: Single Instrument Pricing (Time Value of Money & YTM).
- **Module 2**: Risk Sensitivity (Duration & Convexity).
- **Module 3**: Discrete Term Structure (Bootstrapping).
- **Module 4**: Continuous Curve Optimization (Nelson-Siegel).

---

## 2. Module 1: Single Instrument Pricing Engine (The Fundamentals)

This module establishes the foundational arithmetic of the system. It must be able to price a standard, fixed-rate bond and back-solve for its yield.

### 2.1. Required Inputs

- **Face Value ($F$)**: Principal amount (default to 100 or 1,000).
- **Coupon Rate ($C$)**: Annualized percentage.
- **Maturity ($T$)**: Years to maturity.
- **Compounding Frequency ($m$)**: Usually 2 (semi-annual) or 1 (annual).
- **Market Price ($P$) / Market Yield ($y$)**: Depending on what needs to be solved.

### 2.2. Mathematical Requirements

**Price Calculation**: Given a market yield, the engine must calculate the exact present value of all future cash flows.

$$
P = \sum_{t=1}^{T \times m} \frac{C / m}{\left(1 + \frac{y}{m}\right)^t} + \frac{F}{\left(1 + \frac{y}{m}\right)^{T \times m}}
$$

**Yield to Maturity (YTM) Solver**: Because the YTM equation cannot be algebraically inverted, the system must implement a numerical root-finding algorithm (such as the Newton-Raphson method or Bisection method) to solve for $y$ given $P$.

**Tolerance Constraint**: The YTM solver must converge to an accuracy of $10^{-6}$ (0.0001%).

---

## 3. Module 2: Risk & Sensitivity Engine (Duration & Convexity)

Once a bond can be priced, the model must quantify how sensitive that price is to theoretical changes in the central bank policy rate.

### 3.1. Mathematical Requirements

- **Macaulay Duration ($MacD$)**: Must calculate the time-weighted average of cash flows.
- **Modified Duration ($ModD$)**: Must calculate the first derivative of the price with respect to yield to estimate linear price drops.

$$
ModD = \frac{MacD}{1 + \frac{y}{m}}
$$

- **Convexity ($Cx$)**: Must calculate the second derivative to account for the curvature of the price-yield relationship.

### 3.2. Analytical Outputs

**Shock Simulation**: The module must output a predicted new bond price given user-defined interest rate shocks (e.g., +50 bps, +100 bps, -75 bps) using the Taylor Series expansion approximation:

$$
\Delta P \approx -ModD \times P \times \Delta y + \frac{1}{2} \times Cx \times P \times (\Delta y)^2
$$

---

## 4. Module 3: Discrete Term Structure (Bootstrapping)

With single bonds fully modeled, the system must now link multiple bonds together to extract pure, risk-free interest rates across time.

### 4.1. Required Inputs

A cross-sectional dataset of currently trading, par-valued sovereign bonds with sequential maturities (e.g., 1Y, 2Y, 3Y, 4Y, 5Y).

### 4.2. Mathematical Requirements

**Bootstrapping Algorithm**: The engine must iteratively strip out the coupon payments to isolate the theoretical zero-coupon yield (the "Spot Rate" $z_t$) for every maturity point.

**Logic**: The $1$-year spot rate is equal to the $1$-year par yield. The system must use this $1$-year spot rate to discount the first coupon of the $2$-year bond, allowing it to solve for the $2$-year spot rate. This recursive loop must continue up to the $30$-year bond.

### 4.3. Analytical Outputs

- **Spot Rate Vector**: An array of discrete, zero-coupon yields corresponding exactly to the observable maturities in the market.

---

## 5. Module 4: Continuous Curve Optimization (Nelson-Siegel)

The final stage upgrades the discrete spot rates from Module 3 into a smooth, continuous mathematical function that can price cash flows falling between standard maturities.

### 5.1. Required Inputs

The discrete Spot Rate Vector ($z_t$) generated by Module 3.

### 5.2. Mathematical & Algorithmic Requirements

**The Nelson-Siegel Equation**:

$$
y(t) = \beta_0 + \beta_1 \left( \frac{1 - e^{-t/\tau}}{t/\tau} \right) + \beta_2 \left( \frac{1 - e^{-t/\tau}}{t/\tau} - e^{-t/\tau} \right)
$$

**Optimization Objective**: The module must utilize an optimization solver (e.g., Nelder-Mead) to find the parameters ($\beta_0, \beta_1, \beta_2, \tau$) that minimize the Sum of Squared Errors (SSE) between the bootstrapped spot rates and the theoretical NS curve.

**Constraints**:

- $\beta_0 > 0$ (Long-term rate cannot be negative).
- $\tau > 0$ (Time decay cannot be negative).

### 5.3. Analytical Outputs

- **Continuous Yield Curve**: The ability to query the model for an exact yield at an arbitrary maturity (e.g., inputting $T=4.32$ years and receiving the interpolated theoretical yield).
- **Macro Regime Tracking**: Output of the $\beta_0$ (Level), $\beta_1$ (Slope), and $\beta_2$ (Curvature) parameters to measure market sentiment regarding inflation and growth.

---

## 6. Execution Protocol

This MRD requires that development strictly follows the module sequence. Module N must be thoroughly back-tested against established financial calculators (like a Bloomberg terminal output or verified textbook examples) before development begins on Module N+1.

---

## 7. Extensions (Modules 9 - 12)

### 7.1. Module 9: Credit Risk & CDS
- Implement hazard rate calibration from credit spreads.
- Implement structural models (e.g., Merton model) for firm default probability.
- Implement single-name Credit Default Swap (CDS) pricing.

### 7.2. Module 10: MBS & Prepayment
- Implement CPR (Conditional Prepayment Rate) and SMM (Single Monthly Mortality).
- Generate pass-through mortgage cash flows.
- Implement Option-Adjusted Spread (OAS) for pricing embedded prepayment optionality.

### 7.3. Module 11: Advanced Term Structure & Trees
- Build Trinomial Trees for interest rate evolution.
- Implement Hull-White lattice generation.
- Value Bermudan swaptions using backward induction on trees.

### 7.4. Module 12: Inflation-Linked Bonds
- Construct Real vs. Nominal yield curves.
- Calculate Break-Even Inflation rates.
- Price TIPS (Treasury Inflation-Protected Securities).
