"""Fail-closed governance skeleton for local/demo operations."""

from __future__ import annotations

import re
from .models import GovernanceDecision, OperationalLevel


class GovernanceControlPlane:
    _secret_pattern = re.compile(r"(?i)(access[_-]?key|secret|password|token)\s*[:=]\s*\S+")
    allowed_levels = {OperationalLevel.CONSULT, OperationalLevel.SIMULATE, OperationalLevel.GENERATE, OperationalLevel.TEST}

    def redact(self, value: str) -> str:
        return self._secret_pattern.sub("[REDACTED]", value)

    def authorize(self, level: OperationalLevel, payload: dict | None = None) -> GovernanceDecision:
        payload = payload or {}
        reasons = []
        if level not in self.allowed_levels:
            reasons.append("Operation disabled in the local demo foundation")
        sensitive_keys = {"access_key", "access-key", "secret", "password", "token"}
        if any(str(key).lower() in sensitive_keys for key in payload):
            reasons.append("Sensitive value detected")
        if payload.get("cross_environment"):
            reasons.append("Cross-environment access is denied")
        if payload.get("publish") or payload.get("network_access"):
            reasons.append("External publication and network access are denied")
        return GovernanceDecision(not reasons, level, tuple(reasons), ("manual-owner",) if level in {OperationalLevel.PLAN, OperationalLevel.APPROVE, OperationalLevel.CONTROLLED_APPLY} else ())
