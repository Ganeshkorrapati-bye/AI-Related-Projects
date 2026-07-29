# Architecture

This document describes how the AI Test Case Generator is structured and how data
flows through the system.

## Layers

1. **Presentation (`app.py`)** — the Streamlit UI. Responsible only for rendering
   the dashboard, tabs, charts, filters, and download buttons, and for reading
   user input. It holds no business logic beyond orchestrating calls.

2. **Ingestion (`pdf_reader.py`)** — converts uploaded `PDF`, `DOCX`, and `TXT`
   files into normalised plain text. Validates size, format, and emptiness and
   raises `DocumentReadError` with user-friendly messages.

3. **Prompting (`prompts.py`)** — all prompt templates and the shared system
   persona. Kept separate so prompts can be reviewed and tuned independently of
   code.

4. **AI integration (`ai_service.py`)** — the only module that imports the OpenAI
   SDK. Handles client construction, timeouts, a custom retry loop, JSON parsing
   (including fence stripping and salvage), and normalisation into plain Python
   structures. Fails loudly with `AIServiceError`.

5. **Domain data (`sample_apps.py`)** — curated, realistic requirement sets for
   built-in enterprise applications (OrangeHRM, ERPNext, Saleor).

6. **Transforms (`utils.py`)** — pure helpers that normalise AI output into the
   canonical test-case schema and compute dashboard metrics.

7. **Export (`exporters.py`)** — renders the normalised data to Excel, PDF, CSV,
   and Markdown. Every exporter returns `bytes`/`str` for in-memory downloads.

8. **Configuration (`config.py`)** — central, immutable settings resolved from
   environment variables, plus logging configuration.

## Data flow

```
input (upload | sample)
  → pdf_reader.extract_text        (only for uploads)
  → ai_service.generate_test_cases  → prompts.test_cases_prompt
  → ai_service.generate_analysis    → prompts.analysis_prompt
  → ai_service.generate_api_artifacts (optional) → prompts.api_artifacts_prompt
  → utils.flatten_test_cases / normalize_test_case
  → app renders dashboard + tabs
  → exporters.to_{excel,pdf,csv,markdown}
```

## Design principles

- **Single responsibility** — each module does one thing and is unit-tested.
- **No hidden I/O** — exporters and readers work on bytes; nothing writes to disk.
- **Fail safe** — the UI wraps every generation and export in try/except and
  surfaces friendly messages.
- **Secrets stay in the environment** — never hardcoded, never logged.
