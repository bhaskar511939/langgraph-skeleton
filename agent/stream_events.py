import re
import logging
from typing import AsyncGenerator

from fastapi import Request
from langchain_core.messages import HumanMessage

from agent.graph import get_graph
from agent.events import (
    emit_info, emit_tool_start, emit_tool_end,
    emit_llm_stream, emit_error,
)

logger = logging.getLogger(__name__)


def _clean_tool_name(name: str) -> str:
    """Strip auto-generated suffixes like '_0', '_1' from tool names."""
    return re.sub(r'_\d+$', '', name).replace('_', ' ').strip()


def _extract_text(chunk) -> str:
    """Extract plain text from a model chunk (handles str and list content)."""
    if isinstance(chunk.content, str):
        return chunk.content
    if isinstance(chunk.content, list):
        return "".join(
            b.get("text", "") for b in chunk.content
            if isinstance(b, dict) and b.get("type") == "text"
        )
    return ""


async def stream_graph(
    query:   str,
    config:  dict,
    request: Request | None = None,
) -> AsyncGenerator[dict, None]:
    """
    Execute the LangGraph agent and yield event dicts.

    Design decision: yields plain dicts, not SSE strings.
    The HTTP layer (api/sse.py) handles serialization.
    This separation makes the streaming logic independently testable.

    Filtered events:
      on_tool_start/end/error  — from tool_node only
      on_chat_model_stream     — from model_node only (prevents
                                 summarize node leaking to UI)
      on_custom_event          — dispatch_custom_event() calls
    """
    graph       = get_graph()
    first_token = True

    try:
        async for event in graph.astream_events(
            {"messages": [HumanMessage(content=query)]},
            config=config,
            version="v2",
        ):
            if request and await request.is_disconnected():
                logger.info("Client disconnected — stopping stream")
                break

            kind = event["event"]
            name = event.get("name", "")
            data = event.get("data", {})
            node = event.get("metadata", {}).get("langgraph_node", "")

            if kind == "on_tool_start" and node == "tools":
                yield emit_tool_start(_clean_tool_name(name))
                yield {"__keepalive__": True}

            elif kind == "on_tool_end" and node == "tools":
                first_token = True
                yield emit_tool_end(_clean_tool_name(name))
                yield emit_info("thinking", "Analyzing results...")

            elif kind == "on_tool_error" and node == "tools":
                err = data.get("error", "Tool execution failed")
                logger.error(f"Tool error [{name}]: {err}")
                yield emit_error(f"Tool error: {_clean_tool_name(name)}", tool=name, details=str(err))

            elif kind == "on_chat_model_stream" and node == "model":
                chunk = data.get("chunk")
                if chunk:
                    text = _extract_text(chunk)
                    if text:
                        if first_token:
                            first_token = False
                        yield emit_llm_stream(text)

            elif kind == "on_custom_event":
                custom = data.get("data", {})
                if isinstance(custom, dict) and "type" in custom:
                    yield custom
                else:
                    msg = custom.get("message", f"Event: {name}") if isinstance(custom, dict) else f"Event: {name}"
                    yield emit_info("thinking", msg)

    except Exception as e:
        logger.error(f"Stream error: {e}", exc_info=True)
        yield emit_error("Stream interrupted", details=str(e))
