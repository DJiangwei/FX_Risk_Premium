"""
Chapter 1 & 2: Macro Factor Covariance, Pricing Kernel, and CAPM Beta.
Measures the currency's sensitivity to global marginal utility / wealth shocks (proxied by S&P 500 / VIX).
"""

from typing import Dict, Optional
import numpy as np
import pandas as pd
from ..data.bbg_loader import DataLoader
from ..config import CURRENCIES, GLOBAL_BENCHMARKS


class FactorBetaModel:
    """
    Computes rolling empirical SDF covariance and macro factor betas (Eq. 1.37 & Eq. 2.10):
    E_t^P[(S_T - F_t) / S_t] approx beta_{FX, M} * lambda_M.
    """

    def __init__(self, data_loader: DataLoader):
        self.loader = data_loader
        self.universe_mgr = data_loader.universe_mgr

    def get_currency_returns(self, ccy: str) -> pd.Series:
        """
        Daily log returns of holding foreign currency against USD:
        Positive return = Foreign Currency appreciates against USD.
        """
        spot = self.loader.get_spot(ccy)
        meta = CURRENCIES[ccy]
        if meta.is_usd_base:
            # Market quote USD/CCY: appreciation of CCY means spot falls
            ret = - np.log(spot / spot.shift(1))
        else:
            # Market quote CCY/USD: appreciation of CCY means spot rises
            ret = np.log(spot / spot.shift(1))
        return ret.dropna()

    def get_spx_returns(self) -> pd.Series:
        """Daily log returns of global market proxy (S&P 500)."""
        spx = self.loader.get_global_benchmark("SPX")
        return np.log(spx / spx.shift(1)).dropna()

    def calculate_rolling_beta(self, ccy: str, window: int = 63) -> pd.Series:
        """
        Rolling CAPM beta to S&P 500: Cov(R_FX, R_SPX) / Var(R_SPX).
        A high positive beta indicates high pro-cyclical risk (crashes during recessions).
        """
        r_fx = self.get_currency_returns(ccy)
        r_spx = self.get_spx_returns()

        aligned = pd.concat([r_fx, r_spx], axis=1, join="inner").dropna()
        cov = aligned.iloc[:, 0].rolling(window).cov(aligned.iloc[:, 1])
        var_spx = aligned.iloc[:, 1].rolling(window).var()
        beta = cov / var_spx
        return beta

    def calculate_rolling_correlation(self, ccy: str, window: int = 63) -> pd.Series:
        """Rolling correlation with S&P 500."""
        r_fx = self.get_currency_returns(ccy)
        r_spx = self.get_spx_returns()
        aligned = pd.concat([r_fx, r_spx], axis=1, join="inner").dropna()
        return aligned.iloc[:, 0].rolling(window).corr(aligned.iloc[:, 1])

    def calculate_vix_sensitivity(self, ccy: str, window: int = 63) -> pd.Series:
        """
        Sensitivity to VIX changes: d(R_FX) / d(VIX).
        Typically negative for EM FX (depreciates when VIX spikes).
        """
        r_fx = self.get_currency_returns(ccy)
        vix = self.loader.get_global_benchmark("VIX")
        dvix = vix.diff().dropna()
        aligned = pd.concat([r_fx, dvix], axis=1, join="inner").dropna()
        cov = aligned.iloc[:, 0].rolling(window).cov(aligned.iloc[:, 1])
        var_vix = aligned.iloc[:, 1].rolling(window).var()
        return cov / var_vix

    def cross_sectional_beta_summary(self, window: int = 63, date: Optional[str] = None) -> pd.DataFrame:
        """Cross-sectional factor beta and correlation summary across the universe."""
        records = []
        for ccy in self.universe_mgr.codes:
            meta = CURRENCIES[ccy]
            beta = self.calculate_rolling_beta(ccy, window=window)
            corr = self.calculate_rolling_correlation(ccy, window=window)
            vix_sens = self.calculate_vix_sensitivity(ccy, window=window)

            target_idx = -1 if date is None else beta.index.get_indexer([pd.Timestamp(date)], method="nearest")[0]

            records.append({
                "Currency": ccy,
                "Region": meta.region,
                "SPX_Beta": beta.iloc[target_idx],
                "SPX_Correlation": corr.iloc[target_idx],
                "VIX_Sensitivity": vix_sens.iloc[target_idx]
            })

        df = pd.DataFrame(records).sort_values(by="SPX_Beta", ascending=False)
        return df.reset_index(drop=True)
