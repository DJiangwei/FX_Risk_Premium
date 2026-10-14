import pytest
import numpy as np
import pandas as pd
from em_fx_rp.data.bbg_loader import DataLoader
from em_fx_rp.models.factor_beta import FactorBetaModel


@pytest.fixture
def loader():
    return DataLoader(universe=["MXN", "BRL", "ZAR"], force_mock=True, use_cache=False)


def test_spx_beta(loader):
    model = FactorBetaModel(loader)
    beta = model.calculate_rolling_beta("MXN", window=63)
    valid_beta = beta.dropna()
    assert len(valid_beta) > 0
    # EM FX should have a positive beta to S&P 500 (strengthens when SPX rises, weakens when SPX falls)
    assert valid_beta.mean() > 0.0


def test_vix_sensitivity(loader):
    model = FactorBetaModel(loader)
    vix_sens = model.calculate_vix_sensitivity("MXN", window=63)
    valid_sens = vix_sens.dropna()
    assert len(valid_sens) > 0
    # EM FX depreciates when VIX spikes, so sensitivity should be negative
    assert valid_sens.mean() < 0.0
