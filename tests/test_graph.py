"""
Basic integration tests for the LangGraph agent.
Run with: pytest tests/
"""
import asyncio
import pytest
from langchain_core.messages import HumanMessage


def test_graph_builds():
    """Graph should compile without errors."""
    from agent.graph import build_graph
    graph = build_graph()
    assert graph is not None


def test_state_structure():
    """State should have correct TypedDict structure."""
    from agent.state import State
    assert "messages" in State.__annotations__
    assert "summary" in State.__annotations__


def test_tools_load():
    """Built-in tools should load without errors."""
    from agent.tools.builtin import ALL_TOOLS
    assert len(ALL_TOOLS) > 0
    for tool in ALL_TOOLS:
        assert hasattr(tool, "name")
        assert hasattr(tool, "description")


@pytest.mark.asyncio
async def test_simple_invoke():
    """Agent should respond to a basic query."""
    from agent.graph import get_graph
    graph  = get_graph()
    config = {"configurable": {"thread_id": "test-001"}}
    result = await graph.ainvoke(
        {"messages": [HumanMessage(content="Say hello in one word.")]},
        config=config,
    )
    assert len(result["messages"]) > 0
    last = result["messages"][-1]
    assert last.content
