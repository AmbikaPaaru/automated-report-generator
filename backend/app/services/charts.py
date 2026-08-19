"""Render the chart plan Claude proposed into actual PNG files with matplotlib.

No LLM calls here -- purely mechanical: for each ChartSpec, plot the real columns
from the real DataFrame and save a PNG. If a proposed column doesn't exist (the model
hallucinated, or a name was truncated), skip that chart and log a warning rather than
crashing the whole pipeline over one bad chart.
"""

import logging
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # headless: no GUI backend needed on a server
import matplotlib.pyplot as plt
import pandas as pd

from app.agent.schemas import ChartSpec
from app.config import settings

logger = logging.getLogger(__name__)


def render_charts(job_id: str, df: pd.DataFrame, charts: list[ChartSpec]) -> list[str]:
    out_dir = settings.resolved_chart_dir()
    out_dir.mkdir(parents=True, exist_ok=True)

    chart_paths: list[str] = []
    for i, spec in enumerate(charts):
        try:
            path = _render_one_chart(out_dir, job_id, i, df, spec)
            chart_paths.append(str(path))
        except Exception:
            logger.warning(
                "job %s: skipping chart %d (%s) -- could not render", job_id, i, spec.title, exc_info=True
            )
    return chart_paths


def _render_one_chart(out_dir: Path, job_id: str, index: int, df: pd.DataFrame, spec: ChartSpec) -> Path:
    if spec.x_column not in df.columns:
        raise ValueError(f"x_column '{spec.x_column}' not in dataframe columns")
    if spec.y_column is not None and spec.y_column not in df.columns:
        raise ValueError(f"y_column '{spec.y_column}' not in dataframe columns")

    fig, ax = plt.subplots(figsize=(7, 4.2))

    if spec.chart_type == "hist":
        ax.hist(df[spec.x_column].dropna(), bins=20, color="#4C72B0")
        ax.set_xlabel(spec.x_column)
        ax.set_ylabel("Frequency")

    elif spec.chart_type == "box":
        ax.boxplot(df[spec.x_column].dropna(), vert=True)
        ax.set_xticklabels([spec.x_column])

    elif spec.chart_type == "bar":
        grouped = df.groupby(spec.x_column)[spec.y_column].sum() if spec.y_column else df[spec.x_column].value_counts()
        grouped = grouped.sort_values(ascending=False).head(15)
        ax.bar(grouped.index.astype(str), grouped.values, color="#4C72B0")
        ax.set_xlabel(spec.x_column)
        ax.set_ylabel(spec.y_column or "count")
        ax.tick_params(axis="x", rotation=45)

    elif spec.chart_type == "line":
        plot_df = df[[spec.x_column, spec.y_column]].dropna().sort_values(spec.x_column) if spec.y_column else df[[spec.x_column]].dropna()
        ax.plot(plot_df[spec.x_column], plot_df[spec.y_column] if spec.y_column else range(len(plot_df)), color="#4C72B0")
        ax.set_xlabel(spec.x_column)
        ax.set_ylabel(spec.y_column or "index")
        ax.tick_params(axis="x", rotation=45)

    elif spec.chart_type == "scatter":
        plot_df = df[[spec.x_column, spec.y_column]].dropna()
        ax.scatter(plot_df[spec.x_column], plot_df[spec.y_column], color="#4C72B0", alpha=0.6)
        ax.set_xlabel(spec.x_column)
        ax.set_ylabel(spec.y_column)

    elif spec.chart_type == "pie":
        grouped = df.groupby(spec.x_column)[spec.y_column].sum() if spec.y_column else df[spec.x_column].value_counts()
        grouped = grouped.sort_values(ascending=False)
        # A pie chart with a long tail of tiny slices is unreadable -- cap it at the top
        # 5 categories and fold everything else into one "Other" slice, same spirit as
        # bar's .head(15) above but tighter, since pie slices need to stay visually distinct.
        MAX_SLICES = 5
        if len(grouped) > MAX_SLICES:
            other_total = grouped.iloc[MAX_SLICES:].sum()
            grouped = grouped.head(MAX_SLICES)
            grouped[f"Other ({len(df[spec.x_column].unique()) - MAX_SLICES} more)"] = other_total
        ax.pie(grouped.values, labels=grouped.index.astype(str), autopct="%1.0f%%", startangle=90)
        ax.axis("equal")  # keep it a circle, not an ellipse

    else:
        plt.close(fig)
        raise ValueError(f"Unsupported chart_type '{spec.chart_type}'")

    ax.set_title(spec.title)
    fig.tight_layout()

    path = out_dir / f"{job_id}_{index}.png"
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path
