"""
Bloomberg xbbg Data Loader with automated fallback and local caching.
Supports live fetching via xbbg.blp and offline development via MockProvider.
"""

import logging
from typing import List, Optional, Union
import pandas as pd
from .cache import DataCache
from .universe import UniverseManager
from .mock_data import generate_mock_market_data
from ..config import CURRENCIES, GLOBAL_BENCHMARKS

logger = logging.getLogger(__name__)


class DataLoader:
    """
    Unified Data Loader interfacing with Bloomberg API (via xbbg)
    with automatic disk caching and offline mock support.
    """

    def __init__(
        self,
        universe: Union[str, List[str]] = "EDGE",
        cache_dir: str = ".cache",
        use_cache: bool = True,
        force_mock: bool = False
    ):
        self.universe_mgr = UniverseManager(universe)
        self.cache = DataCache(cache_dir)
        self.use_cache = use_cache
        self.force_mock = force_mock
        self._data: Optional[pd.DataFrame] = None

    def fetch_data(
        self,
        start_date: str = "2020-01-01",
        end_date: str = "2023-12-31",
        flds: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Fetch historical time series for the universe.
        Attempts xbbg -> Cache -> Mock data in order.
        """
        cache_key = f"universe_{'_'.join(sorted(self.universe_mgr.codes))}_{start_date}_{end_date}"

        # 1. Check local cache
        if self.use_cache and self.cache.exists(cache_key):
            logger.info("Loading market data from local cache: %s", cache_key)
            self._data = self.cache.load(cache_key)
            return self._data

        # 2. Try Bloomberg xbbg if not forced to mock
        df = None
        if not self.force_mock:
            try:
                from xbbg import blp
                tickers = self.universe_mgr.get_all_tickers()
                tickers.extend(list(GLOBAL_BENCHMARKS.values()))
                fields = flds or ["PX_LAST"]

                logger.info("Connecting to Bloomberg via xbbg for %d tickers...", len(tickers))
                raw_df = blp.bdh(tickers=tickers, flds=fields, start_date=start_date, end_date=end_date)
                if raw_df is not None and not raw_df.empty:
                    # Flatten multi-index columns if needed
                    if isinstance(raw_df.columns, pd.MultiIndex):
                        df = raw_df.droplevel(1, axis=1) if "PX_LAST" in fields else raw_df
                    else:
                        df = raw_df
                    logger.info("Successfully fetched %d rows from Bloomberg.", len(df))
            except Exception as e:
                logger.warning("Bloomberg xbbg unavailable or failed (%s). Falling back to mock data.", e)

        # 3. Fallback to mock data if Bloomberg is unavailable or returned empty
        if df is None or df.empty:
            logger.info("Generating realistic mock market data for universe: %s", self.universe_mgr.codes)
            df = generate_mock_market_data(
                currencies=self.universe_mgr.codes,
                start_date=start_date,
                end_date=end_date
            )

        # Save to cache
        if self.use_cache and df is not None:
            self.cache.save(cache_key, df)

        self._data = df
        return df

    @property
    def data(self) -> pd.DataFrame:
        if self._data is None:
            return self.fetch_data()
        return self._data

    def get_spot(self, ccy: str) -> pd.Series:
        meta = CURRENCIES[ccy]
        return self.data[meta.spot_ticker]

    def get_forward(self, ccy: str, tenor: str = "1M") -> pd.Series:
        meta = CURRENCIES[ccy]
        if tenor.upper() == "1M":
            return self.data[meta.fwd_1m_ticker]
        elif tenor.upper() == "3M":
            return self.data[meta.fwd_3m_ticker]
        elif tenor.upper() in ["12M", "1Y"]:
            return self.data[meta.fwd_12m_ticker]
        raise ValueError(f"Unsupported tenor: {tenor}")

    def get_implied_vol(self, ccy: str, tenor: str = "1M") -> pd.Series:
        meta = CURRENCIES[ccy]
        ticker = meta.vol_1m_ticker if tenor.upper() == "1M" else meta.vol_3m_ticker
        return self.data[ticker]

    def get_risk_reversal(self, ccy: str, tenor: str = "1M") -> pd.Series:
        meta = CURRENCIES[ccy]
        ticker = meta.rr_25d_1m_ticker if tenor.upper() == "1M" else meta.rr_25d_3m_ticker
        return self.data[ticker]

    def get_butterfly(self, ccy: str, tenor: str = "1M") -> pd.Series:
        meta = CURRENCIES[ccy]
        ticker = meta.bf_25d_1m_ticker if tenor.upper() == "1M" else meta.bf_25d_3m_ticker
        return self.data[ticker]

    def get_policy_rate(self, ccy: str) -> pd.Series:
        meta = CURRENCIES[ccy]
        return self.data[meta.policy_rate_ticker]

    def get_cpi_yoy(self, ccy: str) -> pd.Series:
        meta = CURRENCIES[ccy]
        return self.data[meta.cpi_yoy_ticker]

    def get_global_benchmark(self, name: str) -> pd.Series:
        ticker = GLOBAL_BENCHMARKS[name]
        return self.data[ticker]
