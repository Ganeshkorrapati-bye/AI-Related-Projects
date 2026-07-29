"""Reusable prompt templates for the QA generation engine.

Prompts are stored here (separate from business logic) so they can be versioned,
reviewed, and tuned independently. The system persona is shared across every
generation call to keep the AI's behaviour consistent.
"""
from __future__ import annotations

from textwrap import dedent

# The shared persona applied to every generation request.
SYSTEM_PERSONA: str = dedent(
    """
    You are an ISTQB-certified Senior QA Engineer with 15+ years of enterprise
    software testing experience. You design test artifacts that are precise,
    traceable, and ready to hand to an enterprise QA team.

    Rules you always follow:
    - Base every artifact strictly on the supplied requirements.
    - Prefer realistic, domain-specific detail over generic filler.
    - Never invent APIs, tables, or behaviour that contradict the requirements.
    - Always respond with a single valid JSON object matching the requested
      schema. Do not wrap the JSON in Markdown fences or add commentary.
    """
).strip()


# Canonical field list every functional-style test case must contain.
TEST_CASE_FIELDS: list[str] = [
    "test_case_id",
    "module",
    "feature",
    "priority",
    "severity",
    "preconditions",
    "test_steps",
    "test_data",
    "expected_result",
    "actual_result",
    "status",
    "remarks",
]


def _json_instruction(schema_description: str) -> str:
    return dedent(
        f"""
        Respond ONLY with a valid JSON object with this exact shape:
        {schema_description}
        Do not include Markdown fences or any text outside the JSON object.
        """
    ).strip()


def test_cases_prompt(requirements: str, application: str, categories: list[str]) -> str:
    """Build the prompt that generates every category of test case."""
    field_list = ", ".join(TEST_CASE_FIELDS)
    category_list = "\n".join(f"- {c}" for c in categories)
    schema = (
        '{ "<category_key>": [ { ' + ", ".join(f'"{f}": string' for f in TEST_CASE_FIELDS) + " } ] }"
    )
    return dedent(
        f"""
        Application under test: {application}

        Generate comprehensive test cases for the following requirements.

        Produce these categories (use snake_case category keys derived from the
        names below, e.g. "Functional Test Cases" -> "functional_test_cases"):
        {category_list}

        Every test case object MUST contain exactly these fields: {field_list}.
        - "actual_result" and "status" must be empty strings.
        - "priority" is one of: Critical, High, Medium, Low.
        - "severity" is one of: Blocker, Major, Minor, Trivial.
        - "test_steps" is a single string with steps separated by newlines and
          numbered (1., 2., 3.).
        Provide multiple meaningful cases per category where the requirements allow.

        {_json_instruction(schema)}

        REQUIREMENTS:
        {requirements}
        """
    ).strip()


def api_artifacts_prompt(requirements: str, application: str) -> str:
    """Prompt for API-focused artifacts, only used when APIs are relevant."""
    schema = dedent(
        """
        {
          "api_test_cases": [ { "test_case_id": string, "title": string,
            "endpoint": string, "method": string, "auth": string,
            "json_request": object, "json_response": object,
            "json_schema": object, "expected_status": string,
            "category": string } ],
          "postman_collection": object,
          "rest_assured_tests": string,
          "playwright_api_tests": string
        }
        """
    ).strip()
    return dedent(
        f"""
        Application under test: {application}

        If — and only if — the requirements imply a REST API, generate API test
        artifacts. Cover authentication, authorization, negative, and rate-limit
        cases inside "api_test_cases" using the "category" field to label them.

        - "postman_collection" must be a valid Postman v2.1 collection object.
        - "rest_assured_tests" is Java source (as a string) using REST Assured.
        - "playwright_api_tests" is TypeScript source (as a string) using
          Playwright's APIRequestContext.

        If no API is implied, return every field empty (empty arrays / objects /
        strings).

        {_json_instruction(schema)}

        REQUIREMENTS:
        {requirements}
        """
    ).strip()


def analysis_prompt(requirements: str, application: str) -> str:
    """Prompt for the AI analysis panel artifacts."""
    schema = dedent(
        """
        {
          "requirement_summary": string,
          "complexity_score": { "score": number, "band": string, "rationale": string },
          "coverage": { "percentage": number, "covered_areas": [string], "gaps": [string] },
          "risk_analysis": [ { "risk": string, "likelihood": string,
            "impact": string, "mitigation": string } ],
          "traceability_matrix": [ { "requirement_id": string,
            "requirement": string, "test_case_ids": [string] } ],
          "test_strategy": string,
          "test_plan": string,
          "sql_test_suggestions": [string],
          "bug_report_template": string,
          "duplicate_test_case_notes": [string]
        }
        """
    ).strip()
    return dedent(
        f"""
        Application under test: {application}

        Analyse the requirements below and produce QA management artifacts.
        - "complexity_score.score" is 1-10; "band" is Low/Medium/High.
        - "coverage.percentage" is 0-100.
        - "test_strategy" and "test_plan" are Markdown strings.
        - "bug_report_template" is a Markdown bug template.

        {_json_instruction(schema)}

        REQUIREMENTS:
        {requirements}
        """
    ).strip()
