from langchain_core.messages import AIMessage
from langgraph.graph import END

from config.constants import SUMMARIZE_AFTER
from agent.state import State


def route_node(state: State) -> str:
    """
    Determine the next graph node after model inference.

    Routing logic:
    - Tool calls present → execute tools (tools node)
    - Message count exceeds threshold → summarize old history
    - Otherwise → end the conversation turn

    The summarization threshold prevents unbounded context growth
    in long-running conversations, which would increase latency
    and cost on every request.
    """
    last = state["messages"][-1]
    if isinstance(last, AIMessage) and last.tool_calls:
        return "tools"
    if len(state["messages"]) > SUMMARIZE_AFTER:
        return "summarize"
    return END
