"""Unit tests for the AI service parsing/normalisation (no network calls)."""
from __future__ import annotations

import pytest

from ai_service import AIService, AIServiceError, _parse_json, _strip_code_fences
from config import Settings


def test_strip_code_fences() -> None:
    fenced = "```json\n{\"a\": 1}\n```"
    assert _strip_code_fences(fenced) == '{"a": 1}'


def test_parse_json_plain() -> None:
    assert _parse_json('{"a": 1}') == {"a": 1}


def test_parse_json_embedded() -> None:
    messy = 'Here you go: {"a": 1} thanks'
    assert _parse_json(messy) == {"a": 1}


def test_parse_json_invalid_raises() -> None:
    with pytest.raises(AIServiceError):
        _parse_json("not json at all")


def test_missing_api_key_raises() -> None:
    service = AIService(Settings(openai_api_key=""))
    with pytest.raises(AIServiceError):
        service.generate_analysis("reqs", "App")
