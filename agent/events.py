import time
from typing import Any

EventType  = str
EventStage = str


def emit_event(event_type: EventType, stage: EventStage, message: str, **extra) -> dict[str, Any]:
    """
    Unified event contract for streaming to frontend.

    All events follow: {type, stage, message, timestamp, ...extra}
    This consistent shape allows the frontend to handle all event
    types with a single switch statement.
    """
    return {
        "type":      event_type,
        "stage":     stage,
        "message":   message,
        **extra,
        "timestamp": int(time.time() * 1000),
    }


def emit_info(stage: str, message: str, **extra) -> dict:
    return emit_event("info", stage, message, **extra)


def emit_tool_start(tool: str, message: str | None = None) -> dict:
    return emit_event("tool", "start", message or f"{tool} started", tool=tool)


def emit_tool_end(tool: str, message: str | None = None) -> dict:
    return emit_event("tool", "end", message or f"{tool} completed", tool=tool)


def emit_llm_stream(content: str) -> dict:
    return emit_event("llm", "stream", content)


def emit_done(message: str = "Response complete") -> dict:
    return emit_event("done", "end", message)


def emit_error(message: str, **extra) -> dict:
    return emit_event("error", "end", message, **extra)
