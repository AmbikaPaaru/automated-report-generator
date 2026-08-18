"""Turn a raw CSV into a compact text profile Claude can reason over.

Kept deliberately simple: dtypes, describe(), null counts, a few sample rows, and a
correlation matrix when there are 2+ numeric columns. This text is what feeds the
plan_analysis prompt, so it needs to be information-dense but short.
"""

import logging

import pandas as pd

logger = logging.getLogger(__name__)

MAX_SAMPLE_ROWS = 5
MAX_SUMMARY_CHARS = 6000  # keep the prompt small/cheap


def load_dataframe(csv_path: str) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    if df.empty:
        raise ValueError(f"CSV at {csv_path} has no rows.")
    return df


def build_profile_summary(df: pd.DataFrame) -> str:
    """Build the text block handed to Claude as the dataset's statistical profile."""
    sections: list[str] = []

    sections.append(f"Shape: {df.shape[0]} rows x {df.shape[1]} columns.")

    sections.append("Columns and dtypes:\n" + df.dtypes.to_string())

    null_counts = df.isnull().sum()
    nulls_with_data = null_counts[null_counts > 0]
    if not nulls_with_data.empty:
        sections.append("Null counts (columns with at least one null):\n" + nulls_with_data.to_string())
    else:
        sections.append("Null counts: none -- the dataset has no missing values.")

    sections.append("Summary statistics (describe, all columns):\n" + df.describe(include="all").to_string())

    numeric_df = df.select_dtypes(include="number")
    if numeric_df.shape[1] >= 2:
        sections.append("Correlation matrix (numeric columns):\n" + numeric_df.corr().to_string())

    sample_rows = df.head(MAX_SAMPLE_ROWS)
    sections.append(f"First {len(sample_rows)} sample rows:\n" + sample_rows.to_string())

    summary = "\n\n".join(sections)
    if len(summary) > MAX_SUMMARY_CHARS:
        logger.warning("Profile summary truncated from %d to %d chars", len(summary), MAX_SUMMARY_CHARS)
        summary = summary[:MAX_SUMMARY_CHARS] + "\n...[truncated]"
    return summary
