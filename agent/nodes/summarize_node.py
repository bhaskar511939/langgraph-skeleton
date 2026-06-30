import logging
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage, RemoveMessage

from agent.llm import make_llm
from agent.nodes.model_node import _safe_messages
from agent.state import State
from config.constants import SUMMARIZE_AFTER

logger = logging.getLogger(__name__)


def _text_only_messages(messages: list) -> list:
    """
    Produce a clean human/AI text-only history for summarization.

    Rules:
    - ToolMessage            → drop (raw tool output not needed for summary)
    - AIMessage(tool_calls)  → keep text content only, drop tool_calls
    - Everything else        → keep as-is

    This prevents 'tool_use without tool_result' errors when sending
    history to the summarize LLM which has no tool context.
    """
    result = []
    for msg in messages:
        if isinstance(msg, ToolMessage):
            continue
        if isinstance(msg, AIMessage) and msg.tool_calls:
            if msg.content:
                result.append(AIMessage(content=msg.content))
        else:
            result.append(msg)
    return result


async def summarize_node(state: State) -> dict:
    """
    Compress old conversation history into a rolling summary.

    Why this matters for production:
    Without summarization, context grows unboundedly. A 2-hour
    conversation could consume 50k+ tokens per request, increasing
    both cost and latency. This node keeps the active window small
    while preserving conversational continuity.

    Keeps the 2 most recent messages intact (current exchange)
    and removes all older messages, replacing them with the summary
    injected into the system prompt by model_node.
    """
    existing = state.get("summary", "")

    prompt = (
        f"Existing summary:\n{existing}\n\n"
        "Extend this summary to include the new messages above. Keep it concise."
    ) if existing else (
        "Summarize this conversation in a few concise sentences. "
        "Focus on what was asked and what was answered."
    )

    safe     = _text_only_messages(_safe_messages(state["messages"]))
    response = await make_llm().ainvoke(safe + [HumanMessage(content=prompt)])

    to_delete = [RemoveMessage(id=m.id) for m in state["messages"][:-2]]
    logger.info(f"Conversation summarized — removed {len(to_delete)} messages")
    return {"summary": response.content, "messages": to_delete}
