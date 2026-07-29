# Usage Guide

## Prerequisites

- An n8n instance (n8n Cloud or self-hosted).
- OpenAI access (your own API key, or n8n AI credits on n8n Cloud).
- A Gmail account for failure alerts (optional but recommended).

## Import

1. In n8n, go to **Workflows → Import from File**.
2. Import `workflows/ai-api-test-generator.json`.
3. Import `workflows/ai-api-test-generator-error-handler.json`.

## Configure credentials

- **OpenAI** — open the *Generate Test Cases* node and attach an OpenAI
  credential (or select n8n AI credits).
- **Gmail** — open the *Send Failure Alert* node in the error handler, attach a
  Gmail OAuth2 credential, and set `sendTo` to your email address.

## Attach the error handler

1. Publish/activate the **Error Handler** workflow.
2. In the **main** workflow: **Settings → Error Workflow → AI API Test
   Generator - Error Handler**.

## Run it

1. Activate the main workflow.
2. Open the form at `https://<your-n8n-host>/form/api-test-generator`.
3. Paste an OpenAPI/Swagger JSON spec (see `examples/petstore-openapi.json`).
4. Choose one or more frameworks.
5. Submit. The response is a structured JSON object:

```json
{
  "status": "success",
  "api": "Pet Store API",
  "version": "1.0.0",
  "endpointCount": 4,
  "frameworks": "Python Requests + pytest",
  "endpoints": [ ... ],
  "tests": { "summary": "...", "python_requests": { ... }, "json_schema": { ... } },
  "generatedAt": "2026-07-29T12:27:23.867Z"
}
```

## Error responses

Invalid input returns a clean payload instead of crashing:

```json
{
  "status": "error",
  "message": "The specification is not valid JSON: ...",
  "hint": "Ensure you pasted a valid OpenAPI 3.x or Swagger 2.0 JSON document with a non-empty \"paths\" object.",
  "endpointCount": 0
}
```

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|--------------|-----|
| "No specification was provided" | Empty spec field | Paste a spec |
| "not valid JSON" | Malformed JSON | Validate the JSON |
| "Missing openapi/swagger" | Wrong document | Provide an OpenAPI/Swagger doc |
| No email on failure | Error handler not published/attached | Publish it and set it in Settings → Error Workflow |
