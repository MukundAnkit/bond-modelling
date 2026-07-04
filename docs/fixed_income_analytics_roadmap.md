# Comprehensive Fixed-Income Analytics Roadmap

With the foundational fixed-income pricing engine structurally sound and verified against market standards, the next logical phase is to evolve the model from a basic valuation calculator into a comprehensive, production-grade fixed-income analytics suite.

The following proposals are structured as a cohesive mathematical roadmap. They transition the analysis from static single-instrument pricing to dynamic portfolio risk, term structure analytics, and credit modeling.

## Phase 1: Interest Rate Risk & Sensitivity Analytics
**Purpose:** To move beyond simple valuation and quantify the non-linear price-yield relationship. This fills the immediate gap required for basic portfolio hedging and risk management.

* **First-Order Sensitivity (Duration):** 
    * *Macaulay Duration:* Modeling the time-weighted average of cash flows.
    * *Modified Duration:* Deriving the exact percentage price change for a 100 bps shift in yield.
* **Second-Order Sensitivity (Convexity):** Modeling the second derivative of the price-yield function to account for the curvature missed by Modified Duration, especially critical for large yield shocks.
* **Key Rate Duration (KRD):** Instead of assuming a parallel shift in a flat yield curve, this model measures a bond's price sensitivity to shifts at specific maturity nodes (e.g., 2-year, 5-year, 10-year).

## Phase 2: Term Structure Modeling & Curve Building
**Purpose:** To eliminate the simplified assumption of a flat Yield to Maturity (YTM). In reality, cash flows occurring at different times must be discounted at their respective spot rates to prevent arbitrage.

* **Zero-Coupon Yield Curve Bootstrapping:** A recursive algorithm to extract theoretical spot rates from a universe of liquid, par-priced coupon bonds. 
* **Forward Rate Derivation:** Calculating implied forward rates $f_{t_1, t_2}$ from the bootstrapped spot curve, essential for pricing derivatives and floating-rate instruments.
* **Curve Interpolation Methods:** Implementing mathematical splines (e.g., Cubic Splines, Nelson-Siegel, or Nelson-Siegel-Svensson) to ensure the generated yield curve is continuous and smooth across all maturity nodes.

## Phase 3: Credit Risk & Spread Analytics
**Purpose:** To bridge the gap between risk-free sovereign pricing and corporate/wholesale bond valuation. This is the natural gateway into expected credit loss (ECL) frameworks and default modeling.

* **Z-Spread (Zero-Volatility Spread):** Modeling the constant spread added to the entire risk-free zero curve required to price a corporate bond at its current market value.
* **Implied Probability of Default (PD) Modeling:** Extracting market-implied hazard rates and PDs from the credit spread ($s$), assuming a specific Loss Given Default (LGD). The fundamental continuous-time approximation bridges pricing to credit risk: $s \approx \text{PD} \times \text{LGD}$.
* **Integration with IFRS 9 Frameworks:** Utilizing the implied PDs and term structures derived from wholesale corporate bond spreads to calibrate the forward-looking macro-economic models required for production-grade ECL calculations.

## Phase 4: Advanced Instrument Structuring
**Purpose:** To expand the breadth of the pricing engine to handle dynamic cash flows and embedded optionality.

* **Floating-Rate Notes (FRNs):** Modeling bonds where the coupon is tied to a reference rate (e.g., SOFR). This requires projecting future cash flows using the implied forward rate curve derived in Phase 2.
* **Option-Adjusted Spread (OAS):** Required for pricing bonds with embedded options (callable/puttable bonds). 
* **Interest Rate Lattices:** Implementing binomial interest rate trees (e.g., Black-Derman-Toy or Ho-Lee models) to model the evolution of short rates and evaluate the decision nodes for embedded call/put options.

## Phase 5: Macro-Scenario & Stress Testing
**Purpose:** To evaluate portfolio vulnerabilities against monetary policy shifts and broader economic shocks.

* **Non-Parallel Curve Shifts:** Modeling the pricing impact of yield curve steepening, flattening, and twisting (butterfly shifts).
* **Central Bank Policy Shocks:** Creating deterministic scenarios that simulate abrupt liquidity tightening or easing by central banks (such as the RBI's liquidity management mechanisms) to observe the impact on both risk-free valuation and credit spread widening.
