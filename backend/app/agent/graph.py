"""Build the LangGraph StateGraph: load_data -> plan_analysis -> generate_charts -> summarize."""

from langgraph.graph import END, START, StateGraph

from app.agent.nodes import generate_charts, load_data, plan_analysis, summarize
from app.agent.state import ReportState


def build_graph():
    graph = StateGraph(ReportState)

    graph.add_node("load_data", load_data)
    graph.add_node("plan_analysis", plan_analysis)
    graph.add_node("generate_charts", generate_charts)
    graph.add_node("summarize", summarize)

    graph.add_edge(START, "load_data")
    graph.add_edge("load_data", "plan_analysis")
    graph.add_edge("plan_analysis", "generate_charts")
    graph.add_edge("generate_charts", "summarize")
    graph.add_edge("summarize", END)

    return graph.compile()


# Compiled once at import time; graphs are stateless/reusable across invocations.
report_graph = build_graph()
