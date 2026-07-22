"""Deterministic allocation of human-readable Security Case identifiers."""

from __future__ import annotations

import re
from collections.abc import Iterable
from datetime import datetime


_CASE_ID_PATTERN = re.compile(r"^AIA-(?P<date>\d{8})-(?P<sequence>\d{6})$")


def allocate_case_id(existing_case_ids: Iterable[str], now: datetime | None = None) -> str:
    """Return the next local Case ID for the supplied UTC calendar date.

    Repository persistence remains the source of truth.  This function has no
    side effects, which makes its behavior deterministic and directly testable.
    """

    timestamp = now or datetime.now().astimezone()
    date_prefix = timestamp.strftime("%Y%m%d")
    highest_sequence = 0

    for case_id in existing_case_ids:
        match = _CASE_ID_PATTERN.fullmatch(case_id)
        if match is not None and match.group("date") == date_prefix:
            highest_sequence = max(highest_sequence, int(match.group("sequence")))

    return f"AIA-{date_prefix}-{highest_sequence + 1:06d}"
