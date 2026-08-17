"""Versioned allowlist registry. Plugins receive metadata, never credentials."""

from __future__ import annotations

import re
from .models import PluginManifest


class PluginRegistry:
    def __init__(self, allowlist: tuple[str, ...] = ()):
        self._allowlist = set(allowlist)
        self._plugins: dict[str, PluginManifest] = {}

    def register(self, manifest: PluginManifest) -> None:
        if manifest.name not in self._allowlist:
            raise PermissionError("Plugin is not allowlisted")
        if not re.fullmatch(r"\d+\.\d+\.\d+", manifest.version):
            raise ValueError("Plugin version must use semantic versioning")
        if manifest.timeout_seconds < 1 or manifest.timeout_seconds > 60:
            raise ValueError("Plugin timeout must be between 1 and 60 seconds")
        if not manifest.audit_enabled:
            raise ValueError("Plugin audit is mandatory")
        forbidden = {"credentials", "secrets", "apply", "publish"}
        if forbidden.intersection(manifest.permissions):
            raise PermissionError("Plugin requests a forbidden permission")
        self._plugins[manifest.name] = manifest

    def manifests(self) -> tuple[PluginManifest, ...]:
        return tuple(self._plugins[name] for name in sorted(self._plugins))
