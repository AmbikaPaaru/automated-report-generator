from pathlib import Path

from app.agent.schemas import AnalysisPlan, ChartSpec
from app.services.pdf_report import build_pdf_report
from app.services.profiling import load_dataframe


def test_build_pdf_report_creates_nonempty_pdf(tmp_path, sample_csv_path):
    df = load_dataframe(str(sample_csv_path))
    plan = AnalysisPlan(
        charts=[ChartSpec(chart_type="hist", title="Revenue", x_column="revenue", rationale="Shows spread.")],
        insight_bullets=["Revenue ranges from ~1,650 to ~3,200 per week.", "North region appears most often."],
    )

    output_path = tmp_path / "report.pdf"
    result = build_pdf_report(
        job_id="job-pdf-1",
        filename="sample_sales.csv",
        df=df,
        analysis_plan=plan,
        chart_paths=[],  # no chart image on disk -> chart page should be skipped, not crash
        executive_summary="This is a short executive summary of the sample sales data.",
        output_path=output_path,
    )

    assert result == output_path
    assert output_path.exists()
    assert output_path.stat().st_size > 1000  # a real multi-page PDF, not an empty stub


def test_build_pdf_report_handles_unicode_punctuation(tmp_path, sample_csv_path):
    df = load_dataframe(str(sample_csv_path))
    plan = AnalysisPlan(
        charts=[ChartSpec(chart_type="hist", title="Revenue", x_column="revenue", rationale="Shows spread.")],
        insight_bullets=["Sales rose 12% - that's a strong quarter."],
    )
    output_path = tmp_path / "report_unicode.pdf"

    # smart quotes / em-dash that aren't in fpdf2's core-font Latin-1 range
    tricky_summary = "Revenue climbed — a “strong” quarter overall…"

    build_pdf_report(
        job_id="job-pdf-2",
        filename="sample_sales.csv",
        df=df,
        analysis_plan=plan,
        chart_paths=[],
        executive_summary=tricky_summary,
        output_path=output_path,
    )

    assert output_path.exists()
