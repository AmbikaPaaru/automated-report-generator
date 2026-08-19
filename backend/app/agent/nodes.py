"""LangGraph node functions: load_data -> plan_analysis -> generate_charts -> summarize."""

import logging

from langchain_openai import ChatOpenAI

from app.agent.prompts import (
    PLAN_ANALYSIS_SYSTEM_PROMPT,
    PLAN_ANALYSIS_USER_TEMPLATE,
    SUMMARY_SYSTEM_PROMPT,
    SUMMARY_USER_TEMPLATE,
)
from app.agent.schemas import AnalysisPlan
from app.agent.state import ReportState
from app.config import settings
from app.services.charts import render_charts
from app.services.profiling import build_profile_summary, load_dataframe

logger = logging.getLogger(__name__)


def _chat_model() -> ChatOpenAI:
    # Routed through the internal LiteLLM gateway (OpenAI-compatible), not Anthropic
    # directly -- base_url is what redirects an otherwise-normal ChatOpenAI client to
    # that gateway instead of api.openai.com.
    return ChatOpenAI(
        model=settings.llm_model,
        api_key=settings.llm_api_key,
        base_url=settings.llm_gateway_url,
        timeout=60,
        max_retries=2,
    )


def load_data(state: ReportState) -> ReportState:
    logger.info("job %s: loading + profiling %s", state["job_id"], state["csv_path"])
    df = load_dataframe(state["csv_path"])
    summary = build_profile_summary(df)
    return {**state, "dataframe": df, "df_summary": summary}


def plan_analysis(state: ReportState) -> ReportState:
    logger.info("job %s: asking the LLM to propose charts + insights", state["job_id"])
    model = _chat_model().with_structured_output(AnalysisPlan)
    plan: AnalysisPlan = model.invoke(
        [
            ("system", PLAN_ANALYSIS_SYSTEM_PROMPT),
            ("human", PLAN_ANALYSIS_USER_TEMPLATE.format(df_summary=state["df_summary"])),
        ]
    )
    logger.info(
        "job %s: plan_analysis proposed %d charts, %d insight bullets",
        state["job_id"],
        len(plan.charts),
        len(plan.insight_bullets),
    )
    return {**state, "analysis_plan": plan}


def generate_charts(state: ReportState) -> ReportState:
    plan = state["analysis_plan"]
    logger.info("job %s: rendering %d charts", state["job_id"], len(plan.charts))
    chart_paths = render_charts(state["job_id"], state["dataframe"], plan.charts)
    logger.info("job %s: rendered %d/%d charts successfully", state["job_id"], len(chart_paths), len(plan.charts))
    return {**state, "chart_paths": chart_paths}


def summarize(state: ReportState) -> ReportState:
    logger.info("job %s: writing executive summary", state["job_id"])
    plan = state["analysis_plan"]
    chart_descriptions = "\n".join(f"- {c.title}: {c.rationale}" for c in plan.charts) or "(none)"
    insight_bullets = "\n".join(f"- {b}" for b in plan.insight_bullets) or "(none)"

    model = _chat_model()
    response = model.invoke(
        [
            ("system", SUMMARY_SYSTEM_PROMPT),
            (
                "human",
                SUMMARY_USER_TEMPLATE.format(
                    df_summary=state["df_summary"],
                    chart_descriptions=chart_descriptions,
                    insight_bullets=insight_bullets,
                ),
            ),
        ]
    )
    content = response.content
    executive_summary = content if isinstance(content, str) else str(content)
    return {**state, "executive_summary": executive_summary}
