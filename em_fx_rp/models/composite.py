"""
Composite EM FX Risk Premium Model (FX-RPS).
Integrates Carry, Real Rates, Equity Factor Beta, and Options Tail Skew into a unified scorecard.
"""

from typing import Dict, Optional
import numpy as np
import pandas as pd
from ..data.bbg_loader import DataLoader
from .carry import CarryModel
from .real_rate import RealRateModel
from .factor_beta import FactorBetaModel
from .options_vrp import OptionsVRPModel


class CompositeRiskPremiumModel:
    """
    Synthesizes the multi-dimensional asset pricing metrics of Iqbal (2022) into
    the Composite EM FX Risk Premium Score (FX-RPS).
    """

    def __init__(
        self,
        data_loader: DataLoader,
        weights: Optional[Dict[str, float]] = None
    ):
        self.loader = data_loader
        self.universe_mgr = data_loader.universe_mgr

        self.carry_model = CarryModel(data_loader)
        self.real_model = RealRateModel(data_loader)
        self.beta_model = FactorBetaModel(data_loader)
        self.options_model = OptionsVRPModel(data_loader)

        # Default weights balancing fundamental carry vs market-implied risk
        self.weights = weights or {
            "real_carry": 0.35,     # Weight on Real Rate Differential (Eq. 3.13)
            "carry_to_vol": 0.25,   # Weight on Sharpe proxy Carry-to-Risk (Chapter 2)
            "vrp": 0.15,            # Weight on Volatility Risk Premium (Chapter 4)
            "skew_penalty": 0.15,   # Penalty for high crash risk (Risk Reversal)
            "beta_penalty": 0.10    # Penalty for high pro-cyclical wealth exposure (Eq. 2.10)
        }

    def compute_scorecard(self, date: Optional[str] = None, tenor: str = "1M") -> pd.DataFrame:
        """
        Calculates cross-sectional Z-scores and aggregated FX-RPS ranking for all currencies in the universe.
        """
        rows = []
        for ccy in self.universe_mgr.codes:
            meta = self.universe_mgr.currencies[ccy]

            # 1. Real Carry
            real_carry = self.real_model.calculate_real_carry(ccy)
            # 2. Carry to Vol
            c2v = self.carry_model.calculate_carry_to_risk(ccy, tenor=tenor, vol_type="implied")
            # 3. VRP
            vrp = self.options_model.calculate_vrp(ccy, tenor=tenor)
            # 4. Skew Ratio
            skew = self.options_model.calculate_skew_ratio(ccy, tenor=tenor)
            # 5. SPX Beta
            beta = self.beta_model.calculate_rolling_beta(ccy, window=63)

            # Target date index
            target_idx = -1 if date is None else real_carry.index.get_indexer([pd.Timestamp(date)], method="nearest")[0]

            rows.append({
                "Currency": ccy,
                "Region": meta.region,
                "Real_Carry": float(real_carry.iloc[target_idx]),
                "Carry_to_Vol": float(c2v.iloc[target_idx]),
                "VRP": float(vrp.iloc[target_idx]),
                "Skew_Ratio": float(skew.iloc[target_idx]),
                "SPX_Beta": float(beta.iloc[target_idx])
            })

        df = pd.DataFrame(rows)

        # Standardize features across universe (Z-score)
        def zscore(col: pd.Series) -> pd.Series:
            std = col.std()
            return (col - col.mean()) / (std if std > 1e-6 else 1.0)

        df["z_real_carry"] = zscore(df["Real_Carry"])
        df["z_carry_to_vol"] = zscore(df["Carry_to_Vol"])
        df["z_vrp"] = zscore(df["VRP"])
        df["z_skew"] = zscore(df["Skew_Ratio"])
        df["z_beta"] = zscore(df["SPX_Beta"])

        # Composite Score FX-RPS
        w = self.weights
        df["FX_RPS"] = (
            w["real_carry"] * df["z_real_carry"]
            + w["carry_to_vol"] * df["z_carry_to_vol"]
            + w["vrp"] * df["z_vrp"]
            - w["skew_penalty"] * df["z_skew"]
            - w["beta_penalty"] * df["z_beta"]
        )

        df = df.sort_values(by="FX_RPS", ascending=False).reset_index(drop=True)
        df["Rank"] = np.arange(1, len(df) + 1)
        return df
