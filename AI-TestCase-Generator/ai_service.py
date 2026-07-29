"""OpenAI integration layer.

Wraps the OpenAI client with configuration, retries, timeouts, JSON parsing, and
graceful degradation. Every public method returns plain Python data structures so
the rest of the app never touches the OpenAI SDK directly.
"""
from __future__ import annotations

import json
import logging
import time
from typing import Any

import prompts
from config import Settings, get_settings

logger = logging.getLogger(__name__)


class AIServiceError(Exception):
    """Raised for any unrecoverable AI generation failure."""


# Full catalogue of test-case categories the product advertises.
TEST_CASE_CATEGORIES: list[str] = [
    "Functional Test Cases",
    "Negative Test Cases",
    "Positive Test Cases",
    "Boundary Value Test Cases",
    "Edge Cases",
    "Exploratory Test Ideas",
    "Smoke Test Suite",
    "Sanity Test Suite",
    "Regression Test Suite",
    "Security Test Cases",
    "Performance Test Ideas",
    "Accessibility Test Cases",
    "Compatibility Test Cases",
    "Localization Test Cases",
    "Usability Test Cases",
    "Database Test Cases",
]


def _strip_code_fences(text: str) -> str:
    """Remove Markdown code fences the model may add despite instructions."""
    cleaned = text.strip()
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        # Drop the opening fence (``` or ```json) and a trailing fence if present.
        lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        cleaned = "\n".join(lines)
    return cleaned.strip()


def _parse_json(content: str) -> dict[str, Any]:
    cleaned = _strip_code_fences(content)
    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        # Last-resort: attempt to slice the outermost JSON object.
        start, end = cleaned.find("{"), cleaned.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                parsed = json.loads(cleaned[start : end + 1])
            except json.JSONDecodeError:
                raise AIServiceError("The AI returned malformed JSON.") from exc
        else:
            raise AIServiceError("The AI returned malformed JSON.") from exc
    if not isinstance(parsed, dict):
        raise AIServiceError("The AI response was not a JSON object.")
    return parsed


class AIService:
    """High-level QA-generation service backed by the OpenAI Responses/Chat API."""

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings or get_settings()
        self._client = None  # Lazily constructed so imports never fail without a key.

    # -- client management -------------------------------------------------
    def _ensure_client(self) -> Any:
        if not self._settings.has_api_key:
            raise AIServiceError(
                "OpenAI API key is missing. Set OPENAI_API_KEY in your environment "
                "or .env file."
            )
        if self._client is None:
            try:
                from openai import OpenAI
            except ImportError as exc:  # pragma: no cover
                raise AIServiceError("The 'openai' package is not installed.") from exc

            kwargs: dict[str, Any] = {
                "api_key": self._settings.openai_api_key,
                "timeout": self._settings.request_timeout,
                "max_retries": 0,  # we implement our own retry loop
            }
            if self._settings.openai_base_url:
                kwargs["base_url"] = self._settings.openai_base_url
            self._client = OpenAI(**kwargs)
        return self._client

    # -- low level ---------------------------------------------------------
    def _complete_json(self, system: str, user: str) -> dict[str, Any]:
        """Call the chat completions API and parse a JSON object response."""
        client = self._ensure_client()
        last_error: Exception | None = None

        for attempt in range(1, self._settings.max_retries + 1):
            try:
                response = client.chat.completions.create(
                    model=self._settings.openai_model,
                    temperature=self._settings.temperature,
                    max_tokens=self._settings.max_output_tokens,
                    response_format={"type": "json_object"},
                    messages=[
                        {"role": "system", "content": system},
                        {"role": "user", "content": user},
                    ],
                )
                content = response.choices[0].message.content or ""
                return _parse_json(content)
            except AIServiceError:
                raise
            except Exception as exc:  # network/timeout/rate-limit
                last_error = exc
                wait = min(2 ** attempt, 10)
                logger.warning(
                    "AI call failed (attempt %d/%d): %s. Retrying in %ss",
                    attempt,
                    self._settings.max_retries,
                    exc,
                    wait,
                )
                time.sleep(wait)

        raise AIServiceError(
            f"AI request failed after {self._settings.max_retries} attempts: {last_error}"
        )

    # -- public API --------------------------------------------------------
    def generate_test_cases(
        self,
        requirements: str,
        application: str,
        categories: list[str] | None = None,
    ) -> dict[str, list[dict[str, Any]]]:
        """Generate every test-case category as a mapping of category -> rows."""
        selected = categories or TEST_CASE_CATEGORIES
        prompt = prompts.test_cases_prompt(requirements, application, selected)
        data = self._complete_json(prompts.SYSTEM_PERSONA, prompt)
        # Normalise: ensure each value is a list of dicts.
        result: dict[str, list[dict[str, Any]]] = {}
        for key, value in data.items():
            if isinstance(value, list):
                result[key] = [row for row in value if isinstance(row, dict)]
        return result

    def generate_api_artifacts(self, requirements: str, application: str) -> dict[str, Any]:
        """Generate API test artifacts (empty structures when no API applies)."""
        prompt = prompts.api_artifacts_prompt(requirements, application)
        return self._complete_json(prompts.SYSTEM_PERSONA, prompt)

    def generate_analysis(self, requirements: str, application: str) -> dict[str, Any]:
        """Generate management artifacts: summary, risk, coverage, plans, etc."""
        prompt = prompts.analysis_prompt(requirements, application)
        return self._complete_json(prompts.SYSTEM_PERSONA, prompt)
