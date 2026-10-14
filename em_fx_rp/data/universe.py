"""
FX Universe and quotation management.
Handles conversion between Market Quotation (e.g. USDMXN = 18.0)
and Academic / Iqbal Asset Pricing convention (USD per foreign currency, St = 1/18.0 = 0.055).
"""

from typing import List, Dict, Union
from ..config import CURRENCIES, DEFAULT_UNIVERSES, CurrencyMeta


class UniverseManager:
    """Manages FX universe definitions and quotation convention adjustments."""

    def __init__(self, universe: Union[str, List[str]] = "EM_CORE"):
        if isinstance(universe, str):
            if universe.upper() in DEFAULT_UNIVERSES:
                self.codes = DEFAULT_UNIVERSES[universe.upper()]
            elif universe.upper() in CURRENCIES:
                self.codes = [universe.upper()]
            else:
                raise ValueError(f"Unknown universe name '{universe}'. Available: {list(DEFAULT_UNIVERSES.keys())}")
        else:
            self.codes = [c.upper() for c in universe]

        # Validate currencies
        for c in self.codes:
            if c not in CURRENCIES:
                raise ValueError(f"Currency '{c}' not found in CURRENCIES metadata. Please add it first.")

    @property
    def currencies(self) -> Dict[str, CurrencyMeta]:
        """Return dict of CurrencyMeta for the active universe."""
        return {c: CURRENCIES[c] for c in self.codes}

    def to_domestic_quote(self, ccy: str, market_price: float) -> float:
        """
        Convert market quote to USD-per-unit-of-foreign-currency (St in Iqbal's book).
        For USDMXN = 20, St = 0.05 USD per 1 MXN.
        For EURUSD = 1.08, St = 1.08 USD per 1 EUR.
        """
        meta = CURRENCIES[ccy]
        if meta.is_usd_base:
            return 1.0 / market_price
        return market_price

    def to_market_quote(self, ccy: str, domestic_price: float) -> float:
        """Convert domestic price back to market quote convention."""
        meta = CURRENCIES[ccy]
        if meta.is_usd_base:
            return 1.0 / domestic_price
        return domestic_price

    def get_all_tickers(self, include_options: bool = True, include_macro: bool = True) -> List[str]:
        """Collect all relevant Bloomberg tickers for the universe."""
        tickers = []
        for c in self.codes:
            m = CURRENCIES[c]
            tickers.extend([m.spot_ticker, m.fwd_1m_ticker, m.fwd_3m_ticker])
            if include_options:
                tickers.extend([m.vol_1m_ticker, m.vol_3m_ticker, m.rr_25d_1m_ticker, m.bf_25d_1m_ticker])
            if include_macro:
                tickers.extend([m.cpi_yoy_ticker, m.policy_rate_ticker])
        return list(set(tickers))
