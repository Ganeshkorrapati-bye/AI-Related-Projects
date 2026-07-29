"""Central application configuration.

All tunable settings live here so the rest of the codebase never reaches for
environment variables or magic constants directly. Values are read once at import
time from environment variables (optionally populated from a local ``.env`` file
via :mod:`python-dotenv`).
"""
from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from functools import lru_cache
from typing import Final

try:  # python-dotenv is optional at runtime but listed in requirements.txt
    from dotenv import load_dotenv

    load_dotenv()
except Exception:  # pragma: no cover - dotenv missing should never be fatal
    pass


APP_NAME: Final[str] = "AI Test Case Generator"
APP_TAGLINE: Final[str] = "Turn requirements into enterprise QA documentation with AI"
APP_VERSION: Final[str] = "1.0.0"

# Supported upload formats (extension -> human label).
SUPPORTED_UPLOAD_FORMATS: Final[dict[str, str]] = {
    "pdf": "PDF Document",
    "docx": "Word Document",
    "txt": "Plain Text",
}

# Hard limit for uploaded documents to protect the LLM context window and memory.
MAX_UPLOAD_MB: Final[int] = 10
MAX_REQUIREMENT_CHARS: Final[int] = 120_000


def _get_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None or not raw.strip():
        return default
    try:
        return int(raw)
    except ValueError:
        logging.getLogger(__name__).warning(
            "Invalid integer for %s=%r, falling back to %s", name, raw, default
        )
        return default


def _get_float(name: str, default: float) -> float:
    raw = os.getenv(name)
    if raw is None or not raw.strip():
        return default
    try:
        return float(raw)
    except ValueError:
        logging.getLogger(__name__).warning(
            "Invalid float for %s=%r, falling back to %s", name, raw, default
        )
        return default


@dataclass(frozen=True)
class Settings:
    """Immutable runtime settings resolved from the environment."""

    openai_api_key: str = field(default_factory=lambda: os.getenv("OPENAI_API_KEY", ""))
    openai_model: str = field(default_factory=lambda: os.getenv("OPENAI_MODEL", "gpt-4o-mini"))
    openai_base_url: str = field(default_factory=lambda: os.getenv("OPENAI_BASE_URL", ""))
    request_timeout: float = field(default_factory=lambda: _get_float("OPENAI_TIMEOUT", 90.0))
    max_retries: int = field(default_factory=lambda: _get_int("OPENAI_MAX_RETRIES", 3))
    temperature: float = field(default_factory=lambda: _get_float("OPENAI_TEMPERATURE", 0.2))
    max_output_tokens: int = field(default_factory=lambda: _get_int("OPENAI_MAX_TOKENS", 8000))
    log_level: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))

    @property
    def has_api_key(self) -> bool:
        return bool(self.openai_api_key.strip())


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached :class:`Settings` instance."""
    return Settings()


def configure_logging(level: str | None = None) -> None:
    """Configure root logging once, idempotently."""
    resolved = (level or get_settings().log_level or "INFO").upper()
    logging.basicConfig(
        level=getattr(logging, resolved, logging.INFO),
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    )
