"""Utility helpers for formatting output used across CLI commands."""

from __future__ import annotations

from datetime import datetime, timezone


def format_timestamp(value: datetime | None = None) -> str:
    """Return an ISO timestamp (UTC) accurate to whole seconds."""

    if value is None:
        value = datetime.now(tz=timezone.utc)
    return value.replace(microsecond=0).isoformat()
