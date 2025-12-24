# gui/validators.py
from __future__ import annotations


def parse_positive_int(raw: str) -> int | None:
    try:
        n = int(raw.strip())
        return n if n > 0 else None
    except (ValueError, AttributeError):
        return None
