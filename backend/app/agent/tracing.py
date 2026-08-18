"""Langfuse tracing for the LangGraph run.

Langfuse's Python SDK (v3, OTel-based) reads LANGFUSE_PUBLIC_KEY / LANGFUSE_SECRET_KEY /
LANGFUSE_HOST straight from the environment the first time a client is needed -- there's
nothing to pass in explicitly as long as main.py has called load_dotenv() before this runs.

langfuse.langchain.CallbackHandler() attaches to a LangGraph/LangChain run via
`config={"callbacks": [handler]}` on .invoke(...) and traces every node plus every nested
LLM call (prompts, completions, tokens, latency) as one connected trace. We tag each run
with langfuse_session_id=job_id (a Langfuse-recognized metadata key) so every job's trace
is easy to find and group in the dashboard.
"""

from langfuse.langchain import CallbackHandler


def build_langfuse_handler() -> CallbackHandler:
    return CallbackHandler()


def langgraph_run_config(job_id: str) -> dict:
    """Config dict to pass as graph.invoke(state, config=...)."""
    return {
        "callbacks": [build_langfuse_handler()],
        "metadata": {
            "langfuse_session_id": job_id,
            "langfuse_tags": ["automated-report-generator"],
        },
    }
