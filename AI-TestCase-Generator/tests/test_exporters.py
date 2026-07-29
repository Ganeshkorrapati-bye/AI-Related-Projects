"""Unit tests for the exporters (offline, no network)."""
from __future__ import annotations

from utils import flatten_test_cases

import exporters

SAMPLE = flatten_test_cases(
    {
        "functional_test_cases": [
            {
                "test_case_id": "TC-001",
                "module": "Auth",
                "feature": "Login",
                "priority": "High",
                "severity": "Major",
                "preconditions": "User exists",
                "test_steps": "1. Open login\n2. Submit",
                "test_data": "user/pass",
                "expected_result": "Logged in",
                "remarks": "",
            }
        ]
    }
)

ANALYSIS = {
    "requirement_summary": "Summary",
    "complexity_score": {"score": 6, "band": "Medium", "rationale": "..."},
    "coverage": {"percentage": 80, "gaps": ["No 2FA tests"]},
    "risk_analysis": [
        {"risk": "Weak passwords", "likelihood": "Medium", "impact": "High", "mitigation": "Policy"}
    ],
    "traceability_matrix": [
        {"requirement_id": "R1", "requirement": "Login", "test_case_ids": ["TC-001"]}
    ],
}


def test_csv_export() -> None:
    data = exporters.to_csv(SAMPLE)
    assert isinstance(data, bytes)
    assert b"TC-001" in data


def test_excel_export() -> None:
    data = exporters.to_excel(SAMPLE, ANALYSIS)
    assert isinstance(data, bytes)
    # XLSX files are ZIP archives beginning with 'PK'.
    assert data[:2] == b"PK"


def test_pdf_export() -> None:
    data = exporters.to_pdf(SAMPLE, ANALYSIS, "OrangeHRM")
    assert isinstance(data, bytes)
    assert data[:4] == b"%PDF"


def test_markdown_export() -> None:
    md = exporters.to_markdown(SAMPLE, ANALYSIS, "OrangeHRM")
    assert "# QA Documentation - OrangeHRM" in md
    assert "TC-001" in md
