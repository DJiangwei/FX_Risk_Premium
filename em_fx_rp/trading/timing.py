"""
Tactical timing and drawdown protection rules based on Section 2.3.1.1 of Iqbal (2022):
'Practical Consideration on Implementation of the Carry Trade'.
"""

import numpy as np
import pandas as pd
from ..data.bbg_loader import DataLoader


class VolatilityTimingRule:
    """
    Dynamically scales portfolio leverage based on global volatility regimes.
    Avoids entering carry trades during acute repricing spikes and scales up
    after volatility peaks and stabilizes.
    """

    def __init__(
        self,
        data_loader: DataLoader,
        vix_threshold: float = 25.0,
        vol_lookback: int = 21
    ):
        self.loader = data_loader
        self.vix_threshold = vix_threshold
        self.vol_lookback = vol_lookback

    def compute_allocation_signal(self) -> pd.Series:
        """
        Calculates daily capital allocation multiplier in [0.0, 1.0]:
        1.0 = Full allocation (low volatility / calm regime)
        0.5 = Moderate de-risking (elevated vol)
        0.0 = Complete risk-off cash protection (acute shock / repricing)
        """
        vix = self.loader.get_global_benchmark("VIX")
        vix_ma = vix.rolling(self.vol_lookback).mean()
        vix_change = vix / vix_ma

        signal = pd.Series(1.0, index=vix.index)

        # De-risk when VIX exceeds threshold or spikes by more than 25% above its moving average
        stress_condition = (vix > self.vix_threshold) | (vix_change > 1.25)
        signal[stress_condition] = 0.3

        extreme_stress = (vix > 35.0) | (vix_change > 1.50)
        signal[extreme_stress] = 0.0

        return signal.shift(1).fillna(1.0)
