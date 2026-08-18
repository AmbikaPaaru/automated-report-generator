"""Assemble the final PDF report with fpdf2: cover -> exec summary -> charts -> data table.

fpdf2's built-in core fonts (Helvetica/Arial etc.) only support Latin-1. Claude's prose
sometimes contains smart quotes/em-dashes that aren't in that range, so we sanitize text
to the closest ASCII before writing it rather than shipping a Unicode TTF font just for a
portfolio demo.
"""

import logging
from datetime import datetime
from pathlib import Path

import pandas as pd
from fpdf import FPDF

from app.agent.schemas import AnalysisPlan

logger = logging.getLogger(__name__)

_CHAR_REPLACEMENTS = {
    "‘": "'", "’": "'", "“": '"', "”": '"',
    "–": "-", "—": "-", "…": "...", "•": "-",
}


def _sanitize(text: str) -> str:
    for bad, good in _CHAR_REPLACEMENTS.items():
        text = text.replace(bad, good)
    return text.encode("latin-1", errors="replace").decode("latin-1")


class ReportPDF(FPDF):
    def footer(self) -> None:
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(140, 140, 140)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")


def build_pdf_report(
    job_id: str,
    filename: str,
    df: pd.DataFrame,
    analysis_plan: AnalysisPlan,
    chart_paths: list[str],
    executive_summary: str,
    output_path: Path,
) -> Path:
    pdf = ReportPDF(format="A4")
    pdf.set_auto_page_break(auto=True, margin=20)

    _add_cover_page(pdf, filename, df)
    _add_summary_page(pdf, executive_summary, analysis_plan.insight_bullets)
    for i, (spec, chart_path) in enumerate(zip(analysis_plan.charts, chart_paths, strict=False)):
        _add_chart_page(pdf, spec.title, spec.rationale, chart_path)
    _add_data_table_page(pdf, df)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    pdf.output(str(output_path))
    logger.info("job %s: PDF written to %s", job_id, output_path)
    return output_path


def _add_cover_page(pdf: ReportPDF, filename: str, df: pd.DataFrame) -> None:
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 24)
    pdf.ln(40)
    pdf.cell(0, 15, "Automated Data Report", align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", "", 12)
    pdf.set_text_color(90, 90, 90)
    pdf.cell(0, 10, _sanitize(f"Source file: {filename}"), align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 10, f"Rows: {df.shape[0]}  |  Columns: {df.shape[1]}", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(
        0, 10, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", align="C", new_x="LMARGIN", new_y="NEXT"
    )


def _add_summary_page(pdf: ReportPDF, executive_summary: str, insight_bullets: list[str]) -> None:
    pdf.add_page()
    pdf.set_text_color(20, 20, 20)
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 12, "Executive Summary", new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", "", 11)
    pdf.multi_cell(0, 7, _sanitize(executive_summary), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(6)

    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 10, "Key Insights", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 11)
    for bullet in insight_bullets:
        pdf.multi_cell(0, 7, _sanitize(f"- {bullet}"), new_x="LMARGIN", new_y="NEXT")


def _add_chart_page(pdf: ReportPDF, title: str, rationale: str, chart_path: str) -> None:
    if not Path(chart_path).exists():
        return
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 12, _sanitize(title), new_x="LMARGIN", new_y="NEXT")

    pdf.image(chart_path, x=15, w=180)
    pdf.ln(4)

    pdf.set_font("Helvetica", "I", 10)
    pdf.set_text_color(90, 90, 90)
    pdf.multi_cell(0, 6, _sanitize(rationale), new_x="LMARGIN", new_y="NEXT")
    pdf.set_text_color(20, 20, 20)


def _add_data_table_page(pdf: ReportPDF, df: pd.DataFrame) -> None:
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 12, "Data Summary", new_x="LMARGIN", new_y="NEXT")

    numeric_df = df.select_dtypes(include="number")
    if numeric_df.empty:
        pdf.set_font("Helvetica", "", 11)
        pdf.multi_cell(0, 7, "No numeric columns to summarize.", new_x="LMARGIN", new_y="NEXT")
        return

    described = numeric_df.describe().round(2)
    columns = ["stat"] + list(described.columns)
    col_width = 190 / len(columns)

    pdf.set_font("Helvetica", "B", 8)
    for col in columns:
        pdf.cell(col_width, 8, _sanitize(str(col))[:14], border=1)
    pdf.ln()

    pdf.set_font("Helvetica", "", 8)
    for stat_name, row in described.iterrows():
        pdf.cell(col_width, 8, str(stat_name), border=1)
        for value in row:
            pdf.cell(col_width, 8, str(value), border=1)
        pdf.ln()
