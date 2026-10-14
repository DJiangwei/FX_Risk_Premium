"""
EM FX Risk Premium Quickstart Demo
Demonstrates how to fetch data, compute the multi-dimensional FX Risk Premium metrics,
generate cross-sectional scorecards, and run portfolio backtests.
"""

import os
from pathlib import Path
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend
import matplotlib.pyplot as plt

from em_fx_rp.data.bbg_loader import DataLoader
from em_fx_rp.models.carry import CarryModel
from em_fx_rp.models.real_rate import RealRateModel
from em_fx_rp.models.factor_beta import FactorBetaModel
from em_fx_rp.models.options_vrp import OptionsVRPModel
from em_fx_rp.models.composite import CompositeRiskPremiumModel
from em_fx_rp.trading.backtest import PortfolioBacktest
from em_fx_rp.visualization.plots import (
    plot_cross_sectional_scorecard,
    plot_carry_decomposition,
    plot_risk_neutral_density,
    plot_backtest_performance
)


def main():
    print("=" * 80)
    print("EM FX RISK PREMIUM PIPELINE (Based on Adam S. Iqbal, 2022)")
    print("=" * 80)

    # 1. Initialize DataLoader for Core EM FX Universe
    print("\n[1/5] Initializing Universe and Ingesting Market Data...")
    universe = ["MXN", "BRL", "ZAR", "PLN", "HUF", "TRY", "KRW", "INR", "IDR", "CLP", "COP"]
    loader = DataLoader(universe=universe, use_cache=True)
    loader.fetch_data(start_date="2020-01-01", end_date="2023-12-31")
    print(f"Data ready for {len(universe)} currencies across {len(loader.data)} daily observations.")

    # 2. Compute Cross-Sectional Scorecard (FX-RPS)
    print("\n[2/5] Computing Multi-Dimensional Composite Risk Premium Scorecard (FX-RPS)...")
    comp_model = CompositeRiskPremiumModel(loader)
    scorecard = comp_model.compute_scorecard()

    print("\n--- EM FX RISK PREMIUM SCORECARD ---")
    cols_to_print = ["Rank", "Currency", "Region", "Real_Carry", "Carry_to_Vol", "Skew_Ratio", "SPX_Beta", "FX_RPS"]
    formatted_df = scorecard[cols_to_print].copy()
    formatted_df["Real_Carry"] = formatted_df["Real_Carry"].map("{:+.2f}%".format)
    formatted_df["Carry_to_Vol"] = formatted_df["Carry_to_Vol"].map("{:.2f}".format)
    formatted_df["Skew_Ratio"] = formatted_df["Skew_Ratio"].map("{:.2f}".format)
    formatted_df["SPX_Beta"] = formatted_df["SPX_Beta"].map("{:.2f}".format)
    formatted_df["FX_RPS"] = formatted_df["FX_RPS"].map("{:+.3f}".format)
    print(formatted_df.to_string(index=False))

    # 3. Carry Decomposition (Iqbal Eq. 3.13) for MXN
    print("\n[3/5] Decomposing MXN Carry into Real Risk Premium vs Inflation Differential...")
    real_model = RealRateModel(loader)
    mxn_decomp = real_model.decompose_carry("MXN")
    print(mxn_decomp.tail())

    # 4. Extract Risk-Neutral Q-Density (Breeden-Litzenberger) for MXN
    print("\n[4/5] Reconstructing Options-Implied Q-Distribution for MXN...")
    options_model = OptionsVRPModel(loader)
    strikes, q_pdf = options_model.reconstruct_risk_neutral_density("MXN", tenor="1M")

    # 5. Run Long/Short Backtest
    print("\n[5/5] Backtesting Top 3 Long / Bottom 3 Short Carry & Risk Premium Strategy...")
    backtest = PortfolioBacktest(loader, top_n=3, bottom_n=3, long_only=False)
    bt_res = backtest.run(start_date="2020-06-01")
    stats = backtest.get_summary_stats(bt_res)

    print("\n--- BACKTEST PERFORMANCE SUMMARY ---")
    for k, v in stats.items():
        print(f"  {k:25s}: {v:+.2f}")

    # Generate and save output charts
    out_dir = Path("examples/output")
    out_dir.mkdir(parents=True, exist_ok=True)

    plot_cross_sectional_scorecard(scorecard, save_path=str(out_dir / "fx_rps_scorecard.png"))
    plot_carry_decomposition(mxn_decomp, title="MXN: Nominal Spread vs Real Currency Risk Premium (Eq. 3.13)", save_path=str(out_dir / "mxn_carry_decomp.png"))
    plot_risk_neutral_density(strikes, q_pdf, ccy="USDMXN", save_path=str(out_dir / "mxn_q_density.png"))
    plot_backtest_performance(bt_res, title="EM FX Long/Short Risk Premium Strategy (2020-2023)", save_path=str(out_dir / "backtest_nav.png"))

    print(f"\nAll visual charts saved successfully to: {out_dir.absolute()}/")


if __name__ == "__main__":
    main()
