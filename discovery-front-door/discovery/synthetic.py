from __future__ import annotations

from .adapters.advizorpro import AdvizorProAdapter
from .adapters.matcher5500 import Local5500Adapter
from .synthetic_data import SYNTHETIC_EMPLOYERS

__all__ = ["SYNTHETIC_EMPLOYERS", "build_adapters"]


def build_adapters():
    matcher = Local5500Adapter.from_synthetic()
    return AdvizorProAdapter(), matcher
