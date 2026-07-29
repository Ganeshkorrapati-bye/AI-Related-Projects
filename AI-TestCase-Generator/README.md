<div align="center">

# 🧪 AI Test Case Generator

**Turn software requirements into enterprise-grade QA documentation with AI.**

Upload a requirements document (or pick a built-in enterprise application) and
generate functional, negative, boundary, security, API and 10+ more categories of
test cases — plus risk analysis, traceability, coverage, test plans and export to
Excel / PDF / CSV / Markdown.

![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-App-FF4B4B?logo=streamlit&logoColor=white)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT-412991?logo=openai&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green)

</div>

---

## 📖 Project Overview

The **AI Test Case Generator** is a Streamlit web application that acts as an
ISTQB-certified Senior QA Engineer. Given a set of requirements, it produces a
complete, structured QA documentation suite ready for enterprise use — the kind of
artifacts a real QA team would hand off during a project.

It ships with curated, realistic requirement sets for well-known open-source
enterprise applications (OrangeHRM, ERPNext, Saleor) so you can see full output
immediately, without preparing your own document.

## ✨ Features

- **Two input modes** — upload `PDF` / `DOCX` / `TXT`, or pick a built-in
  enterprise application from a dropdown.
- **16 test-case categories** — Functional, Negative, Positive, Boundary,
  Edge, Exploratory, Smoke, Sanity, Regression, Security, Performance,
  Accessibility, Compatibility, Localization, Usability, Database.
- **Enterprise test-case format** — every case includes ID, Module, Feature,
  Priority, Severity, Preconditions, Steps, Test Data, Expected Result, blank
  Actual Result / Status, and Remarks.
- **AI analysis suite** — Requirement Summary, Complexity Score, Coverage,
  Risk Analysis, Traceability Matrix, Test Strategy, Test Plan, SQL test
  suggestions, duplicate detection notes, and a bug-report template.
- **API artifacts** — API test cases, JSON request/response, schema and status
  validation, auth/authz/negative/rate-limit tests, and a downloadable Postman
  collection (plus REST Assured & Playwright snippets).
- **Premium dashboard UI** — dark/light mode, KPI cards, Plotly charts, search,
  filters, pagination, progress bar, and friendly success/error messages.
- **Exports** — Excel (multi-sheet), PDF (styled), CSV, Markdown, copy to
  clipboard.

## 🏗️ Architecture

```
                ┌──────────────┐
   Upload /     │   app.py     │  Streamlit UI (dashboard, tabs, charts)
   Sample  ───► │  (frontend)  │
                └──────┬───────┘
                       │
        ┌──────────────┼───────────────────────────┐
        ▼              ▼                             ▼
 ┌────────────┐ ┌──────────────┐            ┌───────────────┐
 │ pdf_reader │ │  ai_service  │◄─ prompts ─│   sample_apps │
 │ (ingest)   │ │  (OpenAI)    │  (prompts) │  (built-ins)  │
 └────────────┘ └──────┬───────┘            └───────────────┘
                       │
              ┌────────▼────────┐        ┌────────────┐
              │     utils       │───────►│ exporters  │ Excel/PDF/CSV/MD
              │ (normalisation) │        └────────────┘
              └─────────────────┘
   config.py — central settings (env vars, logging)
```

Each layer is independent and unit-tested. The UI never talks to the OpenAI SDK
directly; everything flows through `ai_service`.

## 📁 Folder Structure

```
AI-TestCase-Generator/
├── app.py                # Streamlit entry point (UI/dashboard)
├── config.py             # Central configuration & settings
├── ai_service.py         # OpenAI integration (retries, JSON parsing)
├── prompts.py            # Reusable, versioned prompt templates
├── pdf_reader.py         # PDF / DOCX / TXT ingestion
├── exporters.py          # Excel / PDF / CSV / Markdown exporters
├── utils.py              # Normalisation & transform helpers
├── sample_apps.py        # Built-in enterprise requirement sets
├── requirements.txt
├── README.md
├── LICENSE               # MIT
├── .gitignore
├── .env.example
├── assets/               # Logos / static assets
├── screenshots/          # README screenshots
├── sample_documents/     # Example requirement files
├── docs/                 # Additional documentation
└── tests/                # Pytest unit tests
```

## ⚙️ Installation

```bash
git clone https://github.com/<your-username>/AI-TestCase-Generator.git
cd AI-TestCase-Generator

python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

## 🔐 Environment Variables

Copy the example file and fill in your key:

```bash
cp .env.example .env
```

| Variable | Required | Default | Description |
|---|---|---|---|
| `OPENAI_API_KEY` | ✅ | — | Your OpenAI API key |
| `OPENAI_MODEL` | ❌ | `gpt-4o-mini` | Chat model to use |
| `OPENAI_BASE_URL` | ❌ | _(OpenAI default)_ | Override for Azure/proxy |
| `OPENAI_TEMPERATURE` | ❌ | `0.2` | Sampling temperature |
| `OPENAI_MAX_TOKENS` | ❌ | `8000` | Max output tokens |
| `OPENAI_TIMEOUT` | ❌ | `90` | Request timeout (seconds) |
| `OPENAI_MAX_RETRIES` | ❌ | `3` | Retry attempts on failure |
| `LOG_LEVEL` | ❌ | `INFO` | Logging verbosity |

Secrets are **never** hardcoded or stored — they are read from the environment.

## ▶️ How to Run

```bash
streamlit run app.py
```

Then open <http://localhost:8501>.

Run the test suite:

```bash
pytest -q
```

## ☁️ How to Deploy (Streamlit Community Cloud)

1. Push this repository to GitHub.
2. Go to <https://share.streamlit.io> and click **New app**.
3. Select your repo, branch, and `app.py` as the entry point.
4. Under **Advanced settings → Secrets**, add:
   ```toml
   OPENAI_API_KEY = "sk-your-key-here"
   OPENAI_MODEL = "gpt-4o-mini"
   ```
5. Click **Deploy**. Streamlit installs `requirements.txt` automatically.

## 🖼️ Screenshots

> Add screenshots to `screenshots/` and reference them here.

| Dashboard | Test Cases | Risk |
|---|---|---|
| `screenshots/dashboard.png` | `screenshots/test-cases.png` | `screenshots/risk.png` |

## 🚀 Future Enhancements

- Persistent history & project storage (database backend)
- Multi-user authentication and workspaces
- Direct Jira / Azure DevOps test-case export
- Live REST Assured / Playwright test execution
- Fine-tuned domain models per industry

## 📄 License

Released under the [MIT License](LICENSE).
