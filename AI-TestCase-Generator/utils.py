"""Shared helper utilities: normalisation, flattening, and small transforms."""
from __future__ import annotations

import re
from typing import Any

from prompts import TEST_CASE_FIELDS


def humanize_key(key: str) -> str:
    """Convert a snake_case category key into a Title Case label."""
    return re.sub(r"[_\-]+", " ", key).strip().title()


def coerce_str(value: Any) -> str:
    """Coerce arbitrary values (lists, dicts, None) into a clean string."""
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, (list, tuple)):
        return "\n".join(coerce_str(v) for v in value)
    if isinstance(value, dict):
        return "; ".join(f"{k}: {coerce_str(v)}" for k, v in value.items())
    return str(value)


def normalize_test_case(row: dict[str, Any], category: str) -> dict[str, str]:
    """Ensure a test-case row contains every mandatory field as a string."""
    normalized: dict[str, str] = {}
    for field in TEST_CASE_FIELDS:
        normalized[field] = coerce_str(row.get(field, ""))
    normalized["category"] = humanize_key(category)
    if not normalized["actual_result"]:
        normalized["actual_result"] = ""
    if not normalized["status"]:
        normalized["status"] = ""
    return normalized


def flatten_test_cases(
    grouped: dict[str, list[dict[str, Any]]],
) -> list[dict[str, str]]:
    """Flatten grouped test cases into a single ordered list of normalised rows."""
    rows: list[dict[str, str]] = []
    for category, cases in grouped.items():
        for row in cases:
            rows.append(normalize_test_case(row, category))
    return rows


def count_by_category(rows: list[dict[str, str]]) -> dict[str, int]:
    """Return a category -> count mapping for dashboard metrics."""
    counts: dict[str, int] = {}
    for row in rows:
        counts[row["category"]] = counts.get(row["category"], 0) + 1
    return counts


def count_by_field(rows: list[dict[str, str]], field: str) -> dict[str, int]:
    """Return a value -> count mapping for a given field (e.g. priority)."""
    counts: dict[str, int] = {}
    for row in rows:
        value = row.get(field, "").strip() or "Unspecified"
        counts[value] = counts.get(value, 0) + 1
    return counts


def safe_filename(name: str, default: str = "export") -> str:
    """Sanitise a string into a safe filename stem."""
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", name).strip("_")
    return cleaned or default
