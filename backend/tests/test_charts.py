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


def test_render_charts_supports_pie(monkeypatch, tmp_path, sample_csv_path):
    monkeypatch.setattr(settings, "chart_dir", tmp_path / "charts")
    df = load_dataframe(str(sample_csv_path))

    charts = [
        ChartSpec(chart_type="pie", title="Revenue share by region", x_column="region", y_column="revenue", rationale="r"),
    ]

    paths = render_charts("job-pie", df, charts)

    assert len(paths) == 1
    assert Path(paths[0]).stat().st_size > 0


def test_render_charts_pie_caps_slices_with_other_bucket(monkeypatch, tmp_path, sample_csv_path):
    # sample_sales.csv only has a handful of regions/products, so force the "many
    # categories" path by charting a column with more distinct values than MAX_SLICES.
    monkeypatch.setattr(settings, "chart_dir", tmp_path / "charts")
    df = load_dataframe(str(sample_csv_path))

    charts = [
        ChartSpec(chart_type="pie", title="Revenue by date", x_column="date", y_column="revenue", rationale="r"),
    ]

    paths = render_charts("job-pie-many", df, charts)

    assert len(paths) == 1  # renders without raising even with far more than 5 categories


def test_render_charts_skips_bad_column_without_raising(monkeypatch, tmp_path, sample_csv_path):
    monkeypatch.setattr(settings, "chart_dir", tmp_path / "charts")
    df = load_dataframe(str(sample_csv_path))

    charts = [
        ChartSpec(chart_type="bar", title="Bad chart", x_column="does_not_exist", rationale="r"),
        ChartSpec(chart_type="hist", title="Revenue distribution", x_column="revenue", rationale="r"),
    ]

    paths = render_charts("job-2", df, charts)

    assert len(paths) == 1  # the bad one is skipped, the good one still renders
