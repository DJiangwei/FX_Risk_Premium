"""
Quantitative asset pricing models for FX risk premium based on Iqbal (2022).
"""

from .carry import CarryModel
from .real_rate import RealRateModel
from .factor_beta import FactorBetaModel
from .options_vrp import OptionsVRPModel
from .composite import CompositeRiskPremiumModel

__all__ = [
    "CarryModel",
    "RealRateModel",
    "FactorBetaModel",
    "OptionsVRPModel",
    "CompositeRiskPremiumModel"
]
