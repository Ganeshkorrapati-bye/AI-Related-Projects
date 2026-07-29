# Architecture

## Overview

The AI API Test Generator is composed of two n8n workflows:

1. **AI API Test Generator** — the main pipeline (form intake → validation → AI generation → structured result).
2. **AI API Test Generator - Error Handler** — a dedicated Error Trigger workflow that emails failure details.

## Main pipeline

```
┌────────────────┐   ┌──────────────────────┐   ┌──────────────────┐
│ Submit API Spec│──▶│ Validate & Parse Spec│──▶│  Is Spec Valid?  │
│ (Form Trigger) │   │      (Code)          │   │       (IF)       │
└────────────────┘   └──────────────────────┘   └───────┬──────────┘
                                                 true     │     false
                                          ┌───────────────▼─┐  ┌─▼───────────────────┐
                                          │Generate Test     │  │ Build Error Response│
                                          │Cases (OpenAI)    │  │       (Code)        │
                                          └────────┬─────────┘  └─────────────────────┘
                                                   ▼
                                          ┌──────────────────┐
                                          │ Assemble Result  │
                                          │      (Code)      │
                                          └──────────────────┘
```

### Node responsibilities

| Node | Type | Responsibility |
|------|------|----------------|
| Submit API Spec | Form Trigger | Public web form: spec JSON, target frameworks, optional base URL |
| Validate & Parse Spec | Code | Input validation + endpoint extraction |
| Is Spec Valid? | IF | Routes valid specs to AI, invalid ones to the error responder |
| Generate Test Cases | OpenAI | Generates test cases as a JSON object (`gpt-4o-mini`) |
| Assemble Result | Code | Normalizes model output, merges with metadata |
| Build Error Response | Code | Produces a clean, user-facing error payload |

## Validation rules

The `Validate & Parse Spec` node enforces, in order:

1. Non-empty input.
2. Valid JSON (parse errors are surfaced with the parser message).
3. Presence of an `openapi` or `swagger` version field.
4. Presence of a `paths` object.
5. At least one recognized HTTP operation (`get/post/put/patch/delete/head/options`).

On any failure, `valid=false` and a specific `error` message is set, and the IF
node routes to `Build Error Response`.

## AI output handling

The OpenAI node uses the Responses API with `json_object` output format. The
`Assemble Result` node handles both possible shapes defensively:

- `content[0].text` returned as an already-parsed object (typical for
  `json_object`), used directly.
- `content[0].text` returned as a string, parsed with `JSON.parse` and a safe
  fallback if parsing fails.

## Error handling workflow

`settings.errorWorkflow` on the main workflow points to the published Error
Handler workflow. On any failed execution, n8n invokes it with the standard
error payload (`workflow`, `execution.error`, `execution.lastNodeExecuted`),
which is emailed via the Gmail node.
