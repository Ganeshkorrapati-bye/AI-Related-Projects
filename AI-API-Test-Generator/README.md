# AI API Test Generator (n8n)

![Platform](https://img.shields.io/badge/platform-n8n-EA4B71)
![AI](https://img.shields.io/badge/AI-OpenAI-412991)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-production--ready-brightgreen)

An AI-powered workflow that turns an **OpenAPI 3.x / Swagger 2.0** specification into
enterprise-grade API test cases across multiple frameworks — built entirely on
[n8n](https://n8n.io).

Submit a spec through a web form, pick your target frameworks, and the workflow
validates the input, extracts every endpoint, and uses the OpenAI API to generate
runnable test cases and JSON Schema validations.

---

## Features

- **Web form intake** — paste an OpenAPI/Swagger JSON spec and select frameworks.
- **Robust validation** — checks for empty input, invalid JSON, missing
  `openapi`/`swagger` version, missing `paths`, and zero endpoints, with clear
  error messages.
- **Endpoint extraction** — parses every HTTP operation (method, path, summary).
- **AI test generation** via OpenAI (`gpt-4o-mini`, JSON-object output):
  - REST Assured (Java)
  - Playwright API (TypeScript)
  - Python Requests + pytest
  - Postman Collection v2.1
  - JSON Schema validation
- **Structured output** — API metadata, endpoint list, per-framework test code, timestamp.
- **Error handling workflow** — a dedicated Error Trigger workflow emails failure
  details (workflow name, execution ID, failed node, error message).

## Architecture

```
Form Trigger  ->  Validate & Parse Spec  ->  Is Spec Valid? (IF)
                                                 |               |
                                              (true)          (false)
                                                 v               v
                                        Generate Test Cases   Build Error Response
                                          (OpenAI)
                                                 v
                                          Assemble Result
```

A separate **Error Handler** workflow (Error Trigger -> Gmail) is attached to the
main workflow via `settings.errorWorkflow` and notifies on any failed execution.

## Repository Structure

```
ai-api-test-generator/
├── workflows/
│   ├── ai-api-test-generator.json                 # Main workflow (import into n8n)
│   └── ai-api-test-generator-error-handler.json   # Error handler workflow
├── examples/
│   └── petstore-openapi.json                      # Sample spec to try
├── README.md
├── LICENSE
└── .gitignore
```

## Installation

> Requires an n8n instance (self-hosted or n8n Cloud) and access to the OpenAI API.

1. **Import the workflows**
   - In n8n: **Workflows -> Import from File**.
   - Import `workflows/ai-api-test-generator.json`.
   - Import `workflows/ai-api-test-generator-error-handler.json`.

2. **Configure credentials**
   - **OpenAI**: on the *Generate Test Cases* node, select or create an OpenAI
     credential. (On n8n Cloud you can use built-in AI credits instead of your
     own key.)
   - **Gmail**: on the *Send Failure Alert* node in the error handler, connect a
     Gmail account and set the recipient (`sendTo`).

3. **Attach the error handler**
   - Publish/activate the error handler workflow.
   - In the main workflow: **Settings -> Error Workflow ->** select
     *AI API Test Generator - Error Handler*.

4. **Activate** the main workflow to expose the public form.

## Usage

1. Open the form URL:
   `https://<your-n8n-host>/form/api-test-generator`
2. Paste an OpenAPI/Swagger JSON spec (see `examples/petstore-openapi.json`).
3. Select one or more target frameworks.
4. Optionally provide a base URL.
5. Submit — the generated test cases are returned as structured JSON.

## Configuration

| Setting            | Where                          | Notes                                  |
|--------------------|--------------------------------|----------------------------------------|
| OpenAI credential  | *Generate Test Cases* node     | API key or n8n AI credits              |
| Model              | *Generate Test Cases* node     | Default `gpt-4o-mini`                   |
| Gmail credential   | *Send Failure Alert* node      | OAuth2                                  |
| Alert recipient    | *Send Failure Alert* node      | `sendTo` parameter                     |
| Error workflow     | Main workflow settings         | Points to the error handler workflow   |

## Security

- No secrets are stored in the workflow JSON. Credentials live in n8n's encrypted
  credential store and are configured per instance after import.
- The exported error-handler JSON uses a placeholder recipient
  (`REPLACE_WITH_YOUR_EMAIL@example.com`) — set your real address in n8n.

## Deployment

- **n8n Cloud** or **self-hosted n8n** (Docker or npm). No extra services required.
- The form trigger provides the public endpoint; activate the workflow to serve it.

## Future Roadmap

- Downloadable artifacts (zip of generated test files).
- Support for YAML specs and remote spec URLs.
- Per-endpoint coverage report and metrics.
- Optional persistence of generated suites to a data store.

## License

MIT — see [LICENSE](LICENSE).
