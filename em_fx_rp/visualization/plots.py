"""
Matplotlib-based visualization routines for EM FX Risk Premium metrics and strategies.
"""

from typing import Optional
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def plot_cross_sectional_scorecard(scorecard_df: pd.DataFrame, save_path: Optional[str] = None):
    """Horizontal bar chart ranking currencies by FX-RPS."""
    df_sorted = scorecard_df.sort_values(by="FX_RPS", ascending=True)

    fig, ax = plt.subplots(figsize=(10, 6))
    colors = ["#2ecc71" if x > 0 else "#e74c3c" for x in df_sorted["FX_RPS"]]

    ax.barh(df_sorted["Currency"], df_sorted["FX_RPS"], color=colors, alpha=0.85, edgecolor="black")
    ax.axvline(0, color="grey", linestyle="--", linewidth=0.8)

    ax.set_title("EM FX Composite Risk Premium Score (FX-RPS)", fontsize=14, fontweight="bold")
    ax.set_xlabel("FX-RPS (Multi-Factor Z-Score)", fontsize=12)
    ax.grid(axis="x", linestyle=":", alpha=0.6)

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=300)
    return fig


def plot_carry_decomposition(decomp_df: pd.DataFrame, title: str = "Carry Decomposition", save_path: Optional[str] = None):
    """
    Plots stacked visualization of Eq. 3.13:
    Nominal Carry = Inflation Differential + Real Risk Premium.
    """
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(decomp_df.index, decomp_df["Nominal_Spread_%"], label="Nominal Rate Spread", color="#2c3e50", linewidth=1.8)
    ax.plot(decomp_df.index, decomp_df["Real_Risk_Premium_%"], label="Real Risk Premium (Eq. 3.13)", color="#27ae60", linewidth=2.0)
    ax.plot(decomp_df.index, decomp_df["Inflation_Differential_%"], label="Inflation Differential (pi_f - pi_d)", color="#e67e22", linestyle="--", linewidth=1.5)

    ax.set_title(title, fontsize=13, fontweight="bold")
    ax.set_ylabel("Annualized %", fontsize=11)
    ax.legend(loc="upper left")
    ax.grid(True, linestyle=":", alpha=0.5)

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=300)
    return fig


def plot_risk_neutral_density(strikes: np.ndarray, q_pdf: np.ndarray, ccy: str, save_path: Optional[str] = None):
    """
    Plots Breeden-Litzenberger risk-neutral PDF Q(S_T = K) extracted from options smile.
    """
    fig, ax = plt.subplots(figsize=(9, 5))
    ax.plot(strikes, q_pdf, color="#8e44ad", linewidth=2.2, label=f"Risk-Neutral Q-PDF ({ccy})")
    ax.fill_between(strikes, q_pdf, color="#8e44ad", alpha=0.2)

    ax.set_title(f"Options-Implied Risk Neutral Density Q(S_T = K): {ccy}", fontsize=13, fontweight="bold")
    ax.set_xlabel("Strike / Spot at Expiry (K)", fontsize=11)
    ax.set_ylabel("Probability Density", fontsize=11)
    ax.legend()
    ax.grid(True, linestyle=":", alpha=0.5)

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=300)
    return fig


def plot_backtest_performance(result_df: pd.DataFrame, title: str = "EM FX Risk Premium Strategy", save_path: Optional[str] = None):
    """Plots equity curve and drawdowns."""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(11, 7), sharex=True, gridspec_kw={"height_ratios": [2.5, 1]})

    ax1.plot(result_df.index, result_df["cumulative_return"], color="#2980b9", linewidth=2.0, label="Strategy Equity")
    ax1.set_title(title, fontsize=14, fontweight="bold")
    ax1.set_ylabel("Cumulative NAV", fontsize=11)
    ax1.legend(loc="upper left")
    ax1.grid(True, linestyle=":", alpha=0.5)

    ax2.fill_between(result_df.index, result_df["drawdown"] * 100, 0, color="#c0392b", alpha=0.4, label="Drawdown %")
    ax2.plot(result_df.index, result_df["drawdown"] * 100, color="#c0392b", linewidth=1.0)
    ax2.set_ylabel("Drawdown %", fontsize=11)
    ax2.grid(True, linestyle=":", alpha=0.5)
    ax2.legend(loc="lower left")

    plt.tight_layout()
    if save_path:
        plt.savefig(save_path, dpi=300)
    return fig
