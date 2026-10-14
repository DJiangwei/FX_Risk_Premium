import pytest
import numpy as np
import pandas as pd
from em_fx_rp.data.bbg_loader import DataLoader
from em_fx_rp.models.real_rate import RealRateModel


@pytest.fixture
def loader():
    return DataLoader(universe=["MXN", "BRL", "TRY"], force_mock=True, use_cache=False)


def test_carry_decomposition_identity(loader):
    """
    Test Eq. (3.13) identity:
    Nominal Spread = Inflation Differential + Real Risk Premium
    """
    model = RealRateModel(loader)
    decomp = model.decompose_carry("MXN")

    # Check Eq. 3.13 holds exactly
    lhs = decomp["Nominal_Spread_%"]
    rhs = decomp["Inflation_Differential_%"] + decomp["Real_Risk_Premium_%"]

    np.testing.assert_allclose(lhs.values, rhs.values, rtol=1e-5, atol=1e-5)


def test_real_rate_cross_sectional(loader):
    model = RealRateModel(loader)
    summary = model.cross_sectional_real_rate_summary()
    assert len(summary) == 3
    assert "Real_Carry_vs_USD_%" in summary.columns
