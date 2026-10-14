"""
Data caching module using local CSV/Parquet storage.
"""

import os
from pathlib import Path
import pandas as pd


class DataCache:
    """Handles local disk caching for downloaded market data."""

    def __init__(self, cache_dir: str = ".cache"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_path(self, key: str) -> Path:
        safe_key = key.replace(" ", "_").replace("/", "_").replace(":", "_")
        return self.cache_dir / f"{safe_key}.csv"

    def save(self, key: str, df: pd.DataFrame) -> None:
        """Save dataframe to disk."""
        path = self._get_path(key)
        df.to_csv(path, index=True)

    def load(self, key: str) -> pd.DataFrame:
        """Load dataframe from disk if exists, else return None."""
        path = self._get_path(key)
        if path.exists():
            return pd.read_csv(path, index_col=0, parse_dates=True)
        return None

    def exists(self, key: str) -> bool:
        """Check if cached file exists."""
        return self._get_path(key).exists()

    def clear(self) -> None:
        """Clear all cached files."""
        for p in self.cache_dir.glob("*.csv"):
            try:
                p.unlink()
            except OSError:
                pass
