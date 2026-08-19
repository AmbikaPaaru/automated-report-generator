"""Structured-output schemas for the Claude "plan_analysis" step.

AnalysisPlan is what Claude returns via ChatAnthropic.with_structured_output(AnalysisPlan) --
this is the actual "agent decides what matters" moment in the pipeline.
"""

from typing import Literal

from pydantic import BaseModel, Field

ChartType = Literal["bar", "line", "scatter", "hist", "box", "pie"]


class ChartSpec(BaseModel):
    """One chart the agent decided is worth generating."""

    chart_type: ChartType = Field(description="Kind of matplotlib chart to render.")
    title: str = Field(description="Short, human-readable chart title.")
    x_column: str = Field(description="Column name from the dataset to use for the x-axis.")
    y_column: str | None = Field(
        default=None,
        description="Column name for the y-axis. Omit for a histogram of x_column.",
    )
    rationale: str = Field(
        description="One sentence on why this chart matters for this dataset."
    )


class AnalysisPlan(BaseModel):
    """The agent's full plan: which charts to build and what stands out."""

    charts: list[ChartSpec] = Field(
        description="3 to 5 charts that best surface what matters in this dataset.",
        min_length=1,
        max_length=6,
    )
    insight_bullets: list[str] = Field(
        description="4 to 6 short, concrete insight bullets grounded in the data.",
        min_length=1,
        max_length=8,
    )
