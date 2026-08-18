from app.services.profiling import build_profile_summary, load_dataframe


def test_load_dataframe_reads_csv(sample_csv_path):
    df = load_dataframe(str(sample_csv_path))
    assert df.shape[0] == 20
    assert list(df.columns) == ["date", "region", "product", "units_sold", "revenue"]


def test_build_profile_summary_mentions_columns_and_shape(sample_csv_path):
    df = load_dataframe(str(sample_csv_path))
    summary = build_profile_summary(df)

    assert "20 rows" in summary
    assert "region" in summary
    assert "revenue" in summary
    assert "Correlation matrix" in summary  # 2+ numeric columns present
