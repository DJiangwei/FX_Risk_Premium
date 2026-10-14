"""
Chapter 3: Exchange Rates, Interest Rates, Inflation and the Risk Premium.
Implements the decomposition of nominal forward premium into expected inflation differential
and real interest rate differential (the ex-ante fundamental Currency Risk Premium, Eq. 3.13).
"""

from typing import Dict, Optional
import pandas as pd
from ..data.bbg_loader import DataLoader
from ..config import CURRENCIES, GLOBAL_BENCHMARKS


class RealRateModel:
    """
    Decomposes nominal carry into inflation compensation and true economic risk premium:
    Eq. (3.13): (r_f^p - r_d^p) = (r_f - r_d) - (pi_f - pi_d) = r_f^{real} - r_d^{real}.
    """

    def __init__(self, data_loader: DataLoader):
        self.loader = data_loader
        self.universe_mgr = data_loader.universe_mgr

    def get_real_policy_rate(self, ccy: str) -> pd.Series:
        """
        Calculate ex-ante real interest rate: Nominal Policy Rate - CPI YoY.
        """
        nom_rate = self.loader.get_policy_rate(ccy)
        cpi = self.loader.get_cpi_yoy(ccy)
        return nom_rate - cpi

    def get_us_real_rate(self) -> pd.Series:
        """Calculate US real interest rate: Fed Funds - US CPI YoY."""
        us_nom = self.loader.get_global_benchmark("US_FED_FUNDS")
        us_cpi = self.loader.get_global_benchmark("US_CPI_YOY")
        return us_nom - us_cpi

    def calculate_real_carry(self, ccy: str) -> pd.Series:
        """
        Calculate Real Rate Differential / Fundamental Currency Risk Premium:
        r_f^{real} - r_d^{real}.
        """
        real_f = self.get_real_policy_rate(ccy)
        real_d = self.get_us_real_rate()
        return real_f - real_d

    def decompose_carry(self, ccy: str, tenor: str = "1M") -> pd.DataFrame:
        """
        Decomposes nominal rate differential into:
        1. Inflation Differential: pi_f - pi_d
        2. Real Yield Differential (Currency Risk Premium): r_f^{real} - r_d^{real}
        """
        nom_f = self.loader.get_policy_rate(ccy)
        nom_d = self.loader.get_global_benchmark("US_FED_FUNDS")
        cpi_f = self.loader.get_cpi_yoy(ccy)
        cpi_d = self.loader.get_global_benchmark("US_CPI_YOY")

        nom_diff = nom_f - nom_d
        infl_diff = cpi_f - cpi_d
        real_diff = (nom_f - cpi_f) - (nom_d - cpi_d)

        df = pd.DataFrame({
            "Nominal_Spread_%": nom_diff,
            "Inflation_Differential_%": infl_diff,
            "Real_Risk_Premium_%": real_diff
        }, index=nom_f.index)
        return df

    def cross_sectional_real_rate_summary(self, date: Optional[str] = None) -> pd.DataFrame:
        """Cross-sectional comparison of nominal rate, inflation, and real risk premium."""
        records = []
        us_real = self.get_us_real_rate()

        for ccy in self.universe_mgr.codes:
            meta = CURRENCIES[ccy]
            nom_rate = self.loader.get_policy_rate(ccy)
            cpi = self.loader.get_cpi_yoy(ccy)
            real_rate = nom_rate - cpi
            real_carry = real_rate - us_real

            target_idx = -1 if date is None else real_rate.index.get_indexer([pd.Timestamp(date)], method="nearest")[0]

            records.append({
                "Currency": ccy,
                "Region": meta.region,
                "Nominal_Policy_Rate_%": nom_rate.iloc[target_idx],
                "CPI_YoY_%": cpi.iloc[target_idx],
                "Real_Policy_Rate_%": real_rate.iloc[target_idx],
                "Real_Carry_vs_USD_%": real_carry.iloc[target_idx]
            })

        df = pd.DataFrame(records).sort_values(by="Real_Carry_vs_USD_%", ascending=False)
        return df.reset_index(drop=True)
