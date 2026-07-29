"""Unit tests for document ingestion."""
from __future__ import annotations

import pytest

from pdf_reader import DocumentReadError, extract_text


def test_txt_extraction() -> None:
    text = extract_text(b"Requirement 1\nRequirement 2", "req.txt")
    assert "Requirement 1" in text


def test_empty_file_rejected() -> None:
    with pytest.raises(DocumentReadError):
        extract_text(b"", "req.txt")


def test_unsupported_format_rejected() -> None:
    with pytest.raises(DocumentReadError):
        extract_text(b"data", "req.xyz")


def test_whitespace_only_rejected() -> None:
    with pytest.raises(DocumentReadError):
        extract_text(b"    \n   ", "req.txt")
