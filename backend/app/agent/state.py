"""Shared state passed between LangGraph nodes."""

from typing import Any, NotRequired, TypedDict

import pandas as pd

from app.agent.schemas import AnalysisPlan


class ReportState(TypedDict):
    job_id: str
    csv_path: str

    # populated by load_data
    df_summary: NotRequired[str]
    dataframe: NotRequired[pd.DataFrame]

    # populated by plan_analysis
    analysis_plan: NotRequired[AnalysisPlan]

    # populated by generate_charts
    chart_paths: NotRequired[list[str]]

    # populated by summarize
    executive_summary: NotRequired[str]

    # allow forward-compatible extra keys without breaking type checking
    extra: NotRequired[dict[str, Any]]
