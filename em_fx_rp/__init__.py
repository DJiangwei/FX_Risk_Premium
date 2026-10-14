"""
em_fx_rp: Emerging Market FX Risk Premium Package
Based on Adam S. Iqbal, "Foreign Exchange: Practical Asset Pricing and Macroeconomic Theory" (2022).
"""

__version__ = "0.1.0"

from .config import DEFAULT_UNIVERSES, CurrencyMeta
from .data.bbg_loader import DataLoader
from .models.carry import CarryModel
from .models.real_rate import RealRateModel
from .models.factor_beta import FactorBetaModel
from .models.options_vrp import OptionsVRPModel
from .models.composite import CompositeRiskPremiumModel

__all__ = [
    "DEFAULT_UNIVERSES",
    "CurrencyMeta",
    "DataLoader",
    "CarryModel",
    "RealRateModel",
    "FactorBetaModel",
    "OptionsVRPModel",
    "CompositeRiskPremiumModel"
]
