"""Node/graph tests with ChatAnthropic mocked out -- no live API key or network calls."""

from app.agent import nodes
from app.agent.schemas import AnalysisPlan, ChartSpec
from app.config import settings


class _FakeStructuredModel:
    def __init__(self, plan: AnalysisPlan):
        self._plan = plan

    def invoke(self, messages):
        return self._plan


class _FakeTextResponse:
    def __init__(self, content: str):
        self.content = content


class _FakeChatModel:
    """Stands in for ChatAnthropic: supports both call shapes nodes.py uses."""

    def __init__(self, plan: AnalysisPlan | None = None, text: str = "fake summary"):
        self._plan = plan
        self._text = text

    def with_structured_output(self, schema):
        assert schema is AnalysisPlan
        return _FakeStructuredModel(self._plan)

    def invoke(self, messages):
        return _FakeTextResponse(self._text)


FAKE_PLAN = AnalysisPlan(
    charts=[
        ChartSpec(chart_type="bar", title="Units by region", x_column="region", y_column="units_sold", rationale="r"),
        ChartSpec(chart_type="hist", title="Revenue distribution", x_column="revenue", rationale="r"),
    ],
    insight_bullets=["North leads in units sold.", "Revenue is fairly stable week over week."],
)


def test_load_data_populates_dataframe_and_summary(sample_csv_path):
    state = {"job_id": "t-load", "csv_path": str(sample_csv_path)}
    result = nodes.load_data(state)

    assert result["dataframe"].shape[0] == 20
    assert "region" in result["df_summary"]


def test_plan_analysis_uses_structured_output(monkeypatch, sample_csv_path):
    monkeypatch.setattr(nodes, "_chat_model", lambda: _FakeChatModel(plan=FAKE_PLAN))

    state = nodes.load_data({"job_id": "t-plan", "csv_path": str(sample_csv_path)})
    result = nodes.plan_analysis(state)

    assert result["analysis_plan"] is FAKE_PLAN
    assert len(result["analysis_plan"].charts) == 2


def test_generate_charts_renders_real_pngs(monkeypatch, tmp_path, sample_csv_path):
    monkeypatch.setattr(settings, "chart_dir", tmp_path / "charts")

    state = nodes.load_data({"job_id": "t-charts", "csv_path": str(sample_csv_path)})
    state = {**state, "analysis_plan": FAKE_PLAN}
    result = nodes.generate_charts(state)

    assert len(result["chart_paths"]) == 2


def test_summarize_returns_text_from_model(monkeypatch, sample_csv_path):
    monkeypatch.setattr(nodes, "_chat_model", lambda: _FakeChatModel(text="North region drove most of the volume."))

    state = nodes.load_data({"job_id": "t-summary", "csv_path": str(sample_csv_path)})
    state = {**state, "analysis_plan": FAKE_PLAN}
    result = nodes.summarize(state)

    assert result["executive_summary"] == "North region drove most of the volume."


def test_full_graph_runs_end_to_end_with_mocked_model(monkeypatch, tmp_path, sample_csv_path):
    monkeypatch.setattr(settings, "chart_dir", tmp_path / "charts")
    monkeypatch.setattr(
        nodes, "_chat_model", lambda: _FakeChatModel(plan=FAKE_PLAN, text="Overall, sales were steady.")
    )

    # Import after monkeypatching _chat_model so the compiled graph's node closures see the fake.
    from app.agent.graph import build_graph

    graph = build_graph()
    result = graph.invoke({"job_id": "t-full", "csv_path": str(sample_csv_path)})

    assert result["analysis_plan"] is FAKE_PLAN
    assert len(result["chart_paths"]) == 2
    assert result["executive_summary"] == "Overall, sales were steady."
