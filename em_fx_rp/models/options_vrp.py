"""
Chapter 4: FX Volatility, FX Options, Volatility Risk Premium (VRP), and Skewness.
Implements VRP (IV - RV), 25d Risk Reversal skew (Crash Risk Premium), 25d Butterfly (kurtosis),
and the 3-point delta smile model (Eq. 4.9) with Breeden-Litzenberger Q-density reconstruction.
"""

from typing import Dict, Optional, Tuple
import numpy as np
import pandas as pd
from scipy.stats import norm
from ..data.bbg_loader import DataLoader
from ..config import CURRENCIES


class OptionsVRPModel:
    """
    Computes options-implied tail risk, skewness, and volatility risk premiums:
    1. Volatility Risk Premium (VRP = IV - RV)
    2. Crash Risk Premium (25d Risk Reversal Skew Ratio = RR / ATM)
    3. Tail Kurtosis Premium (25d Butterfly)
    4. 3-Point Smile Model (Eq. 4.9) & Breeden-Litzenberger Risk-Neutral Density
    """

    def __init__(self, data_loader: DataLoader):
        self.loader = data_loader
        self.universe_mgr = data_loader.universe_mgr

    def calculate_vrp(self, ccy: str, tenor: str = "1M", rv_window: int = 21) -> pd.Series:
        """
        Volatility Risk Premium: IV_ATM - RV (annualized %).
        Positive VRP indicates options trade at an insurance premium over realized moves.
        """
        iv = self.loader.get_implied_vol(ccy, tenor=tenor)
        spot = self.loader.get_spot(ccy)
        log_ret = np.log(spot / spot.shift(1))
        rv = log_ret.rolling(window=rv_window).std() * np.sqrt(252) * 100.0
        return iv - rv

    def calculate_skew_ratio(self, ccy: str, tenor: str = "1M") -> pd.Series:
        """
        Normalized Crash Risk Premium / Skew Ratio: 25d RR / ATM Vol.
        In USD/EM quotes, higher positive ratio means higher priced EM crash risk.
        """
        rr = self.loader.get_risk_reversal(ccy, tenor=tenor)
        atm = self.loader.get_implied_vol(ccy, tenor=tenor)
        return rr / atm

    def get_smile_parameters(self, ccy: str, tenor: str = "1M", date: Optional[str] = None) -> Dict[str, float]:
        """
        Retrieve atm_vol, rr_25d, bf_25d for smile reconstruction.
        """
        atm = self.loader.get_implied_vol(ccy, tenor=tenor)
        rr = self.loader.get_risk_reversal(ccy, tenor=tenor)
        bf = self.loader.get_butterfly(ccy, tenor=tenor)

        target_idx = -1 if date is None else atm.index.get_indexer([pd.Timestamp(date)], method="nearest")[0]

        return {
            "atm": float(atm.iloc[target_idx]),
            "rr": float(rr.iloc[target_idx]),
            "bf": float(bf.iloc[target_idx]),
            "date": str(atm.index[target_idx].date())
        }

    @staticmethod
    def eval_3point_smile(delta: np.ndarray, atm: float, rr: float, bf: float) -> np.ndarray:
        """
        Iqbal (2022) Eq. (4.9):
        sigma_implied(delta) = sigma_atm - 2 * sigma_rr * (delta - 0.5) + 16 * sigma_bf * (delta - 0.5)^2
        """
        d_diff = delta - 0.5
        return atm - 2.0 * rr * d_diff + 16.0 * bf * (d_diff ** 2)

    def reconstruct_risk_neutral_density(
        self,
        ccy: str,
        tenor: str = "1M",
        date: Optional[str] = None,
        n_points: int = 200
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Reconstructs the risk-neutral Q probability density function Q(S_T = K)
        using Iqbal's 3-point smile and Breeden-Litzenberger formula:
        Q(S_T = K) = e^{r_d tau} * d^2 C / dK^2.
        """
        params = self.get_smile_parameters(ccy, tenor=tenor, date=date)
        atm = params["atm"] / 100.0
        rr = params["rr"] / 100.0
        bf = params["bf"] / 100.0

        spot = float(self.loader.get_spot(ccy).iloc[-1 if date is None else -1])
        fwd = float(self.loader.get_forward(ccy, tenor=tenor).iloc[-1 if date is None else -1])

        tau = 1.0 / 12.0 if tenor.upper() == "1M" else 3.0 / 12.0
        rd = float(self.loader.get_global_benchmark("US_FED_FUNDS").iloc[-1 if date is None else -1]) / 100.0

        # Discretize strikes around forward
        vol_scale = atm * np.sqrt(tau)
        k_min = fwd * np.exp(-3.5 * vol_scale)
        k_max = fwd * np.exp(3.5 * vol_scale)
        strikes = np.linspace(k_min, k_max, n_points)
        dk = strikes[1] - strikes[0]

        # Invert Black-Scholes call delta to map strike to delta
        # Delta = e^{-rf tau} * N(d1), approximate delta with N(d1)
        # Using iterative / heuristic delta mapping
        d1_approx = (np.log(fwd / strikes) + 0.5 * (atm ** 2) * tau) / (atm * np.sqrt(tau))
        deltas = np.clip(norm.cdf(d1_approx), 0.01, 0.99)

        # Implied vol across strikes from Iqbal 3-point delta formula
        vols = self.eval_3point_smile(deltas, atm, rr, bf)
        vols = np.maximum(vols, 0.01)

        # Black-Scholes call prices
        d1 = (np.log(fwd / strikes) + 0.5 * (vols ** 2) * tau) / (vols * np.sqrt(tau))
        d2 = d1 - vols * np.sqrt(tau)
        df = np.exp(-rd * tau)
        call_prices = df * (fwd * norm.cdf(d1) - strikes * norm.cdf(d2))

        # Numerical second derivative (Breeden-Litzenberger)
        # d^2 C / dK^2 approx (C[i+1] - 2*C[i] + C[i-1]) / dk^2
        q_pdf = np.zeros_like(strikes)
        q_pdf[1:-1] = np.exp(rd * tau) * (call_prices[2:] - 2 * call_prices[1:-1] + call_prices[:-2]) / (dk ** 2)
        q_pdf = np.maximum(q_pdf, 0.0)

        # Normalize area to 1
        total_area = np.sum(q_pdf) * dk
        if total_area > 0:
            q_pdf /= total_area

        return strikes, q_pdf

    def cross_sectional_options_summary(self, tenor: str = "1M", date: Optional[str] = None) -> pd.DataFrame:
        """Cross-sectional options risk premium summary: ATM vol, VRP, Risk Reversal skew, Butterfly."""
        records = []
        for ccy in self.universe_mgr.codes:
            meta = CURRENCIES[ccy]
            atm = self.loader.get_implied_vol(ccy, tenor=tenor)
            rr = self.loader.get_risk_reversal(ccy, tenor=tenor)
            bf = self.loader.get_butterfly(ccy, tenor=tenor)
            vrp = self.calculate_vrp(ccy, tenor=tenor)
            skew_ratio = self.calculate_skew_ratio(ccy, tenor=tenor)

            target_idx = -1 if date is None else atm.index.get_indexer([pd.Timestamp(date)], method="nearest")[0]

            records.append({
                "Currency": ccy,
                "Region": meta.region,
                "ATM_Vol_%": atm.iloc[target_idx],
                "VRP_%": vrp.iloc[target_idx],
                "Risk_Reversal_25d_%": rr.iloc[target_idx],
                "Butterfly_25d_%": bf.iloc[target_idx],
                "Skew_Ratio_(RR/ATM)": skew_ratio.iloc[target_idx]
            })

        df = pd.DataFrame(records).sort_values(by="Skew_Ratio_(RR/ATM)", ascending=False)
        return df.reset_index(drop=True)
