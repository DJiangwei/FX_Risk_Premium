# `em_fx_rp`: Global & Emerging Market FX Risk Premium Package

[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-17%20passed-brightgreen.svg)]()

An institutional-grade quantitative package for Foreign Exchange (FX) Risk Premium analysis and trading, built directly on the theoretical foundations of:
> **Adam S. Iqbal**, *Foreign Exchange: Practical Asset Pricing and Macroeconomic Theory* (Springer / Palgrave Macmillan, 2022).

---

## 🌍 Supported Currency Universes (57 Currencies across 6 Categories)

The package comes pre-configured with **57 currencies** mapped to standard Bloomberg ticker conventions (`PX_LAST`, forwards, ATM vol, 25d Risk Reversals, 25d Butterflies, policy rates, and CPI YoY):

| Category | Currencies (ISO Codes) | Description |
| :--- | :--- | :--- |
| **1) DM (Developed Markets)** | `EUR`, `GBP`, `CHF`, `AUD`, `NZD`, `CAD`, `SEK`, `NOK`, `DKK` | G10 & Scandis |
| **2) CEEMEA** | `CZK`, `PLN`, `HUF`, `RON`, `TRY`, `ILS`, `EGP`, `ZAR`, `SAR`, `AED`, `QAR`, `RUB`, `UAH` | Central/Eastern Europe, Middle East & Africa |
| **3) LatAM** | `MXN`, `BRL`, `CLP`, `COP`, `PEN`, `ARS` | Latin America |
| **4) SSA** | `NGN`, `KES`, `GHS`, `UGX`, `ZMW`, `TZS`, `AOA`, `XOF` | Sub-Saharan Africa |
| **5) Asia** | `CNY`, `CNH`, `HKD`, `SGD`, `TWD`, `KRW`, `INR`, `IDR`, `PHP`, `THB`, `MYR`, `VND`, `PKR` | Greater China, North & South-East Asia, South Asia |
| **6) Edge (Frontier / Caucasus & Balkans)** | `KZT`, `UZS`, `TJS`, `KGS`, `MNT`, `GEL`, `AZN`, `AMD`, `MDL`, `ALL`, `RSD`, `BSM` | Central Asia, Caucasus, Mongolia & Balkans |

---

## 🌟 Theoretical Pillars & Architecture

1. **The Central Pricing Equation (CPE) & Microfoundations (Chapter 1)**
   $$p_t = \mathbb{E}_t^P \left[ m_{t+1} X_{t+1} \right] = \frac{\mathbb{E}_t^P[X_{t+1}]}{1+r_f} + \text{Cov}_t(m_{t+1}, X_{t+1})$$
   Currencies with payoffs negatively correlated with marginal utility $m_{t+1}$ (i.e. crashing in global recessions) must offer a positive **Currency Risk Premium** to induce risk-averse investors to hold them.

2. **UIP Failure & The Carry Trade as Risk Premium (Chapter 2)**
   $$\mathbb{E}_t^P[S_T] - F_t(T) = - e^{r_d \tau} \rho_t\left( m_{t, T}, S_T \right) \sigma_t(m_{t, T}) \sigma_t(S_T)$$
   Carry return is not an anomaly or "free lunch"—it is direct compensation for bearing pro-cyclical crash risk.

3. **Risk Premium & Real Interest Rate Equivalence (Chapter 3, Eq. 3.13 & 3.16)**
   $$r_f^p - r_d^p = (r_f - r_d) - (\pi_f - \pi_d) = r_f^{real} - r_d^{real}$$
   Nominal interest rate differential decomposes into expected inflation differential (spot depreciation trend) and **true economic risk premium** (real yield buffer).

4. **Options-Implied Tail & Skewness Risk Premiums (Chapter 4, Eq. 4.9)**
   Extracting the Volatility Risk Premium (VRP: $\text{IV} - \text{RV}$), $25\Delta\text{ Risk Reversal}$ skew (crash risk), and Breeden-Litzenberger risk-neutral distributions:
   $$Q(S_T = K) = e^{r_d \tau} \frac{\partial^2 C(K)}{\partial K^2}$$

5. **Multi-Factor Composite Scorecard (FX-RPS)**
   $$\text{FX-RPS}_i = w_1 z(\text{Real Carry}_i) + w_2 z(\text{Carry-to-Vol}_i) + w_3 z(\text{VRP}_i) - w_4 z(\text{Skew Ratio}_i) - w_5 z(\beta_{i, M})$$

---

## 🚀 Quick Start

### Installation

```bash
git clone https://github.com/DJiangwei/FX_Risk_Premium.git
cd FX_Risk_Premium
pip install -e .
```

### Basic Usage with Bloomberg Data (`xbbg`)

```python
from em_fx_rp.data.bbg_loader import DataLoader
from em_fx_rp.models.composite import CompositeRiskPremiumModel

# 1. Choose any category: "DM", "CEEMEA", "LATAM", "SSA", "ASIA", "EDGE", "EM_ALL", "ALL_CURRENCIES"
# or supply your own custom list of currency codes:
loader = DataLoader(universe="EDGE", use_cache=True)
loader.fetch_data(start_date="2020-01-01", end_date="2023-12-31")

# 2. Compute Multi-Dimensional Risk Premium Scorecard
model = CompositeRiskPremiumModel(loader)
scorecard = model.compute_scorecard()
print(scorecard[["Rank", "Currency", "Region", "Real_Carry", "Carry_to_Vol", "Skew_Ratio", "SPX_Beta", "FX_RPS"]])
```

### Carry Decomposition (Iqbal Eq. 3.13)

```python
from em_fx_rp.models.real_rate import RealRateModel

real_model = RealRateModel(loader)
mxn_decomp = real_model.decompose_carry("MXN")
# Returns: Nominal Spread, Inflation Differential, and Real Risk Premium
print(mxn_decomp.tail())
```

### Options-Implied Q-Distribution (Breeden-Litzenberger)

```python
from em_fx_rp.models.options_vrp import OptionsVRPModel
from em_fx_rp.visualization.plots import plot_risk_neutral_density

opt_model = OptionsVRPModel(loader)
strikes, q_pdf = opt_model.reconstruct_risk_neutral_density("MXN", tenor="1M")
fig = plot_risk_neutral_density(strikes, q_pdf, ccy="USDMXN", save_path="mxn_density.png")
```

### Walk-Forward Backtesting

```python
from em_fx_rp.trading.backtest import PortfolioBacktest

# Long Top 3, Short Bottom 3 based on monthly FX-RPS
backtest = PortfolioBacktest(loader, top_n=3, bottom_n=3, long_only=False)
results = backtest.run(start_date="2020-06-01")
stats = backtest.get_summary_stats(results)
print(stats)
```

---

## 📊 Bloomberg Ticker Conventions Reference

| Data Category | Bloomberg Ticker Pattern | Field | Example |
| :--- | :--- | :--- | :--- |
| **Spot Rate** | `USD{CCY} Curncy` (or `{CCY}USD Curncy` for DM base) | `PX_LAST` | `USDMXN Curncy`, `EURUSD Curncy` |
| **Forwards** | `USD{CCY}1M Curncy`, `USD{CCY}3M Curncy` | `PX_LAST` | `USDZAR1M Curncy`, `USDKRW3M Curncy` |
| **ATM Implied Vol** | `USD{CCY}V1M Curncy`, `USD{CCY}V3M Curncy` | `PX_LAST` | `USDBRLV1M Curncy` |
| **25d Risk Reversal** | `USD{CCY}25R1M Curncy` | `PX_LAST` | `USDTRY25R1M Curncy` |
| **25d Butterfly** | `USD{CCY}25B1M Curncy` | `PX_LAST` | `USDMXN25B1M Curncy` |
| **Policy Rates** | e.g. `MXONBR Index`, `BZSTSETA Index` | `PX_LAST` | `SARRP Index`, `CZRP2W Index` |
| **CPI YoY** | e.g. `MXPCYOY Index`, `BZIPTL Index` | `PX_LAST` | `CPI YOY Index`, `KOCPIYOY Index` |
| **Global Factors** | `SPX Index`, `VIX Index`, `FEDL01 Index` | `PX_LAST` | Benchmark proxies |

---

## 🔬 Testing

Run the full automated test suite:
```bash
pytest -v
```
All 17 tests verify exact mathematical alignment with equations in Iqbal (2022) across all 6 regional categories.
