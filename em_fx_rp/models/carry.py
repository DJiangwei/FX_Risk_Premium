"""
Chapter 2: FX Forwards, CIP, UIP, and the Carry Trade.
Calculates nominal carry, forward premiums, and risk-adjusted carry ratios.
"""

from typing import Dict, List, Optional
import numpy as np
import pandas as pd
from ..data.bbg_loader import DataLoader
from ..config import CURRENCIES


class CarryModel:
    """
    Computes nominal carry, forward points, CIP implied yield differentials,
    and Carry-to-Risk ratios as detailed in Iqbal (2022) Chapter 2.
    """

    def __init__(self, data_loader: DataLoader):
        self.loader = data_loader
        self.universe_mgr = data_loader.universe_mgr

    def calculate_annualized_carry(self, ccy: str, tenor: str = "1M") -> pd.Series:
        """
        Calculate annualized carry earned by going LONG foreign currency against USD.
        Annualized Carry approx (r_foreign - r_usd).
        """
        spot = self.loader.get_spot(ccy)
        fwd = self.loader.get_forward(ccy, tenor=tenor)
        meta = CURRENCIES[ccy]

        tau = 1.0 / 12.0 if tenor.upper() == "1M" else (3.0 / 12.0 if tenor.upper() == "3M" else 1.0)

        if meta.is_usd_base:
            # Market quote is USD/CCY (e.g. USDMXN = 18.0, Fwd = 18.15)
            # Long foreign currency earns forward points: (Fwd - Spot) / Spot / tau
            carry = (fwd - spot) / spot / tau
        else:
            # Market quote is CCY/USD (e.g. EURUSD = 1.08, Fwd = 1.082)
            # Long EUR earns: (Spot - Fwd) / Spot / tau
            carry = (spot - fwd) / spot / tau

        return carry

    def calculate_realized_volatility(self, ccy: str, window: int = 63) -> pd.Series:
        """
        Calculate rolling annualized realized volatility from daily spot log returns.
        """
        spot = self.loader.get_spot(ccy)
        log_ret = np.log(spot / spot.shift(1))
        realized_vol = log_ret.rolling(window=window).std() * np.sqrt(252)
        return realized_vol

    def calculate_carry_to_risk(self, ccy: str, tenor: str = "1M", vol_type: str = "implied") -> pd.Series:
        """
        Calculate Carry-to-Risk (Sharpe ratio proxy):
        Carry / Implied Vol (or Realized Vol).
        """
        carry = self.calculate_annualized_carry(ccy, tenor=tenor)
        if vol_type.lower() == "implied":
            vol = self.loader.get_implied_vol(ccy, tenor=tenor) / 100.0
        else:
            vol = self.calculate_realized_volatility(ccy, window=63)
        return carry / vol

    def cross_sectional_carry_summary(self, date: Optional[str] = None, tenor: str = "1M") -> pd.DataFrame:
        """
        Generate cross-sectional carry and carry-to-risk summary table across all currencies in universe.
        """
        records = []
        for ccy in self.universe_mgr.codes:
            meta = CURRENCIES[ccy]
            carry = self.calculate_annualized_carry(ccy, tenor=tenor)
            c2r_imp = self.calculate_carry_to_risk(ccy, tenor=tenor, vol_type="implied")
            c2r_real = self.calculate_carry_to_risk(ccy, tenor=tenor, vol_type="realized")
            implied_vol = self.loader.get_implied_vol(ccy, tenor=tenor)
            real_vol = self.calculate_realized_volatility(ccy) * 100.0
            spot = self.loader.get_spot(ccy)
            fwd = self.loader.get_forward(ccy, tenor=tenor)

            target_idx = -1 if date is None else carry.index.get_indexer([pd.Timestamp(date)], method="nearest")[0]

            records.append({
                "Currency": ccy,
                "Region": meta.region,
                "Spot": spot.iloc[target_idx],
                "Forward": fwd.iloc[target_idx],
                "Annualized_Carry_%": carry.iloc[target_idx] * 100.0,
                "Implied_Vol_%": implied_vol.iloc[target_idx],
                "Realized_Vol_%": real_vol.iloc[target_idx],
                "Carry_to_Implied_Vol": c2r_imp.iloc[target_idx],
                "Carry_to_Realized_Vol": c2r_real.iloc[target_idx]
            })

        df = pd.DataFrame(records).sort_values(by="Carry_to_Implied_Vol", ascending=False)
        return df.reset_index(drop=True)
