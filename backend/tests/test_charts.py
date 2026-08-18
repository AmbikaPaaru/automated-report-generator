from pathlib import Path

from app.agent.schemas import ChartSpec
from app.config import settings
from app.services.charts import render_charts
from app.services.profiling import load_dataframe


def test_render_charts_creates_png_files(monkeypatch, tmp_path, sample_csv_path):
    monkeypatch.setattr(settings, "chart_dir", tmp_path / "charts")
    df = load_dataframe(str(sample_csv_path))

    charts = [
        ChartSpec(chart_type="bar", title="Units by region", x_column="region", y_column="units_sold", rationale="r"),
        ChartSpec(chart_type="hist", title="Revenue distribution", x_column="revenue", rationale="r"),
    ]

    paths = render_charts("job-1", df, charts)

    assert len(paths) == 2
    for p in paths:
        assert Path(p).exists()
        assert Path(p).stat().st_size > 0


def test_render_charts_skips_bad_column_without_raising(monkeypatch, tmp_path, sample_csv_path):
    monkeypatch.setattr(settings, "chart_dir", tmp_path / "charts")
    df = load_dataframe(str(sample_csv_path))

    charts = [
        ChartSpec(chart_type="bar", title="Bad chart", x_column="does_not_exist", rationale="r"),
        ChartSpec(chart_type="hist", title="Revenue distribution", x_column="revenue", rationale="r"),
    ]

    paths = render_charts("job-2", df, charts)

    assert len(paths) == 1  # the bad one is skipped, the good one still renders
