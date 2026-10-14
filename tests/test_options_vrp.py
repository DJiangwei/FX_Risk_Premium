import pytest
import numpy as np
from em_fx_rp.data.bbg_loader import DataLoader
from em_fx_rp.models.options_vrp import OptionsVRPModel


@pytest.fixture
def loader():
    return DataLoader(universe=["MXN", "ZAR"], force_mock=True, use_cache=False)


def test_smile_eval_equations(loader):
    """
    Verify Iqbal (2022) Eq. (4.9), (4.10), (4.11), (4.12) consistency:
    sigma(0.50) = atm
    sigma(0.25) - sigma(0.75) = rr
    (sigma(0.25) + sigma(0.75))/2 - atm = bf
    """
    atm = 10.0
    rr = 2.0
    bf = 0.5

    deltas = np.array([0.50, 0.25, 0.75])
    vols = OptionsVRPModel.eval_3point_smile(deltas, atm, rr, bf)

    vol_50 = vols[0]
    vol_25 = vols[1]
    vol_75 = vols[2]

    # Eq. 4.10: atm = sigma(0.50)
    assert np.isclose(vol_50, atm)

    # Eq. 4.11: rr = sigma(0.25) - sigma(0.75)
    assert np.isclose(vol_25 - vol_75, rr)

    # Eq. 4.12: bf = (sigma(0.25) + sigma(0.75))/2 - atm
    assert np.isclose((vol_25 + vol_75) / 2.0 - atm, bf)


def test_breeden_litzenberger_density(loader):
    model = OptionsVRPModel(loader)
    strikes, q_pdf = model.reconstruct_risk_neutral_density("MXN", tenor="1M", n_points=150)

    # Check non-negativity
    assert np.all(q_pdf >= 0.0)

    # Check integration to approximately 1.0
    dk = strikes[1] - strikes[0]
    total_prob = np.sum(q_pdf) * dk
    assert np.isclose(total_prob, 1.0, atol=0.05)
