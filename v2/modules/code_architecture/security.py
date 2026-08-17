"""Fail-closed, non-executing input gateway for Terraform text and ZIPs."""

from __future__ import annotations
from dataclasses import dataclass
from io import BytesIO
from pathlib import PurePosixPath
import re
from zipfile import BadZipFile, ZipFile


class InputSecurityError(ValueError): pass


@dataclass(frozen=True)
class SecuredInput:
    files: dict[str, str]; redacted_events: tuple[str, ...]


class InputSecurityGateway:
    allowed_extensions = {".tf"}
    max_files = 30
    max_file_bytes = 512_000
    max_total_bytes = 2_000_000
    max_compression_ratio = 50
    _secret = re.compile(r"(?i)(aws_access_key_id|aws_secret_access_key|client_secret|password|token)\s*=\s*\"[^\"]+\"")
    _blocked = (
        re.compile(r"(?is)provisioner\s+\"(?:local-exec|remote-exec|file)\""),
        re.compile(r"(?is)\b(?:file|templatefile)\s*\("),
        re.compile(r"(?is)\bdata\s+\"(?:http|external)\"|\b(?:http|external)\s*\{"),
        re.compile(r"(?is)source\s*=\s*\"(?:git::|https?://)"),
    )

    def secure_text(self, text: str, filename: str = "main.tf") -> SecuredInput:
        self._validate_name(filename)
        raw = text.encode("utf-8", errors="strict")
        if len(raw) > self.max_file_bytes: raise InputSecurityError("File size limit exceeded")
        self._validate_content(text)
        redacted = self._secret.sub(lambda m: m.group(1) + ' = "[REDACTED]"', text)
        events = ("secret-detected-and-redacted",) if redacted != text else ()
        return SecuredInput({filename: redacted}, events)

    def secure_zip(self, payload: bytes) -> SecuredInput:
        if len(payload) > self.max_total_bytes: raise InputSecurityError("Archive size limit exceeded")
        files, events, total = {}, [], 0
        try:
            with ZipFile(BytesIO(payload)) as archive:
                entries = [entry for entry in archive.infolist() if not entry.is_dir()]
                if len(entries) > self.max_files: raise InputSecurityError("Archive file-count limit exceeded")
                for entry in entries:
                    self._validate_name(entry.filename)
                    if (entry.external_attr >> 16) & 0o170000 == 0o120000: raise InputSecurityError("Symbolic links are blocked")
                    if entry.file_size > self.max_file_bytes: raise InputSecurityError("Archive member size limit exceeded")
                    if entry.compress_size == 0 and entry.file_size: raise InputSecurityError("Suspicious compression ratio")
                    if entry.compress_size and entry.file_size / entry.compress_size > self.max_compression_ratio: raise InputSecurityError("ZIP bomb protection triggered")
                    total += entry.file_size
                    if total > self.max_total_bytes: raise InputSecurityError("Expanded archive limit exceeded")
                    text = archive.read(entry).decode("utf-8", errors="strict")
                    secured = self.secure_text(text, entry.filename)
                    files.update(secured.files); events.extend(secured.redacted_events)
        except (BadZipFile, UnicodeDecodeError) as exc:
            raise InputSecurityError("Malformed or non-text Terraform archive") from exc
        return SecuredInput(files, tuple(events))

    def _validate_name(self, name: str) -> None:
        normalized = name.replace("\\", "/")
        path = PurePosixPath(normalized)
        if path.is_absolute() or ".." in path.parts or ":" in normalized: raise InputSecurityError("Path traversal blocked")
        if path.suffix.lower() not in self.allowed_extensions: raise InputSecurityError("Only .tf files are allowed")

    def _validate_content(self, text: str) -> None:
        for pattern in self._blocked:
            if pattern.search(text): raise InputSecurityError("Executable, filesystem, network or remote-module construct blocked")
