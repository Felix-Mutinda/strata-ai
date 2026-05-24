"""Strata AI SDK — Core contract layer."""

__version__ = "0.0.0"

from strata_ai.core.config import StrataBaseConfig
from strata_ai.core.app import StrataAIApp
from strata_ai.core.di import AppState

__all__ = [
    "StrataBaseConfig",
    "StrataAIApp",
    "AppState",
]
