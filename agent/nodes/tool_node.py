from langgraph.prebuilt import ToolNode

from agent.state import State
from agent.tools import get_all_tools


async def tool_node(state: State) -> dict:
    """
    Execute tool calls requested by the model.

    Uses LangGraph's built-in ToolNode which handles:
    - Parallel tool execution
    - Error handling and recovery
    - Proper message formatting for the next model call

    Async so MCP tools (which are inherently async) work correctly.
    A sync tool_node would run in a thread pool where async tools
    cannot properly await their I/O operations.
    """
    node = ToolNode(get_all_tools(), handle_tool_errors=True)
    return await node.ainvoke(state)
