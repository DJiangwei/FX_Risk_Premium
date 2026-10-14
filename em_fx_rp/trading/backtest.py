"""
Walk-forward portfolio simulator for cross-sectional EM FX Risk Premium strategies.
"""

from typing import List, Dict, Optional
import numpy as np
import pandas as pd
from ..data.bbg_loader import DataLoader
from ..models.composite import CompositeRiskPremiumModel
from ..models.carry import CarryModel


class PortfolioBacktest:
    """
    Backtests a rank-based Long/Short or Long-Only Carry & Risk Premium portfolio.
    Rebalances monthly based on Composite Risk Premium Score (FX-RPS).
    """

    def __init__(
        self,
        data_loader: DataLoader,
        top_n: int = 3,
        bottom_n: int = 3,
        long_only: bool = False
    ):
        self.loader = data_loader
        self.composite_model = CompositeRiskPremiumModel(data_loader)
        self.carry_model = CarryModel(data_loader)
        self.top_n = top_n
        self.bottom_n = bottom_n
        self.long_only = long_only

    def run(
        self,
        rebalance_freq: str = "BME",
        start_date: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Run the monthly walk-forward simulation.
        Returns daily portfolio equity curve, drawdowns, and performance metrics.
        """
        df_all = self.loader.data
        if start_date:
            df_all = df_all.loc[start_date:]

        rebal_dates = df_all.resample(rebalance_freq).last().index
        rebal_dates = [d for d in rebal_dates if d in df_all.index]

        # Precompute daily returns for all currencies
        daily_rets = pd.DataFrame(index=df_all.index)
        daily_carries = pd.DataFrame(index=df_all.index)

        for ccy in self.loader.universe_mgr.codes:
            # Spot return of holding long CCY vs USD
            spot = self.loader.get_spot(ccy)
            meta = self.loader.universe_mgr.currencies[ccy]
            if meta.is_usd_base:
                ret = - np.log(spot / spot.shift(1))
            else:
                ret = np.log(spot / spot.shift(1))
            daily_rets[ccy] = ret

            # Carry accrued daily (approx annual carry / 252)
            carry_ann = self.carry_model.calculate_annualized_carry(ccy, tenor="1M")
            daily_carries[ccy] = carry_ann / 252.0

        portfolio_rets = pd.Series(0.0, index=df_all.index)

        for i in range(len(rebal_dates) - 1):
            t_curr = rebal_dates[i]
            t_next = rebal_dates[i + 1]

            # Compute score card on rebalance date
            scorecard = self.composite_model.compute_scorecard(date=str(t_curr.date()))
            longs = scorecard.head(self.top_n)["Currency"].tolist()
            shorts = scorecard.tail(self.bottom_n)["Currency"].tolist() if not self.long_only else []

            period_idx = (df_all.index > t_curr) & (df_all.index <= t_next)

            # Long leg returns (Spot + Carry)
            long_leg = (daily_rets.loc[period_idx, longs] + daily_carries.loc[period_idx, longs]).mean(axis=1)

            if not self.long_only and shorts:
                # Short leg returns: short spot minus carry paid
                short_leg = (- daily_rets.loc[period_idx, shorts] - daily_carries.loc[period_idx, shorts]).mean(axis=1)
                port_ret = 0.5 * long_leg + 0.5 * short_leg
            else:
                port_ret = long_leg

            portfolio_rets.loc[period_idx] = port_ret

        # Calculate metrics
        portfolio_rets = portfolio_rets.fillna(0.0)
        cum_ret = (1.0 + portfolio_rets).cumprod()
        running_max = cum_ret.cummax()
        drawdown = (cum_ret - running_max) / running_max

        result = pd.DataFrame({
            "daily_return": portfolio_rets,
            "cumulative_return": cum_ret,
            "drawdown": drawdown
        })
        return result

    @staticmethod
    def get_summary_stats(res_df: pd.DataFrame) -> Dict[str, float]:
        """Compute annualized metrics (Return, Volatility, Sharpe, Max Drawdown)."""
        ret = res_df["daily_return"].dropna()
        ann_return = float(ret.mean() * 252)
        ann_vol = float(ret.std() * np.sqrt(252))
        sharpe = ann_return / ann_vol if ann_vol > 0 else 0.0
        max_dd = float(res_df["drawdown"].min())
        hit_rate = float((ret > 0).mean())

        return {
            "Annualized_Return_%": ann_return * 100.0,
            "Annualized_Vol_%": ann_vol * 100.0,
            "Sharpe_Ratio": sharpe,
            "Max_Drawdown_%": max_dd * 100.0,
            "Daily_Hit_Rate_%": hit_rate * 100.0
        }
