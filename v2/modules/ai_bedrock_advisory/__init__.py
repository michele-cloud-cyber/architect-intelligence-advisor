"""Deterministic, read-only V3 AI advisory simulation."""

from .service import ALLOWED_MODELS, AdvisoryEstimate, build_demo_advisory
__all__=["ALLOWED_MODELS","AdvisoryEstimate","build_demo_advisory"]
