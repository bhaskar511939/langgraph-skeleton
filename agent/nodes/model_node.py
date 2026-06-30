import logging
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.runnables import RunnableConfig

from agent.llm import make_llm
from agent.state import State
from agent.tools import get_all_tools
from prompts import SYSTEM

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = SYSTEM


def _safe_messages(messages: list) -> list:
    """
    Sanitize message history before sending to LLM.

    Problems this solves:
    1. Orphaned ToolMessages (tool result with no matching tool call) —
       causes API errors on most providers
    2. AIMessages with tool_calls but no corresponding ToolMessage —
       leaves the conversation in an inconsistent state
    3. Oversized tool results — truncate to prevent context overflow

    We start from the last HumanMessage and look back 6 messages max
    to keep context focused on the recent conversation.
    """
    last_human_idx = next(
        (i for i in range(len(messages) - 1, -1, -1) if isinstance(messages[i], HumanMessage)),
        None,
    )
    if last_human_idx is None:
        return []

    msgs = messages[max(0, last_human_idx - 6):]

    tool_call_ids   = {tc["id"] for m in msgs if isinstance(m, AIMessage) and m.tool_calls for tc in m.tool_calls}
    tool_result_ids = {m.tool_call_id for m in msgs if isinstance(m, ToolMessage)}

    cleaned = []
    for i, msg in enumerate(msgs):
        if isinstance(msg, ToolMessage):
            if msg.tool_call_id not in tool_call_ids:
                continue
            if len(str(msg.content)) > 15_000:
                msg = ToolMessage(
                    content=str(msg.content)[:15_000] + "\n...[truncated]",
                    tool_call_id=msg.tool_call_id,
                    name=getattr(msg, "name", None),
                )
        elif isinstance(msg, AIMessage) and msg.tool_calls and i < len(msgs) - 1:
            if not all(tc["id"] in tool_result_ids for tc in msg.tool_calls):
                continue
        cleaned.append(msg)

    while cleaned and not isinstance(cleaned[0], HumanMessage):
        cleaned.pop(0)

    return cleaned


async def model_node(state: State, config: RunnableConfig | None = None) -> dict:
    """
    Core LLM inference node.

    Async to avoid blocking the event loop — critical for production
    systems handling concurrent requests. Sync nodes require LangGraph
    to spin up a thread pool worker per call.

    Supports runtime model override via config.configurable.model_override,
    enabling per-request model selection without graph recompilation.
    """
    summary = state.get("summary", "")
    system  = _SYSTEM_PROMPT
    if summary:
        system += f"\n\nConversation summary:\n{summary}"

    model_override = (config or {}).get("configurable", {}).get("model_override")

    response = await make_llm(model_override).bind_tools(get_all_tools()).ainvoke(
        [SystemMessage(content=system)] + _safe_messages(state["messages"])
    )
    return {"messages": [response]}
