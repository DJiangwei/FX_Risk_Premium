"""
Synthetic / Mock data generator mirroring Bloomberg xbbg output.
Enables offline development, testing, and CI without active Bloomberg Terminal connection.
Supports 57 currencies across DM, CEEMEA, LatAm, SSA, Asia, and Edge.
"""

import numpy as np
import pandas as pd
from typing import List, Dict, Optional
from ..config import CURRENCIES, GLOBAL_BENCHMARKS


def generate_mock_market_data(
    currencies: List[str],
    start_date: str = "2020-01-01",
    end_date: str = "2023-12-31",
    seed: int = 42
) -> pd.DataFrame:
    """
    Generate realistic multi-asset daily data matching Bloomberg field names and ticker codes.
    Includes spot, forward 1M/3M/12M, ATM vol 1M/3M, 25d RR, 25d BF, policy rates, CPI, SPX, VIX.
    """
    np.random.seed(seed)
    dates = pd.date_range(start=start_date, end=end_date, freq="B")
    n = len(dates)

    # Global Factor generation (S&P 500 and VIX)
    # Covid shock around March 2020
    t_covid = (dates >= "2020-02-20") & (dates <= "2020-04-15")
    t_covid_peak = dates == "2020-03-18"

    # S&P 500 base random walk with Covid drawdown
    spx_ret = np.random.normal(0.0004, 0.009, n)
    spx_ret[t_covid] -= 0.015
    spx_price = 3200.0 * np.exp(np.cumsum(spx_ret))

    # VIX with spike up to 82 in March 2020
    vix_base = 15.0 + 5.0 * np.sin(np.linspace(0, 10, n)) + np.random.normal(0, 1.0, n)
    vix = np.clip(vix_base, 10.0, 35.0)
    vix[t_covid] = np.linspace(25.0, 75.0, np.sum(t_covid))
    if np.any(t_covid_peak):
        vix[t_covid_peak] = 82.7

    # US Fed Funds rate and US CPI
    us_rate = np.where(dates < "2020-03-15", 1.75, np.where(dates < "2022-03-15", 0.25, 5.25))
    us_cpi = np.where(dates < "2021-04-01", 1.8, np.where(dates < "2022-07-01", 7.5, 3.2)) + np.random.normal(0, 0.1, n)

    data: Dict[str, np.ndarray] = {
        GLOBAL_BENCHMARKS["SPX"]: spx_price,
        GLOBAL_BENCHMARKS["VIX"]: vix,
        GLOBAL_BENCHMARKS["US_FED_FUNDS"]: us_rate,
        GLOBAL_BENCHMARKS["US_CPI_YOY"]: us_cpi
    }

    # Regional default parameters
    region_defaults = {
        "DM":     {"base_spot": 1.25,   "base_rate": 1.5,  "cpi": 2.0, "base_vol": 7.5,  "rr": 0.2, "bf": 0.15, "beta": 0.35},
        "CEEMEA": {"base_spot": 15.0,   "base_rate": 6.5,  "cpi": 5.0, "base_vol": 12.0, "rr": 2.0, "bf": 0.35, "beta": 0.65},
        "LatAm":  {"base_spot": 20.0,   "base_rate": 7.0,  "cpi": 4.5, "base_vol": 13.0, "rr": 2.5, "bf": 0.40, "beta": 0.75},
        "SSA":    {"base_spot": 150.0,  "base_rate": 13.0, "cpi": 12.0,"base_vol": 15.0, "rr": 3.0, "bf": 0.45, "beta": 0.50},
        "Asia":   {"base_spot": 30.0,   "base_rate": 4.0,  "cpi": 3.0, "base_vol": 7.5,  "rr": 1.0, "bf": 0.20, "beta": 0.45},
        "Edge":   {"base_spot": 400.0,  "base_rate": 10.5, "cpi": 9.0, "base_vol": 10.5, "rr": 1.8, "bf": 0.30, "beta": 0.40},
    }

    # Specific overrides for well-known currencies
    overrides = {
        # DM
        "EUR": {"base_spot": 1.12,  "base_rate": -0.5, "cpi": 1.2, "base_vol": 5.5,  "rr": -0.2, "bf": 0.10, "beta": 0.30},
        "GBP": {"base_spot": 1.30,  "base_rate": 0.75, "cpi": 1.8, "base_vol": 7.8,  "rr": 0.4,  "bf": 0.18, "beta": 0.45},
        "CHF": {"base_spot": 0.97,  "base_rate": -0.75,"cpi": 0.5, "base_vol": 6.0,  "rr": -0.5, "bf": 0.12, "beta": -0.15},
        "AUD": {"base_spot": 0.70,  "base_rate": 0.75, "cpi": 1.6, "base_vol": 9.5,  "rr": 1.2,  "bf": 0.22, "beta": 0.70},
        "NZD": {"base_spot": 0.66,  "base_rate": 1.0,  "cpi": 1.7, "base_vol": 10.0, "rr": 1.1,  "bf": 0.22, "beta": 0.65},
        "CAD": {"base_spot": 1.30,  "base_rate": 1.75, "cpi": 1.9, "base_vol": 6.8,  "rr": 0.3,  "bf": 0.15, "beta": 0.50},
        "SEK": {"base_spot": 9.40,  "base_rate": 0.0,  "cpi": 1.7, "base_vol": 8.5,  "rr": 0.6,  "bf": 0.20, "beta": 0.55},
        "NOK": {"base_spot": 8.80,  "base_rate": 1.5,  "cpi": 2.2, "base_vol": 9.8,  "rr": 0.8,  "bf": 0.22, "beta": 0.60},
        "DKK": {"base_spot": 6.65,  "base_rate": -0.6, "cpi": 1.1, "base_vol": 5.5,  "rr": -0.2, "bf": 0.10, "beta": 0.30},

        # CEEMEA
        "MXN": {"base_spot": 18.8,  "base_rate": 7.25, "cpi": 3.8, "base_vol": 9.5,  "rr": 2.2, "bf": 0.35, "beta": 0.75},
        "BRL": {"base_spot": 4.10,  "base_rate": 6.50, "cpi": 4.2, "base_vol": 13.5, "rr": 3.0, "bf": 0.45, "beta": 0.85},
        "ZAR": {"base_spot": 14.2,  "base_rate": 6.50, "cpi": 4.5, "base_vol": 14.0, "rr": 2.8, "bf": 0.40, "beta": 0.80},
        "PLN": {"base_spot": 3.85,  "base_rate": 1.50, "cpi": 3.0, "base_vol": 8.0,  "rr": 1.5, "bf": 0.25, "beta": 0.60},
        "HUF": {"base_spot": 300.0, "base_rate": 2.0,  "cpi": 4.0, "base_vol": 11.0, "rr": 2.0, "bf": 0.30, "beta": 0.65},
        "CZK": {"base_spot": 22.8,  "base_rate": 2.0,  "cpi": 2.8, "base_vol": 7.5,  "rr": 1.2, "bf": 0.20, "beta": 0.50},
        "RON": {"base_spot": 4.30,  "base_rate": 2.5,  "cpi": 3.8, "base_vol": 6.5,  "rr": 1.0, "bf": 0.18, "beta": 0.45},
        "TRY": {"base_spot": 5.95,  "base_rate": 12.0, "cpi": 18.0,"base_vol": 18.0, "rr": 5.5, "bf": 0.80, "beta": 0.45},
        "ILS": {"base_spot": 3.45,  "base_rate": 0.25, "cpi": 0.8, "base_vol": 6.8,  "rr": 0.5, "bf": 0.15, "beta": 0.40},
        "EGP": {"base_spot": 16.0,  "base_rate": 12.25,"cpi": 11.5,"base_vol": 16.0, "rr": 4.0, "bf": 0.60, "beta": 0.35},
        "SAR": {"base_spot": 3.75,  "base_rate": 2.25, "cpi": 1.5, "base_vol": 0.8,  "rr": 0.1, "bf": 0.05, "beta": 0.05},
        "AED": {"base_spot": 3.67,  "base_rate": 2.00, "cpi": 1.4, "base_vol": 0.8,  "rr": 0.1, "bf": 0.05, "beta": 0.05},
        "QAR": {"base_spot": 3.64,  "base_rate": 2.25, "cpi": 1.2, "base_vol": 0.8,  "rr": 0.1, "bf": 0.05, "beta": 0.05},
        "RUB": {"base_spot": 62.0,  "base_rate": 6.25, "cpi": 4.0, "base_vol": 15.0, "rr": 3.0, "bf": 0.50, "beta": 0.50},
        "UAH": {"base_spot": 24.0,  "base_rate": 13.5, "cpi": 10.0,"base_vol": 18.0, "rr": 3.5, "bf": 0.55, "beta": 0.40},

        # LatAm
        "CLP": {"base_spot": 750.0, "base_rate": 2.50, "cpi": 3.2, "base_vol": 12.0, "rr": 2.2, "bf": 0.30, "beta": 0.70},
        "COP": {"base_spot": 3300.0,"base_rate": 4.25, "cpi": 3.5, "base_vol": 12.5, "rr": 2.4, "bf": 0.35, "beta": 0.75},
        "PEN": {"base_spot": 3.32,  "base_rate": 2.25, "cpi": 1.9, "base_vol": 5.5,  "rr": 1.0, "bf": 0.18, "beta": 0.45},
        "ARS": {"base_spot": 60.0,  "base_rate": 40.0, "cpi": 50.0,"base_vol": 35.0, "rr": 8.0, "bf": 1.20, "beta": 0.30},

        # Asia
        "CNY": {"base_spot": 6.96,  "base_rate": 4.15, "cpi": 2.8, "base_vol": 4.2,  "rr": 0.5, "bf": 0.10, "beta": 0.35},
        "CNH": {"base_spot": 6.96,  "base_rate": 3.50, "cpi": 2.8, "base_vol": 5.0,  "rr": 0.8, "bf": 0.12, "beta": 0.40},
        "HKD": {"base_spot": 7.78,  "base_rate": 2.00, "cpi": 2.0, "base_vol": 0.6,  "rr": 0.1, "bf": 0.04, "beta": 0.05},
        "SGD": {"base_spot": 1.35,  "base_rate": 1.60, "cpi": 1.5, "base_vol": 4.5,  "rr": 0.3, "bf": 0.08, "beta": 0.35},
        "TWD": {"base_spot": 30.1,  "base_rate": 1.37, "cpi": 1.2, "base_vol": 4.5,  "rr": 0.4, "bf": 0.09, "beta": 0.40},
        "KRW": {"base_spot": 1160.0,"base_rate": 1.25, "cpi": 1.5, "base_vol": 7.0,  "rr": 1.0, "bf": 0.15, "beta": 0.55},
        "INR": {"base_spot": 71.3,  "base_rate": 5.15, "cpi": 4.8, "base_vol": 5.5,  "rr": 0.8, "bf": 0.12, "beta": 0.35},
        "IDR": {"base_spot": 13900.0,"base_rate": 5.0, "cpi": 3.0, "base_vol": 7.5,  "rr": 1.2, "bf": 0.18, "beta": 0.40},
        "PHP": {"base_spot": 50.8,  "base_rate": 4.00, "cpi": 2.6, "base_vol": 5.8,  "rr": 0.7, "bf": 0.12, "beta": 0.40},
        "THB": {"base_spot": 30.2,  "base_rate": 1.25, "cpi": 1.0, "base_vol": 5.5,  "rr": 0.5, "bf": 0.11, "beta": 0.45},
        "MYR": {"base_spot": 4.09,  "base_rate": 3.00, "cpi": 1.8, "base_vol": 5.2,  "rr": 0.6, "bf": 0.12, "beta": 0.40},
        "VND": {"base_spot": 23170.0,"base_rate": 6.00,"cpi": 3.5, "base_vol": 3.5,  "rr": 0.4, "bf": 0.08, "beta": 0.20},
        "PKR": {"base_spot": 155.0, "base_rate": 13.25,"cpi": 12.0,"base_vol": 12.0, "rr": 2.5, "bf": 0.35, "beta": 0.35},

        # SSA
        "NGN": {"base_spot": 360.0, "base_rate": 13.5, "cpi": 12.5,"base_vol": 18.0, "rr": 4.5, "bf": 0.60, "beta": 0.40},
        "KES": {"base_spot": 101.0, "base_rate": 8.5,  "cpi": 5.8, "base_vol": 9.5,  "rr": 1.8, "bf": 0.25, "beta": 0.35},
        "GHS": {"base_spot": 5.7,   "base_rate": 16.0, "cpi": 8.5, "base_vol": 16.5, "rr": 3.5, "bf": 0.50, "beta": 0.45},
        "UGX": {"base_spot": 3670.0,"base_rate": 9.0,  "cpi": 4.0, "base_vol": 8.5,  "rr": 1.5, "bf": 0.22, "beta": 0.30},
        "ZMW": {"base_spot": 14.5,  "base_rate": 11.5, "cpi": 11.0,"base_vol": 20.0, "rr": 4.0, "bf": 0.55, "beta": 0.45},
        "TZS": {"base_spot": 2300.0,"base_rate": 6.0,  "cpi": 3.8, "base_vol": 4.5,  "rr": 0.8, "bf": 0.12, "beta": 0.20},
        "AOA": {"base_spot": 480.0, "base_rate": 15.5, "cpi": 17.0,"base_vol": 19.0, "rr": 3.8, "bf": 0.50, "beta": 0.35},
        "XOF": {"base_spot": 585.0, "base_rate": 2.5,  "cpi": 1.5, "base_vol": 5.5,  "rr": -0.2,"bf": 0.10, "beta": 0.30},

        # Edge
        "KZT": {"base_spot": 382.0, "base_rate": 9.25, "cpi": 5.4, "base_vol": 9.0,  "rr": 1.5, "bf": 0.25, "beta": 0.45},
        "UZS": {"base_spot": 9500.0,"base_rate": 16.0, "cpi": 15.0,"base_vol": 7.5,  "rr": 1.2, "bf": 0.20, "beta": 0.25},
        "TJS": {"base_spot": 9.7,   "base_rate": 12.0, "cpi": 8.0, "base_vol": 8.0,  "rr": 1.2, "bf": 0.20, "beta": 0.25},
        "KGS": {"base_spot": 69.8,  "base_rate": 5.0,  "cpi": 3.5, "base_vol": 7.5,  "rr": 1.0, "bf": 0.18, "beta": 0.30},
        "MNT": {"base_spot": 2730.0,"base_rate": 11.0, "cpi": 6.5, "base_vol": 6.5,  "rr": 1.0, "bf": 0.18, "beta": 0.35},
        "GEL": {"base_spot": 2.87,  "base_rate": 9.0,  "cpi": 7.0, "base_vol": 10.5, "rr": 1.8, "bf": 0.28, "beta": 0.45},
        "AZN": {"base_spot": 1.70,  "base_rate": 7.25, "cpi": 3.0, "base_vol": 1.5,  "rr": 0.2, "bf": 0.06, "beta": 0.08},
        "AMD": {"base_spot": 479.0, "base_rate": 5.5,  "cpi": 1.5, "base_vol": 6.0,  "rr": 0.8, "bf": 0.15, "beta": 0.25},
    }

    for ccy in currencies:
        if ccy not in CURRENCIES:
            continue
        meta = CURRENCIES[ccy]
        p = overrides.get(ccy, region_defaults.get(meta.region, region_defaults["CEEMEA"]))

        # Policy rate and CPI dynamics
        if ccy in ["ARS", "TRY"]:
            rate_series = p["base_rate"] + 30.0 * (dates.year >= 2022) + np.random.normal(0, 0.5, n)
            cpi_series = p["cpi"] + 50.0 * (dates.year >= 2022) + np.random.normal(0, 0.8, n)
        elif meta.region in ["LatAm", "CEEMEA", "SSA", "Edge"]:
            rate_series = p["base_rate"] + 5.0 * (dates.year >= 2022) + np.random.normal(0, 0.2, n)
            cpi_series = p["cpi"] + 3.0 * (dates.year >= 2022) + np.random.normal(0, 0.2, n)
        else:
            rate_series = p["base_rate"] + 2.5 * (dates.year >= 2022) + np.random.normal(0, 0.1, n)
            cpi_series = p["cpi"] + 2.0 * (dates.year >= 2022) + np.random.normal(0, 0.1, n)

        data[meta.policy_rate_ticker] = np.maximum(rate_series, 0.05)
        data[meta.cpi_yoy_ticker] = np.maximum(cpi_series, 0.05)

        # Spot dynamics
        fx_daily_ret = - p["beta"] * spx_ret + np.random.normal(0, p["base_vol"] / 100 / np.sqrt(252), n)
        if ccy in ["TRY", "ARS"]:
            fx_daily_ret += 0.0010  # persistent structural depreciation

        spot_path = p["base_spot"] * np.exp(np.cumsum(fx_daily_ret))
        if ccy == "MXN" and np.any(t_covid_peak):
            spot_path[t_covid_peak] = 25.1

        data[meta.spot_ticker] = spot_path

        # Covered Interest Parity Forwards (1M, 3M, 12M)
        tau_1m = 1.0 / 12.0
        tau_3m = 3.0 / 12.0
        tau_12m = 1.0

        rf = data[meta.policy_rate_ticker] / 100.0
        rd = us_rate / 100.0

        if meta.is_usd_base:
            fwd_1m = spot_path * (1.0 + rf * tau_1m) / (1.0 + rd * tau_1m)
            fwd_3m = spot_path * (1.0 + rf * tau_3m) / (1.0 + rd * tau_3m)
            fwd_12m = spot_path * (1.0 + rf * tau_12m) / (1.0 + rd * tau_12m)
        else:
            fwd_1m = spot_path * (1.0 + rd * tau_1m) / (1.0 + rf * tau_1m)
            fwd_3m = spot_path * (1.0 + rd * tau_3m) / (1.0 + rf * tau_3m)
            fwd_12m = spot_path * (1.0 + rd * tau_12m) / (1.0 + rf * tau_12m)

        data[meta.fwd_1m_ticker] = fwd_1m
        data[meta.fwd_3m_ticker] = fwd_3m
        data[meta.fwd_12m_ticker] = fwd_12m

        # Implied Volatility
        vol_path = p["base_vol"] + (vix - 15.0) * (p["beta"] * 0.4)
        vol_path = np.clip(vol_path, 0.5, 60.0)
        data[meta.vol_1m_ticker] = vol_path
        data[meta.vol_3m_ticker] = vol_path * 0.98 + 0.2

        # 25-Delta Risk Reversal & Butterfly
        rr_path = p["rr"] * (vol_path / max(p["base_vol"], 1.0))
        bf_path = p["bf"] * (vol_path / max(p["base_vol"], 1.0)) ** 0.5
        data[meta.rr_25d_1m_ticker] = rr_path
        data[meta.rr_25d_3m_ticker] = rr_path * 0.95
        data[meta.bf_25d_1m_ticker] = bf_path
        data[meta.bf_25d_3m_ticker] = bf_path

    df = pd.DataFrame(data, index=dates)
    df.index.name = "Date"
    return df
