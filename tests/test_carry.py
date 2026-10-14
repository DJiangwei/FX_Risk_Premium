import pytest
import numpy as np
import pandas as pd
from em_fx_rp.data.bbg_loader import DataLoader
from em_fx_rp.models.carry import CarryModel


@pytest.fixture
def loader():
    return DataLoader(universe=["MXN", "BRL", "ZAR", "EUR"], force_mock=True, use_cache=False)


def test_carry_calculation(loader):
    model = CarryModel(loader)
    carry_mxn = model.calculate_annualized_carry("MXN", tenor="1M")

    # In mock data, MXN interest rate is ~7.25% vs US ~1.75%, so carry is positive (~5.5%)
    assert isinstance(carry_mxn, pd.Series)
    assert not carry_mxn.empty
    assert carry_mxn.iloc[0] > 0.02, "MXN carry should be positive and substantial"


def test_realized_volatility(loader):
    model = CarryModel(loader)
    rvol = model.calculate_realized_volatility("MXN", window=63)
    assert not rvol.empty
    valid_vol = rvol.dropna()
    assert len(valid_vol) > 0
    # Annualized vol should typically be between 5% and 40%
    assert 0.05 < valid_vol.mean() < 0.40


def test_cross_sectional_summary(loader):
    model = CarryModel(loader)
    summary = model.cross_sectional_carry_summary()
    assert isinstance(summary, pd.DataFrame)
    assert len(summary) == 4
    assert "Annualized_Carry_%" in summary.columns
    assert "Carry_to_Implied_Vol" in summary.columns
