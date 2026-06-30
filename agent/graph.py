import logging
from langgraph.graph import StateGraph, START, END

from config import settings
from agent.state import State
from agent.checkpointers import get_checkpointer
from agent.nodes import model_node, summarize_node, tool_node, route_node

logger = logging.getLogger(__name__)

_graph = None


def build_graph():
    """
    Build and compile the LangGraph StateGraph.

    Graph topology:
      START → model → [tools → model]* → [summarize →] END

    The model node handles LLM inference.
    The tools node executes tool calls returned by the model.
    The summarize node compresses old conversation history.
    The route_node decides which edge to take after model inference.

    Recursion limit of 17 prevents infinite tool-calling loops
    while allowing enough steps for complex multi-tool queries.
    """
    g = StateGraph(State)

    g.add_node("model",     model_node)
    g.add_node("tools",     tool_node)
    g.add_node("summarize", summarize_node)

    g.add_edge(START, "model")
    g.add_conditional_edges(
        "model",
        route_node,
        {"tools": "tools", "summarize": "summarize", END: END},
    )
    g.add_edge("tools",     "model")
    g.add_edge("summarize", END)

    compiled = g.compile(checkpointer=get_checkpointer())
    compiled.recursion_limit = 17

    logger.info(
        f"Graph ready — model={settings.DEFAULT_MODEL}"
        f"  memory={settings.MEMORY_BACKEND}"
    )
    return compiled


def get_graph():
    global _graph
    if _graph is None:
        _graph = build_graph()
    return _graph
