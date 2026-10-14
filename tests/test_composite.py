import pytest
import pandas as pd
from em_fx_rp.config import DEFAULT_UNIVERSES
from em_fx_rp.data.bbg_loader import DataLoader
from em_fx_rp.models.composite import CompositeRiskPremiumModel
from em_fx_rp.trading.backtest import PortfolioBacktest


@pytest.fixture
def loader():
    return DataLoader(universe="LATAM", force_mock=True, use_cache=False)


def test_composite_scorecard(loader):
    model = CompositeRiskPremiumModel(loader)
    scorecard = model.compute_scorecard()

    assert isinstance(scorecard, pd.DataFrame)
    assert len(scorecard) == len(loader.universe_mgr.codes)
    assert "FX_RPS" in scorecard.columns
    assert "Rank" in scorecard.columns

    # Verify ranking order
    assert scorecard["Rank"].iloc[0] == 1
    assert scorecard["FX_RPS"].iloc[0] >= scorecard["FX_RPS"].iloc[-1]


def test_portfolio_backtest(loader):
    backtest = PortfolioBacktest(loader, top_n=2, bottom_n=2, long_only=False)
    res = backtest.run()

    assert not res.empty
    assert "cumulative_return" in res.columns
    assert "drawdown" in res.columns

    stats = backtest.get_summary_stats(res)
    assert "Sharpe_Ratio" in stats
    assert "Annualized_Return_%" in stats


@pytest.mark.parametrize("category", ["DM", "CEEMEA", "LATAM", "SSA", "ASIA", "EDGE"])
def test_all_six_categories(category):
    """Verify that all 6 categories requested by user load and compute correctly."""
    cat_loader = DataLoader(universe=category, force_mock=True, use_cache=False)
    assert len(cat_loader.universe_mgr.codes) == len(DEFAULT_UNIVERSES[category])

    model = CompositeRiskPremiumModel(cat_loader)
    scorecard = model.compute_scorecard()
    assert len(scorecard) == len(DEFAULT_UNIVERSES[category])
    assert "FX_RPS" in scorecard.columns


def test_edge_currencies_and_no_em_core():
    from em_fx_rp.data.universe import UniverseManager
    assert "EM_CORE" not in DEFAULT_UNIVERSES

    edge_mgr = UniverseManager("EDGE")
    for ccy in ["MDL", "ALL", "RSD", "BAM"]:
        assert ccy in edge_mgr.codes

    # Verify ALL resolves to Albanian Lek currency
    all_mgr = UniverseManager("ALL")
    assert all_mgr.codes == ["ALL"]
    assert all_mgr.currencies["ALL"].name == "Albanian Lek"

