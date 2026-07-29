"""Unit tests for the pure helper utilities."""
from __future__ import annotations

from prompts import TEST_CASE_FIELDS
from utils import (
    coerce_str,
    count_by_category,
    count_by_field,
    flatten_test_cases,
    humanize_key,
    normalize_test_case,
    safe_filename,
)


def test_humanize_key() -> None:
    assert humanize_key("functional_test_cases") == "Functional Test Cases"
    assert humanize_key("api-test-cases") == "Api Test Cases"


def test_coerce_str_handles_types() -> None:
    assert coerce_str(None) == ""
    assert coerce_str("  hi ") == "hi"
    assert coerce_str(["a", "b"]) == "a\nb"
    assert "k: v" in coerce_str({"k": "v"})


def test_normalize_test_case_fills_all_fields() -> None:
    row = normalize_test_case({"test_case_id": "TC1"}, "functional_test_cases")
    for field in TEST_CASE_FIELDS:
        assert field in row
    assert row["category"] == "Functional Test Cases"
    assert row["actual_result"] == ""
    assert row["status"] == ""


def test_flatten_and_counts() -> None:
    grouped = {
        "functional_test_cases": [
            {"test_case_id": "TC1", "priority": "High"},
            {"test_case_id": "TC2", "priority": "Low"},
        ],
        "negative_test_cases": [{"test_case_id": "TC3", "priority": "High"}],
    }
    rows = flatten_test_cases(grouped)
    assert len(rows) == 3
    cats = count_by_category(rows)
    assert cats["Functional Test Cases"] == 2
    assert cats["Negative Test Cases"] == 1
    pri = count_by_field(rows, "priority")
    assert pri["High"] == 2
    assert pri["Low"] == 1


def test_safe_filename() -> None:
    assert safe_filename("OrangeHRM (HR)") == "OrangeHRM_HR"
    assert safe_filename("") == "export"
