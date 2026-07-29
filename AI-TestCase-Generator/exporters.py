"""Export generated QA artifacts to Excel, CSV, PDF, and Markdown.

Every exporter returns ``bytes`` so callers (e.g. Streamlit download buttons) can
serve the file without touching the filesystem.
"""
from __future__ import annotations

import csv
import io
import logging
from typing import Any

from prompts import TEST_CASE_FIELDS
from utils import humanize_key

logger = logging.getLogger(__name__)

_COLUMN_ORDER = ["category", *TEST_CASE_FIELDS]
_COLUMN_LABELS = {field: humanize_key(field) for field in _COLUMN_ORDER}


def to_csv(rows: list[dict[str, Any]]) -> bytes:
    """Serialise flat test-case rows to CSV bytes."""
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=_COLUMN_ORDER, extrasaction="ignore")
    writer.writerow(_COLUMN_LABELS)
    for row in rows:
        writer.writerow({key: row.get(key, "") for key in _COLUMN_ORDER})
    return buffer.getvalue().encode("utf-8-sig")


def to_excel(rows: list[dict[str, Any]], analysis: dict[str, Any] | None = None) -> bytes:
    """Serialise test cases (and optional analysis) to a multi-sheet XLSX."""
    try:
        import pandas as pd
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("Excel export requires 'pandas' and 'openpyxl'.") from exc

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        frame = pd.DataFrame(rows, columns=_COLUMN_ORDER).rename(columns=_COLUMN_LABELS)
        if frame.empty:
            frame = pd.DataFrame(columns=list(_COLUMN_LABELS.values()))
        frame.to_excel(writer, sheet_name="Test Cases", index=False)

        if analysis:
            matrix = analysis.get("traceability_matrix") or []
            if matrix:
                tm_rows = [
                    {
                        "Requirement ID": item.get("requirement_id", ""),
                        "Requirement": item.get("requirement", ""),
                        "Test Case IDs": ", ".join(item.get("test_case_ids", []) or []),
                    }
                    for item in matrix
                    if isinstance(item, dict)
                ]
                pd.DataFrame(tm_rows).to_excel(
                    writer, sheet_name="Traceability", index=False
                )

            risks = analysis.get("risk_analysis") or []
            if risks:
                risk_rows = [
                    {
                        "Risk": r.get("risk", ""),
                        "Likelihood": r.get("likelihood", ""),
                        "Impact": r.get("impact", ""),
                        "Mitigation": r.get("mitigation", ""),
                    }
                    for r in risks
                    if isinstance(r, dict)
                ]
                pd.DataFrame(risk_rows).to_excel(writer, sheet_name="Risk Analysis", index=False)

    return buffer.getvalue()


def to_markdown(
    rows: list[dict[str, Any]],
    analysis: dict[str, Any] | None = None,
    application: str = "",
) -> str:
    """Render a full Markdown QA report."""
    lines: list[str] = [f"# QA Documentation - {application}".rstrip(), ""]

    if analysis:
        summary = analysis.get("requirement_summary")
        if summary:
            lines += ["## Requirement Summary", "", str(summary), ""]

        complexity = analysis.get("complexity_score") or {}
        if complexity:
            lines += [
                "## Requirement Complexity",
                "",
                f"- **Score:** {complexity.get('score', 'N/A')}/10 "
                f"({complexity.get('band', 'N/A')})",
                f"- **Rationale:** {complexity.get('rationale', '')}",
                "",
            ]

        coverage = analysis.get("coverage") or {}
        if coverage:
            lines += [
                "## Requirement Coverage",
                "",
                f"- **Coverage:** {coverage.get('percentage', 'N/A')}%",
            ]
            for gap in coverage.get("gaps", []) or []:
                lines.append(f"  - Gap: {gap}")
            lines.append("")

    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        grouped.setdefault(row.get("category", "Uncategorised"), []).append(row)

    lines += ["## Test Cases", ""]
    for category, cases in grouped.items():
        lines += [f"### {category}", ""]
        for case in cases:
            lines += [
                f"#### {case.get('test_case_id', '')} - {case.get('feature', '')}",
                "",
                f"- **Module:** {case.get('module', '')}",
                f"- **Priority:** {case.get('priority', '')} | "
                f"**Severity:** {case.get('severity', '')}",
                f"- **Preconditions:** {case.get('preconditions', '')}",
                f"- **Test Steps:**\n\n{case.get('test_steps', '')}",
                f"- **Test Data:** {case.get('test_data', '')}",
                f"- **Expected Result:** {case.get('expected_result', '')}",
                f"- **Remarks:** {case.get('remarks', '')}",
                "",
            ]

    return "\n".join(lines)


def to_pdf(
    rows: list[dict[str, Any]],
    analysis: dict[str, Any] | None = None,
    application: str = "",
) -> bytes:
    """Render a professional PDF QA report using ReportLab."""
    try:
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
        from reportlab.lib.units import mm
        from reportlab.platypus import (
            Paragraph,
            SimpleDocTemplate,
            Spacer,
            Table,
            TableStyle,
        )
    except ImportError as exc:  # pragma: no cover
        raise RuntimeError("PDF export requires the 'reportlab' package.") from exc

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=15 * mm,
        rightMargin=15 * mm,
        topMargin=15 * mm,
        bottomMargin=15 * mm,
        title=f"QA Documentation - {application}",
    )
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "TitleX", parent=styles["Title"], textColor=colors.HexColor("#4F46E5")
    )
    h2 = ParagraphStyle("H2X", parent=styles["Heading2"], textColor=colors.HexColor("#111827"))
    body = styles["BodyText"]

    story: list[Any] = [
        Paragraph(f"QA Documentation - {application}", title_style),
        Spacer(1, 8),
    ]

    if analysis:
        summary = analysis.get("requirement_summary")
        if summary:
            story += [Paragraph("Requirement Summary", h2), Paragraph(str(summary), body), Spacer(1, 8)]
        complexity = analysis.get("complexity_score") or {}
        if complexity:
            story += [
                Paragraph("Requirement Complexity", h2),
                Paragraph(
                    f"Score: {complexity.get('score', 'N/A')}/10 "
                    f"({complexity.get('band', 'N/A')}). {complexity.get('rationale', '')}",
                    body,
                ),
                Spacer(1, 8),
            ]

    story.append(Paragraph("Test Cases", h2))
    story.append(Spacer(1, 4))

    header = ["ID", "Module", "Feature", "Priority", "Expected Result"]
    table_data: list[list[Any]] = [header]
    cell_style = ParagraphStyle("Cell", parent=body, fontSize=7, leading=9)
    for row in rows:
        table_data.append(
            [
                Paragraph(str(row.get("test_case_id", "")), cell_style),
                Paragraph(str(row.get("module", "")), cell_style),
                Paragraph(str(row.get("feature", "")), cell_style),
                Paragraph(str(row.get("priority", "")), cell_style),
                Paragraph(str(row.get("expected_result", "")), cell_style),
            ]
        )

    if len(table_data) == 1:
        table_data.append([Paragraph("No test cases generated.", cell_style), "", "", "", ""])

    table = Table(table_data, repeatRows=1, colWidths=[24 * mm, 26 * mm, 40 * mm, 18 * mm, 62 * mm])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4F46E5")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTSIZE", (0, 0), (-1, 0), 8),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#D1D5DB")),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F3F4F6")]),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ]
        )
    )
    story.append(table)

    doc.build(story)
    return buffer.getvalue()
